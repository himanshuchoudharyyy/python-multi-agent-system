import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Fintech Multi-Agent Support System"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

        # Primary Gemini model
    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.5-flash-lite"
    )

    # Fallback Gemini model
    GEMINI_FALLBACK_MODEL: str = os.getenv(
        "GEMINI_FALLBACK_MODEL",
        "gemini-3.5-flash"
    )

settings = Settings()
