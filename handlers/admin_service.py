
import sqlite3

from aiogram import Router, F

from aiogram.filters import StateFilter



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

from handlers.admin import (
    get_admin_menu
)

from datetime import datetime



router = Router()


# -------------------------
# STATES
# -------------------------

class ServiceState(StatesGroup):

    waiting_category = State()

    waiting_vehicle_type = State()

    waiting_vehicle_number = State()

    waiting_action = State()

    waiting_comment = State()


# -------------------------
# GET SERVICE MENU
# -------------------------

def get_service_menu():

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # ШТАБИ
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE
        type IN (
            'штаб',
            'штаб_vna'
        )
        AND status = 'сервіс'
    """)

    stacks_count = cursor.fetchone()[0]

    # ЕЛЕКТРОВІЗКИ
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE
        type IN (
            'лебідь',
            'лебідь_довгий',
            'лебідь_вага'
        )
        AND status = 'сервіс'
    """)

    electric_count = cursor.fetchone()[0]

    # НАВАНТАЖУВАЧІ
    cursor.execute("""
    SELECT COUNT(*)
    FROM vehicles
    WHERE
        type IN (
            'електричка',
            'бичок',
            'хеллі'
        )
        AND status = 'сервіс'
    """)

    loader_count = cursor.fetchone()[0]

    conn.close()

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"🔧 Штаби ({stacks_count})"
                )
            ],
            [
                KeyboardButton(
                    text=f"🔧 Електровізки ({electric_count})"
                )
            ],
            [
                KeyboardButton(
                    text=f"🔧 Навантажувачі ({loader_count})"
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
# OPEN SERVICE MENU
# -------------------------

@router.message(
    F.text.startswith("🔧 Сервіс техніки")
)
async def open_service_menu(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ServiceState.waiting_category
    )

    await message.answer(
        "🔧 Сервіс техніки",
        reply_markup=get_service_menu()
    )


# -------------------------
# CATEGORY
# -------------------------

@router.message(
    ServiceState.waiting_category
)
async def category_handler(
    message: Message,
    state: FSMContext
):

    category = message.text

    # BACK
    if category == "⬅️ Назад":

        await state.clear()

        await message.answer(
            "🛠 Адмін меню",
            reply_markup=get_admin_menu()
        )

        return

    # ШТАБИ
    if category.startswith("🔧 Штаби"):

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="service_штаб"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_штаб_vna"
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

    # ЕЛЕКТРОВІЗКИ
    elif category.startswith("🔧 Електровізки"):

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="service_лебідь"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_лебідь_довгий"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_лебідь_вага"
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

    # НАВАНТАЖУВАЧІ
    elif category.startswith("🔧 Навантажувачі"):

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="service_електричка"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_бичок"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_хеллі"
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

    else:

        await message.answer(
            "❌ Невідома категорія",
            reply_markup=get_service_menu()
        )

        return

    await state.set_state(
        ServiceState.waiting_vehicle_type
    )

    await message.answer(
        "Оберіть тип техніки",
        reply_markup=keyboard
    )


# -------------------------
# VEHICLE TYPE
# -------------------------

@router.message(
    ServiceState.waiting_vehicle_type
)
async def vehicle_type_handler(
    message: Message,
    state: FSMContext
):

    vehicle_type = message.text

    # BACK
    if vehicle_type == "⬅️ Назад":

        await state.set_state(
            ServiceState.waiting_category
        )

        await message.answer(
            "🔧 Сервіс техніки",
            reply_markup=get_service_menu()
        )

        return

    vehicle_type = vehicle_type.replace(
        "service_",
        ""
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT

        id,
        number,
        status

    FROM vehicles

    WHERE type = ?

    ORDER BY number
    """, (
        vehicle_type,
    ))

    vehicles = cursor.fetchall()

    conn.close()

    if not vehicles:

        await message.answer(
            "❌ Техніку не знайдено"
        )

        return

    keyboard_rows = []

    for vehicle in vehicles:

        vehicle_number = vehicle[1]

        status = vehicle[2]

        status_icon = "🟢"

        if status == "зайнятий":

            status_icon = "🔴"

        elif status == "сервіс":

            status_icon = "🔧"

        keyboard_rows.append([
            KeyboardButton(
                text=(
                    f"{status_icon} "
                    f"{vehicle_type} "
                    f"№{vehicle_number}"
                )
            )
        ])

    keyboard_rows.append([
        KeyboardButton(
            text="⬅️ Назад"
        )
    ])

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

    await state.update_data(
        vehicle_type=vehicle_type
    )

    await state.set_state(
        ServiceState.waiting_vehicle_number
    )

    await message.answer(
        "Оберіть техніку",
        reply_markup=keyboard
    )


# -------------------------
# VEHICLE SELECT
# -------------------------

@router.message(
    StateFilter(ServiceState.waiting_vehicle_number)
)
async def vehicle_select_handler(
    message: Message,
    state: FSMContext
):

    selected_vehicle = message.text

    # BACK
    if selected_vehicle == "⬅️ Назад":

        data = await state.get_data()

        vehicle_type = data.get(
            "vehicle_type"
        )

        keyboard_rows = []

        # ШТАБИ
        if vehicle_type in [
            "штаб",
            "штаб_vna"
        ]:

            keyboard_rows = [
                [
                    KeyboardButton(
                        text="service_штаб"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_штаб_vna"
                    )
                ]
            ]

        # ЕЛЕКТРОВІЗКИ
        elif vehicle_type in [
            "лебідь",
            "лебідь_довгий",
            "лебідь_вага"
        ]:

            keyboard_rows = [
                [
                    KeyboardButton(
                        text="service_лебідь"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_лебідь_довгий"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_лебідь_вага"
                    )
                ]
            ]

        # НАВАНТАЖУВАЧІ
        else:

            keyboard_rows = [
                [
                    KeyboardButton(
                        text="service_електричка"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_бичок"
                    )
                ],
                [
                    KeyboardButton(
                        text="service_хеллі"
                    )
                ]
            ]

        keyboard_rows.append([
            KeyboardButton(
                text="⬅️ Назад"
            )
        ])

        keyboard = ReplyKeyboardMarkup(
            keyboard=keyboard_rows,
            resize_keyboard=True
        )

        await state.set_state(
            ServiceState.waiting_vehicle_type
        )

        await message.answer(
            "Оберіть тип техніки",
            reply_markup=keyboard
        )

        return

    service_action_menu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔧 В сервіс"
                )
            ],
            [
                KeyboardButton(
                    text="🟢 Повернути в роботу"
                )
            ],
            [
                KeyboardButton(
                    text="📜 Історія"
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

    await state.update_data(
        selected_vehicle=selected_vehicle
    )
    
    await state.set_state(
    ServiceState.waiting_action
    )

    await message.answer(
        f"🚜 Обрано:\n\n"
        f"{selected_vehicle}",
        reply_markup=service_action_menu
    )


# -------------------------
# SERVICE ACTION
# -------------------------

@router.message(
    StateFilter(ServiceState.waiting_action),
    F.text.in_([
        "🔧 В сервіс",
        "🟢 Повернути в роботу",
        "📜 Історія"
    ])
)
async def service_action_handler(
    message: Message,
    state: FSMContext
):

    action = message.text

    # HISTORY
    if action == "📜 Історія":

        data = await state.get_data()

        selected_vehicle = data.get(
            "selected_vehicle"
        )

        vehicle_number = (
            selected_vehicle
            .split("№")[1]
            .strip()
        )

        vehicle_type = (
            selected_vehicle
            .split("№")[0]
            .replace("🟢", "")
            .replace("🔴", "")
            .replace("🔧", "")
            .strip()
        )

        conn = sqlite3.connect(
            "warehouse.db"
        )

        cursor = conn.cursor()

        cursor.execute("""
        SELECT id
        FROM vehicles
        WHERE
            type = ?
            AND number = ?
        """, (
            vehicle_type,
            vehicle_number
        ))

        vehicle = cursor.fetchone()

        if not vehicle:

            await message.answer(
                "❌ Техніку не знайдено"
            )

            conn.close()

            return

        vehicle_id = vehicle[0]

        cursor.execute("""
        SELECT

            vsl.action,
            vsl.comment,
            vsl.created_at,
            e.full_name

        FROM vehicle_service_logs vsl
        LEFT JOIN employees e
        ON vsl.employee_id = e.id

        WHERE vsl.vehicle_id = ?

        ORDER BY vsl.created_at DESC
        """, (
            vehicle_id,
        ))

        logs = cursor.fetchall()

        conn.close()

        if not logs:

            await message.answer(
                "📭 Історія порожня"
            )

            return

        response = (
            f"📜 Історія\n\n"
        )

        for log in logs:

            log_action = log[0]

            comment = log[1]

            created_at = log[2]

            employee_name = log[3]

            response += (
                f"🔧 {log_action}\n"
                f"👤 {employee_name}\n"
                f"💬 {comment}\n"
                f"📅 {created_at}\n\n"
            )

        await message.answer(
            response
        )

        return

    await state.update_data(
        selected_action=action
    )

    await state.set_state(
        ServiceState.waiting_comment
    )

    await message.answer(
        "💬 Введіть коментар"
    )


# -------------------------
# SERVICE COMMENT
# -------------------------

@router.message(
    StateFilter(ServiceState.waiting_comment)
)
async def service_comment_handler(
    message: Message,
    state: FSMContext
):

    comment = message.text

    data = await state.get_data()

    selected_vehicle = data.get(
        "selected_vehicle"
    )

    selected_action = data.get(
        "selected_action"
    )

    vehicle_number = (
        selected_vehicle
        .split("№")[1]
        .strip()
    )

    vehicle_type = (
        selected_vehicle
        .split("№")[0]
        .replace("🟢", "")
        .replace("🔴", "")
        .replace("🔧", "")
        .strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # VEHICLE
    cursor.execute("""
    SELECT id
    FROM vehicles
    WHERE
        type = ?
        AND number = ?
    """, (
        vehicle_type,
        vehicle_number
    ))

    vehicle = cursor.fetchone()

    if not vehicle:

        await message.answer(
            "❌ Техніку не знайдено"
        )

        conn.close()

        return

    vehicle_id = vehicle[0]

    # EMPLOYEE
    cursor.execute("""
    SELECT id
    FROM employees
    WHERE telegram_id = ?
    """, (
        message.from_user.id,
    ))

    employee = cursor.fetchone()

    if not employee:

        await message.answer(
            "❌ Працівника не знайдено"
        )

        conn.close()

        return

    employee_id = employee[0]

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # SERVICE ON
    if selected_action == "🔧 В сервіс":

        cursor.execute("""
        UPDATE vehicles
        SET status = 'сервіс'
        WHERE id = ?
        """, (
            vehicle_id,
        ))

        action_name = "service_on"

    # SERVICE OFF
    else:

        cursor.execute("""
        UPDATE vehicles
        SET status = 'вільний'
        WHERE id = ?
        """, (
            vehicle_id,
        ))

        action_name = "service_off"

    # INSERT LOG
    cursor.execute("""
    INSERT INTO vehicle_service_logs (

        vehicle_id,
        employee_id,
        action,
        comment,
        created_at

    )

    VALUES (

        ?,
        ?,
        ?,
        ?,
        ?

    )
    """, (
        vehicle_id,
        employee_id,
        action_name,
        comment,
        current_time
    ))

    conn.commit()

    conn.close()

    await message.answer(
        "✅ Статус техніки оновлено",
        reply_markup=get_admin_menu()
    )

    await state.clear()

