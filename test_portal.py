import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()

LOGIN_URL = "https://portal-api.epicentrk.ua/api/system/common/tokens/auth"

PORTAL_CREDENTIALS = {
    "login": os.getenv("PORTAL_LOGIN"),
    "password": os.getenv("PORTAL_PASSWORD")
}

auth_response = requests.post(LOGIN_URL, json=PORTAL_CREDENTIALS)

print(auth_response.status_code)

auth_data = auth_response.json()

access_token = auth_data["authToken"]["accessToken"]

BASE_URL = "https://portal-api.epicentrk.ua/api/organization/contacts/employee/filtered"

HEADERS = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

params = {
    "unitIds": 241,
    "page": 1,
    "limit": 1
}

response = requests.get(BASE_URL, headers=HEADERS, params=params)

data = response.json()

print(json.dumps(data["items"][0], indent=4, ensure_ascii=False))
