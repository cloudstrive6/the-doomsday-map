PASS

Round 2. Checked build/validate.txt ("ok": no `retention:` or `pace:` lines), contact.png (119 frames) and the stills f00060, f00300, f00540, f01032, f01500, f05100, f13128, f30768, f34914, f36000, f37572. Round-1 fixes confirmed on the frames that replaced the old worst ones.

Round-1 items:
1. Label stack over the carrier: fixed. f36000 shows one yellow label ("AIR WING: NOWHERE SAFE TO LAND?") above the ships, "CARRIER" beside its icon, none overlapping, with a legend (US GROUP, DAMAGED ESCORTS, AIRCRAFT) and trails on the aircraft.
2. Unlabelled ships and no legend: fixed. f36000, f37572 and f01500 carry legends that name the colours (blue US group, grey damaged escorts, white aircraft).
3. Floating disclaimer labels: fixed. f37572 shows two labels, "CARRIER" at its icon and "NO NAME TO ANSWER". f01032 shows only "SUBMARINE (SIMULATED)" and "STRIKE GROUP" at the target; they touch but both read.
4. Near-empty aircraft frame: improved. f36000 has trails, a dashed zone and a legend.
5. Plain dark ocean: now carries range rings (f37572, f30768, f00540).
6. Fireball ring: f30768 legend lists the fireball and 20 PSI radii.
7. Attribution: f30768 the "Effects: ..." line and the scale bar still touch at the bottom edge. Minor, legible, not blocking.

Retention and banner: f00060 (cold open on a globe, SIMULATION tag, T+19:20 clock, labels JAPAN, IWO JIMA, SUBMARINE (SIMULATED)), f00300 (banner "SIMULATION · NOT REAL EVENTS" over the moving flash, clear of tag and clock, caption "Simulation: it has not happened."). No static disclaimer card. Corner tags present and right: REAL DATA on f05100, REAL HISTORY on f13128, SIMULATION on map shots. Chapter cards (THE TRIGGER, MINUTE BY MINUTE, THE DAY AFTER) and the end slate keep their layout.

Non-blocking notes for the director if there is another pass:
- f05100 (REAL DATA, Nimitz class): a dark field with one icon and two labels. Sparse but legible and the subject is visible.
- f01500 (T-02:01): the group sits in the right third with the left half empty. Legible. Recentre the camera if time allows.
- f34914 (Able, 1 July 1946): dark field, WIGWAM marker and a very dim SHIELDED SHIP icon; label readable.
- f13128 and similar: "OUR SIZE: THE SAME" on the globe is readable, no overlap.

No P0 found. Stage advanced to visual_approved.

## Shorts

FAIL

Checked `shorts.json` (unedited) against `narration/words.json` and `episode.json`. Staged the three Shorts with `studio.shorts.stage` and rendered 1080x1920 stills: s1 at 0, 1, 2.5, 4.5, 9, 20, 33, 40 s; s2 at 0, 1.5, 3, 8, 18, 28, 31 s; s3 at 0, 1.5, 3, 8, 16, 25, 33, 38 s. Staging snaps s2 start to 325.681 and s3 start to 388.705 (shot boundaries); that is harmless.

What passes:
- Start on a paragraph: s1 0.0 (p01 starts 0.256), s2 325.7 (p28 "The first thing aboard the carrier is light"), s3 388.7 (p33 "At two hundred ninety-seven meters").
- Length 41.8 s, 31.9 s, 38.8 s: inside 30 to 60 s and the craft 30 to 45 s.
- Title band two lines on all three ("ONE 10 KT NUKE / BESIDE A CARRIER GROUP", "ONE 10 KT NUKE / AT SEA", "10 KT RINGS / ON A CARRIER GROUP"), centred, clear of the SIMULATION tag and clock, subtitles at y about 1320 (above the YouTube overlay). SIMULATION tag present in every frame read.
- No history-list Short. Legends name the sides (US GROUP, DAMAGED ESCORTS, AIRCRAFT).
- s1 carries the spoken "This is a simulation" (f00540, 9 s).

Findings:
1. FAIL, opening rule (no Short has the strike or a named target in the first 3 s).
   - s1 f00000 (0 s) and f00060 (1 s): a night globe of Japan and the Pacific, no ship, no target, no flash. The flash (`open-flash`, 3.87 s on the episode timeline, 3.6 s into the Short) is white-out at f00270 (4.5 s), after the 3 s mark.
   - s2 f00000 (0 s), f00090 (1.5 s), f00180 (3 s): a near-black field with one grey and one blue arrow and a "CARRIER" label, then "FIRST: LIGHT". The `m-l` burst is set at t 4.59 s in the shot, so the flash it describes arrives at about 4.6 s; by 8 s (f00480) the field is only a dim brown glow with "THE SEA ITSELF GLOWS".
   - s3 f00000 (0 s), f00090 (1.5 s), f00180 (3 s): a dark field with one grey arrow and no ring at all; only the legend and "THE BURST T+20:06". The 20 psi ring first appears by 8 s (f00480). Near-empty for more than 3 s.
   Fixes: (a) s2: director sets `m-l` burst `t` to about 0.1 so the white-out is on the first frame (no window change). (b) s1: window change below. (c) s3: window change below, so the first frame already carries the rings.
2. FAIL, s1 ends on a question. 41.8 s is the end of p04 ("The question is what one small bomb does to a ship that big, and how far the damage reaches"); f02400 (40 s) shows a dark field with a dashed 1 psi circle, label "WHAT DOES ONE SMALL BOMB DO TO A SHIP THAT BIG?" and a "T-00:00" clock. It is a cliffhanger and the first frames are a dim globe. Fix: replace s1 with `start` 299.1 (p26 "Minute twenty point one. The warhead detonates...") and `end` 337.5 (end of p28, "...it travels slower than light"). Shot `m-k` starts at 301.85 with `burst` t 0.1, so the flash lands 2.85 s into the Short; the payoff is the blast wave line. Length 38.4 s. The cold-open "it has not happened" sentence then lives only in the subtitles and the SIMULATION tag; acceptable, but add the word "simulation" to the hook in `yt_title` (already there).
3. FAIL, s2 would then repeat p28. If s1 becomes 299.1 to 337.5, s2 (325.7 to 357.6) shares 12 s with it. Fix: s2 `start` 338.6 (p29 "In the first seconds, the group goes to general quarters"), `end` 368.7 (after p30 "...We assume it is."; 30.1 s, add no more because p31 is a question). It is not a strike open: the first frame is the carrier with trails, so also ask the director for a flash echo or an aircraft trail in the first second of `a-d`. If that cannot be done, drop s2 and use the cold open (item 6).
4. s3 is a compromise window and ends on a method line. 427.5 is the end of p35 ("The rings are drawn exactly as the engine computes them"), f02280 (38 s) shows rings and "as the engine computes them." Not a payoff. Fix: `start` 404.7 (p34 "The burn ring...", shot `r-d`, which opens with fireball, 20 psi, 5 psi and burn rings already drawn), `end` 446.6 (end of p36, the carrier "between one and five pounds per square inch, outside the burn ring"). 41.9 s, the first frame has rings and "Exposed skin: 1.6 km" at once, and the payoff is where the carrier sits. Check labels at 1.5x in `r-d` and `r-e` (no overlap at the ring centre: f02280 stacked FIREBALL, 20 PSI, 5 PSI, BURNS, 1 PSI with 5 PSI and BURNS touching).
5. FAIL, text over the clock. In the last 3 s the "FULL SIMULATION ON THE CHANNEL" pill (y about 485 to 537) is printed over the clock digits: s1 f02400 ("T-00:00" cut), s2 f01860 ("T+20:12" cut, and the "10 KM" scale chip sits just under it), s3 f02280 ("T+20:06" cut). The corner clock reads half-hidden. This is engine layout, not shorts.json: send to the engine owner to move the pill below y 560 (or hide the clock while the pill shows).
6. Same rings: s1 (old) closes on the 1 psi ring and s3 draws 20, 5, burns and 1 psi; with the new plan s1 shows the 5 psi ring and s3 the full set. Different enough, but both repeat the 5 psi ring. Acceptable; do not add a fourth ring Short.
7. Small: s2 f01860 shows both a boxed "10 KM" chip and the bottom scale bar reading "10 KM" (duplicate), and the CRS attribution line is very faint. Not blocking.

Summary for the packager: the answer to "two of three open on the strike or target" is currently zero of three (s1 flash at 3.6 s, s2 flash at 4.6 s, s3 no ring). With the plan (s1 299.1 to 337.5, s2 338.6 to 368.7 or the cold-open window, s3 404.7 to 446.6, plus `m-l` burst t about 0.1) at most two pass; s2 is the weak one. Re-run after the director fixes and recheck frames 0, 1.5 and 3 s of each.
