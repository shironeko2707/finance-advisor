from typing import overload, List, TypeAlias, Union

from loguru import logger
from openai import AsyncAzureOpenAI

from .settings import get_settings

Embedding: TypeAlias = List[float]

class AzureEmbeddings:
    """Azure Embeddings client for generating text embeddings using Azure OpenAI."""

    def __init__(self) -> None:
        """Initializes the AzureEmbeddings client."""
        self.client: AsyncAzureOpenAI = AsyncAzureOpenAI()

    @overload
    async def embed(self, text: str, **kwargs) -> Embedding:
        ...

    @overload
    async def embed(self, text: List[str], **kwargs) -> List[Embedding]:
        ...

    async def embed(
        self, 
        text: Union[str, List[str]], 
        **kwargs
    ) -> Union[Embedding, List[Embedding]]:
        """Generates embeddings for the given text(s).

        Args:
            text (str or List[str]): The input text or list of texts to embed.
            **kwargs: Additional keyword arguments to pass to the embeddings API.

        Returns:
            Embedding or List[Embedding]: The embedding(s) for the input text(s).

        Raises:
            Exception: If the embedding request fails.

        Example:
            >>> embeddings = await AzureEmbeddings().embed("Hello world")
            >>> embeddings = await AzureEmbeddings().embed(["Hello", "world"])
        """
        try:
            embeddings_response = await self.client.embeddings.create(
                input=text,
                model=get_settings().azure_embedding_deployment,
                **kwargs
            )
        except Exception as e:
            logger.error(
                f"Failed to generate embeddings for input '{text[:9]}{'...' if isinstance(text, str) and len(text) > 9 else ''}': {e}"
            )
            raise

        if isinstance(text, str):
            return embeddings_response.data[0].embedding
        return [e.embedding for e in embeddings_response.data]


if __name__ == "__main__":
    import asyncio
    
    embedding = AzureEmbeddings()
    print(len(asyncio.run(embedding.embed("I love Vietnam"))))