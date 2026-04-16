import json
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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
    timeout: int = 12,
) -> tuple:
    merged_headers = {"User-Agent": ua}
    merged_headers.update(site_headers)  # site headers take precedence

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
        return resp.status_code, resp.text[:2000]
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            OSError):
        return None, ""


def _evaluate_known_check(
    http_code: Optional[int], body: str, e_code: int, e_string: str
) -> tuple:
    if http_code is None:
        return STATUS_SITE_DOWN, "No response — site down or DNS failure"
    if detect_blocking(body, http_code):
        return STATUS_BLOCKED, f"Bot-blocking page detected (HTTP {http_code})"
    if http_code != e_code:
        return STATUS_E_CODE_MISMATCH, f"Expected HTTP {e_code}, got {http_code}"
    if e_string not in body:
        return STATUS_E_STRING_MISSING, f"e_string not found in response body (HTTP {http_code})"
    return STATUS_OK, f"Found: HTTP {http_code}, e_string present"


def _evaluate_random_check(
    http_code: Optional[int], body: str, e_string: str, m_code: int, m_string: str
) -> tuple:
    if http_code is None:
        return STATUS_SITE_DOWN, "No response — site down or DNS failure"
    if detect_blocking(body, http_code):
        return STATUS_BLOCKED, f"Bot-blocking page detected (HTTP {http_code})"
    if e_string and e_string in body:
        return STATUS_FALSE_POSITIVE, "Random username matched as found (false positive)"
    if m_code and http_code != m_code:
        return STATUS_M_CODE_MISMATCH, f"Expected m_code {m_code}, got {http_code}"
    if m_string and m_string not in body:
        return STATUS_M_STRING_MISSING, f"m_string not found in response body (HTTP {http_code})"
    return STATUS_OK, f"Not found as expected: HTTP {http_code}"


def _aggregate_status(checks: list) -> str:
    known_checks = [c for c in checks if c.username_type == "known"]
    random_checks = [c for c in checks if c.username_type == "random"]

    # If any known username passed, the site detection works — don't fail on a stale account
    known_statuses = {c.status for c in known_checks}
    any_known_ok = STATUS_OK in known_statuses

    # Random check statuses always count (false positive, m_code mismatch, etc.)
    random_statuses = {c.status for c in random_checks}

    # Site-down or blocked on all known checks overrides everything
    if known_checks and known_statuses <= {STATUS_SITE_DOWN}:
        return STATUS_SITE_DOWN
    if known_checks and known_statuses <= {STATUS_BLOCKED}:
        return STATUS_BLOCKED

    # If at least one known check passed, only surface random-check failures
    if any_known_ok:
        for priority_status in STATUS_PRIORITY:
            if priority_status in random_statuses and priority_status not in (STATUS_OK,):
                return priority_status
        return STATUS_OK

    # All known checks failed — surface worst known failure, then random failures
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
    )

    if valid_field is False:
        result.overall_status = STATUS_SKIPPED
        return result

    site_headers = site.get("headers", {})

    with requests.Session() as session:
        # Test all known usernames — one may be stale while others still work
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
                body_snippet=body,
                status=status,
                note=note,
            ))

            # Stop on site-down to avoid redundant timeouts
            if status == STATUS_SITE_DOWN:
                break

        # Test random username (false positive detection)
        random_username = generate_random_username()
        random_username = apply_strip_bad_char(random_username, strip_chars)
        url = site["uri_check"].replace("{account}", random_username)
        post_body_str = post_body_template.replace("{account}", random_username) if post_body_template else None

        # Skip random check if site already confirmed down
        known_statuses = {c.status for c in result.checks}
        if STATUS_SITE_DOWN not in known_statuses:
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
                body_snippet=body,
                status=status,
                note=note,
            ))

    result.overall_status = _aggregate_status(result.checks)
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

    selected_uas = random.sample(UA_POOL, 2)
    ua_assignments = {i: selected_uas[i % 2] for i in range(len(sites))}

    progress["total"] = len(sites)
    progress["done"] = 0
    progress["complete"] = False
    progress["running"] = True

    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, site in enumerate(sites):
            future = executor.submit(check_site, site, ua_assignments[i])
            futures[future] = site["name"]

        for future in as_completed(futures):
            site_name = futures[future]
            try:
                result = future.result()
            except Exception as exc:
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
                        note=f"Exception: {exc}",
                    )],
                )

            result_dict = asdict(result)
            with lock:
                for i, r in enumerate(results_list):
                    if r["name"] == result_dict["name"]:
                        results_list[i] = result_dict
                        break
                else:
                    results_list.append(result_dict)
                progress["done"] += 1

    with lock:
        progress["complete"] = True
        progress["running"] = False


def load_sites(data_file: Path) -> list:
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    sites = data.get("sites", [])
    return [s for s in sites if s.get("valid") is not False]
