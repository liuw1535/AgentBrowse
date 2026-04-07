"""配置管理模块"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM设置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4"
    temperature: float = 0.7
    
    # 浏览器设置
    browser_headless: bool = True
    browser_timeout: int = 30000
    browser_user_agent: Optional[str] = None
    browser_stealth_mode: bool = True  # 启用反自动化检测
    
    # API设置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: Optional[str] = None
    
    # Agent设置
    max_iterations: int = 10
    memory_key: str = "chat_history"
    verbose: bool = True
    
    # 日志设置
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()