import re
from datetime import datetime, timezone
from typing import Optional

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(html: Optional[str]) -> str:
    if not html:
        return ""
    text = _TAG_RE.sub(" ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp (with or without trailing Z) into an
    aware UTC datetime. Returns None on any parse failure."""
    if not value:
        return None
    try:
        v = value.strip()
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def parse_epoch_millis(value) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


_SALARY_RE = re.compile(
    r"\$\s?(\d{2,3}(?:,\d{3})?|\d{2,3}k)\s*(?:-|to|–)\s*\$?\s?(\d{2,3}(?:,\d{3})?|\d{2,3}k)",
    re.IGNORECASE,
)


def _to_int(token: str) -> int:
    token = token.strip().lower().replace(",", "")
    if token.endswith("k"):
        return int(float(token[:-1]) * 1000)
    return int(token)


def extract_salary_range(text: str):
    """Best-effort extraction of a $min-$max salary range from free text.
    Returns (min, max) ints, or (None, None) if nothing found."""
    if not text:
        return None, None
    match = _SALARY_RE.search(text)
    if not match:
        return None, None
    try:
        lo = _to_int(match.group(1))
        hi = _to_int(match.group(2))
        if lo > hi:
            lo, hi = hi, lo
        # Guard against nonsense (e.g. matching phone numbers/dates).
        if lo < 1000 or hi < 1000 or lo > 2_000_000 or hi > 2_000_000:
            return None, None
        return lo, hi
    except ValueError:
        return None, None
