"""抖音发布 — mock implementation."""

from .base import BasePublisher, PublishResult


class DouyinPublisher(BasePublisher):
    def __init__(self):
        super().__init__("douyin")

    async def publish(self, title: str, content: str, **kwargs) -> PublishResult:
        # Mock: simulate publishing to Douyin (video script / article)
        return PublishResult(
            success=True,
            platform="douyin",
            article_title=title,
            published_url=f"https://www.douyin.com/video/{abs(hash(title)) % 10**10}",
            extra={"views_simulated": 25000, "likes_simulated": 3200},
        )
