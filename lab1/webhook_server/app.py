from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

APP_DIR = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE = "catty-app.service"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "no json"}, 400

    ref = data.get("ref")
    if not ref or not ref.startswith("refs/heads/"):
        return {"error": "invalid ref"}, 400

    branch = ref.split("/")[-1]
    sha = data.get("after")

    print(f"[WEBHOOK] Deploy branch={branch}, sha={sha}")

    try:
        subprocess.run(
            ["git", "-C", APP_DIR, "fetch", "origin"],
            check=True
        )

        subprocess.run(
            ["git", "-C", APP_DIR, "checkout", branch],
            check=True
        )

        subprocess.run(
            ["git", "-C", APP_DIR, "reset", "--hard", f"origin/{branch}"],
            check=True
        )

        subprocess.run(
            ["git", "-C", APP_DIR, "clean", "-fd"],
            check=True
        )

        with open(os.path.join(APP_DIR, ".env"), "w") as f:
            f.write(f"DEPLOY_BRANCH={branch}\nDEPLOY_SHA={sha}\n")

        subprocess.run(
            ["sudo", "-n", "systemctl", "restart", SERVICE],
            check=True
        )

        print("[WEBHOOK] Deploy success")
        return {"status": "ok", "branch": branch}, 200

    except subprocess.CalledProcessError as e:
        print("[WEBHOOK ERROR]", e)
        return {"status": "failed"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
