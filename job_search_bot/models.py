from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    source: str
    company: str
    title: str
    url: str
    location_text: str = ""
    posted_at: Optional[datetime] = None  # timezone-aware UTC
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_text: str = ""
    description_text: str = ""
    external_id: str = field(default="")

    def dedup_key(self) -> str:
        return f"{self.source}:{self.company}:{self.external_id or self.url}"
