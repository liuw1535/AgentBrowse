"""API路由"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from lengchain.api.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionStreamResponse,
    StreamChoice,
    Message,
    Usage
)
from lengchain.agent.browser_agent import BrowserAgent
from lengchain.utils.logger import get_logger
import uuid
import time
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator

logger = get_logger(__name__)

router = APIRouter()

# 全局Agent实例（在实际应用中可能需要会话管理）
_agent: BrowserAgent = None

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 15


async def get_agent() -> BrowserAgent:
    """获取或创建Agent实例"""
    global _agent
    if _agent is None:
        _agent = BrowserAgent()
        await _agent.initialize()
    return _agent


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI兼容的聊天接口
    
    Args:
        request: 聊天补全请求
        
    Returns:
        聊天补全响应或流式响应
    """
    try:
        # 提取用户消息
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到用户消息"
            )
        
        # 获取Agent
        agent = await get_agent()
        
        # 流式响应
        if request.stream:
            return StreamingResponse(
                stream_response(agent, user_message, request.model),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        
        # 非流式响应
        result = await agent.execute(user_message)
        return create_response(result, request.model)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def create_response(content: str, model: str) -> ChatCompletionResponse:
    """创建标准响应
    
    Args:
        content: 响应内容
        model: 模型名称
        
    Returns:
        ChatCompletionResponse对象
    """
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=Message(role="assistant", content=content),
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
    )


async def stream_response(
    agent: BrowserAgent,
    user_input: str,
    model: str
) -> AsyncGenerator[str, None]:
    """生成流式响应，包含心跳机制
    
    Args:
        agent: Agent实例
        user_input: 用户输入
        model: 模型名称
        
    Yields:
        SSE格式的数据
    """
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())
    last_heartbeat = datetime.now()
    has_sent_content = False
    
    def create_heartbeat():
        """创建心跳数据"""
        return ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[StreamChoice(index=0, delta={}, finish_reason=None)]
        )
    
    try:
        # 发送开始标记
        start_response = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta={"role": "assistant"},
                    finish_reason=None
                )
            ]
        )
        yield f"data: {start_response.model_dump_json()}\n\n"
        last_heartbeat = datetime.now()
        
        logger.info(f"开始流式执行: {user_input[:50]}...")
        
        # 直接迭代 Agent 的流式输出，添加心跳逻辑
        stream_iter = agent.stream_execute(user_input)
        
        # 创建一个任务来异步迭代
        chunk_available = asyncio.Event()
        current_chunk = None
        stream_done = False
        
        async def stream_reader():
            """读取流式数据"""
            nonlocal current_chunk, stream_done
            try:
                async for chunk in stream_iter:
                    logger.debug(f"收到 chunk 类型: {type(chunk)}")
                    if isinstance(chunk, dict):
                        logger.debug(f"chunk 键: {chunk.keys()}")
                    current_chunk = chunk
                    chunk_available.set()
                    # 等待 chunk 被处理
                    await asyncio.sleep(0)
            finally:
                stream_done = True
                chunk_available.set()  # 唤醒等待
        
        # 启动读取任务
        reader_task = asyncio.create_task(stream_reader())
        
        try:
            while not stream_done:
                try:
                    # 等待新数据或超时
                    await asyncio.wait_for(
                        chunk_available.wait(),
                        timeout=HEARTBEAT_INTERVAL
                    )
                    
                    # 处理 chunk
                    if current_chunk is not None:
                        chunk = current_chunk
                        current_chunk = None
                        chunk_available.clear()
                        
                        if isinstance(chunk, dict):
                            logger.debug(f"处理 chunk 键: {chunk.keys()}")
                            
                            # LangGraph 返回格式: {'agent': {'messages': [...]}}
                            # 或者 {'tools': {'messages': [...]}}
                            # 只发送 agent 节点的输出，跳过工具调用的中间细节
                            for node_name, node_data in chunk.items():
                                if isinstance(node_data, dict) and 'messages' in node_data:
                                    messages = node_data['messages']
                                    logger.debug(f"节点 '{node_name}' 包含 {len(messages)} 条消息")
                                    
                                    # 只处理 agent 节点的消息，跳过 tools 节点
                                    if node_name == 'agent' and messages:
                                        last_msg = messages[-1]
                                        if hasattr(last_msg, 'content'):
                                            content = str(last_msg.content)
                                            logger.info(f"发送 AI 回复: {content[:100]}...")
                                            
                                            # 分块发送以模拟流式
                                            chunk_size = 50
                                            for i in range(0, len(content), chunk_size):
                                                chunk_content = content[i:i + chunk_size]
                                                response = ChatCompletionStreamResponse(
                                                    id=completion_id,
                                                    created=created,
                                                    model=model,
                                                    choices=[
                                                        StreamChoice(
                                                            index=0,
                                                            delta={"content": chunk_content},
                                                            finish_reason=None
                                                        )
                                                    ]
                                                )
                                                yield f"data: {response.model_dump_json()}\n\n"
                                                await asyncio.sleep(0.01)
                                            
                                            last_heartbeat = datetime.now()
                                            has_sent_content = True
                    
                except asyncio.TimeoutError:
                    # 超时，发送心跳
                    now = datetime.now()
                    if (now - last_heartbeat).total_seconds() >= HEARTBEAT_INTERVAL:
                        logger.info("发送心跳保持连接")
                        heartbeat = create_heartbeat()
                        yield f"data: {heartbeat.model_dump_json()}\n\n"
                        last_heartbeat = now
                    chunk_available.clear()
        
        finally:
            # 确保读取任务完成
            if not reader_task.done():
                reader_task.cancel()
                try:
                    await reader_task
                except asyncio.CancelledError:
                    pass
        
        # 如果没有发送任何内容，发送一个默认消息
        if not has_sent_content:
            logger.warning("未发送任何内容，发送默认消息")
            default_msg = "任务已完成"
            response = ChatCompletionStreamResponse(
                id=completion_id,
                created=created,
                model=model,
                choices=[
                    StreamChoice(
                        index=0,
                        delta={"content": default_msg},
                        finish_reason=None
                    )
                ]
            )
            yield f"data: {response.model_dump_json()}\n\n"
        
        # 发送结束标记
        logger.info("发送结束标记")
        end_response = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta={},
                    finish_reason="stop"
                )
            ]
        )
        yield f"data: {end_response.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    
    except Exception as e:
        logger.error(f"流式响应错误: {str(e)}", exc_info=True)
        error_response = {
            "error": {
                "message": str(e),
                "type": "server_error"
            }
        }
        yield f"data: {json.dumps(error_response)}\n\n"


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "browser-agent"}


@router.post("/v1/chat/reset")
async def reset_conversation():
    """重置对话（清空记忆）"""
    try:
        agent = await get_agent()
        agent.clear_memory()
        return {"status": "success", "message": "对话已重置"}
    except Exception as e:
        logger.error(f"重置对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )