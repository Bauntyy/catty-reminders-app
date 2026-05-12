from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

APP_DIR = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE = "catty-app.service"
ENV_FILE = f"{APP_DIR}/.env"
LAST_SHA_FILE = "/tmp/catty_last_sha"


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": "no json"}), 400

    if request.headers.get("X-GitHub-Event") != "push":
        return jsonify({"status": "ignored"}), 200

    sha = data.get("after")
    if not sha:
        return jsonify({"status": "no sha"}), 400

    if os.path.exists(LAST_SHA_FILE):
        with open(LAST_SHA_FILE) as f:
            if f.read().strip() == sha:
                return jsonify({"status": "duplicate ignored"}), 200

    try:
        subprocess.run(["git", "-C", APP_DIR, "fetch", "origin"], check=True)
        subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", sha], check=True)
        subprocess.run(["git", "-C", APP_DIR, "clean", "-fd"], check=True)

        with open(LAST_SHA_FILE, "w") as f:
            f.write(sha)

        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")

        subprocess.run(
            ["sudo", "-n", "systemctl", "restart", SERVICE],
            check=False
        )

        return jsonify({"status": "deployed"}), 200

    except Exception as e:
        print("DEPLOY ERROR:", e)
        return jsonify({"status": "deploy failed but ignored"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
