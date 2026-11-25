"""Director pass for episode 018: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 018-kaliningrad-suwalki-gap
Payoff first: the 5 kt airburst over open farmland in eastern Kaliningrad inside 4 s under the banner (a city shot on the
real OSM data), the run-up (the Iskander from a simulated site), real data and history, the thirteen-day crisis, ring by
ring, the day after.  All times in this file are absolute seconds; R(), C() convert items to shot-local time.
Actors: Russia amber, NATO (Poland, Lithuania, Germany, the US) blue, red only for strikes. Roads and rail routes are
approximate and say so.
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


# ------------------------------------------------------------------ places (lon, lat)
ST_BALT, ST_MAR, ST_WARN = sc["strikes"]
FX = ST_WARN["effects"]
B = [ST_WARN["target_lon"], ST_WARN["target_lat"]]        # warning burst, simulated
# Display launch site: the scenario point (54.38N, 20.64E) sits on the Polish border, so the map shows a simulated site
# inside the oblast at the same 98 km range (bearing about 84 degrees from it).
LA = [20.67, 54.62]
LA2 = [ST_MAR["launch_lon"], ST_MAR["launch_lat"]]
MAR = [ST_MAR["target_lon"], ST_MAR["target_lat"]]
BALT = [ST_BALT["target_lon"], ST_BALT["target_lat"]]
PLS = [ST_BALT["launch_lon"], ST_BALT["launch_lat"]]
KAL, VIL, KAU, WAR, GDA = [20.51, 54.71], [25.28, 54.69], [23.9, 54.9], [21.01, 52.23], [18.65, 54.35]
RIGA, MOS, SPB, BRU, DUB = [24.1, 56.95], [37.62, 55.75], [30.3, 59.93], [4.35, 50.85], [-6.26, 53.35]
BER, WIES, SUW, GRO, KYB = [13.4, 52.52], [8.24, 50.08], [22.93, 54.10], [23.83, 53.68], [22.78, 54.64]
OBLAST = [21.2, 54.55]
RU, BY, PL, LT, LV, EE, DE = "643", "112", "616", "440", "428", "233", "276"
GAP_A, GAP_B = [22.85, 54.36], [23.5, 53.95]               # the 65 km gap: Kaliningrad border to Belarus border (approximate)
# approximate routes (drawn as "approximate")
ROAD1 = [[21.01, 52.23], [23.16, 53.13], [22.96, 53.95], SUW, MAR, KAU]                # Via Baltica (E67)
ROAD2 = [[23.16, 53.13], [23.45, 53.85], [23.2, 54.35], [23.7, 54.7], KAU]
RAIL1 = [[21.01, 52.23], [23.16, 53.13], [23.1, 54.0], [23.45, 54.45], KAU]
RAIL_KAL = [KAL, KYB, KAU, VIL, [26.2, 54.5]]
KMX, KMY = 64.6, 111.0


def offp(c, dx, dy):
    return [round(c[0] + dx / KMX, 5), round(c[1] + dy / KMY, 5)]


def circle(c, km, n=48):
    return [offp(c, km * math.cos(math.radians(d)), km * math.sin(math.radians(d))) for d in range(0, 360, 360 // n)]


def hl(iso, color, a=0.10):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return {"iso": iso, "color": color, "fill": f"rgba({r},{g},{b},{a})"}


def cl(iso, text, color):
    return {"iso": iso, "text": text, "color": color}


H_RU, H_BY = hl(RU, AMBER, 0.07), hl(BY, AMBER, 0.05)
H_NATO = [hl(i, BLUE, 0.09) for i in (PL, LT, LV, EE, DE)]
HL = [H_RU, H_BY] + H_NATO
LEG = [{"text": "RUSSIA", "color": AMBER}, {"text": "NATO", "color": BLUE}]
LEG_ROUTE = LEG + [{"text": "ROUTES APPROXIMATE", "color": "rgba(236,239,242,0.8)"}]

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
    d = dict(id=sid, type="city", start=round(a, 3), end=round(b, 3), tag=tag, city="kaliningrad-east", view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, gz=B, camera=ks, rings=rs, **kw)
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


# ================================================================== Cold open [SIMULATION]
FL = round(W("p01", "Kaliningrad:") + 0.1, 2)     # the flash lands on the spoken place name (about 2 s)
LAUNCH0 = 0.3
a, b = 0.0, FL
R("open-fly", a, b, [("s", [21.35, 54.55], 300), ("e", [21.7, 54.5], 190)], clock="T-03:00", clockLabel="SINCE LAUNCH", clockRate=round(180 / FL, 1),
  highlight=HL, countryLabels=[cl(PL, "POLAND", BLUE), cl(LT, "LITHUANIA", BLUE)], legend=LEG,
  cities=[mk(KAL, "KALININGRAD", 0.05, WHITE, "dot", 6), mk(LA, "LAUNCHER (SIMULATED)", 0.4, AMBER, "base", 6), mk(B, None, 1.2, RED, "ring", 7)],
  ships=[ship([LA, B], LAUNCH0, FL, "pla", RED, "ISKANDER", 26)], lines=[ln(LA, B, 0.6, FL - 0.2, RED, None, True, 2)])
a, b = FL, 8.0
C("open-flash", a, b, [(a, B, 26), (a + 2.0, B, 12), (b, B, 6.5)], rings=[{"km": FX["psi5_km"], "label": "5 PSI", "color": RED, "t": a + 1.6}, {"km": FX["psi1_km"], "label": "1 PSI", "color": TEAL, "t": a + 2.8}],
  flash=a + 0.1, clock="T+03:00", clockLabel="THE BURST", labels=[lb(offp(B, 0, 30), "KALININGRAD: 5 KT AIRBURST (SIMULATED)", a + 1.0, WHITE)])
a, b = 8.0, S("p02")
R("open-after", a, b, [(a, B, 70), (a + 1.6, [21.9, 54.5], 150), (b, [21.2, 54.5], 260)], clock="T+03:30", clockLabel="AFTER THE BURST", highlight=HL, legend=LEG,
  burst={"at": B, "t": a - 3.0, "km": 3, "fade": 9}, countryLabels=[cl(RU, "RUSSIA", AMBER), cl(LT, "LITHUANIA", BLUE)],
  cities=[mk(B, "TARGET", a + 0.1, RED, "ring", 7), mk(KAL, "KALININGRAD", a + 1.8, WHITE, "dot", 6), mk(LA, "LAUNCHER (SIMULATED)", a + 2.4, AMBER, "base", 6)],
  labels=[lb(offp(B, 0, 13), "IT HAS NOT HAPPENED", a + 0.3, YELLOW)])
# run-up: three minutes earlier
a, b = S("p02"), W("p02", "It")
R("open-launch", a, b, [(a, [21.0, 54.5], 250), (b, [21.0, 54.5], 175)], caption="Three minutes earlier.", highlight=HL, legend=LEG,
  **cd(a, b, W("p02", "leaves"), S("p03") - 0.5), cities=[mk(KAL, "KALININGRAD", a + 0.2, WHITE, "dot", 6), mk(LA, "LAUNCHER (SIMULATED)", W("p02", "launcher"), AMBER, "base", 7)],
  ships=[fly(a, b, LA, B, W("p02", "leaves"), S("p03") - 0.5, None, 26)], lines=[ln(LA, B, W("p02", "leaves"), W("p02", "leaves") + 1.2, RED, "98 KM", True, 2)])
a, b = W("p02", "It"), S("p03")
R("open-98", a, b, [(a, [21.3, 54.6], 280), (b, [21.5, 54.55], 190)], highlight=HL, legend=LEG, countryLabels=[cl(PL, "POLAND", BLUE)], **cd(a, b, W("p02", "leaves"), S("p03") - 0.5),
  cities=[mk(LA, "LAUNCHER", a + 0.1, AMBER, "base", 7), mk(B, "TARGET", a + 0.2, RED, "ring", 7), mk(KAL, "KALININGRAD", a + 0.3, WHITE, "dot", 6)],
  ships=[fly(a, b, LA, B, W("p02", "leaves"), S("p03") - 0.5, "ISKANDER", 26)], lines=[ln(LA, B, a + 0.3, a + 1.5, RED, "98 KM", True, 2)])
a, b = S("p03"), S("p04")
R("open-target", a, b, [(a, B, 200), (a + 3.0, B, 150), (b, offp(B, 10, 0), 130)], highlight=HL, legend=LEG, countryLabels=[cl(RU, "RUSSIA", AMBER), cl(LT, "LITHUANIA", BLUE), cl(PL, "POLAND", BLUE)],
  cities=[mk(B, "OPEN GROUND (SIMULATED)", W("p03", "open"), RED, "target", 8)], labels=[lb(offp(B, 0, -34), "INSIDE RUSSIA ITSELF", W("p03", "inside"), AMBER)])
a, b = S("p04"), W("p04", "And")
R("open-why", a, b, [(a, OBLAST, 420), (b, OBLAST, 320)], highlight=HL, legend=LEG, cities=[mk(B, "ITS OWN LAND", W("p04", "own"), RED, "target", 8), mk(KAL, "KALININGRAD", a + 0.3, WHITE, "dot", 6)],
  labels=[lb(offp(KAL, -40, -60), "A NUCLEAR WEAPON?", W("p04", "nuclear"), RED)])
a, b = W("p04", "And"), S("p05")
R("open-nato", a, b, [(a, OBLAST, 500), (W("p04", "Thirteen") + 0.5, [23.0, 54.8], 900), (b, [24.0, 55.0], 1250)], highlight=HL, legend=LEG, countryLabels=[cl(PL, "POLAND", BLUE), cl(LT, "LITHUANIA", BLUE), cl(LV, "LATVIA", BLUE), cl(BY, "BELARUS", AMBER)],
  cities=[mk(WAR, "WARSAW", W("p04", "NATO"), BLUE, "dot", 6), mk(VIL, "VILNIUS", W("p04", "hour"), BLUE, "dot", 6)],
  lines=poly(RAIL_KAL, W("p04", "starts") - 0.4, W("p04", "starts") + 1.6, WHITE, "THE ROAD", False, 3), labels=[lb(offp(KAL, -20, 45), "13 DAYS OF PRESSURE", W("p04", "Thirteen"), YELLOW)])

# ================================================================== Chapter 01 [REAL DATA]
a = S("p05")
a = chapter("c1-card", a, 3.75, "CHAPTER 01", "A place with no road home", "REAL DATA")
SRC_ACA = "Arms Control Association, Arms Control Today, Nov 2026; Reuters"
b = 47.4
stamp("c1-stamp", a, b, "30 SEPTEMBER 2026", "Russia's embassy in Dublin issues a warning", AMBER, source=SRC_ACA)
a, b = b, W("p05", "Reuters") - 0.2
EUR = [8.0, 53.5]
R("c1-dublin", a, b, [(a, EUR, 2300), (b, [8.0, 54.0], 2900)], tag="REAL DATA", highlight=HL, legend=LEG, caption='"All its arsenal, including nuclear weapons"', source=SRC_ACA,
  cities=[mk(DUB, "RUSSIAN EMBASSY, DUBLIN", a + 0.4, AMBER, "dot", 7), mk(KAL, "KALININGRAD", W("p05", "isolate"), WHITE, "target", 7)],
  lines=[ln(DUB, KAL, W("p05", "arsenal"), W("p05", "arsenal") + 1.8, AMBER, None, True, 3)])
a, b = b, S("p06")
R("c1-note", a, b, [(a, [12.0, 53.0], 2800), (b, [12.0, 53.0], 2000)], tag="REAL DATA", highlight=HL, legend=LEG, source=SRC_ACA,
  cities=[mk(KAL, "KALININGRAD", a + 0.1, WHITE, "target", 7), mk(BRU, "BRUSSELS", a + 1.2, BLUE, "dot", 6), mk(WAR, "WARSAW", a + 1.6, BLUE, "dot", 6), mk([13.4, 52.52], "BERLIN", a + 2.0, BLUE, "dot", 6)],
  lines=[ln(KAL, BRU, a + 1.0, a + 2.4, AMBER, None, True, 2), ln(KAL, WAR, a + 1.4, a + 2.6, AMBER, None, True, 2), ln(KAL, [13.4, 52.52], a + 1.8, a + 3.0, AMBER, None, True, 2)],
  labels=[lb([14.0, 56.0], "A FORMAL NOTE TO NATO STATES", W("p05", "formal"), AMBER)])
a, b = S("p06"), W("p06", "NATO's", 2) - 0.2
R("c1-sg", a, b, [(a, [10.0, 52.0], 1800), (b, [10.0, 52.5], 1300)], tag="REAL DATA", highlight=HL, legend=LEG, caption='"Stop the nuclear threats."', source=SRC_ACA,
  cities=[mk(BRU, "NATO HQ, BRUSSELS", a + 0.5, BLUE, "dot", 8)], labels=[lb(offp(BRU, 60, 120), "NATO'S SECRETARY GENERAL", W("p06", "answered"), BLUE)])
a, b = b, S("p07")
R("c1-top", a, b, [(a, [18.0, 54.5], 1000), (a + 3.5, [20.5, 54.7], 600), (b, [20.5, 54.7], 380)], tag="REAL DATA", highlight=HL, legend=LEG, source=SRC_ACA, caption='"No need and incentive to escalate."',
  cities=[mk(KAL, "KALININGRAD", a + 0.3, WHITE, "target", 7)], labels=[lb(offp(KAL, -10, -70), "NATO DENIES ANY PLAN", W("p06", "denies"), BLUE)])
a, b = S("p07"), W("p07", "squeezed") - 0.2
SRC_K = "Wikipedia; Foreign Policy; Kyiv Independent"
R("c1-what", a, b, [(a, [20.5, 54.6], 800), (a + 3.0, [20.5, 54.7], 620), (b, [20.5, 54.7], 500)], tag="REAL DATA", highlight=HL, legend=LEG, source=SRC_K, countryLabels=[cl(PL, "POLAND", BLUE), cl(LT, "LITHUANIA", BLUE)],
  cities=[mk(KAL, "KALININGRAD: ABOUT 1 MILLION", W("p07", "million"), AMBER, "target", 8)], labels=[lb(offp(KAL, 30, -85), "ABOUT THE SIZE OF CONNECTICUT", W("p07", "Connecticut"), WHITE)])
a, b = b, S("p08")
R("c1-nolink", a, b, [(a, [24.0, 54.7], 1100), (b, [26.0, 54.8], 1500)], tag="REAL DATA", highlight=HL, legend=LEG, source=SRC_K, countryLabels=[cl(PL, "POLAND", BLUE), cl(LT, "LITHUANIA", BLUE), cl(BY, "BELARUS", AMBER)],
  cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7), mk(MOS, "RUSSIA, 1,000 KM EAST", a + 2.5, AMBER, "dot", 5)],
  lines=[ln(KAL, [33.0, 55.0], W("p07", "no") , W("p07", "no") + 2.0, AMBER, "NO LAND LINK TO RUSSIA", True, 3)])
a, b = S("p08"), 95.9
R("c1-rail", a, b, [(a, [22.5, 54.8], 700), (b, [23.5, 54.8], 520)], tag="REAL DATA", highlight=HL, legend=LEG_ROUTE, source=SRC_K, countryLabels=[cl(LT, "LITHUANIA", BLUE)],
  lines=poly(RAIL_KAL, W("p08", "trains"), W("p08", "trains") + 3.0, WHITE, "ABOUT 150 MILES OF LITHUANIA", False, 4), cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7)],
  labels=[lb(offp(VIL, 50, 40), "RAIL, BY ONE ACCOUNT", W("p08", "account"), YELLOW)])
a, b = b, 101.2
R("c1-power", a, b, [(a, [22.0, 56.0], 1200), (b, [22.0, 55.6], 900)], tag="REAL DATA", highlight=HL + [hl(LV, BLUE, 0.09)], legend=LEG, source="Al Jazeera, 2025-02-08; Foreign Policy",
  countryLabels=[cl(LT, "LITHUANIA", BLUE), cl(LV, "LATVIA", BLUE)],
  cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7)], labels=[lb(offp(KAL, 150, 40), "NO ELECTRICITY LINK SINCE FEB 2025", W("p08", "February"), YELLOW)],
  lines=[ln(KAL, VIL, W("p08", "electricity"), W("p08", "electricity") + 1.2, RED, None, True, 3)])
a, b = b, S("p09")
R("c1-port", a, b, [(a, BALT, 330), (b, offp(BALT, 40, 20), 230)], tag="REAL DATA", highlight=HL, legend=LEG, source=SRC_K,
  cities=[mk(BALT, "BALTIYSK", a + 0.2, AMBER, "base", 8)], labels=[lb(offp(BALT, -20, -35), "ONLY BALTIC PORT FREE OF ICE IN WINTER", W("p08", "ice-free"), WHITE)],
  ships=[ship([offp(BALT, -60, 30), offp(BALT, -4, 4)], a + 0.5, b - 1.0, "cargo", AMBER, None, 18)])
STAT = "CSIS Missile Threat; Congressional Research Service"
a, b = S("p09"), W("p09", "That")
R("c1-fleet", a, b, [(a, OBLAST, 260), (b, OBLAST, 200)], tag="REAL DATA", highlight=HL, legend=LEG, source=STAT,
  cities=[mk(KAL, "KALININGRAD", a + 0.1, WHITE, "dot", 6), mk(BALT, "BALTIC FLEET HQ", W("p09", "headquarters"), AMBER, "base", 8)], rings=[rg(OBLAST, 70, W("p09", "belt"), AMBER, "AIR DEFENCE AND MISSILE BELT", True)])
a, b = b, S("p10")
R("c1-isk", a, b, [(a, [21.2, 54.45], 220), (a + 4.0, [21.2, 54.45], 150), (b, [21.2, 54.45], 190)], tag="REAL DATA", highlight=HL, legend=LEG, source=STAT,
  cities=[mk([21.45, 54.5], "ISKANDER BRIGADE", a + 0.3, AMBER, "base", 8)], labels=[lb(offp(OBLAST, 5, -40), "THERE PERMANENTLY SINCE 2018", W("p09", "permanently"), WHITE), lb(offp(OBLAST, 5, -55), "CONVENTIONAL OR NUCLEAR WARHEAD", W("p09", "conventional"), RED)])
a, b = S("p10"), W("p10", "It") - 0.2
GAPC = [23.2, 54.2]
R("c1-gap", a, b, [(a, [21.5, 54.5], 700), (a + 3.5, GAPC, 330), (b, GAPC, 260)], tag="REAL DATA", highlight=HL, legend=LEG, source="Wikipedia; RTE", countryLabels=[cl(PL, "POLAND", BLUE), cl(BY, "BELARUS", AMBER), cl(LT, "LITHUANIA", BLUE)],
  cities=[mk(GAP_A, "KALININGRAD BORDER", a + 1.5, AMBER, "dot", 6), mk(GAP_B, "BELARUS BORDER", a + 2.0, AMBER, "dot", 6)],
  lines=[ln(GAP_A, GAP_B, W("p10", "sixty-five"), W("p10", "sixty-five") + 1.2, YELLOW, "ABOUT 65 KM", False, 5)], labels=[lb(offp(GAPC, -45, 25), "THE SUWALKI GAP", W("p10", "Suwalki"), YELLOW)])
a, b = b, S("p11")
R("c1-roads", a, b, [(a, GAPC, 300), (a + 4.0, [23.0, 53.6], 600), (b, [22.5, 54.0], 800)], tag="REAL DATA", highlight=HL, legend=LEG_ROUTE, source="Wikipedia; RTE",
  lines=poly(ROAD1, W("p10", "two") + 0.0, W("p10", "two") + 2.0, WHITE, "TWO MAIN ROADS", False, 4) + poly(ROAD2, W("p10", "two") + 0.5, W("p10", "two") + 2.5, WHITE, None, False, 4) + poly(RAIL1, W("p10", "single-track"), W("p10", "single-track") + 2.0, YELLOW, "ONE SINGLE-TRACK RAIL LINE", True, 4),
  labels=[lb([24.2, 56.2], "THE ONLY LAND ROUTE TO ESTONIA, LATVIA, LITHUANIA", W("p10", "only"), WHITE)])
a, b = S("p11"), S("p12")
R("c1-closed", a, b, [(a, GAPC, 450), (a + 3.5, KAU, 650), (W("p11", "tried"), [15.0, 53.0], 2000), (b, BER, 1600)], tag="REAL DATA", highlight=HL, legend=LEG_ROUTE,
  lines=poly(RAIL_KAL, a + 0.3, a + 2.0, WHITE, None, False, 3) + [ln([22.5, 54.5], [23.5, 54.9], W("p11", "closes"), W("p11", "closes") + 1.0, RED, "A CLOSED ROAD", False, 6)],
  cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7), mk(BER, "BERLIN, 1948", W("p11", "tried"), YELLOW, "ring", 8)])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p12"), 3.75, "CHAPTER 02", "How close it has come", "REAL HISTORY")
b = a + 3.6
SRC_B = "US Department of State, Office of the Historian"
stamp("c2-stamp", a, b, "JUNE 1948", "Soviet forces close West Berlin's road, rail and water routes", RED, "REAL HISTORY", source=SRC_B)
a, b = b, W("p12", "airlift") - 0.2
HAM, HAN = [9.99, 53.55], [9.73, 52.37]
R("c2-berlin", a, b, [(a, [11.5, 52.4], 520), (b, BER, 300)], tag="REAL HISTORY", legend=[{"text": "SOVIET ZONE", "color": AMBER}, {"text": "WEST BERLIN", "color": BLUE}], source=SRC_B, highlight=[hl(DE, BLUE, 0.06)],
  cities=[mk(BER, "WEST BERLIN (ALLIED SECTORS)", a + 0.3, BLUE, "target", 8), mk(HAN, "WEST GERMANY", a + 0.6, BLUE, "dot", 5)],
  lines=[ln(HAN, [12.9, 52.45], W("p12", "closed"), W("p12", "closed") + 1.2, RED, "ROAD, RAIL, WATER CLOSED", True, 5), ln(HAM, [13.0, 52.6], W("p12", "closed") + 0.4, W("p12", "closed") + 1.6, RED, None, True, 5)])
a, b = b, W("p12", "lifted") - 0.2
R("c2-air", a, b, [(a, BER, 300), (a + 3.0, [11.5, 52.4], 520), (b, [11.5, 52.4], 420)], tag="REAL HISTORY", legend=[{"text": "AIRLIFT", "color": BLUE}], source=SRC_B, highlight=[hl(DE, BLUE, 0.06)],
  cities=[mk([13.4, 52.475], "TEMPELHOF AIRFIELD", a + 0.3, BLUE, "base", 7)],
  lines=[ln(HAN, [13.4, 52.475], a + 0.3, a + 1.4, BLUE, None, False, 3), ln(HAM, [13.4, 52.475], a + 0.6, a + 1.7, BLUE, None, False, 3), ln(WIES, [13.4, 52.475], a + 0.9, a + 2.0, BLUE, None, False, 3)],
  ships=[ship([HAN, [13.4, 52.475]], a + 1.0 + 0.5 * i, a + 3.0 + 0.5 * i, "ally", "#CFE3FF", None, 16) for i in range(4)] + [ship([HAM, [13.4, 52.475]], a + 1.4 + 0.5 * i, a + 3.4 + 0.5 * i, "ally", "#CFE3FF", None, 16) for i in range(3)],
  labels=[lb([13.4, 51.9], "A PLANE LANDS EVERY 45 SECONDS", W("p12", "forty-five"), BLUE)])
a, b = b, W("p12", "In", 2) - 0.2
add(id="c2-11m", type="timeline", start=round(a, 3), end=round(b, 3), tag="REAL HISTORY", title="BERLIN BLOCKADE", sub="June 1948 to May 1949", total=11, unit="months",
    segments=[{"from": 0, "to": 11, "label": "ROUTES CLOSED, AIRLIFT FLYING", "color": RED}], cursorTo=11, source=SRC_B)
a, b = b, S("p13")
R("c2-swap", a, b, [(a, KAL, 700), (b, KAL, 330)], tag="SIMULATION", highlight=HL, legend=LEG, countryLabels=[cl(PL, "POLAND", BLUE), cl(LT, "LITHUANIA", BLUE)],
  cities=[mk(KAL, "THE CLOSED ENCLAVE IS RUSSIAN", a + 0.3, AMBER, "target", 9)], caption="In our simulation, the closed enclave is Russian.")
a = S("p13")
b = a + 3.6
SRC_22 = "Al Jazeera, 2022-06-18; Wikipedia"
stamp("c2-s22", a, b, "18 JUNE 2022", "Lithuania stops sanctioned goods moving by rail to Kaliningrad", WHITE, "REAL HISTORY", source=SRC_22)
a, b = b, W("p13", "governor") - 0.2
R("c2-rail22", a, b, [(a, [23.5, 54.8], 800), (b, [23.0, 54.8], 500)], tag="REAL HISTORY", highlight=HL, legend=LEG_ROUTE, source=SRC_22,
  lines=poly(RAIL_KAL, a + 0.3, a + 1.8, WHITE, None, False, 3) + [ln([23.4, 54.95], [23.4, 54.8], a + 2.4, a + 3.0, RED, "SANCTIONED GOODS STOPPED", False, 6)],
  cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7), mk(VIL, "VILNIUS", a + 1.0, BLUE, "dot", 6)])
a, b = b, b + 4.0
add(id="c2-pct", type="number", start=round(a, 3), end=round(b, 3), tag="REAL HISTORY", value="40 TO 50%", label="of the goods the enclave moves through Lithuania", sub="Kaliningrad governor, June 2022", color=AMBER, source=SRC_22)
a, b = b, W("p13", "lifted") - 0.2
R("c2-hostile", a, b, [(a, [28.0, 55.0], 1900), (b, [26.0, 55.0], 1400)], tag="REAL HISTORY", highlight=HL, legend=LEG, source=SRC_22, caption='Moscow: "openly hostile"; a Russian lawmaker suggests force',
  cities=[mk(MOS, "MOSCOW", a + 0.3, AMBER, "dot", 7), mk(VIL, "VILNIUS", a + 0.8, BLUE, "dot", 7)], lines=[ln(MOS, VIL, W("p13", "openly"), W("p13", "openly") + 1.8, AMBER, "OPENLY HOSTILE", True, 3)])
a, b = b, W("p13", "Our") - 0.2
add(id="c2-5w", type="timeline", start=round(a, 3), end=round(b, 3), tag="REAL HISTORY", title="LITHUANIA'S 2022 RAIL BAN", sub="Lifted, no shots fired", total=5, unit="weeks",
    segments=[{"from": 0, "to": 5, "label": "BAN IN FORCE", "color": AMBER}], cursorTo=5, source=SRC_22)
a, b = b, S("p14")
R("c2-total", a, b, [(a, [23.5, 54.8], 800), (b, [23.0, 54.6], 520)], tag="SIMULATION", highlight=HL, legend=LEG_ROUTE,
  lines=poly(RAIL_KAL, a + 0.2, a + 1.2, RED, "OUR SIMULATION: THE BAN IS TOTAL", False, 6) + poly(ROAD1[3:], a + 0.6, a + 1.6, RED, None, False, 6), cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7)])
a = S("p14")
b = a + 3.5
SRC_K2 = "Kyiv Independent, 2025-07-18"
stamp("c2-s25", a, b, "JULY 2025", "US Army Europe and Africa's commander on Kaliningrad", BLUE, "REAL HISTORY", source=SRC_K2)
a, b = b, W("p14", "One") - 0.2
R("c2-gen", a, b, [(a, [14.0, 52.5], 1800), (b, [14.0, 53.0], 1300)], tag="REAL HISTORY", highlight=HL, legend=LEG, source=SRC_K2, caption='"In a timeframe that is unheard of"',
  cities=[mk(WIES, "US ARMY EUROPE AND AFRICA", a + 0.3, BLUE, "base", 8), mk(KAL, "KALININGRAD", a + 2.0, AMBER, "target", 7)], lines=[ln(WIES, KAL, W("p14", "control"), W("p14", "control") + 2.0, BLUE, "NATO COULD TAKE CONTROL", True, 3)])
a, b = b, W("p14", "It") - 0.2
R("c2-law", a, b, [(a, [24.0, 54.5], 1900), (a + 3.5, [21.0, 54.0], 1500), (b, [18.0, 53.5], 1700)], tag="REAL HISTORY", highlight=HL, legend=LEG, source=SRC_K2, caption="One report: a Russian lawmaker answers",
  cities=[mk(MOS, "MOSCOW", a + 0.2, AMBER, "dot", 7), mk(WIES, "WIESBADEN", a + 0.4, BLUE, "dot", 6)], lines=[ln(MOS, WIES, a + 1.0, a + 3.5, AMBER, "RETALIATION, INCLUDING NUCLEAR", True, 3)])
a, b = b, S("p15")
R("c2-remark", a, b, [(a, [22.0, 54.6], 1500), (b, [21.0, 54.6], 700)], tag="REAL HISTORY", highlight=HL, legend=LEG, source=SRC_K2,
  cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 8)], labels=[lb(offp(KAL, -60, 90), "ONE GENERAL'S REMARK, NOT NATO POLICY", W("p14", "general's"), YELLOW), lb(offp(KAL, -60, 60), "BOTH SIDES HAVE SAID IT", W("p14", "Both"), WHITE)])
a, b = S("p15"), W("p15", "The") - 0.2
add(id="c2-13d", type="timeline", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="THE SIMULATED CRISIS", sub="Thirteen days, all assumed", total=13, unit="days",
    segments=[{"from": 0, "to": 1, "label": "RAIL CLOSED", "color": RED}, {"from": 1, "to": 7, "label": "PRESSURE", "color": AMBER}, {"from": 7, "to": 8, "label": "FIRST SHOT", "color": RED}, {"from": 8, "to": 11, "label": "PAUSE", "color": AMBER}, {"from": 11, "to": 12, "label": "REPLY", "color": RED}, {"from": 12, "to": 13, "label": "ONE FLASH", "color": RED}], cursorTo=13)
a, b = b, S("p16")
R("c2-3min", a, b, [(a, [21.3, 54.5], 230), (a + 3.0, [21.5, 54.45], 150), (b, [21.7, 54.45], 220)], highlight=HL, legend=LEG, **cd(a, b, a, b - 1.0, label="THE LAST FLIGHT", up=True),
  ships=[ship([LA, B], a + 0.2, b - 1.0, "pla", RED, "ISKANDER", 26)], cities=[mk(LA, "LAUNCHER", a + 0.1, AMBER, "base", 7), mk(B, "WARNING SHOT", a + 0.3, RED, "ring", 7)],
  labels=[lb(offp(B, 0, 30), "3 MINUTES OF FLIGHT", W("p15", "three"), RED)])

# ================================================================== Chapter 03 [SIMULATION]
a = chapter("c3-card", S("p16"), 3.75, "CHAPTER 03", "The trigger", "SIMULATION")
b = W("p16", "It") - 0.2
R("c3-halt", a, b, [(a, [23.0, 54.6], 560), (b, [23.0, 54.6], 420)], highlight=HL, legend=LEG_ROUTE, **DAY(1),
  lines=poly(RAIL_KAL, a + 0.3, a + 1.5, WHITE, None, False, 3) + poly(ROAD1[3:], a + 0.3, a + 1.5, WHITE, None, False, 3) + [ln([22.4, 54.7], [24.4, 54.7], W("p16", "halt"), W("p16", "halt") + 1.0, RED, "HALT", False, 8)],
  cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7), mk(KAU, "LITHUANIA", a + 0.4, BLUE, "dot", 5)], labels=[lb(offp(GAPC, 0, -60), "NATO STATES HALT ALL TRANSIT", W("p16", "halt"), RED)])
a, b = b, S("p17")
R("c3-2022", a, b, [(a, [23.5, 54.8], 700), (b, [22.5, 54.8], 1100)], highlight=HL, legend=LEG, **DAY(1), caption="The simulation assumes it. NATO has not planned it.",
  labels=[lb(offp(KAU, 60, 70), "MODELLED ON THE 2022 BAN", W("p16", "modelled"), WHITE), lb(offp(KAU, 60, 40), "BUT TOTAL THIS TIME", W("p16", "total"), RED)], cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7)])
a, b = S("p17"), W("p17", "Its") - 0.2
R("c3-grid", a, b, [(a, [22.0, 56.0], 1100), (b, [21.0, 55.0], 700)], highlight=HL + [hl(LV, BLUE, 0.09), hl(EE, BLUE, 0.09)], legend=LEG, **DAY(2), countryLabels=[cl(LT, "LITHUANIA", BLUE), cl(LV, "LATVIA", BLUE)],
  cities=[mk(KAL, "KALININGRAD: OWN POWER GRID", W("p17", "own"), AMBER, "target", 8)], labels=[lb([24.0, 57.7], "BALTIC STATES LEFT THE RUSSIAN GRID, 2025", W("p17", "left"), BLUE)])
a, b = b, 287.0
R("c3-sea", a, b, [(a, [24.0, 56.5], 1300), (a + 4.0, [22.0, 55.8], 1000), (b, [20.5, 54.9], 600)], highlight=HL, legend=LEG, **DAY(2),
  ships=[ship([SPB, [22.0, 58.0], [19.5, 55.0], [19.95, 54.66]], a + 0.5 + 0.8 * i, b - 0.5, "cargo", AMBER, "GAS, GOODS, SUPPLIES" if i == 0 else None, 20) for i in range(3)],
  cities=[mk(SPB, "SAINT PETERSBURG", a + 0.1, AMBER, "dot", 6), mk(BALT, "BALTIYSK", a + 1.0, AMBER, "base", 7)], labels=[lb([22.5, 56.8], "ALL NOW NEED THE SEA", W("p17", "sea"), YELLOW)])
a, b = b, S("p18")
add(id="c3-cost", type="number", start=round(a, 3), end=round(b, 3), tag="SIMULATION", value="$647 MILLION", label="a year: Russia's own cost of supplying the enclave", sub="one estimate", color=AMBER, source="Foreign Policy (one estimate)")
a, b = S("p18"), W("p18", "The") - 0.2
R("c3-press", a, b, [(a, [20.0, 55.2], 900), (b, [20.0, 55.0], 650)], highlight=HL, legend=LEG, **DAY(4, "DAYS 02 TO 07"),
  labels=[lb(offp(BALT, 80, 90), "PRESSURE, NOT YET WAR", W("p18", "pressure"), YELLOW), lb(offp(BALT, 80, 60), "NEITHER SIDE FIRES", W("p18", "fires"), WHITE)], cities=[mk(BALT, "BALTIYSK", a + 0.2, AMBER, "base", 7), mk(KAL, "KALININGRAD", a + 0.3, AMBER, "dot", 6)])
a, b = b, W("p18", "Russia") - 0.2
INSP = [[18.3, 54.95], [18.9, 55.2], [19.6, 55.35]]
R("c3-line", a, b, [(a, [19.6, 54.8], 300), (b, [19.3, 54.95], 220)], highlight=HL, legend=LEG, **DAY(5, "DAYS 02 TO 07"),
  lines=poly(INSP, W("p18", "inspection"), W("p18", "inspection") + 2.0, BLUE, "SIMULATED INSPECTION LINE", True, 4),
  ships=[ship([[18.1, 54.9], [18.4, 55.0]], a + 0.5, b, "us", BLUE, None, 20), ship([[18.9, 55.15], [19.1, 55.25]], a + 1.0, b, "us", BLUE, None, 20)], cities=[mk(BALT, "BALTIYSK", a + 0.2, AMBER, "base", 8)])
a, b = b, S("p19")
R("c3-ans", a, b, [(a, [22.0, 57.0], 1000), (a + 4.0, [21.0, 55.6], 700), (b, [20.0, 55.0], 900)], highlight=HL, legend=LEG, **DAY(7, "DAYS 02 TO 07"),
  ships=[ship([SPB, [22.0, 58.0], [19.5, 55.0], [19.95, 54.66]], W("p18", "ferries"), b - 0.5, "cargo", AMBER, "FERRIES", 20)],
  zones=[zn(circle([21.0, 55.0], 90), W("p18", "jamming"), AMBER, "JAMMING", 0.10, True)], cities=[mk(SPB, "SAINT PETERSBURG", a + 0.2, AMBER, "dot", 6)],
  lines=[ln([17.0, 56.2], [21.0, 55.7], W("p18", "cables"), W("p18", "cables") + 1.5, YELLOW, "UNDERSEA CABLES", True, 3), ln(KAL, BRU, W("p18", "note"), W("p18", "note") + 2.0, AMBER, "THE NOTE", True, 2)])
a, b = S("p19"), W("p19", "Planners") - 0.2
R("c3-watch", a, b, [(a, BALT, 280), (b, offp(BALT, -20, 15), 200)], highlight=HL, legend=LEG, **DAY(7, "DAYS 02 TO 07"),
  ships=[ship([[18.2, 54.95], [18.8, 54.9]], a + 0.3, b, "us", BLUE, "NATO SHIPS", 22), ship([[18.0, 55.2], [18.6, 55.1]], a + 0.7, b, "us", BLUE, None, 22), ship([[19.7, 54.7], [19.5, 54.95]], a + 0.5, b, "pla", AMBER, "RUSSIAN SHIPS", 22), ship([[20.1, 54.7], [19.8, 55.0]], a + 0.9, b, "pla", AMBER, None, 22)],
  labels=[lb(offp(BALT, 50, 60), "EACH SIDE WATCHES THE OTHER", W("p19", "watches"), WHITE), lb(offp(BALT, 50, 40), "EACH READS THE OTHER'S SILENCE", W("p19", "reads"), YELLOW)])
a, b = b, W("p19", "Every") - 0.2
R("c3-prec", a, b, [(a, [14.0, 53.0], 1800), (a + 4.0, [16.0, 53.5], 1500), (b, BER, 900)], highlight=HL, legend=LEG, **DAY(7, "DAYS 02 TO 07"),
  cities=[mk(BER, "THE OLD PRECEDENT: BERLIN", W("p19", "precedent"), YELLOW, "ring", 9), mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7)], labels=[lb([18.0, 55.5], "A BLOCKADE CAN END WITHOUT A SHOT", W("p19", "blockade"), WHITE), lb([20.0, 52.0], "NOBODY WANTS THE NEXT STEP", W("p19", "Nobody"), RED)])
a, b = b, S("p20")
R("c3-day8", a, b, [(a, BALT, 240), (a + 4.0, offp(BALT, -10, 5), 170), (b, offp(BALT, -10, 5), 230)], highlight=HL, legend=LEG, **DAY(8, "THE LINE IS NO LONGER ON PAPER"),
  lines=poly(INSP, a + 0.3, a + 1.3, BLUE, "INSPECTION LINE", True, 4),
  ships=[ship([[18.2, 54.95], [18.8, 55.1]], a, b, "us", BLUE, None, 22), ship([[19.7, 54.75], [19.3, 55.0]], a, b, "pla", AMBER, None, 22)], cities=[mk(BALT, "BALTIYSK", a + 0.1, AMBER, "base", 8)],
  labels=[lb(offp(BALT, 40, 50), "BY DAY EIGHT, MORE THAN A LINE", W("p19", "By"), RED), lb(offp(BALT, 40, 30), "WHAT DOES THE FIRST SHOT LOOK LIKE?", W("p19", "What"), YELLOW)])

# ================================================================== Chapter 04 [SIMULATION]
a = chapter("c4-card", S("p20"), 3.75, "CHAPTER 04", "Day by day", "SIMULATION")
b = W("p20", "It") - 0.2
TJ0, TJ1 = W("p20", "launches"), W("p20", "flies") + 5.0           # JASSM: 122 km in about 9 minutes (compressed)
R("c4-d8", a, b, [(a, [20.2, 54.2], 330), (b, [20.2, 54.2], 230)], highlight=HL, legend=LEG, **cd(a, b, TJ0, TJ1, 540, "DAY 08 · SINCE LAUNCH", True),
  cities=[mk(PLS, "POLISH STRIKE PACKAGE (SIMULATED)", a + 0.4, BLUE, "base", 7), mk(BALT, "BALTIYSK", W("p20", "Baltiysk"), AMBER, "base", 8)],
  ships=[fly(a, b, PLS, BALT, TJ0, TJ1, "CRUISE MISSILE", 24)], lines=[ln(PLS, BALT, TJ0, TJ0 + 1.5, RED, None, True, 2)], labels=[lb(offp(PLS, -80, 30), "ONE CONVENTIONAL MISSILE", W("p20", "one"), RED)])
a, b = b, S("p21")
R("c4-flies", a, b, [(a, [20.2, 54.2], 230), (a + 4.0, [20.0, 54.4], 150), (b, [20.0, 54.5], 190)], highlight=HL, legend=LEG, **cd(a, b, TJ0, TJ1, 540, "DAY 08 · SINCE LAUNCH", True),
  cities=[mk(PLS, "POLAND", a + 0.1, BLUE, "dot", 5), mk(BALT, "BALTIYSK: THE BASE THAT GUARDS THE LINE", a + 0.2, AMBER, "base", 8)], ships=[fly(a, b, PLS, BALT, TJ0, TJ1, None, 24)],
  rings=[rg(BALT, 12, W("p20", "crossed"), RED, None, False)], labels=[lb(offp(PLS, 25, 40), "122 KM, ABOUT 9 MINUTES", a + 0.8, RED), lb(offp(BALT, 40, -35), "THE SHOOTING LINE IS CROSSED", W("p20", "shooting"), YELLOW)])
a, b = S("p21"), W("p21", "In") - 0.2
R("c4-wait", a, b, [(a, [20.5, 55.0], 700), (b, [22.0, 55.0], 1100)], highlight=HL, legend=LEG, **DAY(9, "DAYS 08 TO 11"),
  labels=[lb(offp(KAL, 60, 80), "THREE DAYS, NO ANSWER BY FIRE", W("p21", "three"), YELLOW), lb(offp(KAL, 60, 55), "THE NOTE", W("p21", "note"), AMBER)],
  ships=[ship([SPB, [22.0, 58.0], [19.5, 55.0], [19.95, 54.66]], a + 0.5, b, "cargo", AMBER, "FERRIES", 20)], zones=[zn(circle([21.0, 55.0], 90), W("p21", "jammers"), AMBER, "JAMMERS", 0.10, True)], cities=[mk(KAL, "KALININGRAD", a + 0.2, AMBER, "target", 7)])
a, b = b, S("p22")
R("c4-ask", a, b, [(a, [20.0, 54.0], 1300), (b, [20.0, 54.0], 1900)], highlight=HL, legend=LEG, **DAY(10, "DAYS 08 TO 11"),
  cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7), mk(BRU, "BRUSSELS", a + 1.0, BLUE, "dot", 6), mk(WAR, "WARSAW", a + 1.4, BLUE, "dot", 6), mk(MOS, "MOSCOW", a + 1.8, AMBER, "dot", 6)],
  labels=[lb([15.0, 57.0], "THE ALLIANCE WONDERS WHAT COMES NEXT", W("p21", "wonder"), BLUE), lb([17.0, 51.0], "THE NEXT ANSWER WILL COME", W("p21", "believe"), AMBER)])
a, b = S("p22"), W("p22", "to") - 0.2
M0, M1 = W("p22", "flies"), W("p22", "Marijampole")
R("c4-d11", a, b, [(a, [22.3, 54.6], 220), (b, [22.5, 54.6], 150)], highlight=HL, legend=LEG, **cd(a, b, M0, M1, 180, "DAY 11 · SINCE LAUNCH", True),
  ships=[fly(a, b, LA2, MAR, M0, M1, "CONVENTIONAL ISKANDER", 24)], cities=[mk(LA2, "LAUNCHER (SIMULATED)", a + 0.3, AMBER, "base", 7)], lines=[ln(LA2, MAR, M0, M0 + 1.5, RED, None, True, 2)],
  labels=[lb(offp(MAR, -50, -22), "100 KM IN 3 MINUTES", W("p22", "hundred"), RED)])
a, b = b, W("p22", "The") - 0.2
R("c4-mar", a, b, [(a, [22.8, 54.6], 150), (b, MAR, 260)], highlight=HL, legend=LEG_ROUTE, **cd(a, b, M0, M1, 180, "DAY 11 · SINCE LAUNCH", True),
  ships=[fly(a, b, LA2, MAR, M0, M1, None, 24)], cities=[mk(MAR, "MARIJAMPOLE", a + 0.2, RED, "target", 8)], rings=[rg(MAR, 6, M1, RED, None, False)],
  lines=poly(ROAD1[3:], a + 0.5, a + 2.0, WHITE, "VIA BALTICA", False, 3), labels=[lb(offp(MAR, 15, 40), "RAIL AND ROAD JUNCTION, LITHUANIA", W("p22", "junction"), WHITE)])
a, b = b, W("p22", "Russian") - 0.2
R("c4-range", a, b, [(a, [21.5, 54.3], 600), (a + 3.0, [22.0, 54.5], 1500), (b, [22.0, 54.5], 1300)], highlight=HL, legend=LEG, countryLabels=[cl(PL, "POLAND", BLUE)],
  rings=[rg(LA2, 500, W("p22", "reaches"), AMBER, "ABOUT 500 KM, ONE ESTIMATE", True)], cities=[mk(WAR, "WARSAW", W("p22", "Warsaw"), BLUE, "dot", 7), mk(VIL, "VILNIUS", W("p22", "Vilnius"), BLUE, "dot", 7), mk(RIGA, "RIGA", W("p22", "Riga"), BLUE, "dot", 7), mk(LA2, "ISKANDER", a + 0.2, AMBER, "base", 7)])
a, b = b, S("p23")
R("c4-art5", a, b, [(a, MAR, 400), (a + 4.0, offp(MAR, 20, 10), 220), (b, [23.0, 54.6], 500)], highlight=HL, legend=LEG, **DAY(11),
  cities=[mk(MAR, "A LITHUANIAN TOWN (ASSUMED)", a + 0.2, RED, "target", 8)], caption="No death toll is computed for this strike.",
  labels=[lb(offp(MAR, -20, 55), "ARTICLE FIVE IN QUESTION AT ONCE", W("p22", "Article"), BLUE)])
a, b = S("p23"), W("p23", "In", 2) - 0.2
R("c4-d12", a, b, [(a, [24.2, 54.8], 400), (b, [23.6, 54.5], 300)], highlight=HL, legend=LEG, **DAY(12),
  ships=[ship([[24.3, 55.0], [23.3, 54.45]], a + 0.5 + 0.4 * i, b, "us", BLUE, "GERMAN BRIGADE, ALLIED BATTLEGROUP" if i == 0 else None, 20) for i in range(3)],
  cities=[mk([24.3, 55.0], "LITHUANIA", a + 0.2, BLUE, "dot", 5)], labels=[lb([24.6, 54.2], "MOVE TOWARD THE CORRIDOR", W("p23", "move"), BLUE)])
a, b = b, W("p23", "sixty-five") - 0.2
R("c4-grodno", a, b, [(a, [23.7, 54.0], 260), (b, [23.5, 54.0], 200)], highlight=HL, legend=LEG, **DAY(12),
  ships=[ship([GRO, offp(GRO, 0, 38)], a + 0.8 + 0.4 * i, b, "pla", AMBER, "FORCES MOBILISE" if i == 0 else None, 20) for i in range(3)],
  cities=[mk(GRO, "GRODNO", a + 0.3, AMBER, "base", 8), mk(SUW, "SUWALKI", a + 0.6, BLUE, "dot", 7)], lines=[ln(GRO, SUW, W("p23", "seventy-five"), W("p23", "seventy-five") + 1.0, WHITE, "ABOUT 75 KM", False, 3)])
a, b = b, S("p24")
R("c4-edges", a, b, [(a, GAPC, 300), (a + 4.0, GAPC, 220), (b, [23.2, 54.2], 280)], highlight=HL, legend=LEG_ROUTE, **DAY(12), caption="This is assumed.",
  lines=[ln(GAP_A, GAP_B, a + 0.3, a + 1.2, YELLOW, "65 KM", False, 5)] + poly(ROAD1[2:], a + 1.0, a + 2.0, WHITE, None, False, 3) + poly(RAIL1[2:], a + 1.2, a + 2.2, YELLOW, None, True, 3),
  ships=[ship([[23.3, 54.75], [23.1, 54.4]], a + 0.3, b, "us", BLUE, "ONE ARMY", 22), ship([[23.7, 53.8], [23.5, 54.0]], a + 0.3, b, "pla", AMBER, "THE OTHER", 22)],
  labels=[lb(offp(GAPC, 0, 40), "TWO ARMIES ON THE EDGES", W("p23", "armies"), WHITE), lb(offp(GAPC, 0, -45), "TWO ROADS AND ONE RAIL LINE BETWEEN", W("p23", "roads"), YELLOW)])
a, b = S("p24"), W("p24", "Analysts") - 0.2
R("c4-doct", a, b, [(a, [28.0, 56.0], 2000), (b, [26.0, 55.5], 1500)], highlight=HL, legend=LEG, **DAY(13),
  cities=[mk(MOS, "MOSCOW", a + 0.3, AMBER, "dot", 7), mk(KAL, "KALININGRAD", a + 0.6, AMBER, "target", 8)], lines=[ln(MOS, KAL, W("p24", "argues"), W("p24", "argues") + 2.0, AMBER, "A THREAT TO KALININGRAD", True, 3)],
  labels=[lb([30.0, 52.5], "FOURTH CONDITION IN ITS OWN DOCTRINE", W("p24", "fourth"), YELLOW)])
a, b = b, W("p24", "The", 2) - 0.2
R("c4-differ", a, b, [(a, [21.5, 54.6], 900), (b, [21.5, 54.6], 600)], highlight=HL, legend=LEG, **DAY(13),
  cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 8)], labels=[lb(offp(KAL, 40, 70), "DOES ISOLATION MEET IT?", W("p24", "differ"), YELLOW), lb(offp(KAL, 40, 45), "ANALYSTS DIFFER", a + 0.3, WHITE)])
a, b = b, S("p25")
R("c4-warn", a, b, [(a, OBLAST, 400), (a + 3.0, B, 200), (b, B, 150)], highlight=HL, legend=LEG, **DAY(13), countryLabels=[cl(LT, "LITHUANIA", BLUE), cl(PL, "POLAND", BLUE)],
  cities=[mk(B, "WARNING SHOT: RUSSIAN SOIL", W("p24", "warning"), RED, "target", 9), mk(MAR, "MARIJAMPOLE", a + 0.4, BLUE, "dot", 5)], labels=[lb(offp(B, -45, -28), "HARMS NO ALLY", W("p24", "ally"), YELLOW)])
a, b = S("p25"), W("p25", "flash") - 0.1
L0 = W("p25", "raises")
R("c4-ready", a, b, [(a, [21.2, 54.45], 260), (a + 3.0, [21.4, 54.45], 190), (b, [21.7, 54.45], 150)], highlight=HL, legend=LEG, **cd(a, b, L0, b, 180, "UNTIL THE BURST"),
  cities=[mk(LA, "LAUNCHER, 18:10 LOCAL", W("p25", "launcher"), AMBER, "base", 8), mk(B, None, a + 0.5, RED, "ring", 7)], ships=[fly(a, b, LA, B, L0, b, "ISKANDER", 26)],
  labels=[lb(offp(LA, 0, 30), "AT TEN PAST SIX", W("p25", "ten"), WHITE)], lines=[ln(LA, B, L0, L0 + 1.0, RED, None, True, 2)])
a, b = b, S("p26")
R("c4-flash", a, b, [(a, B, 120), (a + 3.0, B, 200), (b, [21.4, 54.5], 280)], highlight=HL, legend=LEG, clock="T+03:00", clockLabel="THE FLASH", clockRate=1, burst={"at": B, "t": a + 0.1, "km": 3, "fade": 7},
  cities=[mk(B, "KALININGRAD: TARGET", a + 0.2, RED, "ring", 7)],
  labels=[lb(offp(B, 0, 28), "ONE MISSILE", a + 1.2, YELLOW), lb(offp(B, 0, -28), "WHAT DOES ONE WARHEAD DO?", W("p25", "What"), WHITE)])

# ================================================================== Chapter 05 [SIMULATION]
a = chapter("c5-card", S("p26"), 3.75, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
b = W("p26", "quarter")
add(id="c5-yield", type="bars", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="YIELD: OUR ASSUMPTION", sub="The Iskander-M's nuclear yield is not published",
    bars=[{"label": "NAGASAKI, 1945", "value": 21, "display": "21 KT", "color": ORANGE}, {"label": "THIS SIMULATION", "value": 5, "display": "5 KT, ASSUMED", "color": RED}])
a, b = b, S("p27")
R("c5-where", a, b, [(a, [21.4, 54.45], 160), (a + 3.5, [21.4, 54.45], 120), (a + 7.0, B, 150), (b, B, 190)], highlight=HL, legend=LEG, clock="T+03:00", clockLabel="THE BURST", clockRate=1,
  cities=[mk(B, "AIRBURST OVER OPEN FOREST AND FARMLAND", W("p26", "forest"), RED, "target", 9)], lines=[ln(LA, B, a + 0.3, a + 1.6, RED, "98 KM", True, 3)], labels=[lb(offp(B, 0, -25), "5 KT: ABOUT A QUARTER OF NAGASAKI", a + 5.0, YELLOW)])
a, b = S("p27"), W("p27", "Inside") - 0.2
RK = {"fire": {"km": FX["fireball_km"], "label": "FIREBALL", "color": WHITE}, "p20": {"km": FX["psi20_km"], "label": "20 PSI", "color": ORANGE},
      "p5": {"km": FX["psi5_km"], "label": "5 PSI", "color": RED}, "b": {"km": FX["thermal3_km"], "label": "BURNS", "color": AMBER}, "p1": {"km": FX["psi1_km"], "label": "WINDOWS", "color": TEAL}}


def rr(k, t, label=True):
    d = dict(RK[k])
    d["t"] = t
    return d


C("c5-fire", a, b, [(a, B, 1.4), (b, B, 0.7)], rings=[rr("fire", W("p27", "fireball") + 0.2)], flash=a + 0.1, clock="T+03:00", clockLabel="THE BURST")
a, b = b, S("p28")
C("c5-20", a, b, [(a, B, 1.1), (b, B, 0.9)], rings=[rr("fire", a - 3.0, False), rr("p20", W("p27", "twenty"))], clock="T+03:05", clockLabel="THE BURST")
a, b = S("p28"), S("p29")
C("c5-5", a, b, [(a, B, 1.8), (a + 4.0, B, 3.2), (b, B, 4.6)], rings=[rr("fire", a - 3.0, False), rr("p20", a - 3.0, False), rr("p5", W("p28", "five"))], clock="T+03:10", clockLabel="THE BURST",
  zones=[], labels=[lb(offp(B, 0, 1.4 * 0.0 + 0.0), "AREA 4.2 KM2", W("p28", "square", 2), RED)])
a, b = S("p29"), S("p30")
C("c5-burn", a, b, [(a, B, 3.0), (a + 4.0, B, 6.5), (b, B, 8.0)], rings=[rr("fire", a - 3.0, False), rr("p20", a - 3.0, False), rr("p5", a - 3.0, False), rr("b", W("p29", "burns")), rr("p1", W("p29", "Windows"))], clock="T+03:20", clockLabel="THE BURST")
a, b = S("p30"), 534.0
R("c5-fall", a, b, [(a, B, 150), (a + 4.0, B, 200), (b, B, 260)], highlight=HL, legend=LEG, clock="T+03:30", clockLabel="THE BURST", burst={"at": B, "t": a - 5.0, "km": 2, "fade": 9},
  plume={"at": B, "bearing": 90, "lengthKm": 70, "widthKm": 10, "t0": a + 0.4, "t1": a + 3.5, "color": AMBER, "label": "WIND, ABOUT 5 M/S (ASSUMED)"},
  cities=[mk(B, "BURST", a + 0.2, RED, "target", 7)],
  labels=[lb(offp(B, 20, 18), "LITTLE LOCAL FALLOUT", W("p30", "fallout"), AMBER), lb(offp(B, -10, -22), "OPEN FOREST AND FARMLAND", W("p30", "forest"), WHITE)])
a, b = b, S("p31")
R("c5-msg", a, b, [(a, [21.5, 54.5], 400), (a + 3.0, [22.5, 54.6], 900), (b, [22.5, 54.6], 1200)], highlight=HL, legend=LEG, clock="T+03:30", clockLabel="A MESSAGE",
  cities=[mk(B, "THE POINT IS THE MESSAGE", W("p30", "message"), RED, "target", 9), mk(VIL, "VILNIUS", a + 1.5, BLUE, "dot", 6), mk(WAR, "WARSAW", a + 1.8, BLUE, "dot", 6)],
  lines=[ln(B, VIL, W("p30", "message"), W("p30", "message") + 1.5, AMBER, None, True, 3), ln(B, WAR, W("p30", "message") + 0.3, W("p30", "message") + 1.8, AMBER, None, True, 3)],
  labels=[lb(offp(B, -60, -80), "FLIGHT TIME: 3 MINUTES", W("p30", "three"), WHITE)])
a, b = S("p31"), S("p32")
C("c5-small", a, b, [(a, B, 5.0), (a + 3.0, B, 14.0), (b, B, 40.0)], rings=[rr("fire", a - 3.0, False), rr("p20", a - 3.0, False), rr("p5", a - 3.0), rr("b", a - 3.0, False), rr("p1", a - 3.0, False)], clock="T+04:00", clockLabel="AFTER THE FLASH",
  labels=[lb(offp(B, 0, 6), "THE RINGS ARE SMALL", W("p31", "small"), WHITE)])

# ================================================================== Chapter 06 [SIMULATION]
a = chapter("c6-card", S("p32"), 3.75, "CHAPTER 06", "The day after", "SIMULATION")
b = W("p32", "Start") + 0.0
b = 561.0
R("c6-wind", a, b, [(a, B, 320), (a + 3.0, offp(B, 20, 0), 220), (b, offp(B, 30, 0), 300)], highlight=HL, legend=LEG, clock="T+01:00:00", clockLabel="THE FIRST HOUR", clockRate=0, caption="Back to the question: what does NATO do in the hour after?",
  burst={"at": B, "t": a - 2.0, "km": 2, "fade": 12}, cities=[mk(B, "BURST", a + 0.2, RED, "target", 7), mk(KAL, "KALININGRAD", a + 0.5, WHITE, "dot", 6)],
  lines=[ln(offp(B, -60, 12 - 10 * i), offp(B, 10, 12 - 10 * i), W("p32", "wind") + 0.2 * i, W("p32", "wind") + 1.6 + 0.2 * i, WHITE, "WEST WIND, ABOUT 5 M/S (OUR ASSUMPTION)" if i == 1 else None, False, 2) for i in range(3)])
a, b = b, S("p33")
R("c6-plume", a, b, [(a, B, 160), (a + 4.0, offp(B, 40, 0), 220), (b, offp(B, 40, 0), 300)], highlight=HL, legend=LEG, countryLabels=[cl(LT, "LITHUANIA", BLUE)], clock="THE FIRST HOUR", clockLabel="", clockRate=0,
  plume={"at": B, "bearing": 90, "lengthKm": 90, "widthKm": 14, "t0": W("p32", "thin"), "t1": W("p32", "thin") + 3.0, "color": AMBER, "label": "THIN CLOUD, NOT A FORECAST"},
  labels=[lb(offp(B, 40, -40), "LITTLE LOCAL FALLOUT, NO DOSE MAP", W("p32", "Little"), WHITE), lb(offp(B, 85, 18), "TOWARD THE LITHUANIAN BORDER", W("p32", "toward"), YELLOW)], cities=[mk(B, "BURST", a + 0.1, RED, "target", 7)])
a, b = S("p33"), W("p33", "Warsaw") - 0.2
R("c6-jam", a, b, [(a, KAL, 700), (a + 3.0, KAL, 1000), (b, KAL, 1250)], highlight=HL, legend=LEG, clock="THE FIRST HOUR", clockLabel="", clockRate=0, source="Kyiv Independent (jammer reach)",
  zones=[zn(circle(KAL, 350), W("p33", "circle"), AMBER, "350 KM: THE JAMMER'S REACH", 0.08, True)], cities=[mk(KAL, "KALININGRAD", a + 0.1, AMBER, "target", 7)], labels=[lb(offp(KAL, 30, -60), "PER THE KYIV INDEPENDENT", a + 3.8, WHITE)])
a, b = b, 581.0
R("c6-in", a, b, [(a, KAL, 1250), (b, KAL, 1000)], highlight=HL, legend=LEG, clock="THE FIRST HOUR", clockLabel="", clockRate=0,
  zones=[zn(circle(KAL, 350), a + 0.05, AMBER, "350 KM: THE JAMMER'S REACH", 0.08, False)], cities=[mk(WAR, "WARSAW", W("p33", "Warsaw"), BLUE, "dot", 7), mk(GDA, "GDANSK", W("p33", "Gdansk"), BLUE, "dot", 7), mk(VIL, "VILNIUS", W("p33", "Vilnius"), BLUE, "dot", 7), mk(KAL, "KALININGRAD", a, AMBER, "target", 7)])
a, b = b, S("p34")
AIR = [[[14.0, 57.0], [17.5, 57.0], [24.0, 57.6], [28.0, 57.0]], [[28.0, 52.0], [24.0, 51.2], [18.0, 51.0], [14.0, 52.0]], [[12.0, 55.0], [15.5, 56.5], [22.0, 57.5], [30.0, 56.5]]]
R("c6-air", a, b, [(a, KAL, 1000), (a + 5.0, [21.0, 55.0], 1500), (b, [21.0, 55.0], 1200)], highlight=HL, legend=LEG, clock="THE FIRST HOUR", clockLabel="", clockRate=0,
  zones=[zn(circle(KAL, 350), a + 0.05, AMBER, None, 0.08, False)],
  ships=[ship(AIR[i], a + 0.5 + 0.4 * i, b - 0.5, "ally", "#CFE3FF", "AIRLINES REROUTE" if i == 0 else None, 16) for i in range(3)], labels=[lb(KAL, "NEARLY EMPTY OF FLIGHT TRACKS", W("p33", "empty"), WHITE)])
a, b = S("p34"), W("p34", "In") - 0.2
R("c6-three", a, b, [(a, GAPC, 450), (b, GAPC, 300)], highlight=HL, legend=LEG_ROUTE, **DAY(14, "THE DAY AFTER"),
  lines=poly(ROAD1[2:], W("p34", "Two"), W("p34", "Two") + 1.6, WHITE, "MAIN ROAD", False, 4) + poly(ROAD2[1:], W("p34", "Two") + 0.4, W("p34", "Two") + 2.0, WHITE, "SECOND ROAD", False, 4) + poly(RAIL1[2:], W("p34", "single-track"), W("p34", "single-track") + 1.5, YELLOW, "RAIL LINE", True, 4),
  cities=[mk(MAR, None, W("p34", "targets"), RED, "target", 8), mk(SUW, None, W("p34", "targets") + 0.3, RED, "target", 8)], labels=[lb(offp(GAPC, 0, -60), "ALL THREE: POSSIBLE TARGETS", W("p34", "possible"), RED)])
a, b = b, S("p35")
R("c6-convoy", a, b, [(a, GAPC, 300), (a + 4.0, [23.3, 54.1], 380), (b, [23.0, 54.0], 480)], highlight=HL, legend=LEG_ROUTE, **DAY(14, "THE DAY AFTER"),
  ships=[ship([[21.01, 52.23], [23.16, 53.13], [22.96, 53.95], SUW], a + 0.3 + 0.6 * i, b - 0.3, "cargo", BLUE, "NATO CONVOY" if i == 0 else None, 18) for i in range(3)],
  lines=poly(ROAD1[2:], a, a + 0.5, WHITE, None, False, 3) + poly(RAIL1[2:], a, a + 0.5, YELLOW, None, True, 3) + poly(ROAD2[1:], a, a + 0.5, WHITE, None, False, 3), labels=[lb(offp(GAPC, 0, -55), "EVERY CONVOY MUST CHOOSE", W("p34", "convoy"), WHITE)])
a, b = S("p35"), W("p35", "Its") - 0.2
R("c6-alone", a, b, [(a, [20.0, 55.0], 700), (b, [20.0, 55.0], 500)], highlight=HL, legend=LEG, **DAY(14, "THE DAY AFTER"),
  cities=[mk(KAL, "QUIETER AND MORE ALONE", W("p35", "alone"), AMBER, "target", 9)])
a, b = b, S("p36")
R("c6-watch", a, b, [(a, [21.0, 56.0], 900), (a + 3.0, [20.0, 55.2], 600), (b, [19.5, 55.0], 700)], highlight=HL, legend=LEG, **DAY(14, "THE DAY AFTER"),
  ships=[ship([SPB, [22.0, 58.0], [19.5, 55.0], [19.95, 54.66]], a + 0.2, b - 0.5, "cargo", AMBER, "FERRIES", 20)], cities=[mk(KAL, "OWN POWER GRID, NO LINK TO RUSSIA", W("p35", "power", 2), YELLOW, "target", 8)],
  labels=[lb([17.0, 56.2], "THE WORLD WATCHES EVERY ONE", W("p35", "world"), WHITE)])
a, b = S("p36"), W("p36", "After") - 0.2
SRC_V = "Arms Control Association, Arms Control Today, Nov 2026"
R("c6-lt", a, b, [(a, VIL, 600), (b, VIL, 350)], highlight=HL, legend=LEG, **DAY(14, "THE DAY AFTER"), source=SRC_V, countryLabels=[cl(LT, "LITHUANIA", BLUE)],
  cities=[mk(VIL, "PARLIAMENT, VILNIUS", W("p36", "parliament"), BLUE, "target", 9)], labels=[lb(offp(VIL, 0, -45), "BAN ON HOSTING NUCLEAR WEAPONS", W("p36", "constitutional"), WHITE)])
a, b = b, S("p37")
add(id="c6-votes", type="timeline", start=round(a, 3), end=round(b, 3), tag="REAL DATA", title="LITHUANIA: REPEAL OF THE BAN", sub="First of three parliamentary votes passed, before this simulation", total=3, unit="votes",
    segments=[{"from": 0, "to": 1, "label": "PASSED", "color": BLUE}, {"from": 1, "to": 3, "label": "TO COME", "color": AMBER}], cursorTo=1, source=SRC_V)
a, b = S("p37"), W("p37", "Whether") - 0.2
R("c6-stop", a, b, [(a, [18.0, 54.0], 1500), (a + 5.0, [16.0, 53.0], 2300), (b, [16.0, 53.0], 2000)], highlight=HL, legend=LEG, **DAY(14, "THE DECISION"),
  cities=[mk(KAL, "THE DECISION", a + 0.3, RED, "target", 9), mk(BRU, "ALLIANCE MEETING", W("p37", "alliance"), BLUE, "dot", 7), mk(WAR, "CONVENTIONAL REPLY", W("p37", "conventional"), BLUE, "dot", 7), mk(MOS, "REPLY IN KIND", W("p37", "kind"), RED, "dot", 7), mk([13.4, 52.52], "PAUSE FOR TALKS", W("p37", "pause"), TEAL, "dot", 7)])
a, b = b, S("p38")
R("c6-open", a, b, [(a, B, 300), (a + 3.0, [20.0, 54.5], 900), (b, [18.0, 54.0], 1500)], highlight=HL, legend=LEG, **DAY(14, "THE DECISION"),
  cities=[mk(B, "A BURST ON RUSSIAN SOIL", a + 0.3, RED, "target", 8)], labels=[lb([19.0, 56.4], "ARTICLE FIVE: THE QUESTION LEFT OPEN", W("p37", "Article"), BLUE)])
a, b = S("p38"), S("p39")
R("c6-end", a, b, [(a, GAPC, 480), (a + 3.0, GAPC, 330), (b, [23.0, 54.1], 420)], highlight=HL, legend=LEG_ROUTE, **DAY(14, "THE DAY AFTER"), caption="The ban is still in force.",
  lines=poly(ROAD1[2:], a + 0.2, a + 1.4, WHITE, "TWO ROADS", False, 4) + poly(ROAD2[1:], a + 0.5, a + 1.7, WHITE, None, False, 4) + poly(RAIL1[2:], a + 0.9, a + 2.1, YELLOW, "ONE RAIL LINE", True, 4),
  labels=[lb(offp(GAPC, 0, -60), "THE GAP IS STILL TWO ROADS AND ONE RAIL LINE", W("p38", "gap"), YELLOW)])

# ------------------------------------------------------------------ End slate
add(id="end", type="endslate", start=round(S("p39"), 3), end=END, tag="", title="Next scenario", line="The first week of a US-China Pacific war: who runs out of missiles first.")

# ------------------------------------------------------------------ audio plan and output
b0 = round(min(FL - 0.3, W("p01", "simulation") - 0.3), 2)
booms = [round(FL + 0.1, 2), round(S("p25") + (W("p25", "flash") - S("p25")) + 0.1, 2), round(S("p27") + 0.1, 2)]
for s in shots:
    for key in ("zones",):
        for z in s.get(key, []):
            z.pop("_deck", None)
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
    s.pop("stamp_", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:14} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
