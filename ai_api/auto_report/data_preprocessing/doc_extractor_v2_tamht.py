import asyncio
from enum import Enum
from typing import List, Dict, Optional, Union, Any, overload
import re
import pandas as pd

from loguru import logger
import openpyxl
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

from auto_report.config import get_settings


class DocumentIntelligentModel(str, Enum):
    """Enum for supported Document Intelligence models."""

    LAYOUT = "prebuilt-layout"
    READ = "prebuilt-read"


class OutputFormat(str, Enum):
    """Enum for output content formats."""
    
    TEXT = "text"
    MARKDOWN = "markdown"


class DocumentExtractorV2:
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
        api_key: Optional[str] = None,
        max_workers: Optional[int] = None,
    ) -> None:
        """
        Initializes the DocumentExtractor.

        Args:
            model (DocumentIntelligentModel, optional): The model to use for analysis.
                Defaults to DocumentIntelligentModel.LAYOUT.
            endpoint (str, optional): Azure Document Intelligence endpoint. If not provided,
                uses value from settings.
            api_key (str, optional): Azure API key. If not provided, uses value from settings.
            max_workers (int, optional): Maximum concurrent workers. If not provided,
                uses value from settings.
        """
        settings = get_settings()
        self.endpoint: str = endpoint or settings.document_intelligent_endpoint
        self.credential: AzureKeyCredential = AzureKeyCredential(
            api_key or settings.document_intelligent_api_key
        )
        self.model: DocumentIntelligentModel = model
        self.document_intelligent_client: Optional[DocumentIntelligenceClient] = None
        self.max_workers = max_workers or settings.extractor_max_workers

    async def __aenter__(self) -> "DocumentExtractorV2":
        """Initializes the DocumentIntelligenceClient when entering async context.

        Returns:
            DocumentExtractorV2: The initialized extractor instance.
        """
        self.document_intelligent_client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=self.credential
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Closes the DocumentIntelligenceClient when exiting async context."""
        if self.document_intelligent_client:
            await self.document_intelligent_client.close()
            self.document_intelligent_client = None

    @overload
    async def extract(
        self, document_path: str, **kwargs
    ) -> Optional[Union[AnalyzeResult, List[Dict[str, str]]]]: ...

    @overload
    async def extract(
        self, document_path: List[str], **kwargs
    ) -> List[Optional[Union[AnalyzeResult, List[Dict[str, str]]]]]: ...

    async def extract(
        self, document_path: Union[str, List[str]], **kwargs
    ) -> Union[
        Optional[Union[AnalyzeResult, List[Dict[str, str]]]],
        List[Optional[Union[AnalyzeResult, List[Dict[str, str]]]]]
    ]:
        """
        Extracts analysis results for one or more documents.
        For PDF files, uses Azure Document Intelligence.
        For Excel files (.xlsx, .xls), uses _extract_excel.

        Args:
            document_path (str or List[str]): Path(s) to document(s) to analyze.
            **kwargs: Additional arguments passed to analyze_document

        Returns:
            For PDF: AnalyzeResult or List[AnalyzeResult]
            For Excel: Dict or List[Dict]
        """
        if isinstance(document_path, str):
            document_paths = [document_path]
            single_input = True
        elif isinstance(document_path, list):
            document_paths = document_path.copy()
            single_input = False
        else:
            raise ValueError("document_path must be a path (str) or a list of paths")

        semaphore = asyncio.Semaphore(kwargs.get("max_workers") or self.max_workers)

        async def analyse_document(doc_path: str):
            ext = doc_path.lower().split('.')[-1]
            if ext in ["pdf"]:
                async with semaphore:
                    with open(doc_path, "rb") as f:
                        poller = await self.document_intelligent_client.begin_analyze_document(
                            model_id=self.model, body=f
                        )
                    logger.info(f"Started analysis for PDF document '{doc_path}'")
                    return await poller.result()
            elif ext in ["xlsx", "xls"]:
                try:
                    logger.info(f"Started extraction for Excel document '{doc_path}'")
                    return self._extract_excel(doc_path)
                except Exception as e:
                    logger.error(f"Error extracting Excel document '{doc_path}': {e}")
                    return None
            else:
                logger.error(f"Unsupported file type for '{doc_path}'")
                return None

        results = await asyncio.gather(*[analyse_document(path) for path in document_paths])

        if single_input:
            return results[0]
        return results

    async def extract_tables_with_context(
        self,
        document_path: Union[str, List[str]],
        filter_table_pages: bool = True
    ) -> Union[List[str], List[List[str]]]:
        """
        Extracts tables with surrounding text context from PDF documents.
        Returns content in HTML or Markdown format, preserving document structure.

        Args:
            document_path (str or List[str]): Path(s) to PDF document(s) to analyze.
            filter_table_pages (bool): If True, only returns pages containing tables.
                Defaults to True.

        Returns:
            - For single document: List[str] where each element is a page's content
            - For multiple documents: List[List[str]] where each inner list contains pages for one document

        Example:
            ```python
            async with DocumentExtractor() as extractor:
                # Single document
                pages = await extractor.extract_tables_with_context("doc.pdf")
                
                # Multiple documents with HTML output
                results = await extractor.extract_tables_with_context(
                    ["doc1.pdf", "doc2.pdf"]
                )
            ```
        """
        if isinstance(document_path, str):
            document_paths = [document_path]
            single_input = True
        elif isinstance(document_path, list):
            document_paths = document_path.copy()
            single_input = False
        else:
            raise ValueError("document_path must be a path (str) or a list of paths")

        # Filter only PDF files
        pdf_paths = [path for path in document_paths] # if path.lower().endswith('.pdf')

        if len(pdf_paths) != len(document_paths):
            logger.warning(f"Some non-PDF files were filtered out. Only processing PDFs.")

        semaphore = asyncio.Semaphore(self.max_workers)

        async def extract_single_document(pdf_path: str) -> List[str]:
            async with semaphore:
                try:
                    # Load the PDF
                    with open(pdf_path, "rb") as f:
                        document = f.read()
                    
                    # Create the analyze request
                    analyze_request = AnalyzeDocumentRequest(bytes_source=document)
                    
                    # Async analyze request with specified output format
                    poller = await self.document_intelligent_client.begin_analyze_document(
                        model_id=self.model.value,
                        body=analyze_request,
                        output_content_format="markdown"
                    )
                    
                    logger.info(f"Started table extraction for PDF document '{pdf_path}'")
                    
                    # Wait for result
                    result = await poller.result()
                    
                    # Get the full content (Markdown or HTML depending on format)
                    full_content = result.content
                    
                    # Split into pages using PageBreak delimiters
                    pages = full_content.split("<!-- PageBreak -->")
                    
                    # Filter to only pages containing tables if requested
                    if filter_table_pages:
                        relevant_pages = []
                        for i, page_content in enumerate(pages):
                            # # Check for table markers (both markdown and HTML)
                            # if "<table" in page_content: 
                            #     html_table = extract_table(page_content)
                            #     if html_table:
                            #         htmt_df = pd.read_html(html_table)[0]  # read_html returns a list, take first table
                            #         df_processed = process_multilayer_columns(htmt_df)
                            #         df_processed.columns = [i if list(df_processed.columns)[i].startswith("Unnamed:") else list(df_processed.columns)[i] for i in range(len(df_processed.columns))]
                            #         new_table = to_minimal_markdown(df_processed.fillna(""))
                            #         modified_text = replace_table(page_content, new_table)

                            #         check_result = calculate_table_percentage(modified_text)
                            #         if check_result['table_percentage'] < 65:
                            #             extracted_content = extract_tables_with_preceding_text(page_content)
                            #             if extracted_content:
                            #                 # Prepend page number for context
                            #                 page_with_number = f"### Page {i + 1}\n\n{extracted_content}\n\n"
                            #                 relevant_pages.append(page_with_number)
                            #         else:
                            #             # Prepend page number for context
                            #             page_with_number = f"### Page {i + 1}\n\n{modified_text.strip()}\n\n"
                            #             relevant_pages.append(page_with_number)

                            # elif "|" in page_content:
                            #     # Prepend page number for context
                            #     check_result = calculate_table_percentage(page_content)
                            #     if check_result['table_percentage'] < 65:
                            #         extracted_content = extract_tables_with_preceding_text(page_content)
                            #         if extracted_content:
                            #             # Prepend page number for context
                            #             page_with_number = f"### Page {i + 1}\n\n{extracted_content}\n\n"
                            #             relevant_pages.append(page_with_number)
                            #     else:
                            #         page_with_number = f"### Page {i + 1}\n\n{page_content.strip()}\n\n"
                            #         relevant_pages.append(page_with_number)

                            ######################################
                            if "<table" in page_content or "|" in page_content:
                                extracted_content = extract_tables_with_preceding_text(page_content)
                                if extracted_content:
                                    # Prepend page number for context
                                    page_with_number = f"### Page {i + 1}\n\n{extracted_content}\n\n"
                                    relevant_pages.append(page_with_number)
                            ######################################
                            # # Prepend page number for context
                            # if "<table" in page_content or "|" in page_content:
                            #     page_with_number = f"### Page {i + 1}\n\n{page_content.strip()}\n\n"
                            #     relevant_pages.append(page_with_number)
                                ######################################
                        
                        logger.info(f"Extracted {len(relevant_pages)} pages with tables from '{pdf_path}'")
                        return relevant_pages
                    else:
                        # Return all pages with page numbers
                        all_pages = [
                            f"### Page {i + 1}\n\n{page.strip()}\n\n"
                            for i, page in enumerate(pages)
                        ]
                        logger.info(f"Extracted {len(all_pages)} pages from '{pdf_path}'")
                        return all_pages
                    
                except Exception as e:
                    logger.error(f"Error extracting tables from PDF document '{pdf_path}': {e}")
                    return []

        def extract_tables_with_preceding_text(content: str) -> str:
            """
            Extract tables along with 2 lines of text directly above and below each table.
            Supports both Markdown and HTML tables.
            """
            result_parts = []
            
            # Split content into lines for processing
            lines = content.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check if this line starts a markdown table (contains |)
                if '|' in line and i > 0:
                    # Find the 2 preceding text lines (skip empty lines)
                    preceding_texts = []
                    j = i - 1
                    while j >= 0 and len(preceding_texts) < 2:
                        if lines[j].strip():
                            preceding_texts.insert(0, lines[j].strip())
                        j -= 1
                    
                    # Extract the full table
                    table_lines = []
                    table_start = i
                    while i < len(lines) and '|' in lines[i]:
                        table_lines.append(lines[i])
                        i += 1
                    table_end = i
                    
                    # Find the 2 following text lines (skip empty lines)
                    following_texts = []
                    j = table_end
                    while j < len(lines) and len(following_texts) < 2:
                        if lines[j].strip():
                            following_texts.append(lines[j].strip())
                        j += 1
                    
                    # Add preceding text, table, and following text to result
                    for text in preceding_texts:
                        result_parts.append(text)
                    result_parts.append('\n'.join(table_lines))
                    for text in following_texts:
                        result_parts.append(text)
                    result_parts.append('')  # Empty line separator
                    continue
                
                # Check if this line starts an HTML table
                if '<table' in line.lower():
                    # Find the 2 preceding text lines (skip empty lines and HTML tags)
                    preceding_texts = []
                    j = i - 1
                    while j >= 0 and len(preceding_texts) < 2:
                        stripped = lines[j].strip()
                        if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
                            preceding_texts.insert(0, stripped)
                        j -= 1
                    
                    # Extract the full HTML table
                    table_lines = []
                    table_start = i
                    while i < len(lines):
                        table_lines.append(lines[i])
                        if '</table>' in lines[i].lower():
                            i += 1
                            break
                        i += 1
                    table_end = i
                    
                    # Find the 2 following text lines (skip empty lines and HTML tags)
                    following_texts = []
                    j = table_end
                    while j < len(lines) and len(following_texts) < 2:
                        stripped = lines[j].strip()
                        if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
                            following_texts.append(stripped)
                        j += 1
                    
                    # Add preceding text, table, and following text to result
                    for text in preceding_texts:
                        result_parts.append(text)

                    html_table = '\n'.join(table_lines)
                    htmt_df = pd.read_html(html_table)[0]  # read_html returns a list, take first table
                    df_processed = process_multilayer_columns(htmt_df)
                    df_processed.columns = [i if list(df_processed.columns)[i].startswith("Unnamed:") else list(df_processed.columns)[i] for i in range(len(df_processed.columns))]
                    result_parts.append(to_minimal_markdown(df_processed.fillna("")))

                    for text in following_texts:
                        result_parts.append(text)
                    result_parts.append('')  # Empty line separator
                    continue
                
                i += 1
            
            return_result = '\n'.join(result_parts).strip()
            
            return return_result

        # Process all documents concurrently
        results = await asyncio.gather(*[extract_single_document(path) for path in pdf_paths])

        if single_input:
            return results[0] if results else []
        return results

    def _extract_excel(self, file_path: str) -> List[Dict[str, str]]:
        """
        Convert Excel file with multiple sheets to markdown tables.
        Handles merged cells by filling merged values in all merged cells.
        
        Args:
            file_path (str): Path to the Excel file
        
        Returns:
            dict: Dictionary with sheet names as keys and markdown strings as values
        """
        
        # Load the workbook with openpyxl to handle merged cells
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        markdown_tables = {}
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            
            # Get the data range
            if sheet.max_row == 1 and sheet.max_column == 1:
                # Empty sheet
                markdown_tables[sheet_name] = f"# {sheet_name}\n\n*Empty sheet*\n"
                continue
                
            # Create a matrix to store all cell values
            max_row = sheet.max_row
            max_col = sheet.max_column
            
            # Initialize data matrix with None values
            data_matrix = [[None for _ in range(max_col)] for _ in range(max_row)]
            
            # Fill the matrix with cell values
            for row in range(1, max_row + 1):
                for col in range(1, max_col + 1):
                    cell = sheet.cell(row=row, column=col)
                    data_matrix[row-1][col-1] = cell.value
            
            # Handle merged cells - fill merged regions with the same value
            for merged_range in sheet.merged_cells.ranges:
                # Get the top-left cell value
                min_row, min_col = merged_range.min_row, merged_range.min_col
                merged_value = sheet.cell(row=min_row, column=min_col).value
                
                # Fill all cells in the merged range with the same value
                for row in range(merged_range.min_row, merged_range.max_row + 1):
                    for col in range(merged_range.min_col, merged_range.max_col + 1):
                        data_matrix[row-1][col-1] = merged_value
            
            # Convert to markdown table
            markdown_table = DocumentExtractorV2.convert_matrix_to_markdown(data_matrix, sheet_name)
            markdown_tables[sheet_name] = markdown_table
        
        workbook.close()
        return markdown_tables
    
    @staticmethod
    def convert_matrix_to_markdown(data_matrix: List[List[int]], sheet_name: str) -> str:
        """
        Convert a data matrix to markdown table format.
        
        Args:
            data_matrix (list): 2D list containing cell values
            sheet_name (str): Name of the sheet for the header
        
        Returns:
            str: Markdown formatted table
        """
        if not data_matrix or not any(any(row) for row in data_matrix):
            return f"# {sheet_name}\n\n*No data found*\n"
        
        # Remove completely empty rows from the end
        while data_matrix and all(cell is None or str(cell).strip() == '' for cell in data_matrix[-1]):
            data_matrix.pop()
        
        if not data_matrix:
            return f"# {sheet_name}\n\n*No data found*\n"
        
        # Find the maximum number of columns that contain data
        max_cols = 0
        for row in data_matrix:
            for i in range(len(row) - 1, -1, -1):
                if row[i] is not None and str(row[i]).strip() != '':
                    max_cols = max(max_cols, i + 1)
                    break
        
        if max_cols == 0:
            return f"# {sheet_name}\n\n*No data found*\n"
        
        # Start building markdown
        markdown = f"# {sheet_name}\n\n"
        
        # Process each row
        processed_rows = []
        for row in data_matrix:
            processed_row = []
            for i in range(max_cols):
                if i < len(row):
                    cell_value = row[i]
                    if cell_value is None:
                        processed_row.append("")
                    else:
                        # Convert to string and escape pipe characters
                        cell_str = str(cell_value).replace('|', '\\|').replace('\n', '<br>')
                        processed_row.append(cell_str)
                else:
                    processed_row.append("")
            processed_rows.append(processed_row)
        
        # Remove empty rows from the end
        while processed_rows and all(cell.strip() == '' for cell in processed_rows[-1]):
            processed_rows.pop()
        
        if not processed_rows:
            return f"# {sheet_name}\n\n*No data found*\n"
        
        # Create markdown table
        for i, row in enumerate(processed_rows):
            # Create table row
            markdown += "| " + " | ".join(row) + " |\n"
            
            # Add header separator after first row
            if i == 0:
                markdown += "| " + " | ".join(["---"] * len(row)) + " |\n"
        
        markdown += "\n"
        return markdown

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
        rows = table.get("rowCount", 0)
        cols = table.get("columnCount", 0)

        if rows == 0 or cols == 0:
            return ""

        # Initialize grid
        grid = [["" for _ in range(cols)] for _ in range(rows)]

        # Fill grid with cell content
        for cell in table.get("cells", []):
            row_index = cell.get("rowIndex", 0)
            col_index = cell.get("columnIndex", 0)
            content = cell.get("content", "").strip()

            # Handle cells that span multiple rows/columns
            row_span = cell.get("rowSpan", 1)
            col_span = cell.get("columnSpan", 1)

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

    items = [
        "data/input/Nan Fung/audited-consolidated-financial-statements-for-the-year-ended-16.pdf",
    ]

    async with DocumentExtractorV2() as analyzer:
        pages_md = await analyzer.extract_tables_with_context(
            items[0]
        )

    return pages_md

#########
def process_multilayer_columns(df):
    """
    Process multi-layer column names:
    - Combine layers if they differ
    - Keep only one if they're duplicates
    
    Args:
        df: DataFrame with multi-layer column names (tuples)
    
    Returns:
        DataFrame with processed column names
    """
    new_columns = []
    
    for col in df.columns:
        if isinstance(col, tuple):
            # Remove empty strings and None values
            parts = [str(part).strip() for part in col if part and str(part).strip()]
            
            if len(parts) == 0:
                new_columns.append('')
            elif len(parts) == 1:
                new_columns.append(parts[0])
            else:
                # Check if all parts are the same (case-insensitive)
                if len(set(part.lower() for part in parts)) == 1:
                    # All parts are duplicates, keep only one
                    new_columns.append(parts[0])
                else:
                    # Parts differ, combine them
                    new_columns.append(' - '.join(parts))
        else:
            # Single-level column name
            new_columns.append(str(col))
    
    # Create a copy of the dataframe with new column names
    df_processed = df.copy()
    df_processed.columns = new_columns
    
    return df_processed

# Alternative function with more customization options
def process_multilayer_columns_advanced(df, separator=' - ', case_sensitive=False, remove_empty=True):
    """
    Process multi-layer column names with more customization options.
    
    Args:
        df: DataFrame with multi-layer column names
        separator: String to use when combining different parts (default: ' - ')
        case_sensitive: Whether to consider case when checking for duplicates (default: False)
        remove_empty: Whether to remove empty/None parts (default: True)
    
    Returns:
        DataFrame with processed column names
    """
    new_columns = []
    
    for col in df.columns:
        if isinstance(col, tuple):
            if remove_empty:
                # Remove empty strings, None values, and whitespace-only strings
                parts = [str(part).strip() for part in col 
                        if part is not None and str(part).strip()]
            else:
                parts = [str(part) for part in col]
            
            if len(parts) == 0:
                new_columns.append('')
            elif len(parts) == 1:
                new_columns.append(parts[0])
            else:
                # Check for duplicates
                if case_sensitive:
                    unique_parts = set(parts)
                else:
                    unique_parts = set(part.lower() for part in parts)
                
                if len(unique_parts) == 1:
                    # All parts are duplicates, keep only one
                    new_columns.append(parts[0])
                else:
                    # Parts differ, combine them
                    new_columns.append(separator.join(parts))
        else:
            new_columns.append(str(col))
    
    df_processed = df.copy()
    df_processed.columns = new_columns
    
    return df_processed

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

def extract_table(text):
    """
    Extract HTML table from a long string.
    Returns the table content or None if no table found.
    """
    pattern = r'<table>.*?</table>'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(0)
    return None

def replace_table(text, new_table):
    """
    Replace the HTML table in text with a new table.
    """
    pattern = r'<table>.*?</table>'
    result = re.sub(pattern, new_table, text, flags=re.DOTALL | re.IGNORECASE)
    return result

def calculate_table_percentage(text):
    """
    Calculate the percentage of text that consists of markdown tables.
    
    Args:
        text (str): The input text containing markdown content
        
    Returns:
        dict: Dictionary containing statistics about table content
    """
    # Pattern to match markdown tables (including the header separator row)
    # Matches lines that start with | and contain | characters
    table_pattern = r'(?:^\|.+\|$\n?)+'
    
    # Find all markdown tables
    tables = re.findall(table_pattern, text, re.MULTILINE)
    
    # Calculate total characters in tables
    total_table_chars = sum(len(table) for table in tables)
    
    # Total characters in the entire text
    total_chars = len(text)
    
    # Calculate percentage
    percentage = (total_table_chars / total_chars * 100) if total_chars > 0 else 0
    
    return {
        'total_characters': total_chars,
        'table_characters': total_table_chars,
        'non_table_characters': total_chars - total_table_chars,
        'table_percentage': round(percentage, 2),
        'non_table_percentage': round(100 - percentage, 2),
        'number_of_tables': len(tables)
    }
##########

if __name__ == "__main__":
    result = asyncio.run(main())
    print("result:", result)
    print("len_result:", len(result))