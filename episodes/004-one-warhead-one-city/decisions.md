# Decisions, episode 004 (2026-11-09)

- Script: fact-screener 3 rounds (FAIL, FAIL, PASS). Narration 11.1 min, 1,480 words.
- Visual: 3 rounds on the shot list (end slate length, label collisions), PASS; Shorts check found the narration reading "[C, engine]" refs aloud (regex in studio/narrate.py only matched A-D, S refs). Fixed the regex, re-narrated, re-aligned, rebuilt the shot list and re-timed the Shorts; final visual round PASS.
- studio/build.py end-slate check now measures from the last word in words.json (it measured from the narration total and let a 12 s slate pass).
- Thumbnails: 2 rounds, PASS (A 7/10, B 7/10, C 7/10). Risks: A subject is smaller (glow 13.6%); B Chicago not identifiable from orbit.
- Risks: scenario t0_utc is an internal date (2027-03-16) used only for sun position; script says "a Tuesday morning" with no date. A1/A19 rows are soft (search listing only); the Princeton Plan A figure is cited to the study. Minor Shorts polish items (clipped labels in s2/s3) left in visual_review.md.
- Hiroshima rings use the script's 1, 3, 12 miles converted, supported by A11.
