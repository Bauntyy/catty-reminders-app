from flask import Flask, request
import subprocess

app = Flask(__name__)

APP_DIR = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE = "catty-app.service"
ENV_FILE = f"{APP_DIR}/.env"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return "no json", 400

    sha = data.get("after")
    if not sha:
        return "no sha", 400

    print("Deploy:", sha)

    try:
        subprocess.run(["git", "-C", APP_DIR, "fetch", "origin"], check=True)
        subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", sha], check=True)
        subprocess.run(["git", "-C", APP_DIR, "clean", "-fd"], check=True)

        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")

        subprocess.run(
            ["sudo", "-n", "systemctl", "restart", SERVICE],
            check=True
        )

        return "ok", 200

    except subprocess.CalledProcessError as e:
        print("DEPLOY ERROR:", e)
        return "deploy failed", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
