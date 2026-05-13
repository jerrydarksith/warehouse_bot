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
# GET STATUS
# -------------------------

def get_setting_status(
    key
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT value
    FROM settings
    WHERE key = ?
    """, (
        key,
    ))

    result = cursor.fetchone()

    conn.close()

    if result:

        return result[0]

    return "false"


# -------------------------
# GET MENU
# -------------------------

def get_automation_menu():

    reminder = get_setting_status(
        "reminder_enabled"
    )

    auto_close = get_setting_status(
        "auto_close_enabled"
    )

    auto_ban = get_setting_status(
        "auto_ban_enabled"
    )

    reminder_text = "🔴 OFF"

    if reminder == "true":

        reminder_text = "🟢 ON"

    auto_close_text = "🔴 OFF"

    if auto_close == "true":

        auto_close_text = "🟢 ON"

    auto_ban_text = "🔴 OFF"

    if auto_ban == "true":

        auto_ban_text = "🟢 ON"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"⏰ Нагадування {reminder_text}"
                )
            ],
            [
                KeyboardButton(
                    text=f"🚫 Автозакриття {auto_close_text}"
                )
            ],
            [
                KeyboardButton(
                    text=f"🔨 Автобан {auto_ban_text}"
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
# OPEN MENU
# -------------------------

@router.message(
    F.text == "⚙️ Автоматизація"
)
async def automation_menu(
    message: Message
):

    await message.answer(
        "⚙️ Автоматизація",
        reply_markup=get_automation_menu()
    )

# -------------------------
# TOGGLE REMINDER
# -------------------------

@router.message(
    F.text.startswith("⏰ Нагадування")
)
async def toggle_reminder(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    current = get_setting_status(
        "reminder_enabled"
    )

    new_value = "true"

    if current == "true":

        new_value = "false"

    cursor.execute("""
    UPDATE settings
    SET value = ?
    WHERE key = 'reminder_enabled'
    """, (
        new_value,
    ))

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Налаштування оновлено",
        reply_markup=get_automation_menu()
    )


# -------------------------
# TOGGLE AUTO CLOSE
# -------------------------

@router.message(
    F.text.startswith("🚫 Автозакриття")
)
async def toggle_auto_close(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    current = get_setting_status(
        "auto_close_enabled"
    )

    new_value = "true"

    if current == "true":

        new_value = "false"

    cursor.execute("""
    UPDATE settings
    SET value = ?
    WHERE key = 'auto_close_enabled'
    """, (
        new_value,
    ))

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Налаштування оновлено",
        reply_markup=get_automation_menu()
    )


# -------------------------
# TOGGLE AUTO BAN
# -------------------------

@router.message(
    F.text.startswith("🔨 Автобан")
)
async def toggle_auto_ban(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    current = get_setting_status(
        "auto_ban_enabled"
    )

    new_value = "true"

    if current == "true":

        new_value = "false"

    cursor.execute("""
    UPDATE settings
    SET value = ?
    WHERE key = 'auto_ban_enabled'
    """, (
        new_value,
    ))

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Налаштування оновлено",
        reply_markup=get_automation_menu()
    )

# -------------------------
# SYSTEM STATUS
# -------------------------

@router.message(
    F.text == "📊 Статус системи"
)
async def system_status(
    message: Message
):

    vehicle_issue = get_setting_status(
        "vehicle_issue_enabled"
    )

    reminder = get_setting_status(
        "reminder_enabled"
    )

    auto_close = get_setting_status(
        "auto_close_enabled"
    )

    auto_ban = get_setting_status(
        "auto_ban_enabled"
    )

    vehicle_issue_text = "🔴 OFF"

    if vehicle_issue == "true":

        vehicle_issue_text = "🟢 ON"

    reminder_text = "🔴 OFF"

    if reminder == "true":

        reminder_text = "🟢 ON"

    auto_close_text = "🔴 OFF"

    if auto_close == "true":

        auto_close_text = "🟢 ON"

    auto_ban_text = "🔴 OFF"

    if auto_ban == "true":

        auto_ban_text = "🟢 ON"

    text = (
        f"📊 Статус системи\n\n"

        f"📦 Видача техніки: "
        f"{vehicle_issue_text}\n"

        f"⏰ Нагадування: "
        f"{reminder_text}\n"

        f"🚫 Автозакриття: "
        f"{auto_close_text}\n"

        f"🔨 Автобан: "
        f"{auto_ban_text}"
    )

    await message.answer(
        text,
        reply_markup=get_admin_menu()
    )


