PASS

Engine fallback only (Gemini HTTP 402; `thumbimages` retried once, no images). Round 1 improved A; round 2 (scale 7000) cropped London and was reverted. Kept: camera lat 54, lon -2, scale 5200, sun lat 50 lon 0, flash radius 600.

thumbcheck: ok, no variety lines. A: brightness 126, glow 28.0%, dark 30.1% (was 83, 10.5%, 57.5%). B 181 / 43.8%. C 183 / 39.0%.

Variant A "SCOTLAND GOES FIRST" (score 15/20)
1. Phone read 1: UK named at once, words readable; no fireball, so it reads as a map, not a blast.
2. Subject 1: Britain fills most of the frame and is the brightest thing, glow 28%; two yellow flash dots. Right side has a black strip (globe edge) but the bottom-right is clear of text.
3. Words 2: 3 words, no tag.
4. Pairing 2: title lint 100, no duplicate.
5. Curiosity 2: "goes first" begs why Scotland, while the title says London 8:49.
6. Truth 2: no number; Scotland hit first matches scenario (Faslane before Westminster).
7. Distinct 1: orbit / map / scale are three concepts, but B and C share the map palette.
8. Vs best competitor 0: no fire, no cloud, a weaker pick than the photoreal six.
9. Light 1: brightness 126 but muddy orange/grey, not fire on deep blue.
10. Fresh 2: first globe-from-above with this text on the right; last five were skyline, missile, cloud, map.
Total 15; no 0 on items 1 to 4.

Variant B "UNDER 9 MINUTES" about 12 (flat map, red lines, number is in the script). Variant C "590 KM APART" about 12 (same palette as B). A ranks first, id "a" is correct.

Fixes (when Gemini credits return)
1. Regenerate A as Big Ben with a fireball behind it, text top left over sky, per decisions.md.
2. Make B a missile breaking out of the sea at dawn, and C the empty-city aftermath, so all three have a different palette.
3. Remove the black strip at the right of A by fixing the globe canvas width in `video/src/Thumbnail.tsx`.
