import sqlite3
from datetime import datetime

from aiogram import Router, F

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

class VehicleState(StatesGroup):

    waiting_category = State()

    waiting_vehicle_type = State()

    waiting_vehicle_number = State()


class ReturnVehicleState(StatesGroup):

    waiting_mileage = State()


# -------------------------
# MAIN MENU
# -------------------------

main_menu = ReplyKeyboardMarkup(
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
# GET VEHICLE
# -------------------------

@router.message(
    F.text == "📦 Отримати техніку"
)
async def get_vehicle(
    message: Message,
    state: FSMContext
):

    keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Електровізок"
            )
        ],
        [
            KeyboardButton(
                text="Штаб"
            )
        ],
        [
            KeyboardButton(
                text="Навантажувач"
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


    await state.set_state(
        VehicleState.waiting_category
    )

    await message.answer(
        "Оберіть категорію техніки",
        reply_markup=keyboard
    )


# -------------------------
# CATEGORY
# -------------------------

@router.message(
    VehicleState.waiting_category
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
            "🏠 Головне меню",
            reply_markup=main_menu
        )
        return


    log_event(
        f"CATEGORY: {category}"
    )

    # ШТАБ
    if category == "Штаб":

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="штаб"
                    )
                ],
                [
                    KeyboardButton(
                        text="штаб_vna"
                    )
                ],
                [ KeyboardButton( 
                    text="⬅️ Назад" ) 
                ]
            ],
            resize_keyboard=True
        )

    # ЕЛЕКТРОВІЗОК
    elif category == "Електровізок":

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="лебідь"
                    )
                ],
                [
                    KeyboardButton(
                        text="лебідь_довгий"
                    )
                ],
                [
                    KeyboardButton(
                        text="лебідь_вага"
                    )
                ],
                [ KeyboardButton( 
                    text="⬅️ Назад" ) 
                ]
            ],
            resize_keyboard=True
        )

    # НАВАНТАЖУВАЧ
    elif category == "Навантажувач":

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="електричка"
                    )
                ],
                [
                    KeyboardButton(
                        text="бичок"
                    )
                ],
                [
                    KeyboardButton(
                        text="хеллі"
                    )
                ],
                [ KeyboardButton( 
                    text="⬅️ Назад" ) 
                ]
            ],
            resize_keyboard=True
        )

    else:

        await message.answer(
            "❌ Невідома категорія",
            reply_markup=main_menu
        )

        return

    await state.set_state(
        VehicleState.waiting_vehicle_type
    )

    await message.answer(
        "Оберіть тип техніки",
        reply_markup=keyboard
    )


# -------------------------
# VEHICLE TYPE
# -------------------------

@router.message(
    VehicleState.waiting_vehicle_type
)
async def vehicle_type_handler(
    message: Message,
    state: FSMContext
):

    vehicle_type = message.text
    if vehicle_type == "⬅️ Назад":

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Електровізок"
                    )
                ],
                [
                    KeyboardButton(
                        text="Штаб"
                    )
                ],
                [
                    KeyboardButton(
                        text="Навантажувач"
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

        await state.set_state(
            VehicleState.waiting_category
        )

        await message.answer(
            "Оберіть категорію техніки",
            reply_markup=keyboard
        )

        return

    log_event(
        f"TYPE SELECTED: {vehicle_type}"
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, number
    FROM vehicles
    WHERE
        type = ?
        AND status = 'вільний'
    """, (
        vehicle_type,
    ))

    vehicles = cursor.fetchall()

    if not vehicles:

        await message.answer(
            "❌ Вільної техніки немає",
            reply_markup=main_menu
        )

        conn.close()

        await state.clear()

        return

    keyboard_rows = []
    
    keyboard_rows.append([
    KeyboardButton(
        text="⬅️ Назад"
    )
])


    for vehicle in vehicles:

        vehicle_number = vehicle[1]

        keyboard_rows.append([
            KeyboardButton(
                text=f"{vehicle_type} №{vehicle_number}"
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
        VehicleState.waiting_vehicle_number
    )

    await message.answer(
        "Оберіть техніку",
        reply_markup=keyboard
    )

    conn.close()


# -------------------------
# VEHICLE NUMBER
# -------------------------

@router.message(
    VehicleState.waiting_vehicle_number
)
async def vehicle_number_handler(
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

        # ШТАБ
        if vehicle_type in [
            "штаб",
            "штаб_vna"
        ]:

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="штаб"
                        )
                    ],
                    [
                        KeyboardButton(
                            text="штаб_vna"
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

        # ЕЛЕКТРОВІЗОК
        elif vehicle_type in [
            "лебідь",
            "лебідь_довгий",
            "лебідь_вага"
        ]:

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="лебідь"
                        )
                    ],
                    [
                        KeyboardButton(
                            text="лебідь_довгий"
                        )
                    ],
                    [
                        KeyboardButton(
                            text="лебідь_вага"
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

        # НАВАНТАЖУВАЧ
        else:

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="електричка"
                        )
                    ],
                    [
                        KeyboardButton(
                            text="бичок"
                        )
                    ],
                    [
                        KeyboardButton(
                            text="хеллі"
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

        await state.set_state(
            VehicleState.waiting_vehicle_type
        )

        await message.answer(
            "Оберіть тип техніки",
            reply_markup=keyboard
        )

        return

    log_event(
        f"VEHICLE SELECTED: {selected_vehicle}"
    )

    data = await state.get_data()

    vehicle_type = data.get(
        "vehicle_type"
    )

    vehicle_number = (
        selected_vehicle
        .split("№")[1]
        .strip()
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # Техніка
    cursor.execute("""
    SELECT id, current_mileage
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
            "❌ Техніку не знайдено",
            reply_markup=main_menu
        )

        conn.close()

        await state.clear()

        return

    vehicle_id = vehicle[0]

    current_vehicle_mileage = vehicle[1]

    # Працівник
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
            "❌ Працівника не знайдено",
            reply_markup=main_menu
        )

        conn.close()

        await state.clear()

        return

    employee_id = employee[0]


    # -------------------------
    # ISSUE ENABLE CHECK
    # -------------------------

    cursor.execute("""
    SELECT value
    FROM settings
    WHERE key = 'vehicle_issue_enabled'
    """)

    issue_status = cursor.fetchone()

    if issue_status:

        if issue_status[0] != "true":

            await message.answer(
                "❌ Видача техніки зараз закрита",
                reply_markup=main_menu
            )

            conn.close()

            await state.clear()

            return


    # -------------------------
    # BAN CHECK
    # -------------------------

    cursor.execute("""
    SELECT id
    FROM user_bans
    WHERE
        employee_id = ?
        AND active = 1
    """, (
        employee_id,
    ))

    active_ban = cursor.fetchone()

    if active_ban:

        await message.answer(
            "⛔ Вам тимчасово заблоковано "
            "отримання техніки\n\n"
            "Будь ласка, зверніться "
            "до адміністратора або механіка",
            reply_markup=main_menu
        )

        conn.close()

        await state.clear()

        return


    # -------------------------
    # ACTIVE VEHICLE CHECK
    # -------------------------

    cursor.execute("""
    SELECT id
    FROM vehicle_usage
    WHERE
        employee_id = ?
        AND end_time IS NULL
    """, (
        employee_id,
    ))

    active_vehicle = cursor.fetchone()

    if active_vehicle:

        await message.answer(
            "❌ У вас уже є активна техніка\n\n"
            "Будь ласка, здайте попередню техніку",
            reply_markup=main_menu
        )

        conn.close()

        await state.clear()

        return


    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # -------------------------
    # INSERT USAGE
    # -------------------------

    cursor.execute("""
    INSERT INTO vehicle_usage (

        vehicle_id,
        employee_id,
        start_time,
        start_mileage

    )

    VALUES (

        ?,
        ?,
        ?,
        ?

    )
    """, (
        vehicle_id,
        employee_id,
        current_time,
        current_vehicle_mileage
    ))


    # -------------------------
    # UPDATE VEHICLE STATUS
    # -------------------------

    cursor.execute("""
    UPDATE vehicles
    SET status = 'зайнятий'
    WHERE id = ?
    """, (
        vehicle_id,
    ))

    conn.commit()


    await message.answer(
        f"✅ Техніку видано\n\n"
        f"🚜 {vehicle_type} №{vehicle_number}\n\n"
        f"🔧 Поточні мотогодини:\n"
        f"{current_vehicle_mileage}",
        reply_markup=main_menu
    )

    log_event(
        f"VEHICLE ISSUED: "
        f"{vehicle_type} №{vehicle_number}"
    )

    conn.close()

    await state.clear()

# -------------------------
# RETURN VEHICLE
# -------------------------

@router.message(
    F.text == "📤 Здати техніку"
)
async def return_vehicle(
    message: Message,
    state: FSMContext
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    # Працівник
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
            "❌ Працівника не знайдено",
            reply_markup=main_menu
        )

        conn.close()

        return

    employee_id = employee[0]

    # Активна техніка
    cursor.execute("""
    SELECT
        vu.id,
        v.type,
        v.number,
        v.id,
        vu.start_mileage

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    WHERE
        vu.employee_id = ?
        AND vu.end_time IS NULL
    """, (
        employee_id,
    ))

    active_vehicle = cursor.fetchone()

    if not active_vehicle:

        await message.answer(
            "❌ У вас немає активної техніки",
            reply_markup=main_menu
        )

        conn.close()

        return

    usage_id = active_vehicle[0]

    vehicle_type = active_vehicle[1]

    vehicle_number = active_vehicle[2]

    vehicle_id = active_vehicle[3]

    start_mileage = active_vehicle[4]

    await state.update_data(
        usage_id=usage_id,
        vehicle_id=vehicle_id,
        start_mileage=start_mileage
    )

    await state.set_state(
        ReturnVehicleState.waiting_mileage
    )

    await message.answer(
        f"🚜 {vehicle_type} №{vehicle_number}\n\n"
        f"🔧 Стартові мотогодини:\n"
        f"{start_mileage}\n\n"
        f"Введіть кінцеві мотогодини"
    )

    conn.close()


# -------------------------
# RETURN MILEAGE
# -------------------------

@router.message(
    ReturnVehicleState.waiting_mileage
)
async def return_mileage_handler(
    message: Message,
    state: FSMContext
):

    mileage = message.text.strip()

    if not mileage.isdigit():

        await message.answer(
            "❌ Введіть число"
        )

        return

    end_mileage = int(mileage)

    data = await state.get_data()

    usage_id = data.get(
        "usage_id"
    )

    vehicle_id = data.get(
        "vehicle_id"
    )

    start_mileage = data.get(
        "start_mileage"
    )

    # Захист
    if end_mileage < start_mileage:

        await message.answer(
            "❌ Кінцеві мотогодини не можуть "
            "бути менші за стартові"
        )

        return

    total_mileage = (
        end_mileage - start_mileage
    )

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # UPDATE usage
    cursor.execute("""
    UPDATE vehicle_usage

    SET
        end_time = ?,
        end_mileage = ?,
        total_mileage = ?

    WHERE id = ?
    """, (
        current_time,
        end_mileage,
        total_mileage,
        usage_id
    ))

    # UPDATE vehicle
    cursor.execute("""
    UPDATE vehicles

    SET
        status = 'вільний',
        current_mileage = ?

    WHERE id = ?
    """, (
        end_mileage,
        vehicle_id
    ))

    conn.commit()

    await message.answer(
        f"✅ Техніку успішно здано\n\n"
        f"📈 Наїзд за зміну:\n"
        f"{total_mileage}",
        reply_markup=main_menu
    )

    log_event(
        f"VEHICLE RETURNED: "
        f"{vehicle_id}"
    )

    conn.close()

    await state.clear()


# -------------------------
# MY VEHICLE
# -------------------------

@router.message(
    F.text == "🚜 Моя техніка"
)
async def my_vehicle(
    message: Message
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

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
            "❌ Працівника не знайдено",
            reply_markup=main_menu
        )

        conn.close()

        return

    employee_id = employee[0]

    cursor.execute("""
    SELECT

        v.type,
        v.number,
        vu.start_time,
        vu.start_mileage

    FROM vehicle_usage vu

    JOIN vehicles v
    ON vu.vehicle_id = v.id

    WHERE
        vu.employee_id = ?
        AND vu.end_time IS NULL
    """, (
        employee_id,
    ))

    vehicle = cursor.fetchone()

    if not vehicle:

        await message.answer(
            "❌ У вас немає активної техніки",
            reply_markup=main_menu
        )

        conn.close()

        return

    vehicle_type = vehicle[0]

    vehicle_number = vehicle[1]

    start_time = vehicle[2]

    start_mileage = vehicle[3]

    await message.answer(
        f"🚜 Ваша техніка:\n\n"
        f"{vehicle_type} №{vehicle_number}\n\n"
        f"📅 Отримано:\n"
        f"{start_time}\n\n"
        f"🔧 Стартові мотогодини:\n"
        f"{start_mileage}",
        reply_markup=main_menu
    )

    conn.close()
