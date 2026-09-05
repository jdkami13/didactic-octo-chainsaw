from datetime import datetime, timedelta, timezone
from typing import List

from . import config
from .models import Job


def _contains_any(haystack: str, needles: List[str]) -> bool:
    haystack = (haystack or "").lower()
    return any(needle.lower() in haystack for needle in needles)


def matches_keywords(job: Job) -> bool:
    combined = f"{job.title} {job.description_text}"
    return _contains_any(combined, config.KEYWORDS)


def matches_level(job: Job) -> bool:
    title = job.title or ""
    if _contains_any(title, config.LEVEL_EXCLUDE):
        return False
    return _contains_any(title, config.LEVEL_INCLUDE)


def matches_location(job: Job) -> bool:
    location = f"{job.location_text} {job.description_text[:500]}"
    if _contains_any(location, config.REMOTE_KEYWORDS):
        return True
    return _contains_any(location, config.NYC_KEYWORDS)


def matches_salary(job: Job) -> bool:
    # If no salary is listed at all, don't exclude the job -- brief says
    # "$90K+ where listed", i.e. only enforce the floor when we have data.
    if job.salary_min is None and job.salary_max is None:
        return True
    best_known = job.salary_max if job.salary_max is not None else job.salary_min
    return best_known >= config.MIN_SALARY


def matches_recency(job: Job, max_age_hours: int = None) -> bool:
    max_age_hours = max_age_hours if max_age_hours is not None else config.MAX_POSTING_AGE_HOURS
    if job.posted_at is None:
        # Unknown posting date -- keep it rather than silently dropping it;
        # let the human reviewer judge it.
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    return job.posted_at >= cutoff


def passes_all_filters(job: Job) -> bool:
    return (
        matches_keywords(job)
        and matches_level(job)
        and matches_location(job)
        and matches_salary(job)
        and matches_recency(job)
    )


def filter_jobs(jobs: List[Job]) -> List[Job]:
    return [job for job in jobs if passes_all_filters(job)]
