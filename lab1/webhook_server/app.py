import os
import json
from flask import Flask, request

app = Flask(__name__)

APP_PATH = "/home/timoha/Desktop/devops/catty-reminders-app/lab1"
SERVICE_NAME = "catty-app"

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

    print(f"Получено событие для ветки: {branch}, SHA: {sha}")

    commands = [
        f"cd {APP_PATH}",
        "git fetch origin",
        f"git reset --hard origin/{branch}",
        f"echo 'DEPLOY_REF={sha}' > {APP_PATH}/.env",
        f"sudo -n systemctl restart {SERVICE_NAME}"
    ]

    full_command = " && ".join(commands)
    exit_code = os.system(full_command)

    if exit_code == 0:
        print(f"Успешно развернута ветка {branch} (SHA: {sha})")
        return f"OK: Deployed branch {branch}", 200
    else:
        print(f"Ошибка при выполнении команд. Код: {exit_code}")
        return 'Error: Deployment failed', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
