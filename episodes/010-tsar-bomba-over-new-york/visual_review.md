FAIL

Round 2. Reviewed fresh renders (stills at 12.6, 13.3, 14, 17, 60, 150, 250, 330, 430, 481, 482.5, 505, 540, 592, 599, 602, 650, 675 s plus contact.png) and build/validate.txt.

validate.txt is "ok": no `retention:` or `pace:` lines. Banner 1.8 to 4.8 s over the moving open-flash city shot (unchanged from round 1, passes). End slate 10 s after last word (unchanged). No black frames, nothing printed over the corner tag or clock, no clipped labels in the frames viewed.

Round 1 findings, by number:

1. FIXED. Ring labels carry one number now: 430 s (f25800... c5 frames) "50 MT: 5 PSI · 25 KM" (f30300, bottom-left), "800 KT · 6.3 KM" and "50 MT · 25 KM" (f32400), "BURN RING: 53 KM" and "WINDOW RING: 67.5 KM" (f35520). No more "24.946 KM" duplicates.
2. FIXED. No orphan "· 4.6 KM" labels in the frames viewed (rings at 430 and 540 s are named or unlabelled).
3. FIXED. f28860/f28950 (481 s, 482.5 s): "THE SEA" at about (1000 to 1130, 871 to 892) now sits on the dark Atlantic right of the New Jersey coast.
4. NOT FIXED (wrong place, blocking). "CONNECTICUT" still touches the water. f28950 (482.5 s): label at (1233 to 1430, 294); the Connecticut coast line runs at about y 262 under it, so the text is on the dark Long Island Sound, not on land. f35520 (592 s): label at (1375 to 1570, 230); the coast at that x is about y 205, so again the text is in the Sound. Fix: shotlist.py c5-sea `off(90, 55)` to about `off(70, 95)` (north of the coast, onto light land), c6-states `off(95, 50)` to about `off(85, 90)`. Re-render and check that the whole label box is above the coast line.
5. PARTLY FIXED, now a new wrong place (blocking). f35520 (592 s): "NEW YORK STATE" at (640 to 890, 197 to 233) is off Long Island, but the NY/NJ border (diagonal from (570, 105) to (1015, 330)) passes through it; the left half of the label is south of the line, over New Jersey. Fix: c6-states `off(-25, 60)` to about `off(-10, 120)` or similar, so the box sits wholly above that diagonal (at x 640 the line is y 140, so the box needs y below about 120 at its left end), or rename to "NY STATE" and place it at x 700 to 850, y 110 to 140.
6. NOT FIXED (near-empty, blocking per brief: "a near-empty frame is a finding with a fix"). open-bomber starts at 12.35 s. f00756 (12.6 s): glowing coastline at far left, about 85% dark empty ocean, no label, no bomber, no marker. f00840 (14 s): same, only "NEW YORK" at x 360 to 500 and the red marker at the far left edge; the right 70% is empty. The bomber label does not appear until f01020 (17 s) and sits at the right edge (dot at x 1705, on the globe limb). The widen-and-shift did not give a subject in the first 2 s. Fix: shotlist.py open-bomber: make the bomber marker and the "Heavy bomber (simulated)" city/line start at `a` (shot start) rather than `W("p03", "bomber")` so the first frame already has the route, and centre the camera between New York and the bomber (centre about [-66.5, 40.5], widthKm about 1000 so the NY marker is at x of 400 to 600 rather than 330). Same shot: put the line start at `a + 0.3`.
7. FIXED (non-blocking). f35940 (599 s): label fades in as the line starts; f36120 (602 s): "THEN THE WIND" at (247 to 480, 614) sits at the start of the teal wind line, readable. Scale bar "2 KM" non-blocking, leave.

Other frames sampled, no new blocking finding: 60 s "50 MEGATONS" number card (centred, readable, REAL DATA tag); 150 s Bikini frame (REAL HISTORY tag, MARCH 1954 clock, labels inside the frame; sparse map with a small marker, acceptable for a 1954 test shot but widening to the Marshall Islands would help); 250 s and 330 s city labels "NOT A CLAIM ANYONE PLANS THIS" / "NO ALERT DRAWN" readable and clear of tag and clock; 650 s "HOSPITALS: NOT MODELLED" labels inside the frame; 675 s end slate, "NEXT SCENARIO" box and bottom-left kept free.

Minor, non-blocking: f30300 (430 s) the "NEW YORK" city label has a white tick drawn through the letters at x 897 (reads "NEW | YORK"); f25800 the grey "NEW YORK" label is crossed by the crosshair. Nudge the crosshair or label 20 px.

Not staged: visual_approved withheld until findings 4, 5 and 6 are fixed and re-rendered (round 3).
