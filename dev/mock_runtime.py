#!/usr/bin/env python3
"""Read-only contract fixture; NOT a working Sidequest runtime."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / 'contracts/snapshot.json'
class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body):
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if self.path == '/health':
            return self.reply(200, {'v':1,'service':'sidequest-runtime','mode':'fixture'})
        if self.headers.get('Authorization') != 'Bearer fixture-only':
            return self.reply(403, {'v':1,'error':{'code':'POLICY_DENIED','message':'Use fixture-only token','retryable':False}})
        if self.path == '/v1/snapshot':
            return self.reply(200, json.loads(SNAPSHOT.read_text()))
        return self.reply(404, {'v':1,'error':{'code':'NOT_FOUND','message':'No fixture endpoint','retryable':False}})
    def do_POST(self):
        return self.reply(503, {'v':1,'error':{'code':'UNAVAILABLE','message':'Read-only fixture. Lane C owns interaction test doubles.','retryable':False}})
if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--port',type=int,default=4317); a=p.parse_args()
    print(f'FIXTURE ONLY: http://127.0.0.1:{a.port}; token fixture-only',flush=True)
    ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
