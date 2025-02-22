from cca.vlm_agent import WindowsOperationAgent
from cca.team import TeamFactory
from cca.constant import *
import asyncio


if __name__ == "__main__":
    agent = WindowsOperationAgent()
    
    user_input = input("请开始提问: ")
    
    team = TeamFactory(
        agents=[agent], 
        team_type=TEAM_ROUND_ROBIN, 
        # max_message=30, 
        terminate_text="APPROVE"
    ) 
    asyncio.run(team.run_stream(user_input))
