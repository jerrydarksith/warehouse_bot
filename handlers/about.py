
from aiogram import (
    Router,
    F
)

from aiogram.filters import (
    Command
)

from aiogram.types import (
    Message
)


router = Router()


@router.message(
    F.text == "/about"
)
async def about_handler(
    message: Message
):

    await message.answer(
        "ℹ️ EpicLift Bot\n\n"
        "Система обліку складської техніки\n\n"
        "📦 Функції:\n"
        "• Видача техніки\n"
        "• Повернення техніки\n"
        "• Контроль активної техніки\n"
        "• Журнал дій\n"
        "• Адміністрування\n\n"
        "🔖 Версія: 1.3\n"
        "🛠 Розробка: Internal Warehouse System\n"
        "📅 2026"
    )

