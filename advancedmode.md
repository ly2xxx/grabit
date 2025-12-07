# 🚀 Advanced Mode (Auto-Clicker Bot) Instructions

The **Advanced Mode** upgrades `qiangpiao.py` from a simple link opener to an automation assistant that can interact with the webpage directly.

## 🛠️ Prerequisites

This mode uses **Playwright** to control a real Chrome browser instance.
If you haven't already, you must install the browser binaries:

```bash
playwright install chromium
```

## 📖 Step-by-Step Guide

### 1. Launch the Bot Browser
1.  Toggle the **"🚀 Advanced Mode"** switch at the top of the app.
2.  Click the **"🚀 Launch/Connect Browser"** button.
3.  A new Chromium window will open. **Do not close this window.**

### 2. Login Manually
1.  In the new browser window, go to the BRS Golf login page.
2.  Log in with your username and password.
3.  Navigate to the specific **Tee Sheet** page you want to target (e.g., the date you want to book).

### 3. Scan for Tee Times
1.  Return to the Streamlit app.
2.  Under **"🤖 Bot Controls"**, click **"🔍 Scan Page for Tee Times"**.
3.  The app will analyze the page and find all clickable booking buttons (times, prices, "Book Now" buttons).
4.  If nothing is found, make sure you are on the correct page and try again.

### 4. Select Your Target
1.  Use the **"Select Target to Auto-Click"** dropdown to choose the specific tee time you want (e.g., `07:00 - £20.00`).

### 5. Start Sniping
You have two options:

*   **🎯 Refresh & Auto-Click ONCE**:
    - Clicks the button once.
    - Useful if the booking window is already open and you just want to act fast.

*   **🔥 Enable Auto-Sniper Loop**:
    - **Best for releases**: Use this 1-2 minutes before the times are released (e.g., 6:58 AM for a 7:00 AM release).
    - Checks the box to enable.
    - Set the **Interval** (e.g., 2-5 seconds).
    - The bot will continuously **Refresh** the page and attempt to **Click** your target immediately upon load.
    - Once the button is clicked, uncheck the box to stop the loop.

## ❓ Troubleshooting

*   **"Browser manager not found"**: Ensure `browser_manager.py` is in the same folder as `qiangpiao.py` and you have installed `playwright`.
*   **Browser closes unexpectedly**: Click "Launch/Connect Browser" to restart it.
*   **Can't find tee times**: Ensure the browser is on the actual Tee Sheet page, not the dashboard or login screen.
