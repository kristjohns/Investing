"""Shared paths, data loaders and chart styling for the Visa analysis.

Every script in this folder imports from here so that inputs live in one place:
  analysis/data/*.csv      hand-compiled figures, one row per figure, each with a source_id
  analysis/data/raw/*.csv  public datasets downloaded by fetch_public_data.py
  analysis/output/*.csv    tables produced by the scripts (the report quotes these)
  charts/*.png             figures produced by charts.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
DATA = ANALYSIS / "data"
RAW = DATA / "raw"
OUT = ANALYSIS / "output"
CHARTS = ROOT / "charts"

for _d in (RAW, OUT, CHARTS):
    _d.mkdir(parents=True, exist_ok=True)

ANALYSIS_DATE = "2026-10-17"
PRICE_DATE = "2026-10-16"

FIRST_FY, LAST_FY = 2015, 2025


def load_annual() -> pd.DataFrame:
    """Visa annual figures as a wide table: index = fiscal year, columns = metrics."""
    long = pd.read_csv(DATA / "visa_annual.csv")
    long = long[pd.to_numeric(long["value"], errors="coerce").notna()].copy()
    long["value"] = long["value"].astype(float)
    wide = long.pivot(index="fiscal_year", columns="metric", values="value")
    return wide.sort_index()


def load_quarterly() -> dict:
    """Visa interim figures keyed by (period, metric). Text values are kept as text."""
    q = pd.read_csv(DATA / "visa_quarterly.csv")
    out = {}
    for _, r in q.iterrows():
        try:
            out[(r["period"], r["metric"])] = float(r["value"])
        except ValueError:
            out[(r["period"], r["metric"])] = r["value"]
    return out


def load_market() -> dict:
    """Market data points keyed by item (latest date wins if an item repeats)."""
    m = pd.read_csv(DATA / "market_data.csv").sort_values("date")
    return {r["item"]: float(r["value"]) for _, r in m.iterrows()}


def market_series(item: str) -> pd.Series:
    m = pd.read_csv(DATA / "market_data.csv")
    m = m[m["item"] == item].copy()
    m["date"] = pd.to_datetime(m["date"])
    return m.set_index("date")["value"].astype(float).sort_index()


def load_fy_prices() -> pd.DataFrame:
    return pd.read_csv(DATA / "visa_fy_end_prices.csv").set_index("fiscal_year")


def load_usdnok_daily() -> pd.Series:
    """NOK per USD, daily (Federal Reserve H.10 via FRED, mirrored by datahub.io)."""
    fx = pd.read_csv(RAW / "exchange_rates_daily.csv", parse_dates=["Date"])
    nok = fx[fx["Country"] == "Norway"].set_index("Date")["Exchange rate"]
    return nok[nok > 0].sort_index()


def load_shiller() -> pd.DataFrame:
    s = pd.read_csv(RAW / "shiller_sp500_monthly.csv", parse_dates=["Date"])
    return s.set_index("Date").sort_index()


def load_10y_monthly() -> pd.Series:
    y = pd.read_csv(RAW / "us_10y_yield_monthly.csv", parse_dates=["Date"])
    return y.set_index("Date")["Rate"].sort_index()


def load_cpi_monthly() -> pd.Series:
    c = pd.read_csv(RAW / "cpi_us_monthly.csv", parse_dates=["Date"])
    return c.set_index("Date")["Index"].sort_index()


def save_table(df: pd.DataFrame, name: str, index: bool = True) -> Path:
    path = OUT / f"{name}.csv"
    df.to_csv(path, index=index, float_format="%.10g")
    return path


# ---------------------------------------------------------------------------
# Chart style. Palette = the dataviz skill's validated reference instance (light
# mode). Categorical slots are always assigned in this fixed order; the subsets
# used here (2-5 slots) pass the validator's CVD and normal-vision gates. Aqua and
# yellow sit below 3:1 contrast, so every chart has a table twin in analysis/output.
# ---------------------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DEEMPH = "#c3c2b7"  # context / de-emphasised series
DIVERGING_NEG = "#e34948"  # red pole (below reference)
DIVERGING_POS = "#2a78d6"  # blue pole (above reference)
DIVERGING_MID = "#f0efec"


def setup_matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.edgecolor": AXIS,
            "axes.labelcolor": INK_2,
            "axes.titlecolor": INK,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.linestyle": "-",
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK_2,
            "ytick.labelcolor": INK_2,
            "legend.frameon": False,
            "legend.labelcolor": INK_2,
            "lines.linewidth": 2,
            "lines.solid_capstyle": "round",
            "lines.solid_joinstyle": "round",
            "text.parse_math": False,  # "$40bn" must print as text, not math
        }
    )
    return plt


def finish(fig, ax, name: str, source: str, subtitle: str | None = None):
    """Common footer (source line), subtitle and save."""
    import textwrap

    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, color=INK_2, fontsize=9, va="bottom")
    note = textwrap.fill(f"Source: {source}", width=135)
    n_lines = note.count("\n") + 1
    fig.text(0.01, 0.01, note, color=MUTED, fontsize=7.5, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.035 + 0.03 * n_lines, 1, 1))
    path = CHARTS / f"{name}.png"
    fig.savefig(path, dpi=160)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path
