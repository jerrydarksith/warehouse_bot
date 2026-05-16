
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
# USERS MENU
# -------------------------

def get_users_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📋 Активні користувачі"
                )
            ],
            [
                KeyboardButton(
                    text="♻️ Скинути реєстрацію"
                )
            ],
            [
                KeyboardButton(
                    text="➕ Зареєструвати вручну"
                )
            ],
            [ KeyboardButton( 
                text="🗑 Видалити ручного користувача" 
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



# -------------------------
# STATES
# -------------------------

class ResetRegistrationState(
    StatesGroup
):

    waiting_search = State()

    waiting_select_user = State()




@router.message(
    F.text.startswith("👤 Користувачі")
)
async def users_menu(
    message: Message
):

    role = get_user_role(
        message.from_user.id
    )

    if role != "super_admin":

        await message.answer(
            "❌ Недостатньо прав"
        )

        return

    await message.answer(
        "👤 Управління користувачами",
        reply_markup=get_users_menu()
    )





# -------------------------
# OPEN RESET REGISTRATION
# -------------------------

@router.message(
    F.text == "♻️ Скинути реєстрацію"
)

@router.message(
    ResetRegistrationState.waiting_search,
    F.text == "♻️ Скинути реєстрацію"
)

@router.message(
    ResetRegistrationState.waiting_select_user,
    F.text == "♻️ Скинути реєстрацію"
)



async def open_reset_registration(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ResetRegistrationState.waiting_search
    )

    await message.answer(
        "👤 Введіть прізвище "
        "або ім'я користувача"
    )



# -------------------------
# SEARCH USER
# -------------------------




@router.message(
    ResetRegistrationState.waiting_search
)



async def search_user(
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
        telegram_id

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
            "❌ Користувачів не знайдено"
        )

        return

    keyboard = []


    for user in users:

        full_name = user[1]

        telegram_id = user[2]

        if telegram_id:

            status = "🟢"

        else:

            status = "🔴"

        keyboard.append([
            KeyboardButton(
                text=f"{status} {full_name}"
            )
        ])



    keyboard.append([
        KeyboardButton(
            text="❌ Скасувати"
        )
    ])

    users_menu_keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await state.set_state(
        ResetRegistrationState.waiting_select_user
    )

    await message.answer(
        "👤 Виберіть користувача",
        reply_markup=users_menu_keyboard
    )



# -------------------------
# CANCEL
# -------------------------

@router.message(
    ResetRegistrationState.waiting_search,
    F.text == "❌ Скасувати"
)

@router.message(
    ResetRegistrationState.waiting_select_user,
    F.text == "❌ Скасувати"
)
async def cancel_reset(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "❌ Скасовано",
        reply_markup=get_users_menu()
    )




# -------------------------
# RESET REGISTRATION
# -------------------------



@router.message(
    ResetRegistrationState.waiting_select_user
)



async def reset_registration(
    message: Message,
    state: FSMContext
):


    full_name = (
        message.text
        .replace("🟢 ", "")
        .replace("🔴 ", "")
        .strip()
    )



    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # USER
    cursor.execute("""
    SELECT

        id,
        telegram_id

    FROM employees

    WHERE full_name = ?
    """, (
        full_name,
    ))

    user = cursor.fetchone()

    if not user:

        conn.close()

        await message.answer(
            "❌ Користувача не знайдено"
        )

        return

    employee_id = user[0]

    telegram_id = user[1]

    # ACTIVE VEHICLE
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
            "здати техніку"
        )

        return

    # RESET TELEGRAM
    cursor.execute("""
    UPDATE employees

    SET telegram_id = NULL

    WHERE id = ?
    """, (
        employee_id,
    ))

    conn.commit()

    conn.close()

    log_event(
        f"REGISTRATION RESET: "
        f"{full_name}"
    )

    await state.clear()

    await message.answer(
        f"✅ Реєстрацію скинуто\n\n"
        f"👤 {full_name}\n\n"
        f"📱 Telegram ID видалено",
        reply_markup=get_users_menu()
    )

# -------------------------
# BACK TO SUPER ADMIN
# -------------------------



@router.message(
    F.text == "⬅️ До супера"
)

@router.message(
    ResetRegistrationState.waiting_search,
    F.text == "⬅️ До супера"
)

@router.message(
    ResetRegistrationState.waiting_select_user,
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
# ACTIVE USERS
# -------------------------


@router.message(
    F.text == "📋 Активні користувачі"
)

@router.message(
    ResetRegistrationState.waiting_search,
    F.text == "📋 Активні користувачі"
)

@router.message(
    ResetRegistrationState.waiting_select_user,
    F.text == "📋 Активні користувачі"
)


async def active_users(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        full_name,
        mobile_phone,
        telegram_id

    FROM employees

    WHERE telegram_id IS NOT NULL

    ORDER BY full_name
    """)

    users = cursor.fetchall()

    conn.close()

    if not users:

        await message.answer(
            "❌ Активних користувачів немає"
        )

        return

    response = (
        "📋 Активні користувачі\n\n"
    )

    for user in users:

        full_name = user[0]

        phone = user[1]

        telegram_id = user[2]

        response += (
            f"👤 {full_name}\n"
            f"📱 {phone}\n"
            f"🆔 {telegram_id}\n\n"
        )

    chunk_size = 3500

    for i in range(
        0,
        len(response),
        chunk_size
    ):

        await message.answer(
            response[i:i + chunk_size]
        )

