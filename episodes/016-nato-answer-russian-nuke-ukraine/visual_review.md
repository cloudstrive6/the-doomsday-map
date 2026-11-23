PASS

Round 2. Basis: stills re-rendered 2026-11-23 (0.5, 1, 2.5, 4, 6, 7.5, 18, 112, 160, 296, 385, 425, 515, 518, 521.5, 523, 525, 640 s), build/validate.txt, episode.json, narration/words.json.

Gate checks
- validate.txt reads "ok": no `retention:` lines and no `pace:` lines (the earlier c5-near pace warning is gone).
- End slate: starts 659.465 s, ends 676.46 s. Last word "first." ends 666.46 s (words.json), so the slate runs 10.0 s after the last word. Music plan segment (bed_tense.mp3) runs to 676.46 s.
- Banner 1.8 to 4.8 s over moving region and city shots. f00150 (2.5 s) and f00240 (4 s): "SIMULATION · NOT REAL EVENTS" is readable and clear of the SIMULATION tag and the clock.
- Corner tags present and correct in every frame checked (SIMULATION, REAL DATA, REAL HISTORY). No clipped text and no text over a tag or clock.

Previous findings 1 to 10
1. FIXED. 525 s (f31500) and 523 s (f31380): one "NEAREST MAPPED PLACE: HLYBOKE, A VILLAGE" label, one "HLYBOKE · 4.3 KM" label clear of the ring line, and "1 PSI · 4.975 KM" in yellow. No doubled "4.3 KM", no bare dot.
2. MOSTLY FIXED. The nearest place is now named on screen. The village footprint is still faint grey roads and there is no marker dot at Hlyboke. Minor: add a dot on the 4.3 km ring at the Hlyboke label and brighten the roads (c5-near2, cities field).
3. FIXED. 518 s (f31080): "5 PSI · 1.838 KM" (red) and "1 PSI · 4.975 KM" (yellow) with the whole 1 psi ring in frame. 515 s (f30900) is the arrival frame (one ring and the heading), and the camera widens within about 3 s. The 4 s stretch has motion.
4. FIXED. 640 s (f38400): Ukraine map with the UKRAINE label, legend and "NO ROAD TO PEACE DRAWN HERE". Not near-empty.
5. FIXED. 425 s (f25500): "REAL RECORD: RUSSIAN EMBASSIES, 2026", "REPLY TO NATO STRIKES: ALL MEANS, NUCLEAR INCLUDED", Minsk, Moscow, BELARUS, source plate "Source (real record): ...". The subject is clear and the source is marked as the real record. 385 s (f23100, HOUR 36 four-options shot): Ukraine and NATO with a legend and heading, readable.
6. FIXED. 18 s (f01080): Ukraine against the Kursk border, launcher marker and labels, "T+00:04" clock.
7. FIXED. 4 s (f00240): LOKHVYTSIA, KOMYSHNIA, the burst glow, "20 KILOTON AIRBURST", white "OPEN FARMLAND, CENTRAL UKRAINE". 6 s (f00360) shows roads, the fireball and a caption; 7.5 s (f00450) shows the 0.202 km and 1.838 km rings.
8. FIXED. The "OPEN FARMLAND, CENTRAL UKRAINE" label is white on a plate at 4 s.
9. FIXED. 160 s (f09600, Washington, Sept 2022): Moscow, Ukraine and Russia are in frame with a Washington line, so it shows who is against whom. 112 s (f06720): Moscow marker added to the doctrine shot.
10. FIXED. 296 s (f17760, HOUR 00): the 500 KM scale bar is clear of the Romania border. Brussels, the FLASH marker and the dashed line show who is reporting what.

Opening 0 to 8 s: f00030 (0.5 s) and f00060 (1 s) open on the Kursk launcher, dashed line and TARGET in Ukraine with a T- clock. The flash is on screen by 2.5 s. Something new arrives every 2 to 3 s.

Remaining notes (not blocking, for the director if a pass is made)
- f00240 (4 s): the LOKHVYTSIA label is dim teal on near-black and hard to read on a phone. Brighten the label colour.
- f00360 (6 s): the "FIREBALL · 0.202 KM" label is still fading in and nearly invisible, so the frame is mostly dark roads. It is a one-frame fade and not a stretch.
- f06720 (112 s): the three stacked doctrine labels sit at different left offsets (x 130 to 165). It is readable; align them if cheap.

## Shorts review (2026-11-23), s1 s2 s3

Basis: stills of the staged vertical shot lists at 0, 1, 2.5, 5, 12, 22, 30 and 35 s of each Short (s3 to 31 s), checked against craft rules 19 to 22. Evidence frames are in /tmp/sh_s1, /tmp/sh_s2, /tmp/sh_s3 (f00000 = 0 s, f00060 = 1 s, f00150 = 2.5 s, f00300 = 5 s, f00720 = 12 s, f01320 = 22 s, f01800 = 30 s, f02100 = 35 s).

FAIL

1. s2 (476.67 to 513.9): FAIL, starts mid-sentence. p32 ("Over the staging area, the engine puts the burst in the air, with a fireball about two hundred metres in radius.") begins at 473.17 s; the window opens at 476.67 s, on the words "in the air, with a fireball". A stranger hears a fragment with no "what", and the first frame (f00000, 0 s) is a black field with one small cross and no label. Fix in shorts.json: set s2 `start` to 473.17 (start of p32; the chapter card is dropped from Shorts and c5-fire then covers the gap) and `end` stays 513.9 or moves to the end of p36 (513.81) (about 40.6 s, still near the 30 to 45 s target). Then the director must give c5-fire a `short` override so the burst and the "AIR BURST OVER THE STAGING AREA" label are on screen by 2.5 s (rule 19), because in the long cut the glow arrives about 1 s after 476.7 s. Also the first words should name the target; p32 does ("Over the staging area").
2. s2, f00000 (0 s) and f00300 (5 s): near-empty frames. At 0 s only a "+" and the title band on near-black; at 5 s (c5-20 just opened at 4.6 s) the same, only the "+" and a scale bar, with no ring or label until about 8 s. Fix: c5-20 `short` override with the 0.374 km ring and its label from the first frame, and keep the fireball glow until the ring appears; widen the camera so the ring and fireball share the frame.
3. s1 (0 to 37.97): FAIL on the payoff. It ends on the last words of p04, "What does the alliance do, and how long before it has to choose?", a question, so it is a cliffhanger (CLAUDE.md: never a cliffhanger). The last frame (f02100, 35 s) is the Europe map with "WHAT DOES THE ALLIANCE DO?" and no ending line. Fix: end at the end of p03 (23.99 s, "Two hundred and thirteen kilometres to fly.") is too short, so instead cut at the end of p02/p03 only if at least 30 s is kept, or better re-window s1 to end on p04's earlier sentence "Nobody in Kyiv or Brussels has three minutes to decide anything." and make the loop to the "ONE 20 KT NUKE" title. Packager to choose; end must be a statement, not the NATO question.
4. s1, f00300 (5 s): near-empty. The city shot open-rings (5.0 to 7.77 s) is a near-black field with one faint cross and a scale bar, after the white-out; the fireball and rings from 2.5 s are gone. Fix: open-rings `short` override to keep the 0.202 km fireball ring and a label ("20 KT AIRBURST") visible, or shorten it to 1 s.
5. s1, f00060 and f00000 (0 to 2 s): the first 2 s show the launcher in Russia, not the strike; the flash arrives at 2.0 s (f00150 at 2.5 s is a full white-out with the fireball ring), so rule 19 (strike moment in the first 3 s, target named) is met by a narrow margin: "TARGET" and "CENTRAL UKRAINE" are labelled at 0 s. Accept, but the flash does not show Ukraine or a place name at 2.5 s (grey screen with a ring). Fix: add the "CENTRAL UKRAINE" label to open-burst.
6. s3 (55.576 to 87.474): not a strike window, and f00000 (0 s) shows only the border line with no label, no launcher and no subject (the "ISKANDER-M" label arrives at about 1 s). The title promises "3 MINUTES WARNING", but the three minutes appear only in the last frame (f01800 at 30 s, "THREE MINUTES: ALL THE WARNING"). Start is fine (p06 start, makes sense to a stranger) and the end is a payoff ("three minutes is all the warning there is"). Fix: put the first label on frame 0 (c1-isk `short` override, label at t 0) and open on the launcher marker.
7. Rule 19: two of three must open on the strike moment or the named target. s1 opens on a launcher and target (passes), s2 opens on a black field (fails until fixed per 1 and 2), s3 opens on an empty border. Today only s1 qualifies. Packager and director must fix s2 and s3 openings.
8. s1, f02100 (35 s): the "FULL SIMULATION ON THE CHANNEL" pill is not in the frame, although the window ends at 37.97 s and the pill should show in the last 3 s (from 34.97 s). s2 (f02100 at 35 s) and s3 (f01800 at 30 s) show the pill, clear of the clock. Check s1's pill (it may start a frame late; re-render at 36 s).
9. Rule 21, title bands: all three are two lines, number or weapon first, target second ("ONE 20 KT NUKE / ON UKRAINE", "5 PSI AT 1.8 KM / OVER UKRAINE", "3 MINUTES WARNING / ISKANDER-M NUKE"), readable and inside the safe area, clear of the corner tag and clock. s3's second line names the weapon, not a target; fine. s2 and s3 never repeat the same rings.
10. Length (rule 20): s1 38.0 s, s2 37.2 s, s3 31.9 s, all in range. No history-list Short.

Not changed: stage.

## Shorts review round 2 (2026-11-23)

PASS

Basis: fresh vertical stills of the staged s1 (33.5 s), s2 (40.73 s) and s3 (31.9 s) at 0, 1, 2.5, 5 s, around 30 to 32 s and in the last 3 s (evidence in /tmp/r2_s1, /tmp/r2_s2, /tmp/r2_s3), checked against craft rules 19 to 22 and the numbered findings of the first Shorts review.

Gate checks
- build/validate.txt reads "ok": no `retention:` lines and no `pace:` lines.
- Long video end slate: starts 659.465 s, ends 676.46 s; the last word "first." ends 666.46 s (words.json), so the slate runs exactly 10.0 s after the last word. Unchanged.

Previous findings
1. FIXED (s2 start). s2 now starts at 473.168 (p32 start), first words "Over the staging area,". f00060 (1 s) shows the fireball and the label "AIR BURST OVER THE STAGING AREA", and "FIREBALL · 0.202 KM".
2. FIXED (s2 near-empty). f00300 (5 s): fireball glow with the ring, "AIR BURST OVER THE STAGING AREA" and "FIREBALL · 0.202 KM". Rings with labels follow ("3RD-DEGREE BURNS · 2.149 KM", "5 PSI · 1.838 KM", "1 PSI: WINDOWS · 4.975 KM"). No empty stretch.
3. FIXED (s1 payoff). s1 now ends at 33.5 s on "one question lands on every NATO table." (a statement). The last frames (33.3 s) show "AFTER THE FLASH: ONE QUESTION ON EVERY NATO TABLE" over Europe with NATO HEADQUARTERS, and it echoes the title. See note A.
4. FIXED (s1 5 s). f00300: "20 KT AIRBURST" label and "FIREBALL · 0.202 KM" ring in frame, not near-empty.
5. FIXED (s1 2.5 s). f00150: white-out with the fireball ring and the "CENTRAL UKRAINE" label.
6. FIXED (s3 frame 0). f00000: REAL DATA tag, "ISKANDER-M", "LIKELY FOR A BATTLEFIELD NUCLEAR STRIKE", "LAUNCHER (ILLUSTRATIVE)" and the source plate are all on frame 0.
7. Rule 19 MET. s1 opens on the launcher, dashed line and TARGET / CENTRAL UKRAINE (flash by 2.5 s); s2 opens on the flash and by 1 s the burst and the named target. Two of three qualify; s3 is the real-data weapon Short.
8. FIXED (s1 pill). "FULL SIMULATION ON THE CHANNEL" is in s1 at 30.5 and 33.3 s, in s2 at 37.7, 39 and 40.5 s, and in s3 at 28.9 s, clear of the SIMULATION tag and the clock.
9. HOLDS. Title bands are two lines, number or weapon first, inside the safe area; the frame-0 labels do not touch them.
10. HOLDS. Lengths 33.5, 40.7 and 31.9 s (rule 20, 30 to 45 s); no history-list Short, no repeated rings.

Notes (not blocking)
A. s1 end 33.5 s sits 0.02 s before the next word "What" (33.48 s, words.json); "table." ends 33.34 s. Set s1 `end` to 33.40 so the question's first word is not audible.
B. s2 f00000 (0 s) is a pure cream white-out with only the title band, SIMULATION tag and clock; the SIMULATION tag is low contrast on it. It is the flash and the burst is on screen by 1 s, but the feed preview frame is blank. If cheap, start the flash at about 0.3 s so frame 0 shows the fireball.
C. s2 f02430 (40.5 s): the "5 PSI · 1.838 KM" and "1 PSI: WINDOWS" labels are stacked close and sit on ring lines. Readable, inside the frame, clear of the tags.

Not changed: stage.
