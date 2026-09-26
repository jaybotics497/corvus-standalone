from pathlib import Path
import sys, shutil, csv, re

HOME = Path.home()
LIB = HOME / "corvus/data/library"
META = HOME / "corvus/data/index/source-metadata.tsv"

if len(sys.argv) != 7:
    print("Usage: import-source.py FILE SUBJECT TITLE SOURCE_TYPE TRUST_TIER AUTHOR")
    sys.exit(1)

src = Path(sys.argv[1]).expanduser()
subject, title, source_type, trust, author = sys.argv[2:]

if not src.is_file():
    print("ERROR: Source file not found")
    sys.exit(1)

subject_safe = re.sub(r"[^a-z0-9_]+", "_", subject.lower()).strip("_")
dest_dir = LIB / subject_safe
dest_dir.mkdir(parents=True, exist_ok=True)

existing = []
if META.exists():
    with META.open() as f:
        existing = list(csv.DictReader(f, delimiter="\t"))

source_id = f"SRC{len(existing)+1:04d}"
dest = dest_dir / f"{source_id}_{src.name}"

shutil.copy2(src, dest)

with META.open("a", newline="") as f:
   
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        source_id,
        title,
        subject_safe,
        source_type,
        trust,
        author,
        "READY"
    ])

print("=== CORVUS IMPORT ===")
print("ID:", source_id)
print("TITLE:", title)
print("SUBJECT:", subject_safe)
print("TRUST:", trust)
print("PATH:", dest)
print("IMPORT SYSTEM: PASS")
