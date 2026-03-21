# FIXME add it into main file
import sys
import os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)


import unreal
import csv
import time
from a2f_rig_maps import A2F_TO_METAHUMAN


# config
#TODO edit paths

CSV_PATH = r"C:/Users/alber/Desktop/"
ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations/"
FRAME_RATE = 30.0

SKELETON_PATH = "/Game/MetaHumans/Common/Face/"
SKELETON_NAME = "Face_Archetype_Skeleton"
#LS_PATH = "/Game/LevelSequences/" # FIXME
LS_PATH = "/Game/"

#prefixes
csv_prefix = "blendShapes."
time_code_tag = "timeCode"

def load_level_sequence(seq_filename:str):
    full_path = LS_PATH + seq_filename + "." + seq_filename
    level_sequence = unreal.load_asset(full_path)
    return level_sequence

def load_anim_sequence(anim_seq_filename:str):
    full_path = ANIMATION_PATH + anim_seq_filename + "." + anim_seq_filename
    anim_sequence = unreal.load_asset(full_path)
    return anim_sequence

def read_csv(filename):

    with open(CSV_PATH + filename, newline='') as f:
        reader = csv.DictReader(f)
        # remove prefix from all blendshapes
        cleaned_keys  = [key.strip().removeprefix(csv_prefix)
                             for key in reader.fieldnames if key.strip() != '']
        arkit_csv_names = cleaned_keys.copy()
        rows = list(reader)

    #remove first element "timeCode"
    if arkit_csv_names and arkit_csv_names[0] == time_code_tag:
        arkit_csv_names.pop(0)

    if not rows:
        raise RuntimeError("CSV is empty or malformed")

    print("CSV read successfully")
    return rows,arkit_csv_names

#mapping
def map_blendshapes(csv_names,map):
    #create list of face control rigs mapped
    morphs_mh = []
    for arkit_name in csv_names:
        if arkit_name in map:
            morph_mh = map[arkit_name]
            morphs_mh.append(morph_mh)

    print("Mapping completed!")
    return morphs_mh

# IMPORTANT: insert keyframes into actor face control rigs
def insert_keyframes(level_sequence,weights_read_from_csv):
    rig_proxies = unreal.ControlRigSequencerLibrary.get_control_rigs(level_sequence)

    face_rig = None
    for proxy in rig_proxies:
        if proxy.control_rig.get_name() == 'Face_ControlBoard_CtrlRig':
            face_rig = proxy.control_rig
            print("Good to go!")
            break

    if face_rig:
        for row in weights_read_from_csv:
            print("Calculating frame: ", row[''])
            for blendshape in A2F_TO_METAHUMAN:
                csv_blendshape_key = csv_prefix+blendshape
                if csv_blendshape_key in row:
                    for face_control_rig in A2F_TO_METAHUMAN[blendshape]:
                        unreal.ControlRigSequencerLibrary.set_local_control_rig_float(level_sequence, face_rig, unreal.Name(face_control_rig),
                                                                          unreal.FrameNumber(int(row[''])), float(row[csv_blendshape_key]))

    # FIXME is correct pos?
    level_sequence.set_playback_start(0)
    level_sequence.set_playback_end(int(weights_read_from_csv[-1]['']))
    print("Keyframe calculation complete!")


def bake_to_animation_sequence(level_sequence,anim_seq_filename:str):
    binding = level_sequence.find_binding_by_name("Face")

    # set skeleton
    skeleton = unreal.load_object(None,SKELETON_PATH+SKELETON_NAME+"."+SKELETON_NAME)
    factory = unreal.AnimSequenceFactory()
    factory.set_editor_property("target_skeleton", skeleton)

    # get world
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()

    # export settings
    anim_seq_export_options = unreal.AnimSeqExportOption()
    anim_seq_export_options.export_transforms = True
    anim_seq_export_options.export_morph_targets = True

    # create asset
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    anim_sequence = unreal.AssetTools.create_asset(
        asset_tools,
        asset_name=anim_seq_filename,
        package_path=ANIMATION_PATH,
        asset_class=unreal.AnimSequence,
        factory=factory
    )

    # bake to animation sequence
    unreal.SequencerTools.export_anim_sequence(
        world,
        level_sequence,
        anim_sequence,
        anim_seq_export_options,
        binding,
        create_link=False
    )

    #save
    asset_path = anim_sequence.get_path_name()
    success = unreal.EditorAssetLibrary.save_asset(asset_path)

    print("Bake executed successfully!")

# TODO could be improved giving animation sequence instead filename?
#WARNING: Metahumans into level sequence must be only ONE!
def attach_anim_sequence_to_face(level_sequence,anim_seq_filename:str):
    binding = level_sequence.find_binding_by_name("Face")

    anim_sequence = load_anim_sequence(anim_seq_filename)

    animation_length_seconds = anim_sequence.get_play_length()

    frame_rate = level_sequence.get_display_rate()
    fps = frame_rate.numerator / frame_rate.denominator

    animation_length_frames = int(animation_length_seconds * fps)

    # FIXME is correct pos?
    '''
    level_sequence.set_playback_start(0)
    level_sequence.set_playback_end(animation_length_frames)'''

    anim_track = binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.set_range(0, animation_length_frames)
    anim_section.params.animation = anim_sequence

    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
    unreal.EditorAssetLibrary.save_asset(level_sequence.get_path_name())

    print("Attached animation sequence to face done successfully!")

def get_csv_file_list(directory:str):
    results = []

    for filename in os.listdir(directory):
        if filename.lower().endswith(".csv"):
            results.append(filename)

    return results

def find_binding(level_sequence):
    binding = level_sequence.find_binding_by_name("Body")
    print(binding.get_tracks()[0].get_display_name())

if __name__ == '__main__':
    start = time.time()

    ls = load_level_sequence("SeqVM")

    #print(get_csv_list(CSV_PATH))

    #attach_anim_sequence_to_face(ls,"NewLipSync")

    #get_all_binding(ls)
    #find_binding(ls)
    #rows, arkit_csv_names = read_csv("animation_frames.csv")
    #insert_keyframes(ls,rows)
    #bake_to_animation_sequence(ls,"VMRig")
    #import_audio_as_asset("1001_DFA_HAP_XX.wav")



    end = time.time()
    print("Time elapsed: " + str(end-start) + " seconds")