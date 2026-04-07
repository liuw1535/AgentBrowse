"""测试反自动化检测模式"""

import asyncio
from lengchain.browser.manager import BrowserManager


async def test_stealth_mode():
    """测试反自动化检测功能"""
    
    print("=" * 60)
    print("测试反自动化检测模式")
    print("=" * 60)
    
    # 创建浏览器管理器（启用反自动化检测）
    async with BrowserManager(
        headless=False,  # 使用有界面模式以便观察
        stealth_mode=True
    ) as browser:
        # 导航到测试网站
        test_url = "https://bot.sannysoft.com/"  # 一个检测机器人的网站
        print(f"\n导航到测试网站: {test_url}")
        await browser.navigate(test_url)
        
        # 等待页面加载
        await asyncio.sleep(5)
        
        # 获取检测结果
        print("\n检查检测结果...")
        
        # 检查webdriver属性
        webdriver_result = await browser.page.evaluate("navigator.webdriver")
        print(f"navigator.webdriver: {webdriver_result}")
        
        # 检查chrome对象
        chrome_result = await browser.page.evaluate("typeof window.chrome")
        print(f"window.chrome: {chrome_result}")
        
        # 检查plugins
        plugins_result = await browser.page.evaluate("navigator.plugins.length")
        print(f"navigator.plugins.length: {plugins_result}")
        
        # 检查languages
        languages_result = await browser.page.evaluate("navigator.languages")
        print(f"navigator.languages: {languages_result}")
        
        print("\n按任意键继续...")
        input()
        
        # 测试另一个检测网站
        test_url2 = "https://arh.antoinevastel.com/bots/areyouheadless"
        print(f"\n导航到第二个测试网站: {test_url2}")
        await browser.navigate(test_url2)
        
        # 等待页面加载
        await asyncio.sleep(5)
        
        print("\n请手动检查页面上的检测结果...")
        print("按任意键结束测试...")
        input()
    
    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(test_stealth_mode())