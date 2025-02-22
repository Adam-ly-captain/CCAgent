from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat, Swarm
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, HandoffTermination
from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.messages import MultiModalMessage, TextMessage, ChatMessage
from autogen_core import Image as AGImage, CancellationToken
from autogen_agentchat.ui import Console
from cca.agent import BasicAgent, get_agent_client
from cca.constant import *


class TeamFactory:
    
    def __init__(
        self,
        agents: list[BasicAgent], 
        team_type: int = TEAM_ROUND_ROBIN, 
        max_message: int = 0, 
        terminate_text: str = "TERMINATE",
        is_handle_user: bool = False
    ):
        
        self.agents = agents
        if team_type == TEAM_ROUND_ROBIN:
            self.team = self.create_round_team(
                agents=agents, 
                max_message=max_message, 
                terminate_text=terminate_text, 
                is_handle_user=is_handle_user
            )

        elif team_type == TEAM_SELECT_GROUP:
            self.team = self.create_select_group(
                agents=agents, 
                max_message=max_message, 
                terminate_text=terminate_text, 
                is_handle_user=is_handle_user
            )
            
        elif team_type == TEAM_SWAM:
            self.team = self.create_swarm(
                agents=agents, 
                max_message=max_message, 
                terminate_text=terminate_text, 
                is_handle_user=is_handle_user
            )
        
        
    def create_condition(
        self, 
        max_message: int = 0, 
        terminate_text: str = "TERMINATE", 
        is_handle_user: bool = False
    ) -> TerminationCondition:
        
        if max_message > 0:
            if is_handle_user:
                return MaxMessageTermination(max_message) | TextMentionTermination(terminate_text) | HandoffTermination(target="user")
                                                                                                                            
            return MaxMessageTermination(max_message) | TextMentionTermination(terminate_text)

        if is_handle_user:
            return TextMentionTermination(terminate_text) | HandoffTermination(target="user")
        
        return TextMentionTermination(terminate_text)
        
        
    def create_round_team(
        self, 
        agents: list[BasicAgent], 
        max_message: int = 0, 
        terminate_text: str = "TERMINATE", 
        is_handle_user: bool = False
    ) -> RoundRobinGroupChat:
        
        # Create a team that uses a round-robin chat strategy.
        return RoundRobinGroupChat(
            [agent.get_agent() for agent in agents], 
            termination_condition=self.create_condition(
                max_message=max_message,
                terminate_text=terminate_text,
                is_handle_user=is_handle_user
            ),
        )
    
    
    def create_select_group(
        self, 
        agents: list[BasicAgent], 
        max_message: int = 0, 
        terminate_text: str = "TERMINATE",
        is_handle_user: bool = False
    ) -> SelectorGroupChat:
        
        # Create a team that uses a select group chat strategy.
        return SelectorGroupChat(
            [agent.get_agent() for agent in agents], 
            termination_condition=self.create_condition(
                max_message=max_message,
                terminate_text=terminate_text,
                is_handle_user=is_handle_user
            ),
            model_client=get_agent_client()
        )
    
    
    def create_swarm(
        self, 
        agents: list[BasicAgent], 
        max_message: int = 0, 
        terminate_text: str = "TERMINATE",
        is_handle_user: bool = False
    ) -> Swarm:
        
        # Create a team that uses a swarm chat strategy.
        return Swarm(
            [agent.get_agent() for agent in agents], 
            termination_condition=self.create_condition(
                max_message=max_message,
                terminate_text=terminate_text,
                is_handle_user=is_handle_user
            ),
        )
    
    
    async def run(self, task: str | ChatMessage = None):
        if self.team and task:
            await self.team.run(task=task)
        
        
    async def run_stream(self, task: str | ChatMessage = None):
        if self.team and task:
            await Console(
                self.team.run_stream(task=task)
            )
    