import os

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 7070))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    
    # OCR 配置
    OCR_CHARSET: str = os.getenv("OCR_CHARSET", "")
    PROBABILITY: bool = os.getenv("PROBABILITY", "false").lower() in ("true", "1")
    
    # 每日配额设置 (自建默认无限，设一个大数字如 999999)
    DAILY_LIMIT: int = int(os.getenv("DAILY_LIMIT", 999999))
    
    # 加密掩码版本
    MASK_VERSION: str = "ctw_2026_slide_mask_v1"

settings = Settings()
