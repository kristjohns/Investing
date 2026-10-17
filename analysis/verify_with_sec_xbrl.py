"""OPTIONAL cross-check of the hand-compiled Visa figures against SEC XBRL data.

Why this exists: the sandbox that produced the report could not reach sec.gov, so
the annual figures in data/visa_annual.csv were transcribed from the filings via a
web-search tool (each row cites its filing). This script lets you re-verify them
against the SEC's machine-readable "companyfacts" API on a machine with normal
internet access. It was NOT executed in the sandbox (SEC was blocked there).

The SEC asks automated clients to identify themselves. Set an environment variable:
    export SEC_USER_AGENT="Your Name your.email@example.com"
then run:
    python analysis/verify_with_sec_xbrl.py

Output: a table of (fiscal year, metric, compiled value, XBRL value, % difference),
also saved to analysis/output/xbrl_crosscheck.csv. Differences can be legitimate
(e.g. later re-presentation of prior years, or trade-date vs cash buybacks).
"""
import json
import os
import sys
import urllib.request

import pandas as pd

from common import OUT, RAW, load_annual

CIK = "0001403161"
URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

# compiled metric -> candidate us-gaap tags (first one found is used)
TAGS = {
    "net_revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment"],
    "sbc": ["ShareBasedCompensation"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "total_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "long_term_debt": ["LongTermDebtNoncurrent"],
}
INSTANT = {"total_equity", "long_term_debt"}


def fetch() -> dict:
    cache = RAW / "sec_companyfacts_visa.json"
    if cache.exists():
        return json.loads(cache.read_text())
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        sys.exit("Set SEC_USER_AGENT (e.g. 'Your Name you@example.com') - the SEC requires it.")
    req = urllib.request.Request(URL, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    cache.write_bytes(data)
    return json.loads(data)


def annual_values(facts: dict, tag: str, instant: bool) -> dict:
    """Fiscal-year values (FY ends 30 Sep) from 10-K filings; latest filing wins."""
    node = facts.get("facts", {}).get("us-gaap", {}).get(tag)
    if not node:
        return {}
    rows = []
    for unit, items in node.get("units", {}).items():
        if unit != "USD":
            continue
        for it in items:
            if it.get("form") != "10-K":
                continue
            end = pd.Timestamp(it["end"])
            if end.month != 9:
                continue
            if not instant:
                start = pd.Timestamp(it.get("start", it["end"]))
                if not 350 <= (end - start).days <= 380:
                    continue
            rows.append((end.year, it["filed"], it["val"] / 1e6))
    out = {}
    for fy, filed, val in sorted(rows, key=lambda x: (x[0], x[1])):
        out[fy] = val  # later filings overwrite earlier ones
    return out


def main():
    facts = fetch()
    compiled = load_annual()
    recs = []
    for metric, tags in TAGS.items():
        for tag in tags:
            vals = annual_values(facts, tag, metric in INSTANT)
            if vals:
                break
        for fy, xval in vals.items():
            if fy in compiled.index and metric in compiled.columns and pd.notna(compiled.loc[fy, metric]):
                cval = compiled.loc[fy, metric]
                diff = (cval / abs(xval) - 1) * 100 if xval else float("nan")
                recs.append({"fiscal_year": fy, "metric": metric, "tag": tag, "compiled": cval,
                             "xbrl": abs(xval), "pct_diff": diff})
    df = pd.DataFrame(recs).sort_values(["metric", "fiscal_year"])
    df.to_csv(OUT / "xbrl_crosscheck.csv", index=False)
    flagged = df[df["pct_diff"].abs() > 0.5]
    print(df.to_string(index=False))
    print(f"\n{len(flagged)} of {len(df)} compiled figures differ from XBRL by more than 0.5%")


if __name__ == "__main__":
    main()
