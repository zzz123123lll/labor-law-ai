"""LLM 适配器工厂。根据配置自动选择适配器。

支持的方式（按优先级）：
1. LLM_PROVIDER 环境变量指定适配器名称（deepseek / openai / qwen / custom）
2. LLM_BASE_URL 如果包含 "deepseek" 则自动选择 deepseek 适配器
3. 默认使用 deepseek 适配器（兼容所有 OpenAI 接口格式）

添加新模型极简：
    只要是 OpenAI 兼容接口（deepseek/qwen/glm/moonshot/...），
    改 LLM_BASE_URL + LLM_MODEL 即可，无需改代码。

添加非 OpenAI 接口（如文心一言原生 API）：
    在 app/ai/ 下新建适配器类，继承 BaseLLMAdapter 实现 chat()，
    然后在 ADAPTERS 字典中注册。
"""
from app.ai.base import BaseLLMAdapter
from app.ai.deepseek import DeepSeekAdapter
from app.config import settings

# 所有适配器注册表
ADAPTERS: dict[str, type[BaseLLMAdapter]] = {
    "deepseek": DeepSeekAdapter,
    "openai": DeepSeekAdapter,   # OpenAI 接口完全兼容
    "custom": DeepSeekAdapter,   # 任何 OpenAI 兼容接口
}

# 当前活跃的适配器单例
_adapter: BaseLLMAdapter | None = None


def get_llm() -> BaseLLMAdapter:
    """获取当前配置的 LLM 适配器（单例）。"""
    global _adapter
    if _adapter is not None:
        return _adapter

    provider = settings.LLM_PROVIDER.lower()
    adapter_cls = ADAPTERS.get(provider, DeepSeekAdapter)
    _adapter = adapter_cls()
    return _adapter
