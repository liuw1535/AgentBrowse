# 流式 API 使用指南

## 快速开始

### 1. 启动服务器

```bash
python run.py
```

服务器会在 `http://localhost:8000` 启动。

### 2. 测试流式响应

```bash
python examples/test_streaming_api.py
```

## 使用 OpenAI 客户端

### 非流式请求

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # 不需要真实的 API key
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "打开百度首页"}
    ],
    stream=False
)

print(response.choices[0].message.content)
```

### 流式请求

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "搜索 Python 教程"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## 心跳机制

在长时间运行的任务中，你会看到定期的心跳：

```
[14:30:15] 💓 心跳 (15.0s)
[14:30:30] 💓 心跳 (15.0s)
[14:30:45] 💓 心跳 (15.0s)
```

这确保了连接不会因为超时而断开。

## 使用 curl 测试

### 非流式

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "打开百度"}],
    "stream": false
  }'
```

### 流式

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "搜索 Python"}],
    "stream": true
  }' \
  --no-buffer
```

## 错误处理

如果遇到问题：

1. **检查服务器日志**：查看 `run.py` 的输出
2. **验证请求格式**：确保 JSON 格式正确
3. **检查超时设置**：某些客户端可能需要增加超时时间

```python
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy",
    timeout=300.0  # 5 分钟超时
)
```

## 注意事项

1. **首次请求较慢**：首次请求需要初始化浏览器，可能需要 3-5 秒
2. **并发限制**：目前使用单个浏览器实例，不支持并发请求
3. **内存管理**：长时间运行可能需要定期重启浏览器

## 性能优化建议

1. **保持连接**：复用 OpenAI 客户端实例
2. **合理超时**：根据任务复杂度设置合适的超时时间
3. **错误重试**：实现指数退避的重试机制

```python
import time
from openai import OpenAI

def chat_with_retry(client, messages, max_retries=3):
    for i in range(max_retries):
        try:
            return client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                stream=False
            )
        except Exception as e:
            if i == max_retries - 1:
                raise
            wait_time = 2 ** i  # 指数退避
            print(f"重试 {i+1}/{max_retries}，等待 {wait_time}s...")
            time.sleep(wait_time)