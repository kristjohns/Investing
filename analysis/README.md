# Visa analysis: scripts and data

Everything quoted in `../visa_report.md` is produced here. Run from the repository root:

```
pip install pandas numpy matplotlib
python analysis/run_all.py                  # downloads public data, then runs every step
python analysis/run_all.py --skip-download  # reuse analysis/data/raw/
```

| Script | What it does | Main outputs (`analysis/output/`) |
|---|---|---|
| `fetch_public_data.py` | Downloads USD/NOK (Fed H.10), Shiller S&P 500, US CPI and 10-year yield mirrors; `--direct` also tries FRED / Norges Bank | `data/raw/*.csv` |
| `financials.py` | FY2015-25 table, derived ratios, 31 consistency checks, trailing 12 months | `financials_annual.csv`, `consistency_checks.csv`, `growth_summary.csv`, `ttm.csv` |
| `valuation.py` | Multiples vs history / Mastercard / S&P 500, DCF, reverse DCF, sensitivities | `valuation_*.csv`, `dcf_*.csv`, `reverse_dcf.csv` |
| `scenarios.py` | Bear/base/bull, probability-weighted return, NOK paths, index comparison, buy-below prices | `scenarios*.csv`, `buy_below_prices.csv`, `return_sensitivity_5y.csv` |
| `macro_fx.py` | USD/NOK statistics, NOK vs USD returns, FX in drawdowns, CPI vs growth | `usdnok_stats.csv`, `returns_usd_vs_nok.csv`, `fx_*.csv`, `downturns.csv` |
| `norway_tax.py` | After-tax illustration for a NOK 40,000 position (ordinary account vs ASK index fund) | `norway_*.csv` |
| `charts.py` | All figures | `../charts/*.png` |
| `verify_with_sec_xbrl.py` | Optional: re-checks compiled figures against SEC XBRL (needs internet + `SEC_USER_AGENT`) | `xbrl_crosscheck.csv` |
| `build_pdf.py` | Renders `visa_report.md` to an A4 PDF with charts, contents page and bookmarks (`pip install markdown-it-py mdit-py-plugins linkify-it-py playwright`; set `CHROMIUM_PATH` or run `playwright install chromium`) | `../visa_report.pdf` |

## Data files (`analysis/data/`)

- `visa_annual.csv`: one row per Visa figure (fiscal year, metric, value, unit, `source_id`, note).
- `visa_quarterly.csv`: 9-month and quarterly FY2025/FY2026 figures used for the trailing 12 months.
- `market_data.csv`, `visa_fy_end_prices.csv`, `mastercard_annual.csv`: market and peer data with sources.
- `qualitative_facts.csv`: dated facts behind the legal, competition, macro and Norway sections.
- `sources.csv`: full citation for every `source_id`.

**Provenance caveat.** The environment that produced this could not reach sec.gov, FRED or Norges Bank directly. Company figures were transcribed from the cited filings via web search and validated by the consistency checks. Edit any CSV value and rerun `run_all.py` to see how the conclusions change. The assumptions are at the top of `valuation.py` and `scenarios.py`.
