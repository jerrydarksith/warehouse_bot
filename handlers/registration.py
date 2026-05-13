import sqlite3

from aiogram import Router, F
from aiogram.filters import Command

from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from aiogram.fsm.state import (
    State,
    StatesGroup
)

from aiogram.fsm.context import FSMContext


from utils.logger import (
    log_event
)


router = Router()


# -------------------------
# STATES
# -------------------------

class RegistrationState(StatesGroup):

    waiting_manual_phone = State()

    waiting_full_name = State()


# -------------------------
# HELPERS
# -------------------------

def mask_phone(phone):

    return (
        phone[:5]
        + "*****"
        + phone[-2:]
    )


def get_main_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📦 Отримати техніку"
                )
            ],
            [
                KeyboardButton(
                    text="📤 Здати техніку"
                )
            ],
            [
                KeyboardButton(
                    text="🚜 Моя техніка"
                )
            ]
        ],
        resize_keyboard=True
    )




# -------------------------
# START
# -------------------------

@router.message(Command("start"))
async def start_handler(
    message: Message,
    state: FSMContext
):

    # Скидання state
    await state.clear()

    # SQLITE
    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # Пошук користувача
    cursor.execute("""
    SELECT full_name, role
    FROM employees
    WHERE telegram_id = ?
    """, (
        message.from_user.id,
    ))

    employee = cursor.fetchone()

    # Якщо зареєстрований
    if employee:

        full_name = employee[0]

        role = employee[1]

        # DEFAULT
        role_text = "Користувач"

        commands = "/start"

        # SUPER ADMIN
        if role == "super_admin":

            role_text = (
                "👑 Супер адміністратор"
            )

            commands = (
                "/start\n"
                "/admin\n"
                "/super"
            )

        # ADMIN
        elif role == "admin":

            role_text = (
                "🛠 Адміністратор"
            )

            commands = (
                "/start\n"
                "/admin"
            )

        # MECHANIC
        elif role == "mechanic":

            role_text = (
                "🔧 Механік"
            )

            commands = (
                "/start\n"
                "/admin"
            )

        await message.answer(
            f"👋 Вітаємо\n\n"
            f"{full_name}\n\n"
            f"🛡 Ваша роль:\n"
            f"{role_text}\n\n"
            f"📌 Робочі команди:\n"
            f"{commands}",
            reply_markup=get_main_menu()
        )

        log_event(
            f"MENU OPENED: {full_name}"
        )

    else:

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📱 Поділитися номером",
                        request_contact=True
                    )
                ]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "Для реєстрації "
            "поділіться номером телефону",
            reply_markup=keyboard
        )

        log_event(
            "REGISTRATION STARTED"
        )

    conn.close()






# -------------------------
# CONTACT
# -------------------------

@router.message(F.contact)
async def contact_handler(
    message: Message,
    state: FSMContext
):

    # Захист від чужих контактів
    if message.contact.user_id != message.from_user.id:

        await message.answer(
            "Надішліть власний номер телефону"
        )

        return

    # Телефон із Telegram
    phone = message.contact.phone_number

    # Нормалізація
    phone = (
        phone
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    log_event(f"PHONE: {phone}")

    # Зберігаємо в state
    await state.update_data(
        telegram_phone=phone
    )

    # SQLITE
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()

    # Пошук працівника
    cursor.execute("""
    SELECT id, full_name, telegram_id
    FROM employees
    WHERE mobile_phone = ?
    """, (phone,))

    employee = cursor.fetchone()

    # Якщо знайдений
    if employee:

        employee_id = employee[0]
        full_name = employee[1]
        existing_telegram_id = employee[2]

        # Уже зареєстрований
        if existing_telegram_id is not None:

            masked_phone = mask_phone(phone)

            await message.answer(
                f"❌ Працівник уже зареєстрований\n\n"
                f"{full_name}\n"
                f"Номер: {masked_phone}\n\n"
                f"Будь ласка, скористайтесь "
                f"Telegram акаунтом "
                f"із цього номера телефону"
            )

            log_event(
                f"REGISTER BLOCKED: {full_name}"
            )

        else:

            # UPDATE telegram_id
            cursor.execute("""
            UPDATE employees
            SET telegram_id = ?
            WHERE id = ?
            """, (
                message.from_user.id,
                employee_id
            ))

            conn.commit()

            await message.answer(
                f"✅ Реєстрація успішна\n\n"
                f"{full_name}",
                reply_markup=get_main_menu()
            )

            log_event(
                f"REGISTERED: {full_name}"
            )

    else:

        await state.set_state(
            RegistrationState.waiting_manual_phone
        )

        await message.answer(
            "❌ Ваш номер не знайдено в базі\n\n"
            "Будь ласка, введіть номер телефону, "
            "який ви вказували при працевлаштуванні\n\n"
            "Формат:\n"
            "380XXXXXXXXX"
        )

        log_event("PHONE NOT FOUND")

    conn.close()


# -------------------------
# MANUAL PHONE
# -------------------------

@router.message(
    RegistrationState.waiting_manual_phone
)
async def manual_phone_handler(
    message: Message,
    state: FSMContext
):

    phone = message.text.strip()

    # Нормалізація
    phone = (
        phone
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    log_event(f"MANUAL PHONE: {phone}")

    # Зберігаємо в state
    await state.update_data(
        manual_phone=phone
    )

    # SQLITE
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()

    # Пошук
    cursor.execute("""
    SELECT id, full_name, telegram_id
    FROM employees
    WHERE mobile_phone = ?
    """, (phone,))

    employee = cursor.fetchone()

    # Якщо знайдений
    if employee:

        employee_id = employee[0]
        full_name = employee[1]
        existing_telegram_id = employee[2]

        # Уже зареєстрований
        if existing_telegram_id is not None:

            masked_phone = mask_phone(phone)

            await message.answer(
                f"❌ Працівник уже зареєстрований\n\n"
                f"{full_name}\n"
                f"Номер: {masked_phone}\n\n"
                f"Будь ласка, скористайтесь "
                f"Telegram акаунтом "
                f"із цього номера телефону"
            )

            log_event(
                f"MANUAL REGISTER BLOCKED: {full_name}"
            )

        else:

            # UPDATE telegram_id
            cursor.execute("""
            UPDATE employees
            SET telegram_id = ?
            WHERE id = ?
            """, (
                message.from_user.id,
                employee_id
            ))

            conn.commit()

            await message.answer(
                f"✅ Реєстрація успішна\n\n"
                f"{full_name}",
                reply_markup=get_main_menu()
            )

            log_event(
                f"MANUAL REGISTERED: {full_name}"
            )

    else:

        await state.set_state(
            RegistrationState.waiting_full_name
        )

        await message.answer(
            "❌ Працівника не знайдено\n\n"
            "Введіть ПОВНЕ прізвище, ім'я "
            "та по батькові\n\n"
            "Наприклад:\n"
            "Іванов Іван Іванович\n\n"
            "⚠️ Важливо:\n"
            "Якщо в компанії є однофамільці,\n"
            "неповне ім'я може прив'язати "
            "вас до чужого акаунта"
        )

        log_event("MANUAL PHONE NOT FOUND")

    conn.close()


# -------------------------
# FULL NAME
# -------------------------

@router.message(
    RegistrationState.waiting_full_name
)
async def full_name_handler(
    message: Message,
    state: FSMContext
):

    search_name = (
        message.text
        .strip()
    )

    log_event(f"FULL NAME SEARCH: {search_name}")

    # Зберігаємо в state
    await state.update_data(
        full_name=search_name
    )

    # SQLITE
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()

    # Пошук
    cursor.execute("""
    SELECT id, full_name, mobile_phone, telegram_id
    FROM employees
    WHERE full_name LIKE ?
    """, (
        f"%{search_name}%",
    ))

    employee = cursor.fetchone()

    # Якщо знайдений
    if employee:

        employee_id = employee[0]
        full_name = employee[1]
        mobile_phone = employee[2]
        existing_telegram_id = employee[3]

        # Уже зареєстрований
        if existing_telegram_id is not None:

            masked_phone = mask_phone(
                mobile_phone
            )

            await message.answer(
                f"❌ Працівник уже зареєстрований\n\n"
                f"{full_name}\n"
                f"Номер: {masked_phone}\n\n"
                f"Будь ласка, скористайтесь "
                f"Telegram акаунтом "
                f"із цього номера телефону"
            )

            log_event(
                f"FULLNAME REGISTER BLOCKED: {full_name}"
            )

        else:

            # UPDATE telegram_id
            cursor.execute("""
            UPDATE employees
            SET telegram_id = ?
            WHERE id = ?
            """, (
                message.from_user.id,
                employee_id
            ))

            conn.commit()

            await message.answer(
                f"✅ Реєстрація успішна\n\n"
                f"{full_name}",
                reply_markup=get_main_menu()
            )

            log_event(
                f"FULLNAME REGISTERED: {full_name}"
            )

    else:

        # Дані зі state
        data = await state.get_data()

        telegram_phone = data.get(
            "telegram_phone"
        )

        manual_phone = data.get(
            "manual_phone"
        )

        full_name = data.get(
            "full_name"
        )

        # LOG ATTEMPT
        cursor.execute("""
        INSERT INTO registration_attempts (
            telegram_user_id,
            telegram_phone,
            manual_phone,
            full_name
        )
        VALUES (?, ?, ?, ?)
        """, (
            message.from_user.id,
            telegram_phone,
            manual_phone,
            full_name
        ))

        conn.commit()

        await message.answer(
            "❌ Працівника не знайдено\n\n"
            "Схоже, реєстрація не пройшла "
            "жодним із доступних способів\n\n"
            "Ваші спроби збережені в системі\n\n"
            "Будь ласка, зверніться "
            "до адміністратора або механіка\n\n"
            "Для повторної спроби:\n"
            "/start"
        )

        log_event("FULL NAME NOT FOUND")

    conn.close()

    await state.clear()