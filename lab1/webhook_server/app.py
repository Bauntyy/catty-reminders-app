import os
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_PATH = "/home/timoha/Desktop/devops/catty-reminders-app"
SERVICE_NAME = "catty-app"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'No JSON', 400

    ref = data.get('ref', '')
    sha = data.get('after', 'unknown')

    if not ref:
        return 'No ref', 400

    branch = ref.split('/')[-1]

    print(f"Deploy branch: {branch}, SHA: {sha}")

    command = f"""
    cd {APP_PATH} &&
    git fetch origin &&
    git reset --hard origin/{branch} &&
    echo 'DEPLOY_REF={sha}' > .env &&
    sudo -n systemctl restart {SERVICE_NAME}
    """

    exit_code = os.system(command)

    if exit_code == 0:
        print("Deploy success")
        return "OK", 200
    else:
        print(f"Deploy failed: {exit_code}")
        return "FAILED", 200 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
