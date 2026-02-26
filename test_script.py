import unreal
import csv

# ========== CONFIGURAZIONE ==========
csv_path = r"C:/Users/alber/Desktop/animation_frames.csv"
skeletal_mesh_path = "/Game/MetaHumans/Bryan/Face/Bryan_FaceMesh.Bryan_FaceMesh"
output_anim_path = "/Game/MetaHumans/Animations"
output_anim_name = "CSV_Anim_MH"
fps = 30

# ========== CARICA SKELETAL MESH ==========
skeletal_mesh = unreal.EditorAssetLibrary.load_asset(skeletal_mesh_path)
skeleton = skeletal_mesh.get_editor_property('skeleton')

# ========== CREA ANIMSEQUENCE ==========
factory = unreal.AnimSequenceFactory()
factory.target_skeleton = skeleton

anim_sequence = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    asset_name=output_anim_name,
    package_path=output_anim_path,
    asset_class=unreal.AnimSequence.static_class(),
    factory=factory
)

anim_sequence_path = output_anim_path + "/" + output_anim_name
unreal.EditorAssetLibrary.save_asset(anim_sequence_path)
anim_sequence = unreal.load_asset(anim_sequence_path)

print("✅ Asset AnimSequence creato:", anim_sequence_path)

# ========== LEGGI CSV ==========
with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

if not rows:
    print("❌ Errore: CSV vuoto!")
    exit()

all_columns = rows[0].keys()
blendshape_columns = [c for c in all_columns if c.startswith("blendShapes.")]

print(f"✅ Blendshapes trovati: {len(blendshape_columns)}")
print(f"✅ Frame totali: {len(rows)}")

# ========== CALCOLA DURATA ==========
# I timeCode sono già in secondi nel CSV Audio2Face
times = []
for row in rows:
    tc = row.get("timeCode", "0")
    try:
        time_sec = float(tc)
        times.append(time_sec)
    except ValueError:
        print(f"⚠️ Valore timeCode non valido: {tc}")
        times.append(0.0)

if not times:
    print("❌ Errore: nessun timeCode valido trovato!")
    exit()

duration = max(times)
num_frames = int(duration * fps) + 1

print(f"✅ Durata animazione: {duration:.2f} secondi ({num_frames} frames a {fps} FPS)")

# ========== IMPOSTA DURATA ANIMAZIONE ==========
# Questo è FONDAMENTALE: senza questa impostazione l'animazione sarà vuota!

# Imposta il FrameRate corretto
from unreal import FrameRate

frame_rate = FrameRate()
frame_rate.numerator = fps
frame_rate.denominator = 1

# Usa il metodo corretto per impostare la durata
anim_data_model = anim_sequence.get_data_model()
controller = anim_data_model.get_controller()

# Inizia la modifica
controller.open_bracket()

# Imposta frame rate e durata
controller.set_frame_rate(frame_rate)
controller.set_number_of_frames(num_frames)


# Chiudi la modifica
controller.close_bracket()

print("✅ Durata impostata correttamente")

# ========== AGGIUNGI CURVE E KEYFRAME ==========
curve_type = unreal.RawCurveTrackTypes.RCT_FLOAT

# Riapri il controller per aggiungere curve
anim_data_model = anim_sequence.get_data_model()
controller = anim_data_model.get_controller()

controller.open_bracket()

for i, blend_col in enumerate(blendshape_columns):
    # Rimuovi il prefisso "blendShapes." per ottenere il nome del morph target
    morph_name_str = blend_col.replace("blendShapes.", "")
    morph_name = unreal.Name(morph_name_str)

    # Aggiungi la curva usando il controller
    curve_id = unreal.AnimationCurveIdentifier(morph_name, unreal.ERawCurveTrackTypes.RCT_FLOAT)
    controller.add_curve(curve_id, unreal.AnimationCurveFlags())

    # Aggiungi i keyframe
    keyframes_added = 0
    for j, row in enumerate(rows):
        time_sec = times[j]

        try:
            value = float(row[blend_col])
            # Usa il controller per aggiungere keyframe
            controller.set_curve_key(curve_id, time_sec, value)
            keyframes_added += 1
        except (ValueError, KeyError) as e:
            print(f"⚠️ Errore al frame {j} per {morph_name_str}: {e}")

    if (i + 1) % 10 == 0:
        print(f"  Processate {i + 1}/{len(blendshape_columns)} curve...")

controller.close_bracket()

print(f"\n✅ COMPLETATO!")
print(f"   - {len(blendshape_columns)} curve morph target create")
print(f"   - {len(rows)} keyframe per curva")
print(f"   - Durata: {duration:.2f} secondi")

# ========== SALVA FINALE ==========
unreal.EditorAssetLibrary.save_asset(anim_sequence_path)
print(f"✅ Asset salvato: {anim_sequence_path}")