FAIL

QC: ok, no issues; loudness -14.0 LUFS, TP -1.5. Banner present. `near_still` = 0.389 of runtime (253.6 s, 15 stretches over 4 s). `pace:` lines = 2 (77.4 s c1-disputed 4.7 s; 166.8 s c2-scale 6.5 s).

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening | 3 | sheet_00 tile 001 (4.0 to 9.9 s): flash with banner "SIMULATION · NOT REAL EVENTS" over moving footage, inside 8 s; but it lands on a flat dark-grey empty map with one label (no recognisable place). Tiles 000 to 006 each arrive every 4 to 6 s; tile 006 (open-fire) holds 5.7 s and tile 007 holds 5.1 s. |
| Story pacing | 4 | Trigger (launch/flash) is the cold open; simulation chapters 03 to 06 (tiles 028 to 069) end on "THE DAY AFTER" / "THE MOUNTAIN IS STILL THERE" (sheet_05 tile 065 "AND SO IS THE QUESTION"). Chapters 01 to 03 (about 44 to 288 s) are long context before the simulation proper. |
| Map readability | 2 | P0 below (shot 050). Large empty inland frames: long_04_183s.png shows only QOM, KASHAN, NATANZ, "HOW FAST?" on flat grey grid; long_00_20s.png same. Labels on sheet_03 tile 6 and sheet_04 tile 2 sit near the edges. Labels otherwise plated and clear of tag and clock. |
| Subject and fidelity | 3 | City shots (sheet_04 tiles 6 to 9: long_10_427s.png fireball 0.191 km with rings) fill the frame well. Region shots show tiny dots on grey (sheet_01 tiles 1 to 4, sheet_05 tiles 3 to 5) with no terrain, so the subject is small. |
| Motion and pacing | 3 | near_still 38.9%; stretches of 28.4 s (61.1 s), 27.3 s (482.3 s), 25.9 s (201.7 s), 25.4 s (526.8 s). Flash has glow and banner but lands on an empty frame. |
| Packaging | 4 | Title "What If Iran Tests a Nuke? Israel's 4-Day Answer" is hypothetical, names who and where. thumb_a.png: "1,670 KM / ONE WARHEAD", readable small, clear map; shares no words with the title. |
| Accuracy and labelling | 4 | SIMULATION tag on all simulation shots; "(SIMULATED)", "OUR CHOICE", "10 KT: ENTIRELY OUR ASSUMPTION", "NO OTHER REAL PLACE" labels (sheet_00 tile 001, sheet_02 tile 7, sheet_04 tile 2). Description states "It has not happened". No em-dashes in metadata.json. |

Mean: 3.3

Findings
1. P0: text cut off by the legend. Shot c4-clock (tile 050, sheet_04 pos 3, shots/050.png, frame 414.9 s): the label "FLIGHT: EIGHT MINUTES" is overprinted by the IRAN/ISRAEL legend plate and reads "GHT: EIGHT MINUTES". Fix by moving the label or the legend (label clamp must avoid the legend), and re-render.
2. Empty inland maps persist despite the HUD grid fix: about 39% near-still, four stretches over 25 s (61.1, 201.7, 482.3, 526.8 s). Add terrain, camera keys, rings or markers; the flash at 4.0 to 9.9 s also lands on a blank map and should show the real mountain, borders or terrain.
3. Two `pace:` warnings: 77.4 s (c1-disputed, 4.7 s) and 166.8 s (c2-scale, 6.5 s).
4. Chapters 01 to 03 hold the viewer in history and context until about 4:48 (288 s) before the simulation resumes; consider trimming.
5. Shorts: subtitles present and inside the safe area, SIMULATION tag present (s1_silent_1, s2_silent_2, s3_silent_1); s1 label "(SIMULATED)" sits close to the left edge but inside.
6. Title and description are true and hypothetical; disclaimer present; end slate half-empty by design.
