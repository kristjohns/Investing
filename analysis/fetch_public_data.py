"""Download the public datasets the analysis uses into analysis/data/raw/.

Default mode downloads machine-readable mirrors hosted on GitHub by datahub.io
(these are what the analysis in this repo was run on):
  * USD/NOK and other daily FX rates  - Federal Reserve H.10 via FRED (datasets/exchange-rates)
  * S&P 500 monthly price/earnings     - Robert Shiller's dataset (datasets/s-and-p-500)
  * US CPI-U monthly index             - BLS (datasets/cpi-us)
  * US 10-year Treasury yield monthly  - Federal Reserve (datasets/bond-yields-us-10y)

`--direct` additionally tries the primary publishers (FRED graph CSV and the
Norges Bank data API). Those hosts were blocked in the sandbox where this report
was produced, so that branch is provided for you to run locally; it is not
needed for the other scripts.

Usage:  python analysis/fetch_public_data.py [--direct]
"""
import argparse
import sys
import urllib.request

from common import RAW

MIRRORS = {
    "exchange_rates_daily.csv": "https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv",
    "shiller_sp500_monthly.csv": "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv",
    "cpi_us_monthly.csv": "https://raw.githubusercontent.com/datasets/cpi-us/main/data/cpiai.csv",
    "us_10y_yield_monthly.csv": "https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv",
}

DIRECT = {
    # FRED: NOK per USD (H.10 noon buying rate), daily
    "fred_DEXNOUS.csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXNOUS",
    # FRED: 10-year Treasury constant maturity, daily
    "fred_DGS10.csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
    # FRED: nominal personal consumption expenditures, monthly
    "fred_PCE.csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCE",
    # Norges Bank: USD/NOK business-day spot rate
    "norgesbank_USDNOK.csv": "https://data.norges-bank.no/api/data/EXR/B.USD.NOK.SP?format=csv&startPeriod=2000-01-01&locale=en",
}

HEADERS = {"User-Agent": "visa-report research script (personal use)"}


def download(url: str, dest) -> bool:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except Exception as exc:  # network policy, DNS, HTTP errors
        print(f"  FAILED {url}: {exc}")
        return False
    dest.write_bytes(data)
    print(f"  ok   {dest.name}  ({len(data):,} bytes)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct", action="store_true", help="also try FRED / Norges Bank directly")
    args = ap.parse_args()

    print("Downloading mirrors to", RAW)
    ok = all(download(url, RAW / name) for name, url in MIRRORS.items())
    if args.direct:
        print("Trying primary publishers (optional)")
        for name, url in DIRECT.items():
            download(url, RAW / name)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
