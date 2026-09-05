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
- **Verified via web search against live Greenhouse posting URLs:**
  Peloton (`peloton`), BARK (`bark`), Little Spoon (`littlespoon`), and
  Change.org (`changeorg58` — note this one is *not* the more obvious
  `changeorg`, an earlier version of this file had that guess wrong).
  These four are pre-filled in `GREENHOUSE_COMPANIES`.
- **PuppySpot could not be confirmed on Greenhouse, Lever, or Ashby.**
  Their public job board runs on a service called
  [Consider](https://consider.com/boards/co/puppyspot), which this script
  doesn't integrate with, so they're left out of `config.py` entirely
  rather than guessing a token that would silently return nothing. If you
  find their actual underlying ATS, add them to the matching dict.
- Tokens can go stale if a company migrates ATS providers — a wrong/old
  token just returns zero results for that company, it won't error out the
  whole run, but it's worth spot-checking periodically.

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

### 3. Email delivery (optional)

If you'd rather get the digest in your inbox than check a file/console
output, add three more values to `.env`:

```
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_16_character_app_password
EMAIL_TO=you@gmail.com
```

For Gmail, `SMTP_PASSWORD` must be an **app password**, not your normal
Gmail password — generate one at
https://myaccount.google.com/apppasswords (requires 2-Step Verification to
already be turned on for your Google account). If you leave these three
unset, the script just skips emailing and behaves as before.

### 4. Run it

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

### 5. Run the tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

The test suite mocks all HTTP calls (no live network needed) and covers the
filter logic and each source's response parsing.

## Running on a schedule

### GitHub Actions (recommended — no computer needs to stay on)

A workflow is already set up at `.github/workflows/job-search.yml`. It runs
every 6 hours automatically, entirely on GitHub's servers, and can also be
triggered manually any time from the GitHub website or app (works fine from
a phone/iPad browser — no terminal needed). To activate it:

1. **Add your credentials as repo secrets**, so the workflow can use them
   without them ever appearing in the code: on GitHub, go to your repo →
   **Settings** → **Secrets and variables** → **Actions** → **New
   repository secret**. Add each of these one at a time (name, then value):
   - `ADZUNA_APP_ID`
   - `ADZUNA_APP_KEY`
   - `SMTP_USER` (your Gmail address)
   - `SMTP_PASSWORD` (the Gmail **app password**, not your real password —
     see the email delivery section above)
   - `EMAIL_TO` (where the digest should be sent)
2. **Trigger it once manually to test**: go to the **Actions** tab → click
   "Job Search Digest" in the left sidebar → **Run workflow** button → **Run
   workflow**. Wait a minute or two, then check that email arrived (and
   check the workflow's log in the Actions tab if it didn't, for what went
   wrong).
3. From then on it just runs itself every 6 hours — nothing else to do.

The workflow also commits an updated `seen_jobs.json` back to the repo
after each run (that's how it remembers what you've already been shown
between runs, since each run starts on a fresh GitHub-hosted machine with
no memory of the last one) — that's the small "Update seen-jobs cache"
commit you'll see appear in the repo's history periodically; it's expected
and not something to worry about.

### Cron (Linux/macOS) — alternative if you have a computer you leave on

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
.github/workflows/
  job-search.yml    # scheduled + manually-triggerable GitHub Actions run
job_search_bot/
  config.py       # companies, keywords, filter thresholds — edit this
  models.py        # the normalized Job record
  filters.py        # keyword/level/location/salary/recency filters
  digest.py        # formats the text digest
  mailer.py        # sends the digest by email (SMTP)
  seen_cache.py       # tracks which jobs you've already been shown
  sources/
    greenhouse.py
    lever.py
    ashby.py
    adzuna.py
  main.py          # orchestrates everything, CLI entrypoint
tests/           # pytest suite, HTTP calls mocked
```
