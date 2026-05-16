from pathlib import Path


def convert_to_mp3(video_path):
    try:
        from moviepy.editor import VideoFileClip
    except ModuleNotFoundError:
        try:
            from moviepy import VideoFileClip
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "moviepy is not installed. Install it with: pip install moviepy"
            ) from error

    video_path = Path(video_path)
    if video_path.suffix.lower() != ".mp4":
        raise ValueError("Only .mp4 files are supported")

    mp3_path = video_path.with_suffix(".mp3")
    if mp3_path.exists():
        raise FileExistsError(f"{mp3_path.name} already exists")

    with VideoFileClip(str(video_path)) as video:
        if video.audio is None:
            raise ValueError("No audio track found")

        video.audio.write_audiofile(str(mp3_path))

    return mp3_path
