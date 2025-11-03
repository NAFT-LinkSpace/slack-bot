import os
import base64
from dotenv import load_dotenv
from pprint import pprint
import requests
import subprocess

load_dotenv()
ROCKETCHAT_URL = os.environ['ROCKETCHAT_URL']
ROCKETCHAT_USER = os.environ['ROCKETCHAT_USER']
ROCKETCHAT_TOKEN = os.environ['ROCKETCHAT_TOKEN']

DO_PROCESS = True
if not ROCKETCHAT_URL or not ROCKETCHAT_USER or not ROCKETCHAT_TOKEN:
    DO_PROCESS = False
    print("Rocket.Chat configuration is incomplete. Skipping import.")

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'fix_database.sh')

rocketchat_headers = {
    'X-User-Id': ROCKETCHAT_USER,
    'X-Auth-Token': ROCKETCHAT_TOKEN,
}
success_response = {'success': True}

def call_api(endpoint, method='GET', data=None):
    url = f'{ROCKETCHAT_URL}/api/v1/{endpoint}'
    headers = rocketchat_headers
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
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

            # Edit database
            subprocess.run(['bash', SCRIPT_PATH], check=True)

            print("Import completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
