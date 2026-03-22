# FIXME add it into main file
import sys
import os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)


import unreal
import csv
import time
from a2f_involved_rig_maps import A2F_TO_METAHUMAN
import contro_rig_processing as crp
#import control_rig_maps as crm


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
CSV_PREFIX = "blendShapes."
time_code_tag = "timeCode"

def load_level_sequence(seq_filename:str):
    full_path = LS_PATH + seq_filename + "." + seq_filename
    level_sequence = unreal.load_asset(full_path)
    return level_sequence

# TODO delete arkit_csv_names?
def read_csv_by_row(filename):

    with open(CSV_PATH + filename, newline='') as f:
        reader = csv.DictReader(f)
        # remove prefix from all blendshapes
        reader.fieldnames  = [key.strip().removeprefix(CSV_PREFIX)
                             for key in reader.fieldnames]
        rows = list(reader)


    if not rows:
        raise RuntimeError("CSV is empty or malformed")

    print("CSV read successfully")
    return rows

"""
    Reads a CSV and converts values as follows:
    - First column: int
    - Other columns: float
    - Headers: strings
    Returns a list of dictionaries.
"""
def read_csv_with_conversion(filename):

    data = []
    with open(CSV_PATH + filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames  = [key.strip().removeprefix(CSV_PREFIX)
                             for key in reader.fieldnames]
        for row in reader:
            new_row = {}
            for i, (key, value) in enumerate(row.items()):
                if i == 0:
                    # First column -> int
                    new_row[key] = unreal.FrameNumber(int(value))
                else:
                    # Other columns -> float
                    new_row[key] = float(value)
            data.append(new_row)
    return data


def transpose_rows_to_columns(rows):
    if not rows:
        raise RuntimeError("Input rows are empty")

    fieldnames = rows[0].keys()

    columns = {field: [] for field in fieldnames}
    for row in rows:
        for field in fieldnames:
            columns[field].append(row[field])

    return columns


# IMPORTANT: insert keyframes into actor face control rigs
def insert_keyframes_by_row(level_sequence, csv_rows):
    rig_proxies = unreal.ControlRigSequencerLibrary.get_control_rigs(level_sequence)

    face_rig = None
    for proxy in rig_proxies:
        if proxy.control_rig.get_name() == 'Face_ControlBoard_CtrlRig':
            face_rig = proxy.control_rig
            print("Good to go!")
            break

    if face_rig is None:
        raise RuntimeError("Face_ControlBoard_CtrlRig not found into Level Sequence")

    # extract frame numbers from the first column (frames: '')
    time_code_key = list(csv_rows[0].keys())[0]
    frame_numbers = [row[time_code_key] for row in csv_rows]

    rig_instances = crp.create_rig_class_instances()
    batch = build_batch_by_column(csv_rows, rig_instances)

    apply_batch_to_unreal(batch, rig_instances, level_sequence, face_rig, frame_numbers)

    level_sequence.set_playback_start(0)
    level_sequence.set_playback_end(frame_numbers[-1].value)
    print("Keyframes inserted successfully!")


# processes all CSV rows and returns a columnar dict: rig_name: [val_frame0, val_frame1, ...]   # float o Vector2D
def build_batch_by_column(csv_rows, rig_instances):
    # initializes the empty list for each rig
    batch = {rig_name: [] for rig_name in rig_instances}
    already_seen_vec2 = set()  # to track which VEC2s have already been initialized

    for frame_row in csv_rows:
        # for each frame, we keep the values calculated in this frame
        frame_values = {rig_name: None for rig_name in rig_instances}
        computed_vec2 = set()

        for blendshape in frame_row:
            rigs_for_blend = A2F_TO_METAHUMAN.get(blendshape, [])

            for rig_name in rigs_for_blend:
                rig = rig_instances[rig_name]

                if rig.type == crp.crm.crc.RigType.VEC2:
                    # VEC2: Calculate only once per frame
                    if rig_name not in computed_vec2:
                        result = rig.calculate(frame_row)
                        frame_values[rig_name] = unreal.Vector2D(result[0], result[1])
                        computed_vec2.add(rig_name)

                else:
                    # FLOAT: accumulate (multiple blendshapes can contribute to the same rig)
                    result = rig.calculate(frame_row, source_blendshape=blendshape)
                    prev = frame_values[rig_name] or 0.0
                    frame_values[rig_name] = prev + result

        # append the values of this frame to the columns
        for rig_name in rig_instances:
            val = frame_values[rig_name]
            if val is None:
                # rig not touched in this frame will be neutral value
                rig = rig_instances[rig_name]
                val = unreal.Vector2D(0.0, 0.0) if rig.type == crp.crm.crc.RigType.VEC2 else 0.0
            batch[rig_name].append(val)

    return batch


def apply_batch_to_unreal(batch, rig_instances, level_sequence, face_rig, frame_numbers):
    # frame_numbers: list of unreal.FrameNumber, one for each CSV frame
    for rig_name, rig in rig_instances.items():
        values = batch[rig_name]

        if rig.type == crp.crm.crc.RigType.FLOAT:
            unreal.ControlRigSequencerLibrary.set_local_control_rig_floats(
                level_sequence,
                face_rig,
                unreal.Name(rig_name),
                frame_numbers,
                values
            )
        elif rig.type == crp.crm.crc.RigType.VEC2:
            unreal.ControlRigSequencerLibrary.set_local_control_rig_vector2_ds(
                level_sequence,
                face_rig,
                unreal.Name(rig_name),
                frame_numbers,
                values
            )





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
    #rows = read_csv_with_conversion("animation_frames.csv")
    #columns = transpose_rows_to_columns(rows)
    #insert_keyframes(ls,columns)
    #bake_to_animation_sequence(ls,"ColumnsTest2")

    #import_audio_as_asset("1001_DFA_HAP_XX.wav")

    rows = read_csv_with_conversion("animation_frames.csv")

    insert_keyframes_by_row(ls, rows)
    #bake_to_animation_sequence(ls,"ColumnsTestNuovo")




    end = time.time()
    print("Time elapsed: " + str(end-start) + " seconds")