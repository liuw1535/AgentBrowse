"""辅助函数"""

import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def is_valid_url(url: str) -> bool:
    """验证URL是否有效
    
    Args:
        url: 要验证的URL
        
    Returns:
        URL是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """标准化URL
    
    Args:
        url: 原始URL
        base_url: 基础URL（用于相对路径）
        
    Returns:
        标准化后的URL
    """
    if base_url and not is_valid_url(url):
        return urljoin(base_url, url)
    return url


def sanitize_text(text: str) -> str:
    """清理文本内容
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int = 1000) -> str:
    """截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."