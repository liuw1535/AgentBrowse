"""LangChain Browser Automation Assistant - 浏览器自动化智能助手"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "基于LangChain和LCEL构建的浏览器自动化AI助手"

from lengchain.agent.browser_agent import BrowserAgent
from lengchain.browser.manager import BrowserManager

__all__ = ["BrowserAgent", "BrowserManager"]