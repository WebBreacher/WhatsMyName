from dataclasses import dataclass, field
from typing import Optional, List

STATUS_OK = "ok"
STATUS_FALSE_POSITIVE = "false_positive"
STATUS_FALSE_NEGATIVE = "false_negative"
STATUS_SITE_DOWN = "site_down"
STATUS_BLOCKED = "blocked"
STATUS_E_CODE_MISMATCH = "e_code_mismatch"
STATUS_E_STRING_MISSING = "e_string_missing"
STATUS_M_CODE_MISMATCH = "m_code_mismatch"
STATUS_M_STRING_MISSING = "m_string_missing"
STATUS_SKIPPED = "skipped"

# Priority order for overall_status aggregation (highest priority first)
STATUS_PRIORITY = [
    STATUS_SITE_DOWN,
    STATUS_BLOCKED,
    STATUS_FALSE_POSITIVE,
    STATUS_FALSE_NEGATIVE,
    STATUS_E_CODE_MISMATCH,
    STATUS_E_STRING_MISSING,
    STATUS_M_CODE_MISMATCH,
    STATUS_M_STRING_MISSING,
    STATUS_OK,
    STATUS_SKIPPED,
]

PROTECTION_TYPES = [
    "anubis", "captcha", "cloudflare", "cloudfront",
    "ddos-guard", "multiple", "other", "user-agent", "user-auth",
]


@dataclass
class CheckDetail:
    username: str
    username_type: str          # 'known' or 'random'
    url: str
    method: str                 # 'GET' or 'POST'
    http_code: Optional[int]
    body_snippet: str           # first 500 chars of response body
    status: str
    note: str


@dataclass
class SiteResult:
    name: str
    cat: str
    uri_check: str
    uri_pretty: Optional[str]
    e_code: int
    e_string: str
    m_code: int
    m_string: str
    known: List[str]
    has_protection: bool
    protection: List[str]
    has_post_body: bool
    valid_field: Optional[bool]     # None = field absent in JSON
    checks: List[CheckDetail] = field(default_factory=list)
    overall_status: str = "pending"
    checked_at: str = ""   # ISO 8601 UTC timestamp set after each check
