# Packaging specialist (titles, thumbnails, description, search), 2026-11-10

## 1. Findings

**Lint of the live and scheduled pairings** (yt-package `title.py`, title plus thumbnail A lines 1 and 2):

| Ep | Title (chars) | Thumb A | Score | Issues |
|---|---|---|---|---|
| 001 | "Russia Launches a Nuclear Strike on America... What Happens Next?" (65) | 27 MINUTES / TO OMAHA | 66 | over 60; no number; The Nuclear Clock's template |
| 002 | "China Blockades Taiwan... and the First Nuke Since 1945 Is Fired" (64) | FIRST NUKE / SINCE 1945 | 62 | **duplicate on first, nuke, since, 1945** |
| 003 | "North Korea Nukes Seattle: A 26 Minute Simulation" (49) | 26 MINUTES / TO SEATTLE | 80 | **duplicate on 26, Seattle** |
| 004 | "One Warhead Hits Chicago: What 800 Kilotons Does Street by Street" (65) | 53X HIROSHIMA / OVER THE LOOP | 66 | over 60; no "nuke" or "nuclear" (search miss); 800 kt and 53X restate one fact |
| 005 | "Russia Fires One Nuclear Missile at Ukraine: The First 7 Days" (61) | 15 KILOTONS / OVER A FIELD | 66 | mobile cut "Russia Fires One Nuclear Missile at..." **loses Ukraine**; "OVER A FIELD" deflates |

Two of five pairings say the same thing twice. 002 still had the best CTR (4.55% on 396, 95% interval 2.9% to 7.1%), so this is a hypothesis; 001 (2.49% on 1,404, interval 1.8% to 3.5%) first ran on an automatic frame.

**Thumbnails against the competitor sheet** (`episodes/004-one-warhead-one-city/build/thumb_review.png`):
- Words: ours carry 7 to 10 words (two lines plus a red tag). In the phone row the tag ("WINDOWS BREAK 17 KM AWAY") is an unreadable smear. Hits: "DEFCON 1" (377K), "DOOMSDAY" (302K), "12 MINUTES TO EXTINCTION" + 3-word tag (1.81M).
- Light and size: our 004 variants measure bright 112 to 120, glow 13.7% to 19.8%; the illustrated hits 152 and 167, glow 36.8% and 48.8%. 004 A's fireball is small (its review: "glow 13.6%, near the 11% of the weakest competitor") and sits bottom right, under the duration badge.
- Sameness: 001 A and 003 A are both "N MINUTES / TO <CITY>"; 004 C "11 MINUTES TO IMPACT" and 005 B "180 SECONDS TO IMPACT" repeat it. On a daily channel page they blur together.
- 005 A shows a wheat field with no place cue, so the title must carry "Ukraine" in its first 40 characters. It does not.

**Variant testing:** `studio/pipeline.py:133` uploads only A (`pkg(ep, thumb="a")`), and A is fixed by role ("the place"), not by score. B and C need a manual Test and compare. At about 400 impressions per video a 3-way split gives about 130 per arm; telling 3% from 5% CTR needs about 1,500 per arm, and Test and compare picks by watch-time share, not CTR. One episode cannot prove a thumbnail.

**Competitor titles:** the lane's outliers lead with the searchable premise: Hindcast "What If Russia Used a Nuke Agains Ukraine? We Mapped Every Strike That Follows" (1.82M, 264x), Know Better "What If Full Nuclear War Happened? Minute by Minute" (92K, 195x), Visualiser 3D "Simulation of a Nuclear Explosion in LONDON" (879K, 155x). So does our best Short: "What One 10-Kiloton Nuke Would Do to a US Carrier Group" (1,199 views).

**Descriptions (C6):** first lines are story openers with no query words (004 "Nine fifteen on a Tuesday morning.", 005 "Day one, nine twenty in the morning."). Search: 38 views in all.

## 2. Recommendations (ranked)

**R1. Title owns who and where; thumbnail owns the number and the stake (C1, C4).** `.claude/agents/packager.md` step 2, Text bullet. Replace "Do not repeat the title." with:
> Title and thumbnail are one pairing. The title names who and where; the thumbnail gives the number and the stake. Lint each variant with `py -I <yt-package>/title.py --title "<title>" --thumb "<line1> <line2> <tag>"`: no `duplicate`, and no fact restated in other units (800 kilotons = 53X HIROSHIMA).

Proof: 004 to 010 lint clean; median 7-day CTR 5% or more.

**R2. Titles: 55 characters, place and "nuke" in the first 40 (C1, C4, C6).** `packager.md` step 1, the `title` clause. Replace "at most 70 characters, the scenario plus the stakes" with:
> at most 55 characters; the country or city AND "nuke" or "nuclear" inside the first 40 characters (the mobile cut); one number or name; preferred forms "What If <X> Nuked <Y>? <twist>" or "What One Nuke Would Do to <City>". Write 10, lint them, log the top 3 in decisions.md, ship one scoring 90 or more.

Proof: 7-day CTR and YT_SEARCH views of 004 to 010 against 001 and 002.

**R3. Slot A is the best bet, not "the place" (C1).** `thumbnail-reviewer.md` step 3, add:
> Rank the three variants by checklist score. The top one must be `id: "a"`; if it is not, swap the `id` and `image` fields in thumbs.json and rerun `package`. Only A is uploaded automatically.

Better (builder): `studio/pipeline.py:133` reads `"upload": "<id>"` from thumbs.json. Proof: A has the top score in every thumb_review.md.

**R4. Fewer, bigger words (C1).** `packager.md` step 2 Text bullet and reviewer step 2:
> Line 1 plus line 2: 4 words at most. The red tag: 3 words at most, or no tag. Never more than 7 words on the image. All readable in the phone row of thumb_review.png.

Proof: tags readable at 250 px; no-tag variants' results in the test log.

**R5. Bigger, brighter subject; one illustrated variant (C1).** Reviewer step 2:
> The subject spans at least one third of the frame height and glow is 18% or more for variant A. Keep the subject out of the bottom-right corner (duration badge). One variant per episode tries the hyper-saturated illustrated look of "DEFCON 1" / "DOOMSDAY" (brightness 140 or more, glow 30% or more).

Proof: illustrated variants win 3 or more of 7 tests.

**R6. Test every episode, judge only pooled results (C1).** `packager.md` new step 5:
> After publish, Test and compare A, B and C in Studio within one hour (manual: Bryce or a browser session; the API cannot). Log in `data/thumb_tests.md`: episode, each variant's concept, the winner and its watch-time share, 7-day CTR and impressions.

Proof rule: a concept is better only when it wins 4 of 7 tests or its pooled CTR's 95% lower bound clears 3.5% (001's upper bound). C1 counts as met at a 5% median on 2,000 or more pooled impressions.

**R7. Description first two lines carry the query (C6).** `packager.md` step 1, `description`:
> First sentence: the search question the video answers, in the words people type ("What would one nuclear bomb do to Chicago?"). Second: the promise with one number. Then the story. Log 3 target queries in decisions.md; title and first two lines contain their words. 15 tags at most.

Proof: YT_SEARCH views per video at 28 days (38 in total so far).

**R8. Repackage now (C1, C4), manual in Studio, Bryce's call** (no studio file changes):
- 005 (publishes 2026-11-12 00:00 UTC): title "What If Russia Nuked Ukraine? The First 7 Days" (46 chars, lint 98); thumb A line 2 "OVER A FIELD" changed to "FIRST SINCE NAGASAKI" (cold open), no tag; Test and compare A, B, C.
- 004 (publishes 2026-11-11): title "What One Nuke Would Do to Chicago, Street by Street" (51 chars, no word shared with 53X HIROSHIMA); Test and compare A, B, C.
- 003 (live): title "What If North Korea Nuked the West Coast?" (41 chars, lint 84) removes the Seattle and 26 repeat.
- 001, 002: leave until their 3-way tests end.

## Reviewer scored checklist (paste into `thumbnail-reviewer.md` step 2)
Each 0 to 2, total 20. PASS: 15 or more, no 0 on items 1 to 4, A scores highest.
1. Phone read: at 250 px, subject named and every word read in 1 second.
2. One subject, a third of frame height, the brightest thing; A glow 18% or more.
3. Words: lines 1 and 2 total 4 or fewer, tag 3 or fewer or none.
4. Pairing: title.py shows no `duplicate`; no fact restated in other units.
5. Curiosity gap: the thumbnail raises a question the title does not answer.
6. Truth: numbers in script.md or scenario.computed.json; weapon, count, place match.
7. Distinct concepts; one tests a new axis from data/thumb_tests.md.
8. Against the best competitor on the sheet, a viewer would pick ours.
9. Light: brightness 110 or more, orange on deep blue, bottom-right empty.
10. Fresh: A's text pattern differs from the previous two episodes' A.

## 3. Craft rules
1. Title names who and where; thumbnail gives the number and stake; no shared words.
2. Title 55 characters at most; place and "nuke" in the first 40.
3. Thumbnail: 4 words in two lines, tag 3 words or none.
4. One subject, a third of the frame, the brightest thing; bottom-right corner empty.
5. Slot A is the top-scored variant: it is the only one uploaded automatically.
6. Do not reuse the previous two episodes' thumbnail text pattern.
7. Description line 1 is the search question in the viewer's words.
8. Test and compare every long video within an hour of publish; judge only pooled results.

## 4. Skills applied and misfits
- **yt-package:** pairing rule, `title.py` on all 15 pairings and 6 proposals, 40/60 character cuts, write ten keep two. Misfits: `voice.md` (AI narration); its 3-word ceiling is stricter than the niche's hits (6 to 8 words); its no-number check ignores names.
- **yt-seo:** first two lines, 3-query test, 15 tags. Search is the smaller lever here (Shorts and browse dominate).
- **youtube-thumbnail:** two colours, one focal element, contrast, phone-width check, empty bottom-right, hook phrases. Not used: face and reference-photo parts (no face on this channel).
