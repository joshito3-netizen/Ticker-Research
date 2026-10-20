# Validation and AI Use — Working Record

## Decision, version, and as-of boundary

- Decision/user: watch/defer MSFT for a buy-side committee with no current position.
- Decision horizon: 12 months; no 12-month price forecast is claimed.
- Financial-statement date: June 30, 2026.
- Filing availability: July 29, 2026.
- Market comparison and evidence cutoff: September 9, 2026.
- Run environment: Python 3 standard-library engine; Streamlit interface dependency.
- Repository commit/tag: [ENTER AFTER REVIEW AND COMMIT].
- Frozen run timestamp: generated in outputs/visible_output.json; update at final freeze.

## Data and convention ledger

| Material input | Source | As-of/availability | Definition/units | Transformation/exclusion | Risk |
|---|---|---|---|---|---|
| FY2026 statements and segments | MSFT FY2026 10-K, Item 8 and Notes 2/10/13/18 | 2026-06-30 / filed 2026-07-29 | USD millions; GAAP | Mapped into source JSON; opening balance sheet reconciles | XBRL/label mapping and aggregation |
| FY2026 net income/EPS | 10-K and Microsoft FY26 release | Public 2026-07-29 | $133,749m; $17.95 diluted EPS | Remove $4,963m after-tax OpenAI gain; normalized NI $128,786m/EPS $17.28 | Other discrete items may remain |
| Cash PP&E additions | 10-K cash flows | FY ended 2026-06-30 | $115,948m cash outflow | Full amount treated as economic reinvestment | Growth versus maintenance not separated |
| Finance leases | 10-K Note 13 | 2026-06-30 | $24,608m new assets; $66,594m liabilities | New assets reduce FCFF; opening liability deducted in bridge | Classification can shift; off-BS commitments remain |
| Cash and short investments | 10-K balance sheet | 2026-06-30 | $76,843m | Reserve 2% of revenue; excess added to equity | Reserve is judgment; tax/liquidity constraints |
| Term debt | 10-K balance sheet | 2026-06-30 | $40,294m carrying amount | Deducted from EV | Carrying amount differs from market value |
| Diluted shares | 10-K Note 2 | FY2026 | 7,453m weighted-average diluted | Fixed denominator | Not point-in-time fully diluted shares |
| Market price | Stock Analysis historical table | 2026-09-09 close | $491.65 unadjusted close | Reverse DCF and decision comparison | Third-party table; not a filing fact |
| Salesforce peer inputs | CRM FY2026 10-K; same-date price table | FY ended 2026-01-31; price 2026-09-09 | GAAP diluted EPS, revenue, shares, cash, securities, debt | P/E and EV/Revenue kept separate | Single peer; fiscal-window and mix mismatch |

## Validation register

| Claim/output | Failure mode | Test and expected result/direction | Actual result | Disposition | Evidence location |
|---|---|---|---|---|---|
| DCF engine | Formula error | Training grid must reproduce nine published answers | All nine cells match to cents | Pass | tests/test_analysis.py, known-answer test |
| Base year | Source mapping does not articulate | Assets $758,376m; liabilities $315,989m; gap zero | Exact match; gap zero | Pass | base-year articulation test |
| Forecast statements | Hidden plug or cash mismatch | BS, cash, PP&E, lease, equity, FCFF gaps zero annually | All five years pass | Pass | analysis.py checks; visible output |
| DCF boundaries | Wrong monotonicity | Higher WACC lowers value; higher g raises value | $276.30 at 8.5% vs $196.51 at 10.5%; $203.51 at 2% g vs $266.62 at 4% | Pass | WACC/growth test |
| Enterprise-equity bridge | Sign/double-count error | EV + excess cash + investment value − debt − finance leases = equity | Identity passes; ending cash not used | Pass | bridge identity test |
| Directional changed input | Broken causal link | Cloud +1 point raises value; cash capex +1 point lowers value | $234.84 (+$4.63); $219.94 (−$10.27) | Pass | directional changed-input test |
| Highest-risk lease treatment | Lease-funded capacity treated as free | Removing new lease investment must raise apparent value, demonstrating omission bias | Value rises from $230.21 to $288.55 (+$58.34) | Pass; omission rejected | finance-lease omission test |
| Invalid terminal boundary | Division/false output | g ≥ WACC must raise an error | Explicit ValueError | Pass | invalid-terminal test |
| Peer definitions | P/E/EV mixing or wrong bridge | P/E has no bridge; EV/Revenue includes debt, leases, cash | CRM P/E 31.3026x; EV/Revenue 5.7385x; Oracle remains excluded | Pass/qualified | comparable definition test |
| Reverse DCF | Bound returned as solution | Bisection must hit price or report no solution | +20.61-point uniform growth shift reproduces $491.65 | Pass/qualified | reverse_dcf_growth_shift |
| Cold run | Undocumented local dependency | Fresh environment follows README and reproduces output/tests/app | Fresh venv; 8/8 tests; HTTP 200; browser output and loud failure verified | Pass | outputs/cold-run-log.txt |

## Locked Changed-Input Record

**Preparation disclosure:** This prediction was drafted with Codex assistance under the
instructor's corrected email guidance permitting that assistance. The interaction is included in
the AI-use record below. The prior instruction in this document that prohibited AI assistance for
the prediction and execution is obsolete and has been removed.

**Precommit timestamp:** 2026-10-19 20:38:12 EDT

**Repository commit:** `16c83f95af80df7a54b7f52ca596f02a3b031d9a`

**Test status:** Prediction recorded before execution; the changed-input run has not been executed.

**Material input:** Forecast effective tax rate

**Input location:** `data/model_inputs.json`, `drivers.tax_rate`

**Old value:** 20.0%

**New value:** 22.0%

**Change:** Increase of 2.0 percentage points

**Units:** Percentage of positive pretax income and positive operating income

### Expected output direction

I expect the higher tax rate to increase forecast tax expense and reduce net income, diluted EPS,
NOPAT, operating cash flow, economic FCFF, ending cash, enterprise value, equity value, and DCF
value per diluted share.

Revenue, EBITDA, EBIT, capital expenditures, working-capital requirements, WACC, terminal growth,
debt, finance-lease liabilities, and diluted shares should remain unchanged because this is a
one-input test.

The effect should occur in every forecast year. The lower FY2031 FCFF should also reduce terminal
value because terminal FCFF is calculated from FY2031 FCFF. Because terminal value represents
approximately 81% of the current enterprise value, the terminal-value reduction should account
for a substantial portion of the valuation change.

All balance-sheet, cash, PP&E, lease, equity, and FCFF-reconciliation checks should continue to
pass. If value rises, remains exactly unchanged, or an articulation check fails, I will treat the
result as evidence that the tax assumption is not propagating correctly or that the model contains
a sign, linkage, or reconciliation error.

### Expected decision effect

I expect the committee decision to remain **watch/defer; do not initiate at the current price**.

The current base DCF value is $230.21 per diluted share, the causal valuation range is
$112.21–$356.33, and the saved market price is $491.65. Increasing the tax rate should reduce the
modeled values rather than close the gap with the market price. The test should therefore reinforce
the watch/defer conclusion without changing its classification.

The decision would not improve to initiate under this change. A materially lower valuation could
strengthen the case for do not initiate, but I do not expect a two-percentage-point tax-rate
increase by itself to justify that stronger action because the existing recommendation already
reflects substantial uncertainty and calls for continued monitoring.

### Variables held constant

All revenue-growth paths, EBITDA margins, capital-investment ratios, depreciation, amortization,
working-capital ratios, stock compensation, debt and lease assumptions, cash yield, operating-cash
reserve, investment recovery, WACC, terminal growth, diluted shares, and market price will remain
at their base values.

### Post-run fields

**Actual output change:** [COMPLETE AFTER RUN]

**Actual decision effect:** [COMPLETE AFTER RUN]

**Prediction matched, partially matched, or failed:** [COMPLETE AFTER RUN]

**Failure diagnosis or reason the decision did not change:** [COMPLETE AFTER RUN]

**Evidence path:** [COMPLETE AFTER RUN]

## Named AI-use register

| Tool/model surface and exposed version | Interaction date | Material task | Output/claim used or considered | Independent check | Disposition | Effect on decision |
|---|---|---|---|---|---|---|
| Codex; exposed model/version not displayed | 2026-10-19 | Repository inventory and architecture | Preserve Edition A; separate statement, filing-availability, and valuation dates | Compared Edition A, Git history, course brief, and saved Week 3/4 files | Accept | Corrected timing boundary; recommendation unchanged |
| Codex; exposed model/version not displayed | 2026-10-19 | Filing research/model design | Treat new finance-lease assets as reinvestment and lease liabilities as an equity-bridge claim | Microsoft FY2026 10-K Note 13 and omission test | Accept | Lower, more economically complete value than cash-capex-only model |
| Codex; exposed model/version not displayed | 2026-10-19 | Code and validation | Three-statement engine, cases, sensitivity, comparables, app, and tests | Known answers; statement/bridge identities; monotonicity; source checks | Modify/accept subject to student review | Produced $112–$356 range and watch/defer draft |
| Codex; exposed model/version not displayed | 2026-10-19 | Peer analysis | Keep CRM as qualified application reference; calculate P/E and EV/Revenue separately | CRM 10-K definitions and saved same-date price evidence | Qualify | Conflicting $562 and $251 references are not averaged with DCF |
| Codex; exposed model/version not displayed | 2026-10-19 | Locked changed-input prediction drafting and record entry | Forecast-tax-rate prediction above | Assistance disclosed under the instructor's corrected email guidance; prediction committed before changing the input or running the test | Accept/pending test | Expected to reinforce watch/defer without changing the classification |

## Limitations, monitoring, and kill/escalation rules

- Accounting checks validate mechanics, not forecast accuracy.
- Terminal value is 81.0% of EV; any conclusion is conditional on steady-state economics.
- Aggregate depreciation, fixed shares, cash reserve, investment recovery, and working-capital
  ratios are simplifications.
- Escalate if combined cash capex plus new finance-lease assets stays above 30% of revenue while
  cloud growth falls below 20%, EBIT margin falls below 45%, or lease commitments rise without
  corresponding cash growth.
- Kill initiation while model price remains below market across the causal upside case, unless
  new sourced evidence changes the operating forecast and survives the same tests.
