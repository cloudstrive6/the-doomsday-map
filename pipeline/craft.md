# Craft guide (read on every episode)

From the orchestrated quality pass of 2026-11-10: four specialist reviews (retention, packaging, Shorts, map visuals),
each following its skill in `.claude/skills/`, and an independent scored review. The owner's playbook is
`doomsday-daily-episode` in the Bryce-Brain vault. Where this guide and `CLAUDE.md` differ, `CLAUDE.md` wins (its
editorial rules are hard). Episode 005 scored a mean of 2.3 of 5 on the rubric before these changes.

## Targets (judged on episodes 004 onward, 7 and 28 days after publish; `data/scorecard.md` is rebuilt daily)

| # | Criterion | Target | Baseline (2026-11-10) |
|---|---|---|---|
| C1 | Long-video thumbnail CTR at 7 days (median) | 5.0% or more | 001 2.49%, 002 4.55% |
| C2 | Viewers left at the 11% retention point (about 75 to 80 s) | 60% or more | 001 46%, 002 54% |
| C3 | Average percentage viewed, long video | 40% or more | 001 27%, 002 42% |
| C4 | Long-video views at 7 days | 150 or more | 001 47, 002 39 (lifetime) |
| C5 | Shorts views at 7 days, and average viewed | 300 or more, 80% or more | about 110, about 83% |
| C6 | Subscribers | 50 or more by 2026-12-10 | 3 |
| C7 | Final screener rubric (`pipeline/prompts/review_final.md`) | no P0; mean 4 or more | 005: 2.3 |

Samples are tiny (21 to 47 viewers per long video so far): read every pattern as a test, and change one thing at a
time (Experiments, below).

## Team and skills

| Agent | Skills it follows |
|---|---|
| script-writer | `yt-script` (hooks, first-15-seconds test; read only its curiosity and brevity scores) |
| director | `map-animation`, `video-director` (read and hold times, type floors, safe areas) |
| packager | `yt-package` (title and thumbnail as one pairing, `title.py` lint), `yt-seo`, `yt-shorts` |
| thumbnail-reviewer | `yt-package`, `youtube-thumbnail` (one focal subject, contrast, phone check) |
| visual-screener, final screener | `video-director` (critic rubric with quoted evidence, default reject) |
| growth-analyst | `yt-retention` (leak, cliff, slide), `yt-package` |

Skills that do not fit this channel, by design: `hookscore.py` rewards "you" and creator-advice words (a documentary
narrator scores low; use it only as a floor of 30); `retention.py` needs 1% bins; map-animation's 12 fps stutter and
Google Earth Studio path (60 fps HUD look, unattended CI); video-director's "ban HUD chrome" (the HUD is our identity;
only overprinting is banned).

## Craft rules

Script
1. Sentence one is the worst moment, its place and its clock time; the disclaimer is sentence two, by about 10 s.
2. The hook opens a question the episode answers out loud later.
3. No totals or inventories before 1:30; chapter 01 opens on a real scene.
4. Chapters 01 and 02 take at most 30% of the words; the trigger lands by 4:00 (aim for 3:30).
5. Each chapter before 05 ends on a line the next chapter answers.
6. Frame each simulation chapter once, then present tense; each honesty line once; never drop a label.
7. The day after is at most 20% of the words, one visible map change per paragraph.

Picture
8. The payoff (flash on the real target) shows inside 8 s, under the banner.
9. Up to 90 s: something new every 4 s, no card over 4 s, no shot over 8 s. After 90 s: something new every 6 s.
10. Reveal each item on the word that names it, never in a shot's last 2 s.
11. Labels stay inside the frame and clear of the tag, clock and caption at every point of a zoom; shorten or drop.
12. No region view under 150 km; the subject fills about a third of the frame at the end of the zoom.
13. One colour per actor all episode; red only for strikes and SIMULATION; no repeated camera move on adjacent shots.

Packaging
14. Title at most 60 characters; place and "nuke" or "nuclear" in the first 40; hypothetical framing for real conflicts.
15. Title names who and where; thumbnail gives the number and the stake; no shared words (lint with `title.py`).
16. Thumbnail: four words over two lines, a tag of three words or none; one bright subject a third of the frame.
17. The best-scored variant is `a` (the only one uploaded automatically); do not reuse the last two episodes' pattern.
18. Description line 1 is the search question in the viewer's words.

Shorts
19. Two of three Shorts are strike windows with the flash or strike moment in the first 3 s and the target named.
20. No history-list Shorts; no two Shorts with the same rings; 30 to 45 s.
21. Title band: the weapon or number, then the named target; the first sentence makes sense to a stranger.
22. End on the biggest line, echoing the title, so it loops.

## Engine work still to do (rules that wait for it are warnings until it ships and two episodes pass)

Ranked by impact over effort: (1) a finished frame 0, cuts without a dip inside a chapter, and the flash on a hard cut
to white; (2) label clamp, plates and a 24 px floor with a bounds validator (`layout:` lines), labels 2x in vertical;
(3) pace and near-still numbers as blocking checks; (4) Shorts bridge to the long video (description line 1, comment,
end line); (5) a ticking clock; (6) digits in subtitles; (7) Shorts built from several segments (cold-open hook);
(8) a region camera with several keyframes; (9) flash v2 (shock ring, shake, afterglow); (10) actor legend chip;
(11) base map v2 (relief, land and sea contrast).

## Experiments (one change at a time; the growth analyst adds rows)

| Started | Change | Criterion | First episode | Result |
|---|---|---|---|---|
| 2026-11-09 | moving banner, history early, end on the day after, 10 s slate | C2, C3 | 004 | due 2026-11-18 (7 days) |
| 2026-11-09 | photoreal Gemini thumbnails, brightness gate | C1 | 004 | due 2026-11-18 |
| 2026-11-10 | this guide: payoff-first open, pace rule, pairing rule, Shorts by type, scored review | C1 to C5, C7 | 006 | due about 2026-11-20 |
