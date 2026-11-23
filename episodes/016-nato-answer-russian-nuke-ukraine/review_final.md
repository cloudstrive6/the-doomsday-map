PASS

qc.json: ok, no issues, shotlist_checks empty (banner present). Loudness -14.0 LUFS, TP -1.8 dBTP. near_still: 56.7 s = 8.4% of runtime (one stretch over 4 s: 101.8 s, 4.2 s, the "c1-conv" shot, within QC tolerance). `pace:` lines: 0.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening | 5 | sheet_00 tile 001 (open-burst, 2.0 to 5.0 s): fireball over Komyshnia with the "SIMULATION · NOT REAL EVENTS" banner on moving footage; tile 002 rings over a city and caption "Simulation: it has not happened." at 7.5 s. Tiles 000 to 008 change every 2 to 6 s, no card over 4 s. |
| Story pacing | 4 | Strike at 280 to 290 s (sheet_04 tiles 049 to 051, c3-m0 to c3-burst), about 4:40, later than the 4:30 target. Each chapter card is followed by a pointer line; sheet_08 tile 102/103 ends on Day 7 and "consult on options in advance". |
| Map readability | 4 | Labels plated, inside the frame and clear of tag and clock (sheet_04 tiles 053 to 059, sheet_06 tiles 072 to 078). Sheet_08 tile 096 has a left label touching the tag column; tile 102 "Moscow has not said it will not fire again" sits near the edge but inside. |
| Subject and fidelity | 4 | Right places: Kursk to central Ukraine (sheet_00 tile 004/005), Brussels and Ukraine in the NATO chapters (sheet_04 tile 053/054), ring-by-ring city shots (sheet_06 tiles 080 to 083). Some Europe-wide shots leave the subject small (sheet_04 tile 058). |
| Motion and pacing | 4 | Burst, rings and clock move; 0 `pace:` lines. Several mid-animation frames (sheet_01 tile 016 yield bars, sheet_06 tile 076 timeline) look empty at sampling time, but they animate in. |
| Packaging | 4 | Title "What If Russia Nuked Ukraine? NATO's 4 Options" is hypothetical and names who and where. thumb_a: "72 HOURS TO CHOOSE" over a wheat field and mushroom cloud, readable small, no shared words. Neither carries the 20 kt number. |
| Accuracy and labelling | 4 | The SIMULATION tag is on every simulation chapter and REAL DATA and REAL HISTORY tags are on the context (sheet_01 and sheet_03). Scenario figures come from the engine (fireball 0.202 km, 5 psi 1.838 km). metadata.json has the disclaimer and "we set no date", and no em-dashes. See finding 1 for one mislabel. |

Mean: 4.14

Findings (none blocking):
1. The last map shot (c6-ac, sheet_08 tile 103, "2022 ADVICE: CONSULT ON OPTIONS IN ADVANCE", source "Atlantic Council, 2022") carries the SIMULATION corner tag, but it is real published advice. REAL DATA or REAL HISTORY would be more accurate. The text is attributed and not misleading, so it is not a P0.
2. The episode ends on advice and the open question rather than a new image of the aftermath. The Day 7 shots do keep it on the simulation's aftermath.
3. The strike lands at about 4:40, a little past the 4:30 mark. Chapters 1 to 3 run long.
4. The 4.2 s near-still stretch at 101.8 s (c1-conv) is just over the 4 s guideline. QC passed it.
5. Sheet_04 tile 049 (c3-m0) and sheet_03 tile 004 (c3-area) are very sparse frames, with a lone staging-area dot on a flat fill. They move, but the subject is small.
