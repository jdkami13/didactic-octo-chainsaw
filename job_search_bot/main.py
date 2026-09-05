#!/usr/bin/env python3
"""
Search Greenhouse, Lever, Ashby, and Adzuna for new job postings matching
the criteria in config.py, and print/save a digest of what's new.

Usage:
    python -m job_search_bot.main
    python -m job_search_bot.main --no-cache   # ignore/skip the seen-jobs dedup cache
    python -m job_search_bot.main --quiet      # suppress console output, file only
"""
import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from . import config
from .digest import build_digest_text
from .filters import filter_jobs
from .seen_cache import load_seen, save_seen, split_new_and_seen
from .sources import adzuna, ashby, greenhouse, lever

logger = logging.getLogger("job_search_bot")


def fetch_all_jobs():
    jobs = []
    jobs.extend(greenhouse.fetch_all(config.GREENHOUSE_COMPANIES.items()))
    jobs.extend(lever.fetch_all(config.LEVER_COMPANIES.items()))
    jobs.extend(ashby.fetch_all(config.ASHBY_COMPANIES.items()))
    jobs.extend(
        adzuna.fetch_all(
            config.KEYWORDS,
            country=config.ADZUNA_COUNTRY,
            max_days_old=config.ADZUNA_MAX_DAYS_OLD,
            results_per_page=config.ADZUNA_RESULTS_PER_PAGE,
        )
    )
    return jobs


def run(use_cache: bool = True, quiet: bool = False) -> int:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("Fetching postings from all sources...")
    all_jobs = fetch_all_jobs()
    logger.info("Fetched %d total postings before filtering.", len(all_jobs))

    matching_jobs = filter_jobs(all_jobs)
    logger.info("%d posting(s) matched filters.", len(matching_jobs))

    if use_cache:
        seen_keys = load_seen(config.SEEN_CACHE_PATH)
        new_jobs = split_new_and_seen(matching_jobs, seen_keys)
        logger.info(
            "%d posting(s) are new since last run (%d already seen).",
            len(new_jobs),
            len(matching_jobs) - len(new_jobs),
        )
    else:
        new_jobs = matching_jobs

    digest_text = build_digest_text(new_jobs)

    if not quiet:
        print(digest_text)

    out_dir = Path(config.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"digest_{timestamp}.txt"
    out_path.write_text(digest_text, encoding="utf-8")
    logger.info("Digest saved to %s", out_path)

    if use_cache:
        seen_keys = load_seen(config.SEEN_CACHE_PATH)
        seen_keys.update(job.dedup_key() for job in matching_jobs)
        save_seen(config.SEEN_CACHE_PATH, seen_keys)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Search job boards for new matching postings.")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Don't dedup against previously-seen postings (show everything that matches filters).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Don't print the digest to the console (still writes the digest file).",
    )
    args = parser.parse_args()
    return run(use_cache=not args.no_cache, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
