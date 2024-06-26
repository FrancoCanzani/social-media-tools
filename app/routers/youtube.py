from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.utils.video_utils import merge_video_audio_ffmpeg
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, AgeRestrictedError, PytubeError
from urllib.parse import unquote
from app.utils.file_utils import remove_file
from app.models.video_metadata import VideoMetadata
import os

# Set the path to ffmpeg executable
FFMPEG_PATH = (
    r"C:\ffmpeg\bin\ffmpeg.exe"  # Update this path according to the installation
)

router = APIRouter()


@router.get("/video/metadata", response_model=VideoMetadata)
def get_video_metadata(url: str):
    try:
        decoded_url = unquote(url)
        yt = YouTube(decoded_url)

        resolutions = [
            stream.resolution
            for stream in yt.streams.filter(file_extension="mp4", only_video=True)
        ]
        captions = (
            [caption.name for caption in yt.caption_tracks]
            if yt.caption_tracks
            else None
        )

    except VideoUnavailable:
        raise HTTPException(
            status_code=400, detail=f"Video {url} is unavailable."
        )

    except AgeRestrictedError:
        raise HTTPException(status_code=403, detail=f"Video {url} is age restricted.")

    except PytubeError:
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the video with Pytube."
        )

    except Exception:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred."
        )

    else:
        return {
            "author": yt.author,
            "channel_url": yt.channel_url,
            "channel_id": yt.channel_id,
            "title": yt.title,
            "thumbnail": yt.thumbnail_url,
            "description": yt.description.replace("\n", ""),
            "keywords": yt.keywords,
            "publish_date": yt.publish_date,
            "length": yt.length,
            "rating": yt.rating,
            "views": yt.views,
            "resolutions": resolutions,
            "captions": captions,
        }


@router.get("/video/download")
def download_video(url: str, res: str, background_tasks: BackgroundTasks):
    try:
        decoded_url = unquote(url)
        yt = YouTube(decoded_url)

    except VideoUnavailable:
        raise HTTPException(
            status_code=400, detail=f"Video {url} is unavailable."
        )

    except AgeRestrictedError:
        raise HTTPException(
            status_code=403, detail=f"Video {url} is age restricted."
        )

    except PytubeError:
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the video with Pytube."
        )

    except Exception:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred."
        )

    video_stream = yt.streams.filter(
        file_extension="mp4", only_video=True, resolution=res
    ).first()
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

    if not video_stream:
        raise HTTPException(status_code=404, detail="Video stream not found")

    if not audio_stream:
        raise HTTPException(status_code=404, detail="Audio stream not found")

    try:
        video_path = video_stream.download(filename="temp_video.mp4")
        audio_path = audio_stream.download(filename="temp_audio.mp4")
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error downloading video or audio stream."
        )

    output_path = f"{yt.title.replace(' ', '_')}.mp4"

    # Ensure ffmpeg path is set
    os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

    try:
        merge_video_audio_ffmpeg(video_path, audio_path, output_path)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error merging video and audio streams."
        )

    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Merged video not found")

    background_tasks.add_task(remove_file, video_path)
    background_tasks.add_task(remove_file, audio_path)
    background_tasks.add_task(remove_file, output_path)

    return FileResponse(
        output_path, media_type="video/mp4", filename=os.path.basename(output_path)
    )
