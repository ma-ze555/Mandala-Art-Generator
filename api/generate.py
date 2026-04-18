from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import urllib.parse
import ssl
import json
import base64
import os

# Pollinations AI — completely free, no token, no credits needed
# Docs: https://pollinations.ai
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true&model=flux"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            user_prompt = body.get("prompt", "mandala art")

            full_prompt = (
                f"highly detailed mandala art, {user_prompt}, "
                "symmetrical, intricate geometric patterns, zentangle, "
                "sacred geometry, high quality, 4k"
            )

            encoded = urllib.parse.quote(full_prompt)
            url = POLLINATIONS_URL.format(prompt=encoded)

            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
                image_bytes = resp.read()
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                self._respond(200, {"image": b64})

        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            self._respond(e.code, {"error": err})

        except Exception as e:
            self._respond(502, {"error": str(e)})

    def _respond(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
