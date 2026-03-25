# CONFIG FILE

# IMPORTANT :Unreal accepts ONLY paths UNIX-like
# ESSENTIAL: these boolean variables are ESSENTIALS to function.

# PREFERENCES
GENERATE_ANIMATION_SEQUENCE = True # Set False if you already have animation sequences. Set True if not, generating them.
IMPORT_AUDIO_ASSETS = False # Set False if you already have audio as ASSETS. Set True if not, importing them.
GENERATE_LS_FOREACH_MH = True
MAKE_LS_WITH_AUDIO = True

# RENDERING (MRQ)
IMPORT_ALL_LS_INTO_MRQ = True


# PATHS
# TODO paths to be set

# input paths
INPUT_AUDIO_PATH = "C:/Users/alber/PycharmProjects/PythonProject1/input_audio_files/"
#CSV_FOLDER_PATH = r"C:/Users/alber/Desktop/"
CSV_FOLDER_PATH = r"C:/Users/alber/PycharmProjects/PythonProject1/output_csv/"




# unreal Paths
TMP_LS_BASE_PATH = "/Game/LevelSequences/TmpSequences/"
ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations/"
#ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations/ProvaAnimazioni/"

AUDIO_ASSETS_PATH = "/Game/AudioAssetImported/"
MH_BASE_PATH = "/Game/MetaHumans/"
LS_BASE_PATH = "/Game/LevelSequences/SequencesToRender/"
SKELETON_PATH = "/Game/MetaHumans/Common/Face/"
SKELETON_NAME = "Face_Archetype_Skeleton"
LEVELS_PATH = "/Game/Levels/"
LEVEL_NAME = "BaseLevel"



# insert ONLY MetaHumans installed into project
# TODO to be completed
METAHUMANS_INSTALLED = [
    "Bryan",
    "Myles",
    "Zeva",
    "Bernice",

]

camera_settings = {
    "AspectRatio": 1.778,
    "FieldOfView": 50.0,
}

# RENDERING SETTINGS

RENDERING_SETTINGS_PATH = "/Game/RenderSettings/"
RENDERING_SETTINGS_NAME = "mp4desktop"

QUEUES_PATH = "/Game/RenderQueues/"
QUEUE_NAME = "EmptyQueue"