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
args = parser.parse_args()

# Check if at least the source and the destination is set
if args.source is None or args.destination is None:
    raise SystemExit("Please enter a valid source and a destination folder. Rest is optional. Please use --help for details")

os.chdir(args.source)
save_to = args.destination


# Clean exit with CTRL+C
def signal_handler(signal, frame):
    print("   Exiting...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def generate_gif(input_file):
    if not os.path.isdir(input_file):

        # this check returns something like "video/mp4"
        if magic.from_file(input_file, mime=True)[:5] == 'video':
            if not os.path.exists(folder):
                os.makedirs(folder)
            video_duration = (int(float(subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                 "default=noprint_wrappers=1:nokey=1",
                 input_file], universal_newlines=True).strip())))

            # creating vars for easy reading
            current_time = args.begin
            random_start = args.randstart
            random_end = args.randend

            print("Current file: " + input_file.split("/")[1])

            bar = ChargingBar('Processing', max=video_duration)
            # initialize bar
            bar.goto(0)

            while current_time <= video_duration:
                current_time = current_time + (random.randrange(random_start, random_end))
                if current_time > video_duration:
                    break

                # creating vars for easy reading
                filename_generator = args.destination + '%s-%s.gif'
                gif_length = args.length

                # you can increase the fps=12 and scale=w=480 values with a higher number for smoother/bigger gifs,
                # increases the file size.
                subprocess.check_output(
                    ['ffmpeg', '-y', '-ss', str(current_time), '-t', gif_length, '-i', input_file, '-filter_complex',
                     '[0:v] fps=12,scale=w=480:h=-1,split [a][b];[a] palettegen=stats_mode=single [p];['
                     'b][p] paletteuse=new=1',
                     filename_generator % (input_file, current_time)],
                    stderr=subprocess.STDOUT,
                    universal_newlines=True).strip()
                bar.goto(current_time)
            bar.finish()


progress_start = time.time()

for file in glob.iglob('**/*.*', recursive=True):
    split_path_name = file.split("/")
    folder = save_to + split_path_name[0]
    generate_gif(file)

progress_end = time.time()
total_run = int(progress_end - progress_start)
print("== FINISHED ==")
print("Total Runtime: " + str(total_run) + " seconds")
