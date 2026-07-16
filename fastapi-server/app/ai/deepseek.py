"""DeepSeek 适配器（兼容所有 OpenAI 接口格式的模型）。"""
import httpx
from app.ai.base import BaseLLMAdapter, ChatMessage, ChatResult, LLMError
from app.config import settings


class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek / OpenAI 兼容适配器。

    配置环境变量：
        LLM_API_KEY=sk-your-key
        LLM_BASE_URL=https://api.deepseek.com
        LLM_MODEL=deepseek-chat
    """

    name = "deepseek"

    async def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResult:
        msgs = [{"role": m.role, "content": m.content} for m in messages]

        async with httpx.AsyncClient(timeout=kwargs.get("timeout", 60.0)) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": msgs,
                    "temperature": kwargs.get("temperature", 0.3),
                    "max_tokens": kwargs.get("max_tokens", 4096),
                },
            )

        if resp.status_code >= 400:
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text)
            except Exception:
                msg = resp.text[:200]
            raise LLMError(f"AI 服务返回错误 HTTP {resp.status_code}: {msg}")

        data = resp.json()
        if "choices" not in data or not data["choices"]:
            raise LLMError("AI 服务返回空响应")

        return ChatResult(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", settings.LLM_MODEL),
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
        )
