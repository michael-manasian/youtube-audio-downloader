import typing

import aiohttp

from src.settings import settings
from src.data_objects import VideoDetails, AudioStreams

if typing.TYPE_CHECKING:
    from src.data_objects import AudioStream


API_KEY = settings.API_KEY


class YouTubePlayer:
    """
    An interface for working with the YouTube
    player (https://www.youtube.com/youtubei/v1/player)
    """

    @property
    def _request_url(self) -> str:
        """
        :returns: The YouTube player request address.
        """
        return "https://www.youtube.com/youtubei/v1/player"

    @property
    def _base_headers(self) -> dict[str, str]:
        """
        :returns: Base request headers.
        """
        return {"Content-Type": "application/json"}

    @property
    def _base_parameters(self) -> dict[str, str]:
        """
        :returns: Base request query parameters.
        """
        return {
            "key": API_KEY,
            "racyCheckOk": "True",
            "contentCheckOk": "True"
        }

    @property
    def _client(self) -> dict[str, str]:
        """
        :returns: Client information.
        """
        return {
            "clientName": settings.CLIENT_NAME,
            "clientVersion": settings.CLIENT_VERSION
        }

    @property
    def _base_payload(self) -> dict:
        """
        :returns: Base request body.
        """
        return {
            "context": {"client": self._client}
        }

    async def _get_raw_data(self,
                            video_id: str,
                            session: aiohttp.ClientSession) -> typing.Any:
        """
        Creates and sends an HTTP request to the YouTube player.

        :returns: The JSON body of the response (raw data of the YouTube video).
        """
        query_parameters = {
            "videoId": video_id,
            **self._base_parameters
        }
        request_kwargs = {
            "url": self._request_url,
            "params": query_parameters,
            "json": self._base_payload,
            "headers": self._base_headers
        }
        async with session.post(**request_kwargs) as response:
            return await response.json()

    async def extract(self,
                      video_id: str,
                      session: aiohttp.ClientSession) -> tuple[VideoDetails, "AudioStream"]:
        """
        :returns:
            Basic information of the video and
            an audio stream with the highest quality.
        """
        raw_data = await self._get_raw_data(video_id, session)

        raw_video_details = raw_data["videoDetails"]
        video_details = VideoDetails(**raw_video_details)

        streams = raw_data["streamingData"]["adaptiveFormats"]
        audio_stream = AudioStreams(streams=streams).highest_quality

        return video_details, audio_stream
