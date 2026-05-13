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
# BAN MENU
# -------------------------

ban_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🚫 Активні бани"
            )
        ],
        [
            KeyboardButton(
                text="📜 Історія банів"
            )
        ],
        [
            KeyboardButton(
                text="🔓 Розбанити користувача"
            )
        ],
        [
            KeyboardButton(
                text="🔓 Розбанити всіх"
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
# OPEN BAN MENU
# -------------------------

@router.message(
    F.text == "🚫 Управління банами"
)
async def open_ban_menu(
    message: Message
):

    await message.answer(
        "🚫 Управління банами",
        reply_markup=ban_menu
    )


# -------------------------
# ACTIVE BANS
# -------------------------

@router.message(
    F.text == "🚫 Активні бани"
)
async def active_bans(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        ub.id,
        e.full_name,
        ub.reason,
        ub.created_at,
        v.type,
        v.number

    FROM user_bans ub

    JOIN employees e
    ON ub.employee_id = e.id

    JOIN vehicles v
    ON ub.vehicle_id = v.id

    WHERE ub.active = 1

    ORDER BY ub.created_at DESC
    """)

    bans = cursor.fetchall()

    conn.close()

    if not bans:

        await message.answer(
            "✅ Активних банів немає",
            reply_markup=ban_menu
        )

        return

    response = "🚫 Активні бани\n\n"

    for ban in bans:

        ban_id = ban[0]

        full_name = ban[1]

        reason = ban[2]

        created_at = ban[3]

        vehicle_type = ban[4]

        vehicle_number = ban[5]

        response += (
            f"🆔 Бан #{ban_id}\n"
            f"👤 {full_name}\n"
            f"🚜 {vehicle_type} №{vehicle_number}\n"
            f"📌 {reason}\n"
            f"📅 {created_at}\n\n"
        )

    await message.answer(
        response,
        reply_markup=ban_menu
    )


# -------------------------
# UNBAN ALL
# -------------------------

@router.message(
    F.text == "🔓 Розбанити всіх"
)
async def unban_all(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE user_bans
    SET active = 0
    WHERE active = 1
    """)

    updated_count = cursor.rowcount

    conn.commit()

    conn.close()

    await message.answer(
        f"✅ Розбанено:\n\n"
        f"{updated_count} користувачів",
        reply_markup=ban_menu
    )


# -------------------------
# UNBAN USER MENU
# -------------------------

@router.message(
    F.text == "🔓 Розбанити користувача"
)
async def unban_user_menu(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        ub.id,
        e.full_name,
        v.type,
        v.number

    FROM user_bans ub

    JOIN employees e
    ON ub.employee_id = e.id

    JOIN vehicles v
    ON ub.vehicle_id = v.id

    WHERE ub.active = 1
    """)

    bans = cursor.fetchall()

    conn.close()

    if not bans:

        await message.answer(
            "✅ Активних банів немає",
            reply_markup=ban_menu
        )

        return

    keyboard_rows = []

    for ban in bans:

        ban_id = ban[0]

        full_name = ban[1]

        vehicle_type = ban[2]

        vehicle_number = ban[3]

        keyboard_rows.append([
            KeyboardButton(
                text=f"🔓 {ban_id} | {full_name} | {vehicle_type} №{vehicle_number}"
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
        "Оберіть користувача для розбану",
        reply_markup=keyboard
    )


# -------------------------
# UNBAN USER
# -------------------------

@router.message(
    F.text.startswith("🔓 ")
)
async def unban_user(
    message: Message
):

    if "|" not in message.text:

        return

    ban_id = (
        message.text
        .replace("🔓", "")
        .split("|")[0]
        .strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE user_bans
    SET active = 0
    WHERE id = ?
    """, (
        ban_id,
    ))

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Користувача розбанено",
        reply_markup=ban_menu
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



# -------------------------
# BAN HISTORY
# -------------------------

@router.message(
    F.text == "📜 Історія банів"
)
async def ban_history(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        e.full_name,
        COUNT(ub.id),
        MAX(ub.created_at),
        MAX(ub.active)

    FROM user_bans ub

    JOIN employees e
    ON ub.employee_id = e.id

    GROUP BY ub.employee_id

    ORDER BY COUNT(ub.id) DESC
    """)

    bans = cursor.fetchall()

    conn.close()

    if not bans:

        await message.answer(
            "📭 Історія банів порожня",
            reply_markup=ban_menu
        )

        return

    response = "📜 Історія банів\n\n"

    for ban in bans:

        full_name = ban[0]

        ban_count = ban[1]

        last_ban = ban[2]

        active = ban[3]

        status = "🟢 Немає"

        if active == 1:

            status = "🔴 Активний"

        response += (
            f"👤 {full_name}\n"
            f"🚫 Банів: {ban_count}\n"
            f"📅 Останній бан:\n"
            f"{last_ban}\n"
            f"📌 Статус: {status}\n\n"
        )

    await message.answer(
        response,
        reply_markup=ban_menu
    )



