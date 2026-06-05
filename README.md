# Giferinos

Giferinos is a small ffmpeg wrapper for generating short GIFs from videos.

By default it creates 5 second GIFs every 30 seconds from every video under a
source folder. Output keeps the source folder hierarchy and puts each video's
GIFs in a folder named after that video.

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` available on your `PATH`

Install the optional Python dependency:

```bash
pip install -r requirements.txt
```

`python-magic` lets Giferinos detect video files by MIME type when the extension
is unusual. Common video extensions work without it.

## Usage

Generate 5 second GIFs every 30 seconds:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs
```

Change the GIF length and spacing:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs --gif-length 4 --skip-seconds 45
```

Change the output size:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs --size 720
```

Skip an intro before generating the first GIF:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs --begin 90
```

Use randomized spacing instead of a fixed interval:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs --random-min 20 --random-max 80
```

Preview the work without creating files:

```bash
python main.py --source /path/to/videos --destination /path/to/gifs --dry-run
```

## Options

```text
-s, --source         folder containing source videos; scanned recursively
-d, --destination    folder where generated gifs will be written
-l, --length,
    --gif-length     gif length in seconds (default: 5)
-b, --begin          seconds to skip before the first gif (default: 0)
-e, --every,
    --skip-seconds   seconds to advance before starting the next gif (default: 30)
--random-min, -r1    minimum randomized seconds between gifs
--random-max, -r2    maximum randomized seconds between gifs
--seed               seed for repeatable randomized intervals
--fps                gif frames per second (default: 12)
-w, --width,
    --size           gif width in pixels; height is preserved (default: 480)
--dry-run            show planned gifs without running ffmpeg
-v, --verbose        print ffmpeg commands and extra video details
```

While it runs, Giferinos shows scan progress and GIF creation progress:

```text
Scanning videos... checked 120 file(s), found 6 video(s)
Found 6 video(s)
[video 1/6] episode-01.mp4: 12 gif(s)
  [gif 1/12] creating episode-01-0s.gif from 0s
```

## Notes

If `--begin` is after the last valid start time for a video, Giferinos falls
back to `0` seconds so short videos still get a GIF when possible.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
