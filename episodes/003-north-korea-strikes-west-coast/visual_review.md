PASS

Second pass after the director's fixes. Re-rendered stills (78 files) checked: contact sheet (all 77 shots: correct corner tags, no black or empty frames, no gore, no real-person likeness) and full-size frames for c6-fireball, c6-burns, c6-fallout, c6-bangor, c6-sf, c6-vafb, c7-third, c1-tests, c3-gmd.

Previous blocking items:
1. c6-burns: fixed. FIRST HILL, MADRONA and SPACE NEEDLE labels removed; the 20 PSI, 5 PSI and burns labels no longer collide with street names.
2. c6-fireball: fixed. Only the fireball and DOWNTOWN SEATTLE labels remain, clear of each other.
3. c7-third: fixed. Label now "THIRD SITE, BY 2031" at x 1190 to 1400 with a dashed line and a ring on the East Coast; clear of the right edge.
4. c6-fallout: fixed. TACOMA and BELLEVUE readable above the caption; "SEATTLE . 1 PSI RING" sits above the ring.
5. Bangor, Vandenberg and San Francisco now carry a place label.
6. c1-tests and c3-gmd: labels moved off the rings and readable.

Remaining nits (not blocking):
- c6-bangor, c6-vafb: the BANGOR and VANDENBERG SFB labels float top right of the rings with no marker; the caption makes the place clear. Optional: anchor the label closer to the ring.
- c7-third: the Vancouver Island coastline touches the corner of the REAL DATA tag. Cosmetic.
- Credit lines are dim (shared theme, left as is) and the endslate preview box is the house template.


## 2026-11-05 Packaging review: thumbnails, Shorts, title claims

FAIL

Checked: thumb_a/b/c at 168x94 and full size; all three Shorts rendered vertically (1080x1920) from shorts.json via the
engine's own shot_list into /tmp (build/stills untouched), frames at start, middle and end of each window plus one per
shot; window boundaries against narration/words.json.

Blocking

1. Short s3 (197.1 to 229.7), shot c2-ucs (bars, 207.4 to 220.9; Short time 10.3 to 23.8 s): the bars card is
   laid out for 16:9 and sits under the Short title band. "HOW LONG / TO SEATTLE?" covers the card heading ("WARNING
   TIME ON A REAL ATTACK PATH"), its sub-line and the Los Angeles bar, and the REAL DATA corner tag sits on top of the
   "SAN FRANCISCO" row label. Three text collisions in one frame. Fix: for portrait (height > width) give bars,
   timeline, number and text shots a top inset of about 440 px so content starts below the title band and the corner
   tag (video/src/components for bars; same inset for timeline), or drop c2-ucs from s3 and retime the window. Whichever
   is chosen, re-render s3 and re-check.
2. Short s3, shot c2-honest (timeline, Short time 23.8 to 32.6 s): the heading "SEATTLE: UNDER THIRTY MINUTES" starts
   at the same y as the REAL DATA tag and touches it at the left edge; the "LOS ANGELES, 38" label is clipped at the right
   edge of the first frame and loses its unit; axis ticks and the "30 MIN" label are hidden behind the marker line. Same
   portrait inset as item 1 fixes the tag and heading; shorten the label to "LOS ANGELES, 38 MIN" and pull the
   timeline right margin in by about 60 px.

Non-blocking, fix if cheap

3. Short s3 start (197.1 s): opens on "Those numbers are not the warning time" with no referent for a cold viewer; the
   numbers (the 47, 53 and 86 minute flights) are on the stamp before it. Move start to 183.6 (shot c2-hs19, a
   paragraph start) if the window stays under 60 s (it would be about 46 s), or accept it, since the title band and the
   next shots carry the point. It ends well: "roughly half an hour." is a clean payoff.
4. Short s2 (493.3 to 544.0), c6-5psi and c6-1psi: ring labels are small mono text and crowd each other. "4.266 KM"
   runs into DOWNTOWN SEATTLE and BELLEVUE in the 1 psi frame; "THIRD-DEGREE BURNS 6.053 KM" crosses its ring and a
   road, with "KM" clipped by the road line; the T+25:30 clock clips the "KIRKLAND" place name at the right edge. Fix:
   in the Short's city shots (CITY_ZOOM or per-shot labels) drop the DOWNTOWN SEATTLE label after c6-fireball and put
   ring labels on the left or lower side of the ring. Starts on a paragraph ("It detonates", 493.6) and ends on the
   payoff "the glass becomes a weapon" before "An airburst" (544.1): good.
5. Short s1 (230.3 to 287.0): starts on the chapter's first paragraph, ends on "no realistic decoys" (285.8), a
   valid payoff. c3-gmd: the FORT GREELY label is about 14 px, drawn over the Alaska border line, and offset from its
   marker; Vandenberg's four interceptors are not shown. Move the label to the left of the marker with a dark backing,
   and add a Vandenberg marker so the 40 plus 4 split reads. The card shots (12 of 21, 2019 stamp, 44 text, scripted)
   leave the bottom 40 percent empty under the subtitle; acceptable, but centering the card content in the safe area
   (y 420 to 1500) would balance it.
6. Subtitle position and title band: bottom 560 px subtitle and 210 px top band are inside the safe area in all three
   Shorts; no text runs under YouTube's bottom overlay. Credit lines at y about 1410 are very dim (house theme), left as is.

Thumbnails (168x94 test)

7. All three headlines are 4 words or fewer, number first, and legible at feed size. thumb_a: "26 MINUTES / TO SEATTLE" is the
   strongest and the promise (a 26 minute clock) is kept (25.5 min flight in scenario.computed.json). Weakness:
   the left 55 percent is empty black and the map is a glow in a corner, with no North Korea shown, so who is against
   whom is not visible. Fix in thumbs.json a: widen `region.view.widthKm` to about 1,800 and centre near [-135, 46] so
   the Pacific and the arc from the west enter the frame, or add a red NK arc.
8. thumb_b: "4 WARHEADS / 32 MINUTES" is accurate (four of six get through; last lands 32.3 min after first launch) but
   carries two numbers and the headline text covers the continental US, the subject. Fix: line1 "32 MINUTES", line2 "4 WARHEADS",
   or shift the camera lon east by about 15 degrees. The NK end of the arcs is off frame; set camera lon to about -170 so
   the launch side shows.
9. thumb_c: "26 MIN / TO IMPACT" has no subject word and the red country is a speck at far left of the globe. It duplicates
   thumb_a's number. Use "26 MINUTES / TO IMPACT" only if a has been changed; otherwise change to "6 MISSILES / 26 MINUTES".
   The red tag text is small at 168 px in all three; acceptable.

Title and thumbnail claims against the editorial rules

10. Numbers: 26 minutes (25.5 for Seattle), 32 minutes (last target), 4 warheads, 250 kt, 44 interceptors, about 60
    warheads all trace to scenario.computed.json or sourced research; no casualty figure, no real person, no real
    date. Pass.
11. Framing: the title "North Korea Nukes Seattle: 26 Minutes From Launch to Impact", the Short titles "One North Korean Nuke Over
    Seattle, Ring by Ring" and "250 KILOTONS OVER SEATTLE", and all three thumbnails state the strike as fact with no word
    "simulation". The description is clear, but the hard rule is never to present a scenario as a prediction.
    Fix: metadata.json title "North Korea Nukes Seattle: A 26 Minute Simulation" (keep it under 70 chars), add
    "(Simulation)" to s2's yt_title, and put "SIMULATION" in the thumbnail tag in thumbs.json (for example tag
    "NORTH KOREA SIMULATION"). Short s1 and s3 are real-data pieces and need no change.
12. s2's hook says "A simulation" but the narration in the window never says it; the SIMULATION corner tag is present on
    every frame, which satisfies the tag rule.

To reach PASS: fix items 1 and 2 and re-render s3; apply item 11 (cheap text edits); items 3 to 9 recommended.
