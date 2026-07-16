"""应用配置，所有环境变量统一管理。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "劳动法智能维权AI"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://laborlaw:laborlaw@postgres:5432/laborlaw"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 微信开放平台
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    # 微信支付
    WXPAY_MCH_ID: str = ""
    WXPAY_API_KEY: str = ""
    WXPAY_NOTIFY_URL: str = ""

    # LLM 适配器（支持任何 OpenAI 兼容接口）
    LLM_PROVIDER: str = "deepseek"      # deepseek / openai / qwen / custom
    LLM_API_KEY: str = ""                # API Key（必填）
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"     # 模型名

    # DeepSeek API（向下兼容，已废弃——优先用 LLM_*）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # 腾讯云 COS
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_BUCKET: str = ""
    COS_REGION: str = "ap-guangzhou"

    # 短信
    SMS_SECRET_ID: str = ""
    SMS_SECRET_KEY: str = ""

    # 免费版限制
    FREE_DAILY_CHAT_LIMIT: int = 5
    FREE_MAX_CASES: int = 3

    # 专业版限制
    PRO_MAX_CASES: int = 20
    PRO_MONTHLY_CONTRACT_REVIEWS: int = 10

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# 向后兼容：旧的 DEEPSEEK_API_KEY → 新的 LLM_API_KEY
if not settings.LLM_API_KEY and settings.DEEPSEEK_API_KEY:
    settings.LLM_API_KEY = settings.DEEPSEEK_API_KEY
if settings.LLM_BASE_URL == "https://api.deepseek.com" and settings.DEEPSEEK_BASE_URL != "https://api.deepseek.com":
    settings.LLM_BASE_URL = settings.DEEPSEEK_BASE_URL
