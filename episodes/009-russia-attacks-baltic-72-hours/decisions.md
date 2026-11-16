009 shotlist: 123 shots, no validate/pace lines (shot count over the 55-70 guide because pace rules need a cut or arrival every 4-6 s).

## Packaging (2026-11-16)
Search queries: "what if russia nuked lithuania"; "russia attacks baltic states simulation"; "suwalki gap kaliningrad".
Ten titles linted (title.py). Top three: (1) "What If Russia Nuked Lithuania? The First 61 Hours" 94, shipped (Lithuania + Nuked inside 31 chars; mobile warning is the generic cut note); (2) "Russia vs NATO: A Nuke Hits Lithuania at Hour 61" 98 but reads as a news statement, rejected; (3) "What If Russia Nuked the Baltics? A 72-Hour War, Simulated" 94, tail too long for mobile and 72 hours is not the video's number (61).
Thumbs: A weapon/dawn-gold (007 A launch/fire-night, 008 A orbit/fire-blue), B witness/daylight, C aftermath/ash. Text shares no word with the title. 72 HOURS from the brief dropped: video runs 61 hours.
Shorts: s1 SIMULATION cold open (flash 2.1 s), s2 SIMULATION ring-by-ring from the chapter card (flash at 2.5 s; the first seconds share the fireball ring with s1, unavoidable, only two flashes exist), s3 REAL DATA one number (65 km). Strike Shorts start on shot starts.

## 2026-11-16 showrunner summary
- Rounds: fact-screener 3 (FAIL, FAIL on a stale file read, PASS); visual screener long video 1 (PASS, 4 non-blocking fixes applied); Shorts 3 rounds (PASS on round 3); thumbnail-reviewer 1 (PASS).
- `pace:` lines left: 0. `retention:` lines: 0. End slate 10 s. 123 shots (over the 55 to 70 guide, set by the 4 to 6 s arrival rules).
- Thumbnails: A scored about 16/20 (weapon concept, dawn-gold: "3 MINUTES / WHICH WARHEAD?"), B about 14, C about 10 (grey, no number; kept as C).
- Title: "What If Russia Nuked Lithuania? The First 61 Hours" (50 chars, lint 94); runner-up "Russia vs NATO: A Nuke Hits Lithuania at Hour 61" (98) rejected as news-style. Third title is in the packager note above.
- Shorts: s1 and s2 are strike windows with their own bursts, s3 is the Kaliningrad context Short. The shorts.json windows changed after the packager note above (s2 474.6 to 514.9 s, s3 83.1 to 114.4 s). Some Shorts opening endings are setup lines rather than big payoffs.
- Risks: research rows for RAND 60 hours, Princeton phases, Norway 1995 and Crimea are single-source and were softened in the script. Brief's "72 HOURS" thumbnail number dropped because the video runs 61 hours. Engine edits: studio/shorts.py (per-shot `short` override) and the Shorts pill position in video/src/Episode.tsx. The long video has a second flash at 29.5 s.
- Hard craft rules: 9 (arrival cadence, forced 123 shots), 11 (Short label placement in vertical), 19 (two strike Shorts).
