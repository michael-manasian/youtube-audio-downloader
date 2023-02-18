import datetime

import pydantic


class Settings(pydantic.BaseSettings):
    API_KEY: str
    CLIENT_NAME: str = "ANDROID"
    CLIENT_VERSION: str = "16.20"
    USER_AGENT: str = "Mozilla/5.0"

    TELEGRAM_BOT_TOKEN: str

    TELEGRAM_AUDIO_ID_LIFETIME: int = datetime.timedelta(weeks=26).total_seconds()


settings = Settings()
