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
    """Scan page for all clickable elements (async)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Create context with storage state if provided
        if storage_state:
            context = await browser.new_context(storage_state=storage_state)
        else:
            context = await browser.new_context()

        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Find all clickable elements
            elements = await page.query_selector_all('button, a, input[type="submit"], input[type="button"], [role="button"]')

            result = []
            for i, elem in enumerate(elements):
                # Check if element is visible
                is_visible = await elem.is_visible()
                if not is_visible:
                    continue

                # Get element properties
                text_content = await elem.text_content()
                value = await elem.get_attribute('value')
                elem_id = await elem.get_attribute('id')
                elem_class = await elem.get_attribute('class')
                tag_name = await elem.evaluate('el => el.tagName')
                is_disabled = await elem.is_disabled()

                # Get text
                text = (text_content or value or '').strip()[:80] or f"Element {i+1}"

                # Generate selector (prefer ID, then class, then nth-of-type)
                if elem_id:
                    selector = f"#{elem_id}"
                elif elem_class and elem_class.strip():
                    first_class = elem_class.strip().split()[0]
                    selector = f".{first_class}"
                else:
                    selector = f"{tag_name.lower()}:nth-of-type({i+1})"

                result.append({
                    'index': i,
                    'text': text,
                    'selector': selector,
                    'enabled': not is_disabled,
                    'visible': True,
                    'type': tag_name,
                    'id': elem_id or '',
                    'class': elem_class or ''
                })

            return True, result

        except Exception as e:
            return False, f"Scan failed: {str(e)}"
        finally:
            await context.close()
            await browser.close()

def scan_clickable_elements(url, storage_state=None):
    """Scan page for all clickable elements"""
    try:
        return run_async(_scan_clickable_elements_async(url, storage_state))
    except Exception as e:
        return False, f"Scan failed: {str(e)}"

async def _click_element_when_ready_async(url, selector, wait_enabled=True, timeout=30, storage_state=None):
    """Click an element on a page, optionally waiting for it to be enabled (async)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Create context with storage state if provided
        if storage_state:
            context = await browser.new_context(storage_state=storage_state)
        else:
            context = await browser.new_context()

        page = await context.new_page()
        try:
            # Navigate to the URL
            await page.goto(url, wait_until="networkidle", timeout=30000)

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
            await context.close()
            await browser.close()

def click_element_when_ready(url, selector, wait_enabled=True, timeout=30, storage_state=None):
    """Click an element on a page, optionally waiting for it to be enabled"""
    try:
        return run_async(_click_element_when_ready_async(url, selector, wait_enabled, timeout, storage_state))
    except Exception as e:
        return False, f"Click failed: {str(e)}"

async def _capture_screenshot_async(url=None, storage_state=None):
    """Capture a screenshot of a page (async)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Create context with storage state if provided
        if storage_state:
            context = await browser.new_context(storage_state=storage_state)
        else:
            context = await browser.new_context()

        page = await context.new_page()
        try:
            if url:
                await page.goto(url, wait_until="networkidle", timeout=30000)

            screenshot_bytes = await page.screenshot(full_page=True)
            return True, screenshot_bytes
        except Exception as e:
            return False, f"Screenshot failed: {str(e)}"
        finally:
            await context.close()
            await browser.close()

def capture_screenshot(url=None, storage_state=None):
    """Capture a screenshot of a page"""
    try:
        return run_async(_capture_screenshot_async(url, storage_state))
    except Exception as e:
        return False, f"Screenshot failed: {str(e)}"

async def _capture_login_session_async(login_url, timeout=180):
    """Open browser for manual login and capture session (async)"""
    async with async_playwright() as p:
        # Use visible browser on local, headless on cloud
        headless = is_streamlit_cloud()
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await browser.new_page()

        try:
            await page.goto(login_url, wait_until="networkidle", timeout=30000)

            if not headless:
                # Local: visible browser - wait for user to manually login
                # Wait for timeout period (user should login and close tab manually or we timeout)
                initial_url = page.url
                start_time = time.time()

                # Poll for URL change (indicates navigation after login)
                while time.time() - start_time < timeout:
                    await asyncio.sleep(2)
                    current_url = page.url
                    # If URL changed from login page, assume login successful
                    if current_url != initial_url and 'login' not in current_url.lower():
                        break

            else:
                # Cloud: headless mode - wait fixed time
                # User won't see browser, so we can't do manual login in cloud
                # This is a fallback - cloud should use alternative method
                return False, "Manual login not supported in headless mode (Streamlit Cloud). Please use local development or configure automated login."

            # Capture storage state (cookies, localStorage, sessionStorage)
            storage_state = await context.storage_state()

            return True, storage_state

        except Exception as e:
            return False, f"Login capture failed: {str(e)}"
        finally:
            await context.close()
            await browser.close()

def capture_login_session(login_url, timeout=180):
    """Open browser for manual login and capture session"""
    try:
        return run_async(_capture_login_session_async(login_url, timeout))
    except Exception as e:
        return False, f"Login capture failed: {str(e)}"

st.set_page_config(page_title="Web Page Launcher", layout="wide", page_icon="🔗")
st.title("🔗 Web Page Launcher")

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
if 'playwright_available' not in st.session_state:
    st.session_state.playwright_available = check_playwright_available()
if 'automation_status' not in st.session_state:
    st.session_state.automation_status = "Not started"
if 'last_screenshot' not in st.session_state:
    st.session_state.last_screenshot = None
# Authentication session state
if 'auth_storage_state' not in st.session_state:
    st.session_state.auth_storage_state = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.markdown("""
This app provides automated web page access with element detection and clicking.
Navigate to pages, detect clickable elements, and automate interactions!
""")

st.markdown("---")

# ============================================================================
# STEP 1: Login Section
# ============================================================================
st.header("📝 Step 1: Login to Website")

# Login URL input
st.markdown("### Login URL")
login_url = st.text_input(
    "Enter website login URL",
    value="https://members.brsgolf.com/gsaayr/login",
    label_visibility="collapsed",
    help="Enter the full URL of the website login page (example shows BRS Golf)",
    key="login_url_input"
)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Quick Login")

    # if st.button("🌐 Open Login Page", use_container_width=True, type="primary", key="open_login"):
    #     webbrowser.open(login_url, new=2)  # new=2 opens in new tab
    #     st.session_state.last_opened = "Login Page"
    #     st.session_state.open_count += 1
    #     st.success("✅ Login page opened in browser!")
    #     st.balloons()
    if st.button("🌐 Open Login Page", use_container_width=True, type="primary", key="open_login"):
        if login_url:
            st.session_state.last_opened = "Login Page"
            st.session_state.open_count += 1
            st.markdown(f'<a href="{login_url}" target="_blank">Click here to open login page</a>', unsafe_allow_html=True)
            st.success("✅ Login link ready - click above to open in browser!")
            st.balloons()
        else:
            st.error("Please enter a login URL first")

    st.caption(f"🔗 URL: `{login_url}`")

    if st.button("📋 Copy Login URL", use_container_width=True):
        if login_url:
            st.code(login_url, language=None)
            st.info("👆 URL displayed above - copy it manually")
        else:
            st.error("No URL to copy")

with col2:
    st.info("""
    **Instructions:**
    1. Click **"🌐 Open Login Page"** button
    2. The website will open in your default browser (Chrome, Edge, Firefox, etc.)
    3. Log in normally with your username and password
    4. Browser will remember your session
    5. Return here for Step 2

    **Benefits:**
    - ✅ Full browser features (autofill, password manager)
    - ✅ No iframe restrictions or blank pages
    - ✅ Your login persists across browser sessions
    """)

# Login Session Capture for Automation
st.markdown("### 🔑 Capture Login Session (For Automation)")

if st.session_state.logged_in:
    st.success(f"✅ Login session active! Automation will use your saved session.")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear Saved Session", use_container_width=True):
            st.session_state.auth_storage_state = None
            st.session_state.logged_in = False
            st.success("Session cleared! Please login again for automation.")
            st.rerun()
    with col2:
        st.caption("💡 Session persists until page reload or manual clear")
else:
    st.warning("⚠️ No active session. Automation may redirect to login page.")

    if not st.session_state.playwright_available:
        st.error("❌ Playwright not available. Cannot capture login session.")
    elif is_streamlit_cloud():
        st.info("""
        🌐 **Streamlit Cloud Detected**

        Manual login capture requires a visible browser, which isn't available on Streamlit Cloud.

        **Alternatives:**
        1. Run this app locally to capture session
        2. Use automated login (configure credentials in Streamlit secrets)
        3. The app will attempt automation but may hit login redirects
        """)
    else:
        if st.button("🔐 Capture Login Session", use_container_width=True, type="primary"):
            if login_url:
                with st.spinner("Opening browser for login... Please login and the browser will auto-detect when done (or wait 3 minutes)."):
                    success, result = capture_login_session(login_url, timeout=180)
                    if success:
                        st.session_state.auth_storage_state = result
                        st.session_state.logged_in = True
                        st.success("✅ Login session captured successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
            else:
                st.error("Please enter a login URL first")

        st.caption("""
        💡 **How it works:**
        1. Click the button above
        2. A Chrome browser window will open
        3. Log in to the website normally
        4. Once logged in (URL changes from login page), the session is automatically captured
        5. Your session will be used for all automation operations
        """)

st.markdown("---")

# ============================================================================
# STEP 2: Automated Element Detection & Clicking
# ============================================================================
st.header("🤖 Step 2: Scan Page & Select Element")

# URL input
st.markdown("### Target Page URL")
user_url = st.text_input(
    "Enter target page URL",
    value="https://members.brsgolf.com/gsaayr/tee-sheet/1/2025/11/11",
    label_visibility="collapsed",
    help="Enter the full URL of the target page you want to scan for clickable elements"
)

# Show Playwright status
if not st.session_state.playwright_available:
    st.warning("⚠️ Playwright not available. Automation features are disabled. Falling back to simple URL opening.")

# Scan and Screenshot buttons
st.markdown("### Page Analysis")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔍 Scan Page for Elements", use_container_width=True, type="primary", disabled=not st.session_state.playwright_available):
        if user_url:
            with st.spinner("🔄 Scanning page for clickable elements..."):
                success, result = scan_clickable_elements(user_url, storage_state=st.session_state.auth_storage_state)
                if success:
                    st.session_state.detected_elements = result
                    st.session_state.automation_status = f"Found {len(result)} elements"
                    st.success(f"✅ Found {len(result)} clickable elements!")
                    st.balloons()
                else:
                    st.error(f"❌ {result}")
                    st.session_state.automation_status = f"Scan failed: {result}"
        else:
            st.error("Please enter a URL first")

with col2:
    if st.button("📸 Capture Screenshot", use_container_width=True, disabled=not st.session_state.playwright_available):
        if user_url:
            with st.spinner("📸 Capturing screenshot..."):
                success, result = capture_screenshot(user_url, storage_state=st.session_state.auth_storage_state)
                if success:
                    st.session_state.last_screenshot = result
                    st.success("✅ Screenshot captured!")
                else:
                    st.error(f"❌ {result}")
        else:
            st.error("Please enter a URL first")

# Display screenshot if available
if st.session_state.last_screenshot:
    with st.expander("📸 View Latest Screenshot"):
        st.image(st.session_state.last_screenshot, caption="Page Screenshot", use_container_width=True)

# Element selection UI
if st.session_state.detected_elements:
    st.markdown("---")
    st.markdown("### 🎯 Select Element to Auto-Click")

    # Create a formatted list for selection
    element_options = {}
    for elem in st.session_state.detected_elements:
        status_icon = "✅" if elem['enabled'] else "⏸️"
        label = f"{status_icon} [{elem['type']}] {elem['text'][:60]}"
        element_options[label] = elem

    selected_label = st.selectbox(
        "Choose which element to automatically click during auto-refresh",
        options=["None"] + list(element_options.keys()),
        index=0 if st.session_state.selected_element is None else
              (list(element_options.keys()).index(
                  f"{'✅' if st.session_state.selected_element['enabled'] else '⏸️'} [{st.session_state.selected_element['type']}] {st.session_state.selected_element['text'][:60]}"
              ) + 1 if st.session_state.selected_element in st.session_state.detected_elements else 0)
    )

    if selected_label != "None":
        st.session_state.selected_element = element_options[selected_label]

        # Show selected element details
        elem = st.session_state.selected_element
        st.markdown("#### Selected Element Details")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Type", elem['type'])
        with col2:
            st.metric("Status", "✅ Enabled" if elem['enabled'] else "⏸️ Disabled")
        with col3:
            st.metric("ID", elem['id'] if elem['id'] else "None")
        with col4:
            st.code(elem['selector'], language=None)

        st.caption(f"**Text:** {elem['text']}")
        st.caption(f"**CSS Class:** {elem['class'] if elem['class'] else 'None'}")

        # Test click button
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🧪 Test Click Now", use_container_width=True):
                with st.spinner(f"🖱️ Clicking element: {elem['text'][:40]}..."):
                    success, message = click_element_when_ready(
                        user_url,
                        elem['selector'],
                        wait_enabled=False,
                        timeout=5,
                        storage_state=st.session_state.auth_storage_state
                    )
                    if success:
                        st.success(f"✅ {message}")
                        # Capture screenshot after click
                        success_ss, screenshot = capture_screenshot(user_url, storage_state=st.session_state.auth_storage_state)
                        if success_ss:
                            st.session_state.last_screenshot = screenshot
                            st.image(screenshot, caption="After Click", use_container_width=True)
                    else:
                        st.error(f"❌ {message}")
        with col2:
            st.info("💡 Use this to verify you selected the correct element before enabling auto-refresh")
    else:
        st.session_state.selected_element = None
        st.info("👆 Select an element from the dropdown to enable automation")

# Fallback: Simple URL opening for non-MCP environments
elif not st.session_state.playwright_available and user_url:
    st.markdown("---")
    st.markdown("### Simple Mode (No Automation)")
    if st.button("🌐 Open URL in Browser", use_container_width=True, type="primary"):
        st.markdown(f'<a href="{user_url}" target="_blank">Click here to open page</a>', unsafe_allow_html=True)
        st.success("✅ Link ready - click above to open!")

# Auto-refresh helper
st.markdown("---")
st.markdown("### 🔄 Auto-Refresh Helper")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    auto_refresh_enabled = st.checkbox("Enable auto-refresh automation", value=False)

with col2:
    refresh_interval = st.number_input(
        "Interval (seconds)",
        min_value=10,
        max_value=3600,
        value=30,
        step=5,
        label_visibility="collapsed"
    )

with col3:
    wait_timeout = st.number_input(
        "Wait timeout (s)",
        min_value=5,
        max_value=120,
        value=30,
        step=5,
        label_visibility="collapsed",
        help="How long to wait for element to become enabled before timeout"
    )

if auto_refresh_enabled:
    # Show status based on whether automation is configured
    if st.session_state.selected_element and st.session_state.playwright_available:
        st.success(f"✅ Browser automation enabled! Will auto-click: **{st.session_state.selected_element['text'][:50]}**")
        st.info(f"⚙️ Checking every {refresh_interval}s, waiting up to {wait_timeout}s for element to be enabled")
    elif not st.session_state.playwright_available:
        st.warning("⚠️ Playwright not available. Auto-refresh will use simple URL opening.")
    else:
        st.warning("⚠️ No element selected. Please scan page and select an element first.")

    # Initialize timer
    if 'next_refresh_time' not in st.session_state:
        st.session_state.next_refresh_time = time.time() + refresh_interval

    current_time = time.time()

    # Check if it's time to refresh
    if current_time >= st.session_state.next_refresh_time:
        if user_url:
            # AUTOMATION MODE: Use browser automation if element is selected and Playwright is available
            if st.session_state.selected_element and st.session_state.playwright_available:
                with st.spinner(f"🤖 Automating click on: {st.session_state.selected_element['text'][:40]}..."):
                    # Navigate to page and click element (with wait if enabled)
                    click_success, click_message = click_element_when_ready(
                        user_url,
                        st.session_state.selected_element['selector'],
                        wait_enabled=True,
                        timeout=wait_timeout,
                        storage_state=st.session_state.auth_storage_state
                    )

                    if click_success:
                        st.session_state.automation_status = f"✅ Auto-clicked successfully at {time.strftime('%H:%M:%S')}"
                        st.session_state.open_count += 1
                        st.session_state.last_opened = f"Auto-click #{st.session_state.open_count}"

                        # Capture screenshot after successful click
                        ss_success, screenshot = capture_screenshot(user_url, storage_state=st.session_state.auth_storage_state)
                        if ss_success:
                            st.session_state.last_screenshot = screenshot

                        st.toast(f"🤖 {click_message}", icon="✅")
                        st.success(f"✅ {click_message}")

                        # Show screenshot if captured
                        if ss_success:
                            st.image(screenshot, caption=f"Auto-clicked at {time.strftime('%H:%M:%S')}", use_container_width=True)
                    else:
                        st.session_state.automation_status = f"❌ Click failed: {click_message}"
                        st.error(f"❌ {click_message}")
                        st.warning("💡 Element may not be available yet. Continuing to monitor...")

            # FALLBACK MODE: Simple URL opening for non-automation cases
            else:
                if is_streamlit_cloud():
                    # Streamlit Cloud: Use JavaScript anchor click
                    auto_click_html = f"""
                    <script>
                    (function() {{
                        const link = document.createElement('a');
                        link.href = '{user_url}';
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }})();
                    </script>
                    """
                    components.html(auto_click_html, height=0)
                    st.warning("🚨 **If no tab opened (popup blocked), click here:**")
                    st.markdown(
                        f'<a href="{user_url}" target="_blank" style="display:inline-block;padding:12px 24px;background-color:#ff4b4b;color:white;text-decoration:none;border-radius:5px;font-weight:bold;font-size:18px;">📱 CLICK TO OPEN PAGE</a>',
                        unsafe_allow_html=True
                    )
                else:
                    # Local development: Use native webbrowser.open
                    webbrowser.open(user_url, new=2)
                    st.toast("🔄 Opened new tab", icon="✅")

                st.session_state.last_opened = f"Simple open #{st.session_state.open_count}"
                st.session_state.open_count += 1

            # Update timer for next refresh
            st.session_state.next_refresh_time = time.time() + refresh_interval

    # Show countdown
    time_remaining = int(st.session_state.next_refresh_time - current_time)
    if time_remaining > 0:
        st.info(f"⏳ Next action in: **{time_remaining}** seconds | Status: {st.session_state.automation_status}")
        time.sleep(1)
        st.rerun()
    else:
        st.rerun()

else:
    # Reset timer when disabled
    if 'next_refresh_time' in st.session_state:
        del st.session_state.next_refresh_time

# ============================================================================
# Session Statistics
# ============================================================================
st.markdown("---")
st.subheader("📊 Session Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Actions", st.session_state.open_count)

with col2:
    if st.session_state.last_opened:
        st.metric("Last Action", st.session_state.last_opened)
    else:
        st.metric("Last Action", "None yet")

with col3:
    automation_status = "🤖 Enabled" if st.session_state.selected_element else "📱 Manual"
    st.metric("Mode", automation_status)

with col4:
    login_status = "✅ Logged In" if st.session_state.logged_in else "🔓 Not Logged In"
    st.metric("Auth Status", login_status)

with col5:
    playwright_status = "✅ Available" if st.session_state.playwright_available else "⚠️ Unavailable"
    st.metric("Playwright", playwright_status)

# ============================================================================
# User Guidance
# ============================================================================
st.markdown("---")
st.info("""
### 📖 How to Use This App

**Automated Workflow (Recommended):**
1. **Step 1:** Click **"🌐 Open Login Page"** → Log in to the website in your browser
2. **Step 2:** Enter the target page URL
3. Click **"🔍 Scan Page for Elements"** → App detects all clickable buttons/links
4. Select which element to auto-click from the dropdown
5. Click **"🧪 Test Click Now"** to verify you selected the right element
6. Enable **"Auto-refresh automation"** to start monitoring
7. The app will automatically navigate to the page, wait for the element to be enabled, and click it!

**Auto-Refresh Automation:**
- **Interval**: How often to check the page (10-3600 seconds)
- **Wait Timeout**: How long to wait for element to become enabled (5-120 seconds)
- Perfect for booking systems, ticket sales, or any button that becomes available at specific times
- Captures screenshot after each successful click for verification

**Button Reference:**
- **🔍 Scan Page for Elements** - Detects all clickable elements on the page
- **📸 Capture Screenshot** - Takes a screenshot of the current page
- **🧪 Test Click Now** - Manually test clicking the selected element
- **Enable auto-refresh automation** - Starts automated monitoring and clicking

**How It Works:**
- ✅ **Browser Automation** - Uses Playwright to control a headless Chromium browser
- ✅ **Smart Waiting** - Monitors element state and clicks when it becomes enabled
- ✅ **Visual Feedback** - Shows screenshots after each automated action
- ✅ **Fallback Mode** - If Playwright unavailable, falls back to simple URL opening
- ✅ **Session Persistence** - Browser maintains login state between checks

**Use Cases:**
- 🎟️ Auto-click "Book Now" when reservations open
- ⛳ Auto-submit tee time requests when slots become available
- 🎫 Auto-purchase tickets when they go on sale
- 📅 Auto-register for events when registration opens
- 🛒 Auto-add items to cart when they're back in stock

**Fallback Mode:**
- If Playwright is not available, the app will warn you and use simple URL opening
- You can still use auto-refresh, but it will just open the URL without clicking elements
""")

# Footer
st.markdown("---")
st.caption("🛠️ Web Page Launcher | Powered by Playwright | Browser Automation Made Easy!")
