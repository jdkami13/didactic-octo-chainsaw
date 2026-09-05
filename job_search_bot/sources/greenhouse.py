"""Greenhouse public job board API.

Docs: https://developers.greenhouse.io/job-board.html
Endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
No auth required.
"""
import logging
from typing import Iterable, List

import requests

from ..models import Job
from ..util import parse_iso8601, strip_html, extract_salary_range

logger = logging.getLogger(__name__)

BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
TIMEOUT = 20


def fetch_jobs(company_name: str, board_token: str) -> List[Job]:
    url = BASE_URL.format(token=board_token)
    try:
        resp = requests.get(url, params={"content": "true"}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Greenhouse fetch failed for %s (%s): %s", company_name, board_token, exc)
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning("Greenhouse returned non-JSON for %s", company_name)
        return []

    jobs = []
    for raw in data.get("jobs", []):
        description = strip_html(raw.get("content"))
        salary_min, salary_max = extract_salary_range(description)
        location_name = (raw.get("location") or {}).get("name", "")
        jobs.append(
            Job(
                source="greenhouse",
                company=company_name,
                title=raw.get("title", ""),
                url=raw.get("absolute_url", ""),
                location_text=location_name,
                posted_at=parse_iso8601(raw.get("updated_at")),
                salary_min=salary_min,
                salary_max=salary_max,
                description_text=description,
                external_id=str(raw.get("id", "")),
            )
        )
    return jobs


def fetch_all(companies: Iterable[tuple]) -> List[Job]:
    """companies: iterable of (display_name, board_token) pairs."""
    jobs: List[Job] = []
    for name, token in companies:
        jobs.extend(fetch_jobs(name, token))
    return jobs
