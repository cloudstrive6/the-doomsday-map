FAIL

Checked: build/validate.txt, the contact sheet and about 30 stills I rendered (the director's folder held only two), plus episode.json and shotlist.py.

Mechanical checks pass:
- validate.txt is "ok", with no `retention:` lines.
- The banner runs 26.57 to 29.57 s (3.0 s) over the moving `open-banner` region shot. It is readable and clear of the SIMULATION tag and the clock. No static disclaimer card exists.
- Last word ends 673.72 s and durationSeconds is 683.72, so the end slate is exactly 10 s. The end-slate layout is as intended.
- Corner tags are correct throughout. Clocks read "Day 1 · Kyiv time 09:20", "T+..." and "Day 4 to 7". The only calendar date is "NOV 2022", which is real history. No simulated calendar date is on screen. `scenario.computed.json` has `t0_utc` 2026-12-08, but it is not rendered, so keep it off screen.

Findings:

1. BLOCKING, editorial and visual contradiction (shots `open-field`, `open-ground`, `c3-farm`, `c4-flash`, `c4-shock`, `c5-*`; scenario target). The close-up OSM map (`kharkiv-farmland`) shows farm-hamlet building clusters and a village road net.
   - Frame f01200 at 20 s shows small building clusters upper right and bottom centre next to the "THAT FIELD" crosshair.
   - Frame f28200 shows the 1 psi ring (4.52 km) covering them. Those clusters are about 2 to 3 km out, so inside the 1.9 km burn ring and the 5 psi ring only in places, and clearly inside the 1 psi ring.
   - The script and captions say "open farmland", "No city", "no unit or person in it is real" and "eight point eight square kilometres of farmland". That does not hold when the rings are drawn over four real villages.
   - A viewer who spots the buildings will read it as an inaccurate or evasive claim, and the villages are real places with real residents.
   - I recommend moving the target. Edit `scenario.json` (the strike target) to a point with no mapped settlement within about 5 km, so the 4.52 km 1 psi ring is clear. Re-run `python -m studio scenario 005-russia-one-tactical-nuke-ukraine`, refetch `node scripts/fetch-city.mjs kharkiv-farmland <lon> <lat> <widthKm>`, and update `TGT` in shotlist.py.
   - If no such site can be found, the fallback is to relabel. Change "open farmland" to "a sparsely settled farming area" in script.md, the captions and the target labels. Say that a few villages lie inside the outer 1 psi zone, and show them as an unlabelled "villages at the edge of the 1 psi zone" callout. Do not claim "no people". This weakens the "No city" line and needs a fact-screener recheck. Moving the target is the cleaner fix.
   - Either way, the c5 captions that quote the 8.8 km² area should say what lies in it.

2. Ring labels are crossed by lines (c5 city frames, f28200 and f27000).
   - The "5 PSI · 1.67 KM" text sits on top of the yellow burn ring.
   - "THIRD-DEGREE BURNS · 1.91 KM" and "1 PSI · 4.52 KM" are cut by the road.
   - "20 PSI · 0.34 KM" overlaps the red ring.
   - "FIREBALL" runs into the fireball glow, and "STAGING AREA (SIMULATED)" touches the crosshair.
   - Fix: give each ring label an offset at a distinct angle (outside its own ring, away from the road), or add a dark backing to the label text. In f27000 the 5 psi label is already fine, so this applies to the stacked-ring frames.

3. The 09:20 opening globe (f00180) has the label "BELGOROD REGION (LOCATION SIMULATED)" over a large red square marker with a white dot on top.
   - The first letters sit on the marker and the text is red on olive. It is small and low-contrast on a phone.
   - Fix: shrink the marker, offset the label right and up, and use a lighter fill or a dark backing.

4. Colour inconsistency in the NATO frame (c6-nato, f32400).
   - Ukraine is yellow ("UKRAINE: NOT A MEMBER") and Russia is not highlighted, while in the opening Ukraine is teal and Russia is yellow.
   - In the NATO frame, teal means NATO and the yellow area is Ukraine, so the viewer cannot tell who is against whom.
   - Fix: either keep yellow for Russia and use a neutral colour for Ukraine, or add a legend line such as "Teal: NATO. Yellow: not a member."

5. Minor. In `open-field` (f01200, 17.8 to 23.6 s), the map is nearly empty and dark with only "THAT FIELD". It has some drift and a clock, so it is allowed under 4 s, but it is the weakest frame in the cold open. Consider a faint rail or road highlight, or cut it to under 4 s. Not blocking.

6. Minor. The legend and footer text in the ring frames ("Effects: Glasstone and Dolan...") are very small and dim. They are fine as credits, but if the thermal and blast numbers are being read aloud, make the ring labels larger (about 28 px).

Frames the director did not check that I viewed:
- Country highlights (opening globe, NATO map): see findings 3 and 4. The Poland/Slovakia/Hungary highlight in the c3 "our choices" map (f34500) is readable and shows who is against whom.
- Ships: the Iskander chevron and dashed path are visible in `open-banner`, `c4-m0` and `c4-m2`. The cargo ships in `c6-seas` are visible with their label, and the labels are inside the frame.
- Chapter 05 rings: legible and correctly scaled, with the issues in finding 2.

Re-review needed after the target is moved. No re-render is needed for items 2 to 6 if they are fixed in the same pass.
