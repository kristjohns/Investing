"""Macro and currency analysis for a NOK-based investor.

Outputs (analysis/output/):
  usdnok_stats.csv            spot, averages, range and volatility of USD/NOK
  returns_usd_vs_nok.csv      Visa and S&P 500 returns FY2015-now in USD and in NOK
  fx_equity_correlation.csv   does NOK weaken when US stocks fall? (monthly, 2000-2026)
  fx_in_drawdowns.csv         USD/NOK move during the 2008-09, 2020 and 2022 equity drawdowns
  cpi_vs_visa_growth.csv      US CPI inflation vs Visa revenue / volume growth by fiscal year
  downturns.csv               Visa vs S&P 500 drawdowns and Visa revenue in the downturn years
"""
import numpy as np
import pandas as pd

from common import OUT, load_cpi_monthly, load_fy_prices, load_market, load_shiller, load_usdnok_daily, save_table

MKT = load_market()
FIN = pd.read_csv(OUT / "financials_annual.csv", index_col=0)


def asof(series: pd.Series, date) -> float:
    return float(series.loc[: pd.Timestamp(date)].iloc[-1])


def usdnok_stats(nok: pd.Series) -> pd.DataFrame:
    end = nok.index[-1]
    m = nok.resample("ME").mean()
    vol10 = np.log(m.loc[end - pd.DateOffset(years=10):]).diff().std() * np.sqrt(12)
    out = {
        "spot": nok.iloc[-1], "spot_date": str(end.date()),
        "avg_5y": nok.loc[end - pd.DateOffset(years=5):].mean(),
        "avg_10y": nok.loc[end - pd.DateOffset(years=10):].mean(),
        "avg_20y": nok.loc[end - pd.DateOffset(years=20):].mean(),
        "min_since_2000": nok.loc["2000":].min(), "min_date": str(nok.loc["2000":].idxmin().date()),
        "max_since_2000": nok.loc["2000":].max(), "max_date": str(nok.loc["2000":].idxmax().date()),
        "annualised_vol_10y_monthly": vol10,
    }
    return pd.Series(out).to_frame("value")


def returns_usd_vs_nok(nok: pd.Series) -> pd.DataFrame:
    px = load_fy_prices()
    shiller = load_shiller()
    # Visa total return: FY-end prices plus dividends per share (dividends paid / diluted shares)
    tr = 1.0
    for fy in range(2016, 2026):
        dps = FIN.loc[fy, "dividends_paid"] / FIN.loc[fy, "diluted_shares_derived"]
        tr *= (px.loc[fy, "close_unadjusted"] + dps) / px.loc[fy - 1, "close_unadjusted"]
    tr *= (MKT["V_close"] + 0.67 * 4) / px.loc[2025, "close_unadjusted"]   # Oct 2025 - 16 Oct 2026
    start, end = pd.Timestamp("2015-09-30"), pd.Timestamp("2026-10-16")
    years = (end - start).days / 365.25
    fx0, fx1 = asof(nok, start), asof(nok, end)
    v_price = MKT["V_close"] / px.loc[2015, "close_unadjusted"]
    spx_price = shiller.loc["2026-09-01", "SP500"] / shiller.loc["2015-09-01", "SP500"]
    rows = []
    for name, mult in (("Visa total return (dividends not reinvested)", tr), ("Visa price only", v_price),
                       ("S&P 500 price only (monthly avg, Sep 2015 - Sep 2026)", spx_price)):
        rows.append({"series": name, "multiple_usd": mult, "cagr_usd": mult ** (1 / years) - 1,
                     "multiple_nok": mult * fx1 / fx0, "cagr_nok": (mult * fx1 / fx0) ** (1 / years) - 1})
    df = pd.DataFrame(rows)
    df.attrs.update(years=years, fx0=fx0, fx1=fx1)
    df["usdnok_start"], df["usdnok_end"], df["years"] = fx0, fx1, years
    return df


def fx_equity_correlation(nok: pd.Series) -> pd.DataFrame:
    shiller = load_shiller()
    spx = shiller["SP500"].loc["2000":]
    fxm = nok.resample("MS").mean().loc["2000":]
    d = pd.concat({"spx": spx.pct_change(), "usdnok": fxm.pct_change()}, axis=1).dropna()
    down = d[d["spx"] < -0.03]
    return pd.DataFrame({
        "months": [len(d)],
        "correlation_spx_vs_usdnok": [d["spx"].corr(d["usdnok"])],
        "avg_usdnok_change_when_spx_down_3pct": [down["usdnok"].mean()],
        "n_down_months": [len(down)],
        "avg_usdnok_change_all_months": [d["usdnok"].mean()],
    })


def fx_in_drawdowns(nok: pd.Series) -> pd.DataFrame:
    episodes = [("2008-09 financial crisis", "2008-05-07", "2009-01-20"),
                ("2020 COVID crash", "2020-02-19", "2020-03-23"),
                ("2022 inflation shock", "2022-02-02", "2022-09-30")]
    rows = []
    for name, a, b in episodes:
        f0, f1 = asof(nok, a), asof(nok, b)
        rows.append({"episode": name, "start": a, "end": b, "usdnok_start": f0, "usdnok_end": f1,
                     "usdnok_change": f1 / f0 - 1})
    return pd.DataFrame(rows)


def cpi_vs_growth() -> pd.DataFrame:
    cpi = load_cpi_monthly()
    rows = []
    for fy in range(2016, 2026):
        infl = cpi.loc[f"{fy}-09-01"] / cpi.loc[f"{fy - 1}-09-01"] - 1
        rows.append({"fiscal_year": fy, "us_cpi_inflation_sep": infl,
                     "visa_net_revenue_growth": FIN.loc[fy, "net_revenue_growth"],
                     "visa_processed_tx_growth": FIN.loc[fy, "processed_transactions_growth"],
                     "visa_payments_volume_growth_12m_june": FIN.loc[fy, "payments_volume_jun_growth"],
                     "visa_cross_border_growth": FIN.loc[fy, "cross_border_growth_ex_europe"] / 100
                     if pd.notna(FIN.loc[fy, "cross_border_growth_ex_europe"]) else np.nan})
    df = pd.DataFrame(rows).set_index("fiscal_year")
    df["real_revenue_growth"] = (1 + df["visa_net_revenue_growth"]) / (1 + df["us_cpi_inflation_sep"]) - 1
    return df


def downturns() -> pd.DataFrame:
    # facts M10-M12 in data/qualitative_facts.csv
    return pd.DataFrame([
        {"episode": "2008-09 financial crisis", "visa_drawdown": -0.521, "spx_drawdown": -0.568,
         "visa_revenue_growth_in_downturn_fy": 0.10, "note": "FY2009 operating revenue +10% (6,911 vs 6,263); Q4 FY2009 payments volume -2%"},
        {"episode": "2020 COVID crash", "visa_drawdown": -0.364, "spx_drawdown": -0.339,
         "visa_revenue_growth_in_downturn_fy": FIN.loc[2020, "net_revenue_growth"],
         "note": "FY2020 net revenue -4.9%; cross-border ex-Europe -22%; payments volume +2% (constant $); prior peak regained 28 Aug 2020"},
        {"episode": "2022 inflation shock", "visa_drawdown": -0.245, "spx_drawdown": -0.254,
         "visa_revenue_growth_in_downturn_fy": FIN.loc[2022, "net_revenue_growth"],
         "note": "FY2022 net revenue +21.6% as travel reopened; drawdown was valuation (rates), not earnings"},
    ]).set_index("episode")


def main():
    nok = load_usdnok_daily()
    stats = usdnok_stats(nok)
    ret = returns_usd_vs_nok(nok)
    corr = fx_equity_correlation(nok)
    fxdd = fx_in_drawdowns(nok)
    cpi = cpi_vs_growth()
    dd = downturns()
    for df, name, idx in ((stats, "usdnok_stats", True), (ret, "returns_usd_vs_nok", False),
                          (corr, "fx_equity_correlation", False), (fxdd, "fx_in_drawdowns", False),
                          (cpi, "cpi_vs_visa_growth", True), (dd, "downturns", True)):
        save_table(df, name, index=idx)
    with pd.option_context("display.float_format", "{:,.4f}".format, "display.width", 220):
        for df in (stats, ret, corr, fxdd, cpi, dd):
            print(df.to_string(), "\n")


if __name__ == "__main__":
    main()
