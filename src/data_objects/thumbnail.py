import typing

import pydantic


class Thumbnail(pydantic.BaseModel):
    """
    A thumbnail of a YouTube video (there may be several).

    Note: we do not take into account the size of a
    thumbnail, although the YouTube player also includes it.
    """
    url: pydantic.HttpUrl


Thumbnails: typing.TypeAlias = list[Thumbnail]
