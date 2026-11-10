# Visuals: map motion graphics (specialist report, 2026-11-10)

Criteria: C7 (craft), C2 and C3 (visual pacing). Evidence: episode 005 (686 s, 70 shots), `episode.json`, the engine in `video/src`, the frames in `orch/frames`, extra frames and strips I pulled from `final.mp4` into `orch/work/`, and an ffmpeg near-still scan.

## 1. Findings

**Pacing (C2, C3)**
- Shots are long and slow-changing. Mean shot 9.8 s; region shots average 12.4 s (30 shots, 372 s); 21 shots run 12 s or more (`c2-doctrine` 22.8 s, `c5-fallout` 20.4 s, `c6-un` 19.6 s). Benchmark: MapLore cuts every 3.1 to 4.2 s with the map always moving (`wiki/sources/maplore-animated-history-samples.md`).
- New information is sparse. Counting every timed arrival in `episode.json` (shot starts, labels, rings, arcs, flashes, camera keys), 40 gaps exceed 6 s and add up to 404 s, 59% of the runtime. Longest: 19.3 s at 198.6 s (`c2-doctrine`), 14.3 s at 257.7 s, 13.4 s at 497 s.
- The opening rule stops too early. C2 is read at about 75 to 80 s, yet `c1-tactical` is a number card held 11.5 s from 64.2 s to 75.6 s, followed by a 3.8 s stamp and a 9 s gap in `c1-range` at 87 s. `c1-bases` holds only "MOSCOW" for 9 s while the caption names land, sea and air forces; those three labels arrive at 9.1 to 10.8 s of an 11.9 s shot (`open_045.jpg`, `open_050.jpg`).
- QC freeze detection (`freezedetect=n=0.001:d=4`) passes footage that looks frozen. Rerun at `n=-45dB:d=2` (10 fps, 320 px), it finds 46 near-still stretches totalling 208 s (30%). Twenty of them last 4 s or more, for 138 s: 157.1 s (12.0 s, `c2-whitehouse`), 361.9 s (12.4 s, `c4-m2`), 375.6 s (9.7 s, after the flash), 484.4 s (11.2 s, `c5-fallout`). The 1% per second drift is too slow to read as motion.

**Readability (C7)**
- Map type sits below every floor. `RegionMap.tsx` `Label` defaults to 18 px, with rings at 15, zones and ships at 14 and the scale bar at 13; CityMap place names are 13 to 17 px and Chrome `source` is 13 px. The skill's floor is 24 px at 1080. In `full_8.jpg` the lines "LAUNCH: BELGOROD REGION (SIMULATED)" and "TARGET: OPEN FARMLAND (SIMULATED)" are thin red mono type on near-black, and on a phone they read as texture.
- Labels get clipped or overprinted, and nothing in the engine prevents it. `c6-answer` (`full_584.jpg`): all three message labels are cut off: "NO ALLY ANSWERS WITH A NUCLEAR WEAPON" sits at the top edge, "...ENTIONAL RESPONSE IS ONE OPTION" and "...ED US GENERAL, NOT FOR HIS GOVERNMENT" at the left. `c6-un` (`body_18_529s.jpg`): "WASHINGTON, 2022: 'DECISIVE' CONSEQUENCES" prints over the SIMULATION tag. `c6-radiation` (`body_19_557s.jpg`): "DETONATION" is cut at the right edge. The labels are placed at world points with `dx = -len*4.6` and no clamp, so a zoom carries them out of frame.
- Some frames are near-empty. `c6-next` at 643 s (`full_643.jpg`): a dark field and a marker cut by the bottom edge. `c2-whitehouse` at 157 s (`body_05_157s.jpg`): a 60 km Natural Earth view has no detail, so the frame shows a black spike and a tiny quote. `open-field` and `open-ground` (`open_018`, `open_021`): a crosshair and "THAT FIELD" on black.
- Land and sea barely separate (land `#1A2128` on `#0B0E12`, actor fills at 7% opacity). Countries read as glowing outlines with nothing inside.

**Motion (C7)**
- Every cut is a 0.35 s dip to black out and a 0.35 s dip in (`Episode.tsx`, `fadeIn`/`fadeOut`/`dark`). That is 69 identical transitions and about 48 s of darkened frames (`strip_cut18.jpg`). Frame 0 is black (`open_000.jpg`).
- The hero flash is muted. In `c4-flash` the burst fires at `flashT 0.1`, inside the shot's fade-in, and the black layer renders on top, so the peak frame comes out grey rather than white (`strip_flash.jpg`, tile 2). After it comes a static orange blob for 10 s with no shock front, no shake and no afterglow. `c5` then repeats the same centred blob five times in 51 s (`strip_flash2.jpg`).
- Colour usually means one actor (Ukraine teal, Russia amber, NATO blue), but `c6-rail` fills Russia red (`body_21_614s.jpg`) and `c2-doctrine` makes Belarus red.

**What works:** a consistent HUD (tag, clock, 34 px captions), the OSM city grid under the rings (a real edge over The Nuclear Clock's abstract plane), ring labels on backing plates, and the moving banner.

**The review step.** `visual-screener.md` and `review_final.md` are loose PASS/FAIL checklists with no scores and no pacing check. The final screener samples 16 frames, one per 43 s, and so missed every defect above. It also filed two real defects as polish under PASS: "'STAGING AREA (SIMULATED)' label runs off the right edge" and "quote line ... cut off at the right edge". The visual screener's round-2 notes quote frames well, but the structure never asks for that.

## 2. Recommendations (ranked)

1. **C7. Engine: label safety plus a validator** (`video/src/components/RegionMap.tsx`, `CityMap.tsx`, `Globe.tsx`; `python -m studio shotlist`). Rule for `CLAUDE.md`, "Shot list essentials": "Map labels render at 24 px or more with a dark plate, stay inside 96 px margins and clear of the tag, clock and caption boxes at every frame; `shotlist` projects every label box at shot start, middle and end and prints `layout:` lines, each a FAIL." Proof: 0 `layout:` lines, and 0 clipped labels across a 1-frame-per-shot sheet.
2. **C2, C3. Pacing rule** (`director.md`, "Opening minute" and step 1). Paste: "Something new arrives on screen (a label, ring, arc, ship, marker, camera key or cut) at least every 4 s up to 90 s and every 6 s after. No card longer than 4 s before 90 s. Map shots run 4 to 10 s; a longer shot needs an arrival at least every 5 s. Reveal each item on the word that names it (`W()`), never in the last 2 s of a shot." The validator prints `pace:` lines. Proof: no `pace:` lines, and C2 at or above 60% on 004 to 010.
3. **C2, C3. Perceptual freeze gate** (`studio/pipeline.py` QC; `CLAUDE.md` "QC"). "Second freeze pass at `n=-45dB:d=6` on a 10 fps, 320 px copy: any stretch outside the end slate is a FAIL, and the near-still total (d=2) stays under 15% of runtime." Proof: qc.json reports both numbers; 005 would show 30% and fail.
4. **C7. Transitions** (`Episode.tsx` plus a `transition` field in `scene.ts`; `director.md`). "Cut, without a dip, between shots in the same chapter; when consecutive map shots share a place, start the next view where the last one ended. Dip to black only into chapter cards. Frame 0 is a finished frame. A burst shot opens on a hard cut to full white." Proof: the cut count matches the shot count and strips show no grey flash frame.
5. **C7, C2. Hero flash v2** (`RegionMap`/`CityMap` burst). The flash peaks at full white for 3 frames, then bloom, a shock ring expanding at the modelled arrival times, 8 to 12 px shake decaying as e^(-14t) and an afterglow grade, and the fireball changes over 6 s. Write `c5` as one continuous pull-out that draws each ring on its word. Proof: a strip of the flash, plus a reviewer score of 5 on Motion.
6. **C7. No empty frames** (`director.md` step 3; `visual-screener.md`). "Region views under 150 km show only Natural Earth outlines: use a city shot or widen. The subject of the sentence fills a third of the frame height and sits inside the safe box at the end of the zoom." Proof: no near-empty frame on the per-shot sheet.
7. **C7. Colour grammar** (`director.md`). "One colour per actor for the whole episode (Ukraine teal, Russia amber, NATO blue, red only for strikes and SIMULATION); every map that shows two sides carries a legend chip." Proof: the contact sheet shows no actor changing colour.
8. **C7. A scored final review** (`review_final.md`, `visual-screener.md`). Replace the checklists with the rubric below. Sample one frame per shot (taken 0.3 s after its last arrival) plus the shot's end frame, as contact sheets, and quote frame names. Proof: every review shows 7 scores with evidence, and C7 can be measured.

## Rubric for the final screener (1 to 5)

| Criterion | 3 looks like | 5 looks like |
|---|---|---|
| Opening (0 to 90 s) | Moves throughout; one hold of 5 to 8 s | Frame 0 finished; an arrival every 4 s or less; no card over 4 s |
| Map readability | Labels legible full-size, 1 or 2 near edges | Every label 24 px or more, plated, inside safe areas, readable on the 360 px sheet |
| Subject and fidelity | Subject visible but small or late | Subject of each sentence is a third of the frame, at the right place, as it is said |
| Pacing and variety | Shots 8 to 14 s; same move on adjacent shots | Arrivals every 6 s or less; shot types and camera moves vary; one designed breath per chapter |
| Motion quality | Eased, but uniform dips and a soft flash | Easing by role, motivated cuts, flash peaks at white then lands |
| Card hierarchy | Primary large, secondary under 24 px | One primary 84 px or more, secondary 32 or more, nothing under 24, held by read time |
| Consistency | One colour or tag slip | Actor colours, tags, type scale and HUD identical in every shot |

Each score cites at least two frame names and what is visible in them. Pass: mean 4.0 or more and no score under 3. A clipped or overprinted label, a near-empty frame of 2 s or more, or a wrong place is a P0, and any P0 means FAIL. By my reading, 005 scores Opening 3, Readability 2, Subject 3, Pacing 2, Motion 2, Cards 3, Consistency 4, a mean of 2.7: FAIL.

## Engine features (impact over effort)

1. Label clamp, plate, 24 px floor and a projected-bounds validator. Small effort.
2. Transition field, cuts within chapters, a frame 0 with no fade. Small.
3. Pace validator and the -45 dB freeze gate. Small.
4. Missile head with trail, and strike or advance arrows with a draw-on head (MapLore's grammar). Small to medium.
5. Multi-key region camera (`[t, center, widthKm]`) for continuous pull-outs and holds. Medium.
6. Flash v2. Medium.
7. Base map v2: free shaded relief (Natural Earth), real land/sea contrast, rivers, 40 to 64 px country names, actor fills at 18 to 25%. Medium.
8. Actor legend chip. Small.

## 3. Craft rules (shared guide)

1. Something new arrives every 4 s up to 90 s and every 6 s after.
2. Reveal on the word that names it, never in a shot's last 2 s.
3. Map shots run 4 to 10 s; cards run 4 s at most before 90 s.
4. Nothing meant to be read is under 24 px; map labels sit on plates.
5. Labels stay inside 96 px margins and clear of the tag, clock and caption.
6. The subject fills a third of the frame height at the end of the zoom.
7. No region view under 150 km: use a city shot.
8. One colour per actor all episode, with a legend chip on two-sided maps.
9. Cut within a chapter; dip to black only into a chapter card.
10. Frame 0 is a finished frame.
11. The nuclear flash hits full white on a hard cut, then the shock front moves.
12. Never repeat the same camera move on adjacent shots.

## 4. Skills applied

- **video-director:** reads and hold times, new information every 2 to 4 s, slideshow and screensaver failures, type floors (24, 32 and 84 px), safe areas, easing by role, "every seam has a reason", the hero moment, the critic rubric with quoted evidence and default-reject, and a beat sheet sampled 0.3 s after each beat. Not a fit: its 7:1 contrast hook floor and 3 s hook card (a muted-feed rule; YouTube long-form opens with sound, so I applied it to Shorts only), its 8-of-10 bar (converted to the brief's 1 to 5 scale) and the "ban HUD chrome" tell (the HUD is this channel's identity; I kept it and banned only overprinting).
- **map-animation:** shared projection for overlays, labels kept horizontal and inside the safe area, colour equals meaning, focus plus context, route draw-on with a leading head, and data-driven beats. Not a fit: the 12 fps stutter (this is a 60 fps documentary HUD register, and stutter would read as dropped frames on a serious subject) and the Google Earth Studio to After Effects path (manual, browser-only and licence-bound, so it cannot run unattended in GitHub Actions).
