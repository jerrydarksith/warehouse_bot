
from aiogram import Router, F

from aiogram.types import (
    Message
)


router = Router()


@router.message(
    F.text == "👤 Користувачі"
)
async def users_menu(
    message: Message
):

    await message.answer(
        "👤 Управління користувачами"
    )
