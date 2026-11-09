FAIL

1. Automated QC (build/qc.json) is not clean: frozen stretch 5.0 s at 449.9 s and 4.1 s at 641.9 s in the long video, both over the 4 s limit. The frame at about 464 s is a static "38 MIN" number card with no movement.
2. Both frozen stretches are in the long video, so fixing the long video's shots (add motion or split the cards at a sentence) clears them.
3. Shorts QC: frozen 6.2 s at 25.4 s in s1_silent and s3_silent (over 4 s). The QC also reports "size 1080x1920" as an issue for a Short. That size is correct for Shorts, so the size check may be misapplied to Shorts and needs checking.
4. Loudness is fine: -13.9 LUFS, true peak -1.8 dBTP.
5. Metadata: the simulation disclaimer is present, there are no em-dashes, and the title and description match the video. No problem there.
6. Spot check: the corner tags are correct (REAL HISTORY on the number card, REAL DATA on the Short). The Short subtitles are present and inside the safe area. The rest of the frames and the thumbnail were not examined, because the QC failure already decides the verdict.

Fix: re-shotlist the long video (add drift or a split at the 450 s and 642 s cards), re-check the Shorts windows that include the 25 s freeze, and re-render.
