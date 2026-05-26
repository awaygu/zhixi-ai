"""SQLite persistence layer for the news AI system."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "news_ai.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS news (
                news_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                source TEXT,
                url TEXT,
                published_at TEXT,
                extra TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                style TEXT,
                news_ids TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS publish_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT,
                platform TEXT,
                success INTEGER,
                url TEXT,
                timestamp TEXT,
                extra TEXT
            )
        """)
        await db.commit()
    logger.info("Database initialized: %s", DB_PATH)


async def save_news(items: list[dict[str, Any]]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM news")
        for item in items:
            extra_json = json.dumps(item.get("extra", {}), ensure_ascii=False)
            await db.execute(
                """
                INSERT OR REPLACE INTO news
                    (news_id, title, summary, content, source, url, published_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["news_id"],
                    item["title"],
                    item.get("summary", ""),
                    item.get("content", ""),
                    item.get("source", ""),
                    item.get("url", ""),
                    item.get("published_at", ""),
                    extra_json,
                ),
            )
        await db.commit()


async def append_news(items: list[dict[str, Any]]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        for item in items:
            extra_json = json.dumps(item.get("extra", {}), ensure_ascii=False)
            await db.execute(
                """
                INSERT OR REPLACE INTO news
                    (news_id, title, summary, content, source, url, published_at, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["news_id"],
                    item["title"],
                    item.get("summary", ""),
                    item.get("content", ""),
                    item.get("source", ""),
                    item.get("url", ""),
                    item.get("published_at", ""),
                    extra_json,
                ),
            )
        await db.commit()


async def update_news_content(news_id: str, content: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE news SET content = ? WHERE news_id = ?",
            (content, news_id),
        )
        await db.commit()


async def load_news() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM news ORDER BY published_at DESC")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            item = {
                "news_id": row["news_id"],
                "title": row["title"],
                "summary": row["summary"],
                "content": row["content"],
                "source": row["source"],
                "url": row["url"],
                "published_at": row["published_at"],
                "extra": json.loads(row["extra"]) if row["extra"] else {},
            }
            result.append(item)
        return result


async def save_article(article: dict[str, Any]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        news_ids_json = json.dumps(article.get("news_ids", []), ensure_ascii=False)
        await db.execute(
            """
            INSERT OR REPLACE INTO articles (article_id, title, content, style, news_ids)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                article["article_id"],
                article["title"],
                article.get("content", ""),
                article.get("style", ""),
                news_ids_json,
            ),
        )
        await db.commit()


async def load_articles() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM articles ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "article_id": row["article_id"],
                "title": row["title"],
                "content": row["content"],
                "style": row["style"],
                "news_ids": json.loads(row["news_ids"]) if row["news_ids"] else [],
            })
        return result


async def save_publish_record(record: dict[str, Any]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        extra_json = json.dumps(record.get("extra", {}), ensure_ascii=False)
        await db.execute(
            """
            INSERT INTO publish_log (article_id, platform, success, url, timestamp, extra)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["article_id"],
                record["platform"],
                int(record.get("success", False)),
                record.get("url", ""),
                record.get("timestamp", ""),
                extra_json,
            ),
        )
        await db.commit()


async def load_publish_log() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM publish_log ORDER BY id DESC")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "article_id": row["article_id"],
                "platform": row["platform"],
                "success": bool(row["success"]),
                "url": row["url"],
                "timestamp": row["timestamp"],
                "extra": json.loads(row["extra"]) if row["extra"] else {},
            })
        return result
