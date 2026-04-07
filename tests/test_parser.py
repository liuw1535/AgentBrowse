"""HTML解析器测试"""

import pytest
from lengchain.browser.parser import HTMLParser


def test_extract_links():
    """测试链接提取"""
    html = """
    <html>
        <body>
            <a href="https://example.com">Example</a>
            <a href="/relative">Relative Link</a>
        </body>
    </html>
    """
    
    parser = HTMLParser(html, "https://test.com")
    links = parser.extract_links()
    
    assert len(links) == 2
    assert links[0]['text'] == "Example"
    assert links[0]['href'] == "https://example.com"


def test_extract_headings():
    """测试标题提取"""
    html = """
    <html>
        <body>
            <h1>Title 1</h1>
            <h2>Title 2</h2>
            <h3>Title 3</h3>
        </body>
    </html>
    """
    
    parser = HTMLParser(html)
    headings = parser.extract_headings()
    
    assert len(headings) == 3
    assert headings[0]['level'] == 'h1'
    assert headings[0]['text'] == "Title 1"


def test_extract_main_content():
    """测试主要内容提取"""
    html = """
    <html>
        <head><script>console.log('test')</script></head>
        <body>
            <main>
                <p>This is the main content.</p>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    
    parser = HTMLParser(html)
    content = parser.extract_main_content()
    
    assert "main content" in content
    assert "Footer" not in content
    assert "console.log" not in content