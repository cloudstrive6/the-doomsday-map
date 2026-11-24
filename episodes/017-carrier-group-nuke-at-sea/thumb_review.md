PASS

Round 1 found the original A (carrier under a mushroom cloud, "5,000 ABOARD / 1 FLASH") scored 12/20. It is the same picture as 012 on the channel sheet (orange mushroom cloud over the sea, white-then-yellow text top left), "ABOARD" touches the cloud top at phone size, and the sky is magenta, not deep blue. The launch variant scored higher, so ids a and b were swapped in thumbs.json and `python -m studio package 017` was rerun. thumbcheck passes (a glow 50.6, b 39.3, c 15.6; brightness 183, 150, 168; no variety lines).

Scores after the swap (A = missile skimming the sea at dawn, "WHO FIRED? / NOBODY KNOWS", right):
A, 16/20
1. Phone read: 2. Missile and every word read at 250 px.
2. One subject: 1. Missile is the brightest thing, but only about a quarter of the frame height; glow 50.6%; bottom-right is clear water.
3. Words: 2. Four words, no tag.
4. Pairing: 1. title.py shows no duplicate; only the generic mobile-truncation note.
5. Curiosity gap: 2. The title says what a nuke does; the thumbnail asks who fired. The video poses exactly this question.
6. Truth: 2. Script: "nobody knows who fired", a low, fast contact. No numbers.
7. Distinct: 2. Concepts launch, skyline-strike, witness; palettes gold, fire-night, daylight.
8. Against the best competitor: 2. Brighter and cleaner than the 450k DEFCON 1 thumbnail; the competitors have bigger subjects.
9. Light: 1. Brightness 183, saturated gold and orange, but warm sky, not fire on deep blue.
10. Fresh: 1. A launch at sea in gold, text right, resembles 014 and 015 in palette and side; the sea setting and the question text are new.
B (carrier and fireball, "5,000 ABOARD / 1 FLASH"), 12/20: see the round 1 findings. "5,000" is in the script ("about five thousand people live aboard").
C (sailor and distant burst, "1 BURST / ESCORT GONE"), about 12/20: the subject is small (glow 15.6%), the dark figure is the strongest contrast, and the burst is far away.

Fixes, optional, to test in Studio:
1. A: regenerate with the missile larger and lower in the frame, filling about a third of the height, and with deeper blue in the upper sky.
2. B: if it is promoted, move the cloud away from the text, or shorten line 1 to "5,000 ABOARD" at a smaller size.
3. C: regenerate with the fireball filling a third of the frame.
