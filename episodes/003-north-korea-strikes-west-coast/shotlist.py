"""Director pass for episode 003: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 003-north-korea-strikes-west-coast
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
STR = {s["id"]: s for s in sc["strikes"]}
SUNAN = [STR["hs18-seattle"]["launch_lon"], STR["hs18-seattle"]["launch_lat"]]
NPYONGAN = [STR["hs18-bangor"]["launch_lon"], STR["hs18-bangor"]["launch_lat"]]
SEATTLE = [-122.3321, 47.6062]
BANGOR = [-122.7134, 47.7305]
SF = [-122.4194, 37.7749]
VAFB = [-120.572, 34.742]
GREELY = [-145.73, 63.95]
LA, CHICAGO, HONOLULU, GUAM = [-118.24, 34.05], [-87.63, 41.88], [-157.86, 21.31], [144.8, 13.5]
PUNGGYE = [129.08, 41.28]
PYONGYANG = [125.75, 39.02]
PORTLAND = [-122.68, 45.52]
USA, KOREAN_N, KOREAN_S, JAPAN, CHINA, RUSSIA = "840", "408", "410", "392", "156", "643"
HL_US = {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}
HL_NK = {"iso": KOREAN_N, "color": RED, "fill": "rgba(255,59,59,0.10)"}
PACIFIC_CAM = {"lat": 46, "lon": 180, "scale": 620}

shots = []


def add(**k):
    shots.append(k)


def off(p, dlon, dlat):
    return [round(p[0] + dlon, 4), round(p[1] + dlat, 4)]


def clock(minute):
    return f"T+{int(minute):02d}:{int(round((minute % 1) * 60)):02d}"


# scenario minute -> video time, piecewise linear anchors (chapter 05 is stretched over the narration)
ANCH = [(S("p28") + 4.0, 0.0), (S("p29") + 1.0, 1.0), (S("p30") + 1.0, 3.0), (S("p30") + 6.0, 4.0), (S("p35") - 0.5, 25.5 - 0.15), (S("p36") + 0.4, 25.5)]


def vt(minute):
    if minute <= ANCH[0][1]:
        return ANCH[0][0] + (minute - ANCH[0][1]) * 4.0
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if minute <= m1:
            return t0 + (t1 - t0) * (minute - m0) / (m1 - m0)
    return ANCH[-1][0]


def mm(t):
    """scenario minute at video time t"""
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if t <= t1:
            return max(0.0, m0 + (m1 - m0) * (t - t0) / (t1 - t0))
    return ANCH[-1][1]


def clk(t):
    return clock(mm(t))


def strike_arcs(start, ids=None, color=RED, mid_only=False):
    out = []
    for s in sc["strikes"]:
        if ids and s["id"] not in ids:
            continue
        out.append({"from": [s["launch_lon"], s["launch_lat"]], "to": [s["target_lon"], s["target_lat"]],
                    "t0": round(vt(s["launch_min"]) - start, 2), "t1": round(vt(s["impact_min"]) - start, 2), "color": color, "loft": 0.16})
    return out


def phase_clock(start):
    return dict(clock=clk(start + 0.5), clockLabel="SINCE FIRST LAUNCH")


# ================================================================== Cold open [SIMULATION]
add(id="open-seattle", type="city", start=0, end=W("p01", "mountains"), tag="SIMULATION", clock="03:05", clockLabel="PACIFIC TIME · SEATTLE", city="seattle",
    view={"center": [-122.34, 47.62], "widthKm": 24}, zoomTo={"center": [-122.34, 47.615], "widthKm": 14}, gz=SEATTLE, rings=[],
    labels=[{"at": [-122.3302, 47.6038], "text": "Downtown Seattle", "color": DIM, "t": 1}, {"at": [-122.3493, 47.6205], "text": "Space Needle", "color": DIM, "t": 2}])
add(id="open-alaska", type="region", start=W("p01", "mountains"), end=S("p02"), tag="SIMULATION", clock="02:05", clockLabel="ALASKA TIME · FORT GREELY",
    view={"center": [-148.0, 63.5], "widthKm": 2600}, zoomTo={"center": [-146.0, 63.8], "widthKm": 1400}, highlight=[HL_US],
    cities=[{"at": GREELY, "label": "Fort Greely", "color": TEAL, "kind": "base", "size": 6, "t": 0.5}, {"at": [-147.72, 64.84], "label": "Fairbanks", "kind": "dot", "t": 1}],
    labels=[{"at": [-142.5, 62.9], "text": "several tracks on a screen", "color": AMBER, "t": 3}])
add(id="open-launch", type="globe", start=S("p02"), end=S("p03"), tag="SIMULATION", clock="T+00:00", clockLabel="FIRST LAUNCH",
    camera=[{"t": 0, "lat": 42, "lon": 150, "scale": 1500}, {"t": 8, "lat": 46, "lon": 180, "scale": 640}], sun=SUN,
    highlight=[HL_NK], markers=[{"at": SUNAN, "label": "Pyongyang area", "color": RED, "kind": "base", "t": 0.5}, {"at": SEATTLE, "label": "Seattle", "color": TEAL, "kind": "dot", "t": 3}],
    arcs=[{"from": SUNAN, "to": SEATTLE, "t0": 1.5, "t1": 1.5 + 7.0, "color": RED, "loft": 0.16}], caption="About twenty-six minutes, launch to impact")
add(id="open-disclaimer", type="text", start=S("p03"), end=W("p03", "But"), tag="SIMULATION",
    lines=["A simulation", "It has not happened. No crisis on the map is real and no date is attached to it."])
add(id="open-title", type="globe", start=W("p03", "But"), end=S("p04"), tag="SIMULATION", caption="North Korea strikes the US West Coast. Minute by minute.",
    camera=[{"t": 0, "lat": 44, "lon": 165, "scale": 560}, {"t": 12, "lat": 46, "lon": -170, "scale": 600}], sun=SUN,
    highlight=[HL_NK, HL_US], arcs=[dict(a, t0=a["t0"] + 1, t1=a["t1"] + 1) for a in
                                    [{"from": SUNAN, "to": SEATTLE, "t0": 0, "t1": 10, "color": RED, "loft": 0.16}, {"from": NPYONGAN, "to": SF, "t0": 1.2, "t1": 11.2, "color": RED, "loft": 0.16}]])

# ================================================================== Chapter 01 what North Korea has [REAL DATA]
add(id="c1-card", type="chapter", start=S("p04"), end=S("p04") + 3.5, tag="REAL DATA", kicker="CHAPTER 01", title="What North Korea has")
add(id="c1-60", type="number", start=S("p04") + 3.5, end=S("p05"), tag="REAL DATA", value="ABOUT 60", countTo=60, prefix="ABOUT ", label="nuclear warheads assembled",
    sub="SIPRI Yearbook 2026 · a year earlier: about 50", color=RED, source="SIPRI Yearbook 2026; NK News; Korea JoongAng Daily")
add(id="c1-counts", type="bars", start=S("p05"), end=S("p06"), tag="REAL DATA", title="Estimates of North Korea's warheads", sub="counts disagree · none is a number the government has confirmed",
    source="SIPRI Yearbook 2026; CRS; South Korean defence minister, 2026-08-20",
    bars=[{"label": "Common estimate", "value": 50, "display": "about 50", "color": TEAL}, {"label": "SIPRI, assembled", "value": 60, "display": "about 60", "color": AMBER},
          {"label": "SIPRI, with material for more", "value": 90, "display": "about 90", "color": ORANGE}, {"label": "South Korean institute view", "value": 120, "display": "up to 120", "color": RED}])
add(id="c1-fission", type="stamp", start=S("p06"), end=S("p07"), tag="REAL DATA", text="Mostly fission", line="single-stage fission devices · only a few may be thermonuclear · SIPRI 2026", color=AMBER)
add(id="c1-tests", type="region", start=S("p07"), end=S("p08"), tag="REAL DATA", clock="2017", clockLabel="3 SEPTEMBER · LAST TEST", source="CRS; CNBC; Norsar",
    view={"center": [127.5, 40.0], "widthKm": 1100}, zoomTo={"center": [128.6, 40.8], "widthKm": 700}, highlight=[HL_NK, {"iso": KOREAN_S, "color": TEAL}, {"iso": CHINA, "color": DIM}],
    cities=[{"at": PUNGGYE, "color": RED, "kind": "target", "size": 6, "t": 0.5}, {"at": PYONGYANG, "label": "Pyongyang", "kind": "dot", "t": 1.5}],
    rings=[{"at": PUNGGYE, "km": 18, "color": RED, "t": 2.0}, {"at": PUNGGYE, "km": 36, "color": AMBER, "t": 3.0}],
    labels=[{"at": off(PUNGGYE, 0.75, 0.0), "text": "Punggye-ri · six tests", "color": WHITE, "t": 0.6}, {"at": [125.4, 41.9], "text": "yield: about 50 to 250 kt", "color": AMBER, "t": 9}])
add(id="c1-icbm", type="number", start=S("p08"), end=S("p09"), tag="REAL DATA", value="10 OR FEWER", label="intercontinental missiles, Defense Intelligence Agency, 2025",
    sub="projected up to about 50 by 2035", color=AMBER, source="DIA via Congressional Research Service")
add(id="c1-models", type="globe", start=S("p09"), end=S("p11"), tag="REAL DATA", source="CSIS Missile Threat; CRS; US Annual Threat Assessment 2026",
    caption="Hwasong-17: liquid fuel, up to 15,000 km. Hwasong-18: solid fuel, less warning.",
    camera=[{"t": 0, "lat": 46, "lon": 170, "scale": 680}, {"t": 18, "lat": 46, "lon": -175, "scale": 760}, {"t": 26, "lat": 42, "lon": -150, "scale": 900}], sun={"lat": 10, "lon": 120},
    highlight=[HL_NK, HL_US], markers=[{"at": SUNAN, "label": "Pyongyang area", "color": RED, "kind": "base", "t": 0.3}, {"at": SEATTLE, "label": "Seattle", "color": TEAL, "kind": "dot", "t": 14}, {"at": SF, "label": "San Francisco", "color": TEAL, "kind": "dot", "t": 15}],
    arcs=[{"from": SUNAN, "to": SF, "t0": 2, "t1": 12, "color": AMBER, "loft": 0.16}, {"from": NPYONGAN, "to": SEATTLE, "t0": 10, "t1": 20, "color": RED, "loft": 0.16},
          {"from": SUNAN, "to": LA, "t0": 19, "t1": 28, "color": AMBER, "loft": 0.16}])
add(id="c1-caveat", type="text", start=S("p11"), end=W("p11", "And"), tag="REAL DATA",
    lines=["The caveat", "No public evidence of an operational warhead for an intercontinental missile. SIPRI, 2026."])
add(id="c1-caveat2", type="text", start=W("p11", "And"), end=S("p12"), tag="REAL DATA", lines=["Never flown full range", "with a real warhead aboard"])

# ================================================================== Chapter 02 how long would it take [REAL HISTORY]
add(id="c2-card", type="chapter", start=S("p12"), end=S("p12") + 3.5, tag="REAL HISTORY", kicker="CHAPTER 02", title="How long would it take")
add(id="c2-hs14", type="globe", start=S("p12") + 3.5, end=S("p13"), tag="REAL HISTORY", clock="2017", clockLabel="JULY · HWASONG-14", source="UCS; The War Zone; CSIS Missile Threat",
    caption="24 days apart, two Hwasong-14 flights. The second lasted 47 minutes.",
    camera=[{"t": 0, "lat": 44, "lon": 165, "scale": 600}, {"t": 14.7, "lat": 42, "lon": -170, "scale": 680}], sun={"lat": 20, "lon": 120}, highlight=[HL_NK, HL_US],
    markers=[{"at": LA, "label": "Los Angeles", "color": AMBER, "kind": "dot", "t": 7}, {"at": CHICAGO, "label": "Chicago", "color": AMBER, "kind": "dot", "t": 8}],
    arcs=[{"from": NPYONGAN, "to": [138.5, 41.0], "t0": 1, "t1": 4, "color": AMBER, "loft": 0.5}, {"from": SUNAN, "to": LA, "t0": 6, "t1": 12, "color": DIM, "loft": 0.16, "width": 1.2},
          {"from": SUNAN, "to": CHICAGO, "t0": 6.5, "t1": 13, "color": DIM, "loft": 0.16, "width": 1.2}])
add(id="c2-flights", type="bars", start=S("p13"), end=W("p13", "In"), tag="REAL HISTORY", title="Flight time of North Korea's long-range tests", sub="minutes in the air · every one lofted",
    source="CSIS Missile Threat; UCS", bars=[{"label": "Hwasong-14 · July 2017", "value": 47, "display": "47 min", "color": AMBER}, {"label": "Hwasong-15 · November 2017", "value": 53, "display": "53 min", "color": AMBER}])
add(id="c2-hs19", type="stamp", start=W("p13", "In"), end=S("p14"), tag="REAL HISTORY", text="October 2024", line="Hwasong-19 · 86 minutes · the last long-range North Korean flight to date", color=RED)
add(id="c2-lofted", type="globe", start=S("p14"), end=S("p15"), tag="REAL HISTORY", source="CSIS Missile Threat; UCS", caption="Lofted: fired steeply upward to land near North Korea",
    camera=[{"t": 0, "lat": 42, "lon": 135, "scale": 1300}, {"t": 9.7, "lat": 42, "lon": 140, "scale": 1100}], sun={"lat": 15, "lon": 100}, highlight=[HL_NK, {"iso": JAPAN, "color": TEAL}],
    markers=[{"at": [131.5, 40.0], "label": "lands about 1,000 km away", "color": AMBER, "kind": "ring", "t": 6}],
    arcs=[{"from": NPYONGAN, "to": [131.5, 40.0], "t0": 0.5, "t1": 6, "color": AMBER, "loft": 1.0}])
add(id="c2-ucs", type="bars", start=S("p15"), end=W("p15", "Another"), tag="REAL DATA", title="Warning time on a real attack path", sub="launch to impact, minutes · Union of Concerned Scientists estimates",
    source="UCS (David Wright), 2017", bars=[{"label": "Los Angeles", "value": 38, "display": "about 38 min", "color": AMBER}, {"label": "San Francisco", "value": 33.5, "display": "about 33 to 34 min", "color": ORANGE}])
add(id="c2-honest", type="timeline", start=W("p15", "Another"), end=S("p17"), tag="REAL DATA", title="Seattle: under thirty minutes", sub="John Schilling, 38 North · so, roughly half an hour",
    total=40, unit="MIN", segments=[{"from": 0, "to": 30, "label": "Seattle, under 30 min", "color": RED}, {"from": 30, "to": 38, "label": "Los Angeles, 38", "color": AMBER}],
    highlight={"from": 0, "to": 30, "label": "roughly half an hour"}, cursorTo=30, source="UCS; 38 North")
# (p16 is only 3 s and is covered by the closing part of the timeline above)
shots[-1]["start"] = W("p15", "Another")

# ================================================================== Chapter 03 the shield [REAL DATA]
add(id="c3-card", type="chapter", start=S("p17"), end=S("p17") + 3.5, tag="REAL DATA", kicker="CHAPTER 03", title="The shield")
add(id="c3-gmd", type="region", start=S("p17") + 3.5, end=S("p18"), tag="REAL DATA", source="Arms Control Association; Defense News",
    view={"center": [-134, 52], "widthKm": 7400}, zoomTo={"center": [-134, 52], "widthKm": 7000}, highlight=[HL_US],
    cities=[{"at": GREELY, "color": TEAL, "kind": "base", "size": 7, "t": 0.5}, {"at": VAFB, "color": TEAL, "kind": "base", "size": 7, "t": 3}],
    rings=[{"at": GREELY, "km": 300, "color": TEAL, "t": 1}, {"at": VAFB, "km": 300, "color": TEAL, "t": 3.5}],
    labels=[{"at": [GREELY[0] - 1.0, GREELY[1] + 4.4], "text": "Fort Greely, Alaska · 40 interceptors", "color": TEAL, "t": 0.5}, {"at": [VAFB[0] + 0.5, VAFB[1] + 4.2], "text": "Vandenberg, California · 4", "color": TEAL, "t": 3},
            {"at": [-136, 45], "text": "Ground-based Midcourse Defense · 44 interceptors", "color": AMBER, "t": 5}])
add(id="c3-hit", type="globe", start=S("p18"), end=S("p19"), tag="REAL DATA", caption="Hit to kill: the interceptor collides with the warhead in space", source="Arms Control Association (illustration)",
    camera=[{"t": 0, "lat": 56, "lon": -165, "scale": 900}, {"t": 8, "lat": 56, "lon": -160, "scale": 1100}], sun={"lat": 10, "lon": 20}, highlight=[HL_US],
    markers=[{"at": GREELY, "label": "Fort Greely", "color": TEAL, "kind": "base", "t": 0.3}],
    arcs=[{"from": [170, 50], "to": SEATTLE, "t0": 0, "t1": 8, "color": RED, "loft": 0.25}, {"from": GREELY, "to": [-168, 54.5], "t0": 1.5, "t1": 4.6, "color": TEAL, "loft": 0.2}],
    flashes=[{"at": [-168, 54.5], "t": 4.6, "radius": 5, "hold": 2, "color": TEAL}])
add(id="c3-12of21", type="number", start=S("p19"), end=S("p20"), tag="REAL DATA", value="12 OF 21", label="scripted intercept tests succeeded",
    sub="Arms Control Association · roughly half to sixty percent", color=TEAL, source="Arms Control Association, Missile Defense factsheet")
add(id="c3-2019", type="stamp", start=S("p20"), end=W("p20", "real"), tag="REAL HISTORY", text="25 March 2019", line="first salvo: two interceptors, one target · both worked", color=TEAL)
add(id="c3-44", type="text", start=W("p20", "real"), end=S("p21"), tag="REAL DATA",
    lines=["44 interceptors is not 44 missiles stopped", "A real engagement would likely use more than one interceptor per warhead."])
add(id="c3-scripted", type="text", start=S("p21"), end=S("p22"), tag="REAL DATA", lines=["Scripted tests", "no realistic decoys, say critics"])
add(id="c3-ngi", type="stamp", start=S("p22"), end=W("p22", "Golden"), tag="REAL DATA", text="Not fielded", line="the next-generation interceptor", color=AMBER)
add(id="c3-golden", type="number", start=W("p22", "Golden"), end=S("p23"), tag="REAL DATA", value="$1.2 TRILLION", countTo=1.2, decimals=1, prefix="$", suffix=" TRILLION", label="Golden Dome over 20 years, Congressional Budget Office estimate",
    sub="a plan, not a roof", color=AMBER, source="CBO, 2026-05-12; Air & Space Forces")

# ================================================================== Chapter 04 the trigger [SIMULATION]
add(id="c4-card", type="chapter", start=S("p23"), end=S("p23") + 3.5, tag="SIMULATION", kicker="CHAPTER 04", title="The trigger")
add(id="c4-order", type="region", start=S("p23") + 3.5, end=S("p24"), tag="SIMULATION", source="CRS (North Korean law, 2013 and 2022)",
    view={"center": [126.5, 38.5], "widthKm": 700}, zoomTo={"center": [126.2, 39.2], "widthKm": 400}, highlight=[HL_NK, {"iso": KOREAN_S, "color": TEAL}],
    cities=[{"at": PYONGYANG, "label": "Pyongyang", "color": RED, "kind": "base", "size": 6, "t": 0.5}, {"at": [126.98, 37.57], "label": "Seoul", "kind": "dot", "t": 1}],
    rings=[{"at": PYONGYANG, "km": 40, "color": RED, "t": 3}], labels=[{"at": [124.3, 40.5], "text": "the final order belongs to one man", "color": AMBER, "t": 5}],
    caption="In our story, the order is given")
add(id="c4-nocause", type="text", start=S("p24"), end=W("p24", "limited"), tag="SIMULATION", lines=["No cause named", "We do not say it is likely."])
add(id="c4-six", type="number", start=W("p24", "limited"), end=W("p24", "That"), tag="SIMULATION", value="4 OF 6", label="missiles get through · two are intercepted · one warhead each",
    sub="six launched in all", color=RED)
add(id="c4-choice", type="text", start=W("p24", "That"), end=W("p24", "Six", 2), tag="SIMULATION", lines=["A choice we made", "not a forecast"])
add(id="c4-dia", type="bars", start=W("p24", "Six", 2), end=S("p25"), tag="SIMULATION", title="Six sits inside the count", sub="intercontinental missiles", source="DIA via CRS",
    bars=[{"label": "Launched in our story", "value": 6, "display": "6", "color": RED}, {"label": "Defense Intelligence Agency count", "value": 10, "display": "10 or fewer", "color": AMBER}])
add(id="c4-types", type="region", start=S("p25"), end=W("p25", "We"), tag="SIMULATION", caption="Two Hwasong-18 class and two Hwasong-17",
    view={"center": [125.0, 39.8], "widthKm": 260}, zoomTo={"center": [125.4, 39.6], "widthKm": 200}, highlight=[HL_NK],
    cities=[{"at": SUNAN, "label": "Hwasong-18 + Hwasong-17 (location simulated)", "color": RED, "kind": "base", "size": 6, "t": 0.5}, {"at": NPYONGAN, "label": "Hwasong-18 + Hwasong-17", "color": RED, "kind": "base", "size": 6, "t": 2}],
    rings=[{"at": SUNAN, "km": 10, "color": RED, "t": 1}, {"at": NPYONGAN, "km": 10, "color": RED, "t": 2.5}])
add(id="c4-hs20", type="text", start=W("p25", "We"), end=S("p26"), tag="SIMULATION", lines=["Not used: Hwasong-20", "unveiled in 2025, never flown"])
add(id="c4-targets", type="region", start=S("p26"), end=S("p27"), tag="SIMULATION", caption="Our choice of four targets",
    view={"center": [-121.6, 41.8], "widthKm": 3600}, zoomTo={"center": [-121.6, 41.8], "widthKm": 3300}, highlight=[HL_US],
    cities=[{"at": SEATTLE, "label": "Seattle", "color": RED, "kind": "target", "size": 7, "t": 1}, {"at": BANGOR, "label": None, "color": RED, "kind": "target", "size": 5, "t": 2.8},
            {"at": SF, "label": "San Francisco", "color": RED, "kind": "target", "size": 7, "t": 6}, {"at": VAFB, "label": "Vandenberg", "color": RED, "kind": "target", "size": 7, "t": 8}],
    labels=[{"at": [-118.2, 47.9], "text": "Bangor submarine base", "color": RED, "t": 2.8}])
add(id="c4-yields", type="bars", start=S("p27"), end=W("p27", "smaller"), tag="SIMULATION", title="Yield assumed, kilotons", sub="our assumption, not a fact",
    source="SIPRI; CNBC; 2017 test estimates of about 50 to 250 kt",
    bars=[{"label": "Seattle", "value": 250, "display": "250 kt", "color": RED}, {"label": "Bangor", "value": 100, "display": "100 kt", "color": ORANGE},
          {"label": "San Francisco", "value": 100, "display": "100 kt", "color": ORANGE}, {"label": "Vandenberg", "value": 100, "display": "100 kt", "color": ORANGE}])

add(id="c4-smaller", type="text", start=W("p27", "smaller"), end=S("p28"), tag="SIMULATION", lines=["A smaller weapon", "a few tens of kilotons would shrink every ring that follows"])

# ================================================================== Chapter 05 minute by minute [SIMULATION]
SITES = [{"at": SUNAN, "label": "Pyongyang area", "color": RED, "kind": "base", "t": 0.5}, {"at": NPYONGAN, "label": "North Pyongan", "color": RED, "kind": "base", "t": 0.8}]
add(id="c5-card", type="chapter", start=S("p28"), end=S("p28") + 3.5, tag="SIMULATION", kicker="CHAPTER 05", title="Minute by minute")
st = S("p28") + 3.5
add(id="c5-m0", type="globe", start=st, end=S("p29"), tag="SIMULATION", clock="T+00:00", clockLabel="FIRST LAUNCH", caption="Satellites see the heat within a minute or two",
    camera=[{"t": 0, "lat": 42, "lon": 140, "scale": 1300}, {"t": 8, "lat": 45, "lon": 160, "scale": 800}], sun=SUN, highlight=[HL_NK], markers=SITES, arcs=strike_arcs(st, ["hs18-seattle"]))
st = S("p29")
add(id="c5-m1", type="globe", start=st, end=S("p31"), tag="SIMULATION", clock=clk(st + 0.5), clockLabel="SINCE FIRST LAUNCH", caption="Minute one: a second Hwasong-18. Minute three: a Hwasong-17. Minute four: the fourth.",
    camera=[{"t": 0, "lat": 43, "lon": 150, "scale": 900}, {"t": 12, "lat": 46, "lon": 175, "scale": 620}, {"t": 26, "lat": 48, "lon": -170, "scale": 640}], sun=SUN,
    highlight=[HL_NK, HL_US], markers=SITES, arcs=strike_arcs(st))
st = S("p31")
add(id="c5-intercepts", type="globe", start=st, end=S("p32"), tag="SIMULATION", clock=clk(st + 0.5), clockLabel="SINCE FIRST LAUNCH", caption="Two more missiles launched, both destroyed. Our choice, not a forecast.",
    camera=[{"t": 0, "lat": 48, "lon": -178, "scale": 640}, {"t": 15, "lat": 50, "lon": -165, "scale": 760}], sun=SUN, highlight=[HL_US],
    arcs=strike_arcs(st) + [{"from": SUNAN, "to": [-175, 55], "t0": -2, "t1": 6.0, "color": AMBER, "loft": 0.2}, {"from": NPYONGAN, "to": [-160, 50.5], "t0": -1, "t1": 8.5, "color": AMBER, "loft": 0.2}],
    flashes=[{"at": [-175, 55], "t": 6.0, "radius": 5, "hold": 2, "color": TEAL}, {"at": [-160, 50.5], "t": 8.5, "radius": 5, "hold": 2, "color": TEAL}],
    markers=[{"at": GREELY, "label": "Fort Greely", "color": TEAL, "kind": "base", "t": 0.3}])
st = S("p32")
add(id="c5-mid", type="globe", start=st, end=W("p34", "In"), tag="SIMULATION", clock=clk(st + 0.5), clockLabel="SINCE FIRST LAUNCH",
    caption="Warheads separate and fall through space. The interceptor window opens.",
    
    camera=[{"t": 0, "lat": 52, "lon": -170, "scale": 760}, {"t": 12, "lat": 54, "lon": -155, "scale": 1000}, {"t": 23, "lat": 50, "lon": -140, "scale": 1200}], sun=SUN, highlight=[HL_US],
    markers=[{"at": GREELY, "label": "Fort Greely · 40", "color": TEAL, "kind": "base", "t": 0.3}, {"at": VAFB, "label": "Vandenberg · 4", "color": TEAL, "kind": "base", "t": 12}],
    arcs=strike_arcs(st), source="Interceptor window: simulation assumption")
add(id="c5-hawaii", type="number", start=W("p34", "In"), end=S("p35"), tag="REAL HISTORY", value="38 MIN", countTo=38, suffix=" MIN", label="a false missile alert in Hawaii stayed uncorrected",
    sub="13 January 2018 · a true alert would leave less time", color=AMBER, source="FCC; NPR")
st = S("p35")
add(id="c5-arrive", type="globe", start=st, end=S("p36"), tag="SIMULATION", clock=clk(st + 0.5), clockLabel="SINCE FIRST LAUNCH",
    camera=[{"t": 0, "lat": 50, "lon": -150, "scale": 1500}, {"t": 4, "lat": 47.6, "lon": -126, "scale": 4200}], sun=SUN,
    markers=[{"at": SEATTLE, "label": "Seattle", "color": RED, "kind": "target", "t": 0.2}], arcs=strike_arcs(st, ["hs18-seattle"]))
shots[-1]["clock"] = "T+25:30"

# ================================================================== Chapter 06 one warhead, ring by ring [SIMULATION]
FX = STR["hs18-seattle"]["effects"]
CITY_LABELS = [{"at": [-122.3302, 47.6038], "text": "Downtown Seattle", "color": WHITE}, {"at": [-122.3493, 47.6205], "text": "Space Needle", "color": DIM},
               {"at": [-122.38621, 47.67651], "text": "Ballard", "color": DIM}, {"at": [-122.2, 47.614], "text": "Bellevue", "color": DIM},
               {"at": [-122.3, 47.5], "text": "Boeing Field", "color": DIM}, {"at": [-122.62, 47.57], "text": "Bremerton", "color": DIM}]
RINGS = [{"km": FX["fireball_km"], "label": "Fireball", "color": WHITE}, {"km": FX["psi20_km"], "label": "20 psi", "color": ORANGE}, {"km": FX["psi5_km"], "label": "5 psi", "color": RED},
         {"km": FX["thermal3_km"], "label": "Third-degree burns", "color": AMBER}, {"km": FX["psi1_km"], "label": "1 psi", "color": TEAL}]
LEGEND = [{"text": f"Fireball {FX['fireball_km']*1000:.0f} m", "color": WHITE}, {"text": f"20 psi {FX['psi20_km']*1000:.0f} m", "color": ORANGE}, {"text": f"5 psi {FX['psi5_km']:.1f} km", "color": RED},
          {"text": f"Burns {FX['thermal3_km']:.1f} km", "color": AMBER}, {"text": f"1 psi {FX['psi1_km']:.1f} km", "color": TEAL}]


HIDE = [{"at": SEATTLE, "text": n, "t": 999} for n in ("First Hill", "Madrona", "Leschi", "Belltown", "Laurelhurst")]  # t far in the future: suppresses the map place label only


def rings_upto(n, new_t):
    return [dict(r, t=(-30 if i < n - 1 else new_t)) for i, r in enumerate(RINGS[:n])]


SRC = "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"
def seattle_shot(sid, pid_a, pid_b, n, w0, w1, flash=None, cl="T+25:30"):
    d = dict(id=sid, type="city", start=S(pid_a), end=S(pid_b), tag="SIMULATION", clock=cl, clockLabel="SINCE FIRST LAUNCH", source=SRC, city="seattle",
             view={"center": [-122.3321, 47.6062], "widthKm": w0}, zoomTo={"center": [-122.3321, 47.6062], "widthKm": w1}, gz=SEATTLE,
             rings=rings_upto(n, 0.6 if flash is None else flash + 0.1), labels=[CITY_LABELS[0]] + CITY_LABELS[2:2 + n] + HIDE, legend=LEGEND[:n])
    if flash is not None:
        d["flashT"] = flash
        d["labels"] = CITY_LABELS[:2]
    else:
        d["flashT"] = -30
    add(**d)


seattle_shot("c6-flash", "p36", "p37", 1, 5.0, 4.2, flash=round(W("p36", "detonates") - S("p36") + 0.1, 2))
seattle_shot("c6-fireball", "p37", "p38", 1, 4.2, 4.8)
seattle_shot("c6-20psi", "p38", "p39", 2, 5.2, 6.2)
seattle_shot("c6-5psi", "p39", "p40", 3, 14, 24)
seattle_shot("c6-burns", "p40", "p41", 4, 20, 30)
seattle_shot("c6-1psi", "p41", "p42", 5, 38, 50)
add(id="c6-fallout", type="region", start=S("p42"), end=S("p43"), tag="SIMULATION", clock="T+25:30", clockLabel="SINCE FIRST LAUNCH", caption="Airburst: little local fallout. The dust rises high; the weather decides where it falls.",
    source=SRC, view={"center": [-122.4, 47.45], "widthKm": 160}, zoomTo={"center": [-122.2, 47.4], "widthKm": 230}, highlight=[HL_US],
    cities=[{"at": SEATTLE, "color": RED, "kind": "target", "size": 6}, {"at": [-122.44, 47.25], "label": "Tacoma", "kind": "dot"}, {"at": [-122.2, 47.61], "label": "Bellevue", "kind": "dot"}],
    rings=[{"at": SEATTLE, "km": FX["psi1_km"], "color": TEAL, "t": 0.5}], labels=[{"at": [-122.33, 47.78], "text": "Seattle · 1 psi ring", "color": WHITE}])


def burst_region(sid, start, end, key, center, w, label, minute, extra=None, name=None):
    e = STR[key]["effects"]
    rings = [{"at": center, "km": e["fireball_km"], "color": WHITE, "t": 0.9, "dashed": False}, {"at": center, "km": e["psi5_km"], "color": RED, "t": 1.4, "label": "5 psi"},
             {"at": center, "km": e["thermal3_km"], "color": AMBER, "t": 1.9, "label": "Burns"}, {"at": center, "km": e["psi1_km"], "color": TEAL, "t": 2.4, "label": "1 psi"}]
    d = dict(id=sid, type="region", start=start, end=end, tag="SIMULATION", clock=clock(minute), clockLabel="SINCE FIRST LAUNCH", source=SRC, caption=label,
             view={"center": center, "widthKm": w}, zoomTo={"center": center, "widthKm": w * 1.1}, highlight=[HL_US],
             cities=[{"at": center, "color": RED, "kind": "target", "size": 5}] + (extra or []), labels=[{"at": off(center, w * 0.0026, w * 0.0016), "text": name, "color": WHITE}], rings=rings,
             burst={"at": center, "t": 0.9, "km": e["fireball_km"], "fade": 5})
    add(**d)


burst_region("c6-bangor", S("p43"), W("p43", "Four"), "hs18-bangor", BANGOR, 30, "Bangor, ground burst: heavy local fallout", STR["hs18-bangor"]["impact_min"],
             [{"at": [-122.62, 47.57], "label": "Bremerton", "kind": "dot"}], name="Bangor")
burst_region("c6-sf", W("p43", "Four"), W("p43", "Then"), "hs17-sf", SF, 36, "San Francisco, airburst, 100 kt", STR["hs17-sf"]["impact_min"],
             [{"at": [-122.27, 37.8], "label": "Oakland", "kind": "dot"}], name="San Francisco")
burst_region("c6-vafb", W("p43", "Then"), S("p44"), "hs17-vafb", VAFB, 30, "Vandenberg: the last warhead, 32 minutes after the first launch", STR["hs17-vafb"]["impact_min"],
             [{"at": [-120.43, 34.64], "label": "Lompoc", "kind": "dot"}], name="Vandenberg SFB")
add(id="c6-total", type="bars", start=S("p44"), end=S("p46"), tag="SIMULATION", title="Four warheads, 550 kilotons in all", sub="no casualty figure: no published study supports one",
    source="Scenario engine", bars=[{"label": "Seattle · air", "value": 250, "display": "250 kt", "color": RED}, {"label": "Bangor · ground", "value": 100, "display": "100 kt", "color": ORANGE},
                                   {"label": "San Francisco · air", "value": 100, "display": "100 kt", "color": ORANGE}, {"label": "Vandenberg · ground", "value": 100, "display": "100 kt", "color": ORANGE}])

# ================================================================== Chapter 07 the bill [REAL DATA]
add(id="c7-card", type="chapter", start=S("p46"), end=S("p46") + 3.5, tag="REAL DATA", kicker="CHAPTER 07", title="The bill")
add(id="c7-study0", type="stamp", start=S("p46") + 3.5, end=W("p46", "Its"), tag="REAL DATA", text="2023", line="Nagasaki University and the Nautilus Institute model a Korean nuclear war", color=AMBER)
add(id="c7-study", type="number", start=W("p46", "Its"), end=W("p46", "It"), tag="REAL DATA", value="2.1 MILLION", countTo=2.1, decimals=1, suffix=" MILLION", label="deaths within months in the largest Korea scenario",
    sub="18 weapons, China joining in", color=RED, source="RECNA and Nautilus Institute, 2023")
add(id="c7-korea", type="region", start=W("p46", "It"), end=S("p47"), tag="REAL DATA", caption="The study covers the Korean region, not this strike", source="RECNA and Nautilus Institute, 2023",
    view={"center": [127.0, 37.0], "widthKm": 1100}, highlight=[HL_NK, {"iso": KOREAN_S, "color": TEAL}, {"iso": JAPAN, "color": DIM}], cities=[{"at": PYONGYANG, "label": "Pyongyang", "kind": "dot"}, {"at": [126.98, 37.57], "label": "Seoul", "kind": "dot"}])
add(id="c7-spc0", type="stamp", start=S("p47"), end=W("p47", "between"), tag="REAL DATA", text="Strategic Posture Commission", line="2023 · North Korea \"on pace\" to deploy enough intercontinental missiles", color=AMBER)
add(id="c7-spc", type="stamp", start=W("p47", "between"), end=S("p48"), tag="REAL DATA", text="2027 to 2035", line="to potentially challenge US ground-based defences", color=RED)
add(id="c7-17", type="number", start=S("p48"), end=W("p48", "After"), tag="REAL DATA", value="17", countTo=17, label="rounds of North Korean launches in 2026, by the end of October",
    sub="all shorter range", color=RED, source="Yonhap; Korea Times")
add(id="c7-1012", type="stamp", start=W("p48", "After"), end=S("p49"), tag="REAL DATA", text="12 October 2026", line="US Indo-Pacific Command: no immediate threat", color=TEAL)
add(id="c7-third", type="region", start=S("p49"), end=S("p50"), tag="REAL DATA", caption="Congress: a third interceptor site on the East Coast by 2031", source="Arms Control Association; Defense News",
    view={"center": [-98, 42], "widthKm": 5400}, highlight=[HL_US], cities=[{"at": VAFB, "label": "Vandenberg · 4", "color": TEAL, "kind": "base", "size": 6, "t": 0.5}],
    labels=[{"at": [-88.5, 35.5], "text": "Third site, by 2031", "color": AMBER, "t": 2.5}], lines=[{"from": [-87.0, 36.2], "to": [-78.5, 39.0], "color": AMBER, "dashed": True, "t0": 2.5, "t1": 4}],
    rings=[{"at": [-77.5, 39.5], "km": 250, "color": AMBER, "t": 3, "dashed": True}])

# ================================================================== Chapter 08 when it stayed unused [REAL HISTORY]
add(id="c8-card", type="chapter", start=S("p50"), end=S("p50") + 3.5, tag="REAL HISTORY", kicker="CHAPTER 08", title="When it stayed unused")
add(id="c8-2006", type="stamp", start=S("p50") + 3.5, end=S("p51"), tag="REAL HISTORY", text="October 2006", line="first nuclear test · most analysts judged the yield below one kiloton", color=AMBER)
add(id="c8-guam", type="globe", start=S("p51"), end=S("p52"), tag="REAL HISTORY", caption="August 2017: \"fire and fury\", then a plan to fire four missiles toward Guam", source="Review-Journal; CBC",
    camera=[{"t": 0, "lat": 28, "lon": 132, "scale": 1200}, {"t": 10, "lat": 26, "lon": 138, "scale": 1000}], sun={"lat": 15, "lon": 90}, highlight=[HL_NK],
    markers=[{"at": GUAM, "label": "Guam", "color": TEAL, "kind": "base", "t": 0.5}],
    arcs=[{"from": SUNAN, "to": [GUAM[0] + dx, GUAM[1] + dy], "t0": 1 + i * 0.5, "t1": 8 + i * 0.5, "color": AMBER, "loft": 0.2} for i, (dx, dy) in enumerate(((0, 0), (1.2, 0.6), (-1.2, 0.6), (0.4, -1.2)))])
add(id="c8-ask", type="text", start=S("p52"), end=S("p53"), tag="REAL HISTORY", lines=["A test. A threat.", "Our simulation asks what an actual attack would look like."])

# ================================================================== Chapter 09 the clock [SIMULATION]
add(id="c9-card", type="chapter", start=S("p53"), end=S("p53") + 3.5, tag="SIMULATION", kicker="CHAPTER 09", title="The clock")
add(id="c9-clock", type="timeline", start=S("p53") + 3.5, end=W("p54", "Our"), tag="SIMULATION", title="Launch to last impact", sub="the window for a president to be woken, briefed and asked what to do · simulation",
    total=34, unit="MIN", segments=[{"from": 0, "to": 4, "label": "Launches", "color": RED}, {"from": 4, "to": 25.5, "label": "In flight", "color": AMBER}, {"from": 25.5, "to": 32.3, "label": "Four impacts", "color": RED}],
    highlight={"from": 0, "to": 25.5, "label": "about 26 minutes to Seattle"}, cursorTo=32.3, source="Scenario engine")
add(id="c9-stop", type="text", start=W("p54", "Our"), end=S("p55"), tag="SIMULATION", lines=["The simulation stops at the last impact", "No one can say what comes next."])
add(id="end-real", type="text", start=S("p55"), end=S("p56"), tag="REAL DATA", lines=["About sixty warheads. Forty-four interceptors.", "A flight of roughly half an hour."], size=64)
add(id="end", type="endslate", start=S("p56"), end=TOTAL + 15, tag="", title="Next scenario", line="One eight-hundred-kiloton airburst over one American city, street by street. New scenario every day.")

# ------------------------------------------------------------------ audio plan and output
flash_shots = [s for s in shots if s["id"] == "c6-flash"]
booms = [s["start"] + s["flashT"] for s in flash_shots] + [s["start"] + s["burst"]["t"] for s in shots if s["type"] == "region" and "burst" in s]
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": round(TOTAL + 15, 2),
           "musicPlan": [
               {"src": "bed.mp3", "from": 0, "to": S("p23") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p23") - 1, "to": S("p46") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p46") - 1, "to": TOTAL + 15, "loop": [2, 174], "gain_db": -17},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.4, "gain_db": -12} for s in shots if s["type"] == "radar"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": t, "gain_db": -4} for t in booms]
                    + [{"src": "boom.mp3", "t": s["start"] + f["t"], "gain_db": -14} for s in shots if s["id"] == "c5-intercepts" for f in s["flashes"]],
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
