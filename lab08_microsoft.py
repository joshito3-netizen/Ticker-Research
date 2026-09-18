"""Lab 08: Microsoft P/E comparison adapted from lab07_asbury.py.

AI disclosure: Codex generated this calculator and helped validate its outputs.
The student must review and understand the inputs, peer policy, and results.
"""

# Comparison date: 2026-09-09, per the student's revised September instruction.
# USD ordinary-common-share closing prices, not dividend-adjusted prices.
# Latest annual reported GAAP diluted EPS public by that date.
# Source URLs, publication dates, and qualifications: lab08-microsoft.md.
COMPARISON_DATE = "2026-09-09"
TARGET = {"ticker": "MSFT", "price": 491.65, "eps": 17.95,
          "fiscal_end": "2026-06-30", "published": "2026-07-29"}
PEERS = [
    {"ticker": "ORCL", "price": 161.63, "eps": 5.83,
     "fiscal_end": "2026-05-31", "published": "2026-06-10",
     "decision": "exclude"},
    {"ticker": "CRM", "price": 244.16, "eps": 7.80,
     "fiscal_end": "2026-01-31", "published": "2026-02-25",
     "decision": "qualify"},
]

from math import isfinite
from statistics import median


def positive(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and isfinite(value) and value > 0)


def ticker(row):
    return str(row.get("ticker") or "").strip().upper()


def multiple(row):
    if positive(row.get("price")) and positive(row.get("eps")):
        return row["price"] / row["eps"]
    return None


def main(target=TARGET, peers=PEERS):
    print("Lab 08 — Microsoft comparable-company P/E (AI-drafted peer policy)")
    print(f"Prices: {COMPARISON_DATE}; latest public annual GAAP diluted EPS.")
    print("USD per common share. No cash/debt bridge. Sources: lab08-microsoft.md")
    for row in peers:
        if row.get("decision") == "exclude":
            print(f"{ticker(row)}: excluded by peer policy; retained in source table.")
    peers = [row for row in peers if row.get("decision") in {"use", "qualify"}]
    for row in [target, *peers]:
        if row["published"] > COMPARISON_DATE:
            raise ValueError(f"{ticker(row)} earnings were not public by comparison date")
    print(f"Target {ticker(target)}: price={target.get('price')}, EPS={target.get('eps')}")
    target_pe = multiple(target)
    print("Target P/E: " + (f"{target_pe:.6f}×" if target_pe is not None
                            else "not meaningful (missing/nonpositive/nonfinite price or EPS)"))
    eps_ok = positive(target.get("eps"))
    if not eps_ok:
        print("All target implied prices: not meaningful (invalid target EPS).")
    if not positive(target.get("price")):
        print("Target market-price comparisons: not meaningful; EPS-based estimates remain possible.")

    seen, valid = set(), []
    for row in peers:
        symbol = ticker(row)
        if not symbol:
            print("Peer excluded: missing ticker.")
            continue
        if symbol == ticker(target):
            print(f"{symbol}: excluded target.")
            continue
        if symbol in seen:
            print(f"{symbol}: duplicate excluded (first occurrence retained).")
            continue
        seen.add(symbol)
        pe = multiple(row)
        print(f"{symbol}: price={row.get('price')}, EPS={row.get('eps')}")
        if pe is None:
            print("  P/E and implied price: not meaningful (invalid price or EPS).")
            continue
        valid.append((symbol, pe))
        implied = f"${pe * target['eps']:.2f}" if eps_ok else "not meaningful"
        print(f"  P/E: {pe:.6f}×; target implied price: {implied}")

    if not valid:
        print("No usable peers.")
        return
    values = [pe for _, pe in valid]
    mid = median(values)
    print(f"Peer median P/E: {mid:.6f}×")
    full = mid * target["eps"] if eps_ok else None
    if len(valid) == 1:
        print("One valid peer: reference estimate, no range.")
    else:
        print(f"Peer minimum/maximum P/E: {min(values):.6f}× / {max(values):.6f}×")
        if eps_ok:
            print(f"Target implied range: ${min(values) * target['eps']:.2f}–${max(values) * target['eps']:.2f}")
    print("Median-implied price: " + (f"${full:.2f}" if full is not None else "not meaningful"))
    print("Leave-one-peer-out (changes computed before rounding):")
    for removed, _ in valid:
        remaining = [pe for symbol, pe in valid if symbol != removed]
        if not remaining:
            print(f"  Remove {removed}: no estimate; no usable peers remain.")
        elif full is None:
            print(f"  Remove {removed}: price and change not meaningful (invalid target EPS).")
        else:
            estimate = median(remaining) * target["eps"]
            change = estimate - full
            label = "reference estimate, no range" if len(remaining) == 1 else "median estimate"
            print(f"  Remove {removed}: ${estimate:.2f}; change {'+' if change >= 0 else '-'}${abs(change):.2f}; {label}.")


if __name__ == "__main__":
    main()
# AI-assisted draft; no claim of independent student review.
