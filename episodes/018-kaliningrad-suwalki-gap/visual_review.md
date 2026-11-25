PASS

Round 3 (final). Stills f00540, f28200, f29280, f31200, f32700 re-rendered at 02:15 after the last shotlist.py change and viewed. validate.txt reads "ok": 0 `retention:` lines, 0 `pace:` lines. End slate and banner were verified in round 2 and are unchanged by this fix.

Round 2 items:
1. Ring labels: FIXED. f31200 (520 s, T+03:22) now reads "FIREBALL · 0.116 KM", "20 PSI · 0.236 KM", "5 PSI · 1.158 KM", "BURNS · 1.217 KM": one name and one value per ring, no bare numbers, no metres/km duplicates. f32700 (545 s, T+04:03) reads the same plus "WINDOWS · 3.134 KM"; all labels inside the frame, clear of the SIMULATION tag and the clock.
2. open-after: still weak, non-blocking. f00540 (9 s, T+03:31) shows the amber glow on a ringed TARGET marker, "IT HAS NOT HAPPENED" above it, the RUSSIA/NATO legend and the border, all clear of tag and clock. About 70 percent of the frame is empty brown field and there is no KALININGRAD name. It does show the subject and who is against whom, so it is not a fail. Optional polish: add a KALININGRAD city label or a stronger afterglow on the first 1.5 s.
3. Orphan labels: FIXED. f28200 (470 s, T+03:03) shows glow on TARGET, "ONE MISSILE", "WHAT DOES ONE WARHEAD DO?", legend; no stray KALININGRAD or LAUNCHER labels. f29280 (488 s, T+03:04) shows the dashed line ending on the burst ring with "AIRBURST OVER OPEN FOREST AND FARMLAND" and no orphan labels.

Cosmetic only: in f28200 the "20 KM" scale text is crossed by the blue border line.

Staged as visual_approved.

## Shorts review (2026-11-25, re-check after fixes)

PASS

Staged with `python -m studio shotlist 018-kaliningrad-suwalki-gap`: validate.txt ok, 0 retention lines. s1 0 to 57.2 s (11 shots), s2 466.29 to 525.8 s (7 shots, 59.5 s), s3 106.94 to 142.9 s (36.0 s, 4 shots). All three are 30 to 60 s. Stills rendered at the Shorts' first frames, the flash, the end frames and the c4-flash overlap (build/stills f00018, f00150, f00240, f00330, f03390, f27984, f28020, f28050, f28110, f31500, f06416, f06450, f06510, f06600, f08520). Two of three Shorts open on the strike moment with the target named, so the rule holds.

Previous findings:
1. s1 flash too late: FIXED. FL is now the spoken "Kaliningrad:" plus 0.1 s. f00018 (0.3 s) shows the enclave with the KALININGRAD dot and label, ISKANDER label, LITHUANIA, legend and T-02:33; f00150 (2.5 s) shows the flash ring and glow under the "SIMULATION . NOT REAL EVENTS" banner, clear of the corner tag and clock. The flash is inside the first 3 s.
2. s1 ending: FIXED. f03390 (56.5 s) ends on "A FORMAL NOTE TO NATO STATES" with KALININGRAD, BERLIN, WARSAW, BRUSSELS and the dashed lines from Kaliningrad: Russia's warning, a payoff. Labels sit inside the frame; the source line is bottom-left.
3. s2 target not named: FIXED. f28020 (467.0 s) shows the flash and ring with the label "KALININGRAD: TARGET" in red, readable beside the glow; f28110 (468.5 s) shows "ONE MISSILE" readable after the glow fades. The c4-flash overlap at 467 s is gone: no text over the corner tag or clock, no label over another label.
4. s2 ending: FIXED. f31500 (525 s) shows the finished ring sequence (FIREBALL 0.116 KM, 20 PSI, 5 PSI, BURNS, WINDOWS 3.134 KM), all labels inside the frame, SIMULATION tag and T+03:27 clear. Ends on a completed ring list, not mid-list.
5. s3 first frame: PARTLY FIXED. f06416 and f06450 (106.94 and 107.5 s) are still a bare amber outline with the legend and source line and no label; KALININGRAD and its dot arrive by f06510 (108.5 s) and BALTIC FLEET HQ by f06600 (110 s). Acceptable because s3 is the third Short and s1 and s2 are the strike openers.

Remaining findings (non-blocking, for the director and packager):
6. s1 label "KALININGRAD: 5 KT AIRBURST (SIMULATED)" (shotlist.py open-flash, lb(offp(B, 0, 30), ..., a + 1.0)) never appears: f00240 (4 s) and f00330 (5.5 s) show only the banner, then "5 PSI . 1.158 KM", and no place name on the burst frames. Fix: move the label to offp(B, 0, 140) and start it at a + 0.3 so it is visible below the banner (y over 130) and before the first ring label.
7. s3 (shot c1-fleet): the KALININGRAD label should be on screen by the first frame (the dot at t 0.1 does not show until about 1.5 s in). Fix: set the city entry t to 0.0 and check that the label fade is not longer than 0.3 s; the first second is an unlabelled map.
8. s1 first frame (f00018) is a dim map, but with a named dot, an ISKANDER label and a ticking T-02:33 clock, and the flash lands at 2.1 s. Keep it that way; do not lengthen open-fly.
