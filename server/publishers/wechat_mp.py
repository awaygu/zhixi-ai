"""微信公众号发布 — mock implementation."""

from .base import BasePublisher, PublishResult


class WechatMpPublisher(BasePublisher):
    def __init__(self):
        super().__init__("wechat_mp")

    async def publish(self, title: str, content: str, **kwargs) -> PublishResult:
        # Mock: simulate publishing to WeChat Official Account
        return PublishResult(
            success=True,
            platform="wechat_mp",
            article_title=title,
            published_url=f"https://mp.weixin.qq.com/s/{abs(hash(title)) % 10**8}",
            extra={"reads_simulated": 8532, "likes_simulated": 532},
        )
