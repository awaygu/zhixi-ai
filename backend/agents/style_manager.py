"""Prompt management for the news AI system.

Loads all prompts from prompts.py. Supports hot-reload via reload().
"""

from __future__ import annotations

import importlib
import logging
from enum import Enum

import prompts as _prompts_module

logger = logging.getLogger(__name__)


class StyleType(str, Enum):
    XIAOHONGSHU = "xiaohongshu"
    WECHAT_MP = "wechat_mp"
    DOUYIN = "douyin"


class PromptManager:
    """Central prompt manager. Loads from prompts.py and provides typed access."""

    def __init__(self):
        self.system: str = ""
        self._styles: dict[StyleType, str] = {}
        self.chat_template: str = ""
        self.generate_with_style_template: str = ""
        self.generate_with_user_prompt_template: str = ""
        self.load()

    def load(self) -> None:
        importlib.reload(_prompts_module)

        self.system = _prompts_module.SYSTEM
        self._styles = {
            StyleType(k): v
            for k, v in _prompts_module.STYLES.items()
            if k in [e.value for e in StyleType]
        }
        self.chat_template = _prompts_module.CHAT
        self.generate_with_style_template = _prompts_module.GENERATE_WITH_STYLE
        self.generate_with_user_prompt_template = _prompts_module.GENERATE_WITH_USER_PROMPT

        logger.info(
            "Loaded prompts: %d styles, system=%d chars",
            len(self._styles),
            len(self.system),
        )

    def get_style_prompt(self, style: StyleType) -> str:
        return self._styles.get(style, self._styles.get(StyleType.WECHAT_MP, ""))

    @property
    def available_styles(self) -> list[StyleType]:
        return list(self._styles.keys())


prompt_manager = PromptManager()
