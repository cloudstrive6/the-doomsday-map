# Episode 017 director decisions (2026-11-24)

- 127 shots, 660.3 s. Above the 55 to 70 guide on purpose: no shot over 8 s to 90 s and about 10 s after, a camera key or label every 4 s (6 s after 90 s) and the 007 failures (long near-still shots, tiny subject on black) needed short shots with the formation filling the frame.
- Validator: `retention:` lines 0, `pace:` lines 0 (build/validate.txt is "ok").
- Open sea has no coast, so every region shot carries its own km grid (lines), the generic ring formation is drawn as hexagon outline, spokes and range rings, and wide shots carry a filled range-ring blob. Lines under about 1 km do not draw in the engine, so deck markings and short bars are thin filled zones (`bar()`).
- Opening: flash on the group at 3.6 s (`open-flash`), banner 3.3 to 6.3 s over `open-group` and `open-flash`, run-up with a T-12:06 countdown clock.
- Burst point is over the east escort; the carrier and two escorts are 2.5 km from it, the supply ship 3.5 km, the far escorts 4.33 to 5 km (placed from the engine rings, not typed).
- Weakest frames left: `c3-fiction`, `c3-icons` and `c5-nohull` are wide or tight with few objects; their labels arrive every 2 s.
- Round 1 visual fixes: legend lifted above source strip (RegionMap), c1-alone/c3-fiction/c3-icons/c5-nohull reframed, carrier-group labels detached from markers. validate ok, 0 pace.

## Packaging (2026-11-24)
- Top titles: (1) "What One 10 kt Nuke Would Do to a US Carrier Group" 98 with thumb B or C (84 with thumb A, 5 words, thumb A trimmed to 3 words in thumbs.json is not possible without losing the stake; A has 4 words); (2) "One 10-Kiloton Nuke vs a US Carrier Group: Simulated" 94; (3) "US Carrier Group Hit by One Nuke: 12 Minutes Warning" 94 (shares "12 minutes" with a thumb idea, not used). Shipped 1.
- Search queries: what would one nuclear bomb do to a US carrier group; what if a nuke hit an aircraft carrier; nuclear bomb at sea.
- Thumb A skyline-strike fire-night (015 A weapon dawn-gold, 016 A daylight-flash daylight); B launch dawn-gold; C witness daylight.
- Shorts: s1 opens on the flash (3.6 s, the shot starts at 0), s2 starts 2.9 s before the fireball shot, s3 REAL DATA.

## Showrunner summary 2026-11-24
- Rounds: script fact-screen 2 (PASS), visual screener 3 on the long video (PASS), Shorts screener 2 (s3 collisions fixed by the director after round 2, not re-screened; s2 opens on a near-empty frame with the fireball by 1 s, s1 ends on the warning line rather than the burst: warnings). Thumbnail review 1 round, A scored 16/20 (swapped to the launch variant "WHO FIRED? NOBODY KNOWS").
- `pace:` lines left: 0. `retention:` lines: 0. Near-still share and frozen stretches are measured only by the CI render QC (007 failed there at 60%), the main risk.
- Top titles: "What One 10 kt Nuke Would Do to a US Carrier Group" (98 with thumbs B and C, 84 with A), "One 10-Kiloton Nuke vs a US Carrier Group: Simulated" (94), "US Carrier Group Hit by One Nuke: 12 Minutes Warning" (94).
- Hard rules: subject scale on open sea (no coast, km grids added), 127 shots to keep the 4 s arrival rate, Shorts opens on strike (2 of 3).
- Engine change: RegionMap.tsx legend sits higher when caption and source are both present.
