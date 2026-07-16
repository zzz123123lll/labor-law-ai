# 如何配置 AI 模型

本项目已内置完整的劳动法专业知识（法律条文库、8 个分析 Agent、赔偿计算公式、文书模板等）。
**你只需要配好 AI API，所有功能自动可用。**

## 3 步上手

### 1. 复制环境变量

```bash
cd fastapi-server
cp .env.example .env
```

### 2. 填入你的 AI API Key

编辑 `.env`，修改这 4 行：

```env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-你的key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

### 3. 启动

```bash
cd fastapi-server
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

访问 `http://localhost:8000/api/health` 确认启动成功。

---

## 支持的 AI 模型

只要接口兼容 OpenAI 格式（`/v1/chat/completions`），改 2 行环境变量即可切换：

| 模型 | LLM_PROVIDER | LLM_BASE_URL | LLM_MODEL |
|------|-------------|-------------|-----------|
| DeepSeek | deepseek | https://api.deepseek.com | deepseek-chat |
| 通义千问 | qwen | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus |
| 智谱 GLM | custom | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| Moonshot | custom | https://api.moonshot.cn/v1 | moonshot-v1-8k |
| OpenAI | openai | https://api.openai.com/v1 | gpt-4o |
| 本地 Ollama | custom | http://localhost:11434/v1 | qwen2.5:7b |
| 任何兼容接口 | custom | 你的接口地址 | 你的模型名 |

**切换示例**——换成通义千问：

```env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-你的阿里云key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

不需要改任何代码。

---

## 需要适配的 AI 内容 vs 已内置内容

| 需要你配置 | 已内置（无需动） |
|-----------|----------------|
| LLM_API_KEY（必填） | 劳动法条文库（31 条 YAML） |
| LLM_BASE_URL（接口地址） | 8 个分析 Agent Prompt |
| LLM_MODEL（模型名） | 赔偿计算公式引擎 |
| | 仲裁申请书等文书模板 |
| | 违法识别规则 |
| | 案件管理系统 |
| | Web 前端 + 管理后台 |

---

## 如果你的 AI 接口不是 OpenAI 格式

在 `fastapi-server/app/ai/` 下新建一个文件，继承 `BaseLLMAdapter`，实现 `chat()` 方法即可。

示例——创建一个通义千问原生接口适配器：

```python
# app/ai/qwen_native.py
from app.ai.base import BaseLLMAdapter, ChatMessage, ChatResult, LLMError
from app.config import settings
import httpx

class QwenNativeAdapter(BaseLLMAdapter):
    name = "qwen_native"

    async def chat(self, messages, **kwargs):
        # 你的通义千问原生 API 调用逻辑
        ...

# 然后在 app/ai/adapters.py 的 ADAPTERS 字典中注册：
# "qwen_native": QwenNativeAdapter
```

---

## 费用参考

以 DeepSeek 为例：

| 操作 | 估算 token | 费用 |
|------|-----------|------|
| 一次案件分析 | ~2000 | ~¥0.001 |
| 一次赔偿计算 | ~1000 | ~¥0.0005 |
| 一次合同审查 | ~3000 | ~¥0.0015 |

DeepSeek 价格约 ¥0.14/百万 token（输入）——日常使用几乎免费。

---

## 问题排查

| 症状 | 检查 |
|------|------|
| AI 返回"服务调用失败" | `.env` 中 `LLM_API_KEY` 是否填写？网络是否通？ |
| AI 回复乱码 | `LLM_MODEL` 是否正确？接口是否支持中文？ |
| 想用付费功能 | 配好 `WECHAT_*` 和 `WXPAY_*` 环境变量 |
