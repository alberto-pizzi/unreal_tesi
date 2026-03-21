from enum import Enum

from a2f_rig_maps import A2F_TO_METAHUMAN


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
        return frame_row.get(self.name, 0.0)

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
        y = frame_row.get("JawOpen", 0)
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

    def calculate(self, frame_row: dict):
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

    def calculate(self, frame_row: dict):
        x = frame_row.get("TongueWide", 0) - frame_row.get("TongueNarrow", 0)
        return x




