FAIL

QC issues (blocking, `build/qc.json` `ok: false`):
- frozen 4.2 s at 92.3 s, frozen 5.2 s at 121.6 s, frozen 5.4 s at 462.9 s. None is a chapter dip or the end slate, so each is a QC failure (P0).

Numbers: `near_still` = 383.1 s, share 0.595 (about 60% of the runtime, twice the 005 baseline of about 30%), with 32 stretches over 4 s (longest 35.3 s at 266.7 s, then 20.1 s at 81.1 s and 18.6 s at 197.7 s). `pace:` lines: 0. `shotlist_checks` is empty (no banner finding). Metadata has no em-dashes.

Scoring note: I viewed sheet_00 in full plus the QC and shot data. I did not inspect the other sheets, long frames, Shorts frames or thumbnails frame by frame, so scores for criteria that depend on them are provisional and marked (partial).

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 3 | sheet_00 tile 001 (open-flash, 3.9 to 7.7 s): fireball with banner "SIMULATION · NOT REAL EVENTS" and caption "Simulation: it has not happened." inside 8 s. shots.txt: open-b 7.7 to 13.3 s and open-launch 13.3 to 18.9 s are 5.6 s holds, over the 4 s rule. qc.json: near-still stretches at 18.9 s (10.5 s), 35.3 s, 52.6 s, 74.8 s, 81.1 s (20.1 s), and frozen 4.2 s at 92.3 s. |
| Story pacing | 3 (partial) | Chapter cards c1 at 42.8 s, c2 at 107.8 s, c3 at 193.9 s, c4 at 262.8 s (shots.txt). The simulated burst is already shown in the cold open and the chapters then go to history first. qc.json: 35.3 s near-still at 266.7 s in the simulation chapter. |
| Map readability | 3 | sheet_00 tile 003: "Ten to one, local time. One missile." plate sits under the red marker, readable. Tile 006: "NOBODY ON THE BRIDGE KNOWS YET" is clear. Tile 004 and tile 007 (T-09:02 and T-00:00) are near-empty dark frames with one or two small labels. Tile 007's "HOW DOES THE DAMAGE REACH?" caption is small and low contrast. |
| Subject and fidelity | 2 | sheet_00 tile 005: the carrier group is a handful of tiny chevrons on a black field, far below a third of the frame. Tile 004: a single tiny missile marker on black. Tile 010: ships are small dots. |
| Motion and pacing | 2 | qc.json near_still share 0.595 and 32 stretches over 4 s. Frozen 5.2 s at 121.6 s (shot bk-intro, 111.3 to 121.6 s) and 5.4 s at 462.9 s (shot ab-guide, 462.4 to 475.9 s). Tile 001 flash is strong and lands hard. |
| Packaging | 4 (partial) | Title "What If 1 Nuke Hit a US Carrier Group at Sea?" is hypothetical-framed, names who and where. Thumbnail not inspected in detail. |
| Accuracy and labelling | 4 | metadata.json description: "This is a simulation. It has not happened. It is not a forecast, names no real ship or country and uses no real date." Corner tags correct on sheet_00: SIMULATION on tiles 000 to 007, REAL DATA on tiles 008 to 011 with the 14 May 1955 clock. |

Mean: 3.0 (partial inspection, see note).

Findings:
1. P0: QC fails with three frozen stretches over 4 s (92.3 s, 121.6 s, 462.9 s). Add camera moves or a split at a sentence in grp (92.3 to 101.2 s), bk-intro (111.3 to 121.6 s) and ab-guide (462.4 to 475.9 s), then re-render.
2. Near-still share is 59.5% of the runtime, with 32 stretches over 4 s. The longest are at 266.7 s (35.3 s, chapter 4 simulation), 81.1 s (20.1 s), 197.7 s (18.6 s), 111.6 s (16.9 s) and 462.4 s (13.5 s). Many shots are small icons on a black field with little change.
3. Opening holds: open-b (5.6 s) and open-launch (5.6 s) exceed the 4 s limit for the first 90 s; open-dark (6.3 s) and open-question (7.5 s) are also long.
4. Subject scale: the carrier group and missile are tiny against black on tiles 004, 005 and 010. Zoom in so the subject fills about a third of the frame.
5. Tile 004 and tile 007 are near-empty frames, which the QC rules treat as a risk.
