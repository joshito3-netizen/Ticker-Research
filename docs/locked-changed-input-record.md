# Locked Changed-Input Record

Precommit timestamp:10/19/2026 9:14PM
Pre-run commit hash:[main 2d1ff1c] Record Al-assisted locked-input prediction
Committer: Josh Clawson <joshclawson@Joshs-MacBook-Pro-2.local>
Your name and email address were configured automatically based on your username and hostname. Please check that they are accurate.
You can suppress this message by setting them explicitly. Run the following command and follow the instructions in your editor to edit your configuration file:
git config --global --edit
After doing this, you may fix the identity used for this commit with:
git commit --amend --reset-author
1 file changed, 97 insertions (+)
create mode 100644 docs/locked-changed-input-record.md
2d1ff1c6a0669ee00f8ccc26b502be344dae5127
(base) joshclawson@Joshs-MacBook-Pro-2 Ticker-Research %
Material input: Forecast depreciation rate
Input location: data/model_inputs.json, base_drivers.depreciation_rate
Old value: 10.0%
New value: 11.0%
Units: Percentage of opening PP&E plus half of current additions

## Expected output direction

Write what you expect to happen to:
I expect depreciation expense to increase in every forecast year because the model applies the higher depreciation rate to opening PP&E plus half of current additions.

I expect EBITDA to remain unchanged because the model calculates EBITDA before depreciation. EBIT and the EBIT margin should decrease because the additional depreciation is deducted from EBITDA.

Pretax income, income-tax expense, net income, and EPS should decrease. Tax expense should decline because the additional depreciation reduces taxable operating income.

I expect operating cash flow to increase slightly. Although net income should decline, depreciation is a noncash expense added back when calculating operating cash flow. The tax reduction should therefore create a cash benefit.

I expect FCFF to increase because the additional depreciation reduces NOPAT by only the after-tax amount while the entire noncash depreciation expense is added back. This produces a depreciation tax shield.

Ending cash should increase as the higher operating cash flow accumulates. In later years, the additional cash may also produce slightly higher interest income.

I expect PP&E to decrease because the model subtracts more depreciation from the PP&E balance. 
Revenue, EBITDA, capital expenditures, and working capital should not be directly affected.
Because forecast FCFF should increase, I expect the present value of explicit FCFF, terminal value, enterprise value, equity value, and value per diluted share to increase.

I expect the balance-sheet, cash, PP&E, finance-lease, equity, and FCFF reconciliation checks to 
continue passing.  ## Variables expected to remain unchanged

I expect the following to remain unchanged:

Segment revenue and total revenue

Revenue-growth assumptions

EBITDA and EBITDA-margin assumptions

Cash capital expenditures

New finance-lease additions

Working-capital assumptions

Stock-compensation assumptions

Debt and finance-lease assumptions

WACC

Terminal-growth rate

Diluted share count



Market price

These items are driven by separate assumptions and should not be directly changed by the depreciation-rate input.

## Expected Decision Effects

I expect the recommendation to remain WATCH / DEFER.

The higher depreciation rate should increase FCFF and estimated value through the depreciation tax shield. However, the current base DCF value of $230.21 per diluted share and the current upside value of $356.33 are both substantially below the $491.65 market price. A one-percentage-point increase in the depreciation rate is unlikely to close that valuation gap or support initiating a position..

## Failure conditions

I would consider the result unexpected or evidence of a broken linkage if:

Depreciation expense does not increase.

EBIT does not decrease.

Income-tax expense increases instead of decreasing.

FCFF or operating cash flow decreases without an identifiable offsetting mechanism.

Revenue, EBITDA, cash capex, or working capital changes.

Enterprise value or value per share decreases despite higher FCFF.

Any balance-sheet, cash, PP&E, finance-lease, equity, or FCFF reconciliation check fails.

The recommendation changes without the resulting valuation range approaching or exceeding the market price.


## Post-run result

Actual output change:
Actual decision effect:
Prediction matched, partially matched, or failed:
Failure diagnosis or no-change reason:
Evidence path:

