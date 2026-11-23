"""Director pass for episode 016: builds episode.json from narration/timing.json and words.json.

Run from the studio root:  python -m studio shotlist 016-nato-answer-russian-nuke-ukraine
Payoff first: the 20 kt airburst over open farmland in central Ukraine inside 3 s (under the banner), the run-up from
a simulated launch site, real data and history, the 72-hour NATO decision, ring by ring, the day after.
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
    add(id=sid, type="city", start=a, end=b, tag=tag, city="staging-area-sim", view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, gz=GZ, camera=c, rings=rs, labels=labels, **kw)


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
UA, RU, BY, PL, CU, US = "804", "643", "112", "616", "192", "840"
NATO_E = ["616", "440", "428", "233", "642", "703", "100", "276", "348", "203"]


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


HL_UA, HL_RU, HL_BY = hl(UA, TEAL, 0.12), hl(RU, AMBER, 0.07), hl(BY, AMBER, 0.05)
HL_NATO = [hl(i, BLUE, 0.10) for i in NATO_E]
CL_UA, CL_RU, CL_BY, CL_PL = cl(UA, "UKRAINE", TEAL), cl(RU, "RUSSIA", AMBER), cl(BY, "BELARUS", AMBER), cl(PL, "POLAND", BLUE)
LEG = [{"text": "UKRAINE", "color": TEAL}, {"text": "RUSSIA", "color": AMBER}, {"text": "NATO", "color": BLUE}]

TGT = sc["strikes"][0]
GZ = [TGT["target_lon"], TGT["target_lat"]]
LAUNCH = [TGT["launch_lon"], TGT["launch_lat"]]
FX = TGT["effects"]
KYIV, BRU, WARS, MOS, MINSK = [30.52, 50.45], [4.35, 50.85], [21.01, 52.23], [37.62, 55.75], [27.56, 53.9]
HAV, WASH, SEV, KURSK = [-82.37, 23.13], [-77.04, 38.9], [33.52, 44.62], [36.19, 51.73]
VILN, RIGA, BUCH, BRAT = [25.28, 54.69], [24.1, 56.95], [26.1, 44.43], [17.1, 48.15]
SRC_T = "Russia defence ministry; Reuters; AP"
SRC_B = "Bulletin of the Atomic Scientists; CFR"


def LB2(text, t, color=WHITE, row=0, col=-0.30):
    return LB(text, col, 0.31 - 0.085 * row, t, color)


def clk(text, label, rate=0):
    return dict(clock=text, clockLabel=label, clockRate=rate)


def fl(a, b, p=LAUNCH, q=GZ, label="Iskander-M", col=RED, t0=None):
    t0 = a if t0 is None else t0
    return dict(ships=[ship([p, q], t0, b - 0.1, label, col, 2.6)], lines=[line(p, q, t0, b - 0.1, col, True)])


EUROPE = [("s", [20.0, 50.0], 3200), ("e", [22.0, 50.5], 2500)]

# ================================================================== Cold open [SIMULATION]
FLASH = 2.0
reg("open-run", 0, FLASH, [("s", [35.0, 50.6], 700), ("e", [34.6, 50.4], 520)],
    [LB("Central Ukraine", -0.02, -0.26, None, RED), LB("Kursk region", 0.12, 0.2, None, AMBER)],
    clock="T-03:18", clockLabel="TO IMPACT", clockRate=100, highlight=[HL_UA, HL_RU], countryLabels=[CL_UA, CL_RU],
    ships=[ship([LAUNCH, GZ], 0.0, FLASH - 0.05, "Iskander-M", RED, 2.8)], lines=[line(LAUNCH, GZ, 0.0, FLASH - 0.05, RED, True)],
    cities=[city(GZ, "TARGET", None, RED, "target", 6), city(LAUNCH, "Launcher (simulated)", None, AMBER, "base", 6)])
a = FLASH
LOKH, KOMY = [33.27418, 50.35952], [33.67962, 50.1838]
reg("open-burst", a, 5.0, [("s", GZ, 210), ("e", GZ, 160)],
    [LB("20 kiloton airburst", 0.10, 0.06, a + 0.9, YELLOW), LB("Open farmland, central Ukraine", 0.10, -0.02, a + 1.3, WHITE)],
    clock="13:43", clockLabel="UKRAINE TIME", clockRate=0, burst={"at": GZ, "t": 0.1, "km": 4, "fade": 4},
    rings=[ring(GZ, 4, a + 0.7, "", RED)], cities=[city(GZ, "", a + 0.5, RED, "target", 6), city(KOMY, "Komyshnia", a + 1.2, TEAL, "base", 6), city(LOKH, "Lokhvytsia", a + 1.8, TEAL, "base", 6)])
a = 5.0
cty("open-rings", a, S("p02"), [("s", GZ, 7000), ("e", GZ, 15000)],
    [dict(ring(GZ, FX["fireball_km"], a + 0.3, "Fireball", WHITE), angle=100), dict(ring(GZ, FX["psi5_km"], a + 1.2, "5 psi", RED), angle=225), dict(ring(GZ, FX["psi1_km"], a + 2.2, "Windows", ORANGE), angle=135)],
    [LB("Open farmland", -0.30, 0.30, a + 0.3, WHITE)], clock="13:43", clockLabel="UKRAINE TIME", clockRate=0,
    caption="Simulation: it has not happened.")
a = S("p02")
tSim, tPub, tNot = W("p02", "simulation"), W("p02", "published"), W("p02", "not")
reg("open-sim", a, S("p03"), [("s", [31.0, 49.5], 1400), (tNot, [34.0, 50.0], 900), ("e", [31.0, 50.3], 1500)],
    [LB2("A simulation", tSim, YELLOW), LB2("Built from published numbers", tPub, WHITE, 1), LB2("It has not happened", tNot + 0.1, RED, 2)], clock="13:43", clockLabel="UKRAINE TIME", highlight=[HL_UA], countryLabels=[CL_UA],
    cities=[city(GZ, "Target (simulated)", a + 0.2, RED, "target", 6), city(KYIV, "Kyiv", a + 0.8, TEAL, "base", 6)])
a = S("p03")
tOne, tTwo = W("p03", "One"), W("p03", "Two")
reg("open-launch", a, tTwo, [("s", [38.0, 51.5], 1300), (tOne, LAUNCH, 800), ("e", [35.0, 50.8], 900)],
    [LB2("Three minutes earlier", a + 0.1, YELLOW), LB2("Kursk region, Russia", a + 1.6, AMBER, 1), LB2("One Iskander-M", tOne, WHITE, 2)], clock="T+00:00", clockLabel="LAUNCH", highlight=[HL_RU, HL_UA], countryLabels=[CL_RU, CL_UA],
    cities=[city(LAUNCH, "Launcher (simulated)", a + 0.6, AMBER, "base", 6), city(GZ, "Target (simulated)", tOne + 0.0, RED, "target", 6)])
a = tTwo
reg("open-213", a, S("p04"), [("s", [35.0, 50.7], 600), ("e", [34.9, 50.6], 480)],
    [LB2("213 km to fly", a + 0.2, YELLOW)], highlight=[HL_UA, HL_RU], **clk("T+00:00", "FLIGHT", 66), **fl(a, S("p04"), t0=a + 0.2),
    cities=[city(GZ, "Target (simulated)", a + 0.3, RED, "target", 6)])
a = S("p04")
tBut, tWhat = W("p04", "But"), W("p04", "What")
reg("open-nobody", a, tBut, [("s", [17.5, 50.6], 2900), ("e", [18.5, 50.6], 2500)],
    [LB2("Nobody has three minutes to decide", a + 0.3, YELLOW)], highlight=[HL_UA] + HL_NATO,
    cities=[city(KYIV, "Kyiv", a + 0.4, TEAL, "base", 6), city(BRU, "Brussels", a + 1.4, BLUE, "base", 6)])
a = tBut
reg("open-table", a, tWhat, [("s", BRU, 1100), ("e", BRU, 600)],
    [LB2("After the flash: one question", a + 0.2, YELLOW), LB2("on every NATO table", a + 1.5, WHITE, 1)], highlight=HL_NATO,
    cities=[city(BRU, "NATO headquarters", a + 0.4, BLUE, "base", 6)])
a = tWhat
reg("open-q", a, S("p05"), [("s", [20.0, 51.0], 3200), ("e", [27.0, 50.5], 2200)],
    [LB2("What does the alliance do?", a + 0.2, WHITE), LB2("How long before it has to choose?", W("p04", "how"), YELLOW, 1)], highlight=[HL_UA] + HL_NATO, legend=LEG,
    cities=[city(BRU, "Brussels", a + 0.1, BLUE, "base", 6), city(GZ, "", a + 0.1, RED, "target", 6)])

# ================================================================== Chapter 01 [REAL DATA] a missile that already exists
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "A missile that already exists", "REAL DATA")
tBel, tRus5 = W("p05", "Belarusian"), W("p05", "Russia's")
reg("c1-ex", a, tBel, [("s", [28.0, 54.0], 2000), ("e", [30.0, 54.5], 1500)],
    [LB2("May 2026: a three-day nuclear exercise", a + 0.2, YELLOW), LB2("Russia and Belarus", a + 1.5, AMBER, 1)], tag="REAL DATA", source=SRC_T, clock="MAY 2026", clockLabel="EXERCISE",
    highlight=[HL_RU, HL_BY], countryLabels=[CL_RU, CL_BY])
a = tBel
reg("c1-fire", a, tRus5, [("s", MINSK, 700), ("e", [27.0, 53.2], 1100)],
    [LB2("Belarusian troops fire an Iskander", a + 0.2, WHITE)], tag="REAL DATA", source=SRC_T, clock="MAY 2026", clockLabel="EXERCISE", highlight=[HL_BY],
    cities=[city(MINSK, "Minsk", a + 0.3, AMBER, "base", 6)])
a = tRus5
reg("c1-mod", a, S("p06"), [("s", [37.0, 55.0], 1700), ("e", MOS, 900)],
    [LB2("Defence ministry: the focus", a + 0.2, YELLOW), LB2("Preparing and using nuclear forces", W("p05", "preparation"), WHITE, 1)], tag="REAL DATA", source=SRC_T, clock="MAY 2026", clockLabel="EXERCISE", highlight=[HL_RU],
    cities=[city(MOS, "Moscow", a + 0.3, AMBER, "base", 6)])
a = S("p06")
tCouncil, tPubl, tRange = W("p06", "Council"), W("p06", "Published"), W("p06", "range")
reg("c1-isk", a, tCouncil, [("s", [36.0, 52.0], 1200), ("e", [35.0, 51.0], 700)],
    [LB2("Iskander-M", a + 0.2, AMBER), LB2("Likely for a battlefield nuclear strike", W("p06", "weapon"), WHITE, 1)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_RU],
    cities=[city(LAUNCH, "Launcher (illustrative)", a + 0.6, AMBER, "base", 6)])
a = tCouncil
reg("c1-cfr", a, tPubl, [("s", [35.0, 51.0], 700), ("e", [33.0, 50.0], 1300)],
    [LB2("Council on Foreign Relations", a + 0.2, YELLOW), LB2("The likely vehicle", W("p06", "likely", 2), WHITE, 1)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_UA, HL_RU])
a = tPubl
reg("c1-kt", a, tRange, [("s", LAUNCH, 900), ("e", LAUNCH, 1100)],
    [LB2("Warhead: up to 100 kilotons", W("p06", "hundred"), RED)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_RU],
    cities=[city(LAUNCH, "Launcher (illustrative)", 0, AMBER, "base", 6)])
a = tRange
reg("c1-rng", a, S("p07"), [("s", LAUNCH, 1100), ("e", [34.0, 50.0], 1500)],
    [LB2("Range: about 350 km", a + 0.2, YELLOW)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_UA, HL_RU],
    rings=[ring(LAUNCH, 350, a + 0.2, "", AMBER, True)], cities=[city(LAUNCH, "Launcher (illustrative)", 0, AMBER, "base", 6)])
a = S("p07")
tSo, tBack = W("p07", "So"), W("p07", "Back")
add(id="c1-hiro", type="bars", start=a, end=tSo, tag="REAL DATA", title="Yield, in kilotons", sub="a yardstick", source="Los Alamos review (Hiroshima); published Iskander tables",
    bars=[{"label": "Hiroshima", "value": 15, "display": "about 15", "color": WHITE}, {"label": "Iskander warhead, up to", "value": 100, "display": "up to 100", "color": AMBER}])
a = tSo
reg("c1-low", a, tBack, [("s", [34.0, 50.0], 900), ("e", GZ, 500)],
    [LB2("A low-yield weapon is not a small one", a + 0.2, YELLOW)], tag="REAL DATA", source="Los Alamos review", clock="", highlight=[HL_UA])
a = tBack
reg("c1-3min", a, S("p08"), [("s", [35.0, 50.7], 600), ("e", [34.8, 50.6], 500)],
    [LB2("Three minutes: all the warning", a + 0.2, RED)], tag="SIMULATION", highlight=[HL_UA, HL_RU], **clk("T+00:00", "FLIGHT", 66), **fl(a, S("p08"), t0=a + 0.2),
    cities=[city(GZ, "Target (simulated)", a + 0.3, RED, "target", 6)])
a = S("p08")
tOnly = W("p08", "Only")
reg("c1-hold", a, tOnly, [("s", [60.0, 58.0], 4200), ("e", [48.0, 55.0], 3000)],
    [LB2("Roughly 1,000 to 2,000", a + 0.3, YELLOW), LB2("non-strategic warheads", W("p08", "warheads"), WHITE, 1)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_RU], countryLabels=[CL_RU])
a = tOnly
reg("c1-frac", a, S("p09"), [("s", [40.0, 53.0], 2000), ("e", LAUNCH, 800)],
    [LB2("Only a fraction on ground-launched missiles", a + 0.2, WHITE)], tag="REAL DATA", source=SRC_B, clock="", highlight=[HL_RU],
    cities=[city(LAUNCH, "Launcher (illustrative)", a + 1.0, AMBER, "base", 6)])
a = S("p09")
tSig, tConv, tOneE, tNotS = W("p09", "signed"), W("p09", "conventional"), W("p09", "One"), W("p09", "does")
stamp("c1-doc", a, a + 3.4, "NOVEMBER 2024", "Putin signs a revised nuclear doctrine", AMBER, tag="REAL DATA", source="Arms Control Association; Kyiv Independent")
a += 3.4
reg("c1-conv", a, tOneE, [("s", MOS, 1000), ("e", [37.0, 54.0], 2200)],
    [LB2("Doctrine: grounds for nuclear use", a + 0.2, YELLOW), LB2("Conventional aggression that creates", tConv, WHITE, 1), LB2("a critical threat to sovereignty", W("p09", "critical"), WHITE, 2)], tag="REAL DATA", source="Arms Control Association; Kyiv Independent", clock="", highlight=[HL_RU],
    cities=[city(MOS, "Moscow", a + 0.3, AMBER, "base", 6)])
a = tOneE
reg("c1-low2", a, S("p10"), [("s", [37.0, 54.0], 2200), ("e", [36.0, 53.0], 1400)],
    [LB2("One expert: it appears to lower the threshold", a + 0.2, YELLOW), LB2("It does not say what Russia would do", tNotS, WHITE, 1)], tag="REAL DATA", source="Arms Control Association", clock="", highlight=[HL_RU])
a = S("p10")
reg("c1-west", a, S("p11"), [("s", [10.0, 48.0], 3800), ("e", [-20.0, 45.0], 5800)],
    [LB2("What has the West said it would do?", a + 0.3, YELLOW)], tag="REAL DATA", clock="", highlight=HL_NATO, countryLabels=[cl(PL, "POLAND", BLUE)])

# ================================================================== Chapter 02 [REAL HISTORY] the answer nobody published
a = chapter("c2-card", S("p11"), 3.5, "CHAPTER 02", "The answer nobody published", "REAL HISTORY")
tAny, tSix, tBackc, tCuba2, tUkr = W("p11", "any"), W("p11", "Six"), W("p11", "back"), W("p11", "Cuba", 2), W("p11", "Ukraine")
CAR = [("s", [-80.0, 28.0], 3200), ("e", [-81.0, 26.0], 2600)]
reg("c2-kennedy", a, tAny, CAR,
    [LB2("October 1962", a + 0.2, YELLOW), LB2("Kennedy names a red line on live television", a + 1.2, WHITE, 1)], tag="REAL HISTORY", source="US State Department, Office of the Historian", clock="1962", clockLabel="CUBA",
    highlight=[hl(CU, AMBER, 0.12), hl(US, BLUE, 0.08)], cities=[city(HAV, "Havana", a + 0.5, AMBER, "base", 6), city(WASH, "Washington", a + 1.0, BLUE, "base", 6)])
a = tAny
reg("c2-line", a, tSix, [("s", [-81.0, 26.0], 2600), ("e", [-82.0, 25.0], 1800)],
    [LB2("Any missile launched from Cuba", a + 0.2, WHITE), LB2("is a Soviet attack", W("p11", "attack"), RED, 1)], tag="REAL HISTORY", source="US State Department, Office of the Historian", clock="1962", clockLabel="CUBA",
    highlight=[hl(CU, AMBER, 0.12)], cities=[city(HAV, "Havana", 0, AMBER, "base", 6)])
a = tSix
reg("c2-six", a, tBackc, [("s", [-80.0, 26.0], 2800), ("e", [-79.0, 28.0], 3200)],
    [LB2("Six days later", a + 0.2, YELLOW), LB2("Khrushchev agrees to withdraw", W("p11", "Khrushchev"), AMBER, 1)], tag="REAL HISTORY", source="US State Department, Office of the Historian", clock="1962", clockLabel="CUBA",
    highlight=[hl(CU, AMBER, 0.12), hl(US, BLUE, 0.08)])
a = tBackc
reg("c2-chan", a, tCuba2, [("s", [-79.0, 28.0], 3000), ("e", [-82.0, 25.0], 1800)],
    [LB2("A back channel made retreat possible", a + 0.2, WHITE)], tag="REAL HISTORY", source="US State Department, Office of the Historian", clock="1962", clockLabel="CUBA",
    highlight=[hl(CU, AMBER, 0.12)], cities=[city(HAV, "Havana", 0, AMBER, "base", 6)])
a = tCuba2
reg("c2-days", a, tUkr, [("s", [-82.0, 25.0], 1800), ("e", [-81.0, 26.0], 2800)],
    [LB2("Cuba: days to talk", a + 0.2, YELLOW)], tag="REAL HISTORY", clock="1962", clockLabel="CUBA", highlight=[hl(CU, AMBER, 0.12)])
a = tUkr
reg("c2-mins", a, S("p12"), [("s", [34.0, 50.0], 1000), ("e", GZ, 600)],
    [LB2("A strike on Ukraine: minutes", a + 0.2, RED)], tag="REAL HISTORY", clock="", highlight=[HL_UA],
    cities=[city(GZ, "", a + 0.2, RED, "target", 6)])
a = S("p12")
tCat, tAsk, tBid, tVag = W("p12", "catastrophic"), W("p12", "Asked"), W("p12", "President"), W("p12", "vague")
reg("c2-sul", a, tCat, [("s", [-77.0, 39.0], 2600), ("e", [-77.0, 38.9], 1400)],
    [LB2("September 2022", a + 0.2, YELLOW), LB2("US national security adviser", a + 1.4, WHITE, 1)], tag="REAL HISTORY", source="NBC News, September 2022", clock="SEPT 2022", clockLabel="WASHINGTON",
    highlight=[hl(US, BLUE, 0.08)], cities=[city(WASH, "Washington", a + 0.4, BLUE, "base", 6)])
a = tCat
reg("c2-cat", a, tAsk, [("s", [-77.0, 38.9], 1400), ("e", [-20.0, 46.0], 11500)],
    [LB2("Russian nuclear use: catastrophic consequences", a + 0.1, RED)], tag="REAL HISTORY", source="NBC News, September 2022", clock="SEPT 2022", clockLabel="WASHINGTON", highlight=[hl(US, BLUE, 0.08), HL_RU, HL_UA],
    cities=[city(WASH, "Washington", 0, BLUE, "base", 6), city(MOS, "Moscow", a + 1.2, AMBER, "base", 6)], lines=[line(WASH, MOS, a + 1.2, a + 3.0, WHITE, True)])
a = tAsk
reg("c2-priv", a, tBid, [("s", [-77.0, 39.0], 1800), ("e", [-78.0, 38.0], 1100)],
    [LB2("Asked for specifics", a + 0.2, WHITE), LB2("Spelled out in private channels", W("p12", "spelled"), YELLOW, 1)], tag="REAL HISTORY", source="NBC News, September 2022", clock="SEPT 2022", clockLabel="WASHINGTON", highlight=[hl(US, BLUE, 0.08)],
    cities=[city(WASH, "Washington", 0, BLUE, "base", 6)])
a = tBid
reg("c2-bid", a, tVag, [("s", [-77.0, 38.9], 1100), ("e", [-77.0, 38.9], 1800)],
    [LB2("Biden: any nuclear use, on any scale", a + 0.2, WHITE), LB2("Completely unacceptable", W("p12", "completely"), RED, 1)], tag="REAL HISTORY", source="NBC News; CFR", clock="2022", clockLabel="WASHINGTON", highlight=[hl(US, BLUE, 0.08)],
    cities=[city(WASH, "Washington", 0, BLUE, "base", 6)])
a = tVag
reg("c2-vag", a, S("p13"), [("s", [-77.0, 38.9], 1800), ("e", [-90.0, 40.0], 3800)],
    [LB2("The public answer: vague on purpose", a + 0.2, YELLOW)], tag="REAL HISTORY", clock="2022", clockLabel="WASHINGTON", highlight=[hl(US, BLUE, 0.08)])
a = S("p13")
tArt, tTrig, tMiss = W("p13", "Article"), W("p13", "triggers"), W("p13", "missile")
reg("c2-pol", a, tArt, [("s", [26.0, 52.0], 1700), ("e", [23.0, 52.0], 1000)],
    [LB2("September 2025", a + 0.2, YELLOW), LB2("Russian drones enter Poland's airspace", a + 1.2, WHITE, 1)], tag="REAL HISTORY", source="PBS NewsHour; NATO", clock="SEPT 2025", clockLabel="POLAND",
    highlight=[hl(PL, BLUE, 0.12), HL_UA, HL_BY], countryLabels=[CL_PL], cities=[city(WARS, "Warsaw", a + 0.4, BLUE, "base", 6)])
a = tArt
reg("c2-a4", a, tTrig, [("s", [23.0, 52.0], 1000), ("e", BRU, 1800)],
    [LB2("Poland asks for Article 4 consultation", a + 0.2, YELLOW), LB2("Article 4 means talking", W("p13", "means"), WHITE, 1)], tag="REAL HISTORY", source="PBS NewsHour; NATO", clock="SEPT 2025", clockLabel="NATO", highlight=HL_NATO,
    cities=[city(BRU, "Brussels", a + 0.3, BLUE, "base", 6), city(WARS, "Warsaw", a + 0.3, BLUE, "base", 6)])
a = tTrig
reg("c2-noauto", a, tMiss, [("s", BRU, 1800), ("e", [10.0, 51.0], 1100)],
    [LB2("No automatic action", a + 0.2, WHITE)], tag="REAL HISTORY", source="NATO", clock="", highlight=HL_NATO, cities=[city(BRU, "Brussels", 0, BLUE, "base", 6)])
a = tMiss
reg("c2-wait", a, S("p14"), [("s", [24.0, 51.0], 3000), ("e", [33.0, 50.5], 1800)],
    [LB2("A missile would not wait for a meeting", a + 0.2, RED)], tag="REAL HISTORY", clock="", highlight=[HL_UA] + HL_NATO, **fl(a, S("p14"), t0=a + 0.4))
a = S("p14")
tUkn = W("p14", "Ukraine")
reg("c2-blank", a, tUkn, [("s", [20.0, 50.0], 3300), ("e", [22.0, 50.0], 2600)],
    [LB2("The public line: a deliberate blank", a + 0.2, YELLOW)], tag="REAL HISTORY", clock="", highlight=HL_NATO, legend=LEG[1:] if False else None)
a = tUkn
reg("c2-art5", a, S("p15"), [("s", [26.0, 49.5], 2000), ("e", [27.0, 50.0], 1500)],
    [LB2("Ukraine is not in NATO", a + 0.2, TEAL), LB2("Article 5 does not cover it", W("p14", "five"), WHITE, 1)], tag="REAL HISTORY", source="North Atlantic Treaty, 1949", clock="", highlight=[HL_UA] + HL_NATO, countryLabels=[CL_UA])
a = S("p15")
reg("c2-cross", a, S("p16"), [("s", [18.0, 50.0], 3600), ("e", [28.0, 50.0], 1800)],
    [LB2("When the flash comes", a + 0.2, YELLOW), LB2("which option crosses a line?", W("p15", "options"), WHITE, 1)], tag="REAL HISTORY", clock="", highlight=[HL_UA] + HL_NATO,
    cities=[city(GZ, "", a + 0.1, RED, "target", 6)])

# ================================================================== Chapter 03 [SIMULATION] the strike
a = chapter("c3-card", S("p16"), 3.5, "CHAPTER 03", "The strike", "SIMULATION")
tWord, tChoice = W("p16", "wording"), W("p16", "choice")
reg("c3-moscow", a, tWord, [("s", [36.0, 52.5], 1500), ("e", [37.0, 54.0], 1100)],
    [LB2("Our simulation: Moscow decides", a + 0.2, YELLOW), LB2("a Ukrainian advance is a critical threat", a + 1.2, WHITE, 1)], clock="", highlight=[HL_RU, HL_UA],
    cities=[city(MOS, "Moscow", a + 0.3, AMBER, "base", 6)])
a = tWord
reg("c3-doc", a, S("p17"), [("s", [37.0, 54.0], 1100), ("e", [36.0, 52.0], 1500)],
    [LB2("The wording of its own doctrine", a + 0.1, WHITE), LB2("Our choice, not a prediction", tChoice, YELLOW, 1)], clock="", highlight=[HL_RU, HL_UA])
a = S("p17")
tCity, tBat, tYld = W("p17", "city"), W("p17", "battlefield"), W("p17", "yield")
reg("c3-area", a, tCity, [("s", [33.0, 49.8], 700), ("e", GZ, 220)],
    [LB2("Target: a Ukrainian reserve staging area", a + 0.2, YELLOW), LB2("Open farmland", W("p17", "farmland"), WHITE, 1)], clock="", highlight=[HL_UA],
    cities=[city(GZ, "Staging area (simulated)", a + 0.6, RED, "target", 6)])
a = tCity
cty("c3-farm", a, tBat, [("s", GZ, 24000), ("e", GZ, 12000)], [],
    [LB("No city, no nuclear plant near", -0.30, 0.31, a + 0.3, WHITE)], clock="")
a = tBat
reg("c3-cfr", a, tYld, [("s", [34.0, 50.0], 900), ("e", [33.0, 50.0], 1500)],
    [LB2("The battlefield case (CFR)", a + 0.2, YELLOW), LB2("Not an attack on civilians", W("p17", "civilians"), WHITE, 1)], clock="", highlight=[HL_UA], source="Council on Foreign Relations")
a = tYld
num("c3-20kt", a, S("p18"), "20 KT", label="Yield: our choice, inside the published range", sub="simulation assumption", color=RED, countTo=20, suffix=" KT")
a = S("p18")
tCent, tApart, tNotice, tStill = W("p18", "central"), W("p18", "apart"), W("p18", "notice"), W("p18", "still")
reg("c3-hard", a, tCent, [("s", [38.0, 53.0], 2000), ("e", [37.0, 52.0], 1200)],
    [LB2("The warhead is the hard part to hide", a + 0.2, YELLOW)], clock="", highlight=[HL_RU])
a = tCent
reg("c3-depot", a, tNotice, [("s", [37.0, 52.0], 1200), ("e", LAUNCH, 500)],
    [LB2("Warheads sit in central depots", a + 0.2, WHITE), LB2("apart from their launchers", tApart, AMBER, 1)], clock="", highlight=[HL_RU],
    cities=[city(LAUNCH, "Launcher (simulated)", tApart, AMBER, "base", 6)])
a = tNotice
reg("c3-obs", a, tStill, [("s", LAUNCH, 500), ("e", [35.0, 51.0], 900)],
    [LB2("A strike needs preparation", a - 1.8, WHITE), LB2("an observer might notice", a + 0.1, YELLOW, 1)], clock="", highlight=[HL_RU, HL_UA])
a = tStill
reg("c3-nowarn", a, S("p19"), [("s", [35.0, 51.0], 900), ("e", [35.0, 50.5], 600)],
    [LB2("Our simulation: no public warning", a + 0.2, RED)], clock="", highlight=[HL_RU, HL_UA], cities=[city(LAUNCH, "Launcher (simulated)", 0, AMBER, "base", 6)])
a = S("p19")
tOver = W("p19", "over")
add(id="c3-yard", type="bars", start=a, end=tOver, tag="SIMULATION", title="Yield, in kilotons", sub="a third more than Hiroshima", source="Scenario engine; Los Alamos review",
    bars=[{"label": "Hiroshima", "value": 15, "display": "about 15", "color": WHITE}, {"label": "Our strike", "value": 20, "display": "20", "color": RED}])
a = tOver
cty("c3-over", a, S("p20"), [("s", GZ, 14000), ("e", GZ, 8000)], [],
    [LB("Over farmland, not a city", -0.30, 0.31, a + 0.3, YELLOW)], clock="")
a = S("p20")
tLeav, tMin2, tBurst = W("p20", "leaves"), W("p20", "Minute", 2), W("p20", "bursts")
reg("c3-m0", a, tLeav, [("s", LAUNCH, 500), ("e", LAUNCH, 300)],
    [LB2("Minute zero", a + 0.2, YELLOW)], **clk("T+00:00", "LAUNCH"), highlight=[HL_RU], cities=[city(LAUNCH, "Launcher (simulated)", a + 0.2, AMBER, "base", 6)])
a = tLeav
reg("c3-fly", a, tBurst, [("s", [35.0, 50.7], 600), ("e", [34.5, 50.3], 450)],
    [LB2("The missile leaves the launcher", a + 0.2, WHITE), LB2("Minute 3.3", tMin2, YELLOW, 1)], highlight=[HL_UA, HL_RU], **clk("T+00:00", "FLIGHT", 66), **fl(a, tBurst, t0=a + 0.1),
    cities=[city(GZ, "", a + 0.2, RED, "target", 6)])
a = tBurst
reg("c3-burst", a, S("p21"), [("s", GZ, 140), ("e", GZ, 100)],
    [LB("Airburst over the field", -0.30, 0.31, a + 0.3, YELLOW)], **clk("T+03:18", "AIRBURST"), burst={"at": GZ, "t": 0.1, "km": 4, "fade": 4}, rings=[ring(GZ, 4, a + 0.7, "", RED)])

# ================================================================== Chapter 04 [SIMULATION] the first 72 hours
a = chapter("c4-card", S("p21"), 3.8, "CHAPTER 04", "The first 72 hours", "SIMULATION")
tWith, tCall, tSg = W("p21", "Within"), W("p21", "call"), W("p21", "Secretary-General")
HR = lambda h: clk(f"HOUR {h:02d}", "AFTER THE BURST")
reg("c4-h0", a, tWith, [("s", [18.0, 52.0], 3300), ("e", [14.0, 52.5], 2600)],
    [LB2("Hour 0: allied sensors register the flash", a + 0.2, YELLOW), LB2("Defence ministries are called at once", W("p21", "every"), WHITE, 1)], **HR(0), highlight=[HL_UA] + HL_NATO,
    cities=[city(GZ, "Flash", a + 0.2, RED, "target", 6), city(BRU, "Brussels", a + 1.2, BLUE, "base", 6)], lines=[line(GZ, BRU, a + 0.4, a + 3.0, RED, True)])
a = tWith
reg("c4-h2", a, tCall, [("s", [10.0, 50.0], 2600), ("e", BRU, 1300)],
    [LB2("Within 2 hours: capitals and NATO's chief", a + 0.2, YELLOW), LB2("call it unacceptable", tSg, WHITE, 1)], **HR(2), highlight=HL_NATO,
    cities=[city(BRU, "Brussels", a + 0.1, BLUE, "base", 6)])
a = tCall
glob("c4-call", a, S("p22"), [("s", 48.0, -30.0, 1100), ("e", 50.0, 0.0, 1500)],
     arcs=[{"from": WASH, "to": MOS, "t0": 0.4, "t1": 3.4, "color": WHITE, "width": 3, "loft": 0.2}],
     markers=[{"at": WASH, "label": "Washington", "color": BLUE, "t": 0.3, "kind": "base"}, {"at": MOS, "label": "Moscow", "color": AMBER, "t": 1.0, "kind": "base"}], **HR(2))
a = S("p22")
tEach, tAsks, tGroup, tRad = W("p22", "Each"), W("p22", "asks"), W("p22", "Group"), W("p22", "Radiation")
reg("c4-h6", a, tEach, [("s", [12.0, 50.0], 3000), ("e", [10.0, 50.0], 2400)],
    [LB2("Hour 6: the Allies do not act as one body", a + 0.2, YELLOW)], **HR(6), highlight=HL_NATO)
a = tEach
reg("c4-each", a, tAsks, [("s", [10.0, 50.0], 2400), ("e", [6.0, 49.0], 3300)],
    [LB2("Each capital: its own intelligence", a + 0.2, WHITE), LB2("and its own election", W("p22", "election"), WHITE, 1)], **HR(6), highlight=HL_NATO)
a = tAsks
reg("c4-nac", a, tGroup, [("s", BRU, 1300), ("e", BRU, 700)],
    [LB2("An ally asks for an emergency meeting", a + 0.2, YELLOW), LB2("North Atlantic Council: Article 4, not 5", W("p22", "North"), WHITE, 1)], **HR(6), highlight=HL_NATO,
    cities=[city(BRU, "Brussels", 0, BLUE, "base", 6)])
a = tGroup
reg("c4-g7", a, tRad, [("s", [10.0, 50.0], 2800), ("e", [16.0, 50.0], 2200)],
    [LB2("The G7 and UN Security Council meet", a + 0.2, WHITE)], **HR(6), highlight=HL_NATO)
a = tRad
reg("c4-radmon", a, S("p23"), [("s", [24.0, 50.0], 1800), ("e", [26.0, 50.0], 1400)],
    [LB2("Radiation monitoring begins", a + 0.2, YELLOW), LB2("Aid for fallout response", a + 1.8, WHITE, 1)], **HR(6), highlight=[HL_UA] + HL_NATO,
    cities=[city(WARS, "Warsaw", a + 0.3, BLUE, "base", 6), city(BUCH, "Bucharest", a + 0.9, BLUE, "base", 6)])
a = S("p23")
tFund, tPost = W("p23", "fundamental"), W("p23", "posture")
reg("c4-npg", a, tFund, [("s", BRU, 1300), ("e", BRU, 700)],
    [LB2("Hour 20: the Nuclear Planning Group meets", a + 0.2, YELLOW)], **HR(20), highlight=HL_NATO, cities=[city(BRU, "NATO headquarters", a + 0.3, BLUE, "base", 6)])
a = tFund
reg("c4-det", a, tPost, [("s", [8.0, 50.0], 2600), ("e", BRU, 1000)],
    [LB2("NATO's line: nuclear forces exist for deterrence", a + 0.2, WHITE)], **HR(20), highlight=HL_NATO, cities=[city(BRU, "Brussels", 0, BLUE, "base", 6)])
a = tPost
reg("c4-pos", a, S("p24"), [("s", BRU, 1000), ("e", [8.0, 50.0], 2600)],
    [LB2("Our simulation: posture does not change", a + 0.2, YELLOW)], **HR(20), highlight=HL_NATO)
a = S("p24")
tDoesnt, tAmb, tAir, tNoT = W("p24", "does"), W("p24", "ambiguity"), W("p24", "Air"), W("p24", "No")
reg("c4-h30", a, tDoesnt, [("s", [10.0, 50.0], 2800), ("e", BRU, 1300)],
    [LB2("Hour 30: any further nuclear use", a + 0.2, YELLOW), LB2("would meet a response", a + 1.6, WHITE, 1)], **HR(30), highlight=HL_NATO)
a = tDoesnt
reg("c4-kind", a, tAmb, [("s", BRU, 1300), ("e", [10.0, 51.0], 2400)],
    [LB2("What kind: not said", a + 0.2, WHITE)], **HR(30), highlight=HL_NATO)
a = tAmb
reg("c4-amb", a, tAir, [("s", [10.0, 51.0], 2400), ("e", [15.0, 51.0], 1800)],
    [LB2("Ambiguity urged by an Atlantic Council analyst, 2022", a + 0.2, YELLOW)], **HR(30), highlight=HL_NATO, source="Atlantic Council, 2022")
a = tAir
reg("c4-east", a, tNoT, [("s", [14.0, 51.0], 1700), ("e", [20.0, 51.0], 1500)],
    [LB2("Air defence and air policing move east", a + 0.2, WHITE)], **HR(30), highlight=[HL_UA] + HL_NATO,
    lines=[line([8.0, 51.0], [21.0, 51.5], a + 0.3, a + 3.0, BLUE, False)])
a = tNoT
reg("c4-notroops", a, S("p25"), [("s", [24.0, 50.0], 1400), ("e", [27.0, 50.0], 1100)],
    [LB2("No NATO troops enter Ukraine", a + 0.2, YELLOW)], **HR(30), highlight=[HL_UA] + HL_NATO, countryLabels=[CL_UA])
a = S("p25")
add(id="c4-tl", type="timeline", start=a, end=a + 3.6, tag="SIMULATION", title="The first 72 hours", sub="Hour 36: the real decision begins", total=72, unit="hours",
    segments=[{"from": 0, "to": 6, "label": "Reaction", "color": BLUE}, {"from": 6, "to": 20, "label": "Meetings", "color": BLUE}, {"from": 20, "to": 36, "label": "Posture", "color": BLUE}, {"from": 36, "to": 72, "label": "Decision", "color": RED}],
    highlight={"from": 36, "to": 72, "label": "The decision"}, cursorTo=36)
a += 3.6
reg("c4-h36", a, S("p26"), [("s", [18.0, 50.0], 3200), ("e", [22.0, 50.0], 2400)],
    [LB2("Hour 36: the real decision begins", a + 0.2, YELLOW)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = S("p26")
reg("c4-four", a, S("p27"), [("s", [22.0, 50.0], 3000), ("e", [28.0, 50.0], 2200)],
    [LB2("Four options, from published analyses", a + 0.3, YELLOW)], **HR(36), highlight=[HL_UA] + HL_NATO, legend=LEG)
a = S("p27")
tPol, tDecl = W("p27", "politically"), W("p27", "NATO")
reg("c4-o1", a, tPol, [("s", [25.0, 50.0], 2400), ("e", [30.0, 50.0], 1500)],
    [LB2("Option 1: answer with a nuclear weapon", a + 0.2, RED)], **HR(36), highlight=[HL_UA])
a = tPol
reg("c4-o1b", a, tDecl, [("s", [30.0, 50.0], 1500), ("e", GZ, 800)],
    [LB2("One analyst: politically infeasible", a + 0.2, WHITE), LB2("on a non-nuclear state's soil", a + 1.4, WHITE, 1)], **HR(36), highlight=[HL_UA])
a = tDecl
reg("c4-o1c", a, S("p28"), [("s", GZ, 800), ("e", [28.0, 50.0], 2200)],
    [LB2("Our simulation: NATO declines", a + 0.2, YELLOW)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = S("p28")
tLaun, tBlack, tOneA, tAnother, tSimul, tEmb = W("p28", "launcher"), W("p28", "Black"), W("p28", "One"), W("p28", "Another"), W("p28", "direct"), W("p28", "embassies")
reg("c4-o2", a, tLaun, [("s", [34.0, 49.0], 1500), ("e", [35.0, 50.0], 800)],
    [LB2("Option 2: conventional strikes", a + 0.2, YELLOW)], **HR(36), highlight=[HL_UA, HL_RU], cities=[city(LAUNCH, "Launcher", tLaun - 0.5, AMBER, "base", 6)])
a = tLaun
reg("c4-o2b", a, tBlack, [("s", [35.0, 50.0], 1000), ("e", [35.0, 49.0], 1700)],
    [LB2("The launcher, or the Iskander unit", a + 0.2, WHITE)], **HR(36), highlight=[HL_UA, HL_RU], cities=[city(LAUNCH, "Launcher", 0, AMBER, "base", 6)])
a = tBlack
reg("c4-o2c", a, tAnother, [("s", [34.0, 47.0], 1500), ("e", SEV, 900)],
    [LB2("Or the Black Sea Fleet", a + 0.2, WHITE), LB2("One analyst proposes it", tOneA, YELLOW, 1)], **HR(36), highlight=[HL_UA, HL_RU],
    cities=[city(SEV, "Black Sea Fleet", a + 0.3, AMBER, "base", 6)])
a = tAnother
reg("c4-o2d", a, tSimul, [("s", [33.0, 49.0], 1800), ("e", [34.0, 50.0], 1300)],
    [LB2("Another warns of Russian retaliation", a + 0.2, RED)], **HR(36), highlight=[HL_UA, HL_RU])
a = tSimul
reg("c4-o2e", a, tEmb, [("s", [30.0, 50.5], 2000), ("e", [28.0, 50.5], 2800)],
    [LB2("First step that makes NATO a direct party", a + 0.2, YELLOW)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = tEmb
reg("c4-o2f", a, S("p29"), [("s", [36.0, 52.0], 2000), ("e", [38.0, 54.0], 1600)],
    [LB2("Real record: Russian embassies, 2026", a + 0.1, YELLOW), LB2("Reply to NATO strikes: all means,", a + 1.0, WHITE, 1), LB2("nuclear included", a + 2.0, RED, 2)], **HR(36), highlight=[HL_RU, HL_BY], countryLabels=[CL_RU, CL_BY],
    cities=[city(MOS, "Moscow", a + 0.3, AMBER, "base", 6), city(MINSK, "Minsk", a + 1.2, AMBER, "base", 6)], source="Source (real record): Russian embassy statements, 2026")
a = S("p29")
tFour = W("p29", "Four")
reg("c4-o3", a, tFour, [("s", [30.0, 50.0], 2200), ("e", [25.0, 50.0], 2800)],
    [LB2("Option 3: stay the course", a + 0.2, YELLOW), LB2("More weapons, sanctions, isolation", W("p29", "weapons"), WHITE, 1)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = tFour
reg("c4-o4", a, S("p30"), [("s", [31.0, 50.0], 1800), ("e", [32.0, 50.0], 1200)],
    [LB2("Option 4: press Ukraine to settle", a + 0.2, YELLOW), LB2("Judged unwise by the same analyst", W("p29", "unwise"), WHITE, 1)], **HR(36), highlight=[HL_UA], countryLabels=[CL_UA])
a = S("p30")
tFi, tSe, tTh, tFo = W("p30", "first"), W("p30", "second"), W("p30", "third"), W("p30", "fourth")
reg("c4-fear0", a, tFi, [("s", [24.0, 50.0], 3200), ("e", [24.0, 50.0], 2600)],
    [LB2("Each option answers a different fear", a + 0.2, YELLOW)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = tFi
reg("c4-fear1", a, tSe, [("s", [24.0, 50.0], 2600), ("e", [26.0, 50.0], 1800)],
    [LB2("Option 1 fears weakness", a + 0.2, WHITE)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = tSe
reg("c4-fear2", a, tTh, [("s", [26.0, 50.0], 1800), ("e", [30.0, 51.0], 1300)],
    [LB2("Option 2 fears a second strike", a + 0.2, WHITE)], **HR(36), highlight=[HL_UA, HL_RU])
a = tTh
reg("c4-fear3", a, tFo, [("s", [28.0, 51.0], 1500), ("e", [20.0, 51.0], 2800)],
    [LB2("Option 3 fears a wider war", a + 0.2, WHITE)], **HR(36), highlight=[HL_UA] + HL_NATO)
a = tFo
reg("c4-fear4", a, S("p31"), [("s", [31.0, 49.0], 1500), ("e", [32.0, 50.0], 900)],
    [LB2("Option 4 fears a lost country", a + 0.2, WHITE)], **HR(36), highlight=[HL_UA])
a = S("p31")
tConvp, tNoDl = W("p31", "conventional"), W("p31", "Nothing")
add(id="c4-tl2", type="timeline", start=a, end=a + 3.5, tag="SIMULATION", title="The first 72 hours", sub="Hour 72: NATO picks option 3", total=72, unit="hours",
    segments=[{"from": 0, "to": 6, "label": "Reaction", "color": BLUE}, {"from": 6, "to": 20, "label": "Meetings", "color": BLUE}, {"from": 20, "to": 36, "label": "Posture", "color": BLUE}, {"from": 36, "to": 72, "label": "Decision", "color": RED}],
    highlight={"from": 36, "to": 72, "label": "Option 3"}, cursorTo=72)
a += 3.5
reg("c4-pkg", a, tNoDl, [("s", [26.0, 50.0], 2400), ("e", [32.0, 50.0], 1500)],
    [LB2("The conventional package stays", a + 0.2, WHITE), LB2("prepared and unlaunched", W("p31", "unlaunched"), YELLOW, 1)], **HR(72), highlight=[HL_UA, HL_RU] + HL_NATO)
a = tNoDl
reg("c4-nodl", a, S("p32"), [("s", [34.0, 52.0], 2400), ("e", [34.0, 53.0], 1400)],
    [LB2("No deadline is announced", a + 0.2, YELLOW), LB2("because no real one exists", W("p31", "because"), WHITE, 1)], **HR(72), highlight=[HL_UA, HL_RU])

# ================================================================== Chapter 05 [SIMULATION] one warhead, ring by ring
a = chapter("c5-card", S("p32"), 3.5, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
CK = dict(clock="13:43", clockLabel="UKRAINE TIME", clockRate=0)
cty("c5-fire", a, S("p33"), [("s", GZ, 1800), ("e", GZ, 1300)],
    [dict(ring(GZ, FX["fireball_km"], a + 0.4, "Fireball", WHITE), angle=100)],
    [LB("Air burst over the staging area", -0.30, 0.31, a + 0.2, YELLOW)], flashT=0.1, **CK)
a = S("p33")
cty("c5-20", a, S("p34"), [("s", GZ, 1500), ("e", GZ, 2400)],
    [dict(ring(GZ, FX["fireball_km"], 0, "Fireball", WHITE), angle=100), dict(ring(GZ, FX["psi20_km"], a + 0.4, "20 psi", RED), angle=300)],
    [LB("Nothing built by hand stands", -0.30, 0.31, W("p33", "Nothing"), WHITE)], **CK)
a = S("p34")
cty("c5-5", a, S("p35"), [("s", GZ, 3600), ("e", GZ, 5200)],
    [dict(ring(GZ, FX["psi20_km"], 0, "20 psi", RED), angle=300), dict(ring(GZ, FX["psi5_km"], a + 0.4, "5 psi", RED), angle=225)],
    [LB("Most buildings badly damaged or collapsed", -0.30, 0.31, W("p34", "most"), WHITE), LB("About 10.5 square km", -0.30, 0.23, W("p34", "ten"), YELLOW)], **CK)
a = S("p35")
cty("c5-burn", a, S("p36"), [("s", GZ, 5200), ("e", GZ, 6600)],
    [dict(ring(GZ, FX["psi5_km"], 0, "5 psi", RED), angle=225), dict(ring(GZ, FX["thermal3_km"], a + 0.4, "3rd-degree burns", ORANGE), angle=45)],
    [LB("Burns reach farther than the heavy damage", -0.30, 0.31, a + 0.2, WHITE)], **CK)
a = S("p36")
cty("c5-1psi", a, S("p37"), [("s", GZ, 6600), ("e", GZ, 12500)],
    [dict(ring(GZ, FX["psi5_km"], 0, "5 psi", RED), angle=225), dict(ring(GZ, FX["thermal3_km"], 0, "Burns", ORANGE), angle=45), dict(ring(GZ, FX["psi1_km"], a + 0.4, "1 psi: windows", YELLOW), angle=135)],
    [], **CK)
a = S("p37")
tNear = W("p37", "nearest")
HLY = [33.84742, 50.13732]   # Hlyboke, village, 4.25 km east of ground zero (staging-area-sim.json places)
cty("c5-near", a, tNear, [("s", GZ, 19000), (a + 3.2, GZ, 24000), ("e", GZ, 21000)],
    [dict(ring(GZ, FX["psi5_km"], a + 0.3, "5 psi", RED), angle=225), dict(ring(GZ, FX["psi1_km"], a + 1.5, "1 psi", YELLOW), angle=135)],
    [LB("Inside the 5 psi and 1 psi rings", -0.30, 0.31, a + 0.2, YELLOW)], **CK)
a = tNear
cty("c5-near2", a, S("p38"), [("s", GZ, 19000), ("e", offp(GZ, 2.2, 0), 13000)],
    [dict(ring(GZ, FX["psi1_km"], 0, "1 psi", YELLOW), angle=135), dict(ring(GZ, 4.3, a + 0.3, "Hlyboke", WHITE), angle=90)],
    [LB("Nearest mapped place: Hlyboke, a village", -0.30, 0.31, a + 0.2, WHITE)], **CK)
a = S("p38")
tChose, tGive, tPubS = W("p38", "chose"), W("p38", "gives"), W("p38", "published")
cty("c5-little", a, tChose, [("s", GZ, 9000), ("e", GZ, 18000)],
    [dict(ring(GZ, FX["psi1_km"], 0, "", YELLOW), angle=135)],
    [LB("Air burst: little local fallout", -0.30, 0.31, a + 0.2, WHITE)], **CK)
a = tChose
reg("c5-wind", a, tGive, [("s", GZ, 200), ("e", [34.6, 49.9], 320)],
    [LB2("Wind: west-north-west", a + 0.2, YELLOW), LB2("Light fallout drifts east-south-east", W("p38", "drifts"), WHITE, 1)], **CK, highlight=[HL_UA],
    plume={"at": GZ, "bearing": 112, "lengthKm": 90, "widthKm": 14, "t0": 1.2, "t1": round(tGive - a, 2), "color": YELLOW, "label": "Light fallout, if any"},
    cities=[city(GZ, "", 0, RED, "target", 6)])
a = tGive
reg("c5-nodose", a, S("p39"), [("s", [33.5, 50.0], 600), ("e", [32.5, 50.0], 1100)],
    [LB2("The engine gives no dose", a + 0.2, WHITE), LB2("No published study: no casualty figure", tPubS, YELLOW, 1)], **CK, highlight=[HL_UA])

# ================================================================== Chapter 06 [SIMULATION] the day after
a = chapter("c6-card", S("p39"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
D4 = clk("DAY 4", "AFTER THE BURST")
tAl, tSol, tSec = W("p39", "ally"), W("p39", "soldier"), W("p39", "second")
reg("c6-held", a, tAl, [("s", [20.0, 50.0], 3300), ("e", [22.0, 50.0], 2800)],
    [LB2("Did the answer hold? Day 4", a + 0.2, YELLOW)], **D4, highlight=[HL_UA] + HL_NATO)
a = tAl
reg("c6-noally", a, tSol, [("s", [12.0, 50.0], 2600), ("e", [10.0, 50.0], 2200)],
    [LB2("No ally has fired a nuclear weapon", a + 0.2, BLUE)], **D4, highlight=HL_NATO)
a = tSol
reg("c6-notroop", a, tSec, [("s", [26.0, 49.5], 1600), ("e", [30.0, 49.5], 1200)],
    [LB2("No NATO soldier is in Ukraine", a + 0.2, TEAL)], **D4, highlight=[HL_UA], countryLabels=[CL_UA])
a = tSec
reg("c6-nosecond", a, S("p40"), [("s", [36.0, 52.0], 1600), ("e", [38.0, 53.0], 1200)],
    [LB2("Russia has not fired a second", a + 0.2, AMBER)], **D4, highlight=[HL_RU])
a = S("p40")
tBg = W("p40", "background")
reg("c6-mon", a, tBg, [("s", [22.0, 49.5], 1500), ("e", [22.0, 48.5], 1200)],
    [LB2("Radiation monitors in neighbouring countries", a + 0.2, WHITE)], **D4, highlight=[HL_UA] + HL_NATO,
    cities=[city(WARS, "Warsaw", a + 0.4, BLUE, "base", 6), city(BRAT, "Bratislava", a + 1.0, BLUE, "base", 6), city(BUCH, "Bucharest", a + 1.6, BLUE, "base", 6)])
a = tBg
reg("c6-bg", a, S("p41"), [("s", [22.0, 48.5], 1200), ("e", [24.0, 50.0], 2200)],
    [LB2("Background level: a modelling expectation", a + 0.2, YELLOW), LB2("not a measurement", a + 1.6, WHITE, 1)], **D4, highlight=[HL_UA] + HL_NATO)
a = S("p41")
tPolB, tCorr, tFlt = W("p41", "Poland"), W("p41", "air"), W("p41", "Flights")
BORDER = [[23.5, 52.2], [24.2, 51.0], [24.0, 50.0], [22.8, 49.2], [21.6, 49.3], [22.2, 51.0]]
reg("c6-united", a, tPolB, [("s", [20.0, 51.0], 2600), ("e", [22.0, 52.0], 1800)],
    [LB2("Did the alliance stay united?", a + 0.2, YELLOW)], **D4, highlight=HL_NATO)
a = tPolB
reg("c6-alert", a, tCorr, [("s", [22.0, 54.0], 1800), ("e", [23.0, 53.0], 1500)],
    [LB2("Poland and the Baltic states raise alert levels", a + 0.2, BLUE)], **D4, highlight=HL_NATO,
    cities=[city(WARS, "Warsaw", a + 0.3, BLUE, "base", 6), city(VILN, "Vilnius", a + 0.6, BLUE, "base", 6), city(RIGA, "Riga", a + 0.9, BLUE, "base", 6)])
a = tCorr
reg("c6-air", a, tFlt, [("s", [23.0, 51.5], 1200), ("e", [23.0, 51.0], 900)],
    [LB2("Air corridors near the border close", a + 0.2, WHITE)], **D4, highlight=[HL_UA] + HL_NATO,
    zones=[{"points": BORDER, "label": "Closed airspace", "color": YELLOW, "t": rel(a, a + 0.4), "fillOpacity": 0.15}])
a = tFlt
reg("c6-reroute", a, S("p42"), [("s", [22.0, 51.0], 1500), ("e", [22.0, 51.0], 2400)],
    [LB2("Flights reroute", a + 0.2, WHITE), LB2("Article 4 of 2025, scaled up", a + 1.6, YELLOW, 1)], **D4, highlight=HL_NATO,
    lines=[line([14.0, 52.0], [30.0, 52.0], a + 0.3, a + 2.5, WHITE, True), line([14.0, 49.0], [30.0, 49.0], a + 0.3, a + 2.5, WHITE, True)])
a = S("p42")
tGas, tGr, tShip, tSet, tGrid = W("p42", "gas"), W("p42", "grain"), W("p42", "insurance"), W("p42", "settlement"), W("p42", "grid")
reg("c6-money", a, tGas, [("s", [15.0, 50.0], 3800), ("e", [15.0, 50.0], 3200)],
    [LB2("The second change is money", a + 0.2, YELLOW)], **D4, highlight=HL_NATO)
a = tGas
reg("c6-gas", a, tSet, [("s", [20.0, 49.0], 3000), ("e", [28.0, 46.0], 2200)],
    [LB2("European gas, grain, shipping insurance", a + 0.2, WHITE), LB2("Prices move: direction only, no number", tGr, YELLOW, 1)], **D4, highlight=[HL_UA] + HL_NATO)
a = tSet
reg("c6-bank", a, tGrid, [("s", [36.0, 54.0], 3000), ("e", MOS, 1400)],
    [LB2("Settlement links for Russian banks tighten", a + 0.2, AMBER)], **D4, highlight=[HL_RU], cities=[city(MOS, "Moscow", a + 0.5, AMBER, "base", 6)])
a = tGrid
reg("c6-grid", a, S("p43"), [("s", [31.0, 49.0], 1800), ("e", GZ, 900)],
    [LB2("At this yield and height, the grid stays up", a + 0.2, TEAL)], **D4, highlight=[HL_UA], cities=[city(KYIV, "Kyiv", a + 0.4, TEAL, "base", 6)])
a = S("p43")
tUn, tSt, tOre = W("p43", "Units"), W("p43", "statement"), W("p43", "Nobody")
reg("c6-words", a, tUn, [("s", [30.0, 54.0], 2800), ("e", [32.0, 55.0], 2000)],
    [LB2("Moscow answers in words", a + 0.2, AMBER)], **D4, highlight=[HL_RU, HL_BY])
a = tUn
reg("c6-bel", a, tSt, [("s", MINSK, 900), ("e", [27.0, 53.5], 1500)],
    [LB2("Units in Belarus go on alert", a + 0.2, AMBER)], **D4, highlight=[HL_BY], cities=[city(MINSK, "Minsk", a + 0.3, AMBER, "base", 6)])
a = tSt
reg("c6-joint", a, tOre, [("s", [37.0, 55.0], 1600), ("e", MOS, 900)],
    [LB2("A statement: Western aid is a joint attack", a + 0.2, WHITE), LB2("The language of the 2024 doctrine", a + 1.8, YELLOW, 1)], **D4, highlight=[HL_RU], cities=[city(MOS, "Moscow", 0, AMBER, "base", 6)])
a = tOre
reg("c6-ore", a, S("p44"), [("s", [34.0, 53.0], 2200), ("e", [32.0, 52.0], 1500)],
    [LB2("Oreshnik or Iskander: nuclear warhead?", a + 0.2, YELLOW), LB2("Nobody can tell from outside", a + 1.6, WHITE, 1)], **D4, highlight=[HL_RU, HL_UA])
a = S("p44")
reg("c6-peace", a, S("p45"), [("s", [26.0, 50.0], 2600), ("e", [28.0, 50.0], 2000)],
    [LB2("No road to peace drawn here", a + 0.2, YELLOW)], **D4, highlight=[HL_UA, HL_RU])
a = S("p45")
tTab, tNATO, tAC = W("p45", "taboo"), W("p45", "NATO"), W("p45", "Atlantic")
reg("c6-d7", a, tTab, [("s", [27.0, 50.0], 2600), ("e", [34.0, 51.0], 1800)],
    [LB2("Day 7", a + 0.2, YELLOW), LB2("No ceasefire", a + 1.0, RED, 1), LB2("The first 72 hours changed nothing here", a + 2.0, WHITE, 2)], clock="DAY 7", clockLabel="AFTER THE BURST", clockRate=0, highlight=[HL_UA, HL_RU], countryLabels=[CL_UA, CL_RU], legend=LEG)
a = tTab
reg("c6-taboo", a, tNATO, [("s", [30.0, 50.0], 1400), ("e", GZ, 700)],
    [LB2("The taboo is broken", a + 0.2, RED)], clock="DAY 7", clockLabel="AFTER THE BURST", clockRate=0, highlight=[HL_UA], cities=[city(GZ, "", 0, RED, "target", 6)])
a = tNATO
reg("c6-next", a, tAC, [("s", [20.0, 51.0], 3200), ("e", [30.0, 52.0], 2400)],
    [LB2("NATO has not said what it would do next", a + 0.2, WHITE), LB2("Moscow has not said it will not fire again", a + 1.8, AMBER, 1)], clock="DAY 7", clockLabel="AFTER THE BURST", clockRate=0, highlight=[HL_UA, HL_RU] + HL_NATO)
a = tAC
reg("c6-ac", a, S("p46"), [("s", BRU, 1500), ("e", [10.0, 50.0], 3000)],
    [LB2("2022 advice: consult on options in advance", a + 0.2, YELLOW)], clock="DAY 7", clockLabel="AFTER THE BURST", clockRate=0, highlight=HL_NATO, source="Atlantic Council, 2022")

# ================================================================== Shorts overrides (vertical cut only)
def _shot(sid):
    return next(x for x in shots if x["id"] == sid)


def _vl(at, text, color=WHITE, t=-1):
    return {"at": at, "text": text, "color": color, "t": t}


_s = _shot("open-burst")
_s["short"] = {"labels": [_vl(offp(GZ, 0, -16), "Central Ukraine", WHITE)] + [dict(l) for l in _s["labels"]]}
_s = _shot("open-rings")
_s["short"] = {"camera": [{"t": 0, "center": GZ, "widthKm": 1.1}, {"t": round(_s["end"] - _s["start"], 2), "center": GZ, "widthKm": 5.5}],
               "rings": [dict(r, t=-1) if r["label"] == "Fireball" else dict(r) for r in _s["rings"]],
               "labels": [_vl(offp(GZ, 0, 0.5), "20 kt airburst", YELLOW)] + [dict(l, t=-1) for l in _s["labels"]]}
_s = _shot("c5-fire")
_s["short"] = {"flashT": 0.0, "camera": [{"t": 0, "center": GZ, "widthKm": 1.8}, {"t": 8.1, "center": GZ, "widthKm": 1.1}],
               "labels": [dict(l, t=-1) for l in _s["labels"]], "rings": [dict(r, t=-1) for r in _s["rings"]]}
_s = _shot("c5-20")
_s["short"] = {"rings": [dict(r, t=-1) for r in _s["rings"]], "labels": [_vl(offp(GZ, 0, 0.3), "20 psi at 370 m", RED)] + [dict(l) for l in _s["labels"]]}
_s = _shot("c1-isk")
_s["short"] = {"labels": [dict(l, t=-1) for l in _s["labels"]], "cities": [dict(c, t=-1) for c in _s["cities"]]}

# ================================================================== End slate
add(id="endslate", type="endslate", start=S("p46"), end=END, tag="", title="Kaliningrad and the Suwalki gap", line="Next on the map: Kaliningrad and the Suwalki gap, and what NATO does when the nuclear warning comes first.")

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
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p16") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p16") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
