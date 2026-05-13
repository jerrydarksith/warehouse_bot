
import os
import asyncio
import subprocess

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler
)

from handlers.registration import (
    router as registration_router
)

from handlers.vehicles import (
    router as vehicles_router
)

from handlers.admin import (
    router as admin_router
)

from handlers.admin_active import (
    router as admin_active_router
)

from handlers.admin_bans import (
    router as admin_bans_router
)

from handlers.admin_automation import (
    router as admin_automation_router
)

from handlers.admin_service import (
    router as admin_service_router
)

from handlers.admin_vehicle_stats import (
    router as admin_vehicle_stats_router
)

from handlers.super_admin import (
    router as super_admin_router
)

from handlers.super_admin_users import (
    router as super_admin_users_router
)

from handlers.super_admin_roles import (
    router as super_admin_roles_router
)

from handlers.super_admin_bans import (
    router as super_admin_bans_router
)

from handlers.super_admin_logs import (
    router as super_admin_logs_router
)




# -------------------------
# ENV
# -------------------------

load_dotenv()

BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


# -------------------------
# BOT
# -------------------------

bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()

scheduler = AsyncIOScheduler()


# -------------------------
# ROUTERS
# -------------------------

dp.include_router(
    registration_router
)

dp.include_router(
    vehicles_router
)

dp.include_router(
    admin_router
)

dp.include_router(
    admin_active_router
)

dp.include_router(
    admin_bans_router
)

dp.include_router(
    admin_automation_router
)

dp.include_router(
    admin_service_router
)

dp.include_router(
    admin_vehicle_stats_router
)

dp.include_router(
    super_admin_router
)

dp.include_router(
    super_admin_users_router
)

dp.include_router(
    super_admin_roles_router
)

dp.include_router(
    super_admin_bans_router
)


dp.include_router(
    super_admin_logs_router
)




# -------------------------
# MAIN
# -------------------------

async def main():

    print(
        "Бот запущений"
    )

    # -------------------------
    # REMINDER 20:30
    # -------------------------

    scheduler.add_job(
        lambda: subprocess.run([
            "python3",
            "services/remind_unclosed.py"
        ]),
        "cron",
        hour=20,
        minute=30
    )

    # -------------------------
    # AUTO CLOSE 21:05
    # -------------------------

    scheduler.add_job(
        lambda: subprocess.run([
            "python3",
            "services/auto_close_vehicles.py"
        ]),
        "cron",
        hour=21,
        minute=5
    )

    scheduler.start()

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )

