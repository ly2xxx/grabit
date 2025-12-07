import asyncio
import logging
from playwright.async_api import async_playwright, Page, BrowserContext, Playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages a persistent browser session using Playwright.
    Allows extracting clickable elements and performing actions.
    """
    def __init__(self):
        self.playwright: Playwright = None
        self.browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self._is_running = False

    async def start_browser(self, headless=False):
        """Launches the browser if not already running."""
        if self._is_running and self.page:
            return

        self.playwright = await async_playwright().start()
        # Launch persistent context to keep login state matching user data dir if possible, 
        # but for this simple version we'll just keep the process alive.
        # To truly persist login across app restarts we would need launch_persistent_context 
        # pointed at a user data dir. For now, we assume "Session" persistence (keep app open).
        
        self.browser = await self.playwright.chromium.launch(headless=headless, args=["--start-maximized"])
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()
        self._is_running = True
        logger.info("Browser started.")

    async def navigate(self, url):
        """Navigates to the specified URL."""
        if not self._is_running or not self.page:
            await self.start_browser()
        
        await self.page.goto(url)
    
    async def get_clickable_items(self):
        """
        Scans the page for likely "Tee Time" buttons or links.
        Returns a list of dicts: {'text': str, 'selector': str, 'type': str}
        """
        if not self.page:
            return []

        # This JS script finds likely booking buttons
        # We look for typical patterns: time formats (XX:XX) or "Book" text
        items = await self.page.evaluate('''() => {
            const items = [];
            const buttons = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
            
            buttons.forEach((el, index) => {
                const text = el.innerText.trim();
                const isTime = /\d{1,2}:\d{2}/.test(text); // Matches 07:00, 7:30
                const isBook = /book/i.test(text);
                const hasPrice = /£|€|\$/.test(text);
                
                // Heuristic: If it has a time, or says "Book", it's interesting
                if ((isTime || isBook) && el.offsetParent !== null) { // visible
                    // Create a unique selector or use path
                    // Ideally we'd have a robust path generator, but for now we'll rely on text matching if unique, or index
                    items.push({
                        text: text.replace(/[\n\r]+/g, ' '), // Clean newlines
                        selector: `xpath=(${getElementXPath(el)})`, // Unique selector
                        index: index
                    });
                }
            });

            function getElementXPath(element) {
                if (element.id !== '')
                    return '//*[@id="' + element.id + '"]';
                if (element === document.body)
                    return element.tagName;

                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getElementXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                        ix++;
                }
            }

            return items;
        }''')
        
        return items

    async def click_element(self, selector):
        """Clicks the element identified by the selector."""
        if not self.page:
            return False
        
        try:
            # Wait for element to be visible/enabled
            await self.page.click(selector, timeout=2000)
            return True
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False

    async def refresh_and_click(self, selector):
        """Reloads the page and attempts to click the selector immediately."""
        if not self.page:
            return False
            
        await self.page.reload()
        # Race condition: Element might not exist immediately properly
        # We can use wait_for_selector
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Auto-click failed: {e}")
            return False

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._is_running = False

# Global instance for Streamlit to access (though streamlit re-runs might need session state mgmt)
# In Streamlit, better to not use a global variable but attach to session_state, 
# but we can't pickle Playwright objects easily.
# We will likely need a singleton pattern or a separate process.
# FOR NOW: We'll try a singleton pattern here, but be aware Streamlit might lose reference on reload 
# if not careful. However, since the Python process persists, a module-level variable persists.
_manager_instance = None

def get_manager():
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = BrowserManager()
    return _manager_instance
