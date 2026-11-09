FAIL

1. QC is blocking: build/qc.json reports "frozen 9.6s at 720.5s" (limit 4 s). Loudness (-14.0 LUFS) and true peak (-1.8 dBTP) are fine.
2. The end slate (frame long_15_707s) has an empty framed box on the right labelled "NEXT SCENARIO" with no map or preview in it. It looks broken and is almost certainly the frozen stretch. It needs motion and content, or the box should be removed and the slate split or animated so no still stretch exceeds 4 s.
3. Not checked: the other 15 long-video frames and the Shorts frames were not inspected, because the QC failure already blocks this episode. Re-run the full visual check after the fix.
4. Metadata: the title and description match the video, the simulation disclaimer ("This is a simulation. It has not happened.") is present, and there are no em-dashes. The thumbnail (26 MINUTES TO SEATTLE, with a SIMULATION tag) is readable at small size.
