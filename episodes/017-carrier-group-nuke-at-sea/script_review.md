FAIL

Round 2, 2026-11-24. Checked against research.md, scenario.computed.json, CLAUDE.md and data/ideas.md. All six round 1 issues are fixed. One small must-fix remains (issue 1, a single-source claim stated flat). Everything else passes.

Passed checks:
- Engine numbers match: fireball 0.153 km radius is about 300 m across; 20 psi 0.297 km ("about three hundred meters"); 5 psi 1.459 km with area 6.7 km2 now attached to the 5 psi ring; burn 1.617 km; 1 psi 3.949 km; 284.4 km ("about two hundred and eighty"); 20.1 min flight ("twenty minutes"). Warning of twelve minutes is minute eight to minute twenty, consistent with chapter 04.
- New ring comparison (chapter 05): carrier and two neighbours at 2.5 km (outside 1.459 and 1.617, inside 3.949), supply ship at 3.5 km, far escorts at 4.33, 4.33 and 5.0 km ("four to five", outside 3.949). Geometry matches research section C. Bikini miss "more than half a kilometer" matches A23 (650 to 700 m). "A miss of one kilometer would move the whole picture" is a simulation inference, not a sourced claim, and it is framed as such.
- Baker and Able figures (A22 to A27, B1, B2), "more than twice our size" (23 kt against 10 kt), B5 (three officers, one refused, "It came close"), A7, A8, B7, A31 all match. No Section D figure appears.
- Belknap/Kennedy paragraph: 1975, off Sicily, "thirteen years" after 1962, cruiser and carrier, fire stopped a few meters from the nuclear magazine, both ships carrying nuclear weapons. I checked this against the FAS page (fas.org/blogs/security/2016/02/nuclear-weapons-at-sea/), which says exactly this. No casualty figure or hull name is spoken. Good.
- Labelling and safety: the cold open is two short sentences ("This is a simulation built from published numbers, and it has not happened." is the one disclaimer sentence), no disclaimer paragraph; no death toll ("there is no death toll in this episode"); no real date, hull, operation, country or living person; the destroyed escort and the doctrine lines are labelled assumptions.
- Style: no em-dashes or en-dashes; numbers in words; about 1,580 words with headers and refs removed, inside 1,400 to 1,800. Structure is cold open, 01 real data, 02 real history and close calls, 03 trigger, 04 minute by minute, 05 rings, 06 day after as the last chapter; nothing historical after it.
- Hook and close: the first line lands the stakes; the last line ("Nobody has decided.") is quiet and true.
- End slate: "Next on the map: Kaliningrad and the Suwalki gap, and what happens if NATO cuts off the enclave." names backlog idea 3 in data/ideas.md (items 1 and 2 are queued and in production). It promises no date or schedule.

Must fix:

1. "Thirteen years later the danger came from the ships themselves. In nineteen seventy-five a cruiser and a carrier collided off Sicily, and the fire on the cruiser stopped a few meters from its nuclear magazine. Both ships carried nuclear weapons that year." [B6]
Problem: the date and casualties in B6 come from Wikipedia, but the nuclear details (fire stopped a few meters from the magazine, both ships carried nuclear weapons) come only from the FAS/Kristensen page. Wikipedia's Belknap page does not carry them. CLAUDE.md requires a single-source fact to be softened or cut, and the script states it flat.
Fix: attribute it and soften, for example: "In nineteen seventy-five a cruiser and a carrier collided off Sicily. One nuclear-weapons analyst reports that the fire on the cruiser stopped a few meters from its nuclear magazine, and that both ships carried nuclear weapons." Keep the paragraph about this length.

Notes (style or soft, may pass as they are):

2. "the US anchored about ninety surplus and captured ships". A22 gives about 95 (93 in the same Wikipedia article); B1 says "about 90". "About ninety" is within the stated range, but "more than ninety" is safer.

3. "The ship has a seawater wash-down that sprays the deck and hull, built for fallout and fire" (A5) is single-source (Wikipedia). It is a mild technical fact and is paired with "the crew would turn it on" as a simulation choice. Optional softening: "The ship is described as having a seawater wash-down".

4. "no open source says how a hardened modern warship answers a blast like this" and "No published source gives a yield for any modern anti-ship missile" are absence claims taken from research (D3, section C). Keep the hedge "we do not say" and consider "we found no published source" for the second.

After issue 1 is fixed, this script should pass.
