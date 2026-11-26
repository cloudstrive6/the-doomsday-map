FAIL

Thumbcheck (final round): all three measured OK, no variety lines. Verdict is FAIL on the CTR judgement: the best we can draw with the engine (bright map) scores 14 of 20 for A, under the 15 needed, because it has no fireball and loses to every competitor on the sheet.

Rounds run: 3. Round 1 original set failed (B dark 70%, A and C empty blue maps, B text repeated "6" from the title). I rebuilt A as a close map of the Luzon Strait, B as a launch map, C as a globe with a flash.

Order after this pass: A = map "1 ISLAND / 5 KT" (id a, 14), B = map "ONE DF-26 / BASCO" (13), C = globe "NO RELOAD / AT SEA" (10, muddy grey haze, text unrelated to image).

Variant A (14/20)
1. Phone read 2: "1 ISLAND 5 KT" reads at 250 px; the thick orange line ending in a ring on a tiny island is named in a second.
2. Subject 1: line and ring are the brightest thing but the ring is small (about 12% of frame height); bottom-right is empty. Glow measures 71% only because the whole blue sea counts.
3. Words 2: four words, no tag.
4. Pairing 2: title.py score 100, no duplicate.
5. Curiosity 1: what is the island, what happens? Raised, but a map does not make it urgent.
6. Truth 2: five kilotons, Batan Island, DF-26 and six minutes are in script.md.
7. Distinct 1: A, B maps; C globe; palettes labelled map and fire-night but A and B look alike.
8. Vs best competitor 0: Defcon 1 and the 85 seconds blast are fiery photoreal; a flat blue map would not be picked.
9. Light 1: brightness 166, but blue sea and sand, not fire orange on deep blue.
10. Fresh 2: first map thumbnail after 014 to 018 (launcher, field, ship, mushroom); text sits top right like 015/017 but the picture is new.

Variant B (13): same checklist; weaker line, text overlaps the ring, "BASCO" means nothing to a viewer (1 on items 1, 5).
Variant C (10): glow haze is muddy grey and brown, a lit-up flash with no visible subject; "NO RELOAD AT SEA" is not shown by the picture (1 on 2, 6, 8, 9).

Numbered fixes
1. When Gemini credits return, regenerate A as a photoreal image: a single DF-26 launcher or a small airport island with a yellow-orange fireball over a deep blue night sea, fireball about a third of the frame height and the brightest object, bottom-right empty. Keep text "1 ISLAND / 5 KT" top right over sky.
2. Regenerate B as a missile launch at night (orange exhaust against blue), text "ONE DF-26 / 6 MINUTES" is a duplicate of the title, so use "ONE DF-26 / BASCO" or a stake tag such as "NO REPLY YET".
3. Replace C: the globe flash is muddy. Use a lit image of a ship firing a missile with "NO RELOAD / AT SEA", or the Earth with glowing impact points.
4. Engine-only fallback if credits stay out: add a fireball glow to the region map (orange and yellow radial gradient at the target, about 35% of frame height) instead of the thin dashed rings, and put the map on a dark blue theme with a brightness lift so brightness stays above 75.
5. After image changes rerun `python -m studio package 019` and `python -m studio thumbcheck 019`; the top scoring variant must be id "a".
