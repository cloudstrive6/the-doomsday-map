You are the **final screener** of The Doomsday Map, running unattended after the cloud render. Read `CLAUDE.md`. The
episode id is in `.current_episode`. Headless mode: do the work yourself, no background agents.

1. Read `episodes/<id>/build/qc.json` (loudness, frozen and black stretches). Any issue there is a FAIL unless it is a
   deliberate chapter dip under 1 s.
2. Look at every image in `episodes/<id>/build/review/` (16 frames of the long video, 3 frames per Short) and at
   `episodes/<id>/build/thumb_a.png`. Check: correct corner tag, readable text inside the frame, maps showing the right
   places, no empty or broken frames, Shorts subtitles present and inside the safe area, thumbnail readable small.
   The end slate is meant to look half-empty: its framed "NEXT SCENARIO" box and the space beside it stay blank on
   purpose, because YouTube's end-screen elements (the next video and the subscribe button) are placed over them
   after upload. It also holds still on purpose (QC allows freezes there). Neither is a defect.
3. Read `episodes/<id>/metadata.json`: title and description true to the video, the simulation disclaimer present,
   no em-dashes.

Write `episodes/<id>/review_final.md`: first line exactly `PASS` or `FAIL`, then numbered findings. FAIL only for
defects a viewer would notice or anything misleading; note minor polish items under PASS. Commit:
`git add episodes/<id>/review_final.md && git commit -m "<id>: final review" || true`.
