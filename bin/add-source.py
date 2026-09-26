#!/usr/bin/env python3
from pathlib import Path
import sqlite3,sys

db=Path.home()/"corvus/data/index/corvus.db"
if len(sys.argv)<4:
 print("USAGE: add-source.py SUBJECT FILE TITLE [AUTHOR] [TYPE]")
 sys.exit(1)
subject=sys.argv[1]
filename=sys.argv[2]
title=sys.argv[3]
author=sys.argv[4] if len(sys.argv)>4 else ""
stype=sys.argv[5] if len(sys.argv)>5 else ""

con=sqlite3.connect(db)
con.execute("INSERT INTO sources(subject,filename,title,author,source_type) VALUES(?,?,?,?,?) ON CONFLICT(subject,filename) DO UPDATE SET title=excluded.title,author=excluded.author,source_type=excluded.source_type",(subject,filename,title,author,stype))
con.commit()
con.close()
print(f"SOURCE ADDED: {title}")
print("SOURCE: PASS")
