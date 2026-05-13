
from datetime import datetime


def log_event(
    text
):

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_line = (
        f"[{current_time}] {text}\n"
    )

    print(
        log_line
    )

    with open(
        "system.log",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            log_line
        )

