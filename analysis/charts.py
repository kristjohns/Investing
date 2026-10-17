"""All report charts (PNG, light surface) built from analysis/output/*.csv.

Each chart has a table twin in analysis/output (the report also prints the key
numbers), so no value depends on reading a colour.
"""
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle

from common import (AXIS, DEEMPH, DIVERGING_MID, DIVERGING_NEG, DIVERGING_POS, GRID, INK, INK_2, MUTED, OUT,
                    SERIES, SURFACE, finish, load_usdnok_daily, setup_matplotlib)

plt = setup_matplotlib()
FIN = pd.read_csv(OUT / "financials_annual.csv", index_col=0)
YEARS = list(FIN.index)
FY = [f"FY{str(y)[2:]}" for y in YEARS]
SRC_V = "Visa 10-K/10-Q filings and earnings releases (SEC EDGAR); analysis/data/visa_annual.csv"


# ----------------------------------------------------------------------------- helpers
def rounded_bars(ax, xs, heights, bottoms=None, width=0.42, color=SERIES[0], round_end=True, radius_px=4):
    """Bars with a ~4px rounded data end and a square base (matplotlib has no native option)."""
    bottoms = np.zeros(len(xs)) if bottoms is None else np.asarray(bottoms, float)
    ax.figure.canvas.draw()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bbox = ax.get_window_extent()
    rx = radius_px * (x1 - x0) / bbox.width
    ry = radius_px * (y1 - y0) / bbox.height
    for x, h, b in zip(xs, heights, bottoms):
        if not np.isfinite(h) or h == 0:
            continue
        left = x - width / 2
        sign = 1 if h > 0 else -1
        if round_end and abs(h) > 2 * ry:
            patch = FancyBboxPatch((left, b if h > 0 else b + h), width, abs(h),
                                   boxstyle=f"round,pad=0,rounding_size={rx}", mutation_aspect=ry / rx,
                                   facecolor=color, edgecolor="none", zorder=3)
            ax.add_patch(patch)
            # square off the base end
            base_h = abs(h) - ry
            ax.add_patch(Rectangle((left, b if h > 0 else b - base_h), width, base_h * 1.0 if h > 0 else base_h,
                                   facecolor=color, edgecolor="none", zorder=3))
        else:
            ax.add_patch(Rectangle((left, b if h > 0 else b + h), width, abs(h), facecolor=color,
                                   edgecolor="none", zorder=3))
        # 2px surface gap at the joint with the segment below (stacks)
        if b != 0:
            ax.plot([left, left + width], [b, b], color=SURFACE, lw=1.6, zorder=4, solid_capstyle="butt")


def pct_axis(ax, decimals=0):
    from matplotlib.ticker import PercentFormatter

    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=decimals))


def end_label(ax, x, y, text, color=INK_2, dx=0.15, dy=0, ha="left", **kw):
    ax.annotate(text, (x, y), xytext=(x + dx, y + dy), color=color, fontsize=8.5, ha=ha, va="center", **kw)


def legend_top(ax, handles=None, labels=None, ncol=4):
    if handles is None:
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol, fontsize=8.5, handlelength=1.2,
                  borderaxespad=0.2, columnspacing=1.2)
    else:
        ax.legend(handles, labels, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol, fontsize=8.5,
                  handlelength=1.2, borderaxespad=0.2, columnspacing=1.2)


def base_axes(figsize=(8, 4.6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axisbelow(True)
    return fig, ax


def title(ax, text, pad=34):
    ax.set_title(text, pad=pad)


# ----------------------------------------------------------------------------- charts
def chart_revenue_mix():
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    fig, ax = base_axes((8.4, 4.9))
    lines = [("service_rev", "Service"), ("data_processing_rev", "Data processing"),
             ("intl_transaction_rev", "International transaction"), ("other_rev", "Other")]
    x = np.arange(len(YEARS))
    gross = FIN["gross_revenue"].values / 1e3
    ax.set_xlim(-0.6, len(x) - 0.2)
    ax.set_ylim(-19, 60)
    bottoms = np.zeros(len(x))
    for i, (col, _) in enumerate(lines):
        vals = FIN[col].values / 1e3
        rounded_bars(ax, x, vals, bottoms, color=SERIES[i], round_end=(col == "other_rev"))
        bottoms += vals
    rounded_bars(ax, x, -FIN["client_incentives"].values / 1e3, color=DEEMPH)
    ax.plot(x, FIN["net_revenue"].values / 1e3, color=INK, lw=2, marker="o", ms=5, mec=SURFACE, mew=1.5, zorder=5)
    ax.axhline(0, color=AXIS, lw=1)
    ax.set_xticks(x, FY)
    ax.set_ylabel("USD bn")
    end_label(ax, x[-1], FIN["net_revenue"].iloc[-1] / 1e3, f"Net revenue\n${FIN['net_revenue'].iloc[-1]/1e3:.1f}bn",
              dx=0.3, dy=-6, color=INK)
    end_label(ax, x[-1], -FIN["client_incentives"].iloc[-1] / 1e3,
              f"Client incentives\n−${FIN['client_incentives'].iloc[-1]/1e3:.1f}bn", dx=0.3, dy=0)
    handles = [Patch(color=SERIES[i]) for i in range(4)] + [Patch(color=DEEMPH),
                                                           Line2D([], [], color=INK, marker="o", ms=5)]
    labels = [l for _, l in lines] + ["Client incentives (contra-revenue)", "Net revenue"]
    legend_top(ax, handles, labels, ncol=3)
    title(ax, "Visa revenue by line: gross revenue streams, incentives paid back, net revenue", pad=44)
    return finish(fig, ax, "01_revenue_mix", SRC_V + ". FY15-16 incentives derived as gross less net revenue.")


def chart_incentives():
    fig, ax = base_axes()
    x = np.arange(len(YEARS))
    y = FIN["incentives_pct_gross"].values
    ax.plot(x, y, color=SERIES[0], marker="o", ms=5, mec=SURFACE, mew=1.5)
    ax.set_xticks(x, FY)
    ax.set_ylim(0.14, 0.31)
    pct_axis(ax)
    end_label(ax, x[0], y[0], f"{y[0]:.1%}", dx=0.1, dy=-0.012, ha="left")
    end_label(ax, x[-1], y[-1], f"{y[-1]:.1%}", dx=-0.1, dy=0.011, ha="right")
    i19 = YEARS.index(2019)
    ax.annotate("ASC 606 adopted (FY19):\npart of incentives reclassified\ninto contra-revenue",
                (x[i19], y[i19]), xytext=(x[i19] - 3.6, 0.262), fontsize=8, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    title(ax, "Client incentives as a share of gross revenue", pad=22)
    return finish(fig, ax, "02_incentives_share", SRC_V,
                  subtitle="Rebates paid to issuers/merchants for volume and exclusivity; rising share = pricing pressure")


def chart_growth_drivers():
    fig, ax = base_axes()
    yrs = YEARS[1:]
    x = np.arange(len(yrs))
    series = [("net_revenue_growth", "Net revenue growth", SERIES[0]),
              ("processed_transactions_growth", "Processed transactions growth", SERIES[1]),
              ("cross_border_growth_ex_europe", "Cross-border volume growth (ex intra-Europe)", SERIES[2])]
    for col, lab, c in series:
        v = FIN.loc[yrs, col].values.astype(float)
        if col == "cross_border_growth_ex_europe":
            v = v / 100
        ax.plot(x, v, color=c, marker="o", ms=5, mec=SURFACE, mew=1.5, label=lab)
    ax.axhline(0, color=AXIS, lw=1)
    ax.set_xticks(x, [f"FY{str(y)[2:]}" for y in yrs])
    pct_axis(ax)
    ax.annotate("Visa Europe consolidated\n(acquired Jun 2016)", (1, FIN.loc[2017, "processed_transactions_growth"]),
                xytext=(1.6, 0.36), fontsize=8, color=INK_2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("COVID: cross-border −22%", (4, -0.22), xytext=(5.0, -0.2), fontsize=8, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    legend_top(ax, ncol=2)
    title(ax, "What drives revenue: transactions and cross-border volume", pad=40)
    return finish(fig, ax, "03_growth_drivers", SRC_V + ". Cross-border: constant-dollar except FY21-22 (nominal); FY20 transactions secondary source.")


def chart_margins():
    fig, ax = base_axes()
    x = np.arange(len(YEARS))
    for col, lab, c in (("op_margin", "Operating margin (GAAP)", SERIES[0]),
                        ("net_margin", "Net margin (GAAP)", SERIES[1]),
                        ("fcf_margin", "Free-cash-flow margin", SERIES[2])):
        v = FIN[col].values
        ax.plot(x, v, color=c, marker="o", ms=5, mec=SURFACE, mew=1.5, label=lab)
        end_label(ax, x[-1], v[-1], f"{v[-1]:.0%}", dx=0.2)
    ax.set_xticks(x, FY)
    ax.set_ylim(0.25, 0.75)
    pct_axis(ax)
    ax.annotate("Visa Europe framework-\nagreement loss (FY16)", (1, FIN.loc[2016, "op_margin"]), xytext=(1.5, 0.30),
                fontsize=8, color=INK_2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("$2.6bn litigation\nprovision (FY25)", (10, FIN.loc[2025, "op_margin"]), xytext=(7.4, 0.71),
                fontsize=8, color=INK_2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    legend_top(ax, ncol=3)
    title(ax, "Margins: roughly two-thirds of net revenue becomes operating profit", pad=40)
    return finish(fig, ax, "04_margins", SRC_V)


def chart_capital_returns():
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    fig, ax = base_axes()
    x = np.arange(len(YEARS))
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.set_ylim(0, 26)
    bb, dv = FIN["buybacks"].values / 1e3, FIN["dividends_paid"].values / 1e3
    rounded_bars(ax, x, bb, color=SERIES[0], round_end=False)
    rounded_bars(ax, x, dv, bottoms=bb, color=SERIES[1])
    ax.plot(x, FIN["fcf"].values / 1e3, color=INK, lw=2, marker="o", ms=5, mec=SURFACE, mew=1.5, zorder=5)
    ax.set_xticks(x, FY)
    ax.set_ylabel("USD bn")
    tot = FIN["capital_returned"].sum() / 1e3
    fcf = FIN["fcf"].sum() / 1e3
    ax.text(0.0, 23.5, f"FY15-25 cumulative: returned ${tot:,.0f}bn vs FCF ${fcf:,.0f}bn ({tot/fcf:.0%})",
            fontsize=8.5, color=INK_2)
    legend_top(ax, [Patch(color=SERIES[0]), Patch(color=SERIES[1]), Line2D([], [], color=INK, marker="o", ms=5)],
               ["Share buybacks", "Dividends", "Free cash flow"], ncol=3)
    title(ax, "Almost all free cash flow is returned to shareholders", pad=40)
    return finish(fig, ax, "05_capital_returns", SRC_V + "; FY16/20-22 buybacks on trade-date basis (10-K repurchase table).")


def chart_shares_sbc():
    fig, ax = base_axes()
    x = np.arange(len(YEARS))
    v = FIN["diluted_shares_derived"].values
    ax.plot(x, v, color=SERIES[0], marker="o", ms=5, mec=SURFACE, mew=1.5)
    ax.set_xticks(x, FY)
    ax.set_ylabel("Diluted shares, millions (as-converted)")
    ax.set_ylim(1800, 2600)
    end_label(ax, x[0], v[0], f"{v[0]:,.0f}m", dx=0.1, dy=40)
    end_label(ax, x[-1], v[-1], f"{v[-1]:,.0f}m", dx=-0.1, dy=-45, ha="right")
    cagr = (v[-1] / v[0]) ** (1 / 10) - 1
    sbc = FIN["sbc_pct_rev"]
    ax.text(0.0, 1835, f"{cagr:.1%} a year FY15-25, net of stock-based pay\n(SBC {sbc.iloc[0]:.1%} of revenue in FY15, "
                       f"{sbc.iloc[-1]:.1%} in FY25)", fontsize=8.5, color=INK_2)
    title(ax, "Buybacks shrink the share count by about 2% a year", pad=22)
    return finish(fig, ax, "06_share_count", SRC_V + ". Shares = GAAP net income / diluted EPS (matches the 10-K's 1,966m for FY25).")


def chart_roic():
    fig, ax = base_axes()
    x = np.arange(len(YEARS))
    for col, lab, c in (("roic_gross", "ROIC on equity + debt", SERIES[0]),
                        ("roic_net", "ROIC on equity + net debt (FY20+)", SERIES[1]),
                        ("roe", "Return on equity", SERIES[2])):
        v = FIN[col].values
        ax.plot(x, v, color=c, marker="o", ms=5, mec=SURFACE, mew=1.5, label=lab)
        if np.isfinite(v[-1]):
            end_label(ax, x[-1], v[-1], f"{v[-1]:.0%}", dx=0.2)
    ax.set_xticks(x, FY)
    pct_axis(ax)
    ax.set_ylim(0, 0.6)
    ax.text(0.0, 0.555, "FY25 goodwill + intangibles ($47.5bn) exceed net invested capital ($43.1bn): "
                        "tangible capital is negative", fontsize=8.5, color=INK_2)
    legend_top(ax, ncol=3)
    title(ax, "Returns on capital", pad=40)
    return finish(fig, ax, "07_roic", SRC_V + ". NOPAT = operating income x (1 - tax); tax rate assumed where not collected (see financials.py).")


def chart_pe_history():
    h = pd.read_csv(OUT / "valuation_history.csv", index_col=0)
    labels = [f"FY{str(i)[2:]}" if i != "now" else "Now" for i in h.index]
    fig, ax = base_axes()
    x = np.arange(len(h))
    ax.plot(x, h["spx_trailing_pe"], color=DEEMPH, marker="o", ms=5, mec=SURFACE, mew=1.5,
            label="S&P 500, trailing P/E (as-reported earnings)")
    ax.plot(x, h["pe_gaap"], color=SERIES[0], marker="o", ms=5, mec=SURFACE, mew=1.5,
            label="Visa, trailing P/E (GAAP EPS)")
    ax.plot(x, h["pe_next_year_nongaap"], color=SERIES[1], marker="o", ms=5, mec=SURFACE, mew=1.5,
            label="Visa, price / next fiscal year's non-GAAP EPS")
    ax.set_xticks(x, labels)
    ax.set_ylim(15, 45)
    ax.set_ylabel("Price / earnings (x)")
    for col in ("pe_gaap", "pe_next_year_nongaap", "spx_trailing_pe"):
        end_label(ax, x[-1], h[col].iloc[-1], f"{h[col].iloc[-1]:.1f}x", dx=0.2)
    legend_top(ax, ncol=2)
    title(ax, "Valuation history at each fiscal year-end (30 Sep) and today", pad=40)
    return finish(fig, ax, "08_pe_history",
                  "Prices: fullratio.com/MarketBeat; EPS: Visa filings; S&P 500: Shiller data (FY15-22), Multpl (FY23-25, now = Jul 2026); next-year EPS for FY25/now = consensus")


def chart_fcf_yield():
    h = pd.read_csv(OUT / "valuation_history.csv", index_col=0)
    labels = [f"FY{str(i)[2:]}" if i != "now" else "Now" for i in h.index]
    fig, ax = base_axes()
    x = np.arange(len(h))
    ax.plot(x, h["fcf_yield"], color=SERIES[0], marker="o", ms=5, mec=SURFACE, mew=1.5, label="Visa free-cash-flow yield")
    ax.plot(x, h["us10y"], color=SERIES[1], marker="o", ms=5, mec=SURFACE, mew=1.5, label="US 10-year Treasury yield")
    ax.set_xticks(x, labels)
    pct_axis(ax, 1)
    ax.set_ylim(0, 0.06)
    end_label(ax, x[-1], h["fcf_yield"].iloc[-1], f"{h['fcf_yield'].iloc[-1]:.1%}", dx=0.2)
    end_label(ax, x[-1], h["us10y"].iloc[-1], f"{h['us10y'].iloc[-1]:.1%}", dx=0.2)
    legend_top(ax, ncol=2)
    title(ax, "Visa's cash yield vs the risk-free rate: now the widest gap in a decade", pad=40)
    return finish(fig, ax, "09_fcf_yield_vs_10y",
                  "Visa FCF (CFO - capex) / market cap at FY-end; 10y: Federal Reserve via datahub.io (Sep avg), now = 16 Oct 2026 close (CNBC)")


def chart_dcf_heatmap():
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    s = pd.read_csv(OUT / "dcf_sensitivity_growth_rate.csv", index_col=0)
    price = pd.read_csv(OUT / "valuation_current_multiples.csv", index_col=0).iloc[0, 0]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.grid(False)
    cmap = LinearSegmentedColormap.from_list("div", ["#c22f2f", "#f2a6a5", DIVERGING_MID, "#9ec5f4", "#1c5cab"])
    vals = s.values
    norm = TwoSlopeNorm(vcenter=price, vmin=min(vals.min(), price * 0.5), vmax=max(vals.max(), price * 1.5))
    ax.imshow(vals, cmap=cmap, norm=norm, aspect="auto")
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            v = vals[i, j]
            rel = abs(norm(v) - 0.5)
            ax.text(j, i, f"${v:,.0f}", ha="center", va="center", fontsize=9,
                    color="white" if rel > 0.33 else INK)
    ax.set_xticks(range(vals.shape[1]), s.columns)
    ax.set_yticks(range(vals.shape[0]), s.index)
    ax.set_xlabel("Discount rate (cost of equity)")
    ax.set_ylabel("Revenue growth FY27-31\n(then fades to 4% by FY36)")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    title(ax, f"DCF value per share vs today's price (${price:,.2f}): blue = above, red = below", pad=22)
    return finish(fig, ax, "10_dcf_sensitivity",
                  "analysis/valuation.py; FCF after SBC = 51.1% of revenue; terminal growth 4%; base case = 10% / 8.5%")


def chart_scenarios():
    sc = pd.read_csv(OUT / "scenarios.csv")
    order = ["bear", "base", "bull", "probability-weighted"]
    fig, ax = base_axes((8, 4.4))
    y = np.arange(len(order))
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.axvspan(0.07, 0.0928, color=GRID, alpha=0.6, zorder=0)
    ax.text(0.0815, -0.62, "Global index fund\nexpected 7.0-9.3%", ha="center", va="center", fontsize=8, color=INK_2)
    for k, (h, c) in enumerate(((5, SERIES[0]), (10, SERIES[1]))):
        d = sc[sc["horizon_years"] == h].set_index("scenario").loc[order]
        vals = d["annualised_return_usd"].values
        ax.barh(y + (k - 0.5) * 0.3, vals, height=0.26, color=c, label=f"{h}-year horizon", zorder=3)
        for yi, v in zip(y + (k - 0.5) * 0.3, vals):
            ax.text(v + (0.004 if v >= 0 else -0.004), yi, f"{v:+.1%}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=8.5, color=INK_2)
    probs = sc[sc["horizon_years"] == 5].set_index("scenario")["probability"]
    ax.set_yticks(y, [f"{o.capitalize()} ({probs[o]:.0%})" if o != "probability-weighted" else "Probability-weighted"
                      for o in order])
    ax.set_ylim(len(order) - 0.45, -0.95)   # inverted, with headroom for the index label
    ax.axvline(0, color=AXIS, lw=1)
    from matplotlib.ticker import PercentFormatter
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlim(-0.06, 0.2)
    ax.set_xlabel("Annualised total return in USD (IRR, buying at $402.61)")
    legend_top(ax, ncol=2)
    title(ax, "Scenario returns: the expected return is roughly the market's", pad=36)
    return finish(fig, ax, "11_scenarios", "analysis/scenarios.py; probabilities are judgement; index range: Damodaran implied ERP + 10y UST (9.3%) and a 7% lower bound")


def chart_usdnok():
    nok = load_usdnok_daily()
    m = nok.resample("ME").mean().loc["2000":]
    fig, ax = base_axes()
    for a, b in (("2008-05-07", "2009-01-20"), ("2020-02-19", "2020-03-23"), ("2022-02-02", "2022-09-30")):
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=GRID, alpha=0.8, zorder=0)
    ax.plot(m.index, m.values, color=SERIES[0], lw=2)
    avg10 = nok.loc[nok.index[-1] - pd.DateOffset(years=10):].mean()
    ax.axhline(avg10, color=MUTED, lw=1)
    ax.text(pd.Timestamp("2000-06-01"), avg10 + 0.15, f"10-year average {avg10:.2f}", fontsize=8, color=INK_2)
    ax.text(pd.Timestamp("2008-03-01"), 11.3, "shaded = Visa share-price\ndrawdowns (2008-09, 2020, 2022)",
            fontsize=8, color=INK_2)
    ax.annotate(f"{nok.iloc[-1]:.2f}\n({nok.index[-1]:%d %b %Y})", (m.index[-1], m.iloc[-1]),
                xytext=(m.index[-1] + pd.DateOffset(months=4), m.iloc[-1] - 0.9), fontsize=8.5, color=INK_2)
    ax.set_ylabel("NOK per USD")
    ax.set_ylim(4.5, 12.5)
    ax.set_xlim(m.index[0], m.index[-1] + pd.DateOffset(months=30))
    title(ax, "USD/NOK: the krone tends to weaken when stocks fall", pad=22)
    return finish(fig, ax, "12_usdnok", "Federal Reserve H.10 (FRED DEXNOUS) via datahub.io, monthly averages")


def chart_drawdowns():
    dd = pd.read_csv(OUT / "downturns.csv", index_col=0)
    fx = pd.read_csv(OUT / "fx_in_drawdowns.csv").set_index("episode")
    dd["visa_nok"] = (1 + dd["visa_drawdown"]) * (1 + fx.loc[dd.index, "usdnok_change"]) - 1
    fig, ax = base_axes((8, 4.4))
    x = np.arange(len(dd))
    w = 0.24
    for k, (col, lab, c) in enumerate((("visa_drawdown", "Visa (USD)", SERIES[0]),
                                       ("spx_drawdown", "S&P 500 (USD)", DEEMPH),
                                       ("visa_nok", "Visa measured in NOK", SERIES[1]))):
        vals = dd[col].values
        ax.bar(x + (k - 1) * (w + 0.03), vals, width=w, color=c, label=lab, zorder=3)
        for xi, v in zip(x + (k - 1) * (w + 0.03), vals):
            ax.text(xi, v - 0.02, f"{v:.0%}", ha="center", va="top", fontsize=8.5, color=INK_2)
    ax.axhline(0, color=AXIS, lw=1)
    ax.set_xticks(x, ["2008-09 financial crisis", "2020 COVID crash", "2022 inflation shock"])
    pct_axis(ax)
    ax.set_ylim(-0.68, 0.05)
    legend_top(ax, ncol=3)
    title(ax, "Peak-to-trough price falls: Visa vs the market, and in NOK", pad=36)
    return finish(fig, ax, "13_drawdowns", "TickerLeague/ChartRow price data (qualitative_facts M11); USD/NOK: FRED H.10 over the same dates")


def main():
    paths = [chart_revenue_mix(), chart_incentives(), chart_growth_drivers(), chart_margins(),
             chart_capital_returns(), chart_shares_sbc(), chart_roic(), chart_pe_history(), chart_fcf_yield(),
             chart_dcf_heatmap(), chart_scenarios(), chart_usdnok(), chart_drawdowns()]
    for p in paths:
        print("wrote", p.relative_to(p.parent.parent))


if __name__ == "__main__":
    main()
