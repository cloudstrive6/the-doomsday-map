---
name: director
description: Turns the narrated script into the shot list (shotlist.py -> episode.json) with maps, globes, ships, rings and cards, and checks sample frames.
---

You direct the visuals. Read `CLAUDE.md` (shot list essentials), `pipeline/craft.md` (the shared craft guide), `video/src/scene.ts` (the full schema), the episode's
`script.md`, `research.md`, `scenario.computed.json`, `narration/timing.json` and `narration/words.json`, and study the
two reference directors: `episodes/001-russia-first-strike-america/shotlist.py` and
`episodes/002-china-blockades-taiwan/shotlist.py`. Reuse their helpers (`S()`, `W()`, `add()`, ring shots, arcs,
dayclock) and their audio plan block. Do not copy three things from them (owner's decision, 2026-11-09, from the
retention curves): the static `open-disclaimer` text card, cards held 6 to 14 s in the first minute, and the 15 s end
slate. The rules below replace them.

Opening (where 001 and 002 lost half their viewers, and 004 and 005 still lost a third by 80 s):
- Payoff first (from 2026-11-10): the cold open's first sentence is the worst moment, so 0 to 8 s shows it on the real
  target with the existing `burst` (the flash and the first ring drawing, 2 to 4 s), ending by about 12 s, then the
  run-up. Under the stakes line, show the target with real place labels and something moving toward it, never a
  near-empty map.
- No disclaimer card. Add an episode-level `banner` to the `episode` dict in shotlist.py:
  `"banner": {"start": b0, "end": b0 + 3.0}`. It covers the first nuclear image and the spoken disclaimer sentence
  (spoken by about 10 s): `b0 = min(<flash time> - 0.3, W(pid, "simulation") - 0.3)`, where `pid` is the cold-open
  paragraph holding that sentence (default text "SIMULATION · NOT REAL EVENTS"; optional `line` such as "BUILT FROM
  PUBLISHED MODELS"). Every shot under it must be a moving globe, region or city shot. The red SIMULATION corner tag
  stays on every simulation shot as before.
- Up to 90 s: something new arrives on screen at least every 4 s (a cut, a camera key, an arc launching, a ring
  drawing, a label arriving), no text, stamp, number or chapter card over 4 s, and no shot over 8 s. Cut long cards into
  map or globe shots with the number as a `caption` or label. No number card in 60 to 90 s unless it counts.
- After 90 s: something new at least every 6 s; map shots run 4 to 10 s, and a longer shot needs an arrival at least
  every 5 s. Reveal each item on the word that names it (`W()`), never in the last 2 s of a shot. The validator prints
  `pace:` lines for every gap; fix them (they are warnings for the screeners until the multi-key camera exists, but
  each one is a stretch where viewers leave: 005 had gaps over 59% of its runtime).

Readability and consistency (from the 2026-11-10 review of 005: clipped and overprinted labels, near-empty frames):
- Labels stay inside the frame with a margin of about 96 px at the start, middle and end of every zoom, and clear of
  the corner tag, the clock and the caption box. If a label cannot fit, shorten it or drop it; never let it run off
  the edge. Long quotes go in the `caption`, not as map labels.
- No region view under 150 km wide (it shows only coastline outlines): use a city shot, or widen. The subject of the
  sentence fills about a third of the frame height at the end of the zoom.
- One colour per actor for the whole episode (Ukraine or Taiwan teal, Russia or China amber, NATO and the US blue, red
  only for strikes and SIMULATION). Never repeat the same camera move on two adjacent shots.

End (the episode ends on the simulation, not on history): the last chapter is the day after; the `endslate` shot
starts on the spoken next-scenario line (the `End slate` paragraph) and ends at `TOTAL + 10`, with
`durationSeconds = TOTAL + 10`. Its `title` and `line` name the same next scenario as the spoken line, with no date or
schedule. The last `musicPlan` segment runs `"to": TOTAL + 10` (the mix lifts it after the last word; never end the
music early).

1. Write `episodes/<id>/shotlist.py` producing 55 to 70 shots that cover the whole timeline with no gaps
   (it prints a table and flags gaps). Every paragraph gets a visual that shows what is said: a real place on a map,
   a number card for a key number, a stamp for a date, a timeline for a countdown, bars for comparisons, ships and
   zones for naval action, arcs and flashes on the globe for launches, the hero strike as a ring-by-ring sequence
   (city shots for a city with OSM data; region shots with `burst` at sea). Tag every shot (REAL DATA, REAL HISTORY,
   SIMULATION), add `source` footers on real-data cards and a `clock` on simulation shots. If the hero target is a city
   without `video/public/city/<slug>.json`, fetch it: `node scripts/fetch-city.mjs <slug> <lon> <lat> 70` (run in `video/`).
   The end slate line names the next scenario from `data/ideas.md`.
2. Run `python -m studio shotlist <id>`; fix until there are no gaps or overlaps and no `validate:` lines (end slate
   length, music to the end, and every `retention:` line), except `pace:` lines: none may remain in the first 90 s, and
   at most 10 after it (004 and 005 had about 40 to 50; add labels, camera keys or cuts on the words that name things).
   Note the count left in decisions.md.
3. Run `python -m studio stills <id>` with 16 to 20 times spread across the episode (at least one per chapter and
   every map type you used, plus one frame in the middle of the banner, one 0.3 s after the flash, one at the END of
   the three longest zooms, and one on the end slate), then Read `episodes/<id>/build/stills/contact.png` and individual
   frames. Fix: subjects cut off by the frame, labels off-screen, cut at an edge or over the tag, clock or caption,
   empty frames, wrong places, unreadable text. Repeat until clean. Reference: `.claude/skills/map-animation/` (focus
   plus context, labels inside the safe area, colour equals meaning, route draw-ons) and
   `.claude/skills/video-director/` (read and hold times, new information every few seconds, type floors).
4. `python -m studio stage <id> shotlisted --note "<n> shots, <seconds> s"`.
