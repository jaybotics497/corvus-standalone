#!/data/data/com.termux/files/usr/bin/python3
from pathlib import Path
import json, os, re, subprocess, sys
HOME=Path.home(); DEV=HOME/'corvus-dev'; STAGE=DEV/'staging/android/corvus'; INFER=HOME/'corvus/bin/infer'
OUT=DEV/'changes/android-operations.json'; RAW=DEV/'changes/android-operations-raw.txt'; ERR=DEV/'changes/android-operations-stderr.txt'
ALLOWED=('AndroidManifest.xml','assets/index.html','assets/style.css','res/values/strings.xml','res/values/styles.xml','src/com/corvus/app/CorvusBridge.java','src/com/corvus/app/CorvusEngineService.java','src/com/corvus/app/MainActivity.java')
OPS={'replace_exact','insert_before','insert_after'}
if len(sys.argv)<2: print('ANDROID OP GENERATOR V2: BLOCKED - objective required'); raise SystemExit(260)
objective=' '.join(sys.argv[1:]).strip(); OUT.unlink(missing_ok=True); RAW.unlink(missing_ok=True); ERR.unlink(missing_ok=True)
# Select the smallest useful context. Explicit filenames win. Otherwise rank and keep at most two files.
low=objective.lower(); explicit=[rel for rel in ALLOWED if rel.lower() in low or Path(rel).name.lower() in low]
if explicit:
    selected=list(dict.fromkeys(explicit))[:2]
else:
    tokens={x.lower() for x in re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}',objective)}
    scored=[]
    for rel in ALLOWED:
        p=STAGE/rel
        if not p.is_file(): continue
        sample=p.read_text(errors='replace')[:8000].lower()
        score=sum(1 for t in tokens if t in rel.lower() or t in sample)
        scored.append((score,rel))
    scored.sort(key=lambda x:(-x[0],x[1])); selected=[rel for score,rel in scored if score>0][:2]
    if not selected: selected=['AndroidManifest.xml']
blocks=[]
for rel in selected:
    p=STAGE/rel
    if not p.is_file(): print('ANDROID OP GENERATOR V2: BLOCKED - missing:',rel); raise SystemExit(261)
    text=p.read_text(errors='replace')
    # 1.5B phone model: keep source context deliberately small.
    if len(text)>9000:
        text=text[:9000]
    blocks.append(f'<CURRENT_FILE path="{rel}">\n{text}\n</CURRENT_FILE>')
prompt=f'''You are CORVUS. Plan one bounded Android edit.\nOBJECTIVE:\n{objective}\n\nReturn JSON only, no markdown or explanation. Maximum 4 operations. Use only AUTHORIZED PATHS. Supported operations: replace_exact, insert_before, insert_after. Each expected string must be copied exactly from CURRENT_FILE and occur once. Keep changes minimal. Do not change package identity or signing.\nJSON schema: {{"objective":"...","operations":[{{"operation":"replace_exact","path":"...","expected":"...","value":"..."}}],"report":{{"summary":"..."}}}}\nAUTHORIZED PATHS:\n'''+ '\n'.join('- '+x for x in selected)+'\nCURRENT SOURCE:\n'+'\n\n'.join(blocks)
env=dict(os.environ); env['CORVUS_MAX_TOKENS']='512'
r=subprocess.run([str(INFER),prompt],capture_output=True,text=True,env=env)
RAW.parent.mkdir(parents=True,exist_ok=True); RAW.write_text(r.stdout or ''); ERR.write_text(r.stderr or '')
if r.returncode:
    print('ANDROID OP GENERATOR V2: FAILED - inference exit',r.returncode); print('STDERR:',ERR); raise SystemExit(262)
text=(r.stdout or '').strip()
if not text:
    print('ANDROID OP GENERATOR V2: BLOCKED - empty inference output'); print('STDERR:',ERR); raise SystemExit(263)
if text.startswith('```json'): text=text[7:]
elif text.startswith('```'): text=text[3:]
if text.endswith('```'): text=text[:-3]
try: data=json.loads(text.strip())
except Exception as e:
    print('ANDROID OP GENERATOR V2: BLOCKED - invalid JSON:',e); print('RAW:',RAW); print('STDERR:',ERR); raise SystemExit(264)
ops=data.get('operations') if isinstance(data,dict) else None
if not isinstance(ops,list) or not ops or len(ops)>4: print('ANDROID OP GENERATOR V2: BLOCKED - invalid operation count'); raise SystemExit(265)
for i,op in enumerate(ops,1):
    if not isinstance(op,dict) or op.get('operation') not in OPS or op.get('path') not in selected: print('ANDROID OP GENERATOR V2: BLOCKED - malformed operation',i); raise SystemExit(266)
    expected=op.get('expected'); value=op.get('value')
    if not isinstance(expected,str) or not expected or not isinstance(value,str): print('ANDROID OP GENERATOR V2: BLOCKED - invalid fields',i); raise SystemExit(267)
    if (STAGE/op['path']).read_text(errors='replace').count(expected)!=1: print('ANDROID OP GENERATOR V2: BLOCKED - expected match count',i); raise SystemExit(268)
OUT.write_text(json.dumps(data,indent=2)+'\n')
print('ANDROID OP GENERATOR V2: PASS'); print('CONTEXT:',','.join(selected)); print('PROMPT_CHARS:',len(prompt)); print('OPERATIONS:',len(ops)); print('OUTPUT:',OUT)
