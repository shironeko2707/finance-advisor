"""
Multi-provider LLM pipeline with load balancing.

Supports: Google Gemini, Anthropic Claude, Azure OpenAI.
Each provider can have multiple API keys for round-robin load balancing.
Configure via environment variables and LLM_PROVIDER setting.
"""

from typing import List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger

from auto_report.agent.utils.load_balancing import LoadBalancerLLM
from ...config import get_settings


settings = get_settings()


# ---------------------------------------------------------------------------
# Provider factory functions
# ---------------------------------------------------------------------------

def _create_gemini_instances() -> List[BaseChatModel]:
    """Create Google Gemini LLM instances from configured API keys."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    instances: List[BaseChatModel] = []
    model_name = settings.gemini_model_name

    for i, key in enumerate(settings.gemini_api_keys, 1):
        if key and key != "placeholder_key" and not key.startswith("placeholder"):
            instances.append(
                ChatGoogleGenerativeAI(
                    model=model_name,
                    api_key=key,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                    max_retries=settings.llm_max_retries,
                )
            )
            logger.info(f"Gemini instance #{i} created (model={model_name})")

    if not instances:
        logger.warning("No valid Gemini API keys found. Gemini provider unavailable.")

    return instances


def _create_claude_instances() -> List[BaseChatModel]:
    """Create Anthropic Claude LLM instances from configured API keys."""
    from langchain_anthropic import ChatAnthropic

    instances: List[BaseChatModel] = []
    model_name = settings.claude_model_name

    for i, key in enumerate(settings.claude_api_keys, 1):
        if key and key != "placeholder_key" and not key.startswith("placeholder"):
            instances.append(
                ChatAnthropic(
                    model_name=model_name,
                    api_key=key,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                    max_retries=settings.llm_max_retries,
                )
            )
            logger.info(f"Claude instance #{i} created (model={model_name})")

    if not instances:
        logger.warning("No valid Claude API keys found. Claude provider unavailable.")

    return instances


def _create_azure_openai_instances() -> List[BaseChatModel]:
    """Create Azure OpenAI LLM instances from configured endpoints."""
    from langchain_openai import AzureChatOpenAI

    instances: List[BaseChatModel] = []

    azure_configs = settings.azure_openai_configs
    for i, cfg in enumerate(azure_configs, 1):
        if (
            cfg["api_key"]
            and cfg["api_key"] != "placeholder_key"
            and not cfg["api_key"].startswith("placeholder")
        ):
            instances.append(
                AzureChatOpenAI(
                    model=cfg["deployment"],
                    azure_endpoint=cfg["endpoint"],
                    api_key=cfg["api_key"],
                    api_version=cfg["api_version"],
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                    max_retries=settings.llm_max_retries,
                )
            )
            logger.info(f"Azure OpenAI instance #{i} created (deployment={cfg['deployment']})")

    if not instances:
        logger.warning("No valid Azure OpenAI configs found. Azure provider unavailable.")

    return instances


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

_PROVIDER_FACTORIES = {
    "gemini": _create_gemini_instances,
    "claude": _create_claude_instances,
    "azure_openai": _create_azure_openai_instances,
}


def _build_llm_instances() -> List[BaseChatModel]:
    """
    Build LLM instances based on LLM_PROVIDERS configuration.

    Supports multiple providers in a single pipeline for diversification.
    E.g. LLM_PROVIDERS="gemini,claude" will round-robin across both.
    """
    all_instances: List[BaseChatModel] = []

    for provider_name in settings.llm_providers:
        provider_name = provider_name.strip().lower()
        factory = _PROVIDER_FACTORIES.get(provider_name)

        if factory is None:
            logger.warning(
                f"Unknown LLM provider '{provider_name}'. "
                f"Available: {list(_PROVIDER_FACTORIES.keys())}"
            )
            continue

        try:
            instances = factory()
            all_instances.extend(instances)
        except Exception as e:
            logger.error(f"Failed to create {provider_name} instances: {e}")

    if not all_instances:
        logger.error(
            "No LLM instances could be created from any provider! "
            "Check your API keys and LLM_PROVIDERS setting."
        )
        raise RuntimeError("No LLM provider available. Cannot proceed.")

    logger.info(
        f"LLM pipeline ready: {len(all_instances)} instance(s) across "
        f"providers [{', '.join(settings.llm_providers)}]"
    )
    return all_instances


def get_chat_model(
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    provider: Optional[str] = None,
    **kwargs,
) -> BaseChatModel:
    """
    Create a single LLM instance for the specified (or default) provider.

    Args:
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        top_p: Nucleus sampling parameter.
        provider: Override the default provider. One of "gemini", "claude", "azure_openai".
        **kwargs: Additional arguments passed to the provider constructor.

    Returns:
        A BaseChatModel instance.
    """
    target = provider or settings.llm_providers[0]
    target = target.strip().lower()

    override_kwargs = {}
    if max_tokens is not None:
        override_kwargs["max_tokens"] = max_tokens
    if temperature is not None:
        override_kwargs["temperature"] = temperature

    if target == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            api_key=settings.gemini_api_keys[0],
            top_p=top_p,
            **override_kwargs,
            **kwargs,
        )

    if target == "claude":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=settings.claude_model_name,
            api_key=settings.claude_api_keys[0],
            top_p=top_p,
            **override_kwargs,
            **kwargs,
        )

    if target == "azure_openai":
        from langchain_openai import AzureChatOpenAI

        cfg = settings.azure_openai_configs[0]
        return AzureChatOpenAI(
            model=cfg["deployment"],
            azure_endpoint=cfg["endpoint"],
            api_key=cfg["api_key"],
            api_version=cfg["api_version"],
            top_p=top_p,
            **override_kwargs,
            **kwargs,
        )

    raise ValueError(f"Unknown provider: {target}")


# ---------------------------------------------------------------------------
# Module-level load-balanced LLM (used by nodes.py)
# ---------------------------------------------------------------------------

llm = LoadBalancerLLM(_build_llm_instances())
