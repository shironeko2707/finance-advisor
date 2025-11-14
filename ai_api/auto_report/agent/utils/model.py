from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from auto_report.agent.utils.load_balancing import LoadBalancerLLM

from ...config import get_settings


settings = get_settings()


def get_chat_model(
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    **kwargs
) -> AzureChatOpenAI:
    """
    Create and return an AzureChatOpenAI model instance using configured settings.

    Args:
        max_token (int | None): Maximum number of tokens to generate in the response.
        temperature (float | None): Sampling temperature for response generation.
        top_p (float | None): Nucleus sampling parameter.
        **kwargs: Additional keyword arguments to pass to AzureChatOpenAI.

    Returns:
        AzureChatOpenAI: An instance of AzureChatOpenAI configured with the provided parameters and application settings.
    """
    return AzureChatOpenAI(
        model=settings.azure_llm_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.openai_api_version,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        **kwargs
    )

# Subscription 1
llm1 = AzureChatOpenAI(
    model=settings.azure_llm_deployment,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.openai_api_version,
    temperature=0,
    max_tokens=4096,
    max_retries=2
)
# Subscription 2
llm3 = AzureChatOpenAI(
    model=settings.azure_llm_deployment_2,
    azure_endpoint=settings.azure_openai_endpoint_2,
    api_key=settings.azure_openai_api_key_2,
    api_version=settings.openai_api_version_2,
    temperature=0,
    max_tokens=4096,
    max_retries=2
)

# specify all models that can be selected in the ChatDynamic instance
llm = LoadBalancerLLM([llm1, llm3])  # Load balancer alternates via round-robin
