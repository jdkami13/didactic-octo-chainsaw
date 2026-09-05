# Job Search Bot

Searches public job-board APIs for new postings matching your criteria and
writes a digest for you to review. No scraping — only official APIs.

**Sources:**
- [Greenhouse](https://developers.greenhouse.io/job-board.html) job board API (per company)
- [Lever](https://github.com/lever/postings-api) postings API (per company)
- [Ashby](https://developers.ashbyhq.com/reference/jobpostingapi) job board API (per company)
- [Adzuna](https://developer.adzuna.com/) aggregator search API (free tier, needs an API key)

**Default filter criteria** (edit in `job_search_bot/config.py`):
- Keywords: lifecycle marketing, CRM marketing, retention marketing, email
  marketing manager, marketing operations
- Level: Manager / Senior Manager / Director (excludes Associate,
  Coordinator, Specialist, Intern, Assistant titles)
- Location: Remote, or hybrid mentioning NYC/Bronx
- Salary: $90K+ where a salary is actually listed (jobs with no listed
  salary aren't excluded)
- Posted within the last 48 hours (configurable)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 1. Configure companies

Edit `job_search_bot/config.py`:

- `GREENHOUSE_COMPANIES` / `LEVER_COMPANIES` / `ASHBY_COMPANIES` are
  `{"Display Name": "board-token-or-slug"}` dicts. To find a company's
  token/slug: open their careers page and look at the URL
  (`https://boards.greenhouse.io/<token>`, `https://jobs.lever.co/<slug>`,
  `https://jobs.ashbyhq.com/<name>`), or open browser dev tools → Network
  tab and look for the API request while the careers page loads.
- **I pre-filled a starter list for BARK, Little Spoon, PuppySpot,
  Change.org, and Peloton under Greenhouse, but this sandboxed environment
  has no outbound internet access, so I could not verify these tokens
  against the live APIs.** `peloton` is Peloton's real Greenhouse token;
  treat the rest as guesses to confirm yourself. A wrong token just returns
  zero results for that company — it won't error out the whole run — so
  it's safe to leave as-is while you verify, but check each company's
  actual careers page and ATS (some of these companies may not use
  Greenhouse at all, in which case move them to the Lever or Ashby dict
  instead, or drop them if they use something else entirely).

### 2. Get an Adzuna API key (free)

1. Go to https://developer.adzuna.com/ and click "Register" (or "Get started").
2. Confirm your email, then go to your dashboard to find your **App ID**
   and **App Key**.
3. Put them in `.env`:
   ```
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```
   The free tier covers a generous number of calls/month — plenty for a
   daily/hourly personal search script. If you skip this, the script just
   logs a warning and continues without the Adzuna results.

### 3. Run it

```bash
python -m job_search_bot.main
```

This prints the digest to the console and also saves it to
`digests/digest_<timestamp>.txt`. It keeps a `seen_jobs.json` cache so that
re-running the script only shows postings you haven't seen yet (matched by
source + company + job ID). Useful flags:

```bash
python -m job_search_bot.main --no-cache   # show everything that matches filters, ignore dedup history
python -m job_search_bot.main --quiet      # only write the file, don't print to console
```

### 4. Run the tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

The test suite mocks all HTTP calls (no live network needed) and covers the
filter logic and each source's response parsing.

## Running on a schedule

### Cron (Linux/macOS)

Edit your crontab:

```bash
crontab -e
```

Add a line to run it every 4 hours (adjust the schedule to taste — the
recency filter is 48h by default so running less often than that is fine
too):

```cron
0 */4 * * * cd /path/to/didactic-octo-chainsaw && /path/to/didactic-octo-chainsaw/.venv/bin/python -m job_search_bot.main --quiet >> /path/to/didactic-octo-chainsaw/cron.log 2>&1
```

Notes:
- Use the **absolute path** to the venv's Python interpreter and to the
  project directory — cron doesn't source your shell profile, so relative
  paths and `source .venv/bin/activate` won't work.
- `--quiet` avoids cluttering the log with the full digest text (it's
  already saved to `digests/`); drop it if you'd rather see it in the log.
- Cron doesn't load `.env` for you, but `python-dotenv` (used in
  `main.py`) reads it directly from the project directory at startup, so
  no extra cron config is needed for the Adzuna credentials.

### macOS alternative: launchd

If cron is disabled on your Mac, use a launchd plist instead — same idea,
different scheduler. Let me know if you'd like one written out.

## Project layout

```
job_search_bot/
  config.py       # companies, keywords, filter thresholds — edit this
  models.py        # the normalized Job record
  filters.py        # keyword/level/location/salary/recency filters
  digest.py        # formats the text digest
  seen_cache.py       # tracks which jobs you've already been shown
  sources/
    greenhouse.py
    lever.py
    ashby.py
    adzuna.py
  main.py          # orchestrates everything, CLI entrypoint
tests/           # pytest suite, HTTP calls mocked
```
