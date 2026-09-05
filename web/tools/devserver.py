#!/usr/bin/env python3
"""Serveur de developpement local pour l'IHM : sert web/ et repond a POST /api/placement en
lancant le binaire du solveur (solveur/build/placement), comme le fait la Cloud Function en
production (sans limiteur ni cache).

    ./solveur/build.sh                      # une fois : compile le solveur
    python3 web/tools/devserver.py          # puis ouvrir http://127.0.0.1:8765/
    python3 web/tools/devserver.py 9000     # autre port
"""
import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'web'
BIN = ROOT / 'solveur' / 'build' / 'placement'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def do_POST(self):
        if not self.path.startswith('/api/placement'):
            self.send_error(404); return
        n = int(self.headers.get('content-length', 0))
        body = self.rfile.read(n)
        if not BIN.exists():
            out = json.dumps({'ok': False, 'message': f'binaire absent : {BIN} (lancer solveur/build.sh)'}).encode()
        else:
            r = subprocess.run([str(BIN), '-', '--silencieux'], input=body, capture_output=True, timeout=120)
            out = r.stdout if r.stdout.strip().startswith(b'{') else json.dumps({'ok': False, 'message': r.stderr.decode(errors='replace')[:500]}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(out)))
        self.end_headers(); self.wfile.write(out)

    def do_GET(self):
        if self.path.startswith('/api/placement/version'):
            v = subprocess.run([str(BIN), '--version'], capture_output=True, text=True).stdout.strip() if BIN.exists() else 'binaire absent'
            out = json.dumps({'ok': BIN.exists(), 'version': v}).encode()
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(out))); self.end_headers(); self.wfile.write(out); return
        super().do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write('%s %s\n' % (self.command, args[0] if args else ''))


if __name__ == '__main__':
    print(f'IHM : http://127.0.0.1:{PORT}/   (solveur : {BIN if BIN.exists() else "ABSENT, lancer solveur/build.sh"})')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
