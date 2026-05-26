"""Keyword filter management API routes."""

from __future__ import annotations

from fastapi import APIRouter

from config import KEYWORDS_FILE
from crawlers.filter import KeywordFilter
from . import deps

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.get("/status")
async def get_keywords_status():
    total_rules = sum(len(rules) for rules in deps.kw_filter.groups.values())
    return {
        "enabled": deps.kw_filter.enabled,
        "file": KEYWORDS_FILE,
        "groups": {
            name: [kw for kw, _ in rules]
            for name, rules in deps.kw_filter.groups.items()
        },
        "total_rules": total_rules,
    }


@router.post("/reload")
async def reload_keywords():
    deps.kw_filter = KeywordFilter(KEYWORDS_FILE)
    total_rules = sum(len(rules) for rules in deps.kw_filter.groups.values())
    return {
        "enabled": deps.kw_filter.enabled,
        "total_rules": total_rules,
        "groups": list(deps.kw_filter.groups.keys()),
    }
