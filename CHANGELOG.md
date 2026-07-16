# Changelog

## [v1.0.0] — 2026-07-16

### 核心功能

- 8 个 AI Agent：案件分析、违法识别、赔偿计算、合同审查、证据分析、文书起草、仲裁指导、维权路线
- 法律条文库：31 条劳动法/劳动合同法/社保法/调解仲裁法（YAML + 2-gram 内存索引）
- 10 个真实劳动仲裁案例（违法解除/双倍工资/拖欠/加班费/试用期/社保/工伤/竞业/年假/调岗）
- AI 咨询对话（SSE 流式 + 信息采集表单 + 意图路由 + Agent 级联执行）
- 赔偿计算器（双倍工资/N/2N/加班费 1.5x-3x，完整公式 + 计算过程）
- 合同审查（文件上传 + PaddleOCR + AI 逐条风险分析）
- 证据分析（文件上传 + OCR + 证据强度评分 + 证据链完整性评估）
- 法律文书生成 + PDF 下载（xhtml2pdf/WeasyPrint 双引擎，A4 中文排版）
- 案件管理系统（CRUD + JSONB 画像 + 维权路线 + 快捷操作）

### 可替换 AI 模型

- LLM 适配器层：支持 DeepSeek/通义千问/智谱GLM/Moonshot/GPT/Ollama/任意 OpenAI 兼容接口
- 切换模型只需改 `.env`，无需改代码

### Web 前端

- Next.js 15 + Tailwind v4 响应式设计
- 移动端底部 Tab / PC 端顶部导航自适应
- 12 个页面路由（首页/AI咨询/工具箱/赔偿/合同/证据/案件/案件详情/文书/个人中心/订阅）
- 设计系统："极简·信"（#FAFAFA + #1E40AF + 系统字体栈）

### 管理后台

- Dashboard 数据面板（用户数/案件数/付费订单/营收）
- 用户管理表格 + VIP 开关
- 案件管理表格 + 风险等级标签

### 安全

- 管理员鉴权（JWT + role 校验，未认证→401，非管理员→403）
- CORS 限制（不可配置 `*`）
- 速率限制（全局 30次/分钟 + AI咨询 10次/分钟）
- 输入长度校验（AI 消息 max 10000 字符）
- 文件上传限制（10MB + 9 种类型白名单）
- 手机号 AES-256 加密存储
- 免费版 5 次/天咨询限制

### 开发体验

- 44+ 个 pytest 测试，0 warnings
- GitHub Actions CI-ready
- Dependabot（pip + npm 每周自动检查）
- MIT License + CONTRIBUTING.md + DISCLAIMER.md
- 一键初始化脚本（`bash scripts/setup.sh`）
- Docker Compose 部署编排

---

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。
