import asyncio
from enum import Enum
from optparse import Option
from typing import List, Dict, Optional, Union, Any, overload, Tuple
import pandas as pd

from loguru import logger
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult

from ..config import get_settings

MAX_WORKERS = 32        # TODO: move to other file in the further.


class DocumentIntelligentModel(str, Enum):
    """Enum for supported Document Intelligence models."""
    LAYOUT = "prebuilt-layout"
    READ = "prebuild-read"


class DocumentExtractor:
    """Asynchronous extractor for Azure Document Intelligence.

    This class provides an async context manager for extracting document analysis
    results from Azure Document Intelligence service.

    Example:
        ```python
        from auto_report.doc_intelligence import DocumentExtractor, DocumentIntelligentModel

        doc_paths = ["path/to/doc1.pdf", "path/to/doc2.pdf"]
        async with DocumentExtractor(model=DocumentIntelligentModel.LAYOUT) as extractor:
            results = await extractor.extract(doc_paths)
            for result in results:
                print(result)
        ```
    """

    def __init__(
        self,
        *,
        model: DocumentIntelligentModel = DocumentIntelligentModel.LAYOUT,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> None:
        """
        Initializes the DocumentExtractor.

        Args:
            model (DocumentIntelligentModel, optional): The model to use for analysis.
                Defaults to DocumentIntelligentModel.LAYOUT.
            endpoint (str, optional): Azure Document Intelligence endpoint. If not provided,
                uses value from settings.
            api_key (str, optional): Azure API key. If not provided, uses value from settings.
        """
        settings = get_settings()
        self.endpoint: str = endpoint or settings.document_intelligent_endpoint
        self.credential: AzureKeyCredential = AzureKeyCredential(api_key or settings.document_intelligent_api_key)
        self.model: DocumentIntelligentModel = model
        self.document_intelligent_client: Optional[DocumentIntelligenceClient] = None

    async def __aenter__(self) -> "DocumentExtractor":
        """Initializes the DocumentIntelligenceClient when entering async context.

        Returns:
            DocumentExtractor: The initialized extractor instance.
        """
        self.document_intelligent_client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Closes the DocumentIntelligenceClient when exiting async context."""
        if self.document_intelligent_client:
            await self.document_intelligent_client.close()
            self.document_intelligent_client = None

    @overload
    async def extract(self, document_path: str, **kwargs) -> Optional[AnalyzeResult]:
        ...

    @overload
    async def extract(self, document_path: List[str], **kwargs) -> List[Optional[AnalyzeResult]]:
        ...
    
    async def extract(
        self, document_path: Union[str, List[str]], **kwargs
    ):
        """Extracts analysis results for one or more documents.

        Args:
            document_path (str or List[str]): Path(s) to document(s) to analyze.

        Returns:
            List[Optional[AnalyzeResult]]: List of analysis results, or None for failed documents.
        """
        if isinstance(document_path, str):
            document_paths = [document_path]
        elif isinstance(document_path, list):
            document_paths = document_path.copy()
        else:
            raise ValueError("document_path must be a path (str) or a list of paths")

        semaphore = asyncio.Semaphore(kwargs.get("max_workers") or MAX_WORKERS)

        async def analyse_document(doc_path: str):
            async with semaphore:
                try:
                    if doc_path.endswith('.pdf'):
                        with open(doc_path, "rb") as f:
                            poller = await self.document_intelligent_client.begin_analyze_document(
                                model_id=self.model,
                                body=f,
                                **kwargs
                            )
                        logger.info(f"Started analysis for document '{doc_path}'")
                        return await poller.result()
                    else:
                        def read_excel_sheets(file_path: str) -> List[Tuple[str, pd.DataFrame]]:
                            """
                            Read all sheets from an Excel file, move column headers to first row,
                            and reset column names to generic integers. Skips empty sheets.

                            Args:
                                file_path (str): Path to the Excel file (.xlsx or .xls)

                            Returns:
                                List[Tuple[str, pd.DataFrame]]: List of tuples containing sheet name and modified DataFrame
                            """
                            # Read all sheets into a dictionary: {sheet_name: DataFrame}
                            excel_file = pd.read_excel(file_path, sheet_name=None)

                            sheet_data = []
                            for sheet_name, df in excel_file.items():
                                # Skip empty sheets (no data or only NaN values)
                                if df.empty or df.isna().all().all():
                                    continue
                                    
                                # Insert column names as the first row
                                df_reset = df.copy()
                                df_reset.loc[-1] = df_reset.columns  # Add column names as a new row
                                df_reset.index = df_reset.index + 1  # Shift index
                                df_reset = df_reset.sort_index()     # Reorder rows

                                # Reset column names to generic integers
                                df_reset.columns = list(range(len(df_reset.columns)))

                                sheet_data.append((sheet_name, df_reset))

                            return sheet_data
                        
                        return read_excel_sheets(doc_path)

                except Exception as e:
                    logger.error(f"Error analyzing document '{doc_path}': {e}")
                    return None

        results = await asyncio.gather(*[
            analyse_document(path) for path in document_paths
        ])

        if isinstance(document_path, str):
            return results[0]
        return results

    @staticmethod
    def azure_tables_to_markdown(table: Dict[str, Any]) -> str:
        """
        Convert a table (from result.tables) returned by Azure Document Intelligence to markdown format.

        Args:
            table (Dict[str, Any]): A single table dictionary from the 'tables' field of an Azure
                Document Intelligence AnalyzeResult (i.e., from result.tables).

        Returns:
            str: Markdown representation of the table. Returns an empty string if the table has no rows or columns.

        Example:
            result = <output from Azure Document Intelligence>
            for table in result.tables:
                markdown = azure_tables_to_markdown(table)
        """
        # Get table dimensions
        rows = table.get('rowCount', 0)
        cols = table.get('columnCount', 0)
        
        if rows == 0 or cols == 0:
            return ""
        
        # Initialize grid
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        
        # Fill grid with cell content
        for cell in table.get('cells', []):
            row_index = cell.get('rowIndex', 0)
            col_index = cell.get('columnIndex', 0)
            content = cell.get('content', '').strip()
            
            # Handle cells that span multiple rows/columns
            row_span = cell.get('rowSpan', 1)
            col_span = cell.get('columnSpan', 1)
            
            # Fill the primary cell
            if row_index < rows and col_index < cols:
                grid[row_index][col_index] = content
                
                # For spanning cells, mark spanned positions
                for r in range(row_index, min(row_index + row_span, rows)):
                    for c in range(col_index, min(col_index + col_span, cols)):
                        if r != row_index or c != col_index:
                            grid[r][c] = ""  # Mark as part of span
        
        # Convert grid to markdown
        markdown_lines = []
        
        # Add header row
        if rows > 0:
            header = "| " + " | ".join(grid[0]) + " |"
            markdown_lines.append(header)
            
            # Add separator
            separator = "| " + " | ".join(["---"] * cols) + " |"
            markdown_lines.append(separator)
            
            # Add data rows
            for row in grid[1:]:
                data_row = "| " + " | ".join(row) + " |"
                markdown_lines.append(data_row)
        
        return "\n".join(markdown_lines)

async def main() -> Any:
    """Example main function to demonstrate usage of DocumentExtractor.

    Returns:
        Any: The results of document extraction.
    """
    import os

    doc_dir = "data/input/Alibaba"
    items = [os.path.join(doc_dir, item) for item in os.listdir(doc_dir)[:1]]

    async with DocumentExtractor() as analyzer:
        results = await analyzer.extract(items)

    return results


if __name__ == "__main__":
    print(asyncio.run(main()))
