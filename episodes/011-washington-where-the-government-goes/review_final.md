PASS

QC: `ok: true`, no issues, `shotlist_checks` empty (banner present), loudness -14.0 LUFS, true peak -1.8 dBTP. `near_still` 13.5% (86.0 s); `pace:` lines: 0.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 5 | sheet_00 tile 001 (2.9 to 5.5 s): flash and fireball on the White House with the "SIMULATION · NOT REAL EVENTS" banner over moving city footage, payoff inside 6 s. Tiles 000 to 004 (0 to 18 s) are 2.6 to 6.3 s shots, with a new arrival at least every 4 s; tile 002 has "A SIMULATION: NOT A PREDICTION / IT HAS NOT HAPPENED" and the subtitle on tile 001 says "Simulation: it has not happened". |
| Story pacing | 4 | The trigger (launch and 11-minute clock) is shown by 0:15 and the detonation by 5 s. The 1:46 to 1:52 shot and the 5:49 shot are the longest holds. sheet_07 ends on the day after (10:12 clock, "WHETHER IT REACHES THEM: NOT MODELLED") and not on history. Chapters 2 and 3 are context-heavy before the minute-by-minute. |
| Map readability | 4 | sheet_05 tiles 8 to 12: labels are plated and inside the frame, and the rings are readable. sheet_05 tile 11 ("INSIDE THE RING" and the "5 PSI" label crowded against ring edges) and sheet_07 tile 4 ("HOUSE SEATS: SPECIAL ELECTIONS ONLY" close to the right edge) are tight but not cut off. |
| Subject and fidelity | 4 | sheet_00 tile 001 and sheet_05 tiles 8 to 12: White House, Capitol and Pentagon at the right places, with 0.4, 3.1 and 8.5 km rings. sheet_07 tile 8: the aircraft is shown only as a small marker, and the subject is small. |
| Motion and pacing | 4 | 0 `pace:` lines. Flash on sheet_05 tile 5 ("IMPACT", orange glow, ring). Five still stretches over 4 s, listed in `qc.json` (the longest 10.8 s at 348.6 s), and QC permits them. |
| Packaging | 4 | Title "What If a Nuke Hit Washington? Who Gets Out in 11 Minutes" is framed as a hypothetical. thumb_a.png has a photoreal blast over the Capitol with the large text "WHO'S STILL IN CHARGE?", which is readable small. The title and thumbnail share the word "who" and the thumbnail has no number. |
| Accuracy and labelling | 5 | The SIMULATION tag is on every simulation tile (sheet_03 tile 7, "a simulation choice, not a fact" under the yield card). The REAL DATA / REAL HISTORY tags are on sheet_00 tiles 8 to 12 and sheet_07 tiles 3 and 5. The 100 kt yield is a scenario choice (script.md:47). metadata.json states "This is a simulation. It has not happened." |
| **Mean** | **4.3** | |

Findings:
1. thumb_a.png has a faint grey translucent rectangle at the top right (behind "STILL"), an image artifact. It is minor but visible at full size. Consider regenerating it.
2. Short 1 frame s1_silent_1: the "CAPITOL: 2.5 KM" label overlaps the faded "WASHINGTON" map label. It stays legible and is not a P0.
3. sheet_03 tile 2 showed "48 KILOTONS" because the review frame was taken during the count-up to 100 (shotlist.py:353). The final value is 100, so this is a sampling artefact and not a defect.
4. The still stretches over 4 s (53.9 s for 8.7 s, 348.6 s for 10.8 s) are within QC rules, but they are the likeliest retention dips.
5. No em-dashes in metadata.json or script.md. `{{CHAPTERS}}` is filled at upload.
