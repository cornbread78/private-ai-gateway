import http.server
import socketserver
import urllib.request
import json
import sqlite3
import socket

PORT = 8080
BACKEND_URL = "http://127.0.0.1:8081"
DB_PATH = "gateway_memory.db"
HISTORY_LIMIT = 10

def check_internet(host="8.8.8.8", port=53, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_to_db(role, content):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interactions (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error] {e}")

def get_recent_history(limit=HISTORY_LIMIT):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM interactions ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except Exception as e:
        print(f"[DB History Error] {e}")
        return []

socketserver.TCPServer.allow_reuse_address = True

class GatewayHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/history":
            try:
                conn = sqlite3.connect(DB_PATH)
                rows = conn.cursor().execute(
                    "SELECT id, timestamp, role, content FROM interactions ORDER BY id ASC"
                ).fetchall()
                conn.close()
                history_data = [
                    {"id": r[0], "timestamp": r[1], "role": r[2], "content": r[3]}
                    for r in rows
                ]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(history_data, indent=2).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        self.proxy_request("GET")

    def do_POST(self):
        if self.path == "/reset":
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("DELETE FROM interactions;")
                conn.commit()
                conn.close()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "memory reset"}).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        if self.path == "/chat" or self.path.endswith("completions"):
            try:
                data = json.loads(body.decode("utf-8")) if body else {}

                # Convert single prompt key into messages list
                if "prompt" in data and "messages" not in data:
                    data["messages"] = [{"role": "user", "content": data["prompt"]}]
                    del data["prompt"]

                incoming_msgs = data.get("messages", [])
                system_msgs = [m for m in incoming_msgs if m.get("role") == "system"]
                new_user_msgs = [m for m in incoming_msgs if m.get("role") != "system"]

                is_online = check_internet()
                net_status = "ONLINE (Service available)" if is_online else "OFFLINE (Local mode)"
                print(f"[Gateway Check] {net_status}")

                if system_msgs:
                    system_msgs[0]["content"] += f"\n[System Note: Connectivity status is {net_status}]"
                else:
                    system_msgs = [{"role": "system", "content": f"You are Rosie, a helpful assistant. [System Note: Connectivity status is {net_status}]"}]

                past_history = get_recent_history(limit=HISTORY_LIMIT)
                data["messages"] = system_msgs + past_history + new_user_msgs
                body = json.dumps(data).encode("utf-8")

                for msg in new_user_msgs:
                    log_to_db(msg.get("role", "user"), msg.get("content", ""))
            except Exception as e:
                print(f"[Gateway Error] {e}")

        self.proxy_request("POST", body)

    def proxy_request(self, method, body=None):
        target_path = "/v1/chat/completions" if self.path == "/chat" else self.path
        url = BACKEND_URL + target_path
        headers = {key: val for key, val in self.headers.items() if key.lower() not in ("host", "content-length")}
        
        if body is not None:
            headers["Content-Length"] = str(len(body))

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for key, val in resp.headers.items():
                    if key.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(key, val)

                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)

                if method == "POST" and (self.path == "/chat" or self.path.endswith("completions")):
                    try:
                        resp_data = json.loads(resp_body.decode("utf-8"))
                        if "choices" in resp_data and len(resp_data["choices"]) > 0:
                            content = (resp_data["choices"][0].get("message", {}).get("content") or "").strip()
                            if content:
                                log_to_db("assistant", content)
                    except Exception as e:
                        print(f"[Log Error] {e}")

        except (BrokenPipeError, ConnectionResetError):
            print("[Gateway] Client disconnected.")
        except urllib.error.URLError as e:
            print(f"[Proxy Error] {e}")
            try:
                self.send_response(502)
                self.end_headers()
            except (BrokenPipeError, ConnectionResetError):
                pass

if __name__ == "__main__":
    init_db()
    server = socketserver.TCPServer(("127.0.0.1", PORT), GatewayHandler)
    print(f"=== Gateway Active on http://127.0.0.1:{PORT} ===")
    server.serve_forever()
