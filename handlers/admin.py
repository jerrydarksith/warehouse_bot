
import sqlite3

from aiogram import Router, F

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)


router = Router()


# -------------------------
# ADMIN CHECK
# -------------------------

def is_admin(role):

    return role in [
        "admin",
        "super_admin"
    ]


# -------------------------
# GET ACTIVE COUNT
# -------------------------

def get_active_vehicle_count():

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicle_usage
    WHERE end_time IS NULL
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# -------------------------
# ADMIN MENU
# -------------------------


def get_admin_menu():

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # ACTIVE VEHICLES
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicle_usage
    WHERE end_time IS NULL
    """)

    active_count = cursor.fetchone()[0]

    # SERVICE VEHICLES
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE status = 'сервіс'
    """)

    service_count = cursor.fetchone()[0]

    conn.close()

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"📋 Активна техніка ({active_count})"
                )
            ],

            [
                KeyboardButton(
                    text="📊 Статус системи"
                )
            ],

            [
                KeyboardButton(
                    text=f"🔧 Сервіс техніки ({service_count})"
                )
            ],
            
            [
                KeyboardButton(
                    text="📋 Журнал техніки"
                )
            ],
            [
                KeyboardButton(
                    text="🚜 Стан техніки"
                )
            ],
            [
                KeyboardButton(
                    text="⚙️ Управління видачею"
                )
            ],

            [
                KeyboardButton(
                    text="🔄 Оновити базу"
                )
            ],

            [
                KeyboardButton(
                    text="⚙️ Автоматизація"
                )
            ],

            [
                KeyboardButton(
                    text="🚫 Управління банами"
                )
            ]
        ],
        resize_keyboard=True
    )




# -------------------------
# ISSUE MENU
# -------------------------

issue_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🟢 Відкрити видачу"
            )
        ],
        [
            KeyboardButton(
                text="🔴 Закрити видачу"
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
# OPEN ADMIN MENU
# -------------------------

@router.message(
    F.text == "/admin"
)
async def admin_panel(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT role
    FROM employees
    WHERE telegram_id = ?
    """, (
        message.from_user.id,
    ))

    user = cursor.fetchone()

    conn.close()

    if not user:

        await message.answer(
            "❌ Користувача не знайдено"
        )

        return

    role = user[0]

    if not is_admin(role):

        await message.answer(
            "❌ Немає доступу"
        )

        return

    await message.answer(
        "🛠 Адмін меню",
        reply_markup=get_admin_menu()
    )


# -------------------------
# ISSUE MENU
# -------------------------

@router.message(
    F.text == "⚙️ Управління видачею"
)
async def issue_control_menu(
    message: Message
):

    await message.answer(
        "⚙️ Управління видачею",
        reply_markup=issue_menu
    )


# -------------------------
# BACK TO ADMIN MENU
# -------------------------

@router.message(
    F.text == "⬅️ Назад"
)
async def back_to_admin_menu(
    message: Message
):

    await message.answer(
        "🛠 Адмін меню",
        reply_markup=get_admin_menu()
    )


# -------------------------
# ENABLE ISSUE
# -------------------------

@router.message(
    F.text == "🟢 Відкрити видачу"
)
async def enable_issue(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE settings
    SET value = 'true'
    WHERE key = 'vehicle_issue_enabled'
    """)

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Видачу техніки відкрито",
        reply_markup=issue_menu
    )


# -------------------------
# DISABLE ISSUE
# -------------------------

@router.message(
    F.text == "🔴 Закрити видачу"
)
async def disable_issue(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE settings
    SET value = 'false'
    WHERE key = 'vehicle_issue_enabled'
    """)

    conn.commit()

    conn.close()

    await message.answer(
        "⛔ Видачу техніки закрито",
        reply_markup=issue_menu
    )


# -------------------------
# ACTIVE VEHICLES
# -------------------------




# -------------------------
# SYNC EMPLOYEES
# -------------------------

@router.message(
    F.text == "🔄 Оновити базу"
)
async def sync_employees(
    message: Message
):

    import subprocess

    await message.answer(
        "🔄 Оновлення бази..."
    )

    result = subprocess.run(
        [
            "/home/ubuntu/warehouse_bot/venv/bin/python3",
            "/home/ubuntu/warehouse_bot/services/sync_employees.py"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout

    error = result.stderr

    if error:

        await message.answer(
            f"❌ Помилка оновлення\n\n"
            f"{error}"
        )

        return

    await message.answer(
        f"✅ Оновлення завершено\n\n"
        f"{output}",
        reply_markup=get_admin_menu()
    )

