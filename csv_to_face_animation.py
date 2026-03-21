# FIXME add it into main file
import sys
import os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)


import unreal
import csv
import time
from a2f_rig_maps import A2F_TO_METAHUMAN
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
        #arkit_csv_names = cleaned_keys.copy()
        rows = list(reader)

    #remove first element "timeCode"
    #if arkit_csv_names and arkit_csv_names[0] == time_code_tag:
    #    arkit_csv_names.pop(0)

    if not rows:
        raise RuntimeError("CSV is empty or malformed")

    print("CSV read successfully")
    return rows

def read_csv_with_conversion(filename):
    """
    Reads a CSV and converts values as follows:
    - First column: int
    - Other columns: float
    - Headers: strings
    Returns a list of dictionaries.
    """
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


def process_frame(frame_row, rig_instances_dict):
    processed_frame = {}
    already_computed = set()  # evita ricalcoli multipli per rig VEC2

    for blendshape, value in frame_row.items():
        rigs_for_blend = A2F_TO_METAHUMAN.get(blendshape, [])

        for rig_name in rigs_for_blend:
            rig = rig_instances_dict[rig_name]

            if rig.type == crp.crm.crc.RigType.VEC2:
                # VEC2: calcola una sola volta (legge tutto il frame_row internamente)
                if rig_name not in already_computed:
                    calc_values = rig.calculate(frame_row)
                    processed_frame[rig_name] = unreal.Vector2D(calc_values[0], calc_values[1])
                    already_computed.add(rig_name)
            else:
                # FLOAT default: usa il blendshape corrente come chiave
                calc_values = rig.calculate(frame_row, blendshape)
                # accumula (somma) se più blendshape mappano sullo stesso rig
                prev = processed_frame.get(rig_name, 0.0)
                processed_frame[rig_name] = prev + calc_values

    return processed_frame


# IMPORTANT: insert keyframes into actor face control rigs
def insert_keyframes_by_row(level_sequence, csv_rows):
    rig_proxies = unreal.ControlRigSequencerLibrary.get_control_rigs(level_sequence)

    face_rig = None
    for proxy in rig_proxies:
        if proxy.control_rig.get_name() == 'Face_ControlBoard_CtrlRig':
            face_rig = proxy.control_rig
            print("Good to go!")
            break

    #frame_array = unreal.Array(unreal.FrameNumber)
    #[frame_array.append(unreal.FrameNumber(int(f))) for f in csv_columns['']]

    #blendshapes = list(csv_rows.keys())[2:]

    rig_instances = crp.create_rig_class_instances()
    #print("lunghezza: ",len(rig_instances))
    processed_frames = [process_frame(f, rig_instances) for f in rows]
    batch_data = build_batch(processed_frames, rig_instances)
    print("lunghezza: ", len(processed_frames))
    print(processed_frames[:2])
    print(processed_frames)
    #apply_batch_to_unreal(batch_data, rig_instances, ls, face_rig)

def build_batch(processed_frames, rig_instances):

    batch_data = {}

    for frame_row in processed_frames:
        for rig_name, rig in rig_instances.items():
            value = frame_row.get(rig_name)

            if value is not None:
                batch_data[rig_name] = value

    return batch_data


def apply_batch_to_unreal(batch_data, rig_instances, level_sequence, face_rig):
    """
    Applica tutti i valori dei rig in batch a Unreal
    """
    for rig_name, rig in rig_instances.items():
        values = batch_data[rig_name]
        frame_indices = list(range(len(values)))

        if rig.type == crp.crm.crc.RigType.FLOAT:
            unreal.ControlRigSequencerLibrary.set_local_control_rig_floats(
                level_sequence,
                face_rig,
                unreal.Name(rig_name),
                frame_indices,
                values
            )
        elif rig.type == crp.crm.crc.RigType.VEC2:
            unreal.ControlRigSequencerLibrary.set_local_control_rig_vector2_ds(
                level_sequence,
                face_rig,
                unreal.Name(rig_name),
                frame_indices,
                values
            )


# IMPORTANT: insert keyframes into actor face control rigs
def insert_keyframes(level_sequence, csv_columns):
    rig_proxies = unreal.ControlRigSequencerLibrary.get_control_rigs(level_sequence)

    face_rig = None
    for proxy in rig_proxies:
        if proxy.control_rig.get_name() == 'Face_ControlBoard_CtrlRig':
            face_rig = proxy.control_rig
            print("Good to go!")
            break

    #frame_array = unreal.Array(unreal.FrameNumber)
    #[frame_array.append(unreal.FrameNumber(int(f))) for f in csv_columns['']]

    #blendshapes = list(csv_columns.keys())[2:]

    rig_instances = crp.create_rig_class_instances()
    processed_frames = [process_frame(f, rig_instances) for f in rows]
    batch_data = build_batch(processed_frames, rig_instances)
    apply_batch_to_unreal(batch_data, rig_instances, ls, face_rig)



    '''
    for blendshape in blendshapes:
        if blendshape not in A2F_TO_METAHUMAN:
            continue

        print("Calculating blendshape:", blendshape)

        #values_array = unreal.Array(float)
        #values_array.append(float(val))
        #values = [float(x) for x in csv_columns[blendshape]]

        # Applica i keyframes a tutti i controlli mappati
        for face_control in A2F_TO_METAHUMAN[blendshape]:
            unreal.ControlRigSequencerLibrary.set_local_control_rig_floats(
                level_sequence,
                face_rig,
                unreal.Name(face_control),
                csv_columns[''],
                csv_columns[blendshape]
            )

    
            for row in csv_columns:
            print("Calculating frame: ", row[''])
            for blendshape in A2F_TO_METAHUMAN:
                csv_blendshape_key = CSV_PREFIX + blendshape
                if csv_blendshape_key in row:
                    for face_control_rig in A2F_TO_METAHUMAN[blendshape]:
                        #print("INIZIO - face_control_rig: " + face_control_rig + " blendshape: " + blendshape)
                        unreal.ControlRigSequencerLibrary.set_local_control_rig_float(level_sequence, face_rig, unreal.Name(face_control_rig),
                                                                          unreal.FrameNumber(int(row[''])), float(row[csv_blendshape_key]))
                        #print("FINE - face_control_rig: " + face_control_rig + " blendshape: " + blendshape)
                          
    '''





    # FIXME is correct pos?
    level_sequence.set_playback_start(0)
    level_sequence.set_playback_end(csv_columns[''][-1].value)
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