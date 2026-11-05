FAIL

Scope: all 77 stills plus contact.png were available. I inspected the contact sheet (every shot: tags present and correct, no black frames, no gore, no real-person likeness, bars/number/stamp/chapter cards readable) and viewed in full size the map, city, globe and bar frames at risk (open-seattle, open-alaska, open-launch, c1-tests, c3-gmd, c4-order, c4-nocause/hs20, c4-yields, c5-intercepts, c5-hawaii, c5-arrive, c6-fireball, c6-burns, c6-fallout, c6-sf, c6-vafb, c6-bangor, c7-third, end). Corner tags: all shots carry REAL DATA, REAL HISTORY or SIMULATION correctly (endslate has none, fine).

Blocking findings (text overlapping text, labels at the edge):

1. c6-burns (frame f31860, T+25:30): the "20 PSI . 0.868 KM" label sits on top of the "FIRST HILL" street label ("FIRST HIL20 PSI"), and "FIREBALL . 0.555 KM" crowds "SPACE NEEDLE" and "MADRONA". The 5 PSI and 6.053 km labels also run across ring lines and a road. Fix in the c6-burns city shot: move the ring labels to a fixed angle clear of street labels (for example place 20 psi at the lower left over water, 5 psi and burns at the right edge of each ring but inset), or drop the neighbourhood labels (FIRST HILL, MADRONA, LESCHI, SPACE NEEDLE) for this shot via its labels field.
2. c6-fireball (frame f30156): "FIREBALL . 0.555 KM" overlaps the "FIRST HILL" label under it. Fix: remove FIRST HILL from this shot's labels, or shift the fireball label above the ring.
3. c7-third (frame f38550): "THIRD SITE: EAST COAST, BY 2031" is anchored at x about 1530 and runs to x 1873, inside the right-edge margin, and a state border/coast line cuts through the word SITE. Fix: anchor the label to the left of the point (right-aligned) or move the point/camera so the label sits at x under 1700; shorten to "THIRD SITE, BY 2031".
4. c6-fallout (frame f32826): the caption band covers the "TACOMA" label (dot visible, name hidden behind "dust rises high"), and the "SEATTLE" label touches the ring edge. Fix: drop or move the Tacoma label up, or shift the camera so cities sit above y 900; keep the caption clear of labels.

Non-blocking but fix if cheap:

5. c6-bangor, c6-sf, c6-vafb (f33342 region, f33630, f33936): the coastline polygons are coarse and unrecognisable at this zoom, and Bangor and Vandenberg have no place label on the map (only the caption names them). A phone viewer cannot tell where on the coast these are. Fix: add a labels entry ("BANGOR", "VANDENBERG SFB") offset from the rings, as c6-sf already does with OAKLAND.
6. c1-tests (f05382): "PUNGGYE-RI . SIX TESTS" starts on the dashed ring, so the first letters collide with it; the source line "CRS; CNBC; Noisar" is partly hidden by a coastline. Fix: offset the label 30 px right and move the source line or lower its overlap by dimming the coastline under it.
7. c3-gmd (f14208 area): "FORT GREELY, ALASKA . 40 INTERCEPTORS" overlaps the dashed range ring. Same offset fix.
8. Source/credit lines (bottom left, all shots) are very dim grey; unreadable on a phone. Raise opacity a little in the shared credit style.
9. endslate (f42900): the right-hand preview box is an empty dashed rectangle with a faint "NEXT SCENARIO" caption, which looks like a missing image. Fix: fill it with a still for the next scenario (the eight-hundred-kiloton airburst) or compare with episodes 001 and 002 and match them; if it is the house template, ignore.
10. open-launch (f00996): "PYONGYANG AREA" sits over the red country fill and the trajectory line starts at it; readable, but only North Korea is marked. The target (US West Coast) is off-frame, so who-against-whom is carried by the caption only. Acceptable for a cold open; optionally widen the view or add a "UNITED STATES" label.

Re-render stills for c6-fireball, c6-burns, c6-fallout, c7-third, and re-run this review. Items 1 to 4 must be fixed before approval.
