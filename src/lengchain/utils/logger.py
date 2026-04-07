"""日志配置模块"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "lengchain",
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        format_string: 日志格式字符串
        
    Returns:
        配置好的日志记录器
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str = "lengchain") -> logging.Logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return logging.getLogger(name)