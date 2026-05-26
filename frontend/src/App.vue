<template>
  <el-container class="app-container">
    <el-header class="app-header" height="52px">
      <div class="header-left">
        <span class="logo">📰</span>
        <span class="title">新闻爬取 · AI解读 · 发布系统</span>
      </div>
      <div class="header-right">
        <el-tag type="success" effect="dark" size="small">🟢 运行中</el-tag>
      </div>
    </el-header>

    <el-main class="app-main">
      <div class="three-columns" ref="columnsRef">
        <div
          class="column column-left"
          :style="{ width: leftWidth + 'px', flex: 'none' }"
        >
          <NewsList />
        </div>

        <div
          class="resize-handle"
          @mousedown="(e) => startResize(e, 'left')"
        ></div>

        <div
          class="column column-center"
          :style="{ width: centerWidth + 'px', flex: 'none' }"
        >
          <NewsDetail />
        </div>

        <div
          class="resize-handle"
          @mousedown="(e) => startResize(e, 'right')"
        ></div>

        <div
          class="column column-right"
          :style="{ width: rightWidth + 'px', flex: 'none' }"
        >
          <RightPanel />
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import NewsList from '@/components/NewsList.vue'
import NewsDetail from '@/components/NewsDetail.vue'
import RightPanel from '@/components/RightPanel.vue'

const columnsRef = ref<HTMLElement | null>(null)

const leftWidth = ref(280)
const centerWidth = ref(500)
const rightWidth = ref(520)

const MIN_LEFT = 220
const MIN_CENTER = 360
const MIN_RIGHT = 380

let resizing: 'left' | 'right' | null = null
let startX = 0
let startLeftW = 0
let startCenterW = 0
let startRightW = 0

function startResize(e: MouseEvent, side: 'left' | 'right') {
  e.preventDefault()
  resizing = side
  startX = e.clientX
  startLeftW = leftWidth.value
  startCenterW = centerWidth.value
  startRightW = rightWidth.value
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function onMouseMove(e: MouseEvent) {
  if (!resizing) return
  const dx = e.clientX - startX

  if (resizing === 'left') {
    const newLeft = startLeftW + dx
    const newCenter = startCenterW - dx
    if (newLeft >= MIN_LEFT && newCenter >= MIN_CENTER) {
      leftWidth.value = newLeft
      centerWidth.value = newCenter
    }
  } else {
    const newCenter = startCenterW + dx
    const newRight = startRightW - dx
    if (newCenter >= MIN_CENTER && newRight >= MIN_RIGHT) {
      centerWidth.value = newCenter
      rightWidth.value = newRight
    }
  }
}

function onMouseUp() {
  resizing = null
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

onMounted(() => {
  const totalGap = 12 * 4
  const padding = 12 * 2
  const available = window.innerWidth - totalGap - padding
  centerWidth.value = Math.max(MIN_CENTER, available - leftWidth.value - rightWidth.value)

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
  color: #303133;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo {
  font-size: 24px;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.app-main {
  flex: 1;
  padding: 12px;
  overflow: hidden;
}

.three-columns {
  display: flex;
  height: 100%;
}

.column {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

.resize-handle {
  width: 12px;
  flex-shrink: 0;
  cursor: col-resize;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resize-handle::after {
  content: '';
  width: 3px;
  height: 32px;
  border-radius: 2px;
  background: #dcdfe6;
  transition: background 0.2s, height 0.2s;
}

.resize-handle:hover::after {
  background: #409eff;
  height: 48px;
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}
</style>
