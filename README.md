# LangChain Browser Automation Assistant

浏览器自动化智能助手 - 基于 LangChain 和 LCEL 构建的智能浏览器自动化工具

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 项目简介

本项目是一个基于 LangChain 框架和 ReAct 模式构建的浏览器自动化AI助手。它能够通过自然语言理解用户意图，自动规划并执行浏览器操作任务，如网页导航、信息提取、内容分析等。

### 核心特性

- 🤖 **智能任务规划**: 使用 ReAct Agent 模式，自主分解和执行复杂任务
- 🌐 **浏览器自动化**: 基于 Playwright，支持完整的浏览器操作
- 🔧 **丰富的工具集**: 内置12+种浏览器操作工具
- 💬 **对话记忆**: 支持多轮对话和上下文记忆
- 🚀 **OpenAI兼容API**: 提供标准的 ChatCompletion 接口
- 📡 **流式响应**: 支持 SSE 流式输出
- 🎯 **易于扩展**: 简单的工具开发接口

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│           用户层 (API Client)            │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────┐
│       API服务层 (FastAPI Server)        │
│  • OpenAI兼容接口                       │
│  • 流式/非流式响应                       │
│  • 认证与日志                           │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│     Agent核心层 (ReAct Agent)           │
│  • 任务理解与规划                       │
│  • 工具选择与执行                       │
│  • 对话记忆管理                         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│        工具层 (Browser Tools)           │
│  • 导航工具 (navigate, wait, back...)  │
│  • 交互工具 (click, input, scroll...)  │
│  • 提取工具 (extract, search...)       │
│  • 分析工具 (analyze, summarize...)    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│     浏览器层 (Playwright Browser)       │
│  • Chromium 浏览器实例                  │
│  • HTML 解析器                          │
│  • 页面操作接口                         │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.14+
- OpenAI API Key (或兼容的 API 服务)

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/lengchain.git
cd lengchain

# 安装依赖
uv sync

# 安装 Playwright 浏览器
playwright install chromium
```

### 配置

复制环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要参数：

```env
# OpenAI配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 浏览器配置
BROWSER_HEADLESS=true

# API配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 使用方式

#### 1. 作为 Python 库使用

```python
import asyncio
from lengchain.agent.browser_agent import BrowserAgent

async def main():
    async with BrowserAgent() as agent:
        result = await agent.execute(
            "打开百度，搜索'LangChain'，总结搜索结果"
        )
        print(result)

asyncio.run(main())
```

#### 2. 启动 API 服务

```bash
# 启动服务器
uv run -m lengchain.api.server

# 或使用 uvicorn
uv run uvicorn lengchain.api.server:app --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

#### 3. 使用 API 客户端

```python
import requests

url = "http://localhost:8000/v1/chat/completions"
payload = {
    "model": "browser-agent",
    "messages": [
        {"role": "user", "content": "打开GitHub，搜索langchain"}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

## 🔧 内置工具

### 导航工具
- `navigate`: 导航到指定URL
- `wait_for_element`: 等待元素出现
- `go_back`: 返回上一页
- `reload_page`: 刷新页面

### 交互工具
- `click`: 点击元素
- `input_text`: 输入文本
- `scroll`: 滚动页面

### 提取工具
- `extract_content`: 提取页面内容
- `search_in_page`: 页面内搜索
- `take_screenshot`: 截图

### 分析工具
- `analyze_page`: 分析页面结构
- `summarize_page`: 总结页面内容

## 📚 示例

### 示例1: 基础搜索

```python
await agent.execute("打开百度，搜索'Python教程'")
```

### 示例2: 信息提取

```python
await agent.execute("""
访问 https://www.python.org
提取页面中所有的链接
总结页面的主要内容
""")
```

### 示例3: 复杂任务

```python
await agent.execute("""
1. 打开GitHub
2. 搜索'langchain'
3. 找到最受欢迎的仓库
4. 告诉我它的名称、star数和简介
""")
```

### 示例4: 自定义工具

查看 `examples/custom_tools.py` 了解如何创建和使用自定义工具。

## 📝 API 接口

### POST /v1/chat/completions

OpenAI 兼容的聊天补全接口

**请求体:**
```json
{
  "model": "browser-agent",
  "messages": [
    {"role": "user", "content": "打开百度搜索Python"}
  ],
  "stream": false
}
```

**响应:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "browser-agent",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "已成功打开百度并搜索Python..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### POST /v1/chat/reset

重置对话历史

### GET /health

健康检查

## 🛠️ 开发

### 项目结构

```
lengchain/
├── src/lengchain/
│   ├── agent/              # Agent 核心
│   │   ├── browser_agent.py
│   │   ├── memory.py
│   │   └── prompts.py
│   ├── api/                # API 服务
│   │   ├── server.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── middleware.py
│   ├── browser/            # 浏览器管理
│   │   ├── manager.py
│   │   └── parser.py
│   ├── tools/              # 工具集
│   │   ├── navigation.py
│   │   ├── interaction.py
│   │   ├── extraction.py
│   │   └── analysis.py
│   ├── utils/              # 工具函数
│   └── config.py           # 配置管理
├── examples/               # 示例代码
├── tests/                  # 测试
└── docs/                   # 文档
```

### 运行测试

```bash
pytest tests/
```

### 代码规范

```bash
# 格式化代码
black src/

# 类型检查
mypy src/

# Lint
ruff src/
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的LLM应用开发框架
- [Playwright](https://playwright.dev/) - 现代化的浏览器自动化工具
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架

## 🗺️ 路线图

- [ ] 支持更多浏览器引擎
- [ ] 增强错误处理和重试机制
- [ ] 添加会话管理功能
- [ ] 支持并发任务执行
- [ ] 提供可视化界面
- [ ] 完善测试覆盖率
- [ ] 支持插件系统

---

如果觉得这个项目有用，请给个 ⭐ Star！