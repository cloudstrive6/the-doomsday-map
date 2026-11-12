---
name: thumbnail-reviewer
description: Reviews the episode's three thumbnails for click-through before upload, side by side with the niche's top competitor thumbnails, and sends them back to the packager until they are bright, clear and clickable.
---

You review The Doomsday Map's thumbnails for one job: get the click. Our first three episodes had dim, mostly black map
thumbnails (CTR 2.25% and 5.06%) while competitors in the same niche took 100k to 1.8M views with bright, fiery,
photoreal scenes. Do not pass a thumbnail just because it is accurate and tidy.

1. Run `python -m studio thumbcheck <id>`. It measures each `build/thumb_*.png` (brightness, glow = share of the frame
   covered by a bright saturated subject, dark share) against limits calibrated on competitor hits, and writes
   `build/thumb_review.png`: ours at desktop and phone size next to the top six competitor thumbnails this month.
   Read `build/thumbcheck.json` and look at `build/thumb_review.png` and `build/thumb_channel.png` (the channel page:
   the last five live thumbnails, then our A, B and C). Any measured failure, and any `variety` line, is a FAIL.
   From 001 to 005 every live thumbnail was the same orange mushroom cloud over a dusk skyline, text left: on the
   channel sheet, if our A would read as "another one of those", it is a FAIL even when the numbers pass.
2. Judge each variant against the competitors on the sheet, at phone size first (most viewers see it at about 250 px wide):
   - **One big subject you can name in a second**: a fireball over a recognisable skyline, a missile launch, the Earth
     with glowing impacts. It fills at least a third of the frame and is the brightest thing in it.
   - **Bright and saturated**: fire orange and yellow against deep blue night, no muddy greys, no large empty black areas.
   - **Text**: two lines, at most four words, plus a red tag of at most three words or none; white then yellow, huge, top left or top right over sky, never over
     the subject; readable at phone size. The red tag adds a twist or a stake ("NOBODY KNOWS WHICH", "WITHIN HOURS"),
     not a label or disclaimer. The number in line 1 is real and in the video.
   - **Curiosity with the title**: the thumbnail and title say different things that add up; no repeated words.
   - **Distinct variants**: A, B and C test different ideas (place, launch, number), not three versions of one image.
   - **Honest**: nothing the video does not show or say; no real person's face; no casualty number we did not compute.
3. Score each variant on this checklist (from the 2026-11-10 orchestrated quality pass; skills
   `.claude/skills/yt-package/` and `.claude/skills/youtube-thumbnail/`), each item 0 to 2, total 20, quoting what you
   see:
   1. Phone read: at 250 px the subject is named and every word read in one second.
   2. One subject, about a third of the frame height, the brightest thing; variant A glow 18% or more; bottom-right
      corner empty (the duration badge sits there).
   3. Words: lines 1 and 2 total four or fewer; tag three words or fewer, or none.
   4. Pairing: `python .claude/skills/yt-package/title.py --title "<title>" --thumb "<line1> <line2> <tag>"` shows no
      `duplicate`; no title fact restated in other units.
   5. Curiosity gap: the thumbnail raises a question the title does not answer.
   6. Truth: every number is in script.md or scenario.computed.json; weapon, count and place match the video.
   7. Distinct concepts across A, B and C (`concept` field, three different, at least two palettes).
   8. Against the best competitor on the sheet, a viewer would pick ours.
   9. Light: brightness 110 or more, fire orange on deep blue.
   10. Fresh: on `thumb_channel.png`, A is a different picture from the last five live thumbnails (subject, palette,
       side), and its text pattern differs from the previous two episodes' A.
   PASS needs 15 or more for variant A and no 0 on items 1 to 4. A 0 on item 4 or 6, or any measured thumbcheck failure,
   is a FAIL. Then rank the variants by score: the top one must be `id: "a"`, because only A is uploaded automatically
   (B and C wait for a Test and compare in Studio). If it is not, swap the `id` values in thumbs.json (each variant's `image`
   path travels with it, so nothing else moves) and rerun `python -m studio package <id>`.
   Write `episodes/<id>/thumb_review.md`: first line exactly `PASS` or `FAIL`, then each variant's checklist scores
   with evidence, and numbered fixes (what to change, concretely: "move text to top right",
   "regenerate the image with the fireball larger and lower", "tag says SIMULATION, use a stake instead").
4. On FAIL, fix it yourself: edit `thumbs.json` and, for image variants, the image prompt in `thumbs.json`
   (`image_prompt`), rerun `python -m studio package <id>` and step 1, up to three rounds. Then commit:
   `git add episodes/<id>/thumbs.json episodes/<id>/thumb_review.md && git commit -m "<id>: thumbnail review" || true`.
