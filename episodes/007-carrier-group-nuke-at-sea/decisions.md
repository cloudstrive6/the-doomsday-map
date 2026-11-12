## Director (2026-11-12)
- 75 shots, 644.4 s. `pace:` lines left: 0; validate.txt: ok. Count is above the 55 to 70 guide: the first 90 s needs a cut or arrival every 4 s and shots of 8 s or less, and the sea has no map features, so the ring and group shots are short.
- No sea model in the engine: all strike pictures are region shots on open water (no city file), 20 km wide for the group and rings, 2 to 3 km for the fireball. Ship icons are fixed-size pixels, enlarged, and every group shot carries a legend or label saying so. Rings come from the scenario engine; the fireball ring and the carrier outline are drawn as zone polygons because the ring and line layers do not draw features under about 300 m.
- Opening: payoff first. A globe run-up (Japan lights, Iwo Jima, Guam, submarine, group) to the flash at 3.87 s, then the burst on a 20 km region shot. Banner 3.57 to 6.57 s over the globe and the burst.
- Wide ocean views use globes (night lights, real places) so the frame is never empty; region shots at 8 to 40 km are sparse by nature (ships and rings only).
- Merged short shots into 8 to 17 s shots with several camera keys and label arrivals (`merge()` in shotlist.py). The longest (up to 17.5 s) have an arrival at least every 4 s.
- Next scenario on the slate: "Full nuclear war minute by minute, globe only." No date.

## Packager (2026-11-12)
- Title (shipped, 45 chars, lint 88): "What If 1 Nuke Hit a US Carrier Group at Sea?". Runners-up: "What If 1 Nuke Went Off Beside a US Carrier Group?" (88), "What If a Sub Nuked a US Carrier Group? 20 Minutes" (84). Titles without a number scored 66 to 70.
- Search queries: "what if a nuke hit a carrier group", "nuclear bomb at sea", "aircraft carrier nuclear attack".
- Thumbnails: A weapon / dawn-gold (previous A: map/map in 006, skyline-strike/fire-night in 005), B launch / fire-night, C witness / daylight. thumbcheck ok. Variants have different text; none shares words with the title.
- Shorts: s1 0.0 to 41.8 (cold-open flash at 3.9 s), s2 325.7 to 357.6 (burst-lit shot, the light then the wave), s3 388.7 to 427.5 (rings; different from s1/s2).

2026-11-12 thumbnail review: original A (carrier, no flash) failed glow 12% and brightness 105 and was not clickable. Swapped ids so the missile launch (glow 20.8%, brightness 118) is A. B (carrier) and C (sailor) still weak on glow; left as Test and compare candidates.

## Packager, Shorts rework (2026-11-12, after visual_review FAIL)
- s1 301.85 to 337.5 (shot m-k start, the engine rejects 299.1 as mid-shot; flash on the first frames, ends on the blast-wave line), s2 543.0 to 587.4 (p44 to p46, the day after: dispersal-free fallout line; opens on a shot start, no chapter card), s3 404.7 to 446.6 (p34 to p36; rings drawn on frame 0, ends on where the carrier sits).
- The m-l burst echo was not used: the new s2 no longer contains p28, and moving a flash into a-d would contradict the long video. Two strike windows (s1, s3); s2 is the aftermath type.
- Finding 5 (engine "FULL SIMULATION ON THE CHANNEL" pill printed over the clock in the last 3 s) is engine layout, not shorts.json: left for the engine owner.

## Showrunner summary (2026-11-12)
- Rounds: research 1; script 4 fact-screen rounds (round 4 after lengthening 9.4 to 10.6 min); visual 2; thumbnail 1 (A swapped to the missile-launch variant, checklist 17/20); Shorts screen 1 plus one fix pass.
- `pace:` lines left: 0. `retention:` lines: 0.
- Top titles: "What If 1 Nuke Hit a US Carrier Group at Sea?" (88), "What If 1 Nuke Went Off Beside a US Carrier Group?" (88), "What If a Sub Nuked a US Carrier Group? 20 Minutes" (84).
- Risks: research had only 11 of 30 A rows two-sourced, so single-source facts were softened; sparse open-ocean frames (legible, not P0); Short s1 starts about 0.5 s into "The warhead detonates" (engine snaps to shot boundary); Short s2 is an aftermath window, not a strike; "FULL SIMULATION" pill overlaps the clock in the last 3 s of Shorts (engine layout, unfixed); B and C thumbnails are weak (only A uploads).
- Engine change: optional `until` on region labels (video/src/scene.ts, RegionMap.tsx).
- Hard craft rules: no sea model in the engine (rule 12 and 13 visuals), 75 shots to keep a new arrival every 4 s.
