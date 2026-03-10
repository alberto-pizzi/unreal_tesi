import unreal
import csv


CSV_PATH = r"C:/Users/alber/Desktop/animation_frames.csv"

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    #reader.fieldnames = [n.strip() for n in reader.fieldnames]
    #rows = [row for row in reader if row and row.get("timeCode", "").strip() != ""]
    rows = list(reader)

if not rows:
    raise RuntimeError("CSV vuoto o malformato")

print(rows[-1])
print("Valore: ",rows[-1]["timeCode"])
print("lunghezza righe", len(rows))

