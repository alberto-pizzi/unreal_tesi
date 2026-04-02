
import subprocess
from pathlib import Path

# WARNING: to run this script, you have to activate your conda env (also with ffmpeg) BEFORE you run it.

videos_folder = "C:/Users/alber/Downloads/MiniDataset/provavide"

# IMPORTANT: set these directories with yours
bash_dir = "C:/Program Files/Git/bin/bash.exe"
frames2v_directory = "C:/Users/alber/PycharmProjects/ESIMtesi/frames2v/frames2v"


def generate_events_for_each_videos(videos_folder:Path,min_fps:str= "0", img_height:str= "", img_width:str= ""):
    frames2v_directory_path = Path(frames2v_directory)

    command = [
        Path(bash_dir),
        "frames_to_ev.sh",
        videos_folder,
        min_fps,
        img_height,
        img_width,
    ]

    result = subprocess.run(command,capture_output=True, text=True, cwd=frames2v_directory_path)

    if result.returncode == 0:
        print("Successfully generated all events ")
    else:
        print("Failed to generate events")



if __name__ == "__main__":

    generate_events_for_each_videos(Path(videos_folder))
