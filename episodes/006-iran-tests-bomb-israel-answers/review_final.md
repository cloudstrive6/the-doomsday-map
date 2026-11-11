FAIL

P0: `qc.json` `ok: false` with three frozen stretches (frozen 7.0s at 60.5s, frozen 4.0s at 163.2s, frozen 4.0s at 361.3s). None is a chapter dip or the end slate, so QC blocks the episode.

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 3 | sheet_00 tile 001 (open-flash, 4.2 to 9.9 s): the flash on "GROUND ZERO (SIMULATION)" arrives inside 8 s with the SIMULATION tag and the caption "Simulation: it has not happened". Tile 006 (28.3 to 33.8 s) and tile 007 (33.8 to 39.4 s) are near-empty dark frames with a few labels, and the QC frozen stretch at 60.5 s (7 s) falls on c1-bombs/c1-sites inside the first 90 s. |
| Story pacing | 3 | The simulated burst comes at 421 s (7:01, c5 h-flash), well past the 4:30 bar. The ending is the simulation aftermath (c6 e-dark, f-plume and so on, sheet_05), which is correct. Chapters 1 to 3 run 43 s to 288 s of real history before the trigger. |
| Map readability | 3 | sheet_04 tile 053 (h-fireball): plated labels are legible and clear of the tag and clock. sheet_00 tile 000: the Iran border line runs through the red "T-00:01" clock at the top right. sheet_00 tile 002: the "JERICHO BATTERY" label overlaps the Iran fill. |
| Subject and fidelity | 3 | sheet_04 tile 054 and tile 056: ring maps are centred on ground zero and sized well. sheet_00 tiles 004 to 007: the subject is a tiny dot on a dark empty map. Tile 011 shows a large red circle with small labels. |
| Motion and pacing | 2 | `near_still` is 310.3 s, a share of 0.478, against about 30% for 005. 19 stretches are over 4 s, including 26.3 s at 482.3 s and 25.1 s at 526.8 s. Three frozen stretches in `qc.json`. `shotlist_checks` is empty, so no `pace:` lines (count 0), but the stills data contradicts it. |
| Packaging | 4 | The title "What If Iran Tests a Nuke? Israel's 4-Day Answer" is a hypothetical. thumb_a.png says "ONE MOUNTAIN / TEN KILOTONS / NO INSPECTORS" in large, readable text, and shares no words with the title. |
| Accuracy and labelling | 4 | The description says "This is a simulation. It has not happened. It is not a forecast". The tags are SIMULATION on tiles 001 to 008 and REAL DATA on tiles 009 to 011. Choices are flagged in the video: "10 KT: ENTIRELY OUR ASSUMPTION", "GROUND BURST: OUR CHOICE". |
| **Mean** | **3.14** | |

Reported numbers: `near_still` 310.3 s (47.8% of runtime), `pace:` lines 0 (`shotlist_checks` is empty).

Findings:
1. P0: QC fails on three frozen stretches (60.5 s for 7.0 s, 163.2 s for 4.0 s, 361.3 s for 4.0 s). Add camera moves or split those shots: c1-bombs (54.6 to 60.5 s), c1-sites (60.5 to 70.7 s), c2-korea (154.1 to 167.2 s) and c4-nine (356.4 to 361.2 s).
2. Near-still share of 47.8% is far above 005 (30%). The longest stretches are 482.3 s (26.3 s, w-plume), 526.8 s (25.1 s, e-dark) and 70.8 s (18.7 s, c1-sites). Each needs a new element every 6 s or less.
3. sheet_00 tile 000: the Iran border line crosses the "T-00:01" clock at the top right. Re-frame the opening region shot so the clock stays clear.
4. The simulated trigger lands at 7:01, well past the 4:30 pacing bar. The real-history chapters 1 to 3 should be tightened, or the trigger moved earlier.
5. `shotlist_checks` is empty, so the banner and end-slate checks were not reported. The "SIMULATION · NOT REAL EVENTS" banner was not seen in the sampled tiles (tiles 000 and 001 carry the tag only). Confirm it exists in `episode.json`.
6. Metadata is clean: no em-dashes found, the disclaimer is present, and the title is framed as a hypothetical.
