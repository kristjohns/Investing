"""Valuation of Visa at the 16 Oct 2026 close: multiples, DCF, reverse DCF, sensitivities.

All money in USD millions unless stated; per-share values in USD.

Outputs (analysis/output/):
  valuation_current_multiples.csv   P/E, EV/EBIT, FCF yield etc. now, with Mastercard
  valuation_history.csv             P/E, FCF yield, 10y yield, S&P 500 P/E at each FY end
  dcf_base.csv                      the base-case DCF year by year
  dcf_sensitivity_growth_rate.csv   value/share: stage-1 growth x discount rate
  dcf_sensitivity_terminal.csv      value/share: terminal growth x discount rate
  dcf_sensitivity_margin.csv        value/share: FCF margin x discount rate
  reverse_dcf.csv                   growth the current price implies
  valuation_assumptions.csv         every assumption with its justification
"""
import numpy as np
import pandas as pd

from common import OUT, load_10y_monthly, load_annual, load_fy_prices, load_market, load_shiller, market_series, save_table

# ----------------------------------------------------------------------------- inputs
MKT = load_market()
PRICE = MKT["V_close"]                      # 16 Oct 2026 close
FIN = pd.read_csv(OUT / "financials_annual.csv", index_col=0)
TTM = pd.read_csv(OUT / "ttm.csv", index_col=0)["ttm_jun2026"]
SHARES = TTM["diluted_shares_q3fy26"]       # as-converted diluted shares, Q3 FY2026 (net income / EPS)
NET_DEBT = FIN.loc[2025, "total_debt"] - FIN.loc[2025, "cash_and_investments"]  # 30 Sep 2025, latest audited
MCAP = PRICE * SHARES
EV = MCAP + NET_DEBT

# Consensus (Zacks after Q3 FY2026; S&P Global via Simply Wall St for FY2028 revenue)
REV_FY26E = MKT["V_consensus_rev_fy2026"]
REV_FY27E = MKT["V_consensus_rev_fy2027"]
REV_FY28E = MKT["V_consensus_rev_fy2028"]
EPS_FY26E = MKT["V_consensus_eps_fy2026"]
EPS_FY27E = MKT["V_consensus_eps_fy2027"]

# Rates (see qualitative_facts.csv M4, and valuation_assumptions.csv)
RISK_FREE = 0.0508          # US 10-year Treasury, 16 Oct 2026
ERP = 0.042                 # Damodaran implied US equity risk premium, 1 Oct 2026
BETA = 0.75                 # Visa 5-year monthly beta (Google Finance / coindataflow, Aug 2026)
CAPM = RISK_FREE + BETA * ERP

BASE = {
    "discount_rate": 0.085,     # CAPM 8.2%, rounded up for single-stock/regulatory uncertainty
    "stage1_growth": 0.10,      # FY2027-31 revenue growth; consensus FY27-28 is ~10.3-10.8%
    "terminal_growth": 0.04,    # nominal, after FY2036
    "fcf_margin": None,         # set below from history: FCF after SBC / net revenue
}
hist_margins = [FIN.loc[2023, "fcf_after_sbc_margin"], FIN.loc[2024, "fcf_after_sbc_margin"],
                FIN.loc[2025, "fcf_after_sbc_margin"], TTM["fcf_after_sbc_margin"]]
BASE["fcf_margin"] = round(float(np.mean(hist_margins)), 3)


# ----------------------------------------------------------------------------- DCF engine
def growth_path(stage1: float, terminal: float, n1: int = 5, n2: int = 5) -> list[float]:
    """n1 years at stage1, then a straight-line fade to the terminal rate over n2 years."""
    fade = [stage1 + (terminal - stage1) * (k / n2) for k in range(1, n2 + 1)]
    return [stage1] * n1 + fade


def dcf(stage1=None, r=None, g_t=None, margin=None, rev0=REV_FY26E, detail=False):
    stage1 = BASE["stage1_growth"] if stage1 is None else stage1
    r = BASE["discount_rate"] if r is None else r
    g_t = BASE["terminal_growth"] if g_t is None else g_t
    margin = BASE["fcf_margin"] if margin is None else margin
    rows, rev, pv_sum = [], rev0, 0.0
    path = growth_path(stage1, g_t)
    for t, g in enumerate(path, start=1):
        rev *= 1 + g
        fcf = rev * margin
        df = (1 + r) ** -(t - 0.5)             # mid-year convention; valuation date ~ start of FY2027
        pv_sum += fcf * df
        rows.append({"fiscal_year": 2026 + t, "revenue_growth": g, "net_revenue": rev, "fcf_after_sbc": fcf,
                     "discount_factor": df, "pv_fcf": fcf * df})
    tv = rows[-1]["fcf_after_sbc"] * (1 + g_t) / (r - g_t)
    pv_tv = tv * (1 + r) ** -(len(path) - 0.5)
    equity = pv_sum + pv_tv - NET_DEBT
    per_share = equity / SHARES
    if detail:
        return per_share, pd.DataFrame(rows), {"pv_explicit": pv_sum, "terminal_value": tv, "pv_terminal": pv_tv,
                                                "net_debt": NET_DEBT, "equity_value": equity,
                                                "terminal_share_of_value": pv_tv / (pv_sum + pv_tv)}
    return per_share


def solve_stage1(target_price, r=None, g_t=None, margin=None, lo=-0.05, hi=0.40):
    """Bisection: stage-1 growth that makes the DCF equal the target price."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if dcf(stage1=mid, r=r, g_t=g_t, margin=margin) > target_price:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def ten_year_cagr(stage1, g_t):
    p = growth_path(stage1, g_t)
    return float(np.prod([1 + g for g in p]) ** (1 / len(p)) - 1)


# ----------------------------------------------------------------------------- multiples
def current_multiples() -> pd.DataFrame:
    fy25_ngaap_ebit = FIN.loc[2025, "net_revenue"] - FIN.loc[2025, "nongaap_opex"]
    fy25_ngaap_margin = fy25_ngaap_ebit / FIN.loc[2025, "net_revenue"]
    ma_price, ma_eps = MKT["MA_close"], MKT["MA_ttm_eps_gaap"]
    ma = pd.read_csv(OUT.parent / "data" / "mastercard_annual.csv").set_index("year")
    ma_adj_ttm = float(ma.loc["2025", "eps_adjusted"]) + float(ma.loc["H1_2026", "eps_adjusted"]) - float(ma.loc["H1_2025", "eps_adjusted"])
    rows = [
        ("Share price (USD, 16 Oct 2026)", PRICE, ma_price),
        ("Diluted shares (m)", SHARES, np.nan),
        ("Market capitalisation (USD bn)", MCAP / 1e3, MKT["MA_market_cap"]),
        ("Net debt (USD bn, 30 Sep 2025)", NET_DEBT / 1e3, np.nan),
        ("Enterprise value (USD bn)", EV / 1e3, np.nan),
        ("P/E trailing, GAAP", PRICE / TTM["eps_gaap_diluted"], ma_price / ma_eps),
        ("P/E trailing, non-GAAP/adjusted", PRICE / TTM["eps_nongaap_diluted"], ma_price / ma_adj_ttm),
        ("P/E forward FY2026E (consensus)", PRICE / EPS_FY26E, MKT["MA_forward_pe_2026"]),
        ("P/E forward FY2027E (consensus)", PRICE / EPS_FY27E, np.nan),
        ("EV/EBIT FY2025, GAAP", EV / FIN.loc[2025, "operating_income"], np.nan),
        ("EV/EBIT FY2025, non-GAAP", EV / fy25_ngaap_ebit, np.nan),
        ("EV/EBIT FY2026E (consensus revenue x FY2025 non-GAAP margin)", EV / (REV_FY26E * fy25_ngaap_margin), np.nan),
        ("EV/net revenue, trailing", EV / TTM["net_revenue"], np.nan),
        ("FCF yield, trailing (%)", TTM["fcf"] / MCAP * 100, np.nan),
        ("FCF-after-SBC yield, trailing (%)", TTM["fcf_after_sbc"] / MCAP * 100, np.nan),
        ("Earnings yield, trailing non-GAAP (%)", TTM["eps_nongaap_diluted"] / PRICE * 100, np.nan),
        ("Dividend yield (%, $0.67 x 4)", 0.67 * 4 / PRICE * 100, np.nan),
        ("US 10-year Treasury yield (%)", RISK_FREE * 100, RISK_FREE * 100),
        ("S&P 500 forward P/E (FactSet)", MKT["SPX_forward_pe"], MKT["SPX_forward_pe"]),
        ("S&P 500 trailing P/E (FactSet, operating)", MKT["SPX_trailing_pe_factset"], MKT["SPX_trailing_pe_factset"]),
    ]
    df = pd.DataFrame(rows, columns=["metric", "visa", "mastercard_or_reference"]).set_index("metric")
    return df


def history() -> pd.DataFrame:
    px = load_fy_prices()
    shiller = load_shiller()
    y10 = load_10y_monthly()
    spx_multpl = market_series("SPX_trailing_pe_multpl")
    recs = []
    for fy in range(2015, 2026):
        p = px.loc[fy, "close_unadjusted"]
        eps_g, eps_n = FIN.loc[fy, "eps_gaap_diluted"], FIN.loc[fy, "eps_nongaap_diluted"]
        mcap = p * FIN.loc[fy, "diluted_shares_derived"]
        sept = pd.Timestamp(f"{fy}-09-01")
        s_row = shiller.loc[sept] if sept in shiller.index else None
        spx_pe = np.nan
        if s_row is not None and s_row["Earnings"] > 0:
            spx_pe = s_row["SP500"] / s_row["Earnings"]
        else:
            m = spx_multpl[spx_multpl.index.year == fy]
            if len(m):
                spx_pe = m.iloc[-1]
        recs.append({
            "fiscal_year": fy, "price": p, "pe_gaap": p / eps_g, "pe_nongaap": p / eps_n,
            "fcf_yield": FIN.loc[fy, "fcf"] / mcap,
            "us10y": y10.loc[sept] / 100 if sept in y10.index else np.nan,
            "spx_trailing_pe": spx_pe,
        })
    h = pd.DataFrame(recs).set_index("fiscal_year")
    # "forward" P/E with hindsight: FY-end price / the NEXT fiscal year's actual non-GAAP EPS
    # (FY2025 uses FY2026E consensus). Shows what multiple of next-year earnings investors paid.
    nxt = FIN["eps_nongaap_diluted"].shift(-1)
    nxt.loc[2025] = EPS_FY26E
    h["pe_next_year_nongaap"] = h["price"] / nxt.reindex(h.index)
    h["pe_premium_vs_spx"] = h["pe_gaap"] / h["spx_trailing_pe"] - 1
    h["fcf_yield_minus_10y"] = h["fcf_yield"] - h["us10y"]
    # current point (trailing to Jun 2026, price 16 Oct 2026)
    h.loc["now"] = {
        "price": PRICE, "pe_gaap": PRICE / TTM["eps_gaap_diluted"], "pe_nongaap": PRICE / TTM["eps_nongaap_diluted"],
        "pe_next_year_nongaap": PRICE / EPS_FY27E,
        "fcf_yield": TTM["fcf"] / MCAP, "us10y": RISK_FREE, "spx_trailing_pe": MKT["SPX_trailing_pe_multpl"],
        "pe_premium_vs_spx": (PRICE / TTM["eps_gaap_diluted"]) / MKT["SPX_trailing_pe_multpl"] - 1,
        "fcf_yield_minus_10y": TTM["fcf"] / MCAP - RISK_FREE,
    }
    return h


# ----------------------------------------------------------------------------- run
def main():
    cm = current_multiples()
    h = history()
    hist10 = h.drop(index="now")
    cols = ["pe_gaap", "pe_nongaap", "pe_next_year_nongaap", "fcf_yield", "pe_premium_vs_spx", "fcf_yield_minus_10y"]
    summary = pd.DataFrame({
        "median_fy2015_2025": hist10[cols].median(),
        "min": hist10[cols].min(),
        "max": hist10[cols].max(),
        "now": h.loc["now", cols].astype(float),
    })
    summary["now_percentile_vs_history"] = [(hist10[c] < h.loc["now", c]).mean() for c in cols]

    base_value, base_rows, base_parts = dcf(detail=True)
    rates = [0.075, 0.08, 0.085, 0.09, 0.095, 0.10]
    growths = [0.04, 0.06, 0.08, 0.10, 0.12, 0.14]
    sens_g = pd.DataFrame([[dcf(stage1=g, r=r) for r in rates] for g in growths],
                          index=[f"{g:.0%}" for g in growths], columns=[f"{r:.1%}" for r in rates])
    sens_g.index.name = "stage-1 growth FY27-31 \\ discount rate"
    terms = [0.03, 0.035, 0.04, 0.045, 0.05]
    sens_t = pd.DataFrame([[dcf(g_t=gt, r=r) for r in rates] for gt in terms],
                          index=[f"{t:.1%}" for t in terms], columns=[f"{r:.1%}" for r in rates])
    sens_t.index.name = "terminal growth \\ discount rate"
    margins = [0.42, 0.45, 0.48, 0.51, 0.54, 0.57]
    sens_m = pd.DataFrame([[dcf(margin=m, r=r) for r in rates] for m in margins],
                          index=[f"{m:.0%}" for m in margins], columns=[f"{r:.1%}" for r in rates])
    sens_m.index.name = "FCF-after-SBC margin \\ discount rate"

    rev_rows = []
    for r in [0.08, 0.085, 0.09, 0.095, 0.10]:
        for m in [0.45, BASE["fcf_margin"], 0.54]:
            g1 = solve_stage1(PRICE, r=r, margin=m)
            rev_rows.append({"discount_rate": r, "fcf_margin": m, "terminal_growth": BASE["terminal_growth"],
                             "implied_stage1_growth_fy27_31": g1,
                             "implied_10y_revenue_cagr": ten_year_cagr(g1, BASE["terminal_growth"])})
    rev = pd.DataFrame(rev_rows)
    # single-stage Gordon check: perpetual growth implied by next-year FCF / price
    fcf_next = TTM["fcf_after_sbc"] * (1 + BASE["stage1_growth"])
    gordon_g = BASE["discount_rate"] - fcf_next / MCAP

    assumptions = pd.DataFrame([
        ("valuation date / price", f"{PRICE:.2f} USD (16 Oct 2026 close)", "market_data.csv"),
        ("diluted shares (m)", f"{SHARES:,.1f}", "Q3 FY2026 net income / diluted EPS (as-converted class A)"),
        ("net debt (USD m)", f"{NET_DEBT:,.0f}", "30 Sep 2025 debt 25,171 less cash & investments 19,996; escrow excluded (earmarked for covered litigation)"),
        ("base revenue FY2026E (USD m)", f"{REV_FY26E:,.0f}", "Zacks consensus after Q3 FY2026; 9M FY2026 actual growth +15.3%"),
        ("stage-1 growth FY2027-31", f"{BASE['stage1_growth']:.1%}", "consensus FY2027 +10.3%, FY2028 +10.8%; FY2015-25 CAGR 11.2%, FY2017-25 10.2%"),
        ("fade FY2032-36", "linear to terminal", "maturing growth; regulation and A2A competition"),
        ("terminal growth", f"{BASE['terminal_growth']:.1%}", "nominal; ~2% inflation + ~2% real, below long-run nominal world GDP"),
        ("FCF after SBC / revenue", f"{BASE['fcf_margin']:.1%}", "mean of FY2023, FY2024, FY2025 and TTM (58.0%/49.7%/51.7%/45.2%); held flat"),
        ("discount rate", f"{BASE['discount_rate']:.1%}", f"CAPM {CAPM:.2%} = 5.08% 10y UST + 0.75 beta x 4.2% ERP, rounded up"),
        ("cash-flow timing", "mid-year", "valuation date ~ start of FY2027 (fiscal year begins 1 Oct)"),
    ], columns=["assumption", "value", "justification / source"])

    save_table(cm, "valuation_current_multiples")
    save_table(h, "valuation_history")
    save_table(summary, "valuation_history_summary")
    save_table(base_rows.set_index("fiscal_year"), "dcf_base")
    save_table(pd.Series(base_parts | {"value_per_share": base_value, "price": PRICE,
                                       "upside": base_value / PRICE - 1, "capm": CAPM,
                                       "gordon_implied_perpetual_growth": gordon_g}).to_frame("base"), "dcf_base_summary")
    save_table(sens_g, "dcf_sensitivity_growth_rate")
    save_table(sens_t, "dcf_sensitivity_terminal")
    save_table(sens_m, "dcf_sensitivity_margin")
    save_table(rev, "reverse_dcf", index=False)
    save_table(assumptions, "valuation_assumptions", index=False)

    with pd.option_context("display.float_format", "{:,.3f}".format, "display.width", 200):
        print(cm.to_string())
        print(h.to_string())
        print(summary.to_string())
        print(f"\nBase DCF value/share: {base_value:,.0f} vs price {PRICE:,.2f} ({base_value / PRICE - 1:+.1%}); "
              f"terminal share of value {base_parts['terminal_share_of_value']:.0%}; FCF margin {BASE['fcf_margin']:.1%}; CAPM {CAPM:.2%}")
        print(sens_g.round(0).to_string())
        print(sens_t.round(0).to_string())
        print(sens_m.round(0).to_string())
        print(rev.to_string(index=False))
        print(f"Gordon single-stage implied perpetual growth at {BASE['discount_rate']:.1%}: {gordon_g:.2%}")


if __name__ == "__main__":
    main()
