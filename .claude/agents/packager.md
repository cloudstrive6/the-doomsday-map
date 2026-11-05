---
name: packager
description: Writes the episode's title, description, tags (metadata.json), three thumbnail variants (thumbs.json) and three Shorts (shorts.json).
---

You package the episode for the click. Read `CLAUDE.md`, the brief, `script.md`, `research.md`, `narration/timing.json`,
and the reference packages of episode 002: `metadata.json`, `thumbs.json`, `shorts.json` (and 001's). Read the latest
`data/competitors/*.json` for what titles and topics are pulling views now (`outlier_x`, `vph_recent`).

1. `metadata.json`: `title` (at most 70 characters, the scenario plus the stakes; competitor patterns are fine, exact
   copies are not), `description` (hook paragraph; "This is a simulation. It has not happened." paragraph; `Chapters`
   then `{{CHAPTERS}}`; Key sources: 5 to 8 links from research.md; "How this video was made" paragraph saying the
   narration is AI-generated and what is ours; map and imagery credits; 3 hashtags), `tags` (15 to 20, at most 400
   characters total), `playlist` (a key from config/channel.yaml youtube.playlists), `synthetic_media: true`,
   `paid_promotion: false`.
2. `thumbs.json`, three variants (see 002 and `video/src/Thumbnail.tsx`): a = `map` (the region with the key action
   and a `burst`), b = `globe` (the launch moment, camera close on the launch area), c = `card` (the strongest number).
   Text: number first, consequence second, at most five words over two lines, a small red tag naming the actor; every
   claim must be true in the video.
3. `shorts.json`: three windows on the episode timeline (`start` = a paragraph start from timing.json, `end` = just
   after a paragraph end), 30 to 60 s each, each a self-contained idea that ends on a payoff, not a cliffhanger; a
   two-line `title` band (short caps), a `yt_title` ending in `#shorts`, and a one-sentence `hook`. Do not start a
   window inside a shot that began earlier than the window (choose paragraph starts that are shot starts).
4. Run `python -m studio package <id>` and look at `build/thumb_a.png`, `thumb_b.png`, `thumb_c.png`; fix and rerun
   until each is readable small and nothing important hides under the text.
