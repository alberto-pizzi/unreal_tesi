import os
import subprocess
import glob
import grpc
from pathlib import Path

import sys

BASE_DIR = Path.cwd()

# Configurazioni
API_KEY = "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"  # NVIDIA API
FUNCTION_ID = "8efc55f5-6f00-424e-afe9-26212cd2c630"  #  Mark model
CONFIG_YAML = BASE_DIR / "config" / "config_mark.yml"  # File YAM (mark) con emozioni
AUDIO_DIR = BASE_DIR / "input_audio_files/*.wav"  # Cartella input
OUTPUT_DIR = BASE_DIR / "output_csv" #cartella output
CLIENT_DIR = BASE_DIR/"Audio2Face-3D-Samples"/"scripts"/"audio2face_3d_api_client"

CLIENT_NAME = "nim_a2f_3d_client"

print("PYTHON:", sys.executable)
print("GRPC:", "grpc" in sys.modules or __import__("grpc"))



def batch_a2f_csv():
    OUTPUT_DIR.mkdir(exist_ok=True)

    client_path = CLIENT_DIR / CLIENT_NAME

    print("Client path: ", client_path)
    # Trova tutti i file WAV
    audio_file_paths = glob.glob(str(AUDIO_DIR))

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{CLIENT_DIR}:{BASE_DIR}"

    for audio_file_path in audio_file_paths:

        audio_file_path = Path(audio_file_path)

        audio_filename = audio_file_path.stem
        output_blendshapes = OUTPUT_DIR / f"{audio_filename}_blendshapes.csv"


        print(audio_file_path)
        print(audio_filename)
        print(output_blendshapes)

        cmd = [
            sys.executable,"-m", CLIENT_NAME,
            audio_file_path, CONFIG_YAML,
            "--apikey", API_KEY,
            "--function-id", FUNCTION_ID
        ]

        print(f"Processing: {audio_file_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=CLIENT_DIR, env=env)

        if result.returncode == 0:
            print(f"Completed: {output_blendshapes}")
        else:
            print(f"Error: {result.stderr}")

# FIXME da fixare tutto

if __name__ == "__main__":
    print("inizio main python")


    #print("prova_base: ", Path.cwd())
    batch_a2f_csv()
    print("fine main python")


    #subprocess.run("echo Ciao dal terminale", shell=True).
    #subprocess.run("python script_batch_csv2.py", shell=True)

