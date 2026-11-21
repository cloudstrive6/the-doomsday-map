PASS

QC: ok true, no issues, `shotlist_checks` empty (banner present: sheet_00 tile 001 shows "SIMULATION · NOT REAL EVENTS" over the burst). Loudness -14.0 LUFS, TP -1.5. `near_still` 42.0 s = 6.3% of runtime. Still stretches over 4 s: 8.0 s at 101.5 s (c1-noexp+signal) and 4.2 s at 258.8 s (c2-start stamp); both under QC's frozen limit, noted below. `pace:` lines: 0 (validate.txt reads "ok").

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening | 4 | sheet_00 tile 001 (2.2 to 5.0 s): fireball on Ramstein under the banner, inside 5 s; tile 002 (5 to 8 s) city view with rings. Arrivals every 1.4 to 4.5 s through 39 s; but tile 009 `open-radars` holds 6.7 s and the spoken disclaimer card text "Simulation: it has not happened." is on screen over moving footage (tile 002). |
| Story pacing | 4 | Trigger (launch, T+00:00) at about 3:00 (sheet_04 tile 054 "THE LAUNCH" card at 289 s, impact 8:13 flight clock at ~7:10); every chapter ends pointing forward (c1 "what does a base in Belarus change?" tile 034, c2 "ask" tile 053). Ends on the day after (sheet_09 tiles 1 to 8 tagged DAY AFTER). Sags: c1 mid-chapter (tiles 028 to 029) is two near-empty map frames. |
| Map readability | 3 | Labels plated and inside the frame on most tiles (sheet_06 tiles 1 to 6, flight-time labels). Weak: sheet_02 tiles 5 and 6 (c1-skeptic, c1-experts) show a bare grey map with two labels and nothing to look at; sheet_09 tile 8 labels crowd at the Belarus edge (VILNIUS 6.0 / LAUNCH overlap the right frame edge). |
| Subject and fidelity | 4 | Right places throughout: Ramstein city view (sheet_07 tile 10) with fireball 0.291 km, 5 psi, 1 psi rings; Belarus launch site east, Germany west (sheet_06 tile 5). Real-data tiles show Dnipro and Kapustin Yar correctly (sheet_01 tiles 3, 4). Weak: long_02_104s is a featureless teal field with a single DNIPRO dot at the 50 km scale. |
| Motion and pacing | 3 | Flash lands hard (sheet_00 tile 001, sheet_07 tile 10). Varied zooms and flight-time clock. But tiles 028, 029 and 025 (8 s, c1-noexp+signal) are near-still maps, and the stamp card at 258.8 s holds 4.2 s. |
| Packaging | 4 | Title "What If an Oreshnik Nuke Hit Germany From Belarus?" names who and where and is framed as a hypothetical. thumb_a.png: "8 MINUTES / NO NOTICE" over a night launcher, readable small, no shared words with the title. Description has the number (8 minutes) in the first lines. |
| Accuracy and labelling | 4 | SIMULATION tag on every tile of chapters 3 to 5 (sheet_04 to sheet_09); 50 kt called "our chosen yield ... no yield has ever been published" (sheet_05 tile 4, script.md:63); "No casualty figure / No published study models this strike" (sheet_08 tile 6); engine numbers match scenario.json (yield 50). metadata.json carries the "This is a simulation. It has not happened" line, no em-dashes. Minor: the day-after tiles mix real facts (Lukashenko's account, INF/New START) under the SIMULATION tag (sheet_09 tiles 3, 4, 7). |

Mean: 3.7 (episode 005 baseline 2.3).

Findings (none is a P0):
1. Near-empty map frames in chapter 1: `c1-skeptic` and `c1-experts` (sheet_02 tiles 5, 6, 121 to 137 s) are a bare grey European map with two small labels, 16 s in total. A viewer would see nothing for those sentences. Give them a subject (Ukraine, the glide path, a Mach 10 versus ballistic bar).
2. `c1-noexp+signal` (101.5 s, 8.0 s) is a featureless teal field with one DNIPRO dot (long_02_104s) and a fading second label. Wide zoom out or an impact marker would help.
3. `c2-start` stamp at 258.8 s holds 4.2 s, just over the 4 s card limit for early chapters; acceptable after 90 s but flagged.
4. `open-radars` (24.2 to 30.9 s) holds 6.7 s, above the 4 s opening cadence rule inside the first 90 s.
5. Day-after tiles (sheet_09 tiles 3, 4, 7) put real-world claims (Lukashenko "several dozen tactical weapons", "No INF treaty. No New START.") under the SIMULATION tag; consider REAL DATA tags for those.
6. sheet_09 tile 8: the right-hand labels (VILNIUS 6.0, LAUNCH (SIMULATED)) sit close to the right edge; legible but tight.
7. Shorts (s1, s2, s3 frames): subtitles present inside the safe area, SIMULATION tag and two-line title band present. s3 `silent_1` caption overlaps the lower part of the Berlin label area but stays readable.
