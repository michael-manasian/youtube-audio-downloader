import re


def extract_video_id(video_url: str) -> str | None:
    """
    Extract the ID from the YouTube video URL.

    This function supports the following patterns:
    - https://youtube.com/watch?v={video_id}
    - https://youtube.com/embed/{video_id}
    - https://youtu.be/{video_id}
    
    :returns: The ID of the YouTube video.
    """
    expression = (
        r"(?:v=|\/)"
        r"([0-9A-Za-z_-]{11}).*"
    )

    regex = re.compile(expression)
    results = regex.search(video_url)

    if results:
        return results.group(1)

