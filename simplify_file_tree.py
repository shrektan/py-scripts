"""Simplify The File Tree

Quickly flat the file structure by removing the first level directories
"""

import argparse
import pathlib
import subprocess


def simplify(tgt: str, rm_empty_folder: bool):
    """Simplify the file tree

    Args:
        tgt (str): the directory to be simplified
        rm_empty_folder (bool): whether the empty folder to be removed or not
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k', '--keepsubfolder', action='store_true', default=False,
        help="Keep the empty subfolder")
    parser.add_argument(
        '-o', '--open', action='store_true', default=False,
        help="Open the folder when finished")
    parser.add_argument(
        'target', help="The folder to be simplified")
    options = parser.parse_args()
    target = options.target
    if len(target) == 0 or pathlib.Path(target).is_dir() is False:
        msg = f"You must provide a valid folder (current input is '{target}')"
        raise FileExistsError(msg)
    simplify(target, not options.keepsubfolder)
    print(f"{target=} cleaned.")
    if options.open:
        # by adding the check=True, we can be sure that an error raised if it fails
        subprocess.run(["open", target], check=True)


if __name__ == "__main__":
    main()
