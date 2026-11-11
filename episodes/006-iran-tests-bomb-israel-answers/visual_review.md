PASS

Round 3 (final). Re-ran `python -m studio shotlist` (70 shots, 649.18 s; build/validate.txt is "ok": no `retention:` or `pace:` lines, end slate and music pass). Rendered 71 fresh stills, one at the midpoint of every shot plus 0.5 s, and read the contact sheet plus the frames below.

Round 2 blockers, verified on frame:
- c4-salvo (f20646, 344 s, HOUR 42): "RAID LANDS: TEST SITE" now sits beside a red marker inside Iran (x 1517, y 403) with a second marker below it; Iran (amber) and Israel (teal, NEVATIM marker) both on screen with the IRAN/ISRAEL legend, "IRAN FIRES BACK" and the red salvo arrow. Who is against whom is clear.
- c4-cabinet (f22656, 377.6 s, DAY 4): teal Israel outline and "ISRAEL'S CABINET DECIDES" marker are on screen together at left, Iran's edge at right, legend present.
- c3-zero (f12852, 214 s): shot is now 7.3 s (210.5 to 217.8) with the test ring, "THE TEST" label and the four named sites; no 20 s static stretch.
- c4-entrances (f19548, 325.8 s, REAL DATA): shot is 9.2 s, label text fully inside the frame, not over the tag or scale.
- w-plume (f29496, 491.6 s, DAY 1): ground zero marker, dashed plume direction line, Fordow and Natanz, caption "Scenario engine; wind is our assumption" clear of the line.
- Captions: f00420 (7 s) caption is plated and readable ("A 10-kiloton ground burst on a mountain. Simulation: it has not happened."); banner window 4.01 to 7.01 s over the moving flash; f00756 (12.6 s) is a moving night globe with Israel against Iran.
- Corner tag present and correct on every frame read (SIMULATION or REAL DATA to match the chapter). No black frames outside the end slate; no label clipped at the frame edge.

Warnings (not blocking, fix if time allows):
1. f20028 (333.8 s, c4-aim, "ISRAEL'S AIM / HOUR 40"): near-empty dark field with five labels and no coast or border; the teal label "ISRAEL'S AIM: THE ENTRANCES" floats 60 px above "OUR SITE" with no marker of its own. Fix: widen to about 150 km or add a border, anchor the aim label to the OUR SITE marker.
2. f19548 (325.8 s, c4-entrances): "STORAGE TUNNELS: TOO DEEP FOR EVEN THAT BOMB" has no marker; field is bare brown. Same fix.
3. f29496 (w-plume): the "DIRECTION ONLY: NO DOSE, NO DISTANCE" plate covers the amber plume glow, so the plume is mostly a dashed line. Move the label 60 px up or left.
4. f20646: the Iran border glow crosses the "THE RAIDS LAND" header and the "200 KM" scale text at the right. Readable, small.
5. f21528 (353.7 s, c4-nine isotype): row of ten marks sits top right, bottom 60% of the frame empty; under 6 s. Enlarge the marks or centre them.
6. Dark-brown sparse frames (c3-zero f12852, c4-aim) are acceptable only because the camera moves and a label arrives within 4 s.

## Shorts

FAIL

Checked `shorts.json` against `episode.json`, `narration/words.json` and the staged Shorts shot lists in `video/public/episodes/006-iran-tests-bomb-israel-answers-s1/s2/s3`. Rendered 28 stills (1080x1920) across the three Shorts and read the contact sheets.

What passes:
- Start on a paragraph: s1 0.0 s is "Four thirty-eight in the morning" (p01); s2 373.552 s is "Day four" (c4 paragraph start, first subtitle "Day 4. In our scenario,"); s3 431.368 s is "A burst on the ground lifts earth..." (paragraph start, shot h-fireball).
- Ends: s2 ends on "11 kilotons together." (payoff). s1 ends on "The work under the rock has not stopped." and s3 on "we give no number for the tunnels." (both are acceptable closes but weak payoffs, see 6).
- SIMULATION corner tag present and correct in every frame read (s1 f00000 to f02004, s2 f00000 to f02466, s3 f00000 to f02088), clear of the title band.
- Title band readable on all three ("ONE 10 KT NUKE / ON A MOUNTAIN", "... FOR A BURIED SITE", "10 KT NUKE / ON A MOUNTAIN"): white and yellow on a dark plate, two lines, centred, no overlap with the tag or clock. Subtitles sit at about y 1320 px, well above YouTube's bottom overlay. "FULL SIMULATION ON THE CHANNEL" pill present in the last 3 s of all three.
- Who is against whom: s1 and s2 map frames carry the IRAN (amber) and ISRAEL (teal) legend.

Findings:
1. s3 first frames (f00000 at 0 s, f00090 at 1.5 s, f00240 at 4 s): a near-empty dark field with one faint crosshair and a ridge line; "SIMULATED LOCATION" arrives at 1.5 s, and the fireball only at about 10 s (f00600 shows it). No strike, no named target in the opening 3 s, and the first four seconds are almost identical (still-stretch risk near the 4 s limit). Fix: start s3 on `h-flash` (421.38 s) so the white-out and fireball open the Short (start must stay on a paragraph: the "In our simulation, the warhead bursts on the ground" paragraph), or add a `camera` key and the fireball ring in the first 2 s of `h-fireball`.
2. s2 first frames (f00000 and f00090, 0 to 1.5 s): a bare teal Israel outline on a dark field with "DAY 4" only. The target (the mountain in Iran) is not on screen, and the cabinet label does not appear until about 4 s (f00240). Fix: reorder so the opening frame shows the Jericho line to the mountain (start at the "One Jericho Two missile" paragraph, p of c4-jericho) or widen c4-cabinet to include Iran with TEST MOUNTAIN labelled from 0 s.
3. Opening rule: only s1 satisfies "two of three open on the strike moment or named target", and only partially. s1 f00000 to f00180 (0 to 3 s) is a dim map of Iran and Israel with a "T-00:05" clock; the flash is at 4.21 s (f00270, 4.5 s, white-out) not in the first 3 s, and "TEST MOUNTAIN (SIMULATED)" is named at 3 s. s2 and s3 start after the flash. Packager: at most one of three Shorts passes the strike-or-target-in-first-frame rule. Fix for s1: open on `open-flash` (4.21 s) or reorder so the flash shot leads; for s2 and s3 see 1 and 2. Also the engine copies no banner into the Shorts, so the "it has not happened" line is carried only by narration and subtitles.
4. Text overlap, s2 f02466 (40 s, `c4-clock`): "FLIGHT: EIGHT MINUTES" is printed under "TWO EVENTS: 11 KT TOGETHER" (both unreadable where they cross, at the left, y about 940 of 1185 in the sheet). Fix: stack the labels or drop the FLIGHT label for the last sentence (c4-clock labels, add `at` offsets or remove one).
5. Text overlap on label stacks: s1 f01860 (31 s, `open-fire`): "THE WORK UNDER THE ROCK GOES ON" runs across the QOM and KASHAN labels and dots (QOM, KASHAN partly covered). s3 f01140 and f01230 (19 and 20.5 s): "FIREBALL 0.191 KM", "SIMULATED LOCATION", "20 PSI 0.238 KM" and "5 PSI 1.167 KM" are touching or crossing at the ring centre, and f01620 "ABOUT 4.3 KM2 INSIDE THE 5 PSI RING" touches "FIREBALL" and "SIMULATED LOCATION". On a phone these are hard to read at 1.5x. Fix: widen the h-fireball and h-5psi view (CITY_ZOOM is tightening it to 0.8) or set label offsets so each ring label sits on its own side.
6. Payoff strength: s1 ends in a cliffhanger-like line ("The work under the rock has not stopped") with the map showing only a label stack, and s3 ends mid-paragraph in the 5 psi caveat, before the burns paragraph. Fix: s3 end at the burns sentence end (466.66 s shot boundary is inside the line; use the paragraph end), s1 end on "Did the weapon reach what was buried inside?" if the window can extend.
7. Still stretch: no stretch over 4 s found in s1 (map camera moves, flash at 4.2 s, globe at 9.9 s) or s2 (rings and arc arrive at 15 s); s3 is the exception (finding 1).
8. Edge safety at 1.5x: no label clipped at the frame edge; widest right-edge labels are s1 f00420 "GROUND ZERO (SIMULATED)" (about 45 px from the edge) and s1 f02004 "ISRAEL HAS NEVER CONFIRMED ITS ARSENAL" (about 120 px). Tight but inside; keep.
