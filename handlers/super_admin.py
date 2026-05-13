
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


router = Router()


# -------------------------
# SUPER ADMIN MENU
# -------------------------

super_admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="👤 Користувачі"
            )
        ],
        [
            KeyboardButton(
                text="🛡 Ролі"
            )
        ],
        [
            KeyboardButton(
                text="🔨 Бани"
            )
        ],
        [
            KeyboardButton(
                text="📜 Логи"
            )
        ],
        [
            KeyboardButton(
                text="⚙️ Система"
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
        reply_markup=super_admin_menu
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
        reply_markup=super_admin_menu
    )


# -------------------------
# BACK
# -------------------------

@router.message(
    F.text == "⬅️ Назад"
)
async def back_handler(
    message: Message
):

    await message.answer(
        "🛠 Адмін меню",
        reply_markup=get_admin_menu()
    )

