import enum


@enum.unique
class YouTubeAudioQuality(enum.StrEnum):
    """
    Possible qualities of a YouTube audio file.
    """

    LOW = "AUDIO_QUALITY_LOW"
    MEDIUM = "AUDIO_QUALITY_MEDIUM"
