"""
SCRIPT COMPLETO: CSV_Anim_MH → MP4 (Camera + MetaHuman GIA' NEL LIVELLO)
Esegui da UE5: Ctrl+Shift+P → Python Script
"""

import unreal
import csv
import os

# ===============================================
# CONFIG (Adatta SOLO QUESTI)
# ===============================================
ANIM_SEQUENCE_PATH = "/Game/MetaHumans/Animations/CSV_Anim_MH.CSV_Anim_MH"  # Il tuo
CSV_PATH = r"C:/Users/alber/Desktop/animation_frames.csv"  # Per FPS nativi
AUDIO_PATH = r"C:/Users/alber/Desktop/Esempio prova script Audio2Face/out.wav"
OUTPUT_DIR = r"C:/Users/alber/Desktop/videos/"

# ===============================================
# 1. CARICA ANIMSEQUENCE + CALCOLA FPS NATIVI
# ===============================================
print("🎬 Caricamento AnimSequence + analisi FPS...")

anim_sequence = unreal.load_asset(ANIM_SEQUENCE_PATH)

# Leggi CSV per FPS nativi (380 frame / 12s)
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total_frames = len(rows)
last_time = float(rows[-1]['timeCode'])
NATIVE_FPS = total_frames / last_time
end_frame = unreal.FrameNumber(total_frames)

print(f"✅ FPS nativi CSV: {NATIVE_FPS:.1f} | Frame: {total_frames} | Durata: {last_time:.1f}s")




# ===============================================
# 2. CREA SEQUENCER CON LIVELLO ATTUALE
# ===============================================
# STEP 3 + 4: Sequencer SEMPLICE (ZERO ERRORI)
print("🎬 STEP 3-4: Sequencer + Actors...")

# Crea Sequencer
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.LevelSequenceFactoryNew()
seq = asset_tools.create_asset(
    asset_name="Facial_Video_Scene",
    package_path="/Game/Sequences",
    asset_class=unreal.LevelSequence.static_class(),
    factory=factory
)
seq_path = "/Game/Sequences/Facial_Video_Scene"

# ✅ METODO SEMPLICE: Aggiungi solo MetaHuman e Camera
print("🏗️  Import MetaHuman + Camera...")

# 1. MetaHuman Bryan (path standard)
seq.add_possessable("/Game/MetaHumans/Bryan/Bryan")
print("✅ Bryan aggiunto!")

# 2. Camera attiva nel viewport
actors = unreal.EditorLevelLibrary.get_all_level_actors()
for actor in actors:
    name = actor.get_name()
    if "Camera" in name or "Cine" in name:
        seq.add_possessable(actor.get_path_name())
        print(f"✅ Camera: {name}")
        break
else:
    # Camera di default se non trovata
    seq.add_possessable("/Engine/EngineSky/BasicSky/BasicSky")
    print("✅ Camera default")

print("✅ Setup Sequencer completato!")


