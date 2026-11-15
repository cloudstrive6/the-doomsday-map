PASS

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 4 | sheet_00 tile 001 (open-flash, 3.7 s): orange fireball on Naval Base Kitsap, Bangor, with "SIMULATION: IT HAS NOT HAPPENED" caption, so the payoff lands inside 8 s. Tiles 000 to 011 are new shots every 2 to 4 s and the chapter card is 3.5 s. Shot 012 (c1-van2) is 6 s, a little over the 4 s rule before 90 s. episode.json has a `banner` and qc has no "no banner" line. |
| Story pacing | 4 | The trigger chapter starts at 198.5 s (sheet_04 tile 052, "THE TRIGGER", about 3:18), inside the 3:30 target. Each chapter ends pointing at the next ("What does a war look like when the warning is real?", sheet_04 tile 003). The last chapter, "THE DAY AFTER" (sheet_11 tile 006), ends on the simulation's aftermath (sheet_13 tile 006 "The clock stops at minute fifty-three"). |
| Map readability | 4 | Labels are plated and inside the frame: sheet_08 tile 003 (OFFUTT AFB, WHITEMAN, CHEYENNE MOUNTAIN, BARKSDALE) and sheet_10 ring labels (FIREBALL, 20 PSI, 5 PSI, BURNS). Minor: sheet_05 tile 000 (SILOS, right-hand labels) and sheet_01 tile 000 ("VANDENBERG, CALIFORNIA") are small, and sheet_10 tile 008 ("NO DEATH TOLL GIVEN") sits close to the right edge but is inside it. |
| Subject and fidelity | 4 | The subject of each sentence is at the right place: Bangor (sheet_06 tile 010 and 011), Cape Cod radar (sheet_06 tile 009), Pentagon and Washington with the "6 WARHEADS" label (sheet_07 tile 003), Kings Bay (sheet_07 tile 004 and 005). Weak spots: the sheet_01 tile 011 bars card is empty 0.3 s after it arrives, and sheet_02 tile 011 ("5 MINUTES" number) is plain text on a dark card. |
| Motion and pacing | 4 | 0 `pace:` lines in build/validate.txt. Hard flash frames at sheet_08 tile 007 (T+36:01, Minot) and sheet_10 tile 002 (T+15:48). Ring-by-ring build in sheet_10 tiles 003 to 011 shows new information every shot. near_still 6.4 percent (44.2 s). |
| Packaging | 4 | The title "What If America and Russia Nuked Each Other? 27 Strikes" is hypothetical and names who. The thumbnail (thumb_a.png) says "375 WARHEADS / ONE HOUR", readable small, with no shared words except the topic. Title and thumbnail use different numbers (27 and 375), which is fine. |
| Accuracy and labelling | 4 | The SIMULATION tag is on every simulation tile. Choices are labelled "OUR CHOICE" or "SIMULATION CHOICE" (sheet_06 tile 004, sheet_10 tile 001). The Princeton and Nature Food figures are credited to the studies (sheet_12 tile 005, "THE STUDY'S NUMBER, NOT OURS"). The description has the "This is a simulation. It has not happened" disclaimer and no em-dashes. |

Mean: 4.0. near_still: 0.064 of runtime (44.2 s). `pace:` lines: 0.

qc.json: ok, no issues, loudness -14.0 LUFS, true peak -1.7 dBTP, `shotlist_checks` empty.

Findings (none P0):
1. Short 3: the title band "8 WARHEADS EACH ON FOUR CITIES" (s3_silent_2) sits over a frame at T+36:00 of the missile fields and a subtitle "about 79 megatons". The band is not wrong, but it does not match what is on screen at that moment. Consider moving the window or the band.
2. near_still has five stretches over 4 s: 374.6 s, 382.3 s (4.1 s each) and 674.4 s, 679.6 s, 685.8 s (5.0 to 6.2 s, the closing globe shots). They are a warning only.
3. Shot c1-van2 (39.3 to 45.3 s) runs 6 s in the first 90 s, over the 4 s arrival rule. The map is moving, so this is minor.
4. Ground-zero label text at the small scale in sheet_05 tile 000 and sheet_01 tile 000 is small at full size. Readable, not a defect.
