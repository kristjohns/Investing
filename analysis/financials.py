"""Visa 10-year financial analysis (fiscal years ending 30 September, FY2015-FY2025).

Reads data/visa_annual.csv and data/visa_quarterly.csv, derives ratios, runs internal
consistency checks (do the revenue lines add up to reported net revenue? do expense
lines add up to total opex? does net income / EPS reproduce the reported share count?)
and writes:
  output/financials_annual.csv      the wide 10-year table incl. derived ratios
  output/consistency_checks.csv     every check with PASS/FAIL
  output/growth_summary.csv         CAGRs over FY2015-25 and FY2017-25
  output/ttm.csv                    trailing twelve months to 30 Jun 2026
"""
import numpy as np
import pandas as pd

from common import FIRST_FY, LAST_FY, load_annual, load_quarterly, save_table

REV_LINES = ["service_rev", "data_processing_rev", "intl_transaction_rev", "other_rev"]

# Tax rate used for NOPAT where the 10-K rate was not collected. ASSUMPTIONS, not data:
# ~30% before the US Tax Cuts and Jobs Act, the 24.5% blended statutory rate in FY2018,
# ~19% thereafter (Visa's reported rate was 18% in FY2023 and 17% in FY2024-25).
ASSUMED_TAX = {2015: 0.30, 2016: 0.30, 2017: 0.30, 2018: 0.245, 2019: 0.19, 2020: 0.19, 2021: 0.19, 2022: 0.19}


def cagr(start, end, years):
    return (end / start) ** (1 / years) - 1


def build_table() -> pd.DataFrame:
    a = load_annual().loc[FIRST_FY:LAST_FY].copy()

    a["gross_revenue"] = a[REV_LINES].sum(axis=1)
    derived_ci = a["client_incentives"].isna()
    a.loc[derived_ci, "client_incentives"] = a.loc[derived_ci, "gross_revenue"] - a.loc[derived_ci, "net_revenue"]
    a["client_incentives_derived"] = derived_ci
    a["incentives_pct_gross"] = a["client_incentives"] / a["gross_revenue"]

    for col in REV_LINES + ["gross_revenue", "client_incentives", "net_revenue"]:
        a[f"{col}_growth"] = a[col].pct_change()
    for col in REV_LINES:
        a[f"{col}_share_gross"] = a[col] / a["gross_revenue"]

    derived_opex = a["total_opex"].isna()
    a.loc[derived_opex, "total_opex"] = a.loc[derived_opex, "net_revenue"] - a.loc[derived_opex, "operating_income"]
    a["op_margin"] = a["operating_income"] / a["net_revenue"]
    a["nongaap_op_margin"] = (a["net_revenue"] - a["nongaap_opex"]) / a["net_revenue"]
    a["net_margin"] = a["net_income"] / a["net_revenue"]
    a["litigation_pct_rev"] = a["litigation_provision"] / a["net_revenue"]

    a["diluted_shares_derived"] = a["net_income"] / a["eps_gaap_diluted"]
    a["diluted_shares_growth"] = a["diluted_shares_derived"].pct_change()
    a["eps_gaap_growth"] = a["eps_gaap_diluted"].pct_change()
    a["eps_nongaap_growth"] = a["eps_nongaap_diluted"].pct_change()

    a["fcf"] = a["cfo"] - a["capex"]
    a["fcf_margin"] = a["fcf"] / a["net_revenue"]
    a["fcf_after_sbc"] = a["fcf"] - a["sbc"]
    a["fcf_after_sbc_margin"] = a["fcf_after_sbc"] / a["net_revenue"]
    a["fcf_conversion"] = a["fcf"] / a["net_income"]
    a["capex_pct_rev"] = a["capex"] / a["net_revenue"]
    a["sbc_pct_rev"] = a["sbc"] / a["net_revenue"]
    a["capital_returned"] = a["buybacks"] + a["dividends_paid"]
    a["capital_returned_pct_fcf"] = a["capital_returned"] / a["fcf"]
    a["buybacks_pct_fcf"] = a["buybacks"] / a["fcf"]

    tax = pd.Series(ASSUMED_TAX, dtype=float).reindex(a.index)
    reported = a["effective_tax_rate"] / 100
    a["tax_rate_used"] = reported.fillna(tax)
    a["tax_rate_is_assumption"] = reported.isna()
    a["nopat"] = a["operating_income"] * (1 - a["tax_rate_used"])

    a["invested_capital_gross"] = a["total_equity"] + a["total_debt"]
    a["net_debt"] = a["total_debt"] - a["cash_and_investments"]
    a["invested_capital_net"] = a["total_equity"] + a["net_debt"]
    for ic in ("invested_capital_gross", "invested_capital_net"):
        avg = (a[ic] + a[ic].shift(1)) / 2
        a[f"{ic}_avg"] = avg.fillna(a[ic])  # first year with data: year-end value
    a["roic_gross"] = a["nopat"] / a["invested_capital_gross_avg"]
    a["roic_net"] = a["nopat"] / a["invested_capital_net_avg"]
    eq_avg = ((a["total_equity"] + a["total_equity"].shift(1)) / 2).fillna(a["total_equity"])
    a["roe"] = a["net_income"] / eq_avg

    a["processed_transactions_growth"] = a["processed_transactions"].pct_change()
    a["payments_volume_jun_growth"] = a["payments_volume_jun"].pct_change()
    a["revenue_per_transaction_usd"] = a["net_revenue"] / (a["processed_transactions"] * 1000)
    return a


def consistency_checks(a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fy, r in a.iterrows():
        if not r["client_incentives_derived"]:
            calc = r["gross_revenue"] - r["client_incentives"]
            rows.append(("revenue lines - incentives = net revenue", fy, r["net_revenue"], calc, 3))
        if pd.notna(r.get("personnel")) and pd.notna(r.get("g_and_a")):
            parts = ["personnel", "marketing", "network_processing", "professional_fees", "d_and_a",
                     "g_and_a", "litigation_provision"]
            rows.append(("opex lines = total opex", fy, r["total_opex"], sum(r[p] for p in parts), 3))
        if fy in (2017, 2018, 2019, 2023, 2024, 2025):
            rows.append(("net revenue - opex = operating income", fy, r["operating_income"],
                         r["net_revenue"] - r["total_opex"], 3))
        if pd.notna(r.get("fcf_reported_secondary")):
            rows.append(("CFO - capex = FCF (Macrotrends/Visa)", fy, r["fcf_reported_secondary"], r["fcf"], 15))
        if pd.notna(r.get("diluted_shares")):
            rows.append(("net income / EPS = reported diluted shares", fy, r["diluted_shares"],
                         r["diluted_shares_derived"], 5))
        if pd.notna(r.get("total_assets")) and pd.notna(r.get("total_liabilities")):
            rows.append(("assets - liabilities = equity", fy, r["total_equity"],
                         r["total_assets"] - r["total_liabilities"], 2))
    df = pd.DataFrame(rows, columns=["check", "fiscal_year", "reported", "recomputed", "tolerance"])
    df["difference"] = df["recomputed"] - df["reported"]
    df["result"] = np.where(df["difference"].abs() <= df["tolerance"], "PASS", "FAIL")
    return df


def growth_summary(a: pd.DataFrame) -> pd.DataFrame:
    items = REV_LINES + ["gross_revenue", "client_incentives", "net_revenue", "operating_income", "net_income",
                         "eps_gaap_diluted", "eps_nongaap_diluted", "fcf", "dividends_paid", "sbc",
                         "diluted_shares_derived"]
    recs = []
    for col in items:
        recs.append({
            "metric": col,
            "fy2015": a.loc[2015, col],
            "fy2017": a.loc[2017, col],
            "fy2025": a.loc[2025, col],
            "cagr_2015_2025": cagr(a.loc[2015, col], a.loc[2025, col], 10),
            "cagr_2017_2025": cagr(a.loc[2017, col], a.loc[2025, col], 8),
        })
    pt = a["processed_transactions"]
    recs.append({"metric": "processed_transactions_bn", "fy2015": np.nan, "fy2017": pt[2017], "fy2025": pt[2025],
                 "cagr_2015_2025": np.nan, "cagr_2017_2025": cagr(pt[2017], pt[2025], 8)})
    pv = a["payments_volume_jun"]
    recs.append({"metric": "payments_volume_12m_to_june_bn", "fy2015": np.nan, "fy2017": np.nan,
                 "fy2025": pv[2025], "cagr_2015_2025": np.nan, "cagr_2017_2025": np.nan,
                 "cagr_2021_2025": cagr(pv[2021], pv[2025], 4)})
    return pd.DataFrame(recs).set_index("metric")


def ttm(a: pd.DataFrame) -> pd.Series:
    """Trailing twelve months to 30 Jun 2026 = FY2025 + 9M FY2026 - 9M FY2025."""
    q = load_quarterly()
    fy = a.loc[2025]
    t = {}
    for m in ["net_revenue", "net_income", "eps_gaap_diluted", "eps_nongaap_diluted", "cfo", "capex", "sbc"]:
        t[m] = fy[m] + q[("9M_FY2026", m)] - q[("9M_FY2025", m)]
    t["fcf"] = t["cfo"] - t["capex"]
    t["fcf_after_sbc"] = t["fcf"] - t["sbc"]
    t["fcf_margin"] = t["fcf"] / t["net_revenue"]
    t["fcf_after_sbc_margin"] = t["fcf_after_sbc"] / t["net_revenue"]
    t["net_margin"] = t["net_income"] / t["net_revenue"]
    t["diluted_shares_q3fy26"] = q[("Q3_FY2026", "net_income")] / q[("Q3_FY2026", "eps_gaap_diluted")]
    t["nine_month_revenue_growth"] = q[("9M_FY2026", "net_revenue")] / q[("9M_FY2025", "net_revenue")] - 1
    t["nine_month_eps_nongaap_growth"] = (q[("9M_FY2026", "eps_nongaap_diluted")]
                                         / q[("9M_FY2025", "eps_nongaap_diluted")] - 1)
    t["nine_month_9m26_opex"] = q[("9M_FY2026", "total_opex")]
    t["nine_month_9m26_op_margin_gaap"] = 1 - q[("9M_FY2026", "total_opex")] / q[("9M_FY2026", "net_revenue")]
    return pd.Series(t)


def main():
    a = build_table()
    checks = consistency_checks(a)
    g = growth_summary(a)
    t = ttm(a)

    save_table(a, "financials_annual")
    save_table(checks, "consistency_checks", index=False)
    save_table(g, "growth_summary")
    save_table(t.to_frame("ttm_jun2026"), "ttm")

    n_fail = (checks["result"] == "FAIL").sum()
    print(f"Consistency checks: {len(checks) - n_fail} PASS, {n_fail} FAIL")
    if n_fail:
        print(checks[checks["result"] == "FAIL"].to_string(index=False))
    show = ["net_revenue", "net_revenue_growth", "incentives_pct_gross", "op_margin", "net_margin", "fcf",
            "fcf_margin", "diluted_shares_derived", "roic_gross", "roic_net", "roe"]
    with pd.option_context("display.float_format", "{:,.3f}".format, "display.width", 200):
        print(a[show].to_string())
        print(g.to_string())
        print(t.to_string())


if __name__ == "__main__":
    main()
