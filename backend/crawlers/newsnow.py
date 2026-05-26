"""NewsNow API unified crawler.

This crawler uses the NewsNow API (https://newsnow.busiyi.world/api/s) to fetch
hot news from various platforms, similar to TrendRadar's implementation.

Supported platforms:
- cls-hot: 财联社热门
- cls-telegraph: 财联社电报
- wallstreetcn-hot: 华尔街见闻
- cankaoxiaoxi: 参考消息
- thepaper: 澎湃新闻
- toutiao: 今日头条
- xueqiu: 雪球
- weibo: 微博
- douyin: 抖音
"""

import hashlib
import json
import random
import time
from datetime import datetime
from typing import Any

from .base import BaseCrawler, NewsItem


PLATFORM_CONFIG = {
    "cls-hot": {"name": "财联社热门", "alias": "cls_hot"},
    "cls-telegraph": {"name": "财联社电报", "alias": "cls_telegraph"},
    "wallstreetcn-hot": {"name": "华尔街见闻", "alias": "wallstreet"},
    "cankaoxiaoxi": {"name": "参考消息", "alias": "cankao"},
    "thepaper": {"name": "澎湃新闻", "alias": "pengpai"},
    "toutiao": {"name": "今日头条", "alias": "toutiao"},
    "xueqiu": {"name": "雪球", "alias": "xueqiu"},
    "weibo": {"name": "微博", "alias": "weibo"},
    "douyin": {"name": "抖音", "alias": "douyin", "media_type": "video"},
}


VIDEO_PLATFORMS = {"douyin"}


class NewsNowCrawler(BaseCrawler):
    """Unified crawler using NewsNow API."""

    DEFAULT_API_URL = "https://newsnow.busiyi.world/api/s"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        platform_id: str,
        api_url: str | None = None,
        max_retries: int = 2,
        retry_wait_min: int = 3,
        retry_wait_max: int = 5,
    ):
        if platform_id not in PLATFORM_CONFIG:
            raise ValueError(
                f"Unknown platform: {platform_id}. "
                f"Available: {list(PLATFORM_CONFIG.keys())}"
            )
        super().__init__(PLATFORM_CONFIG[platform_id]["alias"])
        self.platform_id = platform_id
        self.platform_name = PLATFORM_CONFIG[platform_id]["name"]
        self.alias = PLATFORM_CONFIG[platform_id]["alias"]
        self.api_url = api_url or self.DEFAULT_API_URL
        self.max_retries = max_retries
        self.retry_wait_min = retry_wait_min
        self.retry_wait_max = retry_wait_max

    async def crawl(self) -> list[NewsItem]:
        """Crawl news from NewsNow API."""
        url = f"{self.api_url}?id={self.platform_id}&latest"
        data = await self._fetch_with_retry(url)
        if not data:
            return self._mock_fallback()

        items = []
        seen = set()

        raw_items = data.get("items", [])
        for rank, entry in enumerate(raw_items, 1):
            title = entry.get("title")
            if title is None or isinstance(title, float) or not str(title).strip():
                continue
            title = str(title).strip()

            dedup_key = hashlib.md5(title.encode()).hexdigest()[:12]
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            item_url = entry.get("url", "")
            mobile_url = entry.get("mobileUrl", "")

            if self.platform_id == "toutiao" and item_url:
                tid_match = __import__("re").search(r"/(\d+)/?", item_url)
                if tid_match:
                    item_url = f"https://m.toutiao.com/i{tid_match.group(1)}/"

            items.append(NewsItem(
                news_id=f"{self.alias}_{dedup_key}",
                title=title,
                summary=title[:200],
                source=self.platform_id,
                url=mobile_url or item_url,
                published_at=datetime.now(),
                media_type=PLATFORM_CONFIG[self.platform_id].get("media_type", "article"),
                extra={"original_url": item_url},
            ))

        return items if items else self._mock_fallback()

    async def _fetch_with_retry(self, url: str) -> dict | None:
        """Fetch data with retry mechanism."""
        retries = 0
        while retries <= self.max_retries:
            try:
                text = await self._fetch(url, headers=self.DEFAULT_HEADERS)
                data = json.loads(text)

                status = data.get("status", "")
                if status not in ["success", "cache"]:
                    raise ValueError(f"API status error: {status}")

                return data

            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    wait = random.uniform(self.retry_wait_min, self.retry_wait_max)
                    wait += (retries - 1) * random.uniform(1, 2)
                    await self._sleep(wait)
                else:
                    print(f"[{self.platform_name}] Fetch failed: {e}")
                    return None

        return None

    @staticmethod
    async def _sleep(seconds: float):
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)

    def _mock_fallback(self) -> list[NewsItem]:
        """Fallback mock data when API fails."""
        mocks = [
            (f"{self.platform_name}热点新闻1", "这是第一条热点新闻的详细描述"),
            (f"{self.platform_name}热点新闻2", "这是第二条热点新闻的详细描述"),
            (f"{self.platform_name}热点新闻3", "这是第三条热点新闻的详细描述"),
        ]
        return [
            NewsItem(
                f"{self.alias}_fb{i}",
                t,
                s,
                self.platform_id,
                published_at=datetime.now(),
            )
            for i, (t, s) in enumerate(mocks)
        ]


class NewsNowBatchCrawler:
    """Batch crawler for multiple platforms."""

    def __init__(
        self,
        platform_ids: list[str] | None = None,
        request_interval_ms: int = 100,
    ):
        self.platform_ids = platform_ids or list(PLATFORM_CONFIG.keys())
        self.request_interval_ms = request_interval_ms
        self._crawlers: dict[str, NewsNowCrawler] = {}

        for pid in self.platform_ids:
            try:
                self._crawlers[pid] = NewsNowCrawler(pid)
            except ValueError as e:
                print(f"Warning: {e}")

    async def crawl_all(self) -> dict[str, list[NewsItem]]:
        """Crawl all configured platforms."""
        results: dict[str, list[NewsItem]] = {}

        for i, (pid, crawler) in enumerate(self._crawlers.items()):
            try:
                items = await crawler.crawl()
                results[pid] = items
                print(f"[{crawler.platform_name}] Got {len(items)} items")
            except Exception as e:
                print(f"[{crawler.platform_name}] Error: {e}")
                results[pid] = []

            if i < len(self._crawlers) - 1:
                interval = self.request_interval_ms / 1000
                interval += random.uniform(-0.01, 0.02)
                interval = max(0.05, interval)
                import asyncio
                await asyncio.sleep(interval)

        return results

    def get_platform_names(self) -> dict[str, str]:
        """Get mapping of alias to display name."""
        return {
            crawler.alias: crawler.platform_name
            for crawler in self._crawlers.values()
        }
