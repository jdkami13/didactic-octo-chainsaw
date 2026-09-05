from datetime import datetime, timezone

from job_search_bot.digest import build_digest_text
from job_search_bot.models import Job


def make_job(**overrides) -> Job:
    defaults = dict(
        source="adzuna",
        company="TestCo",
        title="Senior Manager, Lifecycle Marketing",
        url="https://example.com/job/1",
        location_text="Remote",
        posted_at=datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc),
        salary_min=95_000,
        salary_max=110_000,
        description_text="Own our lifecycle marketing and CRM programs end to end.",
    )
    defaults.update(overrides)
    return Job(**defaults)


def test_digest_includes_full_description_text():
    job = make_job(description_text="A" * 2000)  # long description, must not be truncated
    text = build_digest_text([job])
    assert "Description:" in text
    assert "A" * 2000 in text


def test_digest_handles_missing_description():
    job = make_job(description_text="")
    text = build_digest_text([job])
    assert "Description:" in text
    assert "not provided" in text


def test_empty_digest_has_no_description_section():
    text = build_digest_text([])
    assert "Description:" not in text
