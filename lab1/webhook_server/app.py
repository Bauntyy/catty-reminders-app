import os
import json
from flask import Flask, request

app = Flask(__name__)

APP_PATH = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE_NAME = "catty-app.service"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'No JSON data', 400

    ref = data.get('ref', '')
    if not ref:
        return 'No ref found', 400

    branch = ref.split('/')[-1]
    
    sha = data.get('after', 'unknown')

    print(f"Deploy branch: {branch}, SHA: {sha}")

    commands = [
        f"cd {APP_PATH}",
        "git fetch origin",
        f"git reset --hard origin/{branch}",
        f"echo DEPLOY_REF={sha} > {APP_PATH}/.env",
        f"sudo systemctl restart {SERVICE_NAME}"
    ]

    full_command = " && ".join(commands)
    exit_code = os.system(full_command)

    if exit_code == 0:
        print(f"Deployed {branch} ({sha})")
        return "OK", 200
    else:
        print(f"Deploy failed: {exit_code}")
        return "ERROR", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
