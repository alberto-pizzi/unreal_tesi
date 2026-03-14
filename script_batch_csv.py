import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# Settings
API_KEY = "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"  # NVIDIA API
FUNCTION_ID = "8efc55f5-6f00-424e-afe9-26212cd2c630"  #  Mark model
AUDIO_DIR = BASE_DIR / "input_audio_files"  # input folder
OUTPUT_FOLDER = "output_csv" # output folder
CLIENT_NAME = "nim_a2f_3d_client.py"
CLIENT_DIR = BASE_DIR / "Audio2Face-3D-Samples"/"scripts"/"audio2face_3d_api_client"
OUTPUT_DIR = BASE_DIR / OUTPUT_FOLDER
CONFIG_YAML = CLIENT_DIR / "config" / "config_mark.yml"  # file YAM (mark) with emotions



def batch_a2f_csv():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # find all WAV files
    wav_file_paths = list(AUDIO_DIR.glob("*.wav"))
    print("Audio file paths: ", str(wav_file_paths))

    for wav_file_path in wav_file_paths:
        run_a2f(wav_file_path)

def run_a2f(audio_file_path: Path):
    client_path = CLIENT_DIR / CLIENT_NAME
    print("Client path: ", str(client_path))

    audio_filename = audio_file_path.stem
    #output_blendshapes = OUTPUT_DIR / f"{audio_filename}_blendshapes.csv"
    #print(str(output_blendshapes))
    # print(str(audio_file_path))

    print(str(audio_filename))

    cmd = [
        sys.executable, str(CLIENT_DIR/CLIENT_NAME),
        str(audio_file_path), str(CONFIG_YAML),
        "--apikey", API_KEY,
        "--function-id", FUNCTION_ID
    ]

    print("Executing: ", cmd)

    print(f"Processing: {str(audio_file_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)

    if result.returncode == 0:
        folder = find_folder_names_by_prefix("2026")[0]
        rename_folder(folder, audio_filename)
        print(f"Completed: {audio_filename}")
    else:
        print(f"Error: {result.stderr}")

#TODO conviene rinominare anche i csv interni?
def rename_folder(old_folder_name, new_folder_name):
    path = Path().cwd() #take current absolute path
    folder_path = path /Path(OUTPUT_FOLDER)
    os.rename(folder_path / old_folder_name, folder_path / new_folder_name)
    print(f"Renamed: {old_folder_name} -> {new_folder_name}")

# WARNING: the prefix should be "2026" according to the outputs, because it corresponds to the year of creation of the output file
def find_folder_names_by_prefix(prefix):
    path = Path().cwd() #take current absolute path
    folder_path = path /Path(OUTPUT_FOLDER)
    folders = [d.stem for d in folder_path.iterdir() if d.is_dir() and d.name.startswith(prefix)]
    return folders


if __name__ == "__main__":
    print("start main python")

    batch_a2f_csv()

    print("end main python")

