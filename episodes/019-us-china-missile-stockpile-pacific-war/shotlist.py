"""Director pass for episode 019: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 019-us-china-missile-stockpile-pacific-war
Payoff first: the 5 kt airburst over Batan Island on the real OSM city file (flash at about 2 s, under the banner), then the
run-up (the DF-26 from a simulated site in Guangdong), real data (the Iran war's magazines), real history, the first
salvo and the day-by-day, ring by ring, the day after.  Actors: China amber, US and allies blue, Taiwan teal, Iran white,
red only for strikes.  Launch sites are simulated and say so.  All times are absolute seconds.
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
    word = word.strip(".,;:?!\"")
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    cand = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()]
    if len(cand) < nth:
        raise SystemExit(f"W: no word {word!r} #{nth} in {pid}: {[h['word'] for h in WORDS if h['unit'] == pid][:80]}")
    return round(u["start"] + u["duration"] * cand[nth - 1] / len(words), 3)


KMX, KMY = 104.0, 111.0


def offp(c, dx, dy):
    return [round(c[0] + dx / KMX, 5), round(c[1] + dy / KMY, 5)]


def circle(c, km, n=48):
    return [offp(c, km * math.cos(math.radians(d)), km * math.sin(math.radians(d))) for d in range(0, 360, 360 // n)]


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


shots = []


def add(**k):
    shots.append(k)


def tl(a, t):
    return round(max(0.05, t - a), 2)


def fixt(a, b, kw):
    for key in ("labels", "cities", "rings", "zones"):
        for it in kw.get(key, []):
            if "t" in it:
                it["t"] = tl(a, it["t"])
    for it in kw.get("lines", []):
        for f in ("t0", "t1"):
            if f in it:
                it[f] = tl(a, it[f])
    for s in kw.get("ships", []):
        if "t" in s:
            s["t"] = tl(a, s["t"])
        s["t0"] = round(max(0, s.get("t0", a) - a), 2)
        s["t1"] = round(max(0.2, s.get("t1", b) - a), 2)
        if "sunkAt" in s:
            s["sunkAt"] = tl(a, s["sunkAt"])
    if "plume" in kw:
        kw["plume"]["t0"] = round(kw["plume"]["t0"] - a, 2)
        kw["plume"]["t1"] = round(kw["plume"]["t1"] - a, 2)
    if "burst" in kw:
        kw["burst"]["t"] = round(kw["burst"]["t"] - a, 2)
    return kw


def keys_of(a, b, keys):
    out = []
    for t, c, w in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else round(t - a, 2))
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def R(sid, a, b, keys, tag="SIMULATION", **kw):
    ks = keys_of(a, b, keys)
    kw = fixt(a, b, kw)
    add(id=sid, type="region", start=round(a, 3), end=round(b, 3), tag=tag, view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, camera=ks, **kw)


def C(sid, a, b, keys, rings=(), flash=None, tag="SIMULATION", **kw):
    ks = keys_of(a, b, keys)
    kw = fixt(a, b, kw)
    rs = [dict(r) for r in rings]
    for r in rs:
        r["t"] = tl(a, r["t"])
        r.setdefault("angle", 225)
    d = dict(id=sid, type="city", start=round(a, 3), end=round(b, 3), tag=tag, city="basco-batan", view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, gz=BASCO, camera=ks, rings=rs, **kw)
    if flash is not None:
        d["flashT"] = tl(a, flash)
    add(**d)


def lb(at, text, t, color=WHITE):
    return {"at": at, "text": text, "color": color, "t": t}


def mk(at, label, t, color=WHITE, kind="dot", size=6):
    d = {"at": at, "kind": kind, "color": color, "size": size}
    if label:
        d["label"] = label
    if t is not None:
        d["t"] = t
    return d


def ln(p0, p1, t0, t1, color=WHITE, label=None, dashed=False, width=3):
    d = {"from": p0, "to": p1, "color": color, "dashed": dashed, "t0": t0, "t1": t1, "width": width}
    if label:
        d["label"] = label
    return d


def poly(pts, t0, t1, color=WHITE, label=None, dashed=False, width=3):
    n = len(pts) - 1
    out = []
    for i in range(n):
        d = ln(pts[i], pts[i + 1], t0 + (t1 - t0) * i / n, t0 + (t1 - t0) * (i + 1) / n, color, None, dashed, width)
        if label and i == n // 2:
            d["label"] = label
        out.append(d)
    return out


def ship(path, t0, t1, kind="us", color=BLUE, label=None, size=20, t=None, wake=True):
    d = {"path": path, "t0": t0, "t1": t1, "kind": kind, "color": color, "size": size, "wake": wake}
    if label:
        d["label"] = label
    d["t"] = t if t is not None else t0
    return d


def rg(at, km, t, color=WHITE, label=None, dashed=True):
    d = {"at": at, "km": km, "color": color, "t": t, "dashed": dashed}
    if label:
        d["label"] = label
    return d


def zn(points, t, color=BLUE, label=None, fill=0.12, pulse=False, width=2.4, solid=False):
    d = {"points": points, "color": color, "t": t, "fillOpacity": fill, "strokeWidth": width, "solid": solid}
    if label:
        d["label"] = label
    if pulse:
        d["pulse"] = True
    return d


def lerp(p, q, f):
    f = max(0.0, min(1.0, f))
    return [round(p[0] + (q[0] - p[0]) * f, 5), round(p[1] + (q[1] - p[1]) * f, 5)]


def fly(a, b, p, q, T0, T1, label=None, size=24, color=RED, kind="pla"):
    """a missile on the straight line p->q, launched at T0, arriving at T1; the part of the flight inside [a, b]"""
    fa, fb = (a - T0) / (T1 - T0), (b - T0) / (T1 - T0)
    d = ship([lerp(p, q, fa), lerp(p, q, fb)], max(a, T0), min(b, T1), kind, color, label, size, t=max(a, T0) + 0.02)
    return d


def cd(a, b, T0, T1, total=180.0, label="UNTIL THE BURST", up=False):
    """a ticking flight clock: seconds of flight at time t go 0 -> total between T0 and T1"""
    def s(t):
        return total * max(0.0, min(1.0, (t - T0) / (T1 - T0)))
    s0, s1 = s(a), s(b)
    v = s0 if up else total - s0
    v = int(round(v))
    rate = abs(s1 - s0) / (b - a)
    return {"clock": f"T{'+' if up else '-'}{v // 60:02d}:{v % 60:02d}", "clockLabel": label, "clockRate": round(rate, 2)}


def DAY(n, label="SIMULATED CRISIS"):
    return {"clock": f"DAY {n:02d}", "clockLabel": label}


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=round(a, 3), end=round(a + dur, 3), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 3)


def stamp(sid, a, b, text, line, color=WHITE, tag="REAL DATA", **kw):
    add(id=sid, type="stamp", start=round(a, 3), end=round(b, 3), tag=tag, text=text, line=line, color=color, **kw)


# ------------------------------------------------------------------ places (lon, lat) and actors
ST = {s["id"]: s for s in sc["strikes"]}
NUC = ST["df26n-basco"]
FX = NUC["effects"]
BASCO = [NUC["target_lon"], NUC["target_lat"]]
TOWN = [121.96835, 20.44905]                        # "Basco" town label point in the OSM city file (1.2 km west-south-west of the burst)
GD = [116.0, 24.0]                                  # simulated launch site, Guangdong (nuclear shot)
LAO, IWA, SUB = [120.532, 18.178], [132.236, 34.144], [120.27, 14.8]
LONGT, JB = [119.5, 25.67], [118.9, 25.9]
L17, L26, L26B = [116.5, 24.2], [119.5, 29.0], [113.5, 24.0]
LR0, LR1, TL0, JA0 = [129.5, 27.3], [125.5, 27.5], [123.5, 23.5], [124.5, 25.0]
BEI, TPE, MNL, TKY, WAS = [116.4, 39.9], [121.5, 25.05], [120.98, 14.6], [139.7, 35.7], [-77.04, 38.9]
TEH, ISR, GULF, HOR = [51.4, 35.7], [34.8, 31.8], [52.0, 27.0], [56.3, 26.5]
TRI, BRU, OKI = [13.2, 32.9], [4.35, 50.85], [127.8, 26.3]
PAC = [124.0, 24.0]
CN, PH, JP, TW, IR, IL, LY = "156", "608", "392", "158", "364", "376", "434"


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


HL = [hl(CN, AMBER, 0.08), hl(PH, BLUE, 0.10), hl(JP, BLUE, 0.10), hl(TW, TEAL, 0.10)]
HL_IR = [hl(IR, WHITE, 0.07), hl(IL, BLUE, 0.10)]
LEG = [{"text": "CHINA", "color": AMBER}, {"text": "US AND ALLIES", "color": BLUE}]
LEG_EST = LEG + [{"text": "OUTSIDE ESTIMATES", "color": "rgba(236,239,242,0.8)"}]
CLS = [cl(CN, "CHINA", AMBER), cl(PH, "PHILIPPINES", BLUE), cl(JP, "JAPAN", BLUE)]
EXT = {"clock": "", "clockLabel": ""}
KB = 330.0                                           # flight clock of the nuclear shot: 6 minutes = 360 s of story time
DFA, DFB = W("p03", "leaves"), S("p04") - 0.6        # the DF-26 flies from the leave word to just before p04 (compressed time)
LUZ = [121.0, 21.3]

# ================================================================== Cold open [SIMULATION]
FL = round(W("p01", "Batan") + 0.2, 2)               # the flash lands on the spoken place (about 1.8 s)
a, b = 0.0, FL
R("open-fly", a, b, [("s", [119.0, 22.2], 1250), ("e", [120.0, 21.8], 1050)], clock="T-00:06", clockLabel="SINCE LAUNCH", clockRate=round(360 / 2.0, 1), highlight=HL, legend=LEG,
  cities=[mk(GD, "DF-26 SITE (SIMULATED)", 0.1, AMBER, "base", 6), mk(BASCO, None, 0.5, RED, "ring", 7)], ships=[ship([GD, BASCO], 0.05, FL, "pla", RED, "DF-26", 26)],
  lines=[ln(GD, BASCO, 0.2, FL - 0.1, RED, None, True, 2)])
a, b = FL, S("p02")
C("open-flash", a, b, [(a, BASCO, 9), (a + 1.6, BASCO, 4.2), (b, BASCO, 2.6)], rings=[{"km": FX["psi5_km"], "label": "5 PSI", "color": RED, "t": a + 1.2}, {"km": FX["psi1_km"], "label": "1 PSI", "color": TEAL, "t": a + 2.4}],
  flash=a + 0.1, clock="T+00:00", clockLabel="THE BURST", clockRate=1, labels=[lb(offp(BASCO, 0, 1.9), "BASCO AIRPORT: 5 KT AIRBURST (SIMULATED)", a + 0.9, WHITE)])
a, b = S("p02"), S("p03")
R("open-after", a, b, [(a, BASCO, 420), (a + 1.5, [120.0, 21.8], 800), (b, [119.2, 22.6], 1150)], clock="T+00:30", clockLabel="AFTER THE BURST", clockRate=1, highlight=HL, legend=LEG, burst={"at": BASCO, "t": a - 5.0, "km": 4, "fade": 9},
  countryLabels=[cl(CN, "CHINA", AMBER), cl(TW, "TAIWAN", TEAL)], cities=[mk(GD, "DF-26 SITE (SIMULATED)", a + 1.6, AMBER, "base", 6), mk(BASCO, "BATAN ISLAND", a + 0.2, RED, "ring", 7)],
  lines=[ln(GD, BASCO, a + 1.2, a + 2.6, RED, None, True, 2)], labels=[lb(offp(BASCO, 40, -40), "IT HAS NOT HAPPENED", W("p02", "not"), YELLOW), lb([120.6, 21.3], "LUZON STRAIT", a + 2.2, WHITE)])
# run-up: six minutes earlier, the DF-26 flies
a, b = S("p03"), W("p03", "It") - 0.2
R("open-launch", a, b, [(a, [118.5, 22.5], 1700), (b, [118.5, 22.5], 1000)], caption="Six minutes earlier.", highlight=HL, legend=LEG, **cd(a, b, DFA, DFB, 360, "SINCE LAUNCH", True),
  cities=[mk(GD, "DF-26 SITE (SIMULATED)", W("p03", "launcher"), AMBER, "base", 7), mk(BASCO, None, a + 0.3, RED, "ring", 7)], ships=[fly(a, b, GD, BASCO, DFA, DFB, "DF-26", 26)], lines=[ln(GD, BASCO, DFA, DFA + 1.5, RED, "731 KM", True, 2)])
a, b = b, W("p03", "where") - 0.2
R("open-df26", a, b, [(a, [118.8, 22.6], 1250), (a + 3.0, [120.0, 21.8], 900), (b, [120.0, 21.8], 750)], highlight=HL, legend=LEG, countryLabels=CLS[:2] + [cl(TW, "TAIWAN", TEAL)], **cd(a, b, DFA, DFB, 360, "SINCE LAUNCH", True),
  ships=[fly(a, b, GD, BASCO, DFA, DFB, None, 26)], lines=[ln(GD, BASCO, a, a + 0.6, RED, None, True, 2)], cities=[mk(GD, "GUANGDONG", a + 0.2, AMBER, "base", 6), mk(BASCO, "BASCO AIRPORT, BATAN ISLAND", W("p03", "airport"), RED, "target", 8)],
  labels=[lb(offp(GD, 150, 70), "A DF-26: CONVENTIONAL OR NUCLEAR", W("p03", "DF-26"), RED), lb(offp(BASCO, 0, 70), "LUZON STRAIT", W("p03", "Luzon"), WHITE)])
a, b = b, S("p04")
R("open-battery", a, b, [(a, BASCO, 450), (a + 1.7, [121.4, 20.4], 650), (b, [121.4, 20.2], 520)], highlight=HL, legend=LEG, **cd(a, b, DFA, DFB, 360, "SINCE LAUNCH", True),
  ships=[fly(a, b, GD, BASCO, DFA, DFB, None, 26)], cities=[mk(BASCO, "US LAUNCHERS (SIMULATED)", W("p03", "battery"), BLUE, "base", 8), mk(LAO, "LUZON", a + 0.3, WHITE, "dot", 5)], countryLabels=[cl(PH, "PHILIPPINES", BLUE)], rings=[rg(BASCO, 8, W("p03", "American"), RED, None, False)])
a, b = S("p04"), W("p04", "question") - 0.1
R("open-day6", a, b, [(a, BASCO, 450), (b, [119.5, 22.0], 1300)], highlight=HL, legend=LEG, **DAY(6, "SIMULATED WAR"), countryLabels=[cl(CN, "CHINA", AMBER), cl(TW, "TAIWAN", TEAL)],
  cities=[mk(BASCO, "DAY SIX: BASCO", a + 0.2, RED, "target", 8), mk(GD, "DF-26 SITE (SIMULATED)", a + 0.9, AMBER, "base", 6)], lines=[ln(GD, BASCO, a + 0.5, a + 1.6, RED, None, True, 2)],
  labels=[lb(offp(BASCO, 10, 60), "LUZON STRAIT", a + 0.7, WHITE), lb(offp(BASCO, -60, -60), "BATAN ISLANDS", a + 1.2, BLUE)])
a, b = b, S("p05")
R("open-short", a, b, [(a, PAC, 4300), (a + 2.5, [123.0, 25.0], 3300), (b, [123.0, 25.0], 2600)], highlight=HL, legend=LEG, **DAY(6, "SIMULATED WAR"), countryLabels=CLS,
  cities=[mk(BEI, "BEIJING", a + 0.3, AMBER, "dot", 6), mk(TKY, "TOKYO", a + 0.5, BLUE, "dot", 6)],
  labels=[lb([112.0, 20.0], "CHINA'S MISSILES", W("p04", "which"), AMBER), lb([133.0, 17.0], "AMERICA'S MISSILES", W("p04", "runs"), BLUE), lb([124.0, 33.0], "WHO RUNS SHORT FIRST?", W("p04", "short"), YELLOW)])

# ================================================================== Chapter 01 [REAL DATA]
IRL = [{"text": "IRAN", "color": WHITE}, {"text": "US AND ISRAEL", "color": BLUE}]
IRC = [cl(IR, "IRAN", WHITE), cl(IL, "ISRAEL", BLUE)]
a = chapter("c1-card", S("p05"), 3.7, "CHAPTER 01", "The first four days of the Iran war", "REAL DATA")
b = 44.4
R("c1-iran", a, b, [(a, [48.0, 31.0], 3800), (a + 2.5, [46.0, 31.0], 2800)], tag="REAL DATA", highlight=HL_IR, legend=IRL, source="CSIS; RUSI", caption="28 February 2026", countryLabels=IRC,
  cities=[mk(TEH, "TEHRAN", a + 0.4, WHITE, "dot", 6)], ships=[ship([ISR, [44.0, 33.0], TEH], W("p05", "joined"), b - 0.2, "us", BLUE, "US + ISRAEL", 22)],
  labels=[lb([57.0, 36.5], "THE UNITED STATES JOINED", W("p05", "United"), BLUE)])
a, b = b, 49.0
R("c1-5000", a, b, [(a, [52.0, 31.0], 2200), (b, [52.0, 30.0], 1500)], tag="REAL DATA", highlight=HL_IR, legend=[{"text": "IRAN", "color": WHITE}], source="RUSI", countryLabels=[cl(IR, "IRAN", WHITE)],
  ships=[ship([GULF, [51.0, 31.5], TEH], a + 0.4 + 0.3 * i, b, "pla", RED, "MUNITIONS" if i == 0 else None, 20) for i in range(4)], labels=[lb([57.0, 34.2], "5,000+ MUNITIONS IN 96 HOURS", W("p06", "five"), RED)])
a, b = b, 53.0
add(id="c1-11300", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="11,300", label="munitions fired by day 16", sub="RUSI", color=RED, source="RUSI")
a, b = b, W("p07", "CSIS") - 0.2
R("c1-kinds", a, b, [(a, [118.0, 24.0], 5200), (a + 3.0, [124.0, 24.0], 4200), (a + 6.5, [124.0, 24.0], 3200)], tag="REAL DATA", highlight=HL, legend=LEG, source="CSIS; one estimate", countryLabels=CLS,
  labels=[lb([100.0, 40.0], "COST: NEAR $26 BILLION (ONE ESTIMATE)", W("p06", "twenty-six"), AMBER), lb([134.0, 18.0], "THE SAME MISSILES A PACIFIC WAR NEEDS", W("p07", "kinds"), BLUE)])
a, b = b, W("p07", "That")
R("c1-small", a, b, [(a, [121.0, 21.0], 3600), (a + 2.5, [121.0, 21.0], 2800), (b, [121.0, 21.0], 2300)], tag="REAL DATA", highlight=HL, legend=LEG, source="CSIS", countryLabels=CLS,
  labels=[lb([135.0, 16.5], "PREWAR STOCKS: ALREADY TOO SMALL", W("p07", "already"), YELLOW)])
a, b = b, S("p08")
R("c1-top", a, b, [(a, [121.5, 21.0], 1500), (a + 3.0, BASCO, 700), (b, BASCO, 450)], highlight=HL, legend=LEG, countryLabels=[cl(PH, "PHILIPPINES", BLUE), cl(TW, "TAIWAN", TEAL)], **DAY(6, "THE VIDEO'S OPENING"),
  cities=[mk(BASCO, "BASCO: THE DAY SIX SHOT", W("p07", "day"), RED, "target", 8)], labels=[lb(offp(BASCO, 0, 40), "BELONGS TO THIS WAR", W("p07", "belongs"), WHITE)])
a, b = S("p08"), W("p08", "These") - 0.4 if False else 79.0
add(id="c1-tlam", type="bars", start=round(a, 3), end=round(b, 3), tag="REAL DATA", title="TOMAHAWK STOCK, ONE ESTIMATE", sub="CSIS, April 2026",
    bars=[{"label": "BEFORE THE WAR", "value": 3100, "display": "ABOUT 3,100", "color": BLUE}, {"label": "FIRED", "value": 1000, "display": "MORE THAN 1,000", "color": RED}], source="CSIS")
a, b = b, S("p09")
R("c1-fired", a, b, [(a, [50.0, 30.0], 2600), (a + 4.0, [53.0, 28.0], 1900), (a + 8.5, WAS, 2600)], tag="REAL DATA", highlight=HL_IR + [hl("840", BLUE, 0.07)], legend=[{"text": "OUTSIDE ESTIMATES", "color": WHITE}], source="CSIS", countryLabels=[cl(IR, "IRAN", WHITE)],
  ships=[ship([[56.0, 24.0], [54.0, 28.0], TEH], a + 0.5 + 0.4 * i, a + 6.0, "pla", RED, "TOMAHAWKS" if i == 0 else None, 20) for i in range(3)], labels=[lb([58.0, 34.5], "MORE THAN 1,000 FIRED", W("p08", "thousand", 2), RED), lb(offp(WAS, 100, -150), "THESE ARE OUTSIDE ESTIMATES", W("p08", "outside"), YELLOW)],
  cities=[mk(WAS, "REAL INVENTORIES ARE CLASSIFIED", W("p08", "inventories"), BLUE, "base", 8)])
a, b = S("p09"), S("p10")
R("c1-paused", a, b, [(a, [52.0, 30.0], 2700), (a + 4.5, [54.0, 27.0], 1700), (a + 8.5, [90.0, 22.0], 9000), (b, [122.0, 24.0], 5200)], tag="REAL DATA", highlight=HL + HL_IR, legend=[{"text": "IRAN", "color": WHITE}], source="CSIS; RUSI", countryLabels=[cl(IR, "IRAN", WHITE)],
  labels=[lb([58.0, 34.5], "WAR PAUSED, NOT RESOLVED", W("p09", "paused"), YELLOW), lb([125.0, 33.0], "THE OTHER OCEAN", W("p09", "other"), BLUE)], cities=[mk(HOR, "STRAIT OF HORMUZ", a + 1.5, WHITE, "dot", 6)],
  lines=[ln([56.5, 26.8], [57.5, 25.2], W("p09", "blockade"), W("p09", "blockade") + 1.3, RED, "BLOCKADE", False, 5)])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p10"), 3.7, "CHAPTER 02", "Running short", "REAL HISTORY")
b = S("p11")
SRC_L = "Reports at the time; NATO"
R("c2-libya", a, b, [(a, [15.0, 36.0], 3200), (a + 4.0, [15.0, 36.0], 2400), (a + 8.0, [10.0, 43.0], 3000), (a + 12.0, [12.0, 40.0], 3800)], tag="REAL HISTORY", highlight=[hl(LY, WHITE, 0.08)], legend=[{"text": "LIBYA", "color": WHITE}, {"text": "NATO", "color": BLUE}], source=SRC_L, caption="June 2011, eleven weeks in",
  countryLabels=[cl(LY, "LIBYA", WHITE)], cities=[mk(TRI, "TRIPOLI", a + 0.5, WHITE, "dot", 6), mk(BRU, "NATO, BRUSSELS", W("p10", "NATO"), BLUE, "base", 8)], lines=[ln(TRI, BRU, W("p10", "allies"), W("p10", "allies") + 1.6, BLUE, "ALLIES RUNNING SHORT", True, 3)],
  labels=[lb([14.0, 34.0], "A SMALL WAR FOUND THE LIMIT", W("p10", "limit"), YELLOW)])
a = b
b = a + 3.6
stamp("c2-inf", a, b, "AUGUST 2019", "The United States leaves a treaty that banned land-based missiles of this range", BLUE, "REAL HISTORY", source="Reports at the time")
a, b = b, W("p11", "Now") - 0.2
R("c2-test", a, b, [(a, [112.0, 30.0], 4800), (a + 4.0, [108.0, 28.0], 3600), (a + 8.0, [112.0, 28.0], 2600)], tag="REAL HISTORY", highlight=HL, legend=[{"text": "CHINA", "color": AMBER}, {"text": "US", "color": BLUE}], source="US Department of Defense; CSIS", countryLabels=[cl(CN, "CHINA", AMBER)],
  labels=[lb([125.0, 38.0], "500+ KM, 16 DAYS LATER", a + 0.5, BLUE), lb([100.0, 24.0], "CHINA: OUTSIDE THE TREATY", W("p11", "outside"), YELLOW), lb([100.0, 20.5], "THE LARGEST SUCH FORCE", W("p11", "largest"), AMBER)])
a, b = b, S("p12")
R("c2-typhon", a, b, [(a, [121.0, 17.0], 1400), (a + 4.5, [120.5, 16.0], 900), (a + 8.5, [128.0, 28.0], 3000), (b, IWA, 1000)], tag="REAL HISTORY", highlight=HL, legend=LEG, source="Reports at the time", countryLabels=[cl(PH, "PHILIPPINES", BLUE), cl(JP, "JAPAN", BLUE)],
  cities=[mk([120.9, 15.5], "TYPHON SENT TO THE PHILIPPINES", W("p11", "Philippines"), BLUE, "base", 8), mk(IWA, "TYPHON SHOWN IN JAPAN", W("p11", "Japan"), BLUE, "base", 8)])
a = S("p12")
b = a + 3.6
stamp("c2-csis", a, b, "JANUARY 2023", "CSIS wargame: a Chinese invasion of Taiwan, played 24 times", WHITE, "REAL HISTORY", source="CSIS, The First Battle of the Next War")
a, b = b, W("p12", "LRASM") - 0.1
R("c2-game", a, b, [(a, [121.0, 24.0], 1500), (a + 3.0, [121.5, 24.0], 1100), (a + 6.0, [121.0, 23.5], 1700), (b, [121.5, 24.0], 1300)], tag="REAL HISTORY", highlight=HL, legend=[{"text": "TAIWAN", "color": TEAL}, {"text": "CHINA", "color": AMBER}], source="CSIS", countryLabels=[cl(TW, "TAIWAN", TEAL)],
  labels=[lb([118.2, 22.5], "CHINESE INVASION", W("p12", "Chinese"), AMBER), lb([124.0, 21.5], "PLAYED 24 TIMES", a + 4.5, WHITE)], cities=[mk(TPE, "TAIWAN", a + 3.0, TEAL, "target", 8)], lines=[ln([119.2, 25.3], [120.6, 24.9], a + 0.5, a + 1.8, AMBER, None, True, 4)])
a, b = b, b + 5.5
add(id="c2-bars", type="bars", start=round(a, 3), end=round(b, 3), tag="REAL HISTORY", title="WHEN THE US RAN OUT, CSIS WARGAME", sub="Days until the stock ran out", bars=[{"label": "LRASM (ANTI-SHIP)", "value": 7, "display": "3 TO 7 DAYS", "color": RED}, {"label": "JASSM-ER", "value": 30, "display": "ABOUT 30 DAYS", "color": AMBER}], source="CSIS (2023 wargame)")
a, b = b, W("p13", "Replacing") - 0.2
R("c2-shape", a, b, [(a, PAC, 4200), (a + 4.0, [122.0, 24.0], 3000), (S("p13"), [119.0, 22.2], 1300), (b, [119.5, 22.0], 1000)], highlight=HL, legend=LEG, **cd(a, b, S("p13") + 0.3, b - 0.2, 360, "DF-26 FLIGHT", True), countryLabels=CLS,
  ships=[fly(a, b, GD, BASCO, S("p13") + 0.3, b - 0.2, "DF-26", 24)], cities=[mk(GD, "SIMULATED SITE", S("p13"), AMBER, "base", 6), mk(BASCO, "BASCO", S("p13") + 0.4, RED, "ring", 7)],
  labels=[lb([134.0, 16.0], "THIS SIMULATION TAKES ITS SHAPE HERE", W("p12", "shape"), YELLOW), lb([121.0, 25.8], "THE MISSILES FLY IN MINUTES", W("p13", "minutes"), RED)])
a, b = b, b + 5.0
add(id="c2-months", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="42 TO 64 MONTHS", label="to replace what is fired, from the day Congress pays", sub="CSIS", color=AMBER, source="CSIS")
a, b = b, S("p15")
R("c2-df26", a, b, [(a, [114.0, 30.0], 2400), (a + 4.0, [114.0, 26.0], 4400), (a + 8.0, [114.0, 24.0], 6000), (a + 12.0, [110.0, 30.0], 4200)], tag="REAL DATA", highlight=HL, legend=LEG, source="US Department of Defense; CSIS", countryLabels=CLS,
  labels=[lb([100.0, 40.0], "3,150+ BALLISTIC MISSILES, 2024", S("p14") + 0.5, AMBER), lb([100.0, 36.0], "CONVENTIONAL OR NUCLEAR", W("p14", "either"), RED)],
  cities=[mk(GD, "ABOUT 500 ARE DF-26S", W("p14", "five"), AMBER, "base", 8)], rings=[rg(GD, 3000, W("p14", "carry") - 1.0, AMBER, "DF-26 RANGE: 3,000 TO 4,000 KM", True)])
a, b = S("p15"), S("p15") + 4.3
add(id="c2-79", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="79 A YEAR", label="Tomahawks built, five-year average", sub="one estimate", color=BLUE, source="CSIS")
a, b = b, S("p16")
R("c2-reload", a, b, [(a, [136.0, 28.0], 1800), (a + 3.5, [133.0, 26.0], 1200), (a + 7.0, [131.0, 24.0], 1600)], tag="REAL DATA", highlight=HL, legend=LEG, source="CSIS",
  ships=[ship([[140.0, 29.0], [134.0, 26.0], [130.0, 24.0]], a + 0.4, b, "us", BLUE, "US SHIP", 22)], labels=[lb([141.0, 22.5], "NO RELOAD AT SEA", W("p15", "reload"), RED), lb([141.0, 19.5], "WHEN A MAGAZINE RUNS EMPTY?", W("p15", "empty"), YELLOW)])

# ================================================================== Chapter 03 [SIMULATION]
a = chapter("c3-card", S("p16"), 3.7, "CHAPTER 03", "The first salvo", "SIMULATION")
b = S("p17")
R("c3-frame", a, b, [(a, PAC, 4300), (a + 3.0, [123.0, 25.0], 3200), (a + 5.5, [121.0, 24.0], 2200)], highlight=HL, legend=LEG, **DAY(1, "DAYS 01 TO 05"), caption="Every salvo size and launch site is our choice, not a published figure.", countryLabels=CLS,
  labels=[lb([134.0, 16.0], "CONVENTIONAL FOR FIVE DAYS", W("p16", "conventional"), YELLOW)])
a, b = S("p17"), W("p17", "Another") - 0.2
T17 = (W("p17", "leaves"), W("p17", "leaves") + 4.0)
R("c3-laoag", a, b, [(a, [118.5, 21.5], 1700), (a + 3.0, [119.0, 21.0], 1100), (a + 7.0, LAO, 600), (b, LAO, 330)], highlight=HL, legend=LEG, **cd(a, b, T17[0], T17[1] + 3, 372, "DAY 01 · SINCE LAUNCH", True), countryLabels=[cl(PH, "PHILIPPINES", BLUE)],
  ships=[fly(a, b, L17, LAO, T17[0], T17[1] + 3, "DF-17", 24)], cities=[mk(L17, "GUANGDONG (SIMULATED)", a + 0.2, AMBER, "base", 7), mk(LAO, "LAOAG AIRFIELD: US LAUNCHER SITE", W("p17", "Laoag"), RED, "target", 8)],
  lines=[ln(L17, LAO, T17[0], T17[0] + 1.5, RED, "789 KM, 6 MIN", True, 2)])
a, b = b, S("p18")
T26 = W("p17", "goes")
R("c3-iwakuni", a, b, [(a, [126.0, 31.0], 2800), (a + 3.5, [127.0, 32.0], 2000), (a + 7.0, [124.0, 26.0], 4400), (a + 10.5, [124.0, 26.0], 3600)], highlight=HL, legend=LEG, **cd(a, b, T26, T26 + 5, 420, "DAY 01 · SINCE LAUNCH", True),
  ships=[fly(a, b, L26, IWA, T26, T26 + 5, "DF-26", 24)], cities=[mk(L26, "ZHEJIANG (SIMULATED)", a + 0.2, AMBER, "base", 7), mk(IWA, "MCAS IWAKUNI, JAPAN", W("p17", "Marine"), RED, "target", 8), mk(LAO, "LAOAG", W("p17", "Both"), RED, "target", 6)],
  lines=[ln(L26, IWA, T26, T26 + 1.5, RED, "1,334 KM, 7 MIN", True, 2)], labels=[lb([112.0, 18.0], "BOTH SITES ON ALLIED SOIL", W("p17", "allied"), YELLOW)])
TR = (W("p18", "launches"), W("p18", "launches") + 8.0)
a, b = S("p18"), W("p18", "It") - 0.2
R("c3-lrasm", a, b, [(a, [127.5, 27.4], 900), (a + 4.0, [127.5, 27.4], 700), (a + 8.0, [127.5, 27.4], 1100), (b, [126.5, 27.4], 800)], highlight=HL, legend=LEG, **cd(a, b, TR[0], TR[1] + 2, 1674, "DAY 01 · SINCE LAUNCH", True),
  ships=[fly(a, b, LR0, LR1, TR[0], TR[1] + 2, "LRASM", 24)], cities=[mk(LR0, "B-1B BOMBER (SIMULATED)", a + 0.3, BLUE, "base", 7), mk(LR1, "PLA NAVY GROUP (SIMULATED)", W("p18", "Chinese"), AMBER, "target", 8)], lines=[ln(LR0, LR1, TR[0], TR[0] + 1.5, BLUE, "396 KM", True, 2)],
  labels=[lb(offp(LR1, 40, 60), "28 MINUTES IN FLIGHT", W("p18", "Twenty-eight") + 0.1, WHITE)])
a, b = b, S("p19")
R("c3-watch", a, b, [(a, [124.0, 26.0], 2200), (a + 4.0, [123.0, 25.0], 3000), (a + 8.0, [124.5, 27.0], 1700), (a + 12.0, [124.0, 26.0], 2500)], highlight=HL, legend=LEG, **DAY(1), countryLabels=CLS, cities=[mk(LR1, "LRASM", a + 0.2, BLUE, "base", 7)],
  labels=[lb([134.0, 19.0], "THE FIRST US ROUND TO RUN OUT", W("p18", "first"), RED), lb([134.0, 22.0], "CSIS GAME: 3 TO 7 DAYS", W("p18", "wargame"), AMBER), lb([134.0, 16.0], "WATCH HOW LONG IT LASTS HERE", W("p18", "Watch"), YELLOW)])

# ================================================================== Chapter 04 [SIMULATION]
a = chapter("c4-card", S("p19"), 3.7, "CHAPTER 04", "Day by day", "SIMULATION")
T2 = (W("p19", "fires"), W("p19", "fires") + 6.0)
b = W("p19", "One") - 0.2
R("c4-d2", a, b, [(a, [122.0, 24.5], 1000), (a + 3.0, [121.0, 24.8], 650), (a + 8.0, [118.0, 26.0], 1300), (b, [117.0, 26.0], 1700)], highlight=HL, legend=LEG, **cd(a, b, T2[0], T2[1] + 4, 1992, "DAY 02 · SINCE LAUNCH", True), countryLabels=[cl(CN, "CHINA", AMBER)],
  ships=[fly(a, b, TL0, LONGT, T2[0], T2[1] + 4, "TOMAHAWK", 24)], cities=[mk(TL0, "US SUBMARINE (SIMULATED)", a + 0.3, BLUE, "sub", 7), mk(LONGT, "LONGTIAN", W("p19", "Fujian"), RED, "target", 8)],
  lines=[ln(TL0, LONGT, T2[0], T2[0] + 1.5, BLUE, "471 KM, 33 MIN", True, 2)], labels=[lb([113.5, 29.5], "A STRIKE ON THE MAINLAND", W("p19", "strike"), RED)], caption="RAND: such target choices move the nuclear threshold.")
a, b = b, S("p20")
R("c4-154", a, b, [(a, [124.0, 24.0], 1700), (a + 3.5, [124.0, 23.5], 1100), (b, [124.0, 23.0], 1500)], highlight=HL, legend=LEG, **DAY(2),
  cities=[mk(TL0, "ONE SUBMARINE: UP TO 154 TOMAHAWKS", W("p19", "hundred"), BLUE, "sub", 9)], ships=[ship([[126.0, 22.5], TL0], a + 0.3, b, "us", BLUE, None, 22)])
a, b = S("p20"), W("p20", "Every") - 0.2
R("c4-subic", a, b, [(a, [117.0, 19.0], 1900), (a + 3.0, [118.5, 17.0], 1300), (a + 5.5, SUB, 700), (b, [120.5, 16.5], 1700)], highlight=HL, legend=LEG, **cd(a, b, a + 0.4, a + 4.5, 402, "DAY 03 · SINCE LAUNCH", True), countryLabels=[cl(PH, "PHILIPPINES", BLUE)],
  ships=[fly(a, b, L26B, SUB, a + 0.4, a + 4.5, "DF-26", 24)], cities=[mk(L26B, "GUANGDONG (SIMULATED)", a + 0.2, AMBER, "base", 7), mk(SUB, "SUBIC BAY: WHERE SHIPS RELOAD", W("p20", "Subic"), RED, "target", 8), mk(MNL, "MANILA", a + 6.0, WHITE, "dot", 5)],
  lines=[ln(L26B, SUB, a + 0.4, a + 1.6, RED, "1,245 KM, 7 MIN", True, 2)], labels=[lb(offp(SUB, -150, 120), "AN ALLY OF ONE SIDE", W("p20", "ally"), BLUE), lb(offp(SUB, -150, 90), "A TARGET OF THE OTHER", W("p20", "target"), RED)])
a, b = b, S("p21")
R("c4-line", a, b, [(a, [120.5, 16.5], 1700), (a + 3.0, [121.0, 19.0], 1300), (b, [121.0, 20.0], 2000)], highlight=HL, legend=LEG, **DAY(3), labels=[lb([126.0, 21.0], "THE LINE GETS HARDER TO HOLD", W("p20", "harder"), YELLOW)],
  cities=[mk(BASCO, "BATAN", a + 2.0, WHITE, "dot", 5)])
a, b = S("p21"), W("p21", "In") - 0.2
if False: add(id="c4-d4", type="timeline", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="DAY FOUR: THE LRASM IS GONE", sub="Our modelling choice, the fast end of the CSIS 3 to 7 days", total=7, unit="days",
    segments=[{"from": 0, "to": 4, "label": "LRASM IN USE", "color": BLUE}, {"from": 4, "to": 7, "label": "CSIS RANGE: 3 TO 7 DAYS", "color": AMBER}], cursorTo=4)
a, b = S("p21"), S("p22")
R("c4-choice", a, b, [(a, [125.0, 26.0], 3200), (a + 4.0, [124.0, 25.0], 2400), (a + 8.5, [124.0, 25.0], 3600), (b, [123.0, 25.0], 2800)], highlight=HL, legend=LEG, **DAY(4), caption="Not a prediction: our modelling choice.", countryLabels=CLS,
  labels=[lb([134.0, 18.0], "THE FAST END OF THE RANGE", W("p21", "fast"), YELLOW)])
T5 = (W("p22", "fires"), W("p22", "fires") + 7.0)
a, b = S("p22"), W("p22", "In", 2) - 0.2
R("c4-d5", a, b, [(a, [122.0, 25.5], 1200), (a + 3.0, [121.5, 25.5], 800), (a + 6.5, [121.0, 25.5], 650), (b, [121.5, 25.5], 1000)], highlight=HL, legend=LEG, **cd(a, b, T5[0], T5[1] + 4, 2418, "DAY 05 · SINCE LAUNCH", True),
  ships=[fly(a, b, JA0, JB, T5[0], T5[1] + 4, "JASSM-ER", 24)], cities=[mk(JA0, "B-1B BOMBER (SIMULATED)", a + 0.3, BLUE, "base", 7), mk(JB, "ROCKET FORCE BASE (SIMULATED)", W("p22", "Rocket"), RED, "target", 8)], lines=[ln(JA0, JB, T5[0], T5[0] + 1.5, BLUE, "571 KM, 40 MIN", True, 2)],
  labels=[lb([125.8, 28.0], "40 MINUTES", W("p22", "Forty") + 0.1, WHITE)])
a, b = b, S("p23")
R("c4-30", a, b, [(a, [124.0, 26.0], 2200), (a + 3.0, [123.0, 25.0], 3000), (b, [123.0, 25.0], 2400)], highlight=HL, legend=LEG, **DAY(5), countryLabels=[cl(CN, "CHINA", AMBER)],
  labels=[lb([134.0, 20.0], "CSIS GAME: JASSM-ER LASTED ABOUT 30 DAYS", W("p22", "thirty"), AMBER), lb([134.0, 17.0], "HERE IT IS ONLY STARTING", W("p22", "only"), BLUE)])
a, b = S("p23"), W("p23", "That") - 0.2
R("c4-keep", a, b, [(a, [122.0, 21.0], 3000), (a + 3.0, [122.0, 19.0], 2000), (a + 6.0, [121.0, 19.0], 1500), (b, [118.0, 23.0], 3000)], highlight=HL, legend=LEG, **DAY(5), countryLabels=[cl(PH, "PHILIPPINES", BLUE)],
  cities=[mk(LAO, "LAUNCHERS ON ALLIED SOIL", a + 0.2, BLUE, "base", 8), mk(BASCO, None, a + 0.5, BLUE, "base", 7)], labels=[lb([128.0, 16.0], "THEY KEEP FIRING", W("p23", "keep"), BLUE), lb([110.0, 28.0], "MORE CONVENTIONAL MISSILES DO NOT STOP THEM", W("p23", "stop"), AMBER)],
  ships=[ship([L17, LAO], W("p23", "More") + 0.4 * i, W("p23", "More") + 2.6 + 0.4 * i, "pla", AMBER, None, 18) for i in range(3)])
a, b = b, S("p24")
R("c4-assume", a, b, [(a, [123.0, 25.0], 3000), (a + 3.0, [123.0, 25.0], 3600), (b, [122.0, 23.0], 2600)], highlight=HL, legend=LEG, **DAY(5), caption="Our assumption, not a forecast.", countryLabels=CLS,
  labels=[lb([134.0, 17.5], "THE WAR NO LONGER DEPENDS ON THE MAGAZINE COUNT", W("p23", "magazine"), YELLOW)])
a, b = S("p24"), W("p24", "The") - 0.2
R("c4-d6", a, b, [(a, BEI, 2600), (a + 3.5, [114.0, 30.0], 2800), (a + 7.0, [118.0, 24.5], 1400), (b, [120.0, 22.0], 1400)], highlight=HL, legend=LEG, **DAY(6), countryLabels=[cl(CN, "CHINA", AMBER)], ships=[fly(a, b, GD, BASCO, W("p24", "leaves"), b + 3.0, "DF-26", 26)],
  cities=[mk(BEI, "BEIJING", W("p24", "Beijing"), AMBER, "target", 8), mk(GD, "SIMULATED SITE, GUANGDONG", W("p24", "Guangdong") - 1.5, AMBER, "base", 8), mk(BASCO, None, a + 8.0, RED, "ring", 7)],
  labels=[lb(offp(BEI, 80, -150), "BREAKS ITS NO-FIRST-USE POLICY", W("p24", "break"), RED)], lines=[ln(GD, BASCO, W("p24", "leaves"), W("p24", "leaves") + 1.2, RED, "ONE DF-26", True, 2)])
a, b = b, W("p24", "half") + 0.4
add(id="c4-yield", type="bars", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="THE WARHEAD: OUR CHOICE", sub="Yield in kilotons", bars=[{"label": "NAGASAKI, 1945", "value": 21, "display": "21 KT", "color": ORANGE}, {"label": "PENTAGON CEILING (PLA)", "value": 10, "display": "BELOW 10 KT", "color": AMBER}, {"label": "THIS SIMULATION", "value": 5, "display": "5 KT", "color": RED}], source="US Department of Defense; US Strategic Bombing Survey")
a, b = b, W("p24", "day", 2) - 0.3
R("c4-target", a, b, [(a, [121.0, 21.0], 2400), (a + 4.0, [123.0, 22.0], 1500), (a + 8.0, BASCO, 700), (b, BASCO, 420)], highlight=HL, legend=LEG, **DAY(6), cities=[mk(BASCO, "BASCO AIRPORT, BATAN ISLAND", W("p24", "Basco"), RED, "target", 9)],
  labels=[lb([127.5, 24.0], "A QUARTER OF NAGASAKI", W("p24", "quarter"), WHITE)])
a, b = b, S("p25")
R("c4-ours", a, b, [(a, BASCO, 420), (a + 4.0, [121.5, 21.0], 1400), (a + 8.0, [122.0, 22.0], 2400), (b, [123.0, 22.0], 3200)], highlight=HL, legend=LEG, **DAY(6), caption="The day, the target and the weapon are our choices, not a forecast of Chinese policy.", countryLabels=[cl(PH, "PHILIPPINES", BLUE)],
  cities=[mk(BASCO, "BASCO", a + 0.2, RED, "ring", 7), mk(LAO, "LUZON", a + 5.0, WHITE, "dot", 5)])
a, b = S("p25"), S("p26")
R("c4-1126", a, b, [(a, [119.5, 22.0], 1300), (a + 2.5, [120.5, 21.2], 800), (b, BASCO, 350)], highlight=HL, legend=LEG, **cd(a, b, a, b, 360, "SIX MINUTES", False), ships=[fly(a, b, GD, BASCO, a, b, "DF-26", 26)],
  cities=[mk(GD, "SIMULATED SITE", a + 0.1, AMBER, "base", 6), mk(BASCO, "11:26", a + 0.4, RED, "ring", 8)])

# ================================================================== Chapter 05 [SIMULATION]
a = chapter("c5-card", S("p26"), 3.7, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
RK = {"fire": {"km": FX["fireball_km"], "label": "FIREBALL", "color": WHITE}, "p20": {"km": FX["psi20_km"], "label": "20 PSI", "color": ORANGE},
      "p5": {"km": FX["psi5_km"], "label": "5 PSI", "color": RED}, "b": {"km": FX["thermal3_km"], "label": "BURNS", "color": AMBER}, "p1": {"km": FX["psi1_km"], "label": "1 PSI", "color": TEAL}}


def rr(k, t):
    d = dict(RK[k])
    d["t"] = t
    return d


b = S("p27")
C("c5-burst", a, b, [(a, BASCO, 10), (a + 4.0, BASCO, 4.0), (a + 9.0, BASCO, 2.2), (b, BASCO, 3.4)], rings=[rr("fire", W("p26", "Everything"))], flash=a + 0.15, clock="T+00:00", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0, 2.2), "AIRBURST OVER THE AIRPORT", a + 1.0, RED), lb(offp(BASCO, 0, 1.2), "ENGINE: YIELD, WEAPON, HEIGHT OF BURST", W("p26", "yield"), YELLOW)])
a, b = S("p27"), W("p27", "Inside") - 0.2
C("c5-fire", a, b, [(a, BASCO, 1.4), (b, BASCO, 0.8)], rings=[rr("fire", W("p27", "radius") - 0.8)], flash=a + 0.1, clock="T+00:15", clockLabel="THE BURST", clockRate=1, labels=[lb(offp(BASCO, 0, 0.17), "116 M: LENGTH OF A FOOTBALL PITCH", W("p27", "football"), WHITE)])
a, b = b, b + 5.0
add(id="c5-nothing", type="bars", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="FIVE KILOTONS IS SMALL", sub="Yield in kilotons", bars=[{"label": "NAGASAKI, 1945", "value": 21, "display": "21 KT", "color": ORANGE}, {"label": "THIS SIMULATION", "value": 5, "display": "5 KT, ASSUMED", "color": RED}])
a, b = b, S("p29")
C("c5-20", a, b, [(a, BASCO, 0.8), (a + 2.5, BASCO, 1.4), (S("p28"), BASCO, 1.8), (S("p28") + 4.0, BASCO, 1.1), (b, BASCO, 3.0)], rings=[rr("fire", a - 3), rr("p20", W("p28", "twenty"))], clock="T+00:30", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0.0, 0.5), "NOTHING REMAINS INSIDE", a + 0.3, WHITE), lb([121.9765, 20.4505], "AIRPORT: THE TARGET", W("p28", "airport"), RED), lb(offp(BASCO, 0, -0.55), "ANY BUILDING DESTROYED", W("p28", "destroyed"), WHITE)])
a, b = S("p29"), W("p29", "This") - 0.2
C("c5-5a", a, b, [(a, BASCO, 3.0), (a + 3.0, BASCO, 4.0), (b, BASCO, 5.0)], rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", W("p29", "five"))], clock="T+00:40", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0, 1.35), "HOUSES COLLAPSE", W("p29", "collapse"), RED), lb(TOWN, "BASCO TOWN", W("p29", "Basco"), WHITE)])
a, b = b, S("p30")
C("c5-5b", a, b, [(a, BASCO, 5.0), (a + 4.0, BASCO, 4.2), (b, BASCO, 4.6)], rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3)], clock="T+00:45", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0, 1.5), "4.2 KM2 INSIDE THE RING", W("p29", "four"), RED), lb(TOWN, "BASCO TOWN CENTRE: JUST OUTSIDE", W("p29", "stops"), WHITE)])
a, b = S("p30"), S("p31")
C("c5-burn", a, b, [(a, BASCO, 4.6), (a + 4.0, BASCO, 5.6), (a + 8.0, BASCO, 5.0)], rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", W("p30", "burns"))], clock="T+00:50", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0, -1.45), "THIRD-DEGREE BURNS: 1.2 KM", W("p30", "kilometres"), AMBER), lb(offp(BASCO, 0, 1.4), "IN THE OPEN: BURNED BY THE FLASH", W("p30", "flash"), AMBER), lb(offp(BASCO, 0, 0.95), "THE FLASH ARRIVES BEFORE THE SOUND", W("p30", "sound"), WHITE)])
a, b = S("p31"), S("p32")
C("c5-1psi", a, b, [(a, BASCO, 5.5), (a + 3.5, BASCO, 7.0), (a + 7.0, BASCO, 9.0), (b, BASCO, 10.5)], rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", a - 3), rr("p1", W("p31", "one"))], clock="T+01:00", clockLabel="THE BURST", clockRate=1,
  labels=[lb(offp(BASCO, 0, -3.35), "1 PSI: WINDOWS BREAK, 3.1 KM", W("p31", "windows"), TEAL), lb(TOWN, "MOST OF BASCO TOWN INSIDE", W("p31", "Basco"), WHITE), lb(offp(BASCO, 0, 3.7), "THE WIDEST RING, THE LEAST DAMAGE", W("p31", "widest"), YELLOW)])
a, b = S("p32"), W("p32", "What") - 0.2
R("c5-fall", a, b, [(a, BASCO, 200), (a + 3.0, offp(BASCO, -25, -20), 150), (a + 6.5, offp(BASCO, -30, -30), 260), (b, offp(BASCO, -40, -40), 380)], highlight=HL, legend=LEG + [{"text": "SMALL FALLOUT PLUME", "color": AMBER}], clock="T+01:10", clockLabel="THE BURST", clockRate=1, burst={"at": BASCO, "t": a - 5.0, "km": 2, "fade": 9},
  caption="We give no death toll. The engine does not produce one.", cities=[mk(BASCO, "AIR BURST", a + 0.2, RED, "target", 8)], plume={"at": BASCO, "bearing": 225, "lengthKm": 70, "widthKm": 10, "t0": a + 0.5, "t1": a + 4.0, "color": AMBER, "label": "ASSUMED WIND: TO THE SOUTH-WEST"},
  labels=[lb(offp(BASCO, 30, 40), "LITTLE LOCAL FALLOUT", W("p32", "little"), AMBER), lb(offp(BASCO, -75, -75), "OPEN SEA, NO LANDFALL", a + 5.0, WHITE)])
a, b = b, S("p33")
C("c5-near", a, b, [(a, BASCO, 9.0), (a + 3.0, BASCO, 6.0), (b, BASCO, 4.0)], rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", a - 3), rr("p1", a - 3)], clock="T+01:20", clockLabel="THE BURST", clockRate=1,
  labels=[lb(TOWN, "PEOPLE WHO ARE NOT THE TARGET", W("p32", "people"), WHITE), lb(offp(BASCO, 0, 2.0), "HOW SMALL THE BURST IS", W("p32", "small"), YELLOW)])

# ================================================================== Chapter 06 [SIMULATION]
a = chapter("c6-card", S("p33"), 3.7, "CHAPTER 06", "The day after", "SIMULATION")
b = S("p34")
R("c6-back", a, b, [(a, [123.0, 24.0], 3000), (a + 4.0, [123.0, 24.0], 3800), (a + 8.0, BEI, 2800), (a + 12.0, [121.0, 22.0], 2400)], highlight=HL, legend=LEG, **DAY(6, "THE DAY AFTER"), countryLabels=CLS,
  cities=[mk(BASCO, "BASCO", a + 0.3, RED, "ring", 7), mk(BEI, "THE WEAPON IT PROMISED NOT TO USE FIRST", W("p33", "weapon"), RED, "target", 8)],
  labels=[lb([135.0, 16.0], "WHICH SIDE RUNS SHORT FIRST?", W("p33", "which"), YELLOW), lb([134.0, 19.0], "NOBODY HAS TO BE EMPTY", W("p33", "empty"), WHITE), lb([140.0, 22.0], "THE COUNTS NO LONGER DECIDE IT", W("p33", "counts"), YELLOW)])
a, b = b, W("p34", "That") - 0.2
R("c6-wind", a, b, [(a, BASCO, 240), (a + 3.0, [121.3, 20.0], 520), (b, [121.0, 19.6], 700)], highlight=HL, legend=LEG, clock="T+01:00:00", clockLabel="AFTER THE BURST", clockRate=0, burst={"at": BASCO, "t": a - 5, "km": 2, "fade": 12},
  lines=[ln(offp(BASCO, 70, 60 - 12 * i), offp(BASCO, 10, 5 - 12 * i), W("p34", "wind") + 0.2 * i, W("p34", "wind") + 1.5 + 0.2 * i, WHITE, "WIND FROM THE NORTH-EAST (ASSUMED)" if i == 1 else None, False, 2) for i in range(3)],
  cities=[mk(BASCO, "BURST", a + 0.2, RED, "target", 7)], caption="No one can forecast the real wind.", labels=[lb(offp(BASCO, 30, 40), "THE CLOUD FIRST", W("p34", "cloud"), WHITE)])
a, b = b, S("p35")
R("c6-sw", a, b, [(a, [120.6, 19.3], 800), (a + 3.0, [120.2, 18.3], 1000), (b, [120.2, 18.0], 1500)], highlight=HL, legend=LEG, clock="T+01:00:00", clockLabel="AFTER THE BURST", clockRate=0, countryLabels=[cl(PH, "PHILIPPINES", BLUE)],
  plume={"at": BASCO, "bearing": 225, "lengthKm": 220, "widthKm": 24, "t0": a + 0.3, "t1": a + 3.5, "color": AMBER, "label": "SMALL CLOUD, NOT A FORECAST"},
  labels=[lb(offp(LAO, 0, -90), "COAST OF NORTHERN LUZON", W("p34", "coast"), WHITE), lb(offp(BASCO, -170, -60), "OPEN SEA, NO DOSE GIVEN", W("p34", "dose"), YELLOW)], cities=[mk(LAO, "LAOAG", a + 1.0, WHITE, "dot", 5)])
a, b = S("p35"), S("p36")
R("c6-ships", a, b, [(a, [124.0, 19.0], 1400), (a + 4.0, [122.0, 17.0], 1100), (a + 8.0, [121.0, 16.0], 1500), (a + 12.0, SUB, 700), (b, SUB, 500)], highlight=HL, legend=LEG, **DAY(6, "THE DAY AFTER"),
  ships=[ship([[126.0, 21.5 - 0.7 * i], [123.0, 18.0 - 0.5 * i], [120.6, 15.2]], a + 0.3 + 0.4 * i, b, "us", BLUE, "US SHIPS TURN TOWARD PORT" if i == 0 else None, 22) for i in range(3)], cities=[mk(SUB, "SUBIC BAY", a + 0.4, BLUE, "base", 7)],
  labels=[lb([126.5, 13.5], "CANNOT RELOAD AT SEA", W("p35", "reload"), RED), lb([126.5, 11.8], "A SHIP RELOADING IS NOT ON THE LINE", W("p35", "line"), YELLOW), lb([126.5, 10.1], "THE PORT IS ALREADY A TARGET", W("p35", "port", 2), RED)])
a, b = S("p36"), S("p36") + 5.2
add(id="c6-years", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="1 TO 4 YEARS", label="to rebuild the stocks", sub="nothing changes at the factories this week", color=AMBER, source="CSIS; RUSI")
a, b = b, S("p37")
R("c6-neck", a, b, [(a, [-100.0, 38.0], 4600), (a + 3.5, [-100.0, 38.0], 3400), (a + 7.0, [110.0, 32.0], 4400), (b, [108.0, 33.0], 3300)], tag="REAL DATA", highlight=HL + [hl("840", BLUE, 0.07)], legend=[{"text": "US FACTORIES", "color": BLUE}, {"text": "CHINA", "color": AMBER}], source="CSIS; RUSI",
  labels=[lb([-110.0, 30.0], "ROCKET MOTORS", W("p36", "Rocket"), WHITE), lb([-110.0, 28.0], "GUIDANCE ELECTRONICS", W("p36", "guidance"), WHITE), lb([-110.0, 26.0], "ENERGETICS", W("p36", "energetics"), WHITE),
          lb([108.0, 40.0], "OVER 80% OF THE WORLD'S TUNGSTEN", W("p36", "eighty"), AMBER)])
a, b = S("p37"), W("p37", "In") - 0.2
R("c6-options", a, b, [(a, WAS, 2800), (a + 3.5, [122.0, 22.0], 2200), (a + 7.5, [122.0, 24.0], 2900), (a + 11.0, BEI, 2800)], highlight=HL + [hl("840", BLUE, 0.07)], legend=LEG, **DAY(6, "THE DECISION"), cities=[mk(WAS, "THE DECISION BELONGS TO WASHINGTON", a + 0.3, BLUE, "base", 8), mk(BASCO, "BASCO", a + 4.0, RED, "ring", 7), mk(BEI, "BEIJING", a + 11.2, AMBER, "dot", 7)],
  labels=[lb([128.0, 25.0], "OPTION 1: A LOW-YIELD REPLY, ABOUT 5 KT", W("p37", "low-yield"), RED), lb([128.0, 22.0], "OPTION 2: A CONVENTIONAL REPLY", W("p37", "conventional"), BLUE), lb([128.0, 36.0], "OPTION 3: A CALL", W("p37", "call"), TEAL)])
a = b
b = a + 3.7
stamp("c6-19nov", a, b, "19 NOVEMBER 2026", "Beijing's readout: it proposed a crisis communication channel", AMBER, "REAL DATA", source="Reports at the time; Beijing readout")
a, b = b, S("p38")
R("c6-stops", a, b, [(a, [122.0, 22.0], 2400), (b, [122.0, 22.0], 3000)], highlight=HL, legend=LEG, **DAY(6, "THE SIMULATION STOPS HERE"), countryLabels=CLS, cities=[mk(BASCO, "THE DECISION", a + 0.3, RED, "target", 8)])
a, b = S("p38"), S("p39")
R("c6-study", a, b, [(a, TPE, 1500), (a + 3.0, [121.0, 24.0], 2200), (a + 6.0, TPE, 1500), (b, [121.0, 24.0], 2000)], tag="REAL DATA", highlight=HL, legend=[{"text": "THE STUDY'S NUMBER, NOT OURS", "color": WHITE}], source="Bloomberg Economics", countryLabels=[cl(TW, "TAIWAN", TEAL)],
  labels=[lb([127.0, 26.5], "$10.6 TRILLION IN THE FIRST YEAR", W("p38", "ten"), AMBER), lb([127.0, 24.0], "A DIFFERENT WAR FROM OURS", W("p38", "different"), WHITE), lb([127.0, 21.5], "BLOOMBERG ECONOMICS", S("p38") + 0.3, WHITE)])
a, b = S("p39"), S("p40")
R("c6-ring", a, b, [(a, BASCO, 700), (a + 3.0, BASCO, 450), (a + 6.0, [121.0, 21.0], 1500), (b, [121.0, 21.0], 1100)], highlight=HL, legend=LEG, **DAY(6, "THE DAY AFTER"), rings=[rg(BASCO, 3.1, a + 0.3, TEAL, "1 PSI", False), rg(BASCO, 1.16, a + 0.6, RED, "5 PSI", False)],
  cities=[mk(BASCO, "A RING OVER A SMALL ISLAND", a + 0.2, RED, "ring", 8), mk(LAO, "LAUNCHERS STILL THERE", W("p39", "launchers"), BLUE, "base", 8)], labels=[lb([125.0, 22.5], "SO IS THE DECISION", W("p39", "decision"), YELLOW)])

# ------------------------------------------------------------------ End slate
add(id="end", type="endslate", start=round(S("p40"), 3), end=END, tag="", title="Next scenario", line="Russia and Japan: the Kuril Islands and Hokkaido, and a clash that could cross the nuclear line.")

# ------------------------------------------------------------------ audio plan and output
b0 = round(min(FL - 0.3, W("p02", "simulation") - 0.3), 2)
booms = [round(FL + 0.1, 2), round(S("p26") + 3.7 + 0.15, 2), round(S("p27") + 0.1, 2)]
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p16") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p16") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
    print(f"{s['id']:14} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
