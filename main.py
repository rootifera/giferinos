#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from functions import (
    build_timestamps,
    get_video_duration,
    get_video_files,
    require_executable,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="giferinos",
        description="Generate short GIFs from videos at fixed or randomized intervals.",
    )
    parser.add_argument(
        "-s",
        "--source",
        required=True,
        type=Path,
        help="folder containing source videos; scanned recursively",
    )
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        type=Path,
        help="folder where generated gifs will be written",
    )
    parser.add_argument(
        "-l",
        "--length",
        "--gif-length",
        default=5.0,
        type=positive_float,
        help="gif length in seconds (default: 5)",
    )
    parser.add_argument(
        "-b",
        "--begin",
        default=0.0,
        type=non_negative_float,
        help="seconds to skip before the first gif (default: 0)",
    )
    parser.add_argument(
        "-e",
        "--every",
        "--interval",
        "--skip",
        "--skip-seconds",
        dest="interval",
        default=30.0,
        type=positive_float,
        help="seconds to advance before starting the next gif (default: 30)",
    )
    parser.add_argument(
        "--random-min",
        "-r1",
        type=positive_float,
        help="minimum randomized seconds between gifs",
    )
    parser.add_argument(
        "--random-max",
        "-r2",
        type=positive_float,
        help="maximum randomized seconds between gifs",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="seed for repeatable randomized intervals",
    )
    parser.add_argument(
        "--fps",
        default=12,
        type=positive_int,
        help="gif frames per second (default: 12)",
    )
    parser.add_argument(
        "-w",
        "--width",
        "--size",
        "--gif-width",
        default=480,
        type=positive_int,
        help="gif width in pixels; height is preserved (default: 480)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the gifs that would be generated without running ffmpeg",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print ffmpeg commands and extra video details",
    )
    return parser.parse_args()


def positive_float(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return number


def non_negative_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be 0 or greater")
    return number


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return number


def validate_args(args: argparse.Namespace) -> None:
    if not args.source.exists() or not args.source.is_dir():
        raise SystemExit(f"Source folder does not exist: {args.source}")

    if (args.random_min is None) != (args.random_max is None):
        raise SystemExit("Use --random-min and --random-max together.")

    if args.random_min is not None and args.random_min >= args.random_max:
        raise SystemExit("--random-min must be less than --random-max.")


class ScanProgress:
    def __init__(self) -> None:
        self.last_scanned = 0
        self.last_found = 0
        self.last_message = ""
        self.last_printed_message = ""

    def __call__(self, scanned: int, found: int) -> None:
        self.last_scanned = scanned
        if (
            sys.stdout.isatty()
            or scanned == 1
            or scanned % 25 == 0
            or found != self.last_found
        ):
            message = f"Scanning videos... checked {scanned} file(s), found {found} video(s)"
            self.last_message = message
            if sys.stdout.isatty():
                print(f"\r{message}", end="", flush=True)
            else:
                print(message)
            self.last_printed_message = message

        self.last_found = found

    def finish(self) -> None:
        message = (
            f"Scanning videos... checked {self.last_scanned} file(s), "
            f"found {self.last_found} video(s)"
        )
        self.last_message = message
        if sys.stdout.isatty():
            print(f"\r{message}")
        elif message != self.last_printed_message:
            print(message)


def output_dir_for(video_file: Path, source_root: Path, destination_root: Path) -> Path:
    relative_path = video_file.relative_to(source_root)
    return destination_root / relative_path.parent / video_file.stem


def format_timestamp(timestamp: float) -> str:
    return f"{timestamp:.3f}".rstrip("0").rstrip(".").replace(".", "_")


def ffmpeg_command(
    ffmpeg: str,
    video_file: Path,
    output_file: Path,
    timestamp: float,
    length: float,
    fps: int,
    width: int,
) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-ss",
        str(timestamp),
        "-t",
        str(length),
        "-i",
        str(video_file),
        "-filter_complex",
        (
            f"[0:v] fps={fps},scale=w={width}:h=-1,split [a][b];"
            "[a] palettegen=stats_mode=single [p];[b][p] paletteuse=new=1"
        ),
        str(output_file),
    ]


def generate_gifs_for_video(
    video_file: Path,
    source_root: Path,
    destination_root: Path,
    args: argparse.Namespace,
    ffmpeg: str,
    ffprobe: str,
    video_number: int,
    total_videos: int,
) -> int:
    try:
        duration = get_video_duration(video_file, ffprobe)
    except (subprocess.CalledProcessError, ValueError) as error:
        print(f"Skipping {video_file}: could not read duration ({error})", file=sys.stderr)
        return 0

    relative_path = video_file.relative_to(source_root)
    timestamps = list(
        build_timestamps(
            duration=duration,
            gif_length=args.length,
            begin=args.begin,
            interval=args.interval,
            random_min=args.random_min,
            random_max=args.random_max,
            seed=args.seed,
        )
    )

    if not timestamps:
        print(f"Skipping {relative_path}: shorter than {args.length:g}s")
        return 0

    output_dir = output_dir_for(video_file, source_root, destination_root)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[video {video_number}/{total_videos}] {relative_path}: {len(timestamps)} gif(s)")
    if args.verbose:
        print(f"  duration={duration:.2f}s output={output_dir}")

    generated = 0
    for gif_number, timestamp in enumerate(timestamps, start=1):
        output_file = output_dir / f"{video_file.stem}-{format_timestamp(timestamp)}s.gif"
        command = ffmpeg_command(
            ffmpeg=ffmpeg,
            video_file=video_file,
            output_file=output_file,
            timestamp=timestamp,
            length=args.length,
            fps=args.fps,
            width=args.width,
        )

        if args.dry_run:
            print(f"  [gif {gif_number}/{len(timestamps)}] would create {output_file}")
            generated += 1
            continue

        print(
            f"  [gif {gif_number}/{len(timestamps)}] creating {output_file.name} "
            f"from {timestamp:g}s"
        )

        if args.verbose:
            print("  " + " ".join(command))

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            print(f"  failed at {timestamp:g}s: {error.stderr.strip()}", file=sys.stderr)
            continue

        print(f"  [gif {gif_number}/{len(timestamps)}] created {output_file}")
        generated += 1

    return generated


def main() -> int:
    args = parse_args()
    args.source = args.source.expanduser().resolve()
    args.destination = args.destination.expanduser().resolve()
    validate_args(args)

    source_root = args.source
    destination_root = args.destination

    try:
        ffmpeg = require_executable("ffmpeg")
        ffprobe = require_executable("ffprobe")
    except RuntimeError as error:
        raise SystemExit(str(error))

    scan_progress = ScanProgress()
    videos = get_video_files(source_root, on_scanned=scan_progress)
    scan_progress.finish()
    if not videos:
        raise SystemExit(f"No video files found under {source_root}")

    start = time.monotonic()
    print(f"Found {len(videos)} video(s)")

    generated = 0
    for video_number, video_file in enumerate(videos, start=1):
        generated += generate_gifs_for_video(
            video_file=video_file,
            source_root=source_root,
            destination_root=destination_root,
            args=args,
            ffmpeg=ffmpeg,
            ffprobe=ffprobe,
            video_number=video_number,
            total_videos=len(videos),
        )

    elapsed = int(time.monotonic() - start)
    noun = "gif" if generated == 1 else "gifs"
    print(f"Done: {generated} {noun} planned/generated in {elapsed}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
