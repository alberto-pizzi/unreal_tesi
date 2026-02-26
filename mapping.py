import unreal
import csv
import os

# =========================
# CONFIG
# =========================
CSV_PATH = r"C:/Users/alber/Desktop/animation_frames.csv"
ASSET_PATH = "/Game/MetaHumans/Animations"
ASSET_NAME = "ProvaAnimazione"
FRAME_RATE = 30.0

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
    reader.fieldnames = [n.strip() for n in reader.fieldnames]
    rows = [row for row in reader if row and row.get("timeCode", "").strip() != ""]

if not rows:
    raise RuntimeError("CSV vuoto o malformato")

# nomi delle curve
curve_names = [c.replace("blendShapes.", "") for c in rows[0].keys() if c != "timeCode"]
print(curve_names)

"""
# =========================
# CREA CURVE E AGGIUNGI KEYFRAME
# =========================
for curve in curve_names:
    anim_seq.add_float_curve(unreal.Name(curve))
    for row in rows:
        time = float(row["timeCode"])
        value = float(row["blendShapes." + curve])
        unreal.AnimationLibrary.add_float_curve_key()
        anim_seq.add_float_curve_key(unreal.Name(curve), time, value)

# =========================
# SALVA L'ASSET
# =========================
anim_seq.modify(True)
unreal.EditorAssetLibrary.save_loaded_asset(anim_seq)

print("AnimSequence creata con successo:", anim_seq.get_path_name())

"""