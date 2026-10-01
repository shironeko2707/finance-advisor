"""
Multi-provider embedding abstraction.

Supports: Azure OpenAI, Google Gemini.
Configure via EMBEDDING_PROVIDER environment variable.
"""

from typing import overload, List, TypeAlias, Union, Optional
from abc import ABC, abstractmethod

from loguru import logger

from .settings import get_settings

Embedding: TypeAlias = List[float]


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def embed(self, text: Union[str, List[str]], **kwargs) -> Union[Embedding, List[Embedding]]:
        ...


class AzureEmbeddings(BaseEmbeddingProvider):
    """Azure OpenAI Embeddings provider."""

    def __init__(self) -> None:
        from openai import AsyncAzureOpenAI
        self.client = AsyncAzureOpenAI()
        self._deployment = get_settings().azure_embedding_deployment

    @overload
    async def embed(self, text: str, **kwargs) -> Embedding: ...

    @overload
    async def embed(self, text: List[str], **kwargs) -> List[Embedding]: ...

    async def embed(
        self,
        text: Union[str, List[str]],
        **kwargs,
    ) -> Union[Embedding, List[Embedding]]:
        try:
            embeddings_response = await self.client.embeddings.create(
                input=text,
                model=self._deployment,
                **kwargs,
            )
        except Exception as e:
            preview = text[:50] if isinstance(text, str) else f"[{len(text)} texts]"
            logger.error(f"Azure embedding failed for '{preview}': {e}")
            raise

        if isinstance(text, str):
            return embeddings_response.data[0].embedding
        return [e.embedding for e in embeddings_response.data]


class GeminiEmbeddings(BaseEmbeddingProvider):
    """Google Gemini Embeddings provider using google-generativeai SDK."""

    def __init__(self) -> None:
        import google.generativeai as genai

        settings = get_settings()
        api_key = settings.gemini_api_keys[0] if settings.gemini_api_keys else settings.google_llm_api_key
        genai.configure(api_key=api_key)
        self._model_name = settings.gemini_embedding_model

    @overload
    async def embed(self, text: str, **kwargs) -> Embedding: ...

    @overload
    async def embed(self, text: List[str], **kwargs) -> List[Embedding]: ...

    async def embed(
        self,
        text: Union[str, List[str]],
        **kwargs,
    ) -> Union[Embedding, List[Embedding]]:
        import google.generativeai as genai
        import asyncio

        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model=self._model_name,
                content=text,
                **kwargs,
            )
            return result["embedding"]
        except Exception as e:
            preview = text[:50] if isinstance(text, str) else f"[{len(text)} texts]"
            logger.error(f"Gemini embedding failed for '{preview}': {e}")
            raise


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_EMBEDDING_PROVIDERS = {
    "azure_openai": AzureEmbeddings,
    "gemini": GeminiEmbeddings,
}


def get_embedding_provider(provider: Optional[str] = None) -> BaseEmbeddingProvider:
    """
    Get an embedding provider instance.

    Args:
        provider: Override provider name. Defaults to EMBEDDING_PROVIDER setting.

    Returns:
        An embedding provider instance.
    """
    settings = get_settings()
    target = (provider or settings.embedding_provider).strip().lower()

    cls = _EMBEDDING_PROVIDERS.get(target)
    if cls is None:
        raise ValueError(
            f"Unknown embedding provider '{target}'. "
            f"Available: {list(_EMBEDDING_PROVIDERS.keys())}"
        )

    logger.info(f"Using embedding provider: {target}")
    return cls()


if __name__ == "__main__":
    import asyncio

    embedding = get_embedding_provider()
    print(len(asyncio.run(embedding.embed("I love Vietnam"))))
