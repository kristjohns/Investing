"""Numbers for the video, read from the analysis outputs (run analysis/run_all.py first).

Every chart value is loaded from analysis/output/*.csv or recomputed with the analysis
scripts' own functions. The few numbers the report does not state directly (EPS growth
decomposition, half-lives, doubling time, the 2.9% forward FCF yield, the bisection
steps, the price-return curve) are derived here and printed by `python video/data.py`.
Dated qualitative facts (regulation, competition, macro, Norwegian tax) are quoted in
the scene files exactly as they appear in visa_report.md and
analysis/data/qualitative_facts.csv.
"""
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
from common import OUT, load_usdnok_daily  # noqa: E402

YEARS = list(range(2015, 2026))


def _csv(name, **kw):
    return pd.read_csv(OUT / f"{name}.csv", **kw)


def _mixed(series):
    """Key/value tables mix numbers and dates in one column: convert what is numeric."""
    def conv(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return x
    return series.map(conv)


@lru_cache
def fin() -> pd.DataFrame:
    return _csv("financials_annual", index_col=0)


@lru_cache
def ttm() -> pd.Series:
    return _csv("ttm", index_col=0)["ttm_jun2026"]


@lru_cache
def growth() -> pd.DataFrame:
    return _csv("growth_summary", index_col=0)


@lru_cache
def dcf_summary() -> pd.Series:
    return _csv("dcf_base_summary", index_col=0)["base"]


@lru_cache
def dcf_years() -> pd.DataFrame:
    return _csv("dcf_base", index_col=0)


def _grid(name):
    g = _csv(name, index_col=0)
    g.columns = [float(c.rstrip("%")) / 100 for c in g.columns]
    g.index = [float(str(i).rstrip("%x")) / 100 for i in g.index]
    return g


def dcf_grid():           # rows: stage-1 growth, cols: discount rate -> value per share
    return _grid("dcf_sensitivity_growth_rate")


def dcf_terminal_grid():  # rows: terminal growth
    return _grid("dcf_sensitivity_terminal")


def dcf_margin_grid():    # rows: FCF-after-SBC margin
    return _grid("dcf_sensitivity_margin")


def return_grid_5y():     # rows: EPS CAGR, cols: exit P/E -> annualised return
    g = _csv("return_sensitivity_5y", index_col=0)
    g.columns = [float(c.rstrip("x")) for c in g.columns]
    g.index = [float(i.rstrip("%")) / 100 for i in g.index]
    return g


@lru_cache
def reverse() -> pd.DataFrame:
    return _csv("reverse_dcf")


@lru_cache
def scenarios() -> pd.DataFrame:
    return _csv("scenarios")


@lru_cache
def scenario_inputs() -> pd.Series:
    return _mixed(_csv("scenario_inputs", index_col=0)["value"])


@lru_cache
def buy_below() -> pd.DataFrame:
    return _csv("buy_below_prices")


@lru_cache
def history() -> pd.DataFrame:
    return _csv("valuation_history", index_col=0)


@lru_cache
def history_summary() -> pd.DataFrame:
    return _csv("valuation_history_summary", index_col=0)


@lru_cache
def multiples() -> pd.Series:
    return _csv("valuation_current_multiples", index_col=0)["visa"]


@lru_cache
def index_comparison() -> pd.DataFrame:
    return _csv("index_comparison")


@lru_cache
def downturns() -> pd.DataFrame:
    return _csv("downturns", index_col=0)


@lru_cache
def fx_drawdowns() -> pd.DataFrame:
    return _csv("fx_in_drawdowns", index_col=0)


@lru_cache
def fx_stats() -> pd.Series:
    return _mixed(_csv("usdnok_stats", index_col=0)["value"])


@lru_cache
def fx_corr() -> pd.Series:
    return _csv("fx_equity_correlation").iloc[0]


@lru_cache
def returns_usd_nok() -> pd.DataFrame:
    return _csv("returns_usd_vs_nok", index_col=0)


@lru_cache
def scenarios_nok() -> pd.DataFrame:
    return _csv("scenarios_nok")


@lru_cache
def after_tax() -> pd.DataFrame:
    return _csv("norway_after_tax_10y", index_col=0)


@lru_cache
def sizing() -> pd.DataFrame:
    return _csv("position_sizing")


def usdnok_monthly(start="2000-01-01") -> pd.Series:
    s = load_usdnok_daily()
    return s[s.index >= start].resample("MS").mean().dropna()


# ----------------------------------------------------------------------------- derived
def eps_decomposition():
    """Log-growth contributions to non-GAAP EPS growth, FY2015 -> FY2025 (per year)."""
    f = fin()
    n = 2025 - 2015
    rev = math.log(f.loc[2025, "net_revenue"] / f.loc[2015, "net_revenue"]) / n
    sh0, sh1 = f.loc[2015, "diluted_shares_derived"], f.loc[2025, "diluted_shares_derived"]
    m0 = f.loc[2015, "eps_nongaap_diluted"] * sh0 / f.loc[2015, "net_revenue"]
    m1 = f.loc[2025, "eps_nongaap_diluted"] * sh1 / f.loc[2025, "net_revenue"]
    margin = math.log(m1 / m0) / n
    shares = math.log(sh0 / sh1) / n
    total = rev + margin + shares
    eps_cagr = (f.loc[2025, "eps_nongaap_diluted"] / f.loc[2015, "eps_nongaap_diluted"]) ** (1 / n) - 1
    assert abs(math.exp(total) - 1 - eps_cagr) < 1e-9
    return {"revenue": rev, "margin": margin, "buybacks": shares, "total_log": total,
            "eps_cagr": eps_cagr, "margin_2015": m0, "margin_2025": m1}


def half_life(r):
    return math.log(2) / math.log(1 + r)


def doubling_time(g):
    return math.log(2) / math.log(1 + g)


def forward_fcf_yield():
    """Next-year FCF after SBC / market cap, as in valuation.py's single-stage Gordon check."""
    v = _valuation()
    return v.TTM["fcf_after_sbc"] * (1 + v.BASE["stage1_growth"]) / v.MCAP


def discount_rate():
    return _valuation().BASE["discount_rate"]


@lru_cache
def _valuation():
    import valuation  # analysis/valuation.py (module-level inputs only; main() is not run)
    return valuation


@lru_cache
def _scen():
    import scenarios as sc  # analysis/scenarios.py
    return sc


def value_at_growth(g, r=None):
    return _valuation().dcf(stage1=g, r=r)


def bisection_steps(lo=0.04, hi=0.14, n=8):
    """The first n bisection brackets for the stage-1 growth implied by today's price."""
    v = _valuation()
    price = v.PRICE
    steps = []
    for _ in range(n):
        mid = (lo + hi) / 2
        val = v.dcf(stage1=mid)
        steps.append((lo, hi, mid, val))
        lo, hi = (lo, mid) if val > price else (mid, hi)
    return steps


def price_return_curve(prices, years=10):
    sc = _scen()
    return [sc.expected_return_at(p, years) for p in prices]


def scenario_paths():
    """Price path endpoints per scenario (now -> 5y -> 10y)."""
    s = scenarios()
    out = {}
    for name in ("bear", "base", "bull", "probability-weighted"):
        d = s[s["scenario"] == name].set_index("horizon_years")
        out[name] = {h: d.loc[h] for h in (5, 10)}
    return out


def mean_of_returns(h):
    s = scenarios()
    return float(s[(s["scenario"] == "probability-weighted") & (s["horizon_years"] == h)]["mean_of_scenario_returns"].iloc[0])


def price():
    return float(scenario_inputs()["price"])


if __name__ == "__main__":
    d = eps_decomposition()
    print("EPS decomposition (log points/yr): revenue {revenue:.4f}, margin {margin:.4f}, buybacks {buybacks:.4f}, "
          "total {total_log:.4f} -> EPS CAGR {eps_cagr:.4f}; net margin {margin_2015:.3f} -> {margin_2025:.3f}".format(**d))
    print(f"revenue doubling time at 11.2%: {doubling_time(growth().loc['net_revenue', 'cagr_2015_2025']):.2f} years")
    for r in (0.05, 0.085, 0.12):
        print(f"half-life at {r:.1%}: {half_life(r):.2f} years")
    print(f"next-year FCF yield (Gordon check): {forward_fcf_yield():.4f}")
    for lo, hi, mid, val in bisection_steps():
        print(f"bisection [{lo:.4f}, {hi:.4f}] mid {mid:.4f} -> ${val:.1f}")
    print("expected 10y return at $346 / $402.61:", [round(x, 4) for x in price_return_curve([346.4044561, price()])])
    print("mean of scenario returns 5y/10y:", mean_of_returns(5), mean_of_returns(10))
