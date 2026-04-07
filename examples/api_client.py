"""API客户端示例"""

import requests
import json


def chat_completion(message: str, stream: bool = False):
    """调用聊天补全API
    
    Args:
        message: 用户消息
        stream: 是否流式返回
    """
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "browser-agent",
        "messages": [
            {"role": "user", "content": message}
        ],
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json",
        # 如果设置了API_KEY，需要添加认证
        # "Authorization": "Bearer your-api-key"
    }
    
    if stream:
        # 流式请求
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            
            print("流式响应:")
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data == '[DONE]':
                            print("\n响应完成")
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                        except json.JSONDecodeError:
                            pass
    else:
        # 非流式请求
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']
            print(f"\n助手回复: {content}")


def reset_conversation():
    """重置对话"""
    url = "http://localhost:8000/v1/chat/reset"
    response = requests.post(url)
    response.raise_for_status()
    print("对话已重置")


if __name__ == "__main__":
    # 示例1: 非流式请求
    print("=== 示例1: 非流式请求 ===")
    chat_completion("打开百度，搜索'Python'", stream=False)
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 流式请求
    print("=== 示例2: 流式请求 ===")
    chat_completion("打开 https://www.github.com，分析页面结构", stream=True)
    
    print("\n" + "="*50 + "\n")
    
    # 示例3: 重置对话
    print("=== 示例3: 重置对话 ===")
    reset_conversation()