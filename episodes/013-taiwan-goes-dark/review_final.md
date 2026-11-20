PASS

qc.json: ok true, no issues, shotlist_checks empty (banner present at 1.8 to 4.8 s, 3.0 s, over the moving globe/region shots). Loudness -14.0 LUFS, true peak -1.7 dBTP. near_still 4.6% (30.7 s, no stretch over 4 s). `pace:` lines: 0.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 4 | sheet_00 tiles 1 to 12: a new shot every 2 to 6 s (globe 0 to 2 s, region 2 to 6 s, 6 to 9.9 s, 9.9 to 11.7 s), no card until the chapter card at 42 s. The episode has no strike, so the "payoff" is the Kaohsiung grid going dark (sheet_00 tile 2, "10 GW LOST", "BREAKERS OPEN"); it is a map label and not a hard-hitting image. |
| Story pacing | 4 | Trigger "Hour 0" (sheet_04 tile 4, T+03:01) at about 4:37 after a real-data and real-history set-up of 4 min (later than the 3:30 target); the cold open already shows the blackout. Ends on "THE LIGHTS ARE ON / THIS DID NOT HAPPEN" (sheet_08 tile 12) after chapter 06 "THE DAY AFTER" (sheet_07 tile 10). |
| Map readability | 4 | Labels plated and inside frame throughout (sheet_01 tile 1 "HSINTA POWER PLANT", sheet_04 tile 6 "REMOTE CONTROLS: NO ANSWER"); long_00_20s shows the SIMULATION tag, clock and plated labels clear of each other. Some labels are small on the sheet and a few sit on dark discs (sheet_04 tile 5). |
| Subject and fidelity | 3 | Most region shots show all of Taiwan at 100 to 200 km, the subject is small as it is spoken (sheet_07 tile 4, sheet_08 tile 1). City shots (Hsinchu, sheet_00 tile 11) and the Kaohsiung close-ups (long_00_20s) are good. Correct places throughout. |
| Motion and pacing | 4 | 109 shots in 669 s, 0 `pace:` lines, varied cards (number, bars, timeline, stamp, chapter). The number card 10.5 GW is sampled mid count-up (sheet_01 tile 3 shows 5.1 GW, countTo 10.5 in shotlist.py:243), not a defect. No nuclear flash applies. |
| Packaging | 4 | Title "What If Hackers Shut Down Taiwan's Power and TSMC?" is hypothetical and names who and where; thumb_a "11 DAYS OF GAS" gives number and stake, no shared words with the title. The thumbnail art has an explosion-like flare over an LNG tanker (see finding 1). |
| Accuracy and labelling | 4 | Tags are right on every tile checked: REAL DATA on sheet_01 tiles 1 to 4, REAL HISTORY on sheet_07 tiles 2 to 4, SIMULATION on sheet_04 tiles 4 to 12; sources on factual cards ("Taipei Times, 4 Mar 2022; Focus Taiwan"). 10.5 GW and 5.49 million households match research.md B6. Metadata disclaimer present, no em-dashes (0 found). |
| Mean | 3.9 | |

Findings:
1. Thumbnail thumb_a.png shows a mushroom-cloud-like fireball over an LNG tanker. The episode has no explosion, missile or nuclear event ("No missile fired" is the Short 3 title), so the image suggests something the video does not contain. Not a P0 (it is a gas flare reading, the title is hypothetical), but the packager should prefer a darkened coast or a dark tanker without a blast shape next time.
2. Short 2 (s2_silent_2.png) shows two "LIGHTS BACK" labels close together and "DAY FOUR TO SEVEN." printed over a fading label underneath it, and the clock reads "HOUR DAY 4 TO 7". It is a transition frame and still readable, but a viewer may notice the overlap.
3. The map shots keep Taiwan small in many chapters (subject about a tenth of the frame in the 100 to 200 km views), so "subject fidelity" stays at 3.
4. Trigger (Hour 0) arrives at about 4:37, later than the 3:30 target, because the real-data chapters run first. The cold open covers the gap.
5. Several chart cards (sheet_01 tiles 9 and 11, sheet_07 tile 8) show only a title with an empty bar area at the sampled instant; the bars animate in later, so this is a sampling effect, but check that the bars fill within the card.
