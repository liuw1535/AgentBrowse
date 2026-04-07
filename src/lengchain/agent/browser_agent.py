"""浏览器自动化Agent"""

from typing import List, Optional
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from lengchain.browser.manager import BrowserManager
from lengchain.tools import (
    NavigateTool, WaitTool, BackTool, ReloadTool,
    ClickTool, InputTool, ScrollTool,
    ExtractTool, SearchTool, ScreenshotTool,
    AnalyzeTool, SummarizeTool
)
from lengchain.agent.memory import BrowserMemory
from lengchain.agent.prompts import SYSTEM_PROMPT
from lengchain.config import settings
from lengchain.utils.logger import get_logger

logger = get_logger(__name__)


class BrowserAgent:
    """基于ReAct模式的浏览器自动化Agent"""
    
    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[BrowserMemory] = None,
        max_iterations: Optional[int] = None,
        verbose: Optional[bool] = None
    ):
        """初始化Agent
        
        Args:
            browser_manager: 浏览器管理器
            llm: 语言模型
            tools: 工具列表
            memory: 记忆模块
            max_iterations: 最大迭代次数
            verbose: 是否详细输出
        """
        self.browser_manager = browser_manager or BrowserManager()
        self.llm = llm or self._create_llm()
        self.memory = memory or BrowserMemory()
        self.max_iterations = max_iterations or settings.max_iterations
        self.verbose = verbose if verbose is not None else settings.verbose
        
        # 创建工具
        self.tools = tools or self._create_tools()
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        logger.info("BrowserAgent 初始化完成")
    
    def _create_llm(self) -> ChatOpenAI:
        """创建语言模型"""
        return ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
        )
    
    def _create_tools(self) -> List[BaseTool]:
        """创建工具列表"""
        tools = [
            # 导航工具
            NavigateTool(browser_manager=self.browser_manager),
            WaitTool(browser_manager=self.browser_manager),
            BackTool(browser_manager=self.browser_manager),
            ReloadTool(browser_manager=self.browser_manager),
            
            # 交互工具
            ClickTool(browser_manager=self.browser_manager),
            InputTool(browser_manager=self.browser_manager),
            ScrollTool(browser_manager=self.browser_manager),
            
            # 提取工具
            ExtractTool(browser_manager=self.browser_manager),
            SearchTool(browser_manager=self.browser_manager),
            ScreenshotTool(browser_manager=self.browser_manager),
            
            # 分析工具
            AnalyzeTool(browser_manager=self.browser_manager),
            SummarizeTool(browser_manager=self.browser_manager),
        ]
        
        logger.info(f"已创建 {len(tools)} 个工具")
        return tools
    
    def _create_agent(self):
        """创建Agent执行器"""
        # 使用 LangGraph 创建 ReAct Agent
        # prompt 参数接受 SystemMessage 或 str
        agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT
        )
        
        return agent_executor
    
    async def initialize(self) -> None:
        """初始化Agent（启动浏览器）"""
        if not self.browser_manager._initialized:
            await self.browser_manager.initialize()
            logger.info("浏览器已启动")
    
    async def execute(self, user_input: str) -> str:
        """执行用户任务
        
        Args:
            user_input: 用户输入的任务描述
            
        Returns:
            任务执行结果
        """
        try:
            logger.info(f"执行任务: {user_input}")
            
            # 确保浏览器已初始化
            await self.initialize()
            
            # 执行Agent (LangGraph 使用 messages 格式)
            result = await self.agent_executor.ainvoke({
                "messages": [("user", user_input)]
            })
            
            # 从结果中提取输出
            messages = result.get("messages", [])
            if messages:
                output = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
            else:
                output = "任务完成，但没有返回结果"
            
            logger.info("任务执行完成")
            
            return output
        
        except Exception as e:
            error_msg = f"执行任务时出错: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def stream_execute(self, user_input: str):
        """流式执行任务（用于SSE）
        
        Args:
            user_input: 用户输入
            
        Yields:
            执行过程中的中间结果
        """
        try:
            await self.initialize()
            
            # 流式执行 (LangGraph 使用 messages 格式)
            async for chunk in self.agent_executor.astream({
                "messages": [("user", user_input)]
            }):
                yield chunk
        
        except Exception as e:
            error_msg = f"流式执行出错: {str(e)}"
            logger.error(error_msg)
            yield {"error": error_msg}
    
    def clear_memory(self) -> None:
        """清空对话记忆"""
        self.memory.clear()
        logger.info("记忆已清空")
    
    async def close(self) -> None:
        """关闭Agent（关闭浏览器）"""
        await self.browser_manager.close()
        logger.info("Agent已关闭")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()