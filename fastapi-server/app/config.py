"""应用配置，所有环境变量统一管理。"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "劳动法智能维权AI"
    DEBUG: bool = False

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

    # DeepSeek API
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

    class Config:
        env_file = ".env"


settings = Settings()
