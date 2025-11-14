from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter

from .tools import AzureSearchResult
from .structure_output import FillInValues
from auto_report.agent.utils.util_function import markdown_to_df

def format_search_result(search_result: AzureSearchResult) -> str:
    return "\n\n---\n\n".join(
        f"- Table:{res["content"]}\n\n- Document: {res["filename"]}\n- Page: {res["page"]}"
        for res in search_result
    )


def retrieving_tables(search_result: AzureSearchResult): 
    retrieval_tables = []
    for search_dict in search_result:
        try:
            retrieval_tables.append(markdown_to_df(search_dict["content"]))
        except:
            continue
    retrieval_tables = [df.set_index(list(df.columns)[0]) for df in retrieval_tables]
    
    return retrieval_tables
    # return [markdown_to_df(df["content"]).set_index('0') for df in search_result]


def format_fillin_values(fill_in_values: FillInValues) -> str:
    return "\n\t-".join(
        f"Value: {value.result.final_result.value}; Row field: {value.row_field}; Column field: {value.col_field}"
        for value in fill_in_values.values
    )


def worksheet_to_string(
    ws: Worksheet, max_col_width: int = 100, treat_first_row_as_header: bool = True
) -> str:
    """
    Convert Excel sheet to a beautifully formatted table, expanding merged cells.
    Always includes row and column indices for reference.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str): Name of the sheet to convert
        max_col_width (int): Maximum width for each column
        treat_first_row_as_header (bool): Whether to treat first row as headers
    
    Returns:
        str: Beautifully formatted table representation with row/column indices
    """
    # Convert to list of lists
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(list(row))
    
    if not data:
        return "Empty sheet"
    
    # Handle merged cells by expanding them
    merged_ranges = list(ws.merged_cells.ranges)
    for merged_range in merged_ranges:
        # Get the value from the top-left cell
        top_left_value = ws.cell(merged_range.min_row, merged_range.min_col).value
        
        # Fill all cells in the merged range with this value
        for row in range(merged_range.min_row - 1, merged_range.max_row):
            for col in range(merged_range.min_col - 1, merged_range.max_col):
                if row < len(data) and col < len(data[row]):
                    data[row][col] = top_left_value
    
    if not data:
        return "No data found"
    
    # Ensure all rows have the same length
    max_cols = max(len(row) for row in data) if data else 0
    for row in data:
        while len(row) < max_cols:
            row.append("")
    
    # Convert all cells to strings and handle None values
    formatted_data = []
    for row in data:
        formatted_row = []
        for cell in row:
            if cell is None:
                formatted_row.append("")
            else:
                cell_str = str(cell).strip()
                # Truncate if too long
                if len(cell_str) > max_col_width:
                    cell_str = cell_str[:max_col_width-3] + "..."
                formatted_row.append(cell_str)
        formatted_data.append(formatted_row)
    
    if not formatted_data:
        return "No data to display"
    
    # Calculate column widths for data columns
    col_widths = []
    for col_idx in range(max_cols):
        max_width = 0
        for row in formatted_data:
            if col_idx < len(row):
                max_width = max(max_width, len(row[col_idx]))
        # Ensure minimum width and respect maximum
        col_widths.append(min(max(max_width, 3), max_col_width))
    
    # Build the table
    result = []
    
    # Add sheet info
    result.append(f"Sheet: {ws.title}")
    if merged_ranges:
        result.append(f"(Contains {len(merged_ranges)} merged cell range(s) - expanded)")
    result.append("")
    
    # Create header row with column indices
    header_row = "| Row |"
    separator_row = "|-----|"
    
    # Add column headers (Excel column letters)
    for col_idx in range(max_cols):
        col_letter = get_column_letter(col_idx + 1)
        width = col_widths[col_idx]
        # Make sure column header fits
        header_width = max(width, len(col_letter))
        col_widths[col_idx] = header_width  # Update width if needed
        header_row += f" {col_letter:^{header_width}} |"
        separator_row += "-" * (header_width + 2) + "|"
    
    result.append(header_row)
    result.append(separator_row)
    
    # If treating first row as header, add a special header data row
    if treat_first_row_as_header and formatted_data:
        header_data_row = "| HDR |"  # Header row indicator
        for col_idx, header_value in enumerate(formatted_data[0]):
            width = col_widths[col_idx]
            # Make header value bold or distinctive
            header_display = f"**{header_value}**" if header_value else ""
            if len(header_display) > width:
                header_display = header_display[:width-3] + "..."
            header_data_row += f" {header_display:<{width}} |"
        result.append(header_data_row)
        
        # Add separator after header
        separator_row2 = "|-----|"
        for col_idx in range(max_cols):
            width = col_widths[col_idx]
            separator_row2 += "=" * (width + 2) + "|"
        result.append(separator_row2)
        
        # Data rows start from index 1
        data_start_idx = 1
        row_offset = 2  # Since we have header row, actual Excel row 2 starts our data
    else:
        # Data rows start from index 0
        data_start_idx = 0
        row_offset = 1  # Excel rows start from 1
    
    # Add data rows with row indices
    for row_idx in range(data_start_idx, len(formatted_data)):
        row_data = formatted_data[row_idx]
        excel_row_num = row_idx + row_offset
        
        # Include Excel row number
        table_row = f"| {excel_row_num:3d} |"
        
        for col_idx, cell_value in enumerate(row_data):
            width = col_widths[col_idx]
            table_row += f" {cell_value:<{width}} |"
        
        result.append(table_row)
    
    return "\n".join(result)
