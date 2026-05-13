
import sqlite3

from aiogram import Router, F

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from handlers.admin import (
    get_admin_menu
)

router = Router()


# -------------------------
# ACTIVE VEHICLE MENU
# -------------------------

@router.message(
    F.text.regexp(r"^📋 Активна техніка")
)
async def active_vehicles(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # Штаби
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicle_usage vu
    JOIN vehicles v
    ON vu.vehicle_id = v.id
    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'штаб',
            'штаб_vna'
        )
    """)

    shtab_count = cursor.fetchone()[0]

    # Електровізки
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicle_usage vu
    JOIN vehicles v
    ON vu.vehicle_id = v.id
    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'лебідь',
            'лебідь_довгий',
            'лебідь_вага'
        )
    """)

    electro_count = cursor.fetchone()[0]

    # Навантажувачі
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicle_usage vu
    JOIN vehicles v
    ON vu.vehicle_id = v.id
    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'електричка',
            'бичок',
            'хеллі'
        )
    """)

    loader_count = cursor.fetchone()[0]

    conn.close()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"🚜 Штаби ({shtab_count})"
                )
            ],
            [
                KeyboardButton(
                    text=f"⚡ Електровізки ({electro_count})"
                )
            ],
            [
                KeyboardButton(
                    text=f"🏗 Навантажувачі ({loader_count})"
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

    await message.answer(
        "📋 Активна техніка",
        reply_markup=keyboard
    )


# -------------------------
# SHTABS
# -------------------------

@router.message(
    F.text.regexp(r"^🚜 Штаби")
)
async def shtabs(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        v.type,
        v.number,
        e.full_name,
        vu.start_time

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    JOIN employees e
    ON vu.employee_id = e.id

    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'штаб',
            'штаб_vna'
        )

    ORDER BY v.number
    """)

    vehicles = cursor.fetchall()

    conn.close()

    if not vehicles:

        await message.answer(
            "✅ Активних штабів немає"
        )

        return

    response = "🚜 Штаби\n\n"

    for vehicle in vehicles:

        vehicle_type = vehicle[0]

        vehicle_number = vehicle[1]

        full_name = vehicle[2]

        start_time = vehicle[3]

        response += (
            f"🚜 {vehicle_type} №{vehicle_number}\n"
            f"👤 {full_name}\n"
            f"🕒 {start_time}\n\n"
        )

    await message.answer(
        response
    )


# -------------------------
# ELECTRO VEHICLES
# -------------------------

@router.message(
    F.text.regexp(r"^⚡ Електровізки")
)
async def electro_vehicles(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        v.type,
        v.number,
        e.full_name,
        vu.start_time

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    JOIN employees e
    ON vu.employee_id = e.id

    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'лебідь',
            'лебідь_довгий',
            'лебідь_вага'
        )

    ORDER BY v.number
    """)

    vehicles = cursor.fetchall()

    conn.close()

    if not vehicles:

        await message.answer(
            "✅ Активних електровізків немає"
        )

        return

    response = "⚡ Електровізки\n\n"

    for vehicle in vehicles:

        vehicle_type = vehicle[0]

        vehicle_number = vehicle[1]

        full_name = vehicle[2]

        start_time = vehicle[3]

        response += (
            f"🚜 {vehicle_type} №{vehicle_number}\n"
            f"👤 {full_name}\n"
            f"🕒 {start_time}\n\n"
        )

    await message.answer(
        response
    )


# -------------------------
# LOADERS
# -------------------------

@router.message(
    F.text.regexp(r"^🏗 Навантажувачі")
)
async def loaders(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        v.type,
        v.number,
        e.full_name,
        vu.start_time

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    JOIN employees e
    ON vu.employee_id = e.id

    WHERE
        vu.end_time IS NULL
        AND v.type IN (
            'електричка',
            'бичок',
            'хеллі'
        )

    ORDER BY v.number
    """)

    vehicles = cursor.fetchall()

    conn.close()

    if not vehicles:

        await message.answer(
            "✅ Активних навантажувачів немає"
        )

        return

    response = "🏗 Навантажувачі\n\n"

    for vehicle in vehicles:

        vehicle_type = vehicle[0]

        vehicle_number = vehicle[1]

        full_name = vehicle[2]

        start_time = vehicle[3]

        response += (
            f"🚜 {vehicle_type} №{vehicle_number}\n"
            f"👤 {full_name}\n"
            f"🕒 {start_time}\n\n"
        )

    await message.answer(
        response
    )


# -------------------------
# BACK
# -------------------------

@router.message(
    F.text == "⬅️ Назад"
)
async def back_to_admin(
    message: Message
):

    await message.answer(
        "🛠 Адмін меню",
        reply_markup=get_admin_menu()
    )

