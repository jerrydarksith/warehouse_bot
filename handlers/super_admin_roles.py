
from aiogram import Router, F

from aiogram.types import (
    Message
)


router = Router()


@router.message(
    F.text == "🛡 Ролі"
)
async def roles_menu(
    message: Message
):

    await message.answer(
        "🛡 Управління ролями"
    )

