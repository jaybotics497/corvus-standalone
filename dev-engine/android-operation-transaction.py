#!/data/data/com.termux/files/usr/bin/python3
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile

HOME=Path.home(); DEV=HOME/'corvus-dev'; STAGE=DEV/'staging/android/corvus'; ENGINE=DEV/'android-edit-engine.py'
MAX_OPS=4

def emit(**x): print(json.dumps(x, sort_keys=True))
def tree_hash(root):
    h=hashlib.sha256()
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        h.update(str(p.relative_to(root)).encode()+b'\0'); h.update(p.read_bytes())
    return h.hexdigest()

def fail(msg, code, **extra): emit(status='FAIL', message=msg, **extra); raise SystemExit(code)
if len(sys.argv)!=2: fail('usage: android-operation-transaction.py OPERATIONS.json',80)
source=Path(sys.argv[1])
try: data=json.loads(source.read_text())
except Exception as e: fail(f'invalid JSON: {e}',81)
if not isinstance(data,dict): fail('root must be object',82)
ops=data.get('operations')
if not isinstance(ops,list) or not ops: fail('operations must be non-empty array',83)
if len(ops)>MAX_OPS: fail('too many operations',84,requested=len(ops))
if any(not isinstance(op,dict) for op in ops): fail('every operation must be object',85)
if not STAGE.is_dir(): fail('staging missing',86)
if not ENGINE.is_file(): fail('edit engine missing',87)
pre=tree_hash(STAGE); backup=Path(tempfile.mkdtemp(prefix='corvus-android-txn-',dir=str(DEV/'tmp')))
shutil.copytree(STAGE,backup/'stage')
applied=0
try:
    for idx,op in enumerate(ops):
        opfile=backup/f'op-{idx}.json'; opfile.write_text(json.dumps(op))
        r=subprocess.run([str(ENGINE),str(opfile)],text=True,capture_output=True)
        if r.returncode!=0:
            shutil.rmtree(STAGE); shutil.copytree(backup/'stage',STAGE)
            restored=tree_hash(STAGE)==pre
            fail('operation failed',88,requested=len(ops),applied=applied,failed_index=idx,engine_exit=r.returncode,rollback=restored,engine_stdout=r.stdout.strip(),engine_stderr=r.stderr.strip())
        applied+=1
    post=tree_hash(STAGE)
    if post==pre: fail('transaction produced no staging change',89,requested=len(ops),applied=applied)
    emit(status='PASS',requested=len(ops),applied=applied,failed_index=None,pre_sha256=pre,post_sha256=post)
finally:
    shutil.rmtree(backup,ignore_errors=True)
