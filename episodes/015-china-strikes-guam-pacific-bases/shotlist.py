"""Director pass for episode 015: builds episode.json from narration/timing.json and words.json.

Run from the studio root:  python -m studio shotlist 015-china-strikes-guam-pacific-bases
Payoff first: the 10 kt airburst over Andersen AFB inside 3 s (under the banner), then the run-up from a simulated
launch site, real data and history, the seven-weapon minute-by-minute, the ring-by-ring hero strike on a city map of
Andersen, and the day after. Clocks: Guam time (01:43) and T+ flight time; never the scenario t0_utc.
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
    d = {"at": at, "label": label, "kind": kind}
    if t is not None:
        d["t"] = t
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
        if "_fx" in l:
            fx, fy = l.pop("_fx"), l.pop("_fy")
            l["at"] = offp(ctr, fx * wm, fy * 0.5625 * wm)
        if l.get("t") is None:
            l.pop("t", None)
        else:
            l["t"] = rel(a, l["t"])
        labels.append(l)
    kw = fin(a, kw)
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, labels=labels, **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": 0 if t == "s" else (round(b - a, 2) if t == "e" else rel(a, t)), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **fin(a, kw))


def cty(sid, a, b, keys, rings=(), labs=(), tag="SIMULATION", **kw):
    c = cam(a, b, keys)
    for k in c:
        k["widthKm"] = round(k["widthKm"] / 1000.0, 3)
    wm = (c[0]["widthKm"] + c[-1]["widthKm"]) / 2
    labels = []
    for l in labs:
        l = dict(l)
        if "_fx" in l:
            fx, fy = l.pop("_fx"), l.pop("_fy")
            l["at"] = offp(c[0]["center"], fx * wm, fy * 0.5625 * wm)
        l["t"] = rel(a, l["t"])
        labels.append(l)
    rs = []
    for r in rings:
        d = {"km": r["km"], "label": r.get("label", ""), "color": r["color"], "t": rel(a, r["t"]), "angle": r.get("angle", 225)}
        rs.append(d)
    add(id=sid, type="city", start=a, end=b, tag=tag, city="guam-andersen", view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, gz=GZ, camera=c, rings=rs, labels=labels, **kw)


def LA(at, text, t, color=WHITE):
    return {"at": at, "text": text, "color": color, "t": t}


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



# ------------------------------------------------------------------ places and actors
CN, JP, USA_, TW_, KP, PH = "156", "392", "840", "158", "408", "608"


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


HL_CN, HL_JP, HL_US, HL_TW = hl(CN, AMBER, 0.08), hl(JP, BLUE, 0.10), hl(USA_, BLUE, 0.08), hl(TW_, TEAL, 0.12)
CL_CN, CL_JP = cl(CN, "CHINA", AMBER), cl(JP, "JAPAN", BLUE)
LEG = [{"text": "CHINA", "color": AMBER}, {"text": "US AND ALLIES", "color": BLUE}]

AND = [144.924, 13.576]
GZ = AND
APRA = [144.65, 13.43]
GUAM = [144.79, 13.45]
KAD = [127.769, 26.352]
YOK = [139.67, 35.29]
SH = {s["id"]: s for s in sc["strikes"]}
L_N = [SH["df26n-andersen"]["launch_lon"], SH["df26n-andersen"]["launch_lat"]]
L_CA = [SH["df26c-andersen"]["launch_lon"], SH["df26c-andersen"]["launch_lat"]]
L_AP = [SH["df26c-apra"]["launch_lon"], SH["df26c-apra"]["launch_lat"]]
L_KD = [SH["df26c-kadena"]["launch_lon"], SH["df26c-kadena"]["launch_lat"]]
L_17 = [SH["df17-kadena"]["launch_lon"], SH["df17-kadena"]["launch_lat"]]
L_YK = [SH["df26c-yokosuka"]["launch_lon"], SH["df26c-yokosuka"]["launch_lat"]]
L_H6 = [SH["cj20-kadena"]["launch_lon"], SH["cj20-kadena"]["launch_lat"]]
FX = SH["df26n-andersen"]["effects"]
WASH, HAWAII, HAINAN, PARACEL, PEARL = [-77.04, 38.9], [-157.9, 21.4], [110.3, 19.2], [112.3, 16.5], [-157.97, 21.36]
SRC_D = "CSIS Missile Threat; RAND 2025; Stimson Center 2024"
SRC_H = "National Park Service; CSIS; Reuters; Hawaii and Pacific records"
SRC_G = "US Pacific Fleet and INDOPACOM statements; Guam census"


def LB2(text, t, color=WHITE, row=0, col=-0.30):
    return LB(text, col, 0.31 - 0.085 * row, t, color)


def flights(specs):
    """specs: (launch, target, t0, t1, label, color)."""
    return dict(ships=[ship([p, q], t0, t1, lb, col, 2.6) for p, q, t0, t1, lb, col in specs],
                lines=[line(p, q, t0, t1, col, True) for p, q, t0, t1, lb, col in specs])


def part(p, q, f):
    return [round(p[0] + (q[0] - p[0]) * f, 3), round(p[1] + (q[1] - p[1]) * f, 3)]


def clk(text, rate, label="AFTER FIRST LAUNCH"):
    return dict(clock=text, clockLabel=label, clockRate=rate)


def fl_rate(mins, a, b):
    return round(mins * 60 / max(b - a, 0.5), 1)


# ================================================================== Cold open [SIMULATION]
FLASH = 2.2
CL = [CL_CN]
reg("open-run", 0, FLASH, [("s", [134.0, 21.0], 4800), ("e", [137.0, 17.5], 3100)],
    [LB("Andersen Air Force Base, Guam", -0.02, -0.26, None, RED)],
    clock="T-13:18", clockLabel="TO IMPACT", clockRate=370, highlight=[HL_CN], countryLabels=CL,
    ships=[ship([L_N, AND], 0.0, FLASH - 0.05, "DF-26", RED, 2.8)], lines=[line(L_N, AND, 0.0, FLASH - 0.05, RED, True)],
    cities=[city(AND, "GUAM", None, RED, "target", 6), city(L_N, "Launch (simulated)", None, AMBER, "base", 6)])
a = FLASH
reg("open-burst", a, 5.0, [("s", AND, 130), ("e", AND, 90)],
    [LB("10 kiloton airburst", 0.10, 0.06, a + 0.0, YELLOW), LB("Andersen Air Force Base", 0.10, -0.02, a + 0.3, WHITE)],
    clock="01:43", clockLabel="GUAM TIME", clockRate=0, burst={"at": AND, "t": 0.1, "km": 4, "fade": 4},
    rings=[ring(AND, 4, a + 0.7, "", RED)], cities=[city(AND, "", a + 0.5, RED, "target", 6)])
a = 5.0
cty("open-rings", a, S("p02"), [("s", AND, 7000), ("e", AND, 15000)],
    [dict(ring(AND, FX["fireball_km"], a + 0.3, "Fireball", WHITE), angle=100), dict(ring(AND, FX["psi5_km"], a + 1.2, "5 psi", RED), angle=225), dict(ring(AND, FX["psi1_km"], a + 2.2, "Windows", ORANGE), angle=135)],
    [LB("Andersen Air Force Base", -0.30, 0.30, a + 0.3, WHITE)], clock="01:43", clockLabel="GUAM TIME", clockRate=0,
    caption="Simulation: it has not happened.")
a = S("p02")
tSim, tPub, tNot = W("p02", "simulation"), W("p02", "published"), W("p02", "not")
reg("open-sim", a, tNot, [("s", [140.0, 19.0], 3000), ("e", [145.0, 15.0], 2000)],
    [LB("A simulation", -0.30, 0.30, tSim, YELLOW), LB("Built from published numbers", -0.30, 0.22, tPub, WHITE)], clock="01:43", clockLabel="GUAM TIME", clockRate=0,
    cities=[city(AND, "Guam", a + 0.2, BLUE, "base", 6)])
a = tNot
reg("open-not", a, S("p03"), [("s", [145.0, 15.0], 2000), ("e", [140.0, 20.0], 3600)],
    [LB("It has not happened", -0.30, 0.30, a + 0.1, WHITE)], clock="01:43", clockLabel="GUAM TIME", clockRate=0, highlight=[HL_JP], countryLabels=[CL_JP],
    cities=[city(AND, "Guam", a + 0.2, BLUE, "base", 6)])
a = S("p03")
tLa, tOu = W("p03", "launcher"), W("p03", "ourselves")
reg("open-13", a, tLa, [("s", [118.0, 24.0], 2600), ("e", [116.0, 25.0], 1500)],
    [LB2("Thirteen minutes earlier", a + 0.1, YELLOW)], clock="01:30", clockLabel="GUAM TIME", clockRate=0, highlight=[HL_CN], countryLabels=CL)
a = tLa
reg("open-launcher", a, tOu, [("s", [116.0, 25.0], 1500), ("e", L_N, 520)],
    [LB2("A launcher in southern China", a + 0.1, AMBER)], clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_CN],
    cities=[city(L_N, "DF-26 launcher (simulated)", a + 0.3, AMBER, "base", 6)])
a = tOu
reg("open-placed", a, S("p04"), [("s", L_N, 520), ("e", [116.0, 25.5], 1400)],
    [LB2("We placed it ourselves", a + 0.1, YELLOW)], clock="T+00:00", clockLabel="LAUNCH", clockRate=0, highlight=[HL_CN],
    cities=[city(L_N, "Simulated site", a + 0.1, AMBER, "base", 6)])
a = S("p04")
tTh, tKm = W("p04", "thirteen"), W("p04", "kilometres")
glob("open-arc", a, tTh + 0.2, [("s", 21.0, 122.0, 1900), ("e", 19.0, 130.0, 2600)],
     arcs=[{"from": L_N, "to": AND, "t0": 0.2, "t1": tTh + 0.1 - a, "color": RED, "width": 3, "loft": 0.25}],
     markers=[{"at": L_N, "label": "Launch (simulated)", "color": AMBER, "t": 0.2, "kind": "base"}, {"at": AND, "label": "Guam", "color": BLUE, "t": 1.0, "kind": "target"}],
     clock="T+00:00", clockLabel="FLIGHT", clockRate=190)
a = tTh + 0.2
reg("open-flight", a, S("p05"), [("s", [130.0, 20.0], 5200), ("e", [134.0, 19.0], 4300)],
    [LB2("About thirteen minutes", a + 0.1, YELLOW), LB2("3,400 km", tKm, WHITE, 1)], clock="T+06:30", clockLabel="FLIGHT", clockRate=60, highlight=[HL_CN],
    **flights([(L_N, AND, a, a + 5.0, "DF-26", RED)]), cities=[city(AND, "Guam", a + 0.3, BLUE, "base", 6)])
a = S("p05")
tHo = W("p05", "how")
BASES = [city(AND, "Andersen", 0, BLUE, "base", 6), city(KAD, "Kadena", 0, BLUE, "base", 6), city(YOK, "Yokosuka", 0, BLUE, "base", 6)]
def bases(a, t0=0.2, step=0.5):
    return [city(p, n, a + t0 + i * step, BLUE, "base", 6) for i, (p, n) in enumerate([(AND, "Andersen"), (KAD, "Kadena"), (YOK, "Yokosuka")])]
reg("open-q1", a, tHo, [("s", [136.0, 22.0], 5200), ("e", [136.0, 23.0], 3900)],
    [LB2("The first hour", a + 0.1, YELLOW)], clock="01:43", clockLabel="GUAM TIME", clockRate=0, highlight=[HL_JP], countryLabels=[CL_JP], cities=bases(a))
a = tHo
reg("open-q2", a, S("p06"), [("s", [136.0, 23.0], 3900), ("e", [140.0, 21.0], 2700)],
    [LB2("How many fighters can still take off?", a + 0.2, WHITE)], clock="01:43", clockLabel="GUAM TIME", clockRate=0, highlight=[HL_JP], countryLabels=[CL_JP], cities=bases(a, 0.1, 0.2))

# ================================================================== Chapter 01 [REAL DATA] the island that is a runway
a = chapter("c1-card", S("p06"), 3.5, "CHAPTER 01", "The island that is a runway", "REAL DATA")
tPa, tDi = W("p06", "Pacific"), W("p06", "did")
reg("c1-ve", a, tPa, [("s", GUAM, 400), ("e", [144.79, 13.47], 200)],
    [LB2("Valiant Shield, 2026", a + 0.2, YELLOW), LB2("Army Dark Eagle seen on Guam", W("p06", "hypersonic"), WHITE, 1)], tag="REAL DATA", source=SRC_G, clock="2026", clockLabel="EXERCISE", clockRate=0,
    cities=[city(AND, "Andersen AFB", a + 0.6, BLUE, "base", 6), city(APRA, "Naval Base Guam", a + 1.2, BLUE, "base", 6)])
a = tPa
reg("c1-pacom", a, tDi, [("s", [144.79, 13.47], 200), ("e", GUAM, 320)],
    [LB2("Pacific command: photos taken here", a + 0.2, BLUE)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(AND, "Andersen AFB", a + 0.1, BLUE, "base", 6)])
a = tDi
reg("c1-stay", a, S("p07"), [("s", GUAM, 320), ("e", [144.79, 13.5], 160)],
    [LB2("Did the weapon stay? Not said", a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(AND, "Andersen AFB", a + 0.1, BLUE, "base", 6)])
a = S("p07")
tDe = W("p07", "Defense")
reg("c1-guam", a, tDe, [("s", [144.79, 13.45], 220), ("e", [144.79, 13.45], 160)],
    [LB2("An American island", a + 0.3, BLUE), LB2("About 170,000 people", W("p07", "hundred"), WHITE, 1)], tag="REAL DATA", source=SRC_G, clock="",
    cities=[city(AND, "Andersen AFB", a + 0.8, BLUE, "base", 6), city(APRA, "Naval Base Guam", a + 1.6, BLUE, "base", 6)])
a = tDe
reg("c1-dod", a, S("p08"), [("s", [144.79, 13.45], 160), ("e", GUAM, 260)],
    [LB2("Defense Department owns about 29%", a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(AND, "Andersen AFB", a + 0.1, BLUE, "base", 6)])
a = S("p08")
tFl = W("p08", "flash")
reg("c1-cold", a, tFl, [("s", [144.79, 13.5], 150), ("e", [144.9, 13.57], 240)],
    [LB2("The island in our cold open", a + 0.2, WHITE)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(AND, "Andersen AFB", a + 0.8, BLUE, "base", 6)])
a = tFl
reg("c1-143", a, S("p09"), [("s", AND, 200), ("e", AND, 150)],
    [LB2("The flash at 01:43", a + 0.1, RED)], tag="REAL DATA", source=SRC_G, clock="01:43", clockLabel="GUAM TIME", clockRate=0, cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = S("p09")
tBo, tNa = W("p09", "Bombers"), W("p09", "Naval")
cty("c1-runways", a, tBo, [("s", AND, 9000), ("e", AND, 6000)], [],
    [LA([144.91, 13.597], "Runway: about 3.4 km", a + 0.3, WHITE), LA([144.935, 13.555], "Runway: about 3.2 km", W("p09", "three", 2), WHITE), LB("Two parallel runways", -0.30, 0.31, a + 0.1, YELLOW)], tag="REAL DATA", source="Andersen AFB; OpenStreetMap", clock="")
a = tBo
cty("c1-bombers", a, tNa, [("s", AND, 6000), ("e", AND, 11000)], [],
    [LB("Bombers rotate through", -0.30, 0.31, a + 0.2, BLUE), LB("Ad hoc since 2020", -0.30, 0.23, W("p09", "ad"), WHITE)], tag="REAL DATA", source="Andersen AFB; OpenStreetMap", clock="")
a = tNa
reg("c1-naval", a, S("p10"), [("s", [144.78, 13.5], 150), ("e", [144.78, 13.5], 90 + 60)],
    [LB2("Naval Base Guam: submarines", a + 0.2, BLUE), LB2("About 48 km away", W("p09", "forty-eight"), WHITE, 1)], tag="REAL DATA", source="Andersen AFB; Guam Wikipedia", clock="",
    cities=[city(APRA, "Naval Base Guam", a + 0.1, BLUE, "base", 6), city(AND, "Andersen AFB", a + 0.5, BLUE, "base", 6)])
a = S("p10")
tKd = W("p10", "Kadena")
reg("c1-kadena", a, tKd, [("s", [136.0, 20.5], 3600), ("e", [133.0, 22.0], 3000)],
    [LB2("2,300 km north-west", a + 0.2, WHITE)], tag="REAL DATA", source=SRC_G, clock="", highlight=[HL_JP], countryLabels=[CL_JP],
    cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)], lines=[line(AND, KAD, a + 0.3, a + 4.0, WHITE, True)])
a = tKd
reg("c1-kadena2", a, W("p10", "Army"), [("s", [133.0, 22.0], 3000), ("e", [129.5, 25.0], 1600)],
    [LB2("Kadena Air Base, Okinawa", a + 0.2, BLUE)], tag="REAL DATA", source=SRC_G, clock="", highlight=[HL_JP],
    cities=[city(AND, "Guam", 0, BLUE, "base", 6), city(KAD, "Kadena", a + 0.3, BLUE, "base", 6)], lines=[line(AND, KAD, 0, 0.1, WHITE, True)])
a = W("p10", "Army")
reg("c1-patriot", a, S("p11"), [("s", KAD, 520), ("e", KAD, 220)],
    [LB2("Two runways, 3.7 km each", a - 2.0, WHITE), LB2("An Army Patriot battalion", a + 0.2, BLUE, 1)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(KAD, "Kadena AB", a - 2.0, BLUE, "base", 6)])
a = S("p11")
tNk, tGk = W("p11", "Western"), W("p11", "Guam", 2)
tCv11 = W("p11", "conventionally")
reg("c1-df26", a, tCv11, [("s", [128.0, 23.0], 5400), ("e", [126.0, 24.0], 4400)],
    [LB2("DF-26 missile", a + 0.2, AMBER), LB2("CSIS: China's first", a + 2.4, WHITE, 1)], tag="REAL DATA", source=SRC_D, clock="", highlight=[HL_CN], countryLabels=CL,
    cities=[city(AND, "Guam", a + 0.8, BLUE, "base", 6)], lines=[line(L_N, AND, a + 2.0, a + 5.0, AMBER, True)])
a = tCv11
reg("c1-df26b", a, tGk - 0.3, [("s", [126.0, 24.0], 4400), ("e", [134.0, 20.0], 3600)],
    [LB2("Conventionally armed ballistic missile", a + 0.2, AMBER), LB2("Able to reach Guam", W("p11", "able"), WHITE, 1)], tag="REAL DATA", source=SRC_D, clock="", highlight=[HL_CN],
    cities=[city(AND, "Guam", 0, BLUE, "base", 6)], lines=[line(L_N, AND, 0, 0.1, AMBER, True)])
a = tGk - 0.3
reg("c1-nick", a, S("p12"), [("s", [136.0, 19.0], 3600), ("e", [140.0, 18.0], 2800)],
    [LB2("'Guam killer': a nickname", a + 0.2, YELLOW), LB2("Not an official name", W("p11", "official"), WHITE, 1)], tag="REAL DATA", source=SRC_D, clock="", cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)])
a = S("p12")
tOne, tEst = W("p12", "One"), W("p12", "Estimates")
reg("c1-range", a, tOne, [("s", [125.0, 22.0], 9000), ("e", [128.0, 20.0], 8000)],
    [LB2("DF-26 range: about 4,000 km", a + 0.3, AMBER)], tag="REAL DATA", source=SRC_D, clock="", highlight=[HL_CN],
    rings=[ring(L_N, 4000, a + 0.5, "4,000 km", AMBER, True)], cities=[city(L_N, "Launcher (simulated)", a + 0.3, AMBER, "base", 6), city(AND, "Guam", a + 1.0, BLUE, "base", 6)])
a = tOne
reg("c1-swap", a, tEst, [("s", [118.0, 30.0], 3000), ("e", [114.0, 30.0], 2200)],
    [LB2("One warhead can be swapped", a + 0.2, WHITE), LB2("Nuclear or conventional", W("p12", "nuclear"), RED, 1), LB2("Most are conventional", W("p12", "most"), YELLOW, 2)], tag="REAL DATA", source=SRC_D, clock="", highlight=[HL_CN], countryLabels=CL)
a = tEst
LAUNCHERS = [[111.0, 27.5], [114.5, 25.0], [118.0, 28.5], [119.5, 29.0], [117.0, 25.1], [118.5, 36.0], [113.0, 34.0], [108.0, 30.0], [121.0, 41.0], [104.0, 36.0]]
reg("c1-250", a, S("p13"), [("s", [112.0, 31.0], 3600), ("e", [116.0, 30.0], 3000)],
    [LB2("About 250 to 300 launchers", a + 0.2, AMBER), LB2("An outside estimate", a + 1.4, WHITE, 1)], tag="REAL DATA", source=SRC_D, clock="", highlight=[HL_CN], countryLabels=CL,
    cities=[city(p, "DF-26 sites" if i == 0 else "", a + 0.3 + i * 0.45, AMBER, "dot", 5) for i, p in enumerate(LAUNCHERS)])
a = S("p13")
tTe = W("p13", "first")
reg("c1-defence", a, tTe, [("s", GUAM, 200), ("e", [144.79, 13.47], 150)],
    [LB2("Guam's new missile defence", a + 0.2, BLUE), LB2("Not due until late 2027", W("p13", "late"), YELLOW, 1)], tag="REAL DATA", source=SRC_D, clock="", cities=[city(AND, "Andersen AFB", a + 0.3, BLUE, "base", 6), city(APRA, "Naval Base Guam", a + 1.2, BLUE, "base", 6)])
a = tTe
reg("c1-test", a, S("p14"), [("s", [144.79, 13.47], 150), ("e", [144.5, 13.45], 330)],
    [LB2("First interception test from the island", a + 0.2, WHITE), LB2("December 2024", W("p13", "December"), YELLOW, 1)], tag="REAL DATA", source=SRC_D, clock="", cities=[city(AND, "Andersen AFB", a + 0.3, BLUE, "base", 6)])
a = S("p14")
reg("c1-ever", a, S("p15"), [("s", [140.0, 19.0], 2400), ("e", [136.0, 21.0], 3400)],
    [LB2("Has anyone ever fired at Guam?", a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_G, clock="", cities=[city(AND, "Guam", a + 0.3, BLUE, "base", 6)])

# ================================================================== Chapter 02 [REAL HISTORY] the base-attack record
a = chapter("c2-card", S("p15"), 3.5, "CHAPTER 02", "The base-attack record", "REAL HISTORY")
tAi, tAn = W("p15", "aircraft"), W("p15", "cannot")
reg("c2-pearl", a, tAi, [("s", PEARL, 500), ("e", PEARL, 200)],
    [LB2("7 December 1941", a + 0.2, YELLOW), LB2("Japanese carrier planes hit Pearl Harbor", a + 1.0, WHITE, 1)], tag="REAL HISTORY", source=SRC_H, clock="1941", clockLabel="PEARL HARBOR", clockRate=0,
    cities=[city(PEARL, "Pearl Harbor", a + 0.4, BLUE, "base", 6)])
a = tAi
tEv = W("p15", "Every")
reg("c2-aircraft", a, tEv, [("s", PEARL, 200), ("e", [-157.8, 21.4], 340)],
    [LB2("About 200 aircraft destroyed", a + 0.2, RED), LB2("National Park Service count", a + 1.0, WHITE, 1)], tag="REAL HISTORY", source=SRC_H, clock="1941", clockLabel="PEARL HARBOR", clockRate=0,
    cities=[city(PEARL, "Pearl Harbor", a + 0.1, BLUE, "base", 6)])
a = tEv
reg("c2-carriers", a, tAn, [("s", [-157.0, 21.5], 700), ("e", [-157.5, 22.5], 1500)],
    [LB2("Every carrier was away at sea", a + 0.2, BLUE)], tag="REAL HISTORY", source=SRC_H, clock="1941", clockLabel="PEARL HARBOR", clockRate=0,
    cities=[city(PEARL, "Pearl Harbor", a + 0.1, BLUE, "base", 6)], ships=[{"path": [PEARL, [-158.4, 22.8]], "t0": a - a + 0.5, "t1": 4.0, "kind": "us", "color": BLUE, "label": "Carriers", "size": 2.6, "t": 0.5, "wake": True}])
a = tAn
reg("c2-cannot", a, S("p16"), [("s", [-157.5, 22.0], 1500), ("e", [-157.0, 21.4], 500)],
    [LB2("An air base cannot move", a + 0.2, RED), LB2("A carrier can", W("p15", "carrier", 2), BLUE, 1)], tag="REAL HISTORY", source=SRC_H, clock="1941", clockLabel="PEARL HARBOR", clockRate=0,
    cities=[city(PEARL, "Pearl Harbor (base)", a + 0.1, RED, "target", 6)])
a = S("p16")
KP_LAUNCH = [125.7, 39.0]
JAPAN_PATH = [[133.0, 35.5], [134.0, 34.5]]
tFo16 = W("p16", "four")
reg("c2-nk", a, tFo16, [("s", [133.0, 32.0], 3600), ("e", [138.0, 28.0], 4800)],
    [LB2("9 August 2017", a + 0.2, YELLOW), LB2("North Korea studies a plan", a + 1.0, WHITE, 1)], tag="REAL HISTORY", source="Reuters; KCNA reports; AP", clock="2017", clockLabel="NORTH KOREA", clockRate=0,
    highlight=[hl(KP, AMBER, 0.10), HL_JP], countryLabels=[cl(KP, "NORTH KOREA", AMBER), CL_JP], cities=[city(AND, "Guam", a + 0.8, BLUE, "base", 6)])
a = tFo16
reg("c2-four", a, W("p16", "never"), [("s", [138.0, 28.0], 4800), ("e", [140.0, 24.0], 3800)],
    [LB2("Four missiles over Japan", a + 0.2, YELLOW), LB2("Into waters near Guam", W("p16", "waters"), WHITE, 1)], tag="REAL HISTORY", source="Reuters; KCNA reports; AP", clock="2017", clockLabel="NORTH KOREA", clockRate=0,
    highlight=[hl(KP, AMBER, 0.10), HL_JP], countryLabels=[CL_JP], cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)],
    lines=[line([128.0, 38.5], AND, a + 0.4, a + 3.4, AMBER, True)])
a = W("p16", "never")
reg("c2-never", a, S("p17"), [("s", [140.0, 24.0], 3800), ("e", [145.0, 17.0], 2200)],
    [LB2("It never launched", a + 0.2, WHITE), LB2("A threat alone made Guam a target", W("p16", "threat"), YELLOW, 1)], tag="REAL HISTORY", source="Reuters; KCNA reports; AP", clock="2017", clockLabel="NORTH KOREA", clockRate=0,
    cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)])
a = S("p17")
tDf, tSc = W("p17", "DF-26B"), W("p17", "carrier-killer")
reg("c2-scs", a, tDf, [("s", [114.0, 18.5], 2000), ("e", [112.0, 18.0], 1400)],
    [LB2("26 August 2020", a + 0.2, YELLOW), LB2("South China Sea", a + 0.9, WHITE, 1)], tag="REAL HISTORY", source="Reuters; South China Morning Post; CSIS", clock="2020", clockLabel="CHINA TEST", clockRate=0, highlight=[HL_CN], countryLabels=CL,
    cities=[city(HAINAN, "Hainan", a + 1.2, AMBER), city(PARACEL, "Paracel Islands", a + 2.0, AMBER)])
a = tDf
tSo = W("p17", "so-called")
reg("c2-df", a, tSc, [("s", [112.0, 18.0], 1400), ("e", [110.0, 24.0], 3000)],
    [LB2("DF-26B and DF-21D fired", a + 0.2, AMBER), LB2("Into water, near Hainan", W("p17", "Hainan") if False else a + 1.6, WHITE, 1)], tag="REAL HISTORY", source="Reuters; South China Morning Post; CSIS", clock="2020", clockLabel="CHINA TEST", clockRate=0, highlight=[HL_CN],
    cities=[city(HAINAN, "Hainan", a + 0.1, AMBER), city(PARACEL, "Paracel Islands", a + 0.5, AMBER)])
a = tSc
reg("c2-first", a, S("p18"), [("s", [118.0, 22.0], 3000), ("e", [122.0, 20.0], 2200)],
    [LB2("First public 'carrier-killer' test into water", a + 0.2, YELLOW), LB2("The same family as our DF-26", W("p17", "same"), WHITE, 1)], tag="REAL HISTORY", source="Reuters; South China Morning Post; CSIS", clock="2020", clockLabel="CHINA TEST", clockRate=0, highlight=[HL_CN], countryLabels=CL)
a = S("p18")
tDy = W("p18", "threat")
reg("c2-slow", a, tDy, [("s", [175.0, 24.0], 9800), ("e", [170.0, 24.0], 8600)],
    [LB2("Every one of those was slow", a + 0.2, WHITE), LB2("1941: a fleet across an ocean", a + 1.0, BLUE, 1)], tag="REAL HISTORY", source=SRC_H, clock="",
    cities=[city(PEARL, "Pearl Harbor 1941", a + 0.6, BLUE, "base", 6), city(AND, "Guam", a + 1.2, BLUE, "base", 6)])
a = tDy
reg("c2-slow2", a, S("p19"), [("s", [140.0, 22.0], 4000), ("e", [128.0, 20.0], 5000)],
    [LB2("2017: a threat in words", a + 0.2, YELLOW), LB2("2020: a test in empty water", W("p18", "test"), AMBER, 1)], tag="REAL HISTORY", source=SRC_H, clock="", cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)])
a = S("p19")
tNo19 = W("p19", "not")
reg("c2-what", a, W("p19", "flight"), [("s", [128.0, 22.0], 5400), ("e", [132.0, 21.0], 4200)],
    [LB2("What if it were not a test?", a + 0.2, YELLOW)], clock="T+00:00", clockLabel="THIRTEEN MINUTES", clockRate=0, highlight=[HL_CN], countryLabels=CL,
    cities=[city(L_N, "Launch (simulated)", a + 0.3, AMBER, "base", 6), city(AND, "Guam", a + 0.6, BLUE, "base", 6)])
a = W("p19", "flight")
reg("c2-13", a, S("p20"), [("s", [132.0, 21.0], 4200), ("e", [136.0, 19.0], 3200)],
    [LB2("A flight of thirteen minutes", a + 0.2, RED)], clock="T+00:00", clockLabel="FLIGHT", clockRate=fl_rate(13.3, a, a + 3.0), highlight=[HL_CN],
    **flights([(L_N, AND, a + 0.1, a + 3.0, "DF-26", RED)]))

# ================================================================== Chapter 03 [SIMULATION] the order
a = chapter("c3-card", S("p20"), 3.5, "CHAPTER 03", "The order", "SIMULATION")
tTh20, tMi = W("p20", "clock"), W("p20", "minute", 2) if False else W("p20", "zero")
reg("c3-fail", a, tTh20, [("s", [118.0, 27.0], 3000), ("e", [118.0, 27.0], 2200)],
    [LB2("Diplomacy has already failed", a + 0.1, WHITE), LB2("We do not say why", W("p20", "we"), YELLOW, 1)], clock="T-00:30", clockLabel="BEFORE FIRST LAUNCH", clockRate=0, highlight=[HL_CN], countryLabels=CL)
a = tTh20
reg("c3-zero", a, S("p21"), [("s", [118.0, 27.0], 2200), ("e", [122.0, 24.0], 3600)],
    [LB2("The clock starts at the first launch", a + 0.2, YELLOW), LB2("Minute zero", tMi, RED, 1)], clock="T+00:00", clockLabel="MINUTE ZERO", clockRate=0, highlight=[HL_CN],
    cities=[city(L_N, "Launcher (simulated)", a + 0.4, AMBER, "base", 6)])
a = S("p21")
tRe, tSu = W("p21", "releases"), W("p21", "subsonic")
reg("c3-h6", a, tRe + 0.6, [("s", [126.0, 29.0], 1700), ("e", [127.0, 28.0], 1100)],
    [LB2("25 minutes earlier", a + 0.2, YELLOW), LB2("H-6K bomber: East China Sea", a + 1.0, AMBER, 1)], clock="T-25:00", clockLabel="BEFORE FIRST LAUNCH", clockRate=20, highlight=[HL_CN, HL_JP], countryLabels=[CL_JP],
    cities=[city(L_H6, "H-6K (simulated)", a + 0.6, AMBER, "base", 6), city(KAD, "Kadena", a + 1.4, BLUE, "base", 6)])
a = tRe + 0.6
reg("c3-cj20", a, tSu, [("s", [126.0, 28.0], 1200), ("e", [127.0, 27.0], 800)],
    [LB2("One CJ-20 cruise missile", a + 0.2, RED)], clock="T-24:00", clockLabel="BEFORE FIRST LAUNCH", clockRate=20, highlight=[HL_JP],
    **flights([(L_H6, KAD, a + 0.2, a + 8.0, "CJ-20", RED)]), cities=[city(KAD, "Kadena", a + 0.3, BLUE, "base", 6)])
a = tSu
reg("c3-last", a, S("p22"), [("s", [126.0, 27.5], 900), ("e", [127.5, 27.0], 500)],
    [LB2("Subsonic: timed to arrive last", a + 0.2, YELLOW)], clock="T-23:00", clockLabel="BEFORE FIRST LAUNCH", clockRate=20, highlight=[HL_JP],
    cities=[city(KAD, "Kadena", a + 0.1, BLUE, "base", 6)])
a = S("p22")
tHig = W("p22", "bombers")
reg("c3-six", a, tHig, [("s", [124.0, 28.0], 1800), ("e", [123.0, 29.0], 1200)],
    [LB2("An H-6K carries up to six", a + 0.2, WHITE)], clock="T-22:00", clockLabel="BEFORE FIRST LAUNCH", clockRate=0, highlight=[HL_CN],
    cities=[city(L_H6, "H-6K (simulated)", a + 0.2, AMBER, "base", 6)])
a = tHig
reg("c3-one", a, S("p23"), [("s", [123.0, 29.0], 1200), ("e", [125.0, 28.0], 2400)],
    [LB2("High risk of detection", a + 0.2, YELLOW), LB2("We use one", W("p22", "one"), WHITE, 1)], clock="T-22:00", clockLabel="BEFORE FIRST LAUNCH", clockRate=0, highlight=[HL_CN],
    cities=[city(L_H6, "H-6K (simulated)", a + 0.1, AMBER, "base", 6)])
a = S("p23")
tRep = W("p23", "video")
reg("c3-report", a, tRep, [("s", [144.8, 13.5], 600), ("e", [144.85, 13.55], 260)],
    [LB2("One report, 2020", a + 0.2, YELLOW)], clock="", highlight=[], cities=[city(AND, "Andersen AFB", a + 0.3, BLUE, "base", 6)], source="Task & Purpose, 2022 (single source)")
a = tRep
reg("c3-video", a, S("p24"), [("s", [144.85, 13.55], 260), ("e", [144.9, 13.57], 170)],
    [LB2("Chinese air force video", a + 0.2, AMBER), LB2("An airfield laid out like Andersen", W("p23", "airfield"), WHITE, 1)], clock="", source="Task & Purpose, 2022 (single source)",
    cities=[city(AND, "Andersen AFB", a + 0.1, BLUE, "base", 6)])
a = S("p24")
tTw24, tCo, tNu = W("p24", "two"), W("p24", "conventional"), W("p24", "nuclear")
reg("c3-two", a, tCo, [("s", [128.0, 22.0], 5600), ("e", [130.0, 21.0], 4600)],
    [LB2("Minute zero", a + 0.1, RED), LB2("Two DF-26s for Andersen", a + 1.0, WHITE, 1)], highlight=[HL_CN], countryLabels=CL,
    **clk("T+00:00", 40, "MINUTE ZERO"),
    **flights([(L_N, AND, a + 0.4, a + 5.0, "DF-26", YELLOW), (L_CA, AND, a + 0.4, a + 5.0, "DF-26", RED)]), cities=[city(AND, "Andersen AFB", a + 0.3, BLUE, "base", 6)])
a = tCo
reg("c3-types", a, S("p25"), [("s", [130.0, 21.0], 4600), ("e", [135.0, 19.0], 3000)],
    [LB2("One conventional warhead", a + 0.1, RED), LB2("One nuclear warhead", tNu, YELLOW, 1)], highlight=[HL_CN],
    **clk("T+02:00", 40, "MINUTE ZERO"),
    **flights([(part(L_N, AND, 0.95), AND, a + 0.05, a + 3.0, "Nuclear", YELLOW), (part(L_CA, AND, 0.95), AND, a + 0.05, a + 3.0, "Conventional", RED)]), cities=[city(AND, "Andersen AFB", a + 0.1, BLUE, "base", 6)])
a = S("p25")
tAc, tCe = W("p25", "Accuracy"), W("p25", "circular")
cty("c3-cep", a, tCe, [("s", AND, 5000), ("e", AND, 3000)], [],
    [LB("Why so many missiles?", -0.30, 0.31, a + 0.1, WHITE), LB("Accuracy", -0.30, 0.23, tAc, YELLOW)], clock="", )
a = tCe
tC1, tC2 = W("p25", "hundred"), W("p25", "metres")
cty("c3-cep2", a, S("p26"), [("s", AND, 3000), ("e", AND, 2200)],
    [dict(ring(AND, 0.15, a + 0.5, "150 m", WHITE, True), angle=300), dict(ring(AND, 0.45, a + 3.0, "450 m", WHITE, True), angle=225)],
    [LB("Analysts' estimate of error", -0.30, 0.31, a + 0.1, YELLOW), LB("A planner needs many missiles", -0.30, 0.23, W("p25", "planner"), WHITE)], clock="", source="CSIS Missile Threat; USCC staff report summary")
a = S("p26")
bars_t = W("p26", "grew")
add(id="c3-rand", type="bars", start=a, end=a + 6.0, tag="REAL DATA", title="China's intermediate-range missiles", sub="RAND, July 2025: stockpile estimate", source="RAND, July 2025",
    bars=[{"label": "2012", "value": 20, "display": "about 20", "color": AMBER}, {"label": "2023", "value": 500, "display": "about 500", "color": AMBER}])
a += 6.0
reg("c3-notkept", a, S("p27"), [("s", [135.0, 20.0], 3600), ("e", [132.0, 22.0], 2800)],
    [LB2("Air base defence 'has not kept pace'", a + 0.2, YELLOW), LB2("RAND, July 2025", a + 1.0, WHITE, 1)], clock="", source="RAND, July 2025", highlight=[HL_CN], cities=[city(AND, "Andersen AFB", a + 0.3, BLUE, "base", 6)])
a = S("p27")
stamp("c3-ours", a, a + 3.0, "OUR CHOICE, NOT A FORECAST", "", YELLOW, tag="SIMULATION")
a += 3.0
tNF = W("p27", "no")
reg("c3-nfu", a, W("p27", "ten") - 0.1, [("s", [112.0, 32.0], 4400), ("e", [116.0, 30.0], 3600)],
    [LB2("China's declared policy: no first use", a + 0.2, AMBER), LB2("The second missile is our choice", a + 1.2, YELLOW, 1)], clock="", highlight=[HL_CN], countryLabels=CL)
a = W("p27", "ten") - 0.1
num("c3-10kt", a, a + 4.4, "10 KT", label="our nuclear warhead", sub="the top of the Pentagon's below-10 kt estimate", color=YELLOW, tag="SIMULATION", countTo=10, suffix=" KT", source="Pentagon China report, 2025")
a += 4.4
tPe = W("p27", "Pentagon")
tNag = W("p27", "Nagasaki")
reg("c3-nag", a, tPe, [("s", [140.0, 33.0], 3400), ("e", [133.0, 33.0], 2400)],
    [LB2("About half of Nagasaki", a + 0.2, WHITE)], clock="", highlight=[HL_JP], countryLabels=[CL_JP])
a = tPe
reg("c3-pent", a, S("p28"), [("s", [118.0, 30.0], 3200), ("e", [122.0, 28.0], 2400)],
    [LB2("Pentagon: China probably pursuing", a + 0.2, BLUE), LB2("low-yield nuclear warheads", a + 1.0, YELLOW, 1)], clock="", highlight=[HL_CN], countryLabels=CL, source="Pentagon China report, 2025")
a = S("p28")
tCn, tDa = W("p28", "CNAS"), W("p28", "Dangerous")
reg("c3-wargames", a, tCn, [("s", [138.0, 22.0], 4600), ("e", [134.0, 24.0], 3800)],
    [LB2("Pentagon-sponsored war games", a + 0.2, BLUE), LB2("China opens by hitting Guam's bases", a + 1.6, YELLOW, 1)], clock="", highlight=[HL_CN, HL_JP], countryLabels=[CL_CN, CL_JP],
    cities=bases(a, 0.6, 0.6))
a = tCn
reg("c3-cnas", a, W("p28", "We"), [("s", [134.0, 24.0], 3800), ("e", [140.0, 21.0], 3000)],
    [LB2("CNAS 'Dangerous Straits', 2022", a + 0.2, WHITE), LB2("China struck bases in Japan and Guam", W("p28", "struck"), RED, 1)], clock="", highlight=[HL_CN, HL_JP], source="CNAS Dangerous Straits, 2022",
    cities=bases(a, 0.3, 0.4))
a = W("p28", "We")
reg("c3-added", a, S("p29"), [("s", [140.0, 21.0], 3000), ("e", [145.0, 17.0], 2000)],
    [LB2("We added one nuclear shot", a + 0.2, YELLOW), LB2("To test the threshold", W("p28", "test"), WHITE, 1)], clock="", cities=[city(AND, "Andersen AFB", a + 0.2, YELLOW, "target", 6)])
a = S("p29")
tAp = W("p29", "apart")
reg("c3-risk", a, tAp, [("s", [130.0, 22.0], 4600), ("e", [136.0, 19.0], 3400)],
    [LB2("A defender cannot tell them apart", a + 0.2, WHITE)], highlight=[HL_CN], **clk("T+04:00", 30, "AFTER FIRST LAUNCH"),
    **flights([(L_N, AND, a + 0.2, a + 4.0, "?", YELLOW), (L_CA, AND, a + 0.2, a + 4.0, "?", RED)]))
a = tAp
reg("c3-look", a, S("p30"), [("s", [136.0, 19.0], 3400), ("e", [140.0, 17.0], 2300)],
    [LB2("A conventional strike can look nuclear", a + 0.2, YELLOW)], clock="", cities=[city(AND, "Andersen AFB", a + 0.2, BLUE, "base", 6)])
a = S("p30")
tFi = W("p30", "first")
allf = [(L_KD, KAD, 0.3, 5.0, "", RED), (L_17, KAD, 0.7, 5.0, "", RED), (L_YK, YOK, 1.1, 5.0, "", RED), (L_N, AND, 1.5, 5.0, "", YELLOW), (L_AP, APRA, 1.9, 5.0, "", RED), (L_CA, AND, 2.3, 5.0, "", RED)]
reg("c3-seven", a, S("p31"), [("s", [128.0, 26.0], 5800), ("e", [130.0, 24.0], 5200)],
    [LB2("Seven weapons, one nuclear", a + 0.2, YELLOW), LB2("The first to land is not on Guam", tFi, WHITE, 1)], highlight=[HL_CN, HL_JP], countryLabels=[CL_CN, CL_JP],
    **flights([(p, q, a + t0, a + t1, lb, c) for p, q, t0, t1, lb, c in allf]),
    cities=[city(AND, "Guam", a + 0.3, BLUE, "base", 6), city(KAD, "Kadena", a + 0.6, BLUE, "base", 6), city(YOK, "Yokosuka", a + 0.9, BLUE, "base", 6)])

# ================================================================== Chapter 04 [SIMULATION] the first nineteen minutes
a = chapter("c4-card", S("p31"), 3.5, "CHAPTER 04", "The first nineteen minutes", "SIMULATION")
reg("c4-m1", a, S("p32"), [("s", [130.0, 22.0], 5400), ("e", [134.0, 18.0], 4200)],
    [LB2("Minute one", a + 0.1, YELLOW), LB2("A DF-26 for Naval Base Guam", a + 0.8, RED, 1)], highlight=[HL_CN], **clk("T+01:00", 20),
    **flights([(L_AP, APRA, a + 0.2, S("p32") - 0.1, "DF-26", RED)]), cities=[city(APRA, "Naval Base Guam", a + 0.4, BLUE, "base", 6)])
a = S("p32")
tYo = W("p32", "Yokosuka")
reg("c4-m2", a, tYo, [("s", [126.0, 30.0], 3400), ("e", [131.0, 29.0], 3000)],
    [LB2("Minute two", a + 0.1, YELLOW), LB2("Two more DF-26s", a + 0.9, WHITE, 1), LB2("One for Kadena", W("p32", "Kadena"), RED, 2)], highlight=[HL_CN, HL_JP], **clk("T+02:00", 20),
    **flights([(L_KD, KAD, a + 0.3, a + 4.5, "DF-26", RED)]), cities=[city(KAD, "Kadena", a + 0.5, BLUE, "base", 6)])
a = tYo
reg("c4-m2b", a, S("p33"), [("s", [130.0, 33.0], 3200), ("e", [135.0, 34.0], 2400)],
    [LB2("One for Yokosuka, Japan", a + 0.1, RED), LB2("US Navy base", a + 1.2, BLUE, 1)], highlight=[HL_CN, HL_JP], countryLabels=[CL_JP], **clk("T+03:00", 20),
    **flights([(L_YK, YOK, a + 0.1, a + 3.8, "DF-26", RED)]), cities=[city(YOK, "Yokosuka", a + 0.3, BLUE, "base", 6)])
a = S("p33")
tHy = W("p33", "hypersonic")
reg("c4-m3", a, tHy + 1.8, [("s", [122.0, 27.0], 2200), ("e", [125.0, 26.5], 1500)],
    [LB2("Minute three", a + 0.1, YELLOW), LB2("A DF-17 hypersonic glider", tHy, RED, 1)], highlight=[HL_CN, HL_JP], **clk("T+03:00", 20),
    **flights([(L_17, KAD, a + 0.3, a + 6.0, "DF-17", RED)]), cities=[city(L_17, "Fujian (simulated)", a + 0.3, AMBER, "base", 6), city(KAD, "Kadena", a + 1.0, BLUE, "base", 6)])
a = tHy + 1.8
reg("c4-m3b", a, S("p34"), [("s", [125.0, 26.5], 1500), ("e", [127.0, 26.3], 700)],
    [LB2("Conventional", a + 0.2, WHITE), LB2("Fujian to Kadena", a + 0.8, AMBER, 1)], highlight=[HL_JP], **clk("T+04:00", 20),
    cities=[city(KAD, "Kadena", a + 0.1, BLUE, "base", 6)])
a = S("p34")
tWe, tTh34 = W("p34", "We"), W("p34", "launcher")
reg("c4-m8", a, tWe, [("s", [124.0, 27.0], 1400), ("e", KAD, 360)],
    [LB2("Minute eight", a + 0.1, YELLOW), LB2("The first impact", a + 0.9, RED, 1), LB2("DF-26: six minutes of flight", W("p34", "six"), WHITE, 2)], highlight=[HL_JP], **clk("T+06:00", 24),
    **flights([(L_KD, KAD, a + 0.3, a + 4.6, "DF-26", RED)]), rings=[ring(KAD, 8, a + 4.6, "Impact", ORANGE)], cities=[city(KAD, "Kadena", a + 0.4, BLUE, "target", 6)])
a = tWe
reg("c4-patriot", a, tTh34, [("s", KAD, 360), ("e", KAD, 220)],
    [LB2("We do not count which Patriot", a + 0.2, WHITE), LB2("interceptors work", a + 1.0, BLUE, 1)], highlight=[HL_JP], clock="T+08:00", clockLabel="AFTER FIRST LAUNCH", clockRate=0,
    rings=[ring(KAD, 8, 0.0, "", ORANGE)], cities=[city(KAD, "Kadena", a + 0.1, RED, "target", 6)])
a = tTh34
reg("c4-866", a, S("p35"), [("s", [123.0, 27.5], 1600), ("e", [124.0, 27.2], 1100)],
    [LB2("Launcher about 866 km away", a + 0.2, YELLOW)], clock="T+08:00", clockLabel="AFTER FIRST LAUNCH", clockRate=0, highlight=[HL_JP],
    lines=[line(L_KD, KAD, a + 0.2, a + 2.2, AMBER, True, "866 km")], cities=[city(L_KD, "Launcher (simulated)", a + 0.2, AMBER, "base", 6), city(KAD, "Kadena", a + 0.5, BLUE, "base", 6)])
a = S("p35")
tYo35 = W("p35", "Yokosuka")
tSv = W("p35", "seven")
reg("c4-m10", a, tSv, [("s", [128.0, 27.5], 800), ("e", KAD, 300)],
    [LB2("A little after minute ten", a + 0.2, YELLOW), LB2("DF-17 lands at Kadena", a + 1.2, RED, 1)], highlight=[HL_JP], **clk("T+09:30", 6),
    **flights([(L_17, KAD, a + 0.3, a + 4.0, "DF-17", RED)]), rings=[ring(KAD, 6, a + 4.0, "Impact", ORANGE)], cities=[city(KAD, "Kadena", a + 0.3, BLUE, "target", 6)])
a = tSv
reg("c4-m10b", a, tYo35 - 0.5, [("s", KAD, 300), ("e", KAD, 190)],
    [LB2("Seven minutes of flight", a + 0.2, WHITE)], highlight=[HL_JP], clock="T+10:20", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(KAD, 6, 0.0, "", ORANGE)],
    cities=[city(KAD, "Kadena", a + 0.1, RED, "target", 6)])
a = tYo35 - 0.5
tAf = W("p35", "after")
reg("c4-m11", a, W("p35", "home"), [("s", [137.0, 34.0], 1000), ("e", YOK, 300)],
    [LB2("A little before minute eleven", a + 0.2, YELLOW), LB2("DF-26 lands at Yokosuka", a + 1.2, RED, 1)], highlight=[HL_JP], **clk("T+10:20", 6),
    **flights([(L_YK, YOK, a + 0.2, a + 1.8, "DF-26", RED)]), rings=[ring(YOK, 6, a + 1.8, "Impact", ORANGE)], cities=[city(YOK, "Yokosuka", a + 0.3, BLUE, "target", 6)])
a = W("p35", "home")
reg("c4-home", a, W("p35", "We"), [("s", YOK, 300), ("e", [139.9, 35.0], 600)],
    [LB2("Home port of the only US carrier based in Japan", a + 0.2, BLUE)], highlight=[HL_JP], clock="T+10:42", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(YOK, 6, 0.0, "", ORANGE)],
    cities=[city(YOK, "Yokosuka", a + 0.1, RED, "target", 6)])
a = W("p35", "We")
reg("c4-sea", a, S("p36"), [("s", [139.9, 35.0], 600), ("e", [141.0, 32.0], 1500)],
    [LB2("We assume the carrier is at sea", a + 0.2, YELLOW)], highlight=[HL_JP], clock="T+10:42", clockLabel="AFTER FIRST LAUNCH", clockRate=0, cities=[city(YOK, "Yokosuka", a + 0.1, BLUE, "base", 6)],
    ships=[{"path": [YOK, [142.5, 31.0]], "t0": 0.2, "t1": 4.0, "kind": "us", "color": BLUE, "label": "Carrier", "size": 2.8, "t": 0.2, "wake": True}])
a = S("p36")
tNe = W("p36", "nearly")
reg("c4-far", a, tNe, [("s", [130.0, 21.0], 5600), ("e", [134.0, 19.0], 4600)],
    [LB2("Guam is farther", a + 0.2, WHITE)], highlight=[HL_CN], countryLabels=CL, **clk("T+10:42", 0, "AFTER FIRST LAUNCH"), cities=[city(AND, "Guam", a + 0.3, BLUE, "base", 6)],
    lines=[line(L_AP, APRA, a + 0.3, a + 3.0, AMBER, True), line(L_N, AND, a + 0.6, a + 3.2, AMBER, True)])
a = tNe
reg("c4-14", a, S("p37"), [("s", [134.0, 19.0], 4600), ("e", [138.0, 17.0], 3200)],
    [LB2("12.7 to 14.5 minutes of flight", a + 0.2, YELLOW)], highlight=[HL_CN], clock="T+10:42", clockLabel="AFTER FIRST LAUNCH", clockRate=0,
    cities=[city(L_AP, "12.7 min", a + 0.3, AMBER, "base", 6), city(L_N, "13.3 min", a + 0.7, AMBER, "base", 6), city(L_CA, "14.5 min", a + 1.1, AMBER, "base", 6), city(AND, "Guam", a + 0.1, BLUE, "base", 6)],
    lines=[line(L_CA, AND, a + 0.3, a + 3.2, AMBER, True)])
a = S("p37")
tDet, tNo = W("p37", "detonates"), W("p37", "nothing")
reg("c4-m13", a, tDet, [("s", AND, 500), ("e", AND, 150)],
    [LB2("Minute thirteen", a + 0.2, YELLOW), LB2("01:43 in the morning on Guam", a + 1.4, WHITE, 1)], highlight=[], **clk("T+12:00", 22),
    **flights([(L_N, AND, a + 0.1, tDet + 0.2, "DF-26", YELLOW)]), cities=[city(AND, "Andersen AFB", a + 0.4, BLUE, "target", 6)])
a = tDet
reg("c4-flash", a, tNo, [("s", AND, 60), ("e", AND, 50)],
    [LB2("A DF-26 detonates over Andersen", a + 0.5, YELLOW)], clock="T+13:18", clockLabel="AFTER FIRST LAUNCH", clockRate=0, burst={"at": AND, "t": 0.1, "km": 4, "fade": 4},
    rings=[ring(AND, 4, a + 0.7, "", RED)], cities=[city(AND, "Andersen AFB", a + 0.5, RED, "target", 6)])
a = tNo
reg("c4-nothing", a, S("p38"), [("s", AND, 180), ("e", [144.8, 13.5], 260)],
    [LB2("Nothing stops it, by assumption", a + 0.2, WHITE), LB2("One missile against a wave", W("p37", "one", 2), YELLOW, 1)], clock="T+13:18", clockLabel="AFTER FIRST LAUNCH", clockRate=0,
    rings=[ring(AND, 4, 0.0, "", RED)], cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = S("p38")
tSe, tNa38, tCo38 = W("p38", "Seconds"), W("p38", "Naval"), W("p38", "conventional")
reg("c4-cold", a, tSe, [("s", [144.8, 13.5], 260), ("e", [144.8, 13.5], 340)],
    [LB2("The flash is the cold open", a + 0.2, YELLOW)], clock="T+13:18", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(AND, 4, 0.0, "", RED)],
    cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = tSe
reg("c4-14apra", a, tCo38 - 0.3, [("s", [144.7, 13.5], 340), ("e", [144.7, 13.45], 220)],
    [LB2("About minute fourteen", a + 0.2, YELLOW), LB2("Naval Base Guam is hit", tNa38, RED, 1)], clock="T+13:42", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(AND, 4, 0.0, "", RED), ring(APRA, 5, tNa38 + 0.5, "Impact", ORANGE)],
    cities=[city(APRA, "Naval Base Guam", a + 0.1, RED, "target", 6), city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = tCo38 - 0.3
reg("c4-145", a, S("p39"), [("s", [144.8, 13.5], 260), ("e", AND, 160)],
    [LB2("Fourteen and a half", a + 0.2, YELLOW), LB2("Conventional DF-26 on Andersen", a + 0.8, RED, 1)], clock="T+14:30", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(AND, 4, 0.0, "", RED), ring(AND, 5, a + 1.5, "Impact", ORANGE)],
    cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = S("p39")
reg("c4-cruise", a, S("p40"), [("s", [126.0, 27.5], 900), ("e", KAD, 300)],
    [LB2("About minute nineteen", a + 0.1, YELLOW), LB2("The CJ-20 reaches Kadena", a + 1.0, RED, 1)], highlight=[HL_JP], **clk("T+18:00", 12),
    **flights([(L_H6, KAD, a + 0.2, a + 3.6, "CJ-20", RED)]), rings=[ring(KAD, 6, a + 3.6, "Impact", ORANGE)], cities=[city(KAD, "Kadena", a + 0.3, BLUE, "target", 6)])
a = S("p40")
tGl, tYo40, tNa40, tLa40, tSe40 = W("p40", "glider"), W("p40", "Yokosuka"), W("p40", "Naval"), W("p40", "cruise"), W("p40", "Seven")
reg("c4-order1", a, tYo40, [("s", [129.0, 26.5], 1500), ("e", [128.0, 27.0], 900)],
    [LB2("In order of arrival", a + 0.1, YELLOW), LB2("1  DF-26 at Kadena", a + 1.2, RED, 1), LB2("2  DF-17 at Kadena", tGl, RED, 2)], highlight=[HL_JP], clock="", cities=[city(KAD, "Kadena", a + 0.4, BLUE, "target", 6)])
a = tYo40
reg("c4-order2", a, tNa40, [("s", [139.0, 31.0], 1600), ("e", [141.0, 25.0], 3300)],
    [LB2("3  DF-26 at Yokosuka", a + 0.1, RED), LB2("4  The nuclear DF-26 at Andersen", W("p40", "nuclear"), YELLOW, 1)], highlight=[HL_JP], clock="",
    cities=[city(YOK, "Yokosuka", a + 0.2, RED, "target", 6), city(AND, "Andersen", W("p40", "nuclear"), YELLOW, "target", 6)])
a = tNa40
reg("c4-order3", a, tLa40, [("s", [144.8, 13.5], 220), ("e", [144.8, 13.5], 150)],
    [LB2("5  DF-26 at Naval Base Guam", a + 0.1, RED), LB2("6  The conventional DF-26 at Andersen", W("p40", "conventional"), RED, 1)], clock="",
    cities=[city(APRA, "Naval Base Guam", a + 0.2, RED, "target", 6), city(AND, "Andersen", W("p40", "conventional"), RED, "target", 6)])
a = tLa40
reg("c4-order4", a, tSe40, [("s", [126.0, 27.0], 1000), ("e", KAD, 320)],
    [LB2("7  Last: the cruise missile", a + 0.1, RED)], highlight=[HL_JP], clock="", cities=[city(KAD, "Kadena", a + 0.2, RED, "target", 6)])
a = tSe40
add(id="c4-bars", type="bars", start=a, end=S("p41"), tag="SIMULATION", title="Minutes from first launch to impact", sub="seven weapons, four bases, eleven minutes first to last", source="Scenario engine (estimates)",
    bars=[{"label": "DF-26, Kadena", "value": 8.0, "display": "8.0", "color": RED}, {"label": "DF-17, Kadena", "value": 10.3, "display": "10.3", "color": RED}, {"label": "DF-26, Yokosuka", "value": 10.7, "display": "10.7", "color": RED},
          {"label": "DF-26 nuclear, Andersen", "value": 13.3, "display": "13.3", "color": YELLOW}, {"label": "DF-26, Naval Base Guam", "value": 13.7, "display": "13.7", "color": RED},
          {"label": "DF-26, Andersen", "value": 14.5, "display": "14.5", "color": RED}, {"label": "CJ-20, Kadena", "value": 18.7, "display": "18.7", "color": ORANGE}])
a = S("p41")
reg("c4-so", a, S("p42"), [("s", [144.8, 13.5], 150), ("e", AND, 200)],
    [LB2("What did one warhead reach?", a + 0.2, YELLOW)], clock="T+13:18", clockLabel="AFTER FIRST LAUNCH", clockRate=0, rings=[ring(AND, 4, 0.0, "", RED)],
    cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = chapter("c5-card", S("p42"), 3.5, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
CK = dict(clock="01:43", clockLabel="GUAM TIME", clockRate=0)
cty("c5-fire", a, S("p43"), [("s", AND, 3000), ("e", AND, 4800)],
    [dict(ring(AND, FX["fireball_km"], a + 0.3, "Fireball", WHITE), angle=100)],
    [LB("In the air, above the flight line", -0.30, 0.31, a + 0.2, WHITE), LB("Fireball: about 300 m across", -0.30, 0.23, W("p42", "fireball") if False else a + 2.0, YELLOW)], flashT=0.1, **CK)
a = S("p43")
tIn43 = W("p43", "inner")
cty("c5-20psi", a, tIn43, [("s", AND, 3600), ("e", AND, 5000)],
    [dict(ring(AND, FX["fireball_km"], 0, "Fireball", WHITE), angle=100), dict(ring(AND, FX["psi20_km"], W("p43", "twenty"), "20 psi", RED), angle=225)],
    [LB("Out to 300 m: 20 psi", -0.30, 0.31, a + 0.2, YELLOW)], **CK)
a = tIn43
cty("c5-inner", a, S("p44"), [("s", AND, 5000), ("e", AND, 6400)],
    [dict(ring(AND, FX["fireball_km"], 0, "Fireball", WHITE), angle=100), dict(ring(AND, FX["psi20_km"], 0, "20 psi", RED), angle=225)],
    [LB("The inner ring sits on the base", -0.30, 0.31, a + 0.2, WHITE)], **CK)
a = S("p44")
tMo = W("p44", "Most")
cty("c5-5psi", a, tMo, [("s", AND, 5000), ("e", AND, 9000)],
    [dict(ring(AND, FX["fireball_km"], 0, "Fireball", WHITE), angle=100), dict(ring(AND, FX["psi20_km"], 0, "20 psi", RED), angle=225), dict(ring(AND, FX["psi5_km"], a + 0.8, "5 psi", RED), angle=300)],
    [LB("1.5 km: 5 psi", -0.30, 0.31, a + 0.3, YELLOW), LB("About 6.7 square km", -0.30, 0.23, W("p44", "six"), WHITE)], **CK)
a = tMo
cty("c5-homes", a, S("p45"), [("s", AND, 9000), ("e", AND, 7500)],
    [dict(ring(AND, FX["psi20_km"], 0, "20 psi", RED), angle=225), dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300)],
    [LB("Most homes in it collapse", -0.30, 0.31, a + 0.2, WHITE), LB("Along much of one runway", -0.30, 0.23, W("p44", "reaches"), YELLOW)], **CK)
a = S("p45")
cty("c5-miss", a, S("p46"), [("s", AND, 5200), ("e", AND, 3600)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=60), dict(ring(AND, 0.45, a + 3.0, "450 m miss", WHITE, True), angle=200)],
    [LB("Remember the accuracy estimate", -0.30, 0.31, a + 0.2, WHITE), LB("A 450 m miss still lands inside", -0.30, 0.23, W("p45", "miss"), YELLOW)], **CK)
a = S("p46")
tOt = W("p46", "other")
reg("c5-total", a, tOt, [("s", [136.0, 24.0], 4600), ("e", [140.0, 20.0], 3400)],
    [LB2("Ten kilotons: the whole nuclear total", a + 0.2, YELLOW)], clock="", highlight=[HL_JP], cities=[city(AND, "Andersen: 10 kt", a + 0.4, YELLOW, "target", 6)])
a = tOt
reg("c5-six", a, S("p47"), [("s", [136.0, 24.0], 4600), ("e", [133.0, 26.0], 3200)],
    [LB2("Six conventional weapons", a + 0.2, RED), LB2("No blast rings from the engine", W("p46", "blast"), WHITE, 1)], clock="", highlight=[HL_JP], countryLabels=[CL_JP],
    cities=[city(KAD, "Kadena (3)", a + 0.4, RED, "target", 6), city(YOK, "Yokosuka", a + 0.8, RED, "target", 6), city(APRA, "Naval Base", a + 1.2, RED, "target", 6), city(AND, "Andersen", a + 1.6, RED, "target", 6)])
a = S("p47")
cty("c5-burn", a, S("p48"), [("s", AND, 5000), ("e", AND, 7500)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300), dict(ring(AND, FX["thermal3_km"], a + 0.5, "Burns", ORANGE), angle=40)],
    [LB("Just past it, at 1.6 km", -0.30, 0.31, a + 0.2, WHITE), LB("Bare skin: third-degree burns", -0.30, 0.23, W("p47", "bare"), ORANGE)], **CK)
a = S("p48")
tRo = W("p48", "roughly")
tWi = W("p48", "windows")
cty("c5-1psi", a, tWi, [("s", AND, 8000), ("e", AND, 11000)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300), dict(ring(AND, FX["thermal3_km"], 0, "Burns", ORANGE), angle=40), dict(ring(AND, FX["psi1_km"], a + 0.6, "1 psi", YELLOW), angle=135)],
    [LB("Nearly 4 km: 1 psi", -0.30, 0.31, a + 0.2, YELLOW)], **CK)
a = tWi
cty("c5-windows", a, tRo, [("s", AND, 11000), ("e", AND, 14000)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300), dict(ring(AND, FX["thermal3_km"], 0, "Burns", ORANGE), angle=40), dict(ring(AND, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135)],
    [LB("Windows break", -0.30, 0.31, a + 0.2, WHITE)], **CK)
a = tRo
cty("c5-nine", a, S("p49"), [("s", AND, 14000), ("e", [144.8, 13.52], 34000)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300), dict(ring(AND, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135)],
    [LB("About 49 square km", -0.30, 0.31, a + 0.2, WHITE), LB("About 9% of the island", -0.30, 0.23, W("p48", "nine"), YELLOW)], **CK)
a = S("p49")
cty("c5-naval", a, S("p50"), [("s", [144.8, 13.52], 34000), ("e", [144.78, 13.5], 52000)],
    [dict(ring(AND, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135)],
    [LB("Naval Base Guam: outside every ring", -0.30, 0.31, a + 0.2, WHITE), LA(APRA, "Naval Base Guam", a + 0.8, BLUE), LB("So is almost all of the island", -0.30, 0.23, W("p49", "So"), YELLOW)], **CK)
a = S("p50")
cty("c5-toll", a, S("p51"), [("s", AND, 9000), ("e", AND, 6000)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300), dict(ring(AND, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135)],
    [LB("No death toll", -0.30, 0.31, a + 0.2, YELLOW), LB("No published study supplies one", -0.30, 0.23, W("p50", "published"), WHITE)], caption="We will not invent a number.", **CK)
a = S("p51")
reg("c5-pacific", a, S("p52"), [("s", [133.0, 23.0], 4200), ("e", [131.0, 24.0], 5200)],
    [LB2("Guam: the 4 km ring", a + 0.2, RED), LB2("Kadena and Yokosuka beyond", a + 2.2, BLUE, 1)], clock="01:43", clockLabel="GUAM TIME", clockRate=0, highlight=[HL_CN, HL_JP], countryLabels=[CL_CN, CL_JP],
    rings=[ring(AND, 4, a + 0.2, "", RED)], lines=[line(L_N, AND, a + 0.1, a + 2.5, RED, True)], cities=[city(L_N, "Launch area", a + 0.1, AMBER, "base", 6), city(AND, "GUAM", a + 0.2, RED, "target", 6), city(KAD, "Kadena", a + 2.2, BLUE, "base", 6), city(YOK, "Yokosuka", a + 3.6, BLUE, "base", 6)])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p52"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
tIn = W("p52", "In")
reg("c6-q", a, W("p52", "published"), [("s", [136.0, 22.0], 4600), ("e", [134.0, 25.0], 3600)],
    [LB2("How many fighters can still take off?", a + 0.2, YELLOW)], clock="DAY AFTER", clockLabel="WESTERN PACIFIC", clockRate=0, highlight=[HL_JP], cities=bases(a, 0.4, 0.5))
a = W("p52", "published")
reg("c6-range", a, W("p52", "none"), [("s", [134.0, 25.0], 3600), ("e", [140.0, 22.0], 3000)],
    [LB2("Published studies give a range", a + 0.2, WHITE)], clock="DAY AFTER", clockLabel="WESTERN PACIFIC", clockRate=0, highlight=[HL_JP], cities=bases(a, 0.1, 0.2))
a = W("p52", "none")
reg("c6-none", a, S("p53"), [("s", [144.8, 13.5], 200), ("e", AND, 150)],
    [LB2("None covers a nuclear burst", a + 0.2, RED), LB2("on a flight line", W("p52", "flight"), WHITE, 1)], clock="DAY AFTER", clockLabel="GUAM", clockRate=0, rings=[ring(AND, 4, 0.0, "", RED)], cities=[city(AND, "Andersen AFB", a + 0.1, RED, "target", 6)])
a = S("p53")
tSt, tFo = W("p53", "Stimson"), W("p53", "Japan")
cty("c6-dark", a, tSt, [("s", AND, 5000), ("e", AND, 3600)],
    [dict(ring(AND, FX["psi5_km"], 0, "5 psi", RED), angle=300)],
    [LB("The runway under the rings goes dark", -0.30, 0.31, a + 0.2, RED)], clock="DAY AFTER", clockLabel="GUAM", clockRate=0)
a = tSt
add(id="c6-days", type="bars", start=a, end=a + 5.2, tag="SIMULATION", title="Fighter operations lost, in days", sub="Stimson Center cratering study: one estimate with assumed inputs", source="Stimson Center, Cratering Effects, December 2024",
    bars=[{"label": "Guam", "value": 2, "display": "nearly 2 days", "color": BLUE}, {"label": "Japan", "value": 12, "display": "about 12 days", "color": BLUE}])
a += 5.2
reg("c6-est", a, S("p54"), [("s", [138.0, 24.0], 3600), ("e", [136.0, 27.0], 3000)],
    [LB2("One estimate, assumed inputs", a + 0.2, YELLOW), LB2("Not outcomes", a + 1.0, WHITE, 1)], clock="DAY AFTER", clockLabel="WESTERN PACIFIC", clockRate=0, highlight=[HL_JP], source="Stimson Center, December 2024", cities=bases(a, 0.2, 0.4))
a = S("p54")
add(id="c6-rand", type="bars", start=a, end=a + 4.6, tag="SIMULATION", title="Missiles at one base", sub="an older RAND estimate against our hour", source="RAND-style estimates cited 2016; scenario engine",
    bars=[{"label": "RAND, older: low", "value": 50, "display": "50", "color": AMBER}, {"label": "RAND, older: high", "value": 100, "display": "100", "color": AMBER}, {"label": "Our hour, all bases", "value": 7, "display": "7", "color": RED}])
a += 4.6
reg("c6-ours", a, S("p55"), [("s", [138.0, 22.0], 4200), ("e", [142.0, 20.0], 3000)],
    [LB2("Our hour: seven weapons in total", a + 0.2, RED)], clock="DAY AFTER", clockLabel="WESTERN PACIFIC", clockRate=0, highlight=[HL_JP], cities=bases(a, 0.1, 0.2))
a = S("p55")
tBy, tJa, tOn = W("p55", "By"), W("p55", "Japan", 2), W("p55", "One", 1)
tAc55 = W("p55", "account")
reg("c6-tank", a, tBy, [("s", [136.0, 34.0], 2400), ("e", [138.0, 31.0], 1800)],
    [LB2("Tanker routes over Japan", a + 0.2, WHITE)], clock="DAY AFTER", clockLabel="JAPAN", clockRate=0, highlight=[HL_JP], countryLabels=[CL_JP], cities=[city(YOK, "Yokosuka", a + 0.5, BLUE, "base", 6)])
a = tBy
reg("c6-month", a, tJa, [("s", [138.0, 31.0], 1800), ("e", [136.0, 33.0], 2800)],
    [LB2("Tankers: unable to operate", a + 0.2, YELLOW), LB2("for over a month", W("p55", "month"), RED, 1)], clock="DAY AFTER", clockLabel="JAPAN", clockRate=0, highlight=[HL_JP], source="Stimson Center, December 2024")
a = tJa
reg("c6-36", a, tAc55 - 0.2, [("s", [136.0, 35.0], 2400), ("e", [138.0, 33.0], 1700)],
    [LB2("About 36 military airfields", a + 0.2, BLUE), LB2("About 140 aircraft shelters", W("p55", "hundred"), YELLOW, 1)], clock="DAY AFTER", clockLabel="JAPAN", clockRate=0, highlight=[HL_JP], source="One estimate; Asia Times", cities=[city(KAD, "Kadena", a + 0.3, BLUE, "base", 6)])
a = tAc55 - 0.2
reg("c6-crater", a, S("p56"), [("s", [135.0, 33.0], 2200), ("e", KAD, 700)],
    [LB2("Air Force crater repair plan", a + 0.2, BLUE), LB2("24 to 36 hours", a + 1.2, YELLOW, 1), LB2("One account", a + 2.4, WHITE, 2)], clock="DAY AFTER", clockLabel="JAPAN", clockRate=0, highlight=[HL_JP], source="Mitchell Institute; Air Force",
    cities=[city(KAD, "Kadena", a + 0.4, BLUE, "base", 6), city(YOK, "Yokosuka", a + 1.2, BLUE, "base", 6)])
a = S("p56")
tAir = W("p56", "airburst")
cty("c6-noplume", a, tAir, [("s", AND, 16000), ("e", AND, 9000)], [],
    [LB("No plume on this map", -0.30, 0.31, a + 0.2, WHITE)], clock="DAY AFTER", clockLabel="GUAM", clockRate=0)
a = tAir
cty("c6-fallout", a, S("p57"), [("s", AND, 9000), ("e", AND, 20000)],
    [dict(ring(AND, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135)],
    [LB("An airburst of this size", -0.30, 0.31, a + 0.2, WHITE), LB("Little local fallout: none drawn", -0.30, 0.23, W("p56", "little"), YELLOW)], clock="DAY AFTER", clockLabel="GUAM", clockRate=0)
a = S("p57")
tIts, tOpt = W("p57", "Its"), W("p57", "options")
reg("c6-dc", a, tIts, [("s", [-95.0, 38.0], 5600), ("e", [-85.0, 38.0], 4000)],
    [LB2("The decision moves to Washington", a + 0.2, BLUE)], clock="T+19:00", clockLabel="CLOCK STOPPED", clockRate=0, highlight=[HL_US], countryLabels=[cl(USA_, "UNITED STATES", BLUE)], cities=[city(WASH, "Washington", a + 0.4, BLUE, "base", 6)])
a = tIts
reg("c6-policy", a, tOpt, [("s", [-85.0, 38.0], 4000), ("e", [-100.0, 38.0], 6000)],
    [LB2("Nuclear use only in extreme circumstances", a + 0.2, WHITE), LB2("To defend vital interests and allies", W("p57", "defend"), BLUE, 1)], clock="T+19:00", clockLabel="CLOCK STOPPED", clockRate=0, highlight=[HL_US], cities=[city(WASH, "Washington", a + 0.1, BLUE, "base", 6)])
a = tOpt
tTr, tCv, tTa, tWe57 = W("p57", "Trident"), W("p57", "conventional"), W("p57", "talks"), W("p57", "stop")
reg("c6-opt1", a, tCv, [("s", [-130.0, 30.0], 9000), ("e", [-150.0, 28.0], 9500)],
    [LB2("Option: a low-yield Trident", a + 0.2, BLUE), LB2("About 5 kilotons", tTr, YELLOW, 1)], clock="T+19:00", clockLabel="CLOCK STOPPED", clockRate=0, highlight=[HL_US], cities=[city(WASH, "Washington", a + 0.1, BLUE, "base", 6), city(HAWAII, "Hawaii", a + 0.6, BLUE, "base", 6)])
a = tCv
reg("c6-opt2", a, tWe57, [("s", [150.0, 24.0], 5200), ("e", [140.0, 22.0], 3800)],
    [LB2("Option: a conventional answer", a + 0.2, WHITE), LB2("Option: talks", tTa, TEAL, 1)], clock="T+19:00", clockLabel="CLOCK STOPPED", clockRate=0, cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6), city(KAD, "Kadena", a + 0.4, BLUE, "base", 6)])
a = tWe57
reg("c6-stop", a, S("p58"), [("s", [140.0, 22.0], 3800), ("e", [144.0, 16.0], 2000)],
    [LB2("We stop the clock before it chooses", a + 0.2, YELLOW)], clock="T+19:00", clockLabel="CLOCK STOPPED", clockRate=0, cities=[city(AND, "Guam", a + 0.1, BLUE, "base", 6)])
a = S("p58")
num("c6-bill", a, a + 5.0, "$10 TRILLION", label="Bloomberg Economics: first-year cost of a Taiwan war", sub="about, as an estimate", color=YELLOW, tag="REAL DATA", countTo=10, prefix="$", suffix=" TRILLION", source="Bloomberg Economics")
a += 5.0
reg("c6-bill2", a, S("p59"), [("s", [121.0, 24.0], 1500), ("e", [123.0, 23.0], 2200)],
    [LB2("The bill is not on the map", a + 0.2, WHITE)], clock="", highlight=[HL_TW, HL_CN], countryLabels=[cl(TW_, "TAIWAN", TEAL), CL_CN])
a = S("p59")
glob("c6-last", a, S("p60"), [("s", 14.0, 143.0, 1700), ("e", 22.0, 135.0, 3200)],
     markers=[{"at": AND, "label": "Guam", "color": BLUE, "t": 0.2, "kind": "base"}, {"at": KAD, "label": "Kadena", "color": BLUE, "t": 1.4, "kind": "base"}, {"at": YOK, "label": "Yokosuka", "color": BLUE, "t": 2.4, "kind": "base"}],
     clock="", clockRate=0)

# ================================================================== End slate
add(id="endslate", type="endslate", start=S("p60"), end=END, tag="", title="One warhead over London", line="Next on the map: London, one warhead, and the four UK submarines.")

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
    if A.get("tag") != B.get("tag") or (A.get("source") != B.get("source") and A.get("source") and B.get("source")):
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
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p20") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p20") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": FLASH + 0.1, "gain_db": -6}]
                    + [{"src": "boom.mp3", "t": s["start"] + s["burst"]["t"], "gain_db": -6} for s in shots if s.get("burst") and s["id"] != "open-burst"]
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
