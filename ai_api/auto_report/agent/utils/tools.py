import os
from typing import List, Dict, Any
from openpyxl.worksheet import worksheet
from typing_extensions import Annotated, TypeAlias
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.styles import Font
from copy import copy
import re

from loguru import logger
from openpyxl.styles import Font, PatternFill, Border, Alignment, Protection
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain_core.tools import tool


from langgraph.prebuilt import InjectedState
from auto_report.agent.utils.state import WorkflowState
from auto_report.agent.utils.util_function import markdown_to_df, remove_trailing_empty_rows, is_row_empty_except_one_cell, is_currency_string, convert_currency_to_number, convert_to_number

AzureSearchResult: TypeAlias = List[Dict[str, Any]]

async def _hybrid_search_data_impl(
    index_name: str, 
    query: str, 
    top_k: int = 17, 
    score_threshold: float | None = None,
    vector_field: str = "content_vector",
    embedding_model: Any = None  # Pass your embedding model here
) -> AzureSearchResult:
    """
    Hybrid search combining keyword search (BM25) and vector search.
    Provides best of both worlds: exact matching and semantic similarity.

    Args:
        index_name (str): The name of the Azure Search index.
        query (str): The search query string.
        top_k (int, optional): The maximum number of results to return. Defaults to 13.
        score_threshold (float | None, optional): Minimum score threshold for results. Defaults to None.
        vector_field (str, optional): Name of the vector field in index. Defaults to "content_vector".
        embedding_model (Any, optional): Model to generate query embeddings. Required for vector search.

    Returns:
        List[dict]: List of search results ranked by hybrid relevance.
    """
    from azure.search.documents.models import VectorizedQuery
    
    credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=index_name,
        credential=credential
    )

    results: List[Dict[str, Any]] = []
    try:
        # Generate query embedding for vector search
        query_vector = None
        if embedding_model is not None:
            query_vector = await embedding_model.embed_query(query)  # Adjust based on your model
        
        # Create vectorized query
        vector_queries = []
        if query_vector is not None:
            vector_queries.append(
                VectorizedQuery(
                    vector=query_vector,
                    k_nearest_neighbors=top_k,
                    fields=vector_field
                )
            )
        
        # Perform hybrid search
        response = await search_client.search(
            search_text=query,  # Keyword search component
            vector_queries=vector_queries,  # Vector search component
            top=top_k,
            # # Optional: Add semantic ranking on top of hybrid
            # query_type="semantic",
            # semantic_configuration_name="default"
        )
        
        async for result in response:
            # Hybrid search uses @search.score (combines both scores)
            score = getattr(result, "@search.score", None)
            if score_threshold is not None and score is not None and score < score_threshold:
                continue
            
            if hasattr(result, "as_dict"):
                results.append(result.as_dict())
            else:
                try:
                    results.append(dict(result))
                except Exception:
                    results.append(result)
                    
    except Exception as e:
        logger.error(f"Error in _hybrid_search_data_impl: {e}")
    finally:
        await search_client.close()
    
    return results

async def _search_data_impl(
    index_name: str, query: str, top_k: int = 13, score_threshold: float | None = None
) -> AzureSearchResult:
    """
    Internal helper to search Azure Cognitive Search index.

    Args:
        index_name (str): The name of the Azure Search index.
        query (str): The search query string.
        top_k (int, optional): The maximum number of results to return. Defaults to 5.
        score_threshold (float | None, optional): Minimum score threshold for results. Defaults to None.

    Returns:
        List[dict]: List of search results matching the query.
    """
    credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=index_name,
        credential=credential
    )

    results: List[Dict[str, Any]] = []
    try:
        response = await search_client.search(
            search_text=query,
            top=top_k
        )
        async for result in response:
            score = getattr(result, "@search.score", None)
            if score_threshold is not None and score is not None and score < score_threshold:
                continue
            if hasattr(result, "as_dict"):
                results.append(result.as_dict())
            else:
                try:
                    results.append(dict(result))
                except Exception:
                    results.append(result)
    except Exception as e:
        logger.error(f"Error in _search_data_impl: {e}")
    finally:
        await search_client.close()
    return results


@tool
def get_fields_to_fill_dynamic(searching_summary: str, fiscal_year, period_header_row, check_column, component_company, component_sheet, required_unit,
                               state: Annotated[dict, InjectedState]):
    """
    Extracts a list of field names from an Excel worksheet that require user input, starting from a specified row.

    This function scans a sheet in an Excel file, looking for field names in column B (second column), 
    starting from the given row. For each field, it checks if any of the specified columns (by default, column D) 
    in that row are empty and not formulas. If so, it marks the field as needilng input. The output is a markdown table listing 
    only the fields that need to be filled.

    Args:
        searching_summary (str): The searching_summary combining information at the start of a sheet.
        period_header_row (int): The row number that contain the period header.
        check_column (list of str): The columns to check for missing values. Default is ["D"].
        component_company (str): Company name of the file.
        component_sheet (str): Current sheet type.
        required_unit (str): Required unit of the sheet

    Returns:
        str: the searching_summary of the Excel sheet.
        str: A markdown-formatted table of field names that need input, or a message if no fields need to be filled.
    """
    sheet = state['worksheet']  # Replace with your actual sheet name
    
    # Pre-convert column letters to indices for efficiency
    check_col_indices = [column_index_from_string(col) for col in check_column]
    first_check_col = min(check_col_indices)  # Get the first check column index

    fields_to_fill = []
    markdown_rows = [f"| Field Name ({required_unit}) |", "|------------|"]
    seen_field_names = {}
    
    # Optimize row iteration - get actual data range instead of max_row
    max_data_row = min(sheet.max_row, period_header_row + 1000)  # Reasonable limit
    
    for row in range(period_header_row + 1, max_data_row + 1):
        # field_cell = sheet.cell(row=row, column=2)  # Column B
        # field_name = field_cell.value
        temp_field_names = []
        for col in range(2, first_check_col):
            cell_value = sheet.cell(row=row, column=col).value
            if cell_value and str(cell_value).strip():
                temp_field_names.append(str(cell_value).strip())
        field_name = " - ".join(temp_field_names) if temp_field_names else ""
        
        if not field_name or not str(field_name).strip():
            markdown_rows.append("| |")
            continue
        
        field_name_str = str(field_name)
        # Preserve indentation efficiently
        indent = field_name_str[:len(field_name_str) - len(field_name_str.lstrip())]
        stripped_field_name = field_name_str.strip()
        
        # Handle duplicate field names
        if stripped_field_name in seen_field_names:
            seen_field_names[stripped_field_name] += 1
            unique_field_name = f"{stripped_field_name}_{seen_field_names[stripped_field_name]}"
        else:
            seen_field_names[stripped_field_name] = 0
            unique_field_name = stripped_field_name
        
        # Check if any specified columns need input (don't match the pattern)
        def check_needs_input(sheet, row, check_col_indices):
            """Check if any specified columns need input based on pattern matching"""
            pattern = r'[A-Z]+\d+'
            
            for col_idx in check_col_indices:
                cell = sheet.cell(row=row, column=col_idx)
                cell_value = str(cell.value or '')
                
                if not re.findall(pattern, cell_value):
                    return True  # needs_input = True
            
            return False  # needs_input = False
        needs_input = check_needs_input(sheet, row, check_col_indices)

        # needs_input = any(
        #     # sheet.cell(row=row, column=col_idx).value is None and
        #     sheet.cell(row=row, column=col_idx).data_type != 'f'
        #     for col_idx in check_col_indices
        # )
        
        full_field_name = f"{indent}{unique_field_name}"
        if needs_input:
            fields_to_fill.append(full_field_name)
        
        markdown_rows.append(f"| {full_field_name} |" if needs_input else "| |")
    
    # Early return if no fields need filling
    if not fields_to_fill:
        return "No fields need to be filled."
    
    # Build markdown table efficiently
    markdown_table = "\n".join(markdown_rows)
    df = markdown_to_df(markdown_table)
    df = remove_trailing_empty_rows(df)
    
    # Use f-string for cleaner formatting
    return f"""{{
    "searching_summary": '''{searching_summary}''',
    "fiscal_year": '''{fiscal_year}''',
    "input_searching_infor": '''{df.fillna('').to_markdown(index=False)}''',
    "period_header_row": {period_header_row},
    "component_company": '''{component_company}''',
    "component_sheet": '''{component_sheet}''',
    "required_unit": '''{required_unit}''',
}}"""

############# Agent Functions
@tool
def delete_excel_columns(columns_to_delete, state: Annotated[dict, InjectedState]):
    """
    Delete multiple columns from a sheet of an Excel file using Excel-style column letters.

    This function removes the specified columns from the Excel sheet. Columns should be specified as a list of letters
    (e.g., ['D', 'I', 'J']). The function updates the file in place.

    Args:
        columns_to_delete (list of str): A list of Excel column letters to delete (e.g., ['D', 'I', 'J']).
    """    
    # Load the workbook and select the sheet
    ws = state['worksheet']
    
    # Convert column letters to indices and sort in descending order
    col_indices = [column_index_from_string(col) for col in columns_to_delete]
    col_indices.sort(reverse=True)
    
    # Delete columns from right to left to avoid shifting issues
    for col_idx in col_indices:
        ws.delete_cols(col_idx)
    
    # # Save the modified workbook
    # wb.save(excel_file_path)
    
    return f"Deleted columns {', '.join(columns_to_delete)} from {state['sheet_name']}"

@tool
def add_columns(start_column, new_column_names, state: Annotated[dict, InjectedState]):
    """
    Add multiple columns with specified names to a specific row in an Excel sheet using openpyxl,
    preserving row formatting for the newly added columns.
    
    Parameters:
    start_column (str): Excel column letter where new columns will be inserted (e.g., 'D').
    new_column_names (list): List of new column names to be added.
    
    Returns:
    None (Modifies the Excel file and saves it)
    """
    ws = state['worksheet']
    column_name_row = state['period_header_row']
    num_add_column = len(new_column_names)
    start_idx = column_index_from_string(start_column)
    
    if start_idx < 1 or column_name_row < 1:
        raise ValueError("start_column and start_row must be 1-based and positive")
    
    max_row = ws.max_row
    max_col = ws.max_column
    
    # Reference column for copying formatting and formulas (use the column just AFTER start_column)
    # This will be the column that gets shifted to the right after insertion
    ref_column_idx = start_idx
    ref_column_letter = get_column_letter(ref_column_idx)
    
    # Store formatting and formulas from the reference column BEFORE insertion
    ref_column_data = {}
    for row_idx in range(1, max_row + 1):
        ref_cell = ws[f"{ref_column_letter}{row_idx}"]
        ref_column_data[row_idx] = {
            'value': ref_cell.value,
            'has_style': ref_cell.has_style,
            'font': copy(ref_cell.font) if ref_cell.has_style else None,
            'fill': copy(ref_cell.fill) if ref_cell.has_style else None,
            'border': copy(ref_cell.border) if ref_cell.has_style else None,
            'alignment': copy(ref_cell.alignment) if ref_cell.has_style else None,
            'number_format': copy(ref_cell.number_format) if ref_cell.has_style else None
        }
    
    # Store formulas from all columns that will be shifted (for later updating)
    original_formulas = {}
    for col_idx in range(start_idx, max_col + 1):
        col_letter = get_column_letter(col_idx)
        for row_idx in range(1, max_row + 1):
            cell = ws[f"{col_letter}{row_idx}"]
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                original_formulas[f"{col_letter}{row_idx}"] = cell.value
    
    # Insert all columns at once - more efficient than individual inserts
    ws.insert_cols(start_idx, num_add_column)
    
    # Pre-calculate column letters for new columns
    new_column_letters = [get_column_letter(start_idx + i) for i in range(num_add_column)]
    
    # Set column names for new columns
    for i, (name, column_letter) in enumerate(zip(new_column_names, new_column_letters)):
        target_cell = ws[f"{column_letter}{column_name_row}"]
        target_cell.value = name
    
    # Copy formatting AND formulas from reference column to all new columns for ALL rows
    for row_idx in range(1, max_row + 1):
        ref_data = ref_column_data[row_idx]
        for i, column_letter in enumerate(new_column_letters):
            target_cell = ws[f"{column_letter}{row_idx}"]
            
            # Copy formatting if reference cell had styling
            if ref_data['has_style']:
                target_cell.font = ref_data['font']
                target_cell.fill = ref_data['fill']
                target_cell.border = ref_data['border']
                target_cell.alignment = ref_data['alignment']
                target_cell.number_format = ref_data['number_format']
            
            # Copy and adjust formula from reference column (skip header row for formulas)
            if (row_idx != column_name_row and 
                ref_data['value'] and 
                isinstance(ref_data['value'], str) and 
                ref_data['value'].startswith('=')):
                # Adjust formula to point to the correct column
                # The reference column is now at position ref_column_idx + num_add_column
                adjusted_formula = adjust_formula_for_new_column(
                    ref_data['value'], start_idx, i, start_idx + i
                )
                target_cell.value = adjusted_formula
    
    # Update formulas in all columns that were shifted to the right
    update_formulas_after_insertion(ws, start_idx, num_add_column, max_row, original_formulas)
    
    return "Success"

def copy_cell_style(source_cell, target_cell):
    """Helper function to copy cell styling efficiently"""
    target_cell.font = copy(source_cell.font)
    target_cell.fill = copy(source_cell.fill)
    target_cell.border = copy(source_cell.border)
    target_cell.alignment = copy(source_cell.alignment)
    target_cell.number_format = copy(source_cell.number_format)

def adjust_formula_for_new_column(formula, insertion_start_idx, num_inserted_cols, new_col_idx):
    """
    Adjust formula from reference column to work correctly in new column position
    This function properly handles the shift in column references caused by insertion
    """
    if not formula.startswith('='):
        return formula
    
    # Compile regex pattern for cell references (handles both relative and absolute references)
    cell_ref_pattern = re.compile(r'\$?[A-Z]+\$?[0-9]+')
    
    def replace_cell_reference(match):
        cell_ref = match.group(0)
        
        # Handle absolute column references ($A$1) and mixed references ($A1, A$1)
        is_col_absolute = cell_ref.startswith('$')
        
        # Extract column letter and row number, handling $ signs
        if is_col_absolute:
            # Find the end of column part (before row number or second $)
            col_end = next((i for i, c in enumerate(cell_ref[1:], 1) if c.isdigit() or c == '$'), len(cell_ref))
            if cell_ref[col_end:col_end+1] == '$':
                col_letter = cell_ref[1:col_end]  # Skip first $
                row_num = cell_ref[col_end:]      # Include $ before row number
            else:
                col_letter = cell_ref[1:col_end]  # Skip first $
                row_num = cell_ref[col_end:]      # Just the row number
        else:
            # Find where digits start
            col_end = next((i for i, c in enumerate(cell_ref) if c.isdigit() or c == '$'), len(cell_ref))
            col_letter = cell_ref[:col_end]
            row_num = cell_ref[col_end:]
        
        try:
            col_num = column_index_from_string(col_letter)
            
            # Update column references that are at or after the insertion point
            if col_num >= insertion_start_idx:
                # Shift the column reference by the number of inserted columns
                new_col_num = col_num + num_inserted_cols
                new_col_letter = get_column_letter(new_col_num)
                
                # Reconstruct the reference maintaining absolute/relative format
                if is_col_absolute:
                    return f"${new_col_letter}{row_num}"
                else:
                    return f"{new_col_letter}{row_num}"
            
            return cell_ref  # Keep references to columns before insertion point unchanged
            
        except:
            return cell_ref  # Return original if parsing fails
    
    return cell_ref_pattern.sub(replace_cell_reference, formula)

def update_formulas_after_insertion(ws, start_idx, num_add_column, max_row, original_formulas):
    """
    Update formulas in columns that were shifted to the right after insertion
    """
    # Compile regex pattern once for better performance
    cell_ref_pattern = re.compile(r'\$?[A-Z]+\$?[0-9]+')
    
    def update_formula(formula):
        if not formula.startswith('='):
            return formula
        
        def replace_cell_reference(match):
            cell_ref = match.group(0)
            
            # Handle absolute column references ($A$1) and mixed references ($A1, A$1)
            is_col_absolute = cell_ref.startswith('$')
            
            # Extract column letter and row number, handling $ signs
            if is_col_absolute:
                col_end = next((i for i, c in enumerate(cell_ref[1:], 1) if c.isdigit() or c == '$'), len(cell_ref))
                if cell_ref[col_end:col_end+1] == '$':
                    col_letter = cell_ref[1:col_end]
                    row_num = cell_ref[col_end:]
                else:
                    col_letter = cell_ref[1:col_end]
                    row_num = cell_ref[col_end:]
            else:
                col_end = next((i for i, c in enumerate(cell_ref) if c.isdigit() or c == '$'), len(cell_ref))
                col_letter = cell_ref[:col_end]
                row_num = cell_ref[col_end:]
            
            try:
                col_num = column_index_from_string(col_letter)
                # Update references to columns that were at or after the insertion point
                if col_num >= start_idx:
                    new_col_num = col_num + num_add_column
                    new_col_letter = get_column_letter(new_col_num)
                    
                    # Reconstruct the reference maintaining absolute/relative format
                    if is_col_absolute:
                        return f"${new_col_letter}{row_num}"
                    else:
                        return f"{new_col_letter}{row_num}"
            except:
                pass
            return cell_ref
        
        return cell_ref_pattern.sub(replace_cell_reference, formula)
    
    # Update formulas in shifted columns
    for original_cell_ref, original_formula in original_formulas.items():
        # Parse original cell reference
        col_end = next((i for i, c in enumerate(original_cell_ref) if c.isdigit()), len(original_cell_ref))
        col_letter = original_cell_ref[:col_end]
        row_num = original_cell_ref[col_end:]
        
        try:
            original_col_num = column_index_from_string(col_letter)
            # Calculate new position after insertion
            new_col_num = original_col_num + num_add_column
            new_col_letter = get_column_letter(new_col_num)
            new_cell_ref = f"{new_col_letter}{row_num}"
            
            # Update the formula and assign to new cell
            updated_formula = update_formula(original_formula)
            ws[new_cell_ref].value = updated_formula
        except:
            continue  # Skip if there's an error parsing

@tool
def update_yoy_column(yoy_column, new_column_names, state: Annotated[dict, InjectedState]):
    """
    Insert multiple new columns before a specified YoY (Year-over-Year) column in the template_excel_file,
    copy content and formulas from the previous column, update formulas in both the new columns
    and the YoY column to reference the correct columns, and set the new columns' headers.

    This function operates on a specific sheet of the template_excel_file. It takes a YoY column letter and new column names.
    It inserts the specified number of columns before the YoY column, copies values and formulas
    from the column immediately before each new column, updates formulas in both the new columns
    and the YoY column starting under the timestamp row, and sets the new columns' headers.

    Args:
        yoy_column (str): Excel column letter for the YoY column (e.g., 'G').
        new_column_names (list of str): List of header names for the new columns (e.g., ['2024', '2025']).
    """
    sheet = state['worksheet']
    column_name_row = state['period_header_row']
    num_add_column = len(new_column_names) 
    # # Input validation
    # if len(new_column_names) != num_add_column:
    #     raise ValueError("The number of new column names must match num_add_column.")
    
    # Get the column index for the YoY column
    yoy_col_idx = column_index_from_string(yoy_column)
    
    # Insert all columns at once - much more efficient
    sheet.insert_cols(idx=yoy_col_idx, amount=num_add_column)
    
    # Pre-calculate all column information to avoid repeated calculations
    new_yoy_col = get_column_letter(yoy_col_idx + num_add_column)
    max_row = sheet.max_row
    
    # Pre-calculate column mappings for all new columns
    column_mappings = []
    for i in range(num_add_column):
        new_col_idx = yoy_col_idx + i
        new_col = get_column_letter(new_col_idx)
        source_col = get_column_letter(new_col_idx - 1)
        
        column_mappings.append({
            'shift_num': i + 1,
            'new_col': new_col,
            'source_col': source_col,
            'header_name': new_column_names[i]
        })
    
    # Process all new columns efficiently
    _process_new_columns_batch(sheet, column_mappings, column_name_row, max_row)
    
    # Update YoY column formulas
    _update_yoy_formulas(sheet, new_yoy_col, num_add_column, column_name_row, max_row)
    
    # Update all other formulas that reference shifted columns
    _update_shifted_formulas_optimized(sheet, yoy_col_idx, num_add_column, max_row)
    
    return "Success"

def _process_new_columns_batch(sheet, column_mappings, column_name_row, max_row):
    """Efficiently process all new columns with batch operations"""
    # Process data rows first (batch by row for better cache locality)
    for row_idx in range(column_name_row + 1, max_row + 1):
        for mapping in column_mappings:
            source_cell = sheet[f"{mapping['source_col']}{row_idx}"]
            new_cell = sheet[f"{mapping['new_col']}{row_idx}"]
            
            # # Copy value
            # new_cell.value = source_cell.value
            
            # Update formula if needed
            # print("source_cell.data_type:", source_cell.data_type)
            if source_cell.value and isinstance(source_cell.value, str) and source_cell.data_type == 'f':
                pattern = r'[A-Z]+\d+'
                formula = source_cell.value
                references = re.findall(pattern, formula)
                # print("references:", references)
                if references:
                    new_cell.value = shift_column_in_formula(source_cell.value, 1) # mapping['shift_num'])
                    # print("new_cell.value:", new_cell.value)

            # Copy formatting efficiently
            if source_cell.has_style:
                _copy_cell_style_complete(source_cell, new_cell)
    
    # Set headers for all new columns
    header_font = Font(name="Arial", size=12, bold=True)
    for mapping in column_mappings:
        header_cell = sheet[f"{mapping['new_col']}{column_name_row}"]
        header_cell.value = mapping['header_name']
        header_cell.font = header_font

def _update_yoy_formulas(sheet, new_yoy_col, num_add_column, column_name_row, max_row):
    """Efficiently update YoY column formulas"""
    
    for row_idx in range(column_name_row + 1, max_row + 1):
        yoy_cell = sheet[f'{new_yoy_col}{row_idx}']
        if (yoy_cell.value and isinstance(yoy_cell.value, str) 
            and yoy_cell.value.startswith('=')):
            yoy_cell.value = shift_column_in_formula(yoy_cell.value, num_add_column)


def _update_shifted_formulas_optimized(sheet, yoy_col_idx, num_add_column, max_row):
    """Optimized formula updating for shifted columns"""
    # Compile regex once for better performance
    insert_point = yoy_col_idx + num_add_column + 1
        
    # Only process cells from the insertion point onwards
    for row in sheet.iter_rows(min_row=1, max_row=max_row, min_col=insert_point):
        for cell in row:
            if (cell.value and isinstance(cell.value, str) 
                and cell.value.startswith('=')):
                cell.value = shift_column_in_formula(cell.value, num_add_column)


def _copy_cell_style_complete(source_cell, target_cell):
    """Efficiently copy complete cell styling"""
    # Use copy() for complex objects to avoid manual reconstruction
    target_cell.font = copy(source_cell.font)
    target_cell.fill = copy(source_cell.fill)
    target_cell.border = copy(source_cell.border)
    target_cell.alignment = copy(source_cell.alignment)
    target_cell.number_format = source_cell.number_format
    target_cell.protection = copy(source_cell.protection)

def shift_column_in_formula(formula, shift_amount):
    """
    Shift column references in a formula by a specific number.
    
    Args:
        formula: The formula string (e.g., "=A1+B2")
        shift_amount: Number of columns to shift (positive = right, negative = left)
    
    Returns:
        Modified formula with shifted column references
    """
    # Pattern to match cell references (e.g., A1, $B$2, C$3, $D4)
    pattern = r'(\$?)([A-Z]+)(\$?)(\d+)'
    
    def replace_cell(match):
        col_abs = match.group(1)  # $ before column
        col_letter = match.group(2)  # Column letter
        row_abs = match.group(3)  # $ before row
        row_num = match.group(4)  # Row number
        
        # Convert column letter to index
        col_idx = column_index_from_string(col_letter)
        
        # Shift the column
        new_col_idx = col_idx + shift_amount
        
        # Ensure column index is valid (at least 1)
        if new_col_idx < 1:
            new_col_idx = 1
        
        # Convert back to letter
        new_col_letter = get_column_letter(new_col_idx)
        
        # Reconstruct the cell reference
        return f"{col_abs}{new_col_letter}{row_abs}{row_num}"
    
    # Replace all cell references in the formula
    new_formula = re.sub(pattern, replace_cell, formula)
    return new_formula

@tool
def write_df_column_to_excel(column_names, start_cols, state: Annotated[dict, InjectedState]):
    """
    Write multiple columns from a result_df to specific columns and rows in a sheet of the template_excel_file.

    This function takes a list of result_df column names and writes their values to the specified template_excel_file columns. 
    The result_df column_names should be exact (e.g., ['FY2022', 'FY2023', 'FY2024']) and match the meaning of start_cols.
    The Excel columns should be specified as a list of letters (e.g., ['D', 'E', 'F']).

    Args:
        column_names (list of str): The DataFrame column names to write to Excel.
        start_cols (list of str): Excel-style column letters to write each DataFrame column into.
    """
    df = state['result_df']
    confidence_df = state['confidence_df']
    start_row = state['period_header_row'] + 1
    
    # Input validation and filtering
    if len(column_names) != len(start_cols):
        min_leng = min(len(column_names), len(start_cols))
        column_names = column_names[:min_leng]
        start_cols = start_cols[:min_leng]
    
    # Filter to only existing columns
    matched_pairs = [(col, start_col) for col, start_col in zip(column_names, start_cols) if col in df.columns]
    if not matched_pairs:
        return "Success"  # No valid columns to process
    
    column_names, start_cols = zip(*matched_pairs)
    sheet = state['worksheet']
    
    # Pre-create yellow fill pattern
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    
    # Pre-calculate column information to avoid repeated conversions
    column_info = []
    for column_name, start_col in zip(column_names, start_cols):
        col_letter = start_col.upper()
        column_info.append((column_name, col_letter))
    
    # Batch process by row instead of by column for better cache locality
    df_len = len(df)
    confidence_threshold = 0.02
    
    for row_offset in range(df_len):
        excel_row = start_row + row_offset
        
        # Check if row is empty once per row
        row_is_empty = is_row_empty_except_one_cell(sheet, excel_row)
        if row_is_empty:
            continue
            
        for column_name, col_letter in column_info:
            cell = sheet[f"{col_letter}{excel_row}"]
            
            # Skip formula cells
            if cell.data_type == 'f':
                continue
                
            # Get and convert value
            original_value = df.loc[df.index[row_offset], column_name]
            converted_value = convert_to_number(original_value)
            if cell.value is None: 
                EXCLUDED_VALUES = {'–', '-', '*'}
                if converted_value not in EXCLUDED_VALUES:
                    cell.value = converted_value
                    
                    # Apply highlighting if confidence is low
                    confidence_value = confidence_df.iloc[row_offset][column_name]
                    if confidence_value < confidence_threshold:
                        cell.fill = yellow_fill
    
    return "Success"
