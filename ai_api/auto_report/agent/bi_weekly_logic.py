import pandas as pd
import numpy as np
import re
from openpyxl.utils import column_index_from_string, get_column_letter
from langgraph.graph import StateGraph, START, END
import traceback
import sys

from auto_report.agent.utils.state import WorkflowState
from auto_report.agent.utils.nodes import (
    document_retrieval,
    extract_report,
    check_enough_information,
    check_enough_information_function,
    call_write_to_excel_write_df_column_to_excel_agent,
    write_to_excel_write_df_column_to_excel_node,
)

from auto_report.agent.utils.util_function import template_to_markdown, markdown_to_df, remove_trailing_empty_rows
import warnings

warnings.filterwarnings("ignore")  # This ignores all warnings


async def main_bi_weekly(state):
    try:
        # print("start bi-weekly")
        test_bi_weekly = template_to_markdown(state['worksheet'])
        # print("test_bi_weekly:", test_bi_weekly)

        test_md = get_bi_weekly_fill(test_bi_weekly)
        # print("test_md:", test_md)
        
        df = markdown_to_df_with_excel_index(test_md)
        # print("df.fillna('').to_markdown():", df.fillna('').to_markdown())

        # print("df.shape", df.shape)
        # Choose a row index (e.g., row 0)
        if df.shape[0] == 0:
            return state
            
        row = df.iloc[0]
        cleaned = row[~row.isin([''])]           # remove empty strings
        cleaned = cleaned[~cleaned.str.strip().eq('')]  # remove whitespace-only
        cleaned = cleaned.dropna()               # remove NaN
        unique_values = pd.unique(cleaned)
        # print("unique_values:", unique_values)

        # Define a subgraph for document retrieval and report extraction
        sub_workflow = StateGraph(WorkflowState)

        # Add only the desired nodes
        # Add nodes
        sub_workflow.add_node("document_retrieval", document_retrieval)
        sub_workflow.add_node("extract_report", extract_report)
        sub_workflow.add_node("check_enough_information", check_enough_information)
        sub_workflow.add_node("call_write_to_excel_write_df_column_to_excel_agent", call_write_to_excel_write_df_column_to_excel_agent)
        sub_workflow.add_node("write_to_excel_write_df_column_to_excel_node", write_to_excel_write_df_column_to_excel_node)

        # Define edges for the subgraph
        sub_workflow.add_edge(START, "document_retrieval")
        sub_workflow.add_edge("document_retrieval", "extract_report")
        sub_workflow.add_edge("extract_report", "check_enough_information")
        sub_workflow.add_conditional_edges(
            "check_enough_information",
            check_enough_information_function,
            {
                "call_write_to_excel_update_yoy_column_agent": "call_write_to_excel_write_df_column_to_excel_agent",
                "document_retrieval": "document_retrieval",
                END: END
            }
        )
        sub_workflow.add_edge("call_write_to_excel_write_df_column_to_excel_agent", "write_to_excel_write_df_column_to_excel_node")
        sub_workflow.add_edge("write_to_excel_write_df_column_to_excel_node", END)

        # Compile the subgraph
        sub_graph = sub_workflow.compile()

        i = 0
        results = []
        for test_company in unique_values:
            # test_company = "SHK Properties (HK$'m)"
            print("test_company:", test_company)
            report_template, period_list = process_by_company(df, test_company)
            # print("period_list:", period_list)
        
            dict_result = eval(get_fields_to_fill_dynamic(test_company, 54, [get_column_letter(3 + 4*i)],state['worksheet'], i+1))
            # print("dict_result:", dict_result)
            input_searching_infor = dict_result['input_searching_infor']
            input_searching_query = f"""
    Get the following information for these period {period_list} about "{dict_result['searching_summary']}" for the "{state['sheet_name']}" sheet and return them as a table:
    {remove_empty_rows_markdown(input_searching_infor)}
    """       
            state['input_searching_infor'] = input_searching_infor
            state['report_template'] = report_template
            state['category_router'] = "Bi-Weekly"
            state['input_searching_query'] = input_searching_query
            state['injected_state'] = {
                "worksheet": state['worksheet'],
                'data_starting_row': dict_result['data_starting_row'], 
            }
        
            # print("start invoke")
            # print("list(state.keys()):", list(state.keys()))
            result = await sub_graph.ainvoke(state)
            results.append(result)
            i += 1
        
        state['bi_weekly_results'] = results
        # state['processed_companies'] = len(results)

        return state
        
    except Exception as e:
        print("An error occurred:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        print("Traceback:")
        traceback.print_exc()

    
############################# util function
def remove_empty_rows_markdown(markdown_table):
    # Split the table into lines
    lines = markdown_table.strip().split('\n')
    
    # Keep header and separator rows, filter out empty data rows
    cleaned_lines = []
    for i, line in enumerate(lines):
        # Keep header (first row) and separator (second row)
        if i < 2:
            cleaned_lines.append(line)
            continue
        # Check if row is empty (contains only pipes and whitespace)
        if line.strip().replace('|', '').strip() == '':
            continue
        cleaned_lines.append(line)
    
    # Join lines back together
    return '\n'.join(cleaned_lines)

def get_fields_to_fill_dynamic(searching_summary, data_starting_row, check_column, sheet, number):
    # sheet = state['worksheet']  # Replace with your actual sheet name
    
    # Pre-convert column letters to indices for efficiency
    check_col_indices = [column_index_from_string(col) for col in check_column]
    first_check_col = 3 # min(check_col_indices)  # Get the first check column index

    fields_to_fill = []
    markdown_rows = ["| Field Name |", "|------------|"]
    seen_field_names = {}
    
    # Optimize row iteration - get actual data range instead of max_row
    max_data_row = min(sheet.max_row, data_starting_row + 1000)  # Reasonable limit
    
    for row in range(data_starting_row, max_data_row + 1):
        # field_cell = sheet.cell(row=row, column=2)  # Column B
        # field_name = field_cell.value
        temp_field_names = []
        for col in range(1, first_check_col):
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
        
        # Check if any specified columns need input
        needs_input = any(
            sheet.cell(row=row, column=col_idx).value is None and
            sheet.cell(row=row, column=col_idx).data_type != 'f'
            for col_idx in check_col_indices
        )
        
        full_field_name = f"{indent}{unique_field_name}"
        if needs_input:
            fields_to_fill.append(full_field_name)
        
        if needs_input:
            if sheet.cell(row=row, column=6).value is None or str(sheet.cell(row=row, column=6).value) == str(number):
                markdown_rows.append(f"| {full_field_name} |")
            else:
                markdown_rows.append("| |")
        else:
            markdown_rows.append("| |")
    
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
    "input_searching_infor": '''{df.fillna('').to_markdown(index=False)}''',
    "data_starting_row": {data_starting_row}
}}"""

def get_bi_weekly_fill(test_bi_weekly, start_row=52):
    lines = test_bi_weekly.splitlines()
    header = '\n'.join(lines[:2])
    data_part = '\n'.join(lines[start_row+1:])

    return header + '\n' + data_part

def markdown_to_df_with_excel_index(markdown_text):
    """
    Convert markdown table to DataFrame with Excel-style row indices and column names
    """
    # Split into lines and filter out empty lines
    lines = [line.strip() for line in markdown_text.strip().split('\n') if line.strip()]
    
    # Remove the separator line (contains only |, -, :, and spaces)
    data_lines = []
    for line in lines:
        if not re.match(r'^[\|\-\:\s]+$', line):
            data_lines.append(line)
    
    # Parse each line
    rows = []
    for line in data_lines:
        # Split by | and clean up
        cells = [cell.strip() for cell in line.split('|')]
        # Remove empty first and last elements (from leading/trailing |)
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        rows.append(cells)
    
    # Extract row indices (first column) and data
    row_indices = []
    data_rows = []
    
    for row in rows:
        if len(row) > 0:
            # First column is the Excel row index
            excel_row_index = int(row[0]) if row[0].isdigit() else row[0]
            row_indices.append(excel_row_index)
            
            # Rest is data (columns A through I)
            data_row = row[1:] if len(row) > 1 else []
            # Ensure we have exactly 9 columns (A through I)
            while len(data_row) < 9:
                data_row.append('')
            data_rows.append(data_row[:9])

    # Create DataFrame
    df = pd.DataFrame(data_rows, index=row_indices)
    df.columns = df.loc[list(df.index)[0]]
    df = df.drop(list(df.index)[0])

    return df

def process_by_company(df, test_company):
    df_cleaned = df.copy()
    first_row = df.iloc[0, 1:]  # Skip first column (index 0)
    # Check which columns have string values in the first row
    string_columns = []
    period_list = []

    for col_idx, value in enumerate(first_row, start=1):  # start=1 because we skip first column
        # Check if the value is a string (and not NaN/empty)
        if isinstance(value, str) and value.strip() == test_company:
            string_columns.append(col_idx)
            period_list.append(df.iloc[1, col_idx])

    not_contain_set = set(range(1, len(df_cleaned.columns))) -  set(string_columns)
    # Delete data in columns that have strings in the first row (except first column)
    for col_idx in list(not_contain_set):
        col_name = df_cleaned.columns[col_idx]
        df_cleaned.iloc[:, col_idx] = np.nan  # or use '' for empty strings

    return df_cleaned.fillna('').to_markdown(), period_list

################################################
