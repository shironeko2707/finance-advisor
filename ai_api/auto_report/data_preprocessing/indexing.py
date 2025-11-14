import os
import hashlib
import asyncio
import datetime

from .embeddings import AzureEmbeddings
from .doc_intelligence import DocumentExtractor
from .vector_db.milvus import MilvusDB
from .vector_db.schema import MilvusEntity, MilvusEntityMetadata

async def indexing(
    doc_path: str,
    collection_name: str = "documents"
):
    """
    Reads a document, extracts tables, embeds them, and inserts into Milvus vector database.

    Args:
        doc_path (str): Path to the document file.
        collection_name (str): Name of the Milvus collection to insert into.
    """
    # 1. Extract tables from document
    async with DocumentExtractor() as extractor:
        result = await extractor.extract(doc_path, pages="1-10")
        if not result or not hasattr(result, "tables"):
            print(f"No tables found in document: {doc_path}")
            return

        tables = result.tables

    # 2. Convert tables to markdown
    markdown_tables = []
    for table in tables:
        markdown = DocumentExtractor.azure_tables_to_markdown(table)
        if markdown.strip():
            markdown_tables.append(markdown)

    if not markdown_tables:
        print(f"No valid markdown tables extracted from: {doc_path}")
        return

    # 3. Embed markdown tables
    embedder = AzureEmbeddings()
    embeddings = await embedder.embed(markdown_tables)

    # 4. Prepare Milvus entities
    entities = []
    for i, (table, markdown, embedding) in enumerate(zip(tables, markdown_tables, embeddings)):

        # Get just the file name (no path)
        file_name = os.path.basename(doc_path)
        now_iso = datetime.datetime.now().isoformat()
        raw_id = f"{file_name}_{now_iso}_table_{i}"
        id_hash = hashlib.sha256(raw_id.encode()).hexdigest()[:32]
        
        entity = MilvusEntity(
            id=id_hash,
            content=markdown,
            embedding=embedding,
            datetime=now_iso,
            metadata=MilvusEntityMetadata(
                file_name=file_name,
                page=table.cells[0].bounding_regions[0].page_number
            )
        )
        entities.append(entity)

    # 5. Insert into Milvus
    milvus = MilvusDB()
    await milvus.drop_collection(collection_name)
    await milvus.create_collection(collection_name)
    await milvus.insert(collection_name, entities)

    print(f"Indexed {len(entities)} tables from {doc_path} into collection '{collection_name}'.")
    

if __name__ == "__main__":
    import asyncio

    asyncio.run(indexing(
        doc_path="data/input/Alibaba/Alibaba Group Announces December Quarter 2024 Results.pdf",
        collection_name="kl_test"
    ))