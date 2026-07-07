# Grabit × Actioner — Tee-Time Slots via YAML Flows

Replaces the Streamlit prototypes ([local/qiangpiaowang.py](local/qiangpiaowang.py),
[local/qiangpiaoplaywright.py](local/qiangpiaoplaywright.py)) with declarative
flows running in the containerized Playwright MCP actioner
(`playwright_poc/actioner`). Same image as the Betfair setup — **no rebuild**;
everything specific to golf arrives at runtime as mounts + env.

**Why the prototype got stuck on the tee sheet, and how this fixes it:**

1. `/{club}/tee-sheet/{course}/{date}` without an authenticated session 302s to
   `/login` — the prototype's temporary headless browsers had no session, and its
   "persistent browser" path depended on fragile Streamlit session state.
   → Fixed by the shared, long-lived browser context in the actioner + a mounted
   `STORAGE_STATE` captured once on the host (no credentials in the container).
2. The tee sheet is a JS app — the grid renders after load, so `networkidle` on
   the URL wasn't enough. → Fixed by `wait_for` on the actual row selector.

## What's here

| File | Purpose |
|------|---------|
| [flows/brs_tee_sheet.yaml](flows/brs_tee_sheet.yaml) | Read-only MCP tool `brs_tee_sheet(club, course, date, row_selector)` — lists bookable rows. |
| [flows/brs_book_slot.yaml](flows/brs_book_slot.yaml) | GUARDED MCP tool `brs_book_slot(club, course, date, time, confirm, confirm_selector)`. |
| [local/save_brs_session.py](local/save_brs_session.py) | Host-side one-time login → `session/state.json`. |

The flows use two engine features added to `playwright_poc/actioner/flows.py`
for this: an `assert` guard step (YAML-expressible ALLOW_BOOKING/confirm gate)
and `optional: true` on `wait_for` (diagnostics instead of bare timeouts).

## 1. One-time: capture your BRS session on the host

```powershell
pip install playwright
playwright install chromium
python local/save_brs_session.py <yourclub> ./session/state.json
```

A headed browser opens. Log in, **then navigate to a tee sheet and confirm the
grid renders**, then press Enter. Cookies are saved to `session/state.json` —
keep it out of git (it *is* your login).

## 2. Run the golf actioner container

**Rebuild the image once first** — the `assert` / optional-`wait_for` engine
features live in `flows.py`, which is baked into the image (unlike plugins,
which are volume-mounted):

```powershell
cd H:\code\yl\playwright_poc\actioner
docker build -t playwright-actioner:local .
```

Then run with a distinct name + port so it coexists with the betting `actioner`:

```powershell
docker run -d --name golf-actioner -p 8010:8000 --ipc host `
  -v H:/code/yl/grabit/session:/session:ro `
  -v H:/code/yl/grabit/flows:/app/flows:ro `
  -e PLUGINS_DIR=/app/no-plugins `
  -e STORAGE_STATE=/session/state.json `
  -e HEADLESS=true `
  -e USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" `
  playwright-actioner:local
```

- `flows:/app/flows:ro` shadows the bundled example flows → this container
  exposes only the golf tools; `PLUGINS_DIR=/app/no-plugins` (nonexistent)
  keeps the Betfair plugin tools out of it entirely.
- `HEADLESS=true`: BRS has shown no Cloudflare-style anti-bot; if you ever see
  a challenge page in `page_url`, drop to `HEADLESS=false` (Xvfb headed) like
  the Betfair container.
- **No `ALLOW_BOOKING` yet** — read-only by default. Add
  `-e ALLOW_BOOKING=true` only when you're ready for real bookings.

MCP endpoint: `http://localhost:8010/mcp` — add to `~/.claude.json` or any
streamable-HTTP client: `{ "type": "http", "url": "http://localhost:8010/mcp" }`.

## 3. Use it

Read slots:

> "Call brs_tee_sheet for club `<yourclub>`, course 1, date `2026/07/14`"

Result is JSON: `page_url` + `available_slots` (one text blob per bookable
row). Then pick and book:

> "Book the 07:30 slot" → `brs_book_slot(club=…, date=…, time="07:30", confirm=true)`

### First-run tuning checklist (expect one pass of this per new club)

| Symptom | Meaning | Fix |
|---------|---------|-----|
| `page_url` ends in `/login` | Session expired/not valid | Re-run `save_brs_session.py`, restart container |
| `available_slots: []` but `page_url` is the tee sheet | Row markup differs from default selector | Re-call with `row_selector: "tr"` to dump every row, then adjust the default in the YAML |
| `brs_book_slot` times out on the confirm step | Club's booking form uses different button text | Check `booking_page_url` in the error context, walk the form once manually, pass `confirm_selector` |
| Challenge/interstitial page in `page_url` | Anti-bot appeared | `HEADLESS=false`, re-save session |

## 4. Optional: unattended slot watching

The actioner's scheduler can poll and alert with no LLM involved. Mount a
config over `/app/config/schedules.yaml`:

```yaml
schedules:
  - name: watch-saturday-tee
    tool: brs_tee_sheet
    args: { club: yourclub, course: 1, date: "2026/07/18" }
    every_seconds: 300
    run_at_start: true
    alert:
      when_result_contains: "Book"    # any bookable row present
      webhook_env: ALERT_WEBHOOK      # POSTs JSON if this env var is set
```

Booking stays interactive (you pick the slot) — deliberately: the scheduler
alerting + a human/AI calling `brs_book_slot` keeps the write action gated.
If you later want auto-book ("grab the first Saturday 8–10am slot the moment
the sheet opens"), that needs conditional logic the YAML engine doesn't have —
it becomes a small `@action` plugin, following the betfair.py pattern.

## Safety posture

Same tiering as the Betfair actioner: the session mount is read-only, no
credentials enter the container, `brs_book_slot` is double-gated
(`ALLOW_BOOKING` env **and** per-call `confirm=true`), and the container
defaults to read-only because `ALLOW_BOOKING` is simply absent. A booking is a
real-world commitment at your club — verify the first live booking in the BRS
member portal before trusting the receipt output.
