PASS

Round 3 (final). I re-rendered stills at 5 s, 231 s, 376 s, 384 s, 411 s and 414 s and read each. validate.txt reads "ok": no `retention:` lines and no `pace:` lines. The four silo-field items from round 2 are fixed.

Round 2 item 1, checked in frames
 - c4-fields (f22560, 376 s): Minot, Malmstrom and F.E. Warren each show a silo cluster of about 20 blue dots around a square, with labels. Billings and Rapid City are labelled. State borders are drawn and the horizon arc is gone. Pass.
 - c4-60 (f23040, 384 s): three silo clusters on a state-border map, Billings and Rapid City labelled, the caption "The silo fields come early" at the bottom, clear of the tag and clock. The clusters carry no labels of their own (warning, not a blocker). Pass.
 - c4-empty (f24660, 411 s): 20 silo rings, two shown as small blue dots (launched), and a red dot with the label "MINOT MINUTEMAN FIELD" at full opacity. Clock tag reads "SILO FIELD". No horizon arc. Pass.
 - c4-stilland (f24840, 414 s): the label "MINOT: THEY STILL LAND" is now white on a dark plate and readable, with the ring and fireball glow clear of the corner tag. The label's left end touches the ring stroke and the state line (warning). Pass.
Round 2 item 3 (plain slate) is also fixed: state borders are now drawn.

Spot check
 - f00300 (5 s): banner "SIMULATION · NOT REAL EVENTS" over the moving Bangor fireball, caption "SIMULATION: IT HAS NOT HAPPENED", the labelled target NAVAL BASE KITSAP, BANGOR, SIMULATION tag and clock clear. The KINGSTON label sits just under the clock plate without touching it. Pass.
 - f13860 (231 s): Ramstein 50 km view, dashed blast circle, RAMSTEIN AIR BASE and RAMSTEIN AREA in red, with Luxembourg, Frankfurt, Stuttgart and Strasbourg as context. Pass.
 - Rounds 1 and 2 items (ring labels, end slate 10.0 s after the last word, number cards under limit) were not changed since round 2 and still stand.

Warnings for the record
 1. c4-60 silo clusters have no labels of their own (f23040).
 2. c4-stilland label touches the ring (f24840): move it a little right or down if the director reopens the shot.
 3. The spoken disclaimer lands at 12.08 s; the banner and caption carry it from 3.7 s (accepted in round 2).


---

Shorts review (windows in shorts.json, 2026-11-15)

FAIL

I built the vertical shot lists from shorts.json (not staged by the pipeline yet) and rendered 1080x1920 stills of each Short at the first frame and 5 to 7 later points, then read them. Frames: s1 at 0.05, 1, 2.5, 4.5, 15 and 29.5 s; s2 at 0.05, 2, 6, 12, 14.8, 16.2, 22 and 34 s; s3 at 0.05, 2, 8, 12, 18, 22 and 30 s.

Rule check
 - Length: s1 30.6 s, s2 35.5 s, s3 31.7 s. All inside 30 to 60 s; all three are at the low end of craft's 30 to 45. Pass.
 - Start on a paragraph: s1 0.0 (p01), s2 328.783 (p23), s3 430.289 (p28). Pass.
 - Plates and captions: the caption plate sits at about 68% of the height in all three (y about 1280 to 1360 of 1920), clear of YouTube's bottom overlay. Title band, SIMULATION tag and clock are clear of each other. Pass.
 - Same rings across Shorts: s1 uses the Bangor fireball and ring, s2 the Washington ring and Pentagon ring plus the Kings Bay ring, s3 only point marks and the yellow "8 each" ring. No ring repeats. Pass.
 - Two of three open on the strike or the named target: NOT MET. See items 1 and 2.

Findings

1. s2 (start 328.783, c4-m16a), first frame f00003: a dark globe over the Arctic, no marker, no label, caption "Minute 16." Frame at 2 s: one pale "US SUBMARINE (LOCATION SIMULATED)" label over Greenland. No strike and no named target for the first 11 s; the Washington flash is at 343.6 s (14.8 s in). This is the "dim map with no subject" FAIL. Fix for the packager: start s2 at 340.583 (p24, "Washington", c4-m17a). The Washington region shot c4-dc begins at 343.0, so the flash is 2.4 s in, and Kings Bay follows. That window alone is 23.7 s (to 364.25), so extend the end to 373.9 s (the end of "...arrive after about thirty minutes in flight."): 340.583 to 373.9 is 33.3 s, ends inside c4-30min (368.6 to 374.6), and adds the Severomorsk, Vilyuchinsk and Plesetsk strikes as the payoff run. Check that the first 2.4 s (c4-m17a, Atlantic arc with "Warheads inbound") is not a dim empty globe: ask the director to label the arc "Russian submarine missiles, minute 17" or name WASHINGTON on the arc at 340.6 s (shot c4-m17a, marks) so the target is named from frame 0.

2. s3 (start 430.289, c4-m40), first frame f00003 and f00120 (2 s): a dark globe with a faint "LAST SUBMARINES" label that is almost illegible; nothing is hit until "York" at 437.8 s (7.5 s in; New York flash first appears at about 6.9 s in f00480). The first frame is a dim map with no subject. Fix: either (a) start s3 at 415.189 (p27, the Russian missile fields, Kozelsk flash at 421.6, 6.4 s in) and end 461.96: 46.8 s, three strike runs and the payoff, but still not a strike at frame 0; or (b) keep 430.289 to 461.96 and have the director raise the label contrast in c4-m40 (text "LAST SUBMARINES", marks at W("p28","submarines")) and open that shot with the four arcs already running toward NEW YORK, LOS ANGELES, SAINT PETERSBURG and MOSCOW, with the target names from 0 s. With s1 and the fixed s2 that gives two of three; s3 may stay the "scale" Short if it is not a strike open.

3. s1 (0.0 to 30.6) ends on a question: the last frame f01770 (29.5 s) carries the caption "this in under an hour?" with the cold-open line "How does one missile become this in under an hour?" That is a cliffhanger, not a payoff, which breaks the "ending on a payoff" rule. The payoff sentence of the cold open is "By minute fifty-three, it is over." at 25.0 s (end of p03), but that window is 25.0 s, under the 30 s minimum. Packager decision: either end at 25.0 and add 5 s on the front by nothing (not possible, start is 0), so instead change s1 to 0.0 to 30.52 only if the showrunner accepts a looping question ending; otherwise replace s1 with 312.389 to 340.03 (p22 and p23: the Cape Cod, Bangor and Beale strikes at about 323.9 s are 11.5 s in, so this fails the opening rule). Recommended: keep 0.0 to 30.52 and record the question end as an accepted exception, because the video loops straight back to "Minute sixteen, Washington State" and the first Short is the only one that opens on the named target (BANGOR, WASHINGTON appears by 2.5 s) with the flash at 3.7 s.

4. s1, f01770 (29.5 s): the red "FULL SIMULATION ON THE CHANNEL" pill (y 487 to 537) overlaps the bottom edge of the clock plate and cuts the lower part of "T+53:00" (the clock digits end at y 490). Also a stray "BANGOR" label stays at the left edge (x 55 to 220, y 575) with no ring or fireball next to it on the globe, so it reads as an orphan label. Same pill near the clock in s2 f02040 ("T+26:29" touches the pill's right end) and s3 f01800 (pill sits right under the SIMULATION tag). Fix for the engine or director: move the pill below the clock plate (y 540 or lower) or to the lower third above the caption, at about y 1180, so it never touches the clock; and drop the Bangor mark from the last 3 s of p04-pull (shot p04-pull, marks) or place it on the target.

5. s1, 0.05 s (f00003): the first frame is a dim globe with a plain amber line and the clock, with no label. Warning, not a blocker: the flash is at 3.7 s (open-flash). Fix for the director if the cold open is reopened: name BANGOR in open-run (0 to 3.7 s) from the first frame.

6. s3, 22 s (f01320) number card: the large number reads "325 WARHEADS" mid count-up while the subtitle says "375 warheads" (the card counts up to 375 over the shot, shot c4-375 countTo). The frame is not a wrong number in the finished video, but over 3.1 s on a near-empty card (bottom 60% of the frame is blank) it can read as a mismatch. Warning: start the count-up higher or settle it by 1.2 s, and move the stacked text lower toward the middle.

7. s2, f00720 (12 s): the Washington white-out flash fills the whole frame (cream frame with only ghosted tag, clock and caption). This is the deliberate flash (flash v2), under 0.5 s; no finding, but the caption "Washington and the Pentagon." is nearly invisible during it.

Next step for the packager: edit shorts.json s2 to start 340.583 and end 373.9, decide s3 (415.189 to 461.96, or 430.289 with a director fix to c4-m40), set the s1 exception, and send items 4, 5 and 6 to the director. Then re-run `python -m studio shotlist 008-full-nuclear-war-minute-by-minute` and have me re-check the new first frames.


---

Shorts re-check (2026-11-15, after the showrunner's changes)

PASS (with warnings)

I restaged the Shorts (`python -m studio shotlist`; s2 starts 340.584 and s3 starts 415.185 after the shot-boundary snap) and rendered 1080x1920 stills: s1 at 0.05, 1, 2.5, 4.5, 15 and 29.5 s; s2 at 0.05, 1.5, 2.5, 3.2, 6, 12, 20, 30 and 33 s; s3 at 0.05, 2, 6, 10, 16, 24, 32, 36 and 45 s. `validate.txt` has no `retention:` lines.

Rule check
 - Lengths: s1 30.6 s, s2 33.3 s, s3 46.8 s. Pass.
 - Strike-open (two of three needed): met by s1 and s2.
   * s1 f00003: amber missile line over the Pacific toward Washington State, BANGOR named by 1 to 2.5 s, flash at 3.7 s. Meets.
   * s2 f00003 (title "SIX WARHEADS / ON WASHINGTON"): arc running into the Washington DC dot on the US east coast, clock "MINUTE SEVENTEEN", caption "Minute 17.", and the Washington ring and fireball are on screen at 3.2 s (f00192, "Washington and the Pentagon."). Meets. Warning: f00150 (2.5 s) is the 100 km Chesapeake outline with no marker, label or ring for about 1 s before the flash; the target is named only by the title band.
   * s3 f00003: four blue arcs landing on Russian cities, clock "MINUTES THIRTY-NINE TO FORTY-THREE", but no city label and the arcs cross the clock plate. Strike moment, not a named target. Counts as a partial; the first two carry the rule.
 - Plates: caption plate at y 1280 to 1360 in all three, title band, SIMULATION tag and clock clear of each other, labels inside the frame (BANGOR, WASHINGTON; BEALE RADAR; KINGS BAY, GEORGIA). Pass.
 - Pill ("FULL SIMULATION ON THE CHANNEL"): present in the last 3 s of all three (s1 f01770, s2 f01980, s3 f02700). It touches the clock plate (cuts the bottom of the T+ digits in s1 and s2 and sits against the clock in s3). Engine matter (Episode.tsx ShortTitle), accepted as a warning for 008 as instructed.
 - Endings: s1 ends on the question "this in under an hour?" (accepted exception, loops to "Minute sixteen"); s2 ends on "about 30 minutes in flight." over the arc fan; s3 ends on "That is the whole" (of our hour) over a globe.

Fixes made
 - s1 orphan BANGOR label: fixed. shotlist.py shot p04-pull, marks for Bangor and Beale now have no label; f01770 shows no stray text at the left edge (the globe is on Europe and the two marks are off the frame).
 - c4-375 count-up: not fixed. `card` has no count-duration field (countTo animates over the whole shot, scene.ts line 86), so a shotlist.py edit cannot settle it by 1.2 s. Warning only; the subtitle says 375 while the card is mid-count at about 22 s of the old window. In the new s3 window the number card is not in the sampled frames (24 s shows the globe with "27 strikes" markers), so the mismatch risk is lower; check once in the final render.

Warnings for the packager/director (none blocks)
 1. s3 f00960 (16 s, shot c4-m40): a bare globe with no marker or label, caption "Minute 40.", for roughly 4 s. Near-empty frame; fix if the director reopens it: put the four NEW YORK, LOS ANGELES, SAINT PETERSBURG, MOSCOW marks on W("p28","submarines").
 2. s3 f01440 (24 s): the NEW YORK and LOS ANGELES labels sit at the far left limb of the globe, the markers half cut off at x 0 to 50. Readable and inside the frame but weak; fix with a camera key that turns the globe toward North America for that shot.
 3. s3 f00003: the clock plate lies over the arcs; label the target cities from 0 s if reopened.
 4. s2 f00150: add a Washington, DC ring or mark in c4-dc before the flash (t 0 to 3 s of the shot).
