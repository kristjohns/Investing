"""Bull / base / bear scenarios for a Visa purchase at the 16 Oct 2026 close.

Method: exit price = exit forward P/E x forward non-GAAP EPS at the exit date.
  * Start point: consensus FY2027 non-GAAP EPS (USD 14.94) = next-twelve-months EPS today.
  * EPS compounds at the scenario rate; dividends = 21% of EPS (current payout:
    USD 2.68 / TTM non-GAAP EPS 12.77), received yearly, not reinvested.
  * Return = IRR of (-price, dividends..., dividends + exit price).
Horizons: 5 years (Oct 2031) as asked, and 10 years (Oct 2036) to match the
investor's 10-20 year horizon. Probabilities are judgement, not data.

USD returns are translated to NOK under three USD/NOK paths, and compared with an
expected return for a global index fund.

Outputs: output/scenarios.csv, output/scenarios_nok.csv, output/index_comparison.csv,
         output/position_sizing.csv
"""
import numpy as np
import pandas as pd

from common import OUT, load_market, load_usdnok_daily, save_table

MKT = load_market()
PRICE = MKT["V_close"]
EPS_NTM = MKT["V_consensus_eps_fy2027"]
TTM = pd.read_csv(OUT / "ttm.csv", index_col=0)["ttm_jun2026"]
PAYOUT = 0.67 * 4 / TTM["eps_nongaap_diluted"]

SCENARIOS = {
    # name: probability, EPS CAGR yrs 1-5, EPS CAGR yrs 6-10, exit fwd P/E at 5y, exit fwd P/E at 10y
    "bear": dict(prob=0.25, g1=0.05, g2=0.04, pe5=18.0, pe10=16.0,
                 story="US credit routing law (CCCA) or a hard DOJ remedy, faster A2A/wallet "
                       "disintermediation (Pix/UPI/Wero/FedNow), rising incentives, a 2027 recession; "
                       "loses its premium and trades near today's S&P 500 forward multiple (19.0x)"),
    "base": dict(prob=0.50, g1=0.11, g2=0.09, pe5=24.0, pe10=22.0,
                 story="revenue growth fades from ~10% to ~8%, flat margins, ~2%/yr buybacks; "
                       "regulation is friction not structural damage; modest de-rating as growth matures "
                       "and long rates stay ~5%"),
    "bull": dict(prob=0.25, g1=0.14, g2=0.12, pe5=28.0, pe10=26.0,
                 story="value-added services, Visa Direct/B2B and agentic/stablecoin flows accelerate, "
                       "China licence, benign regulation (MDL settlement final, CCCA dies), "
                       "operating leverage; keeps a premium multiple"),
}

INDEX_EXPECTED = {
    # nominal USD, per year. The first is market-implied (Damodaran's implied ERP on top
    # of the current 10y Treasury yield, applied to the US market). The second is our own
    # lower-bound assumption: J.P. Morgan's 2026 LTCMA put a USD 60/40 portfolio at 6.4%;
    # if bonds earn ~5% (today's 10y yield), that implies roughly 7.3% for the equity part.
    "Market-implied: 10y UST 5.08% + Damodaran ERP 4.20%": 0.0508 + 0.042,
    "Lower bound: ~7% (our reading of J.P. Morgan 2026 LTCMA 60/40 = 6.4%)": 0.07,
}
HURDLES = (0.09, 0.10, 0.11, 0.12)  # target expected returns for the 'buy below' price


def irr(cashflows):
    lo, hi = -0.99, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        npv = sum(cf / (1 + mid) ** t for t, cf in enumerate(cashflows))
        lo, hi = (mid, hi) if npv > 0 else (lo, mid)
    return (lo + hi) / 2


def run(name, s, years, price=None):
    price = PRICE if price is None else price
    eps = [EPS_NTM]
    for t in range(1, years + 1):
        g = s["g1"] if t <= 5 else s["g2"]
        eps.append(eps[-1] * (1 + g))
    # dividends paid during year t ~ payout x EPS earned in year t (eps[t-1] is that year's NTM EPS)
    divs = [PAYOUT * eps[t - 1] for t in range(1, years + 1)]
    pe = s["pe5"] if years == 5 else s["pe10"]
    exit_price = pe * eps[years]
    cfs = [-price] + divs[:-1] + [divs[-1] + exit_price]
    r = irr(cfs)
    return {"scenario": name, "horizon_years": years, "probability": s["prob"], "eps_cagr_1_5": s["g1"],
            "eps_cagr_6_10": s["g2"] if years == 10 else np.nan, "exit_forward_pe": pe,
            "eps_at_exit_ntm": eps[years], "exit_price": exit_price, "dividends_received": sum(divs),
            "wealth_multiple": (exit_price + sum(divs)) / price, "annualised_return_usd": r, "story": s["story"]}


def expected_return_at(price, years):
    """Probability-weighted annualised return (expected ending wealth) at a purchase price."""
    ew = sum(s["prob"] * run(n, s, years, price)["wealth_multiple"] for n, s in SCENARIOS.items())
    return ew ** (1 / years) - 1


def buy_below(target, years, lo=50.0, hi=1000.0):
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if expected_return_at(mid, years) > target else (lo, mid)
    return (lo + hi) / 2


def main():
    rows = [run(n, s, h) for h in (5, 10) for n, s in SCENARIOS.items()]
    sc = pd.DataFrame(rows)
    summ = []
    for h in (5, 10):
        d = sc[sc["horizon_years"] == h]
        p = d["probability"]
        ew = (p * d["wealth_multiple"]).sum()           # expected ending wealth per USD invested
        summ.append({"scenario": "probability-weighted", "horizon_years": h, "probability": p.sum(),
                     "exit_price": (p * d["exit_price"]).sum(), "wealth_multiple": ew,
                     "annualised_return_usd": ew ** (1 / h) - 1,
                     "mean_of_scenario_returns": (p * d["annualised_return_usd"]).sum()})
    sc = pd.concat([sc, pd.DataFrame(summ)], ignore_index=True)

    # NOK translation: USD/NOK paths over the horizon
    nok = load_usdnok_daily()
    spot, spot_date = nok.iloc[-1], nok.index[-1].date()
    fx_paths = {"NOK strengthens to 8.50": 8.50, f"flat at {spot:.2f}": spot, "NOK weakens to 10.50": 10.50}
    nrows = []
    for _, r in sc.iterrows():
        for label, end_fx in fx_paths.items():
            fx_factor = (end_fx / spot) ** (1 / r["horizon_years"])
            nrows.append({"scenario": r["scenario"], "horizon_years": r["horizon_years"], "fx_path": label,
                          "annualised_return_nok": (1 + r["annualised_return_usd"]) * fx_factor - 1})
    sc_nok = pd.DataFrame(nrows)

    idx = []
    for h in (5, 10):
        pw = sc[(sc["scenario"] == "probability-weighted") & (sc["horizon_years"] == h)].iloc[0]
        for lbl, er in INDEX_EXPECTED.items():
            idx.append({"horizon_years": h, "index_assumption": lbl, "index_expected_return": er,
                        "visa_prob_weighted_return": pw["annualised_return_usd"],
                        "visa_minus_index": pw["annualised_return_usd"] - er})
    idx = pd.DataFrame(idx)

    sizes = []
    for port in (200_000, 500_000, 1_000_000, 2_000_000):
        for amt in (30_000, 40_000, 50_000):
            sizes.append({"portfolio_nok": port, "visa_position_nok": amt, "weight": amt / port,
                          "visa_lookthrough_in_index_fund_nok": port * 0.0057})
    sizes = pd.DataFrame(sizes)

    bb = pd.DataFrame([{"target_expected_return": t, "horizon_years": h, "buy_below_price": buy_below(t, h),
                        "implied_forward_pe_fy2027e": buy_below(t, h) / EPS_NTM,
                        "discount_to_current": buy_below(t, h) / PRICE - 1}
                       for h in (5, 10) for t in HURDLES])
    save_table(bb, "buy_below_prices", index=False)

    # 5-year return sensitivity around the base case: EPS CAGR x exit forward P/E
    grid = pd.DataFrame(
        [[run("grid", dict(prob=1, g1=g, g2=g, pe5=pe, pe10=pe, story=""), 5)["annualised_return_usd"]
          for pe in (18, 20, 22, 24, 26, 28, 30)] for g in (0.07, 0.09, 0.11, 0.13, 0.15)],
        index=[f"{g:.0%}" for g in (0.07, 0.09, 0.11, 0.13, 0.15)],
        columns=[f"{pe}x" for pe in (18, 20, 22, 24, 26, 28, 30)])
    grid.index.name = "EPS CAGR FY27-32 \\ exit forward P/E"
    save_table(grid, "return_sensitivity_5y")

    save_table(sc, "scenarios", index=False)
    save_table(sc_nok, "scenarios_nok", index=False)
    save_table(idx, "index_comparison", index=False)
    save_table(sizes, "position_sizing", index=False)
    save_table(pd.Series({"price": PRICE, "eps_ntm": EPS_NTM, "payout": PAYOUT, "usdnok_spot": spot,
                          "usdnok_date": str(spot_date)}).to_frame("value"), "scenario_inputs")

    with pd.option_context("display.float_format", "{:,.3f}".format, "display.width", 220,
                           "display.max_colwidth", 40):
        print(f"payout {PAYOUT:.3f}; USD/NOK spot {spot:.4f} on {spot_date}")
        print(sc.drop(columns=["story"]).to_string(index=False))
        print(sc_nok.pivot_table(index=["horizon_years", "scenario"], columns="fx_path",
                                 values="annualised_return_nok").to_string())
        print(idx.to_string(index=False))
        print(bb.to_string(index=False))


if __name__ == "__main__":
    main()
