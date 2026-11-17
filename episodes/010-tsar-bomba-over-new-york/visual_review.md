FAIL

Reviewed: build/stills (director set plus my renders at 0.3, 3, 8, 15, 23, 30, 396 to 670 s incl. 478, 481, 482.5, 589, 591, 592.8, 605, 607 s), validate.txt, shot list.

validate.txt is "ok": no `retention:` or `pace:` lines. Banner 1.8 to 4.8 s (3.0 s) sits over the moving open-flash city shot, clear of the SIMULATION tag and clock; spoken line "One 50 megaton airburst. Simulation: it has not happened." is on screen. Flash at 2.0 s. End slate: last word 670.26 s, duration 680.26 s = exactly 10 s; layout half-empty as intended. No black frames, no text-over-corner-tag, no clipped labels found. Chapter 05/06 tags (SIMULATION, DAY 1 clock) present and correct.

Findings (fix then re-render):

1. Ring-label wording is garbled and shows false precision (blocking). Frames at 396 to 560 s (c5-wider, c5-centre, c5-20psi, c5-hold, c5-s-5psi, c5-vs): "5 PSI: 25 KM · 24.946 KM" (c5-2000/c5-5psi style frame, bottom-left), "50 MT: 25 KM · 24.946 KM", "20 PSI RING · 5.079 KM", "ALMOST 25 KM IN RADIUS · 24.946 KM", "FIREBALL: RADIUS 4.6 KM · 4.618 KM", "5 PSI RING: THE ONE TO HOLD IN MIND · 24.946 KM". The engine appends the raw computed km to every ring label, so the same radius is printed twice at two different precisions (25 vs 24.946). Fix: in shotlist.py `ring()` / `reg`/`cty` ring expansion (line 101 and 121) drop the auto-appended raw km, or round it to one decimal and strip it when the label text already contains a km figure (e.g. "5 PSI: 25 KM" with no suffix, "20 PSI: 5.1 KM", "FIREBALL: 4.6 KM"). Use at most one number per ring.

2. Orphan ring labels starting with a dot (blocking, same fix). c5 frame at 412 s and 425 s: a label reading only "· 4.618 KM"; frame at 424 s: "· 5.079 KM"; frame at 465 s: "· 6.286 KM" and "· 24.946 KM". These are rings with an empty `label=""` plus the appended km, so the viewer sees a bare dot and number with no name. Fix: give each of those rings a real label ("FIREBALL: 4.6 KM", "20 PSI: 5.1 KM", "BURN: 6.3 KM", "5 PSI: 25 KM") or suppress the label.

3. "THE SEA" label is on land (wrong place). c5-sea, 478 to 483 s (still f28950): "THE SEA" at about (700 to 830, 950) sits on the light New Jersey land mass left of the coast line; the sea is the dark area to its right. Fix: shotlist.py line 444, change `off(-12, -62)` for "The sea" to a point clearly over the dark Atlantic, e.g. `off(150, 130)` (south-east of the ring), so it sits right of the coast.

4. "CONNECTICUT" label is in the wrong state (wrong place). Same frame (f28950, about (905 to 1100, 256)) and c6-states at 589 to 593 s (f35568, (1035 to 1230, 224)): the label is left of the New York / Connecticut border line, i.e. over Westchester, New York. Connecticut is the land right of that border and north of the dark Long Island Sound. Fix: line 444 `off(30, 62)` and line 503 `off(40, 60)`: move east, to roughly `off(90, 55)` and `off(95, 50)`, onto the land above the Sound; recheck by render.

5. "NEW YORK" state label sits on Long Island in c6-states (f35568, (1130 to 1280, 632)), beside Brooklyn at the burst point; reads as the city, not the state, and the 50 MT ring shows the same text nearby. Fix: line 503 `off(52, -10)`: move it up-left over upstate land (e.g. `off(-20, -55)`) or rename "NEW YORK STATE".

6. Near-empty frame at 15 s (open-bomber, f00900 rendition): dark grid with one bomber square at the right edge and "NEW YORK" label at the far left edge, about 90% empty field; not a still, but a weak subject for 5.7 s. Fix: shotlist.py open-bomber, widen less or centre the camera so the bomber and Manhattan are both in the middle third, and move the "NEW YORK" label inward.

7. Minor, non-blocking: c6-wind "THEN THE WIND" (f36000, 600 s) shows a floating label with no arrow or plume until later; add the plume/wind line from that shot's start, or move the label to the plume start. Scale bar "2 KM" at 3 s is dimmer than the caption but readable; leave.

Not staged: visual_approved withheld until findings 1 to 5 are fixed and re-rendered.
