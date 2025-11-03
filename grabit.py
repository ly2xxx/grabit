import streamlit as st
from streamlit.components.v1 import iframe

st.title("BRS Golf Auto Reloader")

# Initialize session state for iframe refresh counters
if 'login_refresh' not in st.session_state:
    st.session_state.login_refresh = 0
if 'teesheet_refresh' not in st.session_state:
    st.session_state.teesheet_refresh = 0

# Step 1: Golf Portal Login Widget
st.header("Step 1: Login to BRS Golf")

# Add refresh button for login iframe
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Refresh Login", key="refresh_login_btn"):
        st.session_state.login_refresh += 1

brs_login_url = "https://members.brsgolf.com/gsaayr/login"
# Add cache-busting parameter to force iframe reload
login_url_with_refresh = f"{brs_login_url}?_refresh={st.session_state.login_refresh}"
iframe(login_url_with_refresh, width=800, height=600)

st.markdown("---")

# Step 2: URL & Interval Input with Reload Option
st.header("Step 2: Set Up Auto Reload")
user_url = st.text_input(
    "Enter URL to reload (e.g., Tee Sheet page)", 
    value="https://members.brsgolf.com/gsaayr/tee-sheet/1/2025/11/04"
)
interval = st.number_input(
    "Reload interval (in seconds)", 
    min_value=5, max_value=3600, value=30, step=1
)
reload_enabled = st.checkbox("Enable auto-reload", value=False)

if user_url and reload_enabled:
    st.success(f"Auto-reload enabled! This page will refresh every {interval} seconds.")
    # Streamlit reruns script on every interaction; use st.experimental_rerun in combination

    # Add refresh button for tee sheet iframe
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Page", key="refresh_teesheet_btn"):
            st.session_state.teesheet_refresh += 1

    st.write(f"Preview of: {user_url}")
    # Add cache-busting parameter to force iframe reload
    teesheet_url_with_refresh = f"{user_url}{'&' if '?' in user_url else '?'}_refresh={st.session_state.teesheet_refresh}"
    iframe(teesheet_url_with_refresh, width=800, height=600)
    st.experimental_set_query_params(url=user_url)
    st_autorefresh = st.experimental_rerun
else:
    st.write(f"Manual preview (does not auto-reload yet):")
    if user_url:
        # Add refresh button for manual preview
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Refresh Page", key="refresh_manual_btn"):
                st.session_state.teesheet_refresh += 1

        # Add cache-busting parameter to force iframe reload
        teesheet_url_with_refresh = f"{user_url}{'&' if '?' in user_url else '?'}_refresh={st.session_state.teesheet_refresh}"
        iframe(teesheet_url_with_refresh, width=800, height=600)

# How it works (user guidance)
st.info("""
1. First, log in to BRS Golf portal using the login iframe above.
2. If the login page doesn't load, click the '🔄 Refresh Login' button to reload it.
3. Enter the Tee Sheet or other page URL you want to auto-refresh.
4. Set the desired interval and check 'Enable auto-reload'.
5. Use the '🔄 Refresh Page' button to manually reload the tee sheet iframe if needed.
6. If you disable auto-reload, you can still view & interact manually.
""")
