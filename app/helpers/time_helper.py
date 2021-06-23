from datetime import datetime, timedelta


def get_current_time() -> datetime:
    return datetime.utcnow() + timedelta(hours=7)
