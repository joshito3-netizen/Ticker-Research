# Microsoft Pro-Forma Valuation Workbench

## Finance decision and intended user

This locally runnable system supports a buy-side investment committee deciding whether to
initiate Microsoft (`MSFT`) common stock when the fund holds no position. The committee action is
**watch/defer** over a 12-month decision horizon: the September 9, 2026 market close of $491.65 is
above the model's $112–$356 causal DCF range. Re-underwrite if price enters that range or sourced
evidence supports materially higher cloud cash returns without persistent cash and finance-lease
investment.

The financial-statement date is June 30, 2026; the FY2026 10-K became available July 29, 2026;
the valuation and evidence cutoff is September 9, 2026. Currency is USD, statement units are USD
millions, and per-share values use 7,453 million FY2026 weighted-average diluted shares.

Relevant exclusions: no transaction method is used because no defensible control/synergy/time
match was identified; operating leases remain in operating costs and are not separately deducted;
forecast investment gains and acquisitions are excluded; Salesforce is a qualified reference,
not a whole-company twin; Oracle remains documented but excluded under the narrowed application
peer policy.

## Visible result

[Visible executed output](outputs/visible_output.md) shows the dated inputs, five-year forecast,
valuation range, enterprise-to-equity bridge, peer references, sensitivity ranking, conditions,
limitations, and checks without requiring execution. The machine-readable interface contract is
[`outputs/visible_output.json`](outputs/visible_output.json).

## Setup and run

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 analysis.py
python3 -m unittest discover -s tests -v
streamlit run app.py
```

`analysis.py` uses only the Python standard library. Streamlit is required only for the bounded
interface. No credentials or network calls are needed at run time.

## Repository map

- `project-1-edition-a-microsoft.md` — unchanged Edition A baseline; never overwrite it.
- `data/model_inputs.json` — source-dated filing facts, assumptions, bounds, and peer policy.
- `analysis.py` — three-statement forecast, FCFF DCF, bridge, cases, reverse DCF, comparables,
  checks, and visible-output export.
- `app.py` — bounded driver panel, base reset, statements, sensitivities, evidence, and loud checks.
- `tests/test_analysis.py` — known answer, articulation, monotonicity, bridge, peer-definition,
  directional-input, and highest-risk lease tests.
- `outputs/visible_output.md` / `.json` — frozen visible executed result.
- `docs/` — research evolution, memo, validation/AI-use record, manifest, and transcript drafts.
- Earlier weekly lab files remain as development history; the files above govern the final system.

## Analysis-to-interface flow

1. Filing and market facts plus analyst assumptions live in `data/model_inputs.json`.
2. `analysis.py` validates driver boundaries, builds FY2027–FY2031 statements, and fails if the
   balance sheet, cash roll, PP&E, lease liability, equity, or FCFF reconciliation breaks.
3. The same engine computes causal cases, WACC/growth sensitivity, reverse DCF, comparable
   references, and one-at-a-time operating sensitivities.
4. A successful run deliberately exports the audience subset to `outputs/visible_output.json`
   and `.md`; these are generated results, not hand-entered analysis.
5. `app.py` calls the same engine with bounded controls. The app contains no separate valuation.

## Data sources and conventions

Primary filing: [Microsoft FY2026 Form 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm),
filed July 29, 2026. Microsoft's [FY2026 earnings release](https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast)
cross-checks the statements, segment results, shares, and the $4.963 billion after-tax OpenAI gain.
Salesforce inputs trace to its [FY2026 Form 10-K](https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm).
Historical prices use the dated, unadjusted closing-price rows preserved in the Week 4 work and
linked in `data/model_inputs.json`.

The FY2026 base is normalized by removing the after-tax OpenAI investment gain from reported net
income. Forecast other income includes cash yield and debt/finance-lease interest but no recurring
investment gain. Economic FCFF subtracts both cash PP&E additions and new finance-lease assets;
the equity bridge separately deducts opening finance-lease liabilities.

## Known limitations

- The 12-month action is informed by a long-duration valuation, not a 12-month price forecast.
- Forecast paths and WACC are analyst estimates, not management guidance or probabilities.
- D&A uses an aggregate PP&E schedule; useful lives and commissioning dates are not modeled asset by asset.
- A fixed diluted-share proxy and buybacks equal to stock compensation do not model vesting or repurchase price.
- One qualified peer provides reference estimates, not a statistical peer range.
- Terminal value remains material; accounting agreement validates mechanics, not forecast truth.

See `docs/validation-and-ai-use.md` for test evidence, AI-use disclosure, and the committed Locked
Changed-Input prediction. Its post-run fields remain incomplete until the tax-rate test is run.
