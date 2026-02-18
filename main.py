#!/usr/bin/python3

import glob
import os
import subprocess
import random
import argparse
import magic
import time
import signal
import sys
from progress.bar import ChargingBar
from progress.spinner import PixelSpinner

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, help='source videos full path (recursive)')
parser.add_argument('-d', '--destination', type=str,
                    help='location to save gifs (each video creates a folder same name as the video)')
parser.add_argument('-l', '--length', type=str, help='gif length in seconds (default 4.3s)', default='4.3')
parser.add_argument('-b', '--begin', type=int,
                    help='gif generation starts from this value. Good for skipping intros(in seconds, default 90s)',
                    default=90)
parser.add_argument('-r1', '--randstart', type=int,
                    help='sets the start value of the randomizer. Minimum distance from the previous gif in seconds '
                         '(default 20s)',
                    default=20)
parser.add_argument('-r2', '--randend', type=int,
                    help='sets the end value of the randomizer. Maximum distance from the previous gif in seconds '
                         '(default 80s)',
                    default=80)
parser.add_argument('--dry-run', action='store_true',
                    help='scan and plan gifs without running ffmpeg')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='print debug information')
args = parser.parse_args()

# Check if at least the source and the destination are set
if args.source is None or args.destination is None:
    raise SystemExit("Please enter a valid source and a destination folder. Rest is optional. "
                     "Please use --help for details")

source_root = os.path.abspath(args.source)
dest_root = os.path.abspath(args.destination)

os.chdir(source_root)
os.makedirs(dest_root, exist_ok=True)


# Clean exit with CTRL+C
def signal_handler(_, frame):
    print("   Exiting...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def generate_gif(input_file):
    rel_path = os.path.relpath(input_file, start='.')
    rel_dir = os.path.dirname(rel_path)
    base_name = os.path.splitext(os.path.basename(rel_path))[0]
    output_dir = os.path.join(dest_root, rel_dir, base_name)
    os.makedirs(output_dir, exist_ok=True)

    video_duration = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1",
         input_file], universal_newlines=True).strip())

    # creating vars for easy reading
    gif_length = float(args.length)
    if video_duration < gif_length:
        print(f"Skipping (shorter than gif length {gif_length}s): {rel_path}")
        return

    max_start = max(0.0, video_duration - gif_length)
    # If begin is too late for this video, start at 0 so we still generate gifs
    begin_time = float(args.begin)
    if begin_time > max_start:
        begin_time = 0.0
    current_time = min(begin_time, max_start)
    random_start = args.randstart
    random_end = args.randend

    # workaround for videos in source root folder
    print("\nCurrent file: " + rel_path)
    if args.verbose:
        print(f"Duration: {video_duration:.2f}s, gif_length: {gif_length:.2f}s, "
              f"begin: {begin_time:.2f}s, max_start: {max_start:.2f}s")

    bar = ChargingBar('Processing', max=int(video_duration))
    # initialize bar
    bar.goto(0)

    while current_time <= max_start:
        # creating vars for easy reading
        output_file = os.path.join(output_dir, f"{base_name}-{int(current_time)}.gif")
        gif_length_arg = str(gif_length)

        # you can increase the fps=12 and scale=w=480 values with a higher number for smoother/bigger gifs,
        # increases the file size.
        ffmpeg_cmd = ['ffmpeg', '-y', '-ss', str(current_time), '-t', gif_length_arg, '-i', input_file,
                      '-filter_complex',
                      '[0:v] fps=12,scale=w=480:h=-1,split [a][b];[a] palettegen=stats_mode=single [p];['
                      'b][p] paletteuse=new=1',
                      output_file]
        if args.verbose:
            print("FFmpeg:", " ".join(ffmpeg_cmd))
        if not args.dry_run:
            subprocess.check_output(
                ffmpeg_cmd,
                stderr=subprocess.STDOUT,
                universal_newlines=True).strip()
        bar.goto(int(current_time))
        current_time = current_time + (random.randrange(random_start, random_end))
    bar.finish()


progress_start = time.time()

video_files = []
video_files_populated = False
spinner = PixelSpinner('Please wait while generating video files list ')

if args.randstart >= args.randend:
    raise SystemExit("randstart must be less than randend")

video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv'}

while not video_files_populated:
    for root, dirs, files in os.walk('.'):
        for name in files:
            file = os.path.join(root, name)
            ext = os.path.splitext(file)[1].lower()
            is_video = ext in video_extensions

            if not is_video:
                try:
                    is_video = magic.from_file(file, mime=True).startswith('video')
                except Exception:
                    is_video = False

            if is_video:
                video_files.append(file)
                spinner.next()
    video_files_populated = True

if not video_files:
    raise SystemExit("No video files found under source path.")


for video in range(len(video_files)):
    generate_gif(video_files[video])

progress_end = time.time()
total_run = int(progress_end - progress_start)
print("== FINISHED ==")
print("Total Runtime: " + str(total_run) + " seconds")
