"""Director pass for episode 014: builds episode.json from narration/timing.json and words.json.

Run from the studio root:  python -m studio shotlist 014-oreshnik-belarus-warning-time
Payoff first: one 50 kt airburst over Ramstein inside 3 s (under the banner), then the run-up from a simulated launch
site in Belarus, real data and history, the minute-by-minute flight times, the ring-by-ring hero strike on a city map
of Ramstein, and the day after. Clocks: Berlin time (03:10 launch) and T+ flight time; never the scenario t0_utc.
"""
import json
import math
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = json.load(open(EP / "narration" / "words.json", encoding="utf-8"))
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW, BLUE, GREY = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F", "#6EA8FF", "#8A8F98"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round(max(w["end"] for w in WORDS if not w["word"].startswith("[")) + 10, 2)
HERO = next(s for s in sc["strikes"] if s["id"] == "hero-ramstein")
FX = HERO["effects"]
REFS = {s["id"].split("-")[1]: s for s in sc["strikes"]}


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
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


shots = []


def add(**k):
    shots.append(k)


def rel(a, t):
    return round(max(0.05, t - a), 2)


# Helpers take ABSOLUTE times; fin() converts every item time to shot-local seconds.
def city(at, label, t, color=None, kind="dot", size=None):
    d = {"at": at, "label": label, "kind": kind, "t": t}
    if color:
        d["color"] = color
    if size:
        d["size"] = size
    return d


def LB(text, fx, fy, t, color=WHITE):
    return {"_fx": fx, "_fy": fy, "text": text, "color": color, "t": t}


def line(p, q, t0, t1, color=WHITE, dashed=True, label=None, width=None):
    d = {"from": p, "to": q, "color": color, "dashed": dashed, "t0": t0, "t1": t1}
    if label:
        d["label"] = label
    if width:
        d["width"] = width
    return d


def ship(path, t0, t1, label="", color=RED, size=2.4, t_on=None):
    return {"path": path, "t0": t0, "t1": t1, "kind": "pla", "color": color, "label": label, "size": size, "t": t0 if t_on is None else t_on, "wake": True}


def ring(at, km, t, label="", color=RED, dashed=False):
    return {"at": at, "km": km, "label": label, "color": color, "t": t, "dashed": dashed}


def offp(base, dx, dy):
    return [round(base[0] + dx / (111.32 * math.cos(math.radians(base[1]))), 5), round(base[1] + dy / 110.57, 5)]


def fin(a, kw):
    for lst in ("cities", "lines", "ships", "rings", "markers", "arcs"):
        out = []
        for it in kw.get(lst, []):
            it = dict(it)
            for k in ("t", "t0", "t1"):
                if isinstance(it.get(k), (int, float)):
                    it[k] = rel(a, it[k]) if k != "t1" else round(max(0.2, it[k] - a), 2)
            out.append(it)
        if out:
            kw[lst] = out
    return kw


def cam(a, b, keys):
    out = []
    for t, c, w in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t))
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def reg(sid, a, b, keys, labs=(), tag="SIMULATION", **kw):
    c = cam(a, b, keys)
    wm = (c[0]["widthKm"] + c[-1]["widthKm"]) / 2
    ctr = c[0]["center"]
    labels = []
    for l in labs:
        l = dict(l)
        fx, fy = l.pop("_fx"), l.pop("_fy")
        l["at"] = offp(ctr, fx * wm, fy * 0.5625 * wm)
        l["t"] = rel(a, l["t"])
        labels.append(l)
    kw = fin(a, kw)
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, labels=labels, **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **fin(a, kw))


def cty(sid, a, b, keys, rings=(), labs=(), tag="SIMULATION", **kw):
    c = cam(a, b, keys)
    wm = (c[0]["widthKm"] + c[-1]["widthKm"]) / 2
    labels = []
    for l in labs:
        l = dict(l)
        fx, fy = l.pop("_fx"), l.pop("_fy")
        l["at"] = offp(GZ, fx * wm, fy * 0.5625 * wm)
        l["t"] = rel(a, l["t"])
        labels.append(l)
    RN = {0.291: ("Fireball", 100, None), 0.508: ("20 psi", 260, None), 2.495: ("5 psi", 225, "#FF8A78"), 3.129: ("Burns", 45, None), 6.752: ("1 psi", 135, None)}
    rs = []
    for i, r in enumerate(rings):
        nm, ang, colr = RN.get(r["km"], (r["label"], (215 + 25 * i) % 360, None))
        rs.append({"km": r["km"], "label": nm, "color": colr or r["color"], "t": rel(a, r["t"]), "angle": ang})
    add(id=sid, type="city", start=a, end=b, tag=tag, city="ramstein", view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, gz=GZ, camera=c, rings=rs, labels=labels, **kw)


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


ISO = {"RU": "643", "PL": "616", "LT": "440", "LV": "428", "EE": "233", "BY": "112", "UA": "804", "DE": "276", "US": "840",
       "GB": "826", "FR": "250", "BE": "056", "RO": "642"}


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": ISO[iso], "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": ISO[iso], "text": text, "color": color}


HL_RU, HL_BY, HL_UA, HL_DE, HL_US = hl("RU", AMBER, 0.08), hl("BY", AMBER, 0.12), hl("UA", TEAL, 0.12), hl("DE", BLUE, 0.10), hl("US", BLUE, 0.08)
HL_NATO = [hl(k, BLUE) for k in ("PL", "LT", "LV", "EE", "DE")]
LEG = [{"text": "RUSSIA, BELARUS", "color": AMBER}, {"text": "NATO", "color": BLUE}]

LAUNCH = [31.72, 53.71]
RAM = [7.6, 49.437]
GZ = RAM
VIL, WAR, BER, BRU, LON = [25.28, 54.687], [21.012, 52.23], [13.405, 52.52], [4.352, 50.85], [-0.128, 51.507]
KY, DNI, LVIV, MSK, MOS = [45.76, 48.57], [35.05, 48.46], [24.03, 49.84], [27.56, 53.9], [37.62, 55.75]
REDZ, DEV, WASH = [17.1, 54.48], [24.4, 44.1], [-77.04, 38.9]
SRC_O = "AP; Reuters; Euronews"
SRC_H = "UK Parliament; CIA assessment; INF Treaty text"
SRC_T = "Jamestown Foundation; Arms Control Association"


def FL(sid, a, b, keys, tgt, t0, t1, mins, label, ship_label="Oreshnik", labs=(), cities=(), color=RED, **kw):
    """A flight on a map: a missile marker and dashed line from the launch point to tgt, with a T+ clock that reaches `mins` at t1."""
    rate = round(mins * 60 / max(t1 - a, 0.5), 1)
    reg(sid, a, b, keys, labs, clock="T+00:00", clockLabel=label, clockRate=rate,
        ships=[ship([LAUNCH, tgt], t0, t1, ship_label, color)], lines=[line(LAUNCH, tgt, t0, t1, color, True)], cities=list(cities), **kw)


def BC(label="BERLIN TIME"):
    return dict(clock="03:10", clockLabel=label, clockRate=0)


# ================================================================== Cold open [SIMULATION]
FLASH = 2.2
CL_DE = [cl("DE", "GERMANY", BLUE), cl("BY", "BELARUS", AMBER)]
reg("open-run", 0, FLASH, [("s", [17.0, 51.8], 2600), ("e", [14.0, 51.0], 1900)],
    [LB("Ramstein Air Base", -0.30, 0.22, 0.15, RED), LB("Launch (simulated)", 0.18, 0.12, 0.3, AMBER)],
    clock="T-08:12", clockLabel="TO IMPACT", clockRate=224, highlight=[HL_BY, HL_DE], countryLabels=CL_DE,
    ships=[ship([LAUNCH, RAM], 0.05, FLASH - 0.05, "Oreshnik", RED, 2.8)], lines=[line(LAUNCH, RAM, 0.05, FLASH - 0.05, RED, True)],
    cities=[city(RAM, "", 0.1, RED, "target", 6)])
a = FLASH
reg("open-burst", a, 5.0, [("s", RAM, 330), ("e", RAM, 190)],
    [LB("Ramstein Air Base", -0.38, -0.22, a + 0.5, WHITE), LB("GERMANY", 0.28, 0.22, a + 0.2, BLUE), LB("50 kiloton airburst", -0.38, -0.30, a + 1.2, YELLOW)],
    clock="03:18", clockLabel="BERLIN TIME", clockRate=0, burst={"at": RAM, "t": 0.1, "km": 8, "fade": 4}, highlight=[HL_DE], countryLabels=[cl("DE", "GERMANY", BLUE)],
    rings=[ring(RAM, 6, a + 0.7, "", RED)], cities=[city(RAM, "", a + 0.5, RED, "target", 6)])
a = 5.0
cty("open-rings", a, S("p02"), [("s", RAM, 5.0), ("e", RAM, 11.0)],
    [ring(RAM, FX["fireball_km"], a + 0.3, "Fireball", WHITE), ring(RAM, FX["psi5_km"], a + 1.2, "5 psi", RED), ring(RAM, FX["psi1_km"], a + 2.2, "Windows", ORANGE)],
    [LB("Ramstein Air Base", -0.30, 0.30, a + 0.3, WHITE)], clock="03:18", clockLabel="BERLIN TIME", clockRate=0,
    caption="Simulation: it has not happened.")
a = S("p02")
tSim, tNot = W("p02", "simulation"), W("p02", "not")
reg("open-sim", a, tNot, [("s", [14.0, 51.0], 2400), ("e", [17.0, 52.0], 3000)],
    [LB("A simulation", -0.30, 0.30, tSim, YELLOW)], clock="03:18", clockLabel="BERLIN TIME", clockRate=0, highlight=[HL_BY, HL_DE], countryLabels=CL_DE,
    cities=[city(RAM, "Ramstein", a + 0.2, RED, "target", 6)])
a = tNot
reg("open-not", a, S("p03"), [("s", [17.0, 52.0], 3000), ("e", [24.0, 53.0], 1800)],
    [LB("It has not happened", -0.30, 0.30, a + 0.1, WHITE)], clock="03:10", clockLabel="BERLIN TIME", clockRate=0, highlight=[HL_BY] + HL_NATO,
    cities=[city(LAUNCH, "Launch site (simulated)", a + 0.3, AMBER, "base", 6)])
a = S("p03")
tLa = W("p03", "launcher")
reg("open-8min", a, tLa, [("s", [28.0, 53.5], 1500), ("e", [30.0, 53.7], 800)],
    [LB("Eight minutes earlier", -0.30, 0.30, a + 0.1, YELLOW), LB("03:10 Berlin time", -0.30, 0.22, W("p03", "Eight") + 0.9, WHITE)],
    clock="03:10", clockLabel="BERLIN TIME", clockRate=0, highlight=[HL_BY], countryLabels=[cl("BY", "BELARUS", AMBER)])
a = tLa
tFo = W("p03", "forest")
reg("open-launcher", a, tFo, [("s", [31.0, 53.7], 600), ("e", LAUNCH, 380)],
    [LB("Road-mobile launcher", -0.30, 0.30, a + 0.1, AMBER)], clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_BY],
    cities=[city(LAUNCH, "Launcher (simulated)", a + 0.3, AMBER, "base", 6)])
a = tFo
reg("open-forest", a, S("p04"), [("s", LAUNCH, 380), ("e", [30.0, 53.7], 900)],
    [LB("A forest in eastern Belarus", -0.30, 0.30, a + 0.1, WHITE), LB("No notice is expected", -0.30, 0.22, W("p03", "No"), YELLOW)],
    clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_BY], cities=[city(LAUNCH, "", a + 0.1, AMBER, "base", 6)])
a = S("p04")
tIn, tNo4 = W("p04", "In"), W("p04", "Nobody")
FL("open-climb", a, tIn, [("s", [30.0, 53.7], 900), ("e", [26.0, 53.5], 1700)], [26.0, 53.5], a + 0.1, tIn + 2.0, 1.0, "SECOND 30", "One missile",
   labs=[LB("One missile climbs", -0.30, 0.30, a + 0.3, RED)], highlight=[HL_BY] + HL_NATO)
a = tIn
tGe = W("p04", "Germany")
reg("open-radars", a, tNo4, [("s", [22.0, 52.5], 2200), ("e", [18.0, 52.0], 2600)],
    [LB("Radars pick up a track", -0.30, 0.32, a + 0.2, YELLOW)], clock="T+00:50", clockLabel="AFTER LAUNCH", clockRate=1, highlight=HL_NATO + [HL_BY],
    cities=[city(WAR, "Poland", W("p04", "Poland"), BLUE), city(VIL, "Lithuania", W("p04", "Lithuania"), BLUE), city(BER, "Germany", tGe, BLUE)],
    lines=[line(LAUNCH, RAM, a, tNo4 + 2, RED, True)])
a = tNo4
reg("open-nobody", a, S("p05"), [("s", [14.0, 51.5], 2600), ("e", [10.0, 50.5], 1400)],
    [LB("What is on top of it?", -0.30, 0.30, a + 0.2, WHITE), LB("Nobody can tell", -0.30, 0.22, W("p04", "tell"), YELLOW)],
    clock="T+02:00", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_DE],
    cities=[city(RAM, "Ramstein", a + 0.5, BLUE, "base", 6)], lines=[line(LAUNCH, RAM, a, a + 1, RED, True)])
a = S("p05")
tMin = W("p05", "minutes")
reg("open-q", a, W("p05", "what"), [("s", [16.0, 52.0], 3600), ("e", [14.0, 51.5], 2600)],
    [LB("How many minutes does Europe get?", -0.28, 0.32, tMin, YELLOW)], clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_BY, HL_DE] + HL_NATO,
    lines=[line(LAUNCH, RAM, a + 0.3, a + 3.0, RED, True)], ships=[ship([LAUNCH, RAM], a + 0.3, a + 3.0, "", RED)],
    cities=[city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6), city(RAM, "Ramstein", a + 0.8, RED, "target", 6)])
a = W("p05", "what")
reg("open-q2", a, S("p06"), [("s", [14.0, 51.5], 2600), ("e", [18.0, 52.0], 3600)],
    [LB("What can anyone do with them?", -0.28, 0.32, a + 0.2, WHITE)], clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_BY, HL_DE] + HL_NATO,
    cities=[city(LAUNCH, "Launch", a + 0.1, AMBER, "base", 6), city(RAM, "Ramstein", a + 0.3, RED, "target", 6)])

# ================================================================== Chapter 01 [REAL DATA] the missile that flew fifteen minutes
a = chapter("c1-card", S("p06"), 3.5, "CHAPTER 01", "The missile that flew fifteen minutes", "REAL DATA")
tDn = W("p06", "Dnipro")
reg("c1-ky", a, tDn, [("s", [40.0, 49.5], 1500), ("e", [41.0, 49.0], 1000)],
    [LB("21 November 2024", -0.30, 0.30, a + 0.2, YELLOW), LB("Kapustin Yar test range", -0.30, 0.22, W("p06", "Kapustin"), WHITE)], tag="REAL DATA", source=SRC_O,
    clock="21 NOV 2024", clockLabel="DNIPRO", clockRate=0, highlight=[HL_UA, HL_RU], cities=[city(KY, "Kapustin Yar", a + 0.5, AMBER, "base", 6)],
    ships=[ship([KY, DNI], a + 0.4, a + 4.4, "Oreshnik", RED, 2.4)], lines=[line(KY, DNI, a + 0.4, a + 4.4, RED, True)])
a = tDn
tFt = W("p06", "Flight")
reg("c1-dn", a, tFt, [("s", [36.0, 48.7], 500), ("e", DNI, 220)],
    [LB("A factory area in Dnipro", -0.30, 0.30, a + 0.2, WHITE), LB("Ukraine", -0.30, 0.22, a + 1.0, TEAL)],
    tag="REAL DATA", source=SRC_O, clock="21 NOV 2024", clockLabel="DNIPRO", clockRate=0, highlight=[HL_UA],
    cities=[city(DNI, "Dnipro", a + 0.1, TEAL), city([35.0, 48.5], "Impact area", a + 1.2, RED, "target", 6)])
a = tFt
num("c1-15", a, S("p07") - 0.5, "15 MIN", countTo=15, suffix=" MIN", label="flight time, Kapustin Yar to Dnipro", sub="about 800 km, 21 November 2024", color=YELLOW, tag="REAL DATA", source=SRC_O)
a = S("p07") - 0.5
tPe, tPu = W("p07", "Pentagon"), W("p07", "Putin")
reg("c1-name", a, tPe, [("s", [37.0, 53.0], 3200), ("e", [40.0, 52.0], 2200)],
    [LB("Oreshnik: the hazel tree", -0.30, 0.30, W("p07", "Oreshnik"), AMBER)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_RU],
    countryLabels=[cl("RU", "RUSSIA", AMBER)], cities=[city(MOS, "Moscow", a + 0.5, AMBER)])
a = tPe
reg("c1-pent", a, tPu, [("s", [-77.0, 39.0], 3000), ("e", [-60, 42], 5200)],
    [LB("Pentagon: experimental IRBM", -0.30, 0.30, a + 0.2, BLUE), LB("Built on an older ICBM design", -0.30, 0.22, W("p07", "built"), WHITE)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_US], cities=[city(WASH, "Pentagon", a + 0.3, BLUE, "base", 6)])
a = tPu
reg("c1-putin", a, S("p08"), [("s", [37.6, 55.8], 1000), ("e", [36.0, 52.0], 3500)],
    [LB("Putin: not a nuclear warhead", -0.30, 0.30, a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_RU],
    cities=[city(MOS, "Moscow", a + 0.1, AMBER)])
a = S("p08")
tNb = W("p08", "Nobody", 2)
reg("c1-by", a, tNb, [("s", [30.0, 53.5], 1500), ("e", [29.0, 53.5], 1100)],
    [LB("The missile from the cold open", -0.30, 0.30, a + 0.1, WHITE), LB("One difference: Belarus", -0.30, 0.22, W("p08", "difference"), YELLOW)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_BY], countryLabels=[cl("BY", "BELARUS", AMBER)], cities=[city(LAUNCH, "Launch (simulated)", a + 2.0, AMBER, "base", 6)])
a = tNb
reg("c1-nato", a, S("p09"), [("s", [24.0, 53.0], 1700), ("e", [20.0, 52.0], 2600)],
    [LB("Never fired from Belarus", -0.30, 0.32, a + 0.2, AMBER), LB("Never fired at NATO", -0.30, 0.24, W("p08", "NATO"), BLUE)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_BY] + HL_NATO, legend=LEG)
a = S("p09")
tJa, tMa9, tBr = W("p09", "January"), W("p09", "May"), W("p09", "Britain")
reg("c1-since", a, tJa, [("s", [34.0, 49.5], 1800), ("e", [30.0, 49.5], 1400)],
    [LB("Since Dnipro: twice more", -0.30, 0.32, a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_UA],
    cities=[city(DNI, "Dnipro, Nov 2024", a + 0.5, TEAL)])
a = tJa
tLv = W("p09", "Lviv")
reg("c1-jm", a, tLv - 0.6, [("s", [32.0, 49.5], 1500), ("e", [28.0, 49.5], 1900)],
    [LB("January 2026", -0.30, 0.32, a + 0.1, YELLOW), LB("May 2026", -0.30, 0.24, tMa9, YELLOW)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_UA],
    cities=[city(DNI, "Ukraine", a + 0.3, TEAL)])
a = tLv - 0.6
tSe = W("p09", "seventy")
reg("c1-jan", a, tBr, [("s", [27.0, 49.5], 1300), ("e", [24.5, 49.9], 520)],
    [LB("Lviv region", -0.30, 0.32, tLv, TEAL)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_UA] + [hl("PL", BLUE)],
    cities=[city(LVIV, "Lviv", tLv, TEAL), city([23.0, 50.0], "Polish border", tSe, BLUE, "dot", 6)], lines=[line(LVIV, [23.0, 50.0], tSe, tSe + 2.0, WHITE, True, "About 70 km")])
a = tBr
tUn = W("p09", "unacceptable")
reg("c1-allies", a, S("p10"), [("s", [8.0, 50.0], 3000), ("e", [12.0, 51.0], 3800)],
    [LB("Britain, France, Germany", -0.30, 0.32, a + 0.2, BLUE), LB("Escalatory", -0.30, 0.24, W("p09", "escalatory"), YELLOW), LB("Unacceptable", -0.30, 0.16, tUn, RED)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[hl("GB", BLUE), hl("FR", BLUE), HL_DE], countryLabels=[cl("GB", "UK", BLUE), cl("FR", "FRANCE", BLUE), cl("DE", "GERMANY", BLUE)])
a = S("p10")
tSp = W("p10", "speed")
reg("c1-noexp", a, tSp, [("s", [35.0, 48.5], 600), ("e", DNI, 260)],
    [LB("Conventional version", -0.30, 0.32, a + 0.1, WHITE), LB("No explosive, analysts say", -0.30, 0.24, W("p10", "explosive"), YELLOW)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_UA], cities=[city(DNI, "Dnipro", a + 0.3, TEAL)])
a = tSp
reg("c1-signal", a, S("p11"), [("s", DNI, 260), ("e", [30.0, 50.0], 2200)],
    [LB("Damage: speed and weight", -0.30, 0.32, a + 0.2, WHITE), LB("Value: a signal", -0.30, 0.24, W("p10", "signal"), YELLOW)],
    tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_UA, HL_RU])
a = S("p11")
tPu11, tSk, tEx = W("p11", "Putin"), W("p11", "Skeptics"), W("p11", "Experts")
reg("c1-range", a, tPu11, [("s", [30.0, 50.0], 8500), ("e", [20.0, 51.0], 10500)],
    [LB("Range: 3,000 to 5,000 km", -0.30, 0.32, a + 0.3, YELLOW)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_BY],
    rings=[ring(LAUNCH, 3000, W("p11", "three"), "3,000 km", AMBER, True), ring(LAUNCH, 5000, W("p11", "five"), "5,000 km", ORANGE, True)],
    cities=[city(LAUNCH, "Belarus (simulated)", a + 0.2, AMBER, "base", 6)])
a = tPu11
reg("c1-mach", a, tSk, [("s", [37.0, 52.0], 2600), ("e", [30.0, 50.0], 1600)],
    [LB("Putin claims Mach 10", -0.30, 0.32, a + 0.2, AMBER)], tag="REAL DATA", source=SRC_O, clock="", highlight=[HL_RU], cities=[city(MOS, "Moscow", a + 0.4, AMBER)])
a = tSk
reg("c1-skeptic", a, tEx, [("s", [30.0, 50.0], 1600), ("e", [25.0, 51.0], 2600)],
    [LB("Skeptics: any long-range missile", -0.30, 0.32, a + 0.2, WHITE), LB("hits Mach 10 in its fall", -0.30, 0.24, W("p11", "final"), YELLOW)],
    tag="REAL DATA", source=SRC_O, clock="")
a = tEx
reg("c1-experts", a, S("p12"), [("s", [25.0, 51.0], 2600), ("e", [20.0, 52.0], 1800)],
    [LB("Experts: path is predictable", -0.30, 0.32, a + 0.2, WHITE), LB("Less a superweapon than claimed", -0.30, 0.24, W("p11", "less"), YELLOW)],
    tag="REAL DATA", source="Euronews; AP", clock="")
a = S("p12")
tDec, tSat = W("p12", "Russia", 2), W("p12", "Satellite")
reg("c1-arrive", a, tSat - 4.0, [("s", [28.0, 53.5], 1800), ("e", [29.0, 53.5], 1200)],
    [LB("December 2025: in Belarus", -0.30, 0.32, a + 0.2, YELLOW), LB("On combat duty", -0.30, 0.24, W("p12", "combat"), AMBER)],
    tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY], countryLabels=[cl("BY", "BELARUS", AMBER)], cities=[city(MSK, "Minsk", a + 0.5, AMBER)])
a = tSat - 4.0
reg("c1-notnamed", a, tSat, [("s", [29.0, 53.5], 1200), ("e", [30.5, 53.7], 900)],
    [LB("Base not named by Russia", -0.30, 0.32, a + 0.2, WHITE)], tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY])
a = tSat
tFi = W("p12", "five")
reg("c1-krichev", a, tFi, [("s", [31.0, 53.7], 1000), ("e", LAUNCH, 400)],
    [LB("Satellite analysts", -0.30, 0.32, a + 0.1, WHITE), LB("Former Soviet airfield", -0.30, 0.24, W("p12", "airfield"), YELLOW), LB("Near Krichev", -0.13, -0.05, a + 0.3, WHITE)],
    tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY, HL_RU], countryLabels=[cl("BY", "BELARUS", AMBER), cl("RU", "RUSSIA", AMBER)], cities=[city(LAUNCH, "", a + 0.3, AMBER, "base", 6)])
a = tFi
tPa = W("p12", "patrol")
reg("c1-border", a, tPa, [("s", LAUNCH, 240), ("e", [31.9, 53.7], 170)],
    [LB("5 km from the Russian border", -0.30, 0.32, a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY, HL_RU],
    cities=[city(LAUNCH, "Airfield", a + 0.1, AMBER, "base", 6)])
a = tPa
reg("c1-patrol", a, S("p13"), [("s", [31.5, 53.7], 300), ("e", [30.5, 53.9], 800)],
    [LB("Launchers drive out on patrol", -0.30, 0.32, a + 0.2, AMBER)], tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY],
    ships=[ship([LAUNCH, [31.2, 53.9], [30.7, 53.8]], a + 0.3, a + 4.0, "Launcher", AMBER, 1.8), ship([LAUNCH, [32.0, 53.6], [32.4, 53.9]], a + 0.8, a + 4.4, "Launcher", AMBER, 1.8)])
a = S("p13")
t3, tMi = W("p13", "three"), W("p13", "Minsk")
reg("c1-three", a, tMi, [("s", [30.5, 53.6], 700), ("e", [30.0, 53.7], 1200)],
    [LB("At least three launchers", -0.30, 0.32, t3, AMBER)], tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY],
    cities=[city([31.3, 53.9], "1", t3, AMBER, "base", 5), city(LAUNCH, "2", t3 + 0.4, AMBER, "base", 5), city([32.1, 53.5], "3", t3 + 0.8, AMBER, "base", 5)])
a = tMi
reg("c1-ten", a, S("p14"), [("s", [29.0, 53.7], 1200), ("e", [27.5, 53.9], 1800)],
    [LB("Minsk: up to ten", -0.30, 0.32, a + 0.1, YELLOW), LB("No count of missiles from Moscow", -0.30, 0.24, W("p13", "count"), WHITE)],
    tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY], cities=[city(MSK, "Minsk", a + 0.1, AMBER)])
a = S("p14")
reg("c1-change", a, S("p15"), [("s", [26.0, 53.0], 2200), ("e", [22.0, 52.0], 3600)],
    [LB("What does a base in Belarus change?", -0.28, 0.32, a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_T, clock="", highlight=[HL_BY] + HL_NATO, legend=LEG,
    cities=[city(LAUNCH, "Belarus base", a + 0.3, AMBER, "base", 6)])

# ================================================================== Chapter 02 [REAL HISTORY] the last time Europe had minutes
a = chapter("c2-card", S("p15"), 3.5, "CHAPTER 02", "The last time Europe had minutes", "REAL HISTORY")
tMa15, tWh = W("p15", "Many"), W("p15", "shortens")
reg("c2-less", a, W("p15", "closer"), [("s", [26.0, 53.5], 3400), ("e", [22.0, 52.5], 4200)],
    [LB("Less than analysts first assume", -0.30, 0.32, a + 0.2, YELLOW)], tag="REAL HISTORY", source=SRC_T, clock="", highlight=[HL_BY, HL_RU] + HL_NATO, legend=LEG)
a = W("p15", "closer")
reg("c2-closer", a, tWh, [("s", [22.0, 52.5], 4200), ("e", [14.0, 52.0], 4600)],
    [LB("Parts of Russia are already closer", -0.30, 0.34, a + 0.2, WHITE), LB("to London and Paris", -0.30, 0.26, W("p15", "London"), BLUE)],
    tag="REAL HISTORY", source=SRC_T, clock="", highlight=[HL_RU], cities=[city(LON, "London", W("p15", "London"), BLUE), city([2.35, 48.86], "Paris", W("p15", "Paris"), BLUE)])
a = tWh
reg("c2-shorter", a, S("p16"), [("s", [22.0, 52.5], 2600), ("e", [20.0, 52.5], 1900)],
    [LB("What it shortens", -0.30, 0.32, a + 0.2, YELLOW)], tag="REAL HISTORY", source=SRC_T, clock="", highlight=[HL_BY] + HL_NATO,
    cities=[city(VIL, "Lithuania", W("p15", "Lithuania"), BLUE), city(WAR, "Poland", W("p15", "Poland"), BLUE), city(BER, "Germany", W("p15", "Germany"), BLUE)],
    lines=[line(LAUNCH, VIL, a + 0.5, a + 2.5, AMBER, True), line(LAUNCH, WAR, a + 1.0, a + 3.0, AMBER, True)])
a = S("p16")
tIn16, tBr16, tCi = W("p16", "A"), W("p16", "British"), W("p16", "CIA")
reg("c2-1983", a, tBr16, [("s", [9.5, 50.5], 1400), ("e", [9.0, 50.0], 900)],
    [LB("Late November 1983", -0.30, 0.32, a + 0.5, YELLOW), LB("Pershing II to West Germany", -0.30, 0.24, W("p16", "Pershing"), BLUE)],
    tag="REAL HISTORY", source=SRC_H, clock="NOV 1983", clockLabel="WEST GERMANY", clockRate=0, highlight=[HL_DE], cities=[city([8.24, 50.08], "Wiesbaden area", a + 3.0, BLUE, "base", 5)])
a = tBr16
tCi2 = tCi
add(id="c2-14", type="bars", start=a, end=round(a + 4.5, 2), tag="REAL HISTORY", title="Pershing II flight time, maximum range", sub="UK parliamentary answer, 1983", source=SRC_H,
    bars=[{"label": "Pershing II", "value": 14, "display": "about 14 min", "color": BLUE}])
a = round(tBr16 + 4.5, 2)
reg("c2-14b", a, tCi, [("s", [9.0, 50.0], 900), ("e", [14.0, 51.0], 2000)],
    [LB("14 minutes at maximum range", -0.30, 0.32, a + 0.2, BLUE)], tag="REAL HISTORY", source=SRC_H, clock="NOV 1983", clockLabel="WEST GERMANY", clockRate=0, highlight=[HL_DE])
a = tCi
reg("c2-cia", a, S("p17"), [("s", [14.0, 52.0], 3200), ("e", [20.0, 53.0], 4400)],
    [LB("CIA: first radar to impact", -0.30, 0.32, a + 0.2, WHITE), LB("8 to 10 minutes", -0.30, 0.24, W("p16", "eight"), YELLOW)],
    tag="REAL HISTORY", source=SRC_H, clock="NOV 1983", clockLabel="CIA ESTIMATE", clockRate=0, highlight=[HL_DE])
a = S("p17")
tDe17 = W("p17", "decapitation")
reg("c2-fear", a, tDe17, [("s", [30.0, 53.0], 3600), ("e", [25.0, 52.5], 3200)],
    [LB("Soviet fear", -0.30, 0.32, a + 0.2, AMBER)], tag="REAL HISTORY", source=SRC_H, clock="", highlight=[HL_RU, HL_DE], cities=[city(MOS, "Moscow", a + 0.3, AMBER)],
    lines=[line([9.0, 50.0], MOS, a + 0.8, a + 4.0, BLUE, True)])
a = tDe17
reg("c2-decap", a, W("p17", "reversed") - 0.2, [("s", [25.0, 52.5], 3200), ("e", [30.0, 53.0], 4200)],
    [LB("A decapitation strike", -0.30, 0.32, a + 0.1, RED), LB("Almost no warning", -0.30, 0.24, W("p17", "almost"), YELLOW)],
    tag="REAL HISTORY", source=SRC_H, clock="", highlight=[HL_RU, HL_DE])
a = W("p17", "reversed") - 0.2
reg("c2-rev", a, S("p18"), [("s", [18.0, 52.0], 4200), ("e", [20.0, 52.0], 3000)],
    [LB("This simulation: the same question", -0.30, 0.32, a + 0.2, YELLOW), LB("Reversed", -0.30, 0.24, W("p17", "reversed"), WHITE)],
    tag="REAL HISTORY", source=SRC_H, clock="", highlight=[HL_BY, HL_DE], lines=[line(LAUNCH, RAM, a + 0.4, a + 3.0, RED, True)])
a = S("p18")
stamp("c2-inf", a, a + 2.6, "DECEMBER 1987", "The INF Treaty", WHITE, tag="REAL HISTORY", source="INF Treaty text")
a = a + 2.6
tBa = W("p18", "banned")
reg("c2-ban", a, W("p18", "By"), [("s", [20.0, 52.0], 7000), ("e", [30.0, 53.0], 5500)],
    [LB("Banned: ground-launched missiles", -0.30, 0.34, W("p18", "ground-launched"), YELLOW), LB("500 to 5,500 km", -0.30, 0.26, W("p18", "five"), WHITE)],
    tag="REAL HISTORY", source="INF Treaty text", clock="", highlight=[HL_RU, HL_US])
a = W("p18", "By")
num("c2-2692", a, round(a + 3.8, 2), "2,692", countTo=2692, label="missiles destroyed by 1991", sub="Intermediate-Range Nuclear Forces Treaty", color=YELLOW, tag="REAL HISTORY", source="INF Treaty text")
a = round(a + 3.8, 2)
reg("c2-ours", a, S("p19"), [("s", [24.0, 53.0], 4000), ("e", [22.0, 52.0], 2800)],
    [LB("Nuclear or conventional", -0.30, 0.32, a + 0.2, WHITE)], tag="REAL HISTORY", source="INF Treaty text", clock="", highlight=[HL_BY] + HL_NATO)
a = S("p19")
stamp("c2-2019", a, a + 2.4, "AUGUST 2019", "The United States leaves the treaty; Russia follows", WHITE, tag="REAL HISTORY", source="Arms Control Association")
a = a + 2.4
tAu = W("p19", "dropped")
reg("c2-gone", a, tAu, [("s", [30.0, 52.0], 7000), ("e", [20.0, 52.0], 4800)],
    [LB("That ban is gone", -0.30, 0.34, a + 0.2, RED)], tag="REAL HISTORY", source="Arms Control Association", clock="", highlight=[HL_RU, HL_US])
a = tAu
stamp("c2-2025", a, a + 2.4, "AUGUST 2025", "Russia drops its own moratorium", AMBER, tag="REAL HISTORY", source="Arms Control Association")
a = a + 2.4
tFe = W("p19", "fifth")
reg("c2-six", a, tFe, [("s", [40.0, 52.0], 6000), ("e", [28.0, 52.0], 4000)],
    [LB("Six months later", -0.30, 0.34, a + 0.2, YELLOW)], tag="REAL HISTORY", source="Arms Control Association", clock="", highlight=[HL_RU])
a = tFe
stamp("c2-start", a, S("p20"), "5 FEBRUARY 2026", "New START expires", RED, tag="REAL HISTORY", source="Arms Control Association")
a = S("p20")
tJa20 = W("p20", "Analysts")
reg("c2-notreaty", a, tJa20, [("s", [20.0, 52.0], 6500), ("e", [26.0, 52.0], 5000)],
    [LB("No limits on strategic forces", -0.30, 0.34, a + 0.2, WHITE), LB("For the first time in decades", -0.30, 0.26, W("p20", "decades"), YELLOW)],
    tag="REAL HISTORY", source=SRC_T, clock="", highlight=[HL_RU, HL_US])
a = tJa20
tBe = W("p20", "Belarus")
reg("c2-jam", a, S("p21") - 0.0, [("s", [28.0, 53.5], 2200), ("e", [27.0, 53.5], 1400)],
    [LB("Jamestown Foundation", -0.30, 0.34, a + 0.2, WHITE), LB("Belarus: not a party to the notice deal", -0.30, 0.26, tBe, YELLOW), LB("A launch from there: no treaty notice", -0.30, 0.18, W("p20", "launch"), RED)],
    tag="REAL HISTORY", source=SRC_T, clock="", highlight=[HL_BY], countryLabels=[cl("BY", "BELARUS", AMBER)])
a = S("p21")
FL("c2-ask", a, S("p22"), [("s", [24.0, 52.5], 3600), ("e", [18.0, 52.0], 2800)], RAM, a + 2.0, S("p22") - 0.4, 8.2, "IF IT LEFT THAT FOREST", "Oreshnik",
   labs=[LB("If it left that forest", -0.30, 0.34, a + 0.2, WHITE), LB("How fast would it arrive?", -0.30, 0.26, W("p21", "fast"), YELLOW)], highlight=[HL_BY, HL_DE] + HL_NATO, tag="REAL HISTORY", source=SRC_T)

# ================================================================== Chapter 03 [SIMULATION] the launch
a = chapter("c3-card", S("p22"), 3.5, "CHAPTER 03", "The launch", "SIMULATION")
tDay, tMo = W("p22", "day"), W("p22", "Moscow")
reg("c3-crisis", a, tDay, [("s", [20.0, 57.0], 1800), ("e", [21.0, 56.0], 1400)],
    [LB("Day 8 of a crisis over the Baltic", -0.30, 0.34, a + 0.2, YELLOW)], clock="DAY 8", clockLabel="THE CRISIS", clockRate=0, highlight=[HL_RU, HL_BY] + HL_NATO, legend=LEG,
    cities=[city([21.0, 55.7], "Baltic", a + 0.4, WHITE)])
a = tDay
reg("c3-day9", a, tMo, [("s", [27.0, 54.0], 2400), ("e", [24.0, 53.0], 2000)],
    [LB("Day 9: 03:10 Berlin time", -0.30, 0.34, a + 0.2, YELLOW), LB("We do not model how it began", -0.30, 0.26, W("p22", "model"), WHITE)],
    **BC(), highlight=[HL_RU, HL_BY] + HL_NATO, legend=LEG)
a = tMo
reg("c3-moscow", a, S("p23"), [("s", [34.0, 54.5], 1200), ("e", [30.0, 54.0], 1500)],
    [LB("Moscow fires one missile", -0.30, 0.34, a + 0.2, RED)], **BC(), highlight=[HL_RU, HL_BY], cities=[city(MOS, "Moscow", a + 0.1, AMBER), city(LAUNCH, "Launch (simulated)", a + 1.4, AMBER, "base", 6)],
    lines=[line(MOS, LAUNCH, a + 0.8, a + 3.0, AMBER, True)])
a = S("p23")
tRa, tPu23 = W("p23", "rear"), W("p23", "purpose")
reg("c3-target", a, tPu23, [("s", [10.0, 50.0], 1300), ("e", RAM, 380)],
    [LB("Our target: Ramstein Air Base", -0.30, 0.34, a + 0.4, RED), LB("A rear area, far from the front", -0.30, 0.26, tRa, WHITE)],
    **BC(), highlight=[HL_DE], cities=[city(RAM, "Ramstein Air Base", a + 0.4, RED, "target", 6)])
a = tPu23
reg("c3-purpose", a, W("p23", "These") - 0.1, [("s", RAM, 380), ("e", [10.0, 51.0], 2000)],
    [LB("A nuclear demonstration", -0.30, 0.34, W("p23", "nuclear"), RED), LB("To show the rear can be reached", -0.30, 0.26, W("p23", "reached"), YELLOW)],
    **BC(), highlight=[HL_DE], cities=[city(RAM, "Ramstein", a + 0.1, RED, "target", 6)])
a = W("p23", "These") - 0.1
reg("c3-ours", a, S("p24"), [("s", [14.0, 51.5], 3000), ("e", [20.0, 52.0], 3800)],
    [LB("Our choices", -0.30, 0.34, a + 0.1, YELLOW), LB("Not a forecast. Not a known plan.", -0.30, 0.26, W("p23", "forecast"), WHITE)],
    **BC(), highlight=[HL_DE] + HL_NATO, caption="Our choices, not a forecast and not a known Russian plan.")
a = S("p24")
tLs = W("p24", "placed")
reg("c3-site", a, tLs + 2.0, [("s", [30.0, 53.7], 1000), ("e", LAUNCH, 320)],
    [LB("A point we placed", -0.30, 0.34, tLs, YELLOW), LB("Near the reported base", -0.30, 0.26, W("p24", "reported"), WHITE)],
    **BC(), highlight=[HL_BY], cities=[city(LAUNCH, "Launch site (simulated)", a + 0.3, AMBER, "base", 6)])
a = tLs + 2.0
reg("c3-simloc", a, S("p25"), [("s", LAUNCH, 320), ("e", [30.0, 53.8], 900)],
    [LB("Its location is simulated", -0.30, 0.34, a + 0.2, YELLOW)], **BC(), highlight=[HL_BY], cities=[city(LAUNCH, "Launch site (simulated)", a + 0.1, AMBER, "base", 6)])
a = S("p25")
tAn, tSu = W("p25", "Analysts"), W("p25", "subordinate")
reg("c3-authority", a, tAn, [("s", [33.0, 54.5], 1500), ("e", [36.0, 55.0], 1000)],
    [LB("Launch authority stays in Moscow", -0.30, 0.34, a + 0.3, AMBER)], **BC(), highlight=[HL_RU, HL_BY], cities=[city(MOS, "Moscow", a + 0.2, AMBER)],
    lines=[line(MOS, LAUNCH, a + 1.5, a + 3.5, AMBER, True)])
a = tAn
reg("c3-sub", a, S("p26"), [("s", [34.0, 54.5], 1600), ("e", [30.0, 54.0], 1000)],
    [LB("Jamestown: fully subordinate", -0.30, 0.34, a + 0.2, WHITE), LB("To Strategic Missile Forces", -0.30, 0.26, W("p25", "Strategic"), AMBER)],
    **BC(), highlight=[HL_RU, HL_BY], cities=[city(MOS, "Moscow", a + 0.1, AMBER), city(LAUNCH, "Launcher", a + 0.4, AMBER, "base", 6)])
a = S("p26")
tFi26, tIn26 = W("p26", "fifty"), W("p26", "inside")
reg("c3-one", a, tFi26, [("s", RAM, 500), ("e", RAM, 300)],
    [LB("One warhead", -0.30, 0.34, W("p26", "one"), RED)], **BC(), highlight=[HL_DE], cities=[city(RAM, "Ramstein", a + 0.2, RED, "target", 6)])
a = tFi26
num("c3-50", a, round(a + 3.6, 2), "50 KT", countTo=50, suffix=" KT", label="our chosen yield", sub="no yield has ever been published for Oreshnik", color=RED, source="Scenario engine; choice, not a fact")
a = round(a + 3.6, 2)
reg("c3-scale", a, S("p27"), [("s", [9.0, 50.0], 1200), ("e", [9.0, 50.0], 700)],
    [LB("Pershing II warhead: 5 to 80 kt", -0.30, 0.34, a + 0.2, BLUE), LB("Used only as a scale", -0.30, 0.26, W("p26", "scale"), WHITE)],
    **BC(), highlight=[HL_DE], tag="SIMULATION", cities=[city([8.24, 50.08], "Pershing II, 1983", a + 0.3, BLUE, "base", 5)])
a = S("p27")
tAP, tNW = W("p27", "Associated"), W("p27", "no")
reg("c3-radar", a, tAP, [("s", [20.0, 52.5], 2800), ("e", [16.0, 52.0], 2200)],
    [LB("The same on every radar", -0.30, 0.34, a + 0.2, YELLOW)], clock="T+01:00", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_BY] + HL_NATO,
    ships=[ship([[28.0, 53.5], [14.0, 51.0]], a + 0.2, a + 8, "", RED, 2.4)], lines=[line(LAUNCH, RAM, a + 0.1, a + 6, RED, True)])
a = tAP
reg("c3-ap", a, S("p28"), [("s", [14.0, 51.5], 2200), ("e", [10.0, 50.5], 1400)],
    [LB("Nuclear or conventional?", -0.30, 0.34, tNW, WHITE), LB("No way to tell before impact", -0.30, 0.26, W("p27", "impact"), YELLOW)],
    clock="T+02:00", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_DE], source="AP", cities=[city(RAM, "Ramstein", a + 0.2, BLUE, "base", 6)])
a = S("p28")
reg("c3-clock", a, S("p29"), [("s", [26.0, 53.5], 1800), ("e", [30.0, 53.7], 1000)],
    [LB("The clock starts", -0.30, 0.34, a + 0.2, YELLOW), LB("Without an answer", -0.30, 0.26, W("p28", "without"), WHITE)],
    clock="T+00:00", clockLabel="THE CLOCK STARTS", clockRate=0, highlight=[HL_BY] + HL_NATO, cities=[city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])

# ================================================================== Chapter 04 [SIMULATION] minute by minute
a = chapter("c4-card", S("p29"), 3.5, "CHAPTER 04", "Minute by minute", "SIMULATION")
tTi = W("p29", "times")
FL("c4-zero", a, tTi, [("s", [28.0, 53.7], 500), ("e", [26.0, 53.7], 700)], VIL, a + 0.5, tTi - 0.3, 6.0, "MINUTE ZERO", "Launch",
   labs=[LB("Minute zero: launch", -0.30, 0.34, a + 0.2, RED)], highlight=[HL_BY], cities=[city(LAUNCH, "Launch (simulated)", a + 0.2, AMBER, "base", 6)])
a = tTi
tVi = S("p30")
reg("c4-model", a, S("p30"), [("s", [28.0, 53.5], 1500), ("e", [22.0, 53.0], 2500)],
    [LB("Times from our scenario engine", -0.30, 0.34, a + 0.1, YELLOW), LB("A ballistic path, not a glide", -0.30, 0.26, W("p29", "ballistic"), WHITE)],
    clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_BY] + HL_NATO)
a = S("p30")
tWa = W("p30", "Warsaw")
FL("c4-vilnius", a, tWa, [("s", [28.0, 54.0], 1000), ("e", [27.0, 54.2], 800)], VIL, a + 0.2, a + 3.6, 6.0, "FLIGHT TIME", "Oreshnik",
   labs=[LB("Vilnius: 433 km", -0.30, 0.34, a + 0.3, BLUE), LB("About 6 minutes", -0.30, 0.26, W("p30", "six"), YELLOW)], highlight=[HL_BY, hl("LT", BLUE)],
   cities=[city(VIL, "Vilnius", a + 0.2, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = tWa
tFl = W("p30", "floor")
FL("c4-warsaw", a, tFl, [("s", [26.0, 53.5], 1500), ("e", [24.0, 53.0], 1300)], WAR, a + 0.2, a + 4.0, 6.0, "FLIGHT TIME", "Oreshnik",
   labs=[LB("Warsaw: 735 km", -0.30, 0.34, a + 0.3, BLUE), LB("Still about 6 minutes", -0.30, 0.26, W("p30", "still"), YELLOW)], highlight=[HL_BY, hl("PL", BLUE)],
   cities=[city(WAR, "Warsaw", a + 0.2, BLUE), city(VIL, "Vilnius", a + 0.2, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = tFl
reg("c4-floor", a, S("p31"), [("s", [24.0, 53.0], 1500), ("e", [20.0, 52.5], 2400)],
    [LB("Six is the floor of our model", -0.30, 0.34, a + 0.2, YELLOW)], clock="T+06:00", clockLabel="THE FLOOR", clockRate=0, highlight=[HL_BY] + HL_NATO,
    cities=[city(WAR, "Warsaw", a + 0.1, BLUE), city(VIL, "Vilnius", a + 0.1, BLUE)])
a = S("p31")
tBr31, tLo = W("p31", "Brussels"), W("p31", "London")
FL("c4-berlin", a, tBr31, [("s", [22.0, 53.0], 2400), ("e", [18.0, 52.5], 2600)], BER, a + 0.2, a + 4.5, 6.7, "FLIGHT TIME", "Oreshnik",
   labs=[LB("Berlin: 1,226 km", -0.30, 0.34, a + 0.3, BLUE), LB("About 6.7 minutes", -0.30, 0.26, W("p31", "six"), YELLOW)], highlight=[HL_BY, HL_DE],
   cities=[city(BER, "Berlin", a + 0.2, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = tBr31
FL("c4-brussels", a, tLo, [("s", [16.0, 52.0], 3200), ("e", [12.0, 51.5], 3600)], BRU, a + 0.2, a + 4.5, 8.6, "FLIGHT TIME", "Oreshnik",
   labs=[LB("Brussels", -0.30, 0.34, a + 0.3, BLUE), LB("About 8.6 minutes", -0.30, 0.26, a + 0.8, YELLOW)], highlight=[HL_BY, hl("BE", BLUE)],
   cities=[city(BRU, "Brussels", a + 0.2, BLUE), city(BER, "Berlin", a + 0.2, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = tLo
FL("c4-london", a, S("p32"), [("s", [14.0, 52.0], 3800), ("e", [10.0, 52.0], 4600)], LON, a + 0.2, a + 5.0, 9.4, "FLIGHT TIME", "Oreshnik",
   labs=[LB("London: 2,146 km", -0.30, 0.34, a + 0.3, BLUE), LB("About 9.4 minutes", -0.30, 0.26, W("p31", "nine"), YELLOW)], highlight=[HL_BY, hl("GB", BLUE)],
   cities=[city(LON, "London", a + 0.2, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = S("p32")
tBe32 = W("p32", "between")
FL("c4-ramstein", a, tBe32 + 1.5, [("s", [16.0, 52.0], 3600), ("e", [14.0, 51.0], 3000)], RAM, a + 0.2, a + 6.0, 8.2, "FLIGHT TIME", "Oreshnik",
   labs=[LB("Ramstein: 1,724 km", -0.30, 0.34, a + 0.3, RED), LB("Between Berlin and Brussels", -0.30, 0.26, tBe32, WHITE)], highlight=[HL_BY, HL_DE],
   cities=[city(RAM, "Ramstein", a + 0.2, RED, "target", 6), city(BER, "Berlin", a + 0.5, BLUE), city(BRU, "Brussels", a + 0.8, BLUE), city(LAUNCH, "Launch", a + 0.2, AMBER, "base", 6)])
a = tBe32 + 1.5
reg("c4-min8", a, S("p33"), [("s", [14.0, 51.0], 3000), ("e", [10.0, 50.5], 1500)],
    [LB("Minute eight, and a little more", -0.30, 0.34, a + 0.2, YELLOW)], clock="T+08:12", clockLabel="IMPACT", clockRate=0, highlight=[HL_DE],
    cities=[city(RAM, "Ramstein", a + 0.1, RED, "target", 6)])
a = S("p33")
tMo33, tDn33 = W("p33", "These"), W("p33", "Dnipro")
reg("c4-outputs", a, tDn33, [("s", [28.0, 52.5], 3000), ("e", [24.0, 52.0], 2400)],
    [LB("Model outputs", -0.30, 0.34, a + 0.2, YELLOW), LB("The real path is unpublished", -0.30, 0.26, W("p33", "path"), WHITE)],
    clock="T+00:00", clockLabel="OUR MODEL", clockRate=0, highlight=[HL_BY] + HL_NATO)
a = tDn33
reg("c4-dnipro", a, a + 4.0, [("s", [40.0, 49.0], 1500), ("e", [38.0, 48.8], 1100)],
    [LB("Dnipro: about 15 minutes", -0.30, 0.34, a + 0.3, TEAL), LB("About 800 km, measured", -0.30, 0.26, a + 2.0, WHITE)],
    clock="T+00:00", clockLabel="DNIPRO 2024", clockRate=225, source=SRC_O, highlight=[HL_UA], cities=[city(KY, "Kapustin Yar", a + 0.2, AMBER, "base", 6), city(DNI, "Dnipro", a + 0.2, TEAL)],
    ships=[ship([KY, DNI], a + 0.3, a + 3.9, "Real flight", TEAL, 2.4)], lines=[line(KY, DNI, a + 0.3, a + 3.9, TEAL, True)])
a = a + 4.0
add(id="c4-vs", type="bars", start=a, end=round(a + 4.2, 2), tag="SIMULATION", title="About 800 km: measured and modelled", sub="minutes of flight", source="Dnipro: published reports; model: scenario engine",
    bars=[{"label": "Dnipro, 2024 (measured)", "value": 15, "display": "about 15", "color": TEAL}, {"label": "Our model, same distance", "value": 6, "display": "about 6", "color": RED}])
a = round(a + 4.2, 2)
reg("c4-lofted", a, S("p34"), [("s", [28.0, 52.5], 2600), ("e", [20.0, 52.0], 3400)],
    [LB("A lofted path takes longer", -0.30, 0.34, W("p33", "lofted"), YELLOW)], clock="", highlight=[HL_BY] + HL_NATO,
    lines=[line(LAUNCH, RAM, a + 0.3, a + 2.5, RED, True), line(LAUNCH, RAM, a + 0.3, a + 2.5, ORANGE, True)])
a = S("p34")
tPo34, tBr34 = W("p34", "Poland"), W("p34", "Brussels")
reg("c4-claims", a, tPo34 + 2.0, [("s", [24.0, 52.5], 3200), ("e", [18.0, 52.5], 3800)],
    [LB("Russian state media claims", -0.30, 0.34, a + 0.2, AMBER), LB("11 minutes to an air base in Poland", -0.30, 0.26, W("p34", "eleven"), YELLOW)],
    clock="", highlight=[HL_BY] + HL_NATO, cities=[city([22.0, 51.0], "Air base, Poland", W("p34", "eleven"), BLUE, "base", 5)],
    lines=[line(LAUNCH, [22.0, 51.0], W("p34", "eleven"), W("p34", "eleven") + 2.0, AMBER, True)])
a = tPo34 + 2.0
reg("c4-claims2", a, S("p35"), [("s", [14.0, 51.5], 3800), ("e", [10.0, 51.0], 3200)],
    [LB("17 minutes to NATO headquarters", -0.30, 0.34, W("p34", "seventeen"), YELLOW), LB("Claims, not measurements", -0.30, 0.26, W("p34", "Those"), WHITE)],
    clock="", highlight=[HL_BY, hl("BE", BLUE)], cities=[city(BRU, "Brussels", a + 0.3, BLUE)], lines=[line(LAUNCH, BRU, a + 0.2, a + 2.4, AMBER, True)])
a = S("p35")
reg("c4-do", a, S("p36"), [("s", [18.0, 52.0], 3800), ("e", [12.0, 51.0], 2800)],
    [LB("What can anyone do", -0.30, 0.34, a + 0.2, WHITE), LB("with six to nine minutes?", -0.30, 0.26, W("p35", "six"), YELLOW)],
    clock="T+06:00", clockLabel="SIX TO NINE", clockRate=15, highlight=[HL_BY, HL_DE] + HL_NATO)
a = S("p36")
tAm = W("p36", "American-built")
reg("c4-warn", a, tAm - 0.0, [("s", [16.0, 52.0], 3000), ("e", [13.0, 51.0], 2400)],
    [LB("Does a warning reach anyone?", -0.30, 0.34, a + 0.3, YELLOW), LB("A leader, a commander, a shelter", -0.30, 0.26, W("p36", "commander"), WHITE)],
    clock="", highlight=[HL_DE] + HL_NATO)
a = tAm
tDe36 = W("p36", "Deveselu")
reg("c4-redz", a, tDe36, [("s", [19.0, 54.0], 1500), ("e", REDZ, 900)],
    [LB("American-built missile defence", -0.30, 0.34, a + 0.2, BLUE)], clock="", highlight=[hl("PL", BLUE)], cities=[city(REDZ, "Redzikowo, Poland", W("p36", "Redzikowo"), BLUE, "base", 6)])
a = tDe36
tBu = W("p36", "built")
reg("c4-dev", a, tBu, [("s", [22.0, 47.0], 2400), ("e", DEV, 1200)],
    [LB("Could they engage it?", -0.30, 0.34, a + 0.4, YELLOW), LB("Not publicly established", -0.30, 0.26, W("p36", "publicly"), WHITE)], clock="", highlight=[hl("RO", BLUE)],
    cities=[city(DEV, "Deveselu, Romania", a + 0.2, BLUE, "base", 6)])
a = tBu
reg("c4-limited", a, S("p37"), [("s", [20.0, 49.0], 3600), ("e", [20.0, 52.0], 3000)],
    [LB("Built against a limited threat", -0.30, 0.34, a + 0.2, WHITE), LB("Not a Russian barrage", -0.30, 0.26, W("p36", "barrage"), YELLOW)], clock="", highlight=[hl("PL", BLUE), hl("RO", BLUE)],
    cities=[city(REDZ, "Redzikowo", a + 0.1, BLUE, "base", 6), city(DEV, "Deveselu", a + 0.1, BLUE, "base", 6)])
a = S("p37")
reg("c4-min8b", a, S("p38"), [("s", [12.0, 50.5], 2000), ("e", RAM, 700)],
    [LB("What happens at minute eight", -0.30, 0.34, a + 0.2, YELLOW)], clock="T+07:50", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_DE],
    cities=[city(RAM, "Ramstein", a + 0.1, RED, "target", 6)])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = chapter("c5-card", S("p38"), 3.5, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
tBu38 = W("p38", "bursts")
reg("c5-approach", a, tBu38, [("s", [14.0, 51.0], 1200), ("e", RAM, 320)],
    [LB("Minute eight point two", -0.30, 0.34, a + 0.1, YELLOW)], clock="T+08:00", clockLabel="AFTER LAUNCH", clockRate=1, highlight=[HL_DE],
    ships=[ship([[14.0, 51.0], RAM], a, tBu38, "", RED, 2.4)], cities=[city(RAM, "Ramstein Air Base", a + 0.2, RED, "target", 6)])
a = tBu38
FB, P20, P5, TH, P1 = FX["fireball_km"], FX["psi20_km"], FX["psi5_km"], FX["thermal3_km"], FX["psi1_km"]
CK = dict(clock="T+08:12", clockLabel="IMPACT", clockRate=1)
cty("c5-flash", a, S("p39"), [("s", RAM, 8.0), ("e", RAM, 5.0)],
    [ring(RAM, FB, a + 1.2, "", WHITE)], [LB("50 kt airburst over the base", -0.30, 0.34, a + 0.4, RED)], flashT=0.1, **CK)
a = S("p39")
cty("c5-fire", a, S("p40"), [("s", RAM, 4.0), ("e", RAM, 3.0)],
    [ring(RAM, FB, a + 0.3, "Fireball", WHITE)], [LB("Fireball radius: 290 m", -0.30, 0.34, W("p39", "radius"), YELLOW)], **CK)
a = S("p40")
cty("c5-20", a, S("p41"), [("s", RAM, 5.0), ("e", RAM, 3.5)],
    [ring(RAM, FB, a + 0.05, "", WHITE), ring(RAM, P20, a + 0.4, "20 psi", RED)], [LB("Most severe blast damage", -0.30, 0.34, W("p40", "severe"), YELLOW)], **CK)
a = S("p41")
tAb = W("p41", "ordinary")
cty("c5-5", a, tAb, [("s", RAM, 10.0), ("e", RAM, 7.0)],
    [ring(RAM, FB, a + 0.05, "", WHITE), ring(RAM, P20, a + 0.05, "", RED), ring(RAM, P5, a + 0.5, "5 psi", RED)],
    [LB("Heavy damage to ordinary buildings", -0.30, 0.34, W("p41", "heavy"), YELLOW)], **CK)
a = tAb
cty("c5-5b", a, S("p42"), [("s", RAM, 7.0), ("e", RAM, 9.0)],
    [ring(RAM, FB, a, "", WHITE), ring(RAM, P20, a, "", RED), ring(RAM, P5, a, "", RED)],
    [LB("About 20 square km", -0.30, 0.34, W("p41", "twenty"), YELLOW)], **CK)
a = S("p42")
cty("c5-burn", a, S("p43"), [("s", RAM, 11.0), ("e", RAM, 13.0)],
    [ring(RAM, P5, a, "", RED), ring(RAM, TH, a + 0.4, "Burns", ORANGE)], [LB("Third-degree burns", -0.30, 0.34, W("p42", "three"), ORANGE), LB("From the flash alone", -0.30, 0.26, W("p42", "flash"), WHITE)], **CK)
a = S("p43")
tWi = W("p43", "Windows")
cty("c5-win", a, S("p44"), [("s", RAM, 18.0), ("e", RAM, 22.0)],
    [ring(RAM, P5, a, "", RED), ring(RAM, TH, a, "", ORANGE), ring(RAM, P1, a + 0.4, "1 psi", WHITE)], [LB("Windows break", -0.30, 0.34, tWi, YELLOW)], **CK)
a = S("p44")
tNo44 = W("p44", "We")
cty("c5-towns", a, tNo44, [("s", RAM, 30.0), ("e", RAM, 34.0)],
    [ring(RAM, P5, a, "", RED), ring(RAM, TH, a, "", ORANGE), ring(RAM, P1, a, "", WHITE)], [LB("Base and towns inside the rings", -0.30, 0.40, a + 0.3, WHITE)], **CK)
a = tNo44
cty("c5-nocas", a, S("p45"), [("s", RAM, 34.0), ("e", RAM, 40.0)],
    [ring(RAM, P1, a, "", WHITE), ring(RAM, TH, a, "", ORANGE)], [LB("No casualty figure", -0.30, 0.34, a + 0.2, YELLOW), LB("No published study models this strike", -0.30, 0.26, W("p44", "published"), WHITE)], **CK)

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p45"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
reg("c6-question", a, S("p46"), [("s", [14.0, 51.0], 3800), ("e", [20.0, 52.0], 3000)],
    [LB("The rings are the visible damage", -0.30, 0.34, a + 0.1, WHITE), LB("The question was the minutes", -0.30, 0.26, W("p45", "minutes"), YELLOW)],
    clock="03:18", clockLabel="BERLIN TIME", clockRate=0, highlight=[HL_DE] + HL_NATO,
    ships=[ship([LAUNCH, RAM], a, a + 1.0, "", RED, 2.4)], cities=[city(RAM, "Ramstein", a + 0.2, RED, "target", 6)])
a = S("p46")
tBe46 = W("p46", "because")
cty("c6-rings", a, tBe46, [("s", RAM, 26.0), ("e", RAM, 18.0)],
    [ring(RAM, FB, a, "", WHITE), ring(RAM, P20, a, "", RED), ring(RAM, P5, a, "", RED), ring(RAM, TH, a, "", ORANGE), ring(RAM, P1, a + 0.3, "1 psi", WHITE)],
    [LB("The rings stay marked", -0.30, 0.34, a + 0.3, WHITE)], tag="SIMULATION", clock="DAY AFTER", clockLabel="BERLIN", clockRate=0)
a = tBe46
reg("c6-nofall", a, S("p47"), [("s", RAM, 220), ("e", [10.0, 50.5], 1500)],
    [LB("Air burst: little local fallout", -0.30, 0.34, W("p46", "fallout"), YELLOW), LB("No plume drawn", -0.30, 0.26, W("p46", "plume"), WHITE), LB("We chose no wind", -0.30, 0.18, W("p46", "wind"), WHITE)],
    clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_DE], rings=[ring(RAM, P1, a, "", WHITE), ring(RAM, P5, a, "", RED)], cities=[city(RAM, "Ramstein", a + 0.1, RED, "target", 6)])
a = S("p47")
tVi47, tLo47 = W("p47", "Vilnius"), W("p47", "London")
reg("c6-capitals", a, tVi47 + 1.0, [("s", [16.0, 52.0], 3600), ("e", [20.0, 52.5], 2800)],
    [LB("Across Europe: the same rings", -0.30, 0.34, a + 0.2, WHITE)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY] + HL_NATO,
    cities=[city(VIL, "Vilnius: 6 min", tVi47, BLUE), city(WAR, "Warsaw: 6 min", W("p47", "Warsaw"), BLUE)], rings=[ring(VIL, 60, tVi47, "", BLUE, True), ring(WAR, 60, W("p47", "Warsaw"), "", BLUE, True)])
a = tVi47 + 1.0
reg("c6-london", a, W("p47", "Every") - 0.1, [("s", [10.0, 52.0], 4800), ("e", [4.0, 51.5], 3600)],
    [LB("About 9 minutes for London", -0.30, 0.34, tLo47, YELLOW)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[hl("GB", BLUE)],
    cities=[city(LON, "London: 9 min", tLo47, BLUE)], rings=[ring(LON, 60, tLo47, "", BLUE, True)])
a = W("p47", "Every") - 0.1
reg("c6-knows", a, S("p48"), [("s", [24.0, 53.0], 4200), ("e", LAUNCH, 900)],
    [LB("Every government now knows", -0.30, 0.34, a + 0.2, WHITE), LB("what a launch from that forest means", -0.30, 0.26, W("p47", "forest"), YELLOW)],
    clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY], cities=[city(LAUNCH, "Launch (simulated)", a + 0.4, AMBER, "base", 6)])
a = S("p48")
tTh48 = W("p48", "then")
reg("c6-minutes", a, tTh48, [("s", [12.0, 51.0], 2800), ("e", [10.0, 50.0], 2000)],
    [LB("Minutes to see the missile", -0.30, 0.34, a + 0.3, YELLOW)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_DE] + HL_NATO,
    cities=[city(RAM, "Ramstein", a + 0.2, RED, "target", 6)])
a = tTh48
tOn = W("p48", "only")
reg("c6-days", a, tOn, [("s", [10.0, 50.0], 2000), ("e", [14.0, 51.0], 3200)],
    [LB("Then days to decide", -0.30, 0.34, a + 0.2, WHITE)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_DE] + HL_NATO)
a = tOn
tLv48 = W("p48", "Lviv")
reg("c6-lviv", a, S("p49"), [("s", [14.0, 50.5], 3800), ("e", [24.5, 49.9], 900)],
    [LB("The only reaction on record", -0.30, 0.34, a + 0.2, WHITE), LB("Lviv strike: escalatory", -0.30, 0.26, tLv48, YELLOW), LB("A conventional strike on Ukraine", -0.30, 0.18, W("p48", "conventional"), WHITE)],
    clock="", highlight=[HL_UA, hl("GB", BLUE), hl("FR", BLUE), HL_DE], cities=[city(LVIV, "Lviv", tLv48, TEAL)])
a = S("p49")
tUm, tLu = W("p49", "umbrella"), W("p49", "Lukashenko's")
reg("c6-umbrella", a, tLu, [("s", [28.0, 53.5], 1800), ("e", [27.0, 53.5], 1300)],
    [LB("Belarus: under Russia's umbrella", -0.30, 0.34, a + 0.3, AMBER)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY], countryLabels=[cl("BY", "BELARUS", AMBER)],
    cities=[city(MSK, "Minsk", a + 0.5, AMBER)])
a = tLu
tAf = W("p49", "after")
reg("c6-dozens", a, tAf, [("s", [28.0, 53.5], 1300), ("e", [30.0, 53.7], 1000)],
    [LB("Several dozen tactical weapons", -0.30, 0.34, a + 0.3, YELLOW), LB("By Lukashenko's account", -0.30, 0.26, a + 0.7, WHITE)],
    clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY])
a = tAf
reg("c6-signal", a, S("p50"), [("s", [30.0, 53.7], 1000), ("e", [24.0, 52.5], 3000)],
    [LB("A launch from there", -0.30, 0.34, a + 0.2, WHITE), LB("reads as nuclear first", -0.30, 0.26, W("p49", "nuclear", 2), RED), LB("Conventional, only afterward", -0.30, 0.18, W("p49", "conventional"), YELLOW)],
    clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY] + HL_NATO, cities=[city(LAUNCH, "Launch (simulated)", a + 0.3, AMBER, "base", 6)])
a = S("p50")
tNi = W("p50", "No")
reg("c6-web", a, W("p50", "Treaty"), [("s", [20.0, 52.0], 4500), ("e", [26.0, 53.0], 3200)],
    [LB("The web for a warning is thin", -0.30, 0.34, a + 0.2, YELLOW)], clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY, HL_DE] + HL_NATO)
a = W("p50", "Treaty")
reg("c6-notreaty", a, S("p51"), [("s", [26.0, 53.0], 3200), ("e", [20.0, 52.0], 3800)],
    [LB("No INF Treaty. No New START.", -0.30, 0.34, a + 0.1, WHITE), LB("No launch notice from Belarus", -0.30, 0.26, W("p50", "notice"), RED)],
    clock="DAY AFTER", clockLabel="BERLIN", clockRate=0, highlight=[HL_BY] + HL_NATO)
a = S("p51")
tMi51 = W("p51", "minutes")
reg("c6-final", a, S("p52"), [("s", [22.0, 52.5], 3200), ("e", [14.0, 52.0], 4400)],
    [LB("Distances from a simulated launch point", -0.30, 0.34, a + 0.2, YELLOW), LB("The minutes are only a model", -0.30, 0.26, tMi51, WHITE)],
    clock="", highlight=[HL_BY, HL_DE] + HL_NATO,
    cities=[city(VIL, "Vilnius 6.0", a + 0.5, BLUE), city(WAR, "Warsaw 6.0", a + 0.9, BLUE), city(BER, "Berlin 6.7", a + 1.3, BLUE), city(RAM, "Ramstein 8.2", a + 1.7, RED, "target", 6), city(BRU, "Brussels 8.6", a + 2.1, BLUE), city(LAUNCH, "Launch (simulated)", a + 0.2, AMBER, "base", 6)],
    lines=[line(LAUNCH, p, a + 0.5 + i * 0.4, a + 2.5 + i * 0.4, AMBER, True) for i, p in enumerate([VIL, WAR, BER, RAM, BRU])])

# ================================================================== End slate
add(id="endslate", type="endslate", start=S("p52"), end=END, tag="", title="The nuclear bombs America lost", line="Next on the map: the nuclear weapons America lost and never found.")

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
        if s["type"] != "region" or s["id"].startswith("c5-"):
            continue   # c5 shots are tight views over open sea on purpose (no land to draw, like episode 007)
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




LISTS = ("cities", "labels", "zones", "lines", "ships", "rings", "markers")


def _shift(items, d):
    out = []
    for it in items:
        it = dict(it)
        for k in ("t", "t0", "t1", "until"):
            if isinstance(it.get(k), (int, float)):
                it[k] = round(it[k] + d, 2)
        out.append(it)
    return out


def mergeable(A, B):
    if A["type"] != "region" or B["type"] != "region" or A["id"].startswith("open-") or B["id"].startswith("open-"):
        return False
    if A.get("tag") != B.get("tag") or A.get("source") != B.get("source"):
        return False
    if A.get("clockRate", 0) != B.get("clockRate", 0) or (A.get("lines") and not B.get("lines")):
        return False
    limit = 7.9 if B["end"] <= 90 else 10.0
    return B["end"] - A["start"] <= limit


def merge_pass():
    out = []
    for s in shots:
        if out and mergeable(out[-1], s):
            A = out[-1]
            dA = round(A["end"] - A["start"], 2)
            for lst in ("labels",):
                for it in A.get(lst, []):
                    if "until" not in it:
                        it["until"] = round(dA + 0.2, 2)
            for k in LISTS:
                if s.get(k):
                    A[k] = A.get(k, []) + _shift(s[k], dA)
            for k in ("highlight", "countryLabels", "legend"):
                if s.get(k):
                    A[k] = A.get(k, []) + [x for x in s[k] if x not in A.get(k, [])]
            bk = [dict(x) for x in s["camera"]]
            bk[0]["t"] = 0
            for x in bk:
                x["t"] = round(x["t"] + dA + (min(1.5, (s["end"] - s["start"]) * 0.3) if x is bk[0] else 0), 2)
            A["camera"] = A["camera"] + bk
            if A.get("clock") != s.get("clock") and not A.get("clockRate", 0):
                A["clock"] = ""
                A.pop("clockLabel", None)
            A["end"] = s["end"]
            A["id"] = A["id"] + "+" + s["id"].split("-", 1)[-1]
        else:
            out.append(s)
    shots[:] = out


merge_pass()
for _s in shots:
    if _s["type"] == "region":
        _s["view"] = {"center": _s["camera"][0]["center"], "widthKm": _s["camera"][0]["widthKm"]}


def late():
    for s in shots:
        d = s["end"] - s["start"]
        for k in ("cities", "labels", "lines", "ships", "rings"):
            for it in s.get(k, []):
                t = it.get("t", it.get("t0"))
                if isinstance(t, (int, float)) and t > d - 0.8:
                    print("LATE", s["id"], k, it.get("label") or it.get("text"), t, round(d, 1))


for _s in shots:
    if _s["id"] == "endslate":
        _s["transition"] = "dip"
floors()
densify()
floors()
densify()
check_keys()
late()

# ------------------------------------------------------------------ audio plan and output
b0 = round(min(FLASH + 0.1 - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p06") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p22") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p22") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": FLASH + 0.1, "gain_db": -6}]
                    + [{"src": "boom.mp3", "t": s["start"] + s["flashT"], "gain_db": -6} for s in shots if isinstance(s.get("flashT"), (int, float))],
           "attribution": "Maps: Natural Earth (public domain); OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles. Narration: AI-generated.",
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
