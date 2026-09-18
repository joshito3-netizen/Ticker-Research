# Lab 08 — Microsoft: Peer Evidence and Valuation Triangulation

**Target:** Microsoft Corporation (MSFT)  
**Comparison date:** September 9, 2026  
**Selected peer:** Salesforce (CRM), qualified  
**Decision:** **Watch-defer**

Salesforce implies **$561.88 per Microsoft share**, a **single-peer reference**, not a range. The saved Week 3 DCF reproduces **$228.81**, with a **$180.23–$320.17** sensitivity range. Microsoft's same-date closing price was **$491.65**. The methods disagree materially; I do not average them or treat the peer reference as sufficient evidence to initiate.

## 1. Reopen and explain

The saved Asbury calculator was rerun successfully. Its P/E and leave-one-peer-out logic was adapted into [lab08_microsoft.py](lab08_microsoft.py), with Microsoft inputs.

**How a peer's P/E becomes Microsoft's price:** divide the peer's stock price by its annual diluted EPS, then multiply that multiple by Microsoft's annual diluted EPS. This transfers the price investors pay for a dollar of the peer's earnings to a dollar of Microsoft's earnings. The critical assumption is economic comparability, not similar share prices. P/E already values equity per share; there is no additional cash/debt bridge.

**Date reconciliation:** the recovered [Week 3 note](lab06-microsoft.md) and [DCF calculator](dcf.py) use September 9, 2026 for the market comparison. June 30 is the financial-statement date. September 9 replaces the earlier June and September 1 working comparisons. The original DCF was on GitHub; the local file had contained sample inputs. The actual model has now been restored and rerun.

## 2. Define/Discover — Microsoft first

Microsoft earns money from enterprise applications and Azure infrastructure, alongside Windows, gaming, and advertising. Its broad mix makes a pure application company an imperfect whole-company peer. Annual reported diluted EPS is positive. [Microsoft release][msft-release], “Business Highlights” and “Fiscal Year 2026 Results.”

**Focused research question:** What does a recurring enterprise-application peer imply for Microsoft, and does that reference justify a different decision from the saved cash-flow valuation?

Remaining research concerns the persistence of infrastructure spending, its incremental cash returns, and sustainable earnings.

## 3. Represent — policy and candidate decisions

### Initial policy, preserved

Investigate listed operating companies with recurring enterprise software subscriptions, software support, or cloud services, business-critical workloads, and customer switching costs. Require positive annual reported diluted EPS public by the comparison date and compatible USD common-share prices. Qualify differences in business mix, capital intensity, leverage, growth, fiscal periods, and nonrecurring income. Exclude unrelated principal business economics or unusable earnings/share bases.

**Rejection evidence:** filings showing the apparently comparable activity is immaterial; nonpositive annual EPS; earnings not public by the comparison date; or an unresolved currency/share mismatch. An inconvenient valuation is not a rejection reason.

### Revision before the final calculation

The student selected **Salesforce**. Before the final September 9 rerun, the policy was narrowed to an **enterprise-application reference**. Salesforce fits recurring application subscriptions; Oracle's infrastructure buildout and financing needs make it less suitable for this narrower purpose. This sacrifices coverage of Azure and limits the whole-company inference.

The revision occurred after earlier results had been seen. The sensitivity below shows that excluding Oracle raises the reference. The economic rationale, rather than that increase, must support the choice. Both investigated candidates remain documented.

| Candidate | Decision | Business evidence, difference, and locator |
|---|---|---|
| Salesforce (CRM) | **Qualify; include** | Subscription/support represented approximately 95% of FY2026 revenue. Enterprise customer applications share recurring software economics with parts of Microsoft. The narrower mix does not replicate Azure or Microsoft's consumer businesses; January year-end also creates a different earnings window. [Salesforce 10-K][crm-10k], Item 1 “Business—Overview” and Item 7 “Revenues,” p. 43. |
| Oracle (ORCL) | **Exclude from the application-focused comparison** | Infrastructure and applications make Oracle plausible under the original broad policy. However, FY2026 free cash flow was negative $23.7 billion and debt financing raised was $43 billion. Those investment/funding demands support exclusion from the narrower reference, not a claim that Oracle is unrelated to Microsoft. [Oracle release][orcl-release], “Financial Results for FY 2026” and “Capital Investment Program and Capital Funding.” |

The Salesforce 10-K and both company releases were opened during research. Oracle's full 10-K retrieval failed; its opened release supports the decision.

## 4. Implement — same-date inputs

Prices are **September 9, 2026 Close**, USD per U.S.-listed common share. Earnings are full-year **reported GAAP diluted EPS**, not quarterly, forecast, or adjusted earnings. No ADR conversion or manual split adjustment is applied. Salesforce's Close is $244.16; its dividend-adjusted Adj. Close of $243.73 is not used.

| Company / decision | Close | Annual diluted EPS | Fiscal year-end | Publication date | Earnings source / locator | Price source / locator |
|---|---:|---:|---|---|---|---|
| MSFT — target | $491.65 | $17.95 | 2026-06-30 | 2026-07-29 | [Microsoft release][msft-release], Income Statements, Twelve Months Ended June 30, 2026, Diluted | [MSFT history][msft-price], Sep 9, 2026, Close |
| CRM — qualify | $244.16 | $7.80 | 2026-01-31 | 2026-02-25 | [Salesforce release][crm-release], Consolidated Statements of Operations, Fiscal Year Ended January 31, 2026, diluted net income per share | [CRM history][crm-price], Sep 9, 2026, Close |
| ORCL — exclude | $161.63 | $5.83 | 2026-05-31 | 2026-06-10 | [Oracle release][orcl-release], annual Consolidated Statements of Operations, diluted EPS attributable to common shareholders | [ORCL history][orcl-price], Sep 9, 2026, Close |

Nasdaq history pages were checked first but returned no price rows. Opened Stock Analysis tables supplied the dated prices. These are the latest annual periods public by the comparison date, but not identical fiscal windows. Salesforce's annual period is older; a common price date does not remove that limitation.

**Earnings quality:** Microsoft's annual GAAP EPS includes a $0.67 OpenAI investment benefit; annual non-GAAP EPS is $17.28. Salesforce's annual non-GAAP EPS is $12.52 versus $7.80 GAAP. Neither adjusted figure enters the calculator. [Microsoft release][msft-release], annual reconciliation and “Non-GAAP Definition”; [Salesforce release][crm-release], GAAP/non-GAAP reconciliation. Oracle's excluded non-GAAP EPS is $7.63. Different adjustments are not automatically comparable.

## 5. Validate — arithmetic and removal

Run from the repository folder:

```sh
python3 lab08_microsoft.py
python3 dcf.py
```

**Worked arithmetic:**

```text
Salesforce P/E = 244.16 / 7.80 = 31.3025641026...
Microsoft reference = 31.3025641026... × 17.95 = $561.88
```

Keep full precision until displaying cents. An independent Decimal calculation matched the calculator.

| Check | Result and interpretation |
|---|---|
| Microsoft observed P/E | 27.389972× |
| Salesforce P/E | 31.302564× |
| Microsoft implied price | **$561.88; one-peer reference, no range** |
| Prediction for removing Salesforce | No estimate because no admitted peers remain |
| Calculator result after removal | **No estimate; no usable peers remain** |

Removing the only peer does not imply a zero-dollar valuation or a measurable percentage decline.

**Audit the exclusion:** admitting Oracle under the original policy on the same September 9 inputs would produce an Oracle reference of $497.64 and a two-peer midpoint of $529.76. Excluding it raises the midpoint to the Salesforce reference by **$32.12**, using unrounded figures. This is a sensitivity, not a second base case. It shows why a business reason must support the exclusion.

## 6. Evolve — reproduced Week 3 DCF

The restored DCF forecasts FCFF, discounts it at WACC, then bridges enterprise value to equity. Amounts below are USD millions except per-share results.

| Input | Value and treatment |
|---|---|
| Starting FCFF | **68,196 = 182,935 CFO + 1,500 cash interest × (1 − 19.4%) − 115,948 capital additions** |
| Forecast growth | 20%, 16%, 13%, 10%, 7%; saved assumptions, not guidance |
| WACC / terminal growth | 9.5% / 3%; saved assumptions |
| Cash and short-term investments | 76,843 |
| Debt | 40,294 at carrying amount |
| Diluted shares | 7,453 million annual weighted-average shares |

Historical figures trace to [FY2026 10-K][msft-10k], Cash Flows, Balance Sheets, and Notes 2, 10, and 13, as recorded in [Lab 06](lab06-microsoft.md). CFO, capital additions, cash, debt, and shares were cross-checked in the annual statements in [Microsoft's release][msft-release]. Opened reproductions of the [Debt note][debt-note] and [Income Taxes note][tax-note] support cash interest and the rounded effective tax rate. Cash interest disclosed in rounded billions makes starting FCFF approximate.

**Bridge:** enterprise value $1,668,771.35 + cash $76,843 − debt $40,294 = equity $1,705,320.35; divide by 7,453 million shares = **$228.81**. Terminal value supplies **76.16%** of enterprise value.

| WACC / terminal growth | 2% | 3% | 4% |
|---|---:|---:|---:|
| 8.5% | $236.59 | $270.78 | $320.17 |
| 9.5% | $204.64 | **$228.81** | $261.77 |
| 10.5% | $180.23 | $198.06 | $221.37 |

This is a sensitivity interval, not a statistical confidence interval. The saved model uses five full annual periods and fiscal-year-end balances without a September stub-period roll-forward. It treats all cash/investments as non-operating, uses carrying debt and average diluted shares, and does not separately capitalize leases or deduct stock-based compensation. WACC remains an assumption; its earlier market-input calibration is not asserted as newly verified.

| Method | Microsoft's result and date | Main assumption or limitation |
|---|---|---|
| Week 3 DCF | **$180.23–$320.17**, base **$228.81**; September 9, 2026 comparison | Forecast cash generation/reinvestment, discount rate, terminal growth, simplified timing and bridge |
| Peer P/E | **$561.88 single-peer reference**; September 9, 2026 | Salesforce only; application-focused match, different fiscal windows, reported earnings quality |

The $491.65 market close exceeds the DCF range, while Salesforce implies **14.28% upside from that market price**. A DCF values future cash after reinvestment; P/E transfers market pricing of accounting profit. Infrastructure spending affects cash immediately while depreciation affects earnings over time. Growth expectations, capital intensity, investment gains, and peer selection can therefore produce different answers. Both methods value Microsoft common equity. I do not average them.

**Evidence most likely to change the call:** a cash-flow forecast demonstrating durable incremental returns from infrastructure spending, with the conclusion surviving downside discount-rate and terminal-growth assumptions.

## 7. Skeptical AI review and source-checked judgment

**Weakest supported assumption:** applying Salesforce's whole-company multiple to all Microsoft earnings. The DCF's rapid FCFF growth and terminal dependence also matter; reproducing a formula does not validate its forecast.

| Criticism | Judgment | Evidence checked and consequence |
|---|---|---|
| Salesforce does not represent all Microsoft businesses. | **Accept** | Salesforce's 10-K shows application/subscription concentration; Microsoft's release shows broader segments. Treat $561.88 as a qualified reference. |
| The DCF cannot be reproduced. | **Reject after correction** | The actual GitHub Week 3 model was recovered. Its base, grid, and terminal share reproduce. Forecast uncertainty remains. |
| Excluding Oracle could be motivated by its lower implied price. | **Accept as a selection-bias risk** | The same-date sensitivity shows a $32.12 increase. Preserve the counterfactual and reconsider Oracle if representing infrastructure becomes the priority. |
| Salesforce-implied upside is enough to initiate. | **Reject** | One imperfect peer conflicts with the reproduced DCF and uses reported earnings. That does not establish a margin of safety. |

**Skeptical question:** Would the application-focused policy still justify Salesforce alone if its multiple produced the lower Microsoft value?

**Answer:** selection should rest on recurring application economics, not the resulting price. Salesforce is useful for that limited comparison, but Azure is important enough that this reference cannot establish Microsoft's whole-company fair value. If representing Azure is essential, restore the broader policy and reconsider Oracle before recalculating.

## 8. Reflect — conditional decision

**Watch-defer.** Salesforce adds observable market evidence for enterprise applications, but does not settle the value of Microsoft's infrastructure and consumer businesses. The defensible outputs are the **$180.23–$320.17 DCF sensitivity range under disclosed assumptions** and the separate **$561.88 Salesforce reference**. I withhold a combined fair-value range.

Initiation would require evidence supporting stronger sustainable cash generation or a purchase price offering a margin of safety under reviewed downside assumptions. Weak AI returns or persistent heavy reinvestment would weaken the case. Carry forward this question: how much infrastructure spending is temporary expansion versus recurring expenditure required to sustain growth?

## Reproducibility and disclosure

Supporting files: [peer calculator](lab08_microsoft.py), [restored DCF](dcf.py), [Week 3 source note](lab06-microsoft.md), and [recorded validation](lab08-validation.txt).

AI assisted with research, policy drafting, analysis, and checks; the student selected Salesforce. Initial and revised policies are preserved rather than described as independently written before AI.

[msft-release]: https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast
[msft-10k]: https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm
[debt-note]: https://app.edgar.tools/companies/MSFT/disclosures/debt
[tax-note]: https://app.edgar.tools/companies/MSFT/disclosures/income-taxes
[orcl-release]: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/
[crm-release]: https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Fourth-Quarter-Fiscal-2026-Results/
[crm-10k]: https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm
[msft-price]: https://stockanalysis.com/stocks/msft/history/
[orcl-price]: https://stockanalysis.com/stocks/orcl/history/
[crm-price]: https://stockanalysis.com/stocks/crm/history/
