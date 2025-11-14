import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
import pandas as pd


load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = "/home/phuongbt/cmcglobal-cert.crt"


class Settings(BaseSettings):

    document_intelligent_endpoint: str

    document_intelligent_api_key: str
    
    extractor_max_workers: int = 32

    azure_openai_endpoint: str

    azure_openai_api_key: str

    openai_api_version: str

    azure_llm_deployment: str
    
    azure_openai_endpoint_2: str

    azure_openai_api_key_2: str

    openai_api_version_2: str

    azure_llm_deployment_2: str

    azure_embedding_deployment: str

    azure_embedding_dims: int = 3072

    milvus_uri: str

    milvus_api_key: str = ""

    milvus_token: str = ""

    milvus_user: str = ""

    milvus_password: str = ""

    milvus_collection_name: str = "kl_auto_report"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    component_df: pd.DataFrame = pd.read_excel('auto_report/config/Symnonym and Components.xlsx')

@lru_cache
def get_settings():
    return Settings()


if __name__ == "__main__":
    print(get_settings())