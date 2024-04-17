from datetime import datetime

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from pytz import timezone

app = Flask(__name__)

scheduler = BackgroundScheduler()
reminders = []

user_key = "upy5sdbfmzcokcnywxhzi9va91v5uo"
api_token = "auvmzhqes4ncu6joet7ee5h5hi7bqu"


def send_pushover_notification(message):
    url = "https://api.pushover.net/1/messages.json"
    payload = {"token": api_token, "user": user_key, "message": message}
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("Failed to send notification.")


def send_reminder(text):
    send_pushover_notification(text)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/test", methods=["POST"])
def test():
    reminder = request.get_json()
    send_pushover_notification(reminder["text"])

    return "Task added successfully"


@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    return {"reminders": reminders}


@app.route("/add_task", methods=["POST"])
def add_task():
    reminder = request.get_json()
    reminders.append(reminder)

    mst_timezone = timezone(
        "US/Mountain"
    )  # Set the timezone to Mountain Standard Time (MST)

    reminder_datetime = mst_timezone.localize(
        datetime(
            reminder["year"],
            reminder["month"],
            reminder["day"],
            hour=int(reminder["time"].split(":")[0]),
            minute=int(reminder["time"].split(":")[1]),
        )
    )

    scheduler.add_job(
        send_reminder,
        "date",
        run_date=reminder_datetime,
        args=[reminder["text"]],
    )

    return "Task added successfully"


if __name__ == "__main__":
    scheduler.start()
    app.run(host="0.0.0.0", port=5050)
