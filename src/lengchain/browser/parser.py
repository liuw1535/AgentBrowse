"""HTML解析器"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag
from lengchain.utils.logger import get_logger
from lengchain.utils.helpers import sanitize_text, normalize_url

logger = get_logger(__name__)


class HTMLParser:
    """HTML解析器，用于内容提取和分析"""
    
    def __init__(self, html: str, base_url: Optional[str] = None):
        """初始化解析器
        
        Args:
            html: HTML内容
            base_url: 基础URL（用于处理相对链接）
        """
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
    
    def extract_links(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """提取所有链接
        
        Args:
            limit: 限制数量
            
        Returns:
            链接列表，每个链接包含text和href
        """
        links = []
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            if self.base_url:
                href = normalize_url(href, self.base_url)
            
            links.append({
                'text': sanitize_text(a.get_text()),
                'href': href
            })
            
            if limit and len(links) >= limit:
                break
        
        return links
    
    def extract_headings(self) -> List[Dict[str, str]]:
        """提取所有标题
        
        Returns:
            标题列表，包含level和text
        """
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in self.soup.find_all(tag):
                headings.append({
                    'level': tag,
                    'text': sanitize_text(heading.get_text())
                })
        return headings
    
    def extract_main_content(self) -> str:
        """提取主要内容
        
        Returns:
            主要内容文本
        """
        # 移除script和style标签
        for tag in self.soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # 尝试找到主要内容区域
        main = (
            self.soup.find('main') or
            self.soup.find('article') or
            self.soup.find('div', class_=re.compile(r'content|main', re.I)) or
            self.soup.find('body')
        )
        
        if main:
            text = main.get_text(separator='\n', strip=True)
            return sanitize_text(text)
        return ""
    
    def extract_meta_info(self) -> Dict[str, str]:
        """提取元信息
        
        Returns:
            元信息字典
        """
        meta_info = {}
        
        # 提取title
        title_tag = self.soup.find('title')
        if title_tag:
            meta_info['title'] = sanitize_text(title_tag.get_text())
        
        # 提取meta标签
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_info[name] = content
        
        return meta_info
    
    def extract_images(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """提取图片
        
        Args:
            limit: 限制数量
            
        Returns:
            图片列表
        """
        images = []
        for img in self.soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            
            if self.base_url:
                src = normalize_url(src, self.base_url)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
            
            if limit and len(images) >= limit:
                break
        
        return images
    
    def find_elements(self, selector: str) -> List[Tag]:
        """根据CSS选择器查找元素
        
        Args:
            selector: CSS选择器
            
        Returns:
            元素列表
        """
        return self.soup.select(selector)
    
    def extract_text_from_selector(self, selector: str) -> str:
        """从选择器提取文本
        
        Args:
            selector: CSS选择器
            
        Returns:
            提取的文本
        """
        elements = self.find_elements(selector)
        if not elements:
            return ""
        
        texts = [sanitize_text(elem.get_text()) for elem in elements]
        return '\n'.join(texts)
    
    def extract_table_data(self, selector: Optional[str] = None) -> List[List[str]]:
        """提取表格数据
        
        Args:
            selector: 表格选择器（可选）
            
        Returns:
            表格数据（二维列表）
        """
        table = self.soup.find('table') if not selector else self.soup.select_one(selector)
        if not table:
            return []
        
        data = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(sanitize_text(cell.get_text()))
            if row_data:
                data.append(row_data)
        
        return data


import re