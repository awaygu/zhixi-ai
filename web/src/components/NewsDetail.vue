<template>
  <div class="news-detail">
    <template v-if="news">
      <div class="detail-top">
        <div class="detail-title-row">
          <h2 class="detail-title">{{ news.title }}</h2>
          <el-tag v-if="isVideo" size="small" type="danger" effect="dark" class="media-tag">
            <el-icon><VideoCamera /></el-icon> 视频
          </el-tag>
          <el-button text size="small" @click="store.closeDetail()" title="关闭详情">
            <el-icon :size="18"><Close /></el-icon>
          </el-button>
        </div>
        <div class="detail-meta">
          <el-tag size="small" type="info" effect="plain">{{ SOURCE_LABELS[news.source] ?? news.source }}</el-tag>
          <span class="detail-time">{{ formatTime(news.published_at) }}</span>
          <div class="detail-actions">
            <el-button
              :type="isSelected ? 'success' : 'primary'"
              size="small"
              @click="toggleSelect"
            >
              <el-icon><Select /></el-icon>
              {{ isSelected ? '已选中' : '选中解读' }}
            </el-button>
            <el-button v-if="news.url" size="small" @click="openOriginal">
              <el-icon><Link /></el-icon> {{ isVideo ? '打开视频' : '新窗口打开' }}
            </el-button>
          </div>
        </div>
        <div v-if="news.summary" class="detail-summary">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ news.summary }}</span>
        </div>
      </div>

      <!-- Video content -->
      <div v-if="isVideo" class="video-area">
        <div class="video-placeholder">
          <el-icon :size="64" color="#909399"><VideoCamera /></el-icon>
          <p class="video-hint">这是视频新闻，无法在此嵌入播放</p>
          <el-button type="primary" @click="openOriginal">
            <el-icon><Link /></el-icon> 打开视频
          </el-button>
        </div>
        <div v-if="videoContent" class="video-metadata">
          <div class="meta-title">视频元信息</div>
          <div class="meta-content">{{ videoContent }}</div>
        </div>
      </div>

      <!-- Article content -->
      <div v-else-if="articleContent" class="detail-article">
        <div class="article-body" v-html="articleContent"></div>
        <div class="article-footer">
          <el-button size="small" @click="openOriginal">
            <el-icon><Link /></el-icon> 查看原文
          </el-button>
        </div>
      </div>
      <div v-else-if="news.url" class="detail-iframe-wrap">
        <div v-if="isJsRendered" class="js-rendered-hint">
          <el-icon><Warning /></el-icon>
          <span>此页面为动态加载内容，如未显示正文请点击"新窗口打开"查看</span>
        </div>
        <iframe
          :src="news.url"
          class="detail-iframe"
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
          allow="autoplay; fullscreen"
          loading="lazy"
        />
      </div>
      <div v-else class="detail-no-url">
        <el-empty description="暂无原文链接" />
      </div>
    </template>

    <div v-else class="detail-placeholder">
      <el-icon :size="48" color="#dcdfe6"><Document /></el-icon>
      <p>点击左侧新闻查看详情</p>
      <p class="hint">选中的新闻可在右侧进行AI解读或生成文章</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useNewsStore } from '@/stores'
import { SOURCE_LABELS, VIDEO_SOURCES, JS_RENDERED_SOURCES } from '@/types'
import { fetchNewsContent } from '@/api'

const store = useNewsStore()
const news = computed(() => store.currentDetailNews)

const fetchedContent = ref('')
const fetchingContent = ref(false)

watch(news, async (n) => {
  fetchedContent.value = ''
  if (!n) return
  const content = n.content || ''
  const summary = n.summary || ''
  if (content && content !== summary && !content.startsWith(summary.slice(0, 50))) {
    fetchedContent.value = content
    return
  }
  if (n.news_id && !fetchingContent.value) {
    fetchingContent.value = true
    try {
      const res = await fetchNewsContent(n.news_id)
      if (res.content && res.content !== summary && !res.content.startsWith(summary.slice(0, 50))) {
        fetchedContent.value = res.content
      }
    } catch { /* ignore */ }
    fetchingContent.value = false
  }
}, { immediate: true })

const isVideo = computed(() => {
  if (!news.value) return false
  const mediaType = news.value.extra?.media_type
  if (mediaType === 'video') return true
  return VIDEO_SOURCES.has(news.value.source)
})

const isJsRendered = computed(() => {
  if (!news.value) return false
  const mediaType = news.value.extra?.media_type
  if (mediaType === 'js_rendered') return true
  return JS_RENDERED_SOURCES.has(news.value.source)
})

const videoContent = computed(() => {
  if (!news.value) return ''
  const content = news.value.content || ''
  const summary = news.value.summary || ''
  if (content && content !== summary && !content.startsWith(summary.slice(0, 50))) {
    return content
  }
  return ''
})

const articleContent = computed(() => {
  if (isVideo.value) return ''
  const text = fetchedContent.value
  if (!text) return ''
  const paragraphs = text.split(/\n{2,}/).filter(p => p.trim())
  return paragraphs.map(p => `<p>${p.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>`).join('')
})

const isSelected = computed(() =>
  news.value ? store.selectedNewsIds.includes(news.value.news_id) : false
)

function toggleSelect() {
  if (news.value) {
    store.toggleSelect(news.value.news_id)
  }
}

function openOriginal() {
  if (news.value?.url) {
    window.open(news.value.url, '_blank')
  }
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}
</script>

<style scoped>
.news-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-top {
  flex-shrink: 0;
}

.detail-title-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.detail-title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  line-height: 1.4;
}

.media-tag {
  flex-shrink: 0;
  margin-top: 2px;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.detail-time {
  font-size: 13px;
  color: #909399;
}

.detail-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.detail-summary {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 10px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.detail-summary .el-icon {
  margin-top: 2px;
  flex-shrink: 0;
  color: #409eff;
}

.video-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  margin-top: 12px;
}

.video-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #fafbfc;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  min-height: 200px;
}

.video-hint {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.video-metadata {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.meta-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 6px;
}

.meta-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.detail-iframe-wrap {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 12px;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.detail-article {
  flex: 1;
  margin-top: 12px;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow-y: auto;
}

.article-body {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
}

.article-body p {
  margin: 0 0 12px;
  text-indent: 2em;
}

.article-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  text-align: right;
}

.js-rendered-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fdf6ec;
  border-bottom: 1px solid #e4e7ed;
  font-size: 13px;
  color: #e6a23c;
  flex-shrink: 0;
}

.js-rendered-hint .el-icon {
  flex-shrink: 0;
}

.detail-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.detail-no-url {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
}

.detail-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #c0c4cc;
}

.detail-placeholder p {
  font-size: 14px;
  margin: 0;
}

.detail-placeholder .hint {
  font-size: 12px;
  color: #dcdfe6;
}
</style>
