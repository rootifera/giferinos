import glob
import os
import subprocess
import random
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, help='source videos full path (recursive)')
parser.add_argument('-d', '--destination', type=str, help='location to save gifs (each video creates a folder same name as the video)')
parser.add_argument('-l', '--length', type=str, help='gif length in seconds (default 4.3s)', default='4.3')
parser.add_argument('-b', '--begin', type=int, help='gif generation starts from this value. Good for skipping intros(in seconds, default 90s)', default=90)
parser.add_argument('-r1', '--rand1', type=int, help='sets the start value of the randomizer. Minimum distance from the previous gif in seconds (default 20s)', default=20)
parser.add_argument('-r2', '--rand2', type=int, help='sets the end value of the randomizer. Maximum distance from the previous gif in seconds (default 80s)', default=80)
args = parser.parse_args()

source_folder = args.source
destination_folder = args.destination
gif_length = args.length
start_from = args.begin
random_start = args.rand1
random_end = args.rand2

filename_generator = args.destination+'%s-%s.gif'

os.chdir(source_folder)
save_to = destination_folder


for file in glob.iglob('**/*.mp4', recursive=True):
    split_path_name = file.split("/")
    folder = save_to + split_path_name[0]

    if not os.path.exists(folder):
        os.makedirs(folder)
    video_duration = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         file], universal_newlines=True).strip()

    current_time = args.begin

    while current_time <= int(float(video_duration)):
        current_time = current_time + (random.randrange(random_start, random_end))
        # print(current_time)
        # print(int(float(video_duration)))
        if current_time > int(float(video_duration)):
            break

        subprocess.check_output(['ffmpeg', '-y', '-ss', str(current_time), '-t', gif_length, '-i', file, '-filter_complex',
                                 '[0:v] fps=12,scale=w=480:h=-1,split [a][b];[a] palettegen=stats_mode=single [p];['
                                 'b][p] paletteuse=new=1',
                                 filename_generator % (file, current_time)],
                                 universal_newlines=True).strip()
