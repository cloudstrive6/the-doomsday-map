# The Doomsday Map studio

YouTube channel @TheDoomsdayMap: minute-by-minute what-if simulations of nuclear war and great-power conflict on real
maps. Daily long video (11 to 14 min, 1080p60) plus three vertical Shorts cut from it. Everything here runs unattended
in GitHub Actions; there is no human approval step (owner's decision, 2026-11-05). Quality is gated by the screener
agents and the automated QC in this repo. Read this file fully before working.

## Editorial rules (hard)

- Lanes only (config/channel.yaml `lanes`): nuclear war and weapons; great-power war and flashpoints (Taiwan, Korea,
  Iran, Baltic, Arctic); EMP, infrastructure and cyber attacks on nations. Anything else: do not make it.
- Structure: real history and real data first, then a clearly labelled simulation built from published models, then
  what the world looks like after. The episode ends on the simulation's aftermath, never on a history or statistics
  chapter (viewers of 001 and 002 left at about 80% when the finale turned into history). Every scene carries a corner
  tag: REAL DATA, REAL HISTORY or SIMULATION.
- Two reputable, independent sources per fact (research.md). Single-source facts are softened ("about", "one
  estimate") or cut. Never invent a number. Never state a simulation choice as a fact.
- Blast, burn and fallout numbers come only from the scenario engine (`python -m studio scenario`), never typed by hand.
- No real casualty footage, no gore, no AI likeness of a real person, no named living individuals as victims.
  No death toll for a simulated strike unless a published study supplies it (cite the study, not us).
- Say "simulation" and "it has not happened" in the cold open, as ONE short spoken sentence (not a paragraph), and
  never over a static card. On screen, the episode `banner` ("SIMULATION · NOT REAL EVENTS", 2.5 to 3.5 s over moving
  footage) and the SIMULATION corner tag carry it. Never present a scenario as a prediction. Do not set a simulated
  crisis on a real upcoming date.
- Writing: no em-dashes anywhere (use commas, colons or "to"); absolute dates in files; spoken numbers written out in
  script.md ("twenty twenty-six", "eleven days").
- Titles may follow competitor patterns but never copy a competitor title or tag line exactly.

## Episode layout (`episodes/<NNN>-<slug>/`)

| File | Who | What |
|---|---|---|
| `brief.md` | growth-analyst / showrunner | topic, angle, why now, the hook, the thumbnail number |
| `research.md` | researcher | sections A real data, B real history, C simulation assumptions, D figures not to use; `| # | Claim | Sources |` tables with full URLs |
| `scenario.json` → `scenario.computed.json` | scenario-designer | strikes (launch, target, weapon_class, yield_kt, burst air/ground/conventional, launch_offset_min); run `python -m studio scenario <id>` |
| `script.md` | script-writer | `## Section [TAG]` headers, one paragraph = one narration unit, `[A1, C]` refs at paragraph ends (not read aloud). 1,400 to 1,800 words |
| `script_review.md` | fact-screener | PASS or FAIL with numbered issues |
| `narration/` | `python -m studio narrate <id>` then `python -m studio align <id>` | narration.wav, timing.json, words.json (word times) |
| `shotlist.py` → `episode.json` | director | Python that builds the shot list from timing; see episodes 001 and 002 as the reference implementations |
| `metadata.json` | packager | title, description with `{{CHAPTERS}}`, tags, playlist key, `synthetic_media: true` |
| `thumbs.json` | packager | three photoreal variants (place, scale, moment) with `image_prompt`, made by Gemini (`thumbimages`) and gated by the thumbnail-reviewer (`thumbcheck`); see 003 |
| `shorts.json` | packager | three windows on the episode timeline, 30 to 60 s, each ending on a payoff, two-line title band, YouTube title |
| `status.json` | `python -m studio stage` | current stage and history |

Stages, in order: idea, researched, scripted, script_approved, narrated, shotlisted, visual_approved, packaged,
rendered, qc_passed, uploaded.

## Engine commands (run from this folder)

```
python -m studio new <slug>                    # creates episodes/<NNN>-<slug>/
python -m studio stage <id> <stage> --note ".." # records a stage
python -m studio status
python -m studio scenario <id>                 # scenario.json -> scenario.computed.json (effects, flight times)
python -m studio narrate <id>                  # Google Chirp 3 HD, voice Enceladus, -14 LUFS
python -m studio align <id>                    # faster-whisper word timings snapped to pauses -> narration/words.json
python -m studio shotlist <id>                 # runs episodes/<id>/shotlist.py, stages episode.json and the Shorts, validates
python -m studio stills <id> 12s 95s ...       # renders sample frames to episodes/<id>/build/stills/ + contact.png
python -m studio package <id>                  # chapters, captions, thumbnails (thumbs.json) -> build/
python -m studio slot                          # next free publish slot
python -m studio queue                         # is another episode needed?
python -m studio notify "text"
```

Python: `python` in CI. Node scripts live in `video/` (Remotion 4, rendering on CPU with `--gl=swangle`).

## Shot list (episode.json) essentials

Schema: `video/src/scene.ts`. Shot types: globe, region, city, stamp, number, chapter, isotype, bars, timeline, radar,
text, split, endslate. Region shots support cities, rings, lines, labels, zones (polygons), ships (moving chevrons,
`sunkAt`), plume, highlight, countryLabels, and `burst` (nuclear flash: white-out then fireball glow). City shots need
`video/public/city/<slug>.json` (fetch with `node scripts/fetch-city.mjs <slug> <lon> <lat> <widthKm>`).

Rules learned on 001 and 002:
- Cut on paragraph starts (`S("p12")`) or on a spoken word (`W("p34", "detonates")`), never mid-word.
- Every shot moves (automatic drift exists for single-key cameras; avoid near-empty frames: the QC fails any still
  stretch over 4 s). Cards over ~14 s get split at a sentence.
- The opening minute (from 004, 2026-11-09; 001 and 002 lost half their viewers there on a static disclaimer card):
  no disclaimer card; no text, stamp, number or chapter card longer than 4 s in the first 60 s; something new moves
  every 3 to 5 s. Set the episode-level `banner` (`{"start", "end"}`, 2.5 to 3.5 s, optional `text` and `line`) over a
  moving globe, region or city shot while the disclaimer sentence is spoken. `python -m studio shotlist` prints
  `retention:` lines for any breach and writes them to `build/validate.txt`.
- Region views: `widthKm` is the horizontal width; a 16:9 frame shows 0.56 x that vertically. Taiwan-sized subjects
  need about 1,300 km. Keep important labels away from the right edge.
- Chapter cards overlap the first sentence of their chapter (3.5 to 4 s). The end slate starts on the spoken
  next-scenario line and runs 10 s after the last word (YouTube end screens need at least 5 s; they are placed in Studio
  over the slate's "NEXT SCENARIO" box and bottom-left, so the slate layout stays as it is). Its `title` and `line`
  name the next scenario from `data/ideas.md`, with no date or schedule promise.
- Music plan: `bed.mp3` for context chapters, `bed_tense.mp3` for the simulation chapters; the last segment runs to
  `durationSeconds` (the mix lifts the music 10 dB after the last word so the slate is not quiet). SFX: impact on
  chapter cards, whoosh before stamps, radar on radar cards, boom on each nuclear flash.
- Sun: nuclear night shots use `scenario.computed.json` `sun`.

## Shorts

Three per episode, 1080x1920, cut from the episode timeline (`shorts.json`), each 30 to 60 s, starting on a paragraph
and ending on a payoff (never a cliffhanger). Burned-in word-timed subtitles are automatic. Published the day after the
long video at 09:00, 14:00 and 19:00 New York, each description linking the long video.

## QC (blocking)

Loudness -14 LUFS (plus or minus 1) and true peak at or below -1.5 dBTP; no frozen stretch over 4 s; no black stretch
over 1 s outside chapter dips; 1920x1080 at 60 fps; subtitles never start before their first word. The final screener
looks at frames from the finished video and must PASS. `qc.json` also lists `shotlist_checks` (end slate length, music
to the end, `retention:` lines) for the screeners.

## Never

Touch `.env`, secrets or `.github/workflows`; publish or upload yourself (CI does it after QC); delete published
videos; write em-dashes.
