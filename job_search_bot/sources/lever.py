"""Lever public postings API.

Docs: https://github.com/lever/postings-api
Endpoint: https://api.lever.co/v0/postings/{company}?mode=json
No auth required.
"""
import logging
from typing import Iterable, List

import requests

from ..models import Job
from ..util import parse_epoch_millis, strip_html, extract_salary_range

logger = logging.getLogger(__name__)

BASE_URL = "https://api.lever.co/v0/postings/{company}"
TIMEOUT = 20


def fetch_jobs(company_name: str, company_slug: str) -> List[Job]:
    url = BASE_URL.format(company=company_slug)
    try:
        resp = requests.get(url, params={"mode": "json"}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Lever fetch failed for %s (%s): %s", company_name, company_slug, exc)
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning("Lever returned non-JSON for %s", company_name)
        return []

    jobs = []
    for raw in data:
        categories = raw.get("categories") or {}
        location = categories.get("location", "") or ""
        workplace_type = raw.get("workplaceType", "") or ""
        location_text = f"{location} {workplace_type}".strip()

        description = strip_html(raw.get("descriptionPlain") or raw.get("description"))
        salary_min = salary_max = None
        salary_range = raw.get("salaryRange")
        if isinstance(salary_range, dict):
            salary_min = salary_range.get("min")
            salary_max = salary_range.get("max")
        if salary_min is None or salary_max is None:
            extracted_min, extracted_max = extract_salary_range(description)
            salary_min = salary_min or extracted_min
            salary_max = salary_max or extracted_max

        jobs.append(
            Job(
                source="lever",
                company=company_name,
                title=raw.get("text", ""),
                url=raw.get("hostedUrl", ""),
                location_text=location_text,
                posted_at=parse_epoch_millis(raw.get("createdAt")),
                salary_min=salary_min,
                salary_max=salary_max,
                description_text=description,
                external_id=str(raw.get("id", "")),
            )
        )
    return jobs


def fetch_all(companies: Iterable[tuple]) -> List[Job]:
    """companies: iterable of (display_name, company_slug) pairs."""
    jobs: List[Job] = []
    for name, slug in companies:
        jobs.extend(fetch_jobs(name, slug))
    return jobs
