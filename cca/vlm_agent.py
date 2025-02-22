from cca.agent import BasicAgent
from cca.tools import AnnotateImageTool, ExecuteUIControlActionTool, OpenApplicationTool, GetDesktopWindowsTool, UIAnnotateImageRecognitionTool, TaskImageCheckTool, UIControlClickActionTool, UIControlInputTextActionTool, UIControlInputTextWithoutControlIdActionTool
from cca.constant import *


class WindowsOperationAgent(BasicAgent):
    
    def __init__(self, agent_type: int = AGENT_ASSISTANT):        
        super().__init__(
            agent_name="window_operation_agent", 
            agent_desc="负责Windows应用程序操作的专家",
            system_message="""
            你是一个负责Windows应用程序操作的专家,负责解析用户输入并逐步分析执行以下任务：
            1. 根据用户输入解析目标应用的名称,并尝试打开目标应用程序。
            2. 使用工具获取所有窗口字典信息,从中筛选出目标应用程序的窗口字典ID,ID是1-10之间的数字。
            3. 文本输入UI操作工具不用传入控件ID,直接传入文本内容即可。
            4. 使用工具对目标应用窗口进行截图,并标注所有UI控件的位置信息。
            5. 将标注后的图像传递给UI控件图像分析的工具,工具将返回UI控件ID。
            6. 鼠标点击工具需要传入UI控件唯一标识ID(是一个整数,范围在1-200之间)。调用一次工具只能执行一个鼠标点击或文本输入操作
            在鼠标点击之前需要先对目标窗口进行截图并标注UI控件。
            7. 工具将截图并确认用户的所有目标操作是否已完成。
            注意：
            1. 所有操作需要按照先后顺序执行,避免遗漏任何必要步骤。
            2. 如果用户操作任务已完成,一定要发送"APPROVE"消息以结束对话,否则进入死循环。
            3. 若工具返回的结果表明用户UI任务失败或未完成,则从第4步开始继续执行任务,重复尝试3次,直到任务完成。
            """,
            tools=[
                OpenApplicationTool(), 
                GetDesktopWindowsTool(), 
                AnnotateImageTool(),
                UIAnnotateImageRecognitionTool(),
                UIControlClickActionTool(),
                UIControlInputTextWithoutControlIdActionTool(),
                TaskImageCheckTool(),
            ],
            handoffs=[],  # 此代理不需要交接给其他代理
            agent_type=agent_type,
        )
