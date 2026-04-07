#!/usr/bin/env python
"""项目启动脚本"""

import sys
import asyncio
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LangChain Browser Automation Assistant")
    parser.add_argument(
        "command",
        choices=["server", "demo"],
        help="运行模式: server(启动API服务) 或 demo(运行演示)"
    )
    
    args = parser.parse_args()
    
    if args.command == "server":
        # 启动API服务器
        from lengchain.api.server import run_server
        print("启动 API 服务器...")
        run_server()
    
    elif args.command == "demo":
        # 运行演示
        from examples.basic_usage import main as demo_main
        print("运行基础演示...")
        asyncio.run(demo_main())


if __name__ == "__main__":
    main()