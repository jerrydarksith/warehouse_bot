
import os
import sqlite3
import requests

from datetime import datetime

from utils.logger import (
    log_event
)



from dotenv import load_dotenv


load_dotenv()


# -------------------------
# SQLITE
# -------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "warehouse.db"
)


# -------------------------
# BOT
# -------------------------

BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
)


# -------------------------
# REMINDER TASK
# -------------------------

def remind_unclosed():

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    # enabled?
    cursor.execute("""
    SELECT value
    FROM settings
    WHERE key = 'reminder_enabled'
    """)

    result = cursor.fetchone()

    if not result:

        conn.close()

        return

    if result[0] != "true":

        log_event(
            "REMINDER DISABLED"
        )

        conn.close()

        return

    # active vehicles
    cursor.execute("""
    SELECT

        e.telegram_id,
        e.full_name,
        v.type,
        v.number

    FROM vehicle_usage vu

    JOIN employees e
    ON vu.employee_id = e.id

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    WHERE
        vu.end_time IS NULL
        AND e.telegram_id IS NOT NULL
    """)

    vehicles = cursor.fetchall()

    log_event(
        f"REMINDERS: {len(vehicles)}"
    )

    for vehicle in vehicles:

        telegram_id = vehicle[0]

        vehicle_type = vehicle[2]

        vehicle_number = vehicle[3]

        text = (
            f"⚠️ У вас є нездана техніка\n\n"
            f"🚜 {vehicle_type} №{vehicle_number}\n\n"
            f"Будь ласка, здайте техніку "
            f"до 21:00\n\n"
            f"Після 21:00 техніка буде "
            f"автоматично закрита,\n"
            f"а доступ до отримання "
            f"техніки заблоковано."
        )

        requests.post(
            TELEGRAM_URL,
            json={
                "chat_id": telegram_id,
                "text": text
            }
        )

    conn.close()

    log_event(
        "REMINDERS COMPLETE"
    )
