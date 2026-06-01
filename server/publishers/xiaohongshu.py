"""小红书发布 — mock implementation."""

from .base import BasePublisher, PublishResult


class XiaohongshuPublisher(BasePublisher):
    def __init__(self):
        super().__init__("xiaohongshu")

    async def publish(self, title: str, content: str, **kwargs) -> PublishResult:
        # Mock: simulate publishing to Xiaohongshu
        return PublishResult(
            success=True,
            platform="xiaohongshu",
            article_title=title,
            published_url=f"https://www.xiaohongshu.com/explore/{abs(hash(title)) % 10**8}",
            extra={"likes_simulated": 1523, "comments_simulated": 287},
        )
