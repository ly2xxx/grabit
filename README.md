# GrabIt - Web Content Extractor

A Streamlit-based web content extraction tool using Playwright for scraping and processing web pages. Extract titles, main content, links, and screenshots from any URL.

## Features

- 🌐 **URL Content Extraction**: Extract titles, headings, paragraphs, and links from any webpage
- 📸 **Screenshot Capture**: Automatically capture full-page screenshots of visited URLs
- ⏱️ **Scheduled Scraping**: Set intervals for automatic re-scraping of content
- 🎨 **Clean UI**: User-friendly Streamlit interface
- ⚡ **Async Processing**: Efficient asynchronous web scraping using Playwright

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ly2xxx/grabit.git
cd grabit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Then:
1. Enter a URL in the input field
2. (Optional) Set a scraping interval in seconds for automatic re-scraping
3. Click "Extract Content" button to start extraction
4. View extracted title, screenshot, main content, and links

## Architecture

### Core Modules

- **app.py**: Streamlit UI application for web content extraction
- **extract_cleaner_webpage_sync.py**: Core extraction module with Playwright integration

### Key Classes

**WebContentExtractor**
- Main extractor class handling page navigation and content parsing
- Methods:
  - `extract_clean_content()`: Main extraction method
  - `_take_screenshot()`: Captures full-page screenshots
  - `_extract_content()`: Extracts structured content
  - `_extract_main_content()`: Extracts headings and paragraphs
  - `_extract_links()`: Extracts hyperlinks

## Requirements

- Python 3.8+
- Streamlit 1.28.1
- Playwright 1.40.0

See `requirements.txt` for the complete list of minimal dependencies.

## How It Works

1. **URL Navigation**: Uses Playwright's Chromium browser to load the target URL
2. **Screenshot**: Captures the full rendered page
3. **Content Parsing**: Extracts:
   - Page title
   - Headings (h1, h2)
   - Paragraphs (filtered by minimum length)
   - Links with text and URLs
4. **Async Processing**: All operations run asynchronously for better performance
5. **Auto-Refresh**: Optionally re-runs extraction at specified intervals

## Configuration

### Screenshot Directory
Screenshots are saved to `./screenshots/` by default. This directory is created automatically.

### Content Limits
- First 10 h2 headings extracted
- First 15 paragraphs extracted
- First 20 links extracted
- Paragraphs with less than 20 characters are filtered out

## Error Handling

The module includes comprehensive error handling:
- Network timeouts
- Invalid URLs
- Missing page elements
- Browser launch failures

All errors are logged and displayed to the user through the Streamlit interface.

## Performance Notes

- First run may take 10-15 seconds for browser initialization
- Screenshot capture varies by page size
- Large pages may take longer to extract content

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.
