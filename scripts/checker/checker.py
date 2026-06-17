import functools
import json
import logging
import random
import shutil
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger("wmn")

import requests
import requests.exceptions

from models import (
    CheckDetail, SiteResult,
    STATUS_OK, STATUS_FALSE_POSITIVE, STATUS_SITE_DOWN, STATUS_BLOCKED,
    STATUS_E_CODE_MISMATCH, STATUS_E_STRING_MISSING,
    STATUS_M_CODE_MISMATCH, STATUS_M_STRING_MISSING,
    STATUS_SKIPPED, STATUS_PRIORITY,
)

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

BLOCKING_SIGNALS = [
    "cloudflare", "cf-ray", "just a moment", "ddos-guard",
    "captcha", "access denied", "enable javascript", "checking your browser",
]

# Statuses from the requests pass that warrant a Playwright retry
PLAYWRIGHT_RETRY_STATUSES = {
    STATUS_BLOCKED,
    STATUS_FALSE_POSITIVE,
    STATUS_E_STRING_MISSING,
    STATUS_M_STRING_MISSING,
    STATUS_E_CODE_MISMATCH,
    STATUS_M_CODE_MISMATCH,
}

_CHROMIUM_CANDIDATES = [
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
]

# Playwright's sync API is not thread-safe; serialize all browser launches
_playwright_lock = threading.Lock()

_stop_event = threading.Event()


def request_stop() -> None:
    _stop_event.set()
    log.info("Stop requested")


@functools.lru_cache(maxsize=1)
def _find_chromium() -> Optional[str]:
    for path in _CHROMIUM_CANDIDATES:
        if Path(path).exists():
            return path
    return (
        shutil.which("chromium-browser")
        or shutil.which("chromium")
        or shutil.which("google-chrome")
    )


@functools.lru_cache(maxsize=1)
def _playwright_available() -> bool:
    """Check once at startup whether Playwright + a Chromium binary are usable."""
    try:
        import playwright  # noqa: F401
        path = _find_chromium()
        if path:
            log.info("Playwright available — chromium: %s", path)
            return True
        log.info("Playwright installed but no Chromium binary found — browser fallback disabled")
        return False
    except Exception as exc:
        log.warning("Playwright not available (%s: %s) — browser fallback disabled",
                    type(exc).__name__, exc)
        return False


def generate_random_username() -> str:
    length = random.randint(8, 12)
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def apply_strip_bad_char(username: str, chars: str) -> str:
    if not chars:
        return username
    return username.translate(str.maketrans("", "", chars))


def detect_blocking(body: str, code: int) -> bool:
    body_lower = body.lower()
    return any(signal in body_lower for signal in BLOCKING_SIGNALS)


def do_request(
    session: requests.Session,
    url: str,
    method: str,
    site_headers: dict,
    post_body_str: Optional[str],
    ua: str,
    timeout: int = 60,
) -> tuple:
    merged_headers = {"User-Agent": ua}
    merged_headers.update(site_headers)

    try:
        if method == "POST":
            resp = session.post(
                url,
                data=post_body_str,
                headers=merged_headers,
                timeout=timeout,
                allow_redirects=False,
            )
        else:
            resp = session.get(
                url,
                headers=merged_headers,
                timeout=timeout,
                allow_redirects=False,
            )
        return resp.status_code, resp.text
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            OSError):
        return None, ""


def _fetch_via_playwright(
    url: str,
    method: str,
    post_body_str: Optional[str],
    site_headers: dict,
    timeout: int,
) -> tuple:
    """Fetch a URL using headless Chromium. Returns (http_code, body)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, ""

    chromium = _find_chromium()
    if not chromium:
        return None, ""

    timeout_ms = timeout * 1000
    try:
        with _playwright_lock:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=chromium,
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                try:
                    ctx = browser.new_context(
                        user_agent=random.choice(UA_POOL),
                        extra_http_headers=site_headers,
                    )
                    if method == "POST":
                        resp = ctx.request.post(url, data=post_body_str or "", timeout=timeout_ms)
                        return resp.status, resp.text()
                    else:
                        page = ctx.new_page()
                        try:
                            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                            try:
                                page.wait_for_load_state("networkidle", timeout=5000)
                            except Exception:
                                pass
                            content = page.content()
                            return (response.status if response else None), content
                        finally:
                            page.close()
                finally:
                    browser.close()
    except Exception:
        return None, ""


def _run_browser_checks(
    site: dict,
    strip_chars: str,
    post_body_template: Optional[str],
    method: str,
    site_headers: dict,
    e_code: int,
    e_string: str,
    m_code: int,
    m_string: str,
    known_usernames: list,
    timeout: int = 60,
) -> list:
    """Run known + random checks via Playwright. Returns list of CheckDetail."""
    checks = []

    for username in known_usernames:
        username = apply_strip_bad_char(username, strip_chars)
        url = site["uri_check"].replace("{account}", username)
        post_body_str = post_body_template.replace("{account}", username) if post_body_template else None

        http_code, body = _fetch_via_playwright(url, method, post_body_str, site_headers, timeout)
        status, note = _evaluate_known_check(http_code, body, e_code, e_string)
        checks.append(CheckDetail(
            username=username,
            username_type="known",
            url=url,
            method=method,
            http_code=http_code,
            body_snippet=body[:2000],
            status=status,
            note=f"[browser] {note}",
        ))
        if status == STATUS_SITE_DOWN:
            break

    known_statuses = {c.status for c in checks}
    if STATUS_SITE_DOWN not in known_statuses:
        random_username = generate_random_username()
        random_username = apply_strip_bad_char(random_username, strip_chars)
        url = site["uri_check"].replace("{account}", random_username)
        post_body_str = post_body_template.replace("{account}", random_username) if post_body_template else None

        http_code, body = _fetch_via_playwright(url, method, post_body_str, site_headers, timeout)
        status, note = _evaluate_random_check(http_code, body, e_string, m_code, m_string)
        checks.append(CheckDetail(
            username=random_username,
            username_type="random",
            url=url,
            method=method,
            http_code=http_code,
            body_snippet=body[:2000],
            status=status,
            note=f"[browser] {note}",
        ))

    return checks


def _evaluate_known_check(
    http_code: Optional[int], body: str, e_code: int, e_string: str
) -> tuple:
    if http_code is None:
        return STATUS_SITE_DOWN, "No response — site down or DNS failure"
    if http_code == e_code and e_string in body:
        return STATUS_OK, f"Found: HTTP {http_code}, e_string present"
    if detect_blocking(body, http_code):
        return STATUS_BLOCKED, f"Bot-blocking page detected (HTTP {http_code})"
    if http_code != e_code:
        return STATUS_E_CODE_MISMATCH, f"Expected HTTP {e_code}, got {http_code}"
    return STATUS_E_STRING_MISSING, f"e_string not found in response body (HTTP {http_code})"


def _evaluate_random_check(
    http_code: Optional[int], body: str, e_string: str, m_code: int, m_string: str
) -> tuple:
    if http_code is None:
        return STATUS_SITE_DOWN, "No response — site down or DNS failure"
    if m_code and http_code == m_code and m_string and m_string in body:
        return STATUS_OK, f"Not found as expected: HTTP {http_code}"
    if e_string and e_string in body:
        return STATUS_FALSE_POSITIVE, "Random username matched as found (false positive)"
    if detect_blocking(body, http_code):
        return STATUS_BLOCKED, f"Bot-blocking page detected (HTTP {http_code})"
    if m_code and http_code != m_code:
        return STATUS_M_CODE_MISMATCH, f"Expected m_code {m_code}, got {http_code}"
    if m_string and m_string not in body:
        return STATUS_M_STRING_MISSING, f"m_string not found in response body (HTTP {http_code})"
    return STATUS_OK, f"Not found as expected: HTTP {http_code}"


def _aggregate_status(checks: list) -> str:
    known_checks = [c for c in checks if c.username_type == "known"]
    random_checks = [c for c in checks if c.username_type == "random"]

    known_statuses = {c.status for c in known_checks}
    any_known_ok = STATUS_OK in known_statuses
    random_statuses = {c.status for c in random_checks}

    if known_checks and known_statuses <= {STATUS_SITE_DOWN}:
        return STATUS_SITE_DOWN
    if known_checks and known_statuses <= {STATUS_BLOCKED}:
        return STATUS_BLOCKED

    if any_known_ok:
        for priority_status in STATUS_PRIORITY:
            if priority_status in random_statuses and priority_status not in (STATUS_OK,):
                return priority_status
        return STATUS_OK

    all_statuses = known_statuses | random_statuses
    for priority_status in STATUS_PRIORITY:
        if priority_status in all_statuses:
            return priority_status
    return STATUS_OK


def check_site(site: dict, ua: str) -> SiteResult:
    valid_field = site.get("valid", None)
    protection = site.get("protection", [])
    post_body_template = site.get("post_body")
    method = "POST" if post_body_template else "GET"
    strip_chars = site.get("strip_bad_char", "")
    site_headers = site.get("headers", {})

    result = SiteResult(
        name=site["name"],
        cat=site.get("cat", ""),
        uri_check=site["uri_check"],
        uri_pretty=site.get("uri_pretty"),
        e_code=site["e_code"],
        e_string=site["e_string"],
        m_code=site["m_code"],
        m_string=site["m_string"],
        known=site.get("known", []),
        has_protection=bool(protection),
        protection=protection,
        has_post_body=bool(post_body_template),
        valid_field=valid_field,
        strip_bad_char=strip_chars,
        post_body=post_body_template or "",
        headers=site_headers,
    )

    if valid_field is False:
        result.overall_status = STATUS_SKIPPED
        return result

    # --- Phase 1: fast requests-based check ---
    with requests.Session() as session:
        for username in result.known:
            username = apply_strip_bad_char(username, strip_chars)
            url = site["uri_check"].replace("{account}", username)
            post_body_str = post_body_template.replace("{account}", username) if post_body_template else None

            http_code, body = do_request(session, url, method, site_headers, post_body_str, ua)
            status, note = _evaluate_known_check(http_code, body, result.e_code, result.e_string)

            result.checks.append(CheckDetail(
                username=username,
                username_type="known",
                url=url,
                method=method,
                http_code=http_code,
                body_snippet=body[:2000],
                status=status,
                note=note,
            ))

            if status == STATUS_SITE_DOWN:
                break

        known_statuses = {c.status for c in result.checks}
        if STATUS_SITE_DOWN not in known_statuses:
            random_username = generate_random_username()
            random_username = apply_strip_bad_char(random_username, strip_chars)
            url = site["uri_check"].replace("{account}", random_username)
            post_body_str = post_body_template.replace("{account}", random_username) if post_body_template else None

            http_code, body = do_request(session, url, method, site_headers, post_body_str, ua)
            status, note = _evaluate_random_check(
                http_code, body, result.e_string, result.m_code, result.m_string
            )
            result.checks.append(CheckDetail(
                username=random_username,
                username_type="random",
                url=url,
                method=method,
                http_code=http_code,
                body_snippet=body[:2000],
                status=status,
                note=note,
            ))

    result.overall_status = _aggregate_status(result.checks)
    result.requests_status = result.overall_status   # snapshot before any browser override

    # --- Phase 2: Playwright fallback for inconclusive results ---
    if result.overall_status in PLAYWRIGHT_RETRY_STATUSES and _playwright_available():
        log.info("  %-40s %s → retrying with browser", site["name"], result.overall_status)
        browser_checks = _run_browser_checks(
            site, strip_chars, post_body_template, method, site_headers,
            result.e_code, result.e_string, result.m_code, result.m_string,
            result.known,
        )
        if browser_checks:
            result.checks = browser_checks
            result.overall_status = _aggregate_status(result.checks)
            result.browser_used = True
            log.info("  %-40s %s (browser)", site["name"], result.overall_status)

    result.checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return result


def run_checker(
    sites: list,
    results_list: list,
    lock: threading.Lock,
    progress: dict,
    max_workers: int = 10,
    limit: Optional[int] = None,
) -> None:
    if limit and limit > 0:
        sites = sites[:limit]

    _stop_event.clear()

    selected_uas = random.sample(UA_POOL, 2)
    ua_assignments = {i: selected_uas[i % 2] for i in range(len(sites))}

    progress["total"] = len(sites)
    progress["done"] = 0
    progress["complete"] = False
    progress["running"] = True

    log.info("Checker started: %d sites, %d workers", len(sites), max_workers)
    futures = {}
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        for i, site in enumerate(sites):
            future = executor.submit(check_site, site, ua_assignments[i])
            futures[future] = site["name"]

        for future in as_completed(futures):
            if _stop_event.is_set():
                for f in futures:
                    f.cancel()
                log.info("Checker stopped by user (%d/%d done)", progress["done"], progress["total"])
                break

            site_name = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                log.error("  EXCEPTION [%s]: %s: %s", site_name, type(exc).__name__, exc, exc_info=True)
                result = SiteResult(
                    name=site_name, cat="", uri_check="", uri_pretty=None,
                    e_code=0, e_string="", m_code=0, m_string="",
                    known=[], has_protection=False, protection=[],
                    has_post_body=False, valid_field=None,
                    overall_status=STATUS_SITE_DOWN,
                    checks=[CheckDetail(
                        username="", username_type="known", url="",
                        method="GET", http_code=None,
                        body_snippet="", status=STATUS_SITE_DOWN,
                        note=f"Exception: {type(exc).__name__}: {exc}",
                    )],
                )

            result_dict = asdict(result)
            log.info("  [%d/%d] %-40s %s",
                     progress["done"] + 1, progress["total"],
                     result_dict["name"], result_dict["overall_status"])
            with lock:
                for j, r in enumerate(results_list):
                    if r["name"] == result_dict["name"]:
                        results_list[j] = result_dict
                        break
                else:
                    results_list.append(result_dict)
                progress["done"] += 1
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    log.info("Checker finished: %d/%d sites processed", progress["done"], progress["total"])
    with lock:
        progress["complete"] = True
        progress["running"] = False


def load_sites(data_file: Path) -> list:
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    sites = data.get("sites", [])
    return [s for s in sites if s.get("valid") is not False]
