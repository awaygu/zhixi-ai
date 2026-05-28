<template>
  <el-container class="kb-container">
    <el-header class="kb-header" height="52px">
      <div class="header-left">
        <el-button text @click="$router.push('/')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 首页
        </el-button>
        <span class="title">📚 知识库 · AI检索 · 智能生成</span>
      </div>
    </el-header>

    <el-main class="kb-main">
      <div class="kb-three-columns">
        <div class="kb-col kb-col-left">
          <KBFilePanel />
        </div>
        <div class="kb-col kb-col-center">
          <KBChatPanel ref="chatPanelRef" />
        </div>
        <div class="kb-col kb-col-right">
          <KBActionPanel @generate="onGenerate" />
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import KBFilePanel from '@/components/KBFilePanel.vue'
import KBChatPanel from '@/components/KBChatPanel.vue'
import KBActionPanel from '@/components/KBActionPanel.vue'
import { useNewsStore } from '@/stores'
import type { StyleType } from '@/types'

const store = useNewsStore()
const chatPanelRef = ref<InstanceType<typeof KBChatPanel> | null>(null)

function onGenerate(style: StyleType) {
  chatPanelRef.value?.generateArticle(style)
}

onMounted(() => {
  store.loadKBDocuments()
})
</script>

<style scoped>
.kb-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.kb-header {
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

.back-btn {
  font-size: 14px;
  color: #6366f1;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.kb-main {
  flex: 1;
  padding: 12px;
  overflow: hidden;
}

.kb-three-columns {
  display: flex;
  height: 100%;
  gap: 12px;
}

.kb-col {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.kb-col-left {
  width: 280px;
  flex: none;
}

.kb-col-center {
  flex: 1;
  min-width: 0;
}

.kb-col-right {
  width: 260px;
  flex: none;
}
</style>
