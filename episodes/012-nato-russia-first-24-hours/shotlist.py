"""Director pass for episode 012: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 012-nato-russia-first-24-hours
Payoff first (a conventional Iskander hit on Malbork under the banner), a real-data note and real history, then nine
strikes over 24 simulated hours on region maps with ticking flight clocks, one 10 kt airburst over open sea shown ring
by ring (tight region views with disc zones: there is no land to draw, like episode 007), and the day after.
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

HERO = next(s for s in sc["strikes"] if s["id"] == "isk-warning-baltic")
FX = HERO["effects"]
GZ = [HERO["target_lon"], HERO["target_lat"]]       # the burst point over open Baltic water (simulated)
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


# ------------------------------------------------------------------ places
ST = {s["id"]: s for s in sc["strikes"]}
def P(i, which="target"):
    return [ST[i][which + "_lon"], ST[i][which + "_lat"]]
KAL, MAL, ADZ, LIE = P("isk-malbork", "launch"), P("isk-malbork"), P("isk-adazi"), P("kalibr-lielvarde")
PSK, SHP, BEL, RZE = P("isk-adazi", "launch"), P("kalibr-lielvarde", "launch"), P("oreshnik-rzeszow", "launch"), P("oreshnik-rzeszow")
NAT, CHK, ACB, BAL = P("jassm-chkalovsk", "launch"), P("jassm-chkalovsk"), P("acm-baltiysk", "launch"), P("acm-baltiysk")
ACD, ADB, BEM = P("acm-adbelt", "launch"), P("acm-adbelt"), P("isk-bemowo")
WAW, VIL, RIG, GDA, BRU, MOS, KYIV = [21.01, 52.23], [25.28, 54.69], [24.1, 56.95], [18.65, 54.35], [4.35, 50.85], [37.62, 55.75], [30.52, 50.45]
KLD, TAL, HEL, PRI, ROM, BER, PAR = [20.51, 54.71], [24.75, 59.44], [24.94, 60.17], [21.17, 42.66], [12.5, 41.9], [13.4, 52.5], [2.35, 48.85]
LVIV, DNI, NYC, WDC, VAI = [24.03, 49.84], [35.05, 48.45], [-74.0, 40.7], [-77.04, 38.9], [27.0, 59.5]
EST1, EST2 = [25.55, 60.28], [27.05, 59.37]
ISO = {"RU": "643", "PL": "616", "LT": "440", "LV": "428", "EE": "233", "BY": "112", "FI": "246", "UA": "804", "DE": "276", "IT": "380", "US": "840"}


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": ISO[iso], "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": ISO[iso], "text": text, "color": color}


HL_RU, HL_BY = hl("RU", AMBER), hl("BY", AMBER, 0.07)
HL_NATO = [hl(k, BLUE) for k in ("PL", "LT", "LV", "EE")]
CL_BALT = [cl("RU", "RUSSIA", AMBER), cl("PL", "POLAND", BLUE), cl("LT", "LITHUANIA", BLUE), cl("LV", "LATVIA", BLUE)]
LEG = [{"text": "RUSSIA", "color": AMBER}, {"text": "NATO", "color": BLUE}]
SRC_N = "Reuters; Arms Control Association"
SRC_A = "NATO; Wikipedia, Kaliningrad Oblast; CSIS Missile Threat"
SRC_H = "AP; TWZ; NATO"


def offp(base, dx, dy):
    return [round(base[0] + dx / (111.32 * math.cos(math.radians(base[1]))), 6), round(base[1] + dy / 110.57, 6)]


def disc(km, t, label=None, color=WHITE, at=None, **kw):
    at = at or GZ
    pts = [offp(at, km * math.cos(math.radians(d)), km * math.sin(math.radians(d))) for d in range(0, 360, 4)]
    z = {"points": pts, "color": color, "t": t}
    if label:
        z["label"] = label
    z.update(kw)
    return z


COAST = [21.07, 55.92]    # Lithuanian coast near Palanga: the nearest mainland coast to the burst point


def hav(p, q):
    la1, la2 = math.radians(p[1]), math.radians(q[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(math.radians(q[0] - p[0]) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


D_COAST = int(round(hav(GZ, COAST) / 5.0) * 5)


def ctx(a_, w, t_=0.2):
    """Place context for the tight ring shots: the sea and the distance to the nearest mainland coast (lower left, clear of the clock)."""
    return [lab(a_, offp(GZ, -0.26 * w, -0.16 * w), "BALTIC SEA: OPEN WATER", a_ + t_, WHITE), lab(a_, offp(GZ, -0.26 * w, -0.22 * w), "NEAREST COAST: OVER 100 KM", a_ + t_ + 0.3, YELLOW)]


def CH(h, label="SIMULATED TIME"):
    return dict(clock=f"HOUR {h}", clockLabel=label, clockRate=0)


def tgt(a, key, label, t):
    return city(a, P(key), label, t, RED, "target", 6)


def flight(sid, a, b, keys, strike, t0, t1, mins, ship_label, label_clock="TO IMPACT", **kw):
    """Missile moving along launch to target with a ticking clock that reaches zero at t1."""
    s = ST[strike]
    rate = round(mins * 60 / max(t1 - t0, 0.5), 1)
    reg(sid, a, b, keys, clock=f"T-{int(mins):02d}:{int(round((mins % 1) * 60)):02d}", clockLabel=label_clock, clockRate=rate,
        ships=[ship(a, [P(strike, "launch"), P(strike)], t0, t1, label=ship_label, color=RED, t_on=t0, size=2.4)],
        lines=[line(a, P(strike, "launch"), P(strike), t0, t1, RED, True)], **kw)


# ================================================================== Cold open [SIMULATION]
FL = round(W("p01", "lands") - 0.15, 2)
a = 0
reg("open-run", 0, FL, [("s", [20.45, 54.3], 430), ("e", [20.3, 54.3], 320)], clock="T-03:06", clockLabel="IMPACT IN", clockRate=round(186 / FL, 1),
    highlight=[HL_RU] + HL_NATO[:1], countryLabels=[cl("PL", "POLAND (NATO)", BLUE), cl("RU", "RUSSIA", AMBER)],
    cities=[city(0, MAL, "Malbork Air Base", 0.3, RED, "target", 6), city(0, KLD, "Kaliningrad", 0.4, YELLOW), city(0, GDA, "Gdansk", 1.3, GREY)],
    lines=[line(0, KAL, MAL, 0.2, FL - 0.1, RED, True)],
    ships=[ship(0, [KAL, MAL], 0.2, FL - 0.1, label="Iskander", color=RED, t_on=0.2, size=2.6)])
a = FL
reg("open-burst", a, S("p02"), [("s", MAL, 260), ("e", MAL, 170)], clock="T+00:00", clockLabel="HOUR 0 · IMPACT", clockRate=1,
    burst={"at": MAL, "t": 0.1, "km": 5, "fade": 4}, highlight=[HL_RU] + HL_NATO[:1],
    cities=[city(a, MAL, "Malbork Air Base", a + 0.5, RED, "target", 6)],
    rings=[ring(a, MAL, 9, a + 0.6, "Strike point", RED)], caption="A conventional warhead. Simulation: it has not happened.")
a = S("p02")
reg("open-sim", a, S("p03"), [("s", [20.0, 54.6], 520), ("e", [20.8, 54.7], 760)], clock="T+00:20", clockLabel="AFTER THE STRIKE", clockRate=1,
    highlight=[HL_RU] + HL_NATO[:1], cities=[city(a, MAL, "Malbork", a + 0.2, RED, "target", 6), city(a, KLD, "Kaliningrad", a + 0.5, AMBER), city(a, GDA, "Gdansk", a + 0.8, GREY)],
    labels=[lab(a, [19.5, 55.1], "A simulation: not a prediction", W("p02", "simulation"), YELLOW), lab(a, [19.5, 54.85], "It has not happened", W("p02", "not"), WHITE)])
a = S("p03")
tIt = W("p03", "It")
reg("open-launch", a, tIt, [("s", [21.0, 54.7], 430), (W("p03", "launcher"), [21.3, 54.7], 360), ("e", [21.0, 54.6], 420)], clock="T-03:06", clockLabel="LAUNCH", clockRate=1,
    highlight=[HL_RU], cities=[city(a, KAL, "Iskander launcher (simulated)", W("p03", "Iskander"), AMBER, "base", 6), city(a, KLD, "Kaliningrad", W("p03", "Kaliningrad"), AMBER, "dot", 5)],
    labels=[lab(a, [20.0, 55.2], "Three minutes earlier", a + 0.3, YELLOW), lab(a, [20.0, 54.0], "Kaliningrad oblast", W("p03", "launcher"), WHITE)])
a = tIt
tA2 = W("p03", "A", 2)
flight("open-fly", a, tA2, [("s", [20.5, 54.3], 430), (W("p03", "flight"), [20.4, 54.3], 360), ("e", [20.3, 54.3], 320)], "isk-malbork", W("p03", "hundred"), tA2 - 0.4, 3.1, "Iskander", "FLIGHT",
       highlight=[HL_RU] + HL_NATO[:1], cities=[tgt(a, "isk-malbork", "Malbork Air Base", a + 0.4), city(a, KAL, "Launch (simulated)", a + 0.2, AMBER, "base", 6)],
       labels=[lab(a, [19.0, 55.1], "184 km to fly", W("p03", "eighty-four"), WHITE), lab(a, [19.0, 54.9], "About 3 minutes", W("p03", "three"), YELLOW)])
a = tA2
reg("open-nowarn", a, S("p04"), [("s", [20.3, 54.4], 600), (W("p03", "leaves", 2), [20.5, 54.7], 760), ("e", [20.8, 55.0], 950)], clock="T-00:00", clockLabel="WARNING LEFT", clockRate=0,
    highlight=[HL_RU] + HL_NATO[:1], countryLabels=CL_BALT[:2], cities=[tgt(a, "isk-malbork", "Malbork", a + 0.2), city(a, KLD, "Kaliningrad", a + 0.4, AMBER)],
    labels=[lab(a, [17.8, 55.6], "Almost no warning", W("p03", "no"), YELLOW)])
a = S("p04")
tH = W("p04", "How")
reg("open-clock", a, tH, [("s", [18, 53.5], 2300), ("e", [21, 54.8], 1700)], **CH("0", "THE CLOCK STARTS"), highlight=[HL_RU, HL_BY] + HL_NATO, legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER), city(a, WAW, "Warsaw", a + 1.0, BLUE)],
    labels=[lab(a, [8.5, 58.5], "24 hours on the clock", W("p04", "twenty-four"), YELLOW)])
a = tH
reg("open-q", a, S("p05"), [("s", [21, 54.8], 1500), (W("p04", "line"), [21.5, 54.9], 1100), ("e", [21.5, 54.8], 700)], **CH("24", "HOURS TO RUN"), highlight=[HL_RU] + HL_NATO[:2], legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER), tgt(a, "isk-malbork", "Malbork", a + 0.7)],
    labels=[lab(a, [14.2, 57.8], "How does a day of war end?", W("p04", "day"), WHITE), lab(a, [14.2, 57.3], "What line does it stop at?", W("p04", "line"), YELLOW)])

# ================================================================== Chapter 01 [REAL DATA] a note to NATO
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "A note to NATO", "REAL DATA")
tRu, tIf = W("p05", "Russia"), W("p05", "If")
glob("c1-note", a, tRu, [("s", 52, 20, 1000), ("e", 53, 15, 1500)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="THE NOTE", clockRate=0,
     markers=[{"at": MOS, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 0.3}, {"at": BRU, "label": "NATO states", "color": BLUE, "kind": "base", "size": 5, "t": 1.2}],
     arcs=[{"from": MOS, "to": BRU, "t0": 0.6, "t1": 2.8, "color": AMBER, "loft": 0.25}], caption="30 September 2026: Reuters reports a note sent to NATO states.")
a = tRu
reg("c1-block", a, tIf, [("s", [20.5, 54.7], 600), (W("p05", "naval"), [19.5, 55.0], 520), ("e", [20.0, 55.0], 420)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="RUSSIA'S CLAIM", clockRate=0,
    highlight=[HL_RU] + HL_NATO[:1], countryLabels=CL_BALT[:2],
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER)],
    lines=[line(a, GDA, KLD, W("p05", "blockade"), W("p05", "blockade") + 2.0, BLUE, True, "Blockade, as Russia claims")],
    labels=[lab(a, [18.4, 56.2], "Russia: NATO plans a blockade", W("p05", "information"), WHITE), lab(a, [18.4, 55.8], "Air and naval", W("p05", "air"), YELLOW)])
a = tIf
t2R = W("p05", "Russia", 2)
reg("c1-cut", a, t2R, [("s", [20.5, 54.7], 700), ("e", [20.3, 54.7], 520)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="THE THREAT", clockRate=0,
    highlight=[HL_RU] + HL_NATO[:1], cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER)], labels=[lab(a, [18.0, 56.0], "If NATO cuts it off", a + 0.2, WHITE)])
a = t2R
reg("c1-arsenal", a, S("p06"), [("s", [20.0, 54.7], 800), (W("p05", "entire"), [20.0, 54.7], 700), ("e", [21.0, 54.8], 560)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="THE THREAT", clockRate=0,
    highlight=[HL_RU] + HL_NATO[:1], cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER)],
    rings=[ring(a, KLD, 150, W("p05", "entire"), "", AMBER, True), ring(a, KLD, 300, W("p05", "nuclear"), "", RED, True)],
    labels=[lab(a, [18.0, 55.6], "Its entire arsenal", W("p05", "entire"), YELLOW), lab(a, [18.0, 55.2], "Including nuclear weapons", W("p05", "nuclear"), RED)])
a = S("p06")
tNa = W("p06", "says")
reg("c1-sg", a, tNa, [("s", BRU, 1500), (W("p06", "four"), [6, 51], 1300), ("e", [8, 51.5], 1100)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="NATO'S ANSWER", clockRate=0,
    cities=[city(a, BRU, "NATO headquarters, Brussels", a + 0.4, BLUE, "base", 6)],
    labels=[lab(a, [-0.5, 54.5], "Secretary-general: four words", W("p06", "four"), WHITE), lab(a, [-0.5, 53.9], "Stop the nuclear threats", W("p06", "stop"), YELLOW)])
a = tNa
reg("c1-def", a, S("p07"), [("s", [15, 52], 2200), (W("p06", "plan"), [17, 53], 1900), ("e", [19, 53.5], 1500)], tag="REAL DATA", source=SRC_N, clock="30 SEP 2026", clockLabel="NATO'S ANSWER", clockRate=0,
    highlight=HL_NATO + [hl("DE", BLUE, 0.06)], legend=[{"text": "NATO", "color": BLUE}],
    cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER)],
    labels=[lab(a, [8.0, 57.5], "NATO: a defensive alliance", W("p06", "defensive"), WHITE), lab(a, [8.0, 57.0], "No such plan", W("p06", "no"), YELLOW)])
a = S("p07")
tWi = W("p07", "with")
reg("c1-sn", a, tWi, [("s", [12.5, 43.0], 1800), (W("p07", "Steadfast"), [12.0, 43.5], 1500), ("e", [11.5, 44.0], 1300)], tag="REAL DATA", source="AP; Stars and Stripes", clock="OCT 2026", clockLabel="TWO WEEKS LATER", clockRate=0,
    highlight=[hl("IT", BLUE, 0.12)], countryLabels=[cl("IT", "ITALY", BLUE)],
    labels=[lab(a, [6.0, 46.8], "NATO's annual nuclear exercise", W("p07", "annual"), WHITE), lab(a, [6.0, 46.3], "Steadfast Noon", W("p07", "Steadfast"), YELLOW)])
a = tWi
reg("c1-sn2", a, S("p08"), [("s", [11.5, 44.0], 1300), (W("p07", "called"), [13.0, 45.0], 1700), ("e", [16, 48], 2400)], tag="REAL DATA", source="AP; Stars and Stripes", clock="OCT 2026", clockLabel="TWO WEEKS LATER", clockRate=0,
    highlight=[hl("IT", BLUE, 0.12)] + HL_NATO, countryLabels=[cl("IT", "ITALY", BLUE)],
    cities=[city(a, [12.8, 42.6], "Steadfast Noon: Italy", a + 0.3, BLUE, "base", 6)],
    labels=[lab(a, [12.8, 41.7], "No live weapons", W("p07", "live"), WHITE), lab(a, [7.0, 41.2], "NATO called it routine", W("p07", "routine"), YELLOW)])
a = S("p08")
tInn = W("p08", "In")
reg("c1-spark", a, tInn, [("s", [20.5, 54.7], 700), (W("p08", "spark"), [20.5, 54.8], 560), ("e", [20.5, 54.8], 430)], clock="T+00:00", clockLabel="THE SPARK", clockRate=0,
    highlight=[HL_RU] + HL_NATO[:1], cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER)],
    labels=[lab(a, [18.2, 55.8], "The note: our spark", W("p08", "spark"), YELLOW)])
a = tInn
reg("c1-moscow", a, S("p09"), [("s", [28, 55], 2400), (W("p08", "acts"), [26, 55], 1900), ("e", [22, 54.8], 1200)], clock="T+00:00", clockLabel="THE CLOCK STARTS", clockRate=1,
    highlight=[HL_RU] + HL_NATO[:1], cities=[city(a, MOS, "Moscow", a + 0.3, AMBER), city(a, KLD, "Kaliningrad", a + 0.9, AMBER)],
    lines=[line(a, MOS, KLD, W("p08", "acts"), W("p08", "acts") + 2.2, AMBER, True, "Moscow acts")],
    labels=[lab(a, [18.0, 57.8], "Our simulation: on its own warning", W("p08", "own"), YELLOW)])

a = S("p09")
tAb, tRs = W("p09", "about"), W("p09", "Russia")
reg("c1-kal", a, tAb, [("s", [20.5, 54.8], 480), ("e", [20.8, 54.8], 380)], tag="REAL DATA", source=SRC_A, clock="", highlight=[HL_RU] + HL_NATO[:2], countryLabels=CL_BALT[:1],
    cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER, "base", 6)],
    labels=[lab(a, [18.3, 55.6], "Russian land on the Baltic coast", W("p09", "Baltic"), WHITE)])
a = tAb
reg("c1-kal2", a, tRs, [("s", [21.0, 54.8], 400), ("e", [22.2, 54.8], 700)], tag="REAL DATA", source=SRC_A, clock="", highlight=[HL_RU] + HL_NATO[:1] + [hl("LT", BLUE)], countryLabels=CL_BALT[:4],
    cities=[city(a, KLD, "Kaliningrad", a + 0.2, AMBER, "base", 6)],
    labels=[lab(a, [18.3, 55.9], "About 1 million people", W("p09", "million"), YELLOW), lab(a, [24.2, 53.7], "Wedged in", W("p09", "wedged"), WHITE)])
a = tRs
reg("c1-isk", a, S("p10"), [("s", [20.5, 54.7], 600), (W("p09", "eighteen"), [20.8, 54.8], 420), ("e", [21.0, 54.8], 320)], tag="REAL DATA", source=SRC_A, clock="SINCE 2018", clockLabel="ISKANDER BASED HERE", clockRate=0,
    highlight=[HL_RU], cities=[city(a, KAL, "Iskander missiles", W("p09", "Iskander"), YELLOW, "base", 6), city(a, KLD, "Kaliningrad", a + 0.3, YELLOW)],
    labels=[lab(a, [18.8, 55.5], "Based here since 2018", W("p09", "since"), YELLOW)])
a = S("p10")
tEi = W("p10", "Either")
reg("c1-range", a, tEi, [("s", [21, 54.7], 1300), (W("p10", "five"), [21, 54.7], 1700), ("e", [21, 54.2], 1500)], tag="REAL DATA", source="CSIS Missile Threat; Bulletin of the Atomic Scientists", clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KAL, "Iskander", a + 0.3, AMBER, "base", 6)],
    rings=[ring(a, KAL, 350, W("p10", "fifty"), "350 km", AMBER, True), ring(a, KAL, 500, W("p10", "five"), "500 km", ORANGE, True)],
    labels=[lab(a, [15.5, 56.8], "Iskander range by source", W("p10", "range"), YELLOW)])
a = tEi
reg("c1-reach", a, S("p11"), [("s", [21.5, 54.8], 1500), (W("p10", "Vilnius"), [22.5, 55.0], 1400), ("e", [22.5, 55.0], 1200)], tag="REAL DATA", source="CSIS Missile Threat", clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KAL, "Kaliningrad", a + 0.2, AMBER, "base", 6), city(a, WAW, "Warsaw", W("p10", "Warsaw"), BLUE, "dot", 6), city(a, VIL, "Vilnius", W("p10", "Vilnius"), BLUE, "dot", 6), city(a, RIG, "Riga", W("p10", "Riga"), BLUE, "dot", 6)],
    lines=[line(a, KAL, WAW, W("p10", "Warsaw"), W("p10", "Warsaw") + 1.5, AMBER, True), line(a, KAL, VIL, W("p10", "Vilnius"), W("p10", "Vilnius") + 1.5, AMBER, True), line(a, KAL, RIG, W("p10", "Riga"), W("p10", "Riga") + 1.5, AMBER, True)],
    labels=[lab(a, [16.0, 57.0], "All in reach", W("p10", "reach"), YELLOW)])
a = S("p11")
tIt11 = W("p11", "It")
SW1, SW2 = [22.8, 54.4], [23.6, 54.1]
reg("c1-suw", a, tIt11, [("s", [23.2, 54.3], 480), (W("p11", "Suwalki"), [23.3, 54.2], 340), ("e", [23.3, 54.1], 260)], tag="REAL DATA", source="Wikipedia, Suwalki Gap; TVP World", clock="", highlight=[HL_RU, HL_BY] + HL_NATO,
    countryLabels=[cl("BY", "BELARUS", AMBER), cl("PL", "POLAND", BLUE), cl("LT", "LITHUANIA", BLUE)],
    cities=[city(a, KLD, "Kaliningrad", a + 0.2, AMBER)],
    lines=[line(a, SW1, SW2, W("p11", "strip"), W("p11", "strip") + 1.8, YELLOW, False, "About 65 km", 3)],
    labels=[lab(a, [22.0, 53.6], "The Suwalki Gap", W("p11", "Suwalki"), YELLOW)])
a = tIt11
reg("c1-link", a, S("p12"), [("s", [23.0, 54.8], 900), (W("p11", "shortest"), [23.0, 54.6], 1200), ("e", [23.0, 54.8], 1500)], tag="REAL DATA", source="Wikipedia, Suwalki Gap", clock="", highlight=[HL_RU, HL_BY] + HL_NATO,
    cities=[city(a, WAW, "Poland", a + 0.2, BLUE), city(a, RIG, "Riga", W("p11", "Baltic"), BLUE), city(a, VIL, "Vilnius", W("p11", "Baltic") + 0.3, BLUE)],
    lines=[line(a, WAW, VIL, W("p11", "shortest"), W("p11", "shortest") + 1.8, BLUE, False, "Shortest land link", 3), line(a, VIL, RIG, W("p11", "Baltic") + 0.4, W("p11", "Baltic") + 1.8, BLUE, False, None, 3)],
    labels=[lab(a, [16.0, 56.6], "Poland to the Baltic states", W("p11", "land"), WHITE)])
a = S("p12")
reg("c1-q", a, S("p13"), [("s", [18, 54], 2000), (W("p12", "actually"), [20, 54.2], 1600), ("e", [20, 54.5], 1200)], clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[tgt(a, "isk-malbork", "First missile lands", W("p12", "first")), city(a, KLD, "Kaliningrad", a + 0.4, AMBER)],
    labels=[lab(a, [13.0, 57.2], "What has NATO promised?", W("p12", "promised"), YELLOW)])

# ================================================================== Chapter 02 [REAL HISTORY] how close it has come
a = chapter("c2-card", S("p13"), 3.5, "CHAPTER 02", "How close it has come", "REAL HISTORY")
a = round(S("p13") + 3.5, 2)
tTh, tPo, tOu = W("p13", "Three"), W("p13", "Poland", 2), W("p13", "Our")
CL2 = dict(tag="REAL HISTORY", source=SRC_H, clock="SEPTEMBER 2025", clockLabel="TEN DAYS", clockRate=0)
reg("c2-air", a, tPo, [("s", [24.0, 55.9], 1500), (tTh, [24.5, 56.0], 1400), ("e", [24.5, 56.0], 1250)], **CL2, highlight=HL_NATO[:2] + [hl("EE", BLUE), HL_BY],
    countryLabels=[cl("PL", "POLAND", BLUE), cl("EE", "ESTONIA", BLUE)],
    ships=[ship(a, [[27.5, 52.8], [24.0, 52.4], [21.5, 52.0]], a + 0.4, tTh - 0.2, label="About 20 drones", color=AMBER, t_on=a + 0.4, size=2.0),
           ship(a, [[30.0, 59.9], [27.0, 59.7], [25.0, 59.5]], tTh + 0.3, tPo - 0.3, label="3 jets", color=AMBER, kind="us", t_on=tTh + 0.3, size=2.2)],
    labels=[lab(a, [14.0, 53.9], "About 20 Russian drones", W("p13", "about"), AMBER), lab(a, [14.0, 53.5], "Entered Poland", W("p13", "entered"), WHITE),
            lab(a, [17.5, 59.5], "Three Russian fighter jets", W("p13", "fighter"), AMBER), lab(a, [17.5, 59.1], "Estonian airspace", W("p13", "Estonian"), WHITE)])
a = tPo
reg("c2-art4", a, tOu, [("s", [14, 54.5], 2200), (W("p13", "consultations"), [12, 53.5], 2600), ("e", [10, 52.5], 3000)], **CL2, highlight=HL_NATO,
    cities=[city(a, WAW, "Warsaw", a + 0.2, BLUE), city(a, TAL, "Tallinn", a + 0.5, BLUE), city(a, BRU, "NATO, Brussels", a + 0.8, BLUE, "base", 6)],
    lines=[line(a, WAW, BRU, W("p13", "asked"), W("p13", "asked") + 1.8, BLUE, True), line(a, TAL, BRU, W("p13", "asked") + 0.3, W("p13", "asked") + 2.0, BLUE, True, "Article 4 consultations")])
a = tOu
reg("c2-begin", a, S("p14"), [("s", [20, 54.5], 1500), (W("p13", "begins"), [20.5, 54.5], 1100), ("e", [20.5, 54.7], 800)], tag="REAL HISTORY", source=SRC_H, clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER), tgt(a, "isk-malbork", "Our first strike", W("p13", "begins"))],
    labels=[lab(a, [14.5, 57.5], "Our simulation begins here", W("p13", "begins"), YELLOW)])
a = S("p14")
tA5, tBt, tIt14 = W("p14", "Article", 2), W("p14", "But"), W("p14", "It", 2)
CL3 = dict(tag="REAL HISTORY", source="NATO, The North Atlantic Treaty", clock="", highlight=HL_NATO + [hl("DE", BLUE, 0.06)])
CLN = [cl("PL", "POLAND", BLUE), cl("DE", "GERMANY", BLUE), cl("LT", "LITHUANIA", BLUE), cl("LV", "LATVIA", BLUE), cl("EE", "ESTONIA", BLUE)]
reg("c2-a45", a, tBt, [("s", [10, 52.5], 2300), (W("p14", "Article", 2), [11, 52.3], 2000), ("e", [12, 52], 1700)], **CL3, countryLabels=CLN,
    cities=[city(a, BRU, "NATO, Brussels", a + 0.3, BLUE, "base", 6), city(a, WAW, "Warsaw", W("p14", "Article", 2), BLUE), city(a, RIG, "Riga", W("p14", "Article", 2) + 0.3, BLUE), city(a, BER, "Berlin", W("p14", "Article", 2) + 0.6, BLUE)],
    labels=[lab(a, [0.0, 56.8], "Article 4: talk", W("p14", "talk"), WHITE), lab(a, [0.0, 56.3], "Article 5: the promise", W("p14", "promise"), YELLOW), lab(a, [0.0, 55.8], "An attack on one is an attack on all", W("p14", "attack"), WHITE)])
a = tBt
reg("c2-deems", a, tIt14, [("s", [12, 52], 1700), (W("p14", "deems"), [14, 52.5], 1300), ("e", [18, 54], 1000)], **CL3, countryLabels=CLN[:3],
    cities=[city(a, BRU, "Brussels", a + 0.2, BLUE, "base", 6), city(a, WAW, "Warsaw", a + 0.4, BLUE)],
    lines=[line(a, BRU, WAW, W("p14", "action"), W("p14", "action") + 2.0, BLUE, True, "Each ally decides")],
    labels=[lab(a, [6.0, 56.5], "Each ally: such action as it deems necessary", W("p14", "deems"), WHITE)])
a = tIt14
reg("c2-911", a, S("p15"), [("s", [-76, 39.5], 1200), (W("p14", "invoked"), [-75, 40], 1500), ("e", [-72, 40.3], 1900)], tag="REAL HISTORY", source="NATO, The North Atlantic Treaty", clock="11 SEP 2001", clockLabel="INVOKED ONCE", clockRate=0, highlight=[hl("US", BLUE, 0.10)],
    cities=[city(a, NYC, "New York", a + 0.3, BLUE, "dot", 6), city(a, WDC, "Washington", a + 0.7, BLUE, "dot", 6)],
    labels=[lab(a, [-86.0, 42.5], "Invoked once", W("p14", "once"), YELLOW), lab(a, [-86.0, 41.9], "After 11 September 2001", W("p14", "eleventh"), WHITE)])
a = S("p15")
tNa15, tAA = W("p15", "NATO's"), W("p15", "A")
CL4 = dict(tag="REAL HISTORY", source="Wikipedia, Incident at Pristina Airport; The Irish Times", clock="JUNE 1999", clockLabel="KOSOVO", clockRate=0, highlight=[hl("RU", AMBER, 0.04)])
reg("c2-pri", a, tNa15, [("s", [20.5, 43.5], 900), (W("p15", "Pristina"), [21.0, 42.9], 600), ("e", [21.17, 42.7], 450)], **CL4,
    cities=[city(a, PRI, "Pristina airport", W("p15", "Pristina"), WHITE, "base", 6)],
    ships=[ship(a, [[18.5, 44.5], [20.0, 43.3], PRI], a + 0.4, tNa15 - 0.2, label="About 200 Russian soldiers", color=AMBER, kind="us", t_on=a + 0.4, size=2.0)],
    labels=[lab(a, [18.2, 42.3], "Russians reach it first", W("p15", "ahead"), AMBER)])
a = tNa15
reg("c2-run", a, tAA, [("s", [21.17, 42.66], 450), (W("p15", "wanted"), [21.17, 42.66], 330), ("e", [21.17, 42.66], 230)], **CL4,
    cities=[city(a, PRI, "Pristina airport", a + 0.2, WHITE, "base", 6)],
    rings=[ring(a, PRI, 5, W("p15", "runway"), "Runway", RED)],
    labels=[lab(a, [19.6, 43.1], "NATO's commander: block the runway", W("p15", "wanted"), WHITE)])
a = tAA
tDis = W("p15", "account")
reg("c2-jack", a, S("p16"), [("s", [21.17, 42.66], 230), (W("p15", "refused"), [21.17, 42.66], 330), ("e", [21.17, 42.66], 650)], **CL4, cities=[city(a, PRI, "Pristina airport", a + 0.2, WHITE, "base", 6)],
    labels=[lab(a, [20.2, 43.1], "A British general refused", W("p15", "refused"), WHITE), lab(a, [20.2, 42.2], "Reportedly", W("p15", "reportedly"), YELLOW), lab(a, [18.4, 44.0], "The account is disputed", tDis, YELLOW)],
    caption="Reportedly: he would not start the third world war for you.")
a = S("p16")
tAbl, tOur = W("p16", "A", 2), W("p16", "Our")
CL5 = dict(tag="REAL HISTORY", source="National Security Archive", clock="NOVEMBER 1983", clockLabel="ABLE ARCHER", clockRate=0, highlight=HL_NATO + [hl("DE", BLUE, 0.06), hl("RU", AMBER, 0.06)])
reg("c2-able", a, tAbl, [("s", [15, 52], 3200), (W("p16", "conventional"), [14, 52], 2600), ("e", [13, 52], 2200)], **CL5,
    cities=[city(a, BRU, "NATO", a + 0.3, BLUE, "base", 6), city(a, MOS, "Moscow", a + 0.6, AMBER)],
    labels=[lab(a, [4.0, 58.8], "An exercise: Able Archer", W("p16", "Able"), YELLOW), lab(a, [4.0, 58.3], "Conventional to nuclear", W("p16", "nuclear"), WHITE)])
a = tAbl
reg("c2-hair", a, tOur, [("s", [20, 54], 3000), (W("p16", "hair"), [22, 54], 3300), ("e", [24, 54], 3800)], **CL5,
    cities=[city(a, BRU, "NATO", a + 0.2, BLUE, "base", 6), city(a, MOS, "Moscow", a + 0.4, AMBER)],
    lines=[line(a, MOS, BRU, W("p16", "hair"), W("p16", "hair") + 2.0, RED, True, "Hair trigger")],
    labels=[lab(a, [8.0, 61.0], "A hair trigger", W("p16", "hair"), RED), lab(a, [8.0, 60.0], "Soviets genuinely worried", W("p16", "worried"), WHITE)])
a = tOur
reg("c2-step", a, S("p17"), [("s", [20.5, 54.7], 1600), ("e", [20.5, 54.7], 800)], tag="REAL HISTORY", source="National Security Archive", clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER)],
    labels=[lab(a, [14.5, 57.3], "Our simulation ends at that step", W("p16", "ends"), YELLOW)])
a = S("p17")
tA1, tA2b = W("p17", "An"), W("p17", "An", 2)
flight("c2-isk3", a, tA2b, [("s", [20.5, 54.4], 700), (tA1, [20.5, 54.3], 430), (W("p17", "three"), [20.4, 54.3], 350), ("e", [20.2, 54.3], 320)], "isk-malbork", tA1 + 0.3, tA2b - 0.3, 3.1, "Iskander", "KALININGRAD TO MALBORK", highlight=[HL_RU] + HL_NATO[:1],
       cities=[tgt(a, "isk-malbork", "Polish base", W("p17", "Polish")), city(a, KAL, "Kaliningrad", a + 0.2, AMBER, "base", 6)],
       labels=[lab(a, [18.8, 55.5], "How fast would it unfold?", a + 0.3, WHITE), lab(a, [18.8, 55.1], "About 3 minutes", W("p17", "three"), YELLOW)])
a = tA2b
flight("c2-oresh", a, S("p18"), [("s", [26, 52.6], 1000), (W("p17", "six"), [25, 52.2], 800), ("e", [24.5, 52], 650)], "oreshnik-rzeszow", a + 0.4, S("p18") - 0.3, 6.0, "Oreshnik", "BELARUS TO POLAND", highlight=[HL_BY] + HL_NATO[:1],
       cities=[city(a, BEL, "Belarus (simulated)", a + 0.2, AMBER, "base", 6)],
       labels=[lab(a, [19.0, 54.2], "Oreshnik: about 6 minutes", W("p17", "six"), YELLOW), lab(a, [19.0, 53.8], "In our engine", W("p17", "engine"), WHITE)])
a = S("p18")
reg("c2-which", a, S("p19"), [("s", [22.5, 54.2], 1300), (W("p18", "hit"), [22.5, 54.0], 1000), ("e", [22, 53.5], 1500)], clock="", highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, MAL, "Malbork", a + 0.3, GREY), city(a, BEM, "Bemowo Piskie", a + 0.7, GREY), city(a, ADZ, "Adazi", a + 1.1, GREY), city(a, LIE, "Lielvarde", a + 1.5, GREY), city(a, RZE, "Rzeszow", a + 1.9, GREY)],
    labels=[lab(a, [15.5, 57.0], "Which base first?", W("p18", "Which"), YELLOW), lab(a, [15.5, 56.6], "And why that one?", W("p18", "why"), WHITE)])

# ================================================================== Chapter 03 [SIMULATION] the trigger
a = chapter("c3-card", S("p19"), 3.5, "CHAPTER 03", "The trigger", "SIMULATION")
a = round(S("p19") + 3.5, 2)
tJa, tTn = W("p19", "Jamming"), W("p19", "Then")
reg("c3-first", a, tJa, [("s", [21, 55.5], 1500), ("e", [22, 55.5], 1000)], **CH("0", "THE FIRST HOURS"), highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER)],
    labels=[lab(a, [15.0, 58.2], "The first hours are Russian", W("p19", "Russian"), AMBER), lab(a, [15.0, 57.7], "A choice, not a forecast", W("p19", "choice"), YELLOW)])
a = tJa
reg("c3-jam", a, tTn, [("s", [21, 55], 1000), (W("p19", "cyber"), [21, 55.3], 1300), ("e", [21, 55.5], 1600)], **CH("0", "THE FIRST HOURS"), highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.2, AMBER)],
    rings=[ring(a, KLD, 150, a + 0.3, "Jamming", AMBER, True), ring(a, KLD, 320, W("p19", "cyber"), "Cyber attacks", ORANGE, True)],
    labels=[lab(a, [13.5, 57.9], "The pattern of the real incidents", W("p19", "pattern"), WHITE)])
a = tTn
reg("c3-then", a, S("p20"), [("s", [22.5, 55.8], 1300), (W("p19", "forecasts"), [23, 55.8], 1000), ("e", [24, 55.8], 1600)], **CH("0", "THEN THE MISSILES"), highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KAL, "Kaliningrad", a + 0.2, AMBER, "base", 6), city(a, PSK, "Pskov region", a + 0.6, AMBER, "base", 6), city(a, SHP, "Baltic Fleet", a + 1.0, AMBER, "base", 6)],
    lines=[line(a, KAL, MAL, a + 1.2, a + 2.2, RED, True), line(a, PSK, ADZ, a + 1.5, a + 2.5, RED, True), line(a, SHP, LIE, a + 1.8, a + 2.8, RED, True)],
    labels=[lab(a, [14.5, 58.3], "Three launch points (simulated)", W("p19", "missiles"), WHITE), lab(a, [14.5, 57.8], "Not forecasts", W("p19", "forecasts"), YELLOW)])
a = S("p20")
tPl, tTh20 = W("p20", "Polish"), W("p20", "The")
tImp20 = round(tPl - 0.5, 2)
flight("c3-malf", a, tPl, [("s", [20.5, 54.3], 450), (W("p20", "Iskander"), [20.2, 54.3], 360), ("e", [19.8, 54.2], 280)], "isk-malbork", a + 0.6, tImp20, 3.1, "Iskander", "TO IMPACT", highlight=[HL_RU] + HL_NATO[:1],
       cities=[tgt(a, "isk-malbork", "Malbork Air Base", W("p20", "Malbork")), city(a, KAL, "Kaliningrad", a + 0.2, AMBER, "base", 6)],
       labels=[lab(a, [18.3, 55.0], "Hour 0: first strike", a + 0.3, YELLOW)])
a = tPl
reg("c3-malz", a, tTh20, [("s", MAL, 280), (W("p20", "within"), MAL, 210), ("e", MAL, 170)], **CH("0"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[tgt(a, "isk-malbork", "Malbork Air Base", a + 0.2), city(a, KLD, "Kaliningrad", a + 0.5, AMBER)],
    rings=[ring(a, MAL, 8, a + 0.4, "Conventional hit", RED)],
    labels=[lab(a, [18.0, 54.5], "Within easy reach of Kaliningrad", W("p20", "within"), WHITE)])
a = tTh20
reg("c3-aim", a, S("p21"), [("s", [20.2, 54.3], 400), (W("p20", "before"), [20.2, 54.4], 320), ("e", [20.2, 54.4], 450)], **CH("0"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[tgt(a, "isk-malbork", "Malbork", a + 0.2), city(a, KLD, "Kaliningrad oblast", a + 0.5, AMBER)],
    lines=[line(a, MAL, KLD, W("p20", "use"), W("p20", "use") + 2.0, BLUE, True, "NATO use: prevented")],
    labels=[lab(a, [18.5, 55.3], "The aim: hit it first", W("p20", "aim"), YELLOW), lab(a, [18.5, 55.0], "Before NATO can use it", W("p20", "before"), WHITE)])
a = S("p21")
tHi, tIt21 = W("p21", "hits"), W("p21", "It")
reg("c3-pskov", a, tHi, [("s", [26, 57.3], 800), (W("p21", "Pskov"), [26.5, 57.4], 650), ("e", [26.5, 57.4], 520)], **CH("0.5", "HALF AN HOUR IN"), highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, PSK, "Pskov region (simulated)", W("p21", "Pskov"), AMBER, "base", 6), city(a, ADZ, "Adazi Base", W("p21", "Adazi") if False else a + 2.5, RED, "target", 6)],
    ships=[ship(a, [PSK, ADZ], a + 0.5, tHi + 0.3, label="Iskander", color=RED, t_on=a + 0.5, size=2.4)], lines=[line(a, PSK, ADZ, a + 0.5, tHi + 0.3, RED, True)],
    labels=[lab(a, [20.5, 58.5], "Half an hour in", a + 0.3, YELLOW)])
a = tHi
reg("c3-adazi", a, tIt21, [("s", ADZ, 300), (W("p21", "Canadian-led"), ADZ, 220), ("e", ADZ, 170)], **CH("0.5", "HALF AN HOUR IN"), highlight=HL_NATO,
    cities=[tgt(a, "isk-adazi", "Adazi Base, Latvia", a + 0.3), city(a, RIG, "Riga", a + 0.8, GREY)],
    rings=[ring(a, ADZ, 8, a + 0.2, "Conventional hit", RED)],
    labels=[lab(a, [22.5, 57.6], "Canadian-led NATO battlegroup", W("p21", "Canadian-led"), BLUE)])
a = tIt21
reg("c3-a250", a, S("p22"), [("s", [26.3, 57.4], 620), (W("p21", "minutes"), [26.3, 57.4], 520), ("e", [26.3, 57.4], 460)], **CH("0.5"), highlight=[HL_RU] + HL_NATO,
    cities=[city(a, PSK, "Launch (simulated)", a + 0.2, AMBER, "base", 6), tgt(a, "isk-adazi", "Adazi", a + 0.5)],
    lines=[line(a, PSK, ADZ, W("p21", "two"), W("p21", "two") + 1.5, RED, True, "250 km")],
    labels=[lab(a, [23.0, 58.5], "3.5 minutes", W("p21", "minutes"), YELLOW)])
a = S("p22")
tHe, tIt22 = W("p22", "heads"), W("p22", "It")
reg("c3-ship", a, tHe, [("s", [21.5, 56.5], 700), (W("p22", "ship"), [21.8, 56.6], 560), ("e", [22.0, 56.6], 480)], **CH("1"), highlight=HL_NATO, legend=LEG,
    cities=[city(a, SHP, "Baltic Fleet ship (simulated)", W("p22", "ship"), AMBER, "base", 6)],
    labels=[lab(a, [18.0, 57.6], "Hour 1", a + 0.3, YELLOW), lab(a, [18.0, 57.2], "A Kalibr cruise missile", W("p22", "Kalibr"), WHITE)])
a = tHe
flight("c3-kal", a, S("p23"), [("s", [22.4, 56.6], 560), (W("p22", "twenty-one"), [22.5, 56.6], 520), ("e", [23.6, 56.8], 380)], "kalibr-lielvarde", a + 0.2, S("p23") - 0.5, 21.0, "Kalibr", "TO IMPACT", highlight=HL_NATO,
       cities=[city(a, SHP, "Baltic Fleet ship", a + 0.1, AMBER, "base", 6), tgt(a, "kalibr-lielvarde", "Lielvarde Air Base", W("p22", "Lielvarde"))],
       labels=[lab(a, [20.0, 57.6], "About 21 minutes", W("p22", "twenty-one"), YELLOW), lab(a, [20.0, 57.2], "Far more warning than the Iskanders", W("p22", "warning"), WHITE)])
a = S("p23")
reg("c3-all", a, S("p24"), [("s", [24.5, 56.0], 1300), (W("p23", "real"), [24, 55.8], 1100), ("e", [23, 55.6], 1500)], **CH("1"), highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, KAL, "Launch (simulated)", W("p23", "simulated"), AMBER, "base", 6), city(a, PSK, "Launch (simulated)", W("p23", "simulated") + 0.4, AMBER, "base", 6), city(a, SHP, "Launch (simulated)", W("p23", "simulated") + 0.8, AMBER, "base", 6),
            tgt(a, "isk-malbork", "Malbork", W("p23", "real")), tgt(a, "isk-adazi", "Adazi", W("p23", "real") + 0.4), tgt(a, "kalibr-lielvarde", "Lielvarde", W("p23", "real") + 0.8)],
    lines=[line(a, KAL, MAL, a + 0.3, a + 1.3, RED, True), line(a, PSK, ADZ, a + 0.5, a + 1.5, RED, True), line(a, SHP, LIE, a + 0.7, a + 1.7, RED, True)],
    labels=[lab(a, [15.5, 58.2], "Bases: real and public", W("p23", "public"), WHITE), lab(a, [15.5, 57.7], "Warheads: conventional", W("p23", "conventional"), YELLOW)])
a = S("p24")
tWi = W("p24", "Will")
reg("c3-art", a, tWi, [("s", [11, 52], 2800), (W("p24", "by"), [11, 52], 2400), ("e", [13, 52.3], 2000)], **CH("0 TO 6", "ARTICLES 4 AND 5"), highlight=HL_NATO + [hl("DE", BLUE, 0.06)],
    cities=[city(a, BRU, "NATO, Brussels", a + 0.3, BLUE, "base", 6), city(a, WAW, "Warsaw", W("p24", "five"), BLUE), city(a, RIG, "Riga", W("p24", "five") + 0.3, BLUE)],
    rings=[ring(a, BRU, 250, W("p24", "five"), "", BLUE, True)],
    labels=[lab(a, [-2.0, 57.8], "Article 4: at once", W("p24", "invokes"), WHITE), lab(a, [-2.0, 57.3], "Article 5: by about hour six", W("p24", "five"), YELLOW)])
a = tWi
reg("c3-hit", a, S("p25"), [("s", [20.5, 54.7], 1200), (W("p24", "what"), [20.5, 54.7], 800), ("e", [20.5, 54.7], 600)], **CH("6"), highlight=[HL_RU] + HL_NATO[:1], legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.2, AMBER, "base", 6)],
    labels=[lab(a, [17.2, 55.8], "Will NATO hit back?", W("p24", "hit"), YELLOW), lab(a, [17.2, 55.4], "And with what?", W("p24", "what"), WHITE)])

# ================================================================== Chapter 04 [SIMULATION] hour by hour
a = chapter("c4-card", S("p25"), 3.5, "CHAPTER 04", "Hour by hour", "SIMULATION")
a = round(S("p25") + 3.5, 2)
tIt25 = W("p25", "It")
flight("c4-oresh", a, tIt25, [("s", [27.5, 52.2], 1300), (W("p25", "eastern"), [26.5, 52.0], 1100), ("e", [25.5, 51.8], 950)], "oreshnik-rzeszow", W("p25", "flies"), tIt25 - 0.3, 6.0, "Oreshnik", "TO IMPACT",
       highlight=[HL_BY] + HL_NATO[:1] + [hl("UA", TEAL, 0.06)], countryLabels=[cl("PL", "POLAND", BLUE), cl("UA", "UKRAINE", TEAL), cl("BY", "BELARUS", AMBER)],
       cities=[city(a, BEL, "Eastern Belarus (simulated)", W("p25", "eastern"), AMBER, "base", 6), tgt(a, "oreshnik-rzeszow", "Rzeszow-Jasionka", W("p25", "Rzeszow-Jasionka"))],
       labels=[lab(a, [20.2, 54.0], "Hour 4", a + 0.3, YELLOW), lab(a, [20.2, 53.6], "Oreshnik: several warheads", W("p25", "several"), WHITE)])
a = tIt25
reg("c4-rzz", a, S("p26"), [("s", [26.5, 51.8], 1100), (W("p25", "seventy-four"), [24.5, 51.0], 800), ("e", RZE, 360)], **CH("4"), highlight=HL_NATO[:1] + [hl("UA", TEAL, 0.06), HL_BY],
    countryLabels=[cl("PL", "POLAND", BLUE), cl("UA", "UKRAINE", TEAL), cl("BY", "BELARUS", AMBER)],
    cities=[tgt(a, "oreshnik-rzeszow", "Rzeszow-Jasionka Airport", a + 0.3), city(a, BEL, "Launch (simulated)", a + 0.3, AMBER, "base", 6)], rings=[ring(a, RZE, 12, a + 2.0, "Hit", RED)],
    lines=[line(a, BEL, RZE, a + 0.4, a + 2.6, RED, True, "774 km")],
    labels=[lab(a, [19.8, 50.9], "774 km in about 6 minutes", W("p25", "seven"), YELLOW)])
a = S("p26")
tCs, tRz = W("p26", "CSIS"), W("p26", "Rzeszow")
tDn = W("p26", "Dnipro")
reg("c4-conv", a, tDn, [("s", [24.5, 50.4], 700), (tCs, [26, 50.2], 1000), ("e", [27, 50.2], 1500)], **CH("4"), highlight=HL_NATO[:1] + [hl("UA", TEAL, 0.06)],
    cities=[tgt(a, "oreshnik-rzeszow", "Rzeszow-Jasionka", a + 0.3)],
    labels=[lab(a, [18.0, 51.6], "We make it conventional", W("p26", "conventional"), YELLOW), lab(a, [18.0, 51.2], "CSIS: no nuclear Oreshnik confirmed", tCs, WHITE)])
a = tDn
reg("c4-real", a, S("p27"), [("s", [27.5, 50.0], 1700), (W("p26", "Lviv"), [27.5, 50.0], 1600), (tRz, [27.5, 50.0], 1500), ("e", [27.5, 50.0], 1300)], **CH("4"), highlight=[hl("UA", TEAL, 0.10)] + HL_NATO[:1],
    cities=[city(a, DNI, "Dnipro", W("p26", "Dnipro"), TEAL, "dot", 6), city(a, LVIV, "Lviv", W("p26", "Lviv"), TEAL, "dot", 6), tgt(a, "oreshnik-rzeszow", "Rzeszow", tRz), city(a, KYIV, "Kyiv", tRz + 1.0, TEAL, "dot", 6)],
    lines=[line(a, RZE, KYIV, W("p26", "aid"), W("p26", "aid") + 2.5, TEAL, True, "Aid to Ukraine")],
    labels=[lab(a, [34.0, 52.6], "Two real uses: no nuclear warhead", W("p26", "carried"), YELLOW), lab(a, [34.0, 52.2], "Rzeszow: the aid hub", tRz, WHITE)])
a = S("p27")
tWe, tCr = W("p27", "Western"), W("p27", "cruise")
reg("c4-h5", a, tWe, [("s", [20.5, 54.0], 900), (W("p27", "joins"), [20.5, 54.0], 800), ("e", [20.5, 54.2], 700)], **CH("5", "NATO ANSWERS"), highlight=[HL_RU] + HL_NATO[:1], legend=LEG,
    cities=[city(a, NAT, "NATO aircraft (simulated)", a + 0.4, BLUE, "base", 6), city(a, KLD, "Kaliningrad", a + 0.8, AMBER)],
    labels=[lab(a, [17.2, 55.8], "Hour 5: NATO answers", a + 0.3, YELLOW), lab(a, [17.2, 55.4], "The United States joins", W("p27", "joins"), BLUE)])
a = tWe
reg("c4-first", a, tCr, [("s", [20.5, 54.6], 500), (W("p27", "first"), [20.5, 54.6], 420), ("e", [20.5, 54.6], 340)], **CH("5"), highlight=[HL_RU] + HL_NATO[:1], legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER, "base", 6)],
    labels=[lab(a, [18.4, 55.2], "Key installations: the likely first target", W("p27", "installations"), WHITE), lab(a, [18.4, 54.9], "One report", W("p27", "report"), YELLOW)])
a = tCr
flight("c4-chk", a, S("p28"), [("s", [20.1, 54.2], 400), (W("p27", "northern"), [20.1, 54.2], 340), ("e", [20.3, 54.5], 260)], "jassm-chkalovsk", a + 0.3, S("p28") - 0.6, 9.6, "Cruise missile", "TO IMPACT", highlight=[HL_RU] + HL_NATO[:1],
       cities=[city(a, NAT, "Aircraft over northern Poland", W("p27", "aircraft"), BLUE, "base", 6), tgt(a, "jassm-chkalovsk", "Chkalovsk air base", W("p27", "Chkalovsk"))])
a = S("p28")
tAt28, tWh = W("p28", "At"), W("p28", "Where")
flight("c4-bal", a, tAt28, [("s", [19.0, 54.9], 420), (W("p28", "Baltic"), [19.4, 54.8], 320), ("e", [19.7, 54.7], 260)], "acm-baltiysk", a + 0.4, tAt28 - 0.5, 11.3, "Cruise missile", "TO IMPACT", highlight=[HL_RU],
       cities=[tgt(a, "acm-baltiysk", "Baltiysk naval base", W("p28", "Baltiysk")), city(a, ACB, "NATO aircraft", a + 0.2, BLUE, "base", 6)],
       labels=[lab(a, [17.8, 55.5], "Hour 6", a + 0.3, YELLOW), lab(a, [17.8, 55.2], "Baltic Fleet's main base", W("p28", "Fleet's"), WHITE)])
a = tAt28
flight("c4-ad", a, tWh, [("s", [20.8, 54.3], 400), (W("p28", "dense"), [20.9, 54.4], 330), ("e", [20.9, 54.5], 290)], "acm-adbelt", a + 0.3, tWh - 0.4, 8.3, "Cruise missile", "TO IMPACT", highlight=[HL_RU],
       cities=[tgt(a, "acm-adbelt", "Air-defence belt", W("p28", "belt")), city(a, ACD, "NATO aircraft", a + 0.2, BLUE, "base", 6)],
       labels=[lab(a, [19.0, 55.1], "Hour 6.5", a + 0.3, YELLOW), lab(a, [19.0, 54.8], "A dense belt of air defence", W("p28", "dense"), WHITE)])
a = tWh
reg("c4-adsim", a, S("p29"), [("s", [20.9, 54.5], 290), (W("p28", "simulated"), [20.9, 54.5], 340), ("e", [20.9, 54.5], 400)], **CH("6.5"), highlight=[HL_RU],
    cities=[tgt(a, "acm-adbelt", "Air-defence belt", a + 0.2)], rings=[ring(a, ADB, 20, a + 0.5, "Point simulated", YELLOW, True)],
    labels=[lab(a, [19.3, 55.0], "Exact sites: not in open reporting", W("p28", "open"), WHITE), lab(a, [19.3, 54.7], "So the point is simulated", W("p28", "simulated"), YELLOW)])
a = S("p29")
tWr, tIt29 = W("p29", "where"), W("p29", "It")
flight("c4-bem", a, tWr, [("s", [21.8, 54.2], 340), (W("p29", "Iskander"), [21.8, 54.1], 280), ("e", [21.8, 54.0], 220)], "isk-bemowo", a + 0.6, tWr - 0.3, 3.0, "Iskander", "TO IMPACT", highlight=[HL_RU] + HL_NATO[:1],
       cities=[city(a, KAL, "Kaliningrad", a + 0.2, AMBER, "base", 6), tgt(a, "isk-bemowo", "Bemowo Piskie", W("p29", "Bemowo"))],
       labels=[lab(a, [19.8, 54.6], "Hour 13", a + 0.3, YELLOW)])
a = tWr
reg("c4-us", a, tIt29, [("s", BEM, 260), (W("p29", "stationed"), BEM, 200), ("e", BEM, 170)], **CH("13"), highlight=HL_NATO[:1],
    cities=[tgt(a, "isk-bemowo", "Bemowo Piskie", a + 0.2)], rings=[ring(a, BEM, 8, a + 0.4, "Conventional hit", RED)],
    labels=[lab(a, [20.2, 54.0], "US battalion group", W("p29", "battalion"), BLUE), lab(a, [20.2, 53.7], "By one count, about 800 soldiers", W("p29", "eight") if False else W("p29", "count"), WHITE)])
a = tIt29
reg("c4-106", a, S("p30"), [("s", [21.8, 54.1], 330), (W("p29", "three") , [21.8, 54.1], 260), ("e", [21.8, 54.1], 280)], **CH("13"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[city(a, KAL, "Launch", a + 0.2, AMBER, "base", 6), tgt(a, "isk-bemowo", "Bemowo Piskie", a + 0.5)],
    lines=[line(a, KAL, BEM, W("p29", "hundred", 2) if False else a + 0.8, a + 2.8, RED, True, "106 km")],
    labels=[lab(a, [20.0, 54.5], "3 minutes, launch to target", W("p29", "three"), YELLOW)])
a = S("p30")
tIn30, tRs30, tWar = W("p30", "In"), W("p30", "Russian"), W("p30", "war")
reg("c4-sq", a, tIn30, [("s", [20.5, 54.4], 600), (W("p30", "squeeze"), [20.5, 54.5], 480), ("e", [20.5, 54.6], 420)], **CH("14", "HOUR 14 TO 21"), highlight=[HL_RU] + HL_NATO[:1], legend=LEG,
    cities=[city(a, KLD, "Kaliningrad", a + 0.4, AMBER, "base", 6)],
    labels=[lab(a, [18.2, 55.4], "Hour 14 to 21: the squeeze", W("p30", "squeeze"), YELLOW)])
a = tIn30
reg("c4-thin", a, tRs30, [("s", [20.4, 54.6], 400), (W("p30", "bases"), [20.4, 54.6], 330), ("e", [20.4, 54.6], 280)], **CH("14", "HOUR 14 TO 21"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[tgt(a, "jassm-chkalovsk", "Chkalovsk", a + 0.3), tgt(a, "acm-baltiysk", "Baltiysk", W("p30", "bases"))],
    rings=[ring(a, CHK, 14, W("p30", "bases"), "", ORANGE), ring(a, BAL, 14, W("p30", "burning"), "", ORANGE)],
    labels=[lab(a, [18.6, 55.1], "Air cover: thin", W("p30", "thin"), WHITE), lab(a, [18.6, 54.8], "Its bases are burning", W("p30", "burning"), ORANGE)])
a = tRs30
reg("c4-doct", a, tWar, [("s", [21, 54.5], 800), (W("p30", "threaten"), [22, 54.6], 1100), ("e", [23, 54.8], 1500)], **CH("14", "HOUR 14 TO 21"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[city(a, KLD, "Kaliningrad", a + 0.3, AMBER, "base", 6)],
    rings=[ring(a, KLD, 100, W("p30", "territory"), "Its territory", AMBER, True)],
    labels=[lab(a, [15.8, 56.8], "Russian doctrine: nuclear use", W("p30", "doctrine"), RED), lab(a, [15.8, 56.3], "Attacks that threaten its territory", W("p30", "threaten"), WHITE)])
a = tWar
reg("c4-bound", a, S("p31"), [("s", [21, 55], 1300), (W("p30", "modelled"), [21, 55], 1600), ("e", [21, 55], 1900)], **CH("21", "END OF THE SQUEEZE"), highlight=[HL_RU, HL_BY] + HL_NATO, legend=LEG,
    labels=[lab(a, [13.0, 58.6], "Conventional and bounded", a + 0.3, YELLOW), lab(a, [13.0, 58.1], "No ground push modelled", W("p30", "ground"), WHITE)])
a = S("p31")
tNo, tOn2 = W("p31", "No"), W("p31", "One", 2)
tImpW = round(S("p33") - 0.4, 2)
tFly = W("p32", "flight")
reg("c4-h22", a, tNo, [("s", [20.5, 55.2], 800), (W("p31", "leaves"), [20.8, 55.4], 700), ("e", [20.5, 55.4], 650)], **CH("22", "HOUR 22"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[city(a, KAL, "Iskander-M (simulated)", W("p31", "Iskander-M"), AMBER, "base", 6), city(a, KLD, "Kaliningrad", a + 0.4, AMBER)],
    labels=[lab(a, [17.2, 56.6], "Hour 22", a + 0.3, YELLOW), lab(a, [17.2, 56.2], "One nuclear warhead", W("p31", "nuclear"), RED)])
a = tNo
reg("c4-sea", a, tOn2, [("s", [20.0, 55.6], 650), (W("p31", "coast"), [19.6, 55.8], 520), ("e", [19.4, 56.0], 420)], **CH("22"), highlight=[HL_RU] + HL_NATO[:1],
    cities=[city(a, KAL, "Launch", a + 0.2, AMBER, "base", 6), city(a, GZ, "Open water (simulated)", W("p31", "ship"), RED, "target", 6)],
    lines=[line(a, KAL, GZ, a + 0.4, a + 2.4, RED, True)],
    labels=[lab(a, [17.0, 57.2], "No ship. No coast.", W("p31", "ship"), WHITE), lab(a, [17.0, 56.8], "A warning shot: our choice", W("p31", "warning"), YELLOW)])
a = tOn2
reg("c4-pol", a, S("p32"), [("s", [20.0, 55.8], 900), (W("p31", "possible"), [20.0, 55.8], 1100), ("e", [20.0, 55.8], 1400)], **CH("22"), highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "Warning shot", a + 0.3, RED, "target", 6)],
    labels=[lab(a, [13.5, 58.5], "One reading of Russian signalling", W("p31", "reading"), WHITE), lab(a, [13.5, 58.0], "Not claimed as Russian policy", W("p31", "claim"), YELLOW)])
a = S("p32")
reg("c4-dual", a, tFly, [("s", [21, 55.2], 700), (W("p32", "either"), [21, 55.3], 600), ("e", [21, 55.3], 520)], **CH("22"), highlight=[HL_RU],
    cities=[city(a, KAL, "Iskander: dual-capable", a + 0.3, AMBER, "base", 6)],
    labels=[lab(a, [18.0, 56.4], "Either kind of warhead", W("p32", "either"), YELLOW)])
a = tFly
flight("c4-wfly", a, S("p33"), [("s", [20.6, 55.3], 700), (W("p32", "half"), [20.4, 55.4], 560), ("e", [20.2, 55.5], 480)], "isk-warning-baltic", a + 0.3, S("p33") - 0.3, 3.4, "Iskander-M", "TO BURST", highlight=[HL_RU],
       cities=[city(a, KAL, "Kaliningrad", a + 0.1, AMBER, "base", 6), city(a, GZ, "Burst point (simulated)", a + 0.4, RED, "target", 6)],
       labels=[lab(a, [17.8, 56.7], "234 km, about 3.5 minutes", W("p32", "two"), YELLOW)])
a = S("p33")
tSo = W("p33", "So")
num("c4-10kt", a, round(a + 3.9, 2), "10 KILOTONS", countTo=10, suffix=" KILOTONS", label="the yield we choose", sub="no open source gives it", color=YELLOW)
a = round(a + 3.9, 2)
reg("c4-what", a, S("p34"), [("s", [20.0, 55.8], 700), (W("p33", "Nagasaki"), [19.8, 56.0], 520), ("e", [19.5, 56.1], 420)], **CH("22", "ABOUT HALF OF NAGASAKI"), highlight=[HL_RU],
    cities=[city(a, GZ, "Burst point (simulated)", a + 0.2, RED, "target", 6)],
    labels=[lab(a, [17.0, 57.2], "About half of Nagasaki", W("p33", "half"), YELLOW), lab(a, [17.0, 56.8], "What does it do, over water?", W("p33", "What"), WHITE)])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = S("p34")
tBu, tEv, tWl = W("p34", "bursts"), W("p34", "Every"), W("p34", "well")
cardA = round(max(tEv, S("p35") - 4.0), 2)
A0 = S("p34")


def ck(a_):
    """One continuous clock for the whole chapter: T+03:24 at the flash, then ticking in step with the video."""
    secs = 204 + int(round(a_ - A0))
    return dict(clock=f"T+{secs // 60:02d}:{secs % 60:02d}", clockLabel="THE 10 kt WARHEAD", clockRate=1)
reg("c5-burst", a, tWl, [("s", GZ, 400), ("e", GZ, 300)], clock="T+03:24", clockLabel="IMPACT", clockRate=1, burst={"at": GZ, "t": round(tBu - a + 0.05, 2), "km": 14, "fade": 7}, highlight=[HL_RU],
    cities=[city(a, GZ, "Burst point", tBu + 0.4, RED, "target", 6), city(a, COAST, "Lithuanian coast", tBu + 1.0, BLUE, "dot", 6)],
    lines=[line(a, GZ, COAST, tBu + 0.8, tBu + 3.2, WHITE, True, "Over 100 km to the coast")],
    labels=[lab(a, [17.0, 57.0], "BALTIC SEA: OPEN WATER", a + 0.3, WHITE), lab(a, [17.0, 56.65], "Over open sea", W("p34", "sea"), YELLOW)], caption="One 10 kiloton airburst. Our choice. It has not happened.")
a = tWl
reg("c5-coast", a, cardA, [("s", [20.5, 56.0], 330), ("e", [21.0, 56.0], 560)], **ck(a), highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6), city(a, KLD, "Kaliningrad", a + 0.5, AMBER), city(a, COAST, "Lithuanian coast", a + 0.8, BLUE, "dot", 6)],
    lines=[line(a, GZ, COAST, a + 0.6, a + 2.6, WHITE, True, "Over 100 km")],
    burst={"at": GZ, "t": -4.0, "km": 10, "fade": 7},
    labels=[lab(a, [24.2, 57.7], "Well over 100 km from any coast", W("p34", "hundred"), YELLOW)])
a = chapter("c5-card", cardA, round(S("p35") - cardA, 2), "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
a = S("p35")
FB, P20, P5, TH, P1 = FX["fireball_km"], FX["psi20_km"], FX["psi5_km"], FX["thermal3_km"], FX["psi1_km"]
reg("c5-fire", a, S("p36"), [("s", GZ, 2.2), (W("p35", "three"), GZ, 1.8), ("e", GZ, 1.5)], **ck(a),
    burst={"at": GZ, "t": -2.0, "km": 0.45, "fade": 8},
    zones=[disc(FB, 0.3, "Fireball", WHITE, fillOpacity=0.5, solid=True)],
    labels=[lab(a, offp(GZ, 0, 0.3), "Radius: about 150 m", W("p35", "radius"), YELLOW), lab(a, offp(GZ, 0, -0.3), "About 300 m across", W("p35", "three"), WHITE)] + ctx(a, 1.5))
a = S("p36")
reg("c5-20", a, S("p37"), [("s", GZ, 3.4), (W("p36", "reinforced"), GZ, 2.8), ("e", GZ, 2.4)], **ck(a),
    zones=[disc(FB, -3, None, WHITE, fillOpacity=0.4, solid=True), disc(P20, 0.4, "", RED, fillOpacity=0.25)],
    labels=[lab(a, offp(GZ, 0, 0.5), "20 psi: just under 300 m", a + 0.5, RED), lab(a, offp(GZ, 0, -0.5), "On land: reinforced concrete fails", W("p36", "reinforced"), YELLOW)] + ctx(a, 2.4))
a = S("p37")
tOn37, tTh37 = W("p37", "On"), W("p37", "This")
reg("c5-5a", a, tOn37, [("s", GZ, 9.0), ("e", GZ, 7.5)], **ck(a),
    zones=[disc(FB, -3, None, WHITE, fillOpacity=0.4, solid=True), disc(P20, -3, None, RED, fillOpacity=0.2), disc(P5, 0.4, "", RED, fillOpacity=0.18)],
    labels=[lab(a, offp(GZ, 0, 1.8), "5 psi: 1.46 km", a + 0.6, RED)] + ctx(a, 7.5))
a = tOn37
reg("c5-5b", a, tTh37, [("s", GZ, 7.5), ("e", GZ, 8.5)], **ck(a),
    zones=[disc(FB, -3, None, WHITE, fillOpacity=0.4, solid=True), disc(P20, -3, None, RED, fillOpacity=0.2), disc(P5, -3, None, RED, fillOpacity=0.18)],
    labels=[lab(a, offp(GZ, 0, 1.9), "On land: most buildings flattened", W("p37", "flattened"), YELLOW)] + ctx(a, 7.5, 0.1))
a = tTh37
reg("c5-5c", a, S("p38"), [("s", GZ, 8.5), ("e", GZ, 10.0)], **ck(a),
    zones=[disc(FB, -3, None, WHITE, fillOpacity=0.4, solid=True), disc(P20, -3, None, RED, fillOpacity=0.2), disc(P5, -3, None, RED, fillOpacity=0.22, pulse=True)],
    labels=[lab(a, offp(GZ, 0, 2.2), "6.7 square kilometres", W("p37", "six"), YELLOW), lab(a, offp(GZ, 0, -2.2), "An estimate", W("p37", "covers"), WHITE)] + ctx(a, 8.5, 0.1))
a = S("p38")
reg("c5-burn", a, S("p39"), [("s", GZ, 9.0), (W("p38", "bare"), GZ, 8.5), ("e", GZ, 9.5)], **ck(a),
    zones=[disc(P5, -3, None, RED, fillOpacity=0.15), disc(TH, 0.4, "", ORANGE, fillOpacity=0.15)],
    labels=[lab(a, offp(GZ, 0, 2.2), "Third-degree burns: 1.6 km", a + 0.5, ORANGE), lab(a, offp(GZ, 0, -2.2), "On bare skin", W("p38", "bare"), WHITE)] + ctx(a, 8.5))
a = S("p39")
reg("c5-win", a, S("p40"), [("s", GZ, 22), (W("p39", "windows"), GZ, 20), ("e", GZ, 18)], **ck(a),
    zones=[disc(P5, -3, None, RED, fillOpacity=0.12), disc(TH, -3, None, ORANGE, fillOpacity=0.12), disc(P1, 0.4, "", WHITE, fillOpacity=0.1)],
    labels=[lab(a, offp(GZ, 0, 4.7), "1 psi: 3.95 km", a + 0.6, WHITE), lab(a, offp(GZ, 0, -4.7), "On land: windows shatter", W("p39", "windows"), YELLOW)] + ctx(a, 18))
a = S("p40")
tTe, tWe40 = W("p40", "The"), W("p40", "We")
reg("c5-none", a, tTe, [("s", GZ, 20), (W("p40", "nothing"), GZ, 22), ("e", GZ, 24)], **ck(a),
    zones=[disc(P5, -3, None, RED, fillOpacity=0.1), disc(TH, -3, None, ORANGE, fillOpacity=0.1), disc(P1, -3, None, WHITE, fillOpacity=0.08)],
    labels=[lab(a, offp(GZ, 0, 5.2), "Nothing in those rings", W("p40", "nothing"), YELLOW)] + ctx(a, 20))
a = tTe
reg("c5-fall", a, tWe40, [("s", GZ, 24), ("e", GZ, 40)], **ck(a),
    zones=[disc(P1, -3, None, WHITE, fillOpacity=0.08)],
    labels=[lab(a, offp(GZ, 0, 6.5), "Little local fallout", W("p40", "fallout"), WHITE)] + ctx(a, 24))
a = tWe40
reg("c5-nocas", a, S("p41"), [("s", GZ, 40), ("e", GZ, 220)], **ck(a), highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6)],
    labels=[lab(a, offp(GZ, -12, 9), "No casualty figure", a + 0.3, YELLOW), lab(a, offp(GZ, -12, 6), "None is published for this scenario", W("p40", "published"), WHITE)])
a = S("p41")
tWh41 = W("p41", "What")
reg("c5-first", a, tWh41, [("s", [20.5, 56.0], 500), (W("p41", "Nagasaki"), [20.5, 56.0], 800), ("e", [20.5, 56.0], 1200)], **ck(a), highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "One warhead", a + 0.3, RED, "target", 6), city(a, COAST, "Lithuanian coast", a + 0.6, BLUE, "dot", 6)], burst={"at": GZ, "t": -4.0, "km": 10, "fade": 7},
    countryLabels=[cl("LT", "LITHUANIA", BLUE), cl("RU", "RUSSIA", AMBER)],
    lines=[line(a, GZ, COAST, a + 0.5, a + 2.5, WHITE, True, "Over 100 km to the coast")],
    labels=[lab(a, [14.0, 58.8], "First nuclear weapon in war since Nagasaki", W("p41", "first"), YELLOW), lab(a, [17.2, 56.9], "BALTIC SEA", a + 0.3, WHITE)])
a = tWh41
reg("c5-rest", a, S("p42"), [("s", [20.5, 56.0], 1200), (W("p41", "rest"), [20, 55], 2000), ("e", [18, 54], 2800)], **ck(a), highlight=[HL_RU, HL_BY] + HL_NATO, legend=LEG,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6)],
    labels=[lab(a, [8.0, 59.8], "What the world does next", W("p41", "world"), WHITE), lab(a, [8.0, 59.2], "The rest of the simulation", W("p41", "rest"), YELLOW)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p42"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
a = round(S("p42") + 3.5, 2)
tMa, tRz42, tBe, tBelt = W("p42", "Malbork"), W("p42", "Rzeszow"), W("p42", "Bemowo"), W("p42", "belt")
STK = [("isk-malbork", "Malbork", "Malbork"), ("isk-adazi", "Adazi", "Adazi"), ("kalibr-lielvarde", "Lielvarde", "Lielvarde"), ("oreshnik-rzeszow", "Rzeszow", "Rzeszow"),
       ("jassm-chkalovsk", "Chkalovsk", "Chkalovsk"), ("acm-baltiysk", "Baltiysk", "Baltiysk"), ("isk-bemowo", "Bemowo", "Bemowo Piskie")]


def stk(a_, n, upto, firstnew):
    out = []
    for i, (k, w, lbl) in enumerate(STK[:upto]):
        out.append(tgt(a_, k, lbl, W("p42", w) if i >= firstnew else a_ + 0.1 + 0.1 * i))
    return out


CD = CH("24", "THE DAY AFTER")
reg("c6-line", a, tRz42, [("s", [21, 55.3], 1500), (tMa, [22, 56.0], 800), (W("p42", "Adazi"), [22.5, 55.8], 1000), ("e", [22.5, 55.5], 1300)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=stk(a, 0, 3, 0), labels=[lab(a, [13.5, 58.4], "Hour 24: seven places struck", W("p42", "seven"), YELLOW)])
a = tRz42
reg("c6-s2", a, tBelt, [("s", [21.5, 53.0], 1100), (W("p42", "Chkalovsk"), [21, 53.5], 1000), ("e", [21, 53.8], 800)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=stk(a, 0, 7, 3))
a = tBelt
reg("c6-belt", a, S("p43"), [("s", [20.8, 54.4], 600), (W("p42", "front"), [21, 54.8], 900), ("e", [21, 55.0], 1200)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=stk(a, 0, 7, 7), rings=[ring(a, ADB, 30, a + 0.3, "Air defence: partly down", ORANGE, True)],
    labels=[lab(a, [15.0, 57.3], "The front has not moved", W("p42", "front"), YELLOW)])
a = S("p43")
tIt43 = W("p43", "runway")
reg("c6-rzdark", a, tIt43, [("s", RZE, 300), (W("p43", "dark"), RZE, 230), ("e", RZE, 180)], **CD, highlight=HL_NATO[:1],
    cities=[tgt(a, "oreshnik-rzeszow", "Rzeszow", a + 0.2)], rings=[ring(a, RZE, 6, a + 0.5, "Runway closed", RED)],
    labels=[lab(a, [19.8, 50.8], "Rzeszow goes dark", W("p43", "dark"), WHITE)])
a = tIt43
reg("c6-route", a, S("p44"), [("s", [23.5, 50.3], 700), (W("p43", "route"), [25, 50.2], 1000), ("e", [27, 50.2], 1400)], **CD, highlight=HL_NATO[:1] + [hl("UA", TEAL, 0.10)],
    cities=[tgt(a, "oreshnik-rzeszow", "Rzeszow", a + 0.2), city(a, LVIV, "Lviv", a + 0.6, TEAL), city(a, KYIV, "Kyiv", a + 1.0, TEAL)],
    lines=[line(a, RZE, LVIV, a + 0.8, a + 2.2, RED, False, "Closed", 3), line(a, [21.0, 52.2], LVIV, W("p43", "another"), W("p43", "another") + 2.0, TEAL, True, "Other routes")],
    labels=[lab(a, [18.5, 52.6], "Aid hub for Ukraine", W("p43", "hub"), WHITE), lab(a, [18.5, 52.1], "Every route must find another", W("p43", "route"), YELLOW)])
a = S("p44")
tKy, tCi, tUn = W("p44", "said"), W("p44", "In", 2), W("p44", "Under")
reg("c6-sky", a, tKy, [("s", [20.5, 56.2], 900), (W("p44", "sky"), [20.5, 56.2], 1100), ("e", [20.5, 56.2], 1300)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6)],
    labels=[lab(a, [14.0, 59.0], "Over the Baltic: an empty sky", W("p44", "empty"), WHITE)])
a = tKy
reg("c6-kyiv", a, tCi, [("s", [28, 52], 1400), (W("p44", "course"), [28, 52], 1700), ("e", [27, 52.5], 2000)], tag="REAL DATA", source="Reuters", clock="NOVEMBER 2026", clockLabel="KYIV'S ALERTS", clockRate=0, highlight=[hl("UA", TEAL, 0.10), HL_RU],
    cities=[city(a, KYIV, "Kyiv", a + 0.3, TEAL, "dot", 6)],
    labels=[lab(a, [34.0, 56.6], "Kyiv: Russian jamming", W("p44", "jamming"), WHITE), lab(a, [34.0, 56.1], "Pushed drones off course", W("p44", "course"), YELLOW)])
a = tCi
reg("c6-civil", a, tUn, [("s", [20.5, 56.2], 1300), (W("p44", "avoid"), [20.5, 56.2], 1500), ("e", [21, 56.2], 1700)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    zones=[{"points": [[17.0, 54.2], [24.5, 54.8], [25.0, 58.5], [17.5, 58.5]], "color": YELLOW, "t": W("p44", "avoid") - a, "label": "Civil flights avoid", "fillOpacity": 0.10}],
    labels=[lab(a, [14.0, 59.2], "In our simulation", a + 0.3, YELLOW)])
a = tUn
reg("c6-estlink", a, S("p45"), [("s", [26.2, 59.7], 520), (W("p44", "Estlink"), [26.2, 59.7], 450), ("e", [26.2, 59.7], 400)], tag="REAL HISTORY", source="TWZ; NATO Baltic Sentry", clock="DEC 2024", clockLabel="THE CABLE CUT", clockRate=0, highlight=[hl("FI", GREY, 0.08), hl("EE", BLUE, 0.10), hl("RU", AMBER, 0.05)],
    countryLabels=[cl("FI", "FINLAND", WHITE), cl("EE", "ESTONIA", BLUE), cl("RU", "RUSSIA", AMBER)],
    cities=[city(a, HEL, "Helsinki", a + 0.2, WHITE), city(a, TAL, "Tallinn", a + 0.5, BLUE), city(a, lerp(EST1, EST2, 0.45), "Reported cut: Estlink 2", a + 1.2, RED, "target", 6)],
    lines=[line(a, EST1, EST2, a + 0.3, a + 1.6, RED, False, "Estlink 2 cable", 5)],
    labels=[lab(a, [23.0, 59.95], "Cables under the water", W("p44", "cables"), WHITE), lab(a, [23.0, 59.65], "Finland to Estonia", W("p44", "Finland"), YELLOW)])
a = S("p45")
tTh45 = W("p45", "and")
reg("c6-plume", a, tTh45, [("s", [20.0, 56.2], 300), (W("p45", "fallout"), [20.0, 56.2], 400), ("e", [20.0, 56.2], 520)], **CD, highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "Burst point", a + 0.2, RED, "target", 6)], burst={"at": GZ, "t": -4.0, "km": 6, "fade": 5},
    labels=[lab(a, [16.8, 57.5], "No plume drawn", a + 0.3, WHITE), lab(a, [16.8, 57.1], "Little local fallout", W("p45", "little"), YELLOW), lab(a, [16.8, 56.7], "We assume no wind", W("p45", "wind"), WHITE)])
a = tTh45
reg("c6-safe", a, S("p46"), [("s", [20.0, 56.2], 520), ("e", [20.0, 56.2], 900)], **CD, highlight=[HL_RU] + HL_NATO,
    cities=[city(a, GZ, "Burst point", a + 0.1, RED, "target", 6)],
    labels=[lab(a, [15.6, 58.2], "Not the same as safe", W("p45", "safe"), YELLOW)])
a = S("p46")
tEa, tTr, tWe46 = W("p46", "Each"), W("p46", "Three"), S("p47")
reg("c6-bru", a, tEa, [("s", [5, 51], 1200), (W("p46", "table"), [5, 51], 1000), ("e", [5, 51], 800)], **CD, highlight=[hl("DE", BLUE, 0.06)],
    cities=[city(a, BRU, "Brussels: Article 5 table", W("p46", "table"), BLUE, "base", 7)],
    labels=[lab(a, [0.5, 53.2], "In Brussels", a + 0.3, WHITE)])
a = tEa
reg("c6-ally", a, tTr, [("s", [12, 52], 2600), (W("p46", "own"), [12, 52], 2200), ("e", [13, 52], 1900)], **CD, highlight=HL_NATO + [hl("DE", BLUE, 0.06)],
    cities=[city(a, BRU, "Brussels", a + 0.2, BLUE, "base", 6), city(a, WAW, "Warsaw", a + 0.5, BLUE), city(a, RIG, "Riga", a + 0.8, BLUE), city(a, BER, "Berlin", a + 1.1, BLUE), city(a, PAR, "Paris", a + 1.4, BLUE)],
    lines=[line(a, p, BRU, W("p46", "decides"), W("p46", "decides") + 2.0, BLUE, True) for p in (WAW, RIG, BER, PAR)],
    labels=[lab(a, [4.0, 58.0], "Each ally decides its own action", W("p46", "decides"), YELLOW)])
a = tTr
OPT = [offp(BRU, 0, 0), [-3, 53.5], [6, 56], [12, 49]]
reg("c6-opts", a, tWe46, [("s", [5, 52], 1700), (W("p46", "pause"), [6, 52], 1900), ("e", [7, 52], 2200)], **CD, highlight=[hl("DE", BLUE, 0.06)],
    cities=[city(a, BRU, "Brussels", a + 0.2, BLUE, "base", 6)],
    lines=[line(a, BRU, [-4, 54.5], W("p46", "conventional"), W("p46", "conventional") + 1.5, WHITE, True, "A conventional reply"), line(a, BRU, [8, 57.0], W("p46", "pause"), W("p46", "pause") + 1.5, TEAL, True, "A pause and talks"),
           line(a, BRU, [14, 51.0], W("p46", "kind"), W("p46", "kind") + 1.5, RED, True, "A reply in kind")],
    labels=[lab(a, [-3.0, 59.0], "Three options, as categories", tTr + 0.3, YELLOW), lab(a, [-3.0, 58.4], "We do not pick one", W("p46", "pick"), WHITE)])
a = S("p47")
tRu47, tRo, tWr47 = W("p47", "Russia's"), W("p47", "roughly"), W("p47", "were")
stamp("c6-start", a, round(a + 2.6, 2), "FEBRUARY 2026", "New START lapses: the last treaty limits end", WHITE, tag="REAL DATA", source="Al Jazeera; Congressional Research Service")
a = round(a + 2.6, 2)
reg("c6-ns", a, tRo, [("s", [30, 56], 3200), ("e", [30, 56], 2400)], tag="REAL DATA", source="Bulletin of the Atomic Scientists; CRS", clock="", highlight=[HL_RU],
    cities=[city(a, MOS, "Moscow", a + 0.3, AMBER)],
    labels=[lab(a, [14.0, 63.0], "Nonstrategic weapons", tRu47, AMBER)])
a = tRo
num("c6-1500", a, tWr47, "1,500 TO 2,000", label="Russian nonstrategic warheads, roughly", sub="never covered by any treaty", color=AMBER, tag="REAL DATA", source="Bulletin of the Atomic Scientists; CRS")
a = tWr47
reg("c6-notreaty", a, S("p48"), [("s", [22, 55.6], 1900), ("e", [20.8, 55.4], 1100)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=stk(a, 0, 7, 0) + [city(a, GZ, "Burst point (simulated)", a + 0.6, RED, "target", 6)], burst={"at": GZ, "t": -4.0, "km": 8, "fade": 6},
    labels=[lab(a, [13.0, 58.4], "No treaty covers these weapons", a + 0.3, YELLOW)])
a = S("p48")
reg("c6-line2", a, S("p49"), [("s", [20.5, 55.5], 700), (W("p48", "line"), [20.5, 55.5], 900), ("e", [20.5, 55.3], 1200)], **CD, highlight=[HL_RU] + HL_NATO, legend=LEG,
    cities=stk(a, 0, 7, 0) + [city(a, GZ, "First nuclear use since 1945", a + 0.6, RED, "target", 6)], burst={"at": GZ, "t": -4.0, "km": 8, "fade": 6},
    labels=[lab(a, [14.8, 58.0], "The front has not moved", a + 0.2, WHITE), lab(a, [14.8, 57.5], "A line has been crossed", W("p48", "line"), RED)])

# ================================================================== End slate
add(id="end", type="endslate", start=S("p49"), end=END, tag="", title="Next scenario", line="Taiwan goes dark: a cyber attack on the grid and the chip fabs.")


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

for _s in shots:
    if _s["id"] in ("c5-fire", "c5-20", "c5-5a", "c5-5b", "c5-5c", "c5-burn", "c5-win", "c5-none", "c5-fall"):
        _s["scaleBar"] = False
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
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p19") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p19") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
