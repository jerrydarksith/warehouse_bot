
from aiogram import (
    Router,
    F
)

from aiogram.filters import (
    Command
)

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from handlers.admin import (
    get_admin_menu
)

from utils.roles import (
    get_user_role
)

from datetime import (
    datetime,
    timedelta
)

from aiogram.fsm.state import (
    State,
    StatesGroup
)

from aiogram.fsm.context import (
    FSMContext
)

import sqlite3


router = Router()

# -------------------------
# STATES
# -------------------------

class LogState(StatesGroup):

    waiting_clean_confirm = State()



# -------------------------
# LOG MENU
# -------------------------

logs_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📜 Останні 100"
            )
        ],
        [
            KeyboardButton(
                text="📜 Останні 200"
            )
        ],
        [
            KeyboardButton(
                text="📜 Останні 500"
            )
        ],
        [
            KeyboardButton(
                text="🧹 Очистити > 3 днів"
            )
        ],
        [
            KeyboardButton(
                text="🧹 Очистити > 5 днів"
            )
        ],
        [
            KeyboardButton(
                text="⬅️ В адмін меню"
            )
        ]
    ],
    resize_keyboard=True
)


# -------------------------
# CONFIRM CLEAN MENU
# -------------------------

confirm_clean_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="✅ Так"
            )
        ],
        [
            KeyboardButton(
                text="❌ Ні"
            )
        ]
    ],
    resize_keyboard=True
)


# -------------------------
# OPEN LOGS MENU
# -------------------------

@router.message(
    F.text.startswith("📜 Логи")
)
async def open_logs_menu(
    message: Message
):

    role = get_user_role(
        message.from_user.id
    )

    if role not in [
        "admin",
        "super_admin"
    ]:

        await message.answer(
            "❌ Недостатньо прав"
        )

        return

    await message.answer(
        "📜 Меню логів",
        reply_markup=logs_menu
    )


# -------------------------
# SHOW LOGS
# -------------------------

async def show_logs(
    message: Message,
    limit: int
):

    try:

        with open(
            "system.log",
            "r",
            encoding="utf-8"
        ) as file:

            logs = file.readlines()

        last_logs = logs[-limit:]

        response = (
            f"📜 Останні {limit} логів\n\n"
        )

        for line in last_logs:

            response += line

        chunk_size = 3500

        for i in range(
            0,
            len(response),
            chunk_size
        ):

            await message.answer(
                response[i:i + chunk_size]
            )

    except FileNotFoundError:

        await message.answer(
            "❌ Файл логів не знайдено"
        )

# -------------------------
# LAST 100
# -------------------------

@router.message(
    F.text == "📜 Останні 100"
)
async def last_100_logs(
    message: Message
):

    await show_logs(
        message,
        100
    )


# -------------------------
# LAST 200
# -------------------------

@router.message(
    F.text == "📜 Останні 200"
)
async def last_200_logs(
    message: Message
):

    await show_logs(
        message,
        200
    )


# -------------------------
# LAST 500
# -------------------------

@router.message(
    F.text == "📜 Останні 500"
)
async def last_500_logs(
    message: Message
):

    await show_logs(
        message,
        500
    )



# -------------------------
# SUPER ADMIN MENU
# -------------------------

def get_super_admin_menu():

    try:

        with open(
            "system.log",
            "r",
            encoding="utf-8"
        ) as file:

            logs_count = len(
                file.readlines()
            )

    except:

        logs_count = 0
    
    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM employees
    WHERE telegram_id IS NOT NULL
    """)

    users_count = cursor.fetchone()[0]

    conn.close()


    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"👤 Користувачі ({users_count})"
                )
            ],
            [
                KeyboardButton(
                    text="🛡 Ролі"
                )
            ],
            # [
            #     KeyboardButton(
            #         text="🔨 Бани"
            #     )
            # ],
            [
                KeyboardButton(
                    text=f"📜 Логи ({logs_count})"
                )
            ],
            # [
            #     KeyboardButton(
            #         text="⚙️ Система"
            #     )
            # ],
            [
                KeyboardButton(
                    text="⬅️ Назад"
                )
            ]
        ],
        resize_keyboard=True
    )



# -------------------------
# SUPER COMMAND
# -------------------------

@router.message(
    Command("super")
)
async def super_command(
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
        "👑 Панель супер адміна",
        reply_markup=get_super_admin_menu()
    )


# -------------------------
# OPEN SUPER ADMIN
# -------------------------

@router.message(
    F.text == "👑 Супер адмін"
)
async def open_super_admin(
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
        "👑 Панель супер адміна",
        reply_markup=get_super_admin_menu()
    )


# -------------------------
# BACK
# -------------------------

@router.message(
    F.text == "⬅️ В адмін меню"
)
async def back_handler(
    message: Message
):

    await message.answer(
        "🛠 Адмін меню",
        reply_markup=get_admin_menu()
    )


# -------------------------
# CLEAN OLD LOGS
# -------------------------

def clean_old_logs(
    days: int
):

    try:

        with open(
            "system.log",
            "r",
            encoding="utf-8"
        ) as file:

            logs = file.readlines()

        cutoff_date = (
            datetime.now() -
            timedelta(days=days)
        )

        filtered_logs = []

        for line in logs:

            try:

                date_str = (
                    line
                    .split("]")[0]
                    .replace("[", "")
                )

                log_date = datetime.strptime(
                    date_str,
                    "%Y-%m-%d %H:%M:%S"
                )

                if log_date >= cutoff_date:

                    filtered_logs.append(
                        line
                    )

            except:

                continue

        with open(
            "system.log",
            "w",
            encoding="utf-8"
        ) as file:

            file.writelines(
                filtered_logs
            )

        return len(filtered_logs)

    except:

        return None



# -------------------------
# CLEAN > 3 DAYS
# -------------------------

@router.message(
    F.text == "🧹 Очистити > 3 днів"
)
async def clean_3_days(
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

    await state.update_data(
        clean_days=3
    )

    await state.set_state(
        LogState.waiting_clean_confirm
    )

    await message.answer(
        "⚠️ Видалити логи "
        "старші 3 днів?",
        reply_markup=confirm_clean_menu
    )


# -------------------------
# CLEAN > 5 DAYS
# -------------------------

@router.message(
    F.text == "🧹 Очистити > 5 днів"
)
async def clean_5_days(
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

    await state.update_data(
        clean_days=5
    )

    await state.set_state(
        LogState.waiting_clean_confirm
    )

    await message.answer(
        "⚠️ Видалити логи "
        "старші 5 днів?",
        reply_markup=confirm_clean_menu
    )


# -------------------------
# CONFIRM CLEAN
# -------------------------

@router.message(
    LogState.waiting_clean_confirm,
    F.text == "✅ Так"
)
async def confirm_clean_logs(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    days = data.get(
        "clean_days"
    )

    logs_left = clean_old_logs(
        days
    )

    await state.clear()

    await message.answer(
        f"🧹 Логи очищено\n\n"
        f"📅 Видалено записи "
        f"старші {days} днів\n\n"
        f"📜 Залишилось записів:\n"
        f"{logs_left}",
        reply_markup=get_super_admin_menu()
    )


# -------------------------
# CANCEL CLEAN
# -------------------------

@router.message(
    LogState.waiting_clean_confirm,
    F.text == "❌ Ні"
)
async def cancel_clean_logs(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "❌ Очистку скасовано",
        reply_markup=logs_menu
    )

