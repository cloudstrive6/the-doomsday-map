"""Director pass for episode 004: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 004-one-warhead-one-city
"""
import json
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = json.load(open(EP / "narration" / "words.json", encoding="utf-8")) if (EP / "narration" / "words.json").exists() else []
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F"
DIM = "rgba(236,239,242,0.95)"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round((WORDS[-1]["end"] if WORDS else TOTAL) + 10, 2)


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
ST = sc["strikes"][0]
FX = ST["effects"]
SUB = [ST["launch_lon"], ST["launch_lat"]]
CHICAGO = [ST["target_lon"], ST["target_lat"]]
HIROSHIMA = [132.4536, 34.3955]
BIKINI = [165.5, 11.6]
NZEMLYA = [55.0, 73.4]
GOLDSBORO = [-78.0, 35.38]
HAVANA = [-82.37, 23.11]
MOSCOW = [37.62, 55.75]
SERPUKHOV = [37.4, 54.84]
ANDOYA = [16.13, 69.3]
USA, RUSSIA, JAPAN, CUBA, NORWAY = "840", "643", "392", "192", "578"
HL_US = {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}

shots = []


def add(**k):
    shots.append(k)


def clock(minute):
    return f"T+{int(minute):02d}:{int(round((minute % 1) * 60)):02d}"


# scenario minute -> video time (chapter 04 is stretched over the narration)
ANCH = [(S("p22") + 3.5, 0.0), (S("p24"), 5.0), (S("p25"), 8.0), (S("p26"), 9.0), (S("p27"), 10.0), (S("p28"), 11.0), (W("p28", "fires"), 11.1)]


def vt(minute):
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if minute <= m1:
            return t0 + (t1 - t0) * (minute - m0) / (m1 - m0)
    return ANCH[-1][0]


def mm(t):
    if t <= ANCH[0][0]:
        return 0.0
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if t <= t1:
            return m0 + (m1 - m0) * (t - t0) / (t1 - t0)
    return ANCH[-1][1]


def clk(t):
    return clock(mm(t))


def arc(start, color=RED, width=None):
    a = {"from": SUB, "to": CHICAGO, "t0": round(vt(0) - start, 2), "t1": round(vt(ST["impact_min"]) - start, 2), "color": color, "loft": 0.16}
    if width:
        a["width"] = width
    return [a]


# ================================================================== Cold open [SIMULATION]
# one arc over the first 13.3 s, shown across three shots
LA0, LA1 = 1.0, S("p03")


def open_arc(start):
    return [{"from": SUB, "to": CHICAGO, "t0": round(LA0 - start, 2), "t1": round(LA1 - start, 2), "color": RED, "loft": 0.16}]


T1 = 3.6
add(id="open-sub", type="globe", start=0, end=T1, tag="SIMULATION", clock="09:15", clockLabel="CENTRAL TIME · TUESDAY",
    camera=[{"t": 0, "lat": 38, "lon": -62, "scale": 1500}, {"t": T1, "lat": 40, "lon": -66, "scale": 1250}], sun=SUN, highlight=[HL_US],
    markers=[{"at": SUB, "label": "Submarine (location simulated)", "color": RED, "kind": "sub", "t": 0.3}], arcs=open_arc(0))
add(id="open-climb", type="globe", start=T1, end=S("p02"), tag="SIMULATION", clock="T+00:30", clockLabel="SINCE LAUNCH", caption="One missile. One warhead.",
    camera=[{"t": 0, "lat": 40, "lon": -66, "scale": 1250}, {"t": S("p02") - T1, "lat": 42, "lon": -72, "scale": 1050}], sun=SUN, highlight=[HL_US],
    markers=[{"at": SUB, "label": None, "color": RED, "kind": "sub", "t": 0}], arcs=open_arc(T1))
add(id="open-over", type="region", start=S("p02"), end=S("p03"), tag="SIMULATION", clock="T+02:00", clockLabel="SINCE LAUNCH", caption="Eleven minutes to the Loop",
    view={"center": [-72, 41.5], "widthKm": 3600}, zoomTo={"center": [-78, 41.5], "widthKm": 2300}, highlight=[HL_US],
    cities=[{"at": SUB, "label": "Launch (simulated)", "color": RED, "kind": "base", "size": 5, "t": 0.2}, {"at": CHICAGO, "label": "Chicago", "color": RED, "kind": "target", "size": 7, "t": 1.5}],
    lines=[{"from": SUB, "to": CHICAGO, "color": RED, "t0": 0.2, "t1": 5.2}])
add(id="open-city", type="city", start=S("p03"), end=S("p04"), tag="SIMULATION", clock="09:26", clockLabel="IN ELEVEN MINUTES", city="chicago",
    view={"center": [-87.62, 41.9], "widthKm": 40}, zoomTo={"center": [-87.635, 41.884], "widthKm": 14}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6359, 41.8789], "text": "The Loop", "color": WHITE, "t": 1.2}, {"at": [-87.6, 41.8917], "text": "Navy Pier", "color": DIM, "t": 2.0}])
add(id="open-banner", type="city", start=S("p04"), end=S("p05"), tag="SIMULATION", clock="09:26", clockLabel="IN ELEVEN MINUTES", city="chicago",
    view={"center": [-87.635, 41.884], "widthKm": 13}, zoomTo={"center": [-87.63, 41.882], "widthKm": 6}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6359, 41.8789], "text": "Willis Tower", "color": WHITE, "t": 0.5}, {"at": [-87.6233, 41.8827], "text": "Millennium Park", "color": DIM, "t": 1.8},
            {"at": [-87.6402, 41.8786], "text": "Union Station", "color": DIM, "t": 3.0}])
add(id="open-atmo", type="globe", start=S("p05"), end=W("p05", "On"), tag="SIMULATION", clock="T+05:00", clockLabel="SINCE LAUNCH", caption="Above the atmosphere",
    camera=[{"t": 0, "lat": 50, "lon": -80, "scale": 900}, {"t": 4.5, "lat": 46, "lon": -86, "scale": 1500}], sun=SUN, highlight=[HL_US],
    markers=[{"at": CHICAGO, "label": "Chicago", "color": RED, "kind": "target", "t": 0.5}],
    arcs=[{"from": SUB, "to": CHICAGO, "t0": -6, "t1": 6, "color": RED, "loft": 0.16}])
add(id="open-street", type="city", start=W("p05", "On"), end=S("p06") - 3.9, tag="SIMULATION", clock="09:20", clockLabel="CHICAGO · NOBODY KNOWS", city="chicago",
    view={"center": [-87.64, 41.878], "widthKm": 5}, zoomTo={"center": [-87.628, 41.884], "widthKm": 3.2}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6402, 41.8786], "text": "The trains run", "color": DIM, "t": 0.6}, {"at": [-87.6359, 41.8789], "text": "The offices fill", "color": WHITE, "t": 2.4}])
add(id="open-800", type="number", start=S("p06") - 3.9, end=S("p06"), tag="SIMULATION", value="800 KT", countTo=800, suffix=" KT", label="one warhead · our simulation choice", sub="on its way down", color=RED)

# ================================================================== Chapter 01 how big is one warhead [REAL DATA]
add(id="c1-card", type="chapter", start=S("p06"), end=S("p06") + 3.5, tag="REAL DATA", kicker="CHAPTER 01", title="How big is one warhead")
add(id="c1-hiro", type="city", start=S("p06") + 3.5, end=W("p07", "released"), tag="REAL HISTORY", clock="1945", clockLabel="6 AUGUST · 8:15 A.M.", source="OSTI Manhattan Project history; OpenStreetMap (modern map)", city="hiroshima",
    view={"center": HIROSHIMA, "widthKm": 50}, zoomTo={"center": HIROSHIMA, "widthKm": 22}, gz=HIROSHIMA, rings=[],
    labels=[{"at": [132.4536, 34.3955], "text": "Hiroshima", "color": WHITE, "t": 0.8}, {"at": [132.32, 34.30], "text": "Miyajima", "color": DIM, "t": 2.5}, {"at": [132.55, 34.24], "text": "Kure", "color": DIM, "t": 4}, {"at": [132.36, 34.37], "text": "a uranium bomb", "color": AMBER, "t": 5.5}])
add(id="c1-15kt", type="number", start=W("p07", "released"), end=W("p07", "Nearly"), tag="REAL HISTORY", value="15 KT", countTo=15, suffix=" KT", label="Hiroshima, about", sub="13 to 16 kt in published ranges", color=AMBER, source="OSTI; Hiroshima Committee")
add(id="c1-hirorings", type="city", start=W("p07", "Nearly"), end=W("p07", "seventy"), tag="REAL HISTORY", clock="1945", clockLabel="HIROSHIMA", source="OSTI Manhattan Project history; Hiroshima Committee", city="hiroshima",
    view={"center": HIROSHIMA, "widthKm": 14}, zoomTo={"center": HIROSHIMA, "widthKm": 56}, gz=HIROSHIMA,
    labels=[{"at": HIROSHIMA, "text": "Hiroshima", "color": WHITE, "t": 0.2}],
    rings=[{"km": 1.6, "color": RED, "label": "1 mile gone", "angle": 15, "t": 0.8}, {"km": 4.8, "color": AMBER, "label": "3 miles damaged", "angle": 120, "t": 3}, {"km": 19.3, "color": TEAL, "label": "12 miles glass broke", "angle": 258, "t": 6}], flashT=-30)
add(id="c1-70k", type="number", start=W("p07", "seventy"), end=S("p08"), tag="REAL HISTORY", value="ABOUT 70,000", countTo=70000, prefix="ABOUT ", label="died at once", sub="well over 100,000 by the end of 1945", color=RED, source="OSTI; Hiroshima Committee")
add(id="c1-53x", type="bars", start=S("p08"), end=S("p09"), tag="SIMULATION", title="Our warhead is about 53 times Hiroshima", sub="kilotons · simple arithmetic, 800 divided by 15", source="OSTI (Hiroshima); simulation choice (ours)",
    bars=[{"label": "Hiroshima, 1945", "value": 15, "display": "15 kt", "color": AMBER}, {"label": "Our warhead", "value": 800, "display": "800 kt", "color": RED}])
add(id="c1-range", type="bars", start=S("p09"), end=W("p09", "Russia's"), tag="REAL DATA", title="American warhead sizes today", sub="kilotons · no US warhead is 800 kt", source="Federation of American Scientists; Arms Control Association",
    bars=[{"label": "Smallest, about", "value": 8, "display": "8 kt", "color": TEAL}, {"label": "Largest, about", "value": 1200, "display": "1.2 Mt", "color": AMBER}, {"label": "Our simulation choice", "value": 800, "display": "800 kt", "color": RED}])
add(id="c1-russia", type="globe", start=W("p09", "Russia's"), end=S("p10"), tag="SIMULATION", caption="Among the biggest modern strategic warheads. A simulation choice.", source="Federation of American Scientists",
    camera=[{"t": 0, "lat": 55, "lon": 40, "scale": 700}, {"t": 18, "lat": 52, "lon": -30, "scale": 800}], sun={"lat": 10, "lon": 20}, highlight=[HL_US, {"iso": RUSSIA, "color": AMBER, "fill": "rgba(242,176,30,0.08)"}],
    markers=[{"at": MOSCOW, "label": "Russia: hundreds of kt on a multiple-warhead missile", "color": AMBER, "kind": "dot", "t": 1}, {"at": CHICAGO, "label": "United States: 8 kt to 1.2 Mt", "color": TEAL, "kind": "dot", "t": 8}])
add(id="c1-history", type="globe", start=S("p10"), end=W("p10", "Our"), tag="REAL HISTORY", source="US DOE; Russian Federal Nuclear Center",
    caption="Bikini Atoll, 1954: 15 Mt. Novaya Zemlya, 1961: 50 Mt.",
    camera=[{"t": 0, "lat": 14, "lon": 165, "scale": 800}, {"t": 9, "lat": 20, "lon": 130, "scale": 700}, {"t": 15, "lat": 62, "lon": 70, "scale": 760}], sun={"lat": 10, "lon": 100},
    markers=[{"at": BIKINI, "label": "Bikini Atoll · 15 Mt · 1954", "color": RED, "kind": "target", "t": 0.5}, {"at": NZEMLYA, "label": "Novaya Zemlya · 50 Mt · 1961", "color": RED, "kind": "target", "t": 12}])
add(id="c1-small", type="bars", start=W("p10", "Our"), end=S("p11"), tag="SIMULATION", title="Small by the standards of history", sub="megatons · ours is 0.8", source="US DOE; Russian Federal Nuclear Center; scenario engine",
    bars=[{"label": "Our warhead", "value": 0.8, "display": "0.8 Mt", "color": RED}, {"label": "Bikini, 1954", "value": 15, "display": "15 Mt", "color": ORANGE}, {"label": "Tsar Bomba, 1961", "value": 50, "display": "50 Mt", "color": AMBER}])
add(id="c1-12k", type="number", start=S("p11"), end=W("p11", "since"), tag="REAL DATA", value="ABOUT 12,000", countTo=12000, prefix="ABOUT ", label="nuclear warheads in the world", sub="the United States and Russia hold more than 8 in every 10",
    color=AMBER, source="SIPRI Yearbook; Federation of American Scientists")
add(id="c1-treaty", type="stamp", start=W("p11", "since"), end=S("p12"), tag="REAL DATA", text="5 February 2026", line="no treaty caps the strategic arsenals of either", color=RED, source="Arms Control Association")

# ================================================================== Chapter 02 how close it has come [REAL HISTORY]
add(id="c2-card", type="chapter", start=S("p12"), end=S("p13"), tag="REAL HISTORY", kicker="CHAPTER 02", title="How close it has come")
add(id="c2-gold0", type="stamp", start=S("p13"), end=W("p13", "Each"), tag="REAL HISTORY", text="January 1961", line="a B-52 breaks apart over North Carolina", color=AMBER, source="Sandia memo, 1969; National Security Archive")
add(id="c2-gold", type="region", start=W("p13", "Each"), end=S("p14"), tag="REAL HISTORY", clock="1961", clockLabel="GOLDSBORO, NORTH CAROLINA", source="National Security Archive; Sandia memo, 1969",
    caption="Two hydrogen bombs, each up to 3.8 megatons. One switch, a memo said.",
    view={"center": [-80, 36], "widthKm": 1500}, zoomTo={"center": GOLDSBORO, "widthKm": 500}, highlight=[HL_US],
    cities=[{"at": GOLDSBORO, "label": "Goldsboro area", "color": RED, "kind": "target", "size": 6, "t": 0.8}])
add(id="c2-cuba0", type="stamp", start=S("p14"), end=W("p14", "Officers"), tag="REAL HISTORY", text="October 1962", line="a Soviet submarine, harassed by American ships, nearly fires a nuclear torpedo", color=AMBER, source="National Security Archive")
add(id="c2-cuba", type="region", start=W("p14", "Officers"), end=S("p15"), tag="REAL HISTORY", clock="1962", clockLabel="CUBAN MISSILE CRISIS", source="National Security Archive",
    caption="Officers helped talk the captain out of it. Accounts differ on how near it was.",
    view={"center": [-74, 26], "widthKm": 3000}, zoomTo={"center": [-76, 25], "widthKm": 2200}, highlight=[{"iso": CUBA, "color": RED, "fill": "rgba(255,59,59,0.10)"}, HL_US],
    cities=[{"at": HAVANA, "label": "Cuba", "color": RED, "kind": "dot", "t": 0.5}])
add(id="c2-petrov0", type="stamp", start=S("p15"), end=W("p15", "Duty"), tag="REAL HISTORY", text="26 September 1983", line="a Soviet satellite warns of one American missile, then four more", color=AMBER, source="Arms Control Association; Wired")
add(id="c2-petrov", type="region", start=W("p15", "Duty"), end=S("p16"), tag="REAL HISTORY", clock="1983", clockLabel="SERPUKHOV-15 BUNKER", source="Arms Control Association; Wired",
    caption="Petrov judged it a false alarm: a real attack would be hundreds.",
    view={"center": [34, 56], "widthKm": 1800}, zoomTo={"center": [37, 55.5], "widthKm": 900}, highlight=[{"iso": RUSSIA, "color": AMBER, "fill": "rgba(242,176,30,0.06)"}],
    cities=[{"at": MOSCOW, "label": "Moscow", "kind": "dot", "t": 0.5}, {"at": SERPUKHOV, "label": "Serpukhov-15 (approx. location)", "color": RED, "kind": "base", "size": 6, "t": 1.2}])
add(id="c2-norway", type="region", start=S("p16"), end=S("p17"), tag="REAL HISTORY", clock="1995", clockLabel="25 JANUARY", source="Reuters; Arms Control Association",
    caption="A Norwegian science rocket, tracked by Russian radar. No order was given.",
    view={"center": [26, 64], "widthKm": 2800}, zoomTo={"center": [28, 64], "widthKm": 2200}, highlight=[{"iso": NORWAY, "color": TEAL, "fill": "rgba(62,214,200,0.08)"}, {"iso": RUSSIA, "color": AMBER, "fill": "rgba(242,176,30,0.05)"}],
    cities=[{"at": ANDOYA, "label": "Andoya, Norway", "color": TEAL, "kind": "base", "size": 6, "t": 0.5}, {"at": MOSCOW, "label": "Moscow", "kind": "dot", "t": 3}])
add(id="c2-minutes", type="text", start=S("p17"), end=S("p18"), tag="REAL HISTORY", lines=["None was a deliberate attack", "In two of them, officers had only minutes to judge a warning."])

# ================================================================== Chapter 03 the trigger [SIMULATION]
add(id="c3-card", type="chapter", start=S("p18"), end=S("p18") + 3.5, tag="SIMULATION", kicker="CHAPTER 03", title="The trigger")
add(id="c3-noplan", type="text", start=S("p18") + 3.5, end=S("p19"), tag="SIMULATION", lines=["No war plan. No crisis. No named country.", "The question is only what one warhead does, and where it stops."])
add(id="c3-weapon", type="globe", start=S("p19"), end=S("p20"), tag="SIMULATION", caption="One submarine-launched missile, about 2,700 km. Flight time: 11 minutes.", source="Scenario engine",
    camera=[{"t": 0, "lat": 40, "lon": -68, "scale": 1100}, {"t": 12, "lat": 41, "lon": -78, "scale": 1500}], sun=SUN, highlight=[HL_US],
    markers=[{"at": SUB, "label": "Atlantic (location simulated)", "color": RED, "kind": "sub", "t": 0.3}, {"at": CHICAGO, "label": "Chicago", "color": RED, "kind": "target", "t": 5}],
    arcs=[{"from": SUB, "to": CHICAGO, "t0": 1.5, "t1": 11.5, "color": RED, "loft": 0.16}])
add(id="c3-target", type="city", start=S("p20"), end=S("p21"), tag="SIMULATION", caption="The Loop, a weekday morning. Our choice, not a forecast.", source="Scenario engine; OpenStreetMap", city="chicago",
    view={"center": [-87.7, 41.88], "widthKm": 64}, zoomTo={"center": CHICAGO, "widthKm": 22}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6359, 41.8789], "text": "The Loop", "color": WHITE, "t": 0.5}, {"at": [-87.9048, 41.9742], "text": "O'Hare", "color": DIM, "t": 1.5}, {"at": [-87.5, 41.9], "text": "Lake Michigan", "color": DIM, "t": 2.5}])
add(id="c3-burst", type="split", start=S("p21"), end=S("p22"), tag="SIMULATION", left={"title": "Airburst · our choice", "sub": "blast and heat spread wider, little local fallout", "color": TEAL, "kind": "airburst"},
    right={"title": "Ground burst", "sub": "a crater and local fallout", "color": ORANGE, "kind": "groundburst"})

# ================================================================== Chapter 04 minute by minute [SIMULATION]
add(id="c4-card", type="chapter", start=S("p22"), end=S("p22") + 3.5, tag="SIMULATION", kicker="CHAPTER 04", title="Minute by minute")
st = S("p22") + 3.5
add(id="c4-m0", type="globe", start=st, end=S("p23"), tag="SIMULATION", clock="T+00:00", clockLabel="09:15 CENTRAL", caption="Minute zero. The missile leaves the water.",
    camera=[{"t": 0, "lat": 40, "lon": -58, "scale": 1300}, {"t": S("p23") - st, "lat": 41, "lon": -66, "scale": 1100}], sun=SUN, highlight=[HL_US],
    markers=[{"at": SUB, "label": "Atlantic (location simulated)", "color": RED, "kind": "sub", "t": 0.2}], arcs=arc(st))
add(id="c4-clock", type="timeline", start=S("p23"), end=W("p23", "We"), tag="SIMULATION", title="Launch to impact: 11.1 minutes", sub="the engine keeps one clock · simulation", total=12, unit="MIN",
    segments=[{"from": 0, "to": 11.1, "label": "In flight", "color": AMBER}, {"from": 11.1, "to": 12, "label": "Burst", "color": RED}], highlight={"from": 0, "to": 11.1, "label": "nothing can be changed once it starts"},
    cursorTo=11.1, source="Scenario engine")
add(id="c4-nodef", type="text", start=W("p23", "We"), end=S("p24"), tag="SIMULATION", lines=["No defence. No warning. No second missile.", "We do not model them."])
st = S("p24")
add(id="c4-m5", type="globe", start=st, end=S("p25"), tag="SIMULATION", clock=clk(st + 0.5), clockLabel="09:20 · MINUTE FIVE", caption="Above the atmosphere. Nobody in Chicago has been told.",
    camera=[{"t": 0, "lat": 52, "lon": -70, "scale": 800}, {"t": S("p25") - st, "lat": 46, "lon": -84, "scale": 1300}], sun=SUN, highlight=[HL_US],
    markers=[{"at": CHICAGO, "label": "Chicago", "color": RED, "kind": "target", "t": 1}], arcs=arc(st))
add(id="c4-m8", type="radar", start=S("p25"), end=S("p26"), tag="SIMULATION", title="Minute eight · radar track",
    lines=[{"k": "tracks", "v": "one point"}, {"k": "objects", "v": "one"}, {"k": "second wave", "v": "none"}], tracks=1, big="ONE", bigColor=RED)
shots[-1].pop("footer", None)
add(id="c4-m9a", type="city", start=S("p26"), end=W("p26", "train"), tag="SIMULATION", clock=clock(9.0), clockLabel="MINUTE NINE", city="chicago",
    view={"center": [-87.635, 41.884], "widthKm": 5}, zoomTo={"center": [-87.63, 41.882], "widthKm": 3.4}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6359, 41.8789], "text": "Nothing yet on the street", "color": WHITE, "t": 0.5}, {"at": [-87.6233, 41.8827], "text": "A delivery truck unloads", "color": DIM, "t": 2.5}])
add(id="c4-m9b", type="city", start=W("p26", "train"), end=S("p27"), tag="SIMULATION", clock=clock(9.6), clockLabel="MINUTE NINE", city="chicago",
    view={"center": [-87.6402, 41.8786], "widthKm": 3.6}, zoomTo={"center": [-87.6402, 41.8786], "widthKm": 2.4}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6402, 41.8786], "text": "A train pulls in", "color": WHITE, "t": 0.4}])
add(id="c4-m10", type="city", start=S("p27"), end=S("p28"), tag="SIMULATION", clock=clock(10.0), clockLabel="MINUTE TEN", city="chicago",
    view={"center": [-87.625, 41.88], "widthKm": 6}, zoomTo={"center": [-87.635, 41.879], "widthKm": 3.2}, gz=CHICAGO, rings=[],
    labels=[{"at": [-87.6233, 41.8827], "text": "Offices full", "color": DIM, "t": 0.8}, {"at": [-87.6359, 41.8789], "text": "Nothing left to warn anyone with", "color": WHITE, "t": 4}])
add(id="c4-m11", type="globe", start=S("p28"), end=W("p28", "The"), tag="SIMULATION", clock=clock(11.0), clockLabel="MINUTE ELEVEN · 09:26", caption="Final approach",
    camera=[{"t": 0, "lat": 44, "lon": -80, "scale": 2000}, {"t": W("p28", "The") - S("p28"), "lat": 41.9, "lon": -87.6, "scale": 6000}], sun=SUN, highlight=[HL_US],
    markers=[{"at": CHICAGO, "label": "The Loop", "color": RED, "kind": "target", "t": 0.2}], arcs=[{"from": SUB, "to": CHICAGO, "t0": -8, "t1": 3.8, "color": RED, "loft": 0.16}])

# ================================================================== Chapter 05 one warhead, ring by ring [SIMULATION]
CITY_LABELS = [{"at": [-87.6459, 41.8929], "text": "The Loop", "color": WHITE}, {"at": [-87.6, 41.8917], "text": "Navy Pier", "color": DIM},
               {"at": [-87.6167, 41.8623], "text": "Soldier Field", "color": DIM}, {"at": [-87.6742, 41.8807], "text": "United Center", "color": DIM},
               {"at": [-87.6553, 41.9484], "text": "Wrigley Field", "color": DIM}, {"at": [-87.5942, 41.7943], "text": "Hyde Park", "color": DIM},
               {"at": [-87.7524, 41.7868], "text": "Midway Airport", "color": DIM}, {"at": [-87.45, 41.88], "text": "Lake Michigan", "color": DIM}]
RINGS = [{"km": FX["fireball_km"], "label": "Fireball", "angle": 315, "color": WHITE}, {"km": FX["psi20_km"], "label": "20 psi", "angle": 135, "color": ORANGE}, {"km": FX["psi5_km"], "label": "5 psi", "angle": 45, "color": RED},
         {"km": FX["thermal3_km"], "label": "Third-degree burns", "angle": 255, "color": AMBER}, {"km": FX["psi1_km"], "label": "1 psi", "angle": 300, "color": TEAL}]
LEGEND = [{"text": f"Fireball {FX['fireball_km'] * 1000:.0f} m", "color": WHITE}, {"text": f"20 psi {FX['psi20_km'] * 1000:.0f} m", "color": ORANGE}, {"text": f"5 psi {FX['psi5_km']:.1f} km", "color": RED},
          {"text": f"Burns {FX['thermal3_km']:.1f} km", "color": AMBER}, {"text": f"1 psi {FX['psi1_km']:.1f} km", "color": TEAL}]
LABELS_BY_N = {1: [0, 1], 2: [0, 1, 2], 3: [0, 2, 3], 4: [0, 3, 4, 5], 5: [0, 4, 5, 6, 7]}
HIDE = [{"at": CHICAGO, "text": n, "t": 999} for n in ("Near North Side", "Near South Side", "Chicago Loop", "Near West Side", "Lower West Side", "Lincoln Park", "Hyde Park", "Bridgeport", "Armour Square", "Douglas", "West Town", "Oakland", "Fuller Park", "Grand Boulevard")]
SRC = "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"
CL = clock(ST["impact_min"])


def rings_upto(n, new_t):
    return [dict(r, t=(-30 if i < n - 1 else new_t)) for i, r in enumerate(RINGS[:n])]


def city_shot(sid, a, b, n, w0, w1, flash=None, extra=None, **kw):
    d = dict(id=sid, type="city", start=a, end=b, tag="SIMULATION", clock=CL, clockLabel="09:26 · BURST", source=SRC, city="chicago",
             view={"center": CHICAGO, "widthKm": w0}, zoomTo={"center": CHICAGO, "widthKm": w1}, gz=CHICAGO,
             rings=rings_upto(n, 0.6 if flash is None else flash + 0.1), labels=[CITY_LABELS[i] for i in LABELS_BY_N[n]] + HIDE, legend=LEGEND[:n], flashT=-30 if flash is None else flash)
    if flash is not None:
        d["labels"] = [CITY_LABELS[0], CITY_LABELS[1]] + HIDE
    d.update(kw)
    add(**d)


f_start = W("p28", "The")
city_shot("c5-flash", f_start, S("p30"), 1, 5.0, 4.2, flash=round(W("p28", "fires") - f_start + 0.1, 2))
city_shot("c5-fireball", S("p30"), S("p31"), 1, 4.2, 4.8)
city_shot("c5-20psi", S("p31"), S("p32"), 2, 5.2, 6.2)
city_shot("c5-5psi", S("p32"), S("p33"), 3, 14, 24)
city_shot("c5-burns", S("p33"), S("p34"), 4, 20, 30)
city_shot("c5-1psi", S("p34"), S("p35"), 5, 38, 50)
add(id="c5-grow", type="bars", start=S("p35"), end=W("p35", "That"), tag="SIMULATION", title="From the fireball to the last window", sub="radius of each ring, kilometres · nearly twenty times", source="Scenario engine",
    bars=[{"label": "Fireball", "value": FX["fireball_km"], "display": f"{FX['fireball_km']:.2f}", "color": WHITE}, {"label": "20 psi", "value": FX["psi20_km"], "display": f"{FX['psi20_km']:.2f}", "color": ORANGE},
          {"label": "5 psi", "value": FX["psi5_km"], "display": f"{FX['psi5_km']:.1f}", "color": RED}, {"label": "Third-degree burns", "value": FX["thermal3_km"], "display": f"{FX['thermal3_km']:.1f}", "color": AMBER},
          {"label": "1 psi", "value": FX["psi1_km"], "display": f"{FX['psi1_km']:.1f}", "color": TEAL}])
city_shot("c5-whole", W("p35", "That"), S("p36"), 5, 44, 56, caption="A whole city centre, then the districts around it")
HIRO = lambda km, label, col: {"km": km, "label": label, "color": col, "t": -30, "angle": 150}
add(id="c5-hiro1", type="city", start=S("p36"), end=W("p36", "Our", 2), tag="SIMULATION", clock=CL, clockLabel="COMPARE · HIROSHIMA", source=SRC + "; OSTI", city="chicago",
    view={"center": CHICAGO, "widthKm": 6}, zoomTo={"center": CHICAGO, "widthKm": 8}, gz=CHICAGO,
    rings=[HIRO(1.6, "Hiroshima: nearly everything within 1 mile", AMBER), {"km": FX["fireball_km"], "label": "Our fireball alone", "angle": 315, "color": WHITE, "t": 2.0}],
    labels=[CITY_LABELS[0]] + HIDE, legend=[{"text": "Hiroshima, 15 kt: 1.6 km", "color": AMBER}, {"text": f"Our fireball: {FX['fireball_km'] * 1000:.0f} m", "color": WHITE}], flashT=-30)
add(id="c5-hiro2", type="city", start=W("p36", "Our", 2), end=S("p37"), tag="SIMULATION", clock=CL, clockLabel="COMPARE · HIROSHIMA", source=SRC + "; OSTI", city="chicago",
    view={"center": CHICAGO, "widthKm": 16}, zoomTo={"center": CHICAGO, "widthKm": 22}, gz=CHICAGO,
    rings=[HIRO(1.6, "Hiroshima: 1 mile", AMBER), {"km": FX["psi5_km"], "label": "Our 5 psi: about 4 miles", "color": RED, "t": 1.0}], labels=[CITY_LABELS[0]] + HIDE,
    legend=[{"text": "Hiroshima, 15 kt", "color": AMBER}, {"text": f"Our 5 psi: {FX['psi5_km']:.1f} km", "color": RED}], flashT=-30)
city_shot("c5-lake", S("p37"), S("p38"), 5, 56, 60, caption="The eastern part of the larger rings lies over Lake Michigan. No count of people.")

# ================================================================== Chapter 06 the day after [SIMULATION]
add(id="c6-card", type="chapter", start=S("p38"), end=S("p39"), tag="SIMULATION", kicker="CHAPTER 06", title="The day after")
add(id="c6-plan", type="number", start=S("p39"), end=W("p39", "Researchers"), tag="REAL DATA", value="TENS OF MILLIONS", label="estimated dead in the first hours of a full US-Russia exchange",
    sub="Princeton Plan A, 2019 · 34.1 million dead, 57.4 million injured", color=AMBER, source="Princeton Science and Global Security, Plan A, 2019")
add(id="c6-food", type="number", start=W("p39", "Researchers"), end=W("p39", "That", 2), tag="REAL DATA", value="BILLIONS", label="short of food after soot from thousands of warheads",
    sub="Nature Food, 2022 · not one warhead", color=RED, source="Xia, Robock et al., Nature Food, August 2022")
add(id="c6-smallest", type="region", start=W("p39", "That", 2), end=S("p40"), tag="SIMULATION", caption="That is the far end of the scale. One warhead is the smallest case.",
    view={"center": [-96, 39], "widthKm": 5200}, zoomTo={"center": [-92, 40], "widthKm": 3200}, highlight=[HL_US],
    cities=[{"at": CHICAGO, "label": "One warhead", "color": RED, "kind": "target", "size": 7, "t": 1}], rings=[{"at": CHICAGO, "km": FX["psi1_km"], "color": TEAL, "t": 2}])
add(id="c6-wind", type="city", start=S("p40"), end=S("p41"), tag="SIMULATION", clock="DAY 1", clockLabel="AFTER THE BURST", source=SRC, caption="Wind from the west-northwest, our choice. Light fallout drifts out over the lake.",
    city="chicago", view={"center": CHICAGO, "widthKm": 44}, zoomTo={"center": [-87.45, 41.88], "widthKm": 60}, gz=CHICAGO,
    rings=[dict(RINGS[0], t=-30), dict(RINGS[4], t=-30)], labels=[CITY_LABELS[0], CITY_LABELS[7], {"at": [-87.42, 41.93], "text": "light fallout, if any, drifts east", "color": AMBER}] + HIDE, legend=[LEGEND[0], LEGEND[4]], flashT=-30)
add(id="c6-inside", type="text", start=S("p41"), end=W("p41", "Shelter"), tag="SIMULATION", lines=["Get inside. Stay inside. Stay tuned."], size=84)
add(id="c6-24h", type="number", start=W("p41", "Shelter"), end=W("p41", "Do"), tag="REAL DATA", value="24 HOURS", countTo=24, suffix=" HOURS", label="shelter, at least", sub="radiation levels drop rapidly in the first day", color=TEAL, source="Ready.gov, US government guidance")
add(id="c6-return", type="text", start=W("p41", "Do"), end=S("p42"), tag="REAL DATA", lines=["Do not return to an evacuated area", "until officials say so"], source="Ready.gov")
city_shot("c6-down", S("p42"), S("p43"), 5, 36, 44, clock="DAY 1", clockLabel="WHAT THE RINGS IMPLY", caption="Power, phones and roads would be expected to fail. Not a measured outcome.")
add(id="c6-72", type="timeline", start=S("p43"), end=S("p44"), tag="REAL DATA", title="The first 24 to 72 hours", sub="federal planning focus · outside help must reach the edge of the damage", total=96, unit="HR",
    segments=[{"from": 0, "to": 24, "label": "Shelter", "color": TEAL}, {"from": 24, "to": 72, "label": "Planning window", "color": AMBER}], highlight={"from": 24, "to": 72, "label": "help reaches the edge"},
    cursorTo=72, source="FEMA, Planning Guidance for Response to a Nuclear Detonation, 2022")
add(id="c6-beds", type="number", start=S("p44"), end=S("p45"), tag="REAL DATA", value="ABOUT 2,000", countTo=2000, prefix="ABOUT ", label="specialist burn beds in the whole United States",
    sub="no study here models how many patients one warhead would bring", color=RED, source="Klein et al., JAMA, 2009; PMC burn-centre review")
add(id="c6-country", type="region", start=S("p45"), end=W("p45", "second"), tag="SIMULATION", caption="The rest of the country is untouched by this one weapon.", clock="DAY 1", clockLabel="AFTER THE BURST",
    view={"center": [-96, 39], "widthKm": 4600}, zoomTo={"center": [-90, 41], "widthKm": 1500}, highlight=[HL_US],
    cities=[{"at": CHICAGO, "label": "The Loop", "color": RED, "kind": "target", "size": 7, "t": 0.5}], rings=[{"at": CHICAGO, "km": FX["psi1_km"], "color": TEAL, "t": 1.5}])
add(id="c6-day2", type="city", start=W("p45", "second"), end=S("p46"), tag="SIMULATION", clock="DAY 2", clockLabel="AFTER THE BURST", source=SRC, city="chicago",
    view={"center": CHICAGO, "widthKm": 14}, zoomTo={"center": CHICAGO, "widthKm": 40}, gz=CHICAGO, caption="Rubble at the centre, standing buildings at the edge. Smoke goes east over the lake.",
    rings=[dict(RINGS[0], t=-30), dict(RINGS[2], t=-30), dict(RINGS[4], t=-30)], labels=[CITY_LABELS[0], CITY_LABELS[7]] + HIDE, legend=[LEGEND[0], LEGEND[2], LEGEND[4]], flashT=-30)
city_shot("c6-last", S("p46"), S("p48"), 5, 46, 58, clock="DAY 2", clockLabel="IT HAS NOT HAPPENED", caption="Nothing in this simulation is a prediction. It has not happened.")

# ================================================================== End slate
add(id="end", type="endslate", start=S("p48"), end=END, tag="", title="Next scenario", line="Russia uses one tactical nuke in Ukraine, day by day.")

# ------------------------------------------------------------------ audio plan and output
flash_shots = [s for s in shots if s["id"] == "c5-flash"]
booms = [s["start"] + s["flashT"] for s in flash_shots]
b0 = round(W("p04", "simulation") - 0.3, 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p06") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p18") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p18") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.4, "gain_db": -12} for s in shots if s["type"] == "radar"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": t, "gain_db": -4} for t in booms],
           "attribution": "Maps: Natural Earth (public domain); OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles. Imagery: NASA Blue Marble and Black Marble. Narration: AI-generated.",
           "shots": shots}
for s in shots:
    for key in ("markers", "cities", "ships"):
        for m in s.get(key, []):
            if m.get("label") is None:
                m.pop("label", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
