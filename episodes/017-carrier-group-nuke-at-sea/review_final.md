PASS

qc.json: ok true, no issues, `shotlist_checks` empty (banner present, no retention lines), loudness -14.0 LUFS, TP -1.7 dBTP. `near_still` 160.9 s = 24.4% of runtime (warning, down from about 30% on 005). `pace:` lines: 0. Runtime 660.3 s (11:00).

| Criterion | Score | Evidence |
|---|---|---|
| Hook and opening | 4 | sheet_00 tile 001 (open-flash, 3.6 to 8.0 s): orange fireball with 5 PSI and 1 PSI rings on the group, T+20:09, caption "Simulation: it has not happened." Tile 000: the "SIMULATION - NOT REAL EVENTS" banner is visible at the top over moving footage. Shots in the first 90 s run 3 to 8 s; c1-spacing is 8.4 s and run-who is 7.5 s. No card over 4 s except the 3.8 s chapter card. |
| Story pacing | 4 | The burst is at 3.6 s and the full chain follows from 3:00 to 4:30. Chapters end by pointing at the next: sheet_02 tile 026 ends on the question "What happens to a fleet that is hit by an atomic bomb?", which leads to the Bikini chapter. sheet_08 tile 008 ("THE DAY AFTER") and sheet_10 end on the aftermath, with the unresolved choice "NOTHING KNOWN" / "NOBODY HAS DECIDED". |
| Map readability | 4 | Labels are plated and inside the frame on sheets 00, 02, 05, 08. Examples: sheet_08 tile 000 ring labels 20/5/1 PSI, sheet_05 tile 009 "BEYOND ANY LOOKOUT'S EYE". Small mono labels are tiny on the sheet. sheet_05 tile 004 "CARRIER" sits close to ring edges but is clear of the tag and clock. |
| Subject and fidelity | 3 | The carrier or group is central in most tiles (sheet_08 tile 001 carrier to scale 333 m, sheet_00 tile 006 deck). Several shots show a mostly empty ring-and-grid field: sheet_05 tile 008 (T-03:51, a small dot), sheet_02 tile 011 (Bikini tile with a small marker). The group is generic by design. |
| Motion and pacing | 3 | No `pace:` lines. 14 near-still stretches over 4 s, the longest 9.0 s at 591.5 s and 8.1 s at 228.7 s. Dips are only around chapter cards. The flash is visible in sheet_00 tile 001. |
| Packaging | 4 | Title "What One 10 kt Nuke Would Do to a US Carrier Group" is hypothetical. thumb_a.png reads "WHO FIRED? NOBODY KNOWS" over a missile at sunset, which is legible at small size and shares no words with the title. It does not show the number or the carrier; the stake is implied. |
| Accuracy and labelling | 4 | Corner tags change correctly: SIMULATION on the sheet_00 tiles, REAL DATA on chapter 1 (tile 010), REAL HISTORY 1946 in the Bikini chapter (sheet_02 tiles 003 to 011, and in sheet_08 tiles 006 and 007 for the flashback). Blast figures come from the engine and are credited ("Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"). Source credit on the Bikini shots: "Atomic Archive; nuclearweaponarchive.org". metadata.json has the disclaimer ("This is a simulation. It has not happened."). No em-dashes in metadata.json or script.md. |

Mean: 3.7.

Findings (none are P0):
1. Near-still share is 24.4%, with 14 stretches over 4 s. The 9.0 s one at 591.5 s and the 8.1 s one at 228.7 s are the worst. They pass QC, so the director could add camera moves.
2. A few shots are sparse: sheet_05 tile 008 (T-03:51, a dot with a ring and only a caption) and sheet_02 tile 011. The subject is small at the moment it is spoken.
3. Short 2 (s2_silent_1) has no subtitle in the sampled frame. It may be a gap between words.
4. The thumbnail has no number or carrier. It is true to the video but does not repeat the title; consider that for the next episode.
5. Short 3's 1 PSI ring is clipped by the right edge. Rings are not text, so this is not a defect.
