"""Director pass for episode 011: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 011-washington-where-the-government-goes
One simulated 100 kt airburst over the White House (city file washington.json), real continuity history on region and
globe shots, and a minute-by-minute run-up with ticking clocks. No attacker named, no real date.
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
HERO = sc["strikes"][0]
FX = HERO["effects"]
GZ = [HERO["target_lon"], HERO["target_lat"]]                 # the White House area
REL = [HERO["launch_lon"], HERO["launch_lat"]]                # launch point, open North Atlantic (simulated)
MW = [-77.8875, 39.064]                                       # Mount Weather (A14)
RR = [-77.4194, 39.7344]                                      # Raven Rock (A13)
GB = [-80.3086, 37.7855]                                      # The Greenbrier (A23)
OFFUTT = [-95.9122, 41.1183]
CAP = [-77.0091, 38.8899]
PENT = [-77.0558, 38.8719]
BALT, ANN = [-76.61, 39.29], [-76.49, 38.98]
MOSCOW, WASH = [37.62, 55.75], GZ
US_ = "840"
HLU = {"iso": US_, "color": BLUE, "fill": "rgba(110,168,255,0.10)"}
SRC1 = "Congressional Research Service; History.com"
SRC2 = "Arms Control Association; Congressional Research Service"


def offp(base, dx, dy):
    return [round(base[0] + dx / (111.32 * math.cos(math.radians(base[1]))), 4), round(base[1] + dy / 110.57, 4)]


def off(dx, dy):
    return offp(GZ, dx, dy)


def lerp(p, q, f):
    return [round(p[0] + (q[0] - p[0]) * f, 4), round(p[1] + (q[1] - p[1]) * f, 4)]


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


def ship(a, path, t0, t1, label="", color=WHITE, kind="pla", t_on=None, size=1.8):
    return {"path": path, "t0": rel(a, t0), "t1": rel(a, t1), "kind": kind, "color": color, "label": label, "size": size, "t": rel(a, t0 if t_on is None else t_on), "wake": True}


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
    return round(km) if km >= 10 else round(km, 1)


_RNAMES = [(FX["fireball_km"], "Fireball"), (FX["psi20_km"], "20 psi"), (FX["psi5_km"], "5 psi"), (FX["thermal3_km"], "Burns"), (FX["psi1_km"], "Windows")]


def _rlabel(r):
    t = re.sub(r"[:,]?\s*(radius |about |under |almost )?[\d.,]+ ?(km|m)( wide| across| in radius)?", "", r["label"], flags=re.I).strip(" :,")
    if not t:
        t = next((n for k, n in _RNAMES if abs(k - r["km"]) < 1e-6), "")
    return t


def cty(sid, a, b, keys, rings=(), labels=(), tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    add(id=sid, type="city", start=a, end=b, tag=tag, city="washington", view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, gz=GZ, camera=c,
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


# the Atlantic and the sites, shared by several shots
HLUS = [HLU]
CLUS = [{"iso": US_, "text": "UNITED STATES", "color": BLUE}]
MWC = lambda a, t, lab_="Mount Weather": city(a, MW, lab_, t, BLUE, "base", 6)
RRC = lambda a, t, lab_="Raven Rock": city(a, RR, lab_, t, BLUE, "base", 6)
CTX = lambda a: [city(a, [-71.06, 42.36], "Boston", a + 0.6, GREY), city(a, [-64.78, 32.3], "Bermuda", a + 1.2, GREY)]
GBC = lambda a, t, lab_="The Greenbrier": city(a, GB, lab_, t, BLUE, "base", 6)
WHC = lambda a, t, lab_="White House": city(a, GZ, lab_, t, RED, "target", 6)


# ================================================================== Cold open [SIMULATION]
FL = 2.85   # the cut lands on the flash, which is at +0.1 in the city shot ("bursts" is spoken at 2.95)
reg("open-run", 0, FL, [("s", off(70, 10), 320), ("e", off(8, 2), 170)], clock="T-00:03", clockLabel="TO BURST", clockRate=1,
    cities=[WHC(0, 0.0, "White House"), city(0, BALT, "Baltimore", 0.25), city(0, ANN, "Annapolis", 0.5)],
    lines=[line(0, off(150, 40), GZ, 0.0, 2.8, WHITE)],
    ships=[ship(0, [off(150, 40), GZ], 0.0, 2.8, label="Warhead", color=RED, t_on=0.0)])
a = FL
cty("open-flash", a, S("p02"), [("s", GZ, 9), ("e", GZ, 24)], clock="T+00:00", clockLabel="WASHINGTON · SIMULATED", clockRate=1,
    flashT=0.1, rings=[ring(a, GZ, FX["fireball_km"], a + 0.5, "Fireball", WHITE), ring(a, GZ, FX["psi20_km"], a + 1.2, "20 psi", RED), ring(a, GZ, FX["psi5_km"], a + 1.9, "5 psi", RED)],
    labels=[lab(a, off(0, 1.6), "White House", a + 0.4, WHITE)], caption="One 100 kiloton airburst. Simulation: it has not happened.")
shots[-1]["rings"][0]["angle"] = 65   # fireball label up and right, clear of the city-file "WASHINGTON" under the burst
a = S("p02")
reg("open-sim", a, S("p03"), [("s", GZ, 240), (W("p02", "simulation"), off(-8, 3), 300), ("e", off(-12, 4), 380)], clock="T+00:20", clockLabel="AFTER THE FLASH", clockRate=0,
    cities=[city(a, GZ, "Ground zero", a + 0.3, RED, "target", 6), city(a, BALT, "Baltimore", a + 0.5), city(a, ANN, "Annapolis", a + 0.7)],
    labels=[lab(a, off(-85, 40), "A simulation: not a prediction", W("p02", "simulation"), YELLOW), lab(a, off(-85, 28), "It has not happened", W("p02", "not"), WHITE)])
a = S("p03")
tSat = W("p03", "Satellites")
reg("open-sub", a, tSat, [("s", [-60, 40.5], 3900), (W("p03", "submarine"), [-62, 40.2], 3700), ("e", [-64, 40.0], 3450)], clock="T-11:06", clockLabel="TO BURST", clockRate=1,
    highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, REL, "Submarine (simulated)", W("p03", "submarine"), WHITE, "base", 6), city(a, GZ, "Washington", a + 0.4, RED, "target", 6)] + CTX(a),
    lines=[line(a, REL, GZ, W("p03", "fires"), tSat - 0.5, WHITE, True, "About 2,700 km"), line(a, REL, GZ, W("p03", "fires"), tSat - 0.2, RED, False, None, 3)],
    ships=[ship(a, [REL, lerp(REL, GZ, 0.38)], W("p03", "fires"), tSat - 0.2, label="One missile", color=RED, t_on=W("p03", "fires"), size=4.5)])
a = tSat
tAn = W("p03", "Analysts")
glob("open-sat", a, tAn, [("s", 42, -62, 1000), ("e", 40, -70, 1500)], highlight=HLUS,
     markers=[{"at": REL, "label": "Launch detected", "color": WHITE, "kind": "sub", "size": 6, "t": 0.3}, {"at": GZ, "label": "Washington", "color": RED, "kind": "target", "size": 6, "t": 0.4}],
     arcs=[{"from": REL, "to": GZ, "t0": 0.3, "t1": 2.6, "color": RED, "loft": 0.3}])
a = tAn
reg("open-window", a, S("p04"), [("s", GZ, 420), (W("p03", "less"), GZ, 280), ("e", GZ, 170)], clock="T-10:00", clockLabel="TO DECIDE", clockRate=1,
    cities=[WHC(a, a + 0.2), city(a, off(-9, -5), "Pentagon", a + 1.0, BLUE, "dot", 5), city(a, BALT, "Baltimore", a + 1.6)],
    labels=[lab(a, off(-130, 70), "Analysts' estimate", a + 0.3, YELLOW), lab(a, off(-130, 58), "Under 10 minutes to decide", W("p03", "less"), WHITE)])
a = S("p04")
cty("open-who", a, S("p05"), [("s", GZ, 30), (W("p04", "chain"), GZ, 20), ("e", GZ, 13)], clock="10:12", clockLabel="WHO IS LEFT?", clockRate=0,
    labels=[lab(a, off(0, 1.6), "White House", a + 0.3, WHITE), lab(a, offp(CAP, 0, 0.9), "Capitol", W("p04", "chain"), WHITE), lab(a, offp(PENT, 0, -1.0), "Pentagon", W("p04", "command"), WHITE),
            lab(a, off(0, -6.0), "Who is left at 10:12?", W("p04", "twelve"), YELLOW)])

# ================================================================== Chapter 01 [REAL DATA] the day the government left
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "The day the government left", "REAL DATA")
CL1 = dict(clock="11 SEP 2001", clockLabel="THE MORNING", clockRate=0)
tBun = W("p05", "within")
cty("c1-vp", a, S("p06"), [("s", GZ, 12), (W("p05", "bunker"), GZ, 8), ("e", off(0, -0.5), 6)], tag="REAL DATA", source=SRC1, **CL1,
    labels=[lab(a, off(0, 1.5), "Vice President", W("p05", "Vice"), WHITE), lab(a, off(0, -1.2), "Taken below the White House", W("p05", "below"), YELLOW)],
    caption="Within minutes of the South Tower being hit.")
a = S("p06")
tDef = W("p06", "Defense")
reg("c1-af1", a, tDef, [("s", [-90, 38], 5200), (W("p06", "aboard"), [-88, 37], 4300), ("e", [-84, 37], 3600)], tag="REAL DATA", source=SRC1, **CL1, highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, GZ, "Washington", a + 0.3, BLUE, "dot", 5)],
    ships=[ship(a, [GZ, [-82, 36], [-90, 33]], W("p06", "air") - 0.4, tDef - 0.3, label="Air Force One", color=BLUE, kind="us", t_on=W("p06", "air") - 0.4, size=2.2)],
    labels=[lab(a, [-92, 43], "President: in the air", W("p06", "air"), WHITE), lab(a, [-92, 41.5], "Limited communications", W("p06", "limited"), YELLOW)])
a = tDef
cty("c1-pent", a, S("p07"), [("s", off(-1.7, -2.9), 8), (W("p06", "Pentagon"), PENT, 5.5), ("e", PENT, 4.5)], tag="REAL DATA", source=SRC1, **CL1,
    labels=[lab(a, offp(PENT, 0, 0.9), "Defense Secretary", a + 0.3, WHITE), lab(a, offp(PENT, 0, -0.8), "Pentagon crash site", W("p06", "crash"), YELLOW), lab(a, offp(PENT, 0, -1.4), "Out of reach for much of the crisis", W("p06", "reach"), WHITE)])
a = S("p07")
tMt = W("p07", "mountain")
reg("c1-heli", a, tMt + 0.4, [("s", off(-30, 8), 190), (W("p07", "congressional"), off(-35, 12), 170), ("e", off(-40, 14), 160)], tag="REAL DATA", source=SRC1, **CL1,
    cities=[city(a, CAP, "Capitol", a + 0.3, BLUE, "dot", 5), MWC(a, W("p07", "bunker"))],
    ships=[ship(a, [CAP, MW], W("p07", "helicopters"), tMt + 0.2, label="Military helicopters", color=BLUE, kind="us", t_on=W("p07", "helicopters"), size=2.2)],
    labels=[lab(a, off(-100, 40), "About ten to ten", W("p07", "about"), YELLOW), lab(a, off(-100, 30), "Congressional leaders", W("p07", "congressional"), WHITE)])
a = tMt + 0.4
reg("c1-mw", a, S("p08"), [("s", off(-45, 14), 180), ("e", MW, 150)], tag="REAL DATA", source=SRC1, **CL1,
    cities=[MWC(a, W("p07", "Mount")), city(a, GZ, "White House", a + 0.4, WHITE, "dot", 5)],
    labels=[lab(a, offp(MW, 0, -12), "Virginia", W("p07", "called") + 0.1, GREY), lab(a, offp(MW, 0, -22), "They stayed until late afternoon", W("p07", "stayed"), YELLOW)])
a = S("p08")
tDoz = W("p08", "dozens")
reg("c1-cont", a, tDoz, [("s", off(-30, 30), 240), (W("p08", "quietly"), off(-35, 35), 200), ("e", off(-35, 40), 180)], tag="REAL DATA", source=SRC1, **CL1,
    cities=[city(a, GZ, "Washington", a + 0.3, WHITE, "dot", 5)],
    labels=[lab(a, off(-90, 60), "For the first time", W("p08", "first"), YELLOW), lab(a, off(-90, 49), "Continuity plans activated", W("p08", "activated"), WHITE)])
a = tDoz
tPub = W("p08", "public")
reg("c1-bunkers", a, tPub, [("s", off(-35, 45), 200), (W("p08", "rotating"), off(-35, 50), 240), ("e", off(-30, 50), 280)], tag="REAL DATA", source=SRC1, **CL1,
    cities=[city(a, GZ, "Washington", a + 0.2, WHITE, "dot", 5), MWC(a, a + 0.4), RRC(a, a + 0.8)],
    lines=[line(a, GZ, MW, W("p08", "two"), W("p08", "two") + 1.6, BLUE, True), line(a, GZ, RR, W("p08", "bunkers"), W("p08", "bunkers") + 1.6, BLUE, True)],
    labels=[lab(a, off(-110, 78), "Dozens, perhaps 150 officials", a + 0.1, WHITE), lab(a, off(-110, 66), "Rotating through two bunkers", W("p08", "rotating"), YELLOW)])
stamp("c1-march", tPub, S("p09"), "MARCH 2002", "The public learns of it", WHITE, tag="REAL DATA", source=SRC1)
a = S("p09")
tIn = W("p09", "In")
reg("c1-watch", a, tIn, [("s", GZ, 220), (W("p09", "attacks"), off(-5, 0), 180), ("e", off(-8, 0), 150)], tag="REAL DATA", source=SRC1, **CL1,
    cities=[WHC(a, a + 0.3), city(a, off(-9, -5), "Pentagon", a + 0.6, BLUE, "dot", 5)],
    labels=[lab(a, off(-85, 45), "Attacks you could watch unfold", W("p09", "attacks"), WHITE), lab(a, off(-85, 34), "Minutes at a time", W("p09", "minutes"), YELLOW)])
a = tIn
reg("c1-11", a, S("p10"), [("s", [-60, 40.5], 3900), (W("p09", "warning"), [-62, 40.2], 3700), ("e", [-64, 40.0], 3450)], clock="T-11:06", clockLabel="TO BURST", clockRate=0, highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, REL, "Submarine (simulated)", a + 0.4, WHITE, "base", 6), city(a, GZ, "Washington", a + 0.6, RED, "target", 6)] + CTX(a),
    lines=[line(a, REL, GZ, W("p09", "submarine"), W("p09", "submarine") + 1.8, WHITE, True, "Warning: 11 minutes")],
    labels=[lab(a, [-60, 46], "Our simulation", W("p09", "simulation"), YELLOW)])
a = S("p10")
reg("c1-q", a, S("p11"), [("s", off(-30, 45), 300), (W("p10", "toward"), off(-35, 48), 260), ("e", off(-35, 50), 220)], tag="REAL DATA", clock="", source=SRC1,
    cities=[WHC(a, a + 0.2, "White House"), MWC(a, W("p10", "move")), RRC(a, W("p10", "toward"))],
    lines=[line(a, GZ, MW, W("p10", "how"), W("p10", "how") + 1.6, WHITE, True, "How far away?"), line(a, GZ, RR, W("p10", "far"), W("p10", "far") + 1.6, WHITE, True)])

# ================================================================== Chapter 02 [REAL HISTORY] how close, how fast
a = chapter("c2-card", S("p11"), 3.5, "CHAPTER 02", "How close, how fast", "REAL HISTORY")
a = round(S("p11") + 3.5, 2)
tRv, tBuilt = W("p11", "Raven"), W("p11", "built")
reg("c2-sites1", a, tBuilt, [("s", off(-35, 40), 300), (tRv, off(-35, 58), 280), (W("p11", "Pentagon's"), off(-30, 62), 240)], tag="REAL HISTORY", source=SRC2, clock="",
    cities=[WHC(a, a + 0.1), MWC(a, a + 0.3), RRC(a, tRv)],
    lines=[line(a, GZ, MW, a + 0.9, a + 2.6, BLUE, True, "50 to 60 miles west"), line(a, GZ, RR, W("p11", "north"), W("p11", "north") + 1.8, BLUE, True, "About 60 miles north")],
    labels=[lab(a, offp(MW, 0, -9), "FEMA command centre", W("p11", "FEMA's"), WHITE), lab(a, offp(RR, 0, 10), "Pentagon's emergency home", W("p11", "Pentagon's"), YELLOW)])
a = tBuilt
reg("c2-rr2", a, S("p12"), [("s", offp(RR, -10, -25), 220), ("e", RR, 150)], tag="REAL HISTORY", source=SRC2, clock="EARLY 1950s", clockLabel="RAVEN ROCK", clockRate=0,
    cities=[RRC(a, a + 0.2, "Raven Rock, Pennsylvania")],
    labels=[lab(a, offp(RR, 0, -10), "Built in the early 1950s", W("p11", "early"), WHITE), lab(a, offp(RR, 0, -19), "The underground Pentagon", W("p11", "underground"), YELLOW)])
a = S("p12")
tGb = W("p12", "Greenbrier")
CL12 = dict(clock="1959 TO 1962", clockLabel="THE THIRD SITE", clockRate=0)
reg("c2-gb1", a, tGb, [("s", off(-80, 5), 560), (W("p12", "third"), off(-130, -30), 640), ("e", off(-170, -50), 560)], tag="REAL HISTORY", source=SRC2, **CL12,
    cities=[WHC(a, a + 0.2), MWC(a, a + 0.5), RRC(a, a + 0.7)],
    labels=[lab(a, off(-60, 85), "Built 1959 to 1962", W("p12", "fifty-nine"), WHITE), lab(a, off(-60, 73), "A third site, for all of Congress", W("p12", "third"), YELLOW), lab(a, off(-60, 61), "Under a hotel wing", W("p12", "hotel"), WHITE)])
a = tGb
tPost = W("p12", "Washington")
reg("c2-gb2", a, tPost, [("s", off(-170, -50), 560), (W("p12", "about"), off(-150, -45), 520), ("e", off(-150, -45), 430)], tag="REAL HISTORY", source=SRC2, **CL12,
    cities=[GBC(a, a + 0.2, "The Greenbrier, West Virginia"), WHC(a, a + 0.5, "Washington")],
    lines=[line(a, GZ, GB, W("p12", "about"), W("p12", "about") + 2.0, BLUE, True, "About 300 km")],
    labels=[lab(a, off(-150, 10), "Secret for 30 years", W("p12", "thirty"), YELLOW)])
a = tPost
tNev = W("p12", "never")
reg("c2-exposed", a, W("p12", "whole"), [("s", off(-150, -45), 430), (W("p12", "closed"), off(-160, -50), 380), ("e", off(-170, -55), 330)], tag="REAL HISTORY", source=SRC2, clock="1992", clockLabel="EXPOSED", clockRate=0,
    cities=[GBC(a, a + 0.1, "The Greenbrier")],
    labels=[lab(a, offp(GB, 0, 25), "The Washington Post exposes it", W("p12", "Washington"), WHITE), lab(a, offp(GB, 0, 17), "1992", W("p12", "ninety-two"), YELLOW),
            lab(a, offp(GB, 0, -15), "Closed at once", W("p12", "closed"), WHITE), lab(a, offp(GB, 0, -23), "Never needed", tNev, YELLOW)])
a = W("p12", "whole")
reg("c2-idea", a, S("p13"), [("s", off(-120, -20), 450), (W("p12", "walks"), off(-125, 0), 560), ("e", off(-130, 10), 700)], tag="REAL HISTORY", source=SRC2, clock="",
    cities=[WHC(a, a + 0.2), MWC(a, a + 0.5), RRC(a, a + 0.7), GBC(a, a + 0.9)],
    lines=[line(a, GZ, MW, W("p12", "walks"), W("p12", "walks") + 1.6, BLUE, True), line(a, GZ, RR, W("p12", "walks") + 0.2, W("p12", "walks") + 1.8, BLUE, True), line(a, GZ, GB, W("p12", "walks") + 0.4, W("p12", "walks") + 2.0, BLUE, True)],
    labels=[lab(a, off(-60, 130), "A government that walks away from its capital", W("p12", "walks"), WHITE), lab(a, off(-60, 118), "As old as the hydrogen bomb", W("p12", "hydrogen"), YELLOW)])
a = S("p13")
tTk = W("p13", "The")
glob("c2-1979", a, W("p13", "In", 2), [("s", 48, -25, 900), (W("p13", "attack"), 48, -22, 950), ("e", 46, -30, 1050)], tag="REAL HISTORY", source=SRC2, clock="NOV 1979", clockLabel="FALSE ALARM", clockRate=0, highlight=[HLU],
     markers=[{"at": WASH, "label": "A live warning system", "color": BLUE, "kind": "base", "size": 5, "t": rel(a, W("p13", "system"))}, {"at": MOSCOW, "label": "An attack that was not there", "color": AMBER, "kind": "dot", "t": rel(a, W("p13", "attack"))},
              {"at": [-70, 35.5], "label": "Command post takes off", "color": WHITE, "kind": "dot", "t": rel(a, tTk)}],
     arcs=[{"from": MOSCOW, "to": WASH, "t0": rel(a, W("p13", "attack")), "t1": rel(a, W("p13", "attack")) + 2.4, "color": AMBER, "loft": 0.35}, {"from": [60, 70], "to": WASH, "t0": rel(a, W("p13", "attack")) + 0.3, "t1": rel(a, W("p13", "attack")) + 2.7, "color": AMBER, "loft": 0.4}],
     caption="A training tape in a live system.")
a = W("p13", "In", 2)
glob("c2-1980", a, W("p13", "He"), [("s", 52, -10, 900), (W("p13", "two"), 50, -18, 950), ("e", 48, -25, 1000)], tag="REAL HISTORY", source=SRC2, clock="JUN 1980", clockLabel="A SECOND FALSE ALARM", clockRate=0, highlight=[HLU],
     markers=[{"at": WASH, "label": "National security adviser", "color": BLUE, "kind": "base", "size": 5, "t": rel(a, W("p13", "national"))}, {"at": MOSCOW, "label": "2,200 Soviet missiles reported", "color": AMBER, "kind": "dot", "t": rel(a, W("p13", "two"))}],
     arcs=[{"from": src, "to": WASH, "t0": rel(a, W("p13", "two")) + 0.2 * i, "t1": rel(a, W("p13", "two")) + 2.2 + 0.2 * i, "color": AMBER, "loft": 0.3 + 0.03 * i} for i, src in enumerate([MOSCOW, [60, 70], [90, 65], [135, 55], [30, 62], [110, 50]])])
a = W("p13", "He")
reg("c2-minute", a, S("p14"), [("s", GZ, 300), (W("p13", "minute"), GZ, 230), ("e", GZ, 170)], tag="REAL HISTORY", source=SRC2, clock="JUN 1980", clockLabel="A SECOND FALSE ALARM", clockRate=0,
    cities=[WHC(a, a + 0.2, "The president"), city(a, off(-9, -5), "Pentagon", a + 0.8, BLUE, "dot", 5)],
    labels=[lab(a, off(-100, 55), "About a minute from calling the president", W("p13", "minute"), WHITE), lab(a, off(-100, 43), "The warning proved false", W("p13", "proved"), YELLOW)])
a = S("p14")
tUn = W("p14", "Both", 2)
stamp("c2-computer", a, W("p14", "Both", 2) - 1.4, "A COMPUTER, NOT AN ENEMY", "Both times", AMBER, tag="REAL HISTORY", source=SRC2)
a = W("p14", "Both", 2) - 1.4
tRad = round(S("p15") - 3.9, 2)
reg("c2-clock", a, tRad, [("s", GZ, 270), (W("p14", "clock"), off(-5, 0), 210), ("e", off(-8, 0), 160)], tag="REAL HISTORY", source=SRC2, clock="",
    cities=[WHC(a, a + 0.2, "White House"), city(a, off(-9, -5), "Pentagon", a + 0.7, BLUE, "dot", 5)],
    labels=[lab(a, off(-100, 52), "Both times, the clock was the problem", W("p14", "clock"), YELLOW), lab(a, off(-100, 40), "Deciding in minutes", W("p14", "deciding"), WHITE)])
a = tRad
add(id="c2-radar", type="radar", start=a, end=S("p15"), tag="REAL HISTORY", title="Warning screen", lines=[{"k": "november 1979", "v": "a training tape"}, {"k": "june 1980", "v": "a computer fault"}, {"k": "check against", "v": "nothing"}], tracks=3, big="FALSE ALARM", bigColor=AMBER, footer="On a screen, with nothing to check it against.", source=SRC2)
a = S("p15")
glob("c2-flight", a, W("p15", "Analysts") - 0.3, [("s", 46, 0, 760), (W("p15", "submarine"), 44, -22, 950), ("e", 40, -50, 1250)], tag="REAL HISTORY", source=SRC2, clock="", highlight=[HLU],
     markers=[{"at": [55, 57], "label": "From a silo", "color": AMBER, "kind": "base", "size": 5, "t": rel(a, W("p15", "silo"))}, {"at": WASH, "label": "About 30 minutes", "color": BLUE, "kind": "target", "size": 5, "t": rel(a, W("p15", "thirty"))},
              {"at": REL, "label": "From a submarine offshore", "color": WHITE, "kind": "sub", "size": 5, "t": rel(a, W("p15", "submarine"))}, {"at": [-72, 36], "label": "As little as 10 to 15", "color": RED, "kind": "dot", "t": rel(a, W("p15", "ten"))}],
     arcs=[{"from": [55, 57], "to": WASH, "t0": rel(a, W("p15", "missile")), "t1": rel(a, W("p15", "missile")) + 3.0, "color": AMBER, "loft": 0.5}, {"from": REL, "to": WASH, "t0": rel(a, W("p15", "offshore")), "t1": rel(a, W("p15", "offshore")) + 2.0, "color": RED, "loft": 0.2}])
a = W("p15", "Analysts") - 0.3
reg("c2-ana", a, S("p16"), [("s", GZ, 400), (W("p15", "less"), GZ, 260), (W("p15", "analyst's"), off(-8, 0), 200), ("e", GZ, 160)], tag="REAL HISTORY", source="Congressional Research Service", clock="T-10:00", clockLabel="THE DECISION WINDOW", clockRate=1,
    cities=[WHC(a, a + 0.2), city(a, off(-9, -5), "Pentagon", a + 1.0, BLUE, "dot", 5)],
    labels=[lab(a, off(-130, 70), "Analysts' estimate", W("p15", "Analysts"), YELLOW), lab(a, off(-130, 58), "Under 10 minutes to decide", W("p15", "less"), WHITE),
            lab(a, off(-130, 46), "An analyst's estimate", W("p15", "analyst's"), YELLOW), lab(a, off(-130, 34), "Not an official figure", W("p15", "not"), WHITE)])
a = S("p16")
tFirst = W("p16", "first")
reg("c2-sites2", a, S("p17"), [("s", off(-120, 0), 620), (W("p16", "none"), off(-125, 10), 700), (tFirst, off(-20, 0), 300), ("e", GZ, 170)], tag="REAL HISTORY", source=SRC2, clock="",
    cities=[WHC(a, a + 0.2, "White House"), MWC(a, a + 0.5), RRC(a, a + 0.7), GBC(a, a + 0.9)],
    lines=[line(a, GZ, MW, a + 0.5, a + 2.0, BLUE, True), line(a, GZ, RR, a + 0.7, a + 2.2, BLUE, True), line(a, GZ, GB, a + 0.9, a + 2.4, BLUE, True)],
    labels=[lab(a, off(-60, 130), "Every one built to answer it", W("p16", "built"), WHITE), lab(a, off(-60, 118), "None has faced a nuclear attack", W("p16", "faced"), YELLOW), lab(a, off(-60, 106), "So what happens in the first minutes?", tFirst, WHITE)])

# ================================================================== Chapter 03 [SIMULATION] the trigger
a = chapter("c3-card", S("p17"), 3.5, "CHAPTER 03", "The trigger", "SIMULATION")
CL3 = dict(clock="T-11:06", clockLabel="TO BURST", clockRate=0)
tYield = W("p18", "We")
reg("c3-launch", a, tYield, [("s", [-60, 40.5], 3900), (W("p17", "North"), [-62, 40.2], 3700), (W("p17", "name"), [-63, 40.0], 3550), ("e", [-64, 40.0], 3450)], **CL3, highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, REL, "Submarine (simulated)", W("p17", "submarine"), WHITE, "base", 6), city(a, GZ, "Washington", a + 0.5, RED, "target", 6)] + CTX(a),
    lines=[line(a, REL, GZ, W("p17", "choose"), W("p17", "choose") + 2.5, WHITE, True), line(a, REL, GZ, W("p18", "carries"), W("p18", "carries") + 2.5, RED, False, None, 3)],
    labels=[lab(a, [-60, 47], "Open North Atlantic", W("p17", "open"), GREY), lab(a, [-60, 45.8], "Launch point: our choice", W("p17", "launch"), YELLOW), lab(a, [-60, 34.5], "No attacker named", W("p17", "no"), WHITE), lab(a, [-60, 33.3], "One warhead", W("p18", "carries"), RED)])
a = tYield
num("c3-yield", a, W("p18", "detonating"), "100 KILOTONS", countTo=100, suffix=" KILOTONS", label="the yield we choose", sub="a simulation choice, not a fact", color=YELLOW)
a = W("p18", "detonating")
cty("c3-air", a, S("p19"), [("s", GZ, 40), (W("p18", "ten"), GZ, 26), (W("p18", "flight"), GZ, 17), ("e", GZ, 12)], clock="10:00", clockLabel="LAUNCH TIME: OUR CHOICE", clockRate=0,
    labels=[lab(a, off(0, 5.0), "Airburst over central Washington", W("p18", "air"), WHITE), lab(a, off(0, -6.0), "10 o'clock in the morning", W("p18", "ten"), YELLOW), lab(a, off(0, -4.0), "Flight: 11 minutes", W("p18", "eleven"), WHITE)])
a = S("p19")
reg("c3-why", a, W("p19", "We"), [("s", GZ, 520), (W("p19", "real"), GZ, 380), (W("p19", "published"), GZ, 300), ("e", GZ, 220)], **CL3,
    cities=[WHC(a, a + 0.3)],
    labels=[lab(a, off(-170, 90), "Why one warhead?", a + 0.2, YELLOW), lab(a, off(-170, 78), "Real plans use many", W("p19", "real"), WHITE), lab(a, off(-170, 66), "No published plan", W("p19", "published"), WHITE), lab(a, off(-170, 54), "A single strike on Washington", W("p19", "single"), YELLOW)])
a = W("p19", "We")
cty("c3-small", a, S("p20"), [("s", GZ, 50), (W("p19", "smallest"), GZ, 34), (W("p19", "watch"), GZ, 22), ("e", GZ, 30)], **CL3,
    labels=[lab(a, off(0, 14), "The smallest case", W("p19", "smallest"), YELLOW), lab(a, off(0, 11), "It lets us watch the response", W("p19", "watch"), WHITE), lab(a, off(0, -11), "Instead of a war", W("p19", "instead"), WHITE)])
a = S("p20")
reg("c3-orders", a, S("p21"), [("s", GZ, 320), (W("p20", "follow"), off(-8, 0), 230), (W("p20", "stop"), GZ, 190), ("e", GZ, 160)], **CL3,
    cities=[WHC(a, a + 0.3), city(a, off(-9, -5), "Pentagon", a + 0.7, BLUE, "dot", 5), city(a, CAP, "Capitol", a + 1.0, BLUE, "dot", 5)],
    labels=[lab(a, off(-100, 50), "The president's orders: not modelled", W("p20", "orders"), YELLOW), lab(a, off(-100, 40), "We follow the government's movement only", W("p20", "follow"), WHITE), lab(a, off(-100, 30), "We stop at the flash", W("p20", "stop"), RED)])
a = S("p21")
tNet = W("p21", "nuclear")
glob("c3-sat", a, tNet - 0.2, [("s", 42, -60, 950), (W("p21", "Radars"), 40, -68, 1250), ("e", 39, -73, 1650)], **CL3, highlight=HLUS,
     markers=[{"at": REL, "label": "Satellites see the launch", "color": WHITE, "kind": "sub", "size": 6, "t": rel(a, W("p21", "see"))}, {"at": [-66, 33], "label": "Radars confirm it", "color": YELLOW, "kind": "dot", "t": rel(a, W("p21", "Radars"))},
              {"at": [-72, 41.5], "label": "A second kind of sensor", "color": YELLOW, "kind": "dot", "t": rel(a, W("p21", "second"))}, {"at": GZ, "label": "Dual phenomenology", "color": BLUE, "kind": "target", "size": 5, "t": rel(a, W("p21", "dual"))}],
     arcs=[{"from": REL, "to": GZ, "t0": rel(a, W("p21", "launch")), "t1": rel(a, W("p21", "launch")) + 3.0, "color": RED, "loft": 0.3}])
a = tNet - 0.2
num("c3-250", a, round(a + 3.9, 2), "ABOUT 250", countTo=250, prefix="ABOUT ", label="systems in nuclear command and control", sub="ground, space and airborne", color=BLUE, tag="REAL DATA", source="Congressional Research Service")
a = round(tNet - 0.2 + 3.9, 2)
reg("c3-min", a, S("p22"), [("s", [-60, 40.5], 3900), (W("p21", "Congressional"), [-62, 40.2], 3700), (W("p21", "every"), [-63, 40.0], 3550), ("e", [-64, 40.0], 3450)], clock="T-11:06", clockLabel="TO BURST", clockRate=1, highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, REL, "Launch (simulated)", a + 0.2, WHITE, "base", 6), city(a, GZ, "Washington", a + 0.4, RED, "target", 6)] + CTX(a),
    ships=[ship(a, [REL, GZ], a + 0.2, S("p22") - 0.3, label="Missile", color=RED, t_on=a + 0.2, size=4.5)],
    lines=[line(a, REL, GZ, a + 0.2, S("p22") - 0.3, RED, False, None, 3)],
    labels=[lab(a, [-60, 47], "CRS count of the systems", W("p21", "Congressional"), YELLOW), lab(a, [-60, 45.8], "Each minute of warning comes out of the eleven", W("p21", "every"), WHITE)])
a = S("p22")
cty("c3-who", a, S("p23"), [("s", GZ, 40), (W("p22", "who"), GZ, 26), ("e", GZ, 16)], **CL3,
    labels=[lab(a, off(0, 8), "The first question", a + 0.2, YELLOW), lab(a, off(0, -5.5), "Who moves?", W("p22", "who"), WHITE), lab(a, off(0, -4.0), "How fast?", W("p22", "how"), WHITE)])

# ================================================================== Chapter 04 [SIMULATION] minute by minute
a = chapter("c4-card", S("p23"), 3.5, "CHAPTER 04", "Minute by minute", "SIMULATION")


def CLm(n, label=None):
    return dict(clock=f"T+{n:02d}:00", clockLabel=label or f"MINUTE {n}", clockRate=1)


PENTC = lambda a_, t: city(a_, PENT, "Pentagon", t, BLUE, "dot", 5)
CAPC = lambda a_, t: city(a_, CAP, "Capitol", t, BLUE, "dot", 5)
a = round(S("p23") + 3.5, 2)
reg("c4-m0", a, S("p24"), [("s", GZ, 200), (W("p23", "alert"), off(-6, 0), 150), (W("p23", "Every"), off(-4, 0), 190), ("e", off(-6, 0), 230)], **CLm(0),
    cities=[WHC(a, a + 0.2), PENTC(a, a + 0.5), CAPC(a, a + 0.8)],
    lines=[line(a, off(-9, -5), GZ, W("p23", "alert"), W("p23", "alert") + 1.6, YELLOW, False, "Alert up the chain")],
    labels=[lab(a, off(-70, 40), "Satellites: launch detected", W("p23", "satellites"), WHITE), lab(a, off(-70, 28), "Every step after: our choice", W("p23", "choice"), YELLOW), lab(a, off(-70, 16), "Not a documented schedule", W("p23", "documented"), WHITE)])
a = S("p24")
tPres = W("p24", "president")
cty("c4-m2a", a, W("p24", "They", 1) + 2.0, [("s", GZ, 30), (W("p24", "assess"), off(-3, -1.5), 18), ("e", off(-4, -2), 14)], **CLm(2),
    labels=[lab(a, off(0, 2.5), "Minute two", a + 0.3, WHITE), lab(a, offp(PENT, 0, 0.9), "Warning assessed against a second sensor", W("p24", "assess"), YELLOW), lab(a, offp(PENT, 0, -0.9), "No time for a long review", W("p24", "time"), WHITE)])
a = W("p24", "They", 1) + 2.0
reg("c4-m2b", a, W("p24", "belongs") - 0.6, [("s", GZ, 150), (W("p24", "emergency"), off(-6, 0), 190), ("e", off(-6, 0), 150)], **CLm(2),
    cities=[WHC(a, a + 0.2), PENTC(a, a + 0.5), CAPC(a, a + 0.8)],
    lines=[line(a, GZ, off(-1.7, -2.9), W("p24", "emergency"), W("p24", "emergency") + 1.5, YELLOW, False, "Emergency conference")],
    labels=[lab(a, off(-55, 38), "The president joins", tPres, WHITE), lab(a, off(-55, 28), "Senior officials", W("p24", "senior"), WHITE)])
a = W("p24", "belongs") - 0.6
cty("c4-m2c", a, S("p25"), [("s", GZ, 24), (W("p24", "Neither"), off(-0.5, -0.8), 16), ("e", off(0.5, -0.5), 20)], **CLm(2),
    labels=[lab(a, off(0, 4.0), "The president alone: authority to order a strike", a + 0.2, YELLOW), lab(a, offp(PENT, 0, -1.0), "Military: cannot overrule", W("p24", "military"), WHITE), lab(a, offp(CAP, 0, 1.0), "Congress: cannot overrule", W("p24", "Congress"), WHITE)])
a = S("p25")
tFoot = W("p25", "football")
cty("c4-m4a", a, W("p25", "this"), [("s", GZ, 14), (W("p25", "codes"), off(1, -0.5), 9), ("e", off(2, -1), 11)], **CLm(4),
    labels=[lab(a, off(0, 2.0), "Secret Service takes the president out", W("p25", "Secret"), WHITE), lab(a, off(0, -1.8), "The football: authentication codes", tFoot, YELLOW)])
a = W("p25", "this")
reg("c4-m4b", a, S("p26"), [("s", off(5, -2), 150), (W("p25", "aircraft"), off(10, -4), 170), ("e", off(14, -6), 190)], **CLm(4),
    cities=[WHC(a, a + 0.2, "White House"), city(a, off(25, -12), "An aircraft: our choice", W("p25", "aircraft"), BLUE, "base", 6)],
    ships=[ship(a, [GZ, off(25, -12)], W("p25", "heads"), W("p25", "city") + 0.6, label="President", color=BLUE, kind="us", t_on=W("p25", "heads"), size=2.2)],
    labels=[lab(a, off(-35, 22), "Not a bunker under the city", W("p25", "bunker"), WHITE), lab(a, off(-35, 12), "Our choice, not a documented plan", W("p25", "choice"), YELLOW)])
a = S("p26")
tSpot = W("p26", "not")
reg("c4-m5a", a, W("p26", "It"), [("s", GZ, 700), (W("p26", "modified"), off(-100, 0), 800), ("e", off(-200, 0), 900)], **CLm(5),
    cities=[WHC(a, a + 0.3, "White House")],
    labels=[lab(a, off(-250, 50), "Flying command post: the E-4B", W("p26", "flying"), YELLOW), lab(a, off(-250, 38), "A modified Boeing 747", W("p26", "modified"), WHITE), lab(a, off(-250, 26), "Not on the spot", tSpot, RED)])
a = W("p26", "It")
reg("c4-m5b", a, W("p26", "carry") - 0.3, [("s", [-86.5, 40.3], 3100), (W("p26", "sixteen"), [-86.5, 40.3], 2700), ("e", [-87, 40.3], 2400)], **CLm(5), highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, OFFUTT, "Offutt, Nebraska", W("p26", "Offutt"), BLUE, "base", 6), WHC(a, a + 0.4, "Washington")],
    lines=[line(a, OFFUTT, GZ, W("p26", "sixteen"), W("p26", "sixteen") + 2.0, WHITE, True, "About 1,600 km")])
a = W("p26", "carry") - 0.3
reg("c4-m5c", a, W("p26", "It", 4) - 0.2, [("s", offp(OFFUTT, 150, -30), 900), (W("p26", "week"), offp(OFFUTT, 100, -30), 700), ("e", offp(OFFUTT, 50, -20), 520)], **CLm(5), highlight=HLUS,
    cities=[city(a, OFFUTT, "Offutt Air Force Base", a + 0.2, BLUE, "base", 6)],
    labels=[lab(a, offp(OFFUTT, 330, 100), "Carries about 100 people", W("p26", "carry"), WHITE), lab(a, offp(OFFUTT, 330, 85), "Aloft for about a week, with refuelling", W("p26", "week"), YELLOW), lab(a, offp(OFFUTT, 330, 70), "Shielded against EMP", W("p26", "shielded"), WHITE)])
a = W("p26", "It", 4) - 0.2
reg("c4-m5d", a, W("p26", "needs"), [("s", [-86.5, 40.3], 2500), (W("p26", "cannot"), [-86.5, 40.3], 2800), ("e", [-85, 40.2], 3300)], **CLm(5), highlight=HLUS, countryLabels=CLUS,
    cities=[city(a, OFFUTT, "Offutt", a + 0.2, BLUE, "base", 6), WHC(a, a + 0.4, "Washington")],
    ships=[ship(a, [OFFUTT, lerp(OFFUTT, GZ, 0.1)], W("p26", "cannot"), W("p26", "minutes") + 0.2, label="E-4B after 11 minutes", color=BLUE, kind="us", t_on=W("p26", "cannot"), size=2.4)],
    labels=[lab(a, [-92, 46], "It cannot be there in eleven minutes", W("p26", "cannot"), YELLOW)])
a = W("p26", "needs")
cty("c4-m5e", a, S("p27"), [("s", GZ, 40), (W("p26", "other"), off(8, -4), 22), ("e", off(5, -3), 34)], **CLm(5),
    labels=[lab(a, off(10, 0), "In this simulation", a + 0.2, YELLOW), lab(a, off(10, -4), "Some other aircraft first", W("p26", "other"), WHITE)])
a = S("p27")
reg("c4-m6a", a, W("p27", "as"), [("s", off(-20, 12), 190), (W("p27", "congressional"), off(-30, 15), 170), ("e", off(-40, 18), 160)], **CLm(6),
    cities=[CAPC(a, a + 0.3), MWC(a, W("p27", "toward"))],
    ships=[ship(a, [CAP, lerp(CAP, MW, 0.55)], W("p27", "congressional"), W("p27", "as") + 0.1, label="Congressional leaders", color=BLUE, kind="us", t_on=W("p27", "congressional"), size=2.2)],
    labels=[lab(a, off(-95, 45), "Congressional leaders flown out", W("p27", "flown"), WHITE)])
a = W("p27", "as")
reg("c4-m6b", a, S("p28"), [("s", off(-40, 40), 230), (W("p27", "Raven"), off(-35, 50), 280), ("e", off(-35, 50), 300)], **CLm(6),
    cities=[MWC(a, a + 0.2), RRC(a, W("p27", "Raven")), city(a, GZ, "Washington", a + 0.4, WHITE, "dot", 5)],
    ships=[ship(a, [lerp(CAP, MW, 0.55), MW], a + 0.1, a + 2.8, label="", color=BLUE, kind="us", t_on=a + 0.1, size=2.2)],
    rings=[ring(a, MW, 8, W("p27", "Mount", 2), "Activated", BLUE), ring(a, RR, 8, W("p27", "activated"), "Activated", BLUE)],
    labels=[lab(a, off(-110, 20), "As on September 11", W("p27", "September"), YELLOW)])
a = S("p28")
cty("c4-m8a", a, W("p28", "In"), [("s", GZ, 26), (W("p28", "capitol"), GZ, 18), ("e", off(0, 0), 15)], **CLm(8),
    labels=[lab(a, offp(PENT, 0, -1.0), "Pentagon: counting", W("p28", "Pentagon"), WHITE), lab(a, offp(CAP, 0, 1.0), "Capitol: counting", W("p28", "Capitol"), WHITE), lab(a, off(0, 2.0), "Cabinet offices: counting", W("p28", "cabinet"), WHITE),
            lab(a, off(0, -6), "Who has left, who has not", W("p28", "who"), YELLOW)])
a = W("p28", "In")
cty("c4-m8b", a, S("p29"), [("s", GZ, 15), (W("p28", "many"), GZ, 22), ("e", GZ, 34)], **CLm(8),
    labels=[lab(a, off(0, 2.5), "Many have not left", W("p28", "many"), YELLOW), lab(a, off(0, -4.5), "Who: not modelled", W("p28", "model"), WHITE)])
a = S("p29")
tMiss = off(300, -30)
CL10 = dict(clock="T+10:00", clockLabel="ABOUT ONE MINUTE LEFT", clockRate=6.5)
reg("c4-m10a", a, W("p29", "What"), [("s", off(140, -10), 420), (W("p29", "president"), off(140, -10), 380), ("e", off(120, -10), 330)], **CL10,
    cities=[WHC(a, a + 0.2, "White House")],
    ships=[ship(a, [tMiss, lerp(tMiss, GZ, 0.55)], a + 0.1, W("p29", "What"), label="Warhead: about a minute out", color=RED, t_on=a + 0.1, size=1.8)],
    labels=[lab(a, off(40, 60), "About one minute left", W("p29", "About"), YELLOW), lab(a, off(40, 49), "An aircraft: orders can still be given", W("p29", "reached"), BLUE)])
a = W("p29", "What")
tImp = W("p30", "Impact")
reg("c4-m10b", a, tImp, [("s", off(120, -10), 330), ("e", off(60, -4), 210)], **dict(clock="T+10:53", clockLabel="THE LAST MINUTE", clockRate=1),
    cities=[WHC(a, a + 0.2, "White House")],
    ships=[ship(a, [lerp(tMiss, GZ, 0.55), GZ], a + 0.1, tImp - 0.15, label="Warhead", color=RED, t_on=a + 0.1, size=1.8)],
    labels=[lab(a, off(40, 45), "What the orders are: outside the simulation", W("p29", "What"), WHITE), lab(a, off(40, 34), "Minute eleven", W("p30", "eleven"), YELLOW)])
a = tImp
cty("c4-impact", a, S("p32"), [("s", GZ, 6), (W("p31", "kilotons"), GZ, 12), ("e", GZ, 26)], clock="T+11:06", clockLabel="IMPACT", clockRate=1, flashT=0.1,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.7, "Fireball", WHITE), ring(a, GZ, FX["psi5_km"], W("p31", "ring"), "5 psi", RED)],
    labels=[lab(a, off(0, 1.2), "Impact", a + 0.4, WHITE), lab(a, off(0, -7), "Next: what 100 kilotons does", W("p31", "what"), YELLOW)])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = chapter("c5-card", S("p32"), 3.5, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
CK = dict(clock="T+11:06", clockLabel="THE 100 kt WARHEAD", clockRate=0)
a = round(S("p32") + 3.5, 2)
cty("c5-engine", a, S("p33"), [("s", GZ, 26), (W("p32", "estimates"), GZ, 18), ("e", GZ, 12)], **CK,
    labels=[lab(a, off(0, 4.5), "Every number: our scenario engine", a + 0.2, WHITE), lab(a, off(0, -3.8), "Estimates for a labelled simulation", W("p32", "estimates"), YELLOW)])
a = S("p33")
tAlm = W("p33", "almost")
cty("c5-fire", a, S("p34"), [("s", GZ, 3.4), (tAlm, GZ, 2.6), (W("p33", "above"), GZ, 2.2), ("e", GZ, 2.9)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], W("p33", "fireball"), "Fireball: radius", WHITE)],
    labels=[lab(a, off(0, 0.75), "Almost 800 m across", tAlm, YELLOW), lab(a, off(0, -0.6), "Above the White House", W("p33", "above"), WHITE)])
a = S("p34")
cty("c5-20", a, S("p35"), [("s", GZ, 3.0), (W("p34", "pounds"), GZ, 2.7), ("e", GZ, 3.4)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "", WHITE), ring(a, GZ, FX["psi20_km"], W("p34", "six"), "20 psi: radius", RED)],
    labels=[lab(a, off(0, 0.85), "The blast adds 20 psi", W("p34", "blast"), YELLOW), lab(a, off(0, -0.85), "Almost nothing stays standing", W("p34", "nothing"), WHITE)])
a = S("p35")
cty("c5-5psi", a, W("p35", "Capitol") - 0.2, [("s", GZ, 5.0), (W("p35", "three"), GZ, 7.2), (W("p35", "thirty-one"), GZ, 8.6), ("e", GZ, 9.0)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "", WHITE), ring(a, GZ, FX["psi20_km"], a + 0.2, "", RED), ring(a, GZ, FX["psi5_km"], W("p35", "three"), "5 psi: radius", RED)],
    labels=[lab(a, off(0, 3.6), "Wrecks most buildings", W("p35", "wrecks"), YELLOW), lab(a, off(0, -3.6), "31 square kilometres", W("p35", "thirty-one"), WHITE)])
a = W("p35", "Capitol") - 0.2
cty("c5-cp", a, W("p35", "engine's") - 0.1, [("s", off(1.2, -0.5), 8.5), (W("p35", "Pentagon"), off(-0.4, -1.6), 8.0), ("e", off(-0.8, -1.8), 7.0)], **CK,
    rings=[ring(a, GZ, FX["fireball_km"], a + 0.1, "", WHITE), ring(a, GZ, FX["psi5_km"], a + 0.2, "", RED)],
    labels=[lab(a, offp(CAP, 0, 0.6), "Capitol: 2.5 km", W("p35", "Capitol"), WHITE), lab(a, offp(CAP, 0, -0.6), "Inside the ring", W("p35", "inside"), YELLOW),
            lab(a, offp(PENT, 0, -0.6), "Pentagon: 3.3 km", W("p35", "Pentagon"), WHITE), lab(a, offp(PENT, 0, -1.2), "At the edge", W("p35", "sits"), YELLOW)])
a = W("p35", "engine's") - 0.1
cty("c5-unc", a, S("p36"), [("s", off(-0.8, -1.8), 8.0), ("e", GZ, 14)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    labels=[lab(a, off(-3.0, 3.5), "The engine's uncertainty is bigger than the gap", a + 0.3, WHITE), lab(a, off(-3.0, -4.2), "At the edge never means safe", W("p35", "never"), YELLOW)])
a = S("p36")
cty("c5-burn", a, S("p37"), [("s", GZ, 10), (W("p36", "four"), GZ, 12), ("e", GZ, 14)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["thermal3_km"], W("p36", "burns"), "Burns: radius", ORANGE)],
    labels=[lab(a, off(0, 4.8), "The flash burns bare skin", W("p36", "bare"), YELLOW)])
a = S("p37")
cty("c5-win", a, S("p38"), [("s", GZ, 14), (W("p37", "windows"), GZ, 20), ("e", GZ, 24)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["thermal3_km"], a + 0.2, "", ORANGE), ring(a, GZ, FX["psi1_km"], W("p37", "windows"), "Windows: radius", WHITE)],
    labels=[lab(a, off(0, 6.0), "Windows break", W("p37", "windows"), YELLOW), lab(a, off(0, -6.0), "Glass flies", W("p37", "glass"), WHITE)])
a = S("p38")
cty("c5-fallout", a, S("p39"), [("s", GZ, 24), (W("p38", "honest"), GZ, 30), (W("p38", "close"), GZ, 20), ("e", GZ, 14)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["thermal3_km"], a + 0.2, "", ORANGE), ring(a, GZ, FX["psi1_km"], a + 0.3, "", WHITE)],
    labels=[lab(a, off(0, 7.0), "Air burst: little local fallout", W("p38", "air"), WHITE), lab(a, off(0, -6.5), "Mostly blast and heat", W("p38", "mostly"), YELLOW), lab(a, off(0, -4.5), "Close to the centre", W("p38", "close"), WHITE)])
a = S("p39")
tRvn = W("p39", "Raven")
reg("c5-mw", a, W("p39", "In"), [("s", off(-36, 45), 270), (tRvn, off(-38, 46), 240), ("e", off(-38, 46), 215)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    cities=[WHC(a, a + 0.2, "White House"), MWC(a, W("p39", "Mount"), "Mount Weather: 76 km"), RRC(a, tRvn, "Raven Rock: 99 km")],
    lines=[line(a, GZ, MW, W("p39", "Mount") + 0.2, W("p39", "Mount") + 2.0, BLUE, True), line(a, GZ, RR, tRvn + 0.2, tRvn + 2.0, BLUE, True)],
    labels=[lab(a, off(-110, 5), "Far outside every ring", W("p39", "far"), YELLOW)])
a = W("p39", "In")
reg("c5-nobl", a, S("p40"), [("s", off(-38, 46), 215), (W("p39", "result"), off(-38, 46), 250), ("e", off(-38, 46), 280)], **CK,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    cities=[MWC(a, a + 0.2), RRC(a, a + 0.3)],
    labels=[lab(a, off(-100, 5), "In the engine: no blast at either site", W("p39", "take"), WHITE), lab(a, off(-100, -6), "A result for this yield", W("p39", "result"), YELLOW), lab(a, off(-100, -17), "No guarantee for any bunker", W("p39", "guarantee"), RED)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p40"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
CD = dict(clock="10:12", clockLabel="THE DAY AFTER", clockRate=0)
a = round(S("p40") + 3.5, 2)
reg("c6-left", a, S("p41"), [("s", off(-35, 50), 280), (W("p40", "rings"), GZ, 210), ("e", GZ, 170)], **CD,
    cities=[WHC(a, a + 0.2, "White House"), MWC(a, W("p40", "left")), RRC(a, W("p40", "left") + 0.3)],
    rings=[ring(a, GZ, FX["psi5_km"], W("p40", "rings"), "", RED), ring(a, GZ, FX["psi1_km"], W("p40", "rings") + 0.2, "", WHITE)],
    labels=[lab(a, off(-110, 70), "Who had already left the city?", W("p40", "who", 2), YELLOW), lab(a, off(-110, 58), "Start with the map", W("p40", "Start"), WHITE)])
a = S("p41")
tIn = W("p41", "In")
cty("c6-dark", a, tIn, [("s", GZ, 12), (W("p41", "centre"), GZ, 9), ("e", GZ, 8)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    labels=[lab(a, off(0, 2.2), "Inside 3 km of the White House", a + 0.2, WHITE), lab(a, off(0, -2.0), "The centre of the federal government: dark", W("p41", "dark") - 0.6, YELLOW)])
a = tIn
cty("c6-cover", a, S("p42"), [("s", GZ, 10), (W("p41", "executive"), off(0.5, -0.3), 14), ("e", GZ, 22)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], W("p41", "eight"), "Windows break", WHITE)],
    labels=[lab(a, offp(CAP, 0, 0.8), "Capitol", W("p41", "Capitol"), WHITE), lab(a, off(1.0, -1.5), "The Mall", W("p41", "Mall"), WHITE), lab(a, off(0, 1.0), "Executive offices", W("p41", "executive"), WHITE)])
a = S("p42")
tDr = W("p42", "drifts")
reg("c6-plume", a, W("p42", "For"), [("s", off(35, -5), 200), (W("p42", "west-northwest"), off(40, -8), 210), ("e", off(45, -8), 240)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    cities=[WHC(a, a + 0.2, "White House")],
    plume={"at": GZ, "bearing": 112, "lengthKm": 50, "widthKm": 8, "t0": rel(a, tDr), "t1": rel(a, tDr) + 3.5, "color": AMBER, "label": "Plume: direction only"},
    labels=[lab(a, off(-60, 38), "The plume is small", W("p42", "plume"), WHITE), lab(a, off(-60, 28), "Wind: west-northwest (our assumption)", W("p42", "west-northwest"), YELLOW), lab(a, off(64, -12), "Chesapeake Bay", W("p42", "Chesapeake"), WHITE)])
a = W("p42", "For")
cty("c6-after", a, S("p43"), [("s", GZ, 30), (W("p42", "rubble"), GZ, 22), ("e", GZ, 17)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    labels=[lab(a, off(0, 9.5), "Air burst: little local fallout", W("p42", "little"), WHITE), lab(a, off(2.5, 1.2), "Rubble", W("p42", "rubble"), YELLOW), lab(a, off(-2.5, 2.2), "Fire", W("p42", "fire"), ORANGE), lab(a, off(-4.0, -3.5), "Closed bridges", W("p42", "closed"), WHITE)])
a = S("p43")
tRv6 = W("p43", "Raven")
reg("c6-lit", a, W("p43", "Whoever") - 0.4, [("s", off(-38, 42), 320), (W("p43", "Mount"), off(-40, 45), 260), ("e", off(-40, 45), 235)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    cities=[MWC(a, W("p43", "Mount"), "Mount Weather: lit"), RRC(a, tRv6, "Raven Rock: lit")],
    labels=[lab(a, off(-110, 5), "The rings: dark", a + 0.4, RED), lab(a, off(-110, -6), "Two points stay lit outside", W("p43", "points"), YELLOW)])
a = W("p43", "Whoever") - 0.4
reg("c6-law1", a, W("p43", "Speaker") - 0.2, [("s", off(-40, 45), 240), (W("p43", "law"), off(-35, 40), 280), ("e", off(-25, 32), 320)], **CD,
    cities=[MWC(a, a + 0.2), RRC(a, a + 0.3), WHC(a, a + 0.4, "White House")],
    labels=[lab(a, off(-100, 20), "Whoever reached them", a + 0.2, WHITE), lab(a, off(-100, 8), "The law lists who acts next", W("p43", "law"), YELLOW), lab(a, off(-100, -4), "After the president and vice president", W("p43", "after"), WHITE)])
a = W("p43", "Speaker") - 0.2
reg("c6-law2", a, S("p44") - 3.94, [("s", off(-20, 30), 320), (W("p43", "pro"), off(-35, 40), 260), ("e", off(-40, 45), 240)], **CD,
    cities=[MWC(a, a + 0.2), RRC(a, a + 0.3), WHC(a, a + 0.4, "White House")],
    labels=[lab(a, off(-100, 20), "1. Speaker of the House", W("p43", "Speaker"), WHITE), lab(a, off(-100, 8), "2. President pro tempore of the Senate", W("p43", "pro"), WHITE), lab(a, off(-100, -4), "3. Cabinet, by office", W("p43", "cabinet"), YELLOW)])
a = S("p44") - 3.94
num("c6-17", a, S("p44"), "17 IN ALL", countTo=17, suffix=" IN ALL", label="the line of succession", sub="who holds each office is not modelled", color=BLUE, tag="REAL DATA", source="U.S. Code, Title 3, section 19")
a = S("p44")
cty("c6-gap", a, W("p44", "which") - 0.3, [("s", offp(CAP, -1.2, 0.4), 14), (W("p44", "special"), offp(CAP, -0.4, 0.2), 10), ("e", CAP, 8)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    labels=[lab(a, offp(CAP, 0, 1.2), "The hard gap: Congress", a + 0.3, YELLOW), lab(a, offp(CAP, 0, -1.0), "House seats: special elections only", W("p44", "special"), WHITE)])
a = W("p44", "which") - 0.3
num("c6-4mo", a, W("p44", "Governors") - 0.3, "ABOUT 4 MONTHS", countTo=4, prefix="ABOUT ", suffix=" MONTHS", label="for a state to fill a House seat, on average", color=BLUE, tag="REAL DATA", source="Congressional Research Service")
a = W("p44", "Governors") - 0.3
cty("c6-gov", a, W("p44", "In") - 0.2, [("s", offp(CAP, 0.5, 0), 12), (W("p44", "Whether"), offp(CAP, 0.2, 0.3), 9), ("e", CAP, 7)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED)],
    labels=[lab(a, offp(CAP, 0, 1.1), "Governors: Senate seats within days", W("p44", "Governors"), WHITE), lab(a, offp(CAP, 0, -1.0), "A quorum: the living, or the whole chamber?", W("p44", "quorum"), YELLOW), lab(a, offp(CAP, 0, -1.6), "Scholars dispute it", W("p44", "scholars"), WHITE)])
a = W("p44", "In") - 0.2
cty("c6-2003", a, S("p45"), [("s", offp(CAP, 0, 0), 18), (W("p44", "annihilated"), offp(CAP, 0, 0), 26), ("e", offp(CAP, 0, 0), 34)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    labels=[lab(a, offp(CAP, 0, 4.5), "2003: a commission imagines it", W("p44", "commission"), YELLOW), lab(a, offp(CAP, 0, -4.5), "Congress annihilated", W("p44", "annihilated"), WHITE), lab(a, offp(CAP, 0, -6.5), "It urges a constitutional amendment", W("p44", "urged"), WHITE)])
a = S("p45")
tE4 = W("p45", "E-4B")
reg("c6-aloft", a, tE4 - 0.3, [("s", off(-20, 10), 260), (W("p45", "aircraft"), off(-30, 12), 220), ("e", off(-35, 14), 200)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    cities=[WHC(a, a + 0.2, "White House")],
    ships=[ship(a, [off(4, 2), off(-30, 18), off(-70, 30)], a + 0.4, tE4 + 1.0, label="The president's aircraft", color=BLUE, kind="us", t_on=a + 0.4, size=2.4)],
    labels=[lab(a, off(-85, 30), "One aircraft is aloft", W("p45", "aloft"), YELLOW)])
a = tE4 - 0.3
tDes = round(a + 3.9, 2)
num("c6-35", a, tDes, "35 HOURS", countTo=35, suffix=" HOURS", label="the E-4B stayed up in a test", sub="designed for about a week", color=BLUE, tag="REAL DATA", source="Congressional Research Service")
a = tDes
reg("c6-reach", a, S("p46"), [("s", off(-45, 20), 230), (W("p45", "reaches"), off(-30, 20), 330), ("e", off(-25, 15), 440)], **CD,
    rings=[ring(a, GZ, FX["psi5_km"], a + 0.1, "", RED), ring(a, GZ, FX["psi1_km"], a + 0.2, "", WHITE)],
    cities=[WHC(a, a + 0.2, "White House"), MWC(a, a + 0.4, "Mount Weather: lit"), RRC(a, a + 0.6, "Raven Rock: lit")],
    ships=[ship(a, [off(-70, 30), off(-85, 20), off(-100, 5)], a + 0.2, S("p46") - 0.5, label="Aircraft", color=BLUE, kind="us", t_on=a + 0.2, size=2.4)],
    labels=[lab(a, off(40, 50), "Whether it reaches them: not modelled", W("p45", "reaches"), YELLOW), lab(a, off(40, 38), "That is all the map can say", W("p45", "all"), WHITE)])

# ================================================================== End slate
add(id="end", type="endslate", start=S("p46"), end=END, tag="", title="Next scenario", line="How World War Three starts in Europe, conventional first.")


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





def check_keys():
    """Flag camera first legs under 0.25 s and out-of-order keys (a snap zoom is dropped by the engine)."""
    for s in shots:
        ks = s.get("camera")
        if not ks or s["type"] == "globe":
            continue
        ts = [k["t"] for k in ks]
        d = s["end"] - s["start"]
        for x, y in zip(ts, ts[1:]):
            if y - x < 0.25:
                print("KEYWARN", s["id"], "keys too close", ts)
                break
        if ts and ts[-1] > d + 0.01:
            print("KEYWARN", s["id"], "key past end", ts, d)

floors()
densify()
floors()
densify()
check_keys()

# ------------------------------------------------------------------ audio plan and output
BOOMS = [s["start"] + s["flashT"] for s in shots if s.get("flashT") is not None]
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
                    + [{"src": "radar.mp3", "t": s["start"] + 0.1, "gain_db": -12} for s in shots if s["type"] == "radar"]
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
