import unreal
import csv
import os

from test_script import csv_path

#mapping
arkit_to_metahuman = {

# Eyes
"EyeBlinkLeft": "eye_blink_L",
"EyeBlinkRight": "eye_blink_R",
"EyeLookDownLeft": "eye_lookDown_L",
"EyeLookDownRight": "eye_lookDown_R",
"EyeLookInLeft": "eye_lookIn_L",
"EyeLookInRight": "eye_lookIn_R",
"EyeLookOutLeft": "eye_lookOut_L",
"EyeLookOutRight": "eye_lookOut_R",
"EyeLookUpLeft": "eye_lookUp_L",
"EyeLookUpRight": "eye_lookUp_R",
"EyeSquintLeft": "eye_squint_L",
"EyeSquintRight": "eye_squint_R",
"EyeWideLeft": "eye_widen_L",
"EyeWideRight": "eye_widen_R",

# Brows
"BrowDownLeft": "brow_down_L",
"BrowDownRight": "brow_down_R",
"BrowInnerUp": "brow_raiseInner",
"BrowOuterUpLeft": "brow_raiseOuter_L",
"BrowOuterUpRight": "brow_raiseOuter_R",

# Cheeks
"CheekPuff": "cheek_puff",
"CheekSquintLeft": "cheek_squint_L",
"CheekSquintRight": "cheek_squint_R",

# Nose
"NoseSneerLeft": "nose_sneer_L",
"NoseSneerRight": "nose_sneer_R",

# Jaw
"JawOpen": "jaw_open",
"JawForward": "jaw_forward",
"JawLeft": "jaw_left",
"JawRight": "jaw_right",

# Mouth
"MouthClose": "mouth_close",
"MouthFunnel": "mouth_funnel",
"MouthPucker": "mouth_pucker",
"MouthLeft": "mouth_left",
"MouthRight": "mouth_right",

"MouthSmileLeft": "mouth_cornerPull_L",
"MouthSmileRight": "mouth_cornerPull_R",

"MouthFrownLeft": "mouth_cornerDepress_L",
"MouthFrownRight": "mouth_cornerDepress_R",

"MouthDimpleLeft": "mouth_dimple_L",
"MouthDimpleRight": "mouth_dimple_R",

"MouthStretchLeft": "mouth_stretch_L",
"MouthStretchRight": "mouth_stretch_R",

"MouthRollLower": "mouth_rollLower",
"MouthRollUpper": "mouth_rollUpper",

"MouthShrugLower": "mouth_shrugLower",
"MouthShrugUpper": "mouth_shrugUpper",

"MouthPressLeft": "mouth_press_L",
"MouthPressRight": "mouth_press_R",

"MouthLowerDownLeft": "mouth_lowerDown_L",
"MouthLowerDownRight": "mouth_lowerDown_R",

"MouthUpperUpLeft": "mouth_upperUp_L",
"MouthUpperUpRight": "mouth_upperUp_R",

# Tongue
"TongueOut": "tongue_out"
}


# =========================
# CONFIG
# =========================
CSV_PATH = r"C:/Users/alber/Desktop/animation_frames.csv"
ASSET_PATH = "/Game/MetaHumans/Animations"
ASSET_NAME = "ProvaAnimazione"
FRAME_RATE = 30.0

mh_prefix = "head_lod0_mesh__"
csv_prefix = "blendShapes."
time_code_tag = "timeCode"

SKELETON_PATH = "/Game/MetaHumans/Common/Face/Face_Archetype_Skeleton.Face_Archetype_Skeleton"



# =========================
# CARICA SKELETON
# =========================
skeleton = unreal.load_asset(SKELETON_PATH)
if not skeleton:
    raise RuntimeError(f"Skeleton non trovato: {SKELETON_PATH}")

# =========================
# CREA ANIM SEQUENCE
# =========================
factory = unreal.AnimSequenceFactory()
factory.target_skeleton = skeleton
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
anim_seq = asset_tools.create_asset(ASSET_NAME, ASSET_PATH, unreal.AnimSequence, factory)

# =========================
# LEGGI CSV
# =========================

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    #tolgo il prefisso a tutti i nomi dei blendshape
    cleaned_keys  = [key.strip().removeprefix(csv_prefix)
                         for key in reader.fieldnames if key.strip() != '']
    arkit_csv_names = cleaned_keys.copy()
    rows = list(reader)


#rimuovo primo elemento "timeCode"
if arkit_csv_names and arkit_csv_names[0] == time_code_tag:
    arkit_csv_names.pop(0)

if not rows:
    raise RuntimeError("CSV vuoto o malformato")

print("CSV letto correttamente")

#creo list morph mappati (da arkit a metahuman)
morphs_mh = []
for arkit_name in arkit_csv_names:
    if arkit_name in arkit_to_metahuman:
        morph_mh = mh_prefix + arkit_to_metahuman[arkit_name]
        morphs_mh.append(morph_mh)

print("Mappatura completa")


#creo curve per ogni blendshape (i morphs mappati sono 52)
for name_mh in morphs_mh:
    unreal.AnimationLibrary.add_curve(anim_seq, name_mh,unreal.RawCurveTrackTypes.RCT_FLOAT)

print("Tutte le curve aggiunte")
#inserire keyframe

print(list(zip(morphs_mh, arkit_csv_names)))


for name_mh, arkit_name in zip(morphs_mh, arkit_csv_names):
    times = unreal.Array(float)
    values = unreal.Array(float)

    for row in rows:
        times.append(float(row[time_code_tag]))
        values.append(float(row[csv_prefix + arkit_name]))

    unreal.AnimationLibrary.add_float_curve_keys(anim_seq, name_mh,times,values)


#salva
unreal.EditorAssetLibrary.save_loaded_asset(anim_seq)
print("AnimSequence salvata con successo:", anim_seq.get_path_name())

