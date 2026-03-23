from enum import Enum

class Emotions(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    FEAR = "fear"
    DISGUST = "disgust"
    CALM = "calm"
    SURPRISED = "surprised"

class Intensity(Enum):
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"
    UNSPECIFIED = "unspecified"

# TODO add lambda?
class AudioInfoEnum(Enum):
    ACTOR = "actor"
    SENTENCE = "sentence"
    EMOTIONS = "emotions"
    INTENSITY = "intensity"
    GENRE = "genre"

class Genders(Enum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"



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