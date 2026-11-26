PASS

Basis: build/validate.txt reads "ok" (no retention: or pace: lines), 76 shots, 664.8 s, end slate 17.9 s. Re-rendered stills for 1, 3, 5, 7, 9, 12, 20, 28, 40 and 510 s and read contact.png plus f00300 (5 s), f00540 (9 s), f01200 (20 s), f01680 (28 s), f30600 (510 s).

Round 1 findings, checked by number:
1. open-after (f00540.png, 9 s): FIXED. The frame now shows the China coast with "DF-26 SITE (SIMULATED)", the dashed DF-26 line, a labelled TAIWAN, a red "BATAN ISLAND" burst marker and the CHINA / US AND ALLIES legend. Subject and sides are visible. Still a dark field in the lower left (nit, see A).
2. open-day6 (f01680.png, 28 s): FIXED in substance. Now has the DF-26 line, "LUZON STRAIT", red "DAY SIX: BASCO" burst marker, Taiwan edge, legend and "DAY 06" clock. Not near-empty. The camera is still at 100 KM scale and China's coast is not in frame (nit, see B).
3. c5-fall (f30600.png, 510 s): FIXED. The orange fallout plume is drawn to the south-west with the blue island outline, "AIR BURST", "LITTLE LOCAL FALLOUT", "ASSUMED WIND: TO THE SOUTH-WEST", and a legend entry "SMALL FALLOUT PLUME". The subtitle sits clear of the legend and scale bar.
4. open-launch and open-df26 (contact tiles T-00:00, T+03:01; f01200.png at 20 s): FIXED. The DF-26 track is a full line from the Guangdong coast to Batan, with the chevron on it. Labels "GUANGDONG" and "A DF-26: CONVENTIONAL OR NUCLEAR" are readable and clear of the SIMULATION tag.
5. Banner: unchanged and correct. Contact tile T+00:01 shows "SIMULATION · NOT REAL EVENTS" over the moving city burst, clear of the tag and clock. f00300.png (5 s) shows the burst with the SIMULATION tag and T+00:03 clock, the "5 PSI · 1.158 KM" label inside the frame.
6. Label collisions: the "PHILIPPINES" and "LONGTIAN AIRBASE" / "TOMAHAWK" tiles from round 1 were not in this sample set; no overlapping text in any frame I read this round.
7. Checks that pass: corner tags present and correct on every frame (SIMULATION, REAL DATA on the Iran tile); no clipped text; no text over the tag, clock or subtitle; no black frames outside dips; no static disclaimer card; the end slate layout is unchanged.

Non-blocking nits for the director if there is another pass:
A. open-after: widen to about 300 km so the Luzon Strait and the line's full length to Batan share the frame (the line stops short of the marker at 9 s).
B. open-day6: the "LUZON STRAIT" label sits on the top of an island outline (f01680.png, label at about x 1170 to 1380, y 590 to 625). Offset it a little to the left or up. Add the camera key out to about 400 km so the China coast shows.

---

## Shorts windows (shorts.json), reviewed 2026-11-26

Verdict: FAIL (s3 opens on a dim card). s1 and s2 pass on windows. No window edges were changed; every start is on a shot
boundary and a paragraph start, and the only start that would fix s3 lands mid-word (see 1).

Frames read: build/stills/f00060.png (s1, 1.0 s), f26160.png (s2, 436 s), f28680.png (s2, 478 s), f09180.png (s3, 153 s).

1. s3 (152.912 to 195.506, 42.6 s, p12 to p13), f09180.png at 153 s: first frame is a near-black grid with a very dim
   "JANUARY 2023" stamp and one caption line, "CSIS, The First Battle of the Next War". No subject, no map: this is the
   "dim card with no subject" case, a FAIL for the packager. c2-csis is a stamp that runs 152.91 to 156.51 (3.6 s), so the
   first 3.6 s of the Short are this card. Fix, either: (a) director: give the c2-csis stamp a finished, bright frame 0
   (full-opacity stamp, and a map or the 3,000-mile Pacific behind it) so the Short opens on it; or (b) packager: start
   s3 at 156.51 (shot c2-game), which lands inside the word "CSIS" (156.031 to 157.22) so it is not allowed. Take (a). If
   the stamp cannot change, replace s3 with a window that opens on a map (for example p26 to p29 is already s2; p21 to p24
   of c4, the Day 5 and Day 6 build-up, 338.94 to 389.05, needs a paragraph check before use).
2. s1 (0.0 to 34.555, 34.6 s): opens on open-fly then the open-flash city burst at 1.63 s (flashT 0.1, rings and
   "BASCO AIRPORT: 5 KT AIRBURST (SIMULATED)" label, banner covers it): strike in the first 3 s, PASS. The end (p04, "the
   question is which side runs short first, and whether it matters") is a question, close to a cliffhanger, and the last
   6 s sit on the open-short world map. Not blocking because no later paragraph gives a payoff inside 60 s; packager: keep
   the hook line as the Short title and make sure the "FULL SIMULATION ON THE CHANNEL" pill is visible in the last 3 s.
3. s2 (435.447 to 478.586, 43.1 s, p27 to p29), f26160.png at 436 s: opens on c5-fire, which has its own flash
   (flashT 0.1) with orange afterglow over the Basco runway, SIMULATION tag and T+00:15 clock clear. Strike in the first
   3 s, PASS. f28680.png at 478 s: fireball, 20 PSI, 5 PSI rings and "BASCO TOWN CENTRE: JUST OUTSIDE" all inside the
   frame, no overlaps; it ends on the payoff ("stops just short of the centre of Basco town"). The 5 PSI label at lower
   left (x 200 to 480, y 915 to 950) is close to the left edge: in the 9:16 crop check it is not cut off.
4. s1 and s2 share the same place (Basco airport) and the same 5 PSI ring (s1 open-flash draws 5 PSI and 1 PSI; s2 draws
   fireball, 20 PSI, 5 PSI). They tell different stories (s1 the launch and the six-minute flight, s2 the ring walk), so
   not blocking, but the two titles both start "ONE 5 KT NUKE": packager, change s2 line 1 to a different lead, e.g.
   "THE 5 PSI RING" over "STOPS AT THE TOWN".
5. Title bands: two lines each, no more than 19 characters; s3 "GONE IN 3 TO 7 DAYS" is the longest, check it fits inside
   the safe width on the render. Two of three Shorts (s1, s2) open on the strike, so the 2-of-3 rule is met.

## Shorts re-check (2026-11-26)

Verdict: PASS. No window edges changed; validate.txt reads "ok" (no retention lines).

Frames read: f19572.png (s3, 326.2 s), f21450.png (s3 mid, c4-d5), f02040.png (s1 end, open-short 34 s).

1. s3 (325.847 to 358.4, 32.6 s, p21 to p22), f19572.png: opens on the c4-choice map, not dark or empty. China coast (orange),
   Taiwan (teal), Japan and the Ryukyus (blue), legend CHINA / US AND ALLIES at lower left, SIMULATION tag, "SIMULATED
   CRISIS DAY 04" clock top right, caption "Not a prediction: our modelling choice." Nothing clipped or overlapping. It is a
   map with no strike, so it is not a strike opener, but it shows who is against whom and names the day. Start is a
   paragraph start (first word "By" at 326.04). End sits 0.76 s after "dry." (357.64), before p23 at 358.635: lands on the
   payoff. f21450.png (c4-d5): "DAY 05", "HERE IT IS ONLY STARTING" and "CSIS GAME: JASSM-ER LASTED ABOUT 30 DAYS" inside the
   frame, clear of the scale bar and tag. Packager: in the 9:16 crop check the right-aligned CSIS label is not cut (it
   runs x 1186 to 1840 of 1920).
2. s2 title "THE 5 PSI RING / STOPS AT THE TOWN": two lines, distinct from s1 ("ONE 5 KT NUKE / ON BATAN ISLAND"). The earlier
   duplicate-lead finding is closed. s3 title "THE LRASM RUNS OUT / ON DAY FOUR" is 17 characters on line 1, fits.
3. s1 end warning (open-short 29.31 to 35.655, 6.3 s shot): the Short ends at 34.555, so only the last 5.2 s are on that
   shot, and it is a region map with a camera move and live labels, f02040.png ("WHO RUNS SHORT FIRST?", "CHINA'S
   MISSILES", "AMERICA'S MISSILES", clock "SIMULATED WAR DAY 06") with no overlaps. Accepted as a warning, not a FAIL. End
   is the question line after "matters." (34.2): packager keeps the "FULL SIMULATION ON THE CHANNEL" pill in the last 3 s.
4. Two of three Shorts (s1, s2) open on the strike, so the 2-of-3 rule is met; s3 is the named-subject map.
