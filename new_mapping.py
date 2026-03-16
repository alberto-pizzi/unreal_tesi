import unreal
import csv

# map
A2F_TO_METAHUMAN = {

# EYES

"EyeBlinkLeft": ["CTRL_L_eye_blink"],
"EyeBlinkRight": ["CTRL_R_eye_blink"],

"EyeLookUpLeft": ["CTRL_L_eye"],
"EyeLookDownLeft": ["CTRL_L_eye"],
"EyeLookInLeft": ["CTRL_L_eye"],
"EyeLookOutLeft": ["CTRL_L_eye"],

"EyeLookUpRight": ["CTRL_R_eye"],
"EyeLookDownRight": ["CTRL_R_eye"],
"EyeLookInRight": ["CTRL_R_eye"],
"EyeLookOutRight": ["CTRL_R_eye"],

"EyeSquintLeft": [
    "CTRL_L_eye_squintInner",
    "CTRL_L_eye_cheekRaise"
],

"EyeSquintRight": [
    "CTRL_R_eye_squintInner",
    "CTRL_R_eye_cheekRaise"
],

"EyeWideLeft": ["CTRL_L_eye_eyelidU"],
"EyeWideRight": ["CTRL_R_eye_eyelidU"],

# JAW

"JawOpen": ["CTRL_C_jaw"],
"JawForward": ["CTRL_C_jaw_fwdBack"],
"JawLeft": ["CTRL_C_jaw"],
"JawRight": ["CTRL_C_jaw"],

# MOUTH GENERAL

"MouthClose": [
    "CTRL_L_mouth_lipsTogetherU",
    "CTRL_L_mouth_lipsTogetherD",
    "CTRL_R_mouth_lipsTogetherU",
    "CTRL_R_mouth_lipsTogetherD"
],

"MouthFunnel": [
    "CTRL_L_mouth_funnelU",
    "CTRL_R_mouth_funnelU",
    "CTRL_L_mouth_funnelD",
    "CTRL_R_mouth_funnelD"
],

"MouthPucker": [
    "CTRL_L_mouth_purseU",
    "CTRL_R_mouth_purseU",
    "CTRL_L_mouth_purseD",
    "CTRL_R_mouth_purseD"
],

"MouthLeft": ["CTRL_L_mouth_corner"],
"MouthRight": ["CTRL_R_mouth_corner"],

# SMILE / FROWN

"MouthSmileLeft": ["CTRL_L_mouth_cornerPull"],
"MouthSmileRight": ["CTRL_R_mouth_cornerPull"],

"MouthFrownLeft": ["CTRL_L_mouth_cornerDepress"],
"MouthFrownRight": ["CTRL_R_mouth_cornerDepress"],

# DIMPLER / STRETCH

"MouthDimpleLeft": ["CTRL_L_mouth_dimple"],
"MouthDimpleRight": ["CTRL_R_mouth_dimple"],

"MouthStretchLeft": ["CTRL_L_mouth_stretch"],
"MouthStretchRight": ["CTRL_R_mouth_stretch"],

# LIPS

"MouthRollLower": [
    "CTRL_L_mouth_lipsRollD",
    "CTRL_R_mouth_lipsRollD"
],

"MouthRollUpper": [
    "CTRL_L_mouth_lipsRollU",
    "CTRL_R_mouth_lipsRollU"
],

"MouthShrugLower": [
    "CTRL_L_mouth_lowerLipDepress",
    "CTRL_R_mouth_lowerLipDepress"
],

"MouthShrugUpper": [
    "CTRL_L_mouth_upperLipRaise",
    "CTRL_R_mouth_upperLipRaise"
],

"MouthPressLeft": ["CTRL_L_mouth_pressD", "CTRL_L_mouth_pressU"],
"MouthPressRight": ["CTRL_R_mouth_pressD", "CTRL_R_mouth_pressU"],

"MouthLowerDownLeft": ["CTRL_L_mouth_lowerLipDepress"],
"MouthLowerDownRight": ["CTRL_R_mouth_lowerLipDepress"],

"MouthUpperUpLeft": ["CTRL_L_mouth_upperLipRaise"],
"MouthUpperUpRight": ["CTRL_R_mouth_upperLipRaise"],

# BROWS

"BrowDownLeft": ["CTRL_L_brow_down"],
"BrowDownRight": ["CTRL_R_brow_down"],

"BrowInnerUp": [
    "CTRL_L_brow_raiseIn",
    "CTRL_R_brow_raiseIn"
],

"BrowOuterUpLeft": ["CTRL_L_brow_raiseOut"],
"BrowOuterUpRight": ["CTRL_R_brow_raiseOut"],

# CHEEKS

"CheekPuff": [
    "CTRL_L_mouth_suckBlow",
    "CTRL_R_mouth_suckBlow"
],

"CheekSquintLeft": ["CTRL_L_eye_cheekRaise"],
"CheekSquintRight": ["CTRL_R_eye_cheekRaise"],

# NOSE

"NoseSneerLeft": [
    "CTRL_L_nose",
    "CTRL_L_nose_wrinkleUpper"
],

"NoseSneerRight": [
    "CTRL_R_nose",
    "CTRL_R_nose_wrinkleUpper"
],

# TONGUE

"TongueOut": ["CTRL_C_tongue_inOut"],
"TongueIn": ["CTRL_C_tongue_inOut"],

"TongueUp": ["CTRL_C_tongue_move"],
"TongueDown": ["CTRL_C_tongue_move"],

"TongueLeft": ["CTRL_C_tongue_move"],
"TongueRight": ["CTRL_C_tongue_move"],

"TongueRollUp": ["CTRL_C_tongue_roll"],
"TongueRollDown": ["CTRL_C_tongue_roll"],

"TongueWide": ["CTRL_C_tongue_wideNarrow"],
"TongueNarrow": ["CTRL_C_tongue_wideNarrow"],

"TongueStretch": ["CTRL_C_tongue_press"],

# HEAD

"HeadYaw": ["mha_head_ik_ctrl"],
"HeadPitch": ["mha_head_ik_ctrl"],
"HeadRoll": ["mha_head_ik_ctrl"],

}

# config

CSV_PATH = r"C:/Users/alber/Desktop/"
CSV_NAME = "animation_frames.csv"
ANIMATION_PATH = "/Game/MetaHumans/Animations/CustomAnimations"
ANIMATION_NAME = "ProvaAnimazione"
FRAME_RATE = 30.0

SKELETON_PATH = "/Game/MetaHumans/Common/Face/"
SKELETON_NAME = "Face_Archetype_Skeleton.Face_Archetype_Skeleton"
#LS_PATH = "/Game/LevelSequences/"
LS_PATH = "/Game/"

#prefixes
mh_prefix = "CTRL_expressions_"
csv_prefix = "blendShapes."
time_code_tag = "timeCode"

def load_level_sequence(seq_filename:str):
    full_path = LS_PATH + seq_filename + "." + seq_filename
    level_sequence = unreal.load_asset(full_path)
    return level_sequence

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

# insert keyframes
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

    print("Keyframe calculation complete!")



if __name__ == '__main__':
    ls = load_level_sequence("NewLevelSequence")
    rows, arkit_csv_names = read_csv(CSV_NAME)
    insert_keyframes(ls,rows)