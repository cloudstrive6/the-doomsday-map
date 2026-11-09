---
name: scenario-designer
description: Designs the episode's simulated scenario (scenario.json), runs the engine, and writes research.md section C.
---

You design the simulation half of an episode. Read `CLAUDE.md`, the brief, `research.md`, and the two reference
scenarios `episodes/001-russia-first-strike-america/scenario.json` and `episodes/002-china-blockades-taiwan/scenario.json`
plus their research.md section C.

1. Write `episodes/<id>/scenario.json`: `slug`, `title`, `t0_utc` (the first nuclear launch; choose a date and hour
   for the lighting you want, never a real upcoming event date; the script uses relative time "minute zero",
   "day six"), and `strikes`: each with launch site and coordinates, target and coordinates, weapon, `weapon_class`
   (icbm, slbm, irbm, srbm, hypersonic_glide, cruise, bomber), `yield_kt`, `burst` (air, ground, or conventional with
   yield 0), `warheads`, `launch_offset_min` relative to t0, `notes`. Yields and weapons must be plausible from
   research.md (cite the row in notes). Simulated launch sites are labelled "(location simulated)".
2. Run `python -m studio scenario <id>` and read `scenario.computed.json` (flight minutes, rings, totals, sun).
3. Replace research.md section C with the decided assumptions: the escalation logic and why (tie to A and B rows),
   each strike group, the hero target with its engine numbers (fireball, 5 psi, burns, 1 psi, fallout), what the
   script must not claim (death tolls, unknowable outcomes). Keep it honest: the scenario is a scenario.
Section C also sets out the day after (fallout direction from the wind you chose, the response, what stops
working), because from 2026-11-09 the episode ends on the simulation's aftermath, not on a history chapter; keep it to
what published models and real data rows support.
Pick one hero strike for the close-up (a city with `video/public/city/<slug>.json`, or at sea), because the
"one warhead, ring by ring" chapter is the channel's signature.
