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
2. `thumbs.json`, three photoreal variants (from 2026-11-09; see episode 003's `thumbs.json` and `video/src/Thumbnail.tsx`
   `image` variant). Our map thumbnails were too dark to get clicks (CTR 2 to 5%); the niche's hits are bright photoreal
   scenes with one huge glowing subject. Each variant has `id`, `line1`, `line2`, `tag`, `align` and an `image_prompt`
   that Gemini turns into the background (`python -m studio thumbimages <id>`, about US$0.04 an image):
   - Three different ideas, not three versions of one: a = the place (a recognisable skyline or landmark of the target
     with a fireball behind it), b = the scale (Earth or the region from orbit with the missile trails and impacts),
     c = the moment (the launch, the launcher, the warship: the trigger).
   - The prompt describes only the scene: subject, place, light, where the subject sits (the side away from the text).
     It must match the video: right coast, right number of missiles where the text gives one, right kind of weapon. The
     house style (bright fire against deep blue night, no text, no faces) is added automatically.
   - Title and thumbnail are one pairing: the title names who and where; the thumbnail gives the number and the stake.
     They share no words, and the thumbnail never restates a title fact in other units (800 kilotons = 53X HIROSHIMA).
     (002 repeated "FIRST NUKE SINCE 1945" and 003 repeated "26" and "Seattle".)
   - Text: line 1 the number or the hook (white), line 2 the consequence (yellow), at most four words over the two
     lines; the red `tag` at most three words, or no tag (seven words on the image at most: our 7 to 10 word tags were
     unreadable at phone size). The tag adds a stake or a twist, not a label or the word SIMULATION (the title and the
     video carry that). Every claim must be true in the video. Never a line that deflates the stakes ("OVER A FIELD").
   - Do not reuse the previous two episodes' thumbnail text pattern ("N MINUTES TO <CITY>" has run four times).
   - `align` puts the text on the side with empty sky; the subject goes on the other side.
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
