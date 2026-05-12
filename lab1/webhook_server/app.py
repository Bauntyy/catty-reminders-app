from flask import Flask, request, jsonify
import subprocess
import os
import logging

class WebhookManager:
    def __init__(self):
        self.app = Flask(__name__)

        # 🔧 НАСТРОЙКИ
        self.port = 8080
        self.app_dir = "/home/timoha/Desktop/devops/catty-reminders-app"
        self.service_name = "catty-app.service"
        self.env_file = os.path.join(self.app_dir, ".env")

        logging.basicConfig(level=logging.INFO)

        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule("/", "webhook", self.handle_request, methods=["GET", "POST"])

    def handle_request(self):
        if request.method == "GET":
            return jsonify({"status": "ok", "message": "webhook alive"}), 200

        event = request.headers.get("X-GitHub-Event")
        if event != "push":
            return jsonify({"message": "ignored (not push)"}), 200

        payload = request.get_json(silent=True) or {}
        ref = payload.get("ref")

        if not ref:
            return jsonify({"error": "no ref"}), 400

        branch = ref.split("/")[-1]

        logging.info(f"Deploy started for branch: {branch}")

        try:
            self._deploy(branch)
            return jsonify({"status": "success", "branch": branch}), 200

        except subprocess.CalledProcessError as e:
            logging.error(f"Deploy failed: {e}")
            return jsonify({"status": "failed"}), 500

    def _deploy(self, branch):
        subprocess.run(
            ["git", "-C", self.app_dir, "fetch", "origin"],
            check=True
        )

        subprocess.run(
            ["git", "-C", self.app_dir, "checkout", branch],
            check=True
        )

        subprocess.run(
            ["git", "-C", self.app_dir, "pull", "origin", branch],
            check=True
        )

        logging.info("Code updated")

        with open(self.env_file, "w") as f:
            f.write(f"DEPLOY_BRANCH={branch}\n")

        logging.info("ENV updated")

        subprocess.run(
            ["sudo", "-n", "systemctl", "restart", self.service_name],
            check=True
        )

        logging.info("Service restarted")

    def run(self):
        self.app.run(host="0.0.0.0", port=self.port)


if __name__ == "__main__":
    manager = WebhookManager()
    manager.run()
