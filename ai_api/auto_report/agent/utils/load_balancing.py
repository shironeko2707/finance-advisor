from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class RoundRobinSelector:
    def __init__(self, llms: List[BaseChatModel]):
        self.llms = llms
        self.index = 0

    def __call__(self) -> BaseChatModel:
        if not self.llms:
            raise ValueError("No LLMs available in the load balancer.")
        llm = self.llms[self.index % len(self.llms)]
        self.index += 1
        return llm

class LoadBalancerLLM:
    def __init__(self, llms: List[BaseChatModel]):
        self.llms = llms
        self._selector = RoundRobinSelector(llms)

    def invoke(self, input, config=None, **kwargs):
        llm = self._selector()
        return llm.invoke(input, config=config, **kwargs)

    def bind_tools(self, tools, **kwargs):
        bound_llms = [llm.bind_tools(tools, **kwargs) for llm in self.llms]
        return LoadBalancerLLM(bound_llms)
