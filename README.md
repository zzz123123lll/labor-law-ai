# 劳动法智能维权 AI Agent

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue)](https://python.org)
[![Last commit](https://img.shields.io/github/last-commit/zzz123123lll/labor-law-ai)](https://github.com/zzz123123lll/labor-law-ai/commits/master)
[![CI](https://github.com/zzz123123lll/labor-law-ai/actions/workflows/test.yml/badge.svg)](https://github.com/zzz123123lll/labor-law-ai/actions/workflows/test.yml)
[![Tests](https://img.shields.io/badge/tests-49%20passed-green)](https://github.com/zzz123123lll/labor-law-ai)

面向普通劳动者的 AI 法律维权工具。输入你的劳动问题，AI 自动分析违法、计算赔偿、生成仲裁文书。

> ⚡ **接入你自己的 AI 即可使用** — 支持 DeepSeek / 通义千问 / 智谱 GLM / GPT-4o / Ollama / 任意 OpenAI 兼容接口。 [配置指南 →](./HOW_TO_CONFIGURE_AI.md)

## 特点

- 🧠 **8 个专业 Agent** — 案件分析、违法识别、赔偿计算、合同审查、证据分析、文书起草、仲裁指导、维权路线，级联执行
- 📜 **内置法律库** — 4 部法律 71 条 YAML 条文 + 2-gram 倒排索引检索
- 🤖 **可替换 AI** — 适配器层支持 DeepSeek / 通义千问 / GLM / GPT / Ollama，只改 `.env` 不改代码
- 📱 **响应式 Web** — 移动端底部 Tab + PC 端顶部导航
- 📄 **AI 咨询** — SSE 流式输出 + 结构化数据提取 + 赔偿自动计算
- 🔒 **认证安全** — 手机号 + JWT 双 token + Fernet 加密 + slowapi 限流

## 3 分钟上手

```bash
# 1. 安装后端依赖
cd fastapi-server && pip install -e ".[dev]"

# 2. 配置 AI
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY（DeepSeek 注册即送 500 万 token）

# 3. 启动后端
uvicorn app.main:app --reload

# 4. 启动前端（另一个终端）
cd ../web-app && npm install && npm run dev
```

浏览器打开 `http://localhost:3000`

## 切换 AI 模型

改 `.env` 即可，不需要改任何代码：

```env
# DeepSeek（默认）
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# 通义千问
# LLM_PROVIDER=qwen
# LLM_API_KEY=sk-your-key
# LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# LLM_MODEL=qwen-plus

# 本地 Ollama
# LLM_PROVIDER=ollama
# LLM_API_KEY=ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=qwen2.5:7b
```

详见 [HOW_TO_CONFIGURE_AI.md](./HOW_TO_CONFIGURE_AI.md)

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 16 + React 19 + Tailwind v4 + TypeScript |
| 后端 | Python FastAPI + Pydantic v2 |
| AI 层 | OpenAI 兼容适配器（可替换任意模型） |
| 数据库 | SQLite（开发）/ PostgreSQL 17 + pgvector（生产） |
| OCR | PaddleOCR |
| 部署 | Docker Compose + Nginx + Redis |

## 项目结构

```
labor-law-ai/
├── fastapi-server/
│   ├── app/
│   │   ├── ai/              # LLM 适配器层
│   │   ├── agents/          # 8 个劳动法 Agent（含路由器）
│   │   ├── legal_engine/    # 法律库（71 条 YAML + 内存索引 + 10 个案例）
│   │   ├── api/             # 10 个 REST API 路由模块
│   │   ├── models/          # 9 个 SQLAlchemy 数据模型
│   │   └── schemas/         # 9 个 Pydantic 请求/响应模块
│   └── tests/               # 12 个测试文件，49 个用例
├── web-app/                 # 用户端（9 个页面）
├── admin-panel/             # 管理后台（3 个页面）
├── .github/workflows/       # CI（GitHub Actions）
├── DESIGN.md                # 视觉设计系统
└── HOW_TO_CONFIGURE_AI.md   # AI 配置指南
```

## 功能状态

| 模块 | 状态 | 说明 |
|------|------|------|
| AI 咨询对话 | ✅ | SSE 流式，8 Agent 级联 |
| 违法识别 | ✅ | 5 类自动检测 |
| 赔偿计算 | ✅ | 公式 + 表格 + 结构化提取 |
| 案件管理 | ✅ | CRUD + JSONB 画像 |
| 用户认证 | ✅ | 手机号 + JWT + Fernet 加密 |
| 合同审查 | ✅ | 上传 + OCR + AI 审查 |
| 证据分析 | ✅ | 上传 + OCR + 强度评分 |
| 文书生成 | ✅ | Markdown 模板输出 |
| PDF 下载 | ✅ | xhtml2pdf/WeasyPrint 双引擎 |
| 法律条文 | ✅ | 4 部法律 71 条，WebSearch 校验 |
| 案例库 | ✅ | 10 个劳动仲裁典型案例 |
| 管理后台 | ⚠️ | Dashboard + 用户 + 案件（admin 认证待完善） |
| 支付系统 | ⚠️ | 三档定价 Mock，未接入真实支付 |
| 前端测试 | ❌ | 待实现 |
| 前端 Error Boundary | ❌ | 待实现 |
| CI 质量门控 | ⚠️ | 有 lint 依赖但未配置 ruff/pre-commit |
| 健康检查 | ⚠️ | 仅 ping，未检查 DB/Redis/AI 连通性 |

## 已内置的专业化内容

| 模块 | 内容 |
|------|------|
| 法律条文 | 71 条 YAML（劳动法/劳动合同法/社保法/调解仲裁法） |
| Agent Prompt | 8 个领域完整中文 System Prompt |
| 赔偿公式 | 双倍工资 / 经济补偿 N / 违法解除 2N / 加班费 1.5x-3x |
| 文书模板 | 仲裁申请书 / 投诉信 / 证据清单 |
| 违法检测 | 工资/合同/辞退/加班/社保 5 类自动识别 |
| 案例匹配 | 标签 + 关键词检索 |

## 免责声明

**本系统不替代律师正式法律意见。** 所有 AI 分析仅供用户参考。涉及重大权益请咨询执业律师。
