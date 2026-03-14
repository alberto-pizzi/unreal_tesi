import os
import subprocess
import glob
import grpc
from pathlib import Path


BASE_DIR = Path.cwd()

# Configurazioni
API_KEY = "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"  # NVIDIA API
FUNCTION_ID = "8efc55f5-6f00-424e-afe9-26212cd2c630"  #  Mark model
CONFIG_YAML = "config/config_mark.yml"  # File YAM (mark) con emozioni
AUDIO_DIR = "./input_audio_files"  # Cartella input
OUTPUT_DIR = "./output_csv" #cartella output
CLIENT_DIR = "./Audio2Face-3D-Samples/scripts/audio2face_3d_api_client"

CLIENT_NAME = "nim_a2f_3d_client.py"
outdir = "output_csv"


# FIXME da fixare e testare
def batch_a2f_csv():
    #OUTPUT_DIR.mkdir(exist_ok=True)

    client_path = CLIENT_DIR + "/" + CLIENT_NAME

    print("Client path: ", client_path)
    # Trova tutti i file WAV
    audio_file_paths = glob.glob(AUDIO_DIR+"/*.wav")
    print("Audio file paths: ", audio_file_paths)


    for audio_file_path in audio_file_paths:

        audio_file_path = Path(audio_file_path)



        audio_filename = audio_file_path.stem
        output_blendshapes = OUTPUT_DIR +"/"+ f"{audio_filename}_blendshapes.csv"


        print(audio_file_path)
        print(audio_filename)
        print(output_blendshapes)

        percorso_audio = Path(AUDIO_DIR) / f"{audio_filename}.wav"


        cmd = [
            "python", CLIENT_NAME,
            str(percorso_audio.resolve()), "./"+CONFIG_YAML,
            "--apikey", API_KEY,
            "--function-id", FUNCTION_ID
        ]

        print("Executing: ", cmd)

        print(f"Processing: {audio_file_path}")
        result = subprocess.run(cmd, capture_output=True, text=True,cwd=CLIENT_DIR)

        if result.returncode == 0:
            print(f"Completed: {output_blendshapes}")
        else:
            print(f"Error: {result.stderr}")

#TODO conviene rinominare anche i csv interni?
#funziona con i percorsi assoluti
def rename_folder(old_folder_name, new_folder_name):
    path = Path().cwd() #prendo percorso assoluto corrente
    folder_path = path /Path(outdir)
    os.rename(folder_path / old_folder_name, folder_path / new_folder_name)
    print(f"Renamed: {old_folder_name} -> {new_folder_name}")

# il prefisso dovrebbe essere "2026" secondo gli output, perché corrisponde all'anno di creazione del file output
def find_folder_names_by_prefix(prefix):
    path = Path().cwd() #prendo percorso assoluto corrente
    folder_path = path /Path(outdir)
    folders = [d.stem for d in folder_path.iterdir() if d.is_dir() and d.name.startswith(prefix)]
    return folders


if __name__ == "__main__":
    print("inizio main python")


    #print("prova_base: ", Path.cwd())
    #batch_a2f_csv()
    #rename_folder("C:/Users/alber/PycharmProjects/PythonProject1/output_csv/20260314_062333_765508","C:/Users/alber/PycharmProjects/PythonProject1/output_csv/provarinomina")
    #rename_folder(find_numerical_folder_names()[0],"rinominata")

    print("fine main python")


    #subprocess.run("echo Ciao dal terminale", shell=True).
    #subprocess.run("python script_batch_csv2.py", shell=True)

