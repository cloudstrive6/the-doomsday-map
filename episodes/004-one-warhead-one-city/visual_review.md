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
