"""Core application utilities and helpers."""
import hashlib
import re
from typing import List, Optional
from datetime import datetime, timezone


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip, collapse whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def slugify(text: str) -> str:
    """Create a URL-safe slug from text."""
    if not text:
        return ""
    text = normalize_text(text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text.strip("-")


def hash_content(content: str) -> str:
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def truncate(text: str, max_length: int = 200, suffix: str = "…") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def utc_now() -> datetime:
    """Get current UTC time with timezone."""
    return datetime.now(timezone.utc)


def parse_skills(text: str) -> List[str]:
    """Parse comma/semicolon separated skills string into list."""
    if not text:
        return []
    skills = re.split(r"[,;]", text)
    return [normalize_text(s) for s in skills if s.strip()]


class PaginationParams:
    """Pagination parameters with validation."""
    
    def __init__(self, page: int = 1, per_page: int = 20, max_per_page: int = 100):
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), max_per_page)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page