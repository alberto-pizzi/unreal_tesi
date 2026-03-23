from audio_dataset_classes import *
from typing import Type

DATASET_TYPE = {
    "RAVDESS": Dataset_RAVDESS,
    "CREMA-D": Dataset_CREMA_D,
}


def process_audio_to_AudioInfo(paths: list[Path],DatasetClass:Type[AudioDatasetParser]) -> list[AudioInfo]:
    audio_processed = []

    for path in paths:
        instance = DatasetClass()
        audio_processed.append(instance.parse(path))

    return audio_processed

def filter_AudioInfo_by(AudioInfo_list:list[AudioInfo],emotions=None, genders = None, actors = None, intensity = None) -> list[AudioInfo]:

    if emotions and not isinstance(emotions, list):
        emotions = [emotions]
    if genders and not isinstance(genders, list):
        genders = [genders]
    if actors and not isinstance(actors, list):
        actors = [actors]
    if intensity and not isinstance(intensity, list):
        intensity = [intensity]

    return [
        instance for instance in AudioInfo_list
        if (not emotions or instance.emotion in emotions)
        and (not genders or instance.gender in genders)
           and (not actors or instance.actor in actors)
           and (not intensity or instance.intensity in intensity)

        # you can add here other filters...
    ]

def limit_AudioInfo(AudioInfo_list:list[AudioInfo], max_value_by_parameter:int, class_field_name:str) -> list[AudioInfo]:
    if not max_value_by_parameter or not class_field_name:
        return AudioInfo_list

    groups = {}

    # group by
    for item in AudioInfo_list:
        key = getattr(item, class_field_name)
        groups[key].append(item)

    # limit
    limited_list = []
    for items in groups.values():
        limited_list.extend(items[:max_value_by_parameter])

    return limited_list





