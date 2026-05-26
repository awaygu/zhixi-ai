/** TypeScript type definitions for the News AI system. */

export interface NewsItem {
  news_id: string
  title: string
  summary: string
  content: string
  source: string
  url: string
  published_at: string
  extra: Record<string, any>
}

export interface Article {
  article_id: string
  title: string
  content: string
  style: string
  news_ids: string[]
}

export interface PublishRecord {
  article_id: string
  platform: string
  success: boolean
  url: string
  timestamp: string
  extra: Record<string, any>
}

export type StyleType = 'xiaohongshu' | 'wechat_mp' | 'douyin'

export const STYLE_LABELS: Record<StyleType, string> = {
  xiaohongshu: '小红书风格 ✨',
  wechat_mp: '公众号风格 📰',
  douyin: '抖音风格 🎬',
}

export const SOURCE_LABELS: Record<string, string> = {
  'cls-hot': '财联社热门',
  'cls-telegraph': '财联社电报',
  'wallstreetcn-hot': '华尔街见闻',
  'cankaoxiaoxi': '参考消息',
  'thepaper': '澎湃新闻',
  'toutiao': '今日头条',
  'xueqiu': '雪球',
  'weibo': '微博',
  'douyin': '抖音',
  'hacker-news': 'Hacker News',
  'ruanyifeng': '阮一峰的网络日志',
}

export const VIDEO_SOURCES = new Set(['douyin'])

export const PLATFORM_LABELS: Record<string, string> = {
  xiaohongshu: '小红书',
  wechat_mp: '微信公众号',
  douyin: '抖音',
}
