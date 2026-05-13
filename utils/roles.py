
import sqlite3


def get_user_role(
    telegram_id
):

    conn = sqlite3.connect(
        "warehouse.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT role
    FROM employees
    WHERE telegram_id = ?
    """, (
        telegram_id,
    ))

    result = cursor.fetchone()

    conn.close()

    if not result:

        return None

    return result[0]

