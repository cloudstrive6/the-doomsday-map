FAIL

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening (0 to 90 s) | 3 | sheet_00 tile 001 (open-flash, 4.0 to 9.9 s): flash on the test mountain at about 4 s, a payoff inside 8 s; tiles 002 to 006 arrive every 4 to 6 s. But the banner text is clipped (see P0 1), and `near_still.over_4s` lists 33.8 s (5.1 s) and 56.0 s (4.4 s). |
| Story pacing | 3 | shots.txt: the opening shows the strike, then chapter 1 "A mountain nobody can inspect" (tile 009, 43.7 s) starts the real-data run. `near_still` 61.1 s for 28.4 s, 195.1 s for 28.8 s and 526.8 s for 40.7 s are long sagging stretches. |
| Map readability | 2 | sheet_00 tile 000: the clock "T-00:0?" is clipped at the top-right edge. Tile 003: the label "ONE TARGET: A MOUNTAIN IN IRAN" runs to the right edge. Tile 002: the long red label "JERICHO BATTERY, CENTRAL ISRAEL (SIMULATED)" is overprinted on the glowing Israel coast. |
| Subject and fidelity | 2 | long_01_61s.png and sheet_01 tile 012 (c1-sites, 61 to 69 s): the frame is an empty dark grey field with only the REAL DATA tag, a "50 KM" scale and the source line. No subject is visible. |
| Motion and pacing | 2 | `qc.json` near_still share is 0.395 (257 s), with 16 stretches over 4 s. 2 `pace:` lines: c1-disputed (4.7 s from 77.4 s) and c2-scale (6.5 s from 166.8 s). |
| Packaging | 4 | metadata.json: the title "What If Iran Tests a Nuke? Israel's 4-Day Answer" is hypothetical and names who and where. The description carries "This is a simulation. It has not happened. It is not a forecast". It has no em-dashes (0 found). I did not score the thumbnail in detail. |
| Accuracy and labelling | 3 | The SIMULATION tag is present on the opening tiles, and tiles 010 to 011 carry REAL DATA. The simulation caption on tile 001 ("A 10-kiloton ground burst on a mountain. Simulation: it has not happened.") is good. The banner defect undercuts the labelling. |

Mean: 2.7

near_still: 0.395 (257.0 s). `pace:` lines: 2.

Findings:
1. P0: the banner text is cut off. sheet_00 tile 001 (open-flash, 6.6 s) reads "IMULATION · NOT REAL EVEN". The first and last letters are lost, so the required "SIMULATION · NOT REAL EVENTS" banner is not legible. Fix the banner width or clamp it inside the frame.
2. P0: QC failed. `qc.json` has `ok: false` with the issue "frozen 6.0s at 61.0s". That is the c1-sites region shot, which renders as an empty dark frame (long_01_61s.png). The city or region tiles or data did not load, or the camera sits over empty space. Fix that shot (or its map data) and re-render.
3. P0: the clock is cut off at the frame edge. sheet_00 tile 000 (open-run, 2.7 s) shows "T-00:0" with its last digits hidden at the top-right, partly outside the frame.
4. The label "ONE TARGET: A MOUNTAIN IN IRAN" (tile 003) and the Israel label (tile 002) sit very close to or overlap the edge or other elements. Move the labels inward.
5. Long still stretches in `near_still` need arrivals or camera keys: 61.1 s (28.4 s), 173.3 s (16.2 s), 195.1 s (28.8 s), 323.0 s (14.2 s), 361.3 s (12.3 s), 482.3 s (27.3 s), 526.8 s (40.7 s). Some are chapter text or number cards, but the share (39.5%) is well above the 005 baseline of about 30%.
6. Not every sheet, Short frame and thumbnail was inspected in detail (I looked at sheet_00 and long_01 only). The three P0s above are enough for FAIL. Re-run the full review after the fixes.
