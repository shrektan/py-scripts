"""Simplify The File Tree
Quickly flat the file structure by removing the first level directories
"""
import sys
import os
import shutil
import subprocess

target = ""
if len(sys.argv) >= 2:
    target = sys.argv[1].strip()
if len(target) == 0:
    target = input("Please enter the target folder:\n").strip()
if len(target) == 0 or os.path.exists(target) is False or \
   os.path.isdir(target) is False:
    msg = f"You must provide a valid folder (current input is '{target}')"
    raise FileExistsError(msg)
rm_empty_folder = input("Clean the empty folder? [y]/n\n") != "n"

def simplify(target: str, rm_empty_folder: bool):
    for entry in os.scandir(target):
        if entry.is_dir():
            for f in os.scandir(entry.path):
                file_name = f.name
                if file_name[0] == ".":
                    continue
                if file_name == entry.name:
                    file_name = "0-" + file_name
                dest = os.path.join(target, file_name)
                shutil.move(f.path, dest)
            if rm_empty_folder:
                os.removedirs(entry.path)

simplify(target, rm_empty_folder)
print(f"{target=} cleaned.")
# by adding the check=True, we can be sure that an error raised if it fails
subprocess.run(["open", target], check=True)
