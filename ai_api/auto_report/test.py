"""
Test utilities for the auto report system.
"""
import os
from typing import List

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient


def list_azure_search_indices() -> List[str]:
    """
    List all available Azure Search indices.
    
    Returns:
        List of index names
    """
    load_dotenv()
    
    credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    index_client = SearchIndexClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
        credential=credential
    )
    
    return list(index_client.list_index_names())


def test_azure_search_connection() -> bool:
    """
    Test connection to Azure Search service.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        indices = list_azure_search_indices()
        print(f"Found {len(indices)} indices: {indices}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# def test_graph_invoke() -> bool:
#     try:
#         from agent.graph import graph
#         with open("/home/azureuser/ai-auto-report-tamht/check_logger/state_53.txt", "r", encoding="utf-8") as file:
#             content = file.read()
#         state = eval(content)
#         from openpyxl import load_workbook
#         state['template_path'] = "/home/azureuser/tamht/Xiaomi 1Q2025 Result-250528 Template.xlsx"
#         wb = load_workbook(state['template_path'])
#         state['worksheet'] = wb[state['sheet_name']]  # or wb.active for the first sheet

#         with open("/home/azureuser/ai-auto-report-tamht/check_logger/config_53.txt", "r", encoding="utf-8") as file:
#             content = file.read()
#         config = eval(content)

#         graph.invoke(input=state, config=config)

#     except Exception as e:
#         print(f"Connection failed: {e}")
#         return False

# if __name__ == "__main__":
#     test_graph_invoke()