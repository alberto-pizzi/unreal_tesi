from dataclasses import dataclass
from typing import Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import audio_dataset_maps as d_maps


@dataclass
class AudioInfo:
    path: Path
    actor: str
    emotion: d_maps.Emotions
    sentence: str
    intensity: d_maps.Intensity = d_maps.Intensity.UNSPECIFIED
    extra: Dict[str, Any] = None


# abstract class
class AudioDatasetParser(ABC):
    MAP: Dict[d_maps.AudioInfoEnum, Any] = {}

    @abstractmethod
    def parse(self, filename_path: Path) -> AudioInfo:
        pass

    def decode_info(self, emotion_encoded,intensity_encoded):
        emotion_decoded = self.MAP[d_maps.AudioInfoEnum.EMOTIONS][emotion_encoded]
        intensity_decoded = self.MAP[d_maps.AudioInfoEnum.INTENSITY][intensity_encoded]
        return emotion_decoded, intensity_decoded


# dataset classes

class Dataset_CREMA_D(AudioDatasetParser):
    MAP = d_maps.CREMA_D_MAP

    def parse(self, filename_path: Path) -> AudioInfo:
        filename = filename_path.stem
        split = filename.split("_")

        actor_encoded = split[0]
        sentence_encoded = split[1]
        emotion_encoded = split[2]
        intensity_encoded = split[3]

        emotion_decoded, intensity_decoded = self.decode_info(emotion_encoded, intensity_encoded)

        return AudioInfo(path=filename_path, actor=actor_encoded, emotion=emotion_decoded, sentence=sentence_encoded, intensity=intensity_decoded)

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

        return AudioInfo(path=filename_path, actor=actor_encoded, emotion=emotion_decoded, sentence=sentence_encoded, intensity=intensity_decoded)





