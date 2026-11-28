PASS

qc.json: ok, no issues, `shotlist_checks` empty (banner present, no retention lines). Loudness -14.0 LUFS, true peak -1.5 dBTP (at the limit, inside tolerance). `near_still` = 46.5 s, share 0.075; the three stretches over 4 s sit at 605.4 s, 611.5 s and 617.8 s, which is the end slate (allowed). `pace:` lines: 0 (validate.txt reads "ok").

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening | 4 | sheet_00 tile 001 (open-flash, 3.8 s): fireball over central London at T+00:02, labelled "100 KT AIR BURST (SIMULATION)". Tile 002 (6.6 to 10.8 s): "IT HAS NOT HAPPENED" banner label over the moving UK map. Tiles 000 to 008 change every 2.6 to 8.1 s. open-fly runs 8.1 s (14.1 to 22.2 s), a little over the 8 s ceiling. Tile 008 (open-why2) is a near-empty frame: a single London dot and the label "WHAT DO THREE DAYS MEAN?". |
| Story pacing | 4 | The first warhead is shown at T+07:40 and London at T+08:49 (sheet_05 tiles 1 and 9), with the flash already in the cold open. Chapter 05 "One warhead, ring by ring" (sheet_05 tile 11) is followed by chapter 06 "The day after" (sheet_07 tile 0). The episode ends on the simulation aftermath ("IT HAS NOT HAPPENED", sheet_08 tile 3), not on history. Context chapters 01 and 02 run about 2:30 before the trigger chapter (sheet_03 tile 2). |
| Map readability | 3 | Labels are plated and inside the frame, clear of the tag and clock (sheet_06 tiles 0 to 10, sheet_07 tile 7). The stacked ring labels on London crowd each other (sheet_06 tiles 5 to 10: "FIREBALL", "20 PSI", "5 PSI", "BURNS", "1 PSI" in a diagonal pile). The "5 PSI" and "WESTMINSTER" labels overlap in sheet_00 tile 001. |
| Subject and fidelity | 3 | Faslane ground burst fills the frame with rings (sheet_05 tiles 1 to 3); London rings fill the frame (sheet_06). Several map shots show the labelled place small or off-frame: sheet_00 tile 008 (only a London dot), sheet_02 tile 3 (a lone dot, "SIRENS DISMANTLED"), sheet_04 tile 6 (empty sea with "BOREI-CLASS SUBMARINE"). |
| Motion and pacing | 3 | Varied scales from globe to city (sheet_04, sheet_05), the flash and shock rings land (sheet_00 tile 001, sheet_05 tile 1). Number and bars cards at frame 0.3 s show mostly empty fields (sheet_01 tile 1 "DAYS ON PATROL", sheet_02 tiles 4 and 7), so they read as a blank card until they fill. near_still is 7.5%. |
| Packaging | 4 | Title "What If One Nuke Hit London at 8:49 AM?" is hypothetical, names the place and the number. thumb_a.png reads "SCOTLAND GOES FIRST" over a UK map with two burst dots, readable at small size, with no shared words with the title. The right fifth of the thumbnail is a dark band with nothing in it. |
| Accuracy and labelling | 4 | Corner tags are correct throughout: REAL DATA, REAL HISTORY and SIMULATION (sheet_01 tile 0, sheet_02 tiles 0 and 4, sheet_05 tile 0). Sources are credited on screen (sheet_01 tiles 6 and 8). Rings are engine values (0.384 km, 0.64 km, 3.143 km, 4.158 km, 8.507 km, sheet_06). "NO PUBLISHED STUDY" and "WE DO NOT COUNT WHO IS INSIDE" (sheet_06 tile 10) cover the casualties. "WIND: OUR CHOICE" (sheet_05 tile 5) labels the wind. metadata.json carries the disclaimer and has 0 em-dashes. |

Mean: 3.57 (25 / 7).

Findings (none is a P0):
1. Near-empty map frames where the labelled place is a dot or off-screen: sheet_00 tile 008, sheet_02 tile 3, sheet_04 tile 6. The camera should frame the subject.
2. Number and bars cards (sheet_01 tile 1, sheet_02 tiles 4 and 7) look blank 0.3 s after arrival. Check that the values are visible within the first second.
3. The London ring labels stack and crowd each other (sheet_06 tiles 5 to 10). Fewer simultaneous labels would read better.
4. open-fly lasts 8.1 s, over the 8 s limit for the first 90 s (retention ceiling is a warning, not blocking).
5. The thumbnail has a dark empty band on the right edge. It is still readable.
6. Shorts: subtitles are present and inside the safe area, and the SIMULATION tag and title band are visible. Short 1 opens on a white flash frame, which is deliberate.
