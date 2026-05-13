
from aiogram import Router, F

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)


router = Router()


# -------------------------
# JOURNAL MENU
# -------------------------

journal_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📋 Штаби"
            )
        ],
        [
            KeyboardButton(
                text="📋 Електровізки"
            )
        ],
        [
            KeyboardButton(
                text="📋 Навантажувачі"
            )
        ],
        [
            KeyboardButton(
                text="⬅️ Назад"
            )
        ]
    ],
    resize_keyboard=True
)


# -------------------------
# OPEN JOURNAL
# -------------------------

@router.message(
    F.text == "📋 Журнал техніки"
)
async def open_journal(
    message: Message
):

    await message.answer(
        "📋 Журнал техніки",
        reply_markup=journal_menu
    )

import sqlite3


# -------------------------
# SHOW VEHICLES
# -------------------------

@router.message(
    F.text.in_([
        "📋 Штаби",
        "📋 Електровізки",
        "📋 Навантажувачі"
    ])
)
async def show_journal_vehicles(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    vehicle_types = []

    # ШТАБИ
    if message.text == "📋 Штаби":

        vehicle_types = [
            "штаб",
            "штаб_vna"
        ]

    # ЕЛЕКТРОВІЗКИ
    elif message.text == "📋 Електровізки":

        vehicle_types = [
            "лебідь",
            "лебідь_довгий",
            "лебідь_вага"
        ]

    # НАВАНТАЖУВАЧІ
    elif message.text == "📋 Навантажувачі":

        vehicle_types = [
            "електричка",
            "бичок",
            "хеллі"
        ]

    placeholders = ",".join(
        "?" * len(vehicle_types)
    )

    cursor.execute(f"""
    SELECT

        id,
        type,
        number,
        status

    FROM vehicles

    WHERE type IN ({placeholders})

    ORDER BY type, number
    """, vehicle_types)

    vehicles = cursor.fetchall()

    conn.close()

    keyboard_rows = []

    for vehicle in vehicles:

        vehicle_type = vehicle[1]

        vehicle_number = vehicle[2]

        status = vehicle[3]

        status_icon = "🟢"

        if status == "зайнятий":

            status_icon = "🔴"

        elif status == "сервіс":

            status_icon = "🔧"

        keyboard_rows.append([
            KeyboardButton(
                text=(
                    f"{status_icon} "
                    f"{vehicle_type} "
                    f"№{vehicle_number}"
                )
            )
        ])

    keyboard_rows.append([
        KeyboardButton(
            text="⬅️ Назад"
        )
    ])

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

    await message.answer(
        "📋 Оберіть техніку",
        reply_markup=keyboard
    )


# -------------------------
# VEHICLE JOURNAL
# -------------------------

@router.message()
async def vehicle_journal_handler(
    message: Message
):

    text = message.text

    if "№" not in text:

        return

    try:

        vehicle_data = (
            text.split(" ")
        )

        vehicle_type = vehicle_data[1]

        vehicle_number = (
            text.split("№")[1]
            .strip()
        )

    except:

        return

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # VEHICLE
    cursor.execute("""
    SELECT

        id,
        current_mileage,
        status

    FROM vehicles

    WHERE
        type = ?
        AND number = ?
    """, (
        vehicle_type,
        vehicle_number
    ))

    vehicle = cursor.fetchone()

    if not vehicle:

        await message.answer(
            "❌ Техніку не знайдено"
        )

        conn.close()

        return

    vehicle_id = vehicle[0]

    current_mileage = vehicle[1]

    status = vehicle[2]

    # JOURNAL
    cursor.execute("""
    SELECT

        e.full_name,
        vu.start_time,
        vu.start_mileage,
        vu.end_mileage

    FROM vehicle_usage vu

    JOIN employees e
    ON vu.employee_id = e.id

    WHERE vu.vehicle_id = ?

    ORDER BY vu.id DESC

    LIMIT 30
    """, (
        vehicle_id,
    ))

    logs = cursor.fetchall()

    conn.close()

    status_icon = "🟢"

    if status == "зайнятий":

        status_icon = "🔴"

    elif status == "сервіс":

        status_icon = "🔧"

    response = (
        f"🚜 {status_icon} "
        f"{vehicle_type} №{vehicle_number}\n\n"

        f"📈 Поточні мотогодини:\n"
        f"{current_mileage}\n\n"

        f"📋 Останні записи:\n\n"
    )

    if not logs:

        response += (
            "❌ Історія відсутня"
        )

    else:

        for log in logs:

            full_name = log[0]

            start_time = log[1]

            start_mileage = log[2]

            end_mileage = log[3]

            if end_mileage is None:

                end_mileage = "АКТИВНО"

            response += (
                f"👤 {full_name}\n"
                f"📅 {start_time}\n"
                f"📈 {start_mileage} → "
                f"{end_mileage}\n\n"
            )

    if len(response) > 4000:

        response = response[:4000]

    await message.answer(
        response
    )


