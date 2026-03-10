import unreal
import csv

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


mesh = unreal.load_asset("/Game/MetaHumans/Bryan/Face/Bryan_FaceMesh.Bryan_FaceMesh")

morph_targets = mesh.morph_targets

print("Numero morph targets Skeleton Mesh:", len(morph_targets))

mesh_names = [m.get_name() for m in morph_targets]

'''
#apro morph target csv
txt_path = "F:/Sincronizzazione iCloud/iCloudDrive/UNIFI/Tesi/morph target csv.txt"
with open(txt_path, 'r', encoding='utf-8') as f:
    arkit_csv_names = [riga.strip().removeprefix("blendShapes.") for riga in f]
'''


CSV_PATH = r"C:/Users/alber/Desktop/animation_frames.csv"

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    cleaned_keys  = [key.strip().removeprefix("blendShapes.")
                         for key in reader.fieldnames if key.strip() != '']
    arkit_csv_names = cleaned_keys.copy()
    rows = list(reader)

arkit_csv_names.pop(0)
print("lista chiavi:", arkit_csv_names)
print("numero chiavi:", len(arkit_csv_names))


morphs = []
for arkit_name in arkit_csv_names:
    if arkit_name in arkit_to_metahuman:
        morph = "head_lod0_mesh__" + arkit_to_metahuman[arkit_name]
        morphs.append(morph)


print("corrispondenze:",len(morphs))