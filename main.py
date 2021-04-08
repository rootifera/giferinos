import glob
import os
import subprocess
import random

os.chdir("/mnt/i/Gifs/Movies/")
save_to = '/mnt/i/Gifs/Generated/'

for file in glob.iglob('**/*.mp4', recursive=True):
    split_path_name = file.split("/")
    folder = save_to + split_path_name[0]

    if not os.path.exists(folder):
        os.makedirs(folder)
    video_duration = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         file], universal_newlines=True).strip()

    current_time = 90

    while current_time <= int(float(video_duration)):
        current_time = current_time + (random.randrange(20, 80))
        # print(current_time)
        # print(int(float(video_duration)))
        if current_time > int(float(video_duration)):
            break

        subprocess.check_output(['ffmpeg', '-y', '-ss', str(current_time), '-t', '4.3', '-i', file, '-filter_complex',
                                 '[0:v] fps=12,scale=w=480:h=-1,split [a][b];[a] palettegen=stats_mode=single [p];['
                                 'b][p] paletteuse=new=1',
                                 '/mnt/i/Gifs/Generated/%s-%s.gif' % (file, current_time)],
                                universal_newlines=True).strip()

#        time.sleep(5)
