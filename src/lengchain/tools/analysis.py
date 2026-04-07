"""分析相关工具"""

from pydantic import BaseModel, Field
from lengchain.tools.base import BrowserBaseTool
from lengchain.browser.parser import HTMLParser
from lengchain.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyzeInput(BaseModel):
    """分析工具输入"""
    analysis_type: str = Field(
        default="structure",
        description="分析类型: structure(页面结构), content(内容分析)"
    )


class AnalyzeTool(BrowserBaseTool):
    """页面分析工具"""
    
    name: str = "analyze_page"
    description: str = """分析当前页面的结构和内容。
使用场景: 了解页面组成、查找可交互元素。
参数:
- analysis_type: 分析类型，默认structure (可选)
  * structure: 页面结构分析
  * content: 内容分析
示例: analyze_page(analysis_type="structure")
"""
    args_schema: type[BaseModel] = AnalyzeInput
    
    async def _arun(self, analysis_type: str = "structure") -> str:
        """异步分析页面"""
        try:
            logger.info(f"分析页面: {analysis_type}")
            html = await self.browser_manager.get_html()
            current_url = await self.browser_manager.get_current_url()
            title = await self.browser_manager.get_title()
            
            parser = HTMLParser(html, current_url)
            
            if analysis_type == "structure":
                # 页面结构分析
                headings = parser.extract_headings()
                links = parser.extract_links(limit=10)
                meta = parser.extract_meta_info()
                
                result = f"页面分析 - {title}\n"
                result += f"URL: {current_url}\n\n"
                
                if meta:
                    result += "元信息:\n"
                    for key in ['description', 'keywords', 'author']:
                        if key in meta:
                            result += f"  {key}: {meta[key]}\n"
                    result += "\n"
                
                if headings:
                    result += f"标题结构 (共{len(headings)}个):\n"
                    for h in headings[:10]:
                        result += f"  {h['level']}: {h['text']}\n"
                    result += "\n"
                
                if links:
                    result += f"链接 (前{len(links)}个):\n"
                    for i, link in enumerate(links, 1):
                        result += f"  {i}. {link['text']}\n"
                
                return result
            
            elif analysis_type == "content":
                # 内容分析
                content = parser.extract_main_content()
                word_count = len(content.split())
                
                result = f"内容分析 - {title}\n"
                result += f"URL: {current_url}\n"
                result += f"字数: {word_count}\n\n"
                result += f"内容预览:\n{content[:500]}..."
                
                return result
            
            else:
                return f"不支持的分析类型: {analysis_type}"
        
        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SummarizeInput(BaseModel):
    """总结工具输入"""
    max_length: int = Field(default=200, description="总结最大长度，默认200字")


class SummarizeTool(BrowserBaseTool):
    """内容总结工具"""
    
    name: str = "summarize_page"
    description: str = """总结当前页面的主要内容。
使用场景: 快速了解页面内容、提取关键信息。
参数:
- max_length: 总结最大长度，默认200 (可选)
示例: summarize_page(max_length=200)
注意: 此工具返回页面主要内容的精简版本，不使用LLM生成摘要。
"""
    args_schema: type[BaseModel] = SummarizeInput
    
    async def _arun(self, max_length: int = 200) -> str:
        """异步总结页面"""
        try:
            logger.info("总结页面内容...")
            html = await self.browser_manager.get_html()
            current_url = await self.browser_manager.get_current_url()
            title = await self.browser_manager.get_title()
            
            parser = HTMLParser(html, current_url)
            
            # 提取元描述
            meta = parser.extract_meta_info()
            description = meta.get('description', '')
            
            # 提取主要内容
            content = parser.extract_main_content()
            
            result = f"页面总结 - {title}\n\n"
            
            if description:
                result += f"描述: {description}\n\n"
            
            # 截取主要内容
            if content:
                words = content.split()[:max_length]
                summary = ' '.join(words)
                result += f"主要内容:\n{summary}"
                if len(content.split()) > max_length:
                    result += "..."
            
            return result
        
        except Exception as e:
            error_msg = f"总结失败: {str(e)}"
            logger.error(error_msg)
            return error_msg