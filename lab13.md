# Lab 13 — Portfolio Mandate Defense

## D — Question

Which of these portfolios does the Meridian Foundation's mandate permit — and what must the CIO answer before anyone optimizes?

## Sort S1–S10 before building

| ID | Type | Reason |
|---|---|---|
| S1 | Hard constraint | The seven-year horizon and annual rebalancing frequency bound how the portfolio must be managed. |
| S2 | Objective | CPI + 4% net of costs over rolling five-year periods defines the desired investment result. |
| S3 | Hard constraint | Four quarterly payouts must remain in cash or daily-liquid government securities. |
| S4 | Preference | The 60/40 benchmark is the reference for evaluation, but it does not require matching benchmark weights. |
| S5 | Hard constraint | Long-only and the bans on borrowing, short sales, and derivatives rule out specific positions and instruments. |
| S6 | Hard constraint | The 8% issuer cap is a measurable concentration limit. |
| S7 | Hard constraint | Turnover is capped at 25% annually unless the committee grants approval. |
| S8 | Hard constraint | At least 90% of the portfolio must be redeemable within five business days. |
| S9 | Unverifiable promise | The loss statement gives neither the loss measure nor a breach response, and a future calendar-year loss cannot be guaranteed from weights alone. |
| S10 | Missing | It rules out several preferences but never states what the pilot should optimize. |

S9 is not implemented as a pass/fail test. The checker reports that it requires CIO clarification.

## V — Known-answer validation

Run with:

```bash
python3 mandate.py
```

The checker calculates the 3.0% reserve minimum from the inputs. Its results for the supplied candidates are:

| Rule | A | B | C |
|---|---:|---:|---:|
| Weights sum to 100 | 100.0 pass | 100.0 pass | 100.0 pass |
| Long-only (lowest weight) | 0.0 pass | 0.0 pass | 0.0 pass |
| Reserve ≥ 3.0% | 14.0 pass | 1.0 FAIL | 2.0 FAIL |
| Redeemable in 5 days ≥ 90% | 100.0 pass | 85.0 FAIL | 100.0 pass |
| Largest single company ≤ 8% | 0.0 pass | 9.0 FAIL | 8.0 pass |
| Calendar-year loss | requires CIO clarification | requires CIO clarification | requires CIO clarification |
| Verdict | passes every checkable rule | fails 3 rule(s) | fails 1 rule(s) |

For the required probe, I changed A's cash weight to -2% and its global equity index fund weight to 64%. The weights still totaled 100%; A's lowest weight became -2.0 and failed long-only, while its reserve weight was 10.0 and all other checkable rules passed. I then restored A's original weights.

## E — Attack the checker

Candidate D holds 3% cash and 97% Treasury bills. It passes every rule in `mandate.py`, but it could still reasonably be rejected because an almost all-Treasury-bill portfolio is unlikely to meet S2's CPI + 4% net objective over rolling five-year periods.

The objection holds: passing the feasibility checks does not establish that D can achieve the return objective. S2 is the statement that decides the objection.

As the sceptical colleague reviewing this candidate, I would cite S2 because the checker has no return assumptions or cost data with which to test the stated objective.

Playing the other side of the partner swap, the colleague candidate is 3% cash and 97% global equity index fund; it also passes the checker. I would cite S4 against it because its near-all-equity allocation departs sharply from the stated 60/40 benchmark, even though the CIO has not supplied a tracking-error limit.

## One question for the CIO

**Question:** Subject to the hard constraints, should the pilot optimize for the highest expected net return, the lowest risk, or the smallest tracking error to the 60/40 benchmark?

An answer of “smallest tracking error” would keep the design close to 60% global equities and 40% U.S. investment-grade bonds rather than choosing weights to maximize expected return or minimize risk.

## Investment policy statement

An investment policy statement (IPS) is the written agreement that turns a client's purpose and circumstances into a governing framework for investment decisions. It defines the return objective, risk posture, horizon, liquidity needs, constraints, benchmark, monitoring process, and responsibilities. Portfolio choices are screened against the hard constraints first; feasible choices are then compared using the stated objective and preferences, and the IPS supplies the standards for monitoring and rebalancing.

For Meridian, S1 supplies the horizon and rebalancing schedule; S2 supplies the return objective; S3 supplies the spending reserve; S4 supplies the benchmark; S5 supplies permitted-position limits; S6 supplies the issuer concentration limit; S7 supplies the turnover limit and approval exception; S8 supplies the liquidity minimum; S9 exposes an incomplete risk statement that needs a measure and breach rule; and S10 records absent preferences while exposing the missing optimization objective.

## Reflection

A portfolio can pass every rule the checker can evaluate and still be wrong because feasibility is not suitability: the code does not determine whether expected returns, costs, benchmark behavior, or risk meet the client's objective. Candidate D demonstrates the gap by passing the coded limits while remaining poorly aligned with S2.

S4 was the type I was least sure about. I treated the benchmark as a preference/evaluation reference rather than a hard constraint because the CIO did not specify a tracking-error limit or require the portfolio to hold the benchmark weights.
