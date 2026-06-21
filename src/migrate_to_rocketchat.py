import os
import platform
import base64
from dotenv import load_dotenv
from pprint import pprint
import requests
import subprocess

load_dotenv()
ROCKETCHAT_USER = os.environ['ROCKETCHAT_USER']
ROCKETCHAT_TOKEN = os.environ['ROCKETCHAT_TOKEN']

DO_PROCESS = True
if not ROCKETCHAT_USER or not ROCKETCHAT_TOKEN:
    DO_PROCESS = False
    print("Rocket.Chat configuration is incomplete. Skipping import.")

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'fix_database.sh')
HEADERS = {}
if DO_PROCESS:
    HEADERS = {
        'X-User-Id': ROCKETCHAT_USER,
        'X-Auth-Token': ROCKETCHAT_TOKEN,
    }
IS_WINDOWS = platform.system() == 'Windows'

def call_api(endpoint, method='GET', data=None):
    url = f'http://localhost:3000/api/v1/{endpoint}'
    if method == 'GET':
        response = requests.get(url, headers=HEADERS)
    elif method == 'POST':
        response = requests.post(url, headers=HEADERS, json=data)
    else:
        raise ValueError("Unsupported HTTP method")
    return response.json()

def migrate(zip_file_path):
    if not DO_PROCESS:
        print("Skipping import to 'Rocket.Chat' due to incomplete configuration.")
        return

    try:
        # Upload the Slack export zip file
        with open(zip_file_path, 'rb') as f:
            file_bytes = f.read()
            content = base64.b64encode(file_bytes).decode('utf-8')
            data = {
                'binaryContent': content,
                'importerKey': 'slack',
                'fileName': os.path.basename(zip_file_path),
                'contentType': 'application/zip',
            }
            response = call_api('uploadImportFile', 'POST', data)

            if response['success'] != True:
                pprint(response.json())
                return

            # Confirm the file data is ready (without this, import fails)
            call_api('getImportFileData', 'GET')

            # Start the import process
            data = {
                'input': {
                    'users': {'all': 'true'},
                    'channels': {'all': 'true'},
                },
            }
            response = call_api('startImport', 'POST', data)

            if response['success'] != True:
                pprint(response.json())
                return

            # Edit database (Rocket.Chat のバグ修正により以下は不要なはず)
            # if IS_WINDOWS:
            #     subprocess.run(['busybox64u', 'bash', SCRIPT_PATH], check=True)
            # else:
            #     subprocess.run(['bash', SCRIPT_PATH], check=True)

            # print("Import completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
