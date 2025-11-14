from dotenv import load_dotenv
import langgraph
from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.sqlite import SqliteSaver

from auto_report.agent.utils.state import WorkflowState
from auto_report.agent.utils.nodes import (
    input_searching_query_agent,
    input_searching_query_node,
    document_retrieval,
    extract_report,
    check_enough_information,
    check_enough_information_function,
    call_write_to_excel_update_yoy_column_agent,
    call_write_to_excel_write_df_column_to_excel_agent,
    write_to_excel_update_yoy_column_node,
    write_to_excel_write_df_column_to_excel_node,
)

load_dotenv()


# Define the LangGraph workflow
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node('input_searching_query_agent', input_searching_query_agent)
workflow.add_node('input_searching_query_node', input_searching_query_node)
workflow.add_node("document_retrieval", document_retrieval)
workflow.add_node("extract_report", extract_report)
workflow.add_node("check_enough_information", check_enough_information)
workflow.add_node("call_write_to_excel_update_yoy_column_agent", call_write_to_excel_update_yoy_column_agent)
workflow.add_node("call_write_to_excel_write_df_column_to_excel_agent", call_write_to_excel_write_df_column_to_excel_agent)
workflow.add_node("write_to_excel_update_yoy_column_node", write_to_excel_update_yoy_column_node)
workflow.add_node("write_to_excel_write_df_column_to_excel_node", write_to_excel_write_df_column_to_excel_node)

# Define edges
workflow.add_edge(START, "input_searching_query_agent")
workflow.add_conditional_edges(
    "input_searching_query_agent", 
    lambda state: "input_searching_query_node" if state["messages"][-1].tool_calls else END,
    {
        "input_searching_query_node": "input_searching_query_node",
        END: END,
    }
)
workflow.add_edge('input_searching_query_node', "document_retrieval")
workflow.add_edge("document_retrieval", "extract_report")
workflow.add_edge("extract_report", "check_enough_information")
workflow.add_conditional_edges(
    "check_enough_information",
    check_enough_information_function,
    {
        "call_write_to_excel_update_yoy_column_agent": "call_write_to_excel_update_yoy_column_agent",
        "document_retrieval": "document_retrieval",
        END: END
    }
)
workflow.add_edge("call_write_to_excel_update_yoy_column_agent", "write_to_excel_update_yoy_column_node")
workflow.add_edge("write_to_excel_update_yoy_column_node", "call_write_to_excel_write_df_column_to_excel_agent")
workflow.add_edge("call_write_to_excel_write_df_column_to_excel_agent", "write_to_excel_write_df_column_to_excel_node")
workflow.add_edge("write_to_excel_write_df_column_to_excel_node", END)

graph = workflow.compile()