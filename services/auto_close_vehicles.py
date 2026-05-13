
import os
import sqlite3
import requests

from datetime import datetime

from dotenv import load_dotenv
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from utils.logger import (
    log_event
)



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

conn = sqlite3.connect(
    DB_PATH
)

cursor = conn.cursor()


# -------------------------
# AUTO CLOSE ENABLED?
# -------------------------

cursor.execute("""
SELECT value
FROM settings
WHERE key = 'auto_close_enabled'
""")

result = cursor.fetchone()

if not result:

    conn.close()

    exit()

if result[0] != "true":

    log_event(
        "AUTO CLOSE DISABLED"
    )

    conn.close()

    exit()


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
# GET ADMINS
# -------------------------

cursor.execute("""
SELECT telegram_id
FROM employees
WHERE role IN (
    'admin',
    'super_admin'
)
AND telegram_id IS NOT NULL
""")

admins = cursor.fetchall()


# -------------------------
# GET ACTIVE VEHICLES
# -------------------------

cursor.execute("""
SELECT

    vu.id,
    vu.employee_id,
    vu.vehicle_id,
    vu.start_mileage,

    e.full_name,
    e.telegram_id,

    v.type,
    v.number,
    v.current_mileage

FROM vehicle_usage vu

JOIN employees e
ON vu.employee_id = e.id

JOIN vehicles v
ON vu.vehicle_id = v.id

WHERE vu.end_time IS NULL
""")

vehicles = cursor.fetchall()

log_event(
    f"ACTIVE VEHICLES: {len(vehicles)}"
)


# -------------------------
# REPORT
# -------------------------

report = (
    "🚫 Автоматична обробка техніки\n\n"
)

banned_count = 0

closed_count = 0


# -------------------------
# PROCESS VEHICLES
# -------------------------

for vehicle in vehicles:

    usage_id = vehicle[0]

    employee_id = vehicle[1]

    vehicle_id = vehicle[2]

    start_mileage = vehicle[3]

    full_name = vehicle[4]

    user_telegram = vehicle[5]

    vehicle_type = vehicle[6]

    vehicle_number = vehicle[7]

    current_mileage = vehicle[8]

    # placeholder
    end_mileage = current_mileage + 1

    total_mileage = (
        end_mileage - start_mileage
    )

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -------------------------
    # CLOSE USAGE
    # -------------------------

    cursor.execute("""
    UPDATE vehicle_usage

    SET
        end_time = ?,
        end_mileage = ?,
        total_mileage = ?,
        auto_closed = 1

    WHERE id = ?
    """, (
        current_time,
        end_mileage,
        total_mileage,
        usage_id
    ))

    # -------------------------
    # FREE VEHICLE
    # -------------------------

    cursor.execute("""
    UPDATE vehicles

    SET
        status = 'вільний',
        current_mileage = ?

    WHERE id = ?
    """, (
        end_mileage,
        vehicle_id
    ))

    closed_count += 1

    # -------------------------
    # AUTO BAN ENABLED?
    # -------------------------

    cursor.execute("""
    SELECT value
    FROM settings
    WHERE key = 'auto_ban_enabled'
    """)

    ban_result = cursor.fetchone()

    auto_ban = False

    if ban_result:

        if ban_result[0] == "true":

            auto_ban = True

    # -------------------------
    # BAN USER
    # -------------------------

    if auto_ban:

        # already banned?
        cursor.execute("""
        SELECT id
        FROM user_bans
        WHERE
            employee_id = ?
            AND active = 1
        """, (
            employee_id,
        ))

        existing_ban = cursor.fetchone()

        if not existing_ban:

            cursor.execute("""
            INSERT INTO user_bans (

                employee_id,
                vehicle_id,
                reason,
                created_at,
                active

            )

            VALUES (

                ?,
                ?,
                ?,
                ?,
                1

            )
            """, (
                employee_id,
                vehicle_id,
                "Не здав техніку",
                current_time
            ))

            banned_count += 1

            # USER MESSAGE
            user_text = (
                f"⛔ Вас заблоковано\n\n"
                f"🚜 {vehicle_type} №{vehicle_number}\n\n"
                f"Техніка була автоматично "
                f"закрита після 21:00\n\n"
                f"Для розблокування "
                f"зверніться до адміністратора "
                f"або механіка."
            )

            requests.post(
                TELEGRAM_URL,
                json={
                    "chat_id": user_telegram,
                    "text": user_text
                }
            )

            report += (
                f"👤 {full_name}\n"
                f"🚜 {vehicle_type} №{vehicle_number}\n"
                f"🔨 AUTO BAN\n\n"
            )

        else:

            report += (
                f"👤 {full_name}\n"
                f"🚜 {vehicle_type} №{vehicle_number}\n"
                f"⚠️ Уже заблокований\n\n"
            )

    else:

        report += (
            f"👤 {full_name}\n"
            f"🚜 {vehicle_type} №{vehicle_number}\n"
            f"✅ AUTO CLOSED ONLY\n\n"
        )


# -------------------------
# FINAL REPORT
# -------------------------

report += (
    f"🚜 Закрито техніки: {closed_count}\n"
    f"🚫 Заблоковано: {banned_count}"
)


# -------------------------
# SEND ADMIN REPORT
# -------------------------

for admin in admins:

    admin_telegram = admin[0]

    requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": admin_telegram,
            "text": report
        }
    )


conn.commit()

conn.close()

log_event(
    "AUTO CLOSE COMPLETE"
)
