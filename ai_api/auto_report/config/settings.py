import os
from typing import List, Dict, Any
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
import pandas as pd


load_dotenv()

# Remove hardcoded cert path - only set if file exists
_cert_path = "/home/phuongbt/cmcglobal-cert.crt"
if os.path.exists(_cert_path):
    os.environ["REQUESTS_CA_BUNDLE"] = _cert_path


class Settings(BaseSettings):

    # ------------------------------------------------------------------
    # Document Intelligence (Azure)
    # ------------------------------------------------------------------
    document_intelligent_endpoint: str = ""
    document_intelligent_api_key: str = ""
    extractor_max_workers: int = 32

    # ------------------------------------------------------------------
    # LLM Provider Configuration
    # ------------------------------------------------------------------
    # Comma-separated list of providers to use. Round-robin across all.
    # Options: "gemini", "claude", "azure_openai"
    # Example: "gemini,claude" to diversify across both providers
    llm_providers: List[str] = ["gemini"]

    # Shared LLM parameters
    llm_temperature: float = 1.0
    llm_max_tokens: int = 4096
    llm_max_retries: int = 2

    # ------------------------------------------------------------------
    # Google Gemini Configuration
    # ------------------------------------------------------------------
    gemini_model_name: str = "gemini-3-pro-preview"
    google_llm_api_key: str = ""
    google_llm_api_key_1: str = ""
    google_llm_api_key_2: str = ""
    google_llm_api_key_3: str = ""

    @property
    def gemini_api_keys(self) -> List[str]:
        """Collect all non-empty Gemini API keys."""
        candidates = [
            self.google_llm_api_key_1,
            self.google_llm_api_key_2,
            self.google_llm_api_key_3,
            self.google_llm_api_key,
        ]
        return [k for k in candidates if k and k != "placeholder_key" and not k.startswith("placeholder")]

    # ------------------------------------------------------------------
    # Anthropic Claude Configuration
    # ------------------------------------------------------------------
    claude_model_name: str = "claude-sonnet-4-20250514"
    claude_api_key: str = ""
    claude_api_key_1: str = ""
    claude_api_key_2: str = ""

    @property
    def claude_api_keys(self) -> List[str]:
        """Collect all non-empty Claude API keys."""
        candidates = [
            self.claude_api_key_1,
            self.claude_api_key_2,
            self.claude_api_key,
        ]
        return [k for k in candidates if k and k != "placeholder_key" and not k.startswith("placeholder")]

    # ------------------------------------------------------------------
    # Azure OpenAI Configuration
    # ------------------------------------------------------------------
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    openai_api_version: str = "2024-02-15-preview"
    azure_llm_deployment: str = "gpt-4"

    azure_openai_endpoint_2: str = ""
    azure_openai_api_key_2: str = ""
    openai_api_version_2: str = "2024-02-15-preview"
    azure_llm_deployment_2: str = "gpt-4"

    @property
    def azure_openai_configs(self) -> List[Dict[str, str]]:
        """Collect all Azure OpenAI endpoint configurations."""
        configs = []
        if self.azure_openai_api_key:
            configs.append({
                "endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "api_version": self.openai_api_version,
                "deployment": self.azure_llm_deployment,
            })
        if self.azure_openai_api_key_2:
            configs.append({
                "endpoint": self.azure_openai_endpoint_2,
                "api_key": self.azure_openai_api_key_2,
                "api_version": self.openai_api_version_2,
                "deployment": self.azure_llm_deployment_2,
            })
        return configs

    # ------------------------------------------------------------------
    # Embedding Configuration
    # ------------------------------------------------------------------
    # Options: "azure_openai", "gemini", "local"
    embedding_provider: str = "azure_openai"

    # Azure Embedding
    azure_embedding_deployment: str = "text-embedding-3-large"
    azure_embedding_dims: int = 3072

    # Gemini Embedding
    gemini_embedding_model: str = "models/text-embedding-004"

    # ------------------------------------------------------------------
    # Vector Database (Milvus)
    # ------------------------------------------------------------------
    milvus_uri: str = "http://localhost:19530"
    milvus_api_key: str = ""
    milvus_token: str = ""
    milvus_user: str = ""
    milvus_password: str = ""
    milvus_collection_name: str = "kl_auto_report"

    # ------------------------------------------------------------------
    # Pydantic Settings Config
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # ------------------------------------------------------------------
    # Component DataFrame (loaded from Excel)
    # ------------------------------------------------------------------
    component_df: pd.DataFrame = pd.DataFrame()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load component Excel if available
        excel_path = "auto_report/config/Symnonym and Components.xlsx"
        if os.path.exists(excel_path):
            object.__setattr__(self, "component_df", pd.read_excel(excel_path))


@lru_cache
def get_settings():
    return Settings()


if __name__ == "__main__":
    s = get_settings()
    print(f"LLM Providers: {s.llm_providers}")
    print(f"Gemini keys: {len(s.gemini_api_keys)}")
    print(f"Claude keys: {len(s.claude_api_keys)}")
    print(f"Azure configs: {len(s.azure_openai_configs)}")
    print(f"Embedding provider: {s.embedding_provider}")
