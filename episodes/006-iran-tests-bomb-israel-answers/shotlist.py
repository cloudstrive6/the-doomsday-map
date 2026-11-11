"""Director pass for episode 006: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 006-iran-tests-bomb-israel-answers
No real calendar dates for the simulation; clocks are relative to the test (minute zero). The hero site is invented, so
every strike picture is a region shot (no city file); region views never go under 150 km.
"""
import json
import math
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = json.load(open(EP / "narration" / "words.json", encoding="utf-8")) if (EP / "narration" / "words.json").exists() else []
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW, BLUE = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F", "#6EA8FF"
DIM = "rgba(236,239,242,0.95)"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round((WORDS[-1]["end"] if WORDS else TOTAL) + 10, 2)


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
HERO = next(s for s in sc["strikes"] if s["id"] == "jericho-mountain")
FX = HERO["effects"]
TGT = [HERO["target_lon"], HERO["target_lat"]]       # invented test mountain, central Iran
JER = [HERO["launch_lon"], HERO["launch_lat"]]       # Jericho battery, central Israel (simulated)
NEVATIM = [34.94, 31.21]
WEST_IRAN = [47.0, 34.3]
FORDOW, NATANZ, ISFAHAN = [50.99, 34.88], [51.73, 33.72], [51.68, 32.65]
QOM, KASHAN, TEHRAN = [50.88, 34.64], [51.44, 33.98], [51.39, 35.69]
PICKAXE = [51.82, 33.64]
JERUSALEM, TELAVIV = [35.21, 31.77], [34.78, 32.08]
BAGHDAD, KIBAR = [44.4, 33.3], [40.85, 35.7]
WHITEMAN = [-93.55, 38.73]
WASH = [-77.04, 38.9]
PUNGGYE = [129.08, 41.28]
HORMUZ, DOHA = [56.5, 26.5], [51.53, 25.29]
DESERT = [55.0, 34.6]
ETZION = [34.6, 30.8]
IRAN, ISRAEL, IRAQ, SYRIA, SAUDI, QATAR, USA, NKOR, TURKEY, JORDAN, KUWAIT, UAE, OMAN, PAK = "364", "376", "368", "760", "682", "634", "840", "408", "792", "400", "414", "784", "512", "586"
HL_IRAN = {"iso": IRAN, "color": AMBER, "fill": "rgba(242,176,30,0.07)"}
HL_ISR = {"iso": ISRAEL, "color": TEAL, "fill": "rgba(62,214,200,0.12)"}
LEG = [{"text": "IRAN", "color": AMBER}, {"text": "ISRAEL", "color": TEAL}]
CL_IRAN = {"iso": IRAN, "text": "IRAN", "color": AMBER}
CL_ISR = {"iso": ISRAEL, "text": "ISRAEL", "color": TEAL}

shots = []


def add(**k):
    shots.append(k)


def rel(a, t):
    return round(max(0.1, t - a), 2)


def city(a, at, label, t, color=None, kind="dot", size=None):
    d = {"at": at, "label": label, "kind": kind, "t": rel(a, t)}
    if color:
        d["color"] = color
    if size:
        d["size"] = size
    return d


def lab(a, at, text, t, color=WHITE):
    return {"at": at, "text": text, "color": color, "t": rel(a, t)}


def missile(a, path, t0, t1, label="Jericho II", color=RED, kind="pla", t_on=None):
    return {"path": path, "t0": rel(a, t0), "t1": rel(a, t1), "kind": kind, "color": color, "label": label, "t": rel(a, t0 if t_on is None else t_on), "wake": True}


def cam(a, b, *keys):
    """keys: (absolute time or None for start/end, center, widthKm)"""
    out = []
    for t, c, w in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t) if t > 0 else 0)
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def reg(sid, a, b, keys, tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **kw)


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=a, end=round(a + dur, 2), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 2)


# ================================================================== Cold open [SIMULATION]
FLASH = round(W("p01", "bursts") - 0.12, 2)   # cut lands on the word "bursts"
reg("open-run", 0, FLASH, [("s", [43.0, 33.2], 2700), (2.0, [46.5, 33.6], 2200), ("e", [50.8, 33.9], 1500)], clock="T-00:05", clockLabel="TO IMPACT", clockRate=1.2,
    highlight=[HL_ISR, HL_IRAN], countryLabels=[CL_ISR, CL_IRAN], legend=LEG,
    cities=[city(0, JER, "Jericho battery (simulated)", 0.3, RED, "base", 5), city(0, TEHRAN, "Tehran", 1.4), city(0, TGT, "Test mountain (simulated)", 2.4, RED, "target", 7)],
    lines=[{"from": JER, "to": TGT, "color": RED, "dashed": True, "t0": 0.3, "t1": FLASH - 0.2}],
    ships=[missile(0, [JER, TGT], 0.3, FLASH, label="Jericho II", t_on=0.1)])
tF = round(FLASH, 2)
reg("open-flash", tF, S("p03"), [("s", TGT, 460), (2.2, TGT, 330), (4.4, TGT, 220), ("e", TGT, 170)], clock="04:38", clockLabel="CENTRAL IRAN · LOCAL TIME", clockRate=0,
    highlight=[HL_IRAN], burst={"at": TGT, "t": 0.1, "km": 9, "fade": 6},
    cities=[city(tF, TGT, "Ground zero (simulated)", tF + 0.8, RED, "target", 6), city(tF, KASHAN, "Kashan", tF + 2.3)],
    rings=[{"at": TGT, "km": FX["psi5_km"], "color": RED, "t": 0.6}],
    caption="A 10-kiloton ground burst on a mountain. Simulation: it has not happened.")
tL = W("p03", "It")
glob("open-launch", S("p03"), tL, [("s", 33, 40, 1500), (4.0, 33, 43, 1900), ("e", 33.2, 46, 2300)], clock="T-08:00", clockLabel="TO IMPACT", clockRate=54,
     highlight=[HL_ISR, HL_IRAN], markers=[{"at": JER, "label": "Jericho battery, central Israel (simulated)", "color": RED, "kind": "base", "size": 5, "t": rel(S("p03"), W("p03", "battery"))}],
     arcs=[{"from": JER, "to": TGT, "t0": rel(S("p03"), W("p03", "leaves")), "t1": 9.0, "color": RED, "loft": 0.12}])
reg("open-target", tL, S("p04"), [("s", [46, 33.6], 1100), (2.0, [50, 34], 650), ("e", TGT, 300)], clock="T-03:10", clockLabel="TO IMPACT", clockRate=54,
    highlight=[HL_IRAN], cities=[city(tL, TGT, "One target: a mountain in Iran", W("p03", "target"), RED, "target", 7), city(tL, KASHAN, "Kashan", tL + 2.0)],
    ships=[missile(tL, [[45.0, 33.5], TGT], tL, S("p04") - 0.3, t_on=tL)], rings=[{"at": TGT, "km": 25, "color": RED, "t": 0.6, "dashed": True}])
# p04: first test, the raid, Iran fires back, the work goes on
a = S("p04")
tS, tI, tW = W("p04", "Since"), W("p04", "Iran"), W("p04", "The")
reg("open-test", a, tS, [("s", [49, 33.8], 900), ("e", TGT, 320)], clock="HOUR 00", clockLabel="THE FIRST TEST", clockRate=0, highlight=[HL_IRAN],
    cities=[city(a, TGT, "Iran's first nuclear test (simulated)", W("p04", "hosted"), AMBER, "target", 7)],
    rings=[{"at": TGT, "km": 20, "color": AMBER, "label": "Contained", "t": rel(a, W("p04", "first")), "dashed": True}])
reg("open-raid", tS, tI, [("s", [42, 32.5], 2000), ("e", [48, 33.5], 1300)], clock="HOUR 40", clockLabel="THE RAID", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(tS, NEVATIM, "Nevatim", tS + 0.3, TEAL, "base", 5), city(tS, TGT, "Tunnel entrances", W("p04", "tunnel"), RED, "target", 6)],
    ships=[missile(tS, [NEVATIM, TGT], tS + 0.2, tI - 0.2, label="Israeli raid", color=TEAL, kind="ally")])
reg("open-fire", tI, S("p05"), [("s", [45, 33.5], 2000), (2.2, [47.5, 33.5], 1300), ("e", TGT, 420)], clock="HOUR 42", clockLabel="IRAN FIRES BACK", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    ships=[missile(tI, [WEST_IRAN, NEVATIM], tI + 0.2, tW, label="Iranian salvo", color=RED)],
    cities=[city(tI, NEVATIM, "Nevatim", tI + 0.3, TEAL, "base", 5)],
    labels=[lab(tI, [53.2, 34.9], "The work under the rock goes on", tW + 0.3, AMBER)],
    rings=[{"at": TGT, "km": 20, "color": AMBER, "t": rel(tI, tW + 0.1), "dashed": True}])
tD = W("p05", "This")
reg("q-map", S("p05"), tD, [("s", [49.5, 33.8], 650), (2.5, TGT, 300), ("e", TGT, 190)], clock="", highlight=[HL_IRAN],
    cities=[city(S("p05"), TGT, "One question", S("p05") + 0.4, WHITE, "target", 7)],
    labels=[lab(S("p05"), [52.7, 34.58], "Did the weapon reach what was buried?", W("p05", "buried"), YELLOW)])
glob("q-globe", tD, S("p06"), [("s", 31, 48, 1100), ("e", 33.5, 47, 1700)], highlight=[HL_ISR, HL_IRAN],
     markers=[{"at": TGT, "label": "The test mountain (simulated)", "color": RED, "kind": "target", "t": 0.3}, {"at": FORDOW, "label": "Fordow (real)", "color": AMBER, "kind": "dot", "t": 2.0}])

# ================================================================== Chapter 01 [REAL DATA]
a = chapter("c1-card", S("p06"), 3.5, "CHAPTER 01", "A mountain nobody can inspect", "REAL DATA")
tD1 = W("p06", "drop")
glob("c1-b2", a, tD1, [("s", 38, -96, 1000), (2.2, 40, -40, 800), ("e", 36, 20, 900)], tag="REAL DATA", clock="22 JUNE 2025", clockLabel="ABOUT 02:00, IRAN TIME", clockRate=0,
     source="US Department of Defense briefing; Reuters", highlight=[{"iso": USA, "color": BLUE, "fill": "rgba(110,168,255,0.06)"}, HL_IRAN],
     markers=[{"at": WHITEMAN, "label": "Missouri: seven B-2 bombers", "color": BLUE, "kind": "base", "t": rel(a, W("p06", "Seven"))}, {"at": FORDOW, "label": "Iran", "color": AMBER, "kind": "dot", "t": 4.0}],
     arcs=[{"from": WHITEMAN, "to": FORDOW, "t0": rel(a, W("p06", "Seven")), "t1": rel(a, tD1) + 0.5, "color": BLUE, "loft": 0.3}], caption="A round trip of 36 hours or more.")
tFo = W("p06", "Fordow")
reg("c1-bombs", tD1, tFo, [("s", [51.3, 34.0], 1100), (3.0, [51.3, 34.0], 700), ("e", [51.3, 34.0], 520)], tag="REAL DATA", clock="22 JUNE 2025", clockLabel="THE STRIKE", clockRate=0,
    source="US Department of Defense briefing; Reuters", highlight=[HL_IRAN], caption="Fourteen bombs of about 13.5 tonnes each.",
    cities=[city(tD1, [51.3, 34.3], "14 bombs, two sites", tD1 + 0.5, RED, "target", 6)], rings=[{"at": [51.3, 34.3], "km": 120, "color": RED, "t": 0.6, "dashed": True}])
tQ = W("p07", "Qom")
reg("c1-sites", tFo, W("p07", "That"), [("s", [51.3, 34.3], 520), (2.0, [51.3, 34.3], 380), (tQ, [51.0, 34.7], 240), ("e", [51.0, 34.8], 170)], tag="REAL DATA", clock="", source="IAEA; Institute for Science and International Security",
    highlight=[HL_IRAN],
    cities=[city(tFo, FORDOW, "Fordow", tFo + 0.2, AMBER, "target", 7), city(tFo, NATANZ, "Natanz", W("p06", "Natanz"), AMBER, "target", 6), city(tFo, QOM, "Qom", tQ, WHITE, "dot")],
    labels=[lab(tFo, [51.0, 35.0], "Built into a mountain, 80 to 90 m deep (reported)", W("p07", "reportedly"), WHITE)])
tT = W("p07", "That")
reg("c1-kind", tT, S("p08"), [("s", [50.99, 34.88], 200), (1.5, [51.8, 34.6], 420), ("e", TGT, 300)], tag="REAL DATA", clock="", highlight=[HL_IRAN],
    cities=[city(tT, FORDOW, "Fordow", tT + 0.2, AMBER, "target", 6), city(tT, TGT, "Test mountain (simulated, not Fordow)", W("p07", "target"), RED, "target", 6)],
    lines=[{"from": FORDOW, "to": TGT, "color": WHITE, "dashed": True, "t0": rel(tT, W("p07", "target")), "t1": rel(tT, W("p07", "target")) + 1.2}], caption="The kind of target at the end of the cold open.")
a = S("p08")
tC = W("p08", "confirmed")
reg("c1-disputed", a, W("p08", "Since"), [("s", FORDOW, 260), (2.0, FORDOW, 180), (tC, FORDOW, 150), ("e", [51.0, 34.9], 150)], tag="REAL DATA", clock="", source="IAEA statements, 2025", highlight=[HL_IRAN],
    cities=[city(a, FORDOW, "Fordow", a + 0.2, AMBER, "target", 7)],
    labels=[lab(a, [51.0, 34.99], "Damage: disputed", W("p08", "disputed"), YELLOW), lab(a, [51.0, 34.84], "IAEA: clear and significant damage", tC, WHITE), lab(a, [51.25, 34.95], "Deep halls: may be partly intact", W("p08", "deep"), RED)],
    rings=[{"at": FORDOW, "km": 15, "color": RED, "t": rel(a, W("p08", "deep")), "dashed": True}])
tSi = W("p08", "Since")
reg("c1-dark", tSi, S("p09"), [("s", [51.4, 34.0], 600), (2.4, [51.4, 33.7], 480), ("e", [51.5, 33.5], 420)], tag="REAL DATA", clock="", source="IAEA statements, 2025", highlight=[HL_IRAN],
    cities=[city(tSi, FORDOW, "Fordow", tSi + 0.2, AMBER, "target", 6), city(tSi, NATANZ, "Natanz", tSi + 0.9, AMBER, "target", 6), city(tSi, ISFAHAN, "Isfahan", tSi + 1.5, AMBER, "target", 6)],
    labels=[lab(tSi, [51.9, 34.4], "No inspector has seen inside", W("p08", "no"), YELLOW)])
# p09 numbers
add(id="c1-440", type="number", start=S("p09"), end=S("p09") + 4.2, tag="REAL DATA", value="ABOUT 440 KG", countTo=440, prefix="ABOUT ", suffix=" KG", label="of uranium enriched to 60 percent", sub="below weapons grade", color=AMBER, source="IAEA reports, 2025")
add(id="c1-stale", type="stamp", start=S("p09") + 4.2, end=W("p09", "IAEA"), tag="REAL DATA", text="MORE THAN A YEAR STALE", line="the last figure inspectors could check", color=AMBER, source="IAEA reports, 2025")
add(id="c1-ten", type="number", start=W("p09", "IAEA"), end=(W("p09", "That", 2) - 0.5), tag="REAL DATA", value="UP TO 10", label="bombs' worth, in principle", sub="IAEA chief Rafael Grossi", color=RED, source="IAEA; Reuters")
add(id="c1-notclaim", type="stamp", start=(W("p09", "That", 2) - 0.5), end=S("p10"), tag="REAL DATA", text="NOT A CLAIM THAT IRAN HAS ONE", color=WHITE, source="IAEA; Reuters")
a = S("p10")
tIn = W("p10", "In")
reg("c1-war", a, W("p10", "and", 2), [("s", [44, 32], 2800), (3.0, [46, 32.5], 2200), ("e", [47, 32.5], 1800)], tag="REAL DATA", clock="FEB 2026", clockLabel="A NEW WAR", clockRate=0, source="Reuters; Associated Press",
    highlight=[HL_ISR, HL_IRAN], legend=LEG + [{"text": "UNITED STATES", "color": BLUE}],
    cities=[city(a, [34.8, 32.0], "Israel", a + 0.4, TEAL, "base", 5), city(a, [50.5, 33.0], "Iran struck again", W("p10", "struck"), RED, "target", 7)],
    lines=[{"from": [34.8, 32.0], "to": [50.5, 33.0], "color": TEAL, "dashed": True, "t0": rel(a, W("p10", "Israel")), "t1": rel(a, W("p10", "Israel")) + 3}],
    labels=[lab(a, [48, 36.6], "The United States and Israel strike Iran", W("p10", "United"), BLUE)])
b0 = W("p10", "and", 2)
reg("c1-blockade", b0, S("p11"), [("s", [54, 27.5], 1700), (3.5, [55, 26.8], 1200), (W("p10", "What"), [45, 31], 2300), ("e", [40, 32], 2600)], tag="REAL DATA", clock="", source="Reuters; Associated Press",
    highlight=[HL_IRAN], zones=[{"points": [[50.0, 27.5], [57.5, 27.2], [58.0, 25.2], [56.0, 24.8], [51.0, 26.0]], "label": "US blockade of Iranian ports", "color": BLUE, "t": 0.5, "pulse": True}],
    ships=[{"path": [[60.5, 23.5], [57.5, 25.8]], "t0": 0.4, "t1": 4.0, "kind": "us", "label": "US Navy", "t": 0.3}],
    labels=[lab(b0, [36.0, 35.2], "What has Israel done before?", W("p10", "What"), YELLOW)])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p11"), 3.5, "CHAPTER 02", "How close, how fast", "REAL HISTORY")
reg("c2-osirak", a, S("p12"), [("s", [39, 32], 1900), (3.5, [40, 32.4], 1500), (W("p11", "Iran"), [43, 32.5], 2500), ("e", [43, 32.5], 2300)], tag="REAL HISTORY", clock="7 JUNE 1981", clockLabel="OSIRAK", clockRate=0, source="IAEA; Israeli government records",
    highlight=[HL_ISR, HL_IRAN, {"iso": IRAQ, "color": WHITE, "fill": "rgba(255,255,255,0.05)"}],
    cities=[city(a, ETZION, "Israel", a + 0.3, TEAL, "base", 5), city(a, BAGHDAD, "Osirak reactor, near Baghdad", W("p11", "Osirak"), RED, "target", 7)],
    ships=[missile(a, [ETZION, BAGHDAD], a + 1.0, W("p11", "and") + 1.0, label="Eight F-16s", color=TEAL, kind="ally")],
    rings=[{"at": ETZION, "km": 1600, "color": AMBER, "label": "1,600 km", "t": rel(a, W("p11", "sixteen")), "dashed": True}],
    labels=[lab(a, [50.0, 36.5], "Iran: about 1,600 km from Israel too", W("p11", "Iran"), AMBER)])
a = S("p12")
reg("c2-syria", a, S("p13"), [("s", [37, 33], 1500), (3.2, [40, 34.5], 900), (W("p12", "It"), [40.8, 35.7], 600), ("e", [38, 34], 1300)], tag="REAL HISTORY", clock="5 SEPT 2007", clockLabel="SYRIA", clockRate=0, source="IAEA; Israeli government statement, March 2018",
    highlight=[HL_ISR, {"iso": SYRIA, "color": WHITE, "fill": "rgba(255,255,255,0.05)"}],
    cities=[city(a, [34.9, 31.5], "Israel", a + 0.3, TEAL, "base", 5), city(a, KIBAR, "Secret reactor, half-built", W("p12", "half-built"), RED, "target", 7)],
    ships=[missile(a, [[34.9, 31.5], KIBAR], W("p12", "Israel"), W("p12", "Syria") + 1.0, label="Israeli jets", color=TEAL, kind="ally")],
    labels=[lab(a, [36.5, 37.4], "Israel said nothing for 10+ years", W("p12", "said"), YELLOW), lab(a, [36.5, 36.6], "Until March 2018", W("p12", "March"), WHITE)])
a = S("p13")
reg("c2-korea", a, W("p13", "other"), [("s", [127, 39], 1500), (3.4, PUNGGYE, 700), (W("p13", "It"), PUNGGYE, 450), ("e", PUNGGYE, 320)], tag="REAL HISTORY", clock="9 OCT 2006", clockLabel="NORTH KOREA", clockRate=0, source="US Director of National Intelligence; CTBTO",
    highlight=[{"iso": NKOR, "color": RED, "fill": "rgba(255,59,59,0.08)"}],
    cities=[city(a, PUNGGYE, "First nuclear test", W("p13", "first"), RED, "target", 7)],
    labels=[lab(a, [130.4, 42.4], "Tiny: under 1 kt (US estimate)", W("p13", "under"), YELLOW)])
tM = W("p13", "most")
add(id="c2-scale", type="bars", start=W("p13", "other"), end=S("p14"), tag="REAL HISTORY", title="The scale we use: one kiloton", sub="kilotons · North Korea 2006, published estimates", source="US Director of National Intelligence; Arms Control Association; simulation choice (ours)",
    bars=[{"label": "US intelligence chief: under", "value": 1, "display": "under 1 kt", "color": AMBER}, {"label": "Other estimates, low", "value": 0.5, "display": "0.5 kt", "color": AMBER}, {"label": "Other estimates, high", "value": 2, "display": "2 kt", "color": AMBER}, {"label": "Our simulated test", "value": 1, "display": "1 kt", "color": RED}])
a = S("p14")
tSu = W("p14", "Suppose")
reg("c2-how", a, tSu, [("s", [53, 32.5], 1500), (3.4, [53, 33], 900), (7.0, TGT, 600), ("e", TGT, 450)], tag="REAL DATA", clock="", source="One published estimate (research note A7)", highlight=[HL_IRAN],
    cities=[city(a, [51.4, 33.0], "How fast?", a + 0.3, WHITE, "target", 6)],
    labels=[lab(a, [49.2, 35.2], "Weeks: enrichment", W("p14", "weeks"), AMBER), lab(a, [49.2, 34.6], "Months: a crude device", W("p14", "months"), AMBER), lab(a, [49.2, 34.0], "A year or more: a missile warhead", W("p14", "year"), RED)])
add(id="c2-four", type="timeline", start=tSu, end=S("p15"), tag="SIMULATION", title="The first four days", sub="hours after the test · schematic", total=96, unit="h",
    segments=[{"from": 0, "to": 40, "label": "Waiting", "color": AMBER}, {"from": 40, "to": 42, "label": "Raid", "color": TEAL}, {"from": 42, "to": 96, "label": "Digging goes on", "color": AMBER}, {"from": 95, "to": 96, "label": "Jericho", "color": RED}], cursorTo=96)

# ================================================================== Chapter 03 the test [SIMULATION]
a = chapter("c3-card", S("p15"), 3.5, "CHAPTER 03", "The test", "SIMULATION")
tTh = W("p15", "Then")
reg("c3-npt", a, W("p15", "the", 3), [("s", [53, 33], 2200), (3.5, [53, 33.5], 1400), (tTh + 1.5, TGT, 700), ("e", TGT, 420)], clock="MINUTE ZERO", clockLabel="OUR ASSUMPTION", clockRate=0, highlight=[HL_IRAN],
    countryLabels=[{"iso": IRAN, "text": "IRAN LEAVES THE NPT", "color": AMBER}],
    cities=[city(a, TGT, "One deep test: 1 kt (simulated)", W("p15", "fires"), RED, "target", 7)],
    labels=[lab(a, [57.5, 29.6], "Three months' notice (treaty rule)", W("p15", "three"), WHITE)],
    rings=[{"at": TGT, "km": 30, "color": AMBER, "dashed": True, "t": rel(a, W("p15", "underground"))}])
a = W("p15", "the", 3)
reg("c3-invent", a, S("p16"), [("s", TGT, 420), (2.5, TGT, 300), ("e", TGT, 220)], clock="MINUTE ZERO", clockLabel="OUR ASSUMPTION", clockRate=0, highlight=[HL_IRAN],
    cities=[city(a, TGT, "Invented site", W("p15", "invented"), RED, "target", 7), city(a, FORDOW, "Fordow (real): not this", W("p15", "Fordow"), AMBER, "dot")],
    labels=[lab(a, [52.9, 34.08], "Not any real place", W("p15", "any"), YELLOW)])
a = S("p16")
tW = W("p16", "We")
reg("c3-zero", a, S("p17"), [("s", TGT, 500), (3.0, TGT, 340), (tW, TGT, 240), (W("p16", "On", 2), TGT, 220), (W("p16", "no", 3), TGT, 180), ("e", TGT, 160)], clock="T+00:00", clockLabel="MINUTE ZERO", clockRate=1, highlight=[HL_IRAN],
    cities=[city(a, TGT, "The test", a + 0.4, RED, "target", 7)],
    labels=[lab(a, [52.9, 34.45], "Every clock counts from here", W("p16", "every"), WHITE), lab(a, [52.9, 34.33], "No calendar date", W("p16", "calendar"), YELLOW), lab(a, [52.9, 34.2], "Test assumed contained", tW + 0.3, TEAL),
            lab(a, [52.7, 34.52], "No fireball", W("p16", "no", 2), WHITE), lab(a, [52.7, 34.42], "No fallout", W("p16", "no", 3), WHITE), lab(a, [52.7, 34.12], "No ring numbers", W("p16", "no", 4), WHITE), lab(a, [52.7, 34.02], "A deep test is not a surface burst", W("p16", "because"), YELLOW)],
    rings=[{"at": TGT, "km": 20, "color": TEAL, "dashed": True, "t": rel(a, tW + 0.3)}])
a = S("p17")
tEn = W("p17", "ended")
reg("c3-game24", a, W("p17", "An"), [("s", [43, 32], 2600), (4.5, [42, 32], 2200), (tEn + 1.5, [46, 33], 1900), ("e", [46, 33], 1700)], tag="REAL DATA", clock="2024", clockLabel="WAR GAME", clockRate=0, source="Bulletin of the Atomic Scientists, 2024",
    highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, [34.9, 31.5], "2024 war game, as reported", a + 0.4, TEAL, "base", 5), city(a, TGT, "Warhead work continues", W("p17", "warhead"), AMBER, "target", 6)],
    ships=[missile(a, [[34.9, 31.5], TGT], tEn, tEn + 3.5, label="Air strikes", color=TEAL, kind="ally")],
    labels=[lab(a, [47.0, 36.6], "Israel escalates to nuclear weapons", W("p17", "escalating"), RED)])
a = W("p17", "An")
reg("c3-game12", a, S("p18"), [("s", [42, 29], 3200), (4.0, [44, 28.5], 3000), ("e", [46, 27], 2900)], tag="REAL DATA", clock="2012", clockLabel="ISRAELI EXERCISE", clockRate=0, source="Reuters; Israeli press, 2012 reports",
    highlight=[HL_ISR, HL_IRAN, {"iso": SAUDI, "color": WHITE, "fill": "rgba(255,255,255,0.05)"}],
    cities=[city(a, [34.9, 31.5], "2012 exercise, as reported", a + 0.4, TEAL, "base", 5)],
    labels=[lab(a, [53.5, 34.8], "Iran: a test as a bargaining chip", W("p17", "Iran"), AMBER), lab(a, [44.5, 24.4], "Saudi Arabia: toward its own bomb", W("p17", "Saudi"), WHITE)])
a = S("p18")
tN = W("p18", "non-lethal")
reg("c3-demo", a, W("p18", "In", 2), [("s", [42, 32], 2400), (3.6, [52, 32.5], 1900), (tN + 1.0, [57, 31.5], 1700), (W("p18", "then") + 0.2, [49, 33], 1900), ("e", [49, 33], 1800)], tag="REAL DATA", clock="2024", clockLabel="WAR GAME", clockRate=0, source="Bulletin of the Atomic Scientists, 2024",
    highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, [34.9, 31.5], "Israel", a + 0.3, TEAL, "base", 5), city(a, [59.0, 31.0], "Remote part of Iran", W("p18", "remote"), RED, "target", 7)],
    ships=[missile(a, [[34.9, 31.5], [59.0, 31.0]], tN, tN + 3.0, label="Non-lethal demonstration", color=RED)],
    labels=[lab(a, [49.0, 35.8], "Then 25 targets struck", W("p18", "twenty-five"), YELLOW)])
a = W("p18", "In", 2)
glob("c3-pact", a, S("p19"), [("s", 35, -10, 700), (3.5, 38, -40, 800), ("e", 33, 30, 1100)], tag="REAL DATA", clock="2012", clockLabel="ISRAELI EXERCISE", clockRate=0, source="Reuters; Israeli press, 2012 reports",
     highlight=[HL_ISR, {"iso": USA, "color": BLUE, "fill": "rgba(110,168,255,0.06)"}], markers=[{"at": WASH, "label": "Defence pact with the US, weighed", "color": BLUE, "kind": "dot", "t": rel(a, W("p18", "defence"))}, {"at": [34.8, 32.0], "label": "Strike option kept", "color": TEAL, "kind": "dot", "t": rel(a, W("p18", "keeping"))}],
     arcs=[{"from": [34.8, 32.0], "to": WASH, "t0": rel(a, W("p18", "weighed")), "t1": rel(a, W("p18", "weighed")) + 3.0, "color": BLUE, "loft": 0.2}])
a = S("p19")
add(id="c3-ours", type="bars", start=a, end=W("p19", "We"), tag="SIMULATION", title="Our version is far smaller", sub="targets struck · 2024 game vs this simulation", source="Bulletin of the Atomic Scientists, 2024; our scenario",
    bars=[{"label": "2024 war game", "value": 25, "display": "25 targets", "color": AMBER}, {"label": "Our simulation", "value": 1, "display": "one site", "color": RED}])
a = W("p19", "We")
reg("c3-hours", a, S("p21"), [("s", [42, 32.5], 2500), (3.0, [47, 33.2], 1800), (W("p20", "forty"), [40, 32.5], 2800), ("e", [45, 33], 2200)], clock="HOUR 00", clockLabel="THE TEST", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, TGT, "The mountain", a + 0.4, RED, "target", 6), city(a, NEVATIM, "Nevatim", W("p19", "follow"), TEAL, "base", 5)],
    labels=[lab(a, [41.0, 36.5], "We follow the 2024 game: our choice", W("p19", "choice"), YELLOW), lab(a, [41.0, 28.2], "Israel has forty hours", W("p20", "forty"), WHITE), lab(a, [50.0, 29.5], "And one problem", W("p20", "one"), RED)])

# ================================================================== Chapter 04 hour forty to day four [SIMULATION]
a = chapter("c4-card", S("p21"), 3.5, "CHAPTER 04", "Hour forty to day four", "SIMULATION")
tA = W("p21", "Another")
reg("c4-raid", a, S("p22"), [("s", [37, 31.8], 900), (3.0, [42, 32.5], 1900), (tA, [46, 32.5], 2200), ("e", [47.5, 33], 2000)], clock="HOUR 40", clockLabel="THE RAID", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, NEVATIM, "Nevatim air base", W("p21", "Nevatim"), TEAL, "base", 6), city(a, TGT, "Test mountain: 1,684 km, 112 min", W("p21", "sixteen"), RED, "target", 6), city(a, ISFAHAN, "Isfahan tunnels: 1,586 km, 106 min", W("p21", "Isfahan"), RED, "target", 6)],
    lines=[{"from": NEVATIM, "to": TGT, "color": TEAL, "dashed": True, "t0": rel(a, W("p21", "One")), "t1": rel(a, W("p21", "One")) + 2.5}, {"from": NEVATIM, "to": ISFAHAN, "color": TEAL, "dashed": True, "t0": rel(a, tA), "t1": rel(a, tA) + 2.5}],
    ships=[missile(a, [NEVATIM, TGT], a + 0.4, tA + 3.5, label="F-15I", color=TEAL, kind="ally"), missile(a, [NEVATIM, ISFAHAN], tA, tA + 4.5, label="F-15I", color=TEAL, kind="ally")])
a = S("p22")
tAt = W("p22", "At")
glob("c4-bombs", a, tAt, [("s", 33, 35, 900), (3.8, 40, -10, 650), (W("p22", "America"), 38, -40, 650), ("e", 36, 15, 800)], clock="HOUR 40", clockLabel="WHAT ISRAEL HAS", clockRate=0, highlight=[HL_ISR, {"iso": USA, "color": BLUE, "fill": "rgba(110,168,255,0.06)"}, HL_IRAN],
     markers=[{"at": NEVATIM, "label": "Israel: bunker busters", "color": TEAL, "kind": "base", "t": 0.4}, {"at": WHITEMAN, "label": "US: 13.5 t bomb and B-2", "color": BLUE, "kind": "base", "t": rel(a, W("p22", "America"))}, {"at": FORDOW, "label": "Fordow", "color": AMBER, "kind": "target", "t": rel(a, W("p22", "Fordow"))}],
     arcs=[{"from": WHITEMAN, "to": FORDOW, "t0": rel(a, W("p22", "America")), "t1": rel(a, W("p22", "America")) + 4.0, "color": BLUE, "loft": 0.3}], caption="Israel does not own that bomb, or the B-2 that carries it.")
tEn = W("p22", "Israel's")
reg("c4-entrances", tAt, S("p23"), [("s", ISFAHAN, 400), (3.0, ISFAHAN, 250), (W("p22", "so"), ISFAHAN, 170), (tEn - 0.5, ISFAHAN, 150), (tEn + 0.4, [52.2, 33.6], 500), ("e", TGT, 160)], tag="REAL DATA", clock="", source="IAEA; Institute for Science and International Security", highlight=[HL_IRAN],
    labels=[lab(tAt, [51.9, 32.9], "Storage tunnels: too deep for even that bomb", W("p22", "storage"), WHITE), lab(tAt, [51.9, 32.45], "So the strikes went for the entrances", W("p22", "strikes"), RED), lab(tAt, [52.75, 34.45], "Israel's aim: the entrances", tEn + 0.5, TEAL), lab(tAt, [52.75, 34.12], "Not the halls below", W("p22", "halls"), RED)],
    cities=[city(tAt, ISFAHAN, "Isfahan, 2025", tAt + 0.3, AMBER, "target", 7), city(tAt, TGT, "Our site", tEn + 0.4, RED, "target", 6)])
a = S("p23")
tF2 = W("p23", "fires")
reg("c4-salvo", a, W("p23", "in", 2), [("s", [44, 32.8], 2200), (3.0, [44, 33], 2000), (W("p23", "twelve"), [41, 32.5], 1500), ("e", [38, 32], 1100)], clock="HOUR 42", clockLabel="THE RAIDS LAND", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, TGT, "Raid lands", a + 0.4, RED, "target", 6), city(a, ISFAHAN, "Raid lands", a + 0.9, RED, "target", 6), city(a, NEVATIM, "Nevatim", tF2 + 0.3, TEAL, "base", 6)],
    ships=[missile(a, [WEST_IRAN, NEVATIM], W("p23", "One"), W("p23", "away") + 0.3, label="One missile = a salvo", color=RED)],
    labels=[lab(a, [47.0, 35.9], "Iran fires back", tF2, YELLOW), lab(a, [41.0, 29.0], "About 1,200 km, 6.5 minutes", W("p23", "twelve"), WHITE)])
a = W("p23", "in", 2)
add(id="c4-550", type="number", start=a, end=W("p23", "and", 3), tag="REAL DATA", value="ABOUT 550", countTo=550, prefix="ABOUT ", label="Iranian missiles, June 2025", color=RED, source="Israeli military statements; Reuters")
add(id="c4-nine", type="isotype", start=W("p23", "and", 3), end=S("p24"), tag="REAL DATA", headline="ABOUT NINE IN TEN INTERCEPTED", label="Iranian missiles, June 2025", total=10, filled=9, per="by Israel's count", color=TEAL, source="Israeli military statements; Reuters")
a = S("p24")
reg("c4-digging", a, S("p25"), [("s", [47, 33.5], 1400), (3.0, TGT, 600), (W("p24", "the", 3), TGT, 280), ("e", TGT, 170)], clock="HOUR 42 TO DAY 4", clockLabel="MORE THAN TWO DAYS", clockRate=0, highlight=[HL_IRAN],
    cities=[city(a, TGT, "Entrances hit, work goes on", W("p24", "raids"), RED, "target", 6)],
    zones=[{"points": [[52.3, 34.1], [52.9, 34.1], [52.9, 34.5], [52.3, 34.5]], "label": "The digging goes on", "color": AMBER, "t": rel(a, W("p24", "digging")), "pulse": True}],
    labels=[lab(a, [51.5, 35.3], "As in the 2024 game", W("p24", "as"), WHITE), lab(a, [53.7, 33.7], "And so does the warhead", W("p24", "warhead"), RED)])
a = S("p25")
tOne = W("p25", "One")
reg("c4-cabinet", a, tOne, [("s", JERUSALEM, 400), (3.5, [38, 32.5], 1300), (W("p25", "buried"), [47, 33.3], 1700), ("e", [49, 33.4], 1500)], clock="DAY 4", clockLabel="OUR SCENARIO", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, JERUSALEM, "Israel's cabinet decides", W("p25", "cabinet"), TEAL, "base", 7), city(a, TGT, "A buried target", W("p25", "buried"), RED, "target", 6)],
    labels=[lab(a, [36.5, 33.9], "Only a nuclear weapon addresses it", W("p25", "nuclear"), YELLOW)])
tFl = W("p25", "flies")
reg("c4-jericho", tOne, S("p26"), [("s", [38, 32], 1500), (3.0, [40, 32.5], 1900), (tFl, [43, 33], 2500), (W("p25", "Israel"), [45, 33.5], 2400), ("e", [47, 33.3], 2100)], clock="T+00:00", clockLabel="MINUTES AFTER LAUNCH", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(tOne, JER, "Jericho II battery (simulated)", W("p25", "Jericho"), RED, "base", 6), city(tOne, TGT, "Test mountain", tFl, RED, "target", 6)],
    rings=[{"at": JER, "km": 1500, "color": AMBER, "label": "1,500 km or more", "dashed": True, "t": rel(tOne, W("p25", "fifteen"))}],
    ships=[missile(tOne, [JER, TGT], tFl, W("p25", "Israel") - 0.2, label="Jericho II", color=RED)],
    labels=[lab(tOne, [41.0, 36.3], "1,670 km in eight minutes", W("p25", "sixteen"), WHITE), lab(tOne, [44.0, 30.6], "Israel has never confirmed its arsenal", W("p25", "never"), TEAL), lab(tOne, [47.0, 30.0], "10 kt: entirely our assumption", W("p25", "ten-kiloton"), RED)])
a = S("p26")
reg("c4-clock", a, S("p27"), [("s", [38, 32], 2000), (3.0, [44, 33], 2300), ("e", [48, 33.3], 1700)], clock="HOUR 96", clockLabel="THE LAUNCH", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, JER, "Launch: hour 96", a + 0.3, RED, "base", 6), city(a, TGT, "Test mountain", a + 1.2, RED, "target", 6)],
    ships=[missile(a, [JER, TGT], W("p26", "and"), S("p27") - 0.3, label="Jericho II", color=RED)],
    labels=[lab(a, [41.0, 36.3], "96 hours after the test", W("p26", "ninety-six"), WHITE), lab(a, [44.5, 29.5], "Flight: eight minutes", W("p26", "eight"), WHITE), lab(a, [41.0, 28.4], "The clock from the cold open", W("p26", "clock"), YELLOW)])
add(id="c4-eleven", type="bars", start=S("p27"), end=S("p28"), tag="SIMULATION", title="Two nuclear events, eleven kilotons together", sub="kilotons · no other nuclear weapon is used", source="Scenario engine",
    bars=[{"label": "Test, hour 0", "value": 1, "display": "1 kt", "color": AMBER}, {"label": "Jericho, hour 96", "value": 10, "display": "10 kt", "color": RED}, {"label": "Total", "value": 11, "display": "11 kt", "color": WHITE}])
reg("c4-what", S("p28"), S("p29"), [("s", [49, 33.5], 700), (1.8, TGT, 350), ("e", TGT, 220)], clock="T+00:07", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_IRAN],
    cities=[city(S("p28"), TGT, "What does ten kilotons do to a mountain?", S("p28") + 0.3, RED, "target", 7)])

# ================================================================== Chapter 05 one warhead, ring by ring [SIMULATION]
tC5 = S("p29") + 2.6
chapter("c5-card", S("p29"), 2.6, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
RINGS = [("Fireball", FX["fireball_km"], WHITE, f"Fireball {FX['fireball_km'] * 1000:.0f} m radius"), ("20 psi", FX["psi20_km"], ORANGE, f"20 psi {FX['psi20_km'] * 1000:.0f} m"), ("5 psi", FX["psi5_km"], RED, f"5 psi {FX['psi5_km']:.2f} km"),
         ("Burns", FX["thermal3_km"], AMBER, f"Third-degree burns {FX['thermal3_km']:.1f} km"), ("1 psi", FX["psi1_km"], TEAL, f"Broken windows {FX['psi1_km']:.1f} km")]
LEGEND = [{"text": r[3], "color": r[2]} for r in RINGS]
CLK = "T+08:00"
HC = {"clock": CLK, "clockLabel": "IMPACT · T+96 H", "clockRate": 0, "source": "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)", "highlight": [HL_IRAN]}


def rg(n, t0=-30):
    out = []
    for i, (nm, km, col, _) in enumerate(RINGS[:n]):
        out.append({"at": TGT, "km": km, "color": col, "label": nm if i < n - 1 else nm, "t": t0 if i < n - 1 else t0})
    return out


def ring_at(i, t):
    nm, km, col, _ = RINGS[i]
    return {"at": TGT, "km": km, "color": col, "label": nm, "t": t}


def prior(n):
    return [dict(ring_at(i, -30)) for i in range(n)]


# H1 flash
a = tC5
tEng = W("p29", "Every")
reg("h-flash", a, S("p30"), [("s", TGT, 150), (3.5, [52.62, 34.31], 150), (tEng, [52.6, 34.3], 150), ("e", [52.6, 34.28], 150)], burst={"at": TGT, "t": 0.1, "km": 3.0, "fade": 8}, clock=CLK, clockLabel="IMPACT · T+96 H", clockRate=0,
    source=HC["source"], highlight=[HL_IRAN],
    cities=[city(a, TGT, "Ground zero (simulated)", a + 0.5, RED, "target", 6)],
    labels=[lab(a, [52.62, 34.37], "Ground burst: our choice", W("p29", "ground"), WHITE), lab(a, [52.62, 34.24], "The engine offers air or ground only", W("p29", "engine"), DIM), lab(a, [52.62, 34.31], "Every number here is the engine's", tEng + 0.2, YELLOW)],
    caption="A ground burst lifts earth into the fireball.")
a = S("p30")
reg("h-fireball", a, S("p32"), [("s", TGT, 150), (4.0, [52.61, 34.31], 150), (8.0, [52.6, 34.3], 150), (S("p31") - a, [52.6, 34.3], 150), (S("p31") - a + 3.4, [52.6, 34.31], 150), ("e", [52.6, 34.29], 150)], legend=LEGEND[:2], clock=CLK, clockLabel="IMPACT · T+96 H", clockRate=0, source=HC["source"], highlight=[HL_IRAN],
    rings=[ring_at(0, rel(a, W("p30", "fireball", 2))), ring_at(1, rel(a, S("p31")))],
    cities=[city(a, TGT, "Earth lifted into the fireball", W("p30", "lifts"), RED, "target", 6)],
    labels=[lab(a, [52.62, 34.37], "The earth comes back down as fallout", W("p30", "fallout"), AMBER), lab(a, [52.62, 34.24], "About 380 m across", W("p30", "about"), WHITE), lab(a, [52.62, 34.42], "20 psi: 240 m", W("p31", "two"), ORANGE)])
a = S("p32")
reg("h-5psi", a, S("p33"), [("s", TGT, 150), (4.5, [52.61, 34.31], 150), (8.5, [52.6, 34.3], 150), (12.0, [52.6, 34.29], 150), ("e", [52.59, 34.3], 150)], legend=LEGEND[:3], clock=CLK, clockLabel="IMPACT · T+96 H", clockRate=0, source=HC["source"], highlight=[HL_IRAN],
    rings=prior(2) + [ring_at(2, 0.1)],
    labels=[lab(a, [52.64, 34.38], "5 psi: 1.17 km", W("p32", "one"), RED), lab(a, [52.64, 34.25], "About 4.3 km2 inside", W("p32", "area"), WHITE), lab(a, [52.64, 34.2], "Flat ground: most buildings flattened", W("p32", "flat"), DIM),
            lab(a, [52.64, 34.43], "This is a mountain: rock changes it", W("p32", "mountain"), YELLOW), lab(a, [52.64, 34.16], "No number for the tunnels", W("p32", "tunnels"), YELLOW)])
a = S("p33")
reg("h-burns", a, S("p34"), [("s", TGT, 150), (4.0, [52.6, 34.31], 150), (8.0, [52.6, 34.3], 150), (12.0, [52.6, 34.3], 220), ("e", TGT, 300)], legend=LEGEND[:5], clock=CLK, clockLabel="IMPACT · T+96 H", clockRate=0, source=HC["source"], highlight=[HL_IRAN],
    rings=prior(3) + [ring_at(3, 0.1), ring_at(4, rel(a, W("p33", "Broken")))],
    labels=[lab(a, [52.64, 34.38], "Burns: 1.6 km", W("p33", "Third-degree"), AMBER), lab(a, [52.64, 34.25], "Windows: 3.2 km", W("p33", "Broken"), TEAL), lab(a, [52.64, 34.43], "Thinly populated country (our choice)", W("p33", "thinly"), WHITE), lab(a, [52.64, 34.2], "No town inside these rings", W("p33", "no"), YELLOW)])
# wind and plume
a = S("p34")
reg("w-plume", a, S("p35"), [("s", TGT, 300), (4.0, [52.8, 34.4], 700), (8.5, [53.5, 34.6], 800), (13.0, [52.5, 34.6], 900), ("e", [52, 34.6], 900)], clock="DAY 1", clockLabel="AFTER THE BURST", clockRate=0, source="Scenario engine; wind is our assumption", highlight=[HL_IRAN],
    cities=[city(a, TGT, "Ground zero", a + 0.4, RED, "target", 6), city(a, QOM, "Qom", W("p34", "Qom"), WHITE, "dot"), city(a, KASHAN, "Kashan", W("p34", "Kashan"), WHITE, "dot"), city(a, TEHRAN, "Tehran", W("p34", "Tehran"), WHITE, "dot")],
    lines=[{"from": [50.3, 34.0], "to": [52.3, 34.25], "color": WHITE, "dashed": True, "label": "Wind from the west (assumed)", "t0": rel(a, W("p34", "wind")), "t1": rel(a, W("p34", "wind")) + 2}],
    plume={"at": TGT, "bearing": 70, "lengthKm": 120, "widthKm": 18, "t0": rel(a, W("p34", "plume")), "t1": rel(a, W("p34", "plume")) + 5, "color": AMBER, "label": "Direction only: no dose, no distance"},
    labels=[lab(a, [54.4, 35.3], "Away from the cities", W("p34", "away"), AMBER)])
# the open question
a = S("p35")
reg("d-halls", a, W("p35", "Pickaxe"), [("s", TGT, 300), (3.0, TGT, 170), (W("p35", "Depth"), [51.5, 33.8], 900), ("e", [51.8, 33.7], 700)], clock="", highlight=[HL_IRAN],
    cities=[city(a, TGT, "Did it destroy the deep halls?", a + 0.3, RED, "target", 7), city(a, FORDOW, "Fordow: 80 to 90 m (reported)", W("p35", "Depth") + 0.8, AMBER, "dot"), city(a, NATANZ, "Natanz", W("p35", "Natanz"), AMBER, "dot")],
    labels=[lab(a, [53.0, 34.6], "We do not know", W("p35", "know"), YELLOW)])
tPk = W("p35", "Pickaxe")
add(id="d-bars", type="bars", start=tPk, end=W("p35", "Penetration"), tag="REAL DATA", title="Pickaxe Mountain, near Natanz: how deep?", sub="metres · two published estimates differ", source="Institute for Science and International Security; Reuters",
    bars=[{"label": "One estimate", "value": 100, "display": "80 to 100 m", "color": AMBER}, {"label": "Another repeats", "value": 600, "display": "up to 600 m", "color": RED}])
a = W("p35", "Penetration")
reg("d-model", a, S("p36"), [("s", TGT, 400), (3.0, TGT, 260), ("e", TGT, 170)], clock="", highlight=[HL_IRAN],
    cities=[city(a, TGT, "Penetration: estimates differ too", a + 0.3, RED, "target", 6)],
    labels=[lab(a, [52.7, 34.45], "No published model covers this site", W("p35", "no"), YELLOW)])

# ================================================================== Chapter 06 the day after [SIMULATION]
a = chapter("c6-card", S("p36"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
tSn = W("p36", "since")
reg("e-dark", a, S("p37"), [("s", TGT, 220), (3.0, TGT, 400), (tSn, [51.5, 33.9], 600), (W("p36", "Natanz"), [51.5, 33.6], 520), ("e", [51.5, 33.5], 480)], clock="DAY 1", clockLabel="THE FIRST CHANGE", clockRate=0, highlight=[HL_IRAN],
    zones=[{"points": [[52.2, 34.0], [53.0, 34.0], [53.0, 34.6], [52.2, 34.6]], "label": "Dark: nobody can see in", "color": "#8A8F98", "t": rel(a, W("p36", "dark")), "pulse": True}],
    cities=[city(a, FORDOW, "Fordow", W("p36", "Fordow"), AMBER, "target", 6), city(a, NATANZ, "Natanz", W("p36", "Natanz"), AMBER, "target", 6), city(a, ISFAHAN, "Isfahan", W("p36", "Isfahan"), AMBER, "target", 6)],
    labels=[lab(a, [52.0, 35.4], "Since June 2025: no inspector inside", tSn, YELLOW), lab(a, [52.0, 32.0], "Stockpile figure: more than a year stale", W("p36", "stockpile"), WHITE)])
a = S("p37")
tP = W("p37", "The")
reg("f-plume", a, S("p38"), [("s", TGT, 220), (3.4, TGT, 500), (W("p37", "Dasht-e"), [54.5, 34.6], 800), (W("p37", "Fallout"), [53.5, 34.6], 1200), ("e", [52.5, 34.2], 1300)], clock="DAY 1", clockLabel="THE SECOND CHANGE", clockRate=0, source="Scenario engine; wind is our assumption", highlight=[HL_IRAN],
    cities=[city(a, TGT, "Did the weapon reach the halls?", a + 0.3, RED, "target", 6), city(a, KASHAN, "Kashan", W("p37", "cities"), WHITE, "dot"), city(a, QOM, "Qom", W("p37", "away"), WHITE, "dot")],
    plume={"at": TGT, "bearing": 70, "lengthKm": 120, "widthKm": 18, "t0": rel(a, W("p37", "plume")), "t1": rel(a, W("p37", "plume")) + 5, "color": AMBER, "label": "Drifting east: no dose"},
    labels=[lab(a, [55.3, 35.4], "Dasht-e Kavir desert", W("p37", "Dasht-e"), WHITE), lab(a, [51.0, 35.2], "Thinning away from the cities", W("p37", "thinning"), AMBER)])
a = S("p38")
reg("g-iaea", a, S("p39"), [("s", [51.4, 34.0], 600), (3.0, FORDOW, 300), (W("p38", "Nothing"), [52.0, 34.2], 500), ("e", TGT, 300)], tag="REAL DATA", clock="", source="IAEA statements, 2025", highlight=[HL_IRAN],
    cities=[city(a, FORDOW, "Real sites: deep halls may be partly intact", a + 0.4, AMBER, "target", 7), city(a, TGT, "Our site", W("p38", "Nothing"), RED, "target", 6)],
    labels=[lab(a, [52.8, 34.6], "Nothing in our simulation updates it", W("p38", "Nothing"), YELLOW)])
a = S("p39")
tIn = W("p39", "In")
reg("i-tracks", a, S("p40"), [("s", [44, 33], 2400), (3.4, [43, 32.5], 2000), (tIn, [37, 31.8], 600), (W("p39", "and"), [36.5, 32.0], 420), ("e", [36.5, 31.9], 400)], clock="DAY 1", clockLabel="THE THIRD CHANGE", clockRate=0, highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, TELAVIV, "Tel Aviv", tIn + 0.5, TEAL, "dot"), city(a, NEVATIM, "Nevatim", tIn + 1.2, TEAL, "base", 5)],
    ships=[missile(a, [[47, 34.3], NEVATIM], W("p39", "fires"), W("p39", "again") + 2.0, label="Iranian missiles", color=RED), missile(a, [[47.5, 35.0], TELAVIV], W("p39", "fires") + 0.4, W("p39", "again") + 2.4, label="", color=RED)],
    labels=[lab(a, [41.5, 35.4], "Change 3: the missile tracks", W("p39", "missile"), YELLOW), lab(a, [41.5, 30.0], "June 2025, by Israel's count", W("p39", "Israel's"), WHITE), lab(a, [38.5, 29.8], "About 9 in 10 intercepted", W("p39", "nine"), TEAL), lab(a, [38.5, 29.0], "31+ hit populated areas or key sites", W("p39", "thirty-one"), RED)])
a = S("p40")
tUS = W("p40", "The", 3)
reg("j-water", a, S("p41"), [("s", [51, 31], 1600), (3.4, [53, 29], 1500), (tUS, [55, 27], 1300), (W("p40", "Strait"), [56.5, 26.5], 900), (W("p40", "what", 3), [54, 27.5], 1500), ("e", [54, 27.5], 1700)], clock="DAY 1", clockLabel="THE FOURTH CHANGE", clockRate=0, source="Reuters; Associated Press", highlight=[HL_IRAN],
    zones=[{"points": [[50.0, 27.5], [57.5, 27.2], [58.0, 25.2], [56.0, 24.8], [51.0, 26.0]], "label": "US blockade of Iranian ports", "color": BLUE, "t": rel(a, W("p40", "blockade")), "pulse": True}],
    ships=[{"path": [[60.5, 23.5], [57.5, 25.8]], "t0": rel(a, tUS), "t1": rel(a, tUS) + 4.0, "kind": "us", "label": "US Navy", "t": rel(a, tUS)}, {"path": [[50.5, 28.8], [54.5, 26.8], [56.3, 26.4]], "t0": 0.5, "t1": 9.0, "kind": "tanker", "label": "Tanker", "t": 0.4}],
    cities=[city(a, HORMUZ, "Strait of Hormuz (contested)", W("p40", "Strait"), AMBER, "target", 6)],
    labels=[lab(a, [48.5, 31.0], "What is buried? What is left?", a + 0.4, YELLOW), lab(a, [53.0, 30.1], "Nuclear strike and shipping: no study", W("p40", "no"), WHITE)])
a = S("p41")
tIn2 = W("p41", "In", 2)
reg("k-treaty", a, S("p42"), [("s", [44, 31], 3000), (3.4, [46, 31], 2700), (tIn2, [53, 32.5], 2200), (W("p41", "In", 3), [48, 27], 2700), ("e", [46, 26], 2600)], clock="DAY 1", clockLabel="THE TREATY MAP", clockRate=0, source="UN Treaty Collection; Reuters", highlight=[HL_ISR, HL_IRAN], legend=LEG,
    cities=[city(a, [34.9, 31.7], "Israel: never joined the NPT", W("p41", "Israel"), TEAL, "base", 6), city(a, TGT, "Iran: left it (simulation)", W("p41", "in", 3) if False else W("p41", "simulation"), RED, "target", 6)],
    labels=[lab(a, [53.0, 36.9], "Real life: exit bills in parliament", W("p41", "parliament"), AMBER), lab(a, [47.0, 22.8], "Saudi Arabia: toward its own bomb (2012 game)", W("p41", "toward"), WHITE)])
a = S("p42")
tQa = W("p42", "Qatar")
reg("m-qatar", a, S("p44"), [("s", [48, 30], 2400), (3.0, [48, 29], 1900), (tQa, [48, 28], 1500), (S("p43"), [52.0, 33.0], 1200), (W("p43", "and"), TGT, 400), ("e", TGT, 220)], clock="DAY 1", clockLabel="ONE CHANNEL OPEN", clockRate=0, source="Reuters; Associated Press", highlight=[HL_IRAN, HL_ISR],
    cities=[city(a, TGT, "Iran", a + 0.3, AMBER, "dot"), city(a, DOHA, "Qatar: the real go-between today", tQa, TEAL, "target", 7)],
    lines=[{"from": DOHA, "to": TGT, "color": TEAL, "dashed": True, "t0": rel(a, W("p42", "channel")), "t1": rel(a, W("p42", "channel")) + 2.0}, {"from": DOHA, "to": [35.2, 31.8], "color": TEAL, "dashed": True, "t0": rel(a, tQa), "t1": rel(a, tQa) + 2.5}],
    labels=[lab(a, [47.0, 34.8], "Who asks the question?", a + 0.3, YELLOW), lab(a, [52.8, 34.6], "The mountain is still there", S("p43") + 0.3, RED), lab(a, [52.8, 34.3], "And so is the question", W("p43", "question"), YELLOW)])
# ================================================================== End slate
add(id="end", type="endslate", start=S("p44"), end=END, tag="", title="Next scenario", line="One 10-kiloton nuke at sea, and a US carrier strike group.")


# ------------------------------------------------------------------ pace: put interpolated camera keys where nothing new arrives
def arrivals():
    out = []
    for s in shots:
        st = s["start"]
        out.append(st)
        for k, v in s.items():
            if isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        for tk in ("t", "t0"):
                            if isinstance(it.get(tk), (int, float)):
                                out.append(st + it[tk]); break
            elif isinstance(v, dict) and isinstance(v.get("t0"), (int, float)):
                out.append(st + v["t0"])
        if isinstance(s.get("flashT"), (int, float)):
            out.append(st + s["flashT"])
    return sorted(t for t in out if t >= 0)


def interp(keys, t, fields):
    ks = sorted(keys, key=lambda k: k["t"])
    if t <= ks[0]["t"]:
        return {f: ks[0][f] for f in fields}
    for k0, k1 in zip(ks, ks[1:]):
        if t <= k1["t"]:
            f = (t - k0["t"]) / max(k1["t"] - k0["t"], 1e-6)
            out = {}
            for fld in fields:
                v0, v1 = k0[fld], k1[fld]
                out[fld] = [round(v0[0] + (v1[0] - v0[0]) * f, 4), round(v0[1] + (v1[1] - v0[1]) * f, 4)] if isinstance(v0, list) else round(v0 + (v1 - v0) * f, 3)
            return out
    return {f: ks[-1][f] for f in fields}


def densify():
    slate = next(s["start"] for s in shots if s["type"] == "endslate")
    for _ in range(40):
        times = [t for t in arrivals() if t < slate] + [slate]
        changed = False
        for a, b in zip(times, times[1:]):
            limit = 3.6 if a < 90 else 5.4
            if b - a <= limit:
                continue
            s = next((x for x in shots if x["start"] <= a + 1e-6 < x["end"]), None)
            if not s or s["type"] not in ("region", "globe") or "camera" not in s:
                continue
            n = math.ceil((b - a) / limit) - 1
            fields = ["center", "widthKm"] if s["type"] == "region" else ["lat", "lon", "scale"]
            for i in range(1, n + 1):
                tt = round(a + (b - a) * i / (n + 1) - s["start"], 2)
                key = {"t": tt}
                key.update(interp(s["camera"], tt, fields))
                s["camera"].append(key)
            s["camera"].sort(key=lambda k: k["t"])
            changed = True
        if not changed:
            break


REAL_PLACES = [("Tehran", TEHRAN), ("Qom", QOM), ("Kashan", KASHAN), ("Isfahan", ISFAHAN), ("Natanz", NATANZ), ("Fordow", FORDOW)]


def context():
    """Inland Iran at under 500 km is an empty brown frame: keep the camera at 500 km or wider (hero rings excepted) and
    name the real towns that sit in view, so the picture always has places on it."""
    for s in shots:
        if s["type"] != "region" or s["id"].startswith("h-"):
            continue
        floor = 300 if s["id"] == "open-flash" else 500
        for k in s["camera"]:
            k["widthKm"] = max(k["widthKm"], floor)
        s["view"]["widthKm"] = max(s["view"]["widthKm"], floor)
        c0 = s["camera"][0]["center"]
        if not (44 < c0[0] < 58 and 28 < c0[1] < 38) or s["id"] in ("open-flash", "open-run", "open-launch"):
            continue
        have = [tuple(c["at"]) for c in s.get("cities", [])]
        for nm, at in REAL_PLACES:
            near = any(abs(at[0] - h[0]) < 0.08 and abs(at[1] - h[1]) < 0.08 for h in have)
            inside = all(abs(at[0] - k["center"][0]) < k["widthKm"] / 111 * 0.4 and abs(at[1] - k["center"][1]) < k["widthKm"] / 111 * 0.22 for k in s["camera"])
            if not near and inside:
                s.setdefault("cities", []).append({"at": at, "label": nm, "kind": "dot", "t": 0.3})


context()
densify()

# ------------------------------------------------------------------ audio plan and output
booms = [tF + 0.1, tC5 + 0.1]
b0 = round(min(tF + 0.1 - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p06") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p15") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p15") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
            if m.get("label") in (None, ""):
                m.pop("label", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
