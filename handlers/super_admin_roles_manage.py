
import sqlite3

from aiogram import (
    Router,
    F
)

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from aiogram.fsm.state import (
    State,
    StatesGroup
)

from aiogram.fsm.context import (
    FSMContext
)

from utils.roles import (
    get_user_role
)

from utils.logger import (
    log_event
)


router = Router()


# -------------------------
# STATES
# -------------------------

class ChangeRoleState(
    StatesGroup
):

    waiting_search = State()

    waiting_select_user = State()

    waiting_select_role = State()


# -------------------------
# MENU
# -------------------------

roles_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="⬅️ До супера"
            )
        ],
        [
            KeyboardButton(
                text="❌ Скасувати"
            )
        ]
    ],
    resize_keyboard=True
)


# -------------------------
# OPEN ROLE MENU
# -------------------------

@router.message(
    F.text == "🛡 Ролі"
)
async def open_roles_menu(
    message: Message,
    state: FSMContext
):

    role = get_user_role(
        message.from_user.id
    )

    if role != "super_admin":

        await message.answer(
            "❌ Недостатньо прав"
        )

        return

    await state.clear()

    await state.set_state(
        ChangeRoleState.waiting_search
    )

    await message.answer(
        "👤 Введіть ПІБ користувача",
        reply_markup=roles_menu
    )


# -------------------------
# CANCEL
# -------------------------

@router.message(
    ChangeRoleState.waiting_search,
    F.text == "❌ Скасувати"
)

@router.message(
    ChangeRoleState.waiting_select_user,
    F.text == "❌ Скасувати"
)

@router.message(
    ChangeRoleState.waiting_select_role,
    F.text == "❌ Скасувати"
)
async def cancel_role_change(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "❌ Скасовано",
        reply_markup=roles_menu
    )


# -------------------------
# SEARCH USER
# -------------------------

@router.message(
    ChangeRoleState.waiting_search
)
async def search_role_user(
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
        full_name,
        role

    FROM employees

    WHERE full_name LIKE ?

    ORDER BY full_name
    """, (
        f"%{search_text}%",
    ))

    users = cursor.fetchall()

    conn.close()

    if not users:

        await message.answer(
            "❌ Користувачів не знайдено",
            reply_markup=roles_menu
        )

        return

    keyboard = []

    for user in users:

        keyboard.append([
            KeyboardButton(
                text=f"{user[1]} | {user[2]}"
            )
        ])

    keyboard.append([
        KeyboardButton(
            text="❌ Скасувати"
        )
    ])

    keyboard.append([
        KeyboardButton(
            text="⬅️ До супера"
        )
    ])

    users_keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await state.set_state(
        ChangeRoleState.waiting_select_user
    )

    await message.answer(
        "👤 Виберіть користувача",
        reply_markup=users_keyboard
    )


# -------------------------
# SELECT USER
# -------------------------

@router.message(
    ChangeRoleState.waiting_select_user
)
async def select_role_user(
    message: Message,
    state: FSMContext
):

    selected_text = (
        message.text.strip()
    )

    if "|" not in selected_text:

        await message.answer(
            "❌ Невірний формат"
        )

        return

    full_name = (
        selected_text
        .split("|")[0]
        .strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        id,
        full_name,
        role

    FROM employees

    WHERE full_name = ?
    """, (
        full_name,
    ))

    user = cursor.fetchone()

    conn.close()

    if not user:

        await message.answer(
            "❌ Користувача не знайдено"
        )

        return

    await state.update_data(
        employee_id=user[0],
        full_name=user[1]
    )

    role_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="👤 user"
                )
            ],
            [
                KeyboardButton(
                    text="🛠 admin"
                )
            ],
            [
                KeyboardButton(
                    text="👑 super_admin"
                )
            ],
            [
                KeyboardButton(
                    text="❌ Скасувати"
                )
            ],
            [
                KeyboardButton(
                    text="⬅️ До супера"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        ChangeRoleState.waiting_select_role
    )

    await message.answer(
        f"👤 {user[1]}\n\n"
        f"Поточна роль: {user[2]}\n\n"
        f"Виберіть нову роль",
        reply_markup=role_keyboard
    )


# -------------------------
# UPDATE ROLE
# -------------------------

@router.message(
    ChangeRoleState.waiting_select_role
)
async def update_role(
    message: Message,
    state: FSMContext
):

    role_map = {
        "👤 user": "user",
        "🛠 admin": "admin",
        "👑 super_admin": "super_admin"
    }

    selected_role = role_map.get(
        message.text
    )

    if not selected_role:

        await message.answer(
            "❌ Виберіть роль кнопкою"
        )

        return

    data = await state.get_data()

    employee_id = data.get(
        "employee_id"
    )

    full_name = data.get(
        "full_name"
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE employees
    SET role = ?
    WHERE id = ?
    """, (
        selected_role,
        employee_id
    ))

    conn.commit()

    conn.close()

    log_event(
        f"ROLE UPDATED: "
        f"{full_name} -> {selected_role}"
    )

    await state.clear()

    from handlers.super_admin import (
        get_super_admin_menu
    )

    await message.answer(
        f"✅ Роль оновлено\n\n"
        f"👤 {full_name}\n"
        f"🛡 {selected_role}",
        reply_markup=get_super_admin_menu()
    )

