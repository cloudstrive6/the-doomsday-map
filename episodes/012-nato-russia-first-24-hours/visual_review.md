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

Read all 15 frames (s1, s2, s3 at 0.5 s, 3 s, 10 s, 20 s, 30 s) and shorts.json. Windows are 34.2 s, 42.2 s and 32.7 s (craft 20 length: ok, but s2 is over 40 s). Title bands (y 210 to 392, two lines, white then yellow) are legible and clear of the corner tag and clock in all three. Corner tag SIMULATION present in every frame. No clipped or overlapping labels at the frame edges beyond the notes below.

1. s1 opening FAIL (f00030 0.5 s, f00180 3 s). Both frames show only a dim Kaliningrad outline on a dark map, a faint "HOUR 0: FIRST STRIKE" and a "T-02:46" clock. No strike, no Malbork, no Adazi, no flash in the first 3 s; the first hit appears at f00600 (10 s). Fix: in shorts.json s1 start the window at the Malbork impact paragraph (or the second-strike line), or have the first shot be the Malbork region with the target ring and "MALBORK AIR BASE" visible from frame 0; trim the 8 s of launch build-up.
2. s1 title band (shorts.json s1.title "TWO ISKANDERS / ON NATO BASES", craft 21). No named target; a stranger cannot tell where. Fix: "TWO ISKANDERS / POLAND AND LATVIA" or "ISKANDER HITS MALBORK, POLAND".
3. s1 f00600 (10 s): the hit is a small red ring, no flash, no fireball, the lower 60% of the frame is empty blue. Fix: zoom the region on Malbork (narrower widthKm, camera key toward the target) and add a burst or impact flash on the conventional hit; move "WITHIN EASY REACH OF KALININGRAD" off the coast outline it sits on.
4. s1 f01800 (30 s): the biggest line is a half-faded "250 km" in the subtitle slot, ADAZI is dim red, and the "LAUNCH (SIMULATED)" label sits over the Latvia border line. The last 3 s (pill) was not sampled. Fix: render and supply the final frame (about 34 s) and one at 31.5 s; the ending must be the Adazi impact on screen, not a fading number (craft 22).
5. s2 near-empty frames (f01200 20 s, f01800 30 s). A black field with one grey circle or ring, no coast, no map; the lower 40% of both frames is empty. "NEAREST COAST: OVER 100 KM" has no coast to point at. Fix: use a region view about 300 km wide with the Lithuanian and Gotland coasts and the ring drawn to scale, or a city shot of a real port for the 5 psi ring; keep the ring in the upper-middle of the frame.
6. s2 f01200 (20 s): labels stacked over the fireball disc: "NEAREST COAST: OVER 100 KM" and "BALTIC SEA: OPEN WATER" cross the circle edge, "FIREBALL" sits inside it, and "RADIUS: ABOUT 150 M" repeats "ABOUT 300 M ACROSS". Fix: drop one of the two size labels and place the plates outside the ring (left, x under 300). Same at f01800: "5 PSI: 1.46 KM" is printed across the ring's top edge, move it above the ring.
7. s2 opening (f00030 0.5 s): a dark map with "BALTIC SEA: OPEN WATER" faint grey and no burst; the glow arrives by f00180 (3 s), so it passes, but 0.5 s is a dim map with no subject. Fix: start the window about 3 s later, on "The warhead bursts", or put the burst glow on frame 0 (burst at shot start).
8. s3 opening FAIL (f00030 0.5 s, f00180 3 s). A wide Baltic map with Kaliningrad small and unlabelled (a ghost "KALININGRAD" is half faded under the outline at 0.5 s); no strike and no named target in the first 3 s. The open-water burst point only appears at f00600 (10 s). Fix: open on the launch from Kaliningrad with the dashed line and "OPEN WATER (SIMULATED)" already drawn, or move the window start to the line "One Iskander-M leaves Kaliningrad". With s1 also failing, zero of three Shorts meet "strike or named target in the first 3 s"; s2 is the only one that nearly does.
9. s3 duplicated text (f00030, f00180): "HOUR 22" appears three times (clock "HOUR 22" with caption "HOUR 22", the left label "HOUR 22", and the subtitle "Hour 22."). Fix: remove the left label in the first shot of s3 (labels field) and set the clock caption to "SIMULATED TIME".
10. s3 who is against whom (f01200 20 s): the frame shows Poland, the Baltic states and Kaliningrad in colour but names none of them and has no legend; "WARNING SHOT" is a dot in the sea with no line. Fix: add the region legend (RUSSIA, NATO) as s1 f01200 has, or labels for KALININGRAD and POLAND (NATO), and keep the dashed line.
11. Right rail (Shorts safe area): s3 f00600 "LAUNCH" (plate to x 1020, y 1126) and s3 f01800 "KALININGRAD" (to x 997, y 1102) and "OPEN WATER (SIMULATED)" (to x 1024, y 871) sit in the right 120 px where YouTube's like and share buttons cover the lower right from about y 1100. Fix: keep labels under x 900 below y 1000 (anchor left of the point, or shift the camera so Kaliningrad sits left of centre).
12. Craft 20: s3 (426 to 459 s) and s2 (471 to 513 s) cover the same warning-shot event back to back and read as part one and part two. Not the same rings, so not a FAIL, but s2 at 42 s is over the 30 to 45 s target with several near-empty seconds; trim s2 to about 34 s (drop the "5 PSI" hold to the line that names the ring).
13. Craft 19: strike windows are s1 (conventional, no flash), s2 and s3 (nuclear), but only s2 shows a burst on screen in the first 10 s. Fix as in 1, 3 and 8.

Pass conditions for re-check: s1 and s3 show the target or the burst by 3 s; s1 title names a place; s2 has coast context in every frame after 10 s; the final frame of each Short (supply f at duration minus 0.5 s) ends on the payoff with the pill and nothing in the right rail.
