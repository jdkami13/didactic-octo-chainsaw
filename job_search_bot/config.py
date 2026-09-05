"""
Search configuration: companies to watch, keywords, and filter thresholds.

Edit the lists below to change what the script searches for. Nothing here
requires touching the rest of the code.
"""

# --- Greenhouse companies -------------------------------------------------
# Key = display name, value = Greenhouse "board token" (the slug used in
# https://boards.greenhouse.io/<token> or https://job-boards.greenhouse.io/<token>).
# Find it by opening the company's careers page and checking the URL, or by
# viewing the page's network requests for a call to boards-api.greenhouse.io.
#
# These four tokens were confirmed via web search against live Greenhouse
# posting URLs (e.g. job-boards.greenhouse.io/<token>/jobs/<id>):
#   - peloton     -> job-boards.greenhouse.io/peloton/jobs/7535817
#   - bark        -> job-boards.greenhouse.io/bark/jobs/7957591
#   - littlespoon -> job-boards.greenhouse.io/littlespoon
#   - changeorg58 -> job-boards.greenhouse.io/changeorg58/jobs/6538649003
#     (NOTE: Change.org's token is "changeorg58", not the more obvious
#     "changeorg" -- that guess was wrong in an earlier version of this file.)
# A wrong/stale token just returns an empty result for that company (see
# sources/greenhouse.py), it won't crash the script -- but these four are
# confirmed real, not guesses.
GREENHOUSE_COMPANIES = {
    "Peloton": "peloton",
    "BARK": "bark",
    "Change.org": "changeorg58",
    "Little Spoon": "littlespoon",
}

# --- Lever companies -------------------------------------------------------
# Key = display name, value = Lever company slug (from
# https://jobs.lever.co/<slug>).
LEVER_COMPANIES = {
    # "Example Co": "examplecom",
}

# --- Ashby companies ---------------------------------------------------
# Key = display name, value = Ashby job board name (from
# https://jobs.ashbyhq.com/<name>).
ASHBY_COMPANIES = {
    # "Example Co": "examplecom",
}

# PuppySpot: could NOT confirm Greenhouse, Lever, or Ashby for this company.
# Their public job board appears to run on a service called Consider
# (consider.com/boards/co/puppyspot), which this script does not integrate
# with. Left out of all three dicts above rather than guessing a token that
# would silently return nothing. If you find their actual ATS, add them to
# the matching dict.

# --- Adzuna aggregator search ----------------------------------------------
ADZUNA_COUNTRY = "us"
ADZUNA_MAX_DAYS_OLD = 2
ADZUNA_RESULTS_PER_PAGE = 50

# --- Keyword filter ----------------------------------------------------
# A job's title OR description must contain at least one of these (case
# insensitive) to be considered a match.
KEYWORDS = [
    "lifecycle marketing",
    "crm marketing",
    "retention marketing",
    "email marketing manager",
    "marketing operations",
]

# --- Seniority filter --------------------------------------------------
# Title must contain at least one of these...
LEVEL_INCLUDE = [
    "manager",
    "senior manager",
    "sr. manager",
    "sr manager",
    "director",
]
# ...and must NOT contain any of these.
LEVEL_EXCLUDE = [
    "associate",
    "coordinator",
    "specialist",
    "intern",
    "assistant",
]

# --- Location filter -----------------------------------------------------
# A job passes if it looks remote, OR its location text mentions NYC/Bronx
# (for hybrid roles commutable from the Bronx).
REMOTE_KEYWORDS = ["remote"]
NYC_KEYWORDS = [
    "new york",
    "nyc",
    "ny, ny",
    "bronx",
    "new york, ny",
    "manhattan",
]

# --- Salary filter -------------------------------------------------------
MIN_SALARY = 90_000

# --- Recency filter -----------------------------------------------------
MAX_POSTING_AGE_HOURS = 48

# --- Output / dedup -------------------------------------------------------
OUTPUT_DIR = "digests"
SEEN_CACHE_PATH = "seen_jobs.json"
