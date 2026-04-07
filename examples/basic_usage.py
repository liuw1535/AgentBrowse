"""基础使用示例"""

import asyncio
from lengchain.agent.browser_agent import BrowserAgent


async def main():
    """基础使用示例"""
    
    # 创建Agent（使用上下文管理器自动管理浏览器生命周期）
    async with BrowserAgent() as agent:
        
        # 示例1: 搜索信息
        print("\n=== 示例1: 搜索信息 ===")
        result = await agent.execute(
            "打开百度，搜索'LangChain'"
        )
        print(f"结果: {result}\n")
        
        # 示例2: 提取内容
        print("\n=== 示例2: 提取内容 ===")
        result = await agent.execute(
            "打开 https://www.python.org，提取页面主要内容"
        )
        print(f"结果: {result}\n")
        
        # 示例3: 复杂任务
        print("\n=== 示例3: 复杂任务 ===")
        result = await agent.execute(
            "访问GitHub，搜索'langchain'项目，告诉我最受欢迎的项目名称和star数"
        )
        print(f"结果: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())