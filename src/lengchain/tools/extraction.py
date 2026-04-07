"""内容提取相关工具"""

from pydantic import BaseModel, Field
from typing import Optional
from lengchain.tools.base import BrowserBaseTool
from lengchain.browser.parser import HTMLParser
from lengchain.utils.logger import get_logger
from lengchain.utils.helpers import truncate_text

logger = get_logger(__name__)


class ExtractInput(BaseModel):
    """提取工具输入"""
    content_type: str = Field(
        default="main",
        description="提取内容类型: main(主要内容), links(链接), headings(标题), text(所有文本), meta(元信息)"
    )
    selector: Optional[str] = Field(default=None, description="CSS选择器（可选，用于提取特定元素）")
    limit: Optional[int] = Field(default=None, description="限制数量（可选）")


class ExtractTool(BrowserBaseTool):
    """内容提取工具"""
    
    name: str = "extract_content"
    description: str = """从当前页面提取内容。
使用场景: 获取页面文本、链接、标题等信息。
参数:
- content_type: 内容类型，默认main (可选)
  * main: 主要内容
  * links: 所有链接
  * headings: 标题
  * text: 全部文本
  * meta: 元信息
- selector: CSS选择器，用于提取特定元素 (可选)
- limit: 限制数量 (可选)
示例: extract_content(content_type="links", limit=10)
"""
    args_schema: type[BaseModel] = ExtractInput
    
    async def _arun(
        self,
        content_type: str = "main",
        selector: Optional[str] = None,
        limit: Optional[int] = None
    ) -> str:
        """异步提取内容"""
        try:
            logger.info(f"提取内容类型: {content_type}")
            html = await self.browser_manager.get_html()
            current_url = await self.browser_manager.get_current_url()
            
            parser = HTMLParser(html, current_url)
            
            if content_type == "main":
                content = parser.extract_main_content()
                return truncate_text(content, 2000)
            
            elif content_type == "links":
                links = parser.extract_links(limit)
                if not links:
                    return "未找到链接"
                result = "提取到的链接:\n"
                for i, link in enumerate(links, 1):
                    result += f"{i}. {link['text']}: {link['href']}\n"
                return result
            
            elif content_type == "headings":
                headings = parser.extract_headings()
                if not headings:
                    return "未找到标题"
                result = "提取到的标题:\n"
                for heading in headings:
                    result += f"{heading['level']}: {heading['text']}\n"
                return result
            
            elif content_type == "text":
                if selector:
                    text = parser.extract_text_from_selector(selector)
                else:
                    text = parser.extract_main_content()
                return truncate_text(text, 2000)
            
            elif content_type == "meta":
                meta = parser.extract_meta_info()
                if not meta:
                    return "未找到元信息"
                result = "元信息:\n"
                for key, value in meta.items():
                    result += f"{key}: {value}\n"
                return result
            
            else:
                return f"不支持的内容类型: {content_type}"
        
        except Exception as e:
            error_msg = f"提取内容失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SearchInput(BaseModel):
    """搜索工具输入"""
    query: str = Field(description="要搜索的关键词")


class SearchTool(BrowserBaseTool):
    """页面搜索工具"""
    
    name: str = "search_in_page"
    description: str = """在当前页面中搜索关键词。
使用场景: 在页面中查找特定内容。
参数:
- query: 搜索关键词 (必需)
示例: search_in_page(query="LangChain")
"""
    args_schema: type[BaseModel] = SearchInput
    
    async def _arun(self, query: str) -> str:
        """异步搜索"""
        try:
            logger.info(f"在页面中搜索: {query}")
            html = await self.browser_manager.get_html()
            current_url = await self.browser_manager.get_current_url()
            
            parser = HTMLParser(html, current_url)
            content = parser.extract_main_content()
            
            if query.lower() in content.lower():
                # 提取包含关键词的上下文
                lines = content.split('\n')
                results = []
                for line in lines:
                    if query.lower() in line.lower():
                        results.append(line.strip())
                
                if results:
                    result = f"找到 {len(results)} 处匹配:\n"
                    for i, match in enumerate(results[:10], 1):
                        result += f"{i}. {match}\n"
                    return result
            
            return f"未找到关键词 '{query}'"
        
        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ScreenshotInput(BaseModel):
    """截图工具输入"""
    path: Optional[str] = Field(default=None, description="保存路径（可选）")
    full_page: bool = Field(default=False, description="是否截取整个页面，默认false")


class ScreenshotTool(BrowserBaseTool):
    """截图工具"""
    
    name: str = "take_screenshot"
    description: str = """对当前页面进行截图。
使用场景: 保存页面状态、记录页面内容。
参数:
- path: 保存路径 (可选)
- full_page: 是否截取整页，默认false (可选)
示例: take_screenshot(path="screenshot.png", full_page=true)
"""
    args_schema: type[BaseModel] = ScreenshotInput
    
    async def _arun(self, path: Optional[str] = None, full_page: bool = False) -> str:
        """异步截图"""
        try:
            logger.info("正在截图...")
            await self.browser_manager.screenshot(path, full_page)
            
            if path:
                return f"截图已保存到: {path}"
            return "截图完成（未保存到文件）"
        
        except Exception as e:
            error_msg = f"截图失败: {str(e)}"
            logger.error(error_msg)
            return error_msg