"""Log in to BRS Golf once on your HOST and save the session for the actioner container.

Session-injection approach (same as playwright_poc/actioner/save_session.py for
Betfair): a real headed browser opens, you log in fully — password manager, any
MFA, cookie banners — and the authenticated cookies/localStorage are saved to a
JSON file the container mounts read-only. No credentials ever enter the container.

Usage:
    pip install playwright && playwright install chromium
    python save_brs_session.py <club> [out_path]
    # e.g.:  python save_brs_session.py gsaayr ./session/state.json

Then run the golf actioner container with:
    -v H:/code/yl/grabit/session:/session:ro -e STORAGE_STATE=/session/state.json

IMPORTANT: after logging in, navigate to an actual tee-sheet date and confirm
the grid renders BEFORE pressing Enter — some member areas set additional
cookies on first tee-sheet visit (the Betfair equivalent of this bit us: each
page family can carry its own clearance).
"""

import asyncio
import os
import sys

from playwright.async_api import async_playwright

CLUB = sys.argv[1] if len(sys.argv) > 1 else "gsaayr"
OUT = sys.argv[2] if len(sys.argv) > 2 else "./session/state.json"
LOGIN_URL = f"https://members.brsgolf.com/{CLUB}/login"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


async def main() -> None:
    out_dir = os.path.dirname(OUT)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(user_agent=UA, locale="en-GB")
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        await page.goto(LOGIN_URL, timeout=60000, wait_until="domcontentloaded")
        print(
            f"\n>>> Log in to {LOGIN_URL} in the browser window.\n"
            ">>> Then NAVIGATE TO A TEE SHEET (Tee Booking → pick any date) and\n"
            ">>> confirm the time grid actually renders. When it does, come back\n"
            ">>> here and press Enter to save the session…"
        )
        await asyncio.get_event_loop().run_in_executor(None, input)

        await context.storage_state(path=OUT)
        print(f"\n>>> Saved authenticated session to: {OUT}")

        print(
            "\n>>> Start the golf actioner container with a matching user agent:\n"
            f'docker run -d --name golf-actioner -p 8010:8000 --ipc host '
            f"-v H:/code/yl/grabit/session:/session:ro "
            f"-v H:/code/yl/grabit/flows:/app/flows:ro "
            f"-e PLUGINS_DIR=/app/no-plugins "
            f"-e STORAGE_STATE=/session/state.json "
            f'-e USER_AGENT="{UA}" '
            f"playwright-actioner:local\n"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
