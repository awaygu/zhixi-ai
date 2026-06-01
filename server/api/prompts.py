"""Prompt management API routes."""

from __future__ import annotations

from fastapi import APIRouter

from core.style_manager import prompt_manager

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/status")
async def get_prompts_status():
    return {
        "system_length": len(prompt_manager.system),
        "styles": [s.value for s in prompt_manager.available_styles],
        "has_chat_template": bool(prompt_manager.chat_template),
        "has_generate_style_template": bool(prompt_manager.generate_with_style_template),
        "has_generate_user_prompt_template": bool(prompt_manager.generate_with_user_prompt_template),
    }


@router.post("/reload")
async def reload_prompts():
    prompt_manager.load()
    return {
        "system_length": len(prompt_manager.system),
        "styles": [s.value for s in prompt_manager.available_styles],
    }
