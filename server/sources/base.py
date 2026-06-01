"""Base crawler class."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import requests


class NewsItem:
    """Represents a single news item."""

    def __init__(
        self,
        news_id: str,
        title: str,
        summary: str,
        source: str = "",
        url: str = "",
        published_at: datetime | None = None,
        content: str = "",
        media_type: str = "article",
        extra: dict[str, Any] | None = None,
    ):
        self.news_id = news_id
        self.title = title
        self.summary = summary
        self.source = source
        self.url = url
        self.published_at = published_at or datetime.now()
        self.media_type = media_type
        self.extra = extra or {}

        self.content = content or ""

    def _expand_content(self) -> str:
        return ""

    def to_dict(self) -> dict[str, Any]:
        extra = dict(self.extra)
        extra["media_type"] = self.media_type
        return {
            "news_id": self.news_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at.isoformat(),
            "extra": extra,
        }

    def __repr__(self) -> str:
        return f"[{self.source}] {self.title}"


class BaseCrawler(ABC):
    """Abstract base class for all news crawlers."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    async def crawl(self) -> list[NewsItem]:
        """Crawl news from this source. Returns a list of NewsItem."""
        ...

    async def _fetch(self, url: str, headers: dict | None = None) -> str:
        """Helper: fetch HTML/text from a URL (sync requests in thread)."""
        h = headers or {"User-Agent": self._user_agent()}
        if "User-Agent" not in h:
            h["User-Agent"] = self._user_agent()
        return await asyncio.to_thread(self._sync_fetch, url, h)

    async def _fetch_json(self, url: str, headers: dict | None = None) -> dict:
        """Helper: fetch JSON from a URL."""
        text = await self._fetch(url, headers=headers)
        return json.loads(text)

    @staticmethod
    def _sync_fetch(url: str, headers: dict) -> str:
        resp = requests.get(url, headers=headers, timeout=15.0, allow_redirects=True)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def _user_agent() -> str:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
