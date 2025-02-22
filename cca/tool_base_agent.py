from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import MultiModalMessage, TextMessage
from autogen_core import CancellationToken
from typing import Union, Any
from cca.parse_config import get_tool_agent_config


def get_agent_client():
    config_dict = get_tool_agent_config()
    
    # Create an agent that uses the OpenAI GPT-4o model.
    model_client = OpenAIChatCompletionClient(
        model=config_dict['model'],
        base_url=config_dict['base_url'],
        api_key=config_dict['api_key'],
    )
    
    return model_client


class ToolBasicAgent:

    def __init__(
        self, 
        agent_name: str, 
        agent_desc: str, 
        system_message: str,
    ):
        
        self.agent_name = agent_name
        self.agent_desc = agent_desc
        self.system_message = system_message
        self.agent = self.create_assistant_agent(
            agent_name=agent_name, 
            agent_desc=agent_desc, 
            system_message=system_message,
        )
        

    def create_assistant_agent(
        self, 
        agent_name: str, 
        agent_desc: str, 
        system_message: str,
    ) -> AssistantAgent:
        
        return AssistantAgent(
            name=agent_name,
            description=agent_desc,
            model_client=get_agent_client(),
            system_message=system_message,
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
        
    async def run(self, 
                  messages: Union[list[MultiModalMessage | TextMessage], 
                                  MultiModalMessage, TextMessage]
    ) -> TextMessage | MultiModalMessage:
        
        agent = self.get_agent()
        if isinstance(messages, MultiModalMessage) or isinstance(messages, TextMessage):
            response = await agent.on_messages(
                messages=[messages],
                cancellation_token=CancellationToken(),
            )
            
        elif isinstance(messages, list):
            response = await agent.on_messages(
                    messages=messages,
                    cancellation_token=CancellationToken(),
                )

        return response.chat_message