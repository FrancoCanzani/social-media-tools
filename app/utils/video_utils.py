import ffmpeg


def merge_video_audio_ffmpeg(video_path, audio_path, output_path):
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)

        ffmpeg.output(
            video,
            audio,
            output_path,
            vcodec="copy",
            acodec="aac",
            strict="experimental",
        ).overwrite_output().run()
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e.stderr}")
        raise RuntimeError("ffmpeg failed")
