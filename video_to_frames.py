import subprocess
import os
from pathlib import Path

# WARNING: to run this script, you must have ffmpeg installed into your active env BEFORE you run it.

videos_folder = "C:/Users/alber/Desktop/ProvaGenerazioneFramesDef"

def generate_frames_from_video(input_video_path:Path, output_folder:Path = None):

    #input_path = Path(video_path)
    rgb_video_folder_name = "rgb_frames"

    if output_folder:
        output_path = output_folder / rgb_video_folder_name / input_video_path.stem
    else:
        output_videos_folder_path = Path(videos_folder)
        output_path = output_videos_folder_path / rgb_video_folder_name / input_video_path.stem

    os.makedirs(output_path, exist_ok=True)

    command = [
        "ffmpeg",
        "-i", str(input_video_path),
        str(output_path / "frame_%05d.png")
    ]

    result = subprocess.run(command,capture_output=True, text=True)

    if result.returncode == 0:
        print("Successfully generated frames of video ", input_video_path)
    else:
        print("Failed to generate frames of video ", input_video_path)

def get_videos_into_folder_and_subfolders(input_folder:Path, file_extension:str):

    if not file_extension.startswith("."):
        file_extension = "." + file_extension

    file_founds = list(input_folder.rglob(f"*{file_extension}"))

    return file_founds

def generate_frames_from_videos(input_folder:Path,file_extension:str=".mp4"):
    
    video_paths = get_videos_into_folder_and_subfolders(input_folder, file_extension)
    
    for video_path in video_paths:
        generate_frames_from_video(video_path)


if __name__ == "__main__":
    videos_paths = Path(videos_folder)
    generate_frames_from_videos(videos_paths)

