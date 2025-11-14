import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import asyncio
from loguru import logger
from typing import Optional, Dict, Any
from functools import lru_cache
import traceback
import re
import ast

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.graph import END

from auto_report.agent.utils.model import llm
from auto_report.agent.utils.tools import _hybrid_search_data_impl, _search_data_impl, get_fields_to_fill_dynamic, delete_excel_columns, update_yoy_column, write_df_column_to_excel, add_columns
from auto_report.agent.utils.util_function import parse_only_table, template_to_markdown, remove_leading_tool_messages, merge_template_format, markdown_to_df, get_column_sort_key, extract_row_data, find_max_index_group, find_writing_column, to_minimal_markdown, template_to_markdown_example
from auto_report.agent.utils.state import WorkflowState
from auto_report.agent.utils.helpers import format_search_result, retrieving_tables
from auto_report.agent.utils.confidence import OptimizedFinancialConfidenceCalculator
from auto_report.agent.utils.prompt import WorkflowPrompts
from auto_report.config import get_settings


settings = get_settings()
prompts = WorkflowPrompts()
load_dotenv()


############################################################################
# Optimized Helper Functions

def _create_file_path(base_path: str, sheet_name: str, filename: str) -> str:
    """Create file path without repeated path operations."""
    return f"check_logger/{base_path}/{sheet_name}/reports/{filename}"

def _ensure_directory_and_write(file_path: str, content: str) -> None:
    """Optimized directory creation and file writing."""
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

############################################################################
# Optimized Agent Nodes
# Agent Nodes
input_searching_query_tools = [get_fields_to_fill_dynamic]

input_searching_query_llm = llm.bind_tools(input_searching_query_tools)
async def input_searching_query_agent(state: WorkflowState):
    logger.info(f"Start all flow")

    system_prompt = SystemMessage(content=prompts.input_searching_query_system_prompt(settings.component_df))
    
    current_prompt = HumanMessage(content = f"""
template_file_name =  {os.path.basename(state['template_path'])}
sheet_name = {state['sheet_name']}
template_excel_file = {state['report_template']}
""")
    
    messages = [system_prompt,current_prompt]
    response = input_searching_query_llm.invoke(messages)
    
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_1.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))
    return {"messages": [current_prompt, response]}

async def input_searching_query_node(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_2.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
    
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    tools = {
        "get_fields_to_fill_dynamic": get_fields_to_fill_dynamic,
    }
    tool_func = tools.get(tool_name)
    
    if "__arg1" in tool_args.keys():
        new_tool_args = eval(tool_args['__arg1'])
    else:
        new_tool_args = tool_args
    # print("new_tool_args:", new_tool_args)

    if tool_func:
        # try:
        result_string = tool_func.invoke({
            **new_tool_args,
            "state": state["injected_state"]
        })

        # print("result_string:", result_string)
        result_json = eval(result_string)
        searching_summary = result_json['searching_summary']
        fiscal_year = result_json['fiscal_year']
        input_searching_infor = result_json['input_searching_infor']
        period_header_row = result_json['period_header_row']
        component_company = result_json['component_company']
        component_sheet = result_json['component_sheet']
        required_unit = result_json['required_unit']

        # print("component_sheet:", component_sheet)
        input_searching_query = f"""
Get the following information of all timestamp about "{searching_summary}" for the "{state['sheet_name']}" sheet and return them as a table:
{input_searching_infor}
"""     
        if "Economy" in searching_summary or "economy" in searching_summary.lower():
            category_router = "Economy" 
        elif "Hotel" in searching_summary or "Retail" in searching_summary or "CPF" in searching_summary:
            category_router = "Single" 
        else:
            category_router = "Remaining" 

        # Define the full path to the file
        file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_3.txt"
        folder_path = os.path.dirname(file_path)
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(state))

        return {
            "messages": [ToolMessage(
                content=result_string,
                tool_call_id=tool_call["id"],
                name=tool_name
            )],
            # "messages": result_response,
            "category_router": category_router,
            "fiscal_year": fiscal_year,
            "input_searching_infor": input_searching_infor,
            "input_searching_query": input_searching_query,
            "injected_state": {
                'worksheet':state['worksheet'], 
                'period_header_row': period_header_row
            },
            "component_company": component_company,
            "component_sheet": component_sheet,
            "required_unit": required_unit,
        }
        # except Exception as e:
        #     return {
        #         "messages": [ToolMessage(
        #             content=f"Error: {str(e)}",
        #             tool_call_id=tool_call["id"],
        #             name=tool_name
        #         )]
        #     }
        
async def document_retrieval(state: WorkflowState) -> WorkflowState:
    """Optimized document retrieval with concurrent operations."""
    # Pre-extract values
    template_basename = os.path.basename(state['template_path'])
    sheet_name = state['sheet_name']
    
    # Write log file (non-blocking)
    file_path = _create_file_path(template_basename, sheet_name, "agent_logger_4.txt")
    _ensure_directory_and_write(file_path, str(state))
    
    # Start search task immediately
    # print("state['input_searching_query']:", state['input_searching_query'])
    search_task = asyncio.create_task(_hybrid_search_data_impl( # _search_data_impl(
        index_name=state["index_name"],
        query=state['input_searching_query']
    ))
    # print("search_task:", search_task)

    # Get current iteration efficiently
    iteration = state.get("iteration", 0) + 1
    # print("iteration:", iteration)
    
    # Wait for search results
    search_results = await search_task
    # print("search_results:", search_results)
    
    # Process results concurrently
    documents_task = asyncio.create_task(asyncio.to_thread(format_search_result, search_results))
    tables_task = asyncio.create_task(asyncio.to_thread(retrieving_tables, search_results))
    # print("tables_task:", tables_task)

    # Wait for both processing tasks
    documents, retrieval_tables = await asyncio.gather(documents_task, tables_task)
    # print("documents:", documents)
    
    # Write final log file
    file_path = _create_file_path(template_basename, sheet_name, "agent_logger_5.txt")
    _ensure_directory_and_write(file_path, str(state))
    # print("file_path:", file_path)
    
    return {
        "documents": documents, 
        "retrieval_tables": retrieval_tables, 
        'iteration': iteration
    }

# Cache for repeated file operations
@lru_cache(maxsize=128)
def _ensure_directory_exists(folder_path: str):
    """Cached directory creation to avoid repeated os.makedirs calls"""
    os.makedirs(folder_path, exist_ok=True)

# Optimized file logging function
def _write_log_file(file_path: str, content: str):
    """Optimized logging function with reduced I/O operations"""
    folder_path = os.path.dirname(file_path)
    _ensure_directory_exists(folder_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# Pre-compiled regex or string operations for better performance
_NA_VALUES = {'N/A', '-', '—', 'NaN', 'nan'}

def _replace_na_values(df: pd.DataFrame) -> pd.DataFrame:
    """Optimized NA value replacement using vectorized operations"""
    return df.replace(_NA_VALUES, np.nan)

# Step 2: Extract Report (Optimized)
async def extract_report(state: WorkflowState) -> WorkflowState:
    # Batch file operations
    base_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports"

    # Log initial state (consider making this optional for production)
    _write_log_file(f"{base_path}/agent_logger_6.txt", str(state))
    
    context = state["documents"]
    
    if state['category_router'] == 'Economy':
        system_prompt = prompts.economy_extract_report_system_prompt(context=context)
    elif state['category_router'] == 'Bi-Weekly':
        system_prompt = prompts.bi_weekly_extract_report_system_prompt(context=context)
    elif state['category_router'] == 'Single':
        system_prompt = prompts.extract_report_system_prompt(context=context)
    else:
        component_df = settings.component_df
        if state['component_company'] in component_df['File'].dropna().unique():
            component_df = component_df[(component_df['File'] == state['component_company']) | (component_df['File'].isna())]

        if state['component_sheet'] in component_df['Sheet'].dropna().unique():
            component_df = component_df[(component_df['Sheet'] == state['component_sheet']) | (component_df['File'].isna())]

        if state['component_company'] not in component_df['File'].dropna().unique() and state['component_sheet'] not in component_df['Sheet'].dropna().unique():
            component_df = component_df[(component_df['Sheet'].isna()) | (component_df['File'].isna())]

        system_prompt = prompts.company_extract_report_system_prompt(
            context=context, 
            current_status=state["report_template"],
            conponent_text=to_minimal_markdown(component_df[['Main (Field Name)', 'Components (in CONTEXT)', 'Note']])
        )
        # print("system_prompt:", system_prompt)

#     query = f"""
# Base on the following past extraction, learn to extract information for new periods:
# {template_to_markdown_example(state['worksheet'], start_col=2, start_row=state['injected_state']['period_header_row'])}

# {state["input_searching_query"]}
# """
    query = state["input_searching_query"]
    
    try:
        response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])
    except Exception as e:
        return f"[RETRIEVING] Error generating answer: {str(e)}"
    
    result = response.content
    # print("result:", result)
    table_result = parse_only_table(result)
    table_result = table_result.replace("As at 1 July ", "As at 30 June ")
    print("table_result:", table_result)
    
    # Handle iterations update more efficiently
    if state['iteration'] == 1:
        # Early return for empty results
        default_df = markdown_to_df(parse_only_table(state["input_searching_infor"]))
        if table_result is None or not state['documents']: 
            return {
                "injected_state": {
                    'worksheet': state['worksheet'], 
                    'period_header_row': state['injected_state']['period_header_row'],
                    'result_df': default_df,
                    'confidence_df': default_df,
                },
                "unadded_extraction": True
            }
        
        # Handle template format merging with better error handling
        try:
            table_result = merge_template_format(
                table_result, 
                parse_only_table(state["input_searching_infor"]),
                f"Field Name ({state['required_unit']})",
            )
        except Exception as e:
            print("An error occurred:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {e}")
            print("Traceback:")
            traceback.print_exc()
            
            return {
                "injected_state": {
                    'worksheet': state['worksheet'], 
                    'period_header_row': state['injected_state']['period_header_row'],
                    'result_df': default_df,
                    'confidence_df': default_df
                },
                "unadded_extraction": True
            }
        
        # Optimized NA value replacement
        extracted_data = _replace_na_values(table_result)
        # Initialize calculator and compute confidence matrix
        calculator = OptimizedFinancialConfidenceCalculator(state['retrieval_tables'])
        confidence_matrix = calculator.calculate_confidence_matrix(
            extracted_data.set_index(extracted_data.columns[0])
        ).reset_index()
        
        result_df = extracted_data
        confidence_df = confidence_matrix
        unadded_extraction = False

    # Following iteration
    else:
        # Early return for empty results
        if table_result is None or not state['documents']: 
            return {
                "injected_state": {
                    'worksheet': state['worksheet'], 
                    'period_header_row': state['injected_state']['period_header_row'],
                    'result_df': state['injected_state']['result_df'],
                    'confidence_df': state['injected_state']['confidence_df']
                },
                "unadded_extraction": True
            }
        
        # Handle template format merging with better error handling
        try:
            table_result = merge_template_format(
                table_result, 
                parse_only_table(state["input_searching_infor"]),
                f"Field Name ({state['required_unit']})",
            )
        except Exception as e:
            print("An error occurred:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {e}")
            print("Traceback:")
            traceback.print_exc()

            return {
                "injected_state": {
                    'worksheet': state['worksheet'], 
                    'period_header_row': state['injected_state']['period_header_row'],
                    'result_df': state['injected_state']['result_df'],
                    'confidence_df': state['injected_state']['confidence_df']
                },
                "unadded_extraction": True
            }
        
        # Optimized NA value replacement
        extracted_data = _replace_na_values(table_result)
        # Initialize calculator and compute confidence matrix
        calculator = OptimizedFinancialConfidenceCalculator(state['retrieval_tables'])
        confidence_matrix = calculator.calculate_confidence_matrix(
            extracted_data.set_index(extracted_data.columns[0])
        ).reset_index()
        
        ## Continue Iteration
        result_df, confidence_df, unadded_extraction = _merge_dataframes_optimized(
            state, extracted_data, confidence_matrix
        )
    
    # Final logging
    _write_log_file(f"{base_path}/agent_logger_7.txt", str(state))
    
    return {
        "messages": [HumanMessage(content=query), response],
        "result_markdown": result_df.fillna("").to_markdown(index=False),
        "injected_state": {
            'worksheet': state['worksheet'], 
            'period_header_row': state['injected_state']['period_header_row'],
            'result_df': result_df,
            'confidence_df': confidence_df
        },
        "unadded_extraction": unadded_extraction
    }

def _merge_dataframes_optimized(state: Dict, new_result_df: pd.DataFrame, 
                              new_confidence_df: pd.DataFrame) -> tuple:
    """Optimized dataframe merging logic"""
    result_df = state['injected_state']['result_df'].copy()
    confidence_df = state['injected_state']['confidence_df'].copy()
    
    # Use vectorized operations instead of loops where possible
    result_df_cleaned = _replace_na_values(result_df)
    confidence_df_cleaned = _replace_na_values(confidence_df)
    
    # Get matching columns once
    matching_columns = [col for col in result_df.columns if col in new_result_df.columns]
    
    # Create field name mapping for faster lookup
    field_name_map = {name: idx for idx, name in enumerate(result_df[f"Field Name ({state['required_unit']})"])}
    
    # Batch update operations
    for i, row in new_result_df[matching_columns].iterrows():
        field_name = row[f"Field Name ({state['required_unit']})"]
        if field_name in field_name_map:
            target_idx = field_name_map[field_name]
            
            # Vectorized update for matching columns
            mask = pd.isna(result_df_cleaned.iloc[target_idx][matching_columns])
            update_cols = [col for col, is_na in zip(matching_columns, mask) if is_na and col != f"Field Name ({state['required_unit']})"]
            
            for col in update_cols:
                result_df_cleaned.at[target_idx, col] = row[col]
                confidence_df_cleaned.at[target_idx, col] = new_confidence_df.at[i, col]
    
    # Check if any changes were made
    unadded_extraction = result_df_cleaned.equals(_replace_na_values(result_df))
    
    return result_df_cleaned, confidence_df_cleaned, unadded_extraction

# Step 3: Check Enough Information (Optimized)
async def check_enough_information(state: WorkflowState) -> Dict[str, Any]:
    if state['injected_state']['result_df'].empty:
        return {"check_enough_information_flag": END}
    
    result_df = state['injected_state']['result_df']
    
    # Vectorized operations for better performance
    data_columns = list(result_df.columns)[1:]  # Cache column list
    
    # Use vectorized operations to find NA/missing values
    mask_cell = result_df[data_columns].isin(_NA_VALUES) | result_df[data_columns].isna()
    non_na_count = (~mask_cell).sum(axis=1)
    
    # Find rows with insufficient data (0 or 1 non-NA values)
    insufficient_data_mask = (non_na_count <= 1)
    na_rows = result_df.loc[insufficient_data_mask, f"Field Name ({state['required_unit']})"].dropna()
    
    # Early termination conditions
    if (state['unadded_extraction'] or 
        na_rows.empty or 
        state["iteration"] >= 3 or 
        na_rows.shape[0] < 7):
        return {"check_enough_information_flag": 'call_write_to_excel_update_yoy_column_agent'}
    
    # Update search query
    current_table = parse_only_table(state['input_searching_query'])
    input_searching_query = state['input_searching_query'].replace(
        current_table, 
        na_rows.to_markdown(index=False)
    )
    
    return {
        "check_enough_information_flag": 'call_write_to_excel_update_yoy_column_agent', # document_retrieval
        "input_searching_query": input_searching_query
    }

async def check_enough_information_function(state: WorkflowState) -> str:
    # Conditional logging - consider making this configurable
    base_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports"
    _write_log_file(f"{base_path}/agent_logger_8.txt", str(state))
    return state['check_enough_information_flag']
    

# # Step 5: Write to Excel Template
# 2. Wrap as LangChain tools
write_to_excel_delete_excel_columns_tools = [delete_excel_columns]

write_to_excel_delete_excel_columns_llm = llm.bind_tools(write_to_excel_delete_excel_columns_tools)
async def call_write_to_excel_delete_excel_columns_agent(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_9.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))
    
    system_prompt = SystemMessage(content=prompts.delete_excel_columns_system_prompt()) 
    
    current_prompt = HumanMessage(content=f"""
result_df = 
{state['injected_state']['result_df'].fillna('').to_markdown(index=False)}
template_excel_file = 
{state['report_template']}
""")
    
    messages = [system_prompt ,current_prompt] # state['messages'][-3:] + 
    messages = remove_leading_tool_messages(messages)
    response = write_to_excel_delete_excel_columns_llm.invoke(messages)
    
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_10.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))
    return {"messages": [current_prompt, response]}

async def write_to_excel_delete_excel_columns_node(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_11.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
    
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    tools = {
        "delete_excel_columns": delete_excel_columns, 
    }
    tool_func = tools.get(tool_name)
    
    # param mapping
    if "__arg1" in tool_args.keys():
        # case return string
        try:
            new_tool_args = eval(tool_args['__arg1'])
        except:
            new_tool_args = tool_args['__arg1'].split(',')
    else:
        new_tool_args = tool_args
    if type(new_tool_args) == list:
        new_tool_args = {'columns_to_delete':new_tool_args}

    if tool_func:
        try:
            result_string = tool_func.invoke({
                **new_tool_args,
                "state": state["injected_state"]
            })
            report_template = template_to_markdown(state['worksheet'])

            # Define the full path to the file
            file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_12.txt"
            folder_path = os.path.dirname(file_path)
            os.makedirs(folder_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(state))
            
            return {
                "messages": [ToolMessage(
                    content=result_string,
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )],
                # "messages": result_response,
                "report_template": report_template
            }
        except Exception as e:
            return {
                "messages": [ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )]
            }

##########################################################################
# 2. Wrap as LangChain tools
async def call_write_to_excel_update_yoy_column_agent(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_13.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    if state['category_router'] == 'Economy':
        system_prompt = SystemMessage(content=prompts.economy_update_yoy_column_system_prompt())
        example_prompt = ""
        write_to_excel_update_yoy_column_llm = llm.bind_tools([update_yoy_column, add_columns])
    elif state['category_router'] == 'Single':
        system_prompt = SystemMessage(content=prompts.update_yoy_column_system_prompt())
        example_prompt = prompts.update_yoy_column_examples()
        write_to_excel_update_yoy_column_llm = llm.bind_tools([update_yoy_column])
    else:
        system_prompt = SystemMessage(content=prompts.grouping_period_system_prompt())
        example_prompt = ""
        write_to_excel_update_yoy_column_llm = llm

    if state['category_router'] == 'Remaining':
        current_prompt = HumanMessage(content=f"""
long_string_list = {list(state['injected_state']['result_df'].columns)[1:]}
pair_list = {extract_row_data(state['worksheet'], row_index=state['injected_state']['period_header_row'])}
context = '{state['fiscal_year']}'
""")
    else:
        current_prompt = HumanMessage(content=f"""
EXAMPLES:
{example_prompt}
                                  

NOW, PLEASE PROCESS THIS INPUT:
User:
result_df = 
{state['injected_state']['result_df'].fillna('').to_markdown(index=False)}
template_file_name =  {os.path.basename(state['template_path'])}
sheet_name = {state['sheet_name']}
template_excel_file =
{state['report_template']}
Assistant:

""")
    
    messages = [system_prompt, current_prompt] # state['messages'][-3:] + 
    messages = remove_leading_tool_messages(messages)
    response = write_to_excel_update_yoy_column_llm.invoke(messages)
    
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_14.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    return {"messages": [current_prompt, response]} # current_human_message # messages[-1]

async def write_to_excel_update_yoy_column_node(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_15.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    messages = state["messages"]
    last_message = messages[-1]
    
    if state['category_router'] == 'Remaining':
        # Step 1: Extract the dictionary substring
        match = re.search(r"\{.*\}", last_message.content, re.DOTALL)
        if match:
            dict_str = match.group(0)
            dict_str = dict_str.replace('null', 'None')
            dict_str = dict_str.replace('//', '#')

            # Step 2: Parse into a Python dictionary
            parsed_dict = ast.literal_eval(dict_str)
            tool_activation = find_max_index_group(parsed_dict)
            def check_unique_column(data):
                # Track seen unique values and their indices
                seen = set()
                keep_indices = []

                for i, val in enumerate(data['new_column_names']):
                    if val not in seen:
                        seen.add(val)
                        keep_indices.append(i)

                # Filter both lists based on keep_indices
                data['new_column_names'] = [data['new_column_names'][i] for i in keep_indices]
                # data['column_names'] = [data['column_names'][i] for i in keep_indices]

                return data

            # Track seen unique values and their indices
            for group_key in tool_activation.keys():
                tool_activation[group_key] = check_unique_column(tool_activation[group_key])

            # sort by yoy_column
            def excel_column_to_number(col):
                """Convert Excel column letter to number (A=1, Z=26, AA=27, etc.)"""
                num = 0
                for char in col:
                    num = num * 26 + (ord(char) - ord('A') + 1)
                return num
            sorted_tool_calls = dict(sorted(tool_activation.items(), key=lambda item: excel_column_to_number(item[1]['yoy_column']),reverse=True))
            
            list_ToolMessage = []
            tool_id = 0
            tool_func = update_yoy_column
            for key, new_tool_args in sorted_tool_calls.items():
                tool_id += 1
                try:
                    result_string = tool_func.invoke({
                        **new_tool_args,
                        "state": state["injected_state"]
                    })
    
                    list_ToolMessage.append(ToolMessage(
                            content=result_string,
                            tool_call_id=f"id_{tool_id}",
                            name='update_yoy_column'
                        ))
                    
                except Exception as e:
                    list_ToolMessage.append(ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=f"id_{tool_id}",
                            name='update_yoy_column'
                        ))

    else:
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {}
        
        sorted_tool_calls = sorted(last_message.tool_calls, key=get_column_sort_key, reverse=True)
        
        list_ToolMessage = []
        # for tool_call in last_message.tool_calls:
        for tool_call in sorted_tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            tools = {
                "update_yoy_column": update_yoy_column,
                "add_columns": add_columns,
            }
            tool_func = tools.get(tool_name)
            
            # param mapping
            if "__arg1" in tool_args.keys():
                # case return string
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

            if tool_func:
                try:
                    result_string = tool_func.invoke({
                        **new_tool_args,
                        "state": state["injected_state"]
                    })
    
                    list_ToolMessage.append(ToolMessage(
                            content=result_string,
                            tool_call_id=tool_call["id"],
                            name=tool_name
                        ))
                    
                except Exception as e:
                    list_ToolMessage.append(ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call["id"],
                            name=tool_name
                        ))
            
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_16.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    report_template = template_to_markdown(state['worksheet'])
    return {
        "messages": list_ToolMessage,
        "report_template": report_template
    }
    
##########################################################################
# 2. Wrap as LangChain tools
write_to_excel_write_df_column_to_excel_tools = [
    write_df_column_to_excel
]

write_to_excel_write_df_column_to_excel_llm = llm.bind_tools(write_to_excel_write_df_column_to_excel_tools)
async def call_write_to_excel_write_df_column_to_excel_agent(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_17.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))

    if state['category_router'] == 'Economy':
        system_prompt = SystemMessage(content=prompts.economy_write_df_column_to_excel_system_prompt())
        example_prompt = ""
    elif state['category_router'] == 'Bi-Weekly':
        system_prompt = SystemMessage(content=prompts.bi_weekly_write_df_column_to_excel_system_prompt())
        example_prompt = ""
    elif state['category_router'] == 'Single':
        system_prompt = SystemMessage(content=prompts.write_df_column_to_excel_system_prompt())
        example_prompt = prompts.write_df_column_to_excel_examples()
    else:
        system_prompt = SystemMessage(content=prompts.grouping_period_system_prompt())
        example_prompt = ""
        write_to_excel_write_df_column_to_excel_llm = llm

    if state['category_router'] == 'Remaining':
        current_prompt = HumanMessage(content=f"""
long_string_list = {list(state['injected_state']['result_df'].columns)[1:]}
pair_list = {extract_row_data(state['worksheet'], row_index=state['injected_state']['period_header_row'])}
context = '{state['fiscal_year']}'
""")
    else:
        current_prompt = HumanMessage(content=f"""
EXAMPLES:
{example_prompt}
                                

NOW, PLEASE PROCESS THIS INPUT:
User: 
result_df = 
{state['injected_state']['result_df'].fillna('').to_markdown(index=False)}
template_excel_file = 
{state['report_template']}
Assistant:

""")
    
    messages = [system_prompt, current_prompt] # state['messages'][-3:] + 
    messages = remove_leading_tool_messages(messages)
    response = write_to_excel_write_df_column_to_excel_llm.invoke(messages)
    
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_18.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))
    return {"messages": [current_prompt, response]} # current_human_message # messages[1]

async def write_to_excel_write_df_column_to_excel_node(state: WorkflowState):
    # Define the full path to the file
    file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_19.txt"
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(state))
    
    messages = state["messages"]
    last_message = messages[-1]
    
    try: 
        if state['category_router'] == 'Remaining':
            # Step 1: Extract the dictionary substring
            match = re.search(r"\{.*\}", last_message.content, re.DOTALL)
            if match:
                dict_str = match.group(0)
                dict_str = dict_str.replace('null', 'None')
                dict_str = dict_str.replace('//', '#')

                # Step 2: Parse into a Python dictionary
                parsed_dict = ast.literal_eval(dict_str)
                new_tool_args = find_writing_column(parsed_dict)
                # Track seen unique values and their indices
                seen = set()
                keep_indices = []
                for i, val in enumerate(new_tool_args['start_cols']):
                    if val not in seen:
                        seen.add(val)
                        keep_indices.append(i)

                # Filter both lists based on keep_indices
                new_tool_args['start_cols'] = [new_tool_args['start_cols'][i] for i in keep_indices]
                new_tool_args['column_names'] = [new_tool_args['column_names'][i] for i in keep_indices]

                # Invoking                
                list_ToolMessage = []
                tool_func = write_df_column_to_excel
                try:
                    result_string = tool_func.invoke({
                        **new_tool_args,
                        "state": state["injected_state"]
                    })

                    list_ToolMessage.append(ToolMessage(
                            content=result_string,
                            tool_call_id=f"id_{1}",
                            name='write_df_column_to_excel'
                        ))
                    
                except Exception as e:
                    list_ToolMessage.append(ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=f"id_{1}",
                            name='write_df_column_to_excel'
                        ))
        else:
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return {}
            
            list_ToolMessage = []
            for tool_call in last_message.tool_calls:
                # tool_call = last_message.tool_calls[0]
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                tools = {
                    "write_df_column_to_excel": write_df_column_to_excel,
                }
                tool_func = tools.get(tool_name)
                
                # param mapping
                # new_tool_args = tool_args['__arg1']
                if "__arg1" in tool_args.keys():
                    new_tool_args = eval(tool_args['__arg1'])
                else:
                    new_tool_args = tool_args
                
                # new_tool_args['injected_state'] = state["injected_state"]
                if tool_func:
                    try:
                        result_string = tool_func.invoke({
                            **new_tool_args,
                            "state": state["injected_state"]
                        })
                        # report_template = template_to_markdown(state['worksheet'])
            
                        list_ToolMessage.append(ToolMessage(
                                content=result_string,
                                tool_call_id=tool_call["id"],
                                name=tool_name
                            ))

                    except Exception as e:
                        list_ToolMessage.append(ToolMessage(
                                content=f"Error: {str(e)}",
                                tool_call_id=tool_call["id"],
                                name=tool_name
                            ))
                        # return {
                        #     "messages": [ToolMessage(
                        #         content=f"Error: {str(e)}",
                        #         tool_call_id=tool_call["id"],
                        #         name=tool_name
                        #     )]
                        # }
                
        # Define the full path to the file
        file_path = f"check_logger/{os.path.basename(state['template_path'])}/{state['sheet_name']}/reports/agent_logger_20.txt"
        folder_path = os.path.dirname(file_path)
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(state))
            f.write(str(list_ToolMessage))

        report_template = template_to_markdown(state['worksheet'])
        return {
            "messages": list_ToolMessage,
            # "messages": result_response,
            "report_template": report_template
        } 
    
    except Exception as e:
        print("An error occurred:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        print("Traceback:")
        traceback.print_exc()