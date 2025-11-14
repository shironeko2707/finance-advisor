from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):

    document_intelligent_endpoint: str

    document_intelligent_api_key: str

    azure_openai_endpoint: str

    azure_openai_api_key: str

    openai_api_version: str

    azure_llm_deployment: str

    azure_embedding_deployment: str

    azure_embedding_dims: int

    milvus_uri: str

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