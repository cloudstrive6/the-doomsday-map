FAIL

1. QC is blocking and failed: `frozen 4.3s at 370.6s`. This exceeds the 4 s limit and is not a chapter dip or the end slate. The review frame at 363 s (SIMULATION, T+02:00, Iskander-M descending toward the staging area) shows an almost empty dark map with one dashed line, which fits a near-static stretch. Fix the shot at about 366 to 375 s in shotlist.py: add camera movement, a split at a sentence, or more content, then re-render.
2. Visual polish on the same frame: the "STAGING AREA" label is clipped at the right edge ("STAGING AREA (") and overlaps the scale bar. Move the label inward.
3. Passed checks: loudness -14.0 LUFS and true peak -1.7 dBTP are within limits. `shotlist_checks` is empty, so there is no missing-banner or retention finding.
4. metadata.json: the simulation disclaimer is present, the title and description match the video, and there are no em-dashes. The `{{CHAPTERS}}` placeholder is intended and filled at packaging.
5. Only the 363 s frame was inspected in detail. The other review frames, the Shorts frames and the thumbnail were not examined, because the QC failure already blocks the episode.
