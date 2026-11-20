PASS

Round 2. Re-rendered 0.2, 130, 190, 369.7, 394.8, 449, 590.5, 324 (c4 first map), 451.5 (h5-take later), 559 (c6 first map) s, plus the c4 and c6 chapter cards (322 s, 557 s).
validate.txt reads `ok`: no `retention:` lines, no `pace:` lines. The end slate is 10 s after the last word by the validator's measure (accepted). Banner 1.8 to 4.8 s (3.0 s) over a moving region shot, unchanged from round 1.

Round 1 blocking items, verified:

1. FIXED. f26940 (449 s, h5-take): no clock plate in the top-right, so nothing prints over a basemap label. At 451.5 s (f27090) the plated label "HSINCHU: TSMC AND OTHER FABS" is white on dark, readable, and the crosshair sits directly beside it. Remaining nit (item A).
2. FIXED. f35430 (590.5 s, c6-cut+ships+gasclock): whole island in frame, south tip at y 1030 clear of the edge; "TERMINALS BACK ON" and the duplicate are gone, only "TERMINALS ASSUMED BACK ON" remains; "LNG TANKER" and "CARGO" now sit beside their chevrons, though the chevrons are only a few pixels wide (item B).
3. FIXED. f23688 (394.8 s, c4-clock): now carries "LNG: GUANTANG" and "LNG: TAICHUNG" markers, the label "AND HERE IS THE CLOCK" and the "THE CLOCK / HOUR 12" plate. f22182 (369.7 s): stray cyan line is gone; it shows two dark outage discs, a tower marker and "CELL TOWERS ON THE DARK GRID".
4. FIXED. f00012 (0.2 s): frame 0 is now the night-lights view of China, Japan and Taiwan, bright and readable, with the SIMULATION tag and 21:00 clock clear. The "KAOHSIUNG" label is still ghosted at frame 0 (item C).

Round 1 non-blocking items:
5. FIXED. f19440 (324 s) and f33540 (559 s) show the CHINA grey/orange outline and a TAIWAN / CHINA legend bottom-left, so who is against whom is clear.
6. PARTLY. f07800 (130 s): "NO PUBLIC EVIDENCE" now clear of Kinmen, but Taiwan's southern tip is still cropped at the bottom edge (item D).
7. FIXED. f11400 (190 s): "A PATTERN" at full opacity.

Corner tags are present and correct on every frame checked (SIMULATION, REAL DATA, REAL HISTORY). Chapter cards 04 and 06 are clean. No label is clipped except item A.

Non-blocking, for the director if the file is reopened:
A. f26940 (449 s, 0.3 s into h5-take): basemap label "BADE D..." at the top-right is cut off by the right edge, and the Hsinchu label is dim (fade-in) over road lines. Both clear by about 1 s (f27090 is clean). Nudge h5-take `camera` about 3 km west, or start the label fade 0.3 s earlier.
B. c6-cut+ships+gasclock: ship chevrons are tiny at 590.5 s; raise ship size or `widthKm` down about 20% once the south coast is in frame.
C. open-lit: the first label starts at about 15% opacity at 0.2 s; start at full opacity.
D. c1-none (130 s): widen about 8% so the southern tip is inside the frame.


## Shorts (013, checked 2026-11-20)

PASS

Ran `python -m studio shotlist 013-taiwan-goes-dark`: staged s1 40.9 s (11 shots), s2 48.5 s (7 shots), s3 46.6 s (9 shots), all inside 30 to 60 s. s2 start auto-snapped 389.73 to 389.01 and s3 603.18 to 603.179 (shot boundaries); shorts.json was not changed by me.

1. s1 (0 to 40.94 s). Starts on p01 ("Nine o'clock at night, southern Taiwan: the grid loses ten gigawatts"), ends 0.3 s after the end of p04 ("...take to start again"), a payoff. f00018 (0.3 s): bright night-lights view of China, Japan and Taiwan, KAOHSIUNG marker on the island, SIMULATION tag and 21:00 clock clear. This is the named target, so the opening is good. Mid frames f00480 (8 s, "A SIMULATION" label, black outage discs on southern Taiwan) and f02340 (39 s, Hsinchu streets, "MACHINES INSIDE THE FABS", 22:00 plate) are readable. Band "10 GW LOST AT ONCE" is 18 characters, the same length class as s3's 19-character line, so it fits the two-line band.
2. s2 (389.01 to 437.5 s). Starts 0.7 s before p32 ("And here is the clock", p32 begins 389.73) because c4-clock begins at 389.0 and the window cannot start inside a shot. That is a short silent lead-in, accepted (nit): if the packager wants a hard paragraph start, the director would have to cut c4-clock at p32. Ends 0.26 s after p34 ("Power returns in pieces. The fabs come back at reduced output, not zero."). f23400 (390 s): whole island with "AND HERE IS THE CLOCK" and the "HOUR 12" plate, clear of tags. f26160 (436 s): labels "POWER RETURNS IN PIECES", "LIGHTS BACK" x2 and "FABS: REDUCED OUTPUT, NOT ZERO" all inside the frame and readable. South tip is cropped at the bottom in the 16:9 source; the vertical cut is a separate native render, so this is a nit only.
3. s3 (603.18 to 649.75 s). Starts on p47 ("Where do the chips stop?"), ends 0.3 s after p49 ("This did not happen. The lights are on."), a payoff. f36240 (604 s): satellite globe over China, Korea, Japan, Taiwan, HSINCHU marker bright yellow with caption "Where do the chips stop?" clear of the bottom overlay. The map is darkish but has a named, glowing subject. f38940 (649 s): Taiwan with TAICHUNG, TAINAN, KAOHSIUNG, "THIS DID NOT HAPPEN", "THE LIGHTS ARE ON"; TAIPEI is mid fade-in (clears in a few frames).

Opening check: s1 opens on the target (night-lights, Kaohsiung), s3 on the named target (Hsinchu); s2 opens on the island with the clock. At least two of three qualify. No history list Short.
Static check: longest shot in any window is 9.5 s (s2) and 6.7 s in s1; the 12.1 s c6-nomodel+quiet has 4 camera keys, c4-d4+pieces 4, open-restart 3, so nothing is a still stretch over 4 s. No near-black frames seen. Bands are two lines with no em-dashes.
Caveat: the stills are 16:9 episode frames; I did not review a rendered 1080x1920 file, so safe-area placement of labels in the vertical cut is not verified here.
