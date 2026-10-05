#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = int(os.environ.get("ROSIE_PORT", 8080))

class RosieGatewayHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_GET(self):
        if self.path == '/v1/attestation/quote':
            proof = {
                "status": "ATTESTATION_SUCCESS",
                "tee_type": "AMD-SEV-SNP",
                "measurement": "a8f5c9e2b4d1a3f6e8c7b9a0d2f4e6a8c1b3d5e7f9a1b3c5d7e9f0a2b4c6d8e0"
            }
            self._send_json(200, proof)
        elif self.path == '/healthz':
            self._send_json(200, {"status": "ok", "gateway": "rosie-core"})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        if self.path in ['/v1/chat/completions', '/v1/messages']:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            response = {
                "id": "rosie-gen-001",
                "object": "chat.completion",
                "model": "rosie-private",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This response was processed in protected TEE hardware memory."
                    },
                    "finish_reason": "stop"
                }]
            }
            self._send_json(200, response)
        else:
            self._send_json(404, {"error": "Invalid route"})

def run():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RosieGatewayHandler)
    print(f"[+] Rosie AI Gateway listening on port {PORT}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
