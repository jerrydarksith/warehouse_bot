
import sqlite3

from aiogram import (
    Router,
    F
)

from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
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
# MENU
# -------------------------

manual_menu = ReplyKeyboardMarkup(
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
# STATES
# -------------------------

class ManualRegistrationState(
    StatesGroup
):

    waiting_full_name = State()

    waiting_phone = State()

class DeleteManualUserState(
    StatesGroup
):

    waiting_search = State()

    waiting_select_user = State()



# -------------------------
# OPEN MANUAL REGISTRATION
# -------------------------

@router.message(
    F.text == "➕ Зареєструвати вручну"
)
async def open_manual_registration(
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
        ManualRegistrationState.waiting_full_name
    )

    await message.answer(
        "👤 Введіть повне ПІБ\n\n"
        "Приклад:\n"
        "Іваненко Іван Іванович",
        reply_markup=manual_menu
    )

# -------------------------
# OPEN DELETE MANUAL USER
# -------------------------

@router.message(
    F.text == "🗑 Видалити ручного користувача"
)
async def open_delete_manual_user(
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
        DeleteManualUserState.waiting_search
    )

    await message.answer(
        "🗑 Введіть ПІБ ручного користувача",
        reply_markup=manual_menu
    )


# -------------------------
# DELETE BACK TO SUPER
# -------------------------

@router.message(
    DeleteManualUserState.waiting_search,
    F.text == "⬅️ До супера"
)

@router.message(
    DeleteManualUserState.waiting_select_user,
    F.text == "⬅️ До супера"
)
async def delete_back_to_super(
    message: Message,
    state: FSMContext
):

    await state.clear()

    from handlers.super_admin import (
        get_super_admin_menu
    )

    await message.answer(
        "👑 Панель супер адміна",
        reply_markup=get_super_admin_menu()
    )


# -------------------------
# DELETE CANCEL
# -------------------------

@router.message(
    DeleteManualUserState.waiting_search,
    F.text == "❌ Скасувати"
)

@router.message(
    DeleteManualUserState.waiting_select_user,
    F.text == "❌ Скасувати"
)
async def delete_cancel(
    message: Message,
    state: FSMContext
):

    await state.clear()

    from handlers.super_admin_users import (
        get_users_menu
    )

    await message.answer(
        "❌ Видалення скасовано",
        reply_markup=get_users_menu()
    )


# -------------------------
# SEARCH MANUAL USER
# -------------------------

@router.message(
    DeleteManualUserState.waiting_search
)
async def search_manual_user(
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

    WHERE
        id >= 99000000
        AND full_name LIKE ?

    ORDER BY full_name
    """, (
        f"%{search_text}%",
    ))

    users = cursor.fetchall()

    conn.close()

    if not users:

        await message.answer(
            "❌ Ручних користувачів не знайдено",
            reply_markup=manual_menu
        )

        return

    keyboard = []

    for user in users:

        keyboard.append([
            KeyboardButton(
                text=user[1]
            )
        ])

    keyboard.append([
        KeyboardButton(
            text="❌ Скасувати"
        )
    ])

    users_keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await state.set_state(
        DeleteManualUserState.waiting_select_user
    )

    await message.answer(
        "🗑 Виберіть користувача",
        reply_markup=users_keyboard
    )


# -------------------------
# DELETE MANUAL USER
# -------------------------

@router.message(
    DeleteManualUserState.waiting_select_user
)
async def delete_manual_user(
    message: Message,
    state: FSMContext
):

    full_name = (
        message.text.strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # GET USER
    cursor.execute("""
    SELECT

        id,
        full_name

    FROM employees

    WHERE
        id >= 99000000
        AND full_name = ?
    """, (
        full_name,
    ))

    user = cursor.fetchone()

    if not user:

        conn.close()

        await message.answer(
            "❌ Ручного користувача не знайдено",
            reply_markup=manual_menu
        )

        return

    employee_id = user[0]

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

    if active_vehicle:

        conn.close()

        await message.answer(
            "❌ Користувач має "
            "активну техніку\n\n"
            "Спочатку потрібно "
            "здати техніку",
            reply_markup=manual_menu
        )

        return

    # DELETE USER
    cursor.execute("""
    DELETE FROM employees
    WHERE id = ?
    """, (
        employee_id,
    ))

    conn.commit()

    conn.close()

    log_event(
        f"MANUAL USER DELETED: "
        f"{full_name}"
    )

    await state.clear()

    from handlers.super_admin_users import (
        get_users_menu
    )

    await message.answer(
        f"🗑 Користувача видалено\n\n"
        f"👤 {full_name}",
        reply_markup=get_users_menu()
    )



# -------------------------
# BACK TO SUPER
# -------------------------

@router.message(
    ManualRegistrationState.waiting_full_name,
    F.text == "⬅️ До супера"
)

@router.message(
    ManualRegistrationState.waiting_phone,
    F.text == "⬅️ До супера"
)
async def back_to_super(
    message: Message,
    state: FSMContext
):

    await state.clear()

    from handlers.super_admin import (
        get_super_admin_menu
    )

    await message.answer(
        "👑 Панель супер адміна",
        reply_markup=get_super_admin_menu()
    )


# -------------------------
# CANCEL
# -------------------------

@router.message(
    ManualRegistrationState.waiting_full_name,
    F.text == "❌ Скасувати"
)

@router.message(
    ManualRegistrationState.waiting_phone,
    F.text == "❌ Скасувати"
)
async def cancel_manual_registration(
    message: Message,
    state: FSMContext
):

    await state.clear()

    from handlers.super_admin_users import (
        get_users_menu
    )

    await message.answer(
        "❌ Реєстрацію скасовано",
        reply_markup=get_users_menu()
    )


# -------------------------
# FULL NAME
# -------------------------

@router.message(
    ManualRegistrationState.waiting_full_name
)
async def manual_full_name(
    message: Message,
    state: FSMContext
):

    full_name = (
        message.text.strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # CHECK FULL NAME
    cursor.execute("""
    SELECT

        full_name,
        mobile_phone,
        telegram_id

    FROM employees

    WHERE full_name = ?
    """, (
        full_name,
    ))

    existing_user = cursor.fetchone()

    if existing_user:

        conn.close()

        await message.answer(
            f"❌ Користувач вже існує\n\n"
            f"👤 {existing_user[0]}\n"
            f"📱 {existing_user[1]}\n"
            f"🆔 {existing_user[2]}",
            reply_markup=manual_menu
        )

        return

    conn.close()

    await state.update_data(
        full_name=full_name
    )

    await state.set_state(
        ManualRegistrationState.waiting_phone
    )

    await message.answer(
        "📱 Введіть номер телефону\n\n"
        "Приклад:\n"
        "380961617242",
        reply_markup=manual_menu
    )


# -------------------------
# PHONE
# -------------------------

@router.message(
    ManualRegistrationState.waiting_phone
)
async def manual_phone(
    message: Message,
    state: FSMContext
):

    phone = (
        message.text.strip()
    )

    if (
        not phone.startswith("380")
        or
        not phone.isdigit()
        or
        len(phone) != 12
    ):

        await message.answer(
            "❌ Невірний формат номера",
            reply_markup=manual_menu
        )

        return

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # CHECK PHONE
    cursor.execute("""
    SELECT

        full_name,
        mobile_phone

    FROM employees

    WHERE mobile_phone = ?
    """, (
        phone,
    ))

    existing_phone = cursor.fetchone()

    if existing_phone:

        conn.close()

        await message.answer(
            f"❌ Телефон вже використовується\n\n"
            f"👤 {existing_phone[0]}\n"
            f"📱 {existing_phone[1]}",
            reply_markup=manual_menu
        )

        return

    # GET NEW MANUAL ID
    cursor.execute("""
    SELECT MAX(id)
    FROM employees
    WHERE id >= 99000000
    """)

    last_manual_id = cursor.fetchone()[0]

    if last_manual_id:

        new_id = last_manual_id + 1

    else:

        new_id = 99000001

    data = await state.get_data()

    full_name = data.get(
        "full_name"
    )

    # INSERT USER
    cursor.execute("""
    INSERT INTO employees (

        id,
        full_name,
        mobile_phone,
        role

    ) VALUES (?, ?, ?, ?)
    """, (
        new_id,
        full_name,
        phone,
        "user"
    ))

    conn.commit()

    conn.close()

    log_event(
        f"MANUAL USER REGISTERED: "
        f"{full_name} | {phone}"
    )

    await state.clear()

    from handlers.super_admin_users import (
        get_users_menu
    )

    await message.answer(
        f"✅ Користувача створено\n\n"
        f"🆔 {new_id}\n"
        f"👤 {full_name}\n"
        f"📱 {phone}",
        reply_markup=get_users_menu()
    )

