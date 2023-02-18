import pydantic

from src.data_objects.thumbnail import Thumbnails


class VideoDetails(pydantic.BaseModel):
    """
    Contains basic information of a YouTube
    video, such as its title, author, duration etc.

    Note: this structure only contains the data
    needed to send a subsequent Telegram audio file.
    """
    title: str
    author: str
    thumbnail: dict[str, Thumbnails]
    duration_seconds: int = pydantic.Field(alias="lengthSeconds")

    @property
    def thumbnail_url(self) -> pydantic.HttpUrl:
        """
        :returns:
            The URL of the maximum size thumbnail
            (which is always the last one in the list).
        """
        maxsize_thumbnail = self.thumbnail["thumbnails"][-1]
        return maxsize_thumbnail.url

