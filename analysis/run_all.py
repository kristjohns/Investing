"""Re-run the whole analysis in order:  python analysis/run_all.py [--skip-download]

1. fetch_public_data.py  - FX, S&P 500 (Shiller), CPI, 10y yield mirrors -> data/raw/
2. financials.py         - 10-year table, consistency checks, TTM
3. valuation.py          - multiples, DCF, reverse DCF, sensitivities
4. scenarios.py          - bull/base/bear, NOK translation, index comparison, buy-below prices
5. macro_fx.py           - USD/NOK, downturns, CPI vs growth
6. norway_tax.py         - after-tax illustration for a NOK investor
7. charts.py             - charts/*.png
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["fetch_public_data.py", "financials.py", "valuation.py", "scenarios.py", "macro_fx.py",
         "norway_tax.py", "charts.py"]

if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    skip = "--skip-download" in sys.argv
    for step in STEPS:
        if skip and step == "fetch_public_data.py":
            continue
        print(f"\n=== {step} ===")
        sys.argv = [step]
        try:
            runpy.run_path(str(HERE / step), run_name="__main__")
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise
