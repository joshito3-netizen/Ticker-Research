"""Lab 07: frozen Asbury P/E comparison; standard library only.

AI disclosure: Codex generated this calculator and helped validate its outputs.
The student must review and understand the inputs, peer policy, and results.
"""

# Editable inputs: USD closing prices on 2024-12-31 and FY2024 total GAAP
# diluted EPS, reported subsequently. This is a retrospective training case.
TARGET = {"ticker": "ABG", "price": 243.03, "eps": 21.50}
PEERS = [
    {"ticker": "AN", "price": 169.84, "eps": 16.92},  # Use
    {"ticker": "GPI", "price": 421.48, "eps": 36.81},  # Qualify; included
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
    print("Lab 07 — Asbury comparable-company P/E")
    print("Prices: 2024-12-31; EPS: FY2024 total GAAP diluted, reported later.")
    print("Retrospective training comparison; USD per share. No cash/debt bridge.")
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
# AI disclosure and discretion statement: I used AI to help complete Lab 07,
# and I revised what I needed to.
