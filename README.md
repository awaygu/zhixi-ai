# 📰 新闻爬取 · AI解读 · 发布系统

一站式新闻采集、AI多风格解读、多平台发布的现代化全栈应用。

## 🏗️ 项目结构

```
D:\ai\
├── backend/              # FastAPI 后端
│   ├── app.py            # FastAPI 主入口 + API 路由
│   ├── config.py         # 配置文件
│   ├── requirements.txt  # Python 依赖
│   ├── crawlers/         # 8个新闻来源爬虫（模拟数据）
│   ├── agents/           # AI解读模块（LangChain/模拟）
│   ├── database.py       # SQLite 持久化层
│   └── publishers/       # 3个平台发布器（模拟）
├── frontend/             # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── App.vue       # 三列主布局
│   │   ├── components/   # NewsList / ChatPanel / PublishPanel
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── api/          # Axios API 封装
│   │   └── types/        # TypeScript 类型定义
│   └── ...               # Vite / TS 配置
└── README.md
```

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **爬虫模块** | 8个新闻来源（财联社热门/电报、华尔街见闻、新华网、澎湃、头条、微博、抖音），优先抓取真实网站，失败后 fallback 到模拟数据 |
| **AI解读** | 支持3种风格：小红书风（✨emoji+种草）、公众号风（📰深度长文）、抖音风（🎬短平快） |
| **聊天解读** | 选中新闻后，直接向AI提问，基于新闻上下文回答 |
| **文章生成** | 选择多条新闻 → 选择风格 → 一键生成完整解读文章 |
| **发布系统** | 模拟发布到小红书、微信公众号、抖音，记录发布状态 |
| **数据持久化** | 新闻、文章、发布记录自动持久化到 SQLite，重启不丢失 |

## 🚀 启动指南

### 后端（FastAPI）

```bash
cd D:\ai\backend

# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端默认运行在 **http://localhost:8000**，Swagger文档：http://localhost:8000/docs

后端启动后会自动爬取所有来源的模拟新闻数据。

### 前端（Vue 3 + Vite）

```bash
cd D:\ai\frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认运行在 **http://localhost:5173**，自动代理 `/api` 请求到后端。

### 📦 生产构建

```bash
cd D:\ai\frontend
npm run build
# 输出到 frontend/dist/，可用 nginx 或其他静态服务器部署
```

## 🔌 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news?source=xxx` | 获取新闻，支持来源过滤 |
| GET | `/api/sources` | 获取支持的来源列表 |
| POST | `/api/interpret` | AI解读单条新闻 |
| POST | `/api/chat` | 聊天式解读 |
| POST | `/api/generate_article` | 生成完整解读文章 |
| POST | `/api/publish` | 发布文章到平台 |
| GET | `/api/articles` | 获取已生成的文章 |
| GET | `/api/publish_log` | 获取发布记录 |

## 🎨 支持风格

| 风格 | 关键词 | 适用场景 |
|------|--------|----------|
| `xiaohongshu` | ✨ emoji 丰富、种草语气、标签 | 小红书笔记 |
| `wechat_mp` | 📰 深度长文、标题党、专业分析 | 公众号文章 |
| `douyin` | 🎬 短平快、抓眼球、口播稿 | 抖音短视频 |

## ⚠️ 说明

- 爬虫优先尝试抓取真实网站内容，如请求失败（反爬/网络问题）则自动 fallback 到模拟数据。
- AI解读模块默认使用 **模拟响应**（`mock=True`），如需接入真实 LLM：
  1. 在 `backend/.env` 中配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 等参数
  2. 将 `app.py` 中的 `NewsInterpreter(mock=True)` 改为 `NewsInterpreter(mock=False)`
- 所有配置（LLM、服务器、爬虫间隔等）统一在 `backend/config.py` 中管理，通过 `.env` 覆盖。
- 数据自动持久化到 `backend/news_ai.db`（SQLite），重启服务后自动加载。
- 发布器当前为模拟实现，不涉及真实平台 API 调用。
- 前端使用 Element Plus 组件库，已配置中文语言包；AI 输出支持 Markdown 渲染。

---

*由 AI 自动生成 🦾*
