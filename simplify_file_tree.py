"""Simplify The File Tree

Quickly flat the file structure by removing the first level directories
"""

import sys
import pathlib
import subprocess


def simplify(tgt: str, rm_empty_folder: bool):
    """Simplify the file tree

    Args:
        tgt (str): the directory to be simplified
        rm_empty_folder (bool): wheter the empty folder to be removed or not
    """
    target = pathlib.Path(tgt)
    for entry in target.iterdir():
        if entry.is_dir():
            for f in entry.iterdir():
                if f.name == ".DS_Store":
                    f.unlink()
                    continue
                fname = f.name
                while (dest := target / fname).exists():
                    fname = "0_" + fname
                f.rename(dest)
            if rm_empty_folder:
                entry.rmdir()


def main() -> None:
    target = ""
    if len(sys.argv) >= 2:
        target = sys.argv[1].strip()
    if len(target) == 0:
        target = input("Please enter the target folder:\n").strip()
    if len(target) == 0 or pathlib.Path(target).is_dir() is False:
        msg = f"You must provide a valid folder (current input is '{target}')"
        raise FileExistsError(msg)
    rm_empty_folder = input("Clean the empty folder? [y]/n\n") != "n"

    simplify(target, rm_empty_folder)
    print(f"{target=} cleaned.")
    # by adding the check=True, we can be sure that an error raised if it fails
    subprocess.run(["open", target], check=True)


if __name__ == "__main__":
    main()
