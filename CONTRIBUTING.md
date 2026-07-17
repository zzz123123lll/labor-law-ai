# 贡献指南

感谢你想为劳动法智能维权 AI 项目做贡献！这份指南帮助你快速上手。

## 行为准则

- 尊重所有贡献者。就事论事，不人身攻击。
- 欢迎新手。任何水平的问题都值得认真回答。
- 劳动法领域专业性强——如果你不是法律背景，欢迎在代码、测试、文档方面贡献。

## 项目结构

```
labor-law-ai/
├── fastapi-server/        # Python FastAPI 后端
│   ├── app/
│   │   ├── ai/            # LLM 适配器（接入你自己的 AI）
│   │   ├── agents/        # 8 个劳动法 Agent
│   │   ├── legal_engine/  # 法律条文 + 案例索引
│   │   ├── api/           # REST 路由
│   │   ├── models/        # SQLAlchemy 模型
│   │   └── schemas/       # Pydantic 请求/响应
│   └── tests/             # pytest 测试
├── web-app/               # Next.js 用户端
├── admin-panel/           # Next.js 管理后台
├── DESIGN.md              # 设计系统说明
├── HOW_TO_CONFIGURE_AI.md # 接入 AI 指南
└── DISCLAIMER.md          # 免责声明
```

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/zzz123123lll/labor-law-ai.git
cd labor-law-ai

# 2. 一键初始化
bash scripts/setup.sh

# 3. 配置 AI（用自己的 key）
cp fastapi-server/.env.example fastapi-server/.env
# 编辑 .env，填入 LLM_API_KEY

# 4. 启动后端
cd fastapi-server && uvicorn app.main:app --reload

# 5. 启动前端（另一个终端）
cd web-app && npm run dev
```

## 开发流程

### 1. 创建分支

```bash
git checkout -b feat/你的功能名   # 新功能
git checkout -b fix/你的修复名    # 修 bug
```

### 2. 写代码 + 测试

- **后端**用 Python 3.12+，类型标注必须完整
- **前端**用 TypeScript，组件放 `components/` 目录
- **测试要求**：后端功能代码必须写 pytest 测试。纯 UI/Markdown/配置改动可豁免。

### 3. 跑测试

```bash
# 后端
cd fastapi-server
python -m pytest tests/ -v
# 期望：31 passed

# 前端
cd web-app
npm run build
# 期望：12 条路由全部编译通过
```

### 4. 提交

```bash
git commit -m "feat: 你的功能描述"
```

提交消息格式遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
feat: 新功能
fix: 修 bug
docs: 文档
test: 测试
refactor: 重构
```

### 5. 推送到你的 Fork

```bash
git push origin feat/你的功能名
```

### 6. 在 GitHub 上发起 Pull Request

PR 标题一句说清改了什么。描述里写清楚：改了什么、为什么这么改、怎么验证的。

## 可以贡献的方向

### 适合新手

| 方向 | 说明 |
|------|------|
| 补充法条 | 编辑 `legal_engine/data/laws/*.yaml`，扩展法律条文库 |
| 补充案例 | 编辑 `precedents/index.json`，添加公开的仲裁案例 |
| 完善文书模板 | 改进 Agent Prompt（`agents/*.py` 中的 `build_system_prompt`） |
| 修前端 Bug | 用户端 `web-app/` 下的 TypeScript 文件 |

### 中等难度

| 方向 | 说明 |
|------|------|
| 接入新 AI 模型 | 在 `app/ai/` 新建适配器，继承 `BaseLLMAdapter` |
| 新增 Agent | 新建 Agent 类 + 注册到 `registry.py` + 添加 ROUTER_RULES |
| PDF 排版优化 | 修改 `document_gen.py` 的 `_markdown_to_pdf()` HTML 模板 |
| 赔偿公式优化 | 修改 `compensation_calc.py` 的计算逻辑 |

### 高级

| 方向 | 说明 |
|------|------|
| 小程序移植 | 用 Taro 将 `web-app/` 转为微信小程序 |
| E2E 测试 | Playwright 前后端联合测试 |
| 性能优化 | 法律库2-gram索引优化、Agent并行执行 |

## 编码规范

### Python

- 遵循 PEP 8
- 类型标注完整（`mypy` 兼容）
- docstring 写中文
- API 路由文件不超过 200 行（提取到 services/）

### TypeScript

- 用 `"use client"` 标记客户端组件
- 颜色用 `var(--color-xxx)` 不硬编码
- 设计规范见 `DESIGN.md`

### 全局约束

- 法律条文 YAML 文件不存数据库（用内存索引）
- 所有 Agent 输出末尾拼接免责声明
- Agent name 必须与 `router.py` 的 key 一致

## 问题反馈

遇到 Bug 或有好想法？在 GitHub Issues 提出来。

如果你不确定怎么做、不确定想法合不合适——直接在 Issue 里问。不会有人觉得你问得太简单。

## 许可证

本项目使用 MIT License。你贡献的代码也受 MIT 约束。提交代码即表示你同意。
