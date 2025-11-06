import streamlit as st
import streamlit.components.v1 as components
import webbrowser
import time
import os
import platform

# Environment detection
def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud vs local development"""
    # Streamlit Cloud runs on Linux with empty processor string
    # Also check for 'appuser' which is the default Streamlit Cloud user
    return platform.processor() == '' or os.getenv('USER') == 'appuser'

st.set_page_config(page_title="Web Page Launcher", layout="wide", page_icon="🔗")
st.title("🔗 Web Page Launcher")

# Initialize session state
if 'last_opened' not in st.session_state:
    st.session_state.last_opened = None
if 'open_count' not in st.session_state:
    st.session_state.open_count = 0

st.markdown("""
This app provides quick access to web pages in your default browser.
No iframe restrictions - just pure browser functionality!
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

st.markdown("---")

# ============================================================================
# STEP 2: Target Page Access
# ============================================================================
st.header("🔗 Step 2: Access Target Page")

# URL input with common presets
st.markdown("### Target Page URL")

col1, col2 = st.columns([3, 1])

with col1:
    user_url = st.text_input(
        "Enter target page URL",
        value="https://members.brsgolf.com/gsaayr/tee-sheet/1/2025/11/11",
        label_visibility="collapsed",
        help="Enter the full URL of the target page you want to access (example shows BRS Golf tee sheet)"
    )

with col2:
    # Note: These presets are examples (originally for date-based pages like tee sheets)
    # Users can customize these for their specific use case
    url_preset = st.selectbox(
        "Quick Presets",
        ["Custom", "Today", "Tomorrow", "This Week"],
        label_visibility="collapsed"
    )

# Quick preset URL generator (basic example - adjust dates as needed)
if url_preset != "Custom":
    st.info(f"💡 Selected preset: **{url_preset}** - These are example presets. Modify the URL above to match your needs.")

# Action buttons
st.markdown("### Actions")

col1, col2, col3, col4 = st.columns(4)

# with col1:
#     if st.button("🌐 Open Tee Sheet", use_container_width=True, type="primary"):
#         if user_url:
#             webbrowser.open(user_url, new=2)
#             st.session_state.last_opened = "Tee Sheet"
#             st.session_state.open_count += 1
#             st.success("✅ Tee sheet opened!")
#         else:
#             st.error("Please enter a URL first")
with col1:
    if st.button("🌐 Open Target Page", use_container_width=True, type="primary"):
        if user_url:
            st.session_state.last_opened = "Target Page"
            st.session_state.open_count += 1
            st.markdown(f'<a href="{user_url}" target="_blank">Click here to open target page in new tab</a>', unsafe_allow_html=True)
            st.success("✅ Target page link ready - click above to open!")
        else:
            st.error("Please enter a URL first")

# with col2:
#     if st.button("🔄 Refresh (New Tab)", use_container_width=True):
#         if user_url:
#             webbrowser.open(user_url, new=2)
#             st.session_state.last_opened = f"Refresh #{st.session_state.open_count}"
#             st.session_state.open_count += 1
#             st.success("🔄 Opened fresh tab!")
#         else:
#             st.error("Please enter a URL first")
with col2:
    if st.button("🔄 Refresh (New Tab)", use_container_width=True):
        if user_url:
            st.session_state.last_opened = f"Refresh #{st.session_state.open_count}"
            st.session_state.open_count += 1
            st.markdown(f'<a href="{user_url}" target="_blank">Click here to refresh target page (opens new tab)</a>', unsafe_allow_html=True)
            st.success("🔄 Refresh link ready - click above to open!")
        else:
            st.error("Please enter a URL first")

# with col3:
#     if st.button("🪟 Open in New Window", use_container_width=True):
#         if user_url:
#             webbrowser.open(user_url, new=1)  # new=1 opens in new window
#             st.session_state.last_opened = "New Window"
#             st.session_state.open_count += 1
#             st.success("🪟 Opened in new window!")
#         else:
#             st.error("Please enter a URL first")
with col3:
    if st.button("🪟 Open in New Window", use_container_width=True):
        if user_url:
            st.session_state.last_opened = "New Window"
            st.session_state.open_count += 1
            st.markdown(f'<a href="{user_url}" target="_blank">Click here to open in new window/tab</a>', unsafe_allow_html=True)
            st.success("🪟 Link ready - click above to open in new window/tab!")
        else:
            st.error("Please enter a URL first")

with col4:
    if st.button("📋 Copy URL", use_container_width=True):
        if user_url:
            st.code(user_url, language=None)
            st.info("👆 Copy the URL above")
        else:
            st.error("No URL to copy")

# Auto-refresh helper
st.markdown("---")
st.markdown("### 🔄 Auto-Refresh Helper")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    auto_refresh_enabled = st.checkbox("Enable auto-refresh helper", value=False)

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
    st.caption("⏱️ Timer")

if auto_refresh_enabled:
    st.success(f"✅ Auto-refresh enabled! Opening new tab every {refresh_interval} seconds.")

    # Initialize timer
    if 'next_refresh_time' not in st.session_state:
        st.session_state.next_refresh_time = time.time() + refresh_interval

    current_time = time.time()

    # Check if it's time to refresh
    if current_time >= st.session_state.next_refresh_time:
        if user_url:
            # Detect environment and use appropriate method
            if is_streamlit_cloud():
                # Streamlit Cloud: Use JavaScript programmatic anchor click
                # This has better popup blocker bypass than window.open()
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

                # Render the auto-click component
                components.html(auto_click_html, height=0)

                # Show fallback link only on cloud (where popup blocking is likely)
                st.warning("🚨 **If no tab opened (popup blocked), click here:**")
                st.markdown(
                    f'<a href="{user_url}" target="_blank" style="display:inline-block;padding:12px 24px;background-color:#ff4b4b;color:white;text-decoration:none;border-radius:5px;font-weight:bold;font-size:18px;">📱 CLICK TO OPEN TARGET PAGE</a>',
                    unsafe_allow_html=True
                )
            else:
                # Local development: Use native webbrowser.open (works perfectly)
                webbrowser.open(user_url, new=2)

            # Update session state (same for both environments)
            st.session_state.last_opened = f"Auto-refresh #{st.session_state.open_count}"
            st.session_state.open_count += 1
            st.session_state.next_refresh_time = time.time() + refresh_interval

            # Show success message
            st.toast("🔄 Auto-refreshed! New tab opened.", icon="✅")

    # Show countdown
    time_remaining = int(st.session_state.next_refresh_time - current_time)
    if time_remaining > 0:
        st.info(f"⏳ Next refresh in: **{time_remaining}** seconds")
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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Opens", st.session_state.open_count)

with col2:
    if st.session_state.last_opened:
        st.metric("Last Opened", st.session_state.last_opened)
    else:
        st.metric("Last Opened", "None yet")

with col3:
    browser_status = "🟢 Ready" if user_url else "🔴 No URL"
    st.metric("Status", browser_status)

# ============================================================================
# User Guidance
# ============================================================================
st.markdown("---")
st.info("""
### 📖 How to Use This App

**Basic Workflow:**
1. Click **"🌐 Open Login Page"** → Website login opens in your browser
2. Log in with your credentials (browser remembers your session)
3. Return to this app
4. Enter or modify the target page URL
5. Click **"🌐 Open Target Page"** → Opens in new browser tab
6. Use **"🔄 Refresh"** anytime to open a fresh tab

**Auto-Refresh Feature:**
- Enable **"Auto-refresh helper"** to automatically open new tabs at intervals
- Perfect for monitoring page updates or availability
- Each refresh opens a new tab (close old ones as needed)
- Adjust interval to balance between freshness and tab clutter

**Button Reference:**
- **🌐 Open Target Page** - Opens URL in new browser tab
- **🔄 Refresh (New Tab)** - Opens fresh copy in new tab
- **🪟 Open in New Window** - Opens in separate browser window
- **📋 Copy URL** - Display URL for manual copying

**Why This Approach:**
- ✅ **No iframe restrictions** - Real browser, full functionality
- ✅ **Persistent login** - Browser remembers your session
- ✅ **Full browser features** - Extensions, autofill, password manager
- ✅ **No technical issues** - Simple Python webbrowser module
- ✅ **Works everywhere** - Windows, Mac, Linux
- ✅ **Any browser** - Uses your default (Chrome, Edge, Firefox, Safari)

**Tips:**
- Bookmark frequently used target page URLs
- Use browser's "Duplicate Tab" (Ctrl+Shift+K in Chrome) for manual refresh
- Set auto-refresh interval based on how often the page updates
- Close old tabs periodically to avoid clutter
""")

# Footer
st.markdown("---")
st.caption("🛠️ Web Page Launcher | Streamlit App | No iframe restrictions!")
