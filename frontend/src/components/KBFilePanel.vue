<template>
  <div class="kb-file-panel">
    <div class="panel-header">
      <h3>📁 文件管理</h3>
      <div class="panel-header-right">
        <span class="stat">{{ store.kbTotalChunks }} 切片</span>
        <button class="collapse-btn" title="收起侧栏" @click="$emit('collapse')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M15 19L8 12L15 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>

    <el-upload
      class="upload-area"
      drag
      :auto-upload="true"
      :show-file-list="false"
      :http-request="handleUpload"
      accept=".pdf,.docx,.doc,.txt,.md,.png,.jpg,.jpeg,.gif,.bmp,.webp"
      :disabled="store.kbUploading"
    >
      <div v-if="store.kbUploading" class="upload-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在处理...</span>
      </div>
      <template v-else>
        <el-icon :size="32" color="#a5b4fc"><UploadFilled /></el-icon>
        <div class="upload-text">拖拽文件到此处，或<span class="upload-link">点击上传</span></div>
        <div class="upload-hint">支持 PDF / Word / TXT / Markdown / 图片</div>
      </template>
    </el-upload>

    <el-divider style="margin: 10px 0" />

    <div v-if="store.kbDocuments.length > 0" class="select-bar">
      <el-checkbox
        :model-value="store.kbSelectedDocIds.length === store.kbDocuments.length"
        :indeterminate="store.kbSelectedDocIds.length > 0 && store.kbSelectedDocIds.length < store.kbDocuments.length"
        @change="onSelectAll"
      >全选</el-checkbox>
      <span class="select-count">已选 {{ store.kbSelectedDocIds.length }}/{{ store.kbDocuments.length }}</span>
    </div>

    <div class="doc-list">
      <div v-if="store.kbDocuments.length === 0" class="empty-docs">
        <el-icon :size="32" color="#dcdfe6"><FolderOpened /></el-icon>
        <p>暂无文档，请上传</p>
      </div>
      <div
        v-for="doc in store.kbDocuments"
        :key="doc.doc_id"
        class="doc-card"
        :class="{ selected: store.kbSelectedDocIds.includes(doc.doc_id) }"
      >
        <el-checkbox
          :model-value="store.kbSelectedDocIds.includes(doc.doc_id)"
          @change="store.toggleDocSelection(doc.doc_id)"
          class="doc-check"
        />
        <div class="doc-icon">{{ fileIcon(doc.file_type) }}</div>
        <div class="doc-info" @click="onDocClick(doc)">
          <template v-if="editingDocId === doc.doc_id">
            <el-input
              ref="renameInputRef"
              v-model="editFilename"
              size="small"
              class="rename-input"
              @blur="onSaveRename(doc.doc_id)"
              @keyup.enter="onSaveRename(doc.doc_id)"
              @keyup.escape="editingDocId = ''"
            />
          </template>
          <template v-else>
            <div class="doc-name" :title="doc.filename" @dblclick.stop="startRename(doc.doc_id, doc.filename)">{{ doc.filename }}</div>
          </template>
          <div class="doc-meta">
            <span>{{ formatSize(doc.file_size) }}</span>
            <span>{{ doc.chunk_count }} 切片</span>
          </div>
        </div>
        <el-button
          v-if="editingDocId !== doc.doc_id"
          text
          size="small"
          class="doc-rename-btn"
          @click.stop="startRename(doc.doc_id, doc.filename)"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button
          text
          size="small"
          :loading="store.kbDeleting"
          @click.stop="onDelete(doc.doc_id)"
          class="doc-del"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>

    <el-dialog v-model="summaryVisible" :title="summaryDoc?.filename" width="420px" class="summary-dialog">
      <div v-if="summaryDoc" class="summary-content">
        <div class="summary-meta">
          <span>{{ fileIcon(summaryDoc.file_type) }} {{ summaryDoc.file_type }}</span>
          <span>{{ formatSize(summaryDoc.file_size) }}</span>
          <span>{{ summaryDoc.chunk_count }} 切片</span>
        </div>
        <el-divider style="margin: 12px 0" />
        <div v-if="summaryDoc.summary" class="summary-text">{{ summaryDoc.summary }}</div>
        <div v-else class="summary-empty">暂无概要</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled, Loading, FolderOpened, Delete, Edit } from '@element-plus/icons-vue'
import { useNewsStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { ref, nextTick } from 'vue'
import type { KBDoc } from '@/types'

defineProps<{ kbId: string }>()
defineEmits<{ collapse: [] }>()

const store = useNewsStore()

const editingDocId = ref('')
const editFilename = ref('')
const renameInputRef = ref<InstanceType<typeof ElInput> | null>(null)
const summaryVisible = ref(false)
const summaryDoc = ref<KBDoc | null>(null)

function onDocClick(doc: KBDoc) {
  summaryDoc.value = doc
  summaryVisible.value = true
}

function onSelectAll(val: boolean | string) {
  if (val) {
    store.selectAllDocs()
  } else {
    store.deselectAllDocs()
  }
}

function startRename(docId: string, filename: string) {
  editFilename.value = filename
  editingDocId.value = docId
  nextTick(() => renameInputRef.value?.focus())
}

async function onSaveRename(docId: string) {
  const name = editFilename.value.trim()
  if (!name || name === store.kbDocuments.find(d => d.doc_id === docId)?.filename) {
    editingDocId.value = ''
    return
  }
  try {
    await store.renameKBDoc(docId, name)
    ElMessage.success('文件名已更新')
  } catch (e: any) {
    ElMessage.error(`重命名失败：${e.message || '未知错误'}`)
  } finally {
    editingDocId.value = ''
  }
}

async function handleUpload(options: any) {
  const file = options.file as File
  const ext = file.name.split('.').pop()?.toLowerCase()
  const allowed = ['pdf', 'docx', 'doc', 'txt', 'md', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
  if (!ext || !allowed.includes(ext)) {
    ElMessage.error('不支持的文件格式')
    options.onError(new Error('Unsupported'))
    return
  }
  try {
    await store.uploadKBDoc(file)
    ElMessage.success(`${file.name} 上传成功`)
    options.onSuccess({})
  } catch (e: any) {
    ElMessage.error(`上传失败：${e.message || '未知错误'}`)
    options.onError(e)
  }
}

async function onDelete(docId: string) {
  try {
    await store.deleteKBDoc(docId)
    ElMessage.success('已删除')
  } catch (e: any) {
    ElMessage.error(`删除失败：${e.message}`)
  }
}

function fileIcon(ext: string): string {
  if (ext === '.pdf') return '📄'
  if (ext === '.docx' || ext === '.doc') return '📝'
  if (['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'].includes(ext)) return '🖼️'
  if (ext === '.md') return '📋'
  return '📃'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}
</script>

<style scoped>
.kb-file-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.panel-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  transition: all 0.2s;
}

.collapse-btn:hover {
  border-color: #a5b4fc;
  color: #6366f1;
  background: #eef2ff;
}

.stat {
  font-size: 12px;
  color: #818cf8;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 20px;
  border-radius: 10px;
  border: 2px dashed #ddd6fe;
  background: #faf5ff;
  transition: all 0.2s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #a78bfa;
  background: #ede9fe;
}

.upload-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #818cf8;
  font-size: 14px;
}

.upload-text {
  font-size: 13px;
  color: #64748b;
  margin-top: 6px;
}

.upload-link {
  color: #6366f1;
  font-weight: 500;
}

.upload-hint {
  font-size: 12px;
  color: #a5b4fc;
  margin-top: 4px;
}

.select-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.select-bar :deep(.el-checkbox__label) {
  font-size: 13px;
  color: #64748b;
}

.select-count {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}

.doc-list {
  flex: 1;
  overflow-y: auto;
}

.empty-docs {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 0;
  color: #c0c4cc;
}

.empty-docs p {
  font-size: 13px;
  margin: 0;
}

.doc-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 6px;
  transition: all 0.15s;
}

.doc-card.selected {
  border-color: #c7d2fe;
  background: #f5f3ff;
}

.doc-card:hover {
  border-color: #c7d2fe;
  background: #faf5ff;
}

.doc-check {
  flex-shrink: 0;
}

.doc-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.doc-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.doc-name:hover {
  color: #6366f1;
}

.rename-input {
  width: 100%;
}

.doc-rename-btn {
  flex-shrink: 0;
  color: #94a3b8;
  opacity: 0;
  transition: opacity 0.15s;
}

.doc-card:hover .doc-rename-btn {
  opacity: 1;
}

.doc-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.doc-del {
  flex-shrink: 0;
  color: #f87171;
}

.summary-meta {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: #64748b;
}

.summary-text {
  font-size: 14px;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
}

.summary-empty {
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
  padding: 20px 0;
}
</style>
