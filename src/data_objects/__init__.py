"""
This package provides structures that are easily instantiated with the
data returned by the YouTube player (https://www.youtube.com/youtubei/v1/player).

These structures are designed primarily because it is substantially more
convenient to access data using attributes than using the standard subscript syntax.
"""

from src.data_objects.details import VideoDetails
from src.data_objects.streams import AudioStreams, AudioStream
