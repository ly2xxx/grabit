import streamlit as st
import streamlit.components.v1 as components
import webbrowser
import time
import os
import platform
import json
import asyncio
from io import BytesIO

# Fix Windows asyncio issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Environment detection
def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud vs local development"""
    # Streamlit Cloud runs on Linux with empty processor string
    # Also check for 'appuser' which is the default Streamlit Cloud user
    return platform.processor() == '' or os.getenv('USER') == 'appuser'

# ============================================================================
# Playwright Browser Automation
# ============================================================================

def check_playwright_available():
    """Check if Playwright is available"""
    return PLAYWRIGHT_AVAILABLE

def run_async(coro):
    """Run async function in sync context for Streamlit"""
    # Use persistent event loop if browser session is active
    if st.session_state.get('browser_active') and st.session_state.get('event_loop'):
        loop = st.session_state.event_loop

        # Validate loop is usable
        if loop.is_closed():
            print("[ERROR] Event loop is closed! Creating new temporary loop.")
            # Fall back to temporary loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        if loop.is_running():
            print("[ERROR] Event loop is already running! This shouldn't happen in Streamlit.")
            raise RuntimeError("Cannot run async function: event loop is already running")

        print(f"[DEBUG] Reusing persistent event loop (closed={loop.is_closed()}, running={loop.is_running()})")
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        except Exception as e:
            print(f"[ERROR] Failed to run async function on persistent loop: {e}")
            raise
    else:
        # Create temporary event loop for one-off operations
        print("[DEBUG] Creating temporary event loop for one-off operation")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

async def _navigate_to_page_async(url):
    """Navigate to a URL using Playwright (async)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            return True, "Navigation successful"
        except Exception as e:
            return False, f"Navigation failed: {str(e)}"
        finally:
            await browser.close()

def navigate_to_page(url):
    """Navigate to a URL using Playwright"""
    try:
        return run_async(_navigate_to_page_async(url))
    except Exception as e:
        return False, f"Navigation failed: {str(e)}"

async def _scan_clickable_elements_async(url, storage_state=None):
    """Scan page for all clickable elements (async) - reuses persistent browser if available"""
    # Check if we have a persistent browser session
    use_persistent = st.session_state.browser_active and st.session_state.browser_page is not None

    if use_persistent:
        # Reuse existing browser page
        page = st.session_state.browser_page
        temp_playwright = None
        
        temp_browser = None
        temp_context = None
        print(f"[DEBUG] Using persistent browser session for scanning: {url}")
    else:
        # Create temporary browser for this operation
        st.toast("⚠️ Starting NEW browser (Login session not detected!)", icon="⚠️")
        print(f"[DEBUG] Creating temporary browser for scanning: {url}")
        temp_playwright = await async_playwright().start()
        # User requested visible mode for debugging
        temp_browser = await temp_playwright.chromium.launch(headless=False)

        if storage_state:
            temp_context = await temp_browser.new_context(storage_state=storage_state)
        else:
            temp_context = await temp_browser.new_context()

        page = await temp_context.new_page()

    try:
        # domcontentloaded is much faster than networkidle for simple scanning
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Find all clickable elements using evaluate for performance (batch processing)
        # This prevents the "hang" when there are hundreds of elements by advancing the loop to the browser side
        js_script = """
        () => {
            const elements = document.querySelectorAll('button, a, input[type="submit"], input[type="button"], [role="button"]');
            return Array.from(elements).map((elem, index) => {
                const style = window.getComputedStyle(elem);
                const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && elem.offsetWidth > 0 && elem.offsetHeight > 0;
                
                const text = (elem.innerText || elem.value || '').trim().substring(0, 80);
                const tagName = elem.tagName;
                const isDisabled = elem.disabled || elem.getAttribute('aria-disabled') === 'true';
                const id = elem.id || '';
                const className = elem.className || '';
                
                return {
                    index: index, 
                    isVisible: isVisible,
                    text: text || `Element ${index + 1}`,
                    tag_name: tagName,
                    enabled: !isDisabled,
                    id: id,
                    class: className
                };
            });
        }
        """
        
        all_items = await page.evaluate(js_script)
        
        result = []
        base_query = 'button, a, input[type="submit"], input[type="button"], [role="button"]'
        
        for item in all_items:
            if not item['isVisible']:
                continue
                
            # Construct a robust selector for Playwright
            # If ID is present, use it (fastest/safest)
            if item['id']:
                selector = f"#{item['id']}"
            else:
                # Use the nth-match locator syntax which is reliable for lists
                # Note: creating a locator like this for storage string:
                selector = f"css={base_query} >> nth={item['index']}"
            
            result.append({
                'index': item['index'],
                'text': item['text'],
                'selector': selector,
                'enabled': item['enabled'],
                'visible': True,
                'type': item['tag_name'],
                'id': item['id'],
                'class': item['class']
            })

        return True, result

    except Exception as e:
        return False, f"Scan failed: {str(e)}"
    finally:
        # Only close if we created a temporary browser
        if temp_context:
            await temp_context.close()
        if temp_browser:
            await temp_browser.close()
        if temp_playwright:
            await temp_playwright.stop()

def scan_clickable_elements(url, storage_state=None):
    """Scan page for all clickable elements"""
    try:
        return run_async(_scan_clickable_elements_async(url, storage_state))
    except Exception as e:
        return False, f"Scan failed: {str(e)}"

async def _click_element_when_ready_async(url, selector, wait_enabled=True, timeout=30, storage_state=None):
    """Click an element on a page, optionally waiting for it to be enabled (async) - reuses persistent browser if available"""
    # Check if we have a persistent browser session
    use_persistent = st.session_state.browser_active and st.session_state.browser_page is not None

    if use_persistent:
        # Reuse existing browser page
        page = st.session_state.browser_page
        temp_playwright = None
        temp_browser = None
        temp_context = None
        print(f"[DEBUG] Using persistent browser session for clicking: {url}")
    else:
        # Create temporary browser for this operation
        print(f"[DEBUG] Creating temporary browser for clicking: {url}")
        temp_playwright = await async_playwright().start()
        temp_browser = await temp_playwright.chromium.launch(headless=False)

        if storage_state:
            temp_context = await temp_browser.new_context(storage_state=storage_state)
        else:
            temp_context = await temp_browser.new_context()

        page = await temp_context.new_page()

    try:
        # Navigate to the URL
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        if wait_enabled:
            # Wait for element to be enabled (poll)
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        is_visible = await elem.is_visible()
                        is_disabled = await elem.is_disabled()
                        if is_visible and not is_disabled:
                            # Element is ready, click it
                            await elem.click()
                            return True, "Element clicked successfully"
                    await asyncio.sleep(0.5)
                except:
                    await asyncio.sleep(0.5)

            return False, f"Element not ready after {timeout} seconds"
        else:
            # Click immediately
            elem = await page.query_selector(selector)
            if elem:
                await elem.click()
                return True, "Element clicked successfully"
            else:
                return False, "Element not found"

    except Exception as e:
        return False, f"Click failed: {str(e)}"
    finally:
        # Only close if we created a temporary browser
        if temp_context:
            await temp_context.close()
        if temp_browser:
            await temp_browser.close()
        if temp_playwright:
            await temp_playwright.stop()

def click_element_when_ready(url, selector, wait_enabled=True, timeout=30, storage_state=None):
    """Click an element on a page, optionally waiting for it to be enabled"""
    try:
        return run_async(_click_element_when_ready_async(url, selector, wait_enabled, timeout, storage_state))
    except Exception as e:
        return False, f"Click failed: {str(e)}"

async def _navigate_with_persistent_browser_async(url, storage_state=None):
    """Navigate to URL using persistent browser if available (async) - no clicking"""
    # Check if we have a persistent browser session
    use_persistent = st.session_state.browser_active and st.session_state.browser_page is not None

    if use_persistent:
        # Reuse existing browser page
        page = st.session_state.browser_page
        temp_playwright = None
        temp_browser = None
        temp_context = None
        print(f"[DEBUG] Using persistent browser session for navigation: {url}")
    else:
        # Create temporary browser for this operation
        print(f"[DEBUG] Creating temporary browser for navigation: {url}")
        temp_playwright = await async_playwright().start()
        temp_browser = await temp_playwright.chromium.launch(headless=True)

        if storage_state:
            temp_context = await temp_browser.new_context(storage_state=storage_state)
        else:
            temp_context = await temp_browser.new_context()

        page = await temp_context.new_page()

    try:
        # Navigate to the URL
        await page.goto(url, wait_until="networkidle", timeout=30000)
        return True, "Navigation successful"
    except Exception as e:
        return False, f"Navigation failed: {str(e)}"
    finally:
        # Only close if we created a temporary browser
        if temp_context:
            await temp_context.close()
        if temp_browser:
            await temp_browser.close()
        if temp_playwright:
            await temp_playwright.stop()

def navigate_with_persistent_browser(url, storage_state=None):
    """Navigate to URL using persistent browser if available"""
    try:
        return run_async(_navigate_with_persistent_browser_async(url, storage_state))
    except Exception as e:
        return False, f"Navigation failed: {str(e)}"

async def _capture_screenshot_async(url=None, storage_state=None):
    """Capture a screenshot of a page (async) - reuses persistent browser if available"""
    # Check if we have a persistent browser session
    use_persistent = st.session_state.browser_active and st.session_state.browser_page is not None

    if use_persistent:
        # Reuse existing browser page
        page = st.session_state.browser_page
        temp_playwright = None
        temp_browser = None
        temp_context = None
        print(f"[DEBUG] Using persistent browser session for screenshot: {url}")
    else:
        # Create temporary browser for this operation
        print(f"[DEBUG] Creating temporary browser for screenshot: {url}")
        temp_playwright = await async_playwright().start()
        temp_browser = await temp_playwright.chromium.launch(headless=False)

        if storage_state:
            temp_context = await temp_browser.new_context(storage_state=storage_state)
        else:
            temp_context = await temp_browser.new_context()

        page = await temp_context.new_page()

    try:
        if url:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        screenshot_bytes = await page.screenshot(full_page=True)
        return True, screenshot_bytes
    except Exception as e:
        return False, f"Screenshot failed: {str(e)}"
    finally:
        # Only close if we created a temporary browser
        if temp_context:
            await temp_context.close()
        if temp_browser:
            await temp_browser.close()
        if temp_playwright:
            await temp_playwright.stop()

def capture_screenshot(url=None, storage_state=None):
    """Capture a screenshot of a page"""
    try:
        return run_async(_capture_screenshot_async(url, storage_state))
    except Exception as e:
        return False, f"Screenshot failed: {str(e)}"

async def _cleanup_browser_async():
    """Cleanup browser instances (async)"""
    try:
        if st.session_state.browser_page:
            await st.session_state.browser_page.close()
        if st.session_state.browser_context:
            await st.session_state.browser_context.close()
        if st.session_state.browser:
            await st.session_state.browser.close()
        if st.session_state.playwright_instance:
            await st.session_state.playwright_instance.stop()
    except Exception as e:
        pass  # Silently fail cleanup
    finally:
        # Reset state
        st.session_state.browser_page = None
        st.session_state.browser_context = None
        st.session_state.browser = None
        st.session_state.playwright_instance = None
        st.session_state.browser_active = False

        # Close event loop (if it exists and not the current one being used)
        if st.session_state.event_loop and not st.session_state.event_loop.is_running():
            try:
                st.session_state.event_loop.close()
            except Exception:
                pass
        st.session_state.event_loop = None

def cleanup_browser():
    """Cleanup browser instances"""
    try:
        run_async(_cleanup_browser_async())
    except Exception as e:
        # Force reset even if cleanup fails
        st.session_state.browser_page = None
        st.session_state.browser_context = None
        st.session_state.browser = None
        st.session_state.playwright_instance = None
        st.session_state.browser_active = False

        # Close event loop
        if st.session_state.event_loop and not st.session_state.event_loop.is_running():
            try:
                st.session_state.event_loop.close()
            except Exception:
                pass
        st.session_state.event_loop = None

async def _capture_login_session_async(login_url, timeout=180):
    """Open browser for manual login and keep it open (async) - NO COOKIE STORAGE!"""
    try:
        # Clean up any existing browser first
        await _cleanup_browser_async()

        # Use visible browser on local, headless on cloud
        headless = is_streamlit_cloud()

        if headless:
            # Cloud: headless mode - manual login not supported
            return False, "Manual login not supported in headless mode (Streamlit Cloud). Please use local development or configure automated login."

        # Create new playwright instance (DO NOT use context manager - we want to keep it alive!)
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False)  # Always visible for login
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(login_url, wait_until="networkidle", timeout=30000)

        # Local: visible browser - wait for user to manually login
        initial_url = page.url
        start_time = time.time()

        # Poll for URL change (indicates navigation after login)
        while time.time() - start_time < timeout:
            await asyncio.sleep(2)
            try:
                current_url = page.url
                # If URL changed from login page, assume login successful
                if current_url != initial_url and 'login' not in current_url.lower():
                    break
            except Exception:
                # Page might be closed by user
                return False, "Browser was closed before login completed"

        # Store instances in session state (DO NOT CLOSE!)
        st.session_state.playwright_instance = p
        st.session_state.browser = browser
        st.session_state.browser_context = context
        st.session_state.browser_page = page
        st.session_state.browser_active = True

        return True, "Browser session active - no cookies stored!"

    except Exception as e:
        # Clean up on error
        await _cleanup_browser_async()
        return False, f"Login capture failed: {str(e)}"

def capture_login_session(login_url, timeout=180):
    """Open browser for manual login and capture session"""
    try:
        # Create a new persistent event loop for the browser session
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state.event_loop = loop

        # Run the async function in the persistent loop
        result = loop.run_until_complete(_capture_login_session_async(login_url, timeout))

        # Don't close the loop - keep it alive for the browser session!
        return result
    except Exception as e:
        # Clean up on error
        if st.session_state.event_loop:
            try:
                st.session_state.event_loop.close()
            except:
                pass
            st.session_state.event_loop = None
        return False, f"Login capture failed: {str(e)}"

st.set_page_config(page_title="Web Auto-Clicker", layout="wide", page_icon="🎯")
st.title("🎯 Web Auto-Clicker")

# Initialize session state
if 'last_opened' not in st.session_state:
    st.session_state.last_opened = None
if 'open_count' not in st.session_state:
    st.session_state.open_count = 0
# Browser automation state
if 'detected_elements' not in st.session_state:
    st.session_state.detected_elements = []
if 'selected_element' not in st.session_state:
    st.session_state.selected_element = None
if 'selected_element_selector' not in st.session_state:
    st.session_state.selected_element_selector = None
if 'playwright_available' not in st.session_state:
    st.session_state.playwright_available = check_playwright_available()
if 'automation_status' not in st.session_state:
    st.session_state.automation_status = "Not started"
if 'last_screenshot' not in st.session_state:
    st.session_state.last_screenshot = None
# Browser instance state (for persistent session - no cookie storage!)
if 'playwright_instance' not in st.session_state:
    st.session_state.playwright_instance = None
if 'browser' not in st.session_state:
    st.session_state.browser = None
if 'browser_context' not in st.session_state:
    st.session_state.browser_context = None
if 'browser_page' not in st.session_state:
    st.session_state.browser_page = None
if 'browser_active' not in st.session_state:
    st.session_state.browser_active = False
if 'event_loop' not in st.session_state:
    st.session_state.event_loop = None

# Progress indicators for 3-step workflow
step1_complete = st.session_state.browser_active
step2_complete = st.session_state.selected_element is not None

st.markdown("**Follow the 3 steps below to automate clicking on a web element.**")

st.markdown("---")

# ============================================================================
# STEP 1: Login to Website
# ============================================================================
step1_icon = "✅" if step1_complete else "1️⃣"
st.header(f"{step1_icon} Step 1: Login to Website")

# Login URL input
login_url = st.text_input(
    "Login URL",
    value="https://members.brsgolf.com/gsaayr/login",
    help="Enter the full URL of the website login page",
    key="login_url_input"
)

if st.session_state.browser_active:
    st.success("✅ **Browser session active!** You can proceed to Step 2.")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🛑 Close Browser", use_container_width=True):
            cleanup_browser()
            st.rerun()
    with col2:
        st.caption("Close browser to end session and start fresh")
else:
    if not st.session_state.playwright_available:
        st.error("❌ Playwright not installed. Run `pip install playwright && playwright install chromium`")
    elif is_streamlit_cloud():
        st.warning("⚠️ Manual login requires a visible browser, which isn't available on Streamlit Cloud. Run locally.")
    else:
        if st.button("🔐 Open Browser & Login", use_container_width=True, type="primary"):
            if login_url:
                with st.spinner("Opening browser... Please log in manually."):
                    success, result = capture_login_session(login_url, timeout=180)
                    if success:
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
            else:
                st.error("Please enter a login URL first")
        
        st.caption("A Chrome browser will open. Log in normally, then return here.")

st.markdown("---")

# ============================================================================
# STEP 2: Scan Page & Select Element
# ============================================================================
step2_icon = "✅" if step2_complete else "2️⃣"
st.header(f"{step2_icon} Step 2: Scan Page & Select Element")

# Gate check: Step 1 must be complete
if not st.session_state.browser_active:
    st.warning("⚠️ **Step 1 Incomplete:** Please login and keep the browser open first.")
else:
    # URL input
    col1, col2 = st.columns([3, 1])
    with col1:
        user_url = st.text_input(
            "Target Page URL",
            value="https://members.brsgolf.com/gsaayr/tee-sheet/1/2025/12/23",
            help="Enter the full URL of the target page you want to scan",
            key="target_url_input"
        )
    with col2:
        st.markdown("&nbsp;")
        if st.button("🔍 Scan Page", use_container_width=True, type="primary"):
            if user_url:
                with st.spinner("Scanning page..."):
                    success, result = scan_clickable_elements(user_url)
                    if success:
                        st.session_state.detected_elements = result
                        st.success(f"✅ Found {len(result)} elements!")
                    else:
                        st.error(f"❌ {result}")
            else:
                st.error("Enter URL first")

    # Element selection UI
    if st.session_state.detected_elements:
        st.markdown("### 🎯 Select Element")
        
        # Create options map
        element_options = {}
        for elem in st.session_state.detected_elements:
            status_icon = "✅" if elem['enabled'] else "⏸️"
            label = f"{status_icon} [{elem['type']}] {elem['text'][:60]}"
            element_options[label] = elem

        # Maintain selection
        selected_index = 0
        if st.session_state.selected_element_selector:
            keys = list(element_options.keys())
            for i, label in enumerate(keys):
                if element_options[label]['selector'] == st.session_state.selected_element_selector:
                    selected_index = i
                    break

        selected_label = st.selectbox(
            "Select element to click",
            options=list(element_options.keys()),
            index=selected_index,
            key="element_selector"
        )

        if selected_label:
            st.session_state.selected_element = element_options[selected_label]
            st.session_state.selected_element_selector = element_options[selected_label]['selector']
            
            elem = st.session_state.selected_element
            
            # Show details and test button
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**Selector:** `{elem['selector']}` | **Status:** {'Enabled' if elem['enabled'] else 'Disabled'}")
            with col2:
                if st.button("🧪 Test Click", use_container_width=True):
                    with st.spinner("Testing click..."):
                        success, msg = click_element_when_ready(
                            user_url, 
                            elem['selector'], 
                            wait_enabled=False, 
                            timeout=5
                        )
                        if success:
                            st.success("✅ Clicked!")
                        else:
                            st.error(f"❌ {msg}")
    
    elif user_url and st.session_state.browser_active:
        st.info("👆 Click 'Scan Page' to find buttons and links.")

# Auto-refresh helper
st.markdown("---")
# ============================================================================
# STEP 3: Auto-refresh and Click
# ============================================================================
st.markdown("---")
st.header("3️⃣ Step 3: Auto-refresh and Click")

# Gate check: Step 2 must be complete (element selected)
if not st.session_state.selected_element:
    st.warning("⚠️ **Step 2 Incomplete:** Please scan page and select an element first.")
else:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        refresh_interval = st.number_input("Interval (seconds)", 10, 3600, 30, 5)
    with col2:
        wait_timeout = st.number_input("Wait Timeout (seconds)", 5, 120, 30, 5)
    with col3:
        st.markdown("&nbsp;")
        auto_refresh_enabled = st.checkbox("✅ Enable Auto-Clicker", value=False)

    if auto_refresh_enabled:
        elem_text = st.session_state.selected_element['text'][:40]
        st.success(f"🤖 **Running!** Will check every {refresh_interval}s")
        st.info(f"Target: **{elem_text}** (timeout: {wait_timeout}s)")
        
        # Initialize timer
        if 'next_refresh_time' not in st.session_state:
            st.session_state.next_refresh_time = time.time() + refresh_interval

        current_time = time.time()
        
        # Check if time to refresh
        if current_time >= st.session_state.next_refresh_time:
            with st.spinner(f"⚡ Auto-clicking target element..."):
                # Navigate and click
                hit, msg = click_element_when_ready(
                    user_url,
                    st.session_state.selected_element['selector'],
                    wait_enabled=True,
                    timeout=wait_timeout
                )
                
                if hit:
                    st.session_state.open_count += 1
                    st.toast(f"✅ Clicked! ({st.session_state.open_count})", icon="🎉")
                    st.balloons()
                    # Screenshot validation
                    _, ss = capture_screenshot(user_url)
                    if ss: st.image(ss, caption=f"Clicked at {time.strftime('%H:%M:%S')}")
                else:
                    st.toast(f"❌ Missed: {msg}", icon="⚠️")
                    
            # Reset timer
            st.session_state.next_refresh_time = time.time() + refresh_interval
            st.rerun()
            
        else:
            # Countdown
            remaining = int(st.session_state.next_refresh_time - current_time)
            st.metric("Next check in", f"{remaining}s")
            time.sleep(1)
            st.rerun()

    else:
        # Clear timer when disabled
        if 'next_refresh_time' in st.session_state:
            del st.session_state.next_refresh_time

# ============================================================================
# Status & Footer
# ============================================================================
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"📊 Stats: {st.session_state.open_count} actions performed")
with col2:
    st.caption("🛠️ Powered by Playwright")
