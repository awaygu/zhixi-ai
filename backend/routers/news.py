"""News-related API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from . import deps

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["news"])


@router.post("/news/refresh")
async def refresh_news():
    async with deps.news_lock:
        deps.news_store = []
        results = {}
        all_raw: list = []

        try:
            newsnow_results = await deps.newsnow_batch.crawl_all()
            for platform_id, items in newsnow_results.items():
                all_raw.extend(items)
                results[f"newsnow_{platform_id}"] = {"status": "ok", "count": len(items)}
                logger.info("  ✓ NewsNow-%s: %d items", platform_id, len(items))
        except Exception as e:
            results["newsnow"] = {"status": "error", "error": str(e)}
            logger.warning("  ✗ NewsNow: %s", e)

        try:
            rss_results = await deps.rss_batch.crawl_all()
            for feed_id, items in rss_results.items():
                all_raw.extend(items)
                results[f"rss_{feed_id}"] = {"status": "ok", "count": len(items)}
                logger.info("  ✓ RSS-%s: %d items", feed_id, len(items))
        except Exception as e:
            results["rss"] = {"status": "error", "error": str(e)}
            logger.warning("  ✗ RSS: %s", e)

        filtered = deps.kw_filter.filter_newsitems(all_raw)
        for item in filtered:
            deps.news_store.append(item.to_dict())

        await deps.save_news(deps.news_store)
    return {"total": len(deps.news_store), "total_raw": len(all_raw), "results": results}


@router.get("/news")
async def get_news(
    source: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    pool = [n for n in deps.news_store if n["source"] == source] if source else list(deps.news_store)
    pool.sort(key=lambda n: n.get("published_at", ""), reverse=True)
    total = len(pool)
    items = pool[offset : offset + limit]
    return {"total": total, "offset": offset, "limit": limit, "items": items}


@router.get("/news/{news_id}/content")
async def get_news_content(news_id: str):
    item = deps.find_news(news_id)
    if not item:
        raise HTTPException(404, f"News not found: {news_id}")

    existing_content = item.get("content", "")
    summary = item.get("summary", "")
    if existing_content and existing_content != summary and not existing_content.startswith(summary[:50]):
        return {"news_id": news_id, "content": existing_content, "cached": True}

    url = item.get("url", "")
    if not url:
        return {"news_id": news_id, "content": summary, "cached": False, "source": "summary_only"}

    content = await deps.fetch_article_content(url)
    if not content:
        return {"news_id": news_id, "content": summary, "cached": False, "source": "summary_only"}

    item["content"] = content
    await deps.update_news_content(news_id, content)
    return {"news_id": news_id, "content": content, "cached": False, "source": "original"}


@router.post("/news/refresh/{source}")
async def refresh_news_source(source: str):
    if source in deps.NEWSNOW_CRAWLERS:
        crawler = deps.NEWSNOW_CRAWLERS[source]
        items = await crawler.crawl()
    elif any(feed.id == source for feed in deps.DEFAULT_RSS_FEEDS):
        feed = next(f for f in deps.DEFAULT_RSS_FEEDS if f.id == source)
        from crawlers.rss import RSSCrawler
        crawler = RSSCrawler(feed)
        items = await crawler.crawl()
    else:
        raise HTTPException(400, f"Unknown source: {source}")

    async with deps.news_lock:
        filtered = deps.kw_filter.filter_newsitems(items)
        new_count = 0
        for item in filtered:
            item_dict = item.to_dict()
            existing = any(
                n["news_id"] == item_dict["news_id"]
                for n in deps.news_store
            )
            if not existing:
                deps.news_store.append(item_dict)
                new_count += 1
        await deps.save_news(deps.news_store)

    return {"source": source, "total": len(items), "filtered": len(filtered), "new": new_count}


@router.get("/sources")
async def get_sources():
    return {"sources": deps.NEWS_SOURCES}


@router.get("/newsnow/platforms")
async def get_newsnow_platforms():
    return {
        "platforms": {
            pid: deps.PLATFORM_CONFIG[pid]["name"]
            for pid in deps.NEWSNOW_CRAWLERS
        }
    }


@router.post("/newsnow/refresh")
async def refresh_newsnow():
    async with deps.news_lock:
        results = await deps.newsnow_batch.crawl_all()
        all_raw: list = []
        summary = {}

        for alias, items in results.items():
            all_raw.extend(items)
            summary[alias] = {"total": len(items)}
            logger.info("  ✓ %s: %d items", alias, len(items))

        filtered = deps.kw_filter.filter_newsitems(all_raw)
        new_items = []
        for item in filtered:
            item_dict = item.to_dict()
            existing = any(
                n["news_id"] == item_dict["news_id"]
                for n in deps.news_store
            )
            if not existing:
                deps.news_store.append(item_dict)
                new_items.append(item_dict)

        await deps.save_news(deps.news_store)

    return {
        "total_new": len(new_items),
        "total_raw": len(all_raw),
        "total_filtered": len(filtered),
        "summary": summary,
    }


@router.post("/newsnow/refresh/{platform_id}")
async def refresh_newsnow_platform(platform_id: str):
    if platform_id not in deps.NEWSNOW_CRAWLERS:
        raise HTTPException(
            400,
            f"Unknown platform: {platform_id}. "
            f"Available: {list(deps.NEWSNOW_CRAWLERS.keys())}"
        )

    crawler = deps.NEWSNOW_CRAWLERS[platform_id]
    items = await crawler.crawl()

    async with deps.news_lock:
        filtered = deps.kw_filter.filter_newsitems(items)
        new_count = 0
        for item in filtered:
            item_dict = item.to_dict()
            existing = any(
                n["news_id"] == item_dict["news_id"]
                for n in deps.news_store
            )
            if not existing:
                deps.news_store.append(item_dict)
                new_count += 1

        await deps.save_news(deps.news_store)

    return {
        "platform": platform_id,
        "name": crawler.platform_name,
        "total": len(items),
        "filtered": len(filtered),
        "new": new_count,
    }


@router.get("/rss/feeds")
async def get_rss_feeds():
    return {
        "feeds": [
            {"id": feed.id, "name": feed.name, "url": feed.url, "enabled": feed.enabled}
            for feed in deps.DEFAULT_RSS_FEEDS
        ]
    }


@router.post("/rss/refresh")
async def refresh_rss():
    async with deps.news_lock:
        results = await deps.rss_batch.crawl_all()
        all_raw: list = []
        summary = {}

        for feed_id, items in results.items():
            all_raw.extend(items)
            summary[feed_id] = {"total": len(items)}
            logger.info("  ✓ RSS %s: %d items", feed_id, len(items))

        filtered = deps.kw_filter.filter_newsitems(all_raw)
        new_items = []
        for item in filtered:
            item_dict = item.to_dict()
            existing = any(
                n["news_id"] == item_dict["news_id"]
                for n in deps.news_store
            )
            if not existing:
                deps.news_store.append(item_dict)
                new_items.append(item_dict)

        await deps.save_news(deps.news_store)

    return {
        "total_new": len(new_items),
        "total_raw": len(all_raw),
        "total_filtered": len(filtered),
        "summary": summary,
    }
