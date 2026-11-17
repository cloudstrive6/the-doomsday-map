"""Director pass for episode 010: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 010-tsar-bomba-over-new-york
One simulated 50 Mt airburst over lower Manhattan (city file new-york.json), a 800 kt comparison on the same map, and
the real 1961 and 1954 tests on region and globe shots. No real calendar date; clocks count T- and T+.
"""
import json
import math
import re
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


# ------------------------------------------------------------------ effects (scenario engine)
HERO = next(s for s in sc["strikes"] if s["id"] == "hero-50mt")
CMP = next(s for s in sc["strikes"] if s["id"] == "scale-800kt")
FX, FC = HERO["effects"], CMP["effects"]
GZ = [HERO["target_lon"], HERO["target_lat"]]
REL = [HERO["launch_lon"], HERO["launch_lat"]]          # release point over the North Atlantic (simulated)
ARCTIC = [CMP["launch_lon"], CMP["launch_lat"]]
NZ = [54.9, 73.8]                                      # Novaya Zemlya test site area
BIKINI, MOSCOW, LONDON, WASH = [165.38, 11.6], [37.62, 55.75], [-0.13, 51.5], [-77.04, 38.9]
US_, RU_ = "840", "643"
HLR = {"iso": RU_, "color": AMBER, "fill": "rgba(242,176,30,0.08)"}
HLU = {"iso": US_, "color": BLUE, "fill": "rgba(110,168,255,0.07)"}


def off(dx, dy):
    """Lon/lat of a point dx km east and dy km north of ground zero."""
    return [round(GZ[0] + dx / (111.32 * math.cos(math.radians(GZ[1]))), 4), round(GZ[1] + dy / 110.57, 4)]


def circle(km, n=48):
    return [off(km * math.cos(2 * math.pi * i / n), km * math.sin(2 * math.pi * i / n)) for i in range(n)]


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


def ship(a, path, t0, t1, label="", color=WHITE, kind="pla", t_on=None):
    return {"path": path, "t0": rel(a, t0), "t1": rel(a, t1), "kind": kind, "color": color, "label": label, "size": 1.8, "t": rel(a, t0 if t_on is None else t_on), "wake": True}


def line(a, p, q, t0, t1, color=WHITE, dashed=True, label=None, width=None):
    d = {"from": p, "to": q, "color": color, "dashed": dashed, "t0": rel(a, t0), "t1": rel(a, t1)}
    if label:
        d["label"] = label
    if width:
        d["width"] = width
    return d


def ring(a, at, km, t, label="", color=RED, dashed=False):
    return {"at": at, "km": km, "label": label, "color": color, "t": rel(a, t), "dashed": dashed}


def cam(a, b, *keys):
    out = []
    for t, c, w in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t) if t > 0 else 0)
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def reg(sid, a, b, keys, tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, **kw)


def _rkm(km):
    """The city map prints the ring radius after the label: round it so one number shows."""
    return round(km) if km >= 10 else round(km, 1)


_RNAMES = [(FX["fireball_km"], "Fireball"), (FX["psi20_km"], "20 psi"), (FX["psi5_km"], "5 psi"), (FX["thermal3_km"], "Burns"), (FX["psi1_km"], "Windows"),
           (FC["fireball_km"], "800 kt fireball"), (FC["psi5_km"], "800 kt 5 psi"), (FC["thermal3_km"], "800 kt burns"), (FC["psi1_km"], "800 kt windows")]


def _rlabel(r):
    """Name only (the engine appends the radius): strip any km figure from the text, name unlabelled rings."""
    t = re.sub(r"[:,]?\s*(radius |about |under |almost )?[\d.,]+ ?km( wide| across| in radius)?", "", r["label"], flags=re.I).strip(" :,")
    t = re.sub(r"^(Almost) in radius$", "5 psi", t)
    if not t:
        t = next((n for k, n in _RNAMES if abs(k - r["km"]) < 1e-6), "")
    return t


def cty(sid, a, b, keys, rings=(), labels=(), tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    add(id=sid, type="city", start=a, end=b, tag=tag, city="new-york", view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, gz=GZ, camera=c,
        rings=[{"km": _rkm(r["km"]), "label": _rlabel(r), "color": r["color"], "t": r["t"], "angle": (215 + 25 * i) % 360} for i, r in enumerate(rings)], labels=list(labels), **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **kw)


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=a, end=round(a + dur, 2), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 2)


def num(sid, a, b, value, countTo=None, label="", sub="", color=WHITE, tag="SIMULATION", **kw):
    d = dict(id=sid, type="number", start=a, end=b, tag=tag, value=value, label=label, sub=sub, color=color)
    if countTo is not None:
        d["countTo"] = countTo
    d.update(kw)
    add(**d)


def stamp(sid, a, b, text, line_="", color=WHITE, tag="SIMULATION", **kw):
    add(id=sid, type="stamp", start=a, end=b, tag=tag, text=text, line=line_, color=color, **kw)


# ================================================================== Cold open [SIMULATION]
FL = 2.0   # the cut lands on the flash; the flash itself is at +0.1 in the city shot
CO = dict(clockRate=1)
reg("open-run", 0, FL, [("s", off(-40, 10), 260), ("e", off(-8, 3), 150)], clock="T-00:02", clockLabel="TO BURST", clockRate=1,
    cities=[city(0, GZ, "Lower Manhattan", 0.0, RED, "target", 6), city(0, off(-20, -4), "Newark", 0.15), city(0, off(13, -5), "Brooklyn", 0.3), city(0, off(-6, 14), "Hudson River", 0.5)],
    lines=[line(0, off(-60, 8), GZ, 0.0, 1.9, WHITE)],
    ships=[ship(0, [off(-60, 8), GZ], 0.0, 1.95, label="Bomber", t_on=0.0)])
a = FL
cty("open-flash", a, S("p02"), [("s", GZ, 14), (2.0, GZ, 22), ("e", GZ, 34)], clock="T+00:00", clockLabel="NEW YORK · SIMULATED", clockRate=1,
    flashT=0.1, rings=[ring(a, GZ, FX["fireball_km"], a + 0.7, "Fireball: 9.2 km wide", WHITE), ring(a, GZ, FX["psi20_km"], a + 2.6, "20 psi", RED)],
    labels=[lab(a, off(0, 7.5), "Lower Manhattan", a + 1.0, WHITE)], caption="One 50 megaton airburst. Simulation: it has not happened.")
a = S("p02")
reg("open-sim", a, S("p03"), [("s", off(0, 0), 330), (W("p02", "published"), off(-12, 3), 230), ("e", off(-6, 2), 160)], clock="T+00:20", clockLabel="AFTER THE FLASH", clockRate=0, tag="SIMULATION",
    countryLabels=[{"iso": US_, "text": "UNITED STATES", "color": BLUE}],
    cities=[city(a, GZ, "Ground zero", a + 0.3, RED, "target", 6), city(a, off(-28, -6), "Newark", W("p02", "built")), city(a, off(20, -6), "Brooklyn", W("p02", "numbers"))],
    labels=[lab(a, off(40, 32), "A simulation: not a prediction", W("p02", "simulation"), YELLOW), lab(a, off(40, -32), "It has not happened", W("p02", "not"), RED)])
a = S("p03")
tKm = W("p03", "kilometres")
reg("open-bomber", a, W("p03", "North"), [("s", [-68.6, 40.5], 1400), (W("p03", "heavy"), [-69.4, 40.5], 1250), ("e", [-70.2, 40.5], 1100)], clock="T-62:00", clockLabel="TO BURST", clockRate=0,
    cities=[city(a, REL, "Heavy bomber (simulated)", a + 0.2, WHITE, "base", 6), city(a, GZ, "New York", a + 0.5, RED, "target", 6)],
    lines=[line(a, REL, GZ, a + 0.3, tKm + 1.5, WHITE, True, "About 930 km")])
a = W("p03", "North")
reg("open-atlantic", a, S("p04"), [("s", [-68.0, 40.6], 1100), (W("p03", "one"), [-70.0, 40.7], 700), ("e", [-72.0, 40.7], 520)], clock="T-62:00", clockLabel="TO BURST", clockRate=0,
    cities=[city(a, REL, "Release point", a + 0.2, WHITE, "base", 6), city(a, GZ, "New York", a + 0.4, RED, "target", 6)],
    ships=[ship(a, [REL, GZ], W("p03", "one"), S("p04") - 0.3, label="One bomb aboard", t_on=W("p03", "one"))],
    labels=[lab(a, [-69.0, 38.6], "North Atlantic", a + 0.3, GREY)])
a = S("p04")
tHow = W("p04", "How")
glob("open-nz", a, tHow, [("s", 66, 62, 900), (W("p04", "largest"), 70, 60, 1500), ("e", 73, 56, 2400)], tag="REAL DATA", clock="", highlight=[HLR],
     markers=[{"at": NZ, "label": "Largest bomb ever tested: 1961", "color": AMBER, "kind": "target", "size": 6, "t": rel(a, W("p04", "largest"))}],
     arcs=[{"from": NZ, "to": GZ, "t0": rel(a, W("p04", "size")), "t1": rel(a, W("p04", "size")) + 3.0, "color": WHITE, "loft": 0.3}])
reg("open-reach", tHow, S("p05"), [("s", GZ, 260), (W("p04", "reach"), GZ, 170), ("e", off(0, 4), 120)], clock="", tag="SIMULATION",
    cities=[city(tHow, GZ, "Lower Manhattan", tHow + 0.3, RED, "target", 6), city(tHow, off(-22, -6), "Newark", tHow + 1.2), city(tHow, off(24, -6), "Brooklyn", tHow + 1.6)],
    rings=[ring(tHow, GZ, FX["psi5_km"], W("p04", "reach"), "How far?", YELLOW, True)],
    labels=[lab(tHow, off(-60, 36), "A map you know", W("p04", "map"), WHITE)])

# ================================================================== Chapter 01 [REAL DATA] the bomb that was tested
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "The bomb that was tested", "REAL DATA")
SRC1 = "Arms Control Center; RFE/RL; Nuclear Weapon Archive"
CL1 = dict(clock="30 OCT 1961", clockLabel="NOVAYA ZEMLYA", clockRate=0)
tNZ = W("p05", "Novaya")
reg("c1-bomber", a, S("p06"), [("s", [48.0, 71.0], 2200), (tNZ, [52.0, 72.5], 1500), ("e", [55.0, 73.5], 1100)], tag="REAL DATA", source=SRC1, **CL1, highlight=[HLR],
    countryLabels=[{"iso": RU_, "text": "SOVIET UNION", "color": AMBER}],
    cities=[city(a, NZ, "Novaya Zemlya", tNZ, AMBER, "target", 6)],
    ships=[ship(a, [[40.0, 69.0], NZ], a + 0.2, S("p06") - 0.3, label="Soviet bomber", color=AMBER, t_on=a + 0.2)],
    labels=[lab(a, [53.0, 70.0], "Climbs to about 10.5 km", W("p05", "climbs"), WHITE), lab(a, [53.0, 69.0], "An island in the Arctic", W("p05", "island"), AMBER)])
a = S("p06")
tEi = W("p06", "eight")
num("c1-tonnes", a, tEi, "27 TONNES", countTo=27, suffix=" TONNES", label="the bomb's weight", sub="hung under a parachute", color=AMBER, tag="REAL DATA", source=SRC1)
num("c1-metres", tEi, tEi + 3.2, "8 METRES", countTo=8, suffix=" METRES", label="the bomb's length", color=AMBER, tag="REAL DATA", source=SRC1)
tPa = tEi + 3.2
reg("c1-chute", tPa, S("p07"), [("s", [55, 73.5], 600), (W("p06", "three"), [55, 73.5], 420), ("e", [55, 73.2], 300)], tag="REAL DATA", source=SRC1, **CL1, highlight=[HLR],
    cities=[city(tPa, NZ, "Release point", tPa + 0.2, AMBER, "target", 6)],
    ships=[ship(tPa, [[53.0, 73.9], [56.5, 73.7]], tPa + 0.2, S("p07") - 0.5, label="Bomber flies clear", color=AMBER, t_on=tPa + 0.2)],
    labels=[lab(tPa, [57.0, 74.9], "Parachute: about 3 minutes", W("p06", "parachute", 2), YELLOW)])
a = S("p07")
tSv, tAm = W("p07", "Soviet"), W("p07", "American")
reg("c1-burst", a, tSv, [("s", NZ, 800), ("e", NZ, 500)], tag="REAL DATA", source=SRC1, **CL1, highlight=[HLR], burst={"at": NZ, "t": 0.1, "km": 9, "fade": 4},
    labels=[lab(a, [56.0, 75.5], "Explodes at about 4,000 m", W("p07", "explodes"), WHITE)])
num("c1-50", tSv, tAm, "50 MEGATONS", countTo=50, suffix=" MEGATONS", label="the Soviet figure for the 1961 test", color=AMBER, tag="REAL DATA", source=SRC1)
reg("c1-58", tAm, S("p08"), [("s", NZ, 900), (W("p07", "published"), [48, 72], 1500), ("e", [40, 68], 2200)], tag="REAL DATA", source=SRC1, **CL1, highlight=[HLR],
    cities=[city(tAm, NZ, "1961 test: 50 Mt (Soviet figure)", tAm + 0.2, AMBER, "target", 6)],
    labels=[lab(tAm, [54.0, 70.4], "American estimates: higher", W("p07", "estimates"), BLUE), lab(tAm, [54.0, 69.2], "Published: up to about 58 Mt", W("p07", "fifty-eight"), YELLOW)])
a = S("p08")
tCl, tSh, tPr = W("p08", "cloud"), W("p08", "shock"), W("p08", "pressure")
reg("c1-fireball", a, tCl, [("s", NZ, 400), ("e", NZ, 200)], tag="REAL DATA", source=SRC1, **CL1, highlight=[HLR], burst={"at": NZ, "t": 0.1, "km": 8, "fade": 3},
    rings=[ring(a, NZ, 4.0, a + 0.3, "Fireball: radius", WHITE)])
num("c1-cloud", tCl, tSh, "65 KM", countTo=65, suffix=" KM", label="how high the cloud climbs", color=AMBER, tag="REAL DATA", source=SRC1)
num("c1-pushed", tSh, tPr - 0.35, "1,000 M", countTo=1000, suffix=" M", label="the shock wave pushes the bomber down", color=AMBER, tag="REAL DATA", source=SRC1)
glob("c1-earth", tPr - 0.35, S("p09"), [("s", 40, 70, 900), ("e", 10, 120, 1100)], tag="REAL DATA", source=SRC1, clock="", highlight=[HLR],
     markers=[{"at": NZ, "label": "Pressure wave circles the Earth 3 times", "color": AMBER, "kind": "target", "size": 6, "t": 0.2}],
     arcs=[{"from": NZ, "to": [-125.0, -73.0], "t0": 0.4, "t1": 2.4, "color": WHITE, "loft": 0.05}, {"from": NZ, "to": [-125.0, -73.0], "t0": rel(tPr, W("p08", "three")), "t1": rel(tPr, W("p08", "three")) + 2.0, "color": YELLOW, "loft": 0.08}])
a = S("p09")
tNine, tAg = W("p09", "nine"), W("p09", "against")
cty("c1-ours", a, tAg, [("s", GZ, 18), (tNine, GZ, 14), ("e", GZ, 24)], clock="", rings=[ring(a, GZ, FX["fireball_km"], a + 0.4, "Our engine: radius", WHITE)],
    labels=[lab(a, off(0, 7.0), "The fireball at the start of this video", W("p09", "start"), YELLOW)])
cty("c1-1961", tAg, S("p10"), [("s", GZ, 24), ("e", GZ, 12)], clock="", rings=[ring(tAg, GZ, FX["fireball_km"], tAg + 0.1, "Ours: radius", WHITE), ring(tAg, GZ, 4.0, tAg + 0.5, "1961: radius", AMBER)],
    labels=[lab(tAg, off(0, -8.0), "Same size on the same map", tAg + 1.5, WHITE)])
a = S("p10")
tSw, tRm = W("p10", "swapped"), W("p10", "removed")
reg("c1-twice", a, tSw, [("s", NZ, 900), (W("p10", "August"), [52, 72], 1500), ("e", [50, 70], 2000)], tag="REAL DATA", source=SRC1, clock="AUG 1961", clockLabel="THE DESIGN CHANGE", clockRate=0, highlight=[HLR],
    cities=[city(a, NZ, "The test site", a + 0.3, AMBER, "target", 6)],
    labels=[lab(a, [58.0, 70.0], "Full design: about 100 Mt", W("p10", "twice"), RED), lab(a, [58.0, 68.8], "Tested: 50 Mt", W("p10", "August"), AMBER)])
stamp("c1-lead", tSw, tRm, "URANIUM SWAPPED FOR LEAD", "Sakharov's team, final stage", AMBER, tag="REAL DATA", source=SRC1)
num("c1-97", tRm, S("p11"), "97%", countTo=97, suffix="%", label="of the fallout removed", sub="the full design would have been far dirtier", color=AMBER, tag="REAL DATA", source=SRC1)
a = S("p11")
tLg, tFe, tSs = W("p11", "largest"), W("p11", "Federation"), W("p11", "SS-18")
glob("c1-missile", a, tLg, [("s", 60, 50, 1000), ("e", 50, 5, 1300)], tag="REAL DATA", source=SRC1, clock="", highlight=[HLR, HLU],
     markers=[{"at": MOSCOW, "label": "Too big for any missile of its time", "color": AMBER, "kind": "base", "size": 5, "t": rel(a, W("p11", "missile"))}],
     arcs=[{"from": MOSCOW, "to": WASH, "t0": rel(a, W("p11", "big")), "t1": rel(a, W("p11", "big")) + 2.5, "color": GREY, "loft": 0.4}])
reg("c1-small", tLg, tSs, [("s", GZ, 900), (W("p11", "far"), GZ, 500), ("e", GZ, 300)], tag="REAL DATA", clock="", cities=[city(tLg, GZ, "Missiles today", tLg + 0.3, BLUE, "base", 6)],
    labels=[lab(tLg, off(40, 30), "Largest missile warheads today", W("p11", "largest"), BLUE), lab(tLg, off(40, 20), "Far smaller", W("p11", "far"), WHITE), lab(tLg, off(40, 10), "Federation of American Scientists", W("p11", "Federation"), YELLOW)])
add(id="c1-bars2", type="bars", start=tSs, end=tSs + 5.2, tag="REAL DATA", title="Warhead yield, in kilotons", sub="the 1961 bomb against missile warheads today", source="Federation of American Scientists; Arms Control Center",
    bars=[{"label": "1961 bomb", "value": 50000, "display": "50,000 kt", "color": AMBER}, {"label": "Russia SS-18 (500 to 800 kt)", "value": 800, "display": "up to 800 kt", "color": BLUE}])
a = tSs + 5.2
glob("c1-since", a, S("p13"), [("s", 55, 30, 1000), (W("p12", "fired"), 40, 0, 1100), ("e", 30, -60, 1200)], tag="REAL DATA", clock="", highlight=[HLR],
     markers=[{"at": NZ, "label": "1961: the last one", "color": AMBER, "kind": "target", "size": 6, "t": 0.3}, {"at": GZ, "label": "Nobody since", "color": WHITE, "kind": "dot", "t": rel(a, W("p12", "nobody"))}])

# ================================================================== Chapter 02 [REAL HISTORY] how close, and how fast
a = chapter("c2-card", S("p13"), 3.5, "CHAPTER 02", "How close, and how fast", "REAL HISTORY")
SRC2 = "Arms Control Association; Nuclear Threat Initiative"
tFa, tTs = W("p13", "Fallout"), W("p13", "Tsar")
CL2 = dict(clock="MARCH 1954", clockLabel="CASTLE BRAVO", clockRate=0)
reg("c2-bravo", a, tFa, [("s", BIKINI, 1800), (W("p13", "Bikini"), BIKINI, 900), (W("p13", "fifteen"), [165.4, 11.8], 600), ("e", [165.8, 11.9], 420)], tag="REAL HISTORY", source=SRC2, **CL2,
    burst={"at": BIKINI, "t": rel(a, W("p13", "fifteen")), "km": 10, "fade": 4},
    cities=[city(a, BIKINI, "Bikini Atoll", W("p13", "Bikini"), RED, "target", 6)],
    labels=[lab(a, [168.0, 13.6], "American test: Castle Bravo", W("p13", "Castle"), WHITE), lab(a, [168.0, 12.8], "15 Mt: 2.5 times what designers expected", W("p13", "two"), YELLOW)])
reg("c2-fallout", tFa, tTs, [("s", BIKINI, 700), (W("p13", "covers"), [167.5, 11.5], 1300), (W("p13", "islanders"), [168.5, 11.5], 1900), ("e", [168.5, 11.5], 1500)], tag="REAL HISTORY", source=SRC2, **CL2,
    cities=[city(tFa, BIKINI, "Bikini Atoll", tFa + 0.2, RED, "target", 6)],
    labels=[lab(tFa, [171.0, 14.5], "Fallout: over 7,000 square miles", W("p13", "seven"), YELLOW), lab(tFa, [171.0, 9.6], "Marshall Islanders", W("p13", "islanders"), WHITE), lab(tFa, [171.0, 8.6], "A Japanese fishing crew", W("p13", "Japanese"), WHITE)])
num("c2-3x", tTs, S("p14"), "ABOUT 3 TIMES", countTo=3, prefix="ABOUT ", suffix=" TIMES", label="Tsar Bomba against Castle Bravo", color=AMBER, tag="REAL HISTORY", source=SRC2)
a = S("p14")
tBn, tUn, tAnd = W("p14", "banning"), W("p14", "Underground"), W("p14", "and", 3)
glob("c2-treaty", a, tBn, [("s", 50, 20, 900), (W("p14", "Britain"), 48, 15, 1000), ("e", 45, -20, 1300)], tag="REAL HISTORY", source=SRC2, clock="AUG 1963", clockLabel="THE TREATY", clockRate=0,
     markers=[{"at": MOSCOW, "label": "Soviet Union", "color": AMBER, "kind": "base", "size": 5, "t": rel(a, W("p14", "Soviet"))}, {"at": LONDON, "label": "Britain", "color": BLUE, "kind": "dot", "t": rel(a, W("p14", "Britain"))}, {"at": WASH, "label": "United States", "color": BLUE, "kind": "base", "size": 5, "t": rel(a, W("p14", "United"))}],
     arcs=[{"from": MOSCOW, "to": LONDON, "t0": rel(a, W("p14", "Britain")), "t1": rel(a, W("p14", "Britain")) + 2.0, "color": WHITE, "loft": 0.1}, {"from": LONDON, "to": WASH, "t0": rel(a, W("p14", "United")), "t1": rel(a, W("p14", "United")) + 2.0, "color": WHITE, "loft": 0.2}])
stamp("c2-ban", tBn, tUn, "NO TESTS: AIR · SPACE · UNDERWATER", "Partial Test Ban Treaty, 1963", WHITE, tag="REAL HISTORY", source=SRC2)
glob("c2-under", tUn, tAnd, [("s", 38, -110, 1100), (W("p14", "measured"), 38, -90, 1300), ("e", 36, -60, 1500)], tag="REAL HISTORY", source=SRC2, clock="", highlight=[HLU],
     markers=[{"at": [-116.0, 37.0], "label": "Underground tests go on", "color": WHITE, "kind": "dot", "t": 0.4}, {"at": GZ, "label": "No open-air test since", "color": RED, "kind": "target", "size": 5, "t": rel(tUn, W("p14", "open"))}])
cty("c2-modelled", tAnd, S("p15"), [("s", GZ, 60), ("e", GZ, 80)], clock="", rings=[ring(tAnd, GZ, FX["psi5_km"], tAnd + 0.3, "5 psi: modelled", YELLOW)],
    labels=[lab(tAnd, off(0, 31), "Our rings are modelled, not measured", W("p14", "modelled"), YELLOW)])
a = S("p15")
tRus, tLast, tNew, tNo, tNone = W("p15", "Russia"), W("p15", "The", 3), W("p15", "New"), W("p15", "No"), W("p15", "None")
glob("c2-thinner", a, tLast, [("s", 50, 40, 1000), (tRus, 55, 38, 900), ("e", 55, 30, 800)], tag="REAL HISTORY", source="Arms Control Association; Reuters", clock="NOV 2023", clockLabel="RUSSIA WITHDREW", clockRate=0, highlight=[HLR],
     markers=[{"at": MOSCOW, "label": "Withdrew its test-ban ratification", "color": AMBER, "kind": "base", "size": 5, "t": rel(a, tRus)}])
glob("c2-newstart", tLast, tNew + 1.4, [("s", 50, -20, 1000), ("e", 48, -30, 1400)], tag="REAL HISTORY", source="Arms Control Association; Reuters", clock="", highlight=[HLR, HLU],
     markers=[{"at": MOSCOW, "label": "Russia", "color": AMBER, "kind": "base", "size": 5, "t": 0.3}, {"at": WASH, "label": "United States", "color": BLUE, "kind": "base", "size": 5, "t": rel(tLast, W("p15", "American"))}],
     arcs=[{"from": MOSCOW, "to": WASH, "t0": rel(tLast, W("p15", "capping")), "t1": rel(tLast, W("p15", "capping")) + 2.5, "color": WHITE, "loft": 0.4}], caption="The last cap on long-range warheads.")
stamp("c2-expired", tNew + 1.4, tNo, "NEW START EXPIRED", "5 February 2026", AMBER, tag="REAL HISTORY", source="Arms Control Association; Reuters")
cty("c2-notest", tNo, S("p16"), [("s", GZ, 40), (tNone, GZ, 55), ("e", GZ, 30)], clock="", rings=[ring(tNo, GZ, FX["fireball_km"], tNone, "", WHITE, )],
    labels=[lab(tNo, off(0, 14), "No explosive test reported by either side", W("p15", "explosive"), WHITE), lab(tNo, off(0, -13), "None of this points at New York", tNone, YELLOW)])
a = S("p16")
tIn, tAn = W("p16", "In"), W("p16", "An")
reg("c2-62", a, tAn, [("s", [-66.0, 40.6], 1500), (W("p16", "sixty-two"), [-67.0, 40.6], 1100), ("e", [-68.0, 40.7], 800)], clock="T-62:00", clockLabel="TO BURST", clockRate=0,
    cities=[city(a, REL, "Release point", a + 0.3, WHITE, "base", 6), city(a, GZ, "Burst point", W("p16", "burst"), RED, "target", 6)],
    ships=[ship(a, [REL, GZ], tIn, tAn - 0.3, label="Bomber", t_on=tIn)], labels=[lab(a, [-69.5, 38.9], "62 minutes by bomber", W("p16", "sixty-two"), YELLOW)])
glob("c2-23", tAn, S("p17"), [("s", 62, 20, 900), (W("p16", "launched"), 58, -10, 1100), ("e", 50, -50, 1300)], clock="", highlight=[],
     markers=[{"at": ARCTIC, "label": "Arctic launch (simulated)", "color": WHITE, "kind": "base", "size": 5, "t": rel(tAn, W("p16", "launched"))}, {"at": GZ, "label": "New York", "color": RED, "kind": "target", "size": 5, "t": 0.3}],
     arcs=[{"from": ARCTIC, "to": GZ, "t0": rel(tAn, W("p16", "launched")), "t1": rel(tAn, W("p16", "launched")) + 3.2, "color": YELLOW, "loft": 0.5}], caption="An 800 kiloton missile warhead: 23 minutes.")
add(id="c2-tl", type="timeline", start=S("p17"), end=S("p18"), tag="SIMULATION", title="The bomber's flight", sub="release over the Atlantic to the burst point", total=62, unit="minutes",
    segments=[{"from": 0, "to": 62, "label": "62 minutes, nothing else on the map", "color": YELLOW}], highlight={"from": 0, "to": 62, "label": "T-62:00 to T+00:00"}, cursorTo=62)

# ================================================================== Chapter 03 [SIMULATION] the release
a = chapter("c3-card", S("p18"), 3.5, "CHAPTER 03", "The release", "SIMULATION")
tSc, tOne2 = W("p18", "scale"), W("p18", "one", 2)
reg("c3-noattacker", a, tOne2, [("s", GZ, 900), (tSc, GZ, 600), ("e", off(0, 2), 380)], clock="T-62:00", clockLabel="TO BURST", clockRate=0,
    cities=[city(a, GZ, "Lower Manhattan", a + 0.2, RED, "target", 6)],
    labels=[lab(a, off(60, 50), "No war", a + 0.1, WHITE), lab(a, off(60, 38), "No named attacker", a + 0.9, WHITE), lab(a, off(60, 26), "A scale study", tSc, YELLOW)])
reg("c3-scale", tOne2, S("p19"), [("s", off(0, 0), 380), (W("p18", "reason"), off(0, 0), 260), ("e", off(0, 0), 190)], clock="", tag="SIMULATION",
    cities=[city(tOne2, GZ, "One bomb, one point", tOne2 + 0.2, RED, "target", 7)],
    labels=[lab(tOne2, off(24, 14), "No reason given", W("p18", "reason"), WHITE), lab(tOne2, off(24, 6), "No country accused", W("p18", "country"), YELLOW)])
a = S("p19")
cty("c3-gz", a, S("p20"), [("s", GZ, 60), (W("p19", "forty"), GZ, 30), ("e", GZ, 16)], clock="", rings=[ring(a, GZ, 0.4, a + 0.4, "", RED)],
    labels=[lab(a, off(0, 9), "Ground zero: lower Manhattan", W("p19", "Ground"), WHITE), lab(a, off(0, -5), "40.7 N, 74.0 W", W("p19", "forty"), YELLOW)])
a = S("p20")
tIt, tPl = W("p20", "It"), W("p20", "It", 2)
cty("c3-why", a, tPl, [("s", GZ, 26), (W("p20", "recognisable"), off(-2, 2), 40), ("e", off(0, 2), 56)], clock="",
    labels=[lab(a, off(0, 10), "Why lower Manhattan?", a + 0.1, WHITE), lab(a, off(0, -9), "One of the most recognisable shapes on any map", W("p20", "recognisable"), YELLOW)])
reg("c3-notclaim", tPl, S("p21"), [("s", off(0, 0), 420), ("e", off(0, 0), 700)], clock="", tag="SIMULATION",
    cities=[city(tPl, GZ, "A place a viewer can see", W("p20", "place"), RED, "target", 6)],
    labels=[lab(tPl, off(70, 45), "Not a claim that anyone plans this", W("p20", "claim"), YELLOW)])
a = S("p21")
tIt3, tSi, tRe = W("p21", "It"), W("p21", "single"), W("p21", "releasing")
glob("c3-class", a, tSi, [("s", 55, 30, 1000), (tIt3, 50, -10, 1200), ("e", 45, -50, 1500)], clock="", highlight=[HLU],
     markers=[{"at": NZ, "label": "Tsar Bomba class", "color": AMBER, "kind": "target", "size": 6, "t": rel(a, W("p21", "Tsar"))}, {"at": GZ, "label": "Never deployed", "color": WHITE, "kind": "dot", "t": rel(a, W("p21", "never"))}])
reg("c3-bomber", tSi, S("p22"), [("s", [-62.0, 40.5], 1400), (tRe, [-66.0, 40.6], 1000), ("e", [-70.0, 40.7], 700)], clock="T-62:00", clockLabel="TO BURST", clockRate=0,
    cities=[city(tSi, REL, "Release over the North Atlantic", tRe, WHITE, "base", 6), city(tSi, GZ, "Burst point", W("p21", "burst"), RED, "target", 6)],
    ships=[ship(tSi, [REL, GZ], tRe + 0.5, S("p22") - 0.3, label="Single heavy bomber (our choice)", t_on=tSi + 0.2)])
a = S("p22")
tFo, tBy = W("p22", "For"), W("p22", "By")
num("c3-50mt", a, tFo, "50 MEGATONS", countTo=50, suffix=" MEGATONS", label="the Soviet figure for the real test", color=RED, source="Arms Control Center; scenario engine")
add(id="c3-nagasaki", type="bars", start=tFo, end=W("p22", "more"), tag="SIMULATION", title="Yield, in kilotons", sub="more than 2,000 times the Nagasaki bomb", source="US Department of Energy; scenario engine",
    bars=[{"label": "Nagasaki, 1945", "value": 21, "display": "about 21 kt", "color": GREY}, {"label": "This bomb", "value": 50000, "display": "50,000 kt", "color": RED}])
num("c3-2000", W("p22", "more"), tBy, "2,000 TIMES", countTo=2000, suffix=" TIMES", label="more than the Nagasaki bomb", color=RED, source="Arms Control Center; US Department of Energy")
num("c3-ww2", tBy, W("p22", "Second") - 0.5, "ABOUT 10 TIMES", countTo=10, prefix="ABOUT ", suffix=" TIMES", label="all conventional explosives of the Second World War", sub="one estimate", color=RED, source="Wikipedia (one estimate)")
stamp("c3-ww2b", W("p22", "Second") - 0.5, S("p23"), "SECOND WORLD WAR", "all the conventional explosives used", WHITE, source="Wikipedia (one estimate)")
a = S("p23")
tOur, tIt4 = W("p23", "Our"), W("p23", "It")
cty("c3-height", a, tIt4, [("s", GZ, 40), (tOur, GZ, 26), ("e", GZ, 18)], clock="", tag="SIMULATION",
    labels=[lab(a, off(0, 9), "Real bomb burst: about 4,000 m", W("p23", "four"), AMBER), lab(a, off(0, -6), "Our engine takes no height", W("p23", "engine"), YELLOW)])
reg("c3-widest", tIt4, S("p24"), [("s", GZ, 300), (W("p23", "figures"), GZ, 200), ("e", GZ, 160)], clock="", tag="SIMULATION",
    rings=[ring(tIt4, GZ, FX["psi5_km"], W("p23", "widest"), "Widest 5 psi ring", RED)],
    labels=[lab(tIt4, off(-50, 30), "Engine picks the widest blast ring", W("p23", "picks"), YELLOW), lab(tIt4, off(-50, -30), "Not a measured height", W("p23", "measured"), WHITE)])
a = S("p24")
reg("c3-clock", a, S("p25"), [("s", [-70.0, 40.7], 500), ("e", off(-20, 2), 300)], clock="T-00:00", clockLabel="THE BOMBER ARRIVES", clockRate=0,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6)], ships=[ship(a, [off(-120, 4), off(-4, 0)], a + 0.2, S("p25") - 0.2, label="Bomber", t_on=a + 0.2)])

# ================================================================== Chapter 04 [SIMULATION] sixty-two minutes
a = chapter("c4-card", S("p25"), 3.5, "CHAPTER 04", "Sixty-two minutes", "SIMULATION")
reg("c4-1030", a, S("p26"), [("s", [-63.0, 40.5], 1500), (W("p25", "sixty-two"), [-66.0, 40.6], 1200), ("e", [-68.0, 40.6], 1000)], clock="T-62:00", clockLabel="10:30 · SIMULATED", clockRate=0,
    cities=[city(a, REL, "Bomber, about 930 km out", W("p25", "kilometres"), WHITE, "base", 6), city(a, GZ, "Burst point", a + 0.3, RED, "target", 6)],
    lines=[line(a, REL, GZ, W("p25", "nine"), W("p25", "nine") + 2.0, WHITE, True, "930 km")])
a = S("p26")
tOu = W("p26", "Our")
add(id="c4-chute", type="number", start=a, end=tOu, tag="REAL DATA", value="ABOUT 3 MINUTES", countTo=3, prefix="ABOUT ", suffix=" MINUTES", label="the real bomb's fall under its parachute", sub="left out of our clock", color=AMBER, source="Nuclear Weapon Archive; Arms Control Center")
reg("c4-onlyflight", tOu, S("p27"), [("s", [-66.0, 40.6], 1200), (W("p26", "counts"), [-67.0, 40.6], 1000), ("e", [-68.0, 40.6], 800)], clock="T-62:00", clockLabel="THE BOMBER'S FLIGHT ONLY", clockRate=0,
    cities=[city(tOu, REL, "Bomber", tOu + 0.2, WHITE, "base", 6), city(tOu, GZ, "Burst point", tOu + 0.4, RED, "target", 6)],
    labels=[lab(tOu, [-72.5, 38.4], "The fall is left out", W("p26", "leaves"), AMBER), lab(tOu, [-72.5, 37.6], "The clock counts the flight", W("p26", "counts"), YELLOW)])
a = S("p27")
tWe = W("p27", "We")
reg("c4-quiet", a, tWe, [("s", [-67.0, 40.6], 1100), (W("p27", "Nothing"), [-69.5, 40.7], 800), ("e", [-71.5, 40.7], 600)], clock="T-62:00", clockLabel="TO BURST", clockRate=230,
    cities=[city(a, GZ, "New York", a + 0.3, RED, "target", 6)],
    ships=[ship(a, [REL, off(-60, 3)], a + 0.2, tWe, label="Bomber", t_on=a + 0.2)],
    labels=[lab(a, [-65.5, 38.8], "The next hour is quiet on the map", W("p27", "quiet"), WHITE), lab(a, [-65.5, 38.0], "Nothing the engine can measure", W("p27", "measure"), YELLOW)])
reg("c4-nodraw", tWe, S("p28"), [("s", off(-30, 0), 360), (W("p27", "warning"), off(-20, 0), 260), ("e", off(-10, 0), 200)], clock="T-30:00", clockLabel="TO BURST", clockRate=230,
    cities=[city(tWe, GZ, "Lower Manhattan", tWe + 0.3, RED, "target", 6)],
    labels=[lab(tWe, off(-48, 30), "No alert drawn", W("p27", "alert"), WHITE), lab(tWe, off(-48, 20), "No warning, no response", W("p27", "warning"), WHITE), lab(tWe, off(-48, 10), "No source we use describes one", W("p27", "source"), YELLOW)])
a = S("p28")
tZ = W("p28", "zero")
reg("c4-tminus", a, tZ, [("s", off(-90, 4), 400), ("e", off(-8, 1), 220)], clock="T-00:04", clockLabel="11:32 · SIMULATED", clockRate=1,
    cities=[city(a, GZ, "Burst point", a, RED, "target", 6)], ships=[ship(a, [off(-90, 4), off(-1, 0)], a, tZ + 0.1, label="Bomber", t_on=a)],
    labels=[lab(a, off(10, -12), "T minus 4 seconds", a + 0.4, YELLOW)])
a = tZ
tFo2 = W("p29", "forty")
reg("c4-zero", a, S("p29") + 4.0, [("s", GZ, 300), ("e", GZ, 520)], clock="T+00:00", clockLabel="THE BURST", clockRate=1, burst={"at": GZ, "t": 0.1, "km": 12, "fade": 5},
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.9, "Fireball", WHITE)], labels=[lab(a, off(70, 40), "Clock reads T plus zero", a + 0.3, YELLOW)])
a = S("p29") + 4.0
reg("c4-40km", a, S("p30"), [("s", GZ, 220), (W("p29", "pushed"), off(-8, 0), 180), ("e", off(-10, 0), 160)], clock="T+00:05", clockLabel="THE 1961 BOMBER, FOR SCALE", clockRate=1,
    rings=[ring(a, GZ, 40, a + 0.5, "About 40 km: the 1961 bomber's distance", AMBER, )],
    labels=[lab(a, off(-62, -38), "Still pushed down about 1,000 m", W("p29", "thousand"), WHITE)])
a = S("p30")
tIn2, tEv = W("p30", "In"), W("p30", "even")
reg("c4-light", a, S("p31"), [("s", GZ, 260), (tIn2, GZ, 1200), (W("p30", "thousand"), GZ, 2400), ("e", GZ, 3000)], clock="T+00:10", clockLabel="THE LIGHT", clockRate=1, burst={"at": GZ, "t": 0.1, "km": 12, "fade": 3},
    rings=[ring(a, GZ, 1000, W("p30", "thousand"), "1961 flash: visible at about 1,000 km", YELLOW, True)],
    labels=[lab(a, off(0, 130), "The light comes first", a + 0.3, WHITE), lab(a, off(900, 400), "Even through cloud", tEv, WHITE)])
a = S("p31")
tIn3 = W("p31", "In")
cty("c4-fireball", a, tIn3, [("s", GZ, 30), ("e", GZ, 14)], clock="T+00:15", clockLabel="THE FIREBALL", clockRate=1,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.5, "Fireball: 9.2 km wide", WHITE)], labels=[lab(a, off(0, 7.0), "Then the fireball", a + 0.2, WHITE)])
cty("c4-1961ball", tIn3, S("p32"), [("s", GZ, 14), ("e", GZ, 34)], clock="T+00:20", clockLabel="THE FIREBALL", clockRate=1,
    rings=[ring(tIn3, GZ, FX["fireball_km"], tIn3 + 0.1, "", WHITE)], labels=[lab(tIn3, off(0, -8.0), "1961: nearly the bomber's height", W("p31", "nearly"), AMBER)])
a = S("p32")
tAt, tOu2 = W("p32", "At"), W("p32", "Our")
reg("c4-heat", a, tOu2, [("s", GZ, 200), (tAt, GZ, 420), ("e", GZ, 560)], clock="T+00:25", clockLabel="THE HEAT", clockRate=1,
    labels=[lab(a, off(0, 50), "The heat arrives with the light", a + 0.2, WHITE)],
    rings=[ring(a, GZ, 100, W("p32", "hundred"), "1961: third-degree burns to about 100 km", AMBER, True)])
reg("c4-ourheat", tOu2, S("p33"), [("s", GZ, 300), ("e", GZ, 220)], clock="T+00:30", clockLabel="THE HEAT", clockRate=1,
    rings=[ring(tOu2, GZ, FX["thermal3_km"], tOu2 + 0.3, "Our engine: 53 km", ORANGE)],
    labels=[lab(tOu2, off(-70, 38), "A shorter range than 1961", W("p32", "shorter"), WHITE), lab(tOu2, off(-70, -38), "The rings are coming", W("p32", "coming"), YELLOW)])
a = S("p33")
reg("c4-blast", a, S("p34"), [("s", GZ, 230), (W("p33", "farther"), GZ, 260), ("e", GZ, 300)], clock="T+00:40", clockLabel="THE BLAST WAVE", clockRate=1,
    rings=[ring(a, GZ, FX["psi20_km"], a + 0.6, "Near: arrives first", RED), ring(a, GZ, FX["psi5_km"], W("p33", "farther"), "Farther: waits longer", RED), ring(a, GZ, FX["thermal3_km"], W("p33", "longer"), "Farthest: waits longest", ORANGE)],
    labels=[lab(a, off(-80, 45), "Speed of sound", W("p33", "speed"), YELLOW), lab(a, off(-80, -45), "The rings are next", W("p33", "next"), WHITE)])

# ================================================================== Chapter 05 [SIMULATION] one bomb, ring by ring
a = chapter("c5-card", S("p34"), 3.5, "CHAPTER 05", "One bomb, ring by ring", "SIMULATION")
CK = dict(clock="T+00:40", clockLabel="THE 50 Mt BOMB", clockRate=0)
tTh = W("p34", "That")
cty("c5-fireball", a, tTh, [("s", GZ, 24), (W("p34", "nine"), GZ, 14), ("e", GZ, 18)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "Fireball: radius 4.6 km", WHITE)], labels=[lab(a, off(0, 7.0), "9.2 km across", W("p34", "nine"), YELLOW)])
cty("c5-wider", tTh, S("p35"), [("s", GZ, 18), ("e", GZ, 9)], **CK,
    rings=[ring(tTh, GZ, FX["fireball_km"], tTh + 0.1, "", WHITE)],
    labels=[lab(tTh, off(0, 6.0), "Wider than Manhattan is wide", W("p34", "wider"), WHITE), lab(tTh, off(0, -6.0), "Nothing inside is a building", W("p34", "nothing"), RED)])
a = S("p35")
cty("c5-centre", a, S("p36"), [("s", GZ, 10), (W("p35", "Inside"), GZ, 12), ("e", GZ, 8)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "", WHITE)], labels=[lab(a, off(0, 4.8), "The centre: no ring to read", a + 0.4, WHITE), lab(a, off(0, -4.0), "Nothing is left to measure", W("p35", "nothing"), YELLOW)])
a = S("p36")
cty("c5-20psi", a, S("p37"), [("s", GZ, 16), (W("p36", "twenty"), GZ, 22), ("e", GZ, 18)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "", WHITE), ring(a, GZ, FX["psi20_km"], W("p36", "five"), "20 psi: 5.1 km", RED)],
    labels=[lab(a, off(0, 7.5), "Heavy damage even to strong buildings", W("p36", "heavy"), YELLOW)])
a = S("p37")
tSo, tIt5, tAll = W("p37", "so"), W("p37", "It"), W("p37", "all")
cty("c5-island", a, tIt5, [("s", GZ, 20), (W("p37", "Manhattan"), GZ, 26), ("e", GZ, 22)], **CK,
    rings=[ring(a, GZ, FX["psi20_km"], a + 0.1, "20 psi ring", RED)],
    labels=[lab(a, off(0, 7.0), "Manhattan: at most about 3.7 km wide", W("p37", "Manhattan"), WHITE), lab(a, off(0, -7.0), "The ring is wider than the island", W("p37", "ring", 2), YELLOW)])
cty("c5-takesin", tIt5, S("p38"), [("s", off(-2, -3), 24), (tAll, GZ, 20), ("e", off(1, -3), 26)], **CK,
    rings=[ring(tIt5, GZ, FX["psi20_km"], tIt5 + 0.1, "", RED)],
    labels=[lab(tIt5, off(-5, -4.5), "The harbour", W("p37", "harbour"), WHITE), lab(tIt5, off(0, 6.5), "All of lower Manhattan", tAll, WHITE), lab(tIt5, off(6.5, -3.0), "Brooklyn", W("p37", "Brooklyn"), WHITE), lab(tIt5, off(-7.5, 0.0), "New Jersey", W("p37", "Jersey"), WHITE)])
a = S("p38")
tTh2 = W("p38", "The")
cty("c5-5psi", a, tTh2, [("s", GZ, 30), (W("p38", "five"), GZ, 52), ("e", GZ, 60)], **CK,
    rings=[ring(a, GZ, FX["psi20_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi5_km"], W("p38", "twenty-five"), "5 psi: 25 km", RED)],
    labels=[lab(a, off(0, 30), "Heavily damages most buildings", W("p38", "heavily"), YELLOW)])
cty("c5-2000", tTh2, S("p39"), [("s", GZ, 60), ("e", GZ, 96)], **CK,
    rings=[ring(tTh2, GZ, FX["psi5_km"], tTh2 + 0.1, "5 psi: 25 km", RED)],
    labels=[lab(tTh2, off(0, 17.0), "About 2,000 square kilometres", W("p38", "thousand"), YELLOW)])
a = S("p39")
tWi = W("p39", "with")
cty("c5-street", a, tWi, [("s", GZ, 56), (W("p39", "Manhattan"), GZ, 44), ("e", GZ, 50)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    labels=[lab(a, off(0, 12.0), "Read it street by street", a + 0.2, WHITE), lab(a, off(-3, -11), "All of Manhattan", W("p39", "Manhattan"), WHITE)])
cty("c5-airports", tWi, S("p40"), [("s", GZ, 50), (W("p39", "three"), GZ, 58), ("e", GZ, 64)], **CK,
    rings=[ring(tWi, GZ, FX["psi5_km"], tWi + 0.1, "", RED)],
    labels=[lab(tWi, off(10, -9), "Brooklyn waterfront", tWi + 0.3, WHITE), lab(tWi, off(-14, -2), "Jersey waterfront", W("p39", "Jersey"), WHITE), lab(tWi, off(17, -8), "JFK", W("p39", "airports"), YELLOW), lab(tWi, off(10, 4), "LaGuardia", W("p39", "airports") + 0.4, YELLOW), lab(tWi, off(-14, -9), "Newark", W("p39", "airports") + 0.8, YELLOW)])
a = S("p40")
tAg2 = W("p40", "against")
cty("c5-hold", a, tAg2, [("s", GZ, 70), (W("p40", "area"), GZ, 64), ("e", GZ, 60)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "5 psi ring: the one to hold in mind", RED)],
    labels=[lab(a, off(0, 24), "About 2,000 km2", W("p40", "thousand"), YELLOW)])
cty("c5-124", tAg2, S("p41"), [("s", GZ, 56), ("e", GZ, 84)], **CK,
    rings=[ring(tAg2, GZ, FX["psi5_km"], tAg2 + 0.1, "50 Mt: 25 km", RED), ring(tAg2, GZ, FC["psi5_km"], tAg2 + 0.7, "800 kt: 6.3 km", YELLOW)],
    labels=[lab(tAg2, off(0, 33), "About 124 km2 for the smaller bomb", W("p40", "twenty-four"), YELLOW)])
a = S("p41")
tTh3 = W("p41", "The")
reg("c5-burn", a, tTh3, [("s", GZ, 200), (W("p41", "fifty-three"), GZ, 240), ("e", GZ, 280)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["thermal3_km"], W("p41", "fifty-three"), "Third-degree burns: 53 km", ORANGE)],
    labels=[lab(a, off(0, -45), "Bare skin, clear air", W("p41", "bare"), YELLOW)])
reg("c5-sea", tTh3, S("p42"), [("s", GZ, 280), (W("p41", "Long"), off(10, 5), 330), ("e", off(10, 5), 380)], **CK,
    rings=[ring(tTh3, GZ, FX["psi5_km"], tTh3 + 0.1, "", RED), ring(tTh3, GZ, FX["thermal3_km"], tTh3 + 0.1, "", ORANGE)],
    labels=[lab(tTh3, off(40, -48), "The sea", W("p41", "sea"), WHITE), lab(tTh3, off(40, 10), "Long Island", W("p41", "Long"), WHITE), lab(tTh3, off(-60, 0), "New Jersey", W("p41", "Jersey"), WHITE), lab(tTh3, off(70, 95), "Connecticut", W("p41", "Connecticut"), WHITE)])
a = S("p42")
tTh4 = W("p42", "The", 2)
reg("c5-1psi", a, tTh4, [("s", GZ, 300), (W("p42", "one"), GZ, 340), ("e", GZ, 380)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["thermal3_km"], a + 0.1, "", ORANGE), ring(a, GZ, FX["psi1_km"], W("p42", "one"), "1 psi: 67.5 km", WHITE)],
    labels=[lab(a, off(-75, -50), "Breaks windows", W("p42", "windows"), YELLOW)])
reg("c5-900", tTh4, S("p43"), [("s", GZ, 400), (W("p42", "glass"), off(0, 0), 1400), ("e", off(300, 0), 3600)], **CK,
    rings=[ring(tTh4, GZ, FX["psi1_km"], tTh4 + 0.1, "", WHITE), ring(tTh4, GZ, 900, W("p42", "nine"), "Real test: glass broke to about 900 km", AMBER, True)],
    labels=[lab(tTh4, off(0, 0), "Our rings are conservative", W("p42", "conservative"), YELLOW)])
a = S("p43")
tTh5, tEi2 = W("p43", "This"), W("p43", "eight")
cty("c5-same", a, tEi2, [("s", GZ, 70), ("e", GZ, 100)], **CK, rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "50 Mt: 5 psi", RED)],
    labels=[lab(a, off(0, 35), "The same map, a different bomb", W("p43", "different"), WHITE), lab(a, off(0, -35), "A comparison, not a second attack", tTh5 + 0.8, YELLOW)])
num("c5-800kt", tEi2, S("p44"), "800 KILOTONS", countTo=800, suffix=" KILOTONS", label="the top of Russia's missile warhead range", sub="SS-18 class (500 to 800 kt)", color=YELLOW, source="Federation of American Scientists; scenario engine")
a = S("p44")
tIt6, tIt7 = W("p44", "Its", 2), W("p44", "Its", 3)
CK2 = dict(clock="", clockLabel="")
cty("c5-s-fire", a, tIt6, [("s", GZ, 6), (W("p44", "radius"), GZ, 9), ("e", GZ, 12)], **CK2,
    rings=[ring(a, GZ, FC["fireball_km"], a + 0.3, "800 kt fireball: under 1 km", WHITE)], labels=[lab(a, off(0, 3.2), "A bomb about 60 times smaller", a + 1.0, YELLOW)])
cty("c5-s-burn", tIt6, tIt7, [("s", GZ, 20), (W("p44", "window"), GZ, 28), ("e", GZ, 38)], **CK2,
    rings=[ring(tIt6, GZ, FC["fireball_km"], tIt6 + 0.1, "", WHITE), ring(tIt6, GZ, FC["thermal3_km"], W("p44", "nine"), "Burns: 9.8 km", ORANGE), ring(tIt6, GZ, FC["psi1_km"], W("p44", "seventeen"), "Windows: 17 km", WHITE)])
cty("c5-s-5psi", tIt7, S("p45"), [("s", GZ, 24), (W("p44", "six"), GZ, 30), ("e", GZ, 36)], **CK2,
    rings=[ring(tIt7, GZ, FC["psi5_km"], W("p44", "six"), "5 psi: 6.3 km", YELLOW), ring(tIt7, GZ, FC["thermal3_km"], tIt7 + 0.1, "", ORANGE)],
    labels=[lab(tIt7, off(0, 11.5), "About 124 square kilometres", W("p44", "hundred"), YELLOW)])
a = S("p45")
tTw = W("p45", "twenty-five")
cty("c5-vs", a, S("p46"), [("s", GZ, 60), (tTw, GZ, 72), ("e", GZ, 84)], **CK2,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.2, "50 Mt: 25 km", RED), ring(a, GZ, FC["psi5_km"], tTw, "800 kt: 6.3 km", YELLOW)],
    labels=[lab(a, off(0, 33), "Almost four times as far", W("p45", "four"), WHITE), lab(a, off(0, -33), "About 16 times the area", W("p45", "sixteen"), WHITE)])
a = S("p46")
tSm = W("p46", "Same", 2)
add(id="c5-bars", type="bars", start=a, end=tSm, tag="SIMULATION", title="5 psi ring, radius in km", sub="same point, same island", source="Scenario engine (estimates)",
    bars=[{"label": "800 kt", "value": FC["psi5_km"], "display": "6.3 km", "color": YELLOW}, {"label": "50 Mt", "value": FX["psi5_km"], "display": "24.9 km", "color": RED}])
cty("c5-60x", tSm, S("p48"), [("s", GZ, 70), (W("p46", "sixty"), GZ, 90), ("e", GZ, 110)], **CK2,
    rings=[ring(tSm, GZ, FX["psi5_km"], tSm + 0.1, "", RED), ring(tSm, GZ, FC["psi5_km"], tSm + 0.1, "", YELLOW)],
    labels=[lab(tSm, off(0, 40), "Same point, same island", tSm + 0.3, WHITE), lab(tSm, off(0, -40), "About 60 times larger", W("p46", "sixty"), YELLOW), lab(tSm, off(50, 0), "When the light fades", W("p47", "light"), WHITE)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p48"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
CD = dict(clock="DAY 1", clockLabel="THE DAY AFTER", clockRate=0)
tIn5, tDark = W("p48", "In", 2), W("p48", "dark")
cty("c6-ring", a, tIn5, [("s", GZ, 60), (W("p48", "almost"), GZ, 80), ("e", GZ, 66)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], W("p48", "ring"), "Almost 25 km in radius", RED)],
    labels=[lab(a, off(0, 15.0), "A ring around a single point", W("p48", "single"), YELLOW)])
cty("c6-dark", tIn5, S("p49"), [("s", GZ, 80), (W("p48", "begins"), GZ, 66), ("e", GZ, 60)], **CD,
    rings=[ring(tIn5, GZ, FX["psi5_km"], tIn5 + 0.1, "", RED)],
    labels=[lab(tIn5, off(0, 14.0), "The day after begins", tIn5 + 0.4, WHITE), lab(tIn5, off(0, -14.0), "The ring goes dark", tDark, RED)])
a = S("p49")
tPu = W("p49", "Published")
cty("c6-bridges", a, tPu, [("s", off(-2, -3), 26), (W("p49", "harbour"), off(0, -4), 34), ("e", off(0, -3), 30)], **CD,
    rings=[ring(a, GZ, FX["psi20_km"], a + 0.1, "", RED)],
    labels=[lab(a, off(-5, 6), "Inside it: the harbour's bridges and tunnels", W("p49", "bridges"), WHITE)])
cty("c6-models", tPu, S("p50"), [("s", GZ, 40), ("e", GZ, 66)], **CD,
    rings=[ring(tPu, GZ, FX["psi5_km"], tPu + 0.1, "5 psi: 25 km", RED)],
    labels=[lab(tPu, off(0, 18.0), "Heavy damage to most ordinary buildings", W("p49", "heavy"), YELLOW)])
a = S("p50")
tAt2 = W("p50", "At")
reg("c6-states", a, tAt2, [("s", GZ, 260), (W("p50", "cross"), GZ, 320), ("e", GZ, 360)], **CD,
    rings=[ring(a, GZ, FX["thermal3_km"], a + 0.3, "Burn ring: 53 km", ORANGE), ring(a, GZ, FX["psi1_km"], W("p50", "window"), "Window ring: 67.5 km", WHITE)],
    labels=[lab(a, off(85, 90), "Connecticut", W("p50", "three"), WHITE), lab(a, off(-62, 0), "New Jersey", W("p50", "states"), WHITE), lab(a, off(-10, 120), "New York State", W("p50", "sea"), WHITE)])
reg("c6-900", tAt2, S("p51"), [("s", GZ, 400), (W("p50", "broke"), off(300, 0), 1800), ("e", off(400, 0), 3600)], **CD,
    rings=[ring(tAt2, GZ, FX["psi1_km"], tAt2 + 0.1, "", WHITE), ring(tAt2, GZ, 900, W("p50", "nine"), "1961: windows broke to about 900 km", AMBER, True)])
a = S("p51")
tWi2, tSo2, tTh6, tTh7 = W("p51", "Winds"), W("p51", "so"), W("p51", "That"), W("p51", "The", 5)
tLo = W("p51", "lower")
reg("c6-wind", a, tSo2, [("s", GZ, 300), (tWi2, off(-20, 0), 360), ("e", off(0, 0), 420)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    lines=[line(a, off(-130, -30), off(-30, -8), a + 0.2, tWi2 + 2.5, TEAL, False, "Prevailing wind: from the west", 3)],
    labels=[lab(a, off(-120, -8), "Then the wind", a + 0.2, WHITE)])
reg("c6-drift", tSo2, tTh6, [("s", off(40, 0), 420), ("e", off(90, -10), 560)], **CD,
    rings=[ring(tSo2, GZ, FX["psi5_km"], tSo2 + 0.1, "", RED)],
    lines=[line(tSo2, GZ, off(170, -25), W("p51", "drift"), W("p51", "drift") + 2.5, TEAL, True, "Plume would tend to drift east", 3)],
    labels=[lab(tSo2, off(120, 20), "Long Island and the sea", W("p51", "Long"), WHITE)])
reg("c6-assume", tTh6, W("p51", "A", 2), [("s", GZ, 480), (W("p51", "local"), GZ, 360), ("e", GZ, 300)], **CD,
    rings=[ring(tTh6, GZ, FX["psi5_km"], tTh6 + 0.1, "", RED)],
    labels=[lab(tTh6, off(-70, 50), "An assumption of ours", W("p51", "assumption"), YELLOW), lab(tTh6, off(-70, 40), "Little local fallout from an airburst", W("p51", "local"), WHITE), lab(tTh6, off(-70, 30), "We draw no plume", W("p51", "plume", 2), RED)])
reg("c6-change", W("p51", "A", 2), tTh7, [("s", GZ, 300), ("e", GZ, 420)], **CD,
    rings=[ring(W("p51", "A", 2), GZ, FX["psi5_km"], W("p51", "A", 2) + 0.1, "", RED)],
    labels=[lab(W("p51", "A", 2), off(-70, 45), "A lower burst would change it", tLo, WHITE), lab(W("p51", "A", 2), off(-70, 35), "So would rain", W("p51", "rain"), WHITE)])
glob("c6-100mt", tTh7, S("p52"), [("s", 60, 50, 900), (W("p51", "scrapped"), 70, 58, 1300), ("e", 74, 55, 2000)], tag="REAL HISTORY", clock="1961", clockLabel="THE FULL DESIGN", clockRate=0, highlight=[HLR],
     markers=[{"at": NZ, "label": "100 Mt design: scrapped, 1961", "color": AMBER, "kind": "target", "size": 6, "t": rel(tTh7, W("p51", "full"))}])
a = S("p52")
tAc, tFar = W("p52", "A", 2), W("p52", "far")
reg("c6-point", a, tAc, [("s", GZ, 260), ("e", GZ, 160)], **CD,
    cities=[city(a, GZ, "The cloud: a point at the centre", W("p52", "point"), RED, "target", 7)])
num("c6-65", tAc, tFar, "65 KM", countTo=65, suffix=" KM", label="a cloud like the 1961 one climbs", color=AMBER, tag="REAL DATA", source="Nuclear Weapon Archive; RFE/RL")
reg("c6-above", tFar, S("p53"), [("s", GZ, 300), ("e", GZ, 700)], **CD,
    cities=[city(tFar, GZ, "Far above where airliners fly", tFar + 0.3, WHITE, "target", 6)])
a = S("p53")
tHo, tNo2 = W("p53", "hospitals"), W("p53", "no")
reg("c6-quiet", a, tHo, [("s", GZ, 500), (W("p53", "power"), GZ, 700), ("e", GZ, 900)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.1, "", WHITE)],
    labels=[lab(a, off(130, 100), "Beyond the rings, the map goes quiet", W("p53", "quiet"), WHITE), lab(a, off(130, 85), "Power grid: not modelled", W("p53", "power"), YELLOW), lab(a, off(130, 70), "Phones: not modelled", W("p53", "phones"), YELLOW)])
reg("c6-notmodelled", tHo, S("p54"), [("s", GZ, 900), ("e", GZ, 1300)], **CD,
    rings=[ring(tHo, GZ, FX["psi5_km"], tHo + 0.1, "", RED)],
    labels=[lab(tHo, off(190, 140), "Hospitals: not modelled", tHo + 0.1, YELLOW), lab(tHo, off(190, 120), "The response: not modelled", W("p53", "response"), YELLOW), lab(tHo, off(190, 100), "No published death toll, so none", W("p53", "give"), WHITE)])
a = S("p54")
tTh8, tAnd2 = W("p54", "This"), W("p54", "and")
reg("c6-arctic", a, tTh8, [("s", NZ, 1500), ("e", [52, 72], 900)], tag="REAL DATA", clock="1961", clockLabel="AN ARCTIC RANGE", clockRate=0, highlight=[HLR],
    cities=[city(a, NZ, "1961: an Arctic range", a + 0.3, AMBER, "target", 6)])
num("c6-86", tTh8, tAnd2, "8.6 MILLION", countTo=8.6, decimals=1, suffix=" MILLION", label="people live in New York City", sub="about 8.585 million, July 2025 estimate", color=WHITE, tag="REAL DATA", source="NYC Department of City Planning, March 2026")
cty("c6-edge", tAnd2, S("p55"), [("s", GZ, 70), ("e", GZ, 140)], **CD,
    rings=[ring(tAnd2, GZ, FX["psi5_km"], tAnd2 + 0.2, "", RED), ring(tAnd2, GZ, FX["thermal3_km"], tAnd2 + 0.8, "", ORANGE), ring(tAnd2, GZ, FX["psi1_km"], tAnd2 + 1.4, "", WHITE)],
    labels=[lab(tAnd2, off(0, 35), "The rings do not stop at its edge", W("p54", "stop"), YELLOW)])

# ================================================================== End slate
add(id="end", type="endslate", start=S("p55"), end=END, tag="", title="Next scenario", line="Washington, DC: where the government goes.")


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



ATL_IDS = {"open-bomber", "open-atlantic", "c2-62", "c3-bomber", "c4-1030", "c4-onlyflight", "c4-quiet", "c3-clock"}
for s_ in shots:
    if s_["id"] in ATL_IDS:
        s_.setdefault("highlight", [{"iso": US_, "color": BLUE, "fill": "rgba(110,168,255,0.16)"}])
        s_.setdefault("countryLabels", [{"iso": US_, "text": "UNITED STATES", "color": BLUE}])
        s_["rings"] = s_.get("rings", []) + [{"at": GZ, "km": 929.3, "label": "930 km from New York", "color": WHITE, "t": 0.4, "dashed": True}]
        if not s_.get("lines"):
            s_["lines"] = [{"from": REL, "to": GZ, "color": WHITE, "dashed": True, "t0": 0.5, "t1": 2.5}]
for s_ in shots:
    if s_["id"] in ("c1-arsenal", "c1-answer", "c1-kal", "c1-iskander"):
        s_.setdefault("short", {})["source"] = ""
floors()
densify()

floors()
densify()

# ------------------------------------------------------------------ audio plan and output
BOOMS = [FL + 0.1, S("p07") + 0.1, S("p08") + 0.1, tZ + 0.1, S("p30") + 0.1] + [s["start"] + s["burst"]["t"] for s in shots if s.get("burst") and s["id"] == "c2-bravo"]
b0 = round(min(FL + 0.1 - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p18") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p18") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": t, "gain_db": -4} for t in BOOMS],
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
