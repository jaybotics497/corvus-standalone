#!/usr/bin/env python3
from http.server import HTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,subprocess

HOST="127.0.0.1"
PORT=8765
BASE=Path.home()/"corvus"
TOKEN=(BASE/"api/token").read_text().strip()

COMMANDS={
 "status":[str(BASE/"bin/corvus"),"status"],
 "library":[str(BASE/"bin/corvus"),"library"],
}
class Handler(BaseHTTPRequestHandler):
 def reply(self,code,data):
  body=json.dumps(data).encode()
  self.send_response(code)
  self.send_header("Content-Type","application/json")
  self.send_header("Content-Length",str(len(body)))
  self.end_headers()
  self.wfile.write(body)

 def do_GET(self):
  if self.headers.get("Authorization") != "Bearer "+TOKEN:
   self.reply(401,{"error":"unauthorized"})
   return
  name=self.path.strip("/")
  if name not in COMMANDS:
   self.reply(404,{"error":"unknown command"})
   return

  try:
   r=subprocess.run(COMMANDS[name],capture_output=True,text=True,timeout=30)
   self.reply(200,{"command":name,"code":r.returncode,"output":r.stdout})
  except Exception as e:
   self.reply(500,{"error":str(e)})

 def log_message(self,format,*args):
  pass

if __name__=="__main__":
 print(f"CORVUS API: http://{HOST}:{PORT}")
 HTTPServer((HOST,PORT),Handler).serve_forever()
