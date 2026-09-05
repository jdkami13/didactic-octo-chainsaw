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
# NOTE: this sandboxed environment could not reach external APIs to verify
# these tokens. "peloton" is Peloton's real Greenhouse token. The rest are
# best-guess placeholders -- verify each one before relying on it. A wrong
# token just returns an empty result (see sources/greenhouse.py), it won't
# crash the script.
GREENHOUSE_COMPANIES = {
    "Peloton": "peloton",
    "BARK": "bark",
    "Change.org": "changeorg",
    "Little Spoon": "littlespoon",
    "PuppySpot": "puppyspot",
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
