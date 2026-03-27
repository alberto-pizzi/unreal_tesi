from data_enums import Emotions, Intensity, AudioInfoEnum, Genders



# maps for training (emotion recognition)
LABEL2ID = {emotion.value: idx for idx, emotion in enumerate(Emotions)}
ID2LABEL = {idx: emotion.value for idx, emotion in enumerate(Emotions)}


CREMA_D_MAP = {
    AudioInfoEnum.EMOTIONS: {
        "HAP": Emotions.HAPPY,
        "SAD": Emotions.SAD,
        "ANG": Emotions.ANGRY,
        "DIS": Emotions.DISGUST,
        "FEA": Emotions.FEAR,
        "NEU": Emotions.NEUTRAL,
    },
    AudioInfoEnum.INTENSITY: {
        "MD": Intensity.NORMAL,
        "HI": Intensity.HIGH,
        "LO": Intensity.LOW,
        "XX": Intensity.UNSPECIFIED,
    },
    AudioInfoEnum.GENRE: {
        "Male": Genders.MALE,
        "Female": Genders.FEMALE,
    }
}

RAVDESS_MAP = {
    AudioInfoEnum.EMOTIONS: {
        "05": Emotions.ANGRY,
        "07": Emotions.DISGUST,
        "06": Emotions.FEAR,
        "04": Emotions.SAD,
        "03": Emotions.HAPPY,
        "01": Emotions.NEUTRAL,
        "02": Emotions.CALM,
        "08": Emotions.SURPRISED,
    },
    AudioInfoEnum.INTENSITY: {
        "01": Intensity.NORMAL,
        "02": Intensity.HIGH,
    },
    AudioInfoEnum.GENRE: {
        "MALE": Genders.MALE,
        "FEMALE": Genders.FEMALE,
    }
}