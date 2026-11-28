"""Director pass for episode 021: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 021-london-four-submarines-one-warhead
Payoff first: the 100 kt air burst over Westminster (city shot, flash on the word "Westminster", under the banner), then the
run-up (the Bulava missiles from the Norwegian Sea, Faslane lands first), real data (the boats on the Clyde), real history (the
four-minute warning, Protect and Survive, Be Ready), the trigger, minute by minute, the rings over London, the day after.
Actors: Russia amber, UK and NATO blue, red only for strikes.  The launch point is simulated and says so.  All times are
absolute seconds.
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
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round((WORDS[-1]["end"] if WORDS else TOTAL) + 10, 2)


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    word = word.strip(".,;:?!\"").lower()
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    cand = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word]
    if len(cand) < nth:
        raise SystemExit(f"W: no word {word!r} #{nth} in {pid}: {[h['word'] for h in WORDS if h['unit'] == pid][:80]}")
    return round(u["start"] + u["duration"] * cand[nth - 1] / len(words), 3)


KMY = 111.0


def offp(c, dx, dy):
    """c moved dx km east and dy km north"""
    return [round(c[0] + dx / (111.32 * math.cos(math.radians(c[1]))), 5), round(c[1] + dy / KMY, 5)]


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
            if key == "labels" and len(it["text"]) > 30:
                print("LONG LABEL", len(it["text"]), it["text"])
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


def ZM(a, b, c0, w0, c1, w1, step=4.4):
    """camera keys from (c0, w0) to (c1, w1), a key about every `step` seconds"""
    n = max(1, math.ceil((b - a) / step))
    out = []
    for i in range(n + 1):
        f = i / n
        t = "s" if i == 0 else ("e" if i == n else round(a + (b - a) * f, 2))
        out.append((t, [round(c0[0] + (c1[0] - c0[0]) * f, 4), round(c0[1] + (c1[1] - c0[1]) * f, 4)], round(w0 + (w1 - w0) * f, 1)))
    return out


def ZP(a, b, pts, step=4.6):
    """camera keys along waypoints [(center, widthKm), ...], evenly spaced in time, at least one key every `step` seconds"""
    n = max(len(pts), math.ceil((b - a) / step) + 1)
    out = []
    for i in range(n):
        f = i / (n - 1) * (len(pts) - 1)
        k = min(int(f), len(pts) - 2)
        u = f - k
        (c0, w0), (c1, w1) = pts[k], pts[k + 1]
        t = "s" if i == 0 else ("e" if i == n - 1 else round(a + (b - a) * i / (n - 1), 2))
        out.append((t, [round(c0[0] + (c1[0] - c0[0]) * u, 4), round(c0[1] + (c1[1] - c0[1]) * u, 4)], round(w0 + (w1 - w0) * u, 1)))
    return out


def R(sid, a, b, keys, tag="SIMULATION", **kw):
    ks = keys_of(a, b, keys)
    kw = fixt(a, b, kw)
    add(id=sid, type="region", start=round(a, 3), end=round(b, 3), tag=tag, view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, camera=ks, **kw)


def G(sid, a, b, keys, tag="SIMULATION", **kw):
    add(id=sid, type="globe", start=round(a, 3), end=round(b, 3), tag=tag, sun=SUN,
        camera=[{"t": round(t - a, 2), "lat": la, "lon": lo, "scale": s} for t, la, lo, s in keys], **kw)


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
    return ship([lerp(p, q, fa), lerp(p, q, fb)], max(a, T0), min(b, T1), kind, color, label, size, t=max(a, T0) + 0.02)


def cd(a, b, T0, T1, total, label="SINCE LAUNCH"):
    """a ticking flight clock: story seconds of flight at time t go 0 -> total between T0 and T1"""
    def s(t):
        return total * max(0.0, min(1.0, (t - T0) / (T1 - T0)))
    s0, s1 = s(a), s(b)
    v = int(round(s0))
    return {"clock": f"T+{v // 60:02d}:{v % 60:02d}", "clockLabel": label, "clockRate": round(abs(s1 - s0) / (b - a), 2)}


def DAY(n, label="SIMULATED CRISIS"):
    return {"clock": f"DAY {n:02d}", "clockLabel": label}


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=round(a, 3), end=round(a + dur, 3), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 3)


def stamp(sid, a, b, text, line, color=WHITE, tag="REAL DATA", **kw):
    add(id=sid, type="stamp", start=round(a, 3), end=round(b, 3), tag=tag, text=text, line=line, color=color, **kw)



# ------------------------------------------------------------------ places (lon, lat) and actors
ST = {s["id"]: s for s in sc["strikes"]}
FAS_S, LON_S = ST["nor-faslane"], ST["nor-london"]
FXF, FXL = FAS_S["effects"], LON_S["effects"]
FAS = [FAS_S["target_lon"], FAS_S["target_lat"]]
LON = [LON_S["target_lon"], LON_S["target_lat"]]
SUB = [FAS_S["launch_lon"], FAS_S["launch_lat"]]
COUL, EDI, BOOK = [-4.88, 56.05], [-3.19, 55.95], [-0.81, 51.61]
WATL, VICT = [-0.1137, 51.5036], [-0.1448, 51.4965]
UK, RUS = "826", "643"
HL = [hl(UK, BLUE, 0.10), hl(RUS, AMBER, 0.08)]
LEG = [{"text": "UNITED KINGDOM", "color": BLUE}, {"text": "RUSSIA (SIMULATED)", "color": AMBER}]
BOATSEA = [-13.0, 57.5]


def RR(sid, a, b, pts, **kw):
    """region shot with camera waypoints [(center, widthKm), ...]"""
    kw.setdefault("highlight", HL)
    R(sid, a, b, ZP(a, b, pts, kw.pop("step", 4.6)), **kw)


def fl(c, fx, fy, w, text, t, color=WHITE):
    """label placed by fractions of a city view of width w km (fx, fy in -0.4..0.4)"""
    return lb(offp(c, fx * w, fy * w * 0.56), text, t, color)


def CT(sid, a, b, city, gz, pts, rings=(), flash=None, tag="SIMULATION", **kw):
    """city shot; pts = [(center, widthKm), ...] evenly spaced over [a, b]"""
    ks = keys_of(a, b, ZP(a, b, pts, 4.6))
    kw = fixt(a, b, kw)
    rs = [dict(r) for r in rings]
    for r in rs:
        r["t"] = tl(a, r["t"])
        r.setdefault("angle", 225)
    d = dict(id=sid, type="city", start=round(a, 3), end=round(b, 3), tag=tag, city=city, view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, gz=gz, camera=ks, rings=rs, **kw)
    if flash is not None:
        d["flashT"] = tl(a, flash)
    add(**d)


def rk(FX, key, t, label=True):
    d = {"fire": {"km": FX["fireball_km"], "label": "FIREBALL", "color": WHITE}, "p20": {"km": FX["psi20_km"], "label": "20 PSI", "color": ORANGE},
         "p5": {"km": FX["psi5_km"], "label": "5 PSI", "color": RED}, "b": {"km": FX["thermal3_km"], "label": "BURNS", "color": AMBER},
         "p1": {"km": FX["psi1_km"], "label": "1 PSI", "color": TEAL}}[key]
    d = dict(d)
    d["t"] = t
    return d


def LR(upto, t):
    """London rings up to and including `upto`, all already drawn at t"""
    order = ["fire", "p20", "p5", "b", "p1"]
    return [rk(FXL, k, t) for k in order[:order.index(upto) + 1]]


EXT = {"clock": "", "clockLabel": ""}
W_UK = [-3.0, 55.0]

# ================================================================== Cold open [SIMULATION]
FL = round(W("p01", "Westminster") + 0.05, 2)        # the flash lands on "Westminster"
KA = W("p03", "launches")
TL_ = S("p04") - 0.4                                 # the London missile arrives just before p04
TF_ = round(KA + (TL_ - KA) * FAS_S["flight_min"] / LON_S["flight_min"], 2)
a, b = 0.0, FL
R("open-run", a, b, [("s", [1.0, 60.5], 3500), ("e", [-0.5, 54.0], 2300)], highlight=HL, legend=LEG, clock="T-08:48", clockLabel="UNTIL THE FLASH", clockRate=round(528 / FL, 1),
  ships=[ship([SUB, LON], 0.05, FL, "pla", RED, "BULAVA", 28)], lines=[ln(SUB, LON, 0.1, FL - 0.2, RED, None, True, 2)],
  cities=[mk(LON, "LONDON", 0.3, BLUE, "target", 8)], labels=[lb([-2.0, 66.0], "NORWEGIAN SEA", 0.2, WHITE), lb([-5.5, 56.6], "SCOTLAND", 0.9, BLUE)])
a, b = FL, W("p02", "built")
CT("open-flash", a, b, "london", LON, [(LON, 5.0), (LON, 9.0), (LON, 16.0)], rings=[rk(FXL, "p5", a + 1.0), rk(FXL, "p1", a + 2.6)], flash=a + 0.1, clock="T+00:00", clockLabel="THE FLASH", clockRate=1,
   labels=[lb(offp(LON, 0, 3.0), "100 KT AIR BURST (SIMULATED)", a + 0.6, WHITE), lb(offp(LON, -4.0, -2.5), "WESTMINSTER", a + 1.4, YELLOW)])
a, b = b, S("p03")
R("open-notreal", a, b, ZM(a, b, [-0.5, 52.0], 450, [-1.0, 53.0], 1300), highlight=HL, clock="T+00:30", clockLabel="THE FLASH", clockRate=1, burst={"at": LON, "t": a - 5.0, "km": 6, "fade": 9},
  cities=[mk(LON, "LONDON", a + 0.3, BLUE, "dot", 8)], labels=[lb([-2.5, 53.7], "IT HAS NOT HAPPENED", W("p02", "not"), YELLOW), lb([1.5, 51.2], "SIMULATION", a + 1.2, RED)])
# run-up: nine minutes earlier
a, b = S("p03"), KA
R("open-sub", a, b, ZM(a, b, [4.0, 66.0], 2200, [2.0, 63.0], 3000), highlight=HL, legend=LEG, caption="Nine minutes earlier.", clock="T+00:00", clockLabel="LAUNCH", clockRate=0,
  cities=[mk(SUB, "RUSSIAN SUBMARINE (SIMULATED)", W("p03", "submarine"), AMBER, "sub", 8)], labels=[lb([-4.5, 62.0], "NORWEGIAN SEA", W("p03", "Norwegian"), WHITE)])
a, b = KA, S("p04")
R("open-fly", a, b, ZP(a, b, [([-0.5, 62.0], 3100), ([-2.0, 57.5], 2400), ([-2.2, 55.0], 1500)], 3.0), highlight=HL, legend=LEG, **cd(a, TL_, KA, TL_, 528), burst={"at": FAS, "t": TF_, "km": 30, "fade": 6},
  ships=[fly(a, b, SUB, LON, KA, TL_, "TO LONDON", 28), fly(a, b, SUB, FAS, KA, TF_, "TO SCOTLAND", 28)], cities=[mk(LON, "LONDON", a + 1.0, BLUE, "target", 8), mk(FAS, "FASLANE", W("p03", "naval"), BLUE, "target", 8)],
  labels=[lb([5.5, 59.0], "7.6 AND 8.8 MINUTES", W("p03", "One"), YELLOW), lb([-6.5, 58.6], "SCOTLAND LANDS FIRST", W("p03", "first"), RED)])
a, b = S("p04"), W("p04", "Scottish")
CT("open-rush", a, b, "london", LON, [(LON, 40.0), (LON, 24.0)], clock="08:48", clockLabel="LONDON TIME", clockRate=0,
   labels=[fl(LON, -0.2, 0.3, 24, "MORNING RUSH HOUR", a + 0.3, YELLOW), fl(LON, 0.2, -0.3, 24, "WESTMINSTER", a + 1.2, WHITE)])
a, b = b, S("p05")
RR("open-two", a, b, [([-2.5, 54.6], 900), ([-2.5, 54.4], 1250)], legend=LEG, clock="T+07:36", clockLabel="SINCE LAUNCH", clockRate=1, caption="About 70 seconds apart.",
   cities=[mk(FAS, "FASLANE: 08:48", a + 0.2, RED, "target", 8), mk(LON, "LONDON: 08:49", W("p04", "London"), RED, "target", 8)], lines=[ln(FAS, LON, a + 1.0, a + 2.8, WHITE, "590 KM", True, 2)],
   burst={"at": FAS, "t": a - 5.0, "km": 25, "fade": 9})
a, b = S("p05"), W("p05", "And")
RR("open-why1", a, b, [(FAS, 700), (FAS, 380)], legend=LEG, labels=[lb(offp(FAS, 40, 55), "WHY SCOTLAND FIRST?", a + 0.3, YELLOW)], cities=[mk(FAS, "FASLANE", a + 0.5, BLUE, "base", 8)])
a, b = b, S("p06")
RR("open-why2", a, b, [([-0.5, 52.0], 450), ([-0.2, 51.6], 260)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "target", 8)], labels=[lb([-1.6, 52.4], "WHAT DO THREE DAYS MEAN?", W("p05", "three"), YELLOW)])

# ================================================================== Chapter 01 [REAL DATA]
SRC1 = "gov.uk, The UK's nuclear deterrent; SIPRI Yearbook 2026"
a = chapter("c1-card", S("p06"), 3.7, "CHAPTER 01", "The boats on the Clyde", "REAL DATA")
b = W("p06", "Since")
RR("c1-sea", a, b, [(BOATSEA, 2600), ([-11.0, 58.0], 1800)], tag="REAL DATA", legend=None, source=SRC1,
   ships=[ship([[-16.0, 56.0], [-12.0, 58.0], [-9.0, 59.5]], a, b, "ally", BLUE, "ONE BOAT AT SEA", 26)], labels=[lb([-12.5, 61.0], "NORTH ATLANTIC", a + 0.5, WHITE)])
a, b = b, b + 3.8
stamp("c1-1969", a, b, "APRIL 1969", "One boat on patrol since: not a single break", BLUE, "REAL HISTORY", source="gov.uk, National Endeavour explained")
a, b = b, S("p08") - 3.8
RR("c1-patrol", a, b, [([-11.0, 58.0], 2000), ([-8.0, 59.0], 2800)], tag="REAL DATA", source="SIPRI Yearbook 2026", ships=[ship([[-9.0, 59.5], [-14.0, 57.0], [-18.0, 58.5]], a, b, "ally", BLUE, "PATROL", 26)],
   labels=[lb([-13.0, 61.6], "NOT A SINGLE BREAK", a + 0.3, WHITE), lb([-14.0, 55.0], "ONCE: ABOUT TWO MONTHS", W("p07", "once"), WHITE)])
a, b = b, S("p08")
add(id="c1-bars", type="bars", start=round(a, 3), end=round(b, 3), tag="REAL DATA", title="DAYS ON PATROL", sub="Typical Royal Navy deterrent patrol", source="SIPRI Yearbook 2026; Navy Lookout",
    bars=[{"label": "1970S", "value": 65, "display": "60 TO 70", "color": WHITE}, {"label": "RECENT YEARS", "value": 175, "display": "150 TO 200", "color": BLUE}])
a, b = S("p08"), S("p09")
RR("c1-hold", a, b, [([-3.0, 56.5], 1800), (FAS, 700)], tag="REAL DATA", source=SRC1, cities=[mk(FAS, "FASLANE: WHERE BOTH START", W("p08", "Both"), BLUE, "base", 8)],
   labels=[lb([-9.0, 58.2], "THE UNBROKEN PATROL", W("p08", "unbroken"), WHITE), lb([-1.5, 57.7], "THE MINUTE BETWEEN FLASHES", W("p08", "minute"), YELLOW)])
a, b = S("p09"), W("p09", "Four")
RR("c1-clyde", a, b, [([-3.5, 54.8], 1100), ([-3.2, 55.0], 900)], tag="REAL DATA", source="gov.uk; HM Naval Base Clyde", legend=None, cities=[mk(FAS, "FASLANE, THE CLYDE", W("p09", "Faslane"), BLUE, "base", 8), mk(LON, "LONDON", W("p09", "London") if False else a + 2.0, BLUE, "dot", 8)],
   lines=[ln(FAS, LON, a + 2.2, a + 5.0, WHITE, "ABOUT 590 KM", True, 2)])
a, b = b, S("p10")
RR("c1-boats", a, b, [(FAS, 400), (FAS, 190), (FAS, 260)], tag="REAL DATA", source="gov.uk; SIPRI Yearbook 2026", legend=None,
   labels=[lb(offp(FAS, -35, 50), "4 VANGUARD-CLASS BOATS", a + 0.3, BLUE), lb(offp(FAS, 30, 45), "16 MISSILE TUBES EACH", W("p09", "sixteen"), WHITE), lb(offp(FAS, -35, -35), "ONE IN OVERHAUL", W("p09", "overhaul"), YELLOW), lb(offp(FAS, 35, -45), "THREE OPERATIONAL", W("p09", "three"), BLUE)],
   cities=[mk(FAS, None, a + 0.1, BLUE, "base", 8)])
a, b = S("p10"), W("p10", "Britain")
RR("c1-forty", a, b, [([-11.0, 58.0], 2300), ([-10.0, 58.5], 1700)], tag="REAL DATA", source="SIPRI Yearbook 2026", legend=None, ships=[ship([[-9.0, 59.5], [-12.0, 58.0]], a, b, "ally", BLUE, "THE BOAT AT SEA", 26)],
   labels=[lb([-12.0, 60.5], "ABOUT 40 WARHEADS ON IT", W("p10", "forty"), BLUE)])
a, b = b, W("p10", "rest")
stamp("c1-2021", a, b, "2021", "Britain stops publishing its warhead numbers", WHITE, "REAL DATA", source="SIPRI Yearbook 2026")
a, b = b, S("p11")
RR("c1-est", a, b, [([-3.0, 56.0], 1400), ([-3.0, 56.0], 2200)], tag="REAL DATA", source="SIPRI Yearbook 2026, Table 8A.4", legend=None,
   labels=[lb([-7.5, 58.6], "OUTSIDE ESTIMATES ONLY", a + 0.3, YELLOW), lb([-0.8, 57.6], "ABOUT 120 AVAILABLE", W("p10", "hundred"), WHITE), lb([-0.8, 56.4], "ABOUT 225 IN ALL", W("p10", "two"), WHITE)])
a, b = S("p11"), S("p12")
RR("c1-coulport", a, b, [(FAS, 380), (FAS, 190)], tag="REAL DATA", source="gov.uk; RNAD Coulport", legend=None, cities=[mk(FAS, "FASLANE", a + 0.3, BLUE, "base", 8), mk(COUL, "COULPORT: SPARE WARHEADS", W("p11", "Coulport"), BLUE, "base", 8)],
   lines=[ln(COUL, FAS, W("p11", "three"), W("p11", "three") + 1.4, WHITE, "ABOUT 3 KM", True, 2)])
a, b = S("p12"), W("p12", "One")
CT("c1-london", a, b, "london", LON, [(LON, 70.0), (LON, 40.0)], tag="REAL DATA", source="ONS mid-2024 estimate; GLA", labels=[fl(LON, -0.25, 0.3, 40, "ABOUT 9 MILLION PEOPLE", W("p12", "million"), WHITE), fl(LON, 0.2, -0.3, 40, "1,600 KM2", W("p12", "sixteen"), WHITE)])
a, b = b, S("p13")
RR("c1-pair", a, b, [([-3.0, 55.5], 1200), ([-3.0, 55.0], 1000)], tag="REAL DATA", source="gov.uk; ONS", legend=None, cities=[mk(FAS, "ONE BASE: THE DETERRENT", W("p12", "base"), BLUE, "base", 8), mk(LON, "ONE CITY: THE GOVERNMENT", W("p12", "city"), BLUE, "target", 8)])
a, b = S("p13"), S("p14")
RR("c1-october", a, b, [([-0.8, 52.4], 500), ([-0.2, 51.8], 280)], tag="REAL DATA", source="Cabinet Office, Be Ready, 22 October 2026", cities=[mk(LON, "LONDON", a + 0.3, BLUE, "target", 8)],
   labels=[lb([-2.3, 52.9], "OCTOBER: THE GOVERNMENT SPEAKS", W("p13", "October"), YELLOW), lb([1.2, 51.2], "WHEN THINGS STOP WORKING", W("p13", "stop"), WHITE)])

# ================================================================== Chapter 02 [REAL HISTORY]
SRC2 = "Wikipedia, Four-minute warning; Imperial War Museums"
a = chapter("c2-card", S("p14"), 3.7, "CHAPTER 02", "Four minutes, fourteen days, three days", "REAL HISTORY")
b = W("p14", "name")
RR("c2-hq", a, b, [([-0.9, 51.8], 380), ([-0.7, 51.9], 560)], tag="REAL HISTORY", source=SRC2, legend=None,
   cities=[mk(BOOK, "RAF BOOKER: HEADQUARTERS", W("p14", "RAF"), BLUE, "base", 8), mk(LON, "LONDON", a + 0.4, BLUE, "dot", 7), mk([-1.26, 51.75], "POLICE POSTS: ABOUT 250", W("p14", "police"), WHITE, "dot", 7)],
   lines=[ln(BOOK, LON, W("p14", "police"), W("p14", "police") + 1.4, WHITE, None, True, 2)], labels=[lb([-2.4, 52.3], "FROM 1953", a + 0.3, WHITE), lb([1.0, 51.3], "THOUSANDS OF SIRENS", W("p14", "sirens"), AMBER)])
a, b = b, S("p15")
RR("c2-gap", a, b, [([-0.3, 51.8], 520), ([-0.15, 51.6], 300)], tag="REAL HISTORY", source=SRC2, legend=None, clock="T-04:00", clockLabel="THE FOUR-MINUTE WARNING", clockRate=1,
   cities=[mk(LON, "IMPACT", a + 0.3, RED, "target", 8)], labels=[lb([-1.7, 52.1], "CONFIRMED ATTACK", a + 0.4, WHITE), lb([1.2, 52.1], "THE ESTIMATED GAP", W("p14", "estimated"), YELLOW)])
a, b = S("p15"), W("p15", "flights")
RR("c2-sirens", a, b, [([-1.0, 52.5], 600), ([-1.0, 52.5], 1000)], tag="REAL HISTORY", source=SRC2, legend=None, labels=[lb([-3.4, 53.9], "1992: THE WARNING ENDS", a + 0.3, YELLOW), lb([1.0, 51.4], "SIRENS DISMANTLED", W("p15", "siren"), WHITE)], cities=[mk(BOOK, None, a + 0.1, BLUE, "dot", 7)])
a, b = b, S("p16")
add(id="c2-bars", type="bars", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="WARNING TIME IN THE SIMULATION", sub="Minutes from launch to burst", source="Scenario engine",
    bars=[{"label": "1953 WARNING GAP", "value": 4, "display": "4 MIN", "color": WHITE}, {"label": "FASLANE", "value": 7.6, "display": "7.6 MIN", "color": RED}, {"label": "LONDON", "value": 8.8, "display": "8.8 MIN", "color": RED}])
a, b = S("p16"), W("p16", "told")
stamp("c2-1980", a, b, "MAY 1980", "Protect and Survive goes on public sale", WHITE, "REAL HISTORY", source="Wikipedia, Protect and Survive")
a, b = b, S("p17")
RR("c2-fallout", a, b, [([-1.5, 52.5], 1100), ([-1.0, 52.0], 480), ([-0.2, 51.6], 300)], tag="REAL HISTORY", source="Wikipedia, Protect and Survive", legend=None, cities=[mk(LON, "A HOME IN THE CITY", a + 0.5, BLUE, "dot", 8)],
   labels=[lb([-3.0, 53.0], "BUILD A FALLOUT ROOM", W("p16", "fallout"), WHITE), lb([1.0, 52.4], "STAY HOME: 14 DAYS", W("p16", "fourteen"), YELLOW), lb([-2.6, 51.3], "INNER REFUGE: FIRST 48 HOURS", W("p16", "inner"), AMBER)])
a, b = S("p17"), W("p17", "On")
add(id="c2-bars2", type="bars", start=round(a, 3), end=round(b, 3), tag="REAL HISTORY", title="HOW LONG TO STAY IN", sub="Official household guidance", source="Wikipedia, Protect and Survive; Cabinet Office",
    bars=[{"label": "1980: PROTECT AND SURVIVE", "value": 14, "display": "14 DAYS", "color": WHITE}, {"label": "2026: BE READY", "value": 3, "display": "ABOUT 3 DAYS", "color": BLUE}])
a, b = b, W("p17", "campaign")
stamp("c2-2026", a, b, "22 OCTOBER 2026", "The Cabinet Office launches Be Ready", BLUE, "REAL DATA", source="gov.uk; Cabinet Office")
a, b = b, S("p18")
RR("c2-ready", a, b, [(LON, 380), ([-0.15, 51.5], 250), ([-0.8, 52.4], 700)], tag="REAL DATA", source="gov.uk; Cabinet Office", cities=[mk(WATL, "CABINET OFFICE: WHITEHALL", a + 0.3, BLUE, "base", 8)],
   labels=[lb([-1.5, 52.2], "A THREE-YEAR CAMPAIGN", W("p17", "three"), WHITE), lb([1.2, 52.6], "ABOUT THREE DAYS", W("p17", "days"), YELLOW), lb([-2.0, 51.1], "POWER, WATER", W("p17", "power"), AMBER), lb([1.0, 51.0], "PHONE, INTERNET", W("p17", "phone"), AMBER)])
a, b = S("p18"), W("p18", "reports")
RR("c2-nonuc1", a, b, [([-2.0, 53.5], 1100), ([-1.5, 52.5], 800)], tag="REAL DATA", source="gov.uk; Al Jazeera, 22 October 2026", legend=None,
   labels=[lb([-4.5, 55.0], "NOT A NUCLEAR CAMPAIGN", a + 0.3, YELLOW), lb([-4.0, 53.6], "STORMS", W("p18", "storms"), WHITE), lb([1.0, 54.4], "WILDFIRES", W("p18", "wildfires"), WHITE), lb([0.5, 52.4], "NUCLEAR: NOT MENTIONED", W("p18", "mention"), RED)])
a, b = b, S("p19")
RR("c2-nonuc2", a, b, [([-1.0, 52.3], 600), ([-0.3, 51.7], 380)], tag="REAL DATA", source="Reports quoting the Defence Secretary, October 2026", legend=None, caption="No specific thing to prepare for, in reports of the Defence Secretary.",
   cities=[mk(WATL, "DEFENCE SECRETARY: QUOTED", W("p18", "Defence"), BLUE, "dot", 8)], labels=[lb([-2.4, 52.8], "NO SPECIFIC THING", W("p18", "specific"), YELLOW)])
a, b = S("p19"), S("p20")
CT("c2-hour", a, b, "london", LON, [(LON, 30.0), (LON, 16.0), (LON, 8.0)], tag="REAL DATA", source="Cabinet Office, Be Ready; gov.uk radiation guidance",
   labels=[fl(LON, -0.28, 0.3, 8, "THE KIT", W("p19", "kit"), WHITE), fl(LON, 0.28, 0.2, 8, "THE LIST", W("p19", "list"), WHITE), fl(LON, 0.0, -0.32, 8, "THE FIRST HOUR OF A STRIKE", W("p19", "first"), YELLOW)])
a, b = S("p20"), S("p21")
RR("c2-but", a, b, [(LON, 400), ([2.0, 60.0], 2800)], tag="REAL HISTORY", legend=LEG, cities=[mk(LON, "LONDON", a + 0.2, BLUE, "target", 8)], labels=[lb([-4.0, 58.0], "HOW DOES A STRIKE START?", W("p20", "how"), YELLOW)])

# ================================================================== Chapter 03 [SIMULATION]
a = chapter("c3-card", S("p21"), 3.7, "CHAPTER 03", "The trigger", "SIMULATION")
b = W("p21", "decides")
RR("c3-crisis", a, b, [([18.0, 56.0], 4300), ([12.0, 56.0], 3600)], legend=[{"text": "RUSSIA", "color": AMBER}, {"text": "NATO", "color": BLUE}],
   countryLabels=[cl(RUS, "RUSSIA", AMBER), cl(UK, "UNITED KINGDOM", BLUE)], labels=[lb([20.0, 62.0], "A CRISIS FOR WEEKS", W("p21", "crisis"), YELLOW)])
a, b = b, W("p21", "That")
RR("c3-decide", a, b, [([10.0, 57.0], 3400), ([-2.0, 55.0], 1700)], legend=LEG, lines=[ln([30.0, 59.0], LON, a + 0.4, a + 3.4, RED, "LIMITED STRIKE", True, 2), ln([30.0, 59.0], FAS, a + 0.6, a + 3.4, RED, None, True, 2)],
   cities=[mk(LON, "THE CAPITAL", W("p21", "capital"), BLUE, "target", 8), mk(FAS, "THE DETERRENT BASE", W("p21", "base"), BLUE, "target", 8)])
a, b = b, S("p22")
RR("c3-invent", a, b, [([-2.0, 55.0], 1200), ([-2.0, 55.0], 1700)], legend=LEG, labels=[lb([-6.0, 56.9], "OUR INVENTION", a + 0.3, YELLOW), lb([1.0, 53.4], "NO GOVERNMENT HAS SAID IT", W("p21", "government"), WHITE)])
a, b = S("p22"), W("p22", "The", 2)
RR("c3-bulava", a, b, [([3.0, 66.0], 2400), ([3.0, 65.0], 1800)], legend=LEG, cities=[mk(SUB, "BOREI-CLASS SUBMARINE", W("p22", "Borei-class"), AMBER, "sub", 8)], labels=[lb([-4.0, 62.5], "R-30 BULAVA", W("p22", "Bulava"), RED), lb([10.0, 63.0], "NORWEGIAN SEA", W("p22", "Norwegian"), WHITE)])
a, b = b, S("p23")
RR("c3-short", a, b, [([3.0, 64.0], 2800), ([0.0, 59.0], 3600), ([-0.5, 55.0], 2800)], legend=LEG, lines=[ln(SUB, LON, a + 0.5, a + 3.0, RED, "LESS THAN 9 MINUTES", True, 2)], cities=[mk(SUB, "LAUNCH POINT: SIMULATED", a + 0.2, AMBER, "sub", 8), mk(LON, "LONDON", a + 1.0, BLUE, "target", 8)],
   labels=[lb([8.0, 59.5], "SHORT FLIGHT, LITTLE TIME", W("p22", "short"), YELLOW)])
a, b = S("p23"), W("p23", "We")
RR("c3-yield", a, b, [(SUB, 2000), ([2.0, 62.0], 2600)], legend=LEG, cities=[mk(SUB, "BULAVA ESTIMATES", a + 0.3, AMBER, "sub", 8)], labels=[lb([-3.0, 66.0], "100 TO 150 KILOTONS", W("p23", "hundred"), WHITE), lb([10.0, 64.5], "PUBLISHED ESTIMATES", a + 1.0, YELLOW)])
a, b = b, S("p24")
add(id="c3-bars", type="bars", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="OUR CHOICE: 100 KILOTONS", sub="Yield in kilotons", source="Scenario engine; published Bulava estimates",
    bars=[{"label": "HIROSHIMA, 1945", "value": 15, "display": "15 KT", "color": ORANGE}, {"label": "THIS SIMULATION", "value": 100, "display": "100 KT, ABOUT 7 TIMES", "color": RED}])
a, b = S("p24"), S("p25")
RR("c3-ukwar", a, b, [(FAS, 700), ([-2.5, 54.5], 1300)], legend=LEG, cities=[mk(FAS, "FASLANE", a + 0.3, BLUE, "base", 8)], labels=[lb([-7.0, 57.5], "UK YIELD: NEVER PUBLISHED", W("p24", "never"), YELLOW), lb([1.5, 53.0], "NOT A CLAIM ABOUT IT", W("p24", "claim"), WHITE)])
a, b = S("p25"), W("p25", "first")
RR("c3-two", a, b, [([3.0, 62.0], 3300), ([0.0, 58.0], 3000)], legend=LEG, ships=[], cities=[mk(SUB, "SUBMARINE", a + 0.2, AMBER, "sub", 8)], lines=[ln(SUB, LON, a + 0.6, a + 2.4, RED, None, True, 2), ln(SUB, FAS, a + 0.9, a + 2.6, RED, None, True, 2)],
   labels=[lb([-6.0, 60.5], "TWO WARHEADS, ONE EACH", W("p25", "Two"), YELLOW)])
a, b = b, W("p25", "second")
RR("c3-first", a, b, [([-3.0, 60.0], 2200), (FAS, 900)], legend=LEG, lines=[ln(SUB, FAS, a + 0.4, a + 2.6, RED, "ABOUT 1,400 KM", True, 3)], cities=[mk(FAS, "FASLANE AND COULPORT", W("p25", "Faslane"), BLUE, "target", 8)])
a, b = b, S("p26")
RR("c3-second", a, b, [([-1.0, 58.0], 2200), ([-0.5, 54.0], 1500)], legend=LEG, lines=[ln(SUB, LON, a + 0.4, a + 3.0, RED, "ABOUT 1,840 KM", True, 3)], cities=[mk(LON, "WESTMINSTER AND WHITEHALL", W("p25", "Westminster"), BLUE, "target", 8), mk(FAS, None, a, BLUE, "dot", 6)])
a, b = S("p26"), W("p26", "One")
RR("c3-remove", a, b, [(FAS, 600), (FAS, 300)], legend=LEG, cities=[mk(FAS, "FASLANE: THE DETERRENT", a + 0.3, BLUE, "base", 8)], labels=[lb(offp(FAS, 35, 55), "REMOVE THE DETERRENT", W("p26", "remove"), RED)])
a, b = b, S("p27")
RR("c3-atsea", a, b, [([-8.0, 57.5], 1700), ([-9.0, 58.0], 2400)], legend=LEG, ships=[ship([[-14.0, 56.0], [-10.5, 58.0], [-8.0, 59.0]], a, b, "ally", BLUE, "BOAT AT SEA: NOT IN PORT", 26)],
   labels=[lb([-10.0, 60.5], "ALWAYS ONE AT SEA", W("p26", "One"), WHITE), lb([-4.0, 57.0], "THE BOATS IN PORT", W("p26", "boats"), AMBER)])
a, b = S("p27"), S("p28")
RR("c3-eight", a, b, [([-2.5, 54.5], 900), ([-1.5, 54.0], 1500)], step=3.0, legend=LEG, clock="T+00:00", clockLabel="THE EIGHT MINUTES", clockRate=0,
   cities=[mk(FAS, "FASLANE", a + 0.4, BLUE, "target", 8), mk(LON, "LONDON", a + 1.4, BLUE, "target", 8)], labels=[lb([-6.0, 56.9], "THE FIRST QUESTION", W("p27", "first"), YELLOW), lb([2.0, 52.3], "THE EIGHT MINUTES", W("p27", "eight"), RED)])

# ================================================================== Chapter 04 [SIMULATION]
LA = S("p28") + 3.7
FB, LB = W("p31", "bursts"), W("p35", "bursts")


def SF(t):
    if t <= LA:
        return 0.0
    if t <= FB:
        return 456.0 * (t - LA) / (FB - LA)
    if t <= LB:
        return 456.0 + 72.0 * (t - FB) / (LB - FB)
    return 528.0 + (t - LB)


def ck(a, b):
    s0, s1 = SF(a), SF(b)
    v = int(round(s0))
    return {"clock": f"T+{v // 60:02d}:{v % 60:02d}", "clockLabel": "SINCE LAUNCH", "clockRate": round((s1 - s0) / (b - a), 3)}


def BOTH(a, b):
    return [fly(a, b, SUB, FAS, LA, FB, "TO FASLANE", 28), fly(a, b, SUB, LON, LA, LB, "TO LONDON", 28)]


a = chapter("c4-card", S("p28"), 3.7, "CHAPTER 04", "Minute by minute", "SIMULATION")
b = S("p29")
RR("c4-launch", a, b, [([3.0, 66.0], 1800), ([1.0, 62.0], 3000)], legend=LEG, **ck(a, b), ships=BOTH(a, b), cities=[mk(SUB, "RUSSIAN SUBMARINE (SIMULATED)", a + 0.2, AMBER, "sub", 8)], labels=[lb([-5.0, 63.0], "08:40: MISSILES LEAVE", a + 0.5, RED)])
a, b = S("p29"), W("p29", "missiles")
CT("c4-sky", a, b, "london", LON, [(LON, 30.0), (LON, 18.0)], clock="T+00:40", clockLabel="SINCE LAUNCH", clockRate=round(SF(b) / 1 and (SF(b) - SF(a)) / (b - a), 2),
   labels=[fl(LON, -0.2, 0.3, 18, "A NORMAL MORNING SKY", W("p29", "sky"), WHITE), fl(LON, 0.25, -0.3, 18, "NOTHING VISIBLE YET", a + 0.4, YELLOW)])
a, b = b, S("p30")
RR("c4-inair", a, b, [([-1.0, 59.0], 2600), ([-1.5, 56.5], 1800)], legend=LEG, **ck(a, b), ships=BOTH(a, b), labels=[lb([5.0, 60.0], "IN THE AIR: UNDER 9 MINUTES", W("p29", "flight"), RED)], cities=[mk(LON, "LONDON", a + 0.3, BLUE, "dot", 8), mk(FAS, "FASLANE", a + 0.3, BLUE, "dot", 8)])
a, b = S("p30"), W("p30", "Faslane")
RR("c4-clocks", a, b, [([-2.5, 56.5], 1300), ([-1.5, 54.5], 1800)], legend=LEG, **ck(a, b), ships=BOTH(a, b), labels=[lb([-8.0, 57.6], "THE CLOCKS MATTER MORE", a + 0.3, YELLOW)])
a, b = b, W("p30", "In")
RR("c4-times", a, b, [([-2.5, 54.8], 1100), ([-1.5, 54.0], 1500)], legend=LEG, **ck(a, b), ships=BOTH(a, b), cities=[mk(FAS, "FASLANE: ABOUT 08:48", W("p30", "Faslane"), RED, "target", 8), mk(LON, "LONDON: ABOUT 08:49", W("p30", "London"), RED, "target", 8)])
a, b = b, S("p31")
CT("c4-morning", a, b, "london", LON, [(LON, 30.0), (LON, 40.0), (LON, 24.0)], **ck(a, b), labels=[fl(LON, -0.2, 0.3, 24, "NINE MILLION PEOPLE", W("p30", "nine"), WHITE), fl(LON, 0.2, -0.3, 24, "THE MORNING GOES ON", W("p30", "morning"), YELLOW)])
a, b = S("p31"), FB
RR("c4-arrive", a, b, [(FAS, 500), (FAS, 220)], legend=LEG, **ck(a, b), ships=BOTH(a, b), cities=[mk(FAS, "FASLANE", a + 0.2, BLUE, "target", 8)], labels=[lb(offp(FAS, -45, 40), "7.6 MINUTES", a + 0.4, RED)])
a, b = FB, W("p31", "Blast")
CT("c4-faslane", a, b, "faslane", FAS, [(FAS, 5.0), (FAS, 3.2)], rings=[rk(FXF, "fire", a + 0.4)], flash=a + 0.1, **ck(a, b), caption="Ground burst, 100 kt. Ring sizes from the engine.",
   labels=[lb(offp(FAS, 0, 1.2), "GROUND BURST (SIMULATED)", a + 0.8, WHITE), lb(offp(FAS, -1.6, -1.0), "FIREBALL: ABOUT 0.5 KM", W("p31", "fireball"), ORANGE)])
a, b = b, S("p32")
CT("c4-fpsi", a, b, "faslane", FAS, [(FAS, 3.6), (FAS, 9.0)], rings=[rk(FXF, "fire", a - 3), rk(FXF, "p20", a + 0.4), rk(FXF, "p5", W("p31", "Five"))], **ck(a, b),
   labels=[lb(offp(FAS, 0, 1.5), "20 PSI: JUST OVER 0.5 KM", a + 0.8, RED), lb(offp(FAS, 2.6, -2.0), "5 PSI: 2.5 KM", W("p31", "Five"), RED)])
a, b = S("p32"), S("p33")
CT("c4-heavy", a, b, "faslane", FAS, [(FAS, 10.0), (FAS, 24.0), (FAS, 40.0)], rings=[rk(FXF, "fire", a - 3), rk(FXF, "p20", a - 3), rk(FXF, "p5", a - 3)], **ck(a, b),
   labels=[fl(FAS, -0.28, 0.3, 10, "EARTH THROWN UP", W("p32", "earth"), WHITE), fl(FAS, 0.2, 0.2, 10, "IT COMES DOWN AS FALLOUT", W("p32", "fallout"), AMBER), fl(FAS, 0.0, -0.35, 10, "ENGINE: HEAVY LOCAL FALLOUT", W("p32", "engine"), RED)])
a, b = S("p33"), W("p33", "We")
RR("c4-wind", a, b, [(FAS, 500), ([-3.0, 56.2], 900)], legend=LEG, **ck(a, b), burst={"at": FAS, "t": a - 5.0, "km": 12, "fade": 10},
   plume={"at": FAS, "bearing": 90, "lengthKm": 230, "widthKm": 22, "t0": a + 3.0, "t1": a + 6.5, "color": AMBER, "label": "WIND FROM THE WEST"}, labels=[lb([-7.5, 57.6], "THE COMMONEST WIND", W("p33", "commonest"), WHITE)], cities=[mk(FAS, "FASLANE", a + 0.2, BLUE, "target", 8)])
a, b = b, S("p34")
RR("c4-nodose", a, b, [([-2.0, 56.2], 900), ([-1.0, 55.6], 1300)], legend=LEG, **ck(a, b), plume={"at": FAS, "bearing": 90, "lengthKm": 230, "widthKm": 22, "t0": -2.0 + a, "t1": a + 0.2, "color": AMBER},
   labels=[lb([-1.0, 57.4], "CENTRAL SCOTLAND", a + 0.3, WHITE), lb([-6.0, 54.9], "WIND: OUR CHOICE", W("p33", "choose"), YELLOW), lb([1.5, 54.4], "NO DOSE, NO TOWNS MODELLED", W("p33", "model"), YELLOW)])
a, b = S("p34"), W("p34", "Today's")
RR("c4-1992", a, b, [([-1.0, 52.6], 800), ([-0.4, 51.9], 450)], legend=None, **ck(a, b), ships=[fly(a, b, SUB, LON, LA, LB, "TO LONDON", 28)], labels=[lb([-3.0, 53.6], "1992: SIRENS GONE", W("p34", "ended"), WHITE)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "target", 8)])
a, b = b, S("p35")
RR("c4-advice", a, b, [([-0.5, 52.0], 420), ([-0.2, 51.6], 260)], legend=None, **ck(a, b), ships=[fly(a, b, SUB, LON, LA, LB, "TO LONDON", 28)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "target", 8)],
   labels=[lb([-1.6, 52.5], "GO IN", W("p34", "go"), WHITE), lb([1.0, 52.5], "STAY IN", W("p34", "stay"), WHITE), lb([-1.6, 51.3], "TUNE IN", W("p34", "tune"), WHITE), lb([1.0, 51.3], "NO NUCLEAR WEAPON NAMED", W("p34", "mention"), RED)])
a, b = S("p35"), LB
RR("c4-last", a, b, [(LON, 160), (LON, 170)], legend=None, **ck(a, b), ships=[fly(a, b, SUB, LON, LA, LB, "TO LONDON", 28)], cities=[mk(LON, "WHITEHALL", a + 0.2, BLUE, "target", 8)], labels=[lb(offp(LON, -35, 25), "8.8 MINUTES", a + 0.4, RED)])
a, b = LB, S("p36")
CT("c4-flash", a, b, "london", LON, [(LON, 6.0), (LON, 11.0)], rings=[rk(FXL, "fire", a + 0.4)], flash=a + 0.1, clock="T+08:48", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[lb(offp(LON, 0, 3.4), "AIR BURST OVER WHITEHALL", a + 0.8, WHITE)])
a, b = S("p36"), S("p37")
CT("c4-one", a, b, "london", LON, [(LON, 14.0), (LON, 9.0), (LON, 30.0)], rings=[rk(FXL, "fire", a - 3)], clock="T+08:57", clockLabel="SINCE LAUNCH", clockRate=1, burst={"at": LON, "t": a - 4.0, "km": 1.2, "fade": 9},
   labels=[fl(LON, -0.25, 0.3, 9, "ONE WARHEAD", W("p36", "One"), RED), fl(LON, 0.25, -0.3, 9, "ONE CITY", W("p36", "city"), WHITE), fl(LON, 0.0, 0.3, 9, "RING BY RING", W("p36", "ring"), YELLOW)])

# ================================================================== Chapter 05 [SIMULATION]
a = chapter("c5-card", S("p37"), 3.7, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
b = S("p38")
CT("c5-fire", a, b, "london", LON, [(LON, 1.4), (LON, 2.6)], rings=[rk(FXL, "fire", a + 0.2)], clock="T+09:00", clockLabel="SINCE LAUNCH", clockRate=1, burst={"at": LON, "t": a - 4.0, "km": 0.6, "fade": 8},
   labels=[lb(offp(LON, 0, 0.5), "FIREBALL: 380 M RADIUS", W("p37", "radius"), ORANGE), lb(offp(LON, -0.7, -0.4), "EVERYTHING INSIDE VAPORISED", W("p37", "vaporised"), WHITE)])
a, b = S("p38"), S("p39")
CT("c5-20", a, b, "london", LON, [(LON, 2.0), (LON, 3.4), (LON, 3.0)], rings=[rk(FXL, "fire", a - 3), rk(FXL, "p20", W("p38", "six"))], clock="T+09:10", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[lb(offp(LON, 0.4, 0.7), "20 PSI: 640 M", W("p38", "six"), RED), lb(offp(LON, -0.9, -0.6), "HEAVY BUILDINGS DO NOT STAND", W("p38", "Heavy"), WHITE)])
a, b = S("p39"), W("p39", "That")
CT("c5-5a", a, b, "london", LON, LR("p20", a - 3)[:0] and [] or [(LON, 5.0), (LON, 8.0)], rings=LR("p20", a - 3) + [rk(FXL, "p5", W("p39", "three"))], clock="T+09:20", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[lb(offp(LON, 1.8, 1.4), "5 PSI: 3.1 KM", W("p39", "three"), RED), lb(offp(LON, -2.2, -1.5), "MOST HOUSES COLLAPSE", W("p39", "collapse"), WHITE)])
a, b = b, S("p40")
CT("c5-5b", a, b, "london", LON, [(LON, 8.0), (LON, 16.0)], rings=LR("p5", a - 3), clock="T+09:30", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[fl(LON, 0.2, 0.3, 8, "31 KM2 INSIDE THE RING", W("p39", "thirty-one"), YELLOW), fl(LON, -0.25, -0.3, 8, "ABOUT 2% OF GREATER LONDON", W("p39", "percent"), WHITE)])
a, b = S("p40"), S("p41")
CT("c5-burns", a, b, "london", LON, [(LON, 9.0), (LON, 13.0)], rings=LR("p5", a - 3) + [rk(FXL, "b", W("p40", "four"))], clock="T+09:40", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[lb(offp(LON, 2.6, 2.0), "THIRD-DEGREE BURNS: 4.2 KM", W("p40", "burns"), AMBER), lb(offp(LON, -3.4, -2.4), "BARE SKIN, FROM THE FLASH", W("p40", "skin"), WHITE)])
a, b = S("p41"), S("p42")
CT("c5-1psi", a, b, "london", LON, [(LON, 13.0), (LON, 19.0), (LON, 26.0)], rings=LR("b", a - 3) + [rk(FXL, "p1", W("p41", "eight"))], clock="T+09:50", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[lb(offp(LON, 4.5, 3.4), "1 PSI: 8.5 KM", W("p41", "eight"), TEAL), lb(offp(LON, -5.5, -3.6), "WINDOWS SHATTER", W("p41", "Windows"), WHITE), lb(offp(LON, 4.0, -4.0), "FLYING GLASS INJURES", W("p41", "flying"), YELLOW)])
a, b = S("p42"), S("p43")
CT("c5-air", a, b, "london", LON, [(LON, 26.0), (LON, 40.0), (LON, 50.0)], rings=LR("p1", a - 3), clock="T+10:00", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[fl(LON, -0.25, 0.3, 26, "AIR BURST: LITTLE FALLOUT", W("p42", "small"), AMBER), fl(LON, 0.25, -0.3, 26, "SMOKE AND DUST: NOT MODELLED", W("p42", "smoke"), YELLOW)])
a, b = S("p43"), W("p43", "We")
CT("c5-people", a, b, "london", LON, [(LON, 50.0), (LON, 28.0)], rings=LR("p1", a - 3), clock="T+10:30", clockLabel="SINCE LAUNCH", clockRate=1, source="ONS mid-2024 estimate; GLA",
   labels=[fl(LON, -0.25, 0.3, 28, "ABOUT 5,800 PEOPLE PER KM2", W("p43", "five"), WHITE), fl(LON, 0.2, -0.3, 28, "THE MORNING RUSH MOVES THEM", W("p43", "rush"), YELLOW)])
a, b = b, S("p44")
CT("c5-count", a, b, "london", LON, [(LON, 28.0), (LON, 20.0)], rings=LR("p1", a - 3), clock="T+10:40", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[fl(LON, 0.0, 0.3, 20, "WE DO NOT COUNT WHO IS INSIDE", W("p43", "not"), YELLOW)])
a, b = S("p44"), S("p45")
CT("c5-engine", a, b, "london", LON, [(LON, 20.0), (LON, 34.0), (LON, 24.0)], rings=LR("p1", a - 3), clock="T+10:50", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[fl(LON, -0.25, 0.3, 20, "ENGINE: 100 KT AIR BURST", W("p44", "engine's"), WHITE), fl(LON, 0.2, -0.3, 20, "A LARGER WARHEAD, LARGER RINGS", W("p44", "larger"), RED)])
a, b = S("p45"), W("p46", "That") if False else S("p46")
CT("c5-nostudy", a, b, "london", LON, [(LON, 24.0), (LON, 14.0), (LON, 30.0)], rings=LR("p1", a - 3), clock="T+11:00", clockLabel="SINCE LAUNCH", clockRate=1,
   labels=[fl(LON, -0.25, 0.3, 14, "NO PUBLISHED STUDY", W("p45", "published"), YELLOW), fl(LON, 0.25, -0.3, 14, "WE WILL NOT MAKE ONE UP", W("p45", "make"), WHITE), fl(LON, -0.2, -0.05, 14, "ELECTRONICS: NOT MODELLED", W("p45", "electronics"), WHITE)])
a, b = S("p46"), S("p47")
RR("c5-minute", a, b, [(LON, 80), ([-0.5, 52.0], 900)], legend=None, clock="T+11:30", clockLabel="SINCE LAUNCH", clockRate=1, burst={"at": LON, "t": a - 5.0, "km": 6, "fade": 10},
   rings=[rg(LON, round(FXL["psi1_km"], 2), a + 0.2, TEAL, None, True)], labels=[lb([-2.0, 52.6], "THAT IS THE FIRST MINUTE", a + 0.4, YELLOW), lb([1.2, 51.2], "THE REST IS THE DAY AFTER", W("p46", "rest"), WHITE)])

# ================================================================== Chapter 06 [SIMULATION]
LD = {"clock": "", "clockLabel": ""}
a = chapter("c6-card", S("p47"), 3.7, "CHAPTER 06", "The day after", "SIMULATION")
b = W("p47", "Be")
CT("c6-zone", a, b, "london", LON, [(LON, 9.0), (LON, 7.0)], rings=LR("p5", a - 3)[2:], caption="The first change: a zone.", labels=[lb(offp(LON, 2.5, 1.8), "THE 5 PSI ZONE", a + 0.4, RED)])
a, b = b, W("p47", "Inside")
CT("c6-list", a, b, "london", LON, [(LON, 7.0), (LON, 5.0)], rings=LR("p5", a - 3)[2:], source="Cabinet Office, Be Ready",
   labels=[fl(LON, -0.3, 0.32, 5, "WATER", W("p47", "water"), WHITE), fl(LON, 0.0, 0.34, 5, "LONG-LIFE FOOD", W("p47", "food"), WHITE), fl(LON, 0.3, 0.3, 5, "TORCH", W("p47", "torch"), WHITE),
           fl(LON, -0.3, -0.34, 5, "BATTERIES", W("p47", "batteries"), WHITE), fl(LON, 0.0, -0.1, 5, "POWER BANK", W("p47", "power"), WHITE), fl(LON, 0.3, -0.34, 5, "RADIO", W("p47", "radio"), WHITE)])
a, b = b, S("p48")
CT("c6-collapse", a, b, "london", LON, [(LON, 5.0), (LON, 8.0)], rings=LR("p5", a - 3), labels=[fl(LON, -0.25, 0.3, 5, "IN HOUSES THAT COLLAPSE", W("p47", "collapse"), RED), fl(LON, 0.25, -0.3, 5, "THE LIST IS INSIDE THE RING", a + 0.6, YELLOW)])
a, b = S("p48"), W("p48", "Back")
RR("c6-plume", a, b, [(FAS, 600), ([-2.5, 56.3], 900)], legend=LEG, burst={"at": FAS, "t": a - 5.0, "km": 12, "fade": 12}, plume={"at": FAS, "bearing": 90, "lengthKm": 230, "widthKm": 22, "t0": a + 1.0, "t1": a + 4.0, "color": AMBER, "label": "ASSUMED WIND"},
   cities=[mk(FAS, "FASLANE", a + 0.2, BLUE, "target", 8)], labels=[lb([-7.0, 57.6], "THE SECOND: A PLUME", a + 0.4, YELLOW), lb([1.5, 57.2], "FAR TO THE NORTH", W("p48", "north"), WHITE)])
a, b = b, W("p48", "Neither")
RR("c6-stay", a, b, [([-3.0, 55.5], 1000), ([-2.0, 54.5], 1500)], legend=None, plume={"at": FAS, "bearing": 90, "lengthKm": 230, "widthKm": 22, "t0": -1.0 + a, "t1": a, "color": AMBER}, source="gov.uk, radiation emergencies; Protect and Survive",
   labels=[lb([-7.0, 56.8], "RADIATION ADVICE: 1 TO 2 DAYS", W("p48", "stay"), BLUE), lb([1.5, 55.2], "PROTECT AND SURVIVE: 14", W("p48", "Protect"), WHITE)])
a, b = b, S("p49")
RR("c6-neither", a, b, [(FAS, 700), (FAS, 380)], legend=LEG, plume={"at": FAS, "bearing": 90, "lengthKm": 230, "widthKm": 22, "t0": -1.0 + a, "t1": a, "color": AMBER}, cities=[mk(FAS, "A SUBMARINE BASE", W("p48", "begins"), BLUE, "base", 8)],
   labels=[lb(offp(FAS, 45, 55), "NEITHER WAS WRITTEN FOR THIS", a + 0.4, YELLOW)])
a, b = S("p49"), W("p49", "Three")
CT("c6-glass", a, b, "london", LON, [(LON, 22.0), (LON, 26.0)], rings=LR("p1", a - 3), labels=[fl(LON, -0.25, 0.3, 22, "THE THIRD: BROKEN GLASS", a + 0.3, YELLOW), fl(LON, 0.25, -0.3, 22, "1 PSI: 8.5 KM", W("p49", "ring"), TEAL)])
a, b = b, W("p49", "Here")
RR("c6-three", a, b, [([-1.5, 53.0], 1200), ([-1.5, 52.5], 800)], legend=None, labels=[lb([-4.0, 54.0], "PLANNED FOR STORMS", W("p49", "storms"), WHITE), lb([1.0, 53.5], "A FEW DAYS WITHOUT POWER", W("p49", "power"), WHITE)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "dot", 8)])
a, b = b, W("p49", "London")
CT("c6-hub", a, b, "london", LON, [(LON, 12.0), (LON, 9.0)], rings=LR("p5", a - 3), cities=[mk(WATL, "WATERLOO: TRANSPORT HUB", a + 0.6, WHITE, "dot", 7)],
   labels=[fl(LON, -0.28, 0.3, 9, "CENTRE OF GOVERNMENT", W("p49", "government"), BLUE), fl(LON, 0.25, -0.3, 9, "INSIDE THE DAMAGE", W("p49", "damage"), RED)])
a, b = b, S("p50")
RR("c6-economy", a, b, [([-1.5, 53.0], 900), ([-1.5, 53.5], 1500)], legend=None, source="ONS via GLA, London in figures", cities=[mk(LON, "LONDON: ABOUT A FIFTH OF THE ECONOMY", a + 0.4, BLUE, "target", 8)])
a, b = S("p50"), W("p50", "The", 2)
CT("c6-radio1", a, b, "london", LON, [(LON, 30.0), (LON, 16.0)], rings=LR("p1", a - 3), labels=[fl(LON, -0.25, 0.3, 16, "THE FOURTH: A RADIO", a + 0.3, YELLOW)])
a, b = b, W("p50", "because")
RR("c6-radio2", a, b, [([-1.0, 52.3], 700), ([-0.3, 51.8], 450)], legend=None, source="gov.uk, radiation emergencies; Cabinet Office, Be Ready", labels=[lb([-3.0, 52.9], "ADVICE: TUNE IN", W("p50", "tune"), WHITE), lb([1.0, 52.6], "RADIO: ON THE LIST", W("p50", "battery"), BLUE), lb([-2.6, 51.3], "WHAT DOES IT SOUND LIKE?", W("p50", "sounds"), YELLOW)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "dot", 8)])
a, b = b, S("p51")
RR("c6-examples", a, b, [([-1.5, 53.5], 1300), ([-1.5, 53.0], 1000)], legend=None, source="gov.uk, radiation emergencies", labels=[lb([-4.0, 54.6], "EXAMPLES: POWER PLANTS", W("p50", "power"), WHITE), lb([1.0, 53.8], "TRANSPORT ACCIDENTS", W("p50", "transport"), WHITE), lb([-3.5, 52.3], "NO NUCLEAR WEAPON", W("p50", "examples"), RED)])
a, b = S("p51"), W("p51", "In")
CT("c6-command", a, b, "london", LON, [(LON, 14.0), (LON, 7.0)], rings=LR("p5", a - 3), cities=[mk(LON, "WHITEHALL", a + 0.4, BLUE, "base", 8)],
   labels=[fl(LON, -0.28, 0.32, 7, "THE FIFTH: A COMMAND LINE", a + 0.3, YELLOW), fl(LON, 0.28, -0.3, 7, "ONLY THE PRIME MINISTER", W("p51", "Only"), WHITE)])
a, b = b, W("p51", "What")
CT("c6-inside", a, b, "london", LON, [(LON, 8.0), (LON, 12.0)], rings=LR("p5", a - 3), labels=[fl(LON, -0.28, 0.3, 8, "WHITEHALL: INSIDE 5 PSI", a + 0.3, RED)], cities=[mk(LON, None, a, RED, "target", 8)])
a, b = b, S("p52")
RR("c6-question", a, b, [(LON, 300), ([-1.0, 53.0], 1500)], legend=None, labels=[lb([-3.0, 52.8], "WHAT BECOMES OF AUTHORITY?", a + 0.4, YELLOW), lb([1.5, 51.2], "A QUESTION, NOT AN ANSWER", W("p51", "pose"), WHITE)], cities=[mk(LON, "LONDON", a + 0.2, BLUE, "target", 8)])
a, b = S("p52"), W("p52", "The", 3)
RR("c6-route", a, b, [([-10.0, 58.0], 2400), ([-9.0, 58.5], 1800)], legend=None, ships=[ship([[-14.0, 56.0], [-11.0, 58.0], [-8.5, 59.2]], a, b, "ally", BLUE, "THE BOAT KEEPS PATROLLING", 26)],
   labels=[lb([-13.0, 60.8], "THE SIXTH: A ROUTE", a + 0.3, YELLOW), lb([-5.0, 57.0], "IT DOES NOT CHANGE", W("p52", "not"), WHITE)])
a, b = b, S("p53")
RR("c6-doctrine", a, b, [([-9.0, 58.5], 1800), ([-6.0, 58.0], 2700)], legend=None, ships=[ship([[-8.5, 59.2], [-6.0, 60.0]], a, b, "ally", BLUE, "PATROL", 26)], source="gov.uk, National Endeavour explained",
   labels=[lb([-12.0, 61.0], "EXTREME CIRCUMSTANCES", W("p52", "extreme"), WHITE), lb([-3.0, 56.4], "DELIBERATE AMBIGUITY", W("p52", "deliberate"), YELLOW)])
a, b = S("p53"), S("p54")
RR("c6-end", a, b, [([-9.0, 58.5], 1900), ([-3.0, 56.0], 3200)], legend=None, ships=[ship([[-6.0, 60.0], [-9.0, 58.5]], a, a + 6.0, "ally", BLUE, "THE BOAT ON PATROL", 26)],
   labels=[lb([-12.5, 61.0], "THE ONE THING WE DO NOT DECIDE", W("p53", "one"), YELLOW), lb([0.0, 53.8], "IT HAS NOT HAPPENED", W("p53", "not", 2), RED)], cities=[mk(LON, "LONDON", a + 0.3, BLUE, "dot", 8)])

# ------------------------------------------------------------------ End slate
add(id="end", type="endslate", start=round(S("p54"), 3), end=END, tag="", title="Next scenario", line="Tsar Bomba, the largest bomb ever built, on London, Tokyo and New York.")

# ------------------------------------------------------------------ audio plan and output
b0 = max(0.0, round(min(FL - 0.3, W("p02", "simulation") - 0.3), 2))
booms = [round(FL + 0.1, 2), round(TF_ + 0.1, 2), round(FB + 0.1, 2), round(LB + 0.1, 2)]
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p06") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p21") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p21") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
