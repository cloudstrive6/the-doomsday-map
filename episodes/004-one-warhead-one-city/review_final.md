FAIL

1. qc.json reports "frozen 4.2s at 295.3s", over the 4 s limit. It is not on the end slate and not a chapter dip. The frame at 315 s shows the "Launch to impact: 11.1 minutes" timeline card, so the freeze probably sits on that card. Fix: add motion to the card (a moving marker or camera drift) or split it at a sentence, then re-render.
2. Loudness is -14.0 LUFS and true peak is -1.7 dBTP, both within limits.
3. shotlist_checks is empty, so there is no "no banner" finding and no retention breach. I did not look at the opening frames for the banner. The banner shows only 2.5 to 3.5 s, and the 21 s review frame is too late to catch it.
4. The frames I viewed (273 s, 315 s) carry the correct SIMULATION corner tag. The Loop map shows Chicago, and the subtitles are readable. I did not inspect the other review frames or the Shorts frames individually.
5. thumb_a.png is bright and readable at small size: "53X HIROSHIMA OVER THE LOOP", with a Chicago skyline and mushroom cloud.
6. metadata.json has the simulation disclaimer ("This is a simulation. It has not happened."), no em-dashes and no casualty figure. The title and description match the video.
