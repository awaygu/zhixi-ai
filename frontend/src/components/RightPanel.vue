<template>
  <div class="right-panel">
    <div v-if="store.selectedNewsIds.length > 0" class="selected-news-bar">
      <div class="bar-header">
        <span class="bar-label">已选 {{ store.selectedNewsIds.length }} 条</span>
        <el-button type="primary" text size="small" @click="store.clearSelection()">清除</el-button>
      </div>
      <div class="bar-items">
        <div
          v-for="news in selectedNewsList"
          :key="news.news_id"
          class="bar-item"
          @click="store.viewDetail(news)"
        >
          <span class="bar-item-title">{{ news.title }}</span>
          <span v-if="news.summary" class="bar-item-summary">{{ news.summary.slice(0, 60) }}{{ news.summary.length > 60 ? '...' : '' }}</span>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="right-tabs">
      <el-tab-pane name="chat">
        <template #label>
          <span><el-icon><ChatLineSquare /></el-icon> 解读新闻</span>
        </template>
        <ChatPanel />
      </el-tab-pane>

      <el-tab-pane name="generate">
        <template #label>
          <span><el-icon><MagicStick /></el-icon> 生成文章</span>
        </template>
        <GeneratePanel />
      </el-tab-pane>

      <el-tab-pane name="publish">
        <template #label>
          <span><el-icon><Upload /></el-icon> 发布</span>
        </template>
        <PublishPanel />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useNewsStore } from '@/stores'
import ChatPanel from './ChatPanel.vue'
import GeneratePanel from './GeneratePanel.vue'
import PublishPanel from './PublishPanel.vue'

const store = useNewsStore()
const activeTab = ref('chat')

const selectedNewsList = computed(() =>
  store.newsItems.filter(n => store.selectedNewsIds.includes(n.news_id))
)
</script>

<style scoped>
.right-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.selected-news-bar {
  flex-shrink: 0;
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 8px 10px;
  background: #fafbfc;
}

.bar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.bar-label {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
}

.bar-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 120px;
  overflow-y: auto;
}

.bar-item {
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}

.bar-item:hover {
  background: #ecf5ff;
}

.bar-item-title {
  display: block;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bar-item-summary {
  display: block;
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.right-panel :deep(.right-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.right-panel :deep(.right-tabs .el-tabs__header) {
  margin-bottom: 0;
}

.right-panel :deep(.right-tabs .el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.right-panel :deep(.right-tabs .el-tab-pane) {
  height: 100%;
}
</style>
