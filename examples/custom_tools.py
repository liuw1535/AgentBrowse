"""自定义工具示例"""

import asyncio
from pydantic import BaseModel, Field
from lengchain.tools.base import BrowserBaseTool
from lengchain.agent.browser_agent import BrowserAgent
from lengchain.utils.logger import get_logger

logger = get_logger(__name__)


class CustomSearchInput(BaseModel):
    """自定义搜索工具输入"""
    query: str = Field(description="搜索关键词")
    engine: str = Field(default="google", description="搜索引擎: google, bing, baidu")


class CustomSearchTool(BrowserBaseTool):
    """自定义搜索工具"""
    
    name: str = "custom_search"
    description: str = """使用指定搜索引擎进行搜索。
参数:
- query: 搜索关键词 (必需)
- engine: 搜索引擎，默认google (可选)
示例: custom_search(query="LangChain", engine="google")
"""
    args_schema: type[BaseModel] = CustomSearchInput
    
    async def _arun(self, query: str, engine: str = "google") -> str:
        """执行搜索"""
        try:
            # 根据搜索引擎选择URL
            search_urls = {
                "google": f"https://www.google.com/search?q={query}",
                "bing": f"https://www.bing.com/search?q={query}",
                "baidu": f"https://www.baidu.com/s?wd={query}"
            }
            
            url = search_urls.get(engine, search_urls["google"])
            
            # 导航到搜索页面
            await self.browser_manager.navigate(url)
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 提取页面标题
            title = await self.browser_manager.get_title()
            
            return f"已使用{engine}搜索'{query}'，页面标题: {title}"
        
        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


async def main():
    """使用自定义工具"""
    
    # 创建Agent并添加自定义工具
    agent = BrowserAgent()
    
    # 添加自定义工具
    custom_tool = CustomSearchTool(browser_manager=agent.browser_manager)
    agent.tools.append(custom_tool)
    
    # 重新创建Agent执行器（因为工具列表已更新）
    agent.agent_executor = agent._create_agent()
    
    try:
        await agent.initialize()
        
        # 使用自定义工具
        result = await agent.execute(
            "使用自定义搜索工具在百度上搜索'人工智能'"
        )
        print(f"结果: {result}")
    
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())