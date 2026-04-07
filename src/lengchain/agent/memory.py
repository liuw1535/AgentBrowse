"""记忆管理模块"""

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any


class BrowserMemory:
    """浏览器Agent专用记忆
    
    注意: LangGraph agent 内置了状态管理，这个类主要用于向后兼容
    """
    
    def __init__(self, **kwargs):
        """初始化记忆
        
        Args:
            **kwargs: 保留用于向后兼容
        """
        self.messages: List[BaseMessage] = []
        self.max_messages = kwargs.get('max_messages', 20)
    
    def add_message(self, message: BaseMessage) -> None:
        """添加消息到记忆
        
        Args:
            message: 要添加的消息
        """
        self.messages.append(message)
        # 保持最大消息数限制
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[BaseMessage]:
        """获取所有消息
        
        Returns:
            消息列表
        """
        return self.messages
    
    def get_context(self) -> str:
        """获取对话上下文
        
        Returns:
            格式化的对话历史
        """
        if not self.messages:
            return "暂无对话历史"
        
        context = "对话历史:\n"
        for msg in self.messages[-10:]:  # 只显示最近10条
            if isinstance(msg, HumanMessage):
                role = "用户"
            elif isinstance(msg, AIMessage):
                role = "助手"
            else:
                role = msg.__class__.__name__
            
            content = msg.content if hasattr(msg, 'content') else str(msg)
            context += f"{role}: {content}\n"
        
        return context
    
    def clear(self) -> None:
        """清空记忆"""
        self.messages.clear()
