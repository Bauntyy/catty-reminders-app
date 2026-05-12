import os
from flask import Flask, request

app = Flask(__name__)

APP_PATH = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE = "catty-app.service"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "no json", 400

    ref = data.get("ref", "")
    sha = data.get("after", "")

    if not ref or not sha:
        return "bad payload", 400

    branch = ref.split("/")[-1]

    print(f"deploy {branch} {sha}")

    cmd = f"""
cd {APP_PATH} &&
git fetch origin &&
git reset --hard origin/{branch} &&
echo DEPLOY_REF={sha} > .env &&
sudo -n systemctl restart {SERVICE}
"""

    os.system(cmd)

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
