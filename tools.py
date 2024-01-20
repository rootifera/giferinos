import os.path
import subprocess


def is_ffmpeg_installed(ffmpeg_location: str = None):
    if ffmpeg_location is not None:
        print("1")
        if os.path.exists(ffmpeg_location):
            print("2")
            return ffmpeg_location

    try:
        subprocess.run(['which', 'ffmpeg'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("3")
        return True
    except subprocess.CalledProcessError:
        return False
