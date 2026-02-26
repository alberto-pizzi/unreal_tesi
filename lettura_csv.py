#import unreal
import csv

# ========== CONFIGURAZIONE ==========
csv_path = r"C:/Users/alber/Desktop/animation_frames.csv"
skeletal_mesh_path = "/Game/MetaHumans/Bryan/Face/Bryan_FaceMesh.Bryan_FaceMesh"
output_anim_path = "/Game/MetaHumans/Animations"
output_anim_name = "CSV_Anim_MH"
fps = 30


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

first_row = rows[2]

print(first_row)