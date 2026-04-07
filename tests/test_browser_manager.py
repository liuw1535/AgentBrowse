"""浏览器管理器测试"""

import pytest
from lengchain.browser.manager import BrowserManager


@pytest.mark.asyncio
async def test_browser_initialization():
    """测试浏览器初始化"""
    manager = BrowserManager(headless=True)
    
    await manager.initialize()
    assert manager._initialized is True
    
    await manager.close()
    assert manager._initialized is False


@pytest.mark.asyncio
async def test_browser_navigation():
    """测试浏览器导航"""
    async with BrowserManager(headless=True) as manager:
        await manager.navigate("https://www.example.com")
        
        url = await manager.get_current_url()
        assert "example.com" in url
        
        title = await manager.get_title()
        assert len(title) > 0


@pytest.mark.asyncio
async def test_browser_extract_text():
    """测试文本提取"""
    async with BrowserManager(headless=True) as manager:
        await manager.navigate("https://www.example.com")
        
        text = await manager.extract_text()
        assert len(text) > 0
        assert "Example Domain" in text