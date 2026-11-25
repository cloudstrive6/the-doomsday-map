PASS

QC: `qc.json` ok, no issues; loudness -14.0 LUFS, true peak -1.8 dBTP; `shotlist_checks` empty (banner present at 1.7 to 4.7 s, 3.0 s, over the flash that starts at 2.0 s). `near_still` = 7.9% (53.0 s); `pace:` lines = 0.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 4 | sheet_00 tile 001 `open-flash` (2.0 to 8.0 s): fireball and "5 PSI · 1.158 KM" ring, SIMULATION tag, on the target at 2 s. Arrivals every 4 to 6 s through sheet_00, but tile 007 `open-nato` runs 9.8 s and sheet_01 tile 013 `c1-top` 10.3 s, over the 8 s shot rule. |
| Story pacing | 3 | Payoff is shown at 0:02 and the warning shot is the cold open; the simulated crisis proper (c3 "The Trigger", 251 s) and strike (466 s, sheet_05 tile 070 `c4-flash`) come late. Chapter 6 "The Day After" (sheet_06 tile 081) ends the episode on aftermath (sheet_07 tile 095 `c6-end`). Ch. 2 (152 to 251 s) is a history stretch before the trigger. |
| Map readability | 4 | Labels plated and inside the frame on every sheet (e.g. sheet_04 tile 8 "BALTIYSK: THE BASE THAT GUARDS THE LINE", sheet_05 tile 4 "GERMAN BRIGADE, ALLIED BATTLEGROUP"). Weak: sheet_01 tile 019 `c1-fleet` "ONLY BALTIC PORT FREE OF ICE IN WINTER" is small, and `long_00_21s` is an almost empty frame with only the legend and scale. |
| Subject and fidelity | 3 | Correct places throughout (Kaliningrad, Suwalki, Grodno, Berlin). Ring shots fill the frame (sheet_06 tiles 3 to 6). Many Europe-scale shots show the enclave small (sheet_01 tile 004 `c1-nolink`, sheet_05 tile 2 `c4-range`). |
| Motion and pacing | 3 | Flash lands (sheet_06 tile 003, `c5-20`, with ring and glow). Dips are uniform. Brief empty or near-empty stretches (see findings 1 to 3). |
| Packaging | 4 | Title "One Nuke on Kaliningrad: What If NATO Cut It Off?" is hypothetical and names where. Thumbnail "13 DAYS THEN THIS" with a mushroom cloud, no shared words. The thumbnail scenery is mountains and conifers, not the flat Baltic coast. |
| Accuracy and labelling | 4 | Tags change correctly from REAL DATA to REAL HISTORY to SIMULATION (sheet_02 tile 006 SIMULATION "In our simulation, the closed enclave is Russian."). "No death toll is computed for this strike." (sheet_05 tile 3). Description has the disclaimer ("This is a simulation. It has not happened.") and no em-dashes. Shorts carry the SIMULATION or REAL DATA tags. |

Mean: 3.57

Findings (none a P0):
1. `c4-mar` (sheet_05 tile 060, 390.0 to 390.1 s) is a 0.1 s shot: a stray single frame, not noticeable at speed but worth removing in the shotlist.
2. `long_00_21s` (shot `open-target`, 20.6 to 26.6 s) is almost empty at 21 s (only legend and scale); labels arrive later in the shot. Still inside the 90 s window, so it is a pacing weak spot.
3. `qc.json` near-still stretches over 4 s: 116.8 s (7.4 s), 499.6 s (4.3 s), 658.8 s and 664.4 s (end slate, allowed). The 116.8 s one is `c1-isk`, a nearly blank map with one label.
4. Shots over 8 s inside the first 90 s: `open-nato` (9.8 s), `c1-top` (10.3 s). Not flagged by the engine but outside the written rule.
5. Thumbnail setting shows mountains, not the Baltic lowlands; not misleading about the event, but not the place.
6. Chapter-end frames of `c3-day8` and `c6-end` are mid-fade, so tag and clock read faintly on the sheets (transition, not a defect).
