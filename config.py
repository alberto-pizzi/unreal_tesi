# CONFIG FILE

# IMPORTANT :Unreal accepts ONLY paths UNIX-like

# PREFERENCES
GENERATE_ANIMATION_SEQUENCE = False # Set False if you already have animation sequences. Set True if not, generating them.
IMPORT_AUDIO_ASSETS = False # Set False if you already have audio as ASSETS. Set True if not, importing them.
GENERATE_LS_FOREACH_MH = True
MAKE_LS_WITH_AUDIO = True

# RENDERING (MRQ)
IMPORT_ALL_LS_INTO_MRQ = False


# PATHS
# TODO paths to be set

# input paths
INPUT_AUDIO_PATH = "C:/Users/alber/PycharmProjects/PythonProject1/input_audio_files/"
CSV_FOLDER_PATH = r"C:/Users/alber/Desktop/"




# unreal Paths
TMP_LS_BASE_PATH = "/Game/LevelSequences/TmpSequences/"
ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations/"
AUDIO_ASSETS_PATH = "/Game/AudioAssetImported/"
MH_BASE_PATH = "/Game/MetaHumans/"
LS_BASE_PATH = "/Game/LevelSequences/SequencesToRender/"
LS_PATH_TMP = "/Game/" #TODO to be delete
SKELETON_PATH = "/Game/MetaHumans/Common/Face/"
SKELETON_NAME = "Face_Archetype_Skeleton"
#LS_PATH = "/Game/LevelSequences/" # FIXME
LS_PATH = "/Game/"
LEVELS_PATH = "/Game/Levels/"
LEVEL_NAME = "BaseLevel"
QUEUES_PATH = "/Game/RenderingQueues/"



# insert ONLY MetaHumans installed into project
# TODO to be completed
METAHUMANS_INSTALLED = [
    "Bryan",

]

camera_settings = {
    "AspectRatio": 1.2,
    "FieldOfView": 85.0,
}

# RENDERING SETTINGS

RENDERING_SETTINGS_PATH = "/Game/RenderingSettings/"
RENDERING_SETTINGS_NAME = "mp4_1280x720"

