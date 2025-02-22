from cca.tool_base_agent import ToolBasicAgent


class UIImageAnalysisAgent(ToolBasicAgent):
    
    def __init__(self):        
        super().__init__(
            agent_name="ui_image_analysis_agent", 
            agent_desc="负责UI控件图像分析的专家", 
            system_message="""
            你是一个负责UI控件图像分析的专家,你将会接受标注后的UI控件图像标注信息,并逐步执行以下任务:
            1. 分析用户输入的操作指令,解析出当前应用程序界面具体的操作步骤。
            2. 识别标注后的UI控件图像,从图中确定下一步UI控件操作的唯一ID标识。
            注意：
            1. 所有操作需要按照先后顺序执行,避免遗漏任何必要步骤。
            2. 千万不要点击关闭与最小化按钮。
            3. 你的回答中只需要包含UI控件的唯一标识即可,然后简单地描述一下截图的主要元素。
            """,
        )
        

class TaskImageCheckAgent(ToolBasicAgent):
    
    def __init__(self):        
        super().__init__(
            agent_name="task_check_agent", 
            agent_desc="负责检查整个用户UI操作任务的专家", 
            system_message="""
            你是一名负责检查整个用户UI操作任务的专家,你将会接受应用程序界面截图以及整个用户UI操作任务的描述,并分析执行以下任务：
            1. 根据应用程序界面截图判断用户的所有操作是否已完成
            注意:
            1. 尽可能简洁地描述用户的UI操作任务是否完成
            """,
        )
