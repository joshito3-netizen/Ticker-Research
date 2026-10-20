# Video Recording Guide — Not a Submitted Transcript

## Video 1 — research evolution, maximum 3:00

- Show the unchanged Edition A and receipt.
- Explain the June 30 look-ahead correction and September 9 cutoff.
- Show the A-to-B table: watch/defer remained, but the evidence became decision-ready.
- AI-output check: Codex identified finance leases as missing from the simple DCF; show Note 13
  and the omission test; disposition: accepted after correction and independent filing check.

## Video 2 — code and validation, maximum 5:00

- Run python3 analysis.py, then python3 -m unittest discover -s tests -v.
- Explain data/model_inputs.json → analysis.py → generated output → app.py.
- Trace segment growth through statements, FCFF, DCF, and the EV-to-equity bridge.
- Demonstrate the highest-risk lease-omission test and one loud failure (g ≥ WACC).
- State limitations: terminal share, aggregate depreciation, fixed diluted shares, single peer.

## Video 3 — committee defense, maximum 5:00

- First minute: open Streamlit; move one bounded driver; compare with restored base; select the
  deliberate loud-failure checkbox (terminal growth = WACC), show the red error, uncheck it, and
  press Reset to base.
- Lead with watch/defer at $491.65 and $112–$356 DCF range.
- Explain why CRM P/E ($562) and EV/Revenue ($251) disagree and why they are not averaged.
- Defend conditions, failure rules, monitoring triggers, and the committee ask.

After recording, correct the platform transcripts and save the exact submitted text as the three
transcript-video files.
