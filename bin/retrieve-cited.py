from pathlib import Path
import re
import sys
import csv

HOME = Path.home()
CHUNKS = HOME / "corvus/data/index/chunks"
INDEX = HOME / "corvus/data/index/citations.tsv"

query = " ".join(sys.argv[1:]).strip().lower()

if not query:
    print("Usage: python ~/corvus/bin/retrieve-cited.py <search terms>")
    raise SystemExit(1)

terms = re.findall(r"\w+", query)
citations = {}

if INDEX.exists():
    with INDEX.open(errors="ignore") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            path = Path(row["PATH"])
            citations[path.name] = row

results = []

for f in CHUNKS.glob("*.txt"):
    text = f.read_text(errors="ignore").lower()
    words = max(len(text.split()), 1)
    hits = sum(text.count(term) for term in terms)

    if hits:
        score = (hits / words) * 1000
        results.append((score, f))

results.sort(key=lambda x: x[0], reverse=True)

print("=== CORVUS CITED RETRIEVAL ===")
print("Query:", query)
print()

for score, f in results[:5]:
    cite = citations.get(f.name)

    print(f"SCORE: {score:.2f}")
    print(f"CHUNK: {f.name}")

    if cite:
        print(f"SOURCE: {cite['SOURCE']}")
        print(f"CHAPTER: {cite['CHAPTER']}")
        print(f"PATH: {cite['PATH']}")
    else:
        print("SOURCE: uncatalogued test data")

    print()
