
import sqlite3

from aiogram import Router, F

from aiogram.types import (
    Message
)

from handlers.admin import (
    get_admin_menu
)


router = Router()


# -------------------------
# VEHICLE STATS
# -------------------------

@router.message(
    F.text == "🚜 Стан техніки"
)
async def vehicle_stats(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # TOTAL
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    """)

    total_count = cursor.fetchone()[0]

    # FREE
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE status = 'вільний'
    """)

    free_count = cursor.fetchone()[0]

    # BUSY
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE status = 'зайнятий'
    """)

    busy_count = cursor.fetchone()[0]

    # SERVICE
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE status = 'сервіс'
    """)

    service_count = cursor.fetchone()[0]

    conn.close()

    response = (
        f"🚜 Стан техніки\n\n"

        f"📦 Всього техніки: "
        f"{total_count}\n\n"

        f"🟢 Вільні: "
        f"{free_count}\n"

        f"🔴 Видані: "
        f"{busy_count}\n"

        f"🔧 В ремонті: "
        f"{service_count}"
    )

    await message.answer(
        response,
        reply_markup=get_admin_menu()
    )

