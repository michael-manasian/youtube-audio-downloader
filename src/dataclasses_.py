import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class Audio:
    """
    Represents an audio downloaded from a
    YouTube video (according to a user's request).

    This structure includes all the necessary data to
    send a Telegram audio using aiogram.Bot.send_audio().
    """
    title: str
    author: str
    filename: str
    thumbnail: str
    duration_seconds: int
