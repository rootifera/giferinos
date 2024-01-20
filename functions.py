import os.path
import subprocess


def is_ffmpeg_installed(ffmpeg_location: str = None):
    if ffmpeg_location is not None:
        if os.path.exists(ffmpeg_location):
            return ffmpeg_location

    try:
        subprocess.run(['which', 'ffmpeg'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("3")
        return True
    except subprocess.CalledProcessError:
        return False


def get_video_duration(video_file):
    video_duration = (int(float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1",
         video_file], universal_newlines=True).strip())))

    return round(video_duration, 0)


def get_video_files(source_folder):
    video_files = []

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))

    return video_files

