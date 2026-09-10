# Lab 06 — Microsoft: Sensitivity, Reverse DCF, and Conditional Recommendation

**Company:** Microsoft Corporation (MSFT)  
**Model/filing date:** FY ended June 30, 2026; Form 10-K filed July 29, 2026. Dollar inputs are USD millions except per-share amounts.  
**Price target for reverse DCF:** **$491.65**, NASDAQ closing price on September 9, 2026 at 4:00 p.m. ET (retrieved September 10, 2026). [Historical-price source](https://www.marketminute.com/quote/NQ%3AMSFT/historical)

## Inputs and sources

| Input | Value used | Unit / as-of | Exact locator and treatment |
|---|---:|---|---|
| Starting FCFF | 68,196 | $m; FY ended Jun. 30, 2026 | **Calculated:** 182,935 cash from operations + 1,500 cash interest paid × (1 − 19.4% effective tax rate) − 115,948 additions to property and equipment. Source: [FY26 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm), Item 8, Consolidated Cash Flows Statements p. 53; Note 10—Debt (cash paid for interest) and Note 13—Income Taxes, effective-rate table p. 73. |
| FCFF growth, Years 1–5 | 20.0%, 16.0%, 13.0%, 10.0%, 7.0% | Forecast, FY27–FY31 | **Estimate:** I start above Microsoft’s reported FY26 revenue growth of 18%, then deliberately fade. This is informed by Azure and other cloud-services growth of 41% and Microsoft Cloud growth of 27%, but it is not company guidance. Source: FY26 10-K, Item 7 MD&A, “Fiscal Year 2026 Compared with Fiscal Year 2025,” pp. 34, 39. |
| WACC | 9.5% | Estimate; Sep. 9, 2026 | **Estimate:** cost of equity ≈ 4.79% 10-year Treasury + 0.96 beta × 5.0% ERP = 9.59%; after-tax debt cost ≈ (1,500 / 40,294) × (1 − 19.4%) = 3.00%. Equity weight uses $491.65 × 7,453m diluted shares and debt weight uses $40,294m; rounded WACC = 9.5%. Treasury source: [Federal Reserve H.15, Sep. 9, 2026](https://www.federalreserve.gov/releases/h15/); beta source: [Stock Rover MSFT report](https://www.stockrover.com/report/MSFT.pdf). |
| Terminal growth | 3.0% | Estimate | **Estimate:** long-run economy convention, not a Microsoft-specific forecast. |
| Non-operating cash | 76,843 | $m; Jun. 30, 2026 | FY26 10-K, Item 8, Consolidated Balance Sheets p. 52: cash and cash equivalents of 20,935 plus short-term investments of 55,908. |
| Debt | 40,294 | $m; Jun. 30, 2026 | FY26 10-K, Item 8, Consolidated Balance Sheets p. 52: current portion of long-term debt 9,227 plus long-term debt 31,067. |
| Diluted shares | 7,453 | million weighted-average shares; FY ended Jun. 30, 2026 | FY26 10-K, Item 8, Note 2—Earnings Per Share p. 62. This is diluted weighted-average shares, not the cover-page basic count. |

The FCFF calculation treats all reported additions to property and equipment as capital expenditure. That is a conservative but important choice while Microsoft is expanding cloud and AI infrastructure.

## Training-case check

Before replacing the inputs with Microsoft, I reproduced the supplied training grid exactly. With a $30.00 target, bisection solved a uniform explicit-growth shift of **+1.78 percentage points** (unrounded: +1.777948%).

| WACC \ terminal growth | 2% | 3% | 4% |
|---|---:|---:|---:|
| 9% | 28.60 | 32.94 | 39.02 |
| 10% | 24.36 | 27.50 | 31.69 |
| 11% | 21.06 | 23.41 | 26.44 |

## Microsoft valuation and sensitivity

Base-case equity value per diluted share is **$228.81**. It is **0.47×** the $491.65 market price, so it is outside the 0.5×–2× reasonableness band. I did not adjust the model to fit the price.

The input I distrust most is **starting FCFF**: FY26 additions to property and equipment rose sharply with AI/cloud build-out. Treating all $115.948B as current capital expenditure may understate normalized FCFF if part is unusually front-loaded growth investment; treating it as maintenance-free would overstate it. This is the assumption with the largest immediate effect on value.

| WACC \ terminal growth | 2% | 3% | 4% |
|---|---:|---:|---:|
| 8.5% | $236.59 | $270.78 | $320.17 |
| 9.5% (base) | $204.64 | **$228.81** | $261.77 |
| 10.5% | $180.23 | $198.06 | $221.37 |

The base case is the center cell. Value falls as WACC rises and rises as terminal growth rises. The corner range is **$180.23–$320.17 per share**.

## Reverse DCF

At the $491.65 target price, the initial required bracket of −5 to +10 percentage points had no solution. I widened only the disclosed upper bound to **+30 percentage points**. Bisection then solved for a **+20.74 percentage-point uniform shift** to the five explicit FCFF-growth rates.

This means the price is consistent with explicit-growth rates of approximately **40.74%, 36.74%, 33.74%, 30.74%, and 27.74%** in Years 1–5, with the following held fixed: starting FCFF, 9.5% WACC, 3.0% terminal growth, cash, debt, diluted shares, and the five-year horizon. It is one assumption set consistent with the market price—not proof that MSFT is mispriced.

## Conditional recommendation

**Watch—defer. Initiate if MSFT falls to about $228.81 per share under this unchanged base-case model, or if sourced evidence justifies raising my five explicit FCFF-growth assumptions by roughly 20.74 percentage points. Otherwise, defer. Monitor: quarterly additions to property and equipment relative to Azure/cloud revenue growth and operating margin.**

---

*AI-use disclosure: AI was used to help generate and revise this file and the accompanying `dcf.py`; the inputs, sources, assumptions, and conclusions should be reviewed by the student before submission.*
