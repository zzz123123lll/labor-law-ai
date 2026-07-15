# Design System — 劳动法智能维权 AI Agent

## Product Context
- **What this is:** 面向普通劳动者的 AI 劳动法律维权助手——输入问题，自动分析违法、计算赔偿、生成文书
- **Who it's for:** 遇到劳动争议的普通打工人，可能焦虑、信息不对称、第一次接触法律
- **Space/industry:** 法律科技 / 在线法律服务
- **Project type:** Web 移动端优先（H5），后续拓展小程序

## Aesthetic Direction
- **Direction:** 极简工业风——信·工具
- **Decoration level:** 极低——无渐变、无阴影堆叠、无圆角泛滥
- **Mood:** 安静、有力、可信。用户打开后大脑进入"行动模式"而非"浏览模式"
- **Core word:** 信——信任感是第一位的
- **Reference sites:** Linear, Notion, 裁判文书网

## Typography
- **Body:** system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif
- **Display/Heading:** same as body, weight:600
- **Mono/Data:** JetBrains Mono, monospace — 法条编号、赔偿金额用等宽
- **Scale (rem):** 0.625(10px辅助) / 0.75(12px小字) / 0.875(14px正文) / 1(16px) / 1.125(18px标题) / 1.25(20px大标题) / 1.5(24px hero)

## Color
- **Approach:** 极度克制——全篇无色，颜色仅用于功能语义

| 角色 | 色值 | 用途 |
|------|------|------|
| 背景 | `#FAFAFA` | 全局底色 |
| 卡片/输入 | `#FFFFFF` | 内容容器 |
| 主文字 | `#1A1A1A` | 所有正文 |
| 辅文字 | `#6B7280` | 时间戳、辅助信息 |
| 边框 | `#E5E7EB` | 分割线、卡片边框 |
| 强调蓝 | `#1E40AF` | 超链接、选中态、AI引用块 |
| 危险红 | `#DC2626` | 违法标记、高风险 |
| 成功绿 | `#059669` | 赔偿金额、胜诉标记 |

- **Dark mode:** 暂不建议——劳动法场景用户更熟悉白色文档

## Spacing
- **Base unit:** 4px
- **Density:** 舒适——信息密度高但不压迫
- **Scale:** xs(4) sm(8) md(12) lg(16) xl(20) 2xl(24) 3xl(32) 4xl(48)

## Layout
- **Approach:** 移动端单列、PC 端居中卡片流
- **Max content width:** 640px（手机全宽 + PC 居中）
- **Grid:** 单列，卡片内部堆叠
- **Border radius:** sm(4px, 输入框/按钮) md(8px, 卡片) lg(12px, 消息气泡)

## Motion
- **Approach:** 微交互 only
- **Duration:** 100ms (hover/active), 200ms (page transition)
- **No:** scroll animations, parallax, page transitions

## AI Chat Specific
- 用户气泡：蓝底白字，右对齐，圆角 12/4/12/12
- AI 气泡：白底黑字+灰边框，左对齐，圆角 4/12/12/12
- 法条引用：等宽字体，左侧 2px 蓝色竖线，浅灰背景
- 报告卡片：白色卡片 + 浅灰边框 + 蓝色顶部条 3px

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-15 | 初始设计系统 | /design-consultation，"信·工具"方向，极简工业风 |
| 2026-07-15 | 无暗色模式 | 劳动法用户更习惯白色文档风格 |
| 2026-07-15 | 单列 640px 布局 | 移动优先，PC 上也不会过宽分散注意力 |
