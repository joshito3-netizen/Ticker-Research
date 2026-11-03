"""Find numbers in a memo that were not printed by the SEC analysis script."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


NUMBER_PATTERN = re.compile(r"(?<![\w.])\$?-?\d[\d,]*(?:\.\d+)?%?")


def _canonical_number(token: str) -> tuple[Decimal, bool] | None:
    cleaned = token.replace("$", "").replace(",", "")
    is_percent = cleaned.endswith("%")
    if is_percent:
        cleaned = cleaned[:-1]
    try:
        return Decimal(cleaned), is_percent
    except InvalidOperation:
        return None


def find_unprinted_numbers(memo: str, script_output: str) -> list[str]:
    allowed = {
        canonical
        for token in NUMBER_PATTERN.findall(script_output)
        if (canonical := _canonical_number(token)) is not None
    }
    flagged: list[str] = []
    for token in NUMBER_PATTERN.findall(memo):
        canonical = _canonical_number(token)
        if canonical not in allowed and token not in flagged:
            flagged.append(token)
    return flagged
