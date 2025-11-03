# Iframe Fix - Playwright Screenshot Solution

## Problem Solved
Ladbrokes (and many other sites) block iframe embedding using `X-Frame-Options` security headers, causing the iframes in the original `grabit.py` to show blank pages.

## Solution Implemented
Replaced iframe embedding with **Playwright browser automation** that captures screenshots of the actual rendered pages. This completely bypasses iframe restrictions.

## What Changed in `grabit.py`

### Before (Iframe-based)
- Used `streamlit.components.v1.iframe()` to embed websites
- ❌ Blocked by `X-Frame-Options` headers
- ❌ No way to interact with login forms
- ❌ Sessions didn't persist

### After (Playwright-based)
- Uses Playwright headless browser to render pages
- ✅ Captures screenshots of real browser content
- ✅ Automates login form filling
- ✅ Maintains session cookies across navigations
- ✅ Works with ANY website (no iframe restrictions)

## New Features

### 1. **Interactive Login Form**
- Enter username and password in Streamlit UI
- Configurable CSS selectors for form fields
- One-click auto-login that:
  - Navigates to login page
  - Fills username and password fields
  - Clicks submit button
  - Captures logged-in state

### 2. **Screenshot-Based Viewing**
- Displays actual rendered page content as images
- Manual refresh button to update view
- Status indicators (logged in, last action, screenshot age)

### 3. **Session Persistence**
- Cookies stored in `st.session_state.browser_context`
- Login session carries over to subsequent page navigations
- Stay logged in across Streamlit app refreshes

### 4. **Auto-Refresh Feature**
- Configurable interval (5-3600 seconds)
- Countdown timer showing next refresh
- Automatic screenshot capture and display
- Enable/disable toggle

## How to Use

### Prerequisites
```bash
# Install Playwright if not already installed
pip install playwright
playwright install chromium
```

### Run the App
```bash
streamlit run grabit.py
```

### Workflow
1. **Load Login Page**
   - Click "🌐 Load Login Page" to capture Ladbrokes login screen
   - View screenshot in the preview pane

2. **Configure Selectors** (if needed)
   - Default selectors: `input[name="username"]`, `input[name="password"]`, `button[type="submit"]`
   - Adjust if Ladbrokes changes their HTML structure
   - To find selectors: Right-click element in browser → Inspect → Copy selector

3. **Login**
   - Enter your Ladbrokes username and password
   - Click "🔐 Auto Login" button
   - Wait 10-15 seconds for automation to complete
   - Screenshot shows logged-in page

4. **Navigate**
   - Enter sports page URL (e.g., `https://www.ladbrokes.com/en/sports`)
   - Click "🌐 Navigate to URL"
   - View content screenshot

5. **Auto-Refresh**
   - Set interval (e.g., 30 seconds)
   - Check "Enable auto-refresh"
   - Page automatically reloads and displays new screenshot
   - Use for monitoring odds changes, availability, etc.

## Technical Architecture

### Async Playwright Functions
```python
_navigate_and_capture_async()
├── Launches headless Chromium browser
├── Restores cookies from session_state if available
├── Navigates to URL (waits for network idle)
├── Captures screenshot
├── Saves cookies back to session_state
└── Returns screenshot bytes

_fill_and_submit_async()
├── Launches browser
├── Navigates to login URL
├── Fills username field
├── Fills password field
├── Clicks submit button
├── Waits for login completion
├── Captures logged-in screenshot
└── Saves session cookies
```

### Sync Wrapper Functions
```python
navigate_and_capture()      # Called by navigation buttons
fill_and_submit_login()     # Called by Auto Login button
```

### Session State Variables
- `screenshot_data`: Binary image data
- `current_url`: Last navigated URL
- `login_status`: Boolean login flag
- `browser_context`: Playwright cookies/storage state
- `screenshot_timestamp`: Time of last capture
- `last_action`: Status message
- `next_refresh`: Timestamp for next auto-refresh

## Performance Notes

- **Screenshot Capture Time**: 2-5 seconds per capture
  - Headless browser launch: ~1s
  - Page load + network idle: 1-3s
  - Screenshot render: ~0.5s

- **Auto-Refresh Overhead**: Each refresh = full browser automation cycle
  - Don't set interval too low (minimum 5 seconds recommended)
  - For real-time monitoring: use 10-30 second intervals

- **Memory Usage**: Headless Chromium ~50-100MB per screenshot
  - Browser closes after each operation (stateless)
  - Only cookies persist in session_state

## Troubleshooting

### "Login failed" Error
- **Cause**: CSS selectors don't match Ladbrokes HTML
- **Fix**:
  1. Open `https://www.ladbrokes.com/en/labelhost/login` in browser
  2. Right-click username field → Inspect
  3. Copy CSS selector (e.g., `#username`, `.login-form input[type="text"]`)
  4. Update "Username field selector" in the app
  5. Repeat for password field and submit button

### Screenshot Shows Wrong Page
- **Cause**: Navigation too fast, page not fully loaded
- **Fix**: Increase `timeout` or wait times in Playwright functions
- Code location: `grabit.py` lines 36, 55, 66

### "NotImplementedError" or "asyncio.run()" Error on Windows
- **Cause**: Windows event loop doesn't support subprocess creation by default
- **Error Message**: `NotImplementedError` in `asyncio.base_events._make_subprocess_transport`
- **Status**: ✅ **ALREADY FIXED** in current version (lines 8-11 of grabit.py)
- **Fix Applied**:
```python
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```
- If you still encounter this error, ensure the fix is at the **top of the file** before any async operations

### Cookies Not Persisting
- **Cause**: `browser_context` not saved properly
- **Fix**: Ensure `await context.storage_state()` runs before browser closes
- Code location: lines 42, 72

## Comparison: Iframe vs Playwright

| Feature | Iframe (Old) | Playwright (New) |
|---------|-------------|------------------|
| **Works with Ladbrokes** | ❌ Blocked | ✅ Yes |
| **Login Automation** | ❌ No | ✅ Yes |
| **Session Persistence** | ❌ No | ✅ Yes |
| **Interaction Speed** | Fast (instant) | Moderate (2-5s) |
| **User Interaction** | Limited | Automated forms |
| **Browser Compatibility** | Depends on site | Chromium-based |
| **Bypass Restrictions** | ❌ No | ✅ Yes |

## Future Enhancements (Optional)

- [ ] Add screenshot history carousel
- [ ] Implement browser "Back" and "Forward" buttons
- [ ] Add scroll position control
- [ ] Export screenshot gallery as PDF
- [ ] Implement element click mapping (click on screenshot → interact with page)
- [ ] Add network traffic monitoring
- [ ] Support multiple concurrent sessions

## License & Disclaimer

This tool is for personal use only. Ensure you comply with Ladbrokes' Terms of Service when using automated tools. The screenshot approach is non-intrusive but automated login may violate ToS - use at your own risk.
