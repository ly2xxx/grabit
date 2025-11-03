# External Browser Approach - Quick Guide

## Solution Overview

**Problem:** BRS Golf blocks iframe embedding, and Playwright had Windows asyncio issues.

**Solution:** Launch pages directly in your default browser using Python's `webbrowser` module.

---

## How It Works

### Simple Architecture
```
Streamlit App (localhost:8501)
    ↓
User clicks "Open Login Page" button
    ↓
Python: webbrowser.open(url, new=2)
    ↓
Your default browser opens BRS Golf in new tab
    ↓
User logs in naturally in browser
    ↓
Browser remembers session (cookies persist)
    ↓
User returns to Streamlit app
    ↓
Clicks "Open Tee Sheet"
    ↓
Browser opens tee sheet in new tab (still logged in)
```

---

## Key Features

### 1. **No Dependencies**
- ✅ Uses Python standard library `webbrowser`
- ✅ No Playwright, no async, no complex setup
- ✅ Works on Windows, Mac, Linux

### 2. **Full Browser Experience**
- ✅ No iframe restrictions - it's a real browser tab
- ✅ All browser features work (extensions, autofill, bookmarks)
- ✅ Login sessions persist naturally
- ✅ Can use any browser (Chrome, Edge, Firefox, Safari)

### 3. **Auto-Refresh Helper**
- ✅ Opens new tabs at configurable intervals
- ✅ Perfect for monitoring tee sheet changes
- ✅ Countdown timer shows next refresh
- ✅ Can disable/enable anytime

### 4. **Session Statistics**
- ✅ Tracks how many times you've opened pages
- ✅ Shows what was last opened
- ✅ Status indicator

---

## Usage Guide

### First Time Setup
```bash
# No special setup needed! Just run:
streamlit run grabit.py
```

### Daily Workflow
1. **Open the app**: `streamlit run grabit.py`
2. **Step 1**: Click "🌐 Open Login Page"
   - BRS Golf opens in your browser
   - Log in normally
   - Keep browser open
3. **Step 2**: Adjust tee sheet URL if needed
4. **Click**: "🌐 Open Tee Sheet"
   - Tee sheet opens in new tab (you're already logged in!)
5. **Optional**: Enable auto-refresh to monitor for changes

### Buttons Explained

| Button | What It Does | Use Case |
|--------|-------------|----------|
| **🌐 Open Login Page** | Opens BRS Golf login in new tab | First step - login |
| **📋 Copy Login URL** | Displays URL for manual copy | Share URL or manual paste |
| **🌐 Open Tee Sheet** | Opens tee sheet URL in new tab | Access tee sheet |
| **🔄 Refresh (New Tab)** | Opens fresh tee sheet tab | Check for updates |
| **🪟 Open in New Window** | Opens in separate window | Side-by-side viewing |
| **📋 Copy URL** | Displays tee sheet URL | Share or bookmark |

### Auto-Refresh Feature

**How it works:**
1. Enable "Auto-refresh helper" checkbox
2. Set interval (e.g., 30 seconds)
3. Every 30 seconds, a new tab opens with fresh tee sheet
4. Close old tabs as needed

**Best practices:**
- Set interval based on how often tee sheet updates (30-60 seconds recommended)
- Close old tabs periodically to avoid clutter
- Disable when done monitoring

---

## Advantages Over Other Approaches

| Feature | Iframe | Playwright Screenshot | External Browser |
|---------|--------|----------------------|------------------|
| **Works with BRS Golf** | ❌ Blocked | ✅ Yes (complex) | ✅ Yes (simple) |
| **Login Persistence** | ❌ No | ⚠️ Custom storage | ✅ Native |
| **Full Interaction** | Limited | ❌ Screenshots only | ✅ Full browser |
| **Setup Complexity** | Low | High | Very Low |
| **Dependencies** | Streamlit | Playwright + asyncio fix | None (stdlib) |
| **Windows Issues** | None | ❌ AsyncIO errors | ✅ No issues |
| **Code Lines** | ~80 | ~300 | ~250 (with docs) |
| **User Experience** | Blocked pages | Click-based interaction | Natural browsing |

---

## Technical Details

### webbrowser.open() Parameters

```python
webbrowser.open(url, new=0, autoraise=True)
```

- `new=0`: Open in same browser window/tab (if possible)
- `new=1`: Open in new browser window
- `new=2`: Open in new browser tab (RECOMMENDED)
- `autoraise=True`: Bring browser to front

### Browser Detection Order

Python's `webbrowser` module tries browsers in this order:
1. **Windows**: Edge → Chrome → Firefox → IE
2. **Mac**: Safari → Chrome → Firefox
3. **Linux**: Firefox → Chrome → Chromium

You can override with environment variable:
```bash
# Force Chrome (Windows)
$env:BROWSER="C:\Program Files\Google\Chrome\Application\chrome.exe"
streamlit run grabit.py

# Force Firefox (Linux/Mac)
BROWSER=/usr/bin/firefox streamlit run grabit.py
```

### Session State Variables

```python
st.session_state.last_opened     # What was last opened
st.session_state.open_count      # Total opens this session
st.session_state.next_refresh_time  # Timestamp for next auto-refresh
```

---

## Troubleshooting

### Browser doesn't open
**Cause**: No default browser set or browser path issue
**Fix**:
```python
import webbrowser
webbrowser.get()  # Shows detected browser
```

### Wrong browser opens
**Cause**: System default browser not set correctly
**Fix**: Set default browser in OS settings or use environment variable (see above)

### Auto-refresh doesn't work
**Cause**: Streamlit not rerunning
**Fix**: Check that checkbox is enabled and interval > 10 seconds

### New tabs pile up
**Not a bug**: This is how auto-refresh works (new tab each time)
**Solution**:
- Manually close old tabs
- Use lower interval (less frequent)
- Use browser's "Close tabs to the right" feature

---

## Code Comparison

### Before (Iframe - Didn't Work)
```python
iframe(brs_login_url, width=800, height=600)
# ❌ Shows blank page due to X-Frame-Options
```

### After (External Browser - Works!)
```python
webbrowser.open(brs_login_url, new=2)
# ✅ Opens in real browser tab
```

---

## Future Enhancements (Optional)

Possible additions if desired:

- [ ] **URL Bookmarks**: Save favorite tee sheet URLs
- [ ] **Date Picker**: Generate tee sheet URLs for specific dates
- [ ] **Course Selector**: Dropdown for different courses
- [ ] **Browser Selector**: Choose which browser to use
- [ ] **Tab Manager**: Track/close opened tabs from Streamlit
- [ ] **Notification**: Desktop notification when auto-refresh runs
- [ ] **URL History**: Track recently opened URLs
- [ ] **Export**: Save URLs to file for later

---

## Summary

This approach trades embedded viewing for **simplicity and reliability**:

**What you lose:**
- No preview in Streamlit app
- Tabs open outside Streamlit window
- Manual tab management

**What you gain:**
- ✅ **Zero setup complexity** - works immediately
- ✅ **No technical issues** - no asyncio, no Playwright, no iframe restrictions
- ✅ **Full browser features** - native login, autofill, extensions
- ✅ **Natural workflow** - use browser as intended
- ✅ **Session persistence** - login once, use forever (until logout)
- ✅ **Cross-platform** - Windows, Mac, Linux
- ✅ **Any browser** - Chrome, Edge, Firefox, Safari, etc.

**Perfect for:**
- Quick access to frequently used pages
- Monitoring tee sheet availability
- Bypassing iframe restrictions
- Simple, reliable automation

---

## Quick Start Cheat Sheet

```bash
# 1. Run app
streamlit run grabit.py

# 2. Open BRS Golf login
Click "🌐 Open Login Page"

# 3. Log in (in browser)
Enter credentials → Submit

# 4. Return to Streamlit

# 5. Open tee sheet
Click "🌐 Open Tee Sheet"

# 6. Enable auto-refresh (optional)
Check "Enable auto-refresh helper"
Set interval → Watch tabs open automatically

# 7. Done! Browser tabs have full BRS Golf access
```

---

**Enjoy your unrestricted BRS Golf access!** ⛳
