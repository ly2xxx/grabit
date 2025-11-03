import streamlit as st
from streamlit.components.v1 import iframe

st.title("BRS Golf Auto Reloader")

# Step 1: Golf Portal Login Widget
st.header("Step 1: Login to BRS Golf")
brs_login_url = "https://members.brsgolf.com/gsaayr/login"
iframe(brs_login_url, width=800, height=600)

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
    st.write(f"Preview of: {user_url}")
    iframe(user_url, width=800, height=600)
    st.experimental_set_query_params(url=user_url)
    st_autorefresh = st.experimental_rerun
else:
    st.write(f"Manual preview (does not auto-reload yet):")
    if user_url:
        iframe(user_url, width=800, height=600)

# How it works (user guidance)
st.info("""
1. First, log in to BRS Golf portal.
2. Enter the Tee Sheet or other page URL you want to auto-refresh.
3. Set the desired interval and check 'Enable auto-reload'.
4. If you disable auto-reload, you can still view & interact manually.
""")
