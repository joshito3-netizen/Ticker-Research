#!/usr/bin/env python3
"""Lab 19 legend panel: one SEC fact set, three deterministic screens."""
import argparse, json, os, ssl, sys, urllib.error, urllib.request
from datetime import date
from pathlib import Path

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
GRAHAM_THRESHOLD = 2.0
TAGS = {
 "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"),
 "net_income": ("NetIncomeLoss",),
 "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
 "capital_spending": ("PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"),
 "equity": ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
 "liabilities": ("Liabilities",), "current_assets": ("AssetsCurrent",),
 "current_liabilities": ("LiabilitiesCurrent",),
}
FLOW = {"revenue", "net_income", "operating_cash_flow", "capital_spending"}

def _context():
    for path in ("/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
        if Path(path).is_file(): return ssl.create_default_context(cafile=path)
    return ssl.create_default_context()

def _fetch(url, agent):
    request = urllib.request.Request(url, headers={"User-Agent": agent, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30, context=_context()) as response: return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError) as exc: raise RuntimeError(f"SEC request failed for {url}: {exc}") from exc

def _duration(item):
    try: return (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days
    except (KeyError, TypeError, ValueError): return None

def _eligible(facts, tag, flow):
    items = facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD", [])
    result = []
    for item in items:
        if item.get("form") != "10-K" or not item.get("end") or item.get("val") is None: continue
        days = _duration(item)
        if flow and (days is None or not 300 <= days <= 400): continue
        if not flow and item.get("start"): continue
        result.append(item)
    return result

def _select(facts, key, end):
    for tag in TAGS[key]:
        candidates = [x for x in _eligible(facts, tag, key in FLOW) if x["end"] == end]
        if candidates:
            item = max(candidates, key=lambda x: (x.get("filed", ""), x.get("accn", "")))
            return float(item["val"]) / 1_000_000, tag
    return None, "not found"

def _ratio(a, b): return None if a is None or b in (None, 0) else a / b
def _all(values, predicate): return "not known" if any(v is None for v in values) else ("pass" if all(predicate(v) for v in values) else "fail")
def _growth(values): return "not known" if not values or values[0] is None or values[-1] is None else ("pass" if values[-1] > values[0] else "fail")

def compute_buffett_checks(rows):
    return {"ROE of 15% or more every year": _all([r["roe_percent"] for r in rows], lambda v: v >= 15),
            "Owner earnings positive every year": _all([r["owner_earnings"] for r in rows], lambda v: v > 0),
            "Owner earnings grew, first year to last": _growth([r["owner_earnings"] for r in rows])}

def compute_graham_checks(rows, threshold=GRAHAM_THRESHOLD):
    latest = rows[-1]["current_ratio"] if rows else None
    return {f"Current ratio of {threshold:.1f} or more, latest year": "not known" if latest is None else ("pass" if latest >= threshold else "fail"),
            "Net income positive every year": _all([r["net_income"] for r in rows], lambda v: v > 0),
            "Net income grew, first year to last": _growth([r["net_income"] for r in rows])}

def compute_burry_checks(rows):
    differences = [None if r["operating_cash_flow"] is None or r["net_income"] is None else r["operating_cash_flow"] - r["net_income"] for r in rows]
    latest = rows[-1]["liabilities_to_equity"] if rows else None
    return {"Operating cash flow at least net income every year": _all(differences, lambda v: v >= 0),
            "Liabilities no more than twice equity, latest year": "not known" if latest is None else ("pass" if latest <= 2 else "fail")}

def _verdict(checks):
    values = list(checks.values())
    return "watch" if "not known" in values else ("pass" if all(v == "pass" for v in values) else "fail")

def analyze_ticker(ticker, user_agent=None, graham_threshold=GRAHAM_THRESHOLD):
    ticker = ticker.upper().strip(); agent = (user_agent or os.environ.get("SEC_USER_AGENT", "")).strip()
    if not ticker: raise ValueError("Ticker is required")
    if not agent or "@" not in agent: raise ValueError("Set SEC_USER_AGENT to your real name and email")
    mapping = _fetch(TICKERS_URL, agent); match = next((x for x in mapping.values() if str(x.get("ticker", "")).upper() == ticker), None)
    if not match: raise ValueError(f"Ticker not found: {ticker}")
    cik = int(match["cik_str"]); facts = _fetch(FACTS_URL.format(cik=cik), agent)
    ends = set()
    for key in ("revenue", "net_income", "operating_cash_flow"):
        for tag in TAGS[key]: ends.update(x["end"] for x in _eligible(facts, tag, True))
    ends = sorted(ends)[-5:]
    if len(ends) < 5: raise RuntimeError(f"Only {len(ends)} eligible fiscal years")
    rows = []
    for end in ends:
        row = {"fiscal_year_end": end}
        for key in TAGS: row[key], row[f"{key}_tag"] = _select(facts, key, end)
        row["roe_percent"] = None if row["net_income"] is None or row["equity"] is None or row["equity"] <= 0 else 100 * row["net_income"] / row["equity"]
        row["owner_earnings"] = None if row["operating_cash_flow"] is None or row["capital_spending"] is None else row["operating_cash_flow"] - row["capital_spending"]
        row["current_ratio"] = _ratio(row["current_assets"], row["current_liabilities"])
        row["liabilities_to_equity"] = _ratio(row["liabilities"], row["equity"]); rows.append(row)
    checks = {"Buffett": compute_buffett_checks(rows), "Graham": compute_graham_checks(rows, graham_threshold), "Burry": compute_burry_checks(rows)}
    return {"ticker": ticker, "company": facts.get("entityName") or match.get("title"), "cik": f"{cik:010d}", "graham_threshold": graham_threshold, "rows": rows, "checks": checks, "verdicts": {k: _verdict(v) for k, v in checks.items()}}

def _money(v): return "not found" if v is None else (f"{v:,.0f}" if abs(v-round(v)) < .000001 else f"{v:,.1f}")
def _decimal(v): return "not known" if v is None else f"{v:.2f}"
def _percent(v): return "not known" if v is None else f"{v:.1f}%"

def render_report(a):
    lines = [f"{a['ticker']} — {a['company']}", "Data source: SEC EDGAR company facts; 10-K only", "Amounts: USD millions", "Buffett ROE threshold: 15%", f"Graham current-ratio threshold: {a['graham_threshold']:.1f}", "Burry liabilities/equity threshold: 2.0", ""]
    fields = (("Revenue","revenue",_money),("Net income","net_income",_money),("Operating cash flow","operating_cash_flow",_money),("Capital spending","capital_spending",_money),("Equity","equity",_money),("Liabilities","liabilities",_money),("Current assets","current_assets",_money),("Current liabilities","current_liabilities",_money),("ROE","roe_percent",_percent),("Owner earnings","owner_earnings",_money),("Current ratio","current_ratio",_decimal),("Liabilities / equity","liabilities_to_equity",_decimal))
    for row in a["rows"]:
        lines.append(f"Fiscal year end: {row['fiscal_year_end']}")
        for label,key,formatter in fields: lines.append(f"  {label}: {formatter(row[key])} | XBRL/formula: {row.get(key+'_tag', 'computed in code')}")
        lines.append("")
    for investor, checks in a["checks"].items():
        lines.append(f"{investor} verdict: {a['verdicts'][investor]}")
        lines.extend(f"  {label}: {result}" for label,result in checks.items())
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(); p.add_argument("ticker"); p.add_argument("--json",action="store_true"); p.add_argument("--graham-threshold",type=float,default=GRAHAM_THRESHOLD); p.add_argument("--user-agent"); args=p.parse_args()
    try: result=analyze_ticker(args.ticker,args.user_agent,args.graham_threshold)
    except (ValueError,RuntimeError) as exc: print(f"error: {exc}",file=sys.stderr); return 1
    print(json.dumps(result,indent=2) if args.json else render_report(result)); return 0

if __name__ == "__main__": raise SystemExit(main())
