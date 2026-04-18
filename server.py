"""
Local dev server for Mandala Art Generator.
- Serves the HTML/CSS/JS files on http://localhost:8080
- Proxies /api/generate to Hugging Face Inference API (free, no credit card)

Run with:  python server.py
Then open: http://localhost:8080
"""

import http.server
import urllib.request
import urllib.error
import ssl
import json
import os
import base64

# Load token from .env file (never hardcode secrets in source)
import pathlib

def load_env():
    env_path = pathlib.Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()
HF_TOKEN = os.environ.get("HF_TOKEN", "")


# Pollinations AI — completely free, no token, no credits needed
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true&model=flux"

PORT = 8080

# Skip SSL cert verification (fixes local Windows cert issues)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return urllib.request.Request(
            newurl, data=req.data, method=req.get_method(),
            headers=dict(req.headers)
        )

OPENER = urllib.request.build_opener(
    RedirectHandler,
    urllib.request.HTTPSHandler(context=SSL_CTX)
)


class Handler(http.server.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate":
            self._generate()
        else:
            self.send_error(404)

    def do_GET(self):
        super().do_GET()

    def _generate(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            user_prompt = body.get("prompt", "mandala art")

            full_prompt = (
                f"highly detailed mandala art, {user_prompt}, "
                "symmetrical, intricate geometric patterns, zentangle, "
                "sacred geometry, high quality, 4k"
            )

            import urllib.parse
            encoded = urllib.parse.quote(full_prompt)
            url = POLLINATIONS_URL.format(prompt=encoded)

            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            with OPENER.open(req) as resp:
                image_bytes = resp.read()
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                self._json(200, {"image": b64})

        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"HF API error {e.code}: {err_body[:200]}")
            if e.code == 503:
                self._json(503, {"error": "Model is loading, please wait 20 seconds and try again."})
            elif e.code == 404:
                self._json(404, {"error": f"Model not found on Hugging Face. Raw: {err_body[:200]}"})
            else:
                self._json(e.code, {"error": err_body[:500]})

        except Exception as e:
            print(f"Server error: {e}")
            self._json(502, {"error": str(e)})

    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        print(f"  {fmt % args}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not HF_TOKEN:
        print("\n  ⚠️  HF_TOKEN not set! Add it to your .env file.")
        print("  Copy .env.example to .env and paste your token.\n")
    else:
        print(f"\n  Mandala Art Server running at http://localhost:{PORT}")
        print(f"  Open your browser to: http://localhost:{PORT}\n")
    http.server.HTTPServer(("", PORT), Handler).serve_forever()
