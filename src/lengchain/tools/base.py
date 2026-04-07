"""工具基类"""

from langchain.tools import BaseTool
from lengchain.browser.manager import BrowserManager
from typing import Optional


class BrowserBaseTool(BaseTool):
    """浏览器工具基类"""
    
    browser_manager: BrowserManager
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(self, *args, **kwargs) -> str:
        """同步运行（不支持）"""
        raise NotImplementedError("此工具仅支持异步调用，请使用 _arun 方法")