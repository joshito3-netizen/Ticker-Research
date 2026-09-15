# Lab 07 — Comparable-Company Policy and Implied Range

## Reopen and explain: connection to Week 3

The saved Microsoft DCF was rerun using `python3 dcf.py` from its existing folder. It reproduces **$228.81 per share**, with a sensitivity range of **$180.23–$320.17**. Its editable assumptions include starting FCFF of $68,196 million, five annual growth rates of 20%, 16%, 13%, 10%, and 7%, WACC of 9.5%, and terminal growth of 3%. Higher cash flows or terminal growth raise value; a higher discount rate lowers value. The terminal component represents about 76% of enterprise value, making long-run assumptions especially influential. These are saved-model results, not newly verified financial inputs.

**Question to investigate:** When does a lower peer P/E reflect weaker growth, greater risk, or temporarily inflated earnings instead of an investment bargain?

## Define/Discover: what P/E tells us

Price per share is the market price for one ownership share. Diluted earnings per share (EPS) measures accounting profit attributable to each share using a share count that incorporates potentially dilutive securities. It is not cash distributed to investors. **P/E = price per share ÷ annual diluted EPS.** A 10× multiple means investors pay $10 for each $1 of annual earnings per share.

Dividing price by earnings puts differently sized companies on a common earnings basis. A peer comparison asks what Asbury would be worth if investors priced its earnings at similar businesses' multiples. It complements the DCF's forecast-based valuation with a market-based reference. Disagreement calls for investigation of assumptions and peers; the two answers should not automatically be averaged. The Microsoft DCF and Asbury comparison value different companies, so their dollar results are not competing valuations of the same asset.

P/E works best with positive, reasonably representative earnings and comparable business economics. Check earnings period, total versus continuing operations, GAAP versus adjusted results, dilution, currency consistency, and stock-split basis. Also assess growth, leverage, risk, geography, and profit mix. Negative or zero EPS does not provide a meaningful positive P/E valuation. A one-time gain can make P/E artificially low, while depressed earnings can make it high. A lower P/E may therefore reflect weaker prospects or greater risk rather than better value. [Source: course worked case, “Why use another company's price?” and “A frozen historical comparison.”](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/teach-comps-worked-example.md)

## Represent: business-based peer policy

Use publicly traded franchised vehicle retailers with new/used vehicle sales and meaningful service/parts activities. These activities explain how earnings are generated more directly than a broad automotive industry label. Compare geography, financing, acquisitions, and earnings definitions before choosing peers based on the resulting price.

| Company | Decision | Business evidence and qualification |
|---|---|---|
| Asbury (ABG) | Target; exclude from peer statistics | Vehicle sales, parts/service, and finance/insurance products form the business being valued. |
| AutoNation (AN) | Use | Similar vehicle retail and service activities support inclusion. AutoNation Finance adds lending exposure, so financing economics and credit risk deserve attention. |
| Group 1 (GPI) | Qualify; include in the base comparison | Core dealership activities fit. Its U.S./U.K. geography and acquisition of 54 Inchcape dealerships during 2024 create differences in market exposure and acquisition timing. |

These decisions follow the [case's business evidence and policy](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/teach-comps-worked-example.md#read-the-business-evidence-first). Both peers remain included in the base case. Removing GPI is a sensitivity exercise; a preferred lower price is not a reason to change the policy.

## Implement: frozen inputs and calculation

| Company | December 31, 2024 closing price | FY2024 total GAAP diluted EPS |
|---|---:|---:|
| ABG | $243.03 | $21.50 |
| AN | $169.84 | $16.92 |
| GPI | $421.48 | $36.81 |

This retrospective training exercise pairs year-end prices with annual earnings reported afterward. It is not a tradable December 31 information set. Use the original consistent split basis and total GAAP diluted EPS, including GPI's total earnings rather than its headline continuing-operations figure. The [case input table](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/teach-comps-worked-example.md#a-frozen-historical-comparison) links each proxy price locator and earnings release. No market data are fetched by the calculator.

**Worked arithmetic to practice independently:** AN-implied Asbury price = (169.84 ÷ 16.92) × 21.50 = **$215.81**. Keep the division unrounded until displaying the final price.

Run from the folder containing these files:

```sh
python3 lab07_asbury.py
```

The standard-library calculator has editable inputs at the top. It normalizes tickers, retains the first occurrence of each peer, excludes ABG, labels invalid calculations, and handles one or zero valid peers. Target EPS is required for implied prices; target market price is required only for its observed P/E. P/E already values equity, so there is no cash/debt bridge.

## Validate: calculated results

| Check | Calculator output | Case match |
|---|---:|---|
| AutoNation P/E | 10.037825× | Pass |
| Group 1 P/E | 11.450149× | Pass |
| Peer median P/E | 10.743987× | Pass |
| Asbury implied range | $215.81–$246.18 | Pass |
| Asbury at peer median | $231.00 | Pass |
| Remove GPI: AN reference estimate | $215.81 | Pass |
| Change from full-peer median estimate | −$15.18 | Pass |

Removing AN instead leaves a GPI-based reference estimate of **$246.18**, a **+$15.18** change. Changes use unrounded estimates, so subtracting the displayed rounded prices can differ by a cent. Multiples display six decimals and prices display cents.

## Evolve and reflect

**Prediction to explain before rerunning:** removing the higher-multiple GPI should lower the median-implied price. With only two peers, the median is their arithmetic midpoint. Removing GPI leaves AN's lower multiple, reducing the estimate to $215.81. One observation gives one reference estimate, not evidence of a peer range. Removing the last usable peer leaves no estimate.

Asbury's frozen $243.03 price lies inside the calculated band and above the $231.00 midpoint. That does not prove fair value or establish an attractive investment. The comparison depends on two imperfect peers, historical accounting earnings, and market pricing that may itself be optimistic or pessimistic. Business differences and normalized earnings require judgment.

## Checkout and remaining student activities

Submit GitHub links to this write-up and [the calculator](lab07_asbury.py). Before Thursday, follow the [Week 4 prework](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/student-prework.md) and bring the working calculator and Week 3 DCF.

The student still needs to explain the peer choices and removal result to a partner, practice one calculation independently, and review this AI-assisted write-up. This document does not claim that a before-AI prediction or partner discussion occurred.

<!--
AI disclosure and discretion statement:
I used AI to help complete Lab 07, and I revised what I needed to.
-->
