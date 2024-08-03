import os
import shutil
import sys
from pathlib import Path

current_file = Path(__file__).parent
base_dir = current_file.parent

def move_file(source_path, destination_path):
    if not os.path.isfile(source_path):
        print(f"Source file does not exist: {source_path}")
        sys.exit(1)
    if not os.path.isdir(os.path.dirname(destination_path)):
        print(f"Destination directory does not exist: {os.path.dirname(destination_path)}")
        sys.exit(1)

    shutil.copy2(source_path, destination_path)
    print(f"Moved {source_path} to {destination_path}")

if __name__ == "__main__":
    move_file(
        os.path.join(base_dir,'readme.md'), os.path.join(base_dir,'helper_scripts','readme.md')
    )
    move_file(
        os.path.join(base_dir,'LICENSE'), os.path.join(base_dir,'helper_scripts','LICENSE')
        )
