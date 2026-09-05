from unittest.mock import patch, MagicMock

import requests

from job_search_bot.sources import adzuna, ashby, greenhouse, lever


def _mock_response(json_data, status_ok=True):
    resp = MagicMock()
    resp.json.return_value = json_data
    if status_ok:
        resp.raise_for_status.return_value = None
    else:
        resp.raise_for_status.side_effect = Exception("boom")
    return resp


def test_greenhouse_parses_jobs():
    payload = {
        "jobs": [
            {
                "id": 123,
                "title": "Marketing Manager, Retention",
                "absolute_url": "https://boards.greenhouse.io/testco/jobs/123",
                "updated_at": "2026-09-05T10:00:00Z",
                "location": {"name": "Remote"},
                "content": "<p>Salary: $100,000 - $120,000</p>",
            }
        ]
    }
    with patch("job_search_bot.sources.greenhouse.requests.get", return_value=_mock_response(payload)):
        jobs = greenhouse.fetch_jobs("TestCo", "testco")
    assert len(jobs) == 1
    job = jobs[0]
    assert job.company == "TestCo"
    assert job.title == "Marketing Manager, Retention"
    assert job.salary_min == 100_000
    assert job.salary_max == 120_000
    assert job.source == "greenhouse"


def test_greenhouse_handles_request_failure_gracefully():
    with patch(
        "job_search_bot.sources.greenhouse.requests.get",
        side_effect=requests.exceptions.ConnectionError("network down"),
    ):
        jobs = greenhouse.fetch_jobs("TestCo", "testco")
    assert jobs == []


def test_lever_parses_jobs():
    payload = [
        {
            "id": "abc",
            "text": "Director, Email Marketing",
            "hostedUrl": "https://jobs.lever.co/testco/abc",
            "createdAt": 1893456000000,
            "categories": {"location": "New York City"},
            "workplaceType": "hybrid",
            "descriptionPlain": "Lead our email marketing manager team.",
            "salaryRange": {"min": 95000, "max": 130000},
        }
    ]
    with patch("job_search_bot.sources.lever.requests.get", return_value=_mock_response(payload)):
        jobs = lever.fetch_jobs("TestCo", "testco")
    assert len(jobs) == 1
    job = jobs[0]
    assert job.salary_min == 95000
    assert job.salary_max == 130000
    assert "New York City" in job.location_text
    assert "hybrid" in job.location_text


def test_ashby_parses_jobs():
    payload = {
        "jobs": [
            {
                "id": "xyz",
                "title": "Marketing Operations Manager",
                "jobUrl": "https://jobs.ashbyhq.com/testco/xyz",
                "publishedAt": "2026-09-05T08:00:00.000Z",
                "location": "Remote - US",
                "isRemote": True,
                "descriptionHtml": "<p>Own our lifecycle marketing stack.</p>",
                "compensation": {"compensationTierSummary": "$90,000 - $110,000"},
            }
        ]
    }
    with patch("job_search_bot.sources.ashby.requests.get", return_value=_mock_response(payload)):
        jobs = ashby.fetch_jobs("TestCo", "testco")
    assert len(jobs) == 1
    job = jobs[0]
    assert job.salary_min == 90_000
    assert job.salary_max == 110_000
    assert "Remote" in job.location_text


def test_adzuna_skips_without_credentials(monkeypatch):
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    jobs = adzuna.fetch_all(["lifecycle marketing"])
    assert jobs == []


def test_adzuna_parses_jobs(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "id123")
    monkeypatch.setenv("ADZUNA_APP_KEY", "key123")
    payload = {
        "results": [
            {
                "id": "999",
                "title": "CRM Marketing Manager",
                "company": {"display_name": "SomeCo"},
                "location": {"display_name": "New York, NY"},
                "redirect_url": "https://example.com/job/999",
                "created": "2026-09-05T09:00:00Z",
                "salary_min": 95000,
                "salary_max": 115000,
                "description": "Own CRM marketing lifecycle programs.",
            }
        ]
    }
    with patch("job_search_bot.sources.adzuna.requests.get", return_value=_mock_response(payload)):
        jobs = adzuna.fetch_all(["crm marketing"])
    assert len(jobs) == 1
    job = jobs[0]
    assert job.company == "SomeCo"
    assert job.salary_min == 95000
    assert job.salary_max == 115000
