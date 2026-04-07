"""浏览器管理器"""

from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from lengchain.utils.logger import get_logger
from lengchain.config import settings

logger = get_logger(__name__)


class BrowserManager:
    """浏览器实例管理器
    
    负责管理Playwright浏览器实例、上下文和页面
    """
    
    def __init__(
        self,
        headless: bool = None,
        timeout: int = None,
        user_agent: Optional[str] = None,
        stealth_mode: bool = None
    ):
        """初始化浏览器管理器
        
        Args:
            headless: 是否无头模式
            timeout: 超时时间（毫秒）
            user_agent: 自定义User-Agent
            stealth_mode: 是否启用反自动化检测模式
        """
        self.headless = headless if headless is not None else settings.browser_headless
        self.timeout = timeout if timeout is not None else settings.browser_timeout
        self.user_agent = user_agent or settings.browser_user_agent
        self.stealth_mode = stealth_mode if stealth_mode is not None else settings.browser_stealth_mode
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化浏览器"""
        if self._initialized:
            logger.warning("浏览器已经初始化")
            return
        
        try:
            logger.info("正在启动浏览器...")
            self._playwright = await async_playwright().start()
            
            # 配置浏览器启动参数
            launch_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
            
            # 添加反自动化检测参数
            if self.stealth_mode:
                logger.info("启用反自动化检测模式")
                launch_args.extend([
                    '--disable-blink-features=AutomationControlled',  # 禁用自动化控制特征
                    '--disable-dev-shm-usage',  # 禁用/dev/shm使用
                    '--disable-web-security',  # 禁用web安全
                    '--disable-features=IsolateOrigins,site-per-process',  # 禁用站点隔离
                    '--disable-site-isolation-trials',  # 禁用站点隔离试验
                    '--no-first-run',  # 不显示首次运行界面
                    '--no-default-browser-check',  # 不检查默认浏览器
                    '--disable-infobars',  # 禁用信息栏
                    '--window-size=1920,1080',  # 设置窗口大小
                ])
            
            # 启动浏览器
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=launch_args
            )
            
            # 创建上下文
            context_options: Dict[str, Any] = {
                "viewport": {"width": 1920, "height": 1080}
            }
            if self.user_agent:
                context_options["user_agent"] = self.user_agent
            
            self._context = await self._browser.new_context(**context_options)
            self._context.set_default_timeout(self.timeout)
            
            # 创建页面
            self._page = await self._context.new_page()
            
            # 注入反自动化检测脚本
            if self.stealth_mode:
                await self._inject_stealth_scripts()
            
            self._initialized = True
            logger.info("浏览器启动成功")
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            await self.close()
            raise
    
    @property
    def page(self) -> Page:
        """获取当前页面"""
        if not self._page:
            raise RuntimeError("浏览器未初始化，请先调用 initialize()")
        return self._page
    
    async def navigate(
        self,
        url: str,
        wait_until: str = "load"
    ) -> None:
        """导航到指定URL
        
        Args:
            url: 目标URL
            wait_until: 等待状态 (load, domcontentloaded, networkidle)
        """
        logger.info(f"导航到: {url}")
        await self.page.goto(url, wait_until=wait_until)
    
    async def get_html(self) -> str:
        """获取页面HTML内容"""
        return await self.page.content()
    
    async def get_current_url(self) -> str:
        """获取当前URL"""
        return self.page.url
    
    async def get_title(self) -> str:
        """获取页面标题"""
        return await self.page.title()
    
    async def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """点击元素
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒）
        """
        logger.info(f"点击元素: {selector}")
        await self.page.click(selector, timeout=timeout)
    
    async def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """填充输入框
        
        Args:
            selector: CSS选择器
            text: 要填充的文本
            timeout: 超时时间（毫秒）
        """
        logger.info(f"填充输入框: {selector}")
        await self.page.fill(selector, text, timeout=timeout)
    
    async def press(self, selector: str, key: str) -> None:
        """按键
        
        Args:
            selector: CSS选择器
            key: 按键名称（如 'Enter', 'Tab'）
        """
        await self.page.press(selector, key)
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """滚动页面
        
        Args:
            direction: 方向 (up, down, left, right)
            amount: 滚动距离（像素）
        """
        scroll_map = {
            "down": f"window.scrollBy(0, {amount})",
            "up": f"window.scrollBy(0, -{amount})",
            "right": f"window.scrollBy({amount}, 0)",
            "left": f"window.scrollBy(-{amount}, 0)"
        }
        
        script = scroll_map.get(direction, scroll_map["down"])
        await self.page.evaluate(script)
    
    async def wait_for_selector(
        self,
        selector: str,
        timeout: Optional[int] = None,
        state: str = "visible"
    ) -> None:
        """等待元素出现
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒）
            state: 元素状态 (attached, detached, visible, hidden)
        """
        await self.page.wait_for_selector(selector, timeout=timeout, state=state)
    
    async def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> bytes:
        """截图
        
        Args:
            path: 保存路径（可选）
            full_page: 是否截取整个页面
            
        Returns:
            截图的字节数据
        """
        return await self.page.screenshot(path=path, full_page=full_page)
    
    async def _inject_stealth_scripts(self) -> None:
        """注入反自动化检测脚本"""
        logger.info("注入反自动化检测脚本...")
        
        # 隐藏webdriver属性
        stealth_script = """
        // 覆盖navigator.webdriver属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 覆盖chrome对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 覆盖permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 覆盖plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // 覆盖languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // 覆盖platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        
        // 覆盖hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // 覆盖deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // 覆盖connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            })
        });
        
        // 添加自然的鼠标移动行为
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'mousemove') {
                const wrappedListener = function(e) {
                    // 模拟更自然的鼠标移动
                    listener.call(this, e);
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
        
        // 修改toString方法以隐藏代理
        const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');
        if (elementDescriptor && elementDescriptor.get) {
            const originalGetter = elementDescriptor.get;
            elementDescriptor.get = function() {
                return originalGetter.call(this);
            };
            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', elementDescriptor);
        }
        """
        
        try:
            await self._page.add_init_script(stealth_script)
            logger.info("反自动化检测脚本注入成功")
        except Exception as e:
            logger.warning(f"反自动化检测脚本注入失败: {str(e)}")
    
    async def extract_text(self, selector: Optional[str] = None) -> str:
        """提取文本内容
        
        Args:
            selector: CSS选择器（可选，默认提取整个页面）
            
        Returns:
            文本内容
        """
        if selector:
            element = await self.page.query_selector(selector)
            if element:
                return await element.inner_text()
            return ""
        return await self.page.inner_text("body")
    
    async def go_back(self) -> None:
        """后退"""
        await self.page.go_back()
    
    async def go_forward(self) -> None:
        """前进"""
        await self.page.go_forward()
    
    async def reload(self) -> None:
        """刷新页面"""
        await self.page.reload()
    
    async def close(self) -> None:
        """关闭浏览器"""
        logger.info("正在关闭浏览器...")
        
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {str(e)}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._initialized = False
            logger.info("浏览器已关闭")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()