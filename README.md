# 劳动法智能维权 AI Agent

面向普通劳动者的法律维权辅助工具。覆盖从"遇到劳动问题"到"完成仲裁文书"的全流程 AI 辅助。

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 前端（用户端） | Next.js 15 | Web/H5 响应式，支持后续迁移小程序 |
| 管理后台 | Next.js 15 + Ant Design 5 | 数据面板、用户管理、内容管理 |
| 后端 | Python FastAPI（单体） | AI Agent 调度 + REST API |
| 数据库 | PostgreSQL 17（pgvector） | 结构化数据 + 向量检索 |
| 缓存 | Redis 7 | Session / 速率限制 / 任务队列 |
| AI 推理 | DeepSeek API | 核心 AI 对话、分析、文书生成 |
| OCR | PaddleOCR | 合同/证据图片文字识别 |
| 文件存储 | 腾讯云 COS | 用户上传文件存储 |
| 部署 | Docker Compose + Nginx | 腾讯云轻量服务器一键部署 |

## 项目结构

```
labor-law-ai/
├── fastapi-server/         # 后端 API 服务（Python FastAPI）
│   ├── app/
│   │   ├── api/            # 路由层（认证、案件、咨询、合同审查等）
│   │   ├── agents/         # AI Agent 层（8 个 Agent + Router）
│   │   ├── legal_engine/   # 法律条文引擎（YAML 静态数据 + 内存索引）
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   └── services/       # 业务逻辑层
│   ├── templates/          # 文书 Jinja2 模板
│   ├── tests/              # 测试
│   └── Dockerfile
├── web-app/                # 用户端 Web/H5（Next.js 15）
│   ├── app/                # 页面路由
│   ├── components/         # 组件（对话、报告、上传、合同等）
│   ├── hooks/              # 自定义 hooks（useChat、useAuth 等）
│   └── Dockerfile
├── admin-panel/            # 管理后台（Next.js 15 + Ant Design）
│   └── Dockerfile
├── nginx.conf              # Nginx 反向代理配置
├── docker-compose.yml      # Docker Compose 编排（5 个服务）
├── scripts/
│   └── setup.sh            # 一键初始化脚本
└── ssl/                    # SSL 证书目录（Let's Encrypt）
```

## 本地开发

### 前置条件

- Python 3.12+
- Node.js 20+
- PostgreSQL 17（可选，Docker 运行）
- Redis 7（可选，Docker 运行）

### 后端

```bash
# 克隆后先初始化
bash scripts/setup.sh

# 或手动：
cd fastapi-server
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API 文档自动生成于 http://localhost:8000/docs

### 用户端前端

```bash
cd web-app
npm install
npm run dev
```

### 管理后台

```bash
cd admin-panel
npm install
npm run dev
```

## Docker 部署

### 前置条件

- 服务器安装 Docker + Docker Compose
- 域名已备案并指向服务器 IP
- 准备好 SSL 证书

### 步骤

```bash
# 1. 克隆代码
git clone <repo-url> labor-law-ai
cd labor-law-ai

# 2. 配置环境变量
cp fastapi-server/.env.example fastapi-server/.env
# 编辑 .env，填入 DeepSeek API Key、腾讯云 COS 密钥等

# 3. 放置 SSL 证书到 ssl/ 目录
#   ssl/fullchain.pem
#   ssl/privkey.pem

# 4. 修改 docker-compose.yml 中的域名
#   将 your-domain.com 替换为实际域名

# 5. 启动全部服务
docker compose up -d

# 6. 查看日志
docker compose logs -f
```

### 服务端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|---|---|---|---|
| Nginx | 80/443 | 80/443 | 反向代理 + SSL 终结 |
| Backend | 8000 | - | FastAPI 后端 API |
| Web | 3000 | - | 用户端前端 |
| Admin | 3000 | - | 管理后台 |
| PostgreSQL | 5432 | - | 数据库 |
| Redis | 6379 | - | 缓存 |

## 环境变量说明

主要环境变量定义在 `fastapi-server/.env` 中：

| 变量 | 说明 | 示例 |
|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxx` |
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://laborlaw:xxx@postgres:5432/laborlaw` |
| `REDIS_URL` | Redis 连接串 | `redis://redis:6379/0` |
| `COS_SECRET_ID` | 腾讯云 COS SecretId | `AKIDxxxx` |
| `COS_SECRET_KEY` | 腾讯云 COS SecretKey | `xxxx` |
| `COS_BUCKET` | COS Bucket 名称 | `labor-law-xxxx` |
| `COS_REGION` | COS 地域 | `ap-guangzhou` |
| `WECHAT_APP_ID` | 微信开放平台 AppId | `wxxxxx` |
| `WECHAT_APP_SECRET` | 微信开放平台 AppSecret | `xxxx` |
| `JWT_SECRET` | JWT 签名密钥 | `your-random-secret` |
| `DB_PASSWORD` | PostgreSQL 密码（docker-compose 用） | `laborlaw` |

## 功能模块

### P1 MVP（已实现）
- AI 咨询对话（SSE 流式）
- 违法识别
- 赔偿计算
- 案件管理

### P2 进阶
- 合同审查
- 证据分析（含 OCR）
- 文书生成

### P3 完善
- 仲裁指导
- 维权路线
- 企业反制分析
- 案例检索

### P4 运营
- 管理后台
- 付费系统
- 提醒系统

## 免责声明

**本系统不替代律师正式法律意见。** 所有 AI 分析结果仅供用户参考，不应作为正式法律行动的依据。涉及重大权益的法律事务，请务必咨询执业律师。

---

Built with [FastAPI](https://fastapi.tiangolo.com/) + [Next.js](https://nextjs.org/) + [DeepSeek](https://deepseek.com/)
