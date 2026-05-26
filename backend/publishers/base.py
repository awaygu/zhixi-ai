"""Base publisher class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PublishResult:
    """Result of a publish attempt."""
    success: bool
    platform: str
    article_title: str
    published_url: str = ""
    error_message: str = ""
    published_at: datetime = field(default_factory=datetime.now)
    extra: dict[str, Any] = field(default_factory=dict)


class BasePublisher(ABC):
    """Abstract base class for all platform publishers."""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    @abstractmethod
    async def publish(
        self,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> PublishResult:
        """Publish article to the platform."""
        ...
