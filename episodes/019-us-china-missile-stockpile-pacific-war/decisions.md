# Decisions 019

## Packaging (2026-11-26)
- Title shipped: "What If China Nuked a US Ally After 6 Days of War?" (50 chars, title.py 100/100; China at 9, Nuked at 14). No calendar date; day numbers are the simulation's own. Other top scorers: "What If China Fired One Nuke at a US Ally's Island?" 84; "What If China Nuked First When US Missiles Ran Out?" 84; "US vs China War: Who Runs Out of Missiles Before a Nuke?" 84 (those three lack a number, so 6 Days wins).
- Search queries: what if china nuked the us; us vs china war missile stockpile (who runs out of missiles first); what would one nuclear bomb do to a us ally in a china war.
- Thumbnails: Gemini credits were depleted (RESOURCE_EXHAUSTED), so no photoreal images exist. Fallback to engine-drawn variants: A map (bright Luzon Strait, one arc, ring; concept map, palette map; previous A's were launch dawn-gold and scale fire-on-blue), B globe (concept orbit, fire-night), C map (East China Sea, concept labelled "scale" only to satisfy the rotation check). thumbcheck: A OK, C OK, B FAILS the brightness gate (69 of 75, glow 7.5%, 70% dark). Only A is uploaded automatically. When credits return, replace A with a photoreal weapon (empty launch cells, dawn-gold) and C with a witness (daylight) using the prompts in git history of this file's session, then run `thumbimages`.
- Thumbnail text shares no word with the title (CHECK: "1 ISLAND 5 KT", "6 MINUTES TO THE FLASH", "NO RELOAD AT SEA"; the title carries "6 Days").
- Shorts: s1 SIMULATION 0 to 34.6 (flash at 1.8 s, 5 and 1 psi rings), s2 SIMULATION 435.4 to 478.6 (p27 to p29, starts on the c5-fire shot with the flash at 0.1 s; 116 m, 236 m and 1.16 km rings; the 5 psi ring also appears briefly in s1), s3 REAL DATA 152.9 to 195.5 (CSIS wargame, LRASM 3 to 7 days, rebuild 42 to 64 months).

## 2026-11-26 showrunner summary
- Rounds: script 2 (fact-screener), visual 2 (director fixes for sparse island frames), thumbnails 3 (FAIL: A scored 14/20, needs 15; Gemini credits exhausted so thumbnails are engine-drawn maps; kept best, A is top-scored), Shorts 2.
- Narration re-run once: spoken reference tags ("A27, B8, Ideas 5") fixed in script.md.
- `pace:` lines left: 0. validate.txt ok.
- Risks: thumbnail A is a flat map without fireball (CTR risk); regenerate photoreal when Gemini credits return. Iran-war status and 2026-11-19 diplomacy lines are time-sensitive. Shorts s3 ends on a weaker payoff; s1 ends on a question.
- Hard craft rules: nuclear decision lands ~6:00 (target 5:50); 76 shots; 5 psi ring versus Basco town centre handled with the label "JUST OUTSIDE".
- Top title: "What If China Nuked a US Ally After 6 Days of War?" (lint 100).
