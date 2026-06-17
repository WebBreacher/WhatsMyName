#!/usr/bin/env python3
"""
wmn_check.py — Standalone WMN site checker.

Checks sites from wmn-data.json and writes a dated markdown report organised
by failure type so you can work through it top-to-bottom and fix as you go.

Usage:
    python3 wmn_check.py                        # check all sites
    python3 wmn_check.py --limit 50             # check first 50
    python3 wmn_check.py --workers 20           # more concurrency
    python3 wmn_check.py --output-dir /tmp      # custom output dir
    python3 wmn_check.py --data /path/to/wmn-data.json
"""

import argparse
import logging
import sys
import threading
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from checker import load_sites, run_checker, _c, _cs
from models import (
    STATUS_OK, STATUS_SITE_DOWN, STATUS_BLOCKED, STATUS_SKIPPED,
    STATUS_E_CODE_MISMATCH, STATUS_E_STRING_MISSING,
    STATUS_M_CODE_MISMATCH, STATUS_M_STRING_MISSING,
)

REPO_ROOT = HERE.parent.parent
DEFAULT_DATA = REPO_ROOT / "wmn-data.json"


# ── Categorisation ─────────────────────────────────────────────────────────

def _random_passed(checks: list) -> bool:
    """True if the random-username check came back ok (detection logic is sound)."""
    return any(
        c["username_type"] == "random" and c["status"] == STATUS_OK
        for c in checks
    )


def categorize(results: list) -> dict:
    cats = {
        "site_down":      [],   # 1 — no DNS / no response
        "bad_detection":  [],   # 2 — e_code or e_string config broken
        "bad_known_user": [],   # 3 — detection fine but known account is gone
        "bad_missing":    [],   # 4 — m_code or m_string config broken
        "blocked":        [],   # 5 — Cloudflare / CAPTCHA / bot block
        "other":          [],   # 6 — false_positive, false_negative, etc.
        "ok":             [],   # 7 — all good
        "skipped":        [],   # 8 — valid:false
    }
    for r in results:
        s = r["overall_status"]
        checks = r.get("checks", [])
        if s == STATUS_SKIPPED:
            cats["skipped"].append(r)
        elif s == STATUS_SITE_DOWN:
            cats["site_down"].append(r)
        elif s == STATUS_BLOCKED:
            cats["blocked"].append(r)
        elif s == STATUS_OK:
            cats["ok"].append(r)
        elif s in (STATUS_E_CODE_MISMATCH, STATUS_E_STRING_MISSING):
            # If the random (missing-account) check passed, the detection strings/codes
            # are correct — the problem is just that the specific known account is gone.
            if _random_passed(checks):
                cats["bad_known_user"].append(r)
            else:
                cats["bad_detection"].append(r)
        elif s in (STATUS_M_CODE_MISMATCH, STATUS_M_STRING_MISSING):
            cats["bad_missing"].append(r)
        else:
            cats["other"].append(r)

    for lst in cats.values():
        lst.sort(key=lambda r: r["name"].lower())
    return cats


# ── Per-site markdown block ────────────────────────────────────────────────

def _known_url_lines(r: dict) -> list:
    uri_check = r.get("uri_check", "")
    uri_pretty = r.get("uri_pretty", "")
    has_post = r.get("has_post_body", False)
    lines = []
    for username in r.get("known", []):
        if has_post:
            # POST endpoint — URL is fixed; link to profile if available
            if uri_pretty:
                pretty_url = uri_pretty.replace("{account}", username)
                lines.append(
                    f"- `{username}` → POST [{uri_check}]({uri_check})"
                    f" | [Profile ↗]({pretty_url})"
                )
            else:
                lines.append(f"- `{username}` → POST [{uri_check}]({uri_check})")
        else:
            check_url = uri_check.replace("{account}", username)
            if uri_pretty:
                pretty_url = uri_pretty.replace("{account}", username)
                lines.append(
                    f"- [{check_url}]({check_url})"
                    f" | [Profile ↗]({pretty_url})"
                )
            else:
                lines.append(f"- [{check_url}]({check_url})")
    return lines


def _detection_table(r: dict, checks: list) -> list:
    """Build a compact expected-vs-received table for detection values."""
    known_checks = [c for c in checks if c["username_type"] == "known"]
    random_checks = [c for c in checks if c["username_type"] == "random"]

    kc = known_checks[0] if known_checks else {}
    rc = random_checks[0] if random_checks else {}

    k_code = kc.get("http_code")
    r_code = rc.get("http_code")

    e_code = r.get("e_code", "")
    e_string = r.get("e_string", "")
    m_code = r.get("m_code", "")
    m_string = r.get("m_string", "")

    def code_cell(expected, received):
        if received is None:
            return f"`{expected}` | `none` ⚠️"
        match = "✅" if received == expected else "❌"
        return f"`{expected}` | `{received}` {match}"

    def string_found(expected, check):
        if not expected or not check:
            return f"`{expected}`"
        snippet = check.get("body_snippet", "")
        found = expected in snippet
        mark = "✅ found" if found else "❌ not found"
        return f"`{expected}` — {mark}"

    lines = [
        "",
        "| Field | Expected | Received |",
        "|-------|----------|----------|",
        f"| e_code | `{e_code}` | {code_cell(e_code, k_code)} |",
        f"| e_string | {string_found(e_string, kc)} | |",
        f"| m_code | `{m_code}` | {code_cell(m_code, r_code)} |",
        f"| m_string | {string_found(m_string, rc)} | |",
    ]
    return lines


def _check_lines(checks: list) -> list:
    lines = []
    for c in checks:
        code = c["http_code"] if c["http_code"] is not None else "none"
        note = c.get("note", "").replace("[browser] ", "")
        bmark = " 🌐" if c.get("note", "").startswith("[browser]") else ""
        lines.append(
            f"- `{c['username_type']}` **{c['username']}**"
            f" → HTTP `{code}` — **{c['status']}**{bmark}"
            f"  \n  _{note}_"
        )
    return lines


def site_block(r: dict,
               include_detection: bool = True,
               include_checks: bool = True,
               compact: bool = False) -> str:
    checks = r.get("checks", [])
    parts = [f"### {r['name']}\n"]

    url_lines = _known_url_lines(r)
    if url_lines:
        parts.extend(url_lines)

    if include_detection and not compact:
        parts.extend(_detection_table(r, checks))

    if include_checks and not compact:
        check_lines = _check_lines(checks)
        if check_lines:
            parts.append("\n**Check results:**")
            parts.extend(check_lines)

    # Playwright note
    if r.get("browser_used"):
        req_s = r.get("requests_status", "")
        cur_s = r.get("overall_status", "")
        if req_s and req_s != cur_s:
            parts.append(
                f"\n> 🌐 **Playwright fallback:** requests → `{req_s}` | browser → `{cur_s}`"
            )
        else:
            parts.append("\n> 🌐 *Result via Playwright browser fallback*")

    parts.append("\n---\n")
    return "\n".join(parts)


# ── Section renderer ───────────────────────────────────────────────────────

def render_section(heading: str, emoji: str, sites: list, **kwargs) -> str:
    out = [f"## {emoji} {heading}\n"]
    if not sites:
        out.append("_None._\n")
        return "\n".join(out)
    for r in sites:
        out.append(site_block(r, **kwargs))
    return "\n".join(out)


# ── Playwright metrics ─────────────────────────────────────────────────────

def playwright_section(results: list) -> str:
    pw = [r for r in results if r.get("browser_used")]
    if not pw:
        return "_Playwright was not invoked for any site._\n"

    transitions: dict = defaultdict(int)
    for r in pw:
        key = (r.get("requests_status", "?"), r.get("overall_status", "?"))
        transitions[key] += 1

    improved = sum(v for (rs, bs), v in transitions.items() if rs != bs and bs == STATUS_OK)
    unchanged = sum(v for (rs, bs), v in transitions.items() if rs == bs)
    changed_other = len(pw) - improved - unchanged

    lines = [
        f"**{len(pw)}** site(s) triggered the Playwright fallback.",
        f"- ✅ Resolved by browser: **{improved}**",
        f"- ➡️ Still failing after browser: **{changed_other}**",
        f"- ↔️ Same result either way: **{unchanged}**",
        "",
        "| Requests result | Browser result | Count |",
        "|-----------------|----------------|-------|",
    ]
    for (rs, bs), count in sorted(transitions.items(), key=lambda x: -x[1]):
        arrow = "✅" if bs == STATUS_OK and rs != bs else ("↔️" if rs == bs else "⚠️")
        lines.append(f"| `{rs}` | `{bs}` {arrow} | {count} |")

    return "\n".join(lines) + "\n"


# ── Full report ────────────────────────────────────────────────────────────

def render_report(results: list, cats: dict, ts_str: str,
                  sites_checked: int, workers: int) -> str:
    total = len(results)

    header = [
        "# WhatsMyName Check Report",
        "",
        f"**Date:** {ts_str}  ",
        f"**Sites checked:** {sites_checked}  ",
        f"**Workers:** {workers}  ",
        "",
        "## Summary",
        "",
        "| Category | Count |",
        "|----------|-------|",
        f"| ✅ Correct | {len(cats['ok'])} |",
        f"| ⬇️ Site Down | {len(cats['site_down'])} |",
        f"| ❌ Bad e\\_code / e\\_string | {len(cats['bad_detection'])} |",
        f"| 👤 Bad known user | {len(cats['bad_known_user'])} |",
        f"| ❌ Bad m\\_code / m\\_string | {len(cats['bad_missing'])} |",
        f"| 🔒 Blocked | {len(cats['blocked'])} |",
        f"| 🔄 Other | {len(cats['other'])} |",
        f"| ⏭️ Skipped | {len(cats['skipped'])} |",
        f"| **Total** | **{total}** |",
        "",
        "## 🌐 Playwright Metrics",
        "",
        playwright_section(results),
        "",
        "---",
        "",
    ]

    sections = [
        ("1. Domains That Did Not Resolve",  "⬇️",
            "site_down",      dict(include_detection=False, include_checks=True)),
        ("2. Bad e\\_code or e\\_string",    "❌",
            "bad_detection",  dict(include_detection=True,  include_checks=True)),
        ("3. Bad Known User",               "👤",
            "bad_known_user", dict(include_detection=True,  include_checks=True)),
        ("4. Bad m\\_code or m\\_string",   "❌",
            "bad_missing",    dict(include_detection=True,  include_checks=True)),
        ("5. Blocked / CAPTCHA",            "🔒",
            "blocked",        dict(include_detection=False, include_checks=True)),
        ("6. Other",                        "🔄",
            "other",          dict(include_detection=True,  include_checks=True)),
        ("7. Sites That Checked Correctly", "✅",
            "ok",             dict(include_detection=False, include_checks=False, compact=True)),
        ("8. Skipped (valid:false)",        "⏭️",
            "skipped",        dict(include_detection=False, include_checks=False, compact=True)),
    ]

    body = []
    for title, emoji, key, kwargs in sections:
        body.append(render_section(title, emoji, cats[key], **kwargs))
        body.append("")

    return "\n".join(header) + "\n".join(body)


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WMN standalone checker — writes a dated markdown report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--limit",      type=int,  default=None,
                        help="Max number of sites to check")
    parser.add_argument("--workers",    type=int,  default=10,
                        help="Concurrent worker threads")
    parser.add_argument("--output-dir", type=Path, default=HERE,
                        help="Directory for the output .md file")
    parser.add_argument("--data",       type=Path, default=DEFAULT_DATA,
                        help="Path to wmn-data.json")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    sites = load_sites(args.data)
    if args.limit:
        sites = sites[: args.limit]

    print(f"Checking {len(sites)} sites with {args.workers} workers…")

    results: list = []
    progress: dict = {"total": 0, "done": 0, "complete": False, "running": False}
    lock = threading.Lock()

    run_checker(sites, results, lock, progress, max_workers=args.workers)

    ts = datetime.now(timezone.utc)
    ts_str = ts.strftime("%Y-%m-%d %H:%M UTC")
    filename = ts.strftime("%Y%m%d-%H%M-wmncheck.md")
    output_path = args.output_dir / filename

    cats = categorize(results)
    report = render_report(results, cats, ts_str, len(sites), args.workers)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    issues = len(results) - len(cats["ok"]) - len(cats["skipped"])
    pw_count = sum(1 for r in results if r.get("browser_used"))
    print(f"\n{'─' * 60}")
    print(f"  Report : {output_path}")
    print(f"  Checked: {_c(str(len(results)), 'bold')}")
    print(f"  OK     : {_c(str(len(cats['ok'])), 'green')}")
    print(f"  Issues : {_c(str(issues), 'red' if issues else 'green')}")
    print(f"  Down   : {_c(str(len(cats['site_down'])), 'gray')}")
    print(f"  Blocked: {_c(str(len(cats['blocked'])), 'purple')}")
    print(f"  Browser: {_c(str(pw_count), 'blue')} site(s) used Playwright")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    main()
