PASS

Round 3. Evidence: validate.txt is "ok" (no `retention:` lines; 70 shots, 689.06 s, end slate 673.1 to 689.1 = 10 s after the last word). Stills re-rendered and read at 60, 430, 455, 478, 520, 600 and 615 s. `npx tsc -p video/tsconfig.json` (the `typecheck` script) exits 0. The CityMap/scene.ts change is an optional `angle` on rings; no shotlist for 001 to 003 sets `angle`, so their ring placement is unchanged (the default `40 + i * 26` is kept) apart from the label offset moving from +10 to +18 px and the stronger black halo, which are cosmetic.

Round 2 blocking findings:
1. c5-burns (455 s) text on text: FIXED. "FIREBALL", "20 PSI", "THE LOOP", "UNITED CENTER" each have their own position, no overprint.
2. c5-5psi (430 s) and 600 s collisions: FIXED. Labels are separated; no text overlaps text.
3. c5-1psi (478 s) missing 1 psi label: FIXED. "1 PSI · 17.014 KM" sits on the teal ring, upper left, clear of the corner tag.
4. c5-hiro1 (520 s): FIXED. "HIROSHIMA: 1 MILE · 1.6 KM" now reads in full (a road passes behind "1 MILE", covered by the dark halo).
5. c1-hirorings (60 s): FIXED. The 12 mile label is inboard of its ring at left and readable; 1 mile and 3 mile labels are clear. Corner tag REAL HISTORY, clock "1945" present.

Non-blocking polish (optional, does not fail the episode):
- 430, 455, 478, 615 s: the "20 PSI" label's first letters touch the orange ring, and the ring line crosses "9.7" of "THIRD-DEGREE BURNS" and "KM" of "5 PSI" at 478 s. Still legible. Offset those labels about 10 px further out.
- 615 s (Day 1 shot): the teal 1 psi ring cuts through the top-right "WHAT THE RINGS IMPLY" clock caption, and "1 PSI · 17.014 KM" sits 16 px below the SIMULATION tag. "LAKE MICHIGAN" runs to x 1917 (right edge) and "MIDWAY AIRPORT" is cut at the bottom edge. Readable on a phone; tidy if the director revisits.
- 478 s: "MIDWAY AIRPORT" starts on its airport icon.
- 600 s card ("GET INSIDE. STAY INSIDE. STAY TUNED.") is a deliberate text card with the SIMULATION tag, outside the first minute; acceptable.
- Opening minute, Hiroshima fireball glow, bare end slate: unchanged from round 2, accepted.


## Shorts review (2026-11-09)

FAIL

Evidence: windows checked against episode.json and narration/words.json; vertical stills rendered from the three Short episode.json files at start, middle and end (1080x1920). `python -m studio shotlist` re-run: s1 52.5 s, s2 56.9 s, s3 34.0 s.

Edited by the reviewer (small timing/title fix in shorts.json):
- s3: end moved 233.52 to 224.5. The old end sat on the "c2-minutes" text card and the line "officers had only minutes to judge", which the fact review softened. Window now ends on "No order was given." (a payoff), 34.0 s. Title changed from "A FALSE ALARM / AND FIVE MISSILES" to "TWO FALSE ALARMS / NO ORDER GIVEN"; yt_title now "Two Nuclear False Alarms: Petrov in 1983, Norway in 1995 #shorts" (dropped "Stopped a Nuclear War", an over-claim); hook no longer says "decision made in minutes". Note: script.md p17 still says "only minutes" in the long video; change it to "very little time" in the script (the long video narration must be redone anyway, see 1).
- s1 and s2 timings are fine: both start within 0.4 s before a paragraph start (p30, p08) and end on a payoff (p32 "ordinary buildings fail", p10 "one sixty-second of the second"), 30 to 60 s.

Blocking findings:
1. Narration speaks the source refs. `REF` in studio/narrate.py did not match "[C, engine]" or "[C, engine, A11]", so the TTS text and timing.json units keep them; heard.json shows "C." "Engine." spoken after p30, p31, p32, p33, p34, p35, p36 (for example 439.37 to 440.4 s, inside s1's last second, and p30 at 403 s inside s1). The same tokens leak into burned-in subtitles ("ordinary buildings fail. [C, engine]" on the last s1 frame). Fix applied: REF in studio/narrate.py now strips `engine` refs. Still to do (needs Google TTS credentials): rerun `python -m studio narrate 004-one-warhead-one-city`, `align`, `shotlist`, then re-check shorts.json times (all windows shift slightly after p30). I also removed the bracket tokens from the local narration/words.json (gitignored), which only fixes subtitles, not audio.
2. s2 title band collides with the bars card in vertical. At the start the band sits on the card headline "OUR WARHEAD IS ABOUT 53 TIMES HIROSHIMA" (text on text, also over the "HIROSHIMA, 1945" label); at the end the SIMULATION tag overprints the "15 Mt" bar label. Fix: in shotlist.py for c1-53x, c1-range, c1-small, push the bars' first row and title down about 260 px for the vertical layout (or give the bars shot a `top` offset), and move the tag clear of row 2. Alternatively shorten the s2 start so it opens on the globe c1-russia (but that loses the Hiroshima comparison).
3. s2 first frame (72 s) is near empty: only the headline on a dark background, with the band on top. Same fix as 2 (bars should be drawn from frame 0).

Non-blocking:
- s3 stamp card (26 SEPTEMBER 1983) runs 9 s at the start of a Short, but its sub-line is almost invisible; brighten it.
- s3 mid and end frames: the clock "1995" is struck through by the coastline and "21 JANUARY" is clipped at the right edge.
- s1: band, tag and clock do not overlap; "T+11:06" sits right under the band but is readable. Small ring labels are tiny on a phone.
- Band is two lines, legible, inside the safe area in all three Shorts.
