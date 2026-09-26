from pathlib import Path
import hashlib
import csv

H = Path.home()
LIB = H / "corvus/data/library"
OUT = H / "corvus/data/index/library.tsv"

OUT.parent.mkdir(parents=True, exist_ok=True)

rows = []

for f in sorted(LIB.rglob("*")):
    if not f.is_file():
        continue

    rel = f.relative_to(LIB)
    subject = rel.parts[0] if len(rel.parts) > 1 else "uncategorised"

    stat = f.stat()
    digest = hashlib.sha256(f.read_bytes()).hexdigest()[:16]

    rows.append({
        "ID": digest,
        "SUBJECT": subject,
        "TITLE": f.stem.replace("_", " "),
        "PATH": str(rel),
        "SIZE": stat.st_size,
        "STATUS": "READY"
    })

with OUT.open("w", newline="") as out:
    fields = ["ID","SUBJECT","TITLE","PATH","SIZE","STATUS"]
    writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

print("=== CORVUS LIBRARY INDEX ===")
print("Sources:", len(rows))
print("Index:", OUT)
print("STATUS: PASS")
