import os
from dotenv import load_dotenv
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import threading
from functools import wraps
from datetime import datetime, timedelta
import subprocess

from migrate_to_rocketchat import migrate

POST_URL = 'https://slack.com/api/chat.postMessage'

load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOCKEN = os.environ['SLACK_APP_TOKEN']
POST_CHANNEL_NAME = os.environ['POST_CHANNEL_NAME']

app = App(token=SLACK_BOT_TOKEN)

POST_CHANNEL_ID = ""
CHANNEL_DATA = dict()
USER_DATA = dict()

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../backup')
MERGE_SCRIPT = os.path.join(os.path.dirname(__file__), 'merge_slack_backup.sh')
BACKUP_COMPLETED_MONTHS = set()
BACKUP_REQUIRED_MONTHS = set()

backup_lock = threading.Lock()

# lock for thread safety
def single_threaded(func):
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not lock.acquire(blocking=False):
            print(f"{func.__name__} is already running, skipping.")
            return
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return wrapper

@app.event('message')
def post_message(message, say):
    # ignore messages from the posting channel
    if message["channel"] == POST_CHANNEL_ID:
        return

    # get posted user name and icon
    user_name = USER_DATA[message["user"]]["name"]
    user_icon = USER_DATA[message["user"]]["img"]

    # get message text
    try:
        message_text = message["text"]

        # replace mention
        pattern = r"<@.*?>"
        re_result_list = re.findall(pattern, message_text)
        if re_result_list != []:
            for re_result in re_result_list:
                mention_user_id = re_result[2:-1]
                try:
                    mention_user_name = USER_DATA[mention_user_id]["name"]
                except KeyError:
                    mention_user_name = "unknown user"
                    threading.Thread(target=get_channel_user_data, daemon=True).start()
                message_text = message_text.replace(re_result, " `@" + mention_user_name + "` ")
        message_text = message_text.replace("<!channel>", " `@channel` ")
    except KeyError:
        message_text = ""

    # get posted files
    if "files" in message:
        message_text += "\n"
        for file in message["files"]:
            message_text += f"<{file['permalink']}|{file['name']}>, "
        message_text = message_text[:-2]  # remove last ", "

    # get posted channel name
    try:
        channel_name = CHANNEL_DATA[message["channel"]]
    except KeyError:
        channel_name = "unkown channel"
        threading.Thread(target=get_channel_user_data, daemon=True).start()

    # post message
    say(
        channel = POST_CHANNEL_ID,
        username = user_name,
        icon_url = user_icon,
        text=f"`#{channel_name}`\n{message_text}",
    )

# if mention
@app.event("app_mention")
def mention(body, say):
    text = body["event"]["text"]

    # if include "reload" in mention
    if "reload" in text:
        say(
            channel = POST_CHANNEL_ID,
            username = "rocketryload",
            text=f"channelとuserの情報を更新するよ！"
        )

        # reload channel and user data
        get_channel_user_data()

        say(
            channel = POST_CHANNEL_ID,
            username = "rocketryload",
            text=f"更新が終わったよ！"
        )
    # if include "backup" in mention
    elif "backup" in text:
        say(
            channel = POST_CHANNEL_ID,
            username = "rocketrybackup",
            text=f"バックアップを開始するよ！"
        )

        threading.Thread(target=run_backup_process, args=(say,), daemon=True).start()


@app.event('message')
def handle_message_events(body, logger):
    logger.info(body)

@single_threaded
def get_channel_user_data():
    print("getting channel and user data...")

    # get channel data
    url = "https://slack.com/api/conversations.list?limit=999"
    headres = {"Authorization": "Bearer " + SLACK_BOT_TOKEN}
    response = requests.get(url, headers=headres)
    response_json = response.json()
    global CHANNEL_DATA
    for i in response_json["channels"]:
        CHANNEL_DATA[i["id"]] = i["name"]

    # get user data
    url = "https://slack.com/api/users.list"
    headres = {"Authorization": "Bearer " + SLACK_BOT_TOKEN}
    response = requests.get(url, headers=headres)
    response_json = response.json()
    global USER_DATA
    for i in response_json["members"]:
        try:
            USER_DATA[i["id"]] = {"name": i["real_name"], "img": i["profile"]["image_72"]}
        except KeyError:
            USER_DATA[i["id"]] = {"name": i["name"], "img": i["profile"]["image_72"]}
            print("Error: KeyError of getting user name")

    print("getting channel and user data... done")

def format_date(date_obj):
    return date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def update_backup_months():
    today = datetime.now()
    this_month_first_day = format_date(today)
    one_month_ago_first_day = format_date(this_month_first_day - timedelta(days=1))

    with backup_lock:
        if not one_month_ago_first_day in BACKUP_COMPLETED_MONTHS:
            two_months_ago_first_day = format_date(one_month_ago_first_day - timedelta(days=1))
            three_months_ago_first_day = format_date(two_months_ago_first_day - timedelta(days=1))

            if not two_months_ago_first_day in BACKUP_COMPLETED_MONTHS:
                BACKUP_REQUIRED_MONTHS.add(two_months_ago_first_day)
            BACKUP_REQUIRED_MONTHS.add(one_month_ago_first_day)

            if BACKUP_COMPLETED_MONTHS.__contains__(three_months_ago_first_day):
                BACKUP_COMPLETED_MONTHS.remove(three_months_ago_first_day)

def initialize_backup():
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        update_backup_months()

        log_path = os.path.join(BACKUP_DIR, "log.txt")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
                with backup_lock:
                    for line in lines:
                        date_str = line.strip()
                        date_obj = datetime.strptime(date_str, "%Y%m")
                        if date_obj in BACKUP_REQUIRED_MONTHS:
                            BACKUP_REQUIRED_MONTHS.remove(date_obj)
                            BACKUP_COMPLETED_MONTHS.add(date_obj)
    except Exception as e:
        print(f"Error initializing backup: {e}")

def update_backup_log(date_obj):
    try:
        with backup_lock:
            BACKUP_REQUIRED_MONTHS.remove(date_obj)
            BACKUP_COMPLETED_MONTHS.add(date_obj)
        log_path = os.path.join(BACKUP_DIR, "log.txt")
        with open(log_path, "a") as f:
            f.write(date_obj.strftime("%Y%m") + "\n")
    except Exception as e:
        print(f"Error updating backup log: {e}")

def run_backup():
    try:
        counter = 0
        update_backup_months()

        with backup_lock:
            months_to_process = list(BACKUP_REQUIRED_MONTHS)

        for month in months_to_process:
            month_str = month.strftime("%Y%m")
            zip_path = os.path.join(BACKUP_DIR, "slackdump_" + month_str + ".zip")

            next_month = format_date(month + timedelta(days=31))

            # 1. run slackdump
            # format time range in UTC ISO8601 (YYYY-MM-DDTHH:MM:SSZ)
            start_utc = format_date(month).strftime('%Y-%m-%dT%H:%M:%S')
            end_utc = format_date(next_month).strftime('%Y-%m-%dT%H:%M:%S')

            print(f"Backing up for {month_str} from {start_utc} to {end_utc}...")

            cmd_dump = [
                "slackdump",
                "export",
                "-o", zip_path,
                f"-time-from={start_utc}",
                f"-time-to={end_utc}",
                "-y",
            ]
            subprocess.run(cmd_dump, check=True)

            # 2. update backup log
            update_backup_log(month)
            counter += 1

            # 3. migrate to Rocket.Chat
            migrate(zip_path)
        return counter
    except subprocess.CalledProcessError as e:
        print(f"Error during backup process: {e}")
        return -1

def run_backup_process(say):
    result = run_backup()
    if result > 0:
        say(
            channel = POST_CHANNEL_ID,
            username = "rocketrybackup",
            text=f"バックアップが完了したよ！{result}件のバックアップを作成したよ！"
        )
    elif result == 0:
        say(
            channel = POST_CHANNEL_ID,
            username = "rocketrybackup",
            text=f"バックアップは既に最新の状態だよ！"
        )
    else:
        say(
            channel = POST_CHANNEL_ID,
            username = "rocketrybackup",
            text=f"バックアップ中にエラーが発生したよ！"
        )

def main():
    print("start!")
    get_channel_user_data()
    initialize_backup()
    global POST_CHANNEL_ID
    POST_CHANNEL_ID = [key for key, value in CHANNEL_DATA.items() if value == POST_CHANNEL_NAME][0]

    SocketModeHandler(app, SLACK_APP_TOCKEN).start()

if __name__ == "__main__":
    main()