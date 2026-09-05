"""Adzuna job search API (aggregator, free tier).

Docs: https://developer.adzuna.com/overview
Sign up for an app_id/app_key at https://developer.adzuna.com/
Endpoint: https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
"""
import logging
import os
from typing import Iterable, List, Optional

import requests

from ..models import Job
from ..util import parse_iso8601, strip_html, extract_salary_range

logger = logging.getLogger(__name__)

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
TIMEOUT = 20


def _credentials():
    app_id = os.environ.get("ADZUNA_APP_ID", "").strip()
    app_key = os.environ.get("ADZUNA_APP_KEY", "").strip()
    return app_id, app_key


def fetch_jobs(
    keyword: str,
    country: str = "us",
    max_days_old: int = 2,
    results_per_page: int = 50,
    app_id: Optional[str] = None,
    app_key: Optional[str] = None,
) -> List[Job]:
    app_id = app_id or os.environ.get("ADZUNA_APP_ID", "").strip()
    app_key = app_key or os.environ.get("ADZUNA_APP_KEY", "").strip()
    if not app_id or not app_key:
        logger.warning(
            "Adzuna credentials not set (ADZUNA_APP_ID / ADZUNA_APP_KEY) - skipping Adzuna search."
        )
        return []

    url = BASE_URL.format(country=country, page=1)
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": keyword,
        "max_days_old": max_days_old,
        "sort_by": "date",
        "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Adzuna fetch failed for keyword '%s': %s", keyword, exc)
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning("Adzuna returned non-JSON for keyword '%s'", keyword)
        return []

    jobs = []
    for raw in data.get("results", []):
        company = (raw.get("company") or {}).get("display_name", "Unknown")
        location = (raw.get("location") or {}).get("display_name", "") or ""
        description = strip_html(raw.get("description"))
        salary_min = raw.get("salary_min")
        salary_max = raw.get("salary_max")
        if not salary_min and not salary_max:
            salary_min, salary_max = extract_salary_range(description)

        jobs.append(
            Job(
                source="adzuna",
                company=company,
                title=raw.get("title", ""),
                url=raw.get("redirect_url", ""),
                location_text=location,
                posted_at=parse_iso8601(raw.get("created")),
                salary_min=int(salary_min) if salary_min else None,
                salary_max=int(salary_max) if salary_max else None,
                description_text=description,
                external_id=str(raw.get("id", "")),
            )
        )
    return jobs


def fetch_all(
    keywords: Iterable[str],
    country: str = "us",
    max_days_old: int = 2,
    results_per_page: int = 50,
) -> List[Job]:
    app_id, app_key = _credentials()
    if not app_id or not app_key:
        logger.warning(
            "Adzuna credentials not set (ADZUNA_APP_ID / ADZUNA_APP_KEY) - skipping Adzuna search."
        )
        return []

    jobs: List[Job] = []
    for keyword in keywords:
        jobs.extend(
            fetch_jobs(
                keyword,
                country=country,
                max_days_old=max_days_old,
                results_per_page=results_per_page,
                app_id=app_id,
                app_key=app_key,
            )
        )
    return jobs
