from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.openai._openai_assistant_agent import OpenAIAssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import MultiModalMessage, TextMessage
from autogen_core import CancellationToken

from openai import AsyncClient

from cca.parse_config import get_agent_config
from cca.tools import BasicTool
from cca.constant import *


def get_agent_client():
    config_dict = get_agent_config()
    
    # Create an agent that uses the OpenAI GPT-4o model.
    model_client = OpenAIChatCompletionClient(
        model=config_dict['model'],
        base_url=config_dict['base_url'],
        api_key=config_dict['api_key'],
    )
    
    return model_client


class BasicAgent:

    def __init__(
        self, 
        agent_name: str, 
        agent_desc: str, 
        system_message: str, 
        tools: list[BasicTool] = [],
        handoffs: list[str] = [],
        agent_type: int = AGENT_ASSISTANT,
    ):
        
        self.agent_name = agent_name
        self.agent_desc = agent_desc
        self.system_message = system_message
        self.tools = tools
        self.handoffs = handoffs
        if agent_type == AGENT_ASSISTANT:
            self.agent = self.create_assistant_agent(
                agent_name=agent_name, 
                agent_desc=agent_desc, 
                system_message=system_message, 
                tools=tools,
                handoffs=handoffs
            )
        elif agent_type == AGENT_OPENAI_ASSISTANT:
            self.agent = self.create_openai_assistant_agent(
                agent_name=agent_name, 
                agent_desc=agent_desc,
                system_message=system_message,
                tools=tools,
            )
        

    def create_assistant_agent(
        self, 
        agent_name: str, 
        agent_desc: str, 
        system_message: str, 
        tools: list[BasicTool] = [],
        handoffs: list[str] = []
    ) -> AssistantAgent:
        
        return AssistantAgent(
            name=agent_name,
            description=agent_desc,
            model_client=get_agent_client(),
            system_message=system_message,
            tools=[tool.get_tool() for tool in tools],
            handoffs=handoffs
        )
        

    def create_openai_assistant_agent(
        self, 
        agent_name: str, 
        agent_desc: str, 
        system_message: str,
        tools: list[BasicTool] = [],
    ) -> OpenAIAssistantAgent:
        
        config_dict = get_agent_config()
        return OpenAIAssistantAgent(
            name=agent_name,
            description=agent_desc,
            client=AsyncClient(
                api_key=config_dict['api_key'],
                base_url=config_dict['base_url'],
            ),
            model=config_dict['model'],
            instructions=system_message,
            tools=[tool.get_tool() for tool in tools],
        )
        
        
    def get_agent(self) -> AssistantAgent:
        return self.agent


    async def run_stream(self, user_input: str):
        agent = self.get_agent()
        await Console(
            agent.on_messages_stream(
                [TextMessage(content=user_input, source="user")],
                cancellation_token=CancellationToken(),
            )
        )
