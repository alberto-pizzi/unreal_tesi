from dataclasses import dataclass
from typing import Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import audio_dataset_maps as d_maps
import csv



@dataclass
class AudioInfo:
    path: Path
    actor: str
    emotion: d_maps.Emotions
    sentence: str
    gender: d_maps.Genders = d_maps.Genders.UNSPECIFIED
    intensity: d_maps.Intensity = d_maps.Intensity.UNSPECIFIED
    extra: Dict[str, Any] = None




# abstract class
class AudioDatasetParser(ABC):
    MAP: Dict[d_maps.AudioInfoEnum, Any] = {}

    @abstractmethod
    def parse(self, filename_path: Path) -> AudioInfo:
        pass

    @abstractmethod
    def get_emotion_label(self, folder_name: str) -> d_maps.Emotions:
        pass


    def decode_info(self, emotion_encoded,intensity_encoded):
        emotion_decoded = self.MAP[d_maps.AudioInfoEnum.EMOTIONS][emotion_encoded]
        intensity_decoded = self.MAP[d_maps.AudioInfoEnum.INTENSITY][intensity_encoded]
        return emotion_decoded, intensity_decoded


# dataset classes

class Dataset_CREMA_D(AudioDatasetParser):
    MAP = d_maps.CREMA_D_MAP

    # TODO add path
    CSV_PATH = "C:/Users/alber/Desktop/VideoDemographics.csv"

    def parse(self, filename_path: Path) -> AudioInfo:
        filename = filename_path.stem
        split = filename.split("_")

        actor_encoded = split[0]
        sentence_encoded = split[1]
        emotion_encoded = split[2]
        intensity_encoded = split[3]

        emotion_decoded, intensity_decoded = self.decode_info(emotion_encoded, intensity_encoded)

        data = self.read_csv_file(Path(self.CSV_PATH))

        csv_gender = data[int(actor_encoded)-1001]["Sex"]

        if csv_gender in d_maps.CREMA_D_MAP[d_maps.AudioInfoEnum.GENRE]:
            gender = d_maps.CREMA_D_MAP[d_maps.AudioInfoEnum.GENRE][csv_gender]
        else:
            gender = d_maps.Genders.UNSPECIFIED


        return AudioInfo(path=filename_path, actor=actor_encoded, emotion=emotion_decoded, sentence=sentence_encoded, intensity=intensity_decoded, gender=gender)

    @staticmethod
    def read_csv_file(filename_path: Path):
        actors = []
        with filename_path.open( newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # convert to int
                row['ActorID'] = int(row['ActorID'])
                row['Age'] = int(row['Age'])
                actors.append(row)
        return actors

    def get_emotion_label(self, folder_name: str) -> d_maps.Emotions:
        split = folder_name.split("_")

        emotion_detected = split[3]

        return  d_maps.CREMA_D_MAP[d_maps.AudioInfoEnum.EMOTIONS][emotion_detected]



class Dataset_RAVDESS(AudioDatasetParser):
    MAP = d_maps.RAVDESS_MAP

    def parse(self, filename_path: Path) -> AudioInfo:
        filename = filename_path.stem
        split = filename.split("-")

        emotion_encoded = split[2]
        intensity_encoded = split[3]
        sentence_encoded = split[4]
        actor_encoded = split[6]

        emotion_decoded, intensity_decoded = self.decode_info(emotion_encoded, intensity_encoded)

        # from documentation
        if int(actor_encoded) % 2 == 0:
            gender = d_maps.Genders.FEMALE
        else:
            gender = d_maps.Genders.MALE


        return AudioInfo(path=filename_path, actor=actor_encoded, emotion=emotion_decoded, sentence=sentence_encoded, intensity=intensity_decoded,gender=gender)


    def get_emotion_label(self, folder_name: str) -> d_maps.Emotions:
        split = folder_name.split("-")

        emotion_detected = split[3]

        return d_maps.RAVDESS_MAP[d_maps.AudioInfoEnum.EMOTIONS][emotion_detected]