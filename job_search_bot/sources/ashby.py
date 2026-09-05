"""Ashby public job board API.

Docs: https://developers.ashbyhq.com/reference/jobpostingapi
Endpoint: https://api.ashbyhq.com/posting-api/job-board/{board_name}?includeCompensation=true
No auth required.
"""
import logging
from typing import Iterable, List

import requests

from ..models import Job
from ..util import parse_iso8601, strip_html, extract_salary_range

logger = logging.getLogger(__name__)

BASE_URL = "https://api.ashbyhq.com/posting-api/job-board/{board_name}"
TIMEOUT = 20


def fetch_jobs(company_name: str, board_name: str) -> List[Job]:
    url = BASE_URL.format(board_name=board_name)
    try:
        resp = requests.get(url, params={"includeCompensation": "true"}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Ashby fetch failed for %s (%s): %s", company_name, board_name, exc)
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning("Ashby returned non-JSON for %s", company_name)
        return []

    jobs = []
    for raw in data.get("jobs", []):
        location = raw.get("location", "") or ""
        if raw.get("isRemote"):
            location = f"{location} Remote".strip()

        description = strip_html(raw.get("descriptionHtml") or raw.get("descriptionPlain"))

        salary_min = salary_max = None
        compensation = raw.get("compensation") or {}
        salary_text = compensation.get("compensationTierSummary", "") or ""
        salary_min, salary_max = extract_salary_range(salary_text or description)

        jobs.append(
            Job(
                source="ashby",
                company=company_name,
                title=raw.get("title", ""),
                url=raw.get("jobUrl", "") or raw.get("applyUrl", ""),
                location_text=location,
                posted_at=parse_iso8601(raw.get("publishedAt") or raw.get("updatedAt")),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_text=salary_text,
                description_text=description,
                external_id=str(raw.get("id", "")),
            )
        )
    return jobs


def fetch_all(companies: Iterable[tuple]) -> List[Job]:
    """companies: iterable of (display_name, board_name) pairs."""
    jobs: List[Job] = []
    for name, board_name in companies:
        jobs.extend(fetch_jobs(name, board_name))
    return jobs
