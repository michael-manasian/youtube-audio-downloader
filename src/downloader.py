import asyncio
import os.path
import shutil
import tempfile
import typing
import uuid

import aiofiles
import aiohttp

from src.dataclasses_ import Audio
from src.player import YouTubePlayer


class ChunkRange(typing.NamedTuple):
    """
    There may be large files that require so much
    time to download.

    To effectively reduce that time, we need to
    split every audio file into several chunks and
    distribute their download among different coroutines.
    """
    start: int
    finish: int

    @property
    def range_header(self) -> dict[str, str]:
        """
        :returns:
            The Range HTTP header with the borders defined
            for this ChunkRange object (for a partial download).
        """
        return {
            "Range": "bytes={}-{}".format(self.start, self.finish)
        }


ChunkRanges: typing.TypeAlias = typing.Generator[ChunkRange, None, None]


class YouTubeAudioDownloader:
    """
    Asynchronously downloads the audio from a YouTube video.

    This class performs the download process individually for one YouTube
    video. Each video has its own service directory where everything is stored.

    Therefore, YouTubeAudioDownloader is intended to be instantiated every time
    and used as an asynchronous context manager, which allows to free up the space later.
    """

    def __init__(
        self,
        chunk_size: int = 10 * 1024 ** 2,
        base_directory_name: str = "youtube_audio_files"
    ):
        self._chunk_size = chunk_size
        self._base_directory_path = os.path.abspath(base_directory_name)

        if not os.path.exists(base_directory_name):
            # If this directory does not exist yet,
            # we should create it for the subsequent download.
            os.mkdir(base_directory_name)

        self._audio_directory_path = os.path.join(
            self._base_directory_path, uuid.uuid4().hex
        )
        os.mkdir(self._audio_directory_path)

    async def __aenter__(self) -> typing.Self:
        """
        This class should support the asynchronous context
        manager protocol.

        When the work is done, the method __aexit()__ is called.
        """
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """
        After the audio is downloaded and sent via Telegram,
        or in case of unexpected exception, the service directory of
        the audio should be deleted to free up the space on the hard drive.
        """
        # shutil.rmtree(self._audio_directory_path)

    def _split_into_chunks(self, content_length: int) -> ChunkRanges:
        """
        Splits the content length into smaller chunks whose
        download is to be distributed between multiple coroutines.

        Note: the size of one chunk is determined by the protected
        _chunk_size attribute of this class (received from the user).

        :returns: A generator of ChunkRange objects.
        """
        previous_finish = 0

        while (
            # Runs as long as the remaining content
            # length is greater than the size of one chunk.
            self._chunk_size < (content_length - previous_finish)
        ):
            yield ChunkRange(
                previous_finish,
                next_finish := previous_finish + self._chunk_size
            )
            previous_finish = next_finish

        yield ChunkRange(previous_finish, content_length)

    @staticmethod
    async def _download_chunk(session: aiohttp.ClientSession,
                              audio_url: str,
                              chunk_range: ChunkRange,
                              save_to_filename: str) -> None:
        """
        This method is intended to be used as a task for
        the asyncio.gather() function.

        It saves a certain chunk of the YouTube audio to
        a file with the given name. The size of the chunk,
        in turn, is determined by the chunk_range argument.
        """
        headers = chunk_range.range_header

        async with session.get(audio_url, headers=headers) as response:
            file = await aiofiles.open(save_to_filename, "wb")

            chunk_content = await response.content.read()
            await file.write(chunk_content)

    @staticmethod
    def _assemble_chunks(chunks_filenames: list[str], save_to_filename: str) -> None:
        """
        Goes through the downloaded chunks of the
        YouTube audio and saves them to a final audio file.

        This method is the completion of the downloading process.
        """
        with open(save_to_filename, "wb") as result_file:
            for chunk_filename in chunks_filenames:
                with open(chunk_filename, "rb") as chunk_file:
                    shutil.copyfileobj(chunk_file, result_file)

    async def _download(self,
                        session: aiohttp.ClientSession,
                        audio_url: str,
                        save_format: str,
                        content_length: int) -> str:
        """
        Creates coroutines that are responsible for
        downloading the chunks of the audio file, runs them
        and copies everything into a file with the given name.

        :returns: The absolute path to the downloaded audio file.
        """
        tasks = []
        filenames = []

        chunks_directory = tempfile.TemporaryDirectory(
            None,
            "chunks",
            self._audio_directory_path
        )

        for chunk_range in self._split_into_chunks(content_length):
            chunk_filename = os.path.join(
                chunks_directory.name, uuid.uuid4().hex
            )
            task = self._download_chunk(
                session,
                audio_url,
                chunk_range,
                chunk_filename
            )
            tasks.append(task)
            filenames.append(chunk_filename)

        await asyncio.gather(*tasks)

        save_to_filename = "{}.{}".format(uuid.uuid4().hex, save_format)
        abspath_to_audio = os.path.join(self._audio_directory_path, save_to_filename)
        self._assemble_chunks(filenames, abspath_to_audio)

        return abspath_to_audio

    async def download(self, video_id: str) -> Audio:
        """
        Downloads the audio of the YouTube video.

        :returns:
            An Audio object with all the data required to send a Telegram audio file.

        :raises:
            FileTooLargeForUploading:
                If the size of the audio file is bigger than the specified limit.
        """
        async with aiohttp.ClientSession() as session:
            details, audio_stream = await YouTubePlayer().extract(video_id, session)

            abspath_to_audio = await self._download(
                session,
                audio_stream.url,
                audio_stream.format,
                audio_stream.content_length,
            )
            return Audio(
                details.title,
                details.author,
                abspath_to_audio,
                details.thumbnail_url,
                details.duration_seconds,
            )
