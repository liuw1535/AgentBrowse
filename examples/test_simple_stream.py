"""
简单的流式响应测试
"""
import asyncio
import httpx
import json
from datetime import datetime

API_URL = "http://localhost:8000/v1/chat/completions"

async def test_stream():
    """测试流式响应"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始测试流式响应")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "打开百度首页"}
            ],
            "stream": True
        }
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送请求...")
        print(f"请求数据: {json.dumps(request_data, ensure_ascii=False)}")
        print("=" * 60)
        
        async with client.stream("POST", API_URL, json=request_data) as response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应状态: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print("=" * 60)
            
            if response.status_code != 200:
                content = await response.aread()
                print(f"错误: {content.decode()}")
                return
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始接收流式数据:")
            print("=" * 60)
            
            chunk_count = 0
            content_parts = []
            
            async for line in response.aiter_lines():
                now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                if not line or not line.strip():
                    continue
                
                print(f"[{now}] 原始行: {line[:100]}")
                
                if line.startswith("data: "):
                    data_str = line[6:]
                    
                    if data_str == "[DONE]":
                        print(f"\n[{now}] ✓ 流式响应结束")
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        chunk_count += 1
                        
                        print(f"[{now}] Chunk #{chunk_count}:")
                        print(json.dumps(chunk_data, ensure_ascii=False, indent=2))
                        
                        # 提取内容
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            content = delta["content"]
                            content_parts.append(content)
                            print(f"[{now}] 内容: {content}")
                        elif "role" in delta:
                            print(f"[{now}] 角色: {delta['role']}")
                        else:
                            print(f"[{now}] 心跳")
                        
                        print("-" * 60)
                    
                    except json.JSONDecodeError as e:
                        print(f"[{now}] JSON 解析错误: {e}")
                        print(f"数据: {data_str}")
            
            print("\n" + "=" * 60)
            print("测试完成")
            print(f"总共收到 {chunk_count} 个数据块")
            print(f"完整内容: {''.join(content_parts)}")
            print("=" * 60)

if __name__ == "__main__":
    print("简单流式响应测试")
    print("确保服务器运行在 http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_stream())
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()