# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/ly2xxx/grabit.git
cd grabit
```

### 2. Create a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
The Playwright library requires browser binaries to be installed:
```bash
playwright install chromium
```

## Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Basic Usage

1. **Enter URL**: Type or paste a URL in the "Enter a URL to extract content from:" field
2. **Set Interval (Optional)**: Specify a scraping interval in seconds. Leave as 0 for one-time scraping
3. **Click Extract**: Press the "Extract Content" button
4. **View Results**: 
   - Extracted page title
   - Full-page screenshot
   - Main content (headings and paragraphs)
   - Links found on the page

## Project Structure

```
grabit/
├── app.py                              # Main Streamlit application
├── extract_cleaner_webpage_sync.py     # Core extraction module
├── requirements.txt                    # Python dependencies
├── README.md                          # Full documentation
├── QUICKSTART.md                      # This file
└── .gitignore                         # Git ignore rules
```

## Troubleshooting

### Issue: "playwright is not installed"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "Browser not found"
**Solution**: Run `playwright install chromium`

### Issue: Connection timeout
**Solution**: Ensure you have a stable internet connection and the URL is valid

### Issue: No content extracted
**Solution**: Some websites may block scraping. Try a different URL.

## Key Features Explained

### Screenshot Capture
- Full-page screenshots are saved to `./screenshots/` directory
- Filenames include timestamp for easy identification

### Content Extraction
- **Headings**: Extracts h1 and h2 tags
- **Paragraphs**: Extracts p tags with minimum 20 characters
- **Links**: Extracts href and display text from a tags

### Auto-Refresh
- Set an interval > 0 to enable automatic re-scraping
- The countdown timer shows seconds until next extraction
- Set interval to 0 to disable auto-refresh

## Performance Tips

1. **First Run**: The initial run may take 10-15 seconds as Playwright initializes the browser
2. **Large Pages**: Pages with lots of content may take longer to process
3. **Screenshots**: Full-page screenshots can be large for very tall pages

## Advanced Usage

### Modifying Content Extraction Limits

Edit `extract_cleaner_webpage_sync.py` to change extraction limits:

```python
# In _extract_main_content():
h2_elements = await page.query_selector_all("h2")
for elem in h2_elements[:10]:  # Change 10 to desired limit

# In _extract_links():
a_elements = await page.query_selector_all("a[href]")
for elem in a_elements[:20]:  # Change 20 to desired limit
```

### Custom Screenshot Directory

Modify the `WebContentExtractor` initialization in `app.py`:

```python
extractor = WebContentExtractor(screenshots_dir="custom_path")
```

## Support

For issues and feature requests, visit: https://github.com/ly2xxx/grabit/issues

## Next Steps

- Explore different websites and compare extracted content
- Integrate the extraction module into your own projects
- Contribute improvements back to the project!
