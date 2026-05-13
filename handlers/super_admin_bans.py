
from aiogram import Router, F

from aiogram.types import (
    Message
)


router = Router()


@router.message(
    F.text == "🔨 Бани"
)
async def bans_menu(
    message: Message
):

    await message.answer(
        "🔨 Управління банами"
    )

