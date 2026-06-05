from __future__ import annotations

import random
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Iterable

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v"}


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(f"{name} was not found on PATH")
    return executable


def get_video_duration(video_file: Path, ffprobe: str = "ffprobe") -> float:
    output = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_file),
        ],
        stderr=subprocess.STDOUT,
        text=True,
    ).strip()
    return float(output)


def is_video_file(path: Path) -> bool:
    if path.suffix.lower() in VIDEO_EXTENSIONS:
        return True

    try:
        import magic
    except ImportError:
        return False

    try:
        return magic.from_file(str(path), mime=True).startswith("video/")
    except Exception:
        return False


def get_video_files(
    source_folder: Path,
    on_scanned: Callable[[int, int], None] | None = None,
) -> list[Path]:
    videos = []
    scanned = 0

    for path in source_folder.rglob("*"):
        if not path.is_file():
            continue

        scanned += 1
        if is_video_file(path):
            videos.append(path)

        if on_scanned is not None:
            on_scanned(scanned, len(videos))

    return sorted(videos)


def build_timestamps(
    duration: float,
    gif_length: float,
    begin: float,
    interval: float,
    random_min: float | None = None,
    random_max: float | None = None,
    seed: int | None = None,
) -> Iterable[float]:
    max_start = duration - gif_length
    if max_start < 0:
        return

    current = begin if begin <= max_start else 0.0
    rng = random.Random(seed)

    while current <= max_start:
        yield round(current, 3)
        if random_min is not None and random_max is not None:
            current += rng.uniform(random_min, random_max)
        else:
            current += interval
