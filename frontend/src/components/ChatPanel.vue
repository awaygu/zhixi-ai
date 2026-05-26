<template>
  <div class="chat-panel">
    <div class="messages" ref="messagesRef">
      <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
        <div class="msg-avatar">
          <el-avatar :size="32" :icon="msg.role === 'user' ? 'User' : 'Sparkles'" />
        </div>
        <div class="msg-bubble">
          <div v-if="msg.prompt" class="prompt-block">
            <div class="prompt-header" @click="msg.promptExpanded = !msg.promptExpanded">
              <el-icon size="14"><Document /></el-icon>
              <span>提交的 Prompt</span>
              <el-icon size="12" class="prompt-toggle">
                <component :is="msg.promptExpanded ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
            </div>
            <div v-if="msg.promptExpanded" class="prompt-body">{{ msg.prompt }}</div>
          </div>
          <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
          <span v-if="msg.streaming" class="streaming-cursor">▊</span>
        </div>
      </div>
    </div>

    <div class="input-area">
      <el-input
        v-model="chatMessage"
        placeholder="输入问题，AI帮你解读选中的新闻..."
        size="default"
        clearable
        :disabled="generating"
        @keyup.enter="sendChat"
      >
        <template #append>
          <el-button @click="sendChat" :disabled="!chatMessage.trim() || generating">
            <el-icon><component is="ArrowRight" /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useNewsStore } from '@/stores'
import { streamChat } from '@/api'
import { marked } from 'marked'

const store = useNewsStore()
const messagesRef = ref<HTMLElement | null>(null)
const chatMessage = ref('')
const generating = ref(false)

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  prompt?: string
  promptExpanded?: boolean
}

const messages = ref<ChatMessage[]>([
  { role: 'assistant', content: '👋 你好！请从左侧选择新闻，然后向我提问，我来帮你解读。' },
])

function renderMarkdown(text: string): string {
  return marked.parse(text, { async: false }) as string
}

function addAssistantMessage(): number {
  const msg: ChatMessage = { role: 'assistant', content: '', streaming: true }
  messages.value.push(msg)
  return messages.value.length - 1
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

async function sendChat() {
  const msg = chatMessage.value.trim()
  if (!msg || generating.value) return
  if (store.selectedNewsIds.length === 0) {
    messages.value.push({ role: 'user', content: msg })
    messages.value.push({ role: 'assistant', content: '⚠️ 请先在左侧选择一些新闻，我才能基于它们回复你。' })
    chatMessage.value = ''
    return
  }

  messages.value.push({ role: 'user', content: msg })
  chatMessage.value = ''
  generating.value = true

  const msgIdx = addAssistantMessage()
  scrollToBottom()

  streamChat(msg, store.selectedNewsIds, {
    onLoading(message) {
      messages.value[msgIdx].content = `⏳ ${message}`
      scrollToBottom()
    },
    onPrompt(prompt) {
      messages.value[msgIdx].prompt = prompt
      messages.value[msgIdx].promptExpanded = false
      scrollToBottom()
    },
    onLimited(message) {
      messages.value[msgIdx].content = `ℹ️ ${message}`
      messages.value[msgIdx].streaming = false
      generating.value = false
      scrollToBottom()
    },
    onChunk(text) {
      if (messages.value[msgIdx].content.startsWith('⏳')) {
        messages.value[msgIdx].content = ''
      }
      messages.value[msgIdx].content += text
      scrollToBottom()
    },
    onDone() {
      messages.value[msgIdx].streaming = false
      generating.value = false
      scrollToBottom()
    },
    onError(err) {
      messages.value[msgIdx].content += `\n\n❌ 请求失败：${err}`
      messages.value[msgIdx].streaming = false
      generating.value = false
      scrollToBottom()
    },
  })
}

watch(() => messages.value.length, scrollToBottom)
</script>

<style scoped>
.chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.msg-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #f0f2f5;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
  position: relative;
}

.msg-row.user .msg-bubble {
  background: #409eff;
  color: #fff;
}

.prompt-block {
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.prompt-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #fafbfc;
  font-size: 12px;
  color: #909399;
  cursor: pointer;
  user-select: none;
}

.prompt-header:hover {
  background: #f5f7fa;
}

.prompt-toggle {
  margin-left: auto;
}

.prompt-body {
  padding: 8px;
  font-size: 12px;
  color: #606266;
  background: #fafbfc;
  border-top: 1px solid #e4e7ed;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Consolas', 'Monaco', monospace;
  line-height: 1.5;
}

.msg-content {
  word-break: break-word;
}

.msg-content :deep(h1), .msg-content :deep(h2), .msg-content :deep(h3) {
  margin: 8px 0 4px;
  font-weight: 600;
}
.msg-content :deep(h1) { font-size: 18px; }
.msg-content :deep(h2) { font-size: 16px; }
.msg-content :deep(h3) { font-size: 15px; }
.msg-content :deep(p) { margin: 4px 0; }
.msg-content :deep(ul), .msg-content :deep(ol) { padding-left: 20px; margin: 4px 0; }
.msg-content :deep(li) { margin: 2px 0; }
.msg-content :deep(strong) { font-weight: 600; }
.msg-content :deep(em) { font-style: italic; }
.msg-content :deep(code) {
  background: rgba(0,0,0,0.06);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 13px;
}
.msg-content :deep(pre) {
  background: rgba(0,0,0,0.06);
  padding: 8px 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 13px;
}
.msg-content :deep(blockquote) {
  border-left: 3px solid #dcdfe6;
  padding-left: 12px;
  color: #606266;
  margin: 4px 0;
}

.streaming-cursor {
  display: inline;
  animation: blink 0.7s infinite;
  color: #409eff;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.input-area {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  flex-shrink: 0;
}

.input-area .el-input {
  flex: 1;
}
</style>
