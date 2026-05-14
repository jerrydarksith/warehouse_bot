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

from aiogram.fsm.state import (
    StatesGroup,
    State
)


from aiogram.fsm.context import (
    FSMContext
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
                text="🚫 Ручний бан"
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

    LEFT JOIN vehicles v
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

    LEFT JOIN vehicles v
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

        vehicle_text = "Без техніки"

        if vehicle_type and vehicle_number:
           vehicle_text = (
               f"{vehicle_type} "
               f"№{vehicle_number}"
           )

        keyboard_rows.append([
            KeyboardButton(
                text=f"🔓 {ban_id} | {full_name} | {vehicle_text}"
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


# -------------------------
# STATES
# -------------------------

class ManualBanState(
    StatesGroup
):

    waiting_search = State()

    waiting_select = State()

    waiting_reason = State()





# -------------------------
# MANUAL BAN
# -------------------------

@router.message(
    F.text == "🚫 Ручний бан"
)
async def manual_ban_start(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ManualBanState.waiting_search
    )

    await message.answer(
        "👤 Введіть прізвище\n\n"
        "Наприклад:\n"
        "Босак"
    )


# -------------------------
# SEARCH USER
# -------------------------

@router.message(
    ManualBanState.waiting_search
)
async def manual_ban_search(
    message: Message,
    state: FSMContext
):

    search_text = (
        message.text.strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        id,
        full_name

    FROM employees

    WHERE full_name LIKE ?

    ORDER BY full_name
    """, (
        f"{search_text}%",
    ))

    employees = cursor.fetchall()

    conn.close()

    if not employees:

        await message.answer(
            "❌ Нічого не знайдено"
        )

        return

    keyboard_rows = []

    for employee in employees:

        employee_id = employee[0]

        full_name = employee[1]

        keyboard_rows.append([
            KeyboardButton(
                text=(
                    f"👤 "
                    f"{full_name}"
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

    await state.update_data(
        found_users=employees
    )

    await message.answer(
        "👤 Оберіть користувача",
        reply_markup=keyboard
    )

    await state.set_state(
        ManualBanState.waiting_select
    )

# -------------------------
# SELECT USER
# -------------------------

@router.message(
    ManualBanState.waiting_select
)
async def manual_ban_select(
    message: Message,
    state: FSMContext
):

    text = message.text.replace(
        "👤 ",
        ""
    ).strip()

    data = await state.get_data()

    found_users = data.get(
        "found_users",
        []
    )

    selected_user = None

    for user in found_users:

        if user[1] == text:

            selected_user = user

            break

    if not selected_user:

        await message.answer(
            "❌ Користувача не знайдено"
        )

        return

    employee_id = selected_user[0]

    full_name = selected_user[1]

    await state.update_data(
        selected_employee_id=employee_id,
        selected_full_name=full_name
    )

    await state.set_state(
        ManualBanState.waiting_reason
    )

    await message.answer(
        f"🚫 {full_name}\n\n"
        f"📝 Введіть причину бану"
    )


# -------------------------
# SAVE MANUAL BAN
# -------------------------

@router.message(
    ManualBanState.waiting_reason
)
async def manual_ban_reason(
    message: Message,
    state: FSMContext
):

    reason = (
        message.text.strip()
    )

    data = await state.get_data()

    employee_id = data.get(
        "selected_employee_id"
    )

    full_name = data.get(
        "selected_full_name"
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()


    # ADMIN
    cursor.execute("""
    SELECT id, full_name
    FROM employees
    WHERE telegram_id = ?
    """, (
        message.from_user.id,
    ))

    admin = cursor.fetchone()

    admin_id = admin[0]

    admin_name = admin[1]

    # SAVE BAN
    cursor.execute("""
    INSERT INTO user_bans (

        employee_id,
        reason,
        created_at,
        active,
        ban_type,
        banned_by

    ) VALUES (?, ?, datetime('now'), 1, ?, ?)
    """, (
        employee_id,
        reason,
        "manual",
        admin_id,
    ))

    conn.commit()

    # USER TELEGRAM
    cursor.execute("""
    SELECT telegram_id
    FROM employees
    WHERE id = ?
    """, (
        employee_id,
    ))

    user = cursor.fetchone()

    # ACTIVE VEHICLE
    cursor.execute("""
    SELECT

        v.type,
        v.number

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    WHERE
        vu.employee_id = ?
        AND vu.end_time IS NULL
    """, (
        employee_id,
    ))

    active_vehicle = cursor.fetchone()

    conn.close()

    # NOTIFY USER
    if user and user[0]:

        try:

            if active_vehicle:

                vehicle_type = active_vehicle[0]

                vehicle_number = active_vehicle[1]

                notify_text = (
                    f"🚫 Ваш доступ до техніки "
                    f"заблоковано\n\n"

                    f"📝 Причина:\n"
                    f"{reason}\n\n"

                    f"🚜 Активна техніка:\n"
                    f"{vehicle_type} №{vehicle_number}\n\n"

                    f"⚠️ Негайно припиніть "
                    f"користування технікою\n"
                    f"та здайте її механіку.\n\n"

                    f"👤 Адміністратор:\n"
                    f"{admin_name}"
                )

            else:

                notify_text = (
                    f"🚫 Ваш доступ до техніки "
                    f"заблоковано\n\n"

                    f"📝 Причина:\n"
                    f"{reason}\n\n"

                    f"👤 Адміністратор:\n"
                    f"{admin_name}"
                )

            await message.bot.send_message(
                user[0],
                notify_text
            )

        except:

            pass

    await state.clear()

    await message.answer(
        f"✅ Користувача заблоковано\n\n"
        f"👤 {full_name}\n\n"
        f"📝 Причина:\n"
        f"{reason}",
        reply_markup=ban_menu
    )









