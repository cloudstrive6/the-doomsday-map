# Independent review: The Doomsday Map quality pass (2026-11-10)

Spot checks: freeze45.txt holds 46 stretches (Visuals confirmed). The studio's `.claude/skills/` is untracked in git, so `title.py` is absent in CI.

## 1. Baseline score, episode 005

**Hook and opening minute: 2.**
- open_000 is pure black.
- open_012 and open_018 are 6 s apart and show the same map, with the clock frozen at "T+00:40".
- Under the best line (script.md line 11, "since Nagasaki"), open_021 is a near-black map with "THAT FIELD" and the caption "No mapped building within 5 km of this point."
- open_070 is the "1,000 TO 2,000" card, still up at the 11% point (75.5 s).
- Credit: one-sentence disclaimer (line 13), banner over motion (open_030).

**Story pacing: 2.**
- "4:39 The trigger" (metadata.json) misses the studio's own "by about minute four" rule (script-writer.md line 26).
- Chapter 02 runs from line 31 to line 47; body_05_157s is a near-empty map with a tiny quote.
- Chapter 06 hedges repeatedly: "We assume" (lines 99, 103, 107), "Those are our choices" (107), "All of it is simulated" (111).
- Credit: ends on the aftermath, strong last line (117).

**Map readability: 2.**
- sheet_03: "...NTIONAL RESPONSE IS ONE OPTION" is clipped at the edge, and "WASHINGTON, 2022: 'DECISIVE' CONSEQUENCES" prints over the SIMULATION tag.
- strip_flash: the fireball sits on a black field with no map detail.
- Credit: plated ring labels read (body_15_443s).

**Motion and transitions: 2.**
- strip_flash tiles 2 to 4: the flash peaks grey, because it fires inside the 0.35 s fade-in that every cut gets (Episode.tsx lines 76 to 78).
- `clock` is static text (scene.ts line 13), so the minute-by-minute section never ticks.

**Packaging pairing: 2.**
- The title, "Russia Fires One Nuclear Missile at Ukraine: The First 7 Days", is a news-style statement about a live war, with no "what if" and no "simulation".
- Thumb A, "15 KILOTONS / OVER A FIELD / AND THE WAR GOES ON", is 9 words, and "OVER A FIELD" deflates it. thumb_review.md: "lower half is empty brown field". (thumbs/005.jpg is only a placeholder, so I judged from the files.)

**Shorts selection and first frame: 2.**
- s1_0.02: "MINUTE ZERO / TO THE FLASH" and "Minute zero. The launch." over a dim map; the flash only comes at 36 s.
- s2_0.02: a small glow on black, and "RING BY RING" names no place.
- s3_0.5: the quote is cut off at "...TACTICAL NUCLEAR WEA".
- Credit: two of three are strike windows, the type that won.

**Accuracy and labelling: 4.**
- Line 13 is the disclaimer; lines 51 to 59 name each choice; line 93 says "we give no death toll".
- Refs are on every paragraph, and numbers are spoken in words (line 85). open_030 shows the banner.
- Deductions: the title drops the hypothetical framing, and line 45 (what commentators call it) is referenced only to [C].

**Mean: 16 / 7 = 2.3.** On C7 this fails.

Where I disagree:
- **Retention** ("stakes come late"): the line is placed fine; the picture under it (open_021, after a 13 s single shot) fails.
- **Shorts**: frame 0 is black for under 0.35 s. Cheap to fix, but the window choice moves C5.
- **Packaging** treats the 005 retitle as CTR only. It is also an editorial and misleading-content risk: the only title of five with neither a question nor "simulation", about a live war.
- **Visuals** (2.7) scores frames only; packaging and Shorts are as weak.
- review_final.md filed two clipped labels as "Polish" under PASS: the loose screener structure is the root cause.

## 2. Verdicts

**Retention**
- R1 MODIFY: open on the payoff, built from the existing `burst` (no engine change). The banner covers the first nuclear image, the disclaimer is spoken by 10 s, and frame 0 is never black. The CLAUDE.md banner line needs amending (conflict 3).
- R2 ACCEPT: a real scene is still "real history first".
- R3 MODIFY: chapters 01 and 02 take at most 30% of the words, with the trigger by 4:00 (aim for 3:30), as a warning; two curves cannot prove 3:30 beats 3:54.
- R4 MODIFY: drop the numeric cap. Keep "frame once, then present tense" and "each honesty line once". Any sentence that could read as fact keeps its label, and the fact-screener decides.
- R5 ACCEPT as engine; no rule until the clock can tick.
- R6 MODIFY: merge with Visuals 2 (conflict 4). "No caption against the stakes" is accepted.
- R7 ACCEPT: add "the next chapter answers it; no hype".
- R8 ACCEPT: every map event keeps its SIMULATION tag.

**Packaging**
- R1 MODIFY: the pairing rule applies now. The `title.py` lint waits until `.claude/skills/` is committed to the studio repo.
- R2 MODIFY: at most 60 characters (002 won at 64, so 55 is unproven), with the place and "nuke" or "nuclear" in the first 40. A title about a real conflict is framed as a hypothetical ("What if", "simulated"). Drop "score 90" as a gate.
- R3 ACCEPT.
- R4 ACCEPT: 7 words in total fits the niche's 6 to 8.
- R5 MODIFY: advisory only. The illustrated variant is seen only if R6 runs. Gemini spend is unchanged.
- R6 MODIFY: not a pipeline step, because there is no human step (Bryce, 2026-11-05). It becomes an optional Studio task Claude can run in a browser. The pooled proof rule is accepted.
- R7 ACCEPT.
- R8: moved to list (c).
- Checklist ACCEPT, advisory; FAIL only on items 4 and 6.

**Shorts**
- R1 ACCEPT: n is 6, but strikes are the only clear signal.
- R2 MODIFY: an engine item. Until it lands, start on a paragraph whose first sentence makes sense to a stranger.
- R3 ACCEPT as a validator warning.
- R4 ACCEPT; the echo line goes in the prompt today.
- R5 MODIFY: digits on screen only, with unit tests on the number patterns of 001 to 005, and timing unchanged. Size stays at 50 px (Bryce, 2026-11-05).
- R6 MODIFY: link and on-screen line yes; the comment is non-fatal; the Studio-links notify is optional.
- R7 ACCEPT (engine, with Visuals 1).
- R8: moved to list (c).

**Visuals**
- 1 ACCEPT. `layout:` lines are warnings until the clamp ships. Until then, a label over the HUD is a P0, fixed by dropping the label (as in 005 round 3).
- 2 MODIFY: the merged opening rule. After 90 s it is a warning with a budget (gaps over 6 s take under 30% of the runtime) until the multi-key camera ships. 005 had gaps over 59% of its runtime.
- 3 MODIFY: report the numbers in qc.json as warnings. As a FAIL it would stop every episode on today's engine (005 measured 30%).
- 4 ACCEPT; also fixes the grey flash.
- 5 ACCEPT (modest shake).
- 6 MODIFY: a rule for the director. For the screener, a near-empty frame lowers the score but is not a P0, because a subjective P0 would make FAILs flap.
- 7 ACCEPT; the legend chip waits for the engine.
- 8 MODIFY: record the rubric with frame-quoted evidence on every episode from today, using one frame per shot pulled from final.mp4 with ffmpeg. The gate stays on the P0 list (clipped or overprinted text, wrong place, missing tag or banner, QC fail) until engine items 1, 3 and 4 below ship. Then require no score under 3, and later a mean of 4.

**Conflicts, resolved by the authority order**
1. **Hedge budget vs the simulation label** (Retention R4 vs CLAUDE.md "never state a simulation choice as a fact"). The project rule beats skill advice: cut the repetition, not the labels.
2. **Tighter gates vs daily output** (Visuals 1 to 3 and 8, Retention R6). Bryce's unattended daily pipeline outranks craft results: a new check starts as a warning and blocks only after its engine change ships and two episodes in a row pass it.
3. **Payoff-first open vs the banner rule** ("while the disclaimer sentence is spoken"). Amend the rule so the banner covers the first nuclear image and the disclaimer is spoken by 10 s. This labels more, not less.
4. **Retention's "no shot over 6 s" vs Visuals' "4 to 10 s"**. Merge them into one rule: up to 90 s, something new arrives every 4 s or sooner, no card runs over 4 s and no shot over 8 s.
5. **Manual Studio work vs no human step.** These become optional tasks, never pipeline steps.
6. **Subtitle size.** It stays at 50 px, as Bryce chose.

## 3. Change set

**(a) Safe today (rules and prompts, no new blocking check)**
1. script-writer.md: Retention R1, R2, R3, R4, R7 and R8 as modified above.
2. director.md: the merged opening rule; payoff image in 0 to 8 s from `burst`; Visuals 6 and 7; labels clear of the HUD.
3. CLAUDE.md: banner amendment and merged opening rule.
4. packager.md: Packaging R1 (no lint yet), R2, R4 and R7; Shorts R1, R3 and the echo line of R4.
5. thumbnail-reviewer.md: Packaging R3 and the checklist.
6. visual-screener.md, review_final.md: Visuals 8 (rubric recorded, P0 gate).

**(b) Engine, ranked by impact over effort** (the rule each one gates is in brackets)
1. A finished frame 0, cuts within chapters, and the flash on a hard white cut. Small. [frame 0 rule, Shorts loop]
2. Commit `.claude/skills/` to the studio repo. Trivial. [`title.py` lint]
3. Label clamp, plates, 24 px floor, bounds validator, 2x in vertical. Small. [`layout:` FAIL]
4. Pace validator, and the -45 dB freeze numbers in qc.json. Small. [pace and freeze blocking]
5. The `upload` field in thumbs.json. Trivial.
6. Shorts bridge (link, non-fatal comment, end line). Small.
7. Ticking clock. Small. [R5]
8. Subtitle digits, with tests. Small.
9. Shorts made of several segments. Medium. [cold-open hook Shorts]
10. A region camera with several keyframes. Medium. [pace blocking after 90 s]
11. Flash v2. Medium.
12. Legend chip. Small. [legend rule]
13. Base map v2. Medium.

**(c) Needs Bryce's approval (nothing done)**
1. 005 (2026-11-12 00:00 UTC): retitle it "What If Russia Nuked Ukraine? The First 7 Days", and change thumb A line 2 to "FIRST SINCE NAGASAKI" with no tag. Top priority.
2. 004 (2026-11-11 00:00 UTC, hours away): retitle it "What One Nuke Would Do to Chicago, Street by Street".
3. 004 s1 (2026-11-11 14:00 UTC): re-cut it to 373.82 to 430.03 with the band "ONE 800 KT NUKE / ON CHICAGO". This replaces a scheduled upload.
4. 003 (live): leave it until its 7-day data (2026-11-17), one change at a time.
5. In Studio: Test and compare on 004 and 005, and related-video links on their six Shorts.
6. Studio has another session's uncommitted edits (workflows, scorecard): coordinate first.
