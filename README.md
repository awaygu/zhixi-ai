# 识渊 AI · 智能内容工作台

基于大语言模型的智能内容创作平台，集成新闻AI解读、多知识库RAG检索、联网搜索、智能体短期记忆与多平台内容发布，打造从信息获取到内容发布的完整工作流。

---

## 技术栈

| 分类 | 技术 | 说明 |
|------|------|------|
| **后端** | FastAPI | 高性能 Python Web 框架 |
| **前端** | Vue 3 + TypeScript | 渐进式框架 + 类型安全 |
| **构建** | Vite | 快速构建工具 |
| **UI** | Element Plus | Vue 3 组件库 |
| **状态** | Pinia | Vue 3 状态管理 |
| **路由** | Vue Router | 前端路由 |
| **数据库** | SQLite + aiosqlite | 异步轻量级嵌入式数据库 |
| **AI 框架** | LangChain + LangGraph | LLM 应用框架 + Agent 状态图 |
| **向量** | FAISS + DashScope | 语义检索 + 文本嵌入 |
| **联网搜索** | Kimi / Tavily | 双引擎可切换的互联网搜索 |
| **发布** | Playwright | 浏览器自动化多平台发布 |

---

## 项目结构

```
shiyuan-ai/
├── docker-compose.newsnow.yml   # NewsNow Docker 中台服务配置
├── server/                      # FastAPI 后端服务
│   ├── app.py                  # 主入口 + 应用配置 + 生命周期
│   ├── config.py               # 全局配置管理（含记忆、搜索配置）
│   ├── database.py             # SQLite 数据库操作（8张表）
│   ├── prompts.py              # AI 提示词管理
│   ├── keywords.txt            # 关键词过滤列表
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example            # 环境变量模板
│   ├── data/                   # 运行时数据目录
│   │   ├── agent_memory.db     # Agent 记忆数据库（自动创建）
│   │   └── rag_memory.db      # KB RAG 记忆数据库（自动创建）
│   ├── uploads/                # 文件上传目录（按知识库隔离）
│   ├── cookies/                # 浏览器登录 Cookie 持久化
│   ├── core/                   # AI 核心模块
│   │   ├── agent_graph.py      # LangGraph Agent 定义（create_agent + SummarizationMiddleware）
│   │   ├── rag_graph.py        # KB RAG 短期记忆 LangGraph（rewrite_query + retrieve + generate）
│   │   ├── checkpointer.py     # SQLite 持久化层（conversations + messages 双表）
│   │   ├── interpreter.py      # 新闻解读器
│   │   ├── style_manager.py    # 风格管理器
│   │   └── image_generator.py  # AI 配图生成（DashScope qwen-image）
│   ├── sources/                # 新闻来源模块
│   │   ├── base.py             # 爬虫基类（requests + asyncio.to_thread）
│   │   ├── newsnow.py          # NewsNow 统一爬虫（9平台，含 fallback）
│   │   ├── rss.py              # RSS/Atom 爬虫
│   │   └── filter.py           # 内容过滤器
│   ├── rag/                    # RAG 知识库模块
│   │   ├── loader.py           # 文档解析（PDF/DOCX/TXT/MD）
│   │   ├── chunker.py          # 文本分块
│   │   ├── embeddings.py       # DashScope 文本嵌入
│   │   └── vectorstore.py      # FAISS 向量存储（多库隔离）
│   ├── tools/                  # Agent 工具模块
│   │   ├── web_search.py       # 联网搜索统一路由（Kimi/Tavily 切换）
│   │   ├── web_search_kimi.py  # Kimi $web_search 实现
│   │   └── web_search_tavily.py# Tavily Search API 实现
│   ├── publishers/             # 发布器模块
│   │   ├── base.py             # 发布器基类
│   │   ├── xiaohongshu.py      # 小红书发布器（Playwright）
│   │   ├── wechat_mp.py        # 微信公众号发布器（API + Playwright）
│   │   └── douyin_pub.py       # 抖音发布器（Playwright）
│   ├── api/                    # API 路由
│   │   ├── deps.py             # 依赖注入 + 共享状态
│   │   ├── agent.py            # 智能体对话（LangGraph Agent + SSE 流式）
│   │   ├── conversations.py    # 对话管理 CRUD
│   │   ├── news.py             # 新闻接口（含后台刷新）
│   │   ├── interpret.py        # AI 解读接口
│   │   ├── knowledge.py        # 知识库 CRUD + RAG 接口
│   │   ├── publish.py          # 发布接口
│   │   ├── schedule.py         # 定时任务接口
│   │   ├── tasks.py            # 异步任务管理
│   │   ├── keywords.py         # 关键词管理
│   │   └── prompts.py          # 提示词管理
│   └── specs/                  # 设计规格文档
│       ├── memory-spec.md      # 短期记忆功能规格
│       └── publish-spec.md     # 发布功能规格
├── web/                        # Vue 3 前端应用
│   ├── src/
│   │   ├── App.vue             # 根组件
│   │   ├── main.ts             # 入口文件
│   │   ├── api/index.ts        # API 请求 + SSE 流式消费 + 对话管理
│   │   ├── router/index.ts     # 路由配置（首页/新闻/知识库）
│   │   ├── stores/index.ts     # Pinia 状态管理
│   │   ├── types/index.ts      # TypeScript 类型定义
│   │   ├── pages/              # 页面
│   │   │   ├── HomeView.vue           # 首页（知识库列表）
│   │   │   ├── NewsView.vue           # 新闻解读
│   │   │   └── KnowledgeBaseView.vue  # 知识库详情
│   │   └── components/        # 组件
│   │       ├── NewsList.vue           # 新闻列表
│   │       ├── NewsDetail.vue         # 新闻详情（正文展示 / iframe）
│   │       ├── FloatingAgent.vue      # 智能体浮窗（含会话列表 + 联网搜索开关）
│   │       ├── GeneratePanel.vue      # 文章生成面板
│   │       ├── PublishPanel.vue       # 发布面板
│   │       ├── TaskPanel.vue          # 异步任务面板
│   │       ├── KBFilePanel.vue        # 知识库文件管理
│   │       ├── KBChatPanel.vue        # 知识库 RAG 对话
│   │       ├── KBActionPanel.vue      # 智能生成面板
│   │       └── KeywordSettings.vue    # 关键词过滤设置
│   └── package.json
└── README.md
```

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **新闻AI解读** | 多源新闻爬取 + LLM 深度解读 + 智能体对话 |
| **多知识库管理** | 创建/删除知识库，每个知识库独立向量索引 |
| **文档上传与解析** | 支持 PDF / DOCX / TXT / MD，自动分块嵌入 |
| **RAG 语义检索** | DashScope 嵌入 + FAISS 向量检索，引用来源 |
| **RAG 短期记忆** | LangGraph StateGraph + 查询重写 + SummarizationMiddleware 自动摘要压缩 |
| **多风格文章生成** | 小红书 / 公众号 / 抖音三种风格 |
| **联网搜索** | 支持 Kimi / Tavily 双引擎，前端一键开关 |
| **智能体短期记忆** | LangGraph Agent + SummarizationMiddleware 自动摘要压缩 |
| **会话管理** | 多会话切换、历史恢复、会话列表侧边栏 |
| **AI 配图生成** | DashScope qwen-image 自动生成文章配图 |
| **多平台发布** | Playwright 自动化发布到小红书/公众号/抖音 |
| **定时爬取** | 自动定时刷新新闻数据 |

---

## 智能体架构

### Agent 工具函数（9个）

| 工具 | 说明 |
|------|------|
| `refresh_news` | 刷新所有新闻源 |
| `refresh_source` | 刷新指定新闻源 |
| `get_trends` | 获取热门话题和关键词趋势 |
| `search_news` | 按关键词搜索新闻 |
| `compare_sources` | 对比不同来源对同一话题的报道 |
| `get_news_content` | 获取新闻完整内容 |
| `get_briefing_data` | 获取每日简报数据 |
| `search_knowledge_base` | 搜索用户上传的知识库文档 |
| `web_search` | 联网搜索互联网最新信息 |

### 短期记忆实现

智能体与知识库 RAG 各自独立实现短期记忆，采用相同的核心组件但配置独立。

#### Agent 短期记忆

```
用户消息 ──▶ LangGraph Agent (create_agent)
                │
                ├── SummarizationMiddleware
                │     ├── trigger: token 数超过阈值（默认 6000）
                │     ├── keep: 保留最近 N 条消息（默认 10）
                │     └── 自动调用摘要 LLM 压缩历史
                │
                ├── AsyncSqliteSaver (checkpointer)
                │     └── 按 thread_id 持久化 Agent 状态
                │
                └── 自定义 messages 表
                      └── 按 conversation_id 存储对话历史

前端 ←── SSE 流式事件 ──← Agent astream_events
  ├── conversation_id 事件（新对话创建时）
  ├── chunk 事件（流式输出）
  ├── loading 事件（工具执行中）
  ├── action 事件（前端副作用）
  └── [DONE] 事件
```

#### KB RAG 短期记忆

```
用户消息 ──▶ LangGraph StateGraph (rag_graph)
                │
                ├── rewrite_query 节点（意图识别 + 查询重写）
                │     ├── 规则前置过滤（零成本，~80% 请求直接跳过）
                │     │     ├── 代词检测（它/那/这/上述/刚才）
                │     │     ├── 短句检测（<15字且无主语）
                │     │     └── 祈使句检测（详细/展开/进一步）
                │     └── LLM 精确判断（规则命中时触发）
                │           ├── new_question: 全新问题，直接检索
                │           ├── follow_up_need_search: 追问需检索，消解代词后重写查询
                │           └── follow_up_no_search: 纯追问，跳过检索复用上轮结果
                │
                ├── retrieve 节点（条件执行）
                │     ├── skip_retrieve=False → embed(rewritten_query) → FAISS 检索
                │     └── skip_retrieve=True → 复用 last_context + last_sources
                │
                ├── generate 节点
                │     ├── SummarizationMiddleware
                │     │     ├── trigger: token 数超过阈值（默认 4000）
                │     │     ├── keep: 保留最近 N 条消息（默认 8）
                │     │     └── 仅压缩 Human/AIMessage（检索内容不入历史）
                │     ├── SystemMessage(RAG_PROMPT + context) [临时，不持久化]
                │     ├── messages(历史) + HumanMessage(query) [持久化到 checkpointer]
                │     └── LLM.astream() → SSE 流式输出
                │
                ├── AsyncSqliteSaver (独立 rag_memory.db)
                │     └── 按 thread_id=kb_{kb_id} 持久化 RAG state
                │
                └── kb_messages 双写（前端展示用）

前端 ←── SSE 流式事件 ──← rag_graph.astream_events
  ├── rewrite 事件（查询被重写时，显示原文与改写后的查询）
  ├── prompt 事件（完整 prompt 内容）
  ├── sources 事件（检索来源）
  ├── chunk 事件（流式输出）
  └── [DONE] 事件
```

**关键设计决策：**
- **检索内容不入历史**（策略 B）：每轮 RAG context 临时注入 SystemMessage，不持久化到 messages，避免文档片段被摘要压缩导致信息损失
- **单会话/知识库**：每个知识库仅一个固定会话 `conv_id=kb_{kb_id}`，无会话列表
- **旧历史自动迁移**：首次请求时从 `kb_messages` 表加载旧对话，注入 checkpointer 后由 LangGraph 接管
- **清空会话**：同时清理 `kb_messages` + LangGraph checkpoint 数据

### 联网搜索

支持两种搜索引擎，通过 `WEB_SEARCH_ENGINE` 环境变量切换：

| 引擎 | 配置 | 特点 |
|------|------|------|
| **Kimi** | `WEB_SEARCH_ENGINE=kimi` + `MOONSHOT_API_KEY` | 基于 Kimi $web_search，中文搜索优化 |
| **Tavily** | `WEB_SEARCH_ENGINE=tavily` + `TAVILY_API_KEY` | 基于 Tavily Search API，通用搜索 |

前端提供联网搜索开关，开启后强制先执行搜索，将结果注入上下文后再由主 LLM 回答。

---

## 快速开始

### 环境要求

- **Python**: >= 3.10
- **Node.js**: >= 18.0
- **Docker**: >= 20.10（用于 NewsNow 中台服务，可选）

### 1. 克隆项目

```bash
git clone <repository-url>
cd shiyuan-ai
```

### 2. 启动 NewsNow 中台（推荐）

NewsNow 提供本地新闻聚合 API，作为后端爬虫层的数据源。Docker 部署后端自动连接，无需公网依赖。

```bash
# 启动 NewsNow 容器（端口 4444，256M 内存限制）
docker compose -f docker-compose.newsnow.yml up -d

# 验证服务
curl http://localhost:4444/api/s?id=weibo
```

> 若不启动 Docker，爬虫会自动 fallback 到公共实例 `https://newsnow.busiyi.world/api/s`。

### 3. 后端启动

```bash
cd server

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 配置 LLM_API_KEY、DASHSCOPE_API_KEY 等

# 启动服务（自动等待 NewsNow 就绪，最多10秒）
python app.py
```

后端运行在 **http://localhost:8000**，API 文档: http://localhost:8000/docs

### 4. 前端启动

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 **http://localhost:5173**

---

## 配置说明

### 环境变量（server/.env）

```env
# ── LLM 配置 ──────────────────────────────────────────────
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# ── 服务器 ────────────────────────────────────────────────
HOST=0.0.0.0
PORT=8000

# ── 爬虫间隔（秒）────────────────────────────────────────
CRAWL_INTERVAL=1800
NEWSNOW_CRAWL_INTERVAL=1800
RSS_CRAWL_INTERVAL=1800

# ── 定时任务 ──────────────────────────────────────────────
SCHEDULE_ENABLED=true

# ── NewsNow API ───────────────────────────────────────────
# 本地 Docker（推荐）: http://localhost:4444/api/s
# 公共实例（fallback）: https://newsnow.busiyi.world/api/s
NEWSNOW_API_URL=http://localhost:4444/api/s

# ── 关键词过滤 ────────────────────────────────────────────
KEYWORDS_FILE=keywords.txt
KEYWORDS_FILTER_ENABLED=true

# ── 发布配置 ──────────────────────────────────────────────
PUBLISH_RETRY=3

# ── 微信公众号（已认证服务号）─────────────────────────────
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# ── 浏览器自动化（Playwright）─────────────────────────────
PUBLISH_HEADLESS=true
PUBLISH_TIMEOUT=120

# ── Jina Reader（免费，无需 API Key）─────────────────────
JINA_READER_URL=https://r.jina.ai

# ── DashScope（阿里云）────────────────────────────────────
DASHSCOPE_API_KEY=sk-your-dashscope-key-here

# ── AI 配图 ───────────────────────────────────────────────
IMAGE_GEN_ENABLED=true
IMAGE_GEN_MODEL=qwen-image-2.0-pro

# ── 知识库 ────────────────────────────────────────────────
KB_CHUNK_SIZE=500
KB_CHUNK_OVERLAP=50
KB_VISION_MODEL=qwen-vl-ocr-latest
KB_VISION_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ── 联网搜索 ──────────────────────────────────────────────
WEB_SEARCH_ENABLED=true
WEB_SEARCH_ENGINE=kimi    # kimi / tavily

# Kimi（WEB_SEARCH_ENGINE=kimi 时需要）
MOONSHOT_API_KEY=sk-your-moonshot-key-here

# Tavily（WEB_SEARCH_ENGINE=tavily 时需要）
TAVILY_API_KEY=tvly-your-tavily-key-here

# ── 短期记忆（智能体）──────────────────────────────────────
MEMORY_DB_PATH=data/agent_memory.db
SUMMARY_MODEL=deepseek-chat
SUMMARY_MODEL_BASE_URL=https://api.openai.com/v1
SUMMARY_MODEL_API_KEY=sk-your-api-key-here
SUMMARY_TRIGGER_TOKENS=6000
SUMMARY_KEEP_MESSAGES=10

# ── 短期记忆（KB RAG）──────────────────────────────────────
KB_RAG_SUMMARY_TRIGGER_TOKENS=4000
KB_RAG_SUMMARY_KEEP_MESSAGES=8
KB_RAG_MEMORY_DB_PATH=data/rag_memory.db
```

### NewsNow Docker 配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 镜像 | `ghcr.io/ourongxing/newsnow:latest` | 官方镜像 |
| 端口 | `4444` | 宿主机映射端口 |
| 内存限制 | `256M` | 容器内存上限 |
| 重启策略 | `unless-stopped` | 自动重启 |
| 数据持久化 | `./newsnow-data:/app/data` | SQLite 缓存不丢失 |

---

## API 接口

### 智能体对话

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/agent/chat/stream` | 智能体对话（SSE 流式，支持 `conversation_id` 多轮记忆） |
| GET | `/api/agent/trends` | 获取热门话题 |
| GET | `/api/agent/compare` | 多源对比 |

### 对话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/conversations` | 创建新对话 |
| GET | `/api/conversations` | 获取对话列表（分页） |
| GET | `/api/conversations/{id}` | 获取对话详情 |
| PATCH | `/api/conversations/{id}` | 更新对话标题 |
| DELETE | `/api/conversations/{id}` | 删除对话（硬删除，清理消息+checkpointer） |
| GET | `/api/conversations/{id}/messages` | 获取对话历史消息 |
| DELETE | `/api/conversations/{id}/messages` | 清空对话消息 |

### 知识库管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/knowledge/bases` | 创建知识库 |
| GET | `/api/knowledge/bases` | 获取知识库列表 |
| GET | `/api/knowledge/bases/{kb_id}` | 获取知识库详情 |
| DELETE | `/api/knowledge/bases/{kb_id}` | 删除知识库 |

### 知识库文档

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/knowledge/bases/{kb_id}/upload` | 上传文档 |
| GET | `/api/knowledge/bases/{kb_id}/documents` | 获取文档列表 |
| DELETE | `/api/knowledge/bases/{kb_id}/documents/{doc_id}` | 删除文档 |
| POST | `/api/knowledge/bases/{kb_id}/search` | 语义检索 |

### 知识库对话

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/knowledge/bases/{kb_id}/conversations` | 创建会话 |
| GET | `/api/knowledge/bases/{kb_id}/conversations` | 获取会话列表 |
| DELETE | `/api/knowledge/bases/{kb_id}/conversations/{conv_id}` | 删除会话 |
| GET | `/api/knowledge/bases/{kb_id}/conversations/{conv_id}/messages` | 获取会话消息 |
| POST | `/api/knowledge/bases/{kb_id}/chat/stream` | RAG 对话（SSE 流式，含短期记忆 + 查询重写） |
| DELETE | `/api/knowledge/bases/{kb_id}/chat/clear` | 清空会话（同时清理消息 + LangGraph checkpoint） |
| GET | `/api/knowledge/bases/{kb_id}/chat/messages` | 获取当前会话消息（单会话模式） |
| POST | `/api/knowledge/bases/{kb_id}/generate/stream` | RAG 文章生成（SSE 流式） |

### 新闻与解读

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news` | 获取新闻列表（分页 + 按源筛选） |
| POST | `/api/news/refresh` | 刷新全部新闻（同步） |
| POST | `/api/news/refresh/{source}` | 刷新单源新闻（后台异步，立即返回） |
| GET | `/api/news/{news_id}/content` | 获取新闻正文（后端抓取 + Jina Reader） |
| POST | `/api/interpret/stream` | AI 解读（SSE） |
| POST | `/api/chat/stream` | 对话式解读（SSE） |
| POST | `/api/generate_article/stream` | 文章生成（SSE） |

### 发布与任务

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/publish` | 发布文章到指定平台 |
| GET | `/api/publish/log` | 获取发布记录 |
| GET | `/api/tasks` | 获取异步任务列表 |
| DELETE | `/api/tasks/clear` | 清理已完成任务 |

---

## 数据库设计

### 主数据库（news_ai.db）

| 表名 | 说明 |
|------|------|
| `news` | 新闻数据 |
| `articles` | 生成的文章 |
| `publish_log` | 发布记录 |
| `knowledge_bases` | 知识库 |
| `kb_documents` | 知识库文档（关联 kb_id） |
| `kb_chunks` | 文档分块 |
| `kb_conversations` | 知识库会话 |
| `kb_messages` | 会话消息 |

### 记忆数据库（data/agent_memory.db）

| 表名 | 说明 |
|------|------|
| `conversations` | 智能体对话（id, title, created_at, updated_at） |
| `messages` | 对话消息（conversation_id, role, content, tool_calls, tool_call_id） |
| `checkpoints` | LangGraph checkpointer 状态（thread_id 关联 conversation） |
| `writes` | LangGraph checkpointer 写入记录 |

### RAG 记忆数据库（data/rag_memory.db）

| 表名 | 说明 |
|------|------|
| `checkpoints` | KB RAG LangGraph checkpointer 状态（thread_id = kb_{kb_id}） |
| `writes` | KB RAG checkpointer 写入记录 |
| `checkpoint_blobs` | KB RAG checkpointer 二进制数据 |

---

## 支持风格

| 风格 | 标识符 | 特点 |
|------|--------|------|
| 小红书 | `xiaohongshu` | emoji 丰富、口语化、话题标签、800字以内 |
| 公众号 | `wechat_mp` | 深度长文、专业分析、1200-1800字 |
| 抖音 | `douyin` | 短平快、口播稿、200-300字 |

---

## 新闻来源

### NewsNow 平台（通过 Docker 中台聚合）

| 来源 | 标识符 |
|------|--------|
| 财联社热门 | `cls-hot` |
| 财联社电报 | `cls-telegraph` |
| 华尔街见闻 | `wallstreetcn-hot` |
| 参考消息 | `cankaoxiaoxi` |
| 澎湃新闻 | `thepaper` |
| 今日头条 | `toutiao` |
| 雪球 | `xueqiu` |
| 微博 | `weibo` |
| 抖音 | `douyin` |

### RSS 源

| 来源 | 标识符 |
|------|--------|
| Hacker News | `hacker-news` |
| 阮一峰的网络日志 | `ruanyifeng` |

### 爬虫架构

```
前端 loadNews() ──fire-and-forget──▶ POST /api/news/refresh/{source}
        │                                      │
        │                              asyncio.create_task()
        │                              (_bg_crawl_and_save)
        │                                      │
        ├──等待2s──▶ GET /api/news          ┌───┴───┐
        │                              本地 Docker   公共实例
        │                              :4444/api/s  (fallback)
        │                                  │
        │                              NewsNow 响应
        │                                  │
        └──────── 解析 + 去重 + 入库 ◀─────┘
```

**关键设计：**
- 单源刷新为后台异步任务，API 立即返回 `{"status": "refreshing"}`，前端不阻塞
- 主 API 失败自动 fallback 到公共实例
- 爬虫层使用 `requests`（httpx 与 NewsNow Nitro 服务器不兼容）
- 双层缓存：NewsNow SQLite（最新快照）+ 后端 SQLite（历史持久化）

---

## 更新日志

### v3.1.0
- **KB RAG 短期记忆**：LangGraph StateGraph + SummarizationMiddleware，多轮对话上下文自动保持
- **查询意图识别与重写**：规则前置过滤（代词/短句/祈使句）+ LLM 精确判断，追问时自动消解代词补全查询
- **检索内容不入历史**：RAG context 每轮临时注入，仅 Human/AIMessage 持久化，避免文档片段摘要质量损失
- **条件检索**：纯解释性追问跳过检索，复用上轮结果，节省嵌入 API 调用
- **单会话模式**：每个知识库固定一个会话，支持一键清空（同时清理消息 + checkpoint）
- **独立 RAG 记忆库**：`data/rag_memory.db` 与 Agent 记忆库隔离
- **旧历史自动迁移**：首次请求时从 kb_messages 加载旧对话注入 LangGraph checkpointer
- **SSE 新增 rewrite 事件**：查询被重写时前端可展示原文与改写后的查询对比

### v3.0.0
- **智能体短期记忆**：LangGraph Agent + SummarizationMiddleware + AsyncSqliteSaver
- **会话管理**：多会话切换、历史恢复、会话列表侧边栏、硬删除清理
- **联网搜索**：Kimi / Tavily 双引擎，前端一键开关
- **AI 配图**：DashScope qwen-image 自动生成文章配图
- **异步任务面板**：后台任务状态实时追踪
- **关键词过滤设置**：前端可视化管理过滤词组

### v2.1.0
- NewsNow Docker 中台：本地部署替代公网 API，端口 4444
- 爬虫层 httpx → requests：解决与 Nitro 服务器 502 兼容性问题
- 自动 fallback：主 API 失败自动切换到公共实例
- 单源刷新非阻塞：`POST /api/news/refresh/{source}` 后台异步执行
- 正文内容展示：优先后端抓取正文，纯文本渲染替代 iframe
- JS 渲染源标记：`toutiao`、`cankaoxiaoxi` 标记为动态加载
- 后端启动健康检查：自动等待 NewsNow 就绪（最多 10 秒）

### v2.0.0
- 多知识库支持：独立创建、独立向量索引、独立会话
- RAG 对话：语义检索 + 来源引用
- 会话持久化：对话记录永久保存
- 智能体：8工具函数调用

### v1.0.0
- 多源新闻爬取
- AI 多风格解读
- 多平台发布模拟
- SQLite 数据持久化

---

## 许可证

MIT License
