PASS

Round 3 (final). validate.txt reads "ok": no `retention:` and no `pace:` lines. Read at full size (re-rendered on the current episode.json, where each long c5 shot is now split into -a/-b/-c parts of 3.4 to 6.4 s): f27000 (450 s c5-burst-a), f27300 (455 s burst-b), f27780 (463.0 s fireball-b first frame), f27960 (466 s), f28200 (470 s), f28680 (478 s 20 psi), f29100 (485 s 5 psi), f29700 (495 s burns), f30300 (505 s light), f30900 (515 s 1 psi), f31500 (525 s), f32100 (535 s water), f32520 (542 s fallout), plus contact.png of the shot first frames (453.3, 467.5, 485.2, 520.0, 532.5 s).

Round-2 findings
1. Long static c5 shots: FIXED. Shots are now 3.4 to 6.4 s with a different framing in each part (coast and burst, tight on the group, wide to the 85 km line). No shot over 8 s in c5 except the deliberate 7.7 s c5-fallout. Pace and retention checks are clean.
2. Scale caption: FIXED. "Rings drawn 6 times true size. Ships not to scale." is on every ringed frame read (f27000, f27300, f28200, f28680, f29100, f29700, f30300, f30900, f31500, f32100): bottom centre, Barlow white on a plate, clear of legend, scale bar and clock. It also covers the ship-scale point of finding 4. The fallout frame has no enlarged rings, so it needs none.
3. Label overlap and repeats: FIXED. FIREBALL label appears once (f27960, left of the group, clear of everything). No label crosses a ring or a ship in f28680, f29100, f29700, f30300, f30900, f31500. Labels sit at the frame sides, 24 px or larger, inside the frame, clear of the SIMULATION tag and clock.
4. Ship markers vs rings: ACCEPTED. Markers are now about 25 px, inside the burns ring (f29700, f30900); the caption states they are not to scale. Rings match the engine values times 6 (20 km scale bar in f29700 and f30900).
5. c5-fallout (f32520): still sparse but not empty: coast, Kuril islands, 85 km line, dot, plume and four labels. Minor: "LITTLE MATERIAL LIFTED" sits about 150 px below the dot.
6. c5-water: the "ABOUT 85 KM" line is visible (f32100, 535 s, with the caption and rings). OK.

Warnings (taste, not blockers)
- First frame of the -b/-c parts fades in. f27780 (463.0 s, c5-fireball-b, 0.09 s after the cut) shows only three dim ship chevrons, legend, clock and scale bar on a dark field, with no coast, label or caption. The frames at 485.2 s and 520.0 s start the same way (rings faint). By 466 s (f27960) the frame is complete, so this is under half a second; if cheap, start those elements at the shot start (a - 0.5) in C5 for the -b/-c parts.
- The teal "1 PSI: WINDOWS BREAK, 4 KM" label was not on screen at 515 s (f30900) or 525 s (f31500); the teal ring is unlabelled in those frames, but the legend is not needed to read it and the narration names it. If the label is timed between 519 and 524 s, no action.
- Banner (from round 2): fade-out starts at about 8.7 s while the spoken sentence runs to 12.4 s. Under the 3.5 s cap, accepted.

Checks that pass
- SIMULATION corner tag present on every frame read; nothing over the tag or clock.
- Legend (RUSSIA amber, JAPAN AND US blue) on every region frame, so who is against whom is clear.
- No empty frame outside the sub-second shot-start fade; no static card.

Verdict: PASS. No stage change was made.

## Shorts

Method: read shorts.json against narration/words.json and episode.json, then rendered stills of each short's own episode.json (video/public/episodes/020-russia-japan-kuril-hokkaido-s1, -s2, -s3) at the open, mid-window and end. No thumbnails touched, no stage change.

Overall: FAIL (s3 FAILS; s1 and s2 pass with fixes recommended). Rule 19 holds on the pair s1 + s2 (both strike windows with the target named in the title band).

### s1 "ONE NUCLEAR MISSILE / AT JAPAN'S FLEET" (0.0 to 30.1 s): PASS
- Start: p01 at 0.25 s. End: 30.1 s, 0.6 s after p04 ends (29.52 s "...to do something about it") and just before p05 (30.13 s). Length 30.1 s, inside 30 to 60.
- Hook with the flash at 5.6 s: acceptable. Frame 0.2 s (f00012) already shows the named target: HOKKAIDO coast, KALIBR chevron, ESCORT GROUP, legend (Russia amber, Japan and US blue), a red "T-00:07 UNTIL THE BURST" clock counting down, and the title band. The line "first nuclear weapon used in war since Nagasaki" runs under it, and the white-out lands at 5.7 s (f00342), so the viewer waits for something specific. Not a dim map with no subject.
- End: "The ships have twenty-seven minutes to do something about it." (f01740 shows "27 MINUTES TO ACT", radar ring, pill). It is a stakes line that leaves the question open, so it is closer to a cliffhanger than a payoff (rule 22 wants the biggest line echoing the title). The cold open is fixed, so accepted, but the packager should consider the end at 7.4 s plus aftermath if the open ever changes.
- Minor (director): clock reads T-00:00 at 4 s (f00240) but the flash is at 5.6 s, so the countdown hits zero 1.6 s early; the label stack at 4 s (27 MINUTES AFTER LAUNCH, KUNASHIR, PACIFIC OCEAN, KALIBR, ESCORT GROUP) is crowded. HOKKAIDO label is nearly invisible at frame 0 (fading in). Frame at 8 s (f00480) is a dark field with one glow on the ships; fine because the caption "This is a simulation" carries it.
- No Short banner: the flash is covered by the SIMULATION corner tag and the spoken/caption "This is a simulation" at 7.4 s. Accepted.

### s2 "ONE 10 KT NUKE / OFF HOKKAIDO" (444.44 to 478.8 s): PASS with fixes
- Start: p32 at 444.44 s. The chapter card is not in the Short: c5-burst-a runs 0 to 8.8 s from frame 0, so there is no card hold. End: 478.8 s, 0.84 s after p33 ends (477.96 s) and before p34 (479.35 s). Length 34.4 s.
- Open: f00012 (0.2 s) is the white-out of the burst with the title band, SIMULATION tag, T+27:18 clock, legend and caption "The missile detonates in the air,". Strike moment on frame 0, target named in the band. This is the strongest hook of the three.
- Rule 21: weapon number then target ("ONE 10 KT NUKE / OFF HOKKAIDO"). OK.
- FIX 1 (director, c5-burst-b first frames): f00840 (14 s, c5-fireball-a start) is near empty: dark field, coast, three ship chevrons almost invisible, no label, no ring, no caption. Same fade-in at f00540 (9 s, "CAPE NOSAPPU" label ghosted behind the island). Start labels and ships at the shot start in the Short render, or keep the glow ring on frame.
- FIX 2 (packager, end): the window ends on "Within about three hundred metres ... twenty pounds per square inch" (f02040: "20 PSI: ABOUT 300 M", two blue chevrons and a tiny ring on a dark field, pill over the coast). The biggest line, "a small bright point on a very large sea", sits at 458.8 s (about 14 s in) and is the hook line in shorts.json. A payoff, but a technical one that does not echo the title. Better: end the window at the p33 sentence about the fireball, or keep as is if the loop is acceptable.
- Pill "FULL SIMULATION ON THE CHANNEL" (f02040) sits over empty coast, clear of the labels. OK.

### s3 "4 KM FROM JAPAN / RUSSIA'S ISLANDS" (84.145 to 119.2 s): FAIL
- Start: 84.145 s is the c1-kurils shot start, 0.3 s before p09 (84.44 s), so the first 0.3 s are silent; set start to 84.44. End: 119.2 s, 0.38 s after p10 ends (118.82 s "...piece of that door.") and before p11. Length 35.06 s. Ends on a real line ("Whoever holds the islands holds a piece of that door"), a payoff, but it is a geography point, not a strike (a real-data Short; no history list, so rule 20 is not hit).
- FAIL 1, text over text: f02088 (34.8 s) the red "FULL SIMULATION ON THE CHANNEL" pill is printed over the labels "SOYA STRAIT" (reads "SOYA S...") and "RUSSIAN MISSILE SUBMARINES" (reads "...ARINES"), both cut by the pill. Fix: in the Short render, hold the c1-okhotsk labels clear of y 540 to 600 in the last 3 s (move SOYA STRAIT and RUSSIAN MISSILE SUBMARINES, or drop them from the final shot), or set the pill row away from the label stack.
- FAIL 2, source line against caption: f00300 (5 s) and f00720 (12 s): the plated source line "Wikipedia, Kuril Islands dispute; Japanese government" sits directly under the subtitle plate and touches it; in f00300 it is a two-line block over the Honshu coast. The same happens with "FAS; Lowy Interpreter" at 20 s and 34.8 s. Fix: move the source line to the bottom above the legend, or hide it in Shorts. Also, "Wikipedia" is a weak source to print on screen next to a fact claim (research.md A11 should carry two reputable sources; show those).
- Hook (rule 19 for a non-strike Short): f00012 (0.2 s) is a wide, dim map with the title band, a REAL DATA tag and the Kuril chain, but no marker, no label and no "4 km" shown; the first subject label (NEAREST ISLET, NOTSUKE PENINSULA, dashed line) only appears by 5 s. This is close to the "dim map with no subject" failure. Fix (director/packager): open the Short on the c1-izmena framing (50 km, 6.1 s into the shot) with NEAREST ISLET and the dashed 4 km line on frame 0, or start the c1-kurils shot already zoomed to the Notsuke strait.
- f01680 (28 s) is readable: SEA OF OKHOTSK, RUSSIAN MISSILE SUBMARINES, SOYA STRAIT, KURIL STRAITS, TSUGARU STRAIT, all inside the frame and clear of the tag.

### Summary for the packager and director
1. s3: fix the pill-over-labels overlap (blocking), the source line touching the subtitle, and open on the 4 km subject.
2. s2: remove the near-empty frame at 14 s; consider a stronger last line.
3. s1: pass; the clock reaches zero 1.6 s before the flash.
