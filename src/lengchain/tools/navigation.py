"""导航相关工具"""

from pydantic import BaseModel, Field
from lengchain.tools.base import BrowserBaseTool
from lengchain.utils.logger import get_logger

logger = get_logger(__name__)


class NavigateInput(BaseModel):
    """导航工具输入"""
    url: str = Field(description="要导航到的URL地址")
    wait_until: str = Field(
        default="load",
        description="等待状态: load(页面加载完成), domcontentloaded(DOM加载完成), networkidle(网络空闲)"
    )


class NavigateTool(BrowserBaseTool):
    """浏览器导航工具"""
    
    name: str = "navigate"
    description: str = """导航到指定的URL网址。
使用场景: 打开网站、访问链接、切换页面。
参数:
- url: 目标网址 (必需)
- wait_until: 等待页面加载状态，默认为load (可选)
示例: navigate(url="https://www.google.com", wait_until="load")
"""
    args_schema: type[BaseModel] = NavigateInput
    
    async def _arun(self, url: str, wait_until: str = "load") -> str:
        """异步执行导航"""
        try:
            logger.info(f"导航到: {url}")
            await self.browser_manager.navigate(url, wait_until)
            
            current_url = await self.browser_manager.get_current_url()
            title = await self.browser_manager.get_title()
            
            return f"成功导航到 {current_url}\n页面标题: {title}"
        except Exception as e:
            error_msg = f"导航失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class WaitInput(BaseModel):
    """等待工具输入"""
    selector: str = Field(description="要等待的CSS选择器")
    timeout: int = Field(default=30000, description="超时时间（毫秒），默认30秒")
    state: str = Field(
        default="visible",
        description="等待元素状态: visible(可见), hidden(隐藏), attached(附加), detached(分离)"
    )


class WaitTool(BrowserBaseTool):
    """等待元素工具"""
    
    name: str = "wait_for_element"
    description: str = """等待页面元素出现或达到指定状态。
使用场景: 等待动态内容加载、等待元素显示。
参数:
- selector: CSS选择器 (必需)
- timeout: 超时时间（毫秒），默认30000 (可选)
- state: 元素状态，默认visible (可选)
示例: wait_for_element(selector="#search-button", timeout=30000, state="visible")
"""
    args_schema: type[BaseModel] = WaitInput
    
    async def _arun(self, selector: str, timeout: int = 30000, state: str = "visible") -> str:
        """异步等待元素"""
        try:
            logger.info(f"等待元素: {selector}")
            await self.browser_manager.wait_for_selector(selector, timeout, state)
            return f"元素 {selector} 已{state}"
        except Exception as e:
            error_msg = f"等待元素失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class BackTool(BrowserBaseTool):
    """后退工具"""
    
    name: str = "go_back"
    description: str = """返回到上一个页面。
使用场景: 浏览器后退操作。
示例: go_back()
"""
    
    async def _arun(self) -> str:
        """异步后退"""
        try:
            await self.browser_manager.go_back()
            current_url = await self.browser_manager.get_current_url()
            return f"已后退到: {current_url}"
        except Exception as e:
            error_msg = f"后退失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ReloadTool(BrowserBaseTool):
    """刷新工具"""
    
    name: str = "reload_page"
    description: str = """刷新当前页面。
使用场景: 重新加载页面内容。
示例: reload_page()
"""
    
    async def _arun(self) -> str:
        """异步刷新"""
        try:
            await self.browser_manager.reload()
            return "页面已刷新"
        except Exception as e:
            error_msg = f"刷新失败: {str(e)}"
            logger.error(error_msg)
            return error_msg