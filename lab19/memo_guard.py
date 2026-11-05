"""Flag memo numbers that the deterministic panel report did not print."""
import re
from decimal import Decimal, InvalidOperation

NUMBER_PATTERN = re.compile(r"(?<![\w.])\$?-?\d[\d,]*(?:\.\d+)?%?")

def _number(token):
    cleaned = token.replace("$", "").replace(",", "")
    percent = cleaned.endswith("%")
    try:
        return Decimal(cleaned[:-1] if percent else cleaned), percent
    except InvalidOperation:
        return None

def find_unprinted_numbers(memos, report):
    allowed = {_number(token) for token in NUMBER_PATTERN.findall(report)}
    result = {}
    for investor, memo in memos.items():
        flagged = []
        for token in NUMBER_PATTERN.findall(memo):
            if _number(token) not in allowed and token not in flagged:
                flagged.append(token)
        result[investor] = flagged
    return result
