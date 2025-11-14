import asyncio
from typing import Optional, List, Dict, Any, Union

from loguru import logger
from pymilvus import AsyncMilvusClient, MilvusClient
from pymilvus.milvus_client import IndexParams

from ..settings import get_settings
from .schema import MilvusEntity


class MilvusDB:
    def __init__(
        self,
        uri: Optional[str] = None,
        token: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize MilvusDB client.

        Args:
            uri (Optional[str]): Milvus URI.
            token (Optional[str]): Authentication token.
            user (Optional[str]): Username for authentication.
            password (Optional[str]): Password for authentication.
            **kwargs: Additional keyword arguments for AsyncMilvusClient.
        """
        settings = get_settings()
        self.client = AsyncMilvusClient(
            uri=uri or settings.milvus_uri,
            user=user or settings.milvus_user,
            password=password or settings.milvus_password,
            token=token or settings.milvus_token,
            **kwargs
        )

    async def create_database(
        self,
        db_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new database in Milvus if it does not exist.

        Args:
            db_name (str): Name of the database to create.
            properties (Optional[Dict[str, Any]]): Additional properties for the database.

        Returns:
            bool: True if database created or already exists, False if failed.
        """
        try:
            if db_name not in self.client.list_databases():
                await self.client.create_database(db_name, properties=properties or {})
            else:
                logger.warning(f"Database '{db_name}' already exists. Skipping creation.")
            return True
        except Exception as e:
            logger.error(f"Failed to create database '{db_name}': {e}")
            return False

    async def create_collection(self, collection_name: str) -> None:
        """
        Create a new collection in Milvus with the schema defined in MilvusEntity.

        Args:
            collection_name (str): Name of the collection to create.
        """
        # Check if collection exists before proceeding
        if await self.client.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists.")
            return

        # Cache schema info
        vector_field: str = MilvusEntity.get_vector_field()
        sparse_field: str = MilvusEntity.get_sparse_vector_field()
        primary_field: str = MilvusEntity.get_primary_field()
        embedding_dim: int = MilvusEntity.get_embedding_dim()

        schema = MilvusEntity.get_schema()

        # Create collection asynchronously and wait for completion
        await self.client.create_collection(
            collection_name=collection_name,
            schema=schema,
            dimension=embedding_dim,
            primary_field_name=primary_field,
            vector_field_name=vector_field,
        )
        logger.info(f"Collection {collection_name} created successfully!")

        async def _create_index(
            field_name: str,
            index_type: str,
            metric_type: str,
            params: Dict[str, Any]
        ) -> None:
            """
            Helper to create index for a field.

            Args:
                field_name (str): Name of the field to index.
                index_type (str): Type of index.
                metric_type (str): Metric type for index.
                params (Dict[str, Any]): Index parameters.
            """
            try:
                index_params = MilvusClient.prepare_index_params()
                index_params.add_index(
                    field_name=field_name,
                    index_type=index_type,
                    metric_type=metric_type,
                    params=params
                )
                await self.client.create_index(
                    collection_name=collection_name,
                    index_params=index_params
                )
                logger.info(f"Index {field_name} created successfully!")
            except Exception as e:
                logger.error(f"Failed to create index {field_name}: {e}")

        # Create indexes
        await asyncio.gather(
            _create_index(vector_field, "HNSW", "COSINE", {"M": 48, "efConstruction": 200}),
            # _create_index(sparse_field, "SPARSE_INVERTED_INDEX", "BM25", {"inverted_index_algo": "DAAT_MAXSCORE"})
        )

    async def insert(
        self,
        collection_name: str,
        data: Union[MilvusEntity, List[MilvusEntity]],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Insert or upsert data into the collection.

        Args:
            collection_name (str): The name of the collection to insert data into.
            data (MilvusEntity | List[MilvusEntity]): The data to insert into the collection.
            upsert (bool): Whether to upsert data into the collection.

        Returns:
            Dict[str, Any]: Result of the insert/upsert operation.
        """
        # Ensure data is a list
        if isinstance(data, MilvusEntity):
            data = [data]
        elif not isinstance(data, list):
            raise TypeError("data must be a MilvusEntity or a list of MilvusEntity objects.")

        # Convert class to json data
        entities: List[Dict[str, Any]] = [d.model_dump(exclude_none=True) for d in data if d is not None]
        if not entities:
            logger.warning("No valid entities to insert.")
            return {}

        # Insert/upsert
        func = self.client.upsert if upsert else self.client.insert
        result = await func(
            collection_name=collection_name,
            data=entities,
        )

        async def _flush_collection() -> None:
            """
            Flush the collection to ensure data is persisted.
            """
            try:
                await self.client.flush(collection_name=collection_name)
            except Exception as e:
                logger.error(f"Flush failed for collection {collection_name}: {e}")

        asyncio.create_task(_flush_collection())

        return result

    async def search(
        self,
        collection_name: str,
        query_vectors: List[Any],
        vector_field: str,
        limit: int = 10,
        filter: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for similar vectors in the specified collection.

        Args:
            collection_name (str): The name of the collection to search.
            query_vectors (List[Any]): List of query vectors.
            vector_field (str): The name of the vector field to search.
            limit (int): Number of results to return.
            filter (Optional[str], optional): Optional filter expression.
            params (Optional[Dict[str, Any]], optional): Search parameters.
            output_fields (Optional[List[str]], optional): Fields to include in the result.

        Returns:
            Dict[str, Any]: Search results.
        """
        if params is None:
            params = {"metric_type": "COSINE", "params": {"ef": 128}}
        if output_fields is None:
            output_fields = []

        try:
            results = await self.client.search(
                collection_name=collection_name,
                data=query_vectors,
                anns_field=vector_field,
                param=params,
                limit=limit,
                expr=filter,
                output_fields=output_fields,
            )
            return results
        except Exception as e:
            logger.error(f"Search failed in collection {collection_name}: {e}")
            return {}

    async def drop_collection(self, collection_name: str) -> bool:
        """
        Drop (delete) a collection from Milvus.

        Args:
            collection_name (str): The name of the collection to drop.

        Returns:
            bool: True if the collection was dropped successfully, False otherwise.
        """
        try:
            await self.client.drop_collection(collection_name)
            logger.info(f"Collection '{collection_name}' dropped successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to drop collection '{collection_name}': {e}")
            return False