from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

APP_PATH = "/home/ubuntu/Desktop/devops/lab_1/catty-reminders-app"

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)

            print("Webhook received")

            data = json.loads(body.decode() or "{}")

            # --- ВЫЧИСЛЕНИЕ ВЕТКИ (ВАЖНО ДЛЯ ЛР) ---
            ref = data.get("ref", "refs/heads/lab1")
            branch = ref.split("/")[-1]

            print(f"Deploy branch: {branch}")

            # --- ДЕПЛОЙ ---
            cmd = f"""
            cd {APP_PATH} &&
            git fetch origin &&
            git reset --hard origin/{branch} &&
            sudo systemctl restart catty-app
            """

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                print("SUCCESS: Deployed")
            else:
                print("ERROR:", result.stderr)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            print("EXCEPTION:", e)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")


server = HTTPServer(("0.0.0.0", 8080), Handler)
print("Webhook running on 8080...")
server.serve_forever()
