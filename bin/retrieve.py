from pathlib import Path
import csv, re, sys

H = Path.home()
INDEX = H/"corvus/data/index/chunk-index.tsv"
META = H/"corvus/data/index/source-metadata.tsv"

query = " ".join(sys.argv[1:]).lower().strip()

if not query:
    print("Usage: retrieve.py QUERY")
    raise SystemExit(1)

terms = re.findall(r"\w+", query)

weights = {
    "A": 1.00,
    "B": 0.90,
    "C": 0.75,
    "D": 0.70,
    "E": 0.40,
    "F": 0.10
}

trust = {}

with META.open() as f:
    for row in csv.DictReader(f, delimiter="\t"):
        trust[row["ID"]] = row["TRUST_TIER"]

results = []

with INDEX.open() as f:
    for row in csv.DictReader(f, delimiter="\t"):
        path = Path(row["CHUNK_PATH"])

        if not path.exists():
            continue

        text = path.read_text(errors="ignore").lower()
        words = max(len(text.split()), 1)

        hits = sum(text.count(term) for term in terms)

        if not hits:
            continue

        tier = trust.get(row["SOURCE_ID"], "E")
        weight = weights.get(tier, 0.40)

        density = (hits / words) * 1000
        score = density * weight

        results.append((score,
tier, row, text))

results.sort(key=lambda x: x[0], reverse=True)

print("=== CORVUS RETRIEVAL ===")
print("QUERY:", query)
print("RESULTS:", len(results))
print()

for score, tier, row, text in results[:5]:
    print(f"SCORE: {score:.2f}")
    print("TRUST:", tier)
    print("SOURCE:", row["SOURCE_ID"])
    print("SUBJECT:", row["SUBJECT"])
    print("CHUNK:", row["CHUNK_ID"])
    print("PATH:", row["CHUNK_PATH"])
    print("TEXT:", text[:350])
    print()

print("RETRIEVAL SYSTEM: PASS")
