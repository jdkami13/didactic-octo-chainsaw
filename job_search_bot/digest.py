from datetime import datetime, timezone
from typing import List

from .models import Job


def _fmt_salary(job: Job) -> str:
    if job.salary_min and job.salary_max:
        return f"${job.salary_min:,} - ${job.salary_max:,}"
    if job.salary_max:
        return f"up to ${job.salary_max:,}"
    if job.salary_min:
        return f"${job.salary_min:,}+"
    return "not listed"


def _fmt_date(job: Job) -> str:
    if job.posted_at is None:
        return "unknown"
    return job.posted_at.strftime("%Y-%m-%d %H:%M UTC")


def build_digest_text(jobs: List[Job]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"Job digest - generated {now}", "=" * 60]

    if not jobs:
        lines.append("No new matching postings found this run.")
        return "\n".join(lines)

    jobs_sorted = sorted(
        jobs, key=lambda j: j.posted_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True
    )

    lines.append(f"{len(jobs_sorted)} new matching posting(s):\n")
    for job in jobs_sorted:
        lines.append(f"- {job.company} | {job.title}")
        lines.append(f"  Salary: {_fmt_salary(job)}")
        lines.append(f"  Location: {job.location_text or 'not listed'}")
        lines.append(f"  Posted: {_fmt_date(job)}")
        lines.append(f"  Link: {job.url}")
        lines.append(f"  Source: {job.source}")
        lines.append("  Description:")
        # Adzuna in particular blocks scraping its site directly, so this
        # full text -- captured straight from the API response -- is the
        # only place to get the actual posting content after the fact; the
        # link alone is a dead end for that source.
        lines.append(f"    {job.description_text or 'not provided'}")
        lines.append("")

    return "\n".join(lines)
