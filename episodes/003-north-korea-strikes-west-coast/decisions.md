- 2026-11-05: tts.py strips BOM/whitespace from GOOGLE_TTS_API_KEY (secret had a leading BOM, caused UnicodeEncodeError)

## 2026-11-05 showrunner summary
- Rounds: script 4 (fact-screener FAIL x3, PASS on round 4); visual stills 2 (blocking label overlaps fixed); thumbnails/Shorts 3 (s3 bars/timeline card clash, then ref-tag subtitle bug).
- Engine fixes: studio/tts.py strips a leading BOM from GOOGLE_TTS_API_KEY (UnicodeEncodeError). studio/narrate.py REF regex now accepts S-refs ([A-DS]); "[.., S6, ..]" tags in two paragraphs had been read aloud and captioned. Narration regenerated and everything retimed (11.9 min, 1,484 words).
- Risks: 250 kt and 100 kt yields are labelled stress-case choices (SIPRI: no public evidence of an operational ICBM warhead). Hawaii 2018 and Guam 2017 rows are single-source, softened in script. Shared credit-line opacity (C.faint in video/src/theme.ts) is dim; left as is. Recheck news (Hwasong-20 flight, seventh nuclear test) if the upload slips. Seattle city file is 16 MB.
- Four cards had to be split to meet the 14 s rule; shot count 77.
