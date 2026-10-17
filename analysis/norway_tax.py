"""Illustrative after-tax outcome for a Norwegian personal investor (NOK 40,000).

Compares, over 10 years and before brokerage fees:
  A) Visa held in an ordinary securities account (Visa is US-domiciled, so it is NOT
     eligible for aksjesparekonto/ASK): dividends taxed yearly, gain taxed on sale.
  B) A global equity index fund held in an ASK: no tax until withdrawal above the
     deposited amount; the gain is then taxed at the same rate.

Rules used (see data/qualitative_facts.csv N1-N4 and the report for sources):
  * share income (dividends and gains) x 1.72 x 22% = 37.84% effective (2025 and 2026)
  * shielding deduction (skjermingsfradrag) = cost basis x shielding rate, deductible
    against dividends first, unused amounts carried forward to the gain on sale.
    The rate is set yearly; SHIELD_RATE below is an ASSUMPTION for illustration.
  * US withholding 15% on dividends with a W-8BEN (US-Norway treaty); credit in Norway
    is limited to the Norwegian tax on that dividend. If the shielding deduction removes
    the Norwegian tax, the US tax cannot be credited that year (check with Skatteetaten).
  * Wealth tax treats listed shares and equity funds alike (80% valuation) - ignored here.
Gains/losses are computed in NOK, so currency moves are part of the taxable gain.
"""
import pandas as pd

from common import OUT, load_market, save_table

MKT = load_market()
AMOUNT_NOK = 40_000
TAX = 0.22 * 1.72
US_WHT = 0.15
SHIELD_RATE = 0.03          # ASSUMPTION (recent published rates have been ~2.5-3.6% per secondary sources)
YEARS = 10


def visa_after_tax(usd_return_price: float, div_yield: float, fx_start: float, fx_end: float):
    """Visa in an ordinary account. Price grows at usd_return_price; dividend yield on price."""
    fx_path = [fx_start * (fx_end / fx_start) ** (t / YEARS) for t in range(YEARS + 1)]
    shares = AMOUNT_NOK / fx_start / MKT["V_close"]
    price = MKT["V_close"]
    carry_shield, net_divs, us_tax_lost = 0.0, 0.0, 0.0
    for t in range(1, YEARS + 1):
        price *= 1 + usd_return_price
        div_nok = shares * price * div_yield * fx_path[t]
        shield = AMOUNT_NOK * SHIELD_RATE + carry_shield
        taxable = max(div_nok - shield, 0.0)
        carry_shield = max(shield - div_nok, 0.0)
        no_tax_before_credit = taxable * TAX
        us_tax = div_nok * US_WHT
        credit = min(us_tax, no_tax_before_credit)
        us_tax_lost += us_tax - credit
        net_divs += div_nok - us_tax - (no_tax_before_credit - credit)
    value_nok = shares * price * fx_path[-1]
    gain = value_nok - AMOUNT_NOK
    tax_on_gain = max(gain - carry_shield, 0.0) * TAX
    return {"pre_tax_value": value_nok, "net_dividends_received": net_divs, "tax_on_sale": tax_on_gain,
            "after_tax_wealth": value_nok - tax_on_gain + net_divs, "us_withholding_not_credited": us_tax_lost,
            "unused_shield_at_sale": carry_shield}


def ask_fund_after_tax(total_return: float, fx_start: float, fx_end: float, fee: float = 0.002):
    """Index fund in ASK: total return (incl. reinvested dividends) less fee, taxed on withdrawal."""
    value = AMOUNT_NOK * ((1 + total_return - fee) ** YEARS) * (fx_end / fx_start)
    shield = AMOUNT_NOK * SHIELD_RATE * YEARS          # simplification: shielding accrues on deposit
    gain = value - AMOUNT_NOK
    tax = max(gain - shield, 0.0) * TAX
    return {"pre_tax_value": value, "net_dividends_received": 0.0, "tax_on_sale": tax,
            "after_tax_wealth": value - tax, "us_withholding_not_credited": float("nan"),
            "unused_shield_at_sale": max(shield - gain, 0.0)}


def main():
    sc = pd.read_csv(OUT / "scenarios.csv")
    base10 = sc[(sc["scenario"] == "base") & (sc["horizon_years"] == 10)].iloc[0]
    pw10 = sc[(sc["scenario"] == "probability-weighted") & (sc["horizon_years"] == 10)].iloc[0]
    fx = pd.read_csv(OUT / "scenario_inputs.csv", index_col=0)["value"]
    spot = float(fx["usdnok_spot"])
    div_yield = 0.67 * 4 / MKT["V_close"]
    rows = []
    for label, tot in (("Visa base case", base10["annualised_return_usd"]),
                       ("Visa probability-weighted", pw10["annualised_return_usd"])):
        price_growth = tot - div_yield          # approximate split of total return into price + dividend
        rows.append({"case": label, "assumed_total_return_usd": tot, **visa_after_tax(price_growth, div_yield, spot, spot)})
    for label, er in (("Global index fund in ASK, 7%/yr", 0.07), ("Global index fund in ASK, 9.3%/yr", 0.0928)):
        rows.append({"case": label, "assumed_total_return_usd": er, **ask_fund_after_tax(er, spot, spot)})
    df = pd.DataFrame(rows).set_index("case")
    df["after_tax_cagr"] = (df["after_tax_wealth"] / AMOUNT_NOK) ** (1 / YEARS) - 1
    save_table(df, "norway_after_tax_10y")
    year1 = {
        "shares_bought": AMOUNT_NOK / spot / MKT["V_close"],
        "usd_invested": AMOUNT_NOK / spot,
        "dividend_year1_nok_gross": AMOUNT_NOK * div_yield,
        "us_withholding_15pct_nok": AMOUNT_NOK * div_yield * US_WHT,
        "shield_deduction_year1_nok": AMOUNT_NOK * SHIELD_RATE,
        "effective_tax_rate_share_income": TAX,
    }
    save_table(pd.Series(year1).to_frame("value"), "norway_year1_illustration")
    with pd.option_context("display.float_format", "{:,.2f}".format, "display.width", 200):
        print(df.to_string())
        print(pd.Series(year1).to_string())


if __name__ == "__main__":
    main()
