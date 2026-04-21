import os
import subprocess
import sys
import yaml
import tempfile
from pathlib import Path
import audio_dataset_processing as adp
from audio_dataset_processing import limit_AudioInfo
from data_enums import Emotions

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

# Env settings
API_KEY = os.getenv("API_KEY")
FUNCTION_ID = os.getenv("FUNCTION_ID")

# Paths
AUDIO_DIR = BASE_DIR / "input_audio_files"  # input folder
OUTPUT_FOLDER = "output_csv" # output folder
CLIENT_NAME = "nim_a2f_3d_client.py"
CLIENT_DIR = BASE_DIR / "Audio2Face-3D-Samples"/"scripts"/"audio2face_3d_api_client"
OUTPUT_DIR = BASE_DIR / OUTPUT_FOLDER
CONFIG_YAML = CLIENT_DIR / "config" / "config_james.yml"

# Map dataset emotion labels to A2F emotion names (all 10 emotions the proto expects)
EMOTION_TO_A2F = {
    Emotions.HAPPY:   "joy",
    Emotions.SAD:     "sadness",
    Emotions.ANGRY:   "anger",
    Emotions.DISGUST: "disgust",
    Emotions.FEAR:    "fear",
    Emotions.NEUTRAL: None,  # neutral: let A2E infer freely
}

ALL_A2F_EMOTIONS = ["amazement", "anger", "cheekiness", "disgust", "fear", "grief", "joy", "outofbreath", "pain", "sadness"]


def make_emotion_config(emotion: Emotions) -> str:
    """Generate a per-file temp YAML config with the ground-truth emotion injected."""
    with open(CONFIG_YAML) as f:
        config = yaml.safe_load(f)

    a2f_emotion = EMOTION_TO_A2F.get(emotion)
    is_neutral = a2f_emotion is None

    if not is_neutral:
        # Populate timecode list — required for enable_preferred_emotion to work
        # Start at t=0.3 to let A2E stabilize before GT emotion fades in
        emotion_values = {e: (1.0 if e == a2f_emotion else 0.0) for e in ALL_A2F_EMOTIONS}
        config["emotion_with_timecode_list"] = {
            "emotion_gt_start": {"time_code": 0.3,   "emotions": emotion_values},
            "emotion_gt_end":   {"time_code": 100.0, "emotions": emotion_values},
        }
        config["post_processing_parameters"]["enable_preferred_emotion"] = True
        config["post_processing_parameters"]["preferred_emotion_strength"] = 0.7
    else:
        # Neutral: no overrides, let A2E infer freely
        config["emotion_with_timecode_list"] = {}
        config["post_processing_parameters"]["enable_preferred_emotion"] = False

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
    yaml.dump(config, tmp)
    tmp.close()
    print(f"  [tmp config] {tmp.name}")
    return tmp.name


# WARNING: this is a batch function
def batch_a2f_csv():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # find all WAV files
    wav_file_paths = list(AUDIO_DIR.glob("*.wav"))
    print("Audio file paths: ", str(wav_file_paths))

    audio_files_processed = adp.process_audio_to_AudioInfo(wav_file_paths, adp.Dataset_CREMA_D)

    for audio_info in audio_files_processed:
        run_a2f(audio_info.path, audio_info.emotion)


def run_a2f(audio_file_path: Path, emotion: Emotions):
    print(f"Processing: {audio_file_path.stem} | emotion: {emotion}")

    tmp_config = make_emotion_config(emotion)
    print(f"  GT emotion override: {emotion} -> {EMOTION_TO_A2F.get(emotion)}")

    try:
        cmd = [
            sys.executable, str(CLIENT_DIR / CLIENT_NAME),
            str(audio_file_path), tmp_config,
            "--apikey", API_KEY,
            "--function-id", FUNCTION_ID
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)

        if result.returncode == 0:
            folder = find_folder_names_by_prefix("2026")[0]
            rename_folder(folder, audio_file_path.stem)
            print(f"  Completed: {audio_file_path.stem}")
        else:
            print(f"  Error: {result.stderr}")
    finally:
        os.unlink(tmp_config)

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
    """
    wav_file_paths = list(AUDIO_DIR.glob("*.wav"))
    print("Audio file paths: ", str(wav_file_paths))

    # TODO add dataset
    audio_files_processed = adp.process_audio_to_AudioInfo(wav_file_paths,adp.Dataset_CREMA_D)
    audio_files_filtered = adp.filter_AudioInfo_by(audio_files_processed,emotions=[adp.d_maps.Emotions.HAPPY])
    """

    #print(audio_files_filtered)

    print("end main python")

