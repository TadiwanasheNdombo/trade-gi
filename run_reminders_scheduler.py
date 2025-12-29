import schedule
import time
import requests

import os

TOKEN = os.environ.get("ADMIN_AUTH_TOKEN")
print(f"TOKEN LOADED: {TOKEN!r}")
REMINDER_URL = f"http://127.0.0.1:5000/run-reminders?token={TOKEN}"

def trigger_reminders():
    try:
        response = requests.get(REMINDER_URL)
        print(f"Triggered reminders: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error triggering reminders: {e}")

# Schedule to run one minute from now for testing
import datetime
now = datetime.datetime.now()
run_time = (now + datetime.timedelta(minutes=1)).strftime("%H:%M")
schedule.every().day.at(run_time).do(trigger_reminders)

print(f"Scheduler started. Will trigger reminders at {run_time}...")
while True:
    schedule.run_pending()
    time.sleep(1)
