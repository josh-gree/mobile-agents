from datetime import date


def get_today() -> str:
    """
    Returns today's date as a string in YYYY-MM-DD format.

    Returns:
        str: Today's date in YYYY-MM-DD format
    """
    return date.today().isoformat()
