"""Rotate the video files in a folder
This requires `ffmpeg` available in the system path.
"""
import subprocess
import pathlib
import argparse


def rotate(files: list[pathlib.Path], out_folder: pathlib.Path,
           speed: str, transpose: int) -> None:
    """rotate the video files and generate them into out_folder

    Args:
        files (list[pathlib.Path]): The video files to be rotated.
        out_folder (pathlib.Path): Must be an empty folder.
        It will be created if not exists yet.
        speed (str): Usually be one of ultrafast and fast.
        transpose (int): 1 is 90 clock-wise; 2 is 90 counter clock-wise.
        See more in https://ffmpeg.org/ffmpeg-filters.html#toc-transpose-1

    Raises:
        FileExistsError: May throw when `out_folder` is not empty or can't
        be made.
        FileNotFoundError: May throw when `files` doesn't exist.
    """
    out_folder = out_folder.expanduser()
    out_folder.mkdir(exist_ok=True)
    if not out_folder.exists():
        raise FileExistsError(f"Fail to create folder {out_folder}")
    if len(list(out_folder.iterdir())) > 0:
        raise FileExistsError(f"out_folder is not empty ({out_folder})")
    for file in files:
        if not file.exists():
            raise FileNotFoundError(f"{file}")
    n = len(files)
    print(f"There're {n} files in total.")
    for (i, file) in enumerate(files):
        print(f"Rotating {i+1} of {n}...")
        out_file = out_folder / file.name
        cmd: list[str] = ["ffmpeg", "-i", str(file), "-c:v", "libx264",
                          "-preset", f"{speed}", "-vf", f"transpose={transpose}",
                          str(out_file)]
        subprocess.run(cmd, check=True)
    print(f"All {n} files are done.")


def get_files(x: str) -> list[pathlib.Path]:
    folder = pathlib.Path(x).expanduser()
    if not folder.exists():
        raise FileExistsError(folder)

    def isfile_notdot(f: pathlib.Path) -> bool:
        return f.is_file() and f.name[0] != "."
    return list(filter(isfile_notdot, folder.iterdir()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--transpose', type=int, default=2,
        help="1 is 90 clock-wise; 2 (default) is 90 counter clock-wise. "
        "See more in https://ffmpeg.org/ffmpeg-filters.html#toc-transpose-1")
    parser.add_argument(
        '-s', '--speed', type=str, default="ultrafast",
        help="Should be one of fast and ultrafast (default)")
    parser.add_argument(
        'ffolder', help="The folder contains the video files to be rotated")
    parser.add_argument(
        'tfolder', help="The folder where the rotated files to be generated into")
    options = parser.parse_args()
    files = [pathlib.Path(f) for f in get_files(options.ffolder)]
    out_folder = pathlib.Path(options.tfolder)
    rotate(files, out_folder, options.speed, options.transpose)


if __name__ == "__main__":
    main()
