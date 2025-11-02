import streamlit as st
import asyncio
import time
from extract_cleaner_webpage_sync import extract_clean_content

# st.title("Web Content Extractor")
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Web Content Extractor")
# Create a 2x2 table layout
col1, col2 = st.columns(2)

# First row
with col1:
    # First column, first row: URL input
    url = st.text_input("Enter a URL to extract content from:")

with col2:
    # Add some vertical space to align with the input box
    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    # Second column, first row: Goto icon
    if url:
        st.markdown(f"<a href='{url}' target='_blank'>🔗</a>", unsafe_allow_html=True)

# Second row
with col1:
    # First column, second row: Interval input
    interval = st.number_input("Scraping interval (seconds, 0 for one-time scrape):", 
                            min_value=0, value=0, step=1)

with col2:
    # # Add some vertical space to align with the input box
    # st.markdown("<div style='margin-top: -50px;'></div>", unsafe_allow_html=True)
    
    if interval > 0 and url:
        # Store the last run time in session state if not already there
        if 'last_run_time' not in st.session_state:
            st.session_state.last_run_time = time.time()
        ph = st.empty()
        N = interval
        for secs in range(N,0,-1):
            mm, ss = secs//60, secs%60
            ph.metric("Countdown", f"{mm:02d}:{ss:02d}")
            time.sleep(1)

# Store the last run time in session state
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = 0
# Check if it's time to run again based on the interval
current_time = time.time()
should_run = st.button("Extract Content") or (
    interval > 0 and 
    url and 
    current_time - st.session_state.last_run_time >= interval
)

if should_run and url:
    # Update the last run time
    st.session_state.last_run_time = current_time
    
    with st.spinner("Extracting content..."):
        # Run the async function using an event loop
        loop = asyncio.ProactorEventLoop()
        result = loop.run_until_complete(extract_clean_content(url))
        
        # Store the result in session state
        st.session_state.result = result
        
        # Set a flag to indicate we have results
        st.session_state.has_results = True

# Display the results if we have them
if st.session_state.get('has_results', False):
    result = st.session_state.result
    
    st.subheader("Extracted Title")
    st.write(result['clean_data']['title'])
    
    st.subheader("Screenshot")
    st.image(result['screenshot_path'])
    
    st.subheader("Main Content")
    for item in result['clean_data']['main_content']:
        st.write(f"**{item['type'].upper()}:** {item['text']}")
    
    st.subheader("Links")
    for link in result['clean_data']['links']:
        st.write(f"- [{link['text']}]({link['url']})")

# Add auto-rerun if interval is set
if interval > 0 and url:
    st.info(f"Auto-refreshing every {interval} seconds. Set interval to 0 to stop.")
    time_to_next = max(0, interval - (time.time() - st.session_state.last_run_time))
    st.write(f"Next refresh in {time_to_next:.1f} seconds")
    
    # This is the key part - use Streamlit's rerun to refresh the page
    time.sleep(max(1, interval))  # Small delay to prevent too frequent reruns
    st.rerun()
