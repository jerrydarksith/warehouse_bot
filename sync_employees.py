import os
from dotenv import load_dotenv
import math
import requests
import sqlite3
load_dotenv()

# -------------------------
# SQLITE
# -------------------------

conn = sqlite3.connect("warehouse.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    mobile_phone TEXT
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
    print("ПОМИЛКА АВТОРИЗАЦІЇ")
    exit()

auth_data = auth_response.json()

access_token = auth_data["authToken"]["accessToken"]

print("Авторизація успішна")


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
total_pages = math.ceil(total_count / 100)

print(f"Працівників: {total_count}")

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

        all_employees.extend(page_data["items"])

        print(f"Сторінка {page} OK")


# -------------------------
# SAVE SQLITE
# -------------------------

for emp in all_employees:

    emp_id = emp.get("id")

    full_name = emp.get("fullName", "")

    mobile_phone = emp.get("mobilePhone", "")

    mobile_phone = (
        mobile_phone
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    cursor.execute("""
    INSERT OR REPLACE INTO employees (
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

conn.commit()

print(f"Збережено: {len(all_employees)} працівників")

conn.close()