from autogen_core.tools import FunctionTool
from autogen_agentchat.messages import MultiModalMessage, TextMessage
from autogen_core import Image as AGImage, CancellationToken

from pywinauto import Desktop, Application
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo

from ufo.automator.ui_control.inspector import UIABackendStrategy

from PIL import Image, ImageDraw, ImageFont
from typing import List, Callable, Any
import pyautogui, pyperclip, cv2, os, time
import numpy as np

from cca.parse_config import get_ui_control_config, get_os_config, get_screen_resolution, get_applications_info
from cca.db_operate import *
from cca.constant import *
from cca.tool_agent import UIImageAnalysisAgent, TaskImageCheckAgent


ui_agent = UIImageAnalysisAgent()
task_check_agent = TaskImageCheckAgent()

def get_application_path(application_name: str) -> str | None:
    applications_info = get_applications_info()
    application_name = application_name.strip().lower()
    # 遍历应用程序信息字典
    for app_name, app_info in applications_info.items():
        if application_name in app_name.strip().lower():
            return app_info["path"]
        for alias in app_info["alias"]:
            if application_name in alias.strip().lower():
                return app_info["path"]

    return None


def open_application(application_name: str) -> TextMessage | None:
    if not application_name:
        return TextMessage(
            content="未指定应用程序名称, 请传入application_name参数",
            source="Tool"
        )
    
    is_opened = False
    
    try:
        Application().start(application_name)
        is_opened = True
    except:
        print(f"应用程序 {application_name} 未设置环境变量，尝试通过配置文件的完整路径搜索")
        is_opened = False
        
    if not is_opened:
        app_path = get_application_path(application_name)
        if app_path:
            os.startfile(app_path)
            is_opened = True
            
    if is_opened:
        
        # 插入日志
        insert_app_log(application_name=application_name)
            
        return TextMessage(
            content=f"成功打开应用程序 {application_name}",
            source="Tool"
        )
    else:
        return TextMessage(
            content=f"无法打开应用程序 {application_name}, 请重新输入应用程序名称",
            source="Tool"
        )


def select_application_window(application_name: str) -> UIAWrapper | None:
    config_dict = get_ui_control_config()
    return get_desktop_window_by_title(application_name, config_dict)


def screenshot_to_image(screenshot_path: str) -> Image:
    _os = get_os_config()
    screen_resolution = get_screen_resolution()
    width, height = screen_resolution['width'], screen_resolution['height']
    if _os == 'Windows':
        # Windows系统需要减去任务栏的高度
        height -= screen_resolution['taskbar_height']

    origin_img = pyautogui.screenshot(region=[0, 0, width, height])  # x,y,w,h
    
    img = cv2.cvtColor(np.asarray(origin_img), cv2.COLOR_RGB2BGR)  # cvtColor用于在图像中不同的色彩空间进行转换,用于后续处理。
    cv2.imwrite(screenshot_path, img)
    
    return origin_img


def get_desktop_windows(backend: str = "uia") -> List[UIAWrapper]:
    uia_desktop_windows: List[UIAWrapper] = [
        UIAWrapper(UIAElementInfo(handle_or_elem=window.handle))
        for window in Desktop(backend=backend).windows()
        if window.is_visible()
        and window.window_text() != "" 
        and window.element_info.class_name not in ["IME", "MSCTFIME UI"]
    ]
    
    return uia_desktop_windows


def get_desktop_windows_dict() -> dict:
    config_dict = get_ui_control_config()
    uia_desktop_windows = get_desktop_windows(backend=config_dict["backend"])
    return dict(
        zip([str(i + 1) for i in range(len(uia_desktop_windows))], uia_desktop_windows)
    )


def get_desktop_window_by_title(title: str, config_dict: dict) -> UIAWrapper | None:
    uia_desktop_windows = get_desktop_windows(backend=config_dict["backend"])
    
    for window in uia_desktop_windows:
        if title in window.window_text():
            return window
    
    return None


def get_desktop_window_by_index(index: int, config_dict: dict) -> UIAWrapper | None:
    uia_desktop_windows = get_desktop_windows(backend=config_dict["backend"])
    
    if 1 <= index <= len(uia_desktop_windows):
        return uia_desktop_windows[index - 1]
    
    return None


def batch_insert_ui_control_coordinates(app_log_id: int = -1, coordinates: list[tuple] = None) -> bool:
    return batch_insert_ui_control(app_log_id=app_log_id, coordinates=coordinates)


def add_label_to_image(window: UIAWrapper, config_dict: dict, application_name: str) -> Image:
    """
    add label to image for gpt-4V(o)
    window: target application window
    config_dict: yaml config profile
    """
    window.set_focus()
    application_name = application_name.strip().lower()
    
    backend = UIABackendStrategy()
    control_elements = backend.find_control_elements_in_descendants(
        window, control_type_list=config_dict['control_type_list'],
        is_visible=config_dict['is_visible'], class_name_list=config_dict['class_name_list']
    )
    
    basic_path = config_dict['image_basic_path']
    screenshot_path = f"{basic_path}/{application_name}{config_dict['image_suffix']}"
    screenshot = screenshot_to_image(screenshot_path=screenshot_path)

    coordinates = [
        (
            index,
            element.rectangle().left, 
            element.rectangle().top, 
            element.rectangle().right, 
            element.rectangle().bottom, 
            element.element_info.name.replace("\\", " ")
        )
        for index, element in enumerate(control_elements)
    ]
    
    # 批量插入坐标
    app_log_id = query_last_app_log_id()
    delete_ui_control_by_app_log_id(app_log_id=app_log_id)
    batch_insert_ui_control_coordinates(app_log_id=app_log_id, coordinates=coordinates)
    
    draw = ImageDraw.Draw(screenshot)
    font = ImageFont.truetype("times.ttf", 20)
    
    # 根据控件坐标和标签列表绘制红框和标签
    for coord in coordinates:
        index, left, top, right, bottom, label = coord
        
        draw.rectangle((left, top, right, bottom), outline="red", width=2)
        
        # 文本内容
        text = str(index)
        
        # 使用 getbbox 获取文本边界框
        text_bbox = font.getbbox(text)  # 返回 (xmin, ymin, xmax, ymax)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        revised_left = (right - left) * 0.4
        revised_top = (bottom - top) * 0.5
        text_position = (right - revised_left, top - revised_top)  # 调整文本框的位置
        background_position = (
            text_position[0], text_position[1],
            text_position[0] + text_width, text_position[1] + text_height + 6
        )
        
        # 绘制背景矩形
        draw.rectangle(background_position, fill=(255, 247, 144), outline="red", width=1)
        
        # 绘制文字
        draw.text(text_position, text, fill="red", font=font)
    
    # 保存或显示结果
    screenshot_path = f"{basic_path}/{application_name}_label{config_dict['image_suffix']}"
    os.remove(screenshot_path) if os.path.exists(screenshot_path) else None
    screenshot.save(screenshot_path, quality=85)
    
    return screenshot


def annotate_image(window_id: int = -1) -> MultiModalMessage | TextMessage | None:
    if window_id <= 0:
        return TextMessage(
            content="未指定应用程序窗口ID",
            source="Tool"
        )
        
    # 获取应用程序名称
    application_name = query_last_app_name()
    if application_name:
        config_dict = get_ui_control_config()
        
        # 获取活动窗口
        # application_window = get_desktop_window_by_title(application_name, config_dict)
        application_window = get_desktop_window_by_index(window_id, config_dict)
        if application_window:

            # 标注图片
            add_label_to_image(
                window=application_window, 
                config_dict=config_dict, 
                application_name=application_name
            )

            return TextMessage(
                content="当前应用程序界面截图已标注完成",
                source="Tool"
            )
    
    return TextMessage(
        content="未找到指定的应用程序窗口, 请重新输入应用程序名称",
        source="Tool"
    )


def execute_ui_control_action(
        ui_control_id: int = -1, 
        input_text: str = None, 
        element_action_type: int = ELEMENT_OPERATION_SINGLE_CLICK
    ) -> TextMessage | None:
    if ui_control_id <= -1:
        return TextMessage(
            content="未指定UI控件ID",
            source="Tool"
        )
        
    if element_action_type not in [
            ELEMENT_OPERATION_SINGLE_CLICK, 
            ELEMENT_OPERATION_DOUBLE_CLICK, 
            ELEMENT_OPERATION_INPUT_TEXT, 
            ELEMENT_OPERATION_INPUT_AND_ENTER
        ]:
        
        return TextMessage(
            content="未知的UI控件操作类型",
            source="Tool"
        )
        
    if element_action_type in [
            ELEMENT_OPERATION_INPUT_TEXT, 
            ELEMENT_OPERATION_INPUT_AND_ENTER
        ] and not input_text:
        
        return TextMessage(
            content="未指定输入文本",
            source="Tool"
        )
    
    app_log_id = query_last_app_log_id()
    control_element = query_ui_control_by_cid(app_log_id=app_log_id, cid=ui_control_id)
    # `id`, `left`, `top`, `right`, `bottom`, `label`
    cid, left, top, right, bottom, label = control_element
    
    # 计算控件中心坐标
    x = (left + right) // 2
    y = (top + bottom) // 2
    
    if element_action_type == ELEMENT_OPERATION_SINGLE_CLICK:
        pyautogui.click(x=x, y=y)
        
    elif element_action_type == ELEMENT_OPERATION_DOUBLE_CLICK:
        pyautogui.doubleClick(x=x, y=y)
        
    elif element_action_type == ELEMENT_OPERATION_INPUT_TEXT:
        pyautogui.click(x=x, y=y)
        pyperclip.copy(input_text)
        pyautogui.hotkey('Ctrl', 'V')
        
    elif element_action_type == ELEMENT_OPERATION_INPUT_AND_ENTER:
        pyautogui.click(x=x, y=y)
        pyperclip.copy(input_text)
        pyautogui.hotkey('Ctrl', 'V')
        pyautogui.press("enter")
        
    return TextMessage(
        content=f"UI控件操作已完成",
        source="Tool"
    )
    
    
def execute_ui_control_text_action(ui_control_id: int, input_text: str) -> TextMessage | None:
    return execute_ui_control_action(
        ui_control_id=ui_control_id, 
        input_text=input_text, 
        element_action_type=ELEMENT_OPERATION_INPUT_AND_ENTER
    )
    

def execute_ui_control_click_action(ui_control_id: int, click_type: int = ELEMENT_OPERATION_SINGLE_CLICK) -> TextMessage | None:
    return execute_ui_control_action(
        ui_control_id=ui_control_id, 
        element_action_type=click_type
    )
    

def execute_ui_control_text_action_withtout_control_id(input_text: str) -> TextMessage | None:
    pyperclip.copy(input_text)
    pyautogui.hotkey('Ctrl', 'V')
    pyautogui.press("enter")
    
    return TextMessage(
        content=f"UI控件操作已完成",
        source="Tool"
    )


async def recognize_annotate_image(ui_operation: str) -> TextMessage | None:
    config_dict = get_ui_control_config()
    application_name = query_last_app_name().strip().lower()
    
    annotate_image_path = f"{config_dict['image_basic_path']}/{application_name}_label{config_dict['image_suffix']}"
    img = AGImage(Image.open(annotate_image_path))
    
    # 多模态消息
    multi_modal_message = MultiModalMessage(
        content=[
            f"""
            这是应用程序{application_name}当前的界面截图，
            并在所有可以操作的UI控件的可操作区域的正中间上标注了数字ID。
            请你根据用户输入的操作指令“{ui_operation}”给我完成下一步需要操作的UI控件的数字ID。
            """, 
            img
        ], 
        source="User"
    )
    response_message = await ui_agent.run(multi_modal_message)
    
    return TextMessage(
        content=f"UI控件图像分析已完成,下一步执行的UI控件操作是{response_message.content}",
        source="Tool"
    )
    
    
async def check_task_completed(window_id: int, user_task_desc: str) -> TextMessage | None:
    config_dict = get_ui_control_config()
    application_name = query_last_app_name().strip().lower()
    
    if window_id <= 0:
        return TextMessage(
            content="未指定应用程序窗口ID",
            source="Tool"
        )
    
    annotate_image(window_id=window_id)
    
    annotate_image_path = f"{config_dict['image_basic_path']}/{application_name}_label{config_dict['image_suffix']}"
    img = AGImage(Image.open(annotate_image_path))
    
    # 多模态消息
    multi_modal_message = MultiModalMessage(
        content=[
            f"""
            这是应用程序{application_name}当前的界面截图,
            请你仔细检查用户任务"{user_task_desc}"是否已经完成。
            """, 
            img
        ], 
        source="User"
    )
    
    response_message = await task_check_agent.run(multi_modal_message)
    
    return TextMessage(
        content=f"""
        这是根据应用程序{application_name}当前的界面截图来检查
        整个用户任务是否完成的检查结果“{response_message.content}”。
        """,
        source="Tool"
    )
    

class BasicTool:
    
    def __init__(self, func: Callable[..., Any], name: str, desc: str):
        self.tool = FunctionTool(func=func, name=name, description=desc)
        self.func = func
        self.name = name
        self.desc = desc


    def get_tool(self) -> FunctionTool:
        return self.tool


class AnnotateImageTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=annotate_image, 
            name="annotate_image", 
            desc="""
            为指定应用程序在所有可以操控的UI控件的右上角标注唯一ID
            该工具需要传入1个参数:
            1. window_id: 应用程序窗口ID, 范围是1-10之间的数字
            """
        )


class ExecuteUIControlActionTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=execute_ui_control_action, 
            name="execute_ui_control_action", 
            desc="""
            执行指定UI控件的操作, 一次调用只能执行一个操作
            该工具需要传入三种参数:
            1. ui_control_id: UI控件唯一ID (int), 范围是1-200之间的数字
            2. input_text: 输入文本 (可选)
            3. element_action_type: UI控件操作类型 (int)
            UI控件操作类型对应的int枚举元素有四种:
            1: 鼠标单击
            2: 鼠标双击
            3: 仅输入文本
            4: 输入文本并回车
            """
        )
        
class UIControlClickActionTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=execute_ui_control_click_action, 
            name="execute_ui_control_click_action", 
            desc="""
            执行指定UI控件的点击操作
            该工具需要传入两个参数:
            1. ui_control_id: UI控件唯一ID (int), 范围是1-200之间的数字
            2. click_type: 鼠标点击类型 (int)
            鼠标点击类型对应的int枚举元素有两种:
            1: 鼠标单击
            2: 鼠标双击
            """
        )


class UIControlInputTextActionTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=execute_ui_control_text_action, 
            name="execute_ui_control_text_action", 
            desc="""
            执行指定UI控件的文本输入操作
            该工具需要传入两个参数:
            1. ui_control_id: UI控件唯一ID (int), 范围是1-200之间的数字
            2. input_text: 输入文本 (str)
            """
        )


class UIControlInputTextWithoutControlIdActionTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=execute_ui_control_text_action_withtout_control_id, 
            name="execute_ui_control_text_action_without_control_id", 
            desc="""
            执行文本输入操作
            该工具需要传入一个参数:
            1. input_text: 输入文本 (str)
            """
        )


class OpenApplicationTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=open_application, 
            name="open_application", 
            desc="""
            打开指定的应用程序
            该工具需要传入一个参数:
            1. application_name: 应用程序名称
            """
        )


class GetDesktopWindowsTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=get_desktop_windows_dict, 
            name="get_desktop_windows_dict", 
            desc="""
            获取用户当前桌面所有窗口的字典信息
            该工具不需要传入任何参数
            """
        )


class UIAnnotateImageRecognitionTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=recognize_annotate_image, 
            name="recognize_annotate_image", 
            desc="""
            识别标注后的UI控件图像信息,返回下一步需要操作的UI控件唯一ID
            该工具需要传入一个参数:
            1. ui_operation: 用户输入的UI控件操作指令描述
            """
        )


class TaskImageCheckTool(BasicTool):
    
    def __init__(self):
        super().__init__(
            func=check_task_completed, 
            name="check_task_completed", 
            desc="""
            检查整个用户UI操作任务是否已经完成
            该工具需要传入一个参数:
            1. user_task_desc: 用户UI操作任务描述
            """
        )
