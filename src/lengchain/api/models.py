"""API数据模型"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


class Message(BaseModel):
    """聊天消息"""
    role: Literal["system", "user", "assistant"] = Field(description="角色")
    content: str = Field(description="消息内容")


class ChatCompletionRequest(BaseModel):
    """聊天补全请求"""
    model: str = Field(default="browser-agent", description="模型名称")
    messages: List[Message] = Field(description="消息列表")
    temperature: Optional[float] = Field(default=0.7, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大token数")
    stream: bool = Field(default=False, description="是否流式返回")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "browser-agent",
                "messages": [
                    {"role": "user", "content": "帮我打开百度搜索LangChain"}
                ],
                "temperature": 0.7,
                "stream": False
            }
        }


class Usage(BaseModel):
    """Token使用情况"""
    prompt_tokens: int = Field(default=0, description="提示词token数")
    completion_tokens: int = Field(default=0, description="补全token数")
    total_tokens: int = Field(default=0, description="总token数")


class ChatCompletionChoice(BaseModel):
    """聊天补全选项"""
    index: int = Field(description="选项索引")
    message: Message = Field(description="消息")
    finish_reason: Optional[str] = Field(default="stop", description="完成原因")


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""
    id: str = Field(description="响应ID")
    object: str = Field(default="chat.completion", description="对象类型")
    created: int = Field(description="创建时间戳")
    model: str = Field(description="模型名称")
    choices: List[ChatCompletionChoice] = Field(description="选项列表")
    usage: Usage = Field(description="使用情况")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "browser-agent",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "已打开百度并搜索LangChain"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                }
            }
        }


class StreamChoice(BaseModel):
    """流式响应选项"""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """流式聊天补全响应"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]