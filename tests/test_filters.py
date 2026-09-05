from datetime import datetime, timedelta, timezone

from job_search_bot.filters import passes_all_filters
from job_search_bot.models import Job


def make_job(**overrides) -> Job:
    defaults = dict(
        source="greenhouse",
        company="TestCo",
        title="Senior Manager, Lifecycle Marketing",
        url="https://example.com/job/1",
        location_text="Remote",
        posted_at=datetime.now(timezone.utc) - timedelta(hours=5),
        salary_min=95_000,
        salary_max=110_000,
        salary_text="",
        description_text="Own our lifecycle marketing and CRM programs.",
    )
    defaults.update(overrides)
    return Job(**defaults)


def test_matching_job_passes():
    assert passes_all_filters(make_job()) is True


def test_wrong_keyword_fails():
    job = make_job(
        title="Senior Manager, Paid Social",
        description_text="Run our paid social advertising campaigns.",
    )
    assert passes_all_filters(job) is False


def test_associate_title_excluded():
    job = make_job(title="Marketing Associate, Lifecycle")
    assert passes_all_filters(job) is False


def test_specialist_title_excluded():
    job = make_job(title="Retention Marketing Specialist")
    assert passes_all_filters(job) is False


def test_individual_contributor_without_level_word_excluded():
    job = make_job(title="Lifecycle Marketing Lead")
    assert passes_all_filters(job) is False


def test_non_remote_non_nyc_location_fails():
    job = make_job(location_text="Austin, TX")
    assert passes_all_filters(job) is False


def test_nyc_hybrid_location_passes():
    job = make_job(location_text="Hybrid - New York, NY")
    assert passes_all_filters(job) is True


def test_bronx_location_passes():
    job = make_job(location_text="Hybrid - Bronx, NY")
    assert passes_all_filters(job) is True


def test_description_mentioning_remote_does_not_leak_into_location_match():
    # Regression test: a real posting for a Michigan-based role slipped
    # through because its description happened to mention "remote"
    # somewhere, even though the actual location field was nowhere near
    # NYC or remote-eligible. Only job.location_text should count.
    job = make_job(
        location_text="Cascade, Kent County, MI",
        description_text="This role is not eligible for remote work; onsite in our Michigan office.",
    )
    assert passes_all_filters(job) is False


def test_salary_below_floor_fails():
    job = make_job(salary_min=60_000, salary_max=75_000)
    assert passes_all_filters(job) is False


def test_missing_salary_does_not_exclude():
    job = make_job(salary_min=None, salary_max=None)
    assert passes_all_filters(job) is True


def test_stale_posting_fails():
    job = make_job(posted_at=datetime.now(timezone.utc) - timedelta(hours=72))
    assert passes_all_filters(job) is False


def test_missing_posted_at_does_not_exclude():
    job = make_job(posted_at=None)
    assert passes_all_filters(job) is True
