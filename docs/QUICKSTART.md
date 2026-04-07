# 快速开始指南

本指南将帮助您快速上手 LangChain Browser Automation Assistant。

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/lengchain.git
cd lengchain
```

### 2. 创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装项目
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

### 4. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入您的 OpenAI API Key
# OPENAI_API_KEY=sk-...
```

## 使用方式

### 方式一：命令行交互模式

最简单的使用方式，适合快速测试：

```bash
python -m lengchain.cli
```

然后输入您的任务：

```
您: 打开百度，搜索'Python教程'
助手: 正在执行任务...
```

### 方式二：Python 脚本

创建一个 Python 文件 `test.py`:

```python
import asyncio
from lengchain.agent.browser_agent import BrowserAgent

async def main():
    # 使用上下文管理器，自动处理浏览器生命周期
    async with BrowserAgent() as agent:
        # 执行任务
        result = await agent.execute(
            "打开 https://www.python.org，提取页面主要内容"
        )
        print(result)

# 运行
asyncio.run(main())
```

运行脚本：

```bash
python test.py
```

### 方式三：API 服务

#### 启动服务器

```bash
# 方式1: 使用 run.py
python run.py server

# 方式2: 直接运行
python -m lengchain.api.server

# 方式3: 使用 uvicorn
uvicorn lengchain.api.server:app --host 0.0.0.0 --port 8000
```

#### 访问 API 文档

浏览器打开: http://localhost:8000/docs

#### 使用 curl 测试

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "browser-agent",
    "messages": [
      {"role": "user", "content": "打开百度搜索Python"}
    ]
  }'
```

#### 使用 Python 客户端

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "browser-agent",
        "messages": [
            {"role": "user", "content": "打开GitHub，搜索langchain"}
        ],
        "stream": False
    }
)

result = response.json()
print(result['choices'][0]['message']['content'])
```

## 常见任务示例

### 1. 网页导航

```python
await agent.execute("打开 https://www.example.com")
```

### 2. 信息搜索

```python
await agent.execute("打开百度，搜索'人工智能'")
```

### 3. 内容提取

```python
await agent.execute("""
打开 https://www.python.org
提取页面中所有的标题
提取页面主要内容
""")
```

### 4. 页面分析

```python
await agent.execute("访问 https://github.com，分析页面结构")
```

### 5. 复杂任务

```python
await agent.execute("""
1. 打开GitHub
2. 搜索'langchain'
3. 找到最受欢迎的项目
4. 提取项目名称、star数量和简介
5. 总结这些信息
""")
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | OpenAI API密钥 | 必需 |
| OPENAI_BASE_URL | API地址 | https://api.openai.com/v1 |
| MODEL_NAME | 模型名称 | gpt-4 |
| BROWSER_HEADLESS | 无头模式 | true |
| API_PORT | API端口 | 8000 |

### 浏览器设置

```python
from lengchain.browser.manager import BrowserManager

# 自定义浏览器设置
manager = BrowserManager(
    headless=False,  # 显示浏览器窗口
    timeout=60000,   # 60秒超时
)
```

### Agent 设置

```python
from lengchain.agent.browser_agent import BrowserAgent

agent = BrowserAgent(
    max_iterations=15,  # 最大迭代次数
    verbose=True,       # 详细输出
)
```

## 故障排除

### 问题1: Playwright 浏览器未安装

```bash
# 解决方案
playwright install chromium
```

### 问题2: OpenAI API 连接失败

检查以下几点：
1. API Key 是否正确
2. 网络连接是否正常
3. BASE_URL 是否正确

### 问题3: 浏览器启动失败

```bash
# 在 Linux 上可能需要安装依赖
playwright install-deps chromium
```

### 问题4: 导入错误

确保已正确安装项目：

```bash
pip install -e .
```

## 下一步

- 查看 [示例代码](../examples/) 了解更多用法
- 阅读 [API 文档](API.md) 了解接口详情
- 学习如何 [自定义工具](CUSTOM_TOOLS.md)
- 了解 [架构设计](DESIGN.md)

## 获取帮助

- 查看 [FAQ](FAQ.md)
- 提交 [Issue](https://github.com/yourusername/lengchain/issues)
- 加入讨论组

祝您使用愉快！