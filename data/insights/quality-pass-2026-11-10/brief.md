# Orchestrated quality pass: The Doomsday Map (2026-11-10)

## Objective
Make every daily episode of The Doomsday Map (YouTube @TheDoomsdayMap: minute-by-minute what-if simulations of nuclear
war and great-power conflict on real maps, 11 to 14 min long video plus three Shorts a day, made unattended by Claude
agents in GitHub Actions) earn more clicks, hold viewers longer and grow the channel, by improving the rules the agents
follow. Owner: Bryce. Goal: at least US$1,000 a month by December 2026 (needs YouTube Partner Program: 1,000 subscribers
and 4,000 watch hours, or 10M Shorts views in 90 days).

## Success criteria (judged on episodes 004 to 010, 7 and 28 days after each publish)
| # | Criterion | Target | Baseline (data/analytics/2026-11-10.json) |
|---|---|---|---|
| C1 | Long-video thumbnail CTR at 7 days (median) | 5.0% or more | 001 2.49% (1,404 impressions), 002 4.55% (396) |
| C2 | Opening hold: viewers left at the 11% retention point (about 75 to 80 s) | 60% or more (median) | 001 46%, 002 54% |
| C3 | Average percentage viewed, long video (median) | 40% or more | 001 26.7%, 002 42.1% |
| C4 | Long-video views at 7 days (median) | 150 or more | 001 47, 002 39 (lifetime) |
| C5 | Shorts views at 7 days (median) and average viewed | 300 or more, 80% or more | about 110 views, about 83% (6 Shorts of 001 and 002) |
| C6 | Subscribers | 50 or more by 2026-12-10 | 3 (2026-11-10) |
| C7 | Craft: every episode passes QC and an independent rubric review averages 4 of 5 or more, none below 3 | every episode | no rubric yet |

Samples are tiny (21 to 47 viewers per long video), so treat every pattern as a hypothesis. Traffic so far: Shorts feed
1,670 of 1,811 views; related videos 62; search 38. Countries: US 419, JP 138, PH 90, RU 77, IN 61, DE 60.

Retention curves (share of starting viewers left, at 5% steps of the video):
- 001 (12.5 min): 1%: 0.98, 6%: 0.66, 11%: 0.46, 16%: 0.39, 21%: 0.34, 26%: 0.25, then flat about 0.23 to 0.27, 86%: 0.14, 96%: 0.09.
- 002 (11.2 min): 1%: 1.0, 6%: 0.89, 11%: 0.54, 16%: 0.54, 21%: 0.46, 31%: 0.42, 41%: 0.50, 46% to 76%: 0.39, 81%: 0.27, 96%: 0.27.
Shorts (lifetime views, average viewed): carrier 10 kt 1,199 / 88%; Taiwan 11 days of gas 266 / 99%; Omaha 800 kt 126 / 78%;
President 6 minutes 96 / 115%; China "quarantine" 82 / 40%; 4 near-misses 37 / 51%.

Already changed on 2026-11-09 (from episode 004): 11 s static disclaimer card replaced by a 3 s moving SIMULATION
banner and one spoken sentence; history moved early; episode ends on the simulation's day after; 10 s end slate;
photoreal Gemini thumbnails with a brightness gate and a thumbnail-reviewer agent. 004 publishes 2026-11-11, 005 after.

## Rules that always apply
No em-dashes anywhere (use commas, colons or "to"). Absolute dates. No secrets. Do not edit any file in the studio repo:
you are a reviewer; write only your output file. Do not publish, upload or message anyone. The studio's own rules are in
`Z:\Business Empire\The Doomsday Map\studio\CLAUDE.md` (editorial rules are hard: lanes, two sources per fact, no
death toll without a study, simulation labelled, no gore).

## Output (every specialist)
Write `<scratch>/orch/out/<your-name>.md` with:
1. Findings: what you checked and what you found, each with quoted evidence (file and line, frame name, or number).
2. Recommendations, ranked by expected impact (at most 8): for each, the criterion it serves (C1 to C7), the exact file
   and section to change in the studio, and the new rule text ready to paste (short, imperative, testable). Say what
   would prove it worked.
3. Craft rules: at most 12 one-line rules for a shared craft guide the agents will read on every episode.
4. Which parts of your skill you applied, and anything in the skill that does not fit this channel (and why).
Keep it under 1,500 words.
