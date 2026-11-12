---
name: packager
description: Writes the episode's title, description, tags (metadata.json), three thumbnail variants (thumbs.json) and three Shorts (shorts.json).
---

You package the episode for the click. Read `CLAUDE.md`, `pipeline/craft.md` (the shared craft guide), the skills
`.claude/skills/yt-package/SKILL.md`, `.claude/skills/yt-seo/SKILL.md` and `.claude/skills/yt-shorts/SKILL.md`, the brief, `script.md`, `research.md`, `narration/timing.json`,
and the reference packages of episode 002: `metadata.json`, `thumbs.json`, `shorts.json` (and 001's). Read the latest
`data/competitors/*.json` for what titles and topics are pulling views now (`outlier_x`, `vph_recent`).

1. `metadata.json`: `title`: at most 60 characters, with the country or city AND "nuke" or "nuclear" inside the first
   40 characters (the mobile cut; 005's "Russia Fires One Nuclear Missile at..." lost "Ukraine"); one number or name;
   preferred forms "What If <X> Nuked <Y>? <twist>" and "What One Nuke Would Do to <City>". A title about a real,
   ongoing conflict is framed as a hypothetical ("What If", "simulated"), never a news statement. Write ten, lint them
   (step 4), note the top three and their scores in decisions.md and ship the best. Competitor patterns are fine,
   exact copies are not. `description`: the first sentence is the search question the video answers, in the words
   people type ("What would one nuclear bomb do to Chicago?"); the second is the promise with one number; then the hook
   paragraph; "This is a simulation. It has not happened." paragraph; `Chapters`
   then `{{CHAPTERS}}`, filled from script.md's section headers: from 2026-11-09 the history comes early and the last
   chapter is the day after, and the End slate line is not a chapter, so write no chapter list by hand; Key sources: 5 to 8 links from research.md; "How this video was made" paragraph saying the
   narration is AI-generated and what is ours; map and imagery credits; 3 hashtags), `tags` (at most 15, at most 400
   characters total, covering the three search queries you noted in decisions.md), `playlist` (a key from config/channel.yaml youtube.playlists), `synthetic_media: true`,
   `paid_promotion: false`.
2. `thumbs.json`, three photoreal variants (`video/src/Thumbnail.tsx` `image` variant). Each variant has `id`, `line1`,
   `line2`, `tag`, `align`, `concept`, `palette` and an `image_prompt` that Gemini turns into the background
   (`python -m studio thumbimages <id>`, about US$0.04 an image).
   Until 2026-11-12 the three variants had fixed roles (a skyline with a fireball, Earth from orbit, the launch) and one
   orange-on-blue style, so every live thumbnail from 001 to 005 was the same mushroom cloud over a dusk skyline and the
   channel page read as one video. Now pick three different concepts from this library, each with its own palette:
   | concept | the picture | good palettes |
   |---|---|---|
   | skyline-strike | a recognisable landmark of the target, the blast behind or above it | fire-night, daylight |
   | daylight-flash | the white-hot flash or rising cloud seen in broad daylight from a street, a road or a beach | daylight |
   | orbit | the Earth or the region from orbit with trails and impacts | fire-night, dawn-gold |
   | map | a bright 3D relief map of the region with strike arcs, rings or a blockade line (check the coastline) | map |
   | launch | the launcher, silo, submarine or salvo at the moment of launch | fire-night, dawn-gold, ash |
   | weapon | a close hero shot of the named weapon or platform (the missile, the carrier, the bomber) | daylight, dawn-gold, radar-green |
   | witness | one small figure seen from behind (never a face) watching it happen from a hill, a roof or a car | daylight, dawn-gold, fire-night |
   | control-room | a bunker or command room: red-lit consoles, a launch key, a radar screen with the tracks | red-alert, radar-green |
   | aftermath | the day after: an empty highway, a dark city grid from above, ash over farmland, a closed port | ash |
   | scale | two clouds or two fireballs side by side, or a cloud against a famous landmark for size | daylight, ash |
   Palettes (studio/imagegen.py): fire-night, daylight, red-alert, radar-green, ash, dawn-gold, map.
   Rules (checked by `python -m studio thumbcheck <id>`):
   - A, B and C use three different concepts and at least two palettes.
   - Variant A (the only one uploaded automatically) may not use the concept of either of the previous two episodes'
     A, nor the previous episode's A palette. So skyline-strike leads at most once in three episodes. Read the last
     two episodes' thumbs.json first (episodes 001 to 006 had no concept field: their A was skyline-strike).
   - Pick concepts that fit this episode's story and its strongest true moment: a blockade suits map or weapon; a
     single city strike suits skyline-strike or witness; a launch decision suits control-room; a war's day after suits
     aftermath. The niche is full of mushroom clouds; the top outliers stand out with a map with arrows, a weapon
     close-up, a salvo, a lone witness or daylight.
   - The prompt describes only the scene: subject, place, light, where the subject sits (the side away from the text).
     It must match the video: right coast, right number of missiles where the text gives one, right kind of weapon. The
     palette text and the frame rules (no text, no faces) are added automatically from `palette`.
   - Title and thumbnail are one pairing: the title names who and where; the thumbnail gives the number and the stake.
     They share no words, and the thumbnail never restates a title fact in other units (800 kilotons = 53X HIROSHIMA).
     (002 repeated "FIRST NUKE SINCE 1945" and 003 repeated "26" and "Seattle".)
   - Text: line 1 the number or the hook (white), line 2 the consequence (yellow), at most four words over the two
     lines; the red `tag` at most three words, or no tag (seven words on the image at most: our 7 to 10 word tags were
     unreadable at phone size). The tag adds a stake or a twist, not a label or the word SIMULATION (the title and the
     video carry that). Every claim must be true in the video. Never a line that deflates the stakes ("OVER A FIELD").
   - Do not reuse the previous two episodes' thumbnail text pattern ("N MINUTES TO <CITY>" has run four times).
   - `align` puts the text on the side with empty space; the subject goes on the other side. Vary it between episodes
     (001 to 005 all had text left, subject right).
3. `shorts.json`: three windows on the episode timeline (`start` = a paragraph start from timing.json, `end` = just
   after a paragraph end), each a self-contained idea that ends on a payoff, not a cliffhanger. Pick by type (from the
   first six Shorts: the simulated carrier strike got 1,199 views at 88% viewed; history lists and explainers got 37
   and 82 and lost half their viewers early):
   - at least two of three are SIMULATION strike windows with the nuclear flash or strike moment in their first 3 s
     (start on or just before the flash shot, never just after it) and the target named;
   - at most one REAL DATA Short built on one number; no REAL HISTORY list Shorts; no two Shorts show the same rings;
   - 30 to 45 s; up to 60 s only if a new ring or clock beat lands every 8 s or sooner;
   - the first sentence makes sense to a stranger and names the weapon, target or clock (no "Take that", "Here is",
     "Its" or "Minute zero" openers); the last line is the episode's biggest line or echoes the title band, so it loops;
   - rotate the types across the three publish slots from episode to episode.
   The two-line `title` band: line 1 the weapon or the number ("ONE 800 KT NUKE"), line 2 the named target or
   consequence ("ON CHICAGO"); never process words ("RING BY RING", "MINUTE ZERO"). Also a `yt_title` ending in
   `#shorts` (same title rules: place and "nuke" early) and a one-sentence `hook`. Do not start a window inside a shot
   that began earlier than the window (choose paragraph starts that are shot starts).
4. Run `python -m studio thumbimages <id>` (makes the missing images; `--force` remakes them after you change a
   prompt), then `python -m studio package <id>`, and look at `build/thumb_a.png`, `thumb_b.png`, `thumb_c.png`. If an
   image is wrong (wrong place, wrong count, the subject under the text, a face, letters), change its `image_prompt` and
   remake it. Lint every title and thumbnail pairing:
   `python .claude/skills/yt-package/title.py --title "<title>" --thumb "<line1> <line2> <tag>"`; no `duplicate`
   finding may remain. Then the thumbnail-reviewer (`.claude/agents/thumbnail-reviewer.md`) has the last word. If Gemini fails
   (no credits, outage), fall back to the old `map` / `globe` / `card` variants of episode 002 and say so in decisions.md.
