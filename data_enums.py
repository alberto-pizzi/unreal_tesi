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

class AgeCategory(Enum):
    CHILD = "child"
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    SENIOR = "senior"

class EthnicGroup(Enum):
    EUROPEAN = "european"
    AFRO = "afro"
    EAST_ASIAN = "east_asian"
    SOUTH_ASIAN = "south_asian"
    SOUTHEAST_ASIAN = "southeast_asian"
    MIDDLE_EASTERN = "middle_eastern"
    INDIGENOUS_AMERICANS = "indigenous_americans"
    OCEANIC = "oceanic"
    MIXED = "mixed"

