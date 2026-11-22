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
