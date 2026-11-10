FAIL

Round 2. Checked validate.txt ("ok", no `retention:` lines), the banner, the end slate and about 17 re-rendered stills: 3 s, 12 s, 20 s, 22 s, 28 s, 34 s, 37 s, 315 s, 380 s, 390 s, 430 s, 440 s, 448 s, 460 s, 470 s, 538 s and 675 s.

Resolved from round 1:
- The target no longer sits among villages. At 470 s (f28200) the 4.52 km 1 psi ring contains no buildings, only roads and a stream. The open-field caption "No mapped building within 5 km of this point." is consistent with the map.
- Village labels vs the claim: Lozova is 5.7 km from the target (scenario.json 49.517, 37.824), Berestove 5.8 km, Zahryzove 8.2, Kruhliakivka 7.6, Krokhmalne 9.4 and Tabaivka 9.5. All are outside 5 km and outside the 4.52 km ring, so they do not contradict the claim. Lozova and Berestove sit close to the line, so keep the caption wording "within 5 km" and do not tighten it.
- The NATO frame (f32280) is now consistent: Ukraine teal, Russia yellow, NATO blue. It shows who is against whom.
- Banner at 26.95 to 29.95 s (3.0 s) over the moving `open-banner` region shot. It is readable and clear of the SIMULATION tag and the clock.
- End slate (f40500) keeps the intended half-empty layout with the "NEXT SCENARIO" box. Its line is "Iran tests a bomb, and Israel answers." with no date.
- Ring frames (c5): the labels now have dark backings and are readable. The rings still cross some labels, which is minor (finding 3).

Findings:

1. BLOCKING. Text overlap in shot `open-field` (f01320, about 22 s). The village label "BERESTOVE" drifts into the top-right corner and prints on top of the "09:23" clock, giving "09:23" and "BERESTOVE" overlapped. The label sits outside the safe corner area. Fix in the `open-field` shot's `labels` in shotlist.py: drop the Berestove, Krokhmalne and Kruhliakivka labels, which are not needed. Or keep only Lozova and Tabaivka and make sure no label falls in the top-right clock block or the top-left tag block as the camera zooms from 40 km to 9 km. The zoom is on the shot's `zoomTo`, so check the label positions at the end of the zoom, not at the start.

2. Minor. In `c3-farm` (f18900, 315 s) the "LOZOVA" label sits under the caption box and is partly hidden. Remove the Lozova label from this shot or move the caption. The label has no purpose here.

3. Minor. In the c5 ring frames (f26880, f27600, f28200) several labels still cross rings:
   - "FIREBALL · 0.18 KM" sits on the 5 psi and burn rings.
   - "20 PSI · 0.34 KM" sits on the burn ring.
   - "STAGING AREA (SIMULATED)" is cut by the red ring.
   - "THIRD-DEGREE BURNS · 1.91 KM" sits on the 1 psi ring.
   They are readable thanks to the backings, so this is not blocking. If time allows, give each ring label an offset that places it outside its own ring.

4. Minor. In the opening globe (f00180) the "LAUNCH: BELGOROD REGION (SIMULATED)" label is small, pink on olive, and the first letter touches the marker. It is legible but weak on a phone. Offset the label or enlarge it slightly.

5. Minor. `open-ground` (f02220, 37 s) is almost empty and dark: a crosshair, "NOBODY HAS BEEN TOLD", and a faint road and pond. It is inside the 4.3 s limit and it is deliberate, but it is the weakest frame of the cold open. Not blocking.

To pass: fix finding 1 in shotlist.py, run `python -m studio shotlist 005-russia-one-tactical-nuke-ukraine`, re-render a still at 22 s, and confirm the clock is clear. The stage is not advanced: `visual_approved` was NOT recorded.

## Round 3 (showrunner)
Blocker (Berestove label over clock) fixed by dropping labels; stills 21-23 s checked, clock clear. PASS.

## Shorts
PASS

Windows (checked against narration/timing.json and the staged vertical shot lists; sample frames at 1, 12, 30 and 50 s of each):
- s1 338.384 to 393.300 (54.9 s): starts on p25, ends 0.3 s after the last word of p29 ("to warn them"), on the shock wave. Payoff, not a cliffhanger. In range.
- s2 421.200 to 475.100 (53.9 s): starts on p32, ends on p37 ("flying glass becomes the hazard"), the last ring. Payoff. In range.
- s3 141.416 to 194.700 (53.3 s): starts on p13, ends on p15 ("to warn against it"). Acceptable closing beat. In range.
- All three start on a shot boundary, so the stager does not fail. Title bands (two lines, white then yellow) are legible, centred, below the top bar and clear of the tag and clock. No real-person likeness (maps and globe only; Putin and Biden are named in text only, as speakers, not victims). No simulated date anywhere; s3 shows real 2022 dates tagged REAL HISTORY.

Minor findings (not blocking):
1. s1 at 12 s: the "TARGET: OPEN FARMLAND" label is cut by the right edge, and at 30 s the "STAGING" label is cut too. Shift those labels left or anchor them left of the marker in the c4-m0 and c4-m2 shots (labels/cities `anchor` or offset).
2. s1 at 1 s and 30 s: the map labels (LAUNCH, ISKANDER-M) are very small on a phone, and the lower 40% of the frame is empty apart from the subtitle. At 30 s (c4-m2) the frame is nearly empty: a dashed line and a faint label. Consider a larger label size or a tighter zoom for Shorts.
3. s3 at 30 s: the clock label "DEFENSE CHIEFS" sits just under the title band and is hard to read over the globe. Minor.
4. s2: ring labels still touch rings (already noted for the long video); they are readable.
