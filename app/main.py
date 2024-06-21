from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from urllib.parse import unquote
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def remove_file(path: str):
    """Function to remove a file"""
    os.remove(path)
    
@app.get("/youtube/metadata")
def get_video_metadata(url: str):
    try:
        # Decode the URL
        decoded_url = unquote(url)

        yt = YouTube(decoded_url)
        
        return {'title': yt.title, 'thumbnail': yt.thumbnail_url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/youtube/download")
def download_video(url: str, background_tasks: BackgroundTasks):
    
    try:
        # Decode the URL
        decoded_url = unquote(url)

        yt = YouTube(decoded_url)
        
    except VideoUnavailable:
        print(f'Video {url} is unavaialable, skipping.')        
        raise HTTPException(status_code=400, detail=str(f'Video {url} is unavaialable, skipping.'))

    else:
        stream = yt.streams.filter(progressive=True, file_extension="mp4").first()

        if not stream:
            raise HTTPException(status_code=404, detail="Video stream not found")

        video_path = stream.download()

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Downloaded video not found")

        # Add file removal to background tasks / runs after the response
        background_tasks.add_task(remove_file, video_path)

        return FileResponse(
            video_path, media_type="video/mp4", filename=os.path.basename(video_path)
        )
