import datetime

import redis.asyncio as redis

from src.settings import settings


DEFAULT_LIFETIME = settings.TELEGRAM_AUDIO_ID_LIFETIME


class TelegramStorage:
    """
    Audios sent via Telegram are stored on its servers and
    accessed by identifiers.

    Therefore, since sometimes the process of download takes
    a lot of time, the identifier of once downloaded and sent audio
    file is stored in Redis (which is the responsibility of this class).
    """

    def __init__(
        self,
        redis_storage: redis.Redis | None = None,
        record_lifetime: datetime.timedelta | int = DEFAULT_LIFETIME
    ):
        self._redis_storage = redis_storage or redis.Redis()
        self._record_lifetime = record_lifetime

    async def get(self, video_id: str) -> int | None:
        """
        :param video_id:
            The ID of the YouTube video associated with the audio.

        :return:
            The ID of the audio. None if it does not exist in the
            local Redis storage and accordingly on the Telegram servers.
        """
        audio_id = await self._redis_storage.get(video_id)
        return audio_id

    async def save(self, video_id: str, audio_id: int) -> None:
        """
        After an audio is sent via Telegram, it can be accessed by a
        specific ID returned by the API. Therefore, it should be saved locally.

        :param video_id:
            The ID of the YouTube video associated with the audio.
        :param audio_id:
            The ID of the audio on the Telegram servers.
        """
        await self._redis_storage.set(video_id, audio_id, self._record_lifetime)
