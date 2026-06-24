# WMN Checker

Standalone site-checking script for the [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) project. Checks every site in `wmn-data.json` to verify that the detection strings and HTTP codes are still working, then writes a dated Markdown report organised by failure type so you can work through it and fix issues one section at a time.

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `requests`, `playwright`

Playwright also needs a browser binary. The checker uses your **system-installed Chromium or Chrome** as a fallback — it does not download its own:

```bash
# Ubuntu / Debian
sudo apt install chromium-browser

# Then point Playwright at it (auto-detected from common paths)
# /usr/bin/chromium-browser, /usr/bin/chromium, /usr/bin/google-chrome
```

## How it works

Each site is checked in two phases:

**Phase 1 — `requests` (fast path)**  
Makes a plain HTTP GET or POST with a randomised browser User-Agent. No JavaScript is executed. Checks:
- A **known username** URL: expects `e_code` (HTTP status) and `e_string` (body substring) to confirm the account exists.
- A **random username** URL: expects `m_code` and `m_string` to confirm a non-existent account is handled correctly.

**Phase 2 — Playwright fallback (browser)**  
If Phase 1 returns a suspicious result (`blocked`, `false_positive`, `e_string_missing`, `m_string_missing`, `e_code_mismatch`, or `m_code_mismatch`), the site is re-checked using a headless Chromium browser. The browser executes JavaScript and waits for the page to settle before reading the response, which resolves issues caused by JS-rendered content and basic bot-blocking challenges.

Browser fallbacks are serialized (one at a time) to avoid threading conflicts with Playwright's sync API. The report notes which sites needed the browser and whether it improved the result.

Sites are checked concurrently using a thread pool (default 10 workers).

## Usage

```bash
cd scripts/checker
python3 wmn_check.py [OPTIONS]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--limit N` | all | Check only the first N sites (after any offset) |
| `--workers N` | 10 | Number of concurrent worker threads |
| `--output-dir PATH` | `scripts/checker/` | Directory to write the report file |
| `--data PATH` | `wmn-data.json` | Path to the data file |
| `--start-at NAME` | — | Start at this site name (case-insensitive, prefix match). Mutually exclusive with `--offset` |
| `--offset N` | — | Skip the first N sites. Mutually exclusive with `--start-at` |

### Examples

```bash
# Check all sites
python3 wmn_check.py

# Check 50 sites with 20 workers
python3 wmn_check.py --limit 50 --workers 20

# Start at a specific site by name (case-insensitive, prefix is enough)
python3 wmn_check.py --start-at flickr

# Skip the first 200 sites
python3 wmn_check.py --offset 200

# Check 50 sites starting at GitHub
python3 wmn_check.py --start-at github --limit 50

# Check sites 100–149
python3 wmn_check.py --offset 100 --limit 50

# Write report to a custom directory
python3 wmn_check.py --output-dir ~/reports
```

Press **Ctrl+C** at any time to stop — the script will write a partial report of whatever was completed before the interrupt.

## Output

The script writes a Markdown file named by timestamp:

```
20260617-1421-wmncheck.md          # complete run
20260617-1421-wmncheck-partial.md  # interrupted run
```

These files are listed in `.gitignore` and will not be committed to the repo.

### Report sections

The report opens with a summary count table and a Playwright metrics table (how many sites triggered the browser fallback and whether it helped), then organises sites into 8 sections — each sorted alphabetically by site name:

| # | Section | Status values |
|---|---------|--------------|
| 1 | **Domains That Did Not Resolve** | `site_down` |
| 2 | **Bad e\_code or e\_string** | `e_code_mismatch`, `e_string_missing` where the random check also fails (detection config is broken) |
| 3 | **Bad Known User** | `e_code_mismatch`, `e_string_missing` where the random check passes (detection works, account is gone) |
| 4 | **Bad m\_code or m\_string** | `m_code_mismatch`, `m_string_missing` |
| 5 | **Blocked / CAPTCHA** | `blocked` |
| 6 | **Other** | `false_positive`, `false_negative`, anything uncategorised |
| 7 | **Sites That Checked Correctly** | `ok` |
| 8 | **Skipped** | `valid: false` in data |

Each entry in sections 1–6 includes:

- Clickable `uri_check` link with each known username substituted in
- `uri_pretty` profile link next to it (when present in the data)
- A table of expected vs received `e_code`, `e_string`, `m_code`, `m_string`
- Per-check results (username, HTTP code received, status, note)
- A `🌐` Playwright note when the browser fallback ran, showing the requests result and the browser result side by side

Section 7 (OK) is compact — just the site name and clickable URLs.

## Terminal output

Each site is logged as it completes, coloured by status:

| Colour | Statuses |
|--------|----------|
| Green | `ok` |
| Purple | `blocked` |
| Orange | `e_code_mismatch`, `e_string_missing`, `m_code_mismatch`, `m_string_missing` |
| Red | `false_positive`, `false_negative` |
| Gray | `site_down`, `skipped` |
| Blue | Playwright browser notes |

Colours are suppressed automatically when output is piped to a file.

## Files

| File | Purpose |
|------|---------|
| `wmn_check.py` | CLI entry point — parses args, runs checks, writes report |
| `checker.py` | Core checking engine — HTTP requests, Playwright fallback, result aggregation |
| `models.py` | Dataclasses (`SiteResult`, `CheckDetail`) and status constants |
| `requirements.txt` | Python dependencies |
