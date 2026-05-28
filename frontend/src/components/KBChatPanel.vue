<template>
  <div class="kb-chat-panel">
    <div class="chat-header">
      <h3>💬 知识库对话</h3>
      <span class="hint">基于RAG检索，回答引用知识库</span>
    </div>

    <div class="chat-body" ref="messagesRef">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="msg-row"
        :class="msg.role"
      >
        <div class="msg-avatar">
          <div v-if="msg.role === 'assistant'" class="avatar-ai">📚</div>
          <div v-else class="avatar-user">我</div>
        </div>
        <div class="msg-bubble-wrap">
          <div v-if="msg.sources && msg.sources.length" class="msg-sources">
            <div
              v-for="(s, si) in msg.sources"
              :key="si"
              class="source-card"
              :class="{ expanded: isSourceExpanded(i, si) }"
            >
              <div class="source-header" @click="toggleSource(i, si)">
                <span class="source-file">📎 {{ s.filename }}</span>
                <span v-if="s.page" class="source-page">P.{{ s.page }}</span>
                <span class="source-score">{{ (s.score * 100).toFixed(1) }}%</span>
                <span class="source-toggle">{{ isSourceExpanded(i, si) ? '▲' : '▼' }}</span>
              </div>
              <div v-if="isSourceExpanded(i, si)" class="source-full">{{ s.text || s.preview }}</div>
              <div v-else class="source-preview">{{ s.preview }}</div>
            </div>
          </div>
          <div class="msg-bubble" v-html="renderMsgHtml(msg)"></div>
          <div
            v-if="msg.role === 'assistant' && !msg.streaming && msg.content && msg.type === 'article'"
            class="msg-actions"
          >
            <button class="msg-action-btn" @click="copyContent(msg.content)">📋 复制</button>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-footer">
      <div class="input-area">
        <el-input
          v-model="chatMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 5 }"
          placeholder="输入问题，AI将检索知识库回答..."
          :disabled="generating"
          @keydown.enter.exact="onInputEnter"
          class="chat-input"
        />
        <button class="send-btn" :disabled="!chatMessage.trim() || generating" @click="sendChat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useNewsStore } from '@/stores'
import { kbStreamChat, kbStreamGenerate } from '@/api'
import type { StyleType } from '@/types'
import { marked } from 'marked'

const store = useNewsStore()

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  type?: 'chat' | 'article'
  sources?: KBSource[]
}

const messages = ref<ChatMessage[]>([
  { role: 'assistant', content: '你好！我可以基于知识库内容回答问题。上传文档后，直接提问即可。', type: 'chat' },
])

const messagesRef = ref<HTMLElement | null>(null)
const chatMessage = ref('')
const generating = ref(false)
const expandedSources = ref<Set<string>>(new Set())

function sourceKey(msgIdx: number, srcIdx: number): string {
  return `${msgIdx}-${srcIdx}`
}

function isSourceExpanded(msgIdx: number, srcIdx: number): boolean {
  return expandedSources.value.has(sourceKey(msgIdx, srcIdx))
}

function toggleSource(msgIdx: number, srcIdx: number) {
  const key = sourceKey(msgIdx, srcIdx)
  const s = new Set(expandedSources.value)
  if (s.has(key)) {
    s.delete(key)
  } else {
    s.add(key)
  }
  expandedSources.value = s
}

function renderMarkdown(text: string): string {
  return marked.parse(text, { async: false }) as string
}

function renderMsgHtml(msg: ChatMessage): string {
  let html = renderMarkdown(msg.content)
  if (msg.streaming) {
    const cursor = '<span class="streaming-cursor">▊</span>'
    const lastClose = html.lastIndexOf('</')
    if (lastClose > 0) {
      const tagEnd = html.indexOf('>', lastClose)
      html = html.slice(0, tagEnd) + cursor + html.slice(tagEnd)
    } else {
      html += cursor
    }
  }
  return html
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function pushUserMessage(text: string) {
  messages.value.push({ role: 'user', content: text, type: 'chat' })
}

function addAssistantMessage(type: ChatMessage['type'] = 'chat'): number {
  const msg: ChatMessage = { role: 'assistant', content: '', streaming: true, type }
  messages.value.push(msg)
  return messages.value.length - 1
}

function pushDone(msgIdx: number) {
  messages.value[msgIdx].streaming = false
  generating.value = false
  scrollToBottom()
}

function pushError(msgIdx: number, err: string) {
  messages.value[msgIdx].content += `\n\n❌ ${err}`
  messages.value[msgIdx].streaming = false
  generating.value = false
  scrollToBottom()
}

function onInputEnter(e: KeyboardEvent) {
  if (e.ctrlKey || e.shiftKey) return
  e.preventDefault()
  sendChat()
}

async function sendChat() {
  const msg = chatMessage.value.trim()
  if (!msg || generating.value) return

  pushUserMessage(msg)
  chatMessage.value = ''
  generating.value = true

  const msgIdx = addAssistantMessage('chat')
  scrollToBottom()

  const docIds = store.kbDocuments.map(d => d.doc_id)

  kbStreamChat(msg, docIds, {
    onChunk(text) {
      messages.value[msgIdx].content += text
      scrollToBottom()
    },
    onSources(sources) {
      messages.value[msgIdx].sources = sources
    },
    onPrompt() {},
    onDone() {
      pushDone(msgIdx)
    },
    onError(err) {
      pushError(msgIdx, `请求失败：${err}`)
    },
  })
}

function generateArticle(style: StyleType) {
  if (generating.value) return

  const styleLabels: Record<string, string> = {
    xiaohongshu: '小红书',
    wechat_mp: '公众号',
    douyin: '抖音',
  }

  const lastUserMsg = [...messages.value].reverse().find(m => m.role === 'user')
  const topic = lastUserMsg?.content || '总结知识库核心内容'

  pushUserMessage(`用${styleLabels[style]}风格生成文章`)
  generating.value = true

  const msgIdx = addAssistantMessage('article')
  scrollToBottom()

  const docIds = store.kbDocuments.map(d => d.doc_id)

  kbStreamGenerate(topic, style, {
    onChunk(text) {
      messages.value[msgIdx].content += text
      scrollToBottom()
    },
    onSources(sources) {
      messages.value[msgIdx].sources = sources
    },
    onDone() {
      pushDone(msgIdx)
    },
    onError(err) {
      pushError(msgIdx, `生成失败：${err}`)
    },
  }, docIds)
}

function copyContent(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

defineExpose({ generateArticle })
</script>

<style scoped>
.kb-chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #eef2ff;
  flex-shrink: 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
}

.hint {
  font-size: 11px;
  color: #a5b4fc;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
}

.msg-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.avatar-ai,
.avatar-user {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.avatar-ai {
  background: #eef2ff;
}

.avatar-user {
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #fff;
  font-weight: 500;
  font-size: 11px;
}

.msg-bubble-wrap {
  max-width: 85%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.msg-row.user .msg-bubble-wrap {
  align-items: flex-end;
}

.msg-sources {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.source-card {
  background: #eef2ff;
  border: 1px solid #ddd6fe;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 12px;
}

.source-card.expanded {
  border-color: #a5b4fc;
  background: #eef2ff;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
  cursor: pointer;
  user-select: none;
}

.source-header:hover {
  opacity: 0.85;
}

.source-file {
  font-weight: 500;
  color: #6366f1;
}

.source-page {
  background: #c7d2fe;
  color: #312e81;
  padding: 0 5px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.source-score {
  color: #818cf8;
  font-size: 11px;
}

.source-toggle {
  margin-left: auto;
  font-size: 9px;
  color: #818cf8;
}

.source-preview {
  color: #64748b;
  line-height: 1.45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.source-full {
  color: #334155;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: 4px;
  padding: 6px 8px;
  margin-top: 4px;
  font-size: 12px;
  border: 1px solid #e0e7ff;
}

.msg-bubble {
  padding: 8px 12px;
  border-radius: 10px;
  background: #fff;
  font-size: 13.5px;
  line-height: 1.65;
  word-break: break-word;
}

.msg-row.user .msg-bubble {
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #fff;
}

.msg-bubble :deep(p) { margin: 3px 0; }
.msg-bubble :deep(strong) { font-weight: 600; }
.msg-bubble :deep(code) {
  background: #eef2ff;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12.5px;
  color: #4338ca;
}
.msg-bubble :deep(pre) {
  background: #f1f5f9;
  padding: 8px 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12.5px;
}
.msg-bubble :deep(blockquote) {
  border-left: 2px solid #a5b4fc;
  padding-left: 10px;
  color: #64748b;
  margin: 3px 0;
}

.streaming-cursor {
  display: inline;
  animation: blink 0.7s infinite;
  color: #6366f1;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.msg-actions {
  display: flex;
  gap: 4px;
}

.msg-action-btn {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #e0e7ff;
  background: #fff;
  color: #6366f1;
  cursor: pointer;
  transition: all 0.15s;
}

.msg-action-btn:hover {
  border-color: #818cf8;
  background: #eef2ff;
}

.chat-footer {
  flex-shrink: 0;
  padding: 10px 12px;
  border-top: 1px solid #eef2ff;
  background: #fff;
}

.input-area {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid #e0e7ff;
  border-radius: 10px;
  padding: 4px 4px 4px 2px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-area:focus-within {
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.12);
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 6px 10px;
  font-size: 13.5px;
  line-height: 1.5;
  resize: none;
  background: transparent;
  color: #1e293b;
}

.chat-input :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}

.send-btn:hover:not(:disabled) {
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
}

.send-btn:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}
</style>
