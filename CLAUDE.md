# 劳动法智能维权 AI Agent

## 设计系统

所有视觉或 UI 决策前必须先读 DESIGN.md。字体、颜色、间距、美学方向均在此定义。未经用户明确批准不得偏离。

## 项目结构

```
labor-law-ai/
├── fastapi-server/    # Python FastAPI 后端
├── web-app/           # Next.js 用户端（H5）
├── admin-panel/       # Next.js 管理后台
├── DESIGN.md          # 设计系统
├── docker-compose.yml # 部署编排
└── nginx.conf         # 反向代理
```
