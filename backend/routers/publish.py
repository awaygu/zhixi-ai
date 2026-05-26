"""Publish and article management API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from . import deps

router = APIRouter(prefix="/api", tags=["publish"])


class PublishRequest(BaseModel):
    article_id: str
    platform: str


@router.post("/publish")
async def publish_article(req: PublishRequest):
    article = deps.find_article(req.article_id)
    if not article:
        raise HTTPException(404, f"Article not found: {req.article_id}")

    publisher = deps.PUBLISHERS.get(req.platform)
    if not publisher:
        raise HTTPException(400, f"Unknown platform: {req.platform}. Available: {list(deps.PUBLISH_PLATFORMS.keys())}")

    result = await publisher.publish(article["title"], article["content"])
    record = {
        "article_id": req.article_id,
        "platform": req.platform,
        "success": result.success,
        "url": result.published_url,
        "timestamp": result.published_at.isoformat(),
        "extra": result.extra,
    }

    async with deps.article_lock:
        deps.publish_log.append(record)
        await deps.save_publish_record(record)

    return record


@router.get("/publish_log")
async def get_publish_log(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    sorted_log = sorted(deps.publish_log, key=lambda r: r.get("timestamp", ""), reverse=True)
    total = len(sorted_log)
    return {"total": total, "offset": offset, "limit": limit, "items": sorted_log[offset : offset + limit]}


@router.get("/articles")
async def get_articles(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    sorted_articles = sorted(deps.article_store, key=lambda a: a.get("article_id", ""), reverse=True)
    total = len(sorted_articles)
    return {"total": total, "offset": offset, "limit": limit, "items": sorted_articles[offset : offset + limit]}
