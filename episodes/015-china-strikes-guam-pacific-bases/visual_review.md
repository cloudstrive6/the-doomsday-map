FAIL

Round 2, reviewed 2026-11-22. Rendered stills 0 s, 3.5 s, 5.5 s, 7 s, 580 s, 597 s, 600 s. validate.txt is still `ok` (no retention or pace lines). Round 1 text is kept below.

Round 1 findings, by number:
1. FIXED. f34800: labels now read "5 PSI · 1.459 KM" (red, plated, inside the frame, left of the ring) and "1 PSI · 3.949 KM".
2. FIXED. f36000 (c5-pacific): China coast, Taiwan, Okinawa, Japan, Philippines and Guam all show, with a dashed red launch-to-Guam line, GUAM marker and label, plated labels inside the frame. Who is against whom is clear.
3. FIXED. f00210 (open-burst): island fills the frame, "10 KILOTON AIRBURST" (yellow) and "ANDERSEN AIR FORCE BASE" (white) sit right beside the flash, banner readable and clear of the tag and clock.
4. NOT FIXED, BLOCKING. f00000 (open-run) is still a dim map: China coast, Taiwan, Philippines, no Guam, no marker, no label, no line. Cause found in the engine, so the fix is exact:
   a. Markers and labels are drawn at full opacity on frame 0 when `t` is omitted (RegionMap.tsx: `m.t === undefined ? 1 : ...`). They fade in over 0.4 s only when `t` is set. shotlist.py passes `city(AND, "GUAM", 0.0, ...)` and `city(L_N, ..., 0.0, ...)`, and `LB(..., 0.0, ...)`, so `t=0.0` triggers the fade (frame 0 alpha 0). Fix: for open-run, build those two cities and the label without a `t` key (delete the field rather than passing 0.0). The line has `t0=0.0` and the ship `t=0`; lines draw from k=0 by design, which is fine (it is the launch animation), but the target must be visible.
   b. Guam is also outside the frame at frame 0. Camera start is [132.0, 20.0] at 4300 km; Guam (about 144.8 E, 13.6 N) is off the right/bottom edge until the camera moves. c5-pacific shows both China and Guam with centre [133.0, 23.0] at 4200 km. Fix: open-run `s` camera to about [134.0, 21.0] at 4800 km (e to [137.0, 17.5] at 3100 km can stay) so the launch point at left and GUAM at right are both in frame from frame 0, with the DF-26 line showing the direction.
   After the change, re-render frame 0 and confirm: GUAM marker and label visible, launch marker visible, nothing within 130 px of the SIMULATION tag or the clock.

Judgement on frame 0: the engine's "finished frame 0" claim applies to dips and shot cuts, not to markers that the shotlist itself delays. A bare map with no subject as the first frame of the video is a blocker (it is the thumbnail-like first impression and the retention opener), and a fix exists, so this is not waived.

Non-blocking, unchanged: f00330 and f00420 label contrast (items 5 and 6) were not re-judged beyond the 5.5 s and 7 s stills; both are readable. Item 8 (repeated Andersen runway shots) is covered by validate.txt `ok`.

Not staged: visual_approved is not recorded because of finding 4. Send to the director for a one-shot fix and a round 3 check of f00000 only.

--- Round 1 (kept for reference) ---

Round 1, reviewed 2026-11-22. Frames: the 18 stills the director supplied plus 10 I rendered (0 s, 3.5 s, 26 s, 42 s, 110 s, 165 s, 230 s, 380 s, 500 s, 600 s, 720 s; the director's contact.png was overwritten by this set, the originals are in /tmp/bk/stills). I did not check the 127 shots one by one. No Shorts exist yet (no shorts.json), so Shorts checks are not applicable.

validate.txt: `ok`. There are no `retention:` lines and no `pace:` lines. The end slate is correct: last word "submarines." ends 718.88 s and the slate ends 728.88 s, which is exactly 10 s. Music runs to 728.88 s. The 720 s frame (f43200) shows the slate's half-empty layout with "ONE WARHEAD OVER LONDON" and a faint "NEXT SCENARIO" box, as intended.

Findings (blocking):

1. f34800 (about 580 s, 1 PSI "49 square km / 9% of the island" frame): the red ring label reads only "· 1.459 KM". The "5 PSI" prefix is missing, so the label is cut off or not rendered. It also sits off the ring at left. Every other 5 PSI label reads "5 PSI · 1.459 KM" (f32700). Fix in shotlist.py: find the label for the 5 psi ring in the 49-km2 shot (shot near c5-*, text field), make the text a full "5 PSI · 1.459 KM", and check the same shot on a still for clipping or fade-in.

2. f36000 (600 s, shot c5-pacific, about 597 s): a near-empty frame. It shows a dark blue ocean with one red marker "ANDERSEN: 4 KM" and a blue square "KADENA", with Taiwan and the Philippines faint at the edges. There is no China, no Guam outline and no ring, so it does not show who is against whom, and the marker is tiny. Fix: set `camera` or `widthKm` on c5-pacific to about 3,500 km so Guam, Okinawa and the China coast all show, with the Guam label and the 4 km ring drawn. Or replace it with a city shot of the island. This is the near-empty case from the director's notes, confirmed.

3. f00210 (3.5 s, open-burst, under the banner): near-black field, a tiny Guam polygon with a small flash and a 20 km ring. The label "10 KILOTON AIRBURST" is nearly invisible at bottom left (dark brown on near-black) and is far from the target. "ANDERSEN AIR FORCE BASE" is also bottom left, about 400 px from the flash. The banner is readable and clear of the tag and clock, and the flash is on the real target inside 8 s, so the opening itself is correct. Fix on open-burst: reduce widthKm so the island fills about half the frame, move both labels next to the flash (right side), and start the airburst label at full opacity.

4. f00000 (0 s, open-run): frame 0 shows the China coast, Taiwan and the Philippines with no Guam, no marker and no label. It is a dim map with no subject, and the clock "T-13:18" is the only thing that says what it is. This is the first frame viewers see. Fix on open-run: put the Guam target (marker plus "GUAM" label) in frame from frame 0, or start on the missile launch with a visible DF-26 track. Keep the launch point at left and Guam at right so the line shows who is against whom.

Non-blocking notes:

5. f00330 (5.5 s, open-rings): the "ANDERSEN AIR FORCE BASE" label is grey on a dark grey map. It is faint but readable, 130 px below the SIMULATION tag, and does not overlap it. This is the director's note, confirmed as a contrast problem only. Fix: give that label the white plate used in f00210, or start the fade-in earlier.

6. f00420 and contact frame 2 (7 s): the "5 PSI · 1.459 KM" label is dim red on a red-tinted ring and hard to read at phone size. Same fix: use the plated, brighter label colour.

7. Guam region views being mostly ocean (f35160 at 586 s and f00210) is acceptable only where the ring or marker fills the frame. Only f36000 and f00210 are below the bar. The other region frames I checked (f06600 Pearl Harbor 1941, f13800 China coast, f22800 DF-26 track, f09900 China coast, f30000 bars) show their subject, with labels inside the frame and clear of the corner tag and clock.

8. Not sampled: the 127 shots of which I saw about 28. Many of the sampled city frames are the same Andersen runway at different zoom (f04560, f05040, f05400, f17400, f31260 and others look near-identical). It is fine for the story but the director should confirm each new shot changes the picture (ring, label or zoom) at least every 4 s before 90 s and every 6 s after, which validate.txt already reports as ok.

Not staged: visual_approved is not recorded because of findings 1 to 4. Send to the director with this file; re-screen as round 2.


--- Round 3, reviewed 2026-11-22 ---

PASS

Scope: finding 4 only (f00000, open-run), re-rendered with `python -m studio stills 015-china-strikes-guam-pacific-bases 0s 1s`. validate.txt reads `ok` (no `retention:` or `pace:` lines).

1. f00000 (0 s): fixed. The frame now shows the China coast at left with an amber square and "LAUNCH (SIMULATED)", and a red Guam marker with ring and "GUAM" at right, with Taiwan and the Philippines between. It shows who is against whom, and the SIMULATION tag (top left) and "T-13:18" clock (top right) are clear of all labels. All labels are inside the frame and readable.

Non-blocking note: the red "ANDERSEN AIR FORCE BASE, GUAM" label sits over the Philippines, about 270 px left of the Guam marker and 50 px above its level, so it reads as detached. Fix if the director is revisiting: anchor it right of or below the GUAM marker, or drop it from frame 0 since "GUAM" already names the target.

Staged as visual_approved (round 3).

## Shorts (frames of s1, s2, s3 rendered at start, middle and end; craft rules 19 to 22)

FAIL

Windows: s1 0 to 32.85 s (32.9 s), s2 506.276 to 550.0 (43.7 s), s3 434.42 to 472.4 (38.0 s). All start on a paragraph or shot boundary and all fit 30 to 45 s. Two are strike windows (s1, s2), so rule 19 is met on count only; the problems are below.

1. s3 (13 MINUTES / FROM LAUNCH TO GUAM), frames f00006, f00090, f00180: the opener is a dim map of China and the Philippine Sea with one "CHINA" label and no Guam marker, then the caption "Guam is farther." A stranger cannot tell what "farther" refers to (rule 21 fail), and the first frame has no subject. The flash does not arrive until about 13.8 s (f00828 shows a near-black field with one tiny blue dot). Fix in shorts.json: start s3 later, on the paragraph that opens "At minute zero ..." or "Thirteen minutes earlier. A launcher in southern China raises a DF-26", or open on the c4-flash moment (448.1 s) and let the flight play after it. If kept, give the first sentence a self-contained subject (for example "A DF-26 takes thirteen minutes to reach Guam") and put the Guam marker and the DF-26 arc in frame 0.
2. s3, f00828 (13.8 s) and f00960 (16 s): near-empty dark fields. 13.8 s shows only a tiny Guam dot with a ghosted "ANDERSEN AFB" label; 16 s shows a small island outline and the caption "A DF-26 detonates over" with no marker or flash on it. Fix in the c4-m13 and c4-flash shots (region): tighten widthKm so the island fills the frame (about 60 km), add the marker before the word "detonates", and fire the burst on W("p..", "detonates") so the flash is on screen with the words.
3. s3, f00180 and f00240: a faint ghost label ("12.3 ... MINUTES OF FLIGHT") sits under "GUAM IS FARTHER" at about 8 percent opacity and collides with the arc. Remove the label or hold it clear of the label stack.
4. s1 (ONE 10 KT NUKE / ON GUAM), f01950 (32.5 s) and f01800 (30 s): the window ends mid-flight at T+10:31 with the DF-26 still over the sea and the caption "over 3,400 km." That is a cliffhanger, not a payoff (rule 22 fail), and the hook in shorts.json says the burst, which the Short has already shown at 2 s. Fix: end s1 on the burst line "One forty-three" repeated (the c4-flash payoff, or the end of the open-rings shot with the ring set up), or cut the flight and loop: open on the burst (2.2 s) and end on the same frame at the full-ring close-up. End must echo the title (ONE 10 KT NUKE ON GUAM).
5. s1, f01800 and f01950: the "FULL SIMULATION ON THE CHANNEL" pill sits on top of the "CHINA" label and over the "ABOUT THIRTEEN MINUTES" stack, with "CHINA" cut by the pill (f01950 reads "CHIN" plus the pill). Text over text. Fix: move the label stack or drop the CHINA countryLabel in the last 3 s of the window; or choose a final shot with no labels near y=690 (in the 300 px preview scale).
6. s1, f00006 and f00090: the strike is not in frame at the start. First frame is a dim map with "LAUNCH (SIMULATED)" and the burst is at 2.2 s, only visible at 3 s as a tiny fireball on Guam at 1000 km width (f00180). The Short opens on a launch, not on the flash. Fix: start the window on the burst (open-burst, 2.2 s) so the first frame is the white-out on Andersen, then let the launch follow; and make the Guam shot tighter so the fireball is readable on a phone.
7. s1 and s2 share the same ring set: s1 open-rings (f00480, 8 s) shows the 5 PSI ring, fireball and Andersen runways, and s2 (f00480 to f01800) is the same city shot with fireball, 20 PSI and 5 PSI at the same zoom (rule 20). Fix: let s1 stay at the flight and flash (no ring close-up, use the globe or the region view of the Pacific) and keep the ring-by-ring close-up only in s2. s3 should carry the timing and the minute-thirteen map.
8. s2 (5 PSI AT 1.5 KM / OVER ANDERSEN AFB): passes the opening (f00006 is the white-out, title band legible, 01:43 clock, SIMULATION tag present) and ends on the payoff "A 450 M MISS STILL LANDS INSIDE" with the 450 m ring inside the 5 psi ring (f02610), echoing the title. Two small fixes: at f02610 the pill sits flush on the "5 PSI · 1.459 KM" label, so move that label down or into the ring; and the white-out frame at f00006 shows the title band and clock on cream with no caption, which is fine on a flash but check the SIMULATION tag is readable on white (it is dim).
9. Title bands: all three are inside the safe area, two lines, weapon or number first then the target (s1, s2), s3 puts "13 MINUTES" first. They pass; s3's second line says Guam but the first frame shows no Guam.

Summary for the packager and director: re-cut s1 to open and end on the burst, move s3 to start at its flash or give it a clear subject on frame 0 and drop "Guam is farther.", and split the rings between s2 only. Re-run `python -m studio shotlist` and re-check the three window starts, middles and ends.


## Shorts round 2 (reviewed 2026-11-22; fresh stills of s1, s2, s3 at start, middle and end; validate.txt `ok`, no retention or pace lines)

FAIL

Windows now: s1 "13 MINUTES / FROM LAUNCH TO GUAM" 2.2 to 33.0 (30.8 s), s2 "5 PSI AT 1.5 KM" 506.3 to 550.0 (43.7 s), s3 "ONE 10 KT NUKE / ON GUAM" 448.1 to 478.4 (30.3 s). Note the round 1 numbering used other ids; I map each finding to the Short by title below.

Round 1 findings by number:
1. (13 MINUTES opener was a dim map plus "Guam is farther.") FIXED. s1 f00000 opens on the Guam outline under the title band with the clock, the glow starts by f00036 (0.6 s) and f00090 (1.5 s) shows the burst with "10 KILOTON AIRBURST" and "ANDERSEN AIR FORCE BASE" beside it. f00000 itself is a bare outline with no label (acceptable: the flash is inside 1 s).
2. (near-empty 13.8 s and 16 s frames) FIXED for s1, which no longer contains them. They survive in s3, see new finding A.
3. (ghost "12.3 MINUTES OF FLIGHT" label) FIXED: not present in s1 f00900, f01680, f01830, f01842. A transient 8% "1.5 KM: 5 PSI" fade-in is visible on s2 f01200; it is a normal fade-in, not a defect.
4. (ended mid-flight, cliffhanger) FIXED as judged below. s1 last frame f01842: DF-26 dashed line has reached the GUAM marker, labels "ABOUT THIRTEEN MINUTES" and "3,400 KM", clock T+10:55.
5. (pill over CHINA label) FIXED. s1 f01680 and f01842: the pill (y 540 to 590) is clear of every label; CHINA is no longer stacked there. s2 f02580 and s3 f01680 also clear.
6. (strike not in frame at start) FIXED for s1 and s2 (s2 f00006 is the white-out). s3 f00000 is a bare Guam outline, but f00090 (1.5 s) shows the burst on Andersen, so two of three open on the strike inside 2 s: rule 19 met.
7. (shared rings) FIXED. Rings appear only in s2 (f01200, f02580). s1 shows runway plus fireball radius only (f00240); s3 has no rings.
8. (s2 pill on the 5 PSI label) FIXED: f02580 has a 28 px gap between the pill and "5 PSI · 1.459 KM". The white-out SIMULATION tag at f00006 sits on a grey plate and reads.
9. Title bands: all three pass (inside the safe area, two lines, number or weapon first, target second).

Judgement calls:
- s1 ending: PASS as a payoff. The title asks "how long to Guam" and the last labels answer it ("about thirteen minutes", "3,400 KM") with the arc landing on GUAM, which echoes "13 MINUTES". It is an answer, not a cliffhanger. Optional polish: the clock reads T+10:55 while the label says thirteen minutes; if the director can end on T+13:xx it would be airtight.
- s3 ending: FAIL. It does not echo the title and it is the wrong subject (see finding B).

New findings:
A. s3 f00300 (5 s, c4-flash) and f00900 (15 s, c4-14apra): near-empty dark fields. f00300 shows a Guam outline about 250 px tall in a 1080x1920 frame with one marker and two labels; f00900 shows a tiny island at centre with two markers, a caption and about 80 percent black. Fix in shotlist.py: add a `short` override on c4-flash and c4-14apra (and c4-nothing+cold if it is similar) with a tighter widthKm (about 20 to 25 km for Andersen, so the island fills a third of the frame), or a city shot. Also s3 f00000 and f00090: the clock plate sits on top of the Rota polygon at top right (outline clipped under "T+13:18"); a `short` camera offset on c4-m13 and c4-flash that moves Guam down fixes it.
B. s3 f01680 (28 s) and f01800 (30 s): the window ends at 478.4 on "At about nineteen, the last weapon, the cruise missile, reaches Kadena." f01680 shows Okinawa with the "KADENA" and "CJ-20" labels; f01800 is a bare map of Japan and Korea with no label, no clock and no subject, under the pill. The Short is titled ONE 10 KT NUKE ON GUAM, so it ends on a different target, a different weapon and an empty frame: no payoff, no echo of the title. Fix in shorts.json only: end s3 at 472.6 (the c4-145 / c4-cruise shot and paragraph boundary), after "At fourteen and a half, the conventional DF-26 lands on Andersen", which keeps it on Guam. To stay at 30 s or more, start at 441.9 (the c4-m13 shot boundary), giving 30.7 s. Re-run `python -m studio shotlist 015-china-strikes-guam-pacific-bases` and look at the new s3 start (f00000) before accepting: c4-m13 must show a subject, not a dim map.

Verdict: FAIL. s1 and s2 pass. s3 fails on B (wrong ending) and A (near-empty frames).
Can a shorts.json-only change fix it? B yes (end 472.6, start 441.9). A no: it needs one `short` override per shot in shotlist.py (director), and the clock overlap with it. After both, a round 3 check of s3 only (start, middle, end) should pass.
