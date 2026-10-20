# Locked Changed-Input Test Evidence — Forecast Tax Rate

## Run identity

- Prediction/pre-run commit: `16c83f95af80df7a54b7f52ca596f02a3b031d9a`
- Changed-input result commit: `0fbb8eb5543ed2cd6c721a092d0e5ce64ed81716`
- Prediction timestamp: 2026-10-19 20:38:12 EDT
- Execution timestamp: 2026-10-19 20:40:50 EDT
- Input changed: `data/model_inputs.json`, `base_drivers.tax_rate`
- Old value: 20.0%
- New value: 22.0%
- All amounts are USD millions except per-share values.

The input was changed only after the prediction was committed. The same `analysis.py` engine was
then executed. This file preserves the result before the project input is restored to its 20.0%
base-case value.

## Valuation result

| Output | 20.0% tax | 22.0% tax | Change |
|---|---:|---:|---:|
| DCF value per diluted share | $230.21 | $220.39 | **-$9.82** |
| Downside value per share | $112.21 | $106.41 | -$5.80 |
| Upside value per share | $356.33 | $342.52 | -$13.81 |
| Enterprise value | $1,734,267.8 | $1,661,064.3 | **-$73,203.5** |
| Equity value | $1,715,760.1 | $1,642,556.5 | **-$73,203.5** |
| PV of explicit FCFF | $330,237.8 | $313,011.3 | -$17,226.5 |
| PV of terminal value | $1,404,030.0 | $1,348,053.0 | -$55,977.1 |
| Terminal-value share of EV | 80.96% | 81.16% | +0.20 pp |

The absolute present value of the terminal component fell by $55,977.1m and accounted for 76.5%
of the $73,203.5m enterprise-value decline. Its *share* of enterprise value rose slightly because
the explicit-period component declined proportionally more; this does not contradict the predicted
decline in terminal value.

## Forecast propagation

| Year | Tax expense change | Net income change | EPS change | CFO change | NOPAT/FCFF change | Ending cash change |
|---:|---:|---:|---:|---:|---:|---:|
| 2027 | +$3,576.3 | -$3,576.3 | -$0.48 | -$3,576.3 | -$3,620.0 | -$3,576.3 |
| 2028 | +$4,010.5 | -$4,117.8 | -$0.55 | -$4,117.8 | -$4,075.3 | -$7,694.1 |
| 2029 | +$4,481.0 | -$4,711.8 | -$0.63 | -$4,711.8 | -$4,560.6 | -$12,405.9 |
| 2030 | +$4,967.7 | -$5,339.9 | -$0.72 | -$5,339.9 | -$5,054.3 | -$17,745.8 |
| 2031 | +$5,477.4 | -$6,009.8 | -$0.81 | -$6,009.8 | -$5,561.1 | -$23,755.6 |

NOPAT and FCFF changed by identical amounts in every year because the operating-tax change flows
directly through NOPAT while the other FCFF components remain fixed. The growing difference between
tax expense and net income reflects lower interest income as the lower after-tax cash balance rolls
forward.

## Held-constant and articulation checks

The maximum absolute before/after difference was exactly zero for revenue, EBITDA, EBIT, cash
capital expenditures, new finance-lease assets, change in working capital, and finance-lease
liabilities in all five forecast years. WACC remained 9.5%; terminal growth remained 3.0%; diluted
shares remained 7,453m; market price remained $491.65; and the enterprise-to-equity bridge claims
were unchanged.

All yearly balance-sheet, cash, PP&E, finance-lease, equity, and FCFF-reconciliation gaps remained
within the model's $0.000001m tolerance. The base-year reconciliation also continued to pass.

## Prediction reconciliation and decision effect

**Matched.** Every predicted directional effect occurred, every specified held-constant field stayed
fixed, and every articulation check passed. The committee action remained **watch/defer; do not
initiate at the current price**. The higher tax rate lowered the entire causal range and therefore
widened, rather than closed, the gap to the $491.65 market price. No failure diagnosis was required;
the classification did not change because the pre-test upside case was already below market and the
changed input can only reduce value in this model.
