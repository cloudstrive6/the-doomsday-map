PASS

Round 3 re-check. Read f09000, f36000, f00060, f38400 (new stills, rendered 2026-11-19 05:43) and build/validate.txt, which contains only "ok": no `retention:` or `pace:` lines. Nothing new at P0 level in these four frames. Shorts and thumbnails not supplied, unchecked.

Resolved

A. f09000 (150 s, REAL HISTORY, NATO, BRUSSELS): FIXED. The view now holds all three Baltic states. "ESTONIA" sits on the northern outline, "LATVIA" on the middle one, "LITHUANIA" on the southern one, all inside the frame and clear of the corner tag and the scale bar. POLAND and GERMANY sit on their highlighted outlines, and the NATO, BRUSSELS marker is on the Benelux coast. Each label is on its own country.

B. f36000 (600 s, c6-estlink, REAL HISTORY): FIXED. The red "REPORTED CUT" pin is gone. The Estlink 2 line is drawn from the Finnish coast to Estonia, with HELSINKI, TALLINN, ESTONIA and the "DEC 2024" clock plated. The credit "TWZ; NATO Baltic Sentry" is plated at the bottom left and nothing overlaps the corner tag. The line is now labelled "CABLES UNDER THE WATER", which claims no cut location.

9. f00060 (1 s, SIMULATION): FIXED. "RUSSIA" and "KALININGRAD" in amber, "POLAND (NATO)" in blue, "MALBORK AIR BASE" in red, and "ISKANDER" now clear of the border stroke. The frame shows who is against whom. The dashed line is mid-draw, which was accepted.

640 s. f38400 (c6-ns, REAL DATA): FIXED. RUSSIA and MOSCOW in amber, KALININGRAD labelled at the exclave, and "POLAND (NATO)" on the blue land. The frame shows both sides. The credit "Bulletin of the Atomic Scientists; CRS" is plated and inside the frame.

Optional nits, no action required

1. f36000: "CABLES UNDER THE WATER" sits at the left edge, about 700 px from the red line it names. In c6-estlink, move the label to the line (x about 900, y about 450). Rename it "Estlink 2 cable (route approximate)" if the director wants the route caveat kept.
2. f00060: "ISKANDER" floats about 90 px below the border, far from the dashed line's origin. In open-run, attach it to the line start.
3. f38400: the Kaliningrad box is small, but it is labelled and readable.

## Shorts

FAIL

Round 2 re-check. Read s1 (f00030, f00180, f00600, f01200, f01800, f02010, f02040), s2 (f00030, f00180, f00600, f01200, f01800, f02472, f02502), s3 (f00030, f00180, f00600, f01200, f01800, f01920, f01932) and shorts.json. Windows: s1 34.2 s, s2 42.2 s, s3 32.7 s. Opening rule now met: s1 f00030 shows the Malbork ring with "MALBORK AIR BASE", the RUSSIA and NATO legend and the title "TWO ISKANDERS / POLAND AND LATVIA"; s2 f00030 opens on the flash (white-out with the glow ring) and f00180 shows the burst over open water with the dashed line to "LITHUANIAN COAST"; s3 f00030 shows KALININGRAD, "ISKANDER-M (SIMULATED)", the red target ring and the legend. All three have the SIMULATION tag and clock, plated labels inside the frame, nothing in the right rail below y 1000, and the pill ("FULL SIMULATION ON THE CHANNEL") in every final frame. Fixed from round 1: items 1, 2, 7, 8, 9, 10, 11 and the s1 and s3 final frames now exist.

1. FAIL, s2 f00600 (10 s): the frame is solid near-black with only the title band. No SIMULATION tag, no clock, no map, no caption, no label. Cause from episode.json: c5-card (chapter card, 479.26 to 483.26 s) sits inside the s2 window (470.729 to 512.9), so Short seconds 8.5 to 12.5 are a 4 s blank. A chapter dip is deliberate in the long video, but in a Short it is a 4 s black hole with no corner tag. Fix in shorts.json: s2 must not contain c5-card. Cleanest: s2 start 483.26 (c5-fire, burst glow already on, "ring by ring") and end at 519.32 (c5-burn end, 36 s) so it is over 30 s; s3 then ends on the burst (item 2). Alternative: the Short renderer drops chapter-card shots from a Short (window 38 s).
2. s3 ending (f01932, 32.2 s): last frame reads "T-00:06", the burst point is a dot at the sea, no flash. The Short stops 6 s before the payoff, which is a cliffhanger (craft 22) even though s2 shows the burst. Fix: extend s3 end from 458.7 to about 473.5 (through the c5-burst flash, 47 s is too long, so also start s3 at about 434 on "One Iskander-M leaves", giving about 40 s); then s2 no longer needs the opening flash.
3. Judgement on the known unfixed items. s2 tight-ring frames (f01200 20 s, f01800 30 s, f02472 41 s): a dark field with one ring and labels, "COAST: 100+ KM" and "OPEN WATER" as the only context. This is tolerable as a data card for a Short about ring sizes, but the cost is real: the lower 45% of the frame (y 1150 to 1920) is empty in all three, no map anywhere after 3 s, and the "who/where" is carried only by the title band. It is a near-empty-frame finding, not a P0. Cheap improvement: centre the ring at y about 1100 instead of 960 and move the title-adjacent labels down, or add the compass or a scale ring. The 42 s length is within the 30 to 45 s craft range; the cost is two held ring cards of about 4 to 6 s each. Drop it to about 36 s via item 1 and the length question goes away.
4. s2 f01200 and f01800: "COAST: 100+ KM" (x 56 to 405) touches the ring edge at x 405, y 1042 to 1092, and "AN ESTIMATE" crosses the ring's lower edge at y 1100 to 1150. Fix: shift both plates left of x 330 or below y 1160. "COAST: 100+ KM" and "OPEN WATER" also stack with a 6 px offset; align their left edges.
5. s1 f00600 (10 s): the Malbork hit is still a small ring with "CONVENTIONAL HIT", no impact flash visible, and the lower 55% is empty blue (y 1020 to 1920). Not a FAIL (the target is named by 0.5 s). Fix: move the Malbork ring to y about 1150 (camera key) so the frame is centred, and show the impact flash at the hit.
6. s1 f01800 (30 s): the largest text is a half-faded "250 km" subtitle in the caption slot while "LAUNCH (SIMULATED)" sits across the Latvia coast line. Minor. Fix: hold the number a beat longer or fade after the word; move the launch plate off the outline.
7. s2 f02472 and f02502 (final frames, 41.2 s and 41.7 s): identical, the ending is a static ring card on "6.7 square kilometres", so the Short ends on a number rather than a visual payoff; acceptable, but if s2 is re-cut per item 1, end on the 5 psi ring plus its named effect instead of a hold.

Long video check (c5-burst, from shotlist.py lines 644 to 656 and episode.json): c5-burst starts 470.73 and the flash is set at t 0.4 (471.13 s), with tBu = the spoken "bursts" about 0.6 s later; labels key off tBu + 0.4. A flash 0.6 s ahead of the word is a sync nit, not a P0: the viewer sees the white-out, then hears "bursts" at the peak of the afterglow, and nothing is mislabelled. Fix if cheap: burst t = tBu - a (about 1.0). The conventional Iskander hits (lines 241, 473, 492) use burst km 4 to 5, fade 4, against km 14 for the nuclear flash, so they read smaller; the nuclear boom SFX fires on each (BOOMS list at line 920), which is the nit to fix: give the conventional flashes a lower-weight sfx or no boom so the first nuclear boom at c5-burst keeps its weight. build/validate.txt contains only "ok": no retention or pace lines. No P0 on the long video from this change.

Pass conditions for re-check: s2 contains no chapter card (no black or tagless frame at any sample); s3 ends on the burst, not on a T-minus clock; the rest is nits.
