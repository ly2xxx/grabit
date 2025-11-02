"""
Web content extraction module using Playwright.

This module provides functionality to extract and clean content from web pages,
including taking screenshots and parsing HTML for structured content.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("playwright is required. Install it with: pip install playwright")

# Configure logging
logger = logging.getLogger(__name__)


class WebContentExtractor:
    """Extracts clean content from web pages using Playwright."""
    
    def __init__(self, screenshots_dir: str = "screenshots"):
        """
        Initialize the extractor.
        
        Args:
            screenshots_dir: Directory to save screenshots to
        """
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def extract_clean_content(self, url: str) -> Dict[str, Any]:
        """
        Extract and clean content from a URL.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to the URL
                await page.goto(url, wait_until="networkidle")
                
                # Take a screenshot
                screenshot_path = await self._take_screenshot(page, url)
                
                # Extract content
                clean_data = await self._extract_content(page, url)
                
                return {
                    "url": url,
                    "screenshot_path": screenshot_path,
                    "clean_data": clean_data,
                    "extracted_at": datetime.now().isoformat(),
                }
            
            except Exception as e:
                logger.error(f"Error extracting content from {url}: {e}")
                raise
            
            finally:
                await browser.close()
    
    async def _take_screenshot(self, page, url: str) -> str:
        """
        Take a screenshot of the page.
        
        Args:
            page: Playwright page object
            url: URL being captured (for filename)
            
        Returns:
            Path to the saved screenshot
        """
        # Create a filename from the URL
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.screenshots_dir / filename
        
        await page.screenshot(path=str(filepath), full_page=True)
        return str(filepath)
    
    async def _extract_content(self, page, url: str) -> Dict[str, Any]:
        """
        Extract structured content from the page.
        
        Args:
            page: Playwright page object
            url: URL being parsed
            
        Returns:
            Dictionary with title, main content, and links
        """
        # Extract title
        title = await page.title()
        
        # Extract main content
        main_content = await self._extract_main_content(page)
        
        # Extract links
        links = await self._extract_links(page)
        
        return {
            "title": title,
            "url": url,
            "main_content": main_content,
            "links": links,
        }
    
    async def _extract_main_content(self, page) -> List[Dict[str, str]]:
        """
        Extract main content (headings, paragraphs, etc.).
        
        Args:
            page: Playwright page object
            
        Returns:
            List of content items with type and text
        """
        content = []
        
        try:
            # Extract headings
            h1_elements = await page.query_selector_all("h1")
            for elem in h1_elements:
                text = await elem.text_content()
                if text and text.strip():
                    content.append({"type": "h1", "text": text.strip()})
            
            h2_elements = await page.query_selector_all("h2")
            for elem in h2_elements[:10]:  # Limit to first 10
                text = await elem.text_content()
                if text and text.strip():
                    content.append({"type": "h2", "text": text.strip()})
            
            # Extract paragraphs
            p_elements = await page.query_selector_all("p")
            for elem in p_elements[:15]:  # Limit to first 15
                text = await elem.text_content()
                if text and text.strip() and len(text.strip()) > 20:  # Minimum length
                    content.append({"type": "p", "text": text.strip()})
        
        except Exception as e:
            logger.warning(f"Error extracting main content: {e}")
        
        return content
    
    async def _extract_links(self, page) -> List[Dict[str, str]]:
        """
        Extract links from the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of links with text and URL
        """
        links = []
        
        try:
            a_elements = await page.query_selector_all("a[href]")
            for elem in a_elements[:20]:  # Limit to first 20
                href = await elem.get_attribute("href")
                text = await elem.text_content()
                
                if href and text and text.strip():
                    links.append({
                        "text": text.strip(),
                        "url": href,
                    })
        
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
        
        return links


# Global extractor instance
_extractor = None


async def extract_clean_content(url: str) -> Dict[str, Any]:
    """
    Extract clean content from a URL.
    
    This is the main entry point for content extraction.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        Dictionary containing extracted content, screenshots, and metadata
    """
    global _extractor
    
    if _extractor is None:
        _extractor = WebContentExtractor()
    
    return await _extractor.extract_clean_content(url)


if __name__ == "__main__":
    # Example usage
    async def main():
        url = "https://example.com"
        result = await extract_clean_content(url)
        print(f"Extracted content from: {result['url']}")
        print(f"Title: {result['clean_data']['title']}")
        print(f"Screenshot saved to: {result['screenshot_path']}")
    
    asyncio.run(main())
