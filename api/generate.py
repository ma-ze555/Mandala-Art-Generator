from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import ssl
import json
import base64
import os

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

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
                "sacred geometry, black and white, high quality, 4k"
            )

            payload = json.dumps({"inputs": full_prompt}).encode()
            req = urllib.request.Request(
                HF_API_URL, data=payload, method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {HF_TOKEN}",
                }
            )

            with OPENER.open(req) as resp:
                image_bytes = resp.read()
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                self._respond(200, {"image": b64})

        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            if e.code == 503:
                self._respond(503, {"error": "Model is loading, please wait 20 seconds and try again."})
            else:
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
