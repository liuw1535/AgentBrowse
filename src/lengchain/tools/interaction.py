"""交互相关工具"""

from pydantic import BaseModel, Field
from lengchain.tools.base import BrowserBaseTool
from lengchain.utils.logger import get_logger

logger = get_logger(__name__)


class ClickInput(BaseModel):
    """点击工具输入"""
    selector: str = Field(description="要点击的元素的CSS选择器")
    timeout: int = Field(default=30000, description="超时时间（毫秒），默认30秒")


class ClickTool(BrowserBaseTool):
    """点击元素工具"""
    
    name: str = "click"
    description: str = """点击页面上的元素。
使用场景: 点击按钮、链接、菜单等可交互元素。
参数:
- selector: CSS选择器 (必需)
- timeout: 超时时间（毫秒），默认30000 (可选)
示例: click(selector="button#submit", timeout=30000)
"""
    args_schema: type[BaseModel] = ClickInput
    
    async def _arun(self, selector: str, timeout: int = 30000) -> str:
        """异步点击"""
        try:
            logger.info(f"点击元素: {selector}")
            await self.browser_manager.click(selector, timeout)
            return f"成功点击元素: {selector}"
        except Exception as e:
            error_msg = f"点击失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class InputInput(BaseModel):
    """输入工具输入"""
    selector: str = Field(description="输入框的CSS选择器")
    text: str = Field(description="要输入的文本")
    press_enter: bool = Field(default=False, description="是否在输入后按回车键")
    timeout: int = Field(default=30000, description="超时时间（毫秒）")


class InputTool(BrowserBaseTool):
    """输入文本工具"""
    
    name: str = "input_text"
    description: str = """在输入框中输入文本。
使用场景: 填写表单、搜索框输入等。
参数:
- selector: CSS选择器 (必需)
- text: 要输入的文本 (必需)
- press_enter: 是否按回车，默认false (可选)
- timeout: 超时时间（毫秒），默认30000 (可选)
示例: input_text(selector="input[name='q']", text="LangChain", press_enter=true)
"""
    args_schema: type[BaseModel] = InputInput
    
    async def _arun(
        self,
        selector: str,
        text: str,
        press_enter: bool = False,
        timeout: int = 30000
    ) -> str:
        """异步输入文本"""
        try:
            logger.info(f"在 {selector} 中输入: {text}")
            await self.browser_manager.fill(selector, text, timeout)
            
            if press_enter:
                await self.browser_manager.press(selector, "Enter")
                return f"成功在 {selector} 中输入 '{text}' 并按下回车"
            
            return f"成功在 {selector} 中输入 '{text}'"
        except Exception as e:
            error_msg = f"输入失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ScrollInput(BaseModel):
    """滚动工具输入"""
    direction: str = Field(
        default="down",
        description="滚动方向: down(向下), up(向上), left(向左), right(向右)"
    )
    amount: int = Field(default=500, description="滚动距离（像素），默认500")


class ScrollTool(BrowserBaseTool):
    """页面滚动工具"""
    
    name: str = "scroll"
    description: str = """滚动页面。
使用场景: 加载更多内容、查看页面不同部分。
参数:
- direction: 滚动方向，默认down (可选)
- amount: 滚动距离（像素），默认500 (可选)
示例: scroll(direction="down", amount=500)
"""
    args_schema: type[BaseModel] = ScrollInput
    
    async def _arun(self, direction: str = "down", amount: int = 500) -> str:
        """异步滚动"""
        try:
            logger.info(f"向{direction}滚动 {amount}px")
            await self.browser_manager.scroll(direction, amount)
            return f"成功向{direction}滚动 {amount}px"
        except Exception as e:
            error_msg = f"滚动失败: {str(e)}"
            logger.error(error_msg)
            return error_msg