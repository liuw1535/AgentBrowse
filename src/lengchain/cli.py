"""命令行工具"""

import asyncio
import sys
from lengchain.agent.browser_agent import BrowserAgent
from lengchain.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("LangChain 浏览器自动化助手 - 交互式模式")
    print("=" * 60)
    print("输入您的任务，输入 'exit' 或 'quit' 退出")
    print("输入 'reset' 重置对话历史")
    print("=" * 60)
    print()
    
    agent = BrowserAgent(verbose=False)
    
    try:
        await agent.initialize()
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n您: ").strip()
                
                if not user_input:
                    continue
                
                # 退出命令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n再见！")
                    break
                
                # 重置命令
                if user_input.lower() == 'reset':
                    agent.clear_memory()
                    print("对话历史已重置")
                    continue
                
                # 执行任务
                print("\n助手: ", end='', flush=True)
                result = await agent.execute(user_input)
                print(result)
            
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                logger.error(f"执行出错: {str(e)}")
                print(f"\n错误: {str(e)}")
    
    finally:
        await agent.close()


def main():
    """主函数"""
    try:
        asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)


if __name__ == "__main__":
    main()