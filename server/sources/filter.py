"""Keyword-based news filter.

Reads rules from a text file with groups, plain keywords and regex patterns.
Only news matching at least one whitelist rule is kept; news matching any
exclude rule is discarded (even if it matched a whitelist rule).

File format:
  - Lines starting with # define a group name (used as a tag)
  - Lines starting with ! are exclude rules (match => discard)
  - Lines wrapped in /.../ are compiled as regex patterns
  - All other non-empty lines are plain-text contains-match keywords
  - Empty lines and lines starting with // are ignored
  - Multiple groups are OR-related: any whitelist match => keep
  - Exclude rules take priority: any exclude match => discard
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class KeywordFilter:
    """Filter news items by keyword rules loaded from a text file."""

    def __init__(self, file_path: str | Path | None = None):
        self.groups: dict[str, list[tuple[str, re.Pattern | None]]] = {}
        self.excludes: list[tuple[str, re.Pattern | None]] = []
        self.enabled = False

        if file_path is None:
            return

        path = Path(file_path)
        if not path.exists():
            logger.info("Keywords file not found: %s — filtering disabled", path)
            return

        self._parse(path)
        total_rules = sum(len(rules) for rules in self.groups.values())
        if total_rules == 0 and not self.excludes:
            logger.info("Keywords file is empty: %s — filtering disabled", path)
            return

        self.enabled = True
        logger.info(
            "Keyword filter enabled: %d groups, %d whitelist, %d exclude from %s",
            len(self.groups),
            total_rules,
            len(self.excludes),
            path,
        )

    def _parse(self, path: Path) -> None:
        current_group = "default"
        with open(path, encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.strip()

                if not line:
                    continue

                if line.startswith("//"):
                    continue

                if line.startswith("#"):
                    current_group = line.lstrip("#").strip() or "default"
                    continue

                is_exclude = line.startswith("!")
                rule_text = line[1:] if is_exclude else line

                if rule_text.startswith("/") and rule_text.endswith("/") and len(rule_text) >= 2:
                    pattern_str = rule_text[1:-1]
                    try:
                        pattern = re.compile(pattern_str, re.IGNORECASE)
                    except re.error as e:
                        logger.warning("Invalid regex at line %d: %s (%s)", line_num, rule_text, e)
                        continue
                else:
                    pattern = None

                if is_exclude:
                    self.excludes.append((rule_text, pattern))
                else:
                    if current_group not in self.groups:
                        self.groups[current_group] = []
                    self.groups[current_group].append((rule_text, pattern))

        self.groups = {k: v for k, v in self.groups.items() if v}

    def _match_whitelist(self, text: str) -> str | None:
        for group, rules in self.groups.items():
            for keyword, pattern in rules:
                if pattern is not None:
                    if pattern.search(text):
                        return group
                else:
                    if keyword.lower() in text.lower():
                        return group
        return None

    def _match_exclude(self, text: str) -> bool:
        for keyword, pattern in self.excludes:
            if pattern is not None:
                if pattern.search(text):
                    return True
            else:
                if keyword.lower() in text.lower():
                    return True
        return False

    def filter_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter a list of news dicts. Matching items get extra.matched_group set."""
        if not self.enabled:
            return items

        result = []
        for item in items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            if self._match_exclude(text):
                continue
            group = self._match_whitelist(text)
            if group is not None:
                item.setdefault("extra", {})["matched_group"] = group
                result.append(item)
        return result

    def filter_newsitems(self, items: list) -> list:
        """Filter a list of NewsItem objects. Returns matching items with extra.matched_group."""
        if not self.enabled:
            return items

        result = []
        for item in items:
            d = item.to_dict()
            text = f"{d.get('title', '')} {d.get('summary', '')}"
            if self._match_exclude(text):
                continue
            group = self._match_whitelist(text)
            if group is not None:
                item.extra["matched_group"] = group
                result.append(item)
        return result
