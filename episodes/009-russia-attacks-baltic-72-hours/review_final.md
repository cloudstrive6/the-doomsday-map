PASS

qc.json: ok, no issues, loudness -14.0 LUFS, true peak -1.6 dBTP, `shotlist_checks` empty (no `retention:` lines, banner present). `near_still` = 0.071 (47.2 s). `pace:` lines = 0.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 4 | sheet_00 tile 001 (open-flash, 2.0 to 7.7 s): fireball on Siauliai Air Base, flash inside 8 s, caption "Simulation: it has not happened". Tiles 002 to 009 arrive every 2 to 6 s, chapter card 3.5 s. Held back from 5 by shots of 5.5 to 5.7 s (open-sim, open-which) and a second 5.5 s city shot. |
| Story pacing | 4 | Strike is in the cold open and lands again at 419.8 s (h-flash, sheet_06 tile 012) after the "teaser" at 413 s, so the trigger arrives late in the second sense (7:00). The chapters end pointing at the next (c4-moscow, "Moscow decides"). Ends on the day after: z-quiet "QUIET AT DAWN" (sheet_10 tile 002). |
| Map readability | 4 | sheet_05: labels plated and inside the frame (TAPA ARMY BASE, SUWALKI GAP, ORZYSZ). Small risk: sheet_00 tile 003 "A SIMULATION: NOT A PREDICTION" and tile 012 "THE GROUND FIGHT STALLS" sit near the top edge, clear of the clock. |
| Subject and fidelity | 3 | Right places throughout (Siauliai, Kaliningrad, Suwalki Gap, Orzysz). Many context shots are wide country views where the subject is a small dot (sheet_05 tiles 5 to 6, Orzysz). |
| Motion and pacing | 4 | 0 `pace:` lines, flash with fireball and glow (sheet_00 tile 002). Four near-still stretches of 4.8 to 5.7 s (488.6, 650.0 to 665 s; the last is the end slate). |
| Packaging | 4 | Title "What If Russia Nuked Lithuania? The First 61 Hours" is hypothetical, names who and where. thumb_a "3 MINUTES / WHICH WARHEAD?" is legible small, a launcher at dawn, no shared words. |
| Accuracy and labelling | 4 | Corner tags correct: SIMULATION on strike/hours, REAL DATA on sirens, stamps, bars (sheet_09 tiles 6 to 10). Description: "This is a simulation. It has not happened. It is not a forecast", our choices (10 kt) stated. Caption "Princeton Plan A: a model, not this simulation" (sheet_09 tile 12). |

Mean: 3.9

Findings (none blocking):
1. The sheet frames for the bars chart (shots 116 and 117, 0.3 s after arrival) show an almost empty card; a later frame (623.5 s) shows both bars filled ("about 1,500", "about 2,000"). Not a defect, but the lower half of the card is empty.
2. Four near-still stretches over 4 s in qc.json (488.6 s 5.3 s; 650.0 to 665 s the end slate, allowed).
3. The 10 kt yield is labelled as our choice in the description and in c4-10kt; research rows for RAND 60 hours, Princeton, Norway 1995 and Crimea are single-source and softened (decisions.md).
4. Description contains no em-dashes; metadata.json has synthetic_media true.
5. Shorts frames (checked s2_silent_1): subtitle, SIMULATION tag, title band and clock all inside the safe area.
