# Shorts specialist (C5, C6), 2026-11-10

## 1. Findings

**The six Shorts** (data/analytics/2026-11-10.json; n = 6, so hypotheses only)

| Short | Type | Len | Views | Viewed |
|---|---|---|---|---|
| 10 kt carrier (002 s2) | SIMULATION strike, US target | 60 s | 1,199 | 88% |
| 11 days of gas (002 s1) | one REAL DATA number | 36 s | 266 | 99% |
| Omaha 800 kt (001 s2) | SIMULATION strike, US city | 55 s | 126 | 78% |
| 6 minutes (001 s1) | REAL DATA clock | 54 s | 96 | 115% |
| Quarantine (002 s3) | REAL explainer | 42 s | 82 | 40% |
| 4 near-misses (001 s3) | REAL HISTORY list | 56 s | 37 | 51% |

- The carrier Short combines what no other Short has together:
  - a simulated strike on a named American target;
  - weapon and target in the title band ("ONE NUCLEAR SHOT / AT A US CARRIER");
  - the detonation at 10.1 s, then a new ring every 5 to 10 s;
  - a negation hook ("Its target is not a city.");
  - an ending on the episode's biggest line ("For the first time in eighty-one years, a nuclear weapon has been used in war").
- History and explainer Shorts lose half their viewers by the 16 to 26% point: quarantine falls to 0.667 at 16%, near-misses to 0.461 at 26%. Each needs earlier context ("Why the coast guard...") or covers four events. Both ran at 19:00 New York, so slot and type are mixed together; the 2026-11-08 memo's slot swap was never applied.
- hookscore.py rated the carrier opener 36 and the near-misses opener 39, so it cannot tell hits from misses. It only flags the weakest openers: "Minute zero. The launch." 28, "Take that one warhead" 29.

**004 and 005 against that pattern**
- 004 s1 (Chicago, 388.64 to 430.03) starts *after* the flash shot `c5-flash` (373.82 to 388.64). Its band "ONE WARHEAD / RING BY RING" leaves out Chicago.
- 004 s3 "TWO FALSE ALARMS" is the losing history type again, in the 00:00Z slot.
- 005 s1 opens on "Minute zero. The launch." over a dim border map (frame s1_0.02). The flash comes at 36 s (66% of the Short).
- 005 s2 starts after the flash on a small glow in a black frame (s2_0.02). It ends on "flying glass becomes the hazard", while the payoff line (script.md line 95) and the best hook (line 11, "...first nuclear weapon used in war since Nagasaki") sit outside every window. It also shows the same rings as s1 on the same day.
- 005 s3 "NOT A BLUFF" is a four-event politics story, at 00:00Z again.

**First 1 to 2 s (005 renders)**
- Frame 0 is black in all three. Map luma rises 16, 22, 28, 33, 38 over the first 20 frames, from `ShotView`'s 0.35 s fade from black (Episode.tsx `fadeIn`).
- No hook text: only the static title band (top 210 px, which is safe).
- Subtitles (50 px, bottom 560 px, safe) spell numbers the way they are spoken ("In September twenty twenty-two," in s3_0.02) and split them across cues: "point nine kilometres," in s2_0.75 is the tail of "one point nine". Cause: package.py `word_cues` uses the script text.
- The subtitle box can reach x 983, into the right action rail.
- Ring labels are about 18 to 22 px ("5 PSI · 1.67 KM"), unreadable on a phone.

**Ending.** The last shot fades to black over 0.35 s and the audio fades over 0.7 s (shorts.py `mux`), so no Short can loop seamlessly. The 6-minutes Short reached 115% because its last line echoes its title.

**Path onward.** Nothing on screen points anywhere:
- The long-video link is in the second paragraph of the description (youtube.py line 474).
- The related-video link "has no API: set it in Studio" (line 469), and nothing makes anyone set it.
- Result: 1 attributed subscriber from 1,196 carrier views, and 62 RELATED_VIDEO views.

## 2. Recommendations (ranked)

**R1. Pick Shorts by type (C5).** packager.md step 3, add:
> "At least two of three Shorts are SIMULATION windows with the nuclear flash or strike moment in their first 3 s and the target named. At most one REAL DATA Short with one number. No REAL HISTORY list Shorts. No two Shorts show the same rings. Aim for 30 to 45 s; up to 60 s only if a new ring or clock beat lands every 8 s or sooner. Rotate types across the three slots episode to episode."

Proof: the median 7-day views of strike Shorts against the others, over 004 to 010.

**R2. Hook segment from the cold open (C5).** shorts.py: accept `"segments": [[a, b], [c, d]]`. Build each segment as now, offset it onto the Short timeline, hard-cut the video and crossfade the audio for 30 ms. packager.md:
> "Open every Short with a 2 to 5 s segment that states the stakes, usually the cold-open line ('In eleven minutes, this is Chicago.'). The first sentence must make sense to a stranger: no 'Take that', 'Here is', 'Its' or 'Minute zero' openers."

Proof: "stayed to watch" of 70% or more (read in Studio; not in the API), and under 15% lost by the 16% point.

**R3. The title band names the thing (C5).** packager.md:
> "`title` line 1 = the weapon or the number ('ONE 800 KT NUKE'), line 2 = the named target or consequence ('ON CHICAGO'). Never process words: 'RING BY RING', 'MINUTE ZERO', 'THEN THE PHONES'."

Test: the validator checks for a place name, or a number plus NUKE, WARHEAD or MISSILE.

**R4. Strong first frame, seamless loop (C5).**
- Episode.tsx, when `shortTitle` is set: no fade-in on the first shot and no fade-out on the last.
- shorts.py `mux`: end fade of 0.15 s.
- packager.md: "The last line echoes the title band or the first line."

Test: frame 0 luma is at least 80% of the luma at 1.0 s, and the last frame is not black. Proof: average viewed of 90% or more.

**R5. Subtitles readable with the sound off (C5).** package.py `word_cues`:
- display text uses digits and units ("1.91 km", "5 psi", "2022") with the timing unchanged;
- a phrase never splits a number;
- box width at most 0.74 W.

Unit test: "one point nine one kilometres" becomes "1.91 km" in one cue. Raising the size from 50 to 64 px is a test only Bryce can approve, since 50 px was his decision on 2026-11-05.

**R6. A bridge to the long video and subscribing (C6, C4).**
- youtube.py: description line 1 is "Full simulation: {url}", and the upload posts a channel comment with the link (the API cannot pin).
- Episode.tsx: in the last 3 s, a small "FULL SIMULATION ON THE CHANNEL" line under the band.
- `notify` sends the three Studio edit links so someone sets the related video (about 1 minute a day).

Proof: more than 3 subscribers per 1,000 Shorts views (now about 1), and RELATED_VIDEO views rising.

**R7. Readable map labels in vertical (C5, C7).** Scale ring and place labels at least 2x when H > W, so they are 36 px or more. Test: a 50% still is readable at 360x640.

**R8. One-off, Bryce's call.** Re-cut 004 s1 to 373.82 to 430.03 (56.2 s, which includes the flash) with the band "ONE 800 KT NUKE / ON CHICAGO". It goes live 2026-11-11 14:00Z, and the re-cut replaces a scheduled upload.

## 3. Craft rules

1. Frame 0 is the strongest frame: no fade from black.
2. The first sentence makes sense to a stranger and names the weapon, target or clock.
3. One idea per Short; no lists of events.
4. The strike lands, or is promised with a time, in the first 3 s.
5. Title band: number or weapon, then the named target.
6. Something new every 5 to 8 s (ring, clock, cut).
7. End on the episode's biggest line, echoing the title so it loops.
8. Subtitles use digits, never split a number, and stay within x 60 to 960 and above y 1360.
9. Key map numbers are at least 36 px on a 1080-wide frame.
10. No two Shorts from one episode share a visual sequence.
11. The SIMULATION tag stays on screen; the flash is never gore.
12. Point to the long video in description line 1 and on screen in the last 3 s.

## 4. Skills applied, and fit

- **yt-shorts:** used the picking tests (complete first thought, a turn, ending on a line), a new first line, on-screen text in the first 2 s, and the loop point.
  - hookscore.py does not fit this channel: it rewards "you" in the first six words, which is wrong for a documentary voice, and it scored the hit below the misses. Use it only as a floor (rewrite below 30).
  - Its human "ship it?" gate does not apply to an unattended pipeline.
- **short-form-video:** used the retention arc, no fade-up, the first-against-last loop seam, the safe zones, and the curve debugging (an early cliff means a weak hook).
  - Not used: the 2 to 4 s cut rhythm and punch-ins. Maps need reading time, and our 88 to 99% Shorts cut every 5 to 10 s.
  - Not used: the 7 to 15 s loop length.
