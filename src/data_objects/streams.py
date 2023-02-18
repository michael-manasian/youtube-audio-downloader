import typing

import pydantic

from src.enums import YouTubeAudioQuality


class AudioStream(pydantic.BaseModel):
    url: pydantic.HttpUrl
    format: str = pydantic.Field(alias="mimeType")
    content_length: int = pydantic.Field(alias="contentLength")
    quality: YouTubeAudioQuality = pydantic.Field(alias="audioQuality")

    @pydantic.validator("format", pre=True)
    def extract_format(cls, mimetype_codecs: str) -> str:
        """
        The YouTube player returns the MIME type
        in the following format: type/subtype; codecs.

        Therefore, this method extracts only the subtype -
        the audio format in which it should be saved locally.
        """
        mimetype = mimetype_codecs.split(";")[0]
        return mimetype.split("/")[1]

    def __lt__(self, other: typing.Self) -> bool:
        """
        Compares the quality of this audio stream with the other's.
        """
        priorities = {
            YouTubeAudioQuality.LOW: 0,
            YouTubeAudioQuality.MEDIUM: 1
        }
        return priorities[self.quality] < priorities[other.quality]


RawStreams: typing.TypeAlias = list[dict]


class AudioStreams(pydantic.BaseModel):
    """
    Although the YouTube player returns both video and
    audio streams, we do not need videos. Therefore, this
    class is responsible for extracting and storing audios.
    """
    streams: list[AudioStream]

    @property
    def highest_quality(self) -> AudioStream:
        """
        :returns: An audio stream with the highest quality.
        """
        return max(self.streams)

    @pydantic.validator("streams", pre=True)
    def filter_streams(cls, streams: RawStreams) -> RawStreams:
        """
        Filters the given streams and leaves only audio ones.
        """
        return [
            stream for stream in streams if "audio" in stream["mimeType"]
        ]
