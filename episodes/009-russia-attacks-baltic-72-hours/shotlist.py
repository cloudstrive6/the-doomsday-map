"""Director pass for episode 009: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 009-russia-attacks-baltic-72-hours
No real calendar date for the simulation; clocks count hours of the war ("HOUR 61") or minutes to impact. The hero
strike is Siauliai Air Base (city file siauliai.json); every other picture is a region or globe shot at 150 km or wider.
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
GREY = "#8A8F98"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round(max(w["end"] for w in WORDS if not w["word"].startswith("[")) + 10, 2) if WORDS else round(TOTAL + 10, 2)


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()]
    if len(idx) < nth:
        print("WARNING: word not found", pid, word, nth)
        return round(u["start"] + u["duration"] * 0.5, 3)
    return round(u["start"] + u["duration"] * idx[nth - 1] / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
NUKE = next(s for s in sc["strikes"] if s["id"] == "isk-nuke-siauliai")
FX = NUKE["effects"]
SIA = [NUKE["target_lon"], NUKE["target_lat"]]       # Siauliai Air Base
LAUNCH = [NUKE["launch_lon"], NUKE["launch_lat"]]     # Iskander brigade, Kaliningrad Oblast (simulated)
RUKLA = [24.2, 55.0]
AMARI, TAPA, ORZYSZ = [24.21, 59.26], [25.96, 59.26], [21.95, 53.81]
PSKOV_L, SHIP_L = [28.3, 57.8], [19.0, 55.2]
KALCITY, BALTIYSK = [20.5, 54.71], [19.9, 54.65]
VILNIUS, KAUNAS, RIGA, TALLINN = [25.28, 54.69], [23.9, 54.9], [24.11, 56.95], [24.75, 59.44]
SIAULIAI_C = [23.316, 55.934]
WARSAW, BERLIN, MINSK, MOSCOW, KYIV = [21.01, 52.23], [13.4, 52.52], [27.56, 53.9], [37.62, 55.75], [30.52, 50.45]
SUWALKI, GRODNO, BREST_B = [22.93, 54.1], [23.83, 53.68], [4.35, 50.85]
NARVA, HELSINKI, PSKOV_C = [28.2, 59.38], [24.94, 60.17], [28.33, 57.82]
CRIMEA, ANDOYA, COPENH = [34.1, 44.95], [16.0, 69.3], [12.57, 55.68]
ELK, OLSZTYN = [22.35, 53.83], [20.48, 53.78]
LT, LV, EE, PL, BY, RU, UA, FI, DE, NL, DK, NO, US = "440", "428", "233", "616", "112", "643", "804", "246", "276", "528", "208", "578", "840"
HLB = [{"iso": i, "color": BLUE, "fill": "rgba(110,168,255,0.13)"} for i in (LT, LV, EE)]
HLP = {"iso": PL, "color": BLUE, "fill": "rgba(110,168,255,0.07)"}
HLR = {"iso": RU, "color": AMBER, "fill": "rgba(242,176,30,0.07)"}
HLBY = {"iso": BY, "color": AMBER, "fill": "rgba(242,176,30,0.05)"}
HLU = {"iso": UA, "color": TEAL, "fill": "rgba(62,214,200,0.10)"}
LEG = [{"text": "RUSSIA, BELARUS", "color": AMBER}, {"text": "NATO", "color": BLUE}]


def CL(iso, text, color=BLUE, size=None):
    d = {"iso": iso, "text": text, "color": color}
    if size:
        d["size"] = size
    return d


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


def missile(a, path, t0, t1, label="Iskander-M", color=RED, kind="pla", t_on=None):
    return {"path": path, "t0": rel(a, t0), "t1": rel(a, t1), "kind": kind, "color": color, "label": label, "t": rel(a, t0 if t_on is None else t_on), "wake": True}


def line(a, p, q, t0, t1, color=WHITE, dashed=True, label=None, width=None):
    d = {"from": p, "to": q, "color": color, "dashed": dashed, "t0": rel(a, t0), "t1": rel(a, t1)}
    if label:
        d["label"] = label
    if width:
        d["width"] = width
    return d


def cam(a, b, *keys):
    out = []
    for t, c, w in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t) if t > 0 else 0)
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def reg(sid, a, b, keys, tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    if kw.get("clock") == "DAY 1":
        kw.setdefault("highlight", HLB + [HLP])
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **kw)


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=a, end=round(a + dur, 2), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 2)


# ================================================================== Cold open [SIMULATION]
FL = 2.0   # the cut lands on the flash; the flash itself is at +0.1 in the city shot
reg("open-run", 0, FL, [("s", [23.0, 55.5], 560), ("e", [23.2, 55.55], 420)], clock="T-03:00", clockLabel="TO IMPACT", clockRate=90,
    highlight=HLB + [HLR], countryLabels=[CL(LT, "LITHUANIA"), CL(RU, "RUSSIA", AMBER)],
    cities=[city(0, SIA, "Siauliai Air Base", 0.15, RED, "target", 6), city(0, LAUNCH, "Kaliningrad (launch, simulated)", 0.0, AMBER, "base", 5), city(0, VILNIUS, "Vilnius", 0.4)],
    lines=[line(0, LAUNCH, SIA, 0.0, 1.9, RED)],
    ships=[missile(0, [LAUNCH, SIA], 0.0, 1.95, label="Iskander-M", t_on=0.0)])
a = FL
add(id="open-flash", type="city", start=a, end=S("p02"), tag="SIMULATION", clock="03:43", clockLabel="SIAULIAI, LITHUANIA · LOCAL", clockRate=0, city="siauliai",
    view={"center": SIA, "widthKm": 5.0}, gz=SIA,
    camera=[{"t": 0, "center": SIA, "widthKm": 5.0}, {"t": 2.6, "center": SIA, "widthKm": 3.8}, {"t": 5.4, "center": SIA, "widthKm": 3.0}],
    flashT=0.1, rings=[{"km": FX["fireball_km"], "label": "Fireball", "color": WHITE, "t": 0.6}, {"km": FX["psi5_km"], "label": "5 psi", "color": RED, "t": 2.6}],
    labels=[{"at": [SIA[0], SIA[1] + 0.004], "text": "Siauliai Air Base", "color": WHITE, "t": 0.9}, {"at": [SIA[0], SIA[1] - 0.012], "text": "10 kt airburst (our choice)", "color": YELLOW, "t": 2.0}],
    legend=[], caption="The first nuclear weapon used in war since 1945. Simulation: it has not happened.")
a = S("p02")
reg("open-sim", a, S("p03"), [("s", [23.5, 56.3], 1150), (W("p02", "published"), [24.0, 56.5], 900), ("e", [24.0, 56.4], 700)], clock="HOUR 61", clockLabel="OF THE WAR", clockRate=0,
    highlight=HLB + [HLR, HLP], countryLabels=[CL(LT, "LITHUANIA"), CL(LV, "LATVIA"), CL(EE, "ESTONIA"), CL(RU, "RUSSIA", AMBER, 30)], legend=LEG,
    cities=[city(a, SIA, "Siauliai Air Base", a + 0.3, RED, "target", 6), city(a, LAUNCH, "Kaliningrad", W("p02", "simulation"), AMBER, "base", 5), city(a, RIGA, "Riga", W("p02", "built")), city(a, VILNIUS, "Vilnius", W("p02", "numbers"))],
    labels=[lab(a, [26.2, 57.9], "A simulation: not a prediction", W("p02", "simulation"), YELLOW), lab(a, [27.3, 55.0], "It has not happened", W("p02", "not"), RED)])
a = S("p03")
tIt, tNo = W("p03", "It"), W("p03", "Nobody")
reg("open-radar", a, tIt, [("s", [22.0, 56.6], 1100), (W("p03", "climbing"), [22.6, 55.6], 700), ("e", [22.5, 55.5], 520)], clock="T-03:00", clockLabel="TO IMPACT", clockRate=30,
    highlight=HLB + [HLR, HLP], countryLabels=[CL(LT, "LITHUANIA"), CL(PL, "POLAND"), CL(RU, "RUSSIA", AMBER, 30)], legend=LEG,
    cities=[city(a, [21.5, 57.0], "Radar track (simulated)", W("p03", "radar"), YELLOW, "dot", 5), city(a, KALCITY, "Kaliningrad", W("p03", "Kaliningrad"), AMBER, "base", 6), city(a, SIA, "Siauliai Air Base", W("p03", "picks"), RED, "target", 6)],
    ships=[missile(a, [LAUNCH, SIA], W("p03", "climbing"), tNo + 1.0, label="Ballistic missile", t_on=W("p03", "ballistic"))],
    short={"countryLabels": None, "labels": [lab(a, [23.9, 55.3], "LITHUANIA", a + 0.3, BLUE), lab(a, [20.6, 53.55], "POLAND", a + 0.3, BLUE)]})
reg("open-one", tIt, tNo, [("s", [22.8, 55.4], 420), ("e", [23.1, 55.6], 330)], clock="T-01:30", clockLabel="TO IMPACT", clockRate=30,
    highlight=HLB + [HLR], countryLabels=[CL(LT, "LITHUANIA")],
    cities=[city(tIt, SIA, "One air base", W("p03", "air"), RED, "target", 7), city(tIt, LAUNCH, "Iskander brigade (simulated)", tIt + 0.1, AMBER, "base", 5)],
    ships=[missile(tIt, [[22.2, 55.05], SIA], tIt, tNo + 0.9, label="One missile", t_on=tIt)],
    lines=[line(tIt, LAUNCH, SIA, tIt, tIt + 2.0, RED)])
reg("open-which", tNo, S("p04"), [("s", [23.2, 55.7], 300), ("e", [23.4, 55.9], 190)], clock="T-00:30", clockLabel="TO IMPACT", clockRate=12,
    highlight=HLB, countryLabels=[CL(LT, "LITHUANIA")],
    cities=[city(tNo, SIA, "Siauliai Air Base", tNo + 0.2, RED, "target", 7), city(tNo, SIAULIAI_C, "Siauliai (city)", W("p03", "ground"), WHITE)],
    ships=[missile(tNo, [[22.9, 55.6], SIA], tNo, S("p04") - 0.3, label="", t_on=tNo)],
    labels=[lab(tNo, [24.15, 56.05], "Conventional?", W("p03", "conventional"), YELLOW), lab(tNo, [24.15, 55.75], "Or nuclear?", W("p03", "nuclear"), RED)])
a = S("p04")
tH61 = a
reg("open-h61", a, a + 3.8, [("s", [23.4, 55.9], 150), ("e", [23.4, 55.9], 360)], clock="HOUR 61", clockLabel="OF A SIMULATED WAR", clockRate=0, highlight=HLB,
    countryLabels=[CL(LT, "LITHUANIA")], burst={"at": SIA, "t": 0.1, "km": 6, "fade": 4},
    cities=[city(a, SIA, "Siauliai Air Base", a + 0.4, RED, "target", 6), city(a, SIAULIAI_C, "Siauliai", a + 1.2)],
    short={"countryLabels": None, "labels": [lab(a, [24.0, 55.35], "LITHUANIA", a + 0.3, BLUE)]})
a2 = a + 3.8
glob("open-why", a2, S("p05"), [("s", 52, 22, 1500), (W("p04", "world"), 50, 18, 1050), ("e", 50, 12, 800)], highlight=[HLR, HLU] + HLB, clock="HOUR 61", clockLabel="OF THE WAR", clockRate=0,
     markers=[{"at": MOSCOW, "label": "Why would Moscow fire it?", "color": AMBER, "kind": "base", "size": 5, "t": rel(a2, W("p04", "Why"))}, {"at": SIA, "label": "Lithuania", "color": RED, "kind": "target", "t": 0.3}, {"at": BREST_B, "label": "Brussels, the world", "color": BLUE, "kind": "dot", "t": rel(a2, W("p04", "world"))}],
     arcs=[{"from": MOSCOW, "to": SIA, "t0": rel(a2, W("p04", "fire")), "t1": rel(a2, W("p04", "fire")) + 2.5, "color": RED, "loft": 0.15}])

# ================================================================== Chapter 01 [REAL DATA]
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "A night of sirens", "REAL DATA")
CLN = dict(clock="11 NOV 2026", clockLabel="NIGHT OF THE ALERTS", clockRate=0)
reg("c1-alerts", a, S("p06"), [("s", [24.5, 57.0], 1000), (W("p05", "Latvia"), [24.5, 57.3], 800), ("e", [24.6, 57.6], 650)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=HLB, countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)],
    cities=[city(a, VILNIUS, "Vilnius", W("p05", "Lithuania"), YELLOW, "target", 6), city(a, RIGA, "Riga", W("p05", "Latvia"), YELLOW, "target", 6), city(a, TALLINN, "Tallinn", W("p05", "Estonia"), YELLOW, "target", 6)],
    labels=[lab(a, [22.0, 58.7], "Drone alerts: shelter", W("p05", "urging"), RED)])
a = S("p06")
tLi, tWd = W("p06", "Lithuania's"), W("p06", "The")
reg("c1-nato", a, tLi, [("s", [20.0, 56.0], 1300), ("e", [22.5, 55.6], 750)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=HLB + [HLP], countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(PL, "POLAND", BLUE, 30)],
    cities=[city(a, [21.1, 56.5], "NATO air defence jets", W("p06", "NATO") + 0.3, BLUE, "base", 6), city(a, SIA, "Siauliai", a + 2.2, BLUE, "base", 5)],
    ships=[missile(a, [[21.0, 56.4], [24.0, 55.6]], a + 0.4, tLi, label="Jets scrambled", color=BLUE, kind="ally", t_on=a + 0.3)])
reg("c1-kaunas", tLi, tWd, [("s", [23.9, 54.9], 330), ("e", [23.9, 54.9], 190)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=HLB, countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)], cities=[city(tLi, KAUNAS, "Kaunas, second-largest city", W("p06", "Kaunas"), YELLOW, "target", 7), city(tLi, VILNIUS, "Vilnius", tLi + 0.3)],
    rings=[{"at": KAUNAS, "km": 40, "color": YELLOW, "t": rel(tLi, W("p06", "warning")), "dashed": True}], labels=[lab(tLi, [24.9, 55.25], "Lithuania's warning", W("p06", "warning"), YELLOW)])
reg("c1-clear", tWd, S("p07"), [("s", [24.4, 55.9], 1100), (W("p06", "No"), [24.4, 56.4], 850), ("e", [24.4, 56.6], 1300)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=HLB, countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30)],
    labels=[lab(tWd, [24.2, 55.0], "Alerts withdrawn: same day", tWd + 0.3, TEAL), lab(tWd, [24.2, 54.55], "No injuries reported", W("p06", "No"), WHITE)])
a = S("p07")
tMo, tNot = W("p07", "Moscow"), W("p07", "It")
reg("c1-strays", a, tMo, [("s", [30, 53.5], 1700), (W("p07", "off"), [28, 54.5], 1300), ("e", [26.5, 55.0], 1000)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=[HLU, HLR, HLBY] + HLB, countryLabels=[CL(UA, "UKRAINE", TEAL, 30), CL(BY, "BELARUS", AMBER, 30), CL(LT, "LITHUANIA", BLUE, 30)],
    ships=[missile(a, [[32.5, 51.0], [29.5, 53.0], [24.5, 55.4]], a + 0.5, tMo, label="Stray drone", color=YELLOW, kind="pla", t_on=a + 0.3)],
    labels=[lab(a, [34.0, 53.8], "Strays from the Ukraine war", W("p07", "strays"), TEAL), lab(a, [29.5, 51.9], "Pushed off course: jamming", W("p07", "jamming"), YELLOW)])
reg("c1-thin", tMo, S("p08"), [("s", [32, 53], 2000), (tNot, [28, 55], 1200), ("e", [25, 55.5], 700)], tag="REAL DATA", source="Reuters; Associated Press, 11 November 2026", **CLN,
    highlight=[HLU, HLR] + HLB, countryLabels=[CL(RU, "RUSSIA", AMBER), CL(UA, "UKRAINE", TEAL, 30)],
    cities=[city(tMo, MOSCOW, "Moscow", tMo + 0.2, AMBER, "base", 5), city(tMo, KYIV, "Kyiv", tMo + 0.4, TEAL, "base", 5)],
    lines=[line(tMo, MOSCOW, KYIV, tMo + 0.3, tMo + 1.8, AMBER, label="Moscow blames Kyiv")],
    labels=[lab(tMo, [26.0, 56.8], "Not an attack", tNot, TEAL), lab(tMo, [26.0, 56.3], "But a thin line", W("p07", "thin"), RED)])
a = S("p08")
tH = W("p08", "the", 2)
reg("c1-cross", a, tH, [("s", [23.5, 56.0], 1200), (W("p08", "crosses"), [23.0, 55.3], 600), ("e", [22.8, 55.2], 420)], tag="SIMULATION", clock="HOUR 3", clockLabel="THE LINE IS CROSSED", clockRate=0,
    highlight=HLB + [HLR], countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(a, KALCITY, "Kaliningrad", a + 0.3, AMBER, "base", 5), city(a, RUKLA, "Rukla", W("p08", "hour"), RED, "target", 6), city(a, SIA, "Siauliai", W("p08", "three"), RED, "target", 6)],
    labels=[lab(a, [26.2, 56.7], "Our simulation crosses it", W("p08", "crosses"), YELLOW)])
add(id="c1-tl", type="timeline", start=tH, end=S("p09"), tag="SIMULATION", title="The simulated war", sub="hour 3: first strikes · hour 61: one missile, one question", total=61, unit="hours",
    segments=[{"from": 0, "to": 3, "label": "Hour 3", "color": RED}, {"from": 3, "to": 61, "label": "58 hours of war", "color": AMBER}], highlight={"from": 59, "to": 61, "label": "Hour 61"}, cursorTo=61)
a = S("p09")
tI, tNa = W("p09", "It"), W("p09", "NATO's")
glob("c1-note", a, tI, [("s", 52, 32, 1200), (W("p09", "diplomatic"), 54, 28, 1500), ("e", 54, 24, 1900)], tag="REAL DATA", clock="6 WEEKS EARLIER", clockLabel="THE NOTE", clockRate=0, source="Reuters, 29 and 30 September 2026",
     highlight=[HLR] + HLB, markers=[{"at": MOSCOW, "label": "Russia", "color": AMBER, "kind": "base", "size": 5, "t": 0.3}, {"at": BREST_B, "label": "NATO states", "color": BLUE, "kind": "dot", "t": rel(a, W("p09", "NATO"))}],
     arcs=[{"from": MOSCOW, "to": BREST_B, "t0": rel(a, W("p09", "sent")), "t1": rel(a, tI) + 0.5, "color": AMBER, "loft": 0.2}], caption="A diplomatic note, six weeks before the alerts.",
     short={"type": "region", "camera": cam(a, tI, ("s", [21.2, 54.9], 520), (W("p09", "diplomatic"), [22.5, 55.0], 900), ("e", [24.0, 54.8], 1500)),
            "view": {"center": [21.2, 54.9], "widthKm": 520}, "sun": None, "markers": None, "arcs": None, "source": "", "highlight": [HLR] + HLB + [HLP],
            "legend": [{"text": "RUSSIA", "color": AMBER}, {"text": "NATO", "color": BLUE}],
            "cities": [city(a, KALCITY, "Kaliningrad", a + 0.2, AMBER, "target", 7)],
            "labels": [lab(a, [23.6, 56.2], "Russia's note to NATO states", W("p09", "sent"), YELLOW)]})
reg("c1-arsenal", tI, tNa, [("s", [22.0, 55.0], 700), (W("p09", "including"), [21.5, 54.9], 450), ("e", [21.0, 54.8], 330)], tag="REAL DATA", clock="6 WEEKS EARLIER", clockLabel="THE NOTE", clockRate=0, source="Reuters, 29 and 30 September 2026",
    highlight=[HLR] + HLB + [HLP], countryLabels=[CL(PL, "POLAND", BLUE, 30), CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(tI, KALCITY, "Kaliningrad", tI + 0.2, AMBER, "target", 7)],
    zones=[{"points": [[19.6, 54.4], [22.8, 54.4], [22.8, 55.2], [19.6, 55.2]], "label": "If NATO cuts it off", "color": AMBER, "t": rel(tI, W("p09", "cut")), "pulse": True}],
    labels=[lab(tI, [24.2, 56.2], "Ready to use the entire arsenal", W("p09", "entire"), RED), lab(tI, [24.2, 55.7], "including nuclear weapons", W("p09", "nuclear"), RED)])
reg("c1-answer", tNa, S("p10"), [("s", [14, 52], 3000), (W("p09", "stop"), [10, 52.5], 2400), ("e", [12, 53], 2800)], tag="REAL DATA", clock="6 WEEKS EARLIER", clockLabel="THE ANSWER", clockRate=0, source="Reuters, 29 and 30 September 2026",
    highlight=[HLR, HLP] + HLB, cities=[city(tNa, BREST_B, "NATO, Brussels", tNa + 0.2, BLUE, "base", 6), city(tNa, MOSCOW, "Moscow", tNa + 0.4, AMBER, "base", 5)],
    lines=[line(tNa, BREST_B, MOSCOW, W("p09", "answered"), W("p09", "answered") + 2.5, BLUE)],
    labels=[lab(tNa, [14.0, 57.5], "NATO chief: stop the nuclear threats", W("p09", "stop"), BLUE)])
a = S("p10")
tIt2 = W("p10", "It")
reg("c1-kal", a, tIt2, [("s", [21.0, 54.9], 380), ("e", [21.3, 54.9], 600)], tag="REAL DATA", clock="", source="Reuters; Institute for the Study of War", highlight=[HLR] + HLB + [HLP],
    countryLabels=[CL(PL, "POLAND", BLUE), CL(LT, "LITHUANIA", BLUE)],
    cities=[city(a, KALCITY, "Kaliningrad: about 1 million people", W("p10", "million"), AMBER, "target", 7), city(a, BALTIYSK, "Baltic Fleet, Baltiysk", W("p10", "Baltic"), AMBER, "base", 5)],
    labels=[lab(a, [22.9, 54.15], "Wedged between Poland and Lithuania", W("p10", "wedged"), WHITE)])
reg("c1-iskander", tIt2, S("p11"), [("s", [21.5, 54.9], 500), (W("p10", "nuclear-capable"), [21.5, 54.9], 340), ("e", [22.2, 54.9], 560)], tag="REAL DATA", clock="", source="Reuters; Institute for the Study of War", highlight=[HLR] + HLB + [HLP],
    countryLabels=[CL(PL, "POLAND", BLUE), CL(LT, "LITHUANIA", BLUE)],
    cities=[city(tIt2, BALTIYSK, "Baltic Fleet", tIt2 + 0.3, AMBER, "base", 5), city(tIt2, [21.6, 54.55], "Iskander missiles", W("p10", "nuclear-capable"), RED, "base", 6)],
    rings=[{"at": [21.6, 54.55], "km": 175, "color": RED, "label": "", "t": rel(tIt2, W("p10", "nuclear-capable")), "dashed": True}])
a = S("p11")
tIt3 = W("p11", "It")
reg("c1-gap", a, tIt3, [("s", [23.6, 54.5], 380), (W("p11", "sixty-five"), [23.5, 54.2], 300), ("e", [23.4, 54.1], 230)], tag="REAL DATA", clock="", source="NATO; Center for European Policy Analysis", highlight=[HLR, HLBY, HLP] + HLB,
    countryLabels=[CL(PL, "POLAND", BLUE), CL(BY, "BELARUS", AMBER), CL(LT, "LITHUANIA", BLUE)],
    zones=[{"points": [[22.8, 54.35], [23.8, 53.75], [23.9, 54.2], [23.0, 54.45]], "label": "Suwalki Gap, about 65 km", "color": YELLOW, "t": rel(a, W("p11", "Suwalki")), "pulse": True}],
    cities=[city(a, KALCITY, "Kaliningrad", a + 0.2, AMBER, "base", 5), city(a, GRODNO, "Belarus", a + 0.5, AMBER, "dot")])
reg("c1-rail", tIt3, S("p12"), [("s", [23.4, 54.4], 420), (W("p11", "railway"), [23.3, 54.0], 480), ("e", [23.5, 54.3], 700)], tag="REAL DATA", clock="", source="NATO; Center for European Policy Analysis", highlight=[HLR, HLBY, HLP] + HLB,
    countryLabels=[CL(PL, "POLAND", BLUE), CL(LT, "LITHUANIA", BLUE)],
    lines=[line(tIt3, [21.0, 52.2], [23.6, 54.1], tIt3 + 0.3, tIt3 + 2.2, TEAL, False), line(tIt3, [23.6, 54.1], KAUNAS, tIt3 + 1.8, tIt3 + 3.2, TEAL, False)],
    cities=[city(tIt3, WARSAW, "Poland", tIt3 + 0.3, BLUE, "dot"), city(tIt3, KAUNAS, "Kaunas", tIt3 + 1.8, BLUE, "dot")],
    labels=[lab(tIt3, [25.2, 53.3], "One single-track railway", W("p11", "single-track"), TEAL), lab(tIt3, [25.2, 52.9], "Shortest land route to the Baltics", W("p11", "shortest"), WHITE)])
reg("c1-fast", S("p12"), S("p13"), [("s", [24, 56], 900), (W("p12", "crisis"), [24, 56], 1250), ("e", [23, 55.5], 1700)], tag="REAL DATA", clock="", highlight=[HLR, HLBY, HLP] + HLB,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(S("p12"), KALCITY, "Kaliningrad", S("p12") + 0.3, AMBER, "base", 5), city(S("p12"), SUWALKI, "Suwalki Gap", S("p12") + 1.0, YELLOW, "target", 6)],
    labels=[lab(S("p12"), [27.5, 57.8], "How fast can a crisis become a war?", W("p12", "fast"), YELLOW)])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p13"), 3.5, "CHAPTER 02", "How close it has come", "REAL HISTORY")
tRu, tAm = W("p13", "Russia"), W("p13", "A")
reg("c2-crimea", a, tRu, [("s", [34.0, 45.4], 900), (W("p13", "took"), [34.2, 45.2], 600), ("e", [34.4, 45.4], 450)], tag="REAL HISTORY", clock="FEB 2014", clockLabel="CRIMEA", clockRate=0, source="Reuters; BBC",
    highlight=[HLU, HLR], countryLabels=[CL(UA, "UKRAINE", TEAL, 30), CL(RU, "RUSSIA", AMBER, 30)], legend=[{"text": "UKRAINE", "color": TEAL}, {"text": "RUSSIA", "color": AMBER}],
    cities=[city(a, [34.1, 44.95], "Simferopol, Crimea", W("p13", "Crimea"), WHITE, "dot", 7), city(a, [33.5, 44.6], "Sevastopol", a + 0.5, WHITE)],
    labels=[lab(a, [33.7, 46.1], "Soldiers with no insignia", W("p13", "insignia"), YELLOW)])
reg("c2-denied", tRu, tAm, [("s", [36.0, 47.0], 1500), (W("p13", "admitted"), [36, 49], 1300), ("e", [30, 52], 1900)], tag="REAL HISTORY", clock="FEB 2014", clockLabel="CRIMEA", clockRate=0, source="Reuters; BBC",
    highlight=[HLU, HLR], countryLabels=[CL(UA, "UKRAINE", TEAL), CL(RU, "RUSSIA", AMBER)],
    cities=[city(tRu, MOSCOW, "Moscow", tRu + 0.2, AMBER, "base", 5), city(tRu, CRIMEA, "Crimea", tRu + 0.4, RED, "target", 6)],
    labels=[lab(tRu, [39.8, 49.0], "Russia denied it", tRu + 0.4, AMBER), lab(tRu, [39.8, 48.0], "Putin later admitted it", W("p13", "admitted"), RED)])
reg("c2-model", tAm, S("p14"), [("s", [26, 56], 1600), (W("p13", "hour"), [26, 57], 1000), ("e", [27, 58.5], 650)], tag="REAL HISTORY", clock="", highlight=[HLR, HLBY] + HLB,
    countryLabels=[CL(RU, "RUSSIA", AMBER, 30), CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)],
    cities=[city(tAm, NARVA, "Narva border", tAm + 0.4, YELLOW, "target", 6), city(tAm, PSKOV_C, "Pskov", tAm + 1.0, AMBER, "dot")],
    labels=[lab(tAm, [29.4, 56.7], "Our hour zero: a deniable move", W("p13", "hour"), RED)])
a = S("p14")
tRu2, tThree, tPo2, tOur = W("p14", "Russia"), W("p14", "three"), W("p14", "Poland", 2), W("p14", "Our")
reg("c2-poland", a, tRu2, [("s", [24, 52.5], 1100), (W("p14", "twenty"), [23, 52.5], 800), ("e", [22.5, 52.3], 650)], tag="REAL HISTORY", clock="SEPT 2025", clockLabel="DRONES OVER POLAND", clockRate=0, source="Reuters; NATO",
    highlight=[HLP, HLBY, HLU], countryLabels=[CL(PL, "POLAND", BLUE), CL(BY, "BELARUS", AMBER, 30), CL(UA, "UKRAINE", TEAL, 30)],
    ships=[missile(a, [[27.5, 52.0], [24.5, 52.4], [21.8, 52.3]], a + 1.0, tRu2, label="Drones", color=RED, kind="pla", t_on=a + 0.8)], cities=[city(a, WARSAW, "Warsaw", a + 0.3)],
    labels=[lab(a, [26.5, 54.0], "About 20 Russian drones", W("p14", "twenty"), RED)])
reg("c2-zapad", tRu2, tThree, [("s", [26, 54.5], 1100), ("e", [28, 55], 1500)], tag="REAL HISTORY", clock="SEPT 2025", clockLabel="ZAPAD EXERCISE", clockRate=0, source="Reuters; NATO",
    highlight=[HLR, HLBY, HLP], countryLabels=[CL(BY, "BELARUS", AMBER), CL(RU, "RUSSIA", AMBER, 30), CL(PL, "POLAND", BLUE, 30)],
    zones=[{"points": [[24.5, 55.0], [31.5, 55.0], [31.5, 52.0], [24.5, 52.0]], "label": "Zapad: Russia and Belarus", "color": AMBER, "t": rel(tRu2, W("p14", "Zapad")), "pulse": True}], cities=[city(tRu2, MINSK, "Minsk", tRu2 + 0.3, AMBER, "base", 5)])
reg("c2-estonia", tThree, tPo2, [("s", [26, 59.0], 700), ("e", [25.5, 59.3], 460)], tag="REAL HISTORY", clock="SEPT 2025", clockLabel="JETS OVER ESTONIA", clockRate=0, source="Reuters; NATO",
    highlight=HLB + [HLR], countryLabels=[CL(EE, "ESTONIA", BLUE), CL(RU, "RUSSIA", AMBER, 30)],
    ships=[missile(tThree, [[26.6, 59.9], [25.2, 59.5], [24.4, 59.35]], tThree + 0.3, tPo2, label="3 Russian jets", color=AMBER, kind="pla", t_on=tThree + 0.2)], cities=[city(tThree, TALLINN, "Tallinn", tThree + 0.5, BLUE, "dot")])
reg("c2-consult", tPo2, tOur, [("s", [14, 54], 2200), ("e", [12, 54], 2800)], tag="REAL HISTORY", clock="SEPT 2025", clockLabel="NATO CONSULTATIONS", clockRate=0, source="NATO",
    highlight=[HLP] + HLB, cities=[city(tPo2, WARSAW, "Warsaw asks", tPo2 + 0.2, BLUE, "base", 5), city(tPo2, TALLINN, "Tallinn asks", W("p14", "Estonia"), BLUE, "base", 5), city(tPo2, BREST_B, "NATO, Brussels", tPo2 + 0.9, BLUE, "base", 6)],
    lines=[line(tPo2, WARSAW, BREST_B, tPo2 + 0.4, tPo2 + 2.0, BLUE), line(tPo2, TALLINN, BREST_B, W("p14", "Estonia"), W("p14", "Estonia") + 2.0, BLUE)])
reg("c2-stop", tOur, S("p15"), [("s", [24, 55.8], 1500), (W("p14", "incidents"), [24, 56.2], 900), ("e", [23.8, 56.0], 600)], tag="SIMULATION", clock="", highlight=HLB + [HLR, HLP], countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(tOur, SIA, "Where our simulation starts", W("p14", "begins"), RED, "target", 6), city(tOur, KALCITY, "Kaliningrad", tOur + 0.3, AMBER, "base", 5)])
a = S("p15")
tBy, tBr, tOb, tAd = W("p15", "By"), W("p15", "briefcase"), W("p15", "observers"), W("p15", "A", 3)
reg("c2-rocket", a, tBy, [("s", [20, 69], 1700), (W("p15", "Norwegian"), [24, 70], 1100), ("e", [26, 71], 1300)], tag="REAL HISTORY", clock="JAN 1995", clockLabel="NORWEGIAN ROCKET", clockRate=0, source="Arms Control Association; Reuters",
    highlight=[{"iso": NO, "color": BLUE, "fill": "rgba(110,168,255,0.08)"}, HLR], countryLabels=[CL(NO, "NORWAY", BLUE), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(a, ANDOYA, "Andoya, Norway", a + 0.3, BLUE, "base", 6), city(a, [33.0, 69.0], "Russian radar", W("p15", "radar"), AMBER, "base", 5)],
    ships=[missile(a, [ANDOYA, [24.0, 74.5], [18.0, 79.0]], W("p15", "Norwegian"), tBy + 1.0, label="Research rocket", color=BLUE, kind="ally", t_on=a + 0.5)])
reg("c2-sub", tBy, tBr, [("s", [30, 68], 2200), ("e", [37, 62], 2600)], tag="REAL HISTORY", clock="JAN 1995", clockLabel="THE ALERT", clockRate=0, source="Arms Control Association; Reuters",
    highlight=[HLR, HLBY], countryLabels=[CL(RU, "RUSSIA", AMBER)], cities=[city(tBy, MOSCOW, "Moscow", tBy + 0.2, AMBER, "base", 6), city(tBy, ANDOYA, "Andoya", tBy + 0.4, BLUE, "dot")],
    lines=[line(tBy, ANDOYA, MOSCOW, tBy + 0.5, tBy + 3.0, RED)], labels=[lab(tBy, [40.0, 68.5], "Looks like a US submarine missile", W("p15", "resembled"), RED)])
reg("c2-brief", tBr, tAd, [("s", [37.6, 55.7], 700), (tOb, [37.6, 55.7], 1100), ("e", [35, 60], 2300)], tag="REAL HISTORY", clock="JAN 1995", clockLabel="MINUTES TO DECIDE", clockRate=0, source="Arms Control Association; Reuters",
    highlight=[HLR], cities=[city(tBr, MOSCOW, "Moscow: nuclear briefcase active", tBr + 0.2, AMBER, "target", 7)],
    rings=[{"at": MOSCOW, "km": 60, "color": AMBER, "t": rel(tBr, tBr + 0.6), "dashed": True}], labels=[lab(tBr, [43.8, 57.4], "Within minutes: no threat", tOb + 0.5, TEAL)])
reg("c2-decide", tAd, S("p16"), [("s", [25, 56], 2200), (W("p15", "sixty-one"), [23.5, 55.8], 700), ("e", [23.4, 55.9], 420)], tag="SIMULATION", clock="HOUR 61", clockLabel="THE SAME PROBLEM", clockRate=0, highlight=HLB + [HLR],
    cities=[city(tAd, SIA, "Hour 61: what does it carry?", W("p15", "carries"), RED, "target", 7), city(tAd, KALCITY, "Kaliningrad", tAd + 0.3, AMBER, "base", 5)],
    ships=[missile(tAd, [LAUNCH, SIA], tAd + 1.0, S("p16") - 0.4, label="", t_on=tAd + 0.8)])
a = S("p16")
reg("c2-pattern", a, W("p16", "a"), [("s", [26, 54], 4200), ("e", [22, 55], 3000)], tag="REAL HISTORY", clock="", highlight=[HLU, HLR, HLP, HLBY] + HLB,
    cities=[city(a, CRIMEA, "Crimea 2014", a + 0.4, RED, "target", 6), city(a, [22.5, 52.3], "Poland 2025", a + 1.4, RED, "target", 6), city(a, [16.0, 69.3], "Norway 1995", a + 2.4, RED, "target", 6)])
tSm, tSo = W("p16", "small"), W("p16", "So")
reg("c2-window", W("p16", "a"), tSo, [("s", [24, 55.5], 1800), (tSm, [24, 55.5], 1100), ("e", [24, 56.0], 800)], tag="REAL HISTORY", clock="", highlight=HLB + [HLR, HLP],
    cities=[city(W("p16", "a"), SIA, "A small first move", tSm, YELLOW, "target", 6), city(W("p16", "a"), KALCITY, "Then a short window", W("p16", "short"), AMBER, "base", 6)],
    labels=[lab(W("p16", "a"), [27.0, 56.9], "Each side decides what the other meant", W("p16", "decides"), WHITE)])
reg("c2-first", tSo, S("p17"), [("s", [24, 56], 1000), ("e", [25, 56.5], 1600)], tag="SIMULATION", clock="HOUR 0", clockLabel="THE FIRST DAY", clockRate=0, highlight=HLB + [HLR, HLBY, HLP], legend=LEG,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30), CL(BY, "BELARUS", AMBER, 30)],
    cities=[city(tSo, SIA, "Siauliai", tSo + 0.3, BLUE, "base", 5), city(tSo, KALCITY, "Kaliningrad", tSo + 0.6, AMBER, "base", 5)])

# ================================================================== Chapter 03 [SIMULATION] the trigger
a = chapter("c3-card", S("p17"), 3.5, "CHAPTER 03", "The trigger", "SIMULATION")
tJa, tKr = W("p17", "jamming"), W("p17", "Kremlin")
CH3 = dict(clock="HOUR 0", clockLabel="A DENIABLE MOVE", clockRate=0, highlight=HLB + [HLR, HLBY, HLP], legend=LEG)
reg("c3-hour0", a, tJa, [("s", [27, 58.5], 600), (W("p17", "pretext"), [27.5, 58.0], 900), ("e", [26, 57], 1300)], **CH3,
    countryLabels=[CL(EE, "ESTONIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(a, NARVA, "Russian border, Narva", a + 0.3, AMBER, "base", 5), city(a, PSKOV_C, "Pskov", a + 0.8, AMBER, "dot")],
    labels=[lab(a, [30.0, 59.7], "Unmarked troops", W("p17", "unmarked"), RED), lab(a, [30.0, 59.2], "Pretext: protecting Russian speakers", W("p17", "pretext"), YELLOW)])
reg("c3-claim", tJa, S("p18"), [("s", [23, 55.5], 1400), (W("p17", "claim"), [21.5, 55.0], 600), ("e", [21.0, 54.9], 480)], **CH3,
    countryLabels=[CL(PL, "POLAND", BLUE, 30), CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(tJa, KALCITY, "Kaliningrad", tJa + 0.3, AMBER, "target", 6)],
    zones=[{"points": [[19.8, 54.3], [23.2, 54.3], [23.2, 55.4], [19.8, 55.4]], "label": "Claim: NATO is sealing it off", "color": AMBER, "t": rel(tJa, W("p17", "sealing")), "pulse": True}],
    labels=[lab(tJa, [23.3, 56.3], "Jamming", tJa + 0.2, YELLOW), lab(tJa, [23.3, 56.8], "The Kremlin denies everything", tKr, WHITE)])
a = S("p18")
tOn, tTh = W("p18", "One"), W("p18", "These")
add(id="c3-nopred", type="stamp", start=a, end=tOn, tag="SIMULATION", text="NOT A PREDICTION", line="choices, to follow the escalation", color=YELLOW)
reg("c3-danish", tOn, tTh, [("s", [12, 56], 1800), ("e", [18, 57], 1500)], clock="", highlight=[{"iso": DK, "color": BLUE, "fill": "rgba(110,168,255,0.12)"}, HLR] + HLB,
    cities=[city(tOn, COPENH, "Danish intelligence", tOn + 0.3, BLUE, "base", 6), city(tOn, KALCITY, "NATO member: Lithuania", tOn + 1.2, BLUE, "dot")],
    labels=[lab(tOn, [14.5, 58.8], "Full invasion: highly unlikely", W("p18", "highly"), TEAL)])
reg("c3-choices", tTh, S("p19"), [("s", [24, 56], 1300), ("e", [23.5, 55.6], 800)], clock="", highlight=HLB + [HLR, HLP],
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)], cities=[city(tTh, SIA, "Our choices", tTh + 0.3, YELLOW, "target", 6), city(tTh, KALCITY, "Kaliningrad", tTh + 0.6, AMBER, "base", 5)],
    labels=[lab(tTh, [26.5, 57.4], "To follow the escalation", W("p18", "escalation"), WHITE)])
a = S("p19")
tOne, tThe, tFl, tCv = W("p19", "One"), W("p19", "the", 3), W("p19", "Flight"), W("p19", "Conventional")
CH3b = dict(clock="HOUR 3", clockLabel="THE FIRST STRIKES", clockRate=0, highlight=HLB + [HLR, HLP], legend=LEG)
reg("c3-two", a, tOne, [("s", [23.0, 55.4], 520), (W("p19", "leave"), [23.0, 55.4], 380), ("e", [23.0, 55.4], 440)], **CH3b,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(a, KALCITY, "Kaliningrad area", W("p19", "Kaliningrad"), AMBER, "base", 5), city(a, RUKLA, "Rukla", tOne, RED, "target", 6), city(a, SIA, "Siauliai", tThe, RED, "target", 6)],
    ships=[missile(a, [LAUNCH, RUKLA], W("p19", "leave"), tOne + 2.4, label="Iskander (conv.)", t_on=W("p19", "leave")), missile(a, [LAUNCH, SIA], W("p19", "leave"), tOne + 2.6, label="", t_on=W("p19", "leave"))])
reg("c3-rukla", tOne, tThe, [("s", [22.9, 55.1], 460), ("e", [24.2, 55.0], 190)], **CH3b,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    ships=[missile(tOne, [LAUNCH, RUKLA], tOne + 0.3, W("p19", "hits"), label="Iskander (conv.)", t_on=tOne + 0.3)],
    cities=[city(tOne, KALCITY, "Kaliningrad area", tOne + 0.1, AMBER, "base", 5), city(tOne, RUKLA, "Rukla: German-led battlegroup", W("p19", "hits"), BLUE, "base", 7), city(tOne, VILNIUS, "Vilnius", tOne + 0.4), city(tOne, KAUNAS, "Kaunas", tOne + 0.8)],
    rings=[{"at": RUKLA, "km": 8, "color": RED, "t": rel(tOne, W("p19", "hits")), "dashed": True}])
reg("c3-siauliai", tThe, tFl, [("s", [23.4, 55.9], 330), ("e", [23.4, 55.9], 190)], **CH3b,
    cities=[city(tThe, SIA, "Siauliai Air Base", tThe + 0.3, BLUE, "base", 7), city(tThe, SIAULIAI_C, "Siauliai", tThe + 1.0)],
    rings=[{"at": SIA, "km": 8, "color": RED, "t": rel(tThe, W("p19", "Base")), "dashed": True}])
add(id="c3-flight", type="number", start=tFl, end=S("p20"), tag="SIMULATION", value="ABOUT 3 MINUTES", countTo=3, prefix="ABOUT ", suffix=" MINUTES", label="flight time, Kaliningrad to Lithuania", sub="conventional warheads, our choice", color=RED, source="Scenario engine; flight times fitted to published ranges")
a = S("p20")
tBe, tSi, tTa, tLa = W("p20", "Because"), W("p20", "Siauliai"), W("p20", "The", 2), W("p20", "The", 3)
reg("c3-why", a, tBe, [("s", [23.5, 55.6], 380), ("e", [23.6, 55.5], 300)], **CH3b,
    cities=[city(a, RUKLA, "Rukla", a + 0.3, RED, "target", 6), city(a, SIA, "Siauliai", a + 0.8, RED, "target", 6)], labels=[lab(a, [25.3, 56.1], "Why those two?", a + 0.4, YELLOW)])
reg("c3-army", tBe, tSi, [("s", RUKLA, 260), ("e", RUKLA, 170)], **CH3b,
    cities=[city(tBe, RUKLA, "Rukla: the allied army", W("p20", "Rukla"), BLUE, "base", 7), city(tBe, VILNIUS, "Vilnius", tBe + 0.8), city(tBe, KAUNAS, "Kaunas", tBe + 1.2)])
reg("c3-air", tSi, tTa, [("s", SIA, 260), ("e", SIA, 170)], **CH3b,
    cities=[city(tSi, SIA, "Siauliai: NATO jets fly from here", tSi + 0.2, BLUE, "base", 7), city(tSi, SIAULIAI_C, "Siauliai", tSi + 1.0)])
reg("c3-answer", tTa, tLa, [("s", [23.5, 55.6], 400), ("e", [23.4, 55.5], 650)], **CH3b,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)], cities=[city(tTa, RUKLA, "Rukla", tTa + 0.3, RED, "target", 6), city(tTa, SIA, "Siauliai", tTa + 0.5, RED, "target", 6)],
    labels=[lab(tTa, [25.4, 56.2], "Target: NATO's ability to answer", W("p20", "ability"), YELLOW)], rings=[{"at": RUKLA, "km": 60, "color": BLUE, "t": rel(tTa, W("p20", "ability")), "dashed": True}, {"at": SIA, "km": 60, "color": BLUE, "t": rel(tTa, W("p20", "answer")), "dashed": True}])
reg("c3-sites", tLa, S("p21"), [("s", [21.8, 54.8], 500), ("e", [21.5, 54.9], 380)], **CH3b,
    countryLabels=[CL(PL, "POLAND", BLUE, 30), CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(tLa, LAUNCH, "Launch site: our choice", W("p20", "our"), AMBER, "base", 6), city(tLa, KALCITY, "Kaliningrad", tLa + 0.3, AMBER, "dot")],
    labels=[lab(tLa, [24.0, 54.2], "No real garrison claimed", W("p20", "claimed"), WHITE)])
a = S("p21")
tUn = W("p21", "Under")
reg("c3-nato", a, tUn, [("s", [15, 54], 3200), ("e", [12, 53], 3600)], clock="", highlight=[HLP, {"iso": DE, "color": BLUE, "fill": "rgba(110,168,255,0.08)"}, HLR] + HLB,
    countryLabels=[CL(LT, "LITHUANIA", BLUE), CL(PL, "POLAND", BLUE), CL(DE, "GERMANY", BLUE)], cities=[city(a, SIA, "Hit once", a + 0.3, RED, "target", 6), city(a, BREST_B, "NATO", a + 0.9, BLUE, "base", 6)],
    labels=[lab(a, [20.0, 59.5], "Will NATO call it an armed attack?", W("p21", "armed"), YELLOW)])
add(id="c3-art5", type="stamp", start=tUn, end=S("p22"), tag="SIMULATION", text="ARTICLE FIVE", line="an attack on one is an attack on all", color=BLUE)

# ================================================================== Chapter 04 [SIMULATION] hour by hour
a = chapter("c4-card", S("p22"), 3.5, "CHAPTER 04", "Hour by hour", "SIMULATION")
tUl = W("p22", "Unlike")
CH4 = dict(highlight=HLB + [HLR, HLP], legend=LEG)
reg("c4-kalibr", a, tUl, [("s", [22.5, 57.2], 900), (W("p22", "thirty-nine"), [22.8, 57.5], 700), ("e", [24.0, 58.2], 700)], clock="T+00:00", clockLabel="HOUR 6 · KALIBR FLIGHT", clockRate=180, **CH4,
    countryLabels=[CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)],
    cities=[city(a, SHIP_L, "Baltic Fleet corvette (simulated)", a + 0.1, AMBER, "base", 5), city(a, AMARI, "Amari Air Base, Estonia", W("p22", "Amari"), RED, "target", 6)],
    ships=[missile(a, [SHIP_L, AMARI], a + 0.1, S("p23") - 0.5, label="Kalibr (conv.)", color=RED, kind="pla", t_on=a + 0.1)])
reg("c4-watch", tUl, S("p23"), [("s", [24.5, 58.5], 600), ("e", [24.6, 59.0], 380)], clock="T+25:00", clockLabel="HOUR 6 · KALIBR FLIGHT", clockRate=60, **CH4,
    countryLabels=[CL(EE, "ESTONIA", BLUE, 30)],
    cities=[city(tUl, AMARI, "Amari Air Base", tUl + 0.2, RED, "target", 7), city(tUl, TALLINN, "Tallinn", tUl + 0.6)],
    ships=[missile(tUl, [[22.9, 57.7], AMARI], tUl, tUl + 6.0, label="Kalibr", color=RED, kind="pla", t_on=tUl)],
    labels=[lab(tUl, [28.0, 58.0], "Time to watch it come", tUl + 0.5, YELLOW)])
a = S("p23")
tBy2 = W("p23", "By")
reg("c4-tapa", a, tBy2, [("s", [27.0, 58.6], 650), (W("p23", "hits"), [26.5, 59.0], 520), ("e", [26.2, 59.2], 380)], clock="HOUR 11", clockLabel="TAPA, ESTONIA", clockRate=0, **CH4,
    countryLabels=[CL(EE, "ESTONIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(a, PSKOV_L, "Pskov region (launch, simulated)", a + 0.2, AMBER, "base", 5), city(a, TAPA, "Tapa army base", W("p23", "Tapa"), RED, "target", 7)],
    ships=[missile(a, [PSKOV_L, TAPA], W("p23", "Iskander"), tBy2, label="Iskander (conv.)", color=RED, kind="pla", t_on=W("p23", "Iskander"))])
reg("c4-art5", tBy2, S("p24"), [("s", [15, 55], 2600), (W("p23", "invoked"), [12, 52], 3000), ("e", [10, 52], 3400)], clock="HOUR 12", clockLabel="ARTICLE FIVE", clockRate=0, highlight=HLB + [HLP, {"iso": DE, "color": BLUE, "fill": "rgba(110,168,255,0.10)"}, HLR],
    cities=[city(tBy2, BREST_B, "NATO invokes Article 5 (simulated)", W("p23", "invoked"), BLUE, "target", 7), city(tBy2, TAPA, "Tapa", tBy2 + 0.3, RED, "dot")],
    lines=[line(tBy2, BREST_B, TALLINN, W("p23", "invoked"), W("p23", "invoked") + 2.0, BLUE), line(tBy2, BREST_B, SIA, W("p23", "invoked") + 0.3, W("p23", "invoked") + 2.4, BLUE)])
a = S("p24")
tRe = W("p24", "Reinforcements")
reg("c4-gap", a, tRe, [("s", [23.5, 54.4], 500), (W("p24", "close"), [23.5, 54.2], 360), ("e", [23.4, 54.1], 260)], clock="HOUR 12 TO 48", clockLabel="CLOSING ON THE GAP", clockRate=0, **CH4,
    countryLabels=[CL(PL, "POLAND", BLUE, 30), CL(BY, "BELARUS", AMBER, 30)],
    zones=[{"points": [[22.8, 54.35], [23.8, 53.75], [23.9, 54.2], [23.0, 54.45]], "label": "Suwalki Gap", "color": YELLOW, "t": 0.4, "pulse": True}],
    ships=[missile(a, [[20.8, 54.6], [22.9, 54.2]], a + 1.2, tRe, label="Russian forces", color=AMBER, kind="pla", t_on=a + 1.0), missile(a, [[26.0, 53.5], [23.8, 54.0]], a + 1.6, tRe, label="Belarusian forces", color=AMBER, kind="pla", t_on=a + 1.4)])
reg("c4-rail", tRe, S("p25"), [("s", [16, 53], 1600), (W("p24", "rail"), [20, 53.6], 1000), ("e", [23, 54.4], 800)], clock="HOUR 12 TO 48", clockLabel="REINFORCEMENTS", clockRate=0, **CH4,
    countryLabels=[CL(DE, "GERMANY", BLUE, 30), CL(PL, "POLAND", BLUE, 30)],
    cities=[city(tRe, BERLIN, "Germany, Netherlands", tRe + 0.2, BLUE, "base", 5), city(tRe, WARSAW, "Warsaw", tRe + 0.6), city(tRe, KAUNAS, "Kaunas", tRe + 1.0)],
    ships=[missile(tRe, [BERLIN, WARSAW, [23.6, 54.1], KAUNAS], tRe + 0.2, S("p25") - 0.5, label="NATO reinforcements", color=BLUE, kind="ally", t_on=tRe + 0.1)],
    labels=[lab(tRe, [24.5, 52.2], "One rail line: the bottleneck", W("p24", "rail"), TEAL)])
a = S("p25")
tWh = W("p25", "where")
reg("c4-orzysz", a, tWh, [("s", [22.5, 54.4], 480), (W("p25", "Orzysz"), [22.0, 54.0], 340), ("e", [21.9, 53.9], 250)], clock="HOUR 31", clockLabel="ORZYSZ, POLAND", clockRate=0, **CH4,
    countryLabels=[CL(PL, "POLAND", BLUE, 30)],
    cities=[city(a, LAUNCH, "Kaliningrad area", a + 0.2, AMBER, "base", 5), city(a, ORZYSZ, "Orzysz training area", W("p25", "Orzysz"), RED, "target", 7)],
    ships=[missile(a, [LAUNCH, ORZYSZ], W("p25", "Iskander"), tWh, label="Iskander (conv.)", color=RED, kind="pla", t_on=W("p25", "Iskander"))])
reg("c4-boar", tWh, S("p26"), [("s", [22.0, 53.8], 250), ("e", [22.0, 53.8], 380)], clock="HOUR 31", clockLabel="ORZYSZ, POLAND", clockRate=0, **CH4,
    cities=[city(tWh, ORZYSZ, "Orzysz", tWh + 0.2, RED, "target", 7), city(tWh, ELK, "Elk", tWh + 0.6)],
    labels=[lab(tWh, [23.0, 53.3], "Gallant Boar, June 2026 (one report)", W("p25", "Gallant"), YELLOW)], rings=[{"at": ORZYSZ, "km": 6, "color": RED, "t": rel(tWh, tWh + 0.6), "dashed": True}])
a = S("p26")
tSx, tTh2 = W("p26", "sixty"), W("p26", "That")
reg("c4-rand", a, tSx, [("s", [26.5, 57.5], 1500), (W("p26", "Tallinn"), [25.5, 58.0], 900), ("e", [24.8, 57.6], 700)], tag="REAL DATA", clock="RAND, 2016", clockLabel="WARGAMES", clockRate=0, source="RAND Corporation, 2016 wargames (as summarised)",
    highlight=HLB + [HLR, HLBY], countryLabels=[CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30), CL(RU, "RUSSIA", AMBER, 30)],
    cities=[city(a, TALLINN, "Tallinn", W("p26", "Tallinn"), RED, "target", 7), city(a, RIGA, "Riga", W("p26", "Riga"), RED, "target", 7)],
    lines=[line(a, PSKOV_C, TALLINN, W("p26", "outskirts"), W("p26", "outskirts") + 2.0, AMBER), line(a, [27.0, 55.5], RIGA, W("p26", "outskirts"), W("p26", "outskirts") + 2.0, AMBER)])
add(id="c4-60h", type="number", start=tSx, end=tTh2, tag="REAL DATA", value="AT MOST 60 HOURS", countTo=60, prefix="AT MOST ", suffix=" HOURS", label="RAND wargames, 2016: Russian forces at Tallinn or Riga", color=AMBER, source="RAND Corporation, 2016 wargames (as summarised)")
reg("c4-weaker", tTh2, S("p27"), [("s", [24.5, 57.5], 1100), ("e", [24.0, 56.5], 800)], clock="", highlight=HLB + [HLR, HLP], legend=LEG,
    cities=[city(tTh2, RIGA, "Riga", tTh2 + 0.3, BLUE, "base", 5), city(tTh2, TALLINN, "Tallinn", tTh2 + 0.6, BLUE, "base", 5)],
    labels=[lab(tTh2, [27.5, 56.0], "A weaker NATO posture", W("p26", "weaker"), AMBER), lab(tTh2, [27.5, 55.5], "Not a prediction", W("p26", "not"), YELLOW)])
a = S("p27")
tMs, tSm2, tOth = W("p27", "Moscow"), W("p27", "Some"), W("p27", "Others")
reg("c4-stall", a, tMs, [("s", [24.5, 56.5], 900), (W("p27", "aircraft"), [23.5, 55.8], 1100), ("e", [23.0, 55.5], 1400)], clock="HOUR 55", clockLabel="THE FIGHT STALLS", clockRate=0, **CH4,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(a, SUWALKI, "Suwalki Gap", a + 0.3, YELLOW, "target", 6), city(a, KAUNAS, "Kaunas", a + 0.6)],
    ships=[missile(a, [[15.0, 53.5], [19.0, 54.5], SUWALKI], W("p27", "NATO"), tMs, label="NATO aircraft", color=BLUE, kind="ally", t_on=W("p27", "NATO"))],
    labels=[lab(a, [26.8, 57.2], "The ground fight stalls", W("p27", "stalls"), WHITE)])
reg("c4-moscow", tMs, tSm2, [("s", [37.6, 55.7], 900), ("e", [33, 56], 2200)], clock="", highlight=[HLR, HLBY, HLU] + HLB,
    cities=[city(tMs, MOSCOW, "Moscow decides", tMs + 0.2, AMBER, "target", 7)], rings=[{"at": MOSCOW, "km": 80, "color": AMBER, "t": rel(tMs, tMs + 0.5), "dashed": True}],
    labels=[lab(tMs, [41.5, 58.4], "The war is turning against it", W("p27", "turning"), RED)])
reg("c4-some", tSm2, tOth, [("s", [30, 56], 2400), ("e", [26, 56], 1500)], clock="", highlight=[HLR, HLBY] + HLB,
    cities=[city(tSm2, MOSCOW, "Moscow", tSm2 + 0.2, AMBER, "base", 5), city(tSm2, SIA, "One limited use", W("p27", "limited"), RED, "target", 6)],
    labels=[lab(tSm2, [33.0, 59.4], "Some analysts: one use forces a deal", W("p27", "force"), YELLOW)])
reg("c4-others", tOth, S("p28"), [("s", [28, 57], 2000), ("e", [26, 56.5], 1200)], clock="", highlight=[HLR, HLBY] + HLB,
    cities=[city(tOth, MOSCOW, "Moscow", tOth + 0.2, AMBER, "base", 5), city(tOth, SIA, "Our choice, not a forecast", W("p27", "uses"), RED, "target", 6)],
    labels=[lab(tOth, [33.0, 59.4], "Others: no such policy exists", W("p27", "no"), TEAL)])
a = S("p28")
tTh3, tTh4, tDe = W("p28", "The"), W("p28", "The", 2), W("p28", "Defenders")
reg("c4-h61", a, tTh3, [("s", [23.0, 55.5], 520), (W("p28", "nuclear"), [23.0, 55.5], 380), ("e", [23.0, 55.6], 440)], clock="HOUR 61", clockLabel="ONE ISKANDER-M", clockRate=0, **CH4,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(a, KALCITY, "Kaliningrad", a + 0.2, AMBER, "base", 5), city(a, SIA, "Siauliai Air Base", W("p28", "Siauliai"), RED, "target", 7)],
    ships=[missile(a, [LAUNCH, SIA], W("p28", "nuclear"), tTh3 + 2.0, label="Iskander-M, nuclear", t_on=a + 0.3)])
reg("c4-base", tTh3, tTh4, [("s", SIA, 300), ("e", [23.35, 55.9], 190)], clock="HOUR 61", clockLabel="THE AIM POINT", clockRate=0, **CH4,
    cities=[city(tTh3, SIA, "Air base: the aim point", tTh3 + 0.2, RED, "target", 7), city(tTh3, SIAULIAI_C, "Siauliai (city)", W("p28", "city"), WHITE, "dot")],
    labels=[lab(tTh3, [24.4, 56.4], "A base, not a city", W("p28", "base"), YELLOW)])
reg("c4-warn", tTh4, tDe, [("s", [23.4, 55.6], 450), ("e", [23.4, 55.8], 300)], clock="T-03:10", clockLabel="TO IMPACT", clockRate=40, **CH4,
    cities=[city(tTh4, SIA, "Siauliai Air Base", tTh4 + 0.2, RED, "target", 7)], ships=[missile(tTh4, [[22.3, 55.1], SIA], tTh4, tDe + 0.5, label="", t_on=tTh4)],
    labels=[lab(tTh4, [25.0, 56.4], "No warning but sirens and jets", W("p28", "sirens"), YELLOW)])
reg("c4-know", tDe, S("p29"), [("s", [23.0, 55.6], 700), ("e", [23.3, 55.8], 400)], clock="T-00:40", clockLabel="TO IMPACT", clockRate=20, **CH4,
    cities=[city(tDe, SIA, "What does it carry?", tDe + 0.3, RED, "target", 7)], ships=[missile(tDe, [[22.6, 55.3], SIA], tDe, S("p29") - 0.2, label="Ballistic launch", t_on=tDe)],
    labels=[lab(tDe, [25.2, 56.6], "Defenders cannot know", W("p28", "know"), WHITE)])
a = S("p29")
tTe, tWt = W("p29", "ten"), W("p29", "What")
reg("c4-noyield", a, tTe, [("s", [21.5, 54.9], 600), ("e", [22.0, 55.1], 420)], clock="", highlight=[HLR] + HLB + [HLP],
    cities=[city(a, LAUNCH, "Iskander brigade (simulated)", a + 0.3, AMBER, "base", 6)], labels=[lab(a, [24.4, 56.0], "No published Iskander yield", W("p29", "published"), YELLOW)])
add(id="c4-10kt", type="number", start=tTe, end=tWt, tag="SIMULATION", value="10 KILOTONS", countTo=10, suffix=" KILOTONS", label="our choice, not a published figure", sub="about half of Nagasaki", color=RED, source="Scenario engine; Nagasaki about 21 kt")
add(id="c4-teaser", type="city", start=tWt, end=S("p30"), tag="SIMULATION", clock="HOUR 61", clockLabel="SIAULIAI AIR BASE", clockRate=0, city="siauliai", view={"center": SIA, "widthKm": 9.0}, gz=SIA,
    camera=[{"t": 0, "center": SIA, "widthKm": 9.0}, {"t": 3.0, "center": SIA, "widthKm": 5.0}], rings=[], legend=[], labels=[{"at": [SIA[0], SIA[1] + 0.006], "text": "Ten kilotons on one airfield?", "color": YELLOW, "t": 0.6}])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = chapter("c5-card", S("p30"), 2.4, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
RINGS = [("Fireball", FX["fireball_km"], WHITE, f"Fireball {FX['fireball_km'] * 1000:.0f} m radius"), ("20 psi", FX["psi20_km"], ORANGE, f"20 psi {FX['psi20_km'] * 1000:.0f} m"), ("5 psi", FX["psi5_km"], RED, f"5 psi {FX['psi5_km']:.2f} km"),
         ("Burns", FX["thermal3_km"], AMBER, f"Third-degree burns {FX['thermal3_km']:.1f} km"), ("1 psi", FX["psi1_km"], TEAL, f"Broken windows {FX['psi1_km']:.1f} km")]
LEGEND = [{"text": r[3], "color": r[2]} for r in RINGS]
HC = dict(clock="T+03:06", clockLabel="IMPACT · HOUR 61", clockRate=0, source="Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)")


def ring_at(i, t):
    nm, km, col, _ = RINGS[i]
    return {"km": km, "color": col, "label": nm, "t": t}


def prior(n):
    return [dict(ring_at(i, -30)) for i in range(n)]


def cty(sid, a, b, w0, w1, mid=None, **kw):
    keys = [{"t": 0, "center": SIA, "widthKm": w0}]
    if mid:
        keys.append({"t": round((b - a) * 0.5, 2), "center": SIA, "widthKm": mid})
    keys.append({"t": round(b - a, 2), "center": SIA, "widthKm": w1})
    d = dict(id=sid, type="city", start=a, end=b, tag="SIMULATION", city="siauliai", view={"center": SIA, "widthKm": w0}, camera=keys, gz=SIA, **HC)
    d.update(kw)
    add(**d)


def at(dlat, dlon=0.0):
    return [round(SIA[0] + dlon, 5), round(SIA[1] + dlat, 5)]


tC5 = round(a, 2)
tFlash = tC5  # the flash lands as the clock time is spoken
tEng, tAf = W("p30", "Every"), W("p30", "the", 5)
cty("h-flash", tFlash, tAf, 4.0, 2.4, mid=3.0, flashT=0.1, rings=[ring_at(0, 0.6)], legend=[],
    labels=[{"at": at(0.004), "text": "Siauliai Air Base: airburst", "color": WHITE, "t": 0.5}, {"at": at(-0.006), "text": "Every number: the engine's", "color": YELLOW, "t": rel(tFlash, tEng)}, {"at": at(-0.012), "text": "Every one is an estimate", "color": YELLOW, "t": rel(tFlash, W("p30", "estimate"))}],
    caption="A 10-kiloton airburst. Our choice of yield and burst height.")
a = tAf
cty("h-airfield", a, S("p31"), 2.4, 2.0, legend=LEGEND[:1], rings=prior(1), labels=[{"at": at(0.0045), "text": "Runway and hangars", "color": WHITE, "t": rel(a, W("p30", "runway"))}, {"at": at(-0.0045), "text": "What the base protects", "color": YELLOW, "t": rel(a, W("p30", "built"))}])
a = S("p31")
tIns = W("p31", "Inside")
cty("h-fireball", a, tIns, 1.0, 0.8, legend=LEGEND[:1], rings=[ring_at(0, 0.1)], labels=[{"at": at(0.0022), "text": "About 300 m across", "color": WHITE, "t": rel(a, W("p31", "three"))}])
cty("h-gone", tIns, S("p32"), 1.0, 1.5, legend=LEGEND[:1], rings=prior(1), labels=[{"at": at(0.0028), "text": "Runways, hangars, aircraft: gone", "color": RED, "t": rel(tIns, W("p31", "runways"))}])
a = S("p32")
cty("h-20psi", a, S("p33"), 1.2, 2.2, legend=LEGEND[:2], rings=prior(1) + [ring_at(1, 0.3)], caption="Reinforced concrete fails.")
a = S("p33")
tTh5 = W("p33", "The")
cty("h-5psi", a, tTh5, 2.2, 4.0, legend=LEGEND[:3], source="", rings=prior(2) + [ring_at(2, 0.3)], labels=[{"at": at(0.0125), "text": "Most buildings flattened", "color": WHITE, "t": rel(a, W("p33", "flattened"))}])
cty("h-area", tTh5, S("p34"), 4.0, 5.0, legend=LEGEND[:3], source="", rings=prior(3), labels=[{"at": at(-0.0125), "text": "About 6.7 km2 inside the ring", "color": YELLOW, "t": rel(tTh5, W("p33", "six"))}])
a = S("p34")
cty("h-burns", a, S("p35"), 4.0, 6.0, legend=LEGEND[:4], source="", rings=prior(3) + [ring_at(3, 0.3)], labels=[{"at": at(0.0225), "text": "Third-degree burns, bare skin", "color": WHITE, "t": rel(a, W("p34", "burns"))}])
a = S("p35")
cty("h-1psi", a, S("p36"), 7.0, 9.0, legend=LEGEND, source="", rings=prior(4) + [ring_at(4, 0.3)], labels=[{"at": at(0.036), "text": "Windows shatter", "color": WHITE, "t": rel(a, W("p35", "Windows"))}])
a = S("p36")
tBu, tFa = W("p36", "but"), W("p36", "burst")
cty("h-town", a, tBu, 12.0, 11.0, legend=LEGEND, source="", rings=prior(5),
    labels=[{"at": SIAULIAI_C, "text": "Siauliai city centre", "color": WHITE, "t": rel(a, W("p36", "centre"))}],
    short={"flashT": 0.1, "legend": [], "rings": [ring_at(i, round(0.5 + 0.45 * i, 2)) for i in range(5)],
           "camera": [{"t": 0, "center": SIA, "widthKm": 17.0}, {"t": 3.0, "center": SIA, "widthKm": 15.0}, {"t": round(tBu - a, 2), "center": SIA, "widthKm": 14.0}],
           "view": {"center": SIA, "widthKm": 17.0},
           "labels": [{"at": [SIA[0] - 0.05, SIA[1] + 0.012], "text": "SIAULIAI AIR BASE (GROUND ZERO)", "color": WHITE, "t": 0.2}, {"at": SIAULIAI_C, "text": "Siauliai city centre", "color": WHITE, "t": rel(a, W("p36", "centre"))}]})
cty("h-streets", tBu, tFa, 11.0, 9.0, legend=LEGEND, source="", rings=prior(5), labels=[{"at": at(-0.03, -0.045), "text": "Nearest streets: inside 1 psi", "color": YELLOW, "t": rel(tBu, W("p36", "nearest"))}], short={"legend": []})
cty("h-fallout", tFa, S("p37"), 9.0, 14.0, legend=LEGEND, source="", rings=prior(5), labels=[{"at": at(0.045, 0.0), "text": "High burst: little local fallout", "color": TEAL, "t": rel(tFa, W("p36", "little"))}], short={"legend": []})
a = S("p37")
tFe = W("p37", "For", 2)
reg("h-second", a, tFe, [("s", [23.4, 55.9], 150), ("e", [23.4, 55.9], 320)], clock="T+03:07", clockLabel="ABOUT ONE SECOND", clockRate=0, highlight=HLB, source="Scenario engine",
    cities=[city(a, SIA, "Base: the whole story", W("p37", "base"), RED, "target", 7), city(a, SIAULIAI_C, "Siauliai", a + 0.5)],
    rings=[{"at": SIA, "km": FX["psi1_km"], "color": TEAL, "t": 0.5, "label": "1 psi"}, {"at": SIA, "km": FX["psi5_km"], "color": RED, "t": 1.1, "label": "5 psi"}])
reg("h-after", tFe, S("p38"), [("s", [23.4, 55.9], 320), ("e", [24.0, 56.0], 900)], clock="T+03:07", clockLabel="THEN THE REST", clockRate=0, highlight=HLB + [HLP],
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)], cities=[city(tFe, SIA, "Siauliai Air Base", tFe + 0.2, RED, "target", 6), city(tFe, VILNIUS, "Vilnius", W("p37", "everyone")), city(tFe, KAUNAS, "Kaunas", tFe + 1.0)],
    labels=[lab(tFe, [26.5, 56.9], "For everyone else: after", W("p37", "begins"), YELLOW)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p38"), 3.0, "CHAPTER 06", "The day after", "SIMULATION")
tAt = W("p38", "At")
CH6 = dict(clock="DAY 1", clockRate=0)
reg("d1-base", a, tAt, [("s", [23.4, 55.9], 300), (W("p38", "stop"), [23.5, 55.8], 500), ("e", [23.4, 55.9], 380)], clockLabel="FIRST CHANGE: THE AIRFIELD", **CH6,
    cities=[city(a, SIA, "Siauliai Air Base", a + 0.3, RED, "target", 7), city(a, SIAULIAI_C, "Siauliai", a + 0.8)], labels=[lab(a, [25.0, 56.4], "Aimed at a base, not a city", W("p38", "base"), YELLOW)])
reg("d1-dark", tAt, S("p39"), [("s", SIA, 300), ("e", SIA, 190)], clockLabel="FIRST LIGHT", **CH6,
    cities=[city(tAt, SIA, "Dark gap on the map", tAt + 0.3, RED, "target", 7), city(tAt, SIAULIAI_C, "Siauliai", tAt + 1.0)], zones=[{"points": [[23.33, 55.87], [23.46, 55.87], [23.46, 55.92], [23.33, 55.92]], "label": "Jets go quiet", "color": GREY, "t": rel(tAt, W("p38", "quiet")), "pulse": True}])
a = S("p39")
tAs = W("p39", "as")
reg("d2-skies", a, tAs, [("s", [24.0, 57.5], 1100), (W("p39", "stop"), [24.5, 58.0], 1500), ("e", [24.5, 58.5], 1700)], clockLabel="SECOND CHANGE: CLOSED SKIES", **CH6,
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)],
    zones=[{"points": [[21.0, 54.0], [28.0, 54.0], [28.0, 59.8], [21.0, 59.8]], "label": "Flights stop (simulated)", "color": RED, "t": rel(a, W("p39", "Flights")), "pulse": True}])
reg("d2-finland", tAs, S("p40"), [("s", [26, 60.0], 700), (W("p39", "briefly"), [27, 60.0], 900), ("e", [27, 60.0], 600)], clockLabel="REAL, NOVEMBER 2026", **CH6, tag="REAL DATA", source="Reuters; Associated Press, November 2026",
    countryLabels=[CL(FI, "FINLAND", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)], cities=[city(tAs, HELSINKI, "Helsinki", tAs + 0.3)],
    zones=[{"points": [[24.0, 59.6], [29.5, 59.6], [29.5, 60.3], [24.0, 60.3]], "label": "Gulf of Finland: briefly restricted", "color": YELLOW, "t": rel(tAs, W("p39", "Finland")), "pulse": True}])
a = S("p40")
tSo2, tAn = W("p40", "so"), W("p40", "Any")
PL_ = lambda t0: {"at": SIA, "bearing": 90, "lengthKm": 90, "widthKm": 16, "t0": t0, "t1": t0 + 5, "color": AMBER, "label": "Illustrative only"}
reg("d3-wind", a, tSo2, [("s", [22.0, 56.0], 400), (W("p40", "westerly"), [23.0, 56.0], 550), ("e", [23.6, 55.9], 700)], clockLabel="THIRD CHANGE: THE DUST", **CH6,
    cities=[city(a, SIA, "Burst point", a + 0.3, RED, "target", 6), city(a, SIAULIAI_C, "Siauliai", a + 0.9)],
    lines=[line(a, [21.4, 56.3], [22.7, 56.0], W("p40", "westerly"), W("p40", "westerly") + 2.0, WHITE, label="Light westerly wind (our choice)")])
reg("d3-plume", tSo2, tAn, [("s", [24.0, 55.9], 500), ("e", [25.5, 55.9], 800)], clockLabel="THIRD CHANGE: THE DUST", **CH6, source="Scenario engine; wind is our assumption",
    cities=[city(tSo2, SIA, "Burst point", tSo2 + 0.2, RED, "target", 6), city(tSo2, [26.4, 55.9], "Lithuanian farmland", W("p40", "farmland"), WHITE, "dot")],
    plume=PL_(0.6), labels=[lab(tSo2, [27.0, 56.6], "A thin drift, east", W("p40", "thin"), AMBER)])
reg("d3-ill", tAn, S("p41"), [("s", [25.5, 55.9], 800), ("e", [26.0, 56.0], 1200)], clockLabel="NO DISTANCE, NO DOSE", **CH6, source="Scenario engine; wind is our assumption",
    cities=[city(tAn, SIA, "Burst point", tAn + 0.2, RED, "target", 6)], plume=PL_(0.3),
    labels=[lab(tAn, [27.8, 56.7], "The engine gives no distance", W("p40", "distance"), YELLOW), lab(tAn, [27.8, 56.2], "and no dose", W("p40", "dose"), YELLOW)])
a = S("p41")
tTr, tWe = W("p41", "Three"), W("p41", "We")
reg("d4-treaty", a, tTr, [("s", [8, 51], 1400), (W("p41", "Article"), [8, 51], 1800), ("e", [6, 51], 2300)], clockLabel="FOURTH CHANGE: BRUSSELS", **CH6, tag="SIMULATION",
    cities=[city(a, BREST_B, "NATO, Brussels", a + 0.3, BLUE, "target", 7)], rings=[{"at": BREST_B, "km": 120, "color": BLUE, "t": rel(a, W("p41", "consult")), "dashed": True}],
    labels=[lab(a, [11.0, 53.6], "Allies consult when threatened", W("p41", "consult"), BLUE), lab(a, [11.0, 52.9], "Article 5 allows armed force", W("p41", "five"), RED)])
reg("d4-options", tTr, tWe, [("s", [4.35, 51.5], 1500), ("e", [4.35, 51.0], 1000)], clockLabel="THREE OPTIONS", **CH6,
    cities=[city(tTr, BREST_B, "The table in Brussels", tTr + 0.2, BLUE, "target", 7)],
    labels=[lab(tTr, [8.0, 53.2], "1. Reply in kind", W("p41", "kind"), RED), lab(tTr, [8.0, 52.6], "2. Reply conventionally", W("p41", "conventionally"), ORANGE), lab(tTr, [8.0, 52.0], "3. Stop and talk", W("p41", "stop"), TEAL)])
add(id="d4-nopick", type="stamp", start=tWe, end=S("p42"), tag="SIMULATION", text="WE DO NOT PICK ONE", line="the decision is still open", color=YELLOW)
a = S("p42")
tNo2, tRb = W("p42", "Nothing"), W("p42", "Rail", 2)
reg("d5-gap", a, tNo2, [("s", [23.0, 54.4], 600), (W("p42", "single-track"), [23.3, 54.2], 380), ("e", [23.3, 54.2], 300)], clockLabel="FIFTH CHANGE: THE BOTTLENECK", **CH6,
    highlight=HLB + [HLP, HLBY], countryLabels=[CL(PL, "POLAND", BLUE, 30), CL(LT, "LITHUANIA", BLUE, 30)],
    zones=[{"points": [[22.8, 54.35], [23.8, 53.75], [23.9, 54.2], [23.0, 54.45]], "label": "Suwalki Gap", "color": YELLOW, "t": 0.4}],
    lines=[line(a, [21.0, 52.2], [23.6, 54.1], a + 1.0, a + 3.0, TEAL, False), line(a, [23.6, 54.1], KAUNAS, a + 2.5, a + 4.0, TEAL, False)],
    labels=[lab(a, [25.3, 53.3], "One single-track rail line", W("p42", "single-track"), TEAL)])
reg("d5-nowider", tNo2, tRb, [("s", [23.3, 54.2], 320), ("e", [23.3, 54.4], 700)], clockLabel="THE STRIKE DOES NOT WIDEN IT", **CH6,
    highlight=HLB + [HLP, HLBY], cities=[city(tNo2, SIA, "Siauliai", tNo2 + 0.3, RED, "base", 5), city(tNo2, KAUNAS, "Kaunas", tNo2 + 0.6)],
    labels=[lab(tNo2, [25.4, 55.6], "Nothing widens it", W("p42", "widens"), YELLOW)])
reg("d5-baltica", tRb, S("p43"), [("s", [24.0, 55.5], 1200), (W("p42", "construction"), [24.2, 56.5], 1000), ("e", [24.2, 57.0], 1100)], clockLabel="RAIL BALTICA", **CH6,
    highlight=HLB + [HLP], countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30), CL(EE, "ESTONIA", BLUE, 30)],
    lines=[line(tRb, WARSAW, KAUNAS, tRb + 0.3, tRb + 2.0, TEAL, True), line(tRb, KAUNAS, RIGA, tRb + 1.5, tRb + 3.0, TEAL, True), line(tRb, RIGA, TALLINN, tRb + 2.5, tRb + 4.0, TEAL, True)],
    cities=[city(tRb, RIGA, "Riga", tRb + 1.5), city(tRb, TALLINN, "Tallinn", tRb + 2.5)], labels=[lab(tRb, [27.0, 55.2], "Rail Baltica: still being built", W("p42", "construction"), TEAL)])
a = S("p43")
tLv, tAl = W("p43", "leaving"), W("p43", "Allies")
reg("d6-cut", a, tLv, [("s", [10.5, 50.5], 1100), (W("p43", "five"), [10.5, 50.5], 1500), ("e", [10.5, 50.5], 1900)], clockLabel="SIXTH CHANGE: THINNER HELP", **CH6, tag="REAL DATA", source="Pentagon announcement, 1 May 2026",
    highlight=[{"iso": DE, "color": BLUE, "fill": "rgba(110,168,255,0.12)"}], countryLabels=[CL(DE, "GERMANY", BLUE)], cities=[city(a, [7.6, 49.44], "Ramstein area", a + 0.4, BLUE, "base", 6), city(a, BERLIN, "Berlin", a + 0.8)],
    labels=[lab(a, [15.5, 53.4], "Up to 5,000 troops leave Germany", W("p43", "five"), YELLOW)])
add(id="d6-80k", type="number", start=tLv, end=tAl, tag="REAL DATA", value="ABOUT 80,000", countTo=80000, prefix="ABOUT ", label="US troops left in Europe", sub="after the cut: about 34,000 in Germany", color=BLUE, source="Pentagon announcement, 1 May 2026; Stars and Stripes")
reg("d6-ask", tAl, S("p44"), [("s", [14, 52], 2800), ("e", [18, 53], 2000)], clockLabel="ALLIES ASK", **CH6, tag="SIMULATION",
    highlight=HLB + [HLP, {"iso": DE, "color": BLUE, "fill": "rgba(110,168,255,0.08)"}], cities=[city(tAl, BREST_B, "Allies ask what it means", tAl + 0.3, BLUE, "base", 6), city(tAl, SIA, "After the strike", tAl + 1.2, RED, "target", 6)])
a = S("p44")
tSo3, tAnd, tEs = W("p44", "so"), W("p44", "and"), W("p44", "Estimates")
add(id="d7-start", type="stamp", start=a, end=tSo3, tag="REAL DATA", text="NEW START EXPIRED", line="5 February 2026", color=AMBER, source="CRS, 27 May 2026")
add(id="d7-noinsp", type="stamp", start=tSo3, end=tAnd, tag="REAL DATA", text="NO INSPECTOR COUNTS THEM", line="strategic warheads, either side", color=WHITE, source="CRS, 27 May 2026")
add(id="d7-tactical", type="stamp", start=tAnd, end=tEs, tag="REAL DATA", text="TACTICAL WEAPONS: NEVER COVERED", color=WHITE, source="CRS, 27 May 2026")
tTo = W("p44", "to")
add(id="d7-low", type="bars", start=tEs, end=tTo, tag="REAL DATA", title="Russia's tactical nuclear warheads", sub="estimates only · no treaty counts them", source="Federation of American Scientists; CRS, 2026",
    bars=[{"label": "Lower estimate", "value": 1500, "display": "about 1,500", "color": AMBER}, {"label": "Upper estimate", "value": 0, "display": "", "color": RED}])
add(id="d7-bars", type="bars", start=tTo, end=S("p45"), tag="REAL DATA", title="Russia's tactical nuclear warheads", sub="estimates only · no treaty counts them", source="Federation of American Scientists; CRS, 2026",
    bars=[{"label": "Lower estimate", "value": 1500, "display": "about 1,500", "color": AMBER}, {"label": "Upper estimate", "value": 2000, "display": "about 2,000", "color": RED}])
a = S("p45")
tIn4, tIn5 = W("p45", "In"), W("p45", "In", 2)
glob("d8-ladder", a, tIn4, [("s", 50, 25, 900), ("e", 48, 15, 1300)], clock="", highlight=[HLR] + HLB + [HLP],
     markers=[{"at": SIA, "label": "Hour 61", "color": RED, "kind": "target", "t": 0.3}, {"at": KALCITY, "label": "Where this leads?", "color": YELLOW, "kind": "dot", "t": rel(a, W("p45", "leads"))}])
glob("d8-plana", tIn4, tIn5, [("s", 48, 15, 1300), ("e", 45, -20, 800)], clock="", source="Princeton, Science and Global Security: Plan A (2019)", highlight=[HLR, {"iso": US, "color": BLUE, "fill": "rgba(110,168,255,0.06)"}] + HLB,
     markers=[{"at": SIA, "label": "A war that begins in Europe", "color": RED, "kind": "target", "t": 0.3}, {"at": [-77.04, 38.9], "label": "Strategic strikes", "color": BLUE, "kind": "dot", "t": rel(tIn4, W("p45", "strategic"))}],
     arcs=[{"from": SIA, "to": [-77.04, 38.9], "t0": rel(tIn4, W("p45", "tactical")), "t1": rel(tIn4, W("p45", "tactical")) + 3.5, "color": RED, "loft": 0.3}], caption="Princeton Plan A: a model, not this simulation.")
reg("d8-small", tIn5, S("p46"), [("s", [23.0, 55.6], 900), ("e", [23.4, 55.9], 500)], clock="", source="Princeton, Science and Global Security: Plan A (2019)", highlight=HLB + [HLR, HLP],
    countryLabels=[CL(LT, "LITHUANIA", BLUE, 30), CL(LV, "LATVIA", BLUE, 30)],
    cities=[city(tIn5, KALCITY, "Kaliningrad", tIn5 + 0.3, AMBER, "base", 5), city(tIn5, SIA, "The tactical phase: a small fraction", W("p45", "small"), RED, "target", 6)])
a = S("p46")
reg("z-quiet", a, S("p47"), [("s", [23.4, 55.9], 420), ("e", [23.4, 55.9], 260)], clock="DAWN", clockLabel="DAY 1", clockRate=0, highlight=HLB, countryLabels=[CL(LT, "LITHUANIA", BLUE, 30)],
    cities=[city(a, SIA, "Quiet at dawn", W("p46", "quiet"), RED, "target", 7), city(a, SIAULIAI_C, "Siauliai", a + 0.4)], labels=[lab(a, [24.5, 56.3], "The decision is still open", W("p46", "open"), YELLOW)])
# ================================================================== End slate
add(id="end", type="endslate", start=S("p47"), end=END, tag="", title="Next scenario", line="One Tsar Bomba-class warhead over New York.")


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
        for a_, b_ in zip(times, times[1:]):
            limit = 3.6 if a_ < 90 else 5.4
            if b_ - a_ <= limit:
                continue
            s = next((x for x in shots if x["start"] <= a_ + 1e-6 < x["end"]), None)
            if not s or s["type"] not in ("region", "globe", "city") or "camera" not in s:
                continue
            n = math.ceil((b_ - a_) / limit) - 1
            fields = ["center", "widthKm"] if s["type"] in ("region", "city") else ["lat", "lon", "scale"]
            for i in range(1, n + 1):
                tt = round(a_ + (b_ - a_) * i / (n + 1) - s["start"], 2)
                key = {"t": tt}
                key.update(interp(s["camera"], tt, fields))
                s["camera"].append(key)
            s["camera"].sort(key=lambda k: k["t"])
            changed = True
        if not changed:
            break


def floors():
    """No region view under 150 km (city shots are exempt)."""
    for s in shots:
        if s["type"] != "region":
            continue
        for k in s["camera"]:
            k["widthKm"] = max(k["widthKm"], 150)
        s["view"]["widthKm"] = max(s["view"]["widthKm"], 150)


for s_ in shots:
    if s_["id"] in ("c1-arsenal", "c1-answer", "c1-kal", "c1-iskander"):
        s_.setdefault("short", {})["source"] = ""
floors()
densify()

# ------------------------------------------------------------------ audio plan and output
booms = [FL + 0.1, tH61 + 0.1, tFlash + 0.1]
b0 = round(min(FL + 0.1 - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p17") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p17") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
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
