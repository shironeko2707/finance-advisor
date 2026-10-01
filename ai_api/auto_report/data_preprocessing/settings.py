from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):

    document_intelligent_endpoint: str = ""
    document_intelligent_api_key: str = ""

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    openai_api_version: str = "2024-02-15-preview"
    azure_llm_deployment: str = "gpt-4"

    azure_embedding_deployment: str = "text-embedding-3-large"
    azure_embedding_dims: int = 3072

    # Embedding provider: "azure_openai" or "gemini"
    embedding_provider: str = "azure_openai"

    # Gemini embedding config
    gemini_embedding_model: str = "models/text-embedding-004"
    google_llm_api_key: str = ""
    google_llm_api_key_1: str = ""
    google_llm_api_key_2: str = ""

    @property
    def gemini_api_keys(self):
        candidates = [self.google_llm_api_key_1, self.google_llm_api_key_2, self.google_llm_api_key]
        return [k for k in candidates if k and not k.startswith("placeholder")]

    milvus_uri: str = "http://localhost:19530"
    milvus_api_key: str = ""
    milvus_token: str = ""
    milvus_user: str = ""
    milvus_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


if __name__ == "__main__":
    print(get_settings())
