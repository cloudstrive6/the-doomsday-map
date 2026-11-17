PASS

QC: ok, no issues, `shotlist_checks` empty (banner present, no retention lines). Loudness -14.0 LUFS, TP -1.7 dBTP. `near_still` = 8% (54.4 s). `pace:` lines = 0 (validate.txt reads "ok").

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 4 | sheet_00 tile 001 (open-flash, 2.0 to 6.7 s): fireball glow over the Manhattan street map with "FIREBALL · 4.6 KM" and caption "One 50 megaton airburst. Simulation: it has not happened." inside 8 s. Tiles 000 to 011 arrive every 2 to 6 s; the chapter card (tile 007) is 3.5 s. Held back from 5: tiles 002 to 004 are quiet maps with only labels changing. |
| Story pacing | 4 | Trigger reached in the opening, then history chapters; sheet_09 ends on "THE RINGS DO NOT STOP AT ITS EDGE" and a Day 1 chapter (sheet_08 tile 003 "THE DAY AFTER"), so it ends on the aftermath, not history. Sagging: sheet_09 tiles 008 to 009 (1961 Arctic, "4.0 MILLION") sit in a Day 1 chapter. |
| Map readability | 4 | Labels plated and inside the frame, clear of tag and clock (long_00_21s: "NEW YORK" / "ONE BOMB ABOARD" at left, clock top right). sheet_08 tile 000: "800 KT · 6.3 KM" and "50 MT · 25 KM" legible. Minor: sheet_00 tile 003 "HEAVY BOMBER (SIMULATED)" sits near the right edge but inside it. |
| Subject and fidelity | 3 | Rings and fireball fill the frame on the city maps (sheet_05 tiles 9 to 10, sheet_08 tile 000). Several chapters show a small subject at region scale: sheet_05 tile 004 (Manhattan a speck, labels only), sheet_09 tiles 006 to 007. |
| Motion and pacing | 3 | Flash lands in tile 001. Dips only around chapter cards. QC lists four still stretches over 4 s (142.1 s for 8.6 s; 665.1 to 679.9 s in the end run), all inside the allowed limits and flagged only as near-still. |
| Packaging | 4 | Title "What If a 50 Megaton Nuke Hit New York? Ring by Ring" is hypothetical; thumb_a.png reads "9 KM FIREBALL / BIGGER THAN MANHATTAN" large and legible small, with different words from the title. |
| Accuracy and labelling | 4 | Every scene carries a tag (REAL DATA on sheet_00 tile 005, REAL HISTORY on sheet_03 tile 000, SIMULATION elsewhere). sheet_09 tile 006: "NO PUBLISHED DEATH TOLL, SO NONE", "NOT MODELLED" labels. Metadata states "This is a simulation. It has not happened." and lists our choices. |
| **Mean** | **3.7** | |

Findings:
1. Thumbnail claim "BIGGER THAN MANHATTAN" is true by area only (fireball about 66 km2 against about 59 km2) but Manhattan is about 21 km long and the 9 km figure is a diameter. Soften to "WIDER THAN LOWER MANHATTAN" or similar on a later pass. Not a P0: the 9 km figure matches the engine.
2. Shorts frames: titles and subtitles sit inside the safe area; "FULL SIMULATION ON THE CHANNEL" pill is present in the last seconds of Short 1. Short 1's first frame subtitle area is empty (0 s), acceptable.
3. The "ABOUT 1 MINUTES" number card (sheet_05 tile 001) is a count-up caught mid-animation (final value "ABOUT 3 MINUTES", episode.json:3832); the plural reads oddly at 1. Worth tuning the count-up so the review frame, and the first frames viewers see, never show "1 MINUTES".
4. Chapter 2 Bravo shot (133.4 to 142.8 s) is a 9.4 s single shot, over the 6 s pace target after 90 s. Warning only.
5. Metadata: no em-dashes found; description has the simulation disclaimer, sources and AI-narration note.
