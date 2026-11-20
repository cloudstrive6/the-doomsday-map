"""Director pass for episode 013: builds episode.json from narration/timing.json and words.json.

Run from the studio root:  python -m studio shotlist 013-taiwan-goes-dark
No strike and no flash: the payoff is the south of Taiwan going dark under the banner (moving region shots, dark discs
over lit cities), then real data and history, the hour-by-hour simulation with the loss spreading over minutes (never a
one-minute collapse), one fab shown step by step on a city map of Hsinchu, and the day after.
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




shots = []


def add(**k):
    shots.append(k)


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


def offp(base, dx, dy):
    return [round(base[0] + dx / (111.32 * math.cos(math.radians(base[1]))), 6), round(base[1] + dy / 110.57, 6)]


def disc(at, km, t, label=None, color="#07090E", op=0.88, **kw):
    pts = [offp(at, km * math.cos(math.radians(d)), km * math.sin(math.radians(d))) for d in range(0, 360, 6)]
    z = {"points": pts, "color": color, "t": t, "fillOpacity": op, "solid": True}
    z.update(kw)
    return z


# ------------------------------------------------------------------ places and colours (Taiwan teal, China amber, US/NATO blue)
TW_, CN_, UA_, DE_, US_, JP_ = "158", "156", "804", "276", "840", "392"


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


HL_TW, HL_CN, HL_UA, HL_DE, HL_US = hl(TW_, TEAL, 0.16), hl(CN_, AMBER, 0.07), hl(UA_, TEAL, 0.12), hl(DE_, BLUE, 0.10), hl(US_, BLUE, 0.08)
TW = [120.95, 23.7]
KHH, TNN, TXG, TPE, HSC = [120.30, 22.63], [120.21, 23.0], [120.68, 24.15], [121.56, 25.04], [120.97, 24.80]
HSN, NANKE, MATSU, HUA = [120.20, 22.85], [120.28, 23.10], [119.95, 26.16], [121.60, 23.98]
LNG_N, LNG_C, LNG_S = [121.04, 25.04], [120.50, 24.30], [120.19, 22.80]
KYIV, IVF, CHV, BER, WAS, BEI = [30.52, 50.45], [24.71, 48.92], [25.94, 48.29], [13.4, 52.5], [-77.04, 38.9], [116.4, 39.9]
CELLS = [("Kaohsiung", KHH), ("Tainan", TNN), ("Taichung", TXG), ("Taipei", TPE), ("Hsinchu", HSC)]
SRC_G = "Taipei Times, 4 Mar 2022; Focus Taiwan"
SRC_E = "Atlantic Council, Mar 2026; CSIS, May 2026"
LEG = [{"text": "TAIWAN", "color": TEAL}, {"text": "CHINA", "color": AMBER}]


def lit(a, names, t0, step=0.4):
    return [city(a, p, n, t0 + i * step, YELLOW) for i, (n, p) in enumerate(names)]


def CK(h, label="SIMULATED TIME"):
    return dict(clock=f"HOUR {h}", clockLabel=label, clockRate=0)


# ================================================================== Cold open [SIMULATION]
DK = 2.0
a = 0
glob("open-lit", 0, DK, [("s", 24.5, 124, 2600), ("e", 23.6, 121.5, 3600)], sun={"lat": 20, "lon": -60},
     markers=[{"at": KHH, "label": "Kaohsiung", "color": YELLOW, "kind": "dot", "t": 0.1}, {"at": TPE, "label": "Taipei", "color": YELLOW, "kind": "dot", "t": 1.0}],
     clock="21:00", clockLabel="LOCAL TIME", clockRate=0)
a = DK
reg("open-dark", a, S("p02"), [("s", [120.7, 23.2], 800), ("e", [120.7, 23.6], 560)], clock="21:00", clockLabel="LOCAL TIME", clockRate=12,
    highlight=[HL_TW], cities=lit(a, CELLS[:4], a - 1.9, 0.3) + [city(a, HSC, "Hsinchu: chip fabs", a + 2.2, YELLOW, "base", 6)],
    zones=[disc(KHH, 40, 0.15, "KAOHSIUNG: DARK"), disc(TNN, 36, 1.0), disc(TXG, 38, 2.0)],
    labels=[lab(a, [117.9, 23.6], "10 GW LOST", a + 0.3, WHITE), lab(a, [117.9, 23.1], "Breakers open", a + 1.1, YELLOW)])
a = S("p02")
tAnd = W("p02", "and")
reg("open-sim", a, tAnd, [("s", [121.0, 25.0], 2600), ("e", [121.0, 24.0], 1700)], clock="21:12", clockLabel="LOCAL TIME", clockRate=12,
    highlight=[HL_CN, HL_TW], countryLabels=[cl(CN_, "CHINA", AMBER), cl(TW_, "TAIWAN", TEAL)], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [124.8, 27.8], "A simulation", W("p02", "simulation"), YELLOW)])
a = tAnd
reg("open-nr", a, S("p03"), [("s", [121.0, 24.0], 1700), ("e", [120.9, 23.4], 1000)], clock="21:12", clockLabel="LOCAL TIME", clockRate=12,
    highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, TPE, "Taipei", a + 0.2, YELLOW), city(a, HSC, "Hsinchu", a + 0.8, YELLOW)],
    labels=[lab(a, [117.9, 22.6], "It has not happened", W("p02", "not"), WHITE)])
a = S("p03")
tA = W("p03", "A")
glob("open-night", a, tA, [("s", 24, 124, 2400), ("e", 23.6, 121, 3600)], tag="SIMULATION", sun={"lat": 20, "lon": -60},
     markers=[{"at": KHH, "label": "Kaohsiung", "color": YELLOW, "kind": "dot", "t": 1.2}, {"at": TPE, "label": "Taipei", "color": YELLOW, "kind": "dot", "t": 2.4}],
     caption="Thirty seconds earlier, every light on the island was on.")
a = tA
tTh = W("p03", "Then")
reg("open-summer", a, tTh, [("s", [120.95, 23.7], 800), ("e", [120.95, 24.2], 620)], clock="20:59", clockLabel="LOCAL TIME", clockRate=1,
    highlight=[HL_TW], cities=lit(a, CELLS, a + 0.2, 0.5),
    labels=[lab(a, [117.9, 24.9], "Summer evening", W("p03", "summer"), YELLOW), lab(a, [117.9, 24.4], "Air conditioners running", W("p03", "air"), WHITE)])
a = tTh
tNo = W("p03", "Nobody")
reg("open-kh", a, tNo, [("s", [120.4, 23.0], 280), ("e", [120.3, 22.7], 190)], clock="21:00", clockLabel="LOCAL TIME", clockRate=1,
    highlight=[HL_TW], cities=[city(a, KHH, "Kaohsiung", a + 0.2, YELLOW), city(a, HSN, "Hsinta substations", a + 0.9, WHITE, "base", 5)],
    labels=[lab(a, [120.0, 22.9], "Breakers begin to open", W("p03", "breakers"), YELLOW)], zones=[disc(HSN, 9, 1.6, "OPEN")])
a = tNo
reg("open-nobody", a, S("p04"), [("s", [120.3, 22.9], 260), ("e", [120.6, 23.4], 520)], clock="21:01", clockLabel="LOCAL TIME", clockRate=1,
    highlight=[HL_TW], cities=[city(a, KHH, "Kaohsiung", a + 0.1, YELLOW), city(a, HSN, "Hsinta", a + 0.5, WHITE, "base", 5)],
    zones=[disc(HSN, 9, 0.1), disc(KHH, 14, 1.0, "DARK")], labels=[lab(a, [119.9, 23.4], "Nobody touched them", W("p03", "touched"), WHITE)])
a = S("p04")
tAnd4, tIt = W("p04", "And"), W("p04", "It")
reg("open-fabs", a, tAnd4, [("s", [121.0, 24.2], 520), ("e", [121.0, 24.8], 330)], clock="22:00", clockLabel="END OF THE HOUR", clockRate=1,
    highlight=[HL_TW], cities=[city(a, HSC, "Hsinchu fabs", a + 0.4, YELLOW, "base", 6), city(a, TXG, "Taichung fabs", a + 1.8, YELLOW, "base", 5), city(a, TNN, "Tainan fabs", a + 3.4, YELLOW, "base", 5)],
    zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [118.5, 25.5], "Most advanced chips", W("p04", "most"), WHITE), lab(a, [118.5, 25.0], "In trouble", W("p04", "trouble"), YELLOW)])
a = tAnd4
reg("open-lights", a, tIt, [("s", [120.95, 23.7], 800), ("e", [120.95, 24.2], 600)], clock="22:00", clockLabel="END OF THE HOUR", clockRate=1,
    highlight=[HL_TW], cities=[city(a, TPE, "Taipei", a + 0.2, YELLOW)], zones=[disc(KHH, 48, 0.1), disc(TNN, 42, 0.1), disc(TXG, 46, 0.1)],
    labels=[lab(a, [117.9, 24.6], "Not: will the lights come back", W("p04", "whether"), WHITE)])
a = tIt
cty_id = "open-restart"
add(id=cty_id, type="city", start=a, end=S("p05"), tag="SIMULATION", city="hsinchu", view={"center": [120.99, 24.79], "widthKm": 60}, gz=HSC, rings=[],
    camera=[{"t": 0, "center": [120.99, 24.79], "widthKm": 60}, {"t": rel(a, W("p04", "start")), "center": [121.0, 24.78], "widthKm": 38}, {"t": round(S("p05") - a, 2), "center": [121.0, 24.78], "widthKm": 26}],
    labels=[lab(a, [120.99, 24.80], "Machines inside the fabs", W("p04", "machines"), YELLOW), lab(a, [120.99, 24.77], "How long to start again?", W("p04", "start"), WHITE)],
    clock="22:00", clockLabel="END OF THE HOUR", clockRate=0)

# ================================================================== Chapter 01 [REAL DATA] an island that cannot make its own power
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "An island that cannot make its own power", "REAL DATA")
tAb5, tRo = W("p05", "About"), round(W("p05", "Roughly") + 0.25, 2)
reg("c1-hsinta", a, tAb5, [("s", [120.4, 22.9], 330), ("e", [120.4, 23.0], 250)], tag="REAL DATA", source=SRC_G, clock="3 MAR 2022", clockLabel="THE BLACKOUT", clockRate=0,
    highlight=[HL_TW], cities=[city(a, HSN, "Hsinta power plant", a + 0.3, WHITE, "base", 6), city(a, KHH, "Kaohsiung", a + 1.0, YELLOW)],
    labels=[lab(a, [120.0, 23.3], "A switch fault", W("p05", "switch"), WHITE)], zones=[disc(HSN, 10, W("p05", "tripped") - a)])
a = tAb5
reg("c1-south", a, tRo, [("s", [120.6, 23.4], 560), ("e", [120.9, 23.9], 820)], tag="REAL DATA", source=SRC_G, clock="3 MAR 2022", clockLabel="THE BLACKOUT", clockRate=0,
    highlight=[HL_TW], cities=lit(a, CELLS[:3], a + 0.2, 0.4), zones=[disc(KHH, 44, 0.6), disc(TNN, 40, 1.4), disc(TXG, 38, 2.2)],
    labels=[lab(a, [118.0, 24.2], "5.5 million households", W("p05", "million"), YELLOW)])
a = tRo
num("c1-gw", a, S("p06"), "10.5 GW", countTo=10.5, decimals=1, suffix=" GW", label="of supply lost in the 2022 fault", sub="about 6 percent of national generation: one plant", color=YELLOW, tag="REAL DATA", source=SRC_G)
a = S("p06")
tEc = W("p06", "economics")
reg("c1-noatt", a, tEc, [("s", [120.9, 23.6], 800), ("e", [120.9, 23.4], 620)], tag="REAL DATA", source=SRC_G, clock="3 MAR 2022", clockLabel="THE CAUSE", clockRate=0,
    highlight=[HL_TW], zones=[disc(KHH, 44, 0.1), disc(TNN, 40, 0.1)],
    labels=[lab(a, [118.0, 24.4], "No one attacked anything", W("p06", "No"), YELLOW)])
a = tEc
reg("c1-err", a, S("p07"), [("s", [120.9, 23.4], 620), ("e", [121.0, 24.4], 900)], tag="REAL DATA", source=SRC_G, clock="3 MAR 2022", clockLabel="THE CAUSE", clockRate=0,
    highlight=[HL_TW], cities=[city(a, TPE, "Taipei: the minister", a + 0.3, WHITE)],
    labels=[lab(a, [118.0, 23.8], "Human error", W("p06", "human"), WHITE), lab(a, [118.0, 23.3], "A failed safeguard", W("p06", "failed"), YELLOW)])
a = S("p07")
tIn7, tWe = W("p07", "In"), W("p07", "ask")
reg("c1-size", a, tIn7, [("s", [120.95, 23.7], 900), ("e", [120.7, 23.2], 560)], clock="HOUR 0", clockLabel="OUR SIMULATION", clockRate=0,
    highlight=[HL_TW], zones=[disc(KHH, 40, 0.3, "THE BLACKOUT YOU SAW"), disc(TNN, 36, 0.6), disc(TXG, 38, 0.9)],
    labels=[lab(a, [118.0, 24.6], "The size of the blackout", W("p07", "size"), WHITE)])
a = tIn7
reg("c1-ch", a, tWe, [("s", [120.7, 23.2], 600), ("e", [121.0, 24.0], 900)], tag="SIMULATION", clock="HOUR 0", clockLabel="OUR SIMULATION", clockRate=0,
    highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [118.0, 24.6], "We chose a loss this big", W("p07", "chose"), YELLOW), lab(a, [118.0, 24.1], "As in the 2022 fault", W("p07", "2022"), WHITE)])
a = tWe
reg("c1-cause", a, S("p08"), [("s", [121.0, 24.0], 900), ("e", [121.5, 25.0], 2200)], tag="SIMULATION", clock="HOUR 0", clockLabel="OUR SIMULATION", clockRate=0,
    highlight=[HL_TW, HL_CN], countryLabels=[cl(CN_, "CHINA", AMBER)], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [117.0, 22.3], "What if the cause is not an accident?", W("p07", "not"), YELLOW)])
a = S("p08")
tGa = W("p08", "Almost")
reg("c1-import", a, tGa, [("s", [120.0, 22.0], 7000), ("e", [118.0, 22.0], 4200)], tag="REAL DATA", source="CSIS, May 2026", clock="", highlight=[HL_TW],
    countryLabels=[cl(TW_, "TAIWAN", TEAL)],
    ships=[ship(a, [[51.6, 25.9], [75, 8], [100, 3], [114, 14], [119, 21]], a + 0.2, a + 3.6, "Gas: Qatar", AMBER, "tanker", size=2.4),
           ship(a, [[114.0, -20.0], [117, -5], [120, 10], [121, 21]], a + 1.0, a + 3.8, "Gas: Australia", AMBER, "tanker", size=2.4)],
    labels=[lab(a, [133.0, 16.0], "96 percent imported", W("p08", "ninety-six"), YELLOW)])
a = tGa
tGs = W("p08", "Gas")
reg("c1-gas", a, tGs, [("s", [118.0, 22.0], 4200), ("e", [121.0, 23.5], 1600)], tag="REAL DATA", source="CSIS, May 2026", clock="", highlight=[HL_TW],
    cities=[city(a, LNG_S, "LNG terminals", a + 0.5, WHITE, "base", 5)],
    labels=[lab(a, [125.2, 27.0], "Almost all gas imported", a + 0.2, WHITE)])
a = tGs
tNu = W("p08", "since")
bars_a = a
add(id="c1-mix", type="bars", start=a, end=round(a + 3.9, 2), tag="REAL DATA", title="Taiwan's electricity, 2025", sub="share of generation, approximate", source=SRC_E,
    bars=[{"label": "Natural gas", "value": 48, "display": "nearly half", "color": TEAL}, {"label": "Coal", "value": 33, "display": "about a third", "color": GREY}, {"label": "Nuclear", "value": 0, "display": "none since May 2025", "color": YELLOW}])
a = round(a + 3.9, 2)
reg("c1-nonuke", a, S("p09"), [("s", [121.0, 23.7], 700), ("e", [121.0, 23.2], 520)], tag="REAL DATA", source=SRC_E, clock="", highlight=[HL_TW],
    cities=[city(a, [120.75, 21.95], "Maanshan: last reactor shut", a + 0.4, WHITE, "base", 5)],
    labels=[lab(a, [118.0, 24.4], "May 2025: last reactor off", a + 0.3, YELLOW)])
a = S("p09")
tRe = W("p09", "reserve")
reg("c1-coal", a, tRe, [("s", [120.8, 24.0], 1200), ("e", [120.6, 24.2], 800)], tag="REAL DATA", source=SRC_E, clock="", highlight=[HL_TW],
    cities=[city(a, TXG, "Taichung coal plant", a + 0.6, GREY, "base", 5)], labels=[lab(a, [118.0, 24.8], "Coal: about a third", W("p09", "third"), WHITE)])
a = tRe
add(id="c1-days", type="bars", start=a, end=round(a + 5.0, 2), tag="REAL DATA", title="Fuel in store, in days", sub="gas for the gas plants only, not electricity", source=SRC_E,
    bars=[{"label": "Natural gas", "value": 11, "display": "about 11", "color": TEAL}, {"label": "Coal", "value": 40, "display": "about 40", "color": GREY}, {"label": "Oil", "value": 140, "display": "about 140", "color": AMBER}])
a = round(a + 5.0, 2)
reg("c1-eleven", a, S("p10"), [("s", [121.0, 23.7], 900), ("e", [120.9, 24.2], 650)], tag="REAL DATA", source=SRC_E, clock="", highlight=[HL_TW],
    cities=[city(a, LNG_C, "Taichung LNG", a + 0.4, WHITE, "base", 5)], labels=[lab(a, [118.0, 24.8], "Gas is the short one", a + 0.3, YELLOW)])
a = S("p10")
tNs, tAt = W("p10", "two"), W("p10", "Attempts")
reg("c1-nsb", a, tNs, [("s", [119.0, 29.0], 2200), ("e", [120.0, 26.5], 1500)], tag="REAL DATA", source="National Security Bureau via Focus Taiwan; CyberScoop", clock="", highlight=[HL_TW, HL_CN], legend=LEG,
    cities=[city(a, TPE, "Taipei: NSB", a + 0.4, TEAL, "base", 5)],
    lines=[line(a, [118.5, 28.0], TPE, a + 1.0, a + 4.0, AMBER, True, "Cyber intrusion attempts")],
    labels=[lab(a, [124.6, 31.2], "National Security Bureau", W("p10", "National"), WHITE)])
a = tNs
num("c1-26", a, round(a + 3.6, 2), "2.6 MILLION", countTo=2.6, decimals=1, suffix=" MILLION", label="intrusion attempts a day on critical infrastructure, 2025", sub="Taiwan's own count of attempts", color=AMBER, tag="REAL DATA", source="National Security Bureau via Focus Taiwan; CyberScoop")
a = round(a + 3.6, 2)
reg("c1-attempts", a, S("p11"), [("s", [120.0, 26.5], 1500), ("e", [120.9, 24.5], 1100)], tag="REAL DATA", source="National Security Bureau via Focus Taiwan", clock="", highlight=[HL_TW, HL_CN], legend=LEG,
    labels=[lab(a, [124.0, 28.0], "Attempts, not breaches", W("p10", "breaches"), YELLOW), lab(a, [124.0, 27.2], "China denies it", W("p10", "denies"), AMBER)])
a = S("p11")
tNe = W("p11", "no")
reg("c1-none", a, S("p12"), [("s", [120.9, 23.7], 1000), ("e", [120.9, 24.0], 800)], tag="REAL DATA", source="Reuters; Focus Taiwan", clock="", highlight=[HL_TW],
    cities=lit(a, CELLS[:4], a + 0.3, 0.4),
    labels=[lab(a, [118.0, 25.4], "No public evidence", W("p11", "public"), WHITE), lab(a, [118.0, 24.1], "Nobody has switched it off", W("p11", "switched"), YELLOW)])
a = S("p12")
tSo = W("p12", "Someone")
reg("c1-how", a, tSo, [("s", [120.9, 23.9], 1000), ("e", [118, 30], 4000)], tag="REAL DATA", clock="", highlight=[HL_TW],
    labels=[lab(a, [117.0, 25.0], "How do you switch off a grid", W("p12", "grid"), WHITE), lab(a, [117.0, 24.5], "from a keyboard?", W("p12", "keyboard"), YELLOW)])
a = tSo
glob("c1-other", a, S("p13"), [("s", 30, 100, 1500), ("e", 48, 28, 2200)], tag="REAL DATA", sun={"lat": 25, "lon": 40}, highlight=[{"iso": UA_, "color": TEAL}],
     markers=[{"at": KYIV, "label": "Ukraine", "color": TEAL, "kind": "dot", "t": 2.0}], arcs=[{"from": TPE, "to": KYIV, "t0": 0.4, "t1": 3.8, "color": WHITE, "loft": 0.25}],
     caption="Someone already did, in another country.")

# ================================================================== Chapter 02 [REAL HISTORY] it has been done, and it was fast
SRC_U = "CISA alert IR-ALERT-H-16-056-01; MITRE ATT&CK"
a = chapter("c2-card", S("p13"), 3.5, "CHAPTER 02", "It has been done, and it was fast", "REAL HISTORY")
tAt13, tTh13 = W("p13", "attackers"), W("p13", "About")
reg("c2-ukr", a, tAt13, [("s", [27.0, 49.5], 1500), ("e", [25.5, 49.3], 900)], tag="REAL HISTORY", source=SRC_U, clock="23 DEC 2015", clockLabel="UKRAINE", clockRate=0,
    highlight=[HL_UA], countryLabels=[cl(UA_, "UKRAINE", TEAL)], cities=[city(a, KYIV, "Kyiv", a + 0.4, TEAL), city(a, IVF, "Ivano-Frankivsk", a + 1.0, TEAL)],
    labels=[lab(a, [20.0, 51.8], "Three regional power companies", W("p13", "three"), WHITE)])
a = tAt13
tNum13 = round(S("p14") - 3.8, 2)
reg("c2-open", a, tNum13, [("s", [26.5, 49.3], 1000), ("e", [27.5, 49.3], 1400)], tag="REAL HISTORY", source=SRC_U, clock="23 DEC 2015", clockLabel="UKRAINE", clockRate=0,
    highlight=[HL_UA], cities=[city(a, IVF, "Ivano-Frankivsk", a + 0.2, TEAL), city(a, CHV, "Chernivtsi", a + 0.8, TEAL), city(a, KYIV, "Kyiv", a + 1.4, TEAL)],
    zones=[disc(IVF, 40, W("p13", "opened") - a), disc(CHV, 35, W("p13", "opened") - a + 0.6), disc(KYIV, 45, W("p13", "opened") - a + 1.2)],
    labels=[lab(a, [20.0, 47.0], "Breakers opened by remote control", W("p13", "remote"), YELLOW)])
a = tNum13
num("c2-225", a, S("p14"), "225,000", countTo=225000, label="customers lost power", sub="23 December 2015", color=YELLOW, tag="REAL HISTORY", source=SRC_U)
a = S("p14")
tWi14, tOp = W("p14", "disabled"), W("p14", "Operators")
reg("c2-wipe", a, tWi14, [("s", [26.5, 49.3], 1300), ("e", [25.5, 49.0], 1000)], tag="REAL HISTORY", source=SRC_U, clock="", highlight=[HL_UA],
    cities=[city(a, IVF, "Control computers", a + 0.3, TEAL, "base", 5)], labels=[lab(a, [22.4, 50.0], "Control computers wiped", W("p14", "wiped"), YELLOW)])
a = tWi14
reg("c2-backup", a, tOp, [("s", [25.5, 49.0], 1000), ("e", [27.0, 49.3], 1300)], tag="REAL HISTORY", source=SRC_U, clock="", highlight=[HL_UA],
    cities=[city(a, IVF, "Backup power units", a + 0.3, TEAL, "base", 5)], labels=[lab(a, [22.4, 50.0], "Backup power disabled", a + 0.2, YELLOW), lab(a, [22.4, 49.5], "To slow the repair", W("p14", "slow"), WHITE)])
a = tOp
add(id="c2-hours", type="timeline", start=a, end=S("p15"), tag="REAL HISTORY", title="Lights back by hand", sub="restored by switching manually", source=SRC_U, total=6, unit="HOURS",
    segments=[{"from": 0, "to": 1, "label": "first back", "color": TEAL}, {"from": 1, "to": 6, "label": "the rest", "color": GREY}], highlight={"from": 1, "to": 6, "label": "ONE TO SIX HOURS"}, cursorTo=6)
a = S("p15")
tAb15, tGe = W("p15", "about"), W("p15", "Germany")
stamp("c2-feb", a, round(a + 2.4, 2), "24 FEBRUARY 2022", "An hour before the invasion", WHITE, tag="REAL HISTORY", source="MIT Technology Review; The Record")
a = round(a + 2.4, 2)
tArmy = W("p15", "army")
reg("c2-ka", a, tArmy, [("s", [31.0, 49.5], 1600), ("e", [30.5, 49.0], 1000)], tag="REAL HISTORY", source="MIT Technology Review; The Record", clock="24 FEB 2022", clockLabel="ABOUT AN HOUR BEFORE", clockRate=0,
    highlight=[HL_UA], countryLabels=[cl(UA_, "UKRAINE", TEAL)], cities=[city(a, KYIV, "Army links down", a + 0.8, TEAL)],
    labels=[lab(a, [24.0, 52.8], "KA-SAT modems bricked", W("p15", "bricked"), YELLOW), lab(a, [24.0, 52.3], "Wiper program", W("p15", "wiper"), WHITE)])
a = tArmy
reg("c2-army", a, tGe, [("s", [30.5, 49.0], 1000), ("e", [32.0, 49.0], 1500)], tag="REAL HISTORY", source="MIT Technology Review; The Record", clock="24 FEB 2022", clockLabel="UKRAINE", clockRate=0,
    highlight=[HL_UA], cities=[city(a, KYIV, "Army links down", a + 0.4, TEAL)], labels=[lab(a, [24.0, 52.8], "Ukraine's army lost communications", a + 0.3, WHITE)])
a = tGe
reg("c2-de", a, S("p16"), [("s", [10.5, 51.8], 1500), ("e", [11.0, 52.4], 1000)], tag="REAL HISTORY", source="MIT Technology Review; The Record", clock="24 FEB 2022", clockLabel="GERMANY", clockRate=0,
    highlight=[HL_DE], countryLabels=[cl(DE_, "GERMANY", BLUE)], cities=[city(a, BER, "Wind farms", a + 0.6, BLUE, "base", 5)],
    labels=[lab(a, [3.6, 54.6], "5,800 wind turbines cut off", W("p15", "fifty-eight"), WHITE), lab(a, [3.6, 54.0], "The turbines kept turning", W("p15", "kept"), YELLOW)])
a = S("p16")
tTa, tAn = W("p16", "repair"), W("p16", "strike")
reg("c2-pat", a, tTa, [("s", [26.0, 49.5], 1800), ("e", [24.0, 49.5], 1200)], tag="REAL HISTORY", source=SRC_U, clock="", highlight=[HL_UA],
    labels=[lab(a, [19.8, 52.3], "A pattern", a + 0.1, WHITE), lab(a, [19.8, 51.7], "1. Take the power", W("p16", "power"), YELLOW)])
a = tTa
reg("c2-pat2", a, S("p17"), [("s", [24.0, 49.5], 1200), ("e", [30, 50], 2200)], tag="REAL HISTORY", source=SRC_U, clock="", highlight=[HL_UA],
    labels=[lab(a, [19.8, 52.3], "2. Then the repair", a + 0.2, YELLOW), lab(a, [19.8, 51.7], "3. Strike early", W("p16", "early"), AMBER)])
a = S("p17")
tTs, tFa = W("p17", "virus"), W("p17", "Fabs")
reg("c2-tw18", a, tTs, [("s", [120.95, 23.9], 900), ("e", [120.95, 24.2], 700)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018; ITPro", clock="3 AUG 2018", clockLabel="TAIWAN", clockRate=0,
    highlight=[HL_TW], cities=[city(a, HSC, "TSMC Hsinchu", a + 0.4, TEAL, "base", 5)], labels=[lab(a, [118.0, 24.6], "A scare of its own", a + 0.3, WHITE)])
a = tTs
tTa17 = W("p17", "Tainan")
reg("c2-tool", a, tFa, [("s", [120.95, 24.2], 700), ("e", [120.95, 24.0], 600)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018; ITPro", clock="3 AUG 2018", clockLabel="TAIWAN", clockRate=0,
    highlight=[HL_TW], cities=[city(a, HSC, "Virus spreads", a + 0.3, YELLOW, "base", 5)], labels=[lab(a, [118.0, 24.6], "TSMC's network", W("p17", "network"), WHITE), lab(a, [118.0, 24.1], "A new tool, unscanned", W("p17", "tool"), YELLOW)])
a = tFa
tMo = W("p17", "most")
reg("c2-3fabs", a, tMo, [("s", [120.9, 24.0], 600), ("e", [120.8, 23.9], 700)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018; ITPro", clock="3 AUG 2018", clockLabel="TAIWAN", clockRate=0,
    highlight=[HL_TW], cities=[city(a, TNN, "Tainan fab", W("p17", "Tainan"), YELLOW, "base", 5), city(a, HSC, "Hsinchu fab", W("p17", "Hsinchu"), YELLOW, "base", 5), city(a, TXG, "Taichung fab", W("p17", "Taichung"), YELLOW, "base", 5)])
a = tMo
reg("c2-slow", a, W("p17", "said"), [("s", [120.4, 23.3], 400), ("e", [120.3, 23.1], 260)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018; ITPro", clock="3 AUG 2018", clockLabel="TAIWAN", clockRate=0,
    highlight=[HL_TW], cities=[city(a, NANKE, "Advanced fabs: slowest", a + 0.3, YELLOW, "base", 6)])
a = W("p17", "said")
reg("c2-protocol", a, S("p18"), [("s", [120.4, 23.1], 400), ("e", [120.9, 24.0], 1200)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018; ITPro", clock="3 AUG 2018", clockLabel="TAIWAN", clockRate=0,
    highlight=[HL_TW], labels=[lab(a, [118.0, 24.6], "TSMC: failure to follow protocol", a + 0.3, WHITE), lab(a, [118.0, 24.1], "Not an attack", W("p17", "attack"), YELLOW)])
a = S("p18")
tFb = W("p18", "fabs")
num("c2-2pct", a, round(a + 3.6, 2), "2%", countTo=2, suffix="%", label="of a quarter's revenue, TSMC's cost", sub="a mistake, not an attack", color=YELLOW, tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018")
a = round(a + 3.6, 2)
reg("c2-days", a, S("p19"), [("s", [120.9, 24.0], 1000), ("e", [120.9, 23.7], 700)], tag="REAL HISTORY", source="Taipei Times, 7 Aug 2018", clock="", highlight=[HL_TW],
    cities=lit(a, [("Hsinchu", HSC), ("Taichung", TXG), ("Tainan", TNN)], a + 0.2, 0.5), labels=[lab(a, [118.0, 24.6], "Running again within days", a + 0.2, TEAL), lab(a, [118.0, 24.1], "The benchmark for a mistake", W("p18", "benchmark"), WHITE)])
a = S("p19")
reg("c2-q", a, S("p20"), [("s", [118.0, 26.0], 2400), ("e", [120.9, 23.7], 1000)], tag="SIMULATION", clock="", highlight=[HL_TW, HL_CN], legend=LEG,
    labels=[lab(a, [123.2, 28.0], "A hostile attack", W("p19", "hostile"), AMBER), lab(a, [123.2, 27.4], "How would it begin?", W("p19", "begin"), WHITE)])

# ================================================================== Chapter 03 [SIMULATION] hour zero
a = chapter("c3-card", S("p20"), 3.5, "CHAPTER 03", "Hour zero", "SIMULATION")
tIn20, tAs = W("p20", "assume"), W("p20", "That")
reg("c3-inside", a, tIn20, [("s", [119.0, 25.5], 2200), ("e", [121.0, 24.0], 900)], clock="YEARS EARLIER", clockLabel="ASSUMED", clockRate=0, highlight=[HL_TW, HL_CN], legend=LEG,
    labels=[lab(a, [124.0, 27.8], "Attackers already inside", W("p20", "inside"), AMBER)])
a = tIn20
reg("c3-sleep", a, tAs, [("s", [121.0, 24.0], 900), ("e", [120.9, 23.6], 700)], clock="YEARS EARLIER", clockLabel="ASSUMED", clockRate=0, highlight=[HL_TW],
    cities=[city(a, TPE, "Taipower control", a + 0.4, AMBER, "base", 5), city(a, KHH, "Substations", a + 1.4, AMBER, "base", 5)],
    labels=[lab(a, [118.0, 24.6], "Placed years earlier, asleep", W("p20", "sleep"), YELLOW)])
a = tAs
reg("c3-assume", a, S("p21"), [("s", [120.9, 23.6], 700), ("e", [120.9, 24.0], 1000)], clock="", highlight=[HL_TW],
    labels=[lab(a, [118.0, 24.6], "An assumption, not a finding", a + 0.3, YELLOW)])
a = S("p21")
tT1, tT2, tT3, tT4 = W("p21", "Chinese"), W("p21", "communications"), W("p21", "crisis"), W("p21", "advisory")
VTS = "CISA, NSA, FBI advisory AA24-038A, 7 Feb 2024"
reg("c3-vt", a, tT1, [("s", [-98, 39], 6500), ("e", [-98, 39], 4500)], tag="REAL HISTORY", source=VTS, clock="2024", clockLabel="THE PRECEDENT", clockRate=0, highlight=[HL_US],
    countryLabels=[cl(US_, "UNITED STATES", BLUE)], cities=[city(a, WAS, "Washington", a + 0.5, BLUE)], labels=[lab(a, [-112.0, 26.0], "A precedent for the method", a + 0.3, WHITE)])
a = tT1
reg("c3-typh", a, tT2, [("s", [-98, 39], 4500), ("e", [-96, 38], 3600)], tag="REAL HISTORY", source=VTS, clock="2024", clockLabel="THE PRECEDENT", clockRate=0, highlight=[HL_US],
    lines=[line(a, BEI, WAS, a + 0.6, a + 3.0, AMBER, True, "Volt Typhoon")], labels=[lab(a, [-112.0, 28.5], "Energy", W("p21", "energy"), YELLOW)])
a = tT2
reg("c3-nets", a, tT3, [("s", [-96, 38], 3600), ("e", [-90, 37], 2800)], tag="REAL HISTORY", source=VTS, clock="2024", clockLabel="THE PRECEDENT", clockRate=0, highlight=[HL_US],
    labels=[lab(a, [-112.0, 28.5], "Communications", a + 0.2, WHITE), lab(a, [-112.0, 27.7], "Water", W("p21", "water"), BLUE)])
a = tT3
reg("c3-crisis", a, tT4, [("s", [-90, 37], 2800), ("e", [-80, 36], 2400)], tag="REAL HISTORY", source=VTS, clock="2024", clockLabel="THE PRECEDENT", clockRate=0, highlight=[HL_US],
    labels=[lab(a, [-110.0, 30.0], "To disrupt them in a crisis", a + 0.2, YELLOW)])
a = tT4
reg("c3-notw", a, S("p22"), [("s", [118.0, 26.0], 3000), ("e", [120.9, 24.0], 1100)], tag="REAL HISTORY", source=VTS, clock="2024", clockLabel="THE PRECEDENT", clockRate=0, highlight=[HL_TW, HL_US],
    labels=[lab(a, [124.5, 28.8], "The advisory does not name Taiwan", a + 0.4, WHITE)])
a = S("p22")
tDe = W("p22", "reserve")
reg("c3-summer", a, tDe, [("s", [120.9, 23.7], 900), ("e", [120.9, 24.0], 700)], clock="SUMMER EVENING", clockLabel="THE MOMENT", clockRate=0, highlight=[HL_TW],
    cities=lit(a, CELLS[:4], a + 0.3, 0.4), labels=[lab(a, [118.0, 24.6], "Chosen for harm", W("p22", "chosen"), YELLOW), lab(a, [118.0, 24.1], "Demand far above winter", W("p22", "demand"), WHITE)])
a = tDe
num("c3-7", a, round(a + 3.6, 2), "7%", countTo=7, suffix="%", label="night reserve margin in Taipower's own forecast", sub="summer evening", color=YELLOW, tag="REAL DATA", source="Taipei Times, 27 Jun 2026")
a = round(a + 3.6, 2)
reg("c3-thin", a, S("p23"), [("s", [120.9, 23.8], 800), ("e", [120.9, 23.5], 520)], clock="SUMMER EVENING", clockLabel="THE MOMENT", clockRate=0, highlight=[HL_TW],
    labels=[lab(a, [118.0, 24.6], "Almost no spare power", a + 0.3, WHITE)])
a = S("p23")
tMa, tGen, tLo = W("p23", "malicious"), W("p23", "Generating"), W("p23", "loss")
reg("c3-h0", a, tGen, [("s", [120.4, 23.2], 330), ("e", [120.4, 22.9], 230)], clock="T+00:00", clockLabel="HOUR ZERO", clockRate=20, highlight=[HL_TW],
    cities=[city(a, HSN, "Southern substations", a + 0.8, WHITE, "base", 5), city(a, KHH, "Kaohsiung", a + 1.5, YELLOW), city(a, TNN, "Tainan", a + 2.4, YELLOW)],
    labels=[lab(a, [119.95, 23.45], "Malicious commands", W("p23", "malicious"), AMBER), lab(a, [119.95, 23.2], "Breakers open", W("p23", "breakers"), YELLOW)], zones=[disc(HSN, 8, W("p23", "open") - a)])
a = tGen
reg("c3-trip", a, tLo, [("s", [120.4, 22.9], 230), ("e", [120.7, 23.4], 700)], clock="T+00:05", clockLabel="HOUR ZERO", clockRate=20, highlight=[HL_TW],
    zones=[disc(HSN, 12, 0.2, "UNITS TRIP"), disc(KHH, 18, 1.0), disc(TNN, 20, 1.8)], cities=[city(a, KHH, "Kaohsiung", a + 0.1, YELLOW)],
    labels=[lab(a, [119.5, 23.6], "Generating units trip behind them", W("p23", "units"), WHITE)])
a = tLo
reg("c3-10gw", a, S("p24"), [("s", [120.7, 23.4], 700), ("e", [120.9, 23.9], 1000)], clock="T+00:08", clockLabel="HOUR ZERO", clockRate=20, highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)], labels=[lab(a, [118.0, 24.4], "About 10 GW lost", W("p23", "ten"), WHITE), lab(a, [118.0, 23.9], "Our choice, not a forecast", W("p23", "forecast"), YELLOW)])
a = S("p24")
tTa24, tNo24 = W("p24", "Tainan"), W("p24", "north")
reg("c3-kh", a, tTa24, [("s", [120.4, 22.9], 400), ("e", [120.4, 22.8], 280)], clock="T+00:10", clockLabel="HOUR ZERO", clockRate=20, highlight=[HL_TW],
    cities=[city(a, KHH, "Kaohsiung first", a + 0.3, YELLOW)], zones=[disc(KHH, 40, W("p24", "goes") - a)], labels=[lab(a, [119.95, 23.1], "Kaohsiung goes first", W("p24", "Kaohsiung"), WHITE)])
a = tTa24
reg("c3-tn", a, tNo24, [("s", [120.4, 23.0], 450), ("e", [120.5, 23.6], 800)], clock="T+00:20", clockLabel="HOUR ZERO", clockRate=20, highlight=[HL_TW],
    cities=[city(a, TNN, "Tainan next", a + 0.3, YELLOW)], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.4)], labels=[lab(a, [119.4, 23.5], "Then Tainan", a + 0.2, WHITE)])
a = tNo24
reg("c3-north", a, S("p25"), [("s", [120.7, 23.9], 800), ("e", [121.2, 24.8], 600)], clock="T+00:35", clockLabel="THE DARK SPREADS", clockRate=20, highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1), disc(TXG, 36, 1.2), disc(HSC, 28, 3.0), disc(TPE, 30, 4.5)],
    labels=[lab(a, [118.0, 25.2], "City by city to the north", W("p24", "city"), YELLOW), lab(a, [118.0, 24.7], "The grid shakes itself apart", W("p24", "shakes"), WHITE)])
a = S("p25")
tSw = W("p25", "switch")
reg("c3-ops", a, tSw, [("s", [120.4, 22.95], 360), ("e", [120.4, 22.85], 250)], clock="T+00:40", clockLabel="OPERATORS", clockRate=20, highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1)], cities=[city(a, HSN, "Control room", a + 0.4, WHITE, "base", 5)], labels=[lab(a, [119.95, 23.2], "Remote controls: no answer", W("p25", "nothing"), YELLOW)])
a = tSw
reg("c3-hand", a, S("p26"), [("s", [120.4, 22.9], 250), ("e", [120.6, 23.3], 600)], clock="T+01:00", clockLabel="OPERATORS", clockRate=20, highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1)], cities=[city(a, HSN, "Switching by hand", a + 0.3, YELLOW, "base", 5)], labels=[lab(a, [119.4, 23.5], "As the Ukrainians did", W("p25", "Ukrainians"), WHITE), lab(a, [119.4, 23.2], "That is slow", W("p25", "slow"), YELLOW)])
a = S("p26")
reg("c3-next", a, S("p27"), [("s", [120.9, 23.8], 900), ("e", [120.9, 23.8], 1500)], clock="HOUR 1", clockLabel="THE NEXT 24 HOURS", clockRate=0, highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1), disc(TXG, 36, 0.1), disc(HSC, 28, 0.1)], labels=[lab(a, [118.0, 24.6], "The next 24 hours", W("p26", "twenty-four"), WHITE)])

# ================================================================== Chapter 04 [SIMULATION] the first day
a = chapter("c4-card", S("p27"), 3.5, "CHAPTER 04", "The first day", "SIMULATION")
tWi27, tSa, tCa = W("p27", "Wipers"), W("p27", "Satellite"), W("p27", "Call-centre")
reg("c4-wave", a, tSa, [("s", [120.9, 23.9], 900), ("e", [120.9, 24.2], 650)], **CK("1 TO 3", "SECOND WAVE"), highlight=[HL_TW, HL_CN], legend=LEG, countryLabels=[cl(CN_, "CHINA", AMBER)], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, TPE, "Control systems", a + 0.5, AMBER, "base", 5)], labels=[lab(a, [118.0, 24.8], "The second wave", a + 0.2, WHITE), lab(a, [118.0, 24.3], "Wipers corrupt controls", W("p27", "corrupt"), YELLOW)])
a = tSa
reg("c4-sat", a, tCa, [("s", [120.9, 24.2], 650), ("e", [120.9, 23.6], 800)], **CK("1 TO 3", "SECOND WAVE"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [118.0, 24.8], "Satellite backup terminals", W("p27", "terminals"), YELLOW), lab(a, [118.0, 24.3], "Knocked out, like KA-SAT", W("p27", "KA-SAT"), WHITE)])
a = tCa
reg("c4-calls", a, S("p28"), [("s", [120.9, 23.6], 800), ("e", [121.0, 24.9], 500)], **CK("1 TO 3", "SECOND WAVE"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, TPE, "Call centres flooded", a + 0.4, AMBER, "base", 5)], labels=[lab(a, [118.0, 24.6], "Crews cannot be dispatched", W("p27", "dispatched"), WHITE)])
a = S("p28")
tNum, tMa28, tReg, tIn28 = W("p28", "number"), W("p28", "Matsu"), W("p28", "regulator"), W("p28", "assumed")
CAB = [([121.83, 24.86], [128.0, 26.8]), ([120.65, 22.3], [114.2, 22.3]), ([121.4, 25.17], [118.1, 24.5])]
reg("c4-cables", a, tNum, [("s", [122.0, 24.8], 1700), ("e", [121.5, 24.5], 1100)], **CK("1 TO 3", "UNDERSEA CABLES"), highlight=[HL_TW, HL_CN],
    lines=[line(a, p, q, a + 0.3 + i * 1.0, a + 2.2 + i * 1.0, GREY, False, "Undersea cable") for i, (p, q) in enumerate(CAB)],
    ships=[ship(a, [[124.5, 27.5], [122.0, 25.4]], a + 0.4, a + 3.5, "Ship (simulated)", AMBER, "pla", size=2.4), ship(a, [[116.5, 22.0], [117.5, 22.5]], a + 1.0, a + 4.0, "Ship (simulated)", AMBER, "pla", size=2.4)],
    labels=[lab(a, [127.0, 22.5], "Two or three segments cut", W("p28", "Two"), YELLOW)])
a = tNum
reg("c4-disputed", a, tMa28, [("s", [121.5, 24.5], 1100), ("e", [120.5, 25.5], 800)], **CK("1 TO 3", "UNDERSEA CABLES"), highlight=[HL_TW, HL_CN], lines=[line(a, p, q, 0.1, 0.3, GREY, False) for p, q in CAB],
    labels=[lab(a, [127.0, 22.5], "We choose the number", a + 0.2, YELLOW), lab(a, [127.0, 21.9], "Real cases are disputed", W("p28", "disputed"), WHITE)])
a = tMa28
reg("c4-matsu", a, tReg, [("s", [120.2, 25.6], 450), ("e", [120.3, 25.9], 330)], tag="REAL HISTORY", source="Foreign Policy, 21 Feb 2023; The Diplomat", clock="2023", clockLabel="MATSU", clockRate=0, highlight=[HL_TW, HL_CN],
    cities=[city(a, MATSU, "Matsu Islands", a + 0.3, TEAL, "base", 6)], labels=[lab(a, [118.7, 26.3], "Two cables cut in a week", W("p28", "within"), WHITE)])
a = tReg
reg("c4-reg", a, tIn28, [("s", [120.3, 25.9], 330), ("e", [120.6, 25.2], 700)], tag="REAL HISTORY", source="Foreign Policy, 21 Feb 2023; The Diplomat", clock="2023", clockLabel="MATSU", clockRate=0, highlight=[HL_TW, HL_CN],
    cities=[city(a, MATSU, "Matsu Islands", a + 0.1, TEAL, "base", 6)], labels=[lab(a, [118.7, 26.3], "Regulator: no sign it was intentional", a + 0.3, YELLOW)])
a = tIn28
reg("c4-intent", a, S("p29"), [("s", [121.0, 24.4], 1100), ("e", [121.0, 24.3], 1700)], **CK("1 TO 3", "UNDERSEA CABLES"), highlight=[HL_TW, HL_CN],
    lines=[line(a, p, q, 0.1, 0.3, GREY, False) for p, q in CAB], labels=[lab(a, [127.0, 22.5], "Our simulation: intent assumed", a + 0.3, YELLOW)])
a = S("p29")
tPh = W("p29", "Phones")
reg("c4-reroute", a, tPh, [("s", [120.9, 24.0], 1000), ("e", [121.0, 24.0], 1500)], **CK("3", "THE LINKS LEFT"), highlight=[HL_TW],
    lines=[line(a, [121.83, 24.86], [128.0, 26.8], 0.2, 0.4, GREY, False), line(a, [120.65, 22.3], [114.2, 22.3], 0.2, 0.4, GREY, False), line(a, [121.4, 25.17], [118.1, 24.5], a + 0.5, a + 2.5, TEAL, False, "Reroute")],
    labels=[lab(a, [125.8, 22.5], "The internet slows, not dies", W("p29", "slows"), TEAL)])
a = tPh
reg("c4-towers", a, S("p30"), [("s", [120.9, 24.0], 800), ("e", [120.9, 23.7], 600)], **CK("3", "THE WEAK POINT"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1), disc(TXG, 36, 0.1)],
    cities=[city(a, TXG, "Cell towers on the dark grid", a + 0.4, WHITE, "base", 5)], labels=[lab(a, [118.0, 24.6], "Phones are the weak point", a + 0.3, YELLOW)])
a = S("p30")
tSo30 = W("p30", "south")
reg("c4-h6", a, tSo30, [("s", [121.2, 24.6], 650), ("e", [121.0, 24.4], 800)], **CK("6", "MANUAL SWITCHING"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, TPE, "North: half restored", a + 0.3, TEAL)], labels=[lab(a, [118.0, 25.3], "About half back in the north", W("p30", "half"), TEAL)])
a = tSo30
reg("c4-h6s", a, S("p31"), [("s", [120.7, 23.2], 600), ("e", [120.5, 22.9], 400)], **CK("6", "ROTATING CUTS"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [118.4, 23.8], "The south: rotating cuts", a + 0.3, YELLOW)])
a = S("p31")
tFu = W("p31", "Fuel")
reg("c4-h12", a, tFu, [("s", [120.9, 23.7], 900), ("e", [121.0, 24.8], 500)], **CK("12", "HOSPITALS AND WATER"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, TPE, "Hospitals", a + 0.5, WHITE, "base", 5), city(a, TXG, "Water pumps", a + 1.8, WHITE, "base", 5)], labels=[lab(a, [118.0, 24.9], "On diesel", W("p31", "diesel"), YELLOW)])
a = tFu
reg("c4-road", a, S("p32"), [("s", [121.0, 24.8], 500), ("e", [120.9, 24.0], 1000)], **CK("12", "FUEL AND ROADS"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    cities=[city(a, KHH, "Fuel depot", a + 0.4, WHITE, "base", 5), city(a, TPE, "Hospital", a + 0.8, WHITE, "base", 5)],
    lines=[line(a, KHH, TNN, W("p31", "truck"), W("p31", "truck") + 1.5, TEAL, True, "Fuel truck"), line(a, TNN, TXG, W("p31", "truck") + 1.5, W("p31", "truck") + 3.0, TEAL, True), line(a, TXG, TPE, W("p31", "road"), W("p31", "road") + 2.0, TEAL, True)],
    labels=[lab(a, [118.0, 24.9], "A truck needs a road", W("p31", "road"), WHITE), lab(a, [118.0, 24.4], "A phone, a working signal", W("p31", "signal"), YELLOW)])
a = S("p32")
tOur, tThe, tEl = W("p32", "terminals"), W("p32", "untouched"), W("p32", "eleven")
reg("c4-clock", a, tOur, [("s", [120.9, 23.9], 1000), ("e", [120.9, 23.8], 700)], **CK("12", "THE CLOCK"), highlight=[HL_TW],
    cities=[city(a, LNG_N, "LNG: Guantang", a + 1.2, WHITE, "base", 5), city(a, LNG_C, "LNG: Taichung", a + 2.2, WHITE, "base", 5)],
    labels=[lab(a, [118.0, 24.8], "And here is the clock", a + 0.3, YELLOW)])
a = tOur
reg("c4-lng", a, tThe, [("s", [120.9, 24.0], 750), ("e", [120.8, 23.7], 600)], **CK("12", "GAS TERMINALS"), highlight=[HL_TW],
    cities=[city(a, LNG_N, "LNG: Guantang", a + 0.4, WHITE, "base", 5), city(a, LNG_C, "LNG: Taichung", a + 1.2, WHITE, "base", 5), city(a, LNG_S, "LNG: Yung-An", a + 2.0, WHITE, "base", 5)],
    zones=[disc(LNG_N, 12, 3.0), disc(LNG_C, 12, 3.3), disc(LNG_S, 12, 3.6)],
    labels=[lab(a, [118.2, 24.8], "Terminals stall", W("p32", "stall"), YELLOW), lab(a, [118.2, 24.3], "No power, no controls", W("p32", "lack"), WHITE)])
a = tThe
reg("c4-untouched", a, tEl, [("s", [120.8, 23.7], 600), ("e", [120.9, 23.9], 900)], **CK("12", "THE CLOCK"), highlight=[HL_TW],
    cities=[city(a, LNG_C, "Gas itself untouched", a + 0.3, WHITE, "base", 5)], labels=[lab(a, [118.0, 24.8], "The gas itself is untouched", a + 0.2, WHITE)])
a = tEl
add(id="c4-11", type="timeline", start=a, end=round(a + 3.9, 2), tag="SIMULATION", title="The gas clock", sub="about eleven days in store: our assumption that terminals stall", total=11, unit="DAYS",
    segments=[{"from": 0, "to": 11, "label": "gas in store", "color": TEAL}], highlight={"from": 0, "to": 11, "label": "ABOUT 11 DAYS"}, cursorTo=11)
a = round(a + 3.9, 2)
reg("c4-cannot", a, S("p33"), [("s", [120.9, 23.9], 900), ("e", [120.5, 24.0], 600)], **CK("12", "THE CLOCK"), highlight=[HL_TW],
    cities=[city(a, LNG_C, "Gas stuck at the terminals", a + 0.3, WHITE, "base", 5)], labels=[lab(a, [118.0, 24.8], "It cannot burn what it cannot move", W("p32", "burn"), YELLOW), lab(a, [118.0, 24.3], "Our assumption, not a finding", W("p32", "assumption"), WHITE)])
a = S("p33")
tIn33, tCp = W("p33", "ransomware"), W("p33", "gas")
reg("c4-d2", a, tIn33, [("s", [120.9, 23.9], 900), ("e", [120.9, 24.2], 700)], **CK("DAY 2 TO 3", "ROTATING CUTS"), highlight=[HL_TW], zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)],
    labels=[lab(a, [118.0, 24.8], "Rotating cuts continue", a + 0.3, YELLOW), lab(a, [118.0, 24.3], "Card payments degrade", W("p33", "payments"), WHITE)])
a = tIn33
reg("c4-cpc", a, S("p34"), [("s", [120.9, 23.9], 1000), ("e", [121.0, 24.4], 700)], tag="REAL HISTORY", source="CFR; CyberScoop, May 2020", clock="2020", clockLabel="CPC RANSOMWARE", clockRate=0, highlight=[HL_TW],
    cities=[city(a, KHH, "CPC gas stations", a + 0.4, TEAL, "base", 5)], labels=[lab(a, [118.0, 24.6], "Ransomware at state oil firm CPC", a + 0.3, WHITE), lab(a, [118.0, 24.1], "Card payments knocked out", tCp, YELLOW)])
a = S("p34")
tTh34 = W("p34", "pieces")
reg("c4-d4", a, tTh34, [("s", [120.7, 23.3], 700), ("e", [121.0, 24.0], 1000)], **CK("DAY 4 TO 7", "POWER RETURNS"), highlight=[HL_TW],
    zones=[disc(KHH, 40, 0.1), disc(TNN, 36, 0.1)], cities=[city(a, TPE, "Lights back", a + 0.4, TEAL), city(a, TXG, "Lights back", a + 1.2, TEAL)], labels=[lab(a, [118.0, 24.6], "Day four to seven", a + 0.2, WHITE)])
a = tTh34
reg("c4-pieces", a, S("p35"), [("s", [121.0, 24.2], 1000), ("e", [120.9, 24.6], 600)], **CK("DAY 4 TO 7", "POWER RETURNS"), highlight=[HL_TW],
    cities=[city(a, HSC, "Fabs: reduced output, not zero", a + 0.4, YELLOW, "base", 6)], labels=[lab(a, [118.0, 24.6], "Power returns in pieces", a + 0.2, TEAL)])
a = S("p35")
tLe = W("p35", "Let")
reg("c4-why", a, tLe, [("s", [120.9, 24.2], 800), ("e", [120.95, 24.7], 330)], **CK("DAY 7", "THE SLOWEST TO RECOVER"), highlight=[HL_TW],
    cities=[city(a, HSC, "Fabs", a + 0.4, YELLOW, "base", 6)], labels=[lab(a, [118.0, 25.0], "Why are the fabs slowest?", W("p35", "fabs"), WHITE)])
a = tLe
add(id="c4-look", type="city", start=a, end=S("p36"), tag="SIMULATION", city="hsinchu", view={"center": [120.99, 24.79], "widthKm": 70}, gz=HSC, rings=[],
    camera=[{"t": 0, "center": [120.99, 24.79], "widthKm": 70}, {"t": round(S("p36") - a, 2), "center": [121.0, 24.78], "widthKm": 36}],
    labels=[lab(a, [120.99, 24.82], "Hsinchu Science Park", a + 0.4, YELLOW)], clock="DAY 7", clockLabel="LOOK CLOSER", clockRate=0)

# ================================================================== Chapter 05 [SIMULATION] one voltage dip, step by step
a = chapter("c5-card", S("p36"), 3.5, "CHAPTER 05", "One voltage dip, step by step", "SIMULATION")
tTs36 = W("p36", "run")
cty5 = lambda sid, a, b, keys, labels, tag="SIMULATION", **kw: add(id=sid, type="city", start=a, end=b, tag=tag, city="hsinchu", view={"center": keys[0][1], "widthKm": keys[0][2]}, gz=HSC, rings=[],
                                                                camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "center": c, "widthKm": w} for t, c, w in keys], labels=labels, **kw)
cty5("h5-take", a, S("p37"), [("s", [120.99, 24.79], 60), ("e", [121.0, 24.78], 30)], [lab(a, [120.975, 24.80], "Hsinchu: TSMC and other fabs", W("p36", "Hsinchu"), WHITE)], clock="", clockRate=0)
a = S("p37")
tAp, tSp = W("p37", "In"), W("p37", "split-second")
reg("h5-1", a, tAp, [("s", [121.0, 24.8], 300), ("e", [120.5, 24.0], 600)], **CK("0", "STEP ONE"), highlight=[HL_TW, HL_CN], legend=LEG, countryLabels=[cl(CN_, "CHINA", AMBER)], labels=[lab(a, [118.0, 25.2], "Step one: a dip", a + 0.2, YELLOW), lab(a, [118.0, 24.7], "A fraction of a second", W("p37", "fraction"), WHITE)])
a = tAp
reg("h5-nanke", a, tSp, [("s", [120.4, 23.2], 400), ("e", [120.3, 23.1], 250)], tag="REAL HISTORY", source="TrendForce, 15 Apr 2021", clock="APRIL 2021", clockLabel="NAN-KE, TAINAN", clockRate=0, highlight=[HL_TW],
    cities=[city(a, NANKE, "TSMC Nan-ke", a + 0.3, TEAL, "base", 6)], labels=[lab(a, [119.6, 23.5], "A sudden voltage drop", W("p37", "voltage"), WHITE), lab(a, [119.6, 23.35], "Backup took over", W("p37", "backup"), YELLOW)])
a = tSp
cty5("h5-scrap", a, S("p38"), [("s", [120.99, 24.79], 50), ("e", [121.0, 24.78], 28)], [lab(a, [120.99, 24.80], "Wafers in process: scrapped", a + 0.3, YELLOW)], tag="REAL HISTORY", source="TrendForce, 15 Apr 2021", clock="APRIL 2021", clockLabel="A SPLIT SECOND", clockRate=0)
a = S("p38")
tIn38, tBk = W("p38", "In", 2), W("p38", "carry")
reg("h5-2", a, tIn38, [("s", [121.0, 24.8], 400), ("e", [121.0, 24.8], 220)], **CK("0", "STEP TWO"), highlight=[HL_TW], cities=[city(a, HSC, "Backups carry the load", a + 0.4, TEAL, "base", 6)],
    labels=[lab(a, [119.8, 25.2], "Step two: backups take over", a + 0.2, YELLOW)])
a = tIn38
cty5("h5-2b", a, S("p39"), [("s", [120.99, 24.79], 40), ("e", [121.0, 24.78], 24)], [lab(a, [120.99, 24.80], "Our simulation: backups alone", W("p38", "alone"), YELLOW)], clock="HOUR 0", clockLabel="THE DIP COMES WITH THE BLACKOUT", clockRate=0)
a = S("p39")
tTo, tRs = W("p39", "intact"), W("p39", "restart")
cty5("h5-3", a, tTo, [("s", [120.99, 24.79], 45), ("e", [121.0, 24.78], 30)], [lab(a, [120.99, 24.80], "Step three: power back", a + 0.2, TEAL), lab(a, [120.99, 24.78], "Network not", W("p39", "network"), YELLOW)], clock="DAY 4", clockLabel="STEP THREE", clockRate=0)
a = tTo
cty5("h5-tools", a, tRs, [("s", [121.0, 24.78], 30), ("e", [121.0, 24.78], 20)], [lab(a, [120.99, 24.795], "Tools intact", W("p39", "intact"), TEAL), lab(a, [120.99, 24.78], "Control systems corrupted", W("p39", "corrupted"), YELLOW)], clock="DAY 4", clockLabel="STEP THREE", clockRate=0)
a = tRs
reg("h5-net", a, S("p40"), [("s", [121.0, 24.8], 220), ("e", [120.9, 24.0], 900)], **CK("DAY 4", "THE RESTART"), highlight=[HL_TW], labels=[lab(a, [118.4, 25.2], "Set by the network, not the grid", a + 0.3, YELLOW)])
a = S("p40")
tAf, tSt = W("p40", "earthquake"), W("p40", "TSMC")
reg("h5-4", a, tAf, [("s", [121.0, 24.8], 600), ("e", [121.2, 24.3], 800)], **CK("0", "STEP FOUR"), highlight=[HL_TW], labels=[lab(a, [118.0, 25.0], "Step four: clean network", a + 0.2, YELLOW), lab(a, [118.0, 24.5], "Intact tools", W("p40", "intact"), WHITE)])
a = tAf
reg("h5-quake", a, tSt, [("s", [121.6, 24.0], 450), ("e", [121.2, 24.4], 900)], tag="REAL HISTORY", source="Focus Taiwan, 4 Apr 2024; CNBC", clock="3 APR 2024", clockLabel="HUALIEN EARTHQUAKE", clockRate=0, highlight=[HL_TW],
    cities=[city(a, HUA, "Hualien epicentre", a + 0.3, WHITE, "target", 5), city(a, HSC, "TSMC", a + 1.8, TEAL, "base", 5)], labels=[lab(a, [118.8, 24.2], "April 2024", a + 0.3, WHITE)])
a = tSt
num("c5-70", a, round(a + 3.6, 2), "70%+", countTo=70, suffix="%+", label="of TSMC's machines back by the end of the same day", sub="after the April 2024 earthquake", color=TEAL, tag="REAL HISTORY", source="Focus Taiwan, 4 Apr 2024; CNBC")
a = round(a + 3.6, 2)
reg("h5-fast", a, S("p41"), [("s", [121.0, 24.4], 900), ("e", [121.0, 24.8], 500)], tag="REAL HISTORY", source="Focus Taiwan, 4 Apr 2024; CNBC", clock="3 APR 2024", clockLabel="HOURS", clockRate=0, highlight=[HL_TW],
    cities=[city(a, HSC, "Back within hours", a + 0.4, TEAL, "base", 6)], labels=[lab(a, [118.0, 25.2], "Fast: tools and network intact", a + 0.3, WHITE)])
a = S("p41")
tNo41, tDa = W("p41", "not"), W("p41", "days")
reg("h5-dirty", a, tNo41, [("s", [121.0, 24.8], 400), ("e", [121.0, 24.8], 260)], **CK("DAY 4", "OUR SIMULATION"), highlight=[HL_TW], cities=[city(a, HSC, "Networks not clean", a + 0.5, AMBER, "base", 6)],
    labels=[lab(a, [119.6, 25.2], "In our simulation", a + 0.2, YELLOW)])
a = tNo41
reg("h5-2018", a, S("p42"), [("s", [121.0, 24.8], 260), ("e", [120.5, 24.0], 800)], **CK("DAY 4", "OUR SIMULATION"), highlight=[HL_TW], labels=[lab(a, [118.0, 25.3], "Closer to 2018 than 2024", W("p41", "closer"), WHITE), lab(a, [118.0, 24.8], "Days, not hours", tDa, YELLOW)])
a = S("p42")
tWa = W("p42", "wafers")
reg("h5-none", a, S("p43"), [("s", [120.9, 24.0], 900), ("e", [120.9, 24.3], 600)], **CK("DAY 4", "OUR SIMULATION"), highlight=[HL_TW], labels=[lab(a, [118.0, 24.8], "No count of wafers lost", tWa, WHITE), lab(a, [118.0, 24.3], "No source supports one", W("p42", "source"), YELLOW)])
a = S("p43")
tAb43 = W("p43", "about")
glob("h5-world", a, tAb43, [("s", 25, 121, 3200), ("e", 20, 140, 1500)], sun={"lat": 15, "lon": 40}, markers=[{"at": HSC, "label": "Hsinchu", "color": YELLOW, "kind": "dot", "t": 0.5}],
     arcs=[{"from": HSC, "to": [-122.0, 37.4], "t0": 1.0, "t1": 4.2, "color": TEAL, "loft": 0.35}, {"from": HSC, "to": [8.0, 50.0], "t0": 1.6, "t1": 4.8, "color": TEAL, "loft": 0.3}],
     caption="Most of the world's most advanced chips.")
a = tAb43
add(id="h5-share", type="bars", start=a, end=round(a + 4.6, 2), tag="REAL DATA", title="Share of the most advanced chips made in Taiwan", sub="two counts, depending on who counts", source="Bloomberg Economics, Feb 2026; Rhodium Group, Dec 2022",
    bars=[{"label": "Bloomberg Economics", "value": 62, "display": "62%", "color": TEAL}, {"label": "Rhodium Group", "value": 92, "display": "92%", "color": TEAL}])

a = round(a + 4.6, 2)
reg("h5-who", a, S("p44"), [("s", [120.9, 24.0], 1100), ("e", [120.9, 24.2], 700)], tag="REAL DATA", source="Bloomberg Economics, Feb 2026; Rhodium Group, Dec 2022", clock="", highlight=[HL_TW],
    cities=[city(a, HSC, "Taiwan's fabs", a + 0.3, TEAL, "base", 6)], labels=[lab(a, [118.0, 24.8], "62 percent by one count", a + 0.2, WHITE), lab(a, [118.0, 24.3], "92 percent by another", a + 1.4, YELLOW)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p44"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
tBy, tTh44 = W("p44", "By"), W("p44", "south")
reg("c6-patch", a, tBy, [("s", [120.9, 23.7], 900), ("e", [120.9, 23.9], 760)], clock="DAY 4", clockLabel="THE PATCHWORK", clockRate=0, highlight=[HL_TW, HL_CN], legend=LEG, countryLabels=[cl(CN_, "CHINA", AMBER)],
    labels=[lab(a, [118.0, 24.8], "Can the lights come back?", W("p44", "lights"), WHITE)])
a = tBy
reg("c6-north", a, tTh44, [("s", [121.0, 24.6], 650), ("e", [121.0, 24.9], 500)], clock="DAY 4", clockLabel="THE PATCHWORK", clockRate=0, highlight=[HL_TW],
    cities=[city(a, TPE, "Taipei", a + 0.3, YELLOW), city(a, HSC, "Hsinchu", a + 0.7, YELLOW), city(a, TXG, "Taichung", a + 1.1, YELLOW)], labels=[lab(a, [118.0, 25.4], "The north glows", W("p44", "north"), YELLOW)])
a = tTh44
reg("c6-south", a, S("p45"), [("s", [120.7, 23.2], 600), ("e", [120.6, 22.9], 420)], clock="DAY 4", clockLabel="THE PATCHWORK", clockRate=0, highlight=[HL_TW],
    cities=[city(a, KHH, "Kaohsiung", a + 0.2, YELLOW), city(a, TNN, "Tainan", a + 0.8, YELLOW)], zones=[disc(KHH, 8, 1.0), disc(TNN, 7, 1.8), disc(offp(KHH, 8, -3), 6, 2.6)],
    labels=[lab(a, [119.1, 23.5], "The south flickers", W("p44", "flickers"), WHITE), lab(a, [119.1, 23.2], "Block by block", W("p44", "block"), YELLOW)])
a = S("p45")
tRa = W("p45", "Rail")
reg("c6-lights", a, tRa, [("s", [120.3, 22.7], 260), ("e", [120.3, 22.65], 170)], clock="DAY 4", clockLabel="DARK BLOCKS", clockRate=0, highlight=[HL_TW],
    zones=[disc(KHH, 6, 0.2), disc(offp(KHH, 4, 3), 5, 0.6)], labels=[lab(a, [119.95, 22.9], "Traffic lights stay off", W("p45", "traffic"), WHITE)])
a = tRa
reg("c6-rail", a, S("p46"), [("s", [120.8, 24.0], 700), ("e", [121.0, 24.4], 1000)], clock="DAY 4", clockLabel="RAIL", clockRate=0, highlight=[HL_TW],
    lines=[line(a, KHH, TNN, a + 0.4, a + 1.4, TEAL, False, "Rail runs in sections"), line(a, TXG, HSC, a + 1.8, a + 2.8, TEAL, False), line(a, HSC, TPE, a + 3.0, a + 4.0, TEAL, False)],
    labels=[lab(a, [118.0, 25.0], "What would the operator choose?", W("p45", "choose"), YELLOW)])
a = S("p46")
tIs, tShips = W("p46", "Not"), W("p46", "Ships")
reg("c6-cut", a, tShips, [("s", [120.9, 23.8], 1300), ("e", [121.0, 24.0], 1000)], clock="DAY 4", clockLabel="NOT CUT OFF", clockRate=0, highlight=[HL_TW], labels=[lab(a, [118.0, 24.8], "Is the island cut off?", a + 0.2, WHITE), lab(a, [118.0, 24.3], "Not quite", tIs, YELLOW)])
a = tShips
tBy2 = W("p46", "terminals")
reg("c6-ships", a, tBy2, [("s", [121.0, 23.2], 1300), ("e", [121.0, 23.0], 1100)], clock="DAY 4", clockLabel="SHIPS STILL ARRIVE", clockRate=0, highlight=[HL_TW],
    ships=[ship(a, [[125.5, 22.0], [121.9, 22.8]], a + 0.2, a + 3.5, "Cargo", TEAL, "cargo", size=2.2), ship(a, [[118.0, 21.0], [120.0, 22.4]], a + 1.0, a + 4.2, "LNG tanker", TEAL, "tanker", size=2.2)],
    labels=[lab(a, [124.0, 25.2], "Ships still arrive", a + 0.2, WHITE)])
a = tBy2
tCa46 = W("p46", "cables")
reg("c6-gasclock", a, tCa46, [("s", [121.0, 23.5], 1100), ("e", [121.0, 23.7], 900)], **CK("DAY 4", "THE GAS CLOCK STOPS"), highlight=[HL_TW], cities=[city(a, LNG_C, "Terminals assumed back on", a + 0.3, TEAL, "base", 5)],
    labels=[lab(a, [118.0, 24.8], "The gas clock stops", a + 0.4, YELLOW)])
a = tCa46
tLive = W("p46", "lives")
reg("c6-cables", a, tLive, [("s", [121.5, 24.5], 1300), ("e", [121.0, 25.0], 800)], tag="REAL HISTORY", source="Foreign Policy, 21 Feb 2023", clock="2023", clockLabel="MATSU REPAIRS", clockRate=0, highlight=[HL_TW, HL_CN],
    cities=[city(a, MATSU, "Matsu repairs: weeks to months", a + 0.4, TEAL, "base", 5)], lines=[line(a, [121.83, 24.86], [128.0, 26.8], 0.2, 0.4, GREY, False, "Cable")],
    labels=[lab(a, [118.0, 23.5], "The cables are the problem", a + 0.3, YELLOW)])
a = tLive
reg("c6-links", a, S("p47"), [("s", [121.0, 25.0], 800), ("e", [121.0, 24.2], 1300)], clock="DAY 4", clockLabel="WHAT IS LEFT", clockRate=0, highlight=[HL_TW],
    labels=[lab(a, [118.0, 24.8], "The island lives on what is left", a + 0.3, WHITE)])
a = S("p47")
tLe47, tOn = W("p47", "Leading-edge"), W("p47", "One")
glob("c6-chips", a, tLe47, [("s", 28, 121, 3000), ("e", 20, 140, 1700)], sun={"lat": 15, "lon": 40}, markers=[{"at": HSC, "label": "Hsinchu", "color": YELLOW, "kind": "dot", "t": 0.4}],
     arcs=[{"from": HSC, "to": [-122.0, 37.4], "t0": 1.0, "t1": 3.2, "color": TEAL, "loft": 0.35}], caption="Where do the chips stop?")
a = tLe47
tOn47 = W("p47", "One")
glob("c6-late", a, tOn47, [("s", 20, 140, 1700), ("e", 30, 40, 1500)], sun={"lat": 15, "lon": 40},
     markers=[{"at": [-122.0, 37.4], "label": "Phones", "color": WHITE, "kind": "dot", "t": 0.8}, {"at": [10.0, 49.0], "label": "Cars", "color": WHITE, "kind": "dot", "t": 1.6}, {"at": [-96.0, 33.0], "label": "Servers", "color": WHITE, "kind": "dot", "t": 2.4}],
     arcs=[{"from": HSC, "to": [-122.0, 37.4], "t0": 0.1, "t1": 0.4, "color": GREY, "loft": 0.35}], caption="Chips for phones, cars and servers are delayed.")
a = tOn47
reg("c6-study", a, W("p47", "We"), [("s", [120.9, 23.9], 1500), ("e", [121.5, 24.5], 2200)], tag="REAL DATA", source="CSIS; Bloomberg Economics", clock="", highlight=[HL_TW, HL_CN],
    labels=[lab(a, [117.0, 27.2], "One study of a blockade", W("p47", "study"), WHITE), lab(a, [117.0, 26.6], "Not of a blackout", W("p47", "blackout"), YELLOW)])
a = W("p47", "We")
num("c6-2t", a, S("p48"), "2 TRILLION+", countTo=2, suffix=" TRILLION+", prefix="$", label="at risk in one blockade study", sub="we do not apply this figure here", color=GREY, tag="REAL DATA", source="CSIS blockade study")
a = S("p48")
tNo48 = W("p48", "No")
glob("c6-world", a, tNo48, [("s", 35, 100, 1200), ("e", 40, 20, 1400)], sun={"lat": 15, "lon": 40}, markers=[{"at": WAS, "label": "Washington", "color": BLUE, "kind": "dot", "t": 0.6}, {"at": BEI, "label": "Beijing", "color": AMBER, "kind": "dot", "t": 1.2}],
     caption="How does the world respond?")
a = tNo48
reg("c6-nomodel", a, S("p49"), [("s", [119.0, 25.0], 2400), ("e", [120.5, 24.0], 1200)], clock="", highlight=[HL_TW, HL_CN], legend=LEG,
    labels=[lab(a, [124.8, 28.8], "No model covers this", a + 0.3, WHITE), lab(a, [124.8, 28.2], "CSIS wargames: no cyber", W("p48", "wargames"), YELLOW), lab(a, [124.8, 27.6], "We do not know", W("p48", "know"), WHITE)])
a = S("p49")
tWh, tAg = W("p49", "grid"), W("p49", "Ukraine")
reg("c6-quiet", a, tWh, [("s", [120.9, 23.9], 1100), ("e", [120.9, 23.9], 800)], clock="DAY 7", clockLabel="THE QUIET LINE", clockRate=0, highlight=[HL_TW],
    zones=[disc(KHH, 18, 0.1), disc(TNN, 16, 0.1)], labels=[lab(a, [118.0, 24.8], "What we do know is smaller", W("p49", "smaller"), WHITE)])
a = tWh
reg("c6-nomissile", a, tAg, [("s", [120.9, 23.9], 800), ("e", [121.0, 24.3], 1500)], clock="DAY 7", clockLabel="THE QUIET LINE", clockRate=0, highlight=[HL_TW],
    zones=[disc(KHH, 18, 0.1), disc(TNN, 16, 0.1)], labels=[lab(a, [118.0, 24.6], "A grid can fall without a missile", W("p49", "without"), YELLOW)])
a = tAg
tTh49 = W("p49", "did", 1)
reg("c6-before", a, tTh49, [("s", [121.0, 24.3], 1500), ("e", [30, 49], 3500)], tag="REAL HISTORY", clock="", highlight=[HL_TW, HL_UA],
    labels=[lab(a, [117.0, 26.0], "It has before, in Ukraine", a + 0.4, WHITE), lab(a, [117.0, 25.5], "And in Taiwan itself", W("p49", "Taiwan"), TEAL)])
a = tTh49
reg("c6-lights", a, S("p50"), [("s", [120.95, 23.7], 900), ("e", [120.95, 24.0], 760)], clock="", highlight=[HL_TW],
    cities=lit(a, CELLS, a + 0.5, 0.4), labels=[lab(a, [118.0, 24.6], "This did not happen", W("p49", "happen"), WHITE), lab(a, [118.0, 24.1], "The lights are on", W("p49", "lights"), YELLOW)])
a = S("p50")
add(id="endslate", type="endslate", start=a, end=END, tag="", title="Oreshnik: what it can reach from Belarus", line="Next on the map")

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



# ------------------------------------------------------------------ merge short neighbouring region shots (fewer cuts, same arrivals)
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
    limit = 7.9 if B["end"] <= 90 else 13.0
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
        for k in LISTS:
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
b0 = round(min(DK + 0.1 - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p20") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p20") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.1, "gain_db": -12} for s in shots if s["type"] == "radar"],
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
