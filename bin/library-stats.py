#!/usr/bin/env python3
import sqlite3
from pathlib import Path
db=Path.home()/"corvus/data/index/corvus.db"
con=sqlite3.connect(db)
print("=== CORVUS LIBRARY ===")
print("Sources:",con.execute("SELECT COUNT(*) FROM sources").fetchone()[0])
print("Chunks:",con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
con.close()
