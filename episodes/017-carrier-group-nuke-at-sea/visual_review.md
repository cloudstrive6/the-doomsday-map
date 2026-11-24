PASS

Round 3. Checked: build/validate.txt ("ok", no `retention:` or `pace:` lines), re-run shotlist (127 shots, 660.32 s), fresh stills at 254, 258, 261, 264, 303 and 396 s.

1. FIXED (was round 2 finding 2). f15660.png (261 s) and f15840.png (264 s), c3-fiction: the frame now shows the red SUBMARINE marker, the dashed red missile track with the arrow and MISSILE label, and the blue US CARRIER GROUP with three concentric rings, plus the yellow "THE WEAPON IS FICTIONAL" label, a white "NO PUBLISHED YIELD FOR ANY MODERN ANTI-SHIP MISSILE" label and the caption. Who is against whom is clear. All labels are inside the frame and clear of the SIMULATION tag and the caption.
2. c3-dist, f15480.png (258 s): SUBMARINE at left, missile arrow mid-track, US CARRIER GROUP marker and label at right, 50 KM scale. Clear.
3. c3-sub, f15240.png (254 s): red SUBMARINE and MISSILE labels, "ATTACKER'S SUBMARINE" and caption readable, the carrier group is only the large range rings. This is the first 2 s of the shot and the next shot shows the group, so this is a warning only: add a "US CARRIER GROUP" label on the ring if the shot is ever lengthened.
4. c3-icons, f18180.png (303 s): large hexagon with five ship chevrons, "DESTROYER, ICON" label, legend and caption all separate, no overlap.
5. c4-flash, f23760.png (396 s): fireball with ship icons around it, legend bottom-left, clock top-right, no overlap. The caption "FOR A MOMENT THE SEA IS BRIGHTER THAN DAY" is still grey-pink and low contrast on the glow. Warning only: make it white.

The end slate is half-empty by design and compliant. Verdict: PASS.


---

## Shorts and thumbnails review (2026-11-24)

FAIL

Checked: shorts.json, Short frames rendered with video/scripts/stills.mjs from `video/public/episodes/017-...-s1/s2/s3/episode.json` (0, 2, 5, 16, 40 s for s1; 0, 3, 10, 25, 44 s for s2; 0, 4, 12, 25, 35 s for s3), and build/thumb_a.png, thumb_b.png, thumb_c.png. All Short labels are inside the frame, clear of the title band, the corner tag and the clock; the "FULL SIMULATION ON THE CHANNEL" pill appears in the last 3 s of each.

1. s3 (start 54.064, end 89.9), "5,000 PEOPLE ON ONE SHIP": FAIL. Frames at 0 s, 4 s, 12 s are a ship outline, "ABOUT 82,202 TONS, FULLY LOADED" and "ABOUT 5,000 PEOPLE ABOARD", all tagged REAL DATA. There is no strike, no burst and no simulation anywhere in the 36 s, and the last shot (c1-miles, 33.4 to 35.8 s) ends on "spread over many miles of sea" over a dim ring. This is a specification list that ends on a description, not a payoff. Fix: drop s3 and replace it with a window from the simulation chapters (for example the c4 burst and the aftermath for the group, ending on the closing line of the episode), or move its start to the burst and end on a result.
2. s1 (0.0 to 42.4), "ONE 10 KT NUKE BESIDE A US CARRIER": PASS on the open, FAIL on the end. It opens on the carrier group (f00000, "US CARRIER GROUP" label, icons, 00:30 clock) and the burst glow is on screen at 5 s (T+20:07), so the strike is early. It ends in shot run-who (35.45 to 42.4 s) with the caption "when nobody knows who fired?" and the narration "what does a carrier group do when nobody knows who fired?". That is a cliffhanger; CLAUDE.md requires the end on a payoff. Fix: end at about 35 s (before run-question) and cut after the 12-minute warning is paid off, or end on a result sentence. Also the first 12 s hold only a dark map with a hexagon of icons; swap the first frame to the burst (start the Short on "bursts", then the flashback) so the first frame shows the strike.
3. s2 (399.062 to 444.3), "ONE 10 KT NUKE AT SEA": the first frame (f00000, c5-fire) is a near-empty dark field with one blue arrow and a "THE BURST T+20:06" clock; the fireball only appears about 3 s in (f00180 shows a grey disc, "FIREBALL: 300 M ACROSS"). Fix: start 3 s later (at the fireball) or give c5-fire a burst shot/glow at frame 0 and widen the view. The ending (c5-1psi, "reaches 3.95 km", full ring stack) is an acceptable payoff but is a ring-by-ring list; keep it, and make the last line a result ("a ship inside the 5 psi ring is gone"), if the script supports it. Also the destroyed shot caption "DESTROYED: OUR ASSUMPTION" is yellow on near-black and readable; no change.
4. Opening rule: 1 of 3 Shorts opens on the strike or named target (s1). s2 opens on a lone arrow, s3 on a ship spec. Needs at least two of three; the fixes above for s2 and s3 satisfy it. No Short is a history list after the s3 replacement, but s3 as built is one (REAL DATA only). For the packager.
5. thumb_a.png (3 x 1280x720, read at full size): "WHO FIRED? NOBODY KNOWS", five words, a missile over a sunset sea. Readable, but no number and no scale, and the promise ("who fired") is not answered by the video (the script says the attacker is fictional). Warning: retitle the headline to something the video keeps, for example "1 NUKE AT SEA" over the missile.
6. thumb_b.png: "5,000 ABOARD 1 FLASH", number first, four words, a mushroom cloud over a carrier on a vivid sunset. Readable at 168x94, strong. This is the recommended primary. Warning: the cloud sits on the ship, which is a larger visual than a 10 kt burst "beside" the group; acceptable.
7. thumb_c.png: "1 BURST ESCORT GONE", four words, number first, a burst on the horizon with a sailor in the foreground. Readable and clear. Note "ESCORT GONE" must be supported by the engine (c5 rings); check the script says the escort inside the ring is destroyed and not "gone" for the whole group.

Verdict: FAIL for the packager. Rework shorts.json: replace s3, move s1 end before the question, start s2 at the fireball, then re-render the Short stills and re-review. Thumbnails: PASS (b recommended; a warning).


---

## Shorts round 2 (2026-11-24)

FAIL

Checked: reworked shorts.json (s1 0 to 32.4 s, s2 393.58 to 436.0, s3 444.304 to 481.4). Stills rendered with video/scripts/stills.mjs at 0 s, 1 s, end minus 3.5 s and end minus 0.4 s for each Short.

1. s3 last frame (f02202, c5-miss, 36.7 s): the red "FULL SIMULATION ON THE CHANNEL" pill is printed on top of the white label "NO CREW CAN COUNT ON THE AIM" (both at y of about 565, the label is half hidden). Also "1 PSI" is stacked twice at top right and the caption "it is aimed." touches the "Effects: Glasstone and Dolan scaling" note. Text over text is a FAIL. Fix: in the s3 shot c5-miss, move or drop the "NO CREW CAN COUNT ON THE AIM" label (put it lower, below CARRIER, or end the label before the pill appears at end minus 3 s), drop the duplicate 1 PSI label, and hide the "Effects:" note in Shorts.
2. s3 first frame (f00000, c5-ships): the "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP" note is printed over the first legend row ("FIREBALL 300 M ACROSS" is unreadable under it). It is also a near-empty dark field with a dashed hexagon and one red dot, no label naming the carrier or the burst. Fix: drop the Effects note on c5-ships, label the hexagon "US CARRIER GROUP" and the dot "BURST", or start the Short a few seconds later on the ring stack.
3. s2 first frame (f00000, c4-flash): near-empty, a dark field with one blue arrow and a legend; the burst glow is full by 1 s (f00060, orange fireball over the escort, clear). Warning, not blocking: start the shot with the flash already building, or trim the first 0.5 s. The last frame (f02520, c5-burns, 42.0 s) is clean: 20 PSI, 5 PSI and burn rings with "THIRD-DEGREE BURNS: 1.62 KM ON BARE SKIN", pill clear of every label. Payoff: a result, PASS.
4. s1 first frame (f00000): "US CARRIER GROUP" and "CARRIER" labels, hexagon of icons, three rings, clock 00:30. The target is named and the frame is not empty, PASS. Last frame (f01920, run-warning, 32.0 s): red MISSILE track toward the US CARRIER GROUP, T-04:23, caption "the warning there is.", pill clear of labels. It closes the hook sentence ("twelve minutes is all the warning there is"), so it is an acceptable payoff, but weak: the burst itself is not shown. Warning only.
5. Opening rule: s1 opens on the named target and s2 reaches the strike in 1 s; two of three, so the rule is met once s3 is fixed or not counted.

Verdict: FAIL. Blocking: s3 text collisions (findings 1 and 2). s1 and s2 pass. After the label fix in c5-miss and c5-ships, re-render only the s3 first and last frames.
