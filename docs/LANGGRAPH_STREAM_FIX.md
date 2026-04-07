# LangGraph 流式响应修复说明

## 问题描述

在使用 OpenAI 兼容接口时,流式响应无法正常工作,导致:
- API 接口返回默认消息 "任务已完成"
- 无法获取 Agent 的实际执行结果
- CLI 模式工作正常,但 API 流式模式失败

## 问题根源

**数据格式不匹配**

`routes.py` 中的流式响应处理逻辑期望的数据格式:
```python
{
    'actions': [...],
    'messages': [...]
}
```

但 LangGraph 的 `astream()` 实际返回的格式:
```python
{
    'agent': {
        'messages': [AIMessage(...)]
    }
}
```

或者:
```python
{
    'tools': {
        'messages': [...]
    }
}
```

## 修复方案

修改 `src/lengchain/api/routes.py` 中的 `stream_response()` 函数,正确处理 LangGraph 的输出格式:

### 修改前
```python
# 处理 Agent 动作
if "actions" in chunk:
    # ...

# 处理消息（最终输出）
if "messages" in chunk:
    # ...
```

### 修改后
```python
# LangGraph 返回格式: {'agent': {'messages': [...]}}
# 或者 {'tools': {'messages': [...]}}
# 提取实际内容
for node_name, node_data in chunk.items():
    if isinstance(node_data, dict) and 'messages' in node_data:
        messages = node_data['messages']
        # 处理消息...
```

## 验证步骤

1. **启动服务器**
   ```bash
   python -m lengchain.api.server
   ```

2. **测试流式响应**
   ```bash
   python examples/test_simple_stream.py
   ```

3. **检查日志输出**
   - 应该看到: `发送输出 (来自节点 'agent'): ...`
   - 不应该看到: `未发送任何内容，发送默认消息`

## 测试脚本

创建 `test_langgraph_stream.py` 来查看 LangGraph 的实际输出格式:

```python
"""测试 LangGraph 流式输出格式"""
import asyncio
from lengchain.agent.browser_agent import BrowserAgent

async def test_stream_format():
    agent = BrowserAgent(verbose=False)
    await agent.initialize()
    
    async for chunk in agent.stream_execute("测试消息"):
        print(f"类型: {type(chunk)}")
        if isinstance(chunk, dict):
            print(f"键: {chunk.keys()}")
            for key, value in chunk.items():
                print(f"{key}: {type(value)}")
    
    await agent.close()

asyncio.run(test_stream_format())
```

## 相关文件

- `src/lengchain/api/routes.py` - API 路由和流式响应处理
- `src/lengchain/agent/browser_agent.py` - Agent 实现
- `examples/test_simple_stream.py` - 流式响应测试
- `test_langgraph_stream.py` - LangGraph 输出格式测试

## 技术细节

### LangGraph 的流式输出

LangGraph 的 `astream()` 方法会为每个执行的节点(node)产生一个 chunk:

```python
{
    'node_name': {
        'messages': [Message1, Message2, ...],
        # 其他节点特定数据
    }
}
```

常见的节点名称:
- `agent` - Agent 节点,包含 AI 的响应
- `tools` - 工具节点,包含工具执行结果
- `__start__` - 开始节点
- `__end__` - 结束节点

### 消息类型

LangGraph 使用 LangChain 的消息类型:
- `AIMessage` - AI 生成的消息
- `HumanMessage` - 用户输入的消息
- `ToolMessage` - 工具执行结果
- `SystemMessage` - 系统提示

### 提取内容

从消息中提取文本内容:
```python
if hasattr(message, 'content'):
    content = str(message.content)
```

## 相关问题

如果遇到类似问题:

1. **检查 LangGraph 版本** - 不同版本的输出格式可能略有不同
2. **启用调试日志** - 设置 `logger.setLevel(logging.DEBUG)` 查看详细输出
3. **测试输出格式** - 使用测试脚本查看实际的 chunk 结构
4. **检查节点配置** - 确认 Agent 的节点配置正确

## 更新日期

2026-04-07

## 作者

陈七