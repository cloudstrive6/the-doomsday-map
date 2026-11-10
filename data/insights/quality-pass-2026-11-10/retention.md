# Retention specialist: C2, C3 (and C4)

## 1. Findings

**001 curve on the script** (narration/timing.json, episode.json; 6% = 45 s, 11% = 82 s).
- 7 to 45 s (0.98 to 0.66, retention.py's biggest cliff): p02 ends 21.7 s; then p03 "What you are about to watch is a simulation. It has not happened. But the missiles are real..." (22.2 to 41.6 s, 48 words) over the 11 s static `open-disclaimer` card and `open-title`.
- 45 to 82 s (0.66 to 0.46): p04 "Start with what exists today... About twelve thousand in total" (42.7 to 65.2 s, 19 s `c1-iso` "12,000+" card), then p05 "eleven missile divisions, from Kozelsk and Tatishchevo..." (65.7 to 90.2 s). An inventory where the viewer expected a launch. 002 is the same: 40 to 74 s lost 35 points on a 14 s disclaimer card and "ninety-seven percent of its energy".

**Do 004 and 005 fix it? Half.** Fixed: disclaimer is one 15-word sentence; 3 s banner over moving maps (004 17.4 s, 005 27.4 s); no card over 4 s in the first 60 s (qc.json clean). Not fixed:
1. Stakes come late. 005 p01 to p02 (about 0 to 18 s) is time, place, "aimed at open farmland", "looks like any other Iskander"; "the first nuclear weapon used in war since Nagasaki" lands at about 19 to 26 s (`open-field` 18.2 s, `open-nagasaki` 24.7 s). 004 says it twice: "Eleven minutes from now, it will be over the Loop" then "In eleven minutes, this is Chicago."
2. Payoff never proven. Both briefs name the flash as the hook moment; it first appears at 373.8 s (004 `c5-flash`) and 374.6 s (005 `c4-flash`), 55% in. 005 promises "In three minutes" and pays six minutes later.
3. No open question. hookscore.py (digits for numbers): 001 41, 004 40, 005 p01 39, 005 stakes line 39, all WEAK, CURIOSITY the weakest property in every one.
4. 005 repeats 001's 45 to 82 s mistake: chapter 01 opens on totals ("about forty-four hundred nuclear warheads", `c1-4400` 43 s), then `c1-tactical` "1,000 TO 2,000" held 11.5 s (64.2 to 75.6 s) and "NO PUBLISHED YIELD" at 75.6 s. The 11% point of 686 s is 75.5 s. 004 did open on a story (Hiroshima rings, 39 to 64 s).

**005 opening frames.** open_000 black. open_006 to open_018: one dark map with a dotted line for 13.2 s (`open-flight`), clock frozen at "T+00:40" in all five. open_021/024, under the strongest line: a near-empty dark map, a crosshair, "THAT FIELD", and the caption "No mapped building within 5 km of this point.", which deflates it. open_045 "ABOUT 4,400", open_050/055 a dark map with one dot, open_070 "1,000 TO 2,000".

**005 middle and end.** Chapter 02 (history) is 351 words, 24%, 112 to 280 s, mostly quotes and diplomacy captions over border maps (body_05_157s almost empty). Chapters 01 to 02 take 35% of words and the trigger lands at 4:40 (`c3-card` 280 s): the rule ("about a third... by about minute four") is missed; 004 met it (30%, 3:54). Hedge phrases ("we assume", "our choice", "simulated", "we give no", "expectation"): 001 10, 004 24, 005 23; "NO PUBLISHED YIELD" shown twice (75 s, 327 s); "We are choosing" card (300 s). Chapter 06 is 344 words (24%), mostly "We assume..." lists over static borders (body_18_529s to body_22_643s): a weaker form of the 80% exit seen in 001 and 002. Strongest frames: the fireball and rings (body_13_386s, body_15_443s, body_16_471s).

**Why C3 follows C2:** after 82 s both curves are flat (001 about 0.25, 002 about 0.39), so average percentage viewed is set mostly by who survives the first 80 s. retention.py on 5% bins reports HOOK LEAK 0.0 "healthy" because the first bin is at 45 s; 1% bins are needed (memo recommendation 8).

## 2. Recommendations (ranked)

**R1. Open on the payoff (C2, C3).** script-writer.md, Shape, Cold open; director.md, Opening minute.
> Cold open sentence one (at most 15 words): the worst moment, its place and its clock time ("Nine twenty-three in the morning, eastern Ukraine: the first nuclear weapon used in war since Nagasaki."). Sentence two: the disclaimer sentence. Then "Three minutes earlier." and the run-up. Director: 0 to 8 s shows that moment on the real target (the `burst` flash and the first ring drawing, 2 to 4 s), the banner over it while the disclaimer is spoken, ending by 12 s. Never open on a black frame.

Proof: 1% retention at 30 s of 85% or more; C2 of 60% or more on 006 to 010. The rewrite above, built from 005's own lines (A14, B1), scores 48 against 39.

**R2. Chapter 01 opens on a scene, no inventory before 1:30 (C2).** script-writer.md, Chapter 01 bullet.
> Chapter 01 opens with one real, concrete scene tied to the target (a test, a launch, a documented decision), not a total. No warhead, stockpile or force count before 1:30. Between 1:00 and 1:20, one line points back to the cold open ("Hold that number: it decides what happens to that field at minute three.").

Director: no number card in 60 to 90 s. Proof: higher 11% bin than 005.

**R3. Trigger by 3:30 (C3).** script-writer.md, Chapter 02 bullet.
> Chapters 01 and 02 together are at most 25% of the words (about 370); the trigger chapter card lands by 3:30. The history chapter keeps at most three events, each ending on a line that links it to this scenario.

Proof: average percentage viewed of 40% or more; the relative-retention peak moves earlier.

**R4. Hedge budget (C3, C7; keeps the editorial rule).** script-writer.md, Voice.
> In a [SIMULATION] chapter, frame it once in its first paragraph ("In our simulation, ..."), then narrate in plain present tense. At most one more hedge per chapter, only where a choice could be taken as fact (target, yield, a government's decision). Each honesty line ("no published yield", "no death toll") appears once in the episode. The fact-screener has the final word on any sentence that could read as fact.

Proof: 12 or fewer hedge phrases with script_review PASS.

**R5. Running clock (C2).** director.md, Opening minute.
> Cold-open and minute-by-minute simulation shots show a countdown to impact ("IMPACT IN 2:47") that changes every second; never a static per-shot stamp.

Needs a ticking mode in `scene.ts` if none exists (owner code change). Proof: no identical clock in frames 3 s apart.

**R6. Tighter opening-minute check (C2).** CLAUDE.md, Shot list essentials, opening-minute rule, plus a `retention:` line in the validator.
> In the first 60 s, no single shot over 6 s. The frame under the stakes line shows the target with real place labels and something moving toward it, never a near-empty map. No caption in the first 60 s argues against the stakes (move notes like "no mapped building" to the ring-by-ring chapter).

Proof: 005's `open-flight` (13.2 s) and `open-field` would have failed.

**R7. Re-hook at every chapter end (C3).** script-writer.md, Shape.
> Every chapter before chapter 05 ends on one sentence that the next chapter answers: an open question or forward pointer, no hype words.

Proof: no 5% bin drop over 8 points after 16%.

**R8. The day after is map events, not a list (C3).** script-writer.md, Chapter 06; director.md.
> Chapter 06 is at most 20% of the words. Each paragraph is one visible change on the map (a zone, a rerouted route, a plume, a closed border, a dark grid), tied to a study or real data row. Its first line restates the cold-open question.

Proof: the 76 to 86% bins hold within 5 points of the 71% bin.

C4: retention feeds browse and suggested reach, but at this sample size C4 rides mostly on CTR and the Shorts bridge (packaging lane). R1 also yields a "flash first" Short.

## 3. Craft rules
1. Sentence one is the worst moment, its place and its clock time.
2. Show the payoff (flash, first ring) in the first 8 s, labelled SIMULATION.
3. Say the disclaimer once, as sentence two, under the banner over motion.
4. Every hook opens a question the episode later answers out loud.
5. No totals or inventories before 1:30; chapter 01 starts with a scene.
6. The trigger arrives by 3:30.
7. No shot over 6 s in the first minute; nothing near-empty under a key line.
8. Simulation clocks tick; they never freeze.
9. Frame each simulation chapter once; never repeat a hedge.
10. Each chapter ends pointing at the next.
11. Every day-after paragraph changes something visible on the map.
12. Each number is said once and held no longer than its sentence.

## 4. Skill fit
Applied: yt-retention's leak/cliff/slide split and "biggest leak first" (retention.py on 001 and 002). yt-script's first-15-seconds test (confirm the click, open a question, prove the payoff), "show the artifact inside 20 seconds", "the turn", and hookscore.py on 14 hooks.

Does not fit: hookscore's ADDRESS ("you") and STAKES ("lose", "quit") lexicons suit creator-advice hooks and cap a calm narrator near 48; read only CURIOSITY and BREVITY, and score with digits. retention.py needs 1% bins. The voice-profile step and "one ask" are already covered by script-writer.md and the end slate rule.
