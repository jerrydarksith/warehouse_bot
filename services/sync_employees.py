import os
import math
import requests
import sqlite3

from dotenv import load_dotenv


import sys
import os

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

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (

    id INTEGER PRIMARY KEY,

    full_name TEXT,

    mobile_phone TEXT,

    telegram_id INTEGER,

    role TEXT DEFAULT 'user'
)
""")

conn.commit()


# -------------------------
# PORTAL AUTH
# -------------------------

LOGIN_URL = "https://portal-api.epicentrk.ua/api/system/common/tokens/auth"

PORTAL_CREDENTIALS = {
    "login": os.getenv("PORTAL_LOGIN"),
    "password": os.getenv("PORTAL_PASSWORD")
}

auth_response = requests.post(
    LOGIN_URL,
    json=PORTAL_CREDENTIALS
)

if auth_response.status_code != 200:

    log_event("ПОМИЛКА АВТОРИЗАЦІЇ")

    exit()


auth_data = auth_response.json()

access_token = auth_data["authToken"]["accessToken"]

log_event("Авторизація успішна")


# -------------------------
# GET EMPLOYEES
# -------------------------

BASE_URL = "https://portal-api.epicentrk.ua/api/organization/contacts/employee/filtered"

HEADERS = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

params = {
    "unitIds": 241,
    "page": 1,
    "limit": 100
}

first_response = requests.get(
    BASE_URL,
    headers=HEADERS,
    params=params
)

first_data = first_response.json()

total_count = first_data["totalCount"]

total_pages = math.ceil(
    total_count / 100
)

log_event(f"Працівників: {total_count}")

all_employees = first_data["items"]


# -------------------------
# PAGINATION
# -------------------------

for page in range(2, total_pages + 1):

    params["page"] = page

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        params=params
    )

    if response.status_code == 200:

        page_data = response.json()

        all_employees.extend(
            page_data["items"]
        )

        log_event(f"Сторінка {page} OK")


# -------------------------
# BEFORE SYNC STATS
# -------------------------

cursor.execute("""
SELECT COUNT(*)
FROM employees
WHERE id < 99000000
""")

before_portal_count = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM employees
WHERE id >= 99000000
""")

manual_users_count = cursor.fetchone()[0]



# -------------------------
# SAVE SQLITE
# -------------------------

portal_employee_ids = []


for emp in all_employees:

    emp_id = emp.get("id")

    portal_employee_ids.append(
        emp_id
    )

    full_name = emp.get(
        "fullName",
        ""
    )

    mobile_phone = emp.get(
        "mobilePhone",
        ""
    )

    mobile_phone = (
        mobile_phone
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    # CHECK EMPLOYEE
    cursor.execute("""
    SELECT id
    FROM employees
    WHERE id = ?
    """, (
        emp_id,
    ))

    existing_employee = cursor.fetchone()

    # UPDATE
    if existing_employee:

        cursor.execute("""
        UPDATE employees
        SET
            full_name = ?,
            mobile_phone = ?
        WHERE id = ?
        """, (
            full_name,
            mobile_phone,
            emp_id
        ))

    # INSERT
    else:

        cursor.execute("""
        INSERT INTO employees (
            id,
            full_name,
            mobile_phone
        )
        VALUES (?, ?, ?)
        """, (
            emp_id,
            full_name,
            mobile_phone
        ))

        log_event(
            f"NEW EMPLOYEE: "
            f"{full_name}"
        )


# -------------------------
# REMOVE OLD EMPLOYEES
# -------------------------

cursor.execute("""
SELECT

    id,
    full_name

FROM employees

WHERE id < 99000000
""")

local_employees = cursor.fetchall()


for employee in local_employees:

    employee_id = employee[0]

    full_name = employee[1]

    # IF NOT EXISTS IN PORTAL
    if employee_id not in portal_employee_ids:

        # ACTIVE VEHICLE CHECK
        cursor.execute("""
        SELECT id
        FROM vehicle_usage
        WHERE
            employee_id = ?
            AND end_time IS NULL
        """, (
            employee_id,
        ))

        active_vehicle = cursor.fetchone()

        # SKIP IF ACTIVE VEHICLE
        if active_vehicle:

            log_event(
                f"SKIPPED DELETE "
                f"(ACTIVE VEHICLE): "
                f"{full_name}"
            )

            continue

        # DELETE EMPLOYEE
        cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
        """, (
            employee_id,
        ))

        log_event(
            f"EMPLOYEE REMOVED: "
            f"{full_name}"
        )


conn.commit()


# -------------------------
# AFTER SYNC STATS
# -------------------------

cursor.execute("""
SELECT COUNT(*)
FROM employees
WHERE id < 99000000
""")

after_portal_count = cursor.fetchone()[0]


log_event(
    "========== SYNC =========="
)

log_event(
    f"Було portal users: "
    f"{before_portal_count}"
)

log_event(
    f"З порталу отримано: "
    f"{len(all_employees)}"
)

log_event(
    f"Стало portal users: "
    f"{after_portal_count}"
)

log_event(
    f"Manual users: "
    f"{manual_users_count}"
)

log_event(
    "=========================="
)


