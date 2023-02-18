import typing

import aiogram
from aiogram.dispatcher.filters import CommandStart

from src.downloader import YouTubeAudioDownloader
from src.messages import Messages
from src.settings import settings
from src.storage import TelegramStorage
from src.utils import extract_video_id


bot = aiogram.Bot(settings.TELEGRAM_BOT_TOKEN)
dispatcher = aiogram.Dispatcher(bot)

telegram_storage = TelegramStorage()


@dispatcher.message_handler(CommandStart())
async def send_welcome_message(message: aiogram.types.Message) -> typing.Any:
    """
    Sends the welcome message to the user.
    """
    user = message.from_user
    full_name = "{} {}".format(user.first_name, user.last_name)

    message_answer = Messages.WELCOME_MESSAGE.format(full_name)
    await bot.send_message(message.from_id, message_answer)


@dispatcher.message_handler()
async def process_audio_download_request(message: aiogram.types.Message) -> typing.Any:
    """
    The main handler that receives a YouTube video's link, extracts its ID
    and sends its audio after successful download.

    Please note that although it does not take long to download and open even
    a large audio file, it can take a significant amount of time to upload it to
    the Telegram servers. Apparently, it can not be affected from the client side.
    """
    video_id = extract_video_id(message.text)
    if video_id is None:
        return await bot.send_message(
            message.from_id,
            Messages.INCORRECT_MESSAGE
        )

    audio_id = await telegram_storage.get(video_id)
    if audio_id is not None:
        return await bot.send_audio(message.from_id, audio_id)

    await bot.send_message(
        message.from_id,
        Messages.AUDIO_BEING_DOWNLOADED
    )

    async with YouTubeAudioDownloader() as downloader:
        audio = await downloader.download(video_id)

        audio_message = await bot.send_audio(
            chat_id=message.from_id,
            audio=open(audio.filename, "rb"),
            title=audio.title,
            thumb=audio.thumbnail,
            performer=audio.author,
            duration=audio.duration_seconds
        )
        await telegram_storage.save(video_id, audio_message.audio.file_id)


if __name__ == '__main__':
    aiogram.executor.start_polling(dispatcher, skip_updates=True)
