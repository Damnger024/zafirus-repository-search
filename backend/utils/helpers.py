from datetime import datetime
import re


def calculate_days_inactive(last_update: str):

    last_update_date = datetime.strptime(
        last_update,
        "%Y-%m-%dT%H:%M:%SZ"
    )

    now = datetime.utcnow()

    days_inactive = (now - last_update_date).days

    return days_inactive

def tokenize_text(text: str):

    if not text:
        return []

    text = text.lower()

    tokens = re.findall(r'\b\w+\b', text)

    return tokens