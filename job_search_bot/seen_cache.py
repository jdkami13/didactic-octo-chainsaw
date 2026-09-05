import json
import logging
from pathlib import Path
from typing import List, Set

from .models import Job

logger = logging.getLogger(__name__)


def load_seen(path: str) -> Set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_keys", []))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read seen-jobs cache at %s: %s", path, exc)
        return set()


def save_seen(path: str, seen_keys: Set[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump({"seen_keys": sorted(seen_keys)}, f, indent=2)


def split_new_and_seen(jobs: List[Job], seen_keys: Set[str]):
    new_jobs = [j for j in jobs if j.dedup_key() not in seen_keys]
    return new_jobs
