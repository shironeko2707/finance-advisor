import os
import hashlib
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from dotenv import load_dotenv
from loguru import logger
import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchableField,
    SearchIndex,
    SearchFieldDataType,
)

from auto_report.agent.utils.state import InjectedState
from .data_preprocessing import DocumentExtractor
from .data_preprocessing.doc_extractor_v2_tamht import DocumentExtractorV2
from .agent import WorkflowState, FillInValues, graph
from .helpers import write_fill_in_values_to_worksheet
from auto_report.agent.utils.util_function import template_to_markdown, file_category_router
from .agent.bi_weekly_logic import main_bi_weekly
import warnings

warnings.filterwarnings("ignore")  # This ignores all warnings

load_dotenv()

# Configuration constants
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "1"))
OUTPUT_TEMPLATE_DIRS = os.getenv("OUTPUT_TEMPLATE_DIRS", "./run_data/output")


def _generate_index_name(document_paths: List[str]) -> str:
    """
    Generate Azure Search compliant index name from document paths.
    
    Args:
        document_paths: List of document file paths
        
    Returns:
        Valid Azure Search index name
    """
    # Create index name that meets Azure Search requirements:
    # - only lowercase letters, digits, or dashes
    # - cannot start or end with dashes
    # - max 128 characters
    document_names = "-".join(
        os.path.splitext(os.path.basename(doc))[0] for doc in document_paths
    )
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_index_name = f"{document_names}-{date_str}"

    # Hash the base index name and get the first 128 characters
    hashed_index_name = hashlib.sha256(base_index_name.encode()).hexdigest()[:128]
    return hashed_index_name


async def _create_search_index(index_client: SearchIndexClient, index_name: str) -> bool:
    """
    Create Azure Search index with predefined schema.
    
    Args:
        index_client: Azure Search index client
        index_name: Name of the index to create
        
    Returns:
        True if successful, False otherwise
    """
    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="filename", type=SearchFieldDataType.String),
            SimpleField(name="page", type=SearchFieldDataType.Int32),
            SimpleField(name="created_date", type=SearchFieldDataType.DateTimeOffset, sortable=True)
        ]
        index = SearchIndex(name=index_name, fields=fields)
        result = await index_client.create_index(index)
        logger.info(f"Index '{result.name}' created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        return False
    finally:
        await index_client.close()


async def index_document(document_path: str | List[str]) -> Optional[str]:
    """
    Index documents in Azure Search and return the index name.
    
    Args:
        document_path: Single document path or list of document paths
        
    Returns:
        Index name if successful, None otherwise
    """
    # Normalize document paths to a list
    document_paths: List[str] = (
        [document_path] if isinstance(document_path, str) else document_path
    )

    # Extract tables from documents
    async with DocumentExtractorV2() as extractor:
        documents = await extractor.extract_tables_with_context(document_paths) # (DocumentExtractorV2) extractor.extract_tables_with_context(document_paths)
        if not documents:
            logger.info("No documents extracted.")
            return None

    # Generate Azure Search compliant index name
    index_name = _generate_index_name(document_paths)
    
    # Initialize Azure Search clients
    credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    index_client = SearchIndexClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
        credential=credential
    )
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
        index_name=index_name, 
        credential=credential
    )

    # Create the index
    if not (await _create_search_index(index_client, index_name)):
        return None

    # Prepare and upload documents
    uploaded_data = _prepare_documents_for_upload(documents, document_paths)
    
    # Check if any tables were extracted
    if not uploaded_data:
        logger.warning("No tables found in the provided documents. Cannot create index.")
        return None
    
    try:
        await search_client.upload_documents(documents=uploaded_data)
        logger.info(f"Uploaded {len(uploaded_data)} tables to index '{index_name}'.")
        return index_name
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        return None
    finally:
        await asyncio.gather(index_client.close(), search_client.close())


def _prepare_documents_for_upload(documents: List[Any], document_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Prepare documents for Azure Search upload.
    
    Args:
        documents: Extracted document objects
        document_paths: Original document file paths
        
    Returns:
        List of document dictionaries ready for upload
    """
    uploaded_data = []
    for doc, path in zip(documents, document_paths):
        if path.endswith('.pdf'):
            i = 0
            for table_text in doc:
                try:
                    page_number = table.cells[0].bounding_regions[0].page_number
                except Exception:
                    page_number = None
                
                # preceding_text = _get_preceding_text(doc, table)
                # content_table = DocumentExtractor.azure_tables_to_markdown(table)
                # content_table = content_table.replace("\n:selected:", "")
                uploaded_data.append({
                    "id": hashlib.sha256(f"{os.path.basename(path)}_{i}".encode()).hexdigest()[:32],
                    "filename": os.path.basename(path),
                    "page": page_number,
                    "content": table_text, # preceding_text + '\n' + content_table,
                    "created_date": datetime.now()
                })
                i += 1
        else:
            def excel_column_name(n):
                """Convert a column index (0-based) to Excel-style column name."""
                name = ''
                while n >= 0:
                    name = chr(n % 26 + ord('A')) + name
                    n = n // 26 - 1
                return name

            def rename_df_like_excel(df):
                """Rename columns to Excel letters and set index to 1-based."""
                # Rename columns
                df.columns = [excel_column_name(i) for i in range(len(df.columns))]
                
                # Reset index to start at 1
                df.index = range(1, len(df) + 1)
                
                return df

            i = 0
            for sheet_name, table in doc:
                uploaded_data.append({
                    "id": hashlib.sha256(f"{os.path.basename(path)}_{i}".encode()).hexdigest()[:32],
                    "filename": os.path.basename(path),
                    "page": i,
                    "content": rename_df_like_excel(table).fillna('').to_markdown(),
                    "created_date": datetime.now()
                })
                i += 1
    
    return uploaded_data


def load_template(template_path: str) -> Tuple[Workbook, List[Worksheet]]:
    """
    Load Excel template and return workbook with worksheets.
    
    Args:
        template_path: Path to Excel template file
        
    Returns:
        Tuple of (workbook, list of worksheets excluding cover sheets)
    """
    if template_path.endswith(".xlsm"):
        report_workbook = openpyxl.load_workbook(template_path, keep_vba=True)
    else:
        report_workbook = openpyxl.load_workbook(template_path)
    worksheets = [
        report_workbook[sheetname] 
        for sheetname in report_workbook.sheetnames 
        if "cover" not in sheetname.lower()
    ]
    
    return report_workbook, worksheets


def prepare_report_state(template_path, ws: Worksheet, index_name: str) -> WorkflowState:
    """
    Prepare report state for processing.
    
    Args:
        ws: Excel worksheet
        index_name: Azure Search index name
        
    Returns:
        WorkflowState object ready for processing
    """
    return WorkflowState(
        messages= [HumanMessage(content="")],
        template_path= template_path,
        category_router=file_category_router(ws.title),
        sheet_name= ws.title,
        report_template=template_to_markdown(ws),
        worksheet=ws,
        index_name=index_name,
        injected_state={
            "worksheet": ws,
        }
    )


async def run_report_graph(state: WorkflowState, config: Dict[str, Any]) -> WorkflowState:
    """
    Run the report generation graph with given state and config.
    
    Args:
        state: WorkflowState object
        config: Configuration dictionary
        
    Returns:
        Updated WorkflowState with results
    """
    def check_bi_weekly(sheet):
        # Define the region to search (e.g., A1 to D10)
        search_range = sheet['E1':'E1']
        target_string = "Bi-Weekly"

        # Check if any cell matches the target string
        for row in search_range:
            for cell in row:
                if cell.value == None:
                    continue
                else:
                    if target_string in cell.value or target_string.lower() in cell.value.lower():
                        return target_string

        return "other"

    # print("router condition")
    if check_bi_weekly(state['worksheet']) == "Bi-Weekly":
        return await main_bi_weekly(state)
    else:   
        return await graph.ainvoke(input=state, config=config)

async def main(
    template_path: str, 
    document_path: str | List[str], 
    **kwargs
) -> str:
    """
    Main function to process documents and generate reports.
    
    Args:
        template_path: Path to Excel template file
        document_path: Single document path or list of document paths
        **kwargs: Additional configuration options
        
    Returns:
        Path to the generated output file
        
    Raises:
        RuntimeError: If document indexing fails
    """
    # # Index documents
    index_name = await index_document(document_path)
    if index_name is None:
        raise RuntimeError("Failed to index documents")

    # Load template
    workbook, worksheets = load_template(template_path)

    # Process worksheets concurrently
    max_workers = kwargs.get("max_workers", MAX_WORKERS)
    results = await _process_worksheets_concurrent(template_path, worksheets, '0cdade3927bd5d414f1f7901875977ce31e53c3ff7e6ba98ca7f9592aba13fda', max_workers) # index_name

    ## Shorten
    # Tencent: 41f2da4ce58437659275b69bce17dba73ffd7f9e08e59716e10e8c0bd29b9ddb
    # Alibaba: 0cdade3927bd5d414f1f7901875977ce31e53c3ff7e6ba98ca7f9592aba13fda, fd6f7680c11acf51e7855dbba08d8518f32c4a468c9c1a3e1d6e6b9fb29b4ef2
    # Trip: 585f38677cde3ef5840a4652fcac6f200100b2827dbbd0638b5200fe5bce3f8b
    ##########

    # UBS: 67d83111db8f2c39aff5db4c03584244a54e8caa0a7aba56bcdee88f4c5bf40c
    # Kingboard: 31771435a03badb762fff1f6ea17c2b85777684445eef5a533ed867d5af90392
    # Lining: 79c595e44d10c7a7d4d065759077e6b5f8a0153d6c414fd41995182e90a569eb
    # Nanfun: 8d08b8e6c8df5e0d1001f0b8d42004e8aceeccee5f3dfb581ec936606ac1e17b
    # Nongfu: c7c1907f6c381fc75781607c751ef61348c545d8a4314640bc0373255c699f3e
    # SHKP: 20c22eed9c31353ce6b5b57a41bebab362194ba4327f2670bc5b2d3e6d5b5982
    # SHKP New: 9e8df5e4a9d74bdb01095f91df74f08a9d894a71d7dc2acc8122fea0421879ff
    # Tencent: cbb82aed4ae281d2f985e739533740d926dd9444f7be937284d1552cf7d10e51
    # Trip: 44243f60a47d05d4ba4f45ea3c94919695256cc747ba61f3d3fb89a757fe9a09
    # UOBKH: 9f4eaf04f278211d113396f7a7f752a750c89211deb41b82677e456ac1d9295e
    # Wilmar: f7e215da9b0bd5b8fec63d3aac891efb2dc0b5df5810295c132995c2f9232cde
    # Xiaomi: 938eab06d577c13d2dab26aded6e3d678cacdcf8ecc63b3042bb378985ab0390
    # GenM: acf5a0b59a1c373560abcb97123ec9e8d58bfef7438003baaf9a5c4e7cfb98d3
    # BNP (condense): 90853409e99c78391d0f239a0000c21706bacd7be97fb520136ff58758811965
    # CQNC: 75f06e1151de9c756a036adc87027177348cf923159ae1134cca01a6c7818da1
    # China Vanke: 62ad1d62b8a6d0ad2c82c98b19da2d66baa38d47687fa636470fd49b9a1f9015
    # HSBC: 74f988bfdd9cf8b0b6fda6e21dd24207467c6857b425f7e184e3f2bb19556108
    # Hutch: 47e59b17cf7d163f1dc91d0b89fe010bdcaf3567955ea4911d4e22738cd6344d

    # UOB (condense): d685e103a84e4dff1aa07b9b96c915f19060a3434234c170a94d9fe87fa08e77
    # UOB (condense update): e1d69d932457addd1fbb8d37d5f5d4c541f2cdcec04d154ac4ac14e63a2c67e6
    # Haw Par (condense): 6ed0380d3a7952f5d0c470d30a93438b3a099913b871a0e4bb0d13dc42ae907b
    # Kraft Heinz (condense): dff36bf1630335140ccea2d64daaf7e25cefd4a4c0cae1dda01d3c8bbb880467
    # SingLang (condense): 7fa862c49dfccf985f0fe887d620e38c62bde3da254b577c6486e5046a344ecd
    # Straits Trading (condense): f8e192b5dc455b0cd0d831ffce17c09fb998e5714c893f3074a54f1e91efc1b8
    # Yanlord (condense): f90a18bb43bd7df70ccf3b25e0ec91e791ba3619e65bff2042ee8255064fcd2c

    # NWD: 8675d6d686a8a185724a3beaaf5f51095b912e2e1849cd10b0a45f6732952d07, (2 line context): 
    # NWD (condense no 1H): cb193aa94315300df456cc0edc4d2a3f876ae88a78ef08c4904b92815bf3a3ad
    # NWD (condense): 2caf0ef0c5009dd19aa67385fa22648c560c9b892b814b016ee822fa83e254c4
    # SIA: c1ad4689e189658e14a2427cea61df6297c8d1a6c4ddaf9ae2d54429abcaf4cd
    # SIA (Condense No 2025): b6e268bc198047ec0acd35edde66e96ca4612f4ea3e061aa41eecf414c023eb9
    # Grab: 448c74b416685ef2e014e530a202b506c18b0c4121cbf05aed8533067e391550
    # Grab (4Q 2024): 73238f9d8016072b18c58c491a4b194a77bacddcdce7331df420c9118cb1b4de
    # Grab (4Q 2024 update): 0d66f60dd85850c878b608b21fe8cd3277cbc5ed433211dcaf52b8fbe303af31
    # Grab (4Q 2024 1 page new): b3a0a62770049dde1d154e10b4590246ba6a9eba407d79ff6c047fddc7c56e5d, (2 line context): 0ffdccee1a43a7c2777d88a8feecd11f606162cc4dcee6f166d58967abb14233
    # Grab (condense): dec4d198e31cd01e70bfc041fbe9a8444a5e622b3ca4427c819552ea5417acb9

    # Bi-weekly (Conglomerate): 

    # Save output file
    output_path = _save_output_file(workbook, template_path)
    logger.info(f"Workbook saved to {output_path}")
    
    return output_path


async def _process_worksheets_concurrent(
    template_path: str,
    worksheets: List[Worksheet], 
    index_name: str, 
    max_workers: int
) -> List[WorkflowState]:
    """
    Process worksheets concurrently with rate limiting.
    
    Args:
        worksheets: List of Excel worksheets to process
        index_name: Azure Search index name
        max_workers: Maximum number of concurrent workers
        
    Returns:
        List of WorkflowState results
    """
    semaphore = asyncio.Semaphore(max_workers)
    
    async def run_graph(ws: Worksheet) -> WorkflowState:
        async with semaphore:
            state = prepare_report_state(template_path, ws, index_name)
            config = {"configurable": {"thread": _make_thread_id(ws)}}
            return await run_report_graph(state, config)

    tasks = [run_graph(ws) for ws in worksheets]
    return await asyncio.gather(*tasks)


def _make_thread_id(ws: Worksheet) -> str:
    """Generate unique thread ID for worksheet processing."""
    sheetname = ws.title
    now_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
    base = f"{sheetname}-{now_str}"
    return hashlib.sha256(base.encode()).hexdigest()


def _save_output_file(workbook: Workbook, template_path: str) -> str:
    """
    Save workbook to output directory.
    
    Args:
        workbook: Excel workbook to save
        template_path: Original template path
        
    Returns:
        Path to saved output file
    """
    os.makedirs(OUTPUT_TEMPLATE_DIRS, exist_ok=True)
    template_filename = os.path.basename(template_path)
    output_path = os.path.join(OUTPUT_TEMPLATE_DIRS, template_filename)
    workbook.save(output_path)

    return output_path

def _get_preceding_text(result, table) -> str:
        """
        Extract text that appears immediately before the table.
        
        Args:
            result: AnalyzeResult object
            table: Table object
            
        Returns:
            str: Text content appearing before the table
        """
        if not result.paragraphs:
            return ""
        
        # Get the table's bounding region (first cell's region)
        table_start_page = table.bounding_regions[0].page_number if table.bounding_regions else 1
        
        # Find paragraphs on the same page that appear before the table
        preceding_paragraphs = []
        for paragraph in result.paragraphs:
            if not paragraph.bounding_regions:
                continue
                
            para_page = paragraph.bounding_regions[0].page_number
            
            # Only consider paragraphs on the same page as the table
            if para_page == table_start_page:
                # Check if paragraph appears before table (basic position check)
                if table.bounding_regions and paragraph.bounding_regions:
                    para_top = paragraph.bounding_regions[0].polygon[0].y
                    table_top = table.bounding_regions[0].polygon[0].y
                    
                    if para_top < table_top:
                        preceding_paragraphs.append((para_top, paragraph.content))
        
        # Sort by vertical position and get the last paragraph (closest to table)
        if preceding_paragraphs:
            preceding_paragraphs.sort(key=lambda x: x[0])
            return preceding_paragraphs[-1][1]
        
        return ""
