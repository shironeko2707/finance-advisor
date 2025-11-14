import re
import io
import pandas as pd
from typing import List, Dict, Any
import openpyxl
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from decimal import Decimal, InvalidOperation
from openpyxl.styles.numbers import builtin_format_code
import datetime
from openpyxl.utils import column_index_from_string, get_column_letter

def convert_to_number(value):
    """
    Convert a cell value to a number, handling various formats.
    Returns the original value if conversion fails.
    """
    if value is None:
        return value
    
    # If already a number, return as is
    if isinstance(value, (int, float)):
        return value
    
    # Convert to string for processing
    str_value = str(value).strip()
    
    # Empty string case
    if not str_value:
        return value
    
    try:
        # Remove whitespace
        cleaned = str_value.strip()
        
        # Handle parentheses for negative numbers: (123) -> -123
        is_negative = False
        if cleaned.startswith('(') and cleaned.endswith(')'):
            is_negative = True
            cleaned = cleaned[1:-1].strip()
        
        # Remove commas (thousand separators)
        cleaned = cleaned.replace(',', '')
        
        # Remove currency symbols and other common characters
        cleaned = re.sub(r'[$€£¥%]', '', cleaned)
        
        # Handle percentage (convert to decimal)
        if '%' in str_value:
            cleaned = cleaned.replace('%', '')
            if cleaned:
                number = float(cleaned) / 100
                return -number if is_negative else number
        
        # Try to convert to number
        if cleaned:
            # Try integer first
            if '.' not in cleaned and 'e' not in cleaned.lower():
                try:
                    number = int(cleaned)
                    return -number if is_negative else number
                except ValueError:
                    pass
            
            # Try float
            try:
                number = float(cleaned)
                return -number if is_negative else number
            except ValueError:
                pass
            
            # Try using Decimal for high precision
            try:
                number = float(Decimal(cleaned))
                return -number if is_negative else number
            except (InvalidOperation, ValueError):
                pass
    
    except Exception:
        pass
    
    # If all conversions fail, return original value
    return value

def remove_trailing_empty_rows(df):
    # Check for rows that are completely empty or contain only whitespace
    mask = df.apply(lambda row: row.isna().all(), axis=1)
    
    # Find the last non-empty row index
    last_valid_index = mask[::-1].idxmin()
    
    # Slice the DataFrame up to the last valid row
    return df.loc[:last_valid_index]

def merge_template_format(result_markdown, searching_template, field_name):
    local_result_df = markdown_to_df(result_markdown)
    searching_template = markdown_to_df(searching_template)

    for i, row in local_result_df.iterrows():
        writing_index = searching_template.index[searching_template[field_name] == row[field_name]].tolist()
        searching_template.loc[writing_index, local_result_df.columns] = row[local_result_df.columns].values
    
    return searching_template # .fillna('').to_markdown(index=False)

def is_row_empty_except_one_cell(ws, row_num):
    # Get the row
    row = ws[row_num]
    # Count non-empty cells (cells with value not None or not empty string)
    non_empty_count = sum(1 for cell in row if cell.value is not None and str(cell.value).strip() != "")
    
    # Return True if exactly one cell has a value
    return non_empty_count == 1

def is_currency_string(value):
    # Check if the value is a string that matches currency format like "$1,234.56", "$(295)", "$ 19,543", "$ 6,303*", or "$ 1,511**"
    if isinstance(value, str):
        return bool(re.match(r'^\$?-?\s*\(?[\d,]+(?:\.\d+)?\)?[\*]*$', value))
    return False

def convert_currency_to_number(value):
    # Remove dollar sign, spaces, commas, parentheses, and asterisks, convert to float
    if isinstance(value, str):
        # Check if it's a negative number in parentheses, e.g., "$(295)"
        is_negative = value.startswith('$(') and value.endswith(')')
        # Clean the value: remove $, spaces, commas, parentheses, and asterisks
        cleaned_value = value.replace('$', '').replace(' ', '').replace(',', '').replace('(', '').replace(')', '').replace('*', '')
        try:
            number = float(cleaned_value)
            # Apply negative sign if parentheses were used
            return -number if is_negative else number
        except ValueError:
            return value  # Return original value if conversion fails
    return value

def remove_leading_tool_messages(messages):
    result = messages[:]
    while result and isinstance(result[0], ToolMessage):
        result.pop(0)
    return result

def template_to_markdown(sheet): # template_path, sheet_name):
    # # Load workbook without evaluating formulas
    # wb = openpyxl.load_workbook(template_path, data_only=False)
    # sheet = wb[sheet_name]

    # Extract cell values preserving display format
    data = []
    for row in sheet.iter_rows(values_only=False):
        row_data = []
        for cell in row:
            if cell.value is None:
                row_data.append(None)
            elif hasattr(cell, 'displayed_value') and cell.displayed_value is not None:
                # Use displayed_value if available (preserves formatting)
                row_data.append(cell.displayed_value)
            elif hasattr(cell, 'number_format') and cell.number_format != 'General':
                # For formatted numbers/dates, try to preserve the format
                try:                    
                    # Handle date formatting specifically
                    if isinstance(cell.value, datetime.datetime) or isinstance(cell.value, datetime.date):
                        # Common date formats
                        if 'mmm' in cell.number_format.lower() and 'yy' in cell.number_format.lower():
                            # Format like "Jan-24"
                            row_data.append(cell.value.strftime('%b-%y'))
                        elif 'mmm' in cell.number_format.lower():
                            row_data.append(cell.value.strftime('%b-%Y'))
                        else:
                            # Use the cell's display format or fallback
                            row_data.append(str(cell.value))
                    else:
                        # For other formatted numbers, preserve as string
                        row_data.append(str(cell.value))
                except:
                    row_data.append(cell.value)
            else:
                row_data.append(cell.value)
        data.append(row_data)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df = excel_indices(df)
    df = trim_trailing_nans(df)
    df = df.map(lambda x: '' if str(x) == "NaT" else x)

    # # Optional: use first row as headers if your Excel file has them
    # df.columns = df.iloc[0]  # First row as header
    # df = df[1:]              # Drop header row from data

    return df.fillna("").to_markdown()

def file_category_router(sheet_name):
    if 'bi-weekly' in sheet_name.lower():
        return "Bi weekly stock update"
    if 'CPF' in sheet_name:
        return "CPF"
    if 'hotel' in sheet_name.lower():
        return "Hotel statistics"
    if 'indicators' in sheet_name.lower() or 'index' in sheet_name.lower():
        return "Monthly Econ results"

def trim_trailing_nans(df):
    # Find last row with at least one non-NaN
    last_valid_row = df.apply(lambda row: row.notna().any(), axis=1)[::-1].idxmax()
    df = df.loc[:last_valid_row]

    # Find last column with at least one non-NaN
    last_valid_col = df.apply(lambda col: col.notna().any(), axis=0)[::-1].idxmax()
    df = df.loc[:, :last_valid_col]

    return df

def get_excel_col_label(n):
    """Convert a zero-based column index to Excel-style label."""
    label = ""
    while n >= 0:
        label = chr(n % 26 + ord('A')) + label
        n = n // 26 - 1
    return label

def excel_indices(df):
    # Map numeric column indices to Excel-style letters
    df.columns = [get_excel_col_label(i) for i in range(len(df.columns))]

    # Map numeric row indices to Excel-style numbers (starting from 1)
    df.index = [i + 1 for i in range(len(df))]

    return df

def clean_markdown_header(markdown_table):
    markdown_table = markdown_table.replace("\n:selected:", "")
    try:
        header_index = markdown_table.index("| --- ")
        new_header = markdown_table[:header_index].replace('\n', '')
        return new_header + '\n' + markdown_table[header_index:]
    except:
        return markdown_table

def markdown_to_df(markdown_str):
    """
    Convert a Markdown table string back to a pandas DataFrame, handling separator rows.
    
    Args:
        markdown_str (str): Markdown table string
        
    Returns:
        pandas.DataFrame: Reconstructed DataFrame
    """
    # Clean markdown header if needed
    markdown_str = clean_markdown_header(markdown_str)

    # Split the markdown string into lines
    lines = markdown_str.strip().split('\n')

    # Remove the separator row (second row with dashes)
    if len(lines) > 1 and re.match(r'^\s*\|([-:\s]+\|)+$', lines[1].strip()):
        lines.pop(1)  # Remove the separator row
    
    # Normalize rows to have consistent column count
    def normalize_table_rows(lines):
        """Normalize all rows to have the same number of columns"""
        if not lines:
            return lines
            
        # Find the maximum number of columns across all rows
        max_cols = 0
        processed_lines = []
        
        for line in lines:
            # Split by pipes
            parts = line.strip().split('|')
            
            # Remove empty parts at the beginning and end (from leading/trailing pipes)
            if len(parts) > 0 and parts[0].strip() == '':
                parts.pop(0)
            if len(parts) > 0 and parts[-1].strip() == '':
                parts.pop()
            
            # Keep track of max columns
            max_cols = max(max_cols, len(parts))
            processed_lines.append(parts)
        
        # Pad all rows to have the same number of columns
        normalized_lines = []
        for parts in processed_lines:
            # Pad with empty strings if needed
            while len(parts) < max_cols:
                parts.append('')
            
            # Reconstruct the line with proper pipe formatting
            # Add empty leading column to match pandas read_csv behavior
            normalized_line = '|' + '|'.join(parts) + '|'
            normalized_lines.append(normalized_line)
        
        return normalized_lines
    
    # Apply normalization to all lines
    lines = normalize_table_rows(lines)
    
    # Join the remaining lines back into a string
    cleaned_markdown = '\n'.join(lines)

    # Use StringIO to read the markdown string as a file-like object
    df = pd.read_csv(io.StringIO(cleaned_markdown), sep='|', skipinitialspace=True)

    # Clean up the DataFrame
    df = df.dropna(axis=1, how='all')  # Remove empty columns
    df.columns = df.columns.str.strip()  # Remove whitespace from column names
    
    # Remove the first column if it's an empty index column
    if len(df.columns) > 0 and df.columns[0] == '':
        df = df.drop(columns=[''])
    
    # Make column names unique and clean up data values
    df.columns = make_unique_columns(df.columns)
    
    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()

    return df

def build_context(search_results: List[Dict[str, Any]]) -> str:
    """
    Build a formatted context from Milvus search results.
    
    Args:
        search_results: List of search result dictionaries from Milvus containing
                       'id', 'distance', and 'metadata' keys
    
    Returns:
        String containing formatted context from all chunks
    """
    # Format each chunk
    context_parts = []
    for i, result in enumerate(search_results):
        # Extract metadata and text
        metadata = result.get('metadata', {})
        chunk_id = metadata.get('chunk_id', 'Unknown')
        text = metadata.get('text', 'No text available')
        
        # Create header with chunk ID and similarity score
        header = f"CHUNK {i+1} (ID: {chunk_id}, similarity score: {1 - result['distance']:.4f})"
        
        # Add any additional metadata if available
        if 'page_num' in metadata:
            header += f", Page {metadata['page_num']}"
        if 'chunk_type' in metadata:
            header += f", {metadata['chunk_type']}"
            
        # Add the formatted chunk to context parts
        context_parts.append(f"{header}:\n{text}")
    
    # Join all parts with double newlines
    return "\n\n".join(context_parts)

def parse_only_table(text):
    """
    Extract markdown table from a long string and return it as clean markdown table text.
    
    Args:
        text (str): Input text containing markdown table
        
    Returns:
        str: Markdown table text, or None if no table found
    """
    lines = text.split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        # Check if line looks like a table row (contains |)
        if '|' in line:
            table_lines.append(line)
            in_table = True
        elif in_table:
            # If we were in a table and hit a non-table line, we're done
            break
    
    if not table_lines:
        return None
    
    # Clean up and reconstruct the table
    cleaned_lines = []
    for line in table_lines:
        # Keep the line as is, just strip whitespace
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines) if cleaned_lines else None

def make_index_unique(index):
    counts = {}
    new_index = []
    for label in index:
        if label in counts:
            counts[label] += 1
            new_index.append(f"{label}_{counts[label]}")
        else:
            counts[label] = 0
            new_index.append(label)
    return new_index

# Ensure column names are unique by appending a suffix if duplicates exist
def make_unique_columns(columns):
    seen = {}
    unique_columns = []
    for col in columns:
        if col in seen:
            seen[col] += 1
            unique_columns.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            unique_columns.append(col)
    return unique_columns

def excel_column_to_number(column):
    """Convert Excel column letter(s) to number (A=1, B=2, ..., Z=26, AA=27, etc.)"""
    result = 0
    for char in column.upper():
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

def get_column_sort_key(tool_call):
    """Extract column for sorting from tool call"""
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    # Handle __arg1 parameter mapping first
    if "__arg1" in tool_args.keys():
        try:
            new_tool_args = eval(tool_args['__arg1'])
        except:
            temp_tool_args = tool_args['__arg1'].split(',')
            if tool_name == 'update_yoy_column':
                new_tool_args = {
                    'yoy_column': temp_tool_args[0], 
                    "new_column_names": temp_tool_args[1], 
                }
            else:
                new_tool_args = {
                    'start_column': temp_tool_args[0], 
                    'new_column_names': temp_tool_args[1],
                }
    else:
        new_tool_args = tool_args
    
    # Get the column to sort by
    if tool_name == 'update_yoy_column' and 'yoy_column' in new_tool_args:
        column = new_tool_args['yoy_column'].strip()
    elif tool_name == 'add_columns' and 'start_column' in new_tool_args:
        column = new_tool_args['start_column'].strip()
    else:
        return float('inf')  # Put tools without sortable columns at the end
    
    return excel_column_to_number(column)

def extract_row_data(worksheet, row_index):
    """
    Extract non-empty cell values from a specific row in an Excel worksheet.
    
    Parameters:
    -----------
    worksheet : openpyxl.worksheet.worksheet.Worksheet
        The worksheet object to read from
    row_index : int
        The row index to extract data from (1-based indexing)
    
    Returns:
    --------
    list
        List of [value, column_index] pairs where value is formatted as string
        and column_index is 1-based
    """
    list_return = []
    
    # Get all cells in the specified row
    row_data = worksheet[row_index]
    
    for col_index, cell in enumerate(row_data, start=1):
        value = cell.value
        
        # Skip None/empty values
        if value is None:
            continue
        
        # Handle date formatting specifically
        if isinstance(cell.value, datetime.datetime) or isinstance(cell.value, datetime.date):
            # Common date formats
            if 'mmm' in cell.number_format.lower() and 'yy' in cell.number_format.lower():
                # Format like "Jan-24"
                processed_value = cell.value.strftime('%b-%y')
            elif 'mmm' in cell.number_format.lower():
                processed_value = cell.value.strftime('%b-%Y')
            else:
                # Use the cell's display format or fallback
                processed_value = str(cell.value)
        else:
            # For other formatted numbers, preserve as string
            processed_value = str(cell.value)
        
        # Store value with its column index (1-based)
        list_return.append([processed_value, col_index])
    
    return list_return

def get_next_available_index(current_index, taken_indexes):
    taken_set = set(taken_indexes)
    next_index = current_index
    while next_index in taken_set:
        next_index += 1
    return next_index

def sort_by_year(dates):
    def get_year_and_order(date_str):
        import re
        
        # Case 1: Year only (YYYY format)
        if re.match(r'^\d{4}$', date_str):
            year = int(date_str)
            return {'year': year, 'period_type': 0, 'period': 0, 'month': 0, 'day': 0}
        
        # Case 2: MM/DD/YYYY format
        if '/' in date_str:
            parts = date_str.split('/')
            year = int(parts[2])
            month = int(parts[0])
            day = int(parts[1])
            return {'year': year, 'period_type': 0, 'period': 0, 'month': month, 'day': day}
        
        # Case 3: DD-Mon-YY format (31-Dec-21)
        date_match = re.match(r'(\d{1,2})-(\w{3})-(\d{2})', date_str)
        if date_match:
            day = int(date_match.group(1))
            month_str = date_match.group(2)
            year_short = int(date_match.group(3))
            
            # Convert 2-digit year to 4-digit (assuming 2000s for now)
            year = 2000 + year_short
            
            # Convert month abbreviation to number
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = month_map.get(month_str, 0)
            
            return {'year': year, 'period_type': 0, 'period': 0, 'month': month, 'day': day}
        
        # Case 3b: Mon-YY format (Jun-24, Dec-23) - NEW
        month_year_match = re.match(r'^(\w{3})-(\d{2})$', date_str)
        if month_year_match:
            month_str = month_year_match.group(1)
            year_short = int(month_year_match.group(2))
            
            # Convert 2-digit year to 4-digit (assuming 2000s for now)
            year = 2000 + year_short
            
            # Convert month abbreviation to number
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = month_map.get(month_str, 0)
            
            return {'year': year, 'period_type': 0, 'period': 0, 'month': month, 'day': 0}
        
        # Case 4: FY format (FY2020 or FY 2020)
        fy_match = re.match(r'FY\s*(\d{4})', date_str)
        if fy_match:
            year = int(fy_match.group(1))
            return {'year': year, 'period_type': 1, 'period': 0, 'month': 0, 'day': 0}
        
        # Case 5: Quarter format (1Q2024 or 1Q 2024)
        quarter_match = re.match(r'(\d)Q\s*(\d{4})', date_str)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            return {'year': year, 'period_type': 2, 'period': quarter, 'month': 0, 'day': 0}
        
        # Case 6: Half-year format (1H2022 or 1H 2022)
        half_match = re.match(r'(\d)H\s*(\d{4})', date_str)
        if half_match:
            half = int(half_match.group(1))
            year = int(half_match.group(2))
            return {'year': year, 'period_type': 3, 'period': half, 'month': 0, 'day': 0}
        
        # Case 7: Month format (9M2023 or 9M 2023)
        month_match = re.match(r'(\d+)M\s*(\d{4})', date_str)
        if month_match:
            months = int(month_match.group(1))
            year = int(month_match.group(2))
            return {'year': year, 'period_type': 4, 'period': months, 'month': 0, 'day': 0}
        
        return {'year': 0, 'period_type': 0, 'period': 0, 'month': 0, 'day': 0}
    
    def sort_key(date_str):
        info = get_year_and_order(date_str)
        return (info['year'], info['period_type'], info['period'], info['month'], info['day'])
    
    return sorted(dates, key=sort_key)

def find_max_index_group(data):
    data_dict = data['Mapping']
    # Extract the Adding section
    taken_indexes = []
    for key in data['Groups'].keys():
        strings = data['Groups'][key]['periods']
        list_relative_index = []
        for s_index in range(len(strings)):
            if any(char.isdigit() for char in strings[s_index]):
                list_relative_index.append(s_index)
                
        taken_indexes.extend([data['Groups'][key]['indexes'][relative_index] for relative_index in list_relative_index])
    # print(taken_indexes)

    update_yoy_dict = {}

    for key in data_dict.keys():
        if data_dict[key]:
            if data_dict[key][1] in data['Groups'].keys():
                list_periods = data['Groups'][data_dict[key][1]]['periods']

                if data_dict[key][0] not in list_periods:
                    if data_dict[key][1] not in update_yoy_dict:
                        current_index = max(data['Groups'][data_dict[key][1]]['indexes']) + 1
                        update_yoy_dict[data_dict[key][1]] = {
                            'yoy_column': get_column_letter(get_next_available_index(current_index, taken_indexes)),
                            "new_column_names": [data_dict[key][0]],
                        }
                    else:
                        update_yoy_dict[data_dict[key][1]]['new_column_names'] = sort_by_year(update_yoy_dict[data_dict[key][1]]['new_column_names'] + [data_dict[key][0]])
           
    return update_yoy_dict 

def find_writing_column(data):
    data_dict = data['Mapping']
    # Extract the Adding section

    write_dict = {"column_names": [], "start_cols": []}

    for key in data_dict.keys():
        if data_dict[key]:
            if data_dict[key][1] in data['Groups'].keys():
                list_periods = data['Groups'][data_dict[key][1]]['periods']
                list_indexes = data['Groups'][data_dict[key][1]]['indexes']

                if data_dict[key][0] in list_periods:
                    period_index = list_periods.index(data_dict[key][0])
                    writing_index = get_column_letter(list_indexes[period_index])
                    write_dict['column_names'].append(key)
                    write_dict['start_cols'].append(writing_index)
                
    return write_dict

def to_minimal_markdown(df):
    """
    Convert DataFrame to markdown with absolute minimal spacing.
    No padding, just separators.
    """
    cols = df.columns.tolist()
    
    # Header
    header = '|' + '|'.join(str(col) for col in cols) + '|'
    
    # Separator
    separator = '|' + '|'.join('-' * len(str(col)) for col in cols) + '|'
    
    # Data rows
    rows = []
    for _, row in df.iterrows():
        row_str = '|' + '|'.join(str(val) for val in row) + '|'
        rows.append(row_str)
    
    markdown = '\n'.join([header, separator] + rows)
    return markdown

def template_to_markdown_example(sheet, start_row=1, start_col=1):
    """
    Convert Excel template to markdown starting from specific row and column.
    
    Args:
        template_path: Path to the Excel file
        sheet_name: Name of the sheet to process
        start_row: Starting row number (1-based index, default=1)
        start_col: Starting column number (1-based index, default=1)
    """
    # # Load workbook without evaluating formulas
    # wb = openpyxl.load_workbook(template_path, data_only=False)
    # sheet = wb[sheet_name]
    
    # Extract cell values preserving display format
    data = []
    for row_idx, row in enumerate(sheet.iter_rows(values_only=False), start=1):
        # Skip rows before start_row
        if row_idx < start_row:
            continue
            
        row_data = []
        for col_idx, cell in enumerate(row, start=1):
            # Skip columns before start_col
            if col_idx < start_col:
                continue
                
            if cell.value is None:
                row_data.append(None)
            elif hasattr(cell, 'displayed_value') and cell.displayed_value is not None:
                # Use displayed_value if available (preserves formatting)
                row_data.append(cell.displayed_value)
            elif hasattr(cell, 'number_format') and cell.number_format != 'General':
                # For formatted numbers/dates, try to preserve the format
                try:                    
                    # Handle date formatting specifically
                    if isinstance(cell.value, datetime.datetime) or isinstance(cell.value, datetime.date):
                        # Common date formats
                        if 'mmm' in cell.number_format.lower() and 'yy' in cell.number_format.lower():
                            # Format like "Jan-24"
                            row_data.append(cell.value.strftime('%b-%y'))
                        elif 'mmm' in cell.number_format.lower():
                            row_data.append(cell.value.strftime('%b-%Y'))
                        else:
                            # Use the cell's display format or fallback
                            row_data.append(str(cell.value))
                    else:
                        # For other formatted numbers, preserve as string
                        row_data.append(str(cell.value))
                except:
                    row_data.append(cell.value)
            else:
                row_data.append(cell.value)
        data.append(row_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df = excel_indices(df)
    df = trim_trailing_nans(df)
    df = df.map(lambda x: '' if str(x) == "NaT" else x)
    df.columns = df.loc[1,:]
    df = df.drop(1)
    
    return df.fillna("").to_markdown(index=False)
