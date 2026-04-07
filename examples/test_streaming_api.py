"""
测试流式 API 响应
"""
import asyncio
import httpx
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000/v1/chat/completions"

async def test_non_streaming():
    """测试非流式响应"""
    print("\n" + "="*50)
    print("测试非流式响应")
    print("="*50)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "打开百度首页"}
            ],
            "stream": False
        }
        
        start_time = time.time()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送请求...")
        
        response = await client.post(API_URL, json=request_data)
        elapsed = time.time() - start_time
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应状态码: {response.status_code}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应时间: {elapsed:.2f}秒")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应内容:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"错误: {response.text}")

async def test_streaming():
    """测试流式响应"""
    print("\n" + "="*50)
    print("测试流式响应")
    print("="*50)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "搜索 Python 教程"}
            ],
            "stream": True
        }
        
        start_time = time.time()
        last_data_time = start_time
        chunk_count = 0
        heartbeat_count = 0
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送流式请求...")
        
        async with client.stream("POST", API_URL, json=request_data) as response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                content = await response.aread()
                print(f"错误: {content.decode()}")
                return
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始接收流式数据...\n")
            
            async for line in response.aiter_lines():
                if not line or not line.strip():
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]  # 移除 "data: " 前缀
                    
                    if data_str == "[DONE]":
                        elapsed = time.time() - start_time
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 流式响应完成")
                        print(f"总耗时: {elapsed:.2f}秒")
                        print(f"收到 {chunk_count} 个数据块")
                        print(f"收到 {heartbeat_count} 个心跳")
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        chunk_count += 1
                        now = time.time()
                        time_since_last = now - last_data_time
                        last_data_time = now
                        
                        # 检查是否是心跳
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        if not delta or (not delta.get("content") and not delta.get("role")):
                            heartbeat_count += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❤️ 心跳 (距上次 {time_since_last:.1f}s)")
                        else:
                            # 打印内容
                            content = delta.get("content", "")
                            role = delta.get("role", "")
                            if role:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] 角色: {role}")
                            if content:
                                print(content, end="", flush=True)
                    
                    except json.JSONDecodeError as e:
                        print(f"\n解析错误: {e}, 数据: {data_str}")

async def test_long_running_stream():
    """测试长时间运行的流式请求（验证心跳）"""
    print("\n" + "="*50)
    print("测试长时间运行的流式请求")
    print("="*50)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "访问 https://www.python.org 并告诉我首页的主要内容"}
            ],
            "stream": True
        }
        
        start_time = time.time()
        last_data_time = start_time
        chunk_count = 0
        heartbeat_count = 0
        max_gap = 0.0
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送长时间运行的请求...")
        
        async with client.stream("POST", API_URL, json=request_data) as response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                content = await response.aread()
                print(f"错误: {content.decode()}")
                return
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始接收数据...\n")
            
            async for line in response.aiter_lines():
                if not line or not line.strip():
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]
                    
                    if data_str == "[DONE]":
                        elapsed = time.time() - start_time
                        print(f"\n\n[{datetime.now().strftime('%H:%M:%S')}] 完成")
                        print(f"总耗时: {elapsed:.2f}秒")
                        print(f"数据块: {chunk_count}, 心跳: {heartbeat_count}")
                        print(f"最大间隔: {max_gap:.2f}秒")
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        chunk_count += 1
                        now = time.time()
                        gap = now - last_data_time
                        max_gap = max(max_gap, gap)
                        last_data_time = now
                        
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        if not delta or (not delta.get("content") and not delta.get("role")):
                            heartbeat_count += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💓 心跳 ({gap:.1f}s)")
                        else:
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                    
                    except json.JSONDecodeError:
                        pass

async def main():
    """运行所有测试"""
    try:
        # 测试非流式
        await test_non_streaming()
        await asyncio.sleep(2)
        
        # 测试流式
        await test_streaming()
        await asyncio.sleep(2)
        
        # 测试长时间运行
        await test_long_running_stream()
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("流式 API 测试工具")
    print("确保服务器正在运行: python run.py")
    asyncio.run(main())