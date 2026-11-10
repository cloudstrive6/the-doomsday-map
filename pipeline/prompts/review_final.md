You are the **final screener** of The Doomsday Map, running unattended after the cloud render. Read `CLAUDE.md`. The
episode id is in `.current_episode`. Headless mode: do the work yourself, no background agents.

1. Read `episodes/<id>/build/qc.json` (loudness, frozen and black stretches). Any issue there is a FAIL unless it is a
   deliberate chapter dip under 1 s. Its `shotlist_checks` list the shot-list rules from 2026-11-09: a missing banner
   ("retention: no banner") is a FAIL, because the moving "SIMULATION · NOT REAL EVENTS" banner replaced the old
   disclaimer card; other `retention:` lines, the end slate length and early-ending music are findings to note under
   PASS.
2. Look at every image in `episodes/<id>/build/review/`: `sheet_NN.png` (one frame per shot, 12 to a sheet, taken
   0.3 s after the shot's last arrival; `shots.txt` maps each tile to its shot id and time), the 16 evenly spaced
   `long_*` frames, 3 frames per Short, and `episodes/<id>/build/thumb_a.png`. Check: correct corner tag, readable text inside the frame, maps showing the right
   places, no empty or broken frames, Shorts subtitles present and inside the safe area, thumbnail readable small.
   The end slate is meant to look half-empty: its framed "NEXT SCENARIO" box and the space beside it stay blank on
   purpose, because YouTube's end-screen elements (the next video and the subscribe button) are placed over them
   after upload. It also holds still on purpose (QC allows freezes there). Neither is a defect. It runs 10 s after the
   last word, which is a spoken line naming the next scenario. There is no static "this is a simulation" text card in
   the opening any more; the disclaimer is spoken once and shown as a short banner over moving footage.
3. Read `episodes/<id>/metadata.json`: title and description true to the video, the simulation disclaimer present,
   no em-dashes.

4. Score the rubric (from the 2026-11-10 orchestrated quality pass; episode 005 scored a mean of 2.3 as the baseline).
   Each criterion 1 to 5, and each score quotes at least two pieces of evidence (a sheet and tile, or a frame name, and
   what is visible in it; or a file and line). "Looks good" is not evidence.
   | Criterion | 3 looks like | 5 looks like |
   |---|---|---|
   | Hook and opening (0 to 90 s) | moves throughout, one hold of 5 to 8 s | the payoff (flash on the real target) inside 8 s, an arrival every 4 s or less, no card over 4 s |
   | Story pacing | trigger by about 4:30, one sagging chapter | trigger by 3:30, every chapter ends pointing at the next, ends on the day after |
   | Map readability | labels legible full size, one or two near an edge | every label plated, inside the frame and clear of the tag, clock and caption, readable on the sheet |
   | Subject and fidelity | subject visible but small or late | the subject of each sentence fills about a third of the frame, at the right place, as it is said |
   | Motion and pacing | eased moves, uniform dips, a soft flash | new information every 6 s or less (`pace:` lines few), varied moves, the flash lands hard |
   | Packaging | title and thumbnail true but repeat each other | title names who and where, thumbnail the number and stake, no shared words, hypothetical framing for real conflicts |
   | Accuracy and labelling | labels present, one repeated hedge | simulation labelled once per chapter, every number from research.md or the engine, no unlabelled choice |
   Also report `qc.json` `near_still` (share of the runtime) and the count of `pace:` lines as numbers.
   **P0 (any one is a FAIL):** text cut off at a frame edge or printed over the corner tag, clock or caption; a wrong
   place; a missing SIMULATION tag or banner; any QC issue; a title that states a simulated attack on a real, ongoing
   conflict as news; anything misleading. Scores below 3 are findings, not a FAIL, until the engine upgrades (label
   clamp, hard cuts, pace) ship; then the pass bar becomes no score under 3, and later a mean of 4.

Write `episodes/<id>/review_final.md`: first line exactly `PASS` or `FAIL`, then the rubric table (score and evidence
per criterion, and the mean), then numbered findings. FAIL for any P0, for defects a viewer would notice, or anything
misleading; never file a P0 as "polish". Commit:
`git add episodes/<id>/review_final.md && git commit -m "<id>: final review" || true`.
