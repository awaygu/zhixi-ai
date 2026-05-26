# 📰 新闻爬取 · AI解读 · 发布系统

一站式新闻采集、AI多风格解读、多平台发布的现代化全栈应用。

---

## 🛠️ 技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端** | FastAPI | ^0.104 | 高性能 Python Web 框架 |
| **前端** | Vue 3 | ^3.4 | 渐进式 JavaScript 框架 |
| **前端** | TypeScript | ^5.3 | 类型安全 |
| **前端** | Vite | ^5.0 | 快速构建工具 |
| **前端** | Element Plus | ^2.4 | UI 组件库 |
| **前端** | Pinia | ^2.1 | 状态管理 |
| **数据库** | SQLite | - | 轻量级嵌入式数据库 |
| **AI** | LangChain | ^0.1 | LLM 应用框架 |

---

## 🏗️ 项目结构

```
news-interpretation/
├── backend/                    # FastAPI 后端服务
│   ├── app.py                 # 主入口 + 应用配置
│   ├── config.py              # 全局配置管理
│   ├── database.py            # SQLite 数据库操作
│   ├── prompts.py             # AI 提示词管理
│   ├── prompts.yaml           # 提示词模板配置
│   ├── keywords.txt           # 关键词过滤列表
│   ├── requirements.txt       # Python 依赖
│   ├── .env                   # 环境变量（需自行创建）
│   ├── agents/                # AI 解读模块
│   │   ├── __init__.py
│   │   ├── interpreter.py     # 新闻解读器
│   │   └── style_manager.py   # 风格管理器
│   ├── crawlers/              # 新闻爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py            # 爬虫基类
│   │   ├── cls_hot.py         # 财联社热门
│   │   ├── cls_telegraph.py   # 财联社电报
│   │   ├── wallstreet.py      # 华尔街见闻
│   │   ├── cankao.py          # 参考消息
│   │   ├── pengpai.py         # 澎湃新闻
│   │   ├── toutiao.py         # 今日头条
│   │   ├── weibo.py           # 微博热搜
│   │   ├── douyin.py          # 抖音热点
│   │   ├── newsnow.py         # NewsNow RSS
│   │   ├── rss.py             # 通用 RSS 爬虫
│   │   └── filter.py          # 内容过滤器
│   ├── publishers/            # 发布器模块
│   │   ├── __init__.py
│   │   ├── base.py            # 发布器基类
│   │   ├── xiaohongshu.py     # 小红书发布器
│   │   ├── wechat_mp.py       # 微信公众号发布器
│   │   └── douyin_pub.py      # 抖音发布器
│   └── routers/               # API 路由
│       ├── __init__.py
│       ├── deps.py            # 依赖注入
│       ├── news.py            # 新闻相关接口
│       ├── interpret.py       # AI 解读接口
│       ├── publish.py         # 发布接口
│       ├── schedule.py        # 定时任务接口
│       ├── keywords.py        # 关键词管理接口
│       └── prompts.py         # 提示词管理接口
├── frontend/                   # Vue 3 前端应用
│   ├── src/
│   │   ├── App.vue            # 根组件（三列布局）
│   │   ├── main.ts            # 入口文件
│   │   ├── api/               # API 请求封装
│   │   │   └── index.ts
│   │   ├── components/        # 组件
│   │   │   ├── NewsList.vue   # 新闻列表
│   │   │   ├── NewsDetail.vue # 新闻详情
│   │   │   ├── ChatPanel.vue  # 聊天解读面板
│   │   │   ├── GeneratePanel.vue # 文章生成面板
│   │   │   ├── PublishPanel.vue # 发布面板
│   │   │   └── RightPanel.vue # 右侧工具栏
│   │   ├── stores/            # Pinia 状态管理
│   │   │   └── index.ts
│   │   └── types/             # TypeScript 类型定义
│   │       └── index.ts
│   ├── index.html             # HTML 模板
│   ├── package.json           # Node 依赖
│   ├── vite.config.ts         # Vite 配置
│   ├── tsconfig.json          # TypeScript 配置
│   └── dist/                  # 构建产物（npm run build 生成）
├── .gitignore                # Git 忽略配置
└── README.md                  # 项目说明文档
```

---

## ✨ 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **多源新闻爬取** | 支持 10+ 新闻来源，自动去重和过滤 | ✅ |
| **AI 智能解读** | 基于 LLM 的新闻深度分析 | ✅ |
| **多风格输出** | 小红书/公众号/抖音三种风格 | ✅ |
| **聊天式解读** | 基于新闻上下文的对话交互 | ✅ |
| **文章生成** | 多条新闻合成完整解读文章 | ✅ |
| **多平台发布** | 模拟发布到小红书/公众号/抖音 | ✅ |
| **定时任务** | 自动定时爬取和生成内容 | ✅ |
| **数据持久化** | SQLite 本地存储，重启不丢失 | ✅ |

---

## 🚀 快速开始

### 环境要求

- **Python**: >= 3.10
- **Node.js**: >= 18.0
- **npm**: >= 9.0

### 1. 克隆项目

```bash
git clone <repository-url>
cd news-interpretation
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件（可选）
# cp .env.example .env
# 编辑 .env 配置 LLM 等参数

# 启动服务
python app.py
```

后端默认运行在 **http://localhost:8000**

- Swagger 文档: http://localhost:8000/docs
- Redoc 文档: http://localhost:8000/redoc

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认运行在 **http://localhost:5173**

### 4. 生产构建

```bash
cd frontend
npm run build
# 构建产物输出到 frontend/dist/
```

---

## 🔧 配置说明

### 环境变量（backend/.env）

```env
# LLM 配置
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 爬虫配置
NEWSNOW_CRAWL_INTERVAL=3600
RSS_CRAWL_INTERVAL=1800

# 定时任务
SCHEDULE_ENABLED=true
```

### 配置优先级

1. 环境变量（`.env` 文件）
2. `config.py` 中的默认值

---

## 🔌 API 接口

### 新闻相关

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/news` | 获取新闻列表 | `source`（可选）, `limit`（可选） |
| GET | `/api/news/{id}` | 获取单条新闻 | `id`（必填） |
| GET | `/api/sources` | 获取支持的来源列表 | - |
| POST | `/api/news/crawl` | 手动触发爬取 | `source`（可选） |

### AI 解读

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| POST | `/api/interpret` | AI 解读单条新闻 | `news_id`, `style` |
| POST | `/api/chat` | 聊天式解读 | `news_id`, `question` |
| POST | `/api/generate_article` | 生成完整文章 | `news_ids`, `style`, `title`（可选） |

### 发布相关

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| POST | `/api/publish` | 发布文章 | `article_id`, `platform` |
| GET | `/api/articles` | 获取已生成的文章 | - |
| GET | `/api/publish_log` | 获取发布记录 | `article_id`（可选） |

### 管理接口

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/keywords` | 获取关键词列表 | - |
| POST | `/api/keywords` | 添加关键词 | `word`, `type` |
| DELETE | `/api/keywords/{id}` | 删除关键词 | `id` |
| GET | `/api/prompts` | 获取提示词列表 | - |
| PUT | `/api/prompts/{style}` | 更新提示词 | `style`, `content` |
| GET | `/api/schedule/status` | 获取定时任务状态 | - |
| POST | `/api/schedule/toggle` | 开启/关闭定时任务 | `enabled` |

---

## 🎨 支持风格

| 风格 | 标识符 | 特点 | 适用场景 |
|------|--------|------|----------|
| 小红书风 | `xiaohongshu` | ✨ emoji 丰富、种草语气、话题标签 | 小红书笔记 |
| 公众号风 | `wechat_mp` | 📰 深度长文、标题党、专业分析 | 微信公众号 |
| 抖音风 | `douyin` | 🎬 短平快、抓眼球、口播稿 | 抖音短视频 |

---

## 📁 新闻来源

| 来源 | 标识符 | 说明 |
|------|--------|------|
| 财联社热门 | `cls_hot` | 财经新闻 |
| 财联社电报 | `cls_telegraph` | 即时资讯 |
| 华尔街见闻 | `wallstreet` | 国际财经 |
| 参考消息 | `cankao` | 国际新闻 |
| 澎湃新闻 | `pengpai` | 综合新闻 |
| 今日头条 | `toutiao` | 综合资讯 |
| 微博热搜 | `weibo` | 热点话题 |
| 抖音热点 | `douyin` | 短视频热点 |

---

## 📦 部署方案

### 方案一：Nginx + Uvicorn（推荐）

**后端配置（gunicorn + uvicorn）**

```bash
# 安装 gunicorn
pip install gunicorn

# 启动生产服务
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Nginx 配置**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket 支持（用于流式响应）
    location /api/chat {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 方案二：Docker 部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_BASE_URL=${LLM_BASE_URL}
    volumes:
      - ./backend:/app
      - db-data:/app/data

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend

volumes:
  db-data:
```

---

## 🐛 常见问题

### Q1: 前端无法连接后端？

确保后端服务已启动，并检查 `vite.config.ts` 中的代理配置：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

### Q2: AI 解读返回模拟数据？

默认使用模拟模式，如需接入真实 LLM：

1. 在 `backend/.env` 配置 `LLM_API_KEY` 和 `LLM_BASE_URL`
2. 修改 `app.py` 中 `NewsInterpreter(mock=True)` 为 `NewsInterpreter(mock=False)`

### Q3: 爬虫无法获取真实数据？

部分网站有反爬机制，爬虫会自动 fallback 到模拟数据。可尝试：
- 设置合理的请求间隔
- 添加 User-Agent 伪装
- 使用代理 IP

---

## 📝 更新日志

### v1.0.0 (2024-01-xx)
- 初始版本
- 支持多源新闻爬取
- AI 多风格解读
- 多平台发布模拟
- SQLite 数据持久化

---

## 📄 许可证

MIT License

---

*由 AI 驱动开发 🦾*
