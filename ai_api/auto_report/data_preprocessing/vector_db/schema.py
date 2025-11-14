from pydantic import BaseModel, ConfigDict
from pymilvus import FieldSchema, DataType, CollectionSchema, Function, FunctionType
from pymilvus.exceptions import FunctionsTypeException

from ..embeddings import Embedding
from ..settings import get_settings


SETTINGS = get_settings()


class MilvusEntityMetadata(BaseModel):
    """Metadata for a Milvus entity."""
    file_name: str | None = None
    page: int | None = None


class MilvusEntity(BaseModel):
    """Represents an entity stored in Milvus."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    """id (str): Unique identifier for the entity."""
    
    content: str
    """content (str): Text content of the entity."""
    
    embedding: Embedding
    """embedding (Embedding): Vector embedding of the content."""

    datetime: str
    """datetime (str): Datetime string in ISO format."""

    metadata: MilvusEntityMetadata
    """metadata (MilvusEntityMetadata): Metadata as JSON (including file name, page number)."""

    @classmethod
    def get_primary_field(cls) -> str:
        return "id"

    @classmethod
    def get_vector_field(cls) -> str:
        return "embedding"

    @classmethod
    def get_sparse_vector_field(cls) -> str:
        return "sparse_vector"

    @classmethod
    def get_embedding_dim(cls) -> int:
        return SETTINGS.azure_embedding_dims

    @classmethod
    def get_schema(cls) -> CollectionSchema:
        """
        Returns the Milvus collection schema for MilvusEntity.

        Returns:
            CollectionSchema: The schema definition for the MilvusEntity collection.
        """
        fields: list[FieldSchema] = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=64,
                description="Unique identifier for the entity"
            ),
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=65535,       # 2^16
                enable_analyzer=True,
                description="Text content of the entity"
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=3072,           # openai embedding large v3 dims      
                description="Vector embedding of the content"
            ),
            # FieldSchema(
            #     name="sparse_vector",
            #     dtype=DataType.SPARSE_FLOAT_VECTOR,
            #     description="Sparse Embedding vector for BM25-like keyword search",
            # ),
            FieldSchema(
                name="datetime",
                dtype=DataType.VARCHAR,
                max_length=32,
                description="Datetime string"
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
                description="Metadata as JSON (including file name, page number.)"
            ),
        ]

        # functions = [
        #         Function(
        #         name="text_bm25_emb",
        #         input_field_names=["content"],
        #         output_field_names=["sparse_vector"],
        #         function_type=FunctionType.BM25,
        #     )
        # ]

        return CollectionSchema(
            fields=fields,
            # functions=functions,
            description="Schema for MilvusEntity collection"
        )
