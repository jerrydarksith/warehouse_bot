
from aiogram import Router, F

from aiogram.types import (
    Message
)

from utils.roles import (
    get_user_role
)


router = Router()


# -------------------------
# LOGS
# -------------------------

@router.message(
    F.text == "📜 Логи"
)
async def logs_handler(
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

    try:

        with open(
            "system.log",
            "r",
            encoding="utf-8"
        ) as file:

            logs = file.readlines()

        # Останні 30 рядків
        last_logs = logs[-30:]

        response = (
            "📜 Системні логи\n\n"
        )

        for line in last_logs:

            response += line

        # Telegram limit safety
        if len(response) > 4000:

            response = response[-4000:]

        await message.answer(
            response
        )

    except FileNotFoundError:

        await message.answer(
            "❌ Файл логів не знайдено"
        )

