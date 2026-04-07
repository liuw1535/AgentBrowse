# 浏览器自动化助理设计文档

## 1. 项目概述

### 1.1 项目名称
LangChain Browser Automation Assistant (浏览器自动化智能助手)

### 1.2 项目目标
基于LangChain和LCEL构建一个能够自主规划并操作浏览器的AI助手，通过自然语言理解用户意图，自动执行浏览器操作任务，如搜索、导航、信息提取和内容总结。

### 1.3 核心功能
- 自然语言任务理解与规划
- 浏览器自动化操作（导航、点击、输入、滚动等）
- 网页内容解析与提取
- 多步骤任务执行与状态管理
- 对话历史记忆
- OpenAI格式API接口

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│                 (HTTP Client / API Consumer)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST API (OpenAI格式)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      API 服务层                              │
│                    (FastAPI Server)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  路由层: /v1/chat/completions                         │  │
│  │  - 请求验证                                           │  │
│  │  - 流式/非流式响应                                     │  │
│  │  - 错误处理                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent 核心层                              │
│                  (LangChain ReAct Agent)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Executor                                       │  │
│  │  - 任务规划                                           │  │
│  │  - 工具选择                                           │  │
│  │  - 执行循环                                           │  │
│  │  - 结果总结                                           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Memory (对话历史)                                     │  │
│  │  - ConversationBufferMemory                           │  │
│  │  - 上下文管理                                         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     工具层                                   │
│                  (LangChain Tools)                          │
│  ┌────────────┬────────────┬────────────┬────────────────┐ │
│  │ 浏览器导航  │ 元素操作    │ 内容提取    │ 页面分析      │ │
│  │ Tool       │ Tool       │ Tool       │ Tool          │ │
│  │            │            │            │               │ │
│  │ - navigate │ - click    │ - extract  │ - analyze     │ │
│  │ - wait     │ - input    │ - scroll   │ - summarize   │ │
│  │ - back     │ - select   │ - search   │               │ │
│  └────────────┴────────────┴────────────┴────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   浏览器控制层                               │
│              (Playwright + BeautifulSoup4)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Browser Manager                                      │  │
│  │  - 浏览器实例管理                                      │  │
│  │  - 页面上下文管理                                      │  │
│  │  - 会话状态维护                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HTML Parser                                          │  │
│  │  - DOM解析                                            │  │
│  │  - 元素定位                                           │  │
│  │  - 内容提取                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件说明

#### 2.2.1 API服务层 (FastAPI)
- **职责**: 对外提供OpenAI兼容的REST API接口
- **主要功能**:
  - 处理 `/v1/chat/completions` 端点
  - 支持流式和非流式响应
  - 请求验证和错误处理
  - API密钥认证（可选）

#### 2.2.2 Agent核心层 (LangChain ReAct Agent)
- **职责**: 任务理解、规划和执行协调
- **主要功能**:
  - 使用ReAct模式进行推理和行动
  - 动态选择合适的工具
  - 管理多步骤任务执行流程
  - 维护对话上下文和历史

#### 2.2.3 工具层 (LangChain Tools)
- **职责**: 提供浏览器操作的原子能力
- **工具列表**:
  1. **NavigateTool**: 导航到指定URL
  2. **ClickTool**: 点击页面元素
  3. **InputTool**: 向输入框输入文本
  4. **ExtractTool**: 提取页面内容
  5. **ScrollTool**: 滚动页面
  6. **WaitTool**: 等待元素加载
  7. **AnalyzeTool**: 分析页面结构
  8. **SearchTool**: 在页面中搜索文本

#### 2.2.4 浏览器控制层
- **职责**: 底层浏览器操作实现
- **技术栈**:
  - Playwright: 浏览器自动化
  - BeautifulSoup4: HTML解析

## 3. 技术栈

### 3.1 核心依赖

```toml
[project.dependencies]
# LangChain 核心
langchain = ">=1.2.14"
langchain-core = ">=1.2.23"
langchain-openai = ">=1.1.12"

# Web 框架
fastapi = ">=0.115.0"
uvicorn = ">=0.32.0"
pydantic = ">=2.10.0"

# 浏览器自动化
playwright = ">=1.48.0"
beautifulsoup4 = ">=4.12.0"
lxml = ">=5.3.0"

# 工具库
httpx = ">=0.27.0"
python-dotenv = ">=1.0.0"
```

### 3.2 开发依赖

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "black>=24.10.0",
    "ruff>=0.8.0",
]
```

## 4. 项目目录结构

```
lengchain/
├── src/
│   ├── lengchain/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI应用入口
│   │   ├── config.py                  # 配置管理
│   │   │
│   │   ├── api/                       # API层
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # API路由
│   │   │   ├── models.py              # API数据模型
│   │   │   └── middleware.py          # 中间件
│   │   │
│   │   ├── agent/                     # Agent层
│   │   │   ├── __init__.py
│   │   │   ├── browser_agent.py       # ReAct Agent实现
│   │   │   ├── prompts.py             # Agent提示词
│   │   │   └── memory.py              # 记忆管理
│   │   │
│   │   ├── tools/                     # 工具层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 工具基类
│   │   │   ├── navigation.py          # 导航工具
│   │   │   ├── interaction.py         # 交互工具
│   │   │   ├── extraction.py          # 提取工具
│   │   │   └── analysis.py            # 分析工具
│   │   │
│   │   ├── browser/                   # 浏览器控制层
│   │   │   ├── __init__.py
│   │   │   ├── manager.py             # 浏览器管理器
│   │   │   ├── parser.py              # HTML解析器
│   │   │   └── utils.py               # 工具函数
│   │   │
│   │   └── utils/                     # 通用工具
│   │       ├── __init__.py
│   │       ├── logger.py              # 日志配置
│   │       └── helpers.py             # 辅助函数
│   │
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_browser.py
│
├── docs/                              # 文档目录
│   ├── DESIGN.md                      # 设计文档
│   ├── API.md                         # API文档
│   └── USAGE.md                       # 使用指南
│
├── examples/                          # 示例代码
│   ├── simple_search.py
│   └── news_summary.py
│
├── .env.example                       # 环境变量示例
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

## 5. 核心模块设计

### 5.1 Agent设计 (ReAct Pattern)

```python
# agent/browser_agent.py 伪代码

class BrowserAgent:
    """基于ReAct模式的浏览器自动化Agent"""
    
    def __init__(self, llm, tools, memory):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """创建Agent执行器"""
        # 使用LCEL构建Agent链
        agent_chain = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: self._format_scratchpad(x)
            )
            | prompt
            | llm
            | ReActOutputParser()
        )
        
        return AgentExecutor(
            agent=agent_chain,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10
        )
    
    async def execute(self, user_input: str) -> str:
        """执行用户任务"""
        result = await self.agent.ainvoke({
            "input": user_input
        })
        return result["output"]
```

### 5.2 工具设计 (LangChain Tools)

```python
# tools/navigation.py 伪代码

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class NavigateInput(BaseModel):
    """导航工具输入模型"""
    url: str = Field(description="要导航到的URL地址")
    wait_until: str = Field(
        default="load",
        description="等待状态: load, domcontentloaded, networkidle"
    )

class NavigateTool(BaseTool):
    """浏览器导航工具"""
    
    name: str = "navigate"
    description: str = """
    导航到指定的URL。
    使用场景: 打开网站、访问链接。
    参数:
    - url: 目标网址
    - wait_until: 等待页面加载状态
    """
    args_schema: type[BaseModel] = NavigateInput
    browser_manager: BrowserManager
    
    async def _arun(self, url: str, wait_until: str = "load") -> str:
        """异步执行导航"""
        try:
            await self.browser_manager.navigate(url, wait_until)
            current_url = await self.browser_manager.get_current_url()
            title = await self.browser_manager.get_title()
            return f"成功导航到 {current_url}，页面标题: {title}"
        except Exception as e:
            return f"导航失败: {str(e)}"
```

### 5.3 浏览器管理器设计

```python
# browser/manager.py 伪代码

class BrowserManager:
    """浏览器实例管理器"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def initialize(self):
        """初始化浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def navigate(self, url: str, wait_until: str = "load"):
        """导航到URL"""
        await self.page.goto(url, wait_until=wait_until)
    
    async def get_html(self) -> str:
        """获取页面HTML"""
        return await self.page.content()
    
    async def click(self, selector: str):
        """点击元素"""
        await self.page.click(selector)
    
    async def fill(self, selector: str, text: str):
        """填充输入框"""
        await self.page.fill(selector, text)
    
    async def extract_text(self, selector: str = None) -> str:
        """提取文本内容"""
        if selector:
            element = await self.page.query_selector(selector)
            return await element.inner_text() if element else ""
        return await self.page.inner_text("body")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
```

### 5.4 HTML解析器设计

```python
# browser/parser.py 伪代码

from bs4 import BeautifulSoup

class HTMLParser:
    """HTML解析器，用于内容提取和分析"""
    
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'lxml')
    
    def extract_links(self, limit: int = None) -> list[dict]:
        """提取所有链接"""
        links = []
        for a in self.soup.find_all('a', href=True)[:limit]:
            links.append({
                'text': a.get_text(strip=True),
                'href': a['href']
            })
        return links
    
    def extract_headings(self) -> list[str]:
        """提取标题"""
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in self.soup.find_all(tag):
                headings.append(heading.get_text(strip=True))
        return headings
    
    def extract_main_content(self) -> str:
        """提取主要内容"""
        # 移除script和style标签
        for tag in self.soup(['script', 'style']):
            tag.decompose()
        
        # 尝试找到主要内容区域
        main = (
            self.soup.find('main') or
            self.soup.find('article') or
            self.soup.find('div', class_='content') or
            self.soup.find('body')
        )
        
        return main.get_text(separator='\n', strip=True) if main else ""
    
    def find_elements(self, selector: str) -> list:
        """根据CSS选择器查找元素"""
        return self.soup.select(selector)
```

## 6. API接口设计

### 6.1 OpenAI兼容接口

```python
# api/models.py

from pydantic import BaseModel
from typing import List, Optional, Literal

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "browser-agent"
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict
```

### 6.2 API路由

```python
# api/routes.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Browser Automation Assistant API")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI兼容的聊天接口"""
    
    # 提取用户消息
    user_message = request.messages[-1].content
    
    # 执行Agent任务
    try:
        if request.stream:
            return StreamingResponse(
                stream_response(user_message),
                media_type="text/event-stream"
            )
        else:
            result = await agent.execute(user_message)
            return create_response(result, request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 7. 执行流程示例

### 7.1 任务: "帮我搜索今天的最新新闻"

```
1. 用户输入 → API层接收请求
   ↓
2. Agent层分析任务
   Thought: 需要打开新闻网站并搜索今天的新闻
   ↓
3. Agent选择工具: NavigateTool
   Action: navigate(url="https://news.google.com")
   ↓
4. 浏览器控制层执行
   - Playwright打开浏览器
   - 导航到目标URL
   - 等待页面加载
   ↓
5. 返回结果: "成功打开新闻网站"
   ↓
6. Agent继续规划
   Thought: 需要提取今天的新闻标题
   ↓
7. Agent选择工具: ExtractTool
   Action: extract(selector="article h3")
   ↓
8. 浏览器控制层执行
   - 获取页面HTML
   - BeautifulSoup解析
   - 提取新闻标题
   ↓
9. 返回结果: ["新闻1", "新闻2", "新闻3"...]
   ↓
10. Agent总结
    Final Answer: 格式化输出今天的新闻列表
    ↓
11. API层返回结果给用户
```

### 7.2 任务: "打开第一条新闻并总结内容"

```
1. Agent分析: 需要点击链接并提取内容
   ↓
2. 使用ClickTool点击第一条新闻
   ↓
3. 等待页面加载 (WaitTool)
   ↓
4. 提取文章内容 (ExtractTool)
   ↓
5. 使用LLM总结内容
   ↓
6. 返回总结结果
```

## 8. 关键技术要点

### 8.1 LCEL (LangChain Expression Language)

使用LCEL构建Agent链，实现灵活的组件组合：

```python
# 使用LCEL构建处理链
chain = (
    {"input": RunnablePassthrough()}
    | prompt
    | llm
    | output_parser
)
```

### 8.2 ReAct模式

Agent使用ReAct (Reasoning + Acting) 模式：
- **Thought**: 分析当前状态，规划下一步
- **Action**: 选择工具并执行
- **Observation**: 观察工具执行结果
- 循环直到完成任务

### 8.3 异步处理

全面使用异步编程提高性能：
- FastAPI异步路由
- Playwright异步API
- LangChain异步调用

### 8.4 错误处理

- 工具执行失败重试机制
- 浏览器超时处理
- Agent最大迭代限制
- 优雅的错误信息返回

## 9. 配置管理

### 9.1 环境变量 (.env)

```bash
# LLM配置
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 浏览器配置
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secret-key

# Agent配置
MAX_ITERATIONS=10
MEMORY_KEY=chat_history
```

### 9.2 配置类

```python
# config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM设置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4"
    
    # 浏览器设置
    browser_headless: bool = True
    browser_timeout: int = 30000
    
    # API设置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str = ""
    
    # Agent设置
    max_iterations: int = 10
    memory_key: str = "chat_history"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 10. 部署方案

### 10.1 本地开发

```bash
# 安装依赖
uv sync

# 安装Playwright浏览器
playwright install chromium

# 启动服务
uvicorn src.lengchain.main:app --reload --port 8000
```

### 10.2 生产部署

```bash
# 使用Docker
docker build -t browser-agent .
docker run -p 8000:8000 --env-file .env browser-agent

# 或使用docker-compose
docker-compose up -d
```

## 11. 测试策略

### 11.1 单元测试
- 测试各个工具的功能
- 测试HTML解析器
- 测试API端点

### 11.2 集成测试
- 测试完整的Agent执行流程
- 测试浏览器操作链
- 测试端到端场景

### 11.3 性能测试
- API响应时间
- 浏览器操作延迟
- 并发请求处理

## 12. 未来扩展

### 12.1 功能扩展
- [ ] 支持截图和视觉理解
- [ ] 支持表单自动填写
- [ ] 支持文件下载和上传
- [ ] 支持多标签页管理
- [ ] 支持Cookie和会话管理

### 12.2 性能优化
- [ ] 浏览器实例池化
- [ ] 智能等待策略
- [ ] 缓存机制
- [ ] 结果流式返回

### 12.3 工具增强
- [ ] 更多预定义工具
- [ ] 自定义工具支持
- [ ] 工具链组合
- [ ] 工具执行可视化

## 13. 安全考虑

- API密钥认证
- 请求频率限制
- URL白名单/黑名单
- 敏感信息过滤
- 浏览器沙箱隔离

## 14. 总结

本设计文档提供了一个完整的浏览器自动化助理架构方案，基于LangChain和LCEL实现，具有以下特点：

1. **模块化设计**: 清晰的分层架构，便于维护和扩展
2. **标准化接口**: OpenAI兼容API，易于集成
3. **智能化**: 使用ReAct Agent实现自主规划和执行
4. **可靠性**: 完善的错误处理和重试机制
5. **可扩展**: 灵活的工具系统，支持自定义扩展

该方案为构建强大的浏览器自动化助理提供了坚实的基础。