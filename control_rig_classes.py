from enum import Enum

from a2f_involved_rig_maps import A2F_TO_METAHUMAN


def theshold_boosts(x,low_threshold:float, high_threshold:float,base:float):
    if x < low_threshold:
        dist = (low_threshold - x) / low_threshold
        boosted = base * (1 + dist)
    elif x > high_threshold:
        dist = (x - high_threshold) / (1 - high_threshold)
        boosted = base * (1 + dist)
    else:
        boosted = base

    return boosted

class RigType(Enum):
    FLOAT = "float"
    VEC2  = "vec2"

class SourceType(Enum):
    DEFAULT = 1
    VEC2 = 2



# TODO by frame or in block
class ControlRig:
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name: str):
        self.name = name
        self.type = self.DEFAULT_TYPE
        # blendshape_sources are every blendshape useful to calculation of new value (it is like an archive)
        #self.blendshape_sources = blendshape_sources
    # default calculation is float. it calculates on CSV BLENDSHAPES
    def calculate(self, frame_row: dict, source_blendshape: str = None):
        key = source_blendshape if source_blendshape else self.name
        return frame_row.get(key, 0.0)

    # TODO to be deleted?
    def normalize(self, values):
        return values



class EyeCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = frame_row.get("EyeLookOutLeft", 0) - frame_row.get("EyeLookInLeft", 0)
        y = frame_row.get("EyeLookUpLeft", 0) - frame_row.get("EyeLookDownLeft", 0)
        return x, y

class JawOpenCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = frame_row.get("JawLeft", 0) - frame_row.get("JawRight", 0)
        y = frame_row.get("JawOpen", 0) * 0.42
        return x, y

class MouthCornerLeftCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = frame_row.get("MouthLeft", 0) - frame_row.get("MouthRight", 0)
        y = frame_row.get("MouthSmileLeft", 0) - frame_row.get("MouthFrownLeft", 0)
        return x, y

class MouthCornerRightCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = frame_row.get("MouthRight", 0) - frame_row.get("MouthLeft", 0)
        y = frame_row.get("MouthSmileRight", 0) - frame_row.get("MouthDepressRight", 0)
        return x, y

class NoseLeftCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = 0
        y = frame_row.get("NoseSneerLeft", 0)
        return x, y

class NoseRightCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = 0
        y = frame_row.get("NoseSneerRight", 0)
        return x, y

class TongueInOutCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = frame_row.get("TongueIn", 0) - frame_row.get("TongueOut", 0)
        return x

class TongueMoveCR(ControlRig):
    DEFAULT_TYPE = RigType.VEC2

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict):
        x = frame_row.get("TongueLeft", 0) - frame_row.get("TongueRight", 0)
        y = frame_row.get("TongueUp", 0) - frame_row.get("TongueDown", 0)
        return x, y

class TongueWideNarrowCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = frame_row.get("TongueWide", 0) - frame_row.get("TongueNarrow", 0)
        return x

class FaceScrunchLeftCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = 0.55*frame_row.get("CheekSquintLeft", 0) + frame_row.get("EyeSquintLeft", 0)*0.25
        return x

class FaceScrunchRightCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = 0.6*frame_row.get("CheekSquintRight", 0) + frame_row.get("EyeSquintRight", 0)*0.3
        return x

class EyeBlinkRightCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = frame_row.get("EyeBlinkRight", 0)

        base = (2*x-1)*0.58

        low_threshold = 0.2
        high_threshold = 0.8

        #boosted = theshold_boosts(x, low_threshold, high_threshold, base)

        return base


class EyeBlinkLeftCR(ControlRig):
    DEFAULT_TYPE = RigType.FLOAT

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, frame_row: dict,source_blendshape: str = None):
        x = frame_row.get("EyeBlinkLeft", 0)
        base = (2*x-1)*0.54

        low_threshold = 0.2
        high_threshold = 0.8

        #boosted = theshold_boosts(x, low_threshold, high_threshold, base)

        return base




