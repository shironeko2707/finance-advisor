from typing import TypedDict, List, Dict, Any, Annotated
import pandas as pd
from langgraph.graph.message import add_messages
from openpyxl.worksheet.worksheet import Worksheet


class InjectedState(TypedDict):
    worksheet: Worksheet
    data_starting_row: int
    result_df: pd.DataFrame

# State definition for LangGraph
class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    template_path: str
    category_router: str
    fiscal_year: str
    sheet_name: str
    report_template: str
    worksheet: Worksheet
    index_name: str
    input_searching_infor: str
    input_searching_query: str
    documents: List[Any]
    retrieval_tables: List[Any]
    unadded_extraction: str
    check_enough_information_flag: str
    missing_fields: List[str]
    iteration: int
    result_markdown: str
    injected_state: InjectedState
    component_company: str
    component_sheet: str
    required_unit: str
    
    