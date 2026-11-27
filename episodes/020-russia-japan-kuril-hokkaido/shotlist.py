"""Director pass for episode 020: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 020-russia-japan-kuril-hokkaido
Payoff first: the 10 kt air burst over the Pacific off south-east Hokkaido (a region shot with `burst`, flash at about 3 s,
under the banner), then the run-up (the Kalibr from the Sea of Okhotsk), real data (the islands), real history, the spark and
the day-by-day, ring by ring, the day after.  Actors: Russia amber, Japan and the US blue, red only for strikes.  Launch sites
are simulated and say so.  All times are absolute seconds.
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


KMX, KMY = 80.0, 111.0                               # km per degree at about 43 N


def offp(c, dx, dy):
    return [round(c[0] + dx / KMX, 5), round(c[1] + dy / KMY, 5)]


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
NUC = ST["kalibr-escort-group"]
FX = NUC["effects"]
BURST = [NUC["target_lon"], NUC["target_lat"]]
SUBP = [NUC["launch_lon"], NUC["launch_lat"]]
KUN = [ST["bastion-nemuro"]["launch_lon"], ST["bastion-nemuro"]["launch_lat"]]
DEST = [ST["bastion-nemuro"]["target_lon"], ST["bastion-nemuro"]["target_lat"]]
HOKL = [ST["type12-kunashir"]["launch_lon"], ST["type12-kunashir"]["launch_lat"]]
ITU, NOS, HABI, NEM = [147.6, 45.0], [145.82, 43.39], [145.87, 43.41], [145.58, 43.33]
SOYA, TSU, VLA, SAK2, YKS, TKY = [141.94, 45.52], [140.5, 41.5], [131.9, 43.1], [143.1, 46.65], [139.67, 35.28], [139.7, 35.7]
HAK, CHI, SHU, MOS, KENG = [140.73, 41.77], [141.67, 42.8], [156.4, 50.7], [37.6, 55.75], [130.7, 32.8]
RU, JP = "643", "392"
HL = [hl(RU, AMBER, 0.08), hl(JP, BLUE, 0.10)]
LEG = [{"text": "RUSSIA", "color": AMBER}, {"text": "JAPAN AND US", "color": BLUE}]
OFFS = [(-0.05, -0.03), (0.0, 0.0), (0.05, 0.035)]


def GR(a, b, label=None, spread=0.0, t=None, size=34):
    """the Japanese and American escort group around the target point"""
    out = []
    for i, (dx, dy) in enumerate(OFFS):
        p0 = [round(BURST[0] + dx, 4), round(BURST[1] + dy, 4)]
        p1 = [round(BURST[0] + dx * (1 + spread) + 0.02, 4), round(BURST[1] + dy * (1 + spread) - 0.012, 4)]
        out.append(ship([p0, p1], a, b, "ally" if i != 1 else "us", BLUE, label if i == 1 else None, size, t=t if t is not None else a))
    return out


SC = 6.0   # rings are drawn 6x true size at sea (10 kt rings are metres to a few km on a 200 km frame); captioned as such
CC = offp(BURST, -30, 4)   # c5 camera centre: shifted west so the Hokkaido coast stays in frame


def rr(key, t):
    base = {"fire": (FX["fireball_km"], ORANGE, "FIREBALL, 20 PSI: UNDER 0.3 KM", False), "p20": (FX["psi20_km"], RED, None, False), "p5": (FX["psi5_km"], RED, "5 PSI", False),
            "b": (FX["thermal3_km"], AMBER, "BURNS", True), "p1": (FX["psi1_km"], TEAL, "1 PSI", False)}[key]
    return rg(BURST, round(base[0] * SC, 3), t, base[1], None, base[3])



CAP5 = "Rings drawn 6 times true size. Ships not to scale."


def C5(sid, a, b, views, burst=None, rings=(), labels=(), cities=(), lines=(), caption=CAP5, maxd=6.5, **kw):
    """c5 shot split into equal segments (each at most maxd s), a different camera move per segment, rings and ships carried across"""
    n = max(1, math.ceil((b - a) / maxd))
    for i in range(n):
        sa, sb = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
        c0, w0, c1, w1 = views[i % len(views)]
        labs = []
        for l in labels:
            if sa - 0.01 <= l["t"] < sb:
                l = dict(l)
                l["t"] = min(l["t"], sb - 2.0)
                labs.append(l)
        extra = dict(kw)
        if burst:
            extra["burst"] = dict(burst)
        R(sid if n == 1 else f"{sid}-{'abc'[i]}", sa, sb, ZM(sa, sb, c0, w0, c1, w1), highlight=HL, legend=LEG, clock=kw.get("clock"), clockLabel="THE BURST", clockRate=1,
          rings=[dict(r) for r in rings], ships=GR(sa, sb, size=12), cities=[dict(c) for c in cities], lines=[dict(l) for l in lines], labels=labs, caption=caption,
          **{k: v for k, v in extra.items() if k not in ("clock",)})


EXT = {"clock": "", "clockLabel": ""}

# ================================================================== Cold open [SIMULATION]
FL = round(W("p01", "Nagasaki") + 0.05, 2)          # the flash lands on "Nagasaki" (about 5.75 s) so the banner reaches the spoken disclaimer
KA, KB = W("p03", "fires"), S("p05") - 0.2          # the cold-open Kalibr, compressed time
Q = lerp(SUBP, BURST, 0.85)
a, b = 0.0, FL
R("open-run", a, b, [("s", [146.8, 44.4], 820), (2.8, [146.6, 43.9], 680), ("e", [146.5, 43.4], 560)], clock="T-00:08", clockLabel="UNTIL THE BURST", clockRate=2.8, highlight=HL, legend=LEG,
  ships=GR(a, b, "ESCORT GROUP", 0.0, 0.0) + [ship([[147.25, 45.2], [146.55, 42.95]], 0.05, b, "pla", RED, "KALIBR", 26)],
  labels=[lb([143.6, 43.4], "HOKKAIDO", 0.1, BLUE), lb([145.7, 44.4], "KUNASHIR", 0.5, AMBER), lb([147.9, 41.9], "PACIFIC OCEAN", 1.2, WHITE), lb([143.2, 44.6], "27 MINUTES AFTER LAUNCH", 3.0, YELLOW), lb([146.2, 42.2], "THE TARGET", 4.2, RED)])
a, b = FL, S("p02")
R("open-flash", a, b, [(a, BURST, 170), (a + 1.2, BURST, 140), ("e", BURST, 200)], clock="T+00:00", clockLabel="THE BURST", clockRate=1, highlight=HL,
  burst={"at": BURST, "t": a + 0.1, "km": 9, "fade": 8}, rings=[rg(BURST, round(FX["psi5_km"] * SC, 2), a + 1.3, RED, None, False)],
  ships=GR(a, b), labels=[lb(offp(BURST, 0, 24), "10 KT AIR BURST (SIMULATED)", a + 0.6, WHITE), lb(offp(BURST, 38, -22), "ESCORT GROUP", a + 0.5, BLUE)])
a, b = S("p02"), S("p03")
R("open-after", a, b, ZM(a, b, BURST, 260, [145.4, 43.5], 820), clock="T+00:30", clockLabel="AFTER THE BURST", clockRate=1, highlight=HL, legend=LEG,
  burst={"at": BURST, "t": a - 5.0, "km": 9, "fade": 9}, ships=GR(a, b), cities=[mk(NOS, "CAPE NOSAPPU", a + 1.2, BLUE, "dot", 6)],
  lines=[ln(NOS, BURST, a + 2.0, a + 3.2, WHITE, "ABOUT 85 KM", True, 2)],
  labels=[lb(offp(BURST, 25, 26), "IT HAS NOT HAPPENED", W("p02", "not"), YELLOW), lb([143.6, 43.5], "HOKKAIDO", a + 0.5, BLUE)])
# run-up: twenty-seven minutes earlier, the Kalibr flies
a, b = S("p03"), W("p03", "fires")
R("open-sub", a, b, ZM(a, b, [146.3, 46.9], 1500, [147.2, 46.5], 900), caption="27 minutes earlier.", highlight=HL, legend=LEG, **cd(a, b, KA, KB, 1392),
  cities=[mk(SUBP, "RUSSIAN SUBMARINE (SIMULATED)", W("p03", "submarine"), AMBER, "sub", 8)], labels=[lb([145.4, 48.4], "SEA OF OKHOTSK", W("p03", "Okhotsk"), WHITE), lb(BURST, "TARGET AREA", a + 1.0, BLUE)])
a, b = b, S("p04")
R("open-fire", a, b, ZM(a, b, [147.0, 45.0], 1000, [146.7, 43.8], 650), highlight=HL, legend=LEG, **cd(a, b, KA, KB, 1392),
  ships=GR(a, b, "ESCORT GROUP") + [fly(a, b, SUBP, Q, KA, KB, "KALIBR", 26)], lines=[ln(SUBP, BURST, a + 0.2, a + 1.8, RED, "386 KM", True, 2)],
  labels=[lb([145.3, 44.7], "JAPANESE AND US WARSHIPS", W("p03", "Japanese"), BLUE)])
a, b = S("p04"), S("p05")
R("open-radar", a, b, ZM(a, b, [146.6, 43.4], 520, [146.5, 42.95], 300), highlight=HL, legend=LEG, **cd(a, b, KA, KB, 1392),
  ships=GR(a, b, "ESCORT GROUP") + [fly(a, b, SUBP, Q, KA, KB, "KALIBR", 26)], rings=[rg(BURST, 60, a + 0.4, BLUE, "RADAR RANGE (SIMPLIFIED)", True)],
  labels=[lb([146.9, 44.0], "RADAR PICKS IT UP", W("p04", "Radar"), WHITE), lb([145.7, 42.6], "27 MINUTES TO ACT", W("p04", "twenty-seven"), YELLOW)])
a, b = S("p05"), W("p05", "And", 2)
R("open-why", a, b, ZM(a, b, [146.3, 43.5], 520, [145.6, 43.5], 380), highlight=HL, legend=LEG, **DAY(7, "11:10 LOCAL"), ships=GR(a, b, "SHIPS"),
  cities=[mk(NEM, "NEMURO: A JAPANESE CITY", W("p05", "city"), BLUE, "dot", 7)], labels=[lb([146.6, 43.2], "WHY SHIPS?", W("p05", "ships"), YELLOW)])
a, b = b, W("p05", "answer")
R("open-who", a, b, ZM(a, b, [141.5, 39.6], 1900, [140.5, 38.0], 2600), highlight=HL, legend=LEG, **DAY(7, "11:10 LOCAL"),
  cities=[mk(TKY, "TOKYO", W("p05", "Tokyo"), BLUE, "dot", 8), mk(YKS, "YOKOSUKA: US NAVY", W("p05", "Washington"), BLUE, "base", 8)], labels=[lb([146.0, 42.2], "27 MINUTES", W("p05", "half"), YELLOW)])
a, b = b, S("p06")
R("open-isl", a, b, ZM(a, b, [145.8, 43.7], 800, [145.8, 43.7], 420), highlight=HL, legend=LEG, **DAY(7, "11:10 LOCAL"),
  labels=[lb([145.4, 44.3], "KUNASHIR", W("p05", "islands"), AMBER), lb([143.8, 43.4], "HOKKAIDO", W("p05", "Japan"), BLUE)])

# ================================================================== Chapter 01 [REAL DATA]
a = chapter("c1-card", S("p06"), 3.7, "CHAPTER 01", "Islands within sight", "REAL DATA")
b = W("p06", "No")
R("c1-iturup", a, b, ZM(a, b, [146.0, 44.3], 1000, [147.4, 44.9], 480), tag="REAL DATA", highlight=HL, legend=LEG, source="Al Jazeera, 13 August 2026",
  cities=[mk(ITU, "ITURUP: PUTIN LANDED", a + 0.3, AMBER, "target", 8)], labels=[lb([148.0, 45.9], "LARGEST KURIL ISLAND", W("p06", "largest"), WHITE)], caption="13 August 2026")
a, b = b, S("p07")
R("c1-reaction", a, b, ZM(a, b, [145.0, 43.5], 900, [141.5, 41.5], 2200), tag="REAL DATA", highlight=HL, legend=LEG, source="Al Jazeera, 13 August 2026; Stars and Stripes",
  labels=[lb([146.2, 45.4], "FIRST RUSSIAN PRESIDENT HERE", a + 0.3, AMBER), lb([141.7, 43.0], "JAPAN: ABSOLUTELY UNACCEPTABLE", W("p06", "absolutely"), BLUE)])
a, b = S("p07"), W("p07", "ships")
R("c1-fire1", a, b, ZM(a, b, [147.2, 45.2], 1000, [147.5, 45.0], 620), tag="REAL DATA", highlight=HL, legend=LEG, source="Russian Pacific Fleet, via Stars and Stripes, August 2026",
  cities=[mk(ITU, "MISSILES FIRED FROM THE ISLANDS", W("p07", "islands"), AMBER, "base", 8)], lines=[ln(ITU, [150.3, 43.6], a + 1.5, a + 3.5, RED, None, True, 2)], labels=[lb([145.8, 45.9], "AUGUST 2026 DRILLS", a + 0.3, WHITE)])
a, b = b, S("p08")
R("c1-fire2", a, b, ZM(a, b, [148.5, 44.6], 800, [148.2, 45.0], 1300), tag="REAL DATA", highlight=HL, legend=LEG, source="Russian Pacific Fleet, via Stars and Stripes, August 2026",
  ships=[ship([[149.8, 46.6], [149.0, 44.9]], a, b, "pla", AMBER, "RUSSIAN WARSHIPS", 22)], cities=[mk([148.4, 46.6], "SUBMARINE", a + 0.8, AMBER, "sub", 8)],
  labels=[lb([150.0, 43.4], "HYPOTHETICAL ENEMY SHIPS", W("p07", "hypothetical"), WHITE)])
a, b = S("p08"), W("p08", "their")
R("c1-bastion", a, b, ZM(a, b, [146.7, 44.5], 800, [146.7, 44.5], 520), tag="REAL DATA", highlight=HL, legend=LEG, source="Russian Defence Ministry, via GlobalSecurity",
  cities=[mk(KUN, "BASTION: KUNASHIR", W("p08", "Bastion"), AMBER, "base", 8), mk([147.2, 44.95], "BASTION: ITURUP", W("p08", "southern"), AMBER, "base", 8)], labels=[lb([146.1, 45.8], "SINCE 2016", W("p08", "sixteen"), WHITE)])
a, b = b, S("p09")
R("c1-range", a, b, ZM(a, b, [145.5, 44.0], 700, [144.0, 44.0], 1600), tag="REAL DATA", highlight=HL, legend=LEG, source="Russian Defence Ministry, via GlobalSecurity",
  cities=[mk(KUN, "BASTION BATTERY", a + 0.2, AMBER, "base", 8)], rings=[rg(KUN, 300, W("p08", "hundreds"), AMBER, "ABOUT 300 KM", True)], labels=[lb([141.5, 42.3], "SIMULATION: FIRST SHOT", W("p08", "simulation"), YELLOW)])
a, b = S("p09"), W("p09", "Kunashir")
R("c1-kurils", a, b, ZM(a, b, [144.5, 43.8], 1100, [145.4, 43.8], 620), tag="REAL DATA", highlight=HL, legend=LEG, source="Wikipedia, Kuril Islands dispute; Japanese government",
  labels=[lb([146.6, 44.7], "SOUTHERN KURILS", a + 0.3, AMBER), lb([143.0, 43.5], "HOKKAIDO", W("p09", "Hokkaido"), BLUE), lb([144.6, 42.6], "A FEW KM TO A FEW DOZEN", W("p09", "few"), WHITE)])
a, b = b, S("p10")
R("c1-izmena", a, b, ZP(a, b, [([145.45, 43.75], 300), ([145.55, 43.7], 190), ([145.9, 43.4], 190), ([145.85, 43.4], 260)]), tag="REAL DATA", highlight=HL, source="Wikipedia, Kuril Islands dispute; Japanese government",
  lines=[ln([145.3, 43.6], [145.45, 43.78], W("p09", "sixteen") - 0.3, W("p09", "sixteen") + 1.2, WHITE, "ABOUT 16 KM", True, 2), ln(NOS, HABI, W("p09", "four"), W("p09", "four") + 1.2, WHITE, "ABOUT 4 KM", True, 2)],
  labels=[lb([145.65, 44.0], "KUNASHIR", a + 0.2, AMBER), lb([145.1, 43.5], "NOTSUKE PENINSULA", W("p09", "peninsula"), BLUE)],
  cities=[mk(NOS, "CAPE NOSAPPU, HOKKAIDO", W("p09", "cape"), BLUE, "dot", 7), mk(HABI, "NEAREST ISLET", W("p09", "islet"), AMBER, "dot", 7)])
a, b = S("p10"), S("p11")
R("c1-okhotsk", a, b, ZP(a, b, [([146.0, 49.0], 1300), ([147.0, 48.5], 1900), ([145.0, 44.5], 1300), ([144.5, 43.7], 650)]), tag="REAL DATA", highlight=HL, legend=LEG, source="FAS; Lowy Interpreter",
  labels=[lb([146.0, 50.6], "SEA OF OKHOTSK", a + 0.3, WHITE), lb([149.0, 47.5], "RUSSIAN MISSILE SUBMARINES", W("p10", "missile"), AMBER), lb([148.8, 45.2], "KURIL STRAITS", W("p10", "Kurils"), AMBER), lb([146.7, 44.2], "A PIECE OF THE DOOR", W("p10", "piece"), YELLOW)],
  cities=[mk([148.0, 49.3], None, a + 2.5, AMBER, "sub", 8), mk([150.5, 48.3], None, a + 3.0, AMBER, "sub", 8), mk(SOYA, "SOYA STRAIT", W("p10", "Soya"), BLUE, "dot", 8), mk(TSU, "TSUGARU STRAIT", W("p10", "Tsugaru"), BLUE, "dot", 8)])
a, b = S("p11"), W("p11", "Its")
R("c1-kengun", a, b, ZP(a, b, [([134.0, 36.0], 2700), ([136.0, 38.5], 3300), ([142.0, 42.0], 1500), ([143.5, 43.6], 480)]), tag="REAL DATA", highlight=HL, legend=LEG, source="PBS NewsHour; Lowy Interpreter",
  cities=[mk(KENG, "KUMAMOTO: DEPLOYED MARCH 2026", W("p11", "March"), BLUE, "base", 8), mk([142.47, 43.46], "PLANNED: CAMP KAMIFURANO", W("p11", "Hokkaido"), BLUE, "base", 8)],
  rings=[rg(KENG, 1000, W("p11", "thousand"), BLUE, "RANGE ABOUT 1,000 KM", True)], labels=[lb([144.6, 44.5], "HOKKAIDO ITSELF", W("p11", "itself"), BLUE)])
a, b = b, S("p12")
add(id="c1-yen", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="9 TRILLION YEN", label="record defence budget, fiscal 2026", sub="about 58 billion dollars", color=BLUE, source="PBS NewsHour; Lowy Interpreter")
a, b = S("p12"), W("p12", "navy")
R("c1-fleet", a, b, ZM(a, b, [148.0, 47.0], 3000, [148.0, 47.0], 2200), tag="REAL DATA", highlight=HL, legend=LEG, source="FAS; Bulletin of the Atomic Scientists",
  cities=[mk(VLA, "VLADIVOSTOK", a + 0.5, AMBER, "base", 8), mk([158.65, 53.0], "PETROPAVLOVSK", a + 1.8, AMBER, "base", 8)], labels=[lb([146.0, 45.0], "THE PACIFIC FLEET", a + 0.3, AMBER)])
a, b = b, b + 5.5
add(id="c1-767", type="number", start=round(a, 3), end=round(b, 3), tag="REAL DATA", value="767", countTo=767, label="navy non-strategic warheads, one estimate", sub="for cruise missiles and torpedoes", color=AMBER, source="FAS; Bulletin of the Atomic Scientists, 2026")
a, b = b, S("p14")
R("c1-storage", a, b, ZP(a, b, [([146.5, 46.5], 1500), ([146.5, 45.0], 850), ([145.6, 43.7], 500)]), tag="REAL DATA", highlight=HL, legend=LEG, source="FAS; Bulletin of the Atomic Scientists, 2026",
  labels=[lb([142.0, 49.0], "DECLARED: CENTRAL STORAGE", a + 0.3, AMBER), lb([147.3, 44.3], "NONE ON THE ISLANDS", W("p12", "islands"), WHITE), lb([144.6, 44.7], "HAS EITHER SIDE FIRED BEFORE?", S("p13") + 0.2, YELLOW)])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p14"), 3.7, "CHAPTER 02", "The treaty that never came", "REAL HISTORY")
b = S("p15")
R("c2-1945", a, b, ZP(a, b, [([150.0, 48.0], 2400), ([149.0, 47.0], 1700), ([146.6, 43.8], 700), ([146.3, 43.6], 420)]), tag="REAL HISTORY", highlight=HL, source="Wikipedia, Invasion of the Kuril Islands; History.com",
  lines=[ln(SHU, ITU, a + 0.6, a + 3.0, AMBER, "SOVIET LANDINGS", False, 3)], cities=[mk(SHU, "SHUMSHU: 18 AUGUST 1945", W("p14", "landing"), AMBER, "target", 8), mk([146.0, 43.45], "HABOMAI: BY 4 SEPTEMBER", W("p14", "September"), AMBER, "dot", 7), mk(KUN, "KUNASHIR: 1 SEPTEMBER", W("p14", "September") + 1.0, AMBER, "dot", 7)],
  labels=[lb([145.3, 44.7], "AFTER THE WAR WAS OVER", W("p14", "after"), YELLOW), lb([144.2, 43.5], "17,000 ISLANDERS SENT AWAY", W("p14", "seventeen"), WHITE)], caption="15 August 1945: Japan announces its surrender")
a, b = S("p15"), W("p15", "In", 2)
R("c2-treaty", a, b, ZM(a, b, [146.5, 44.0], 700, [146.0, 43.8], 1100), tag="REAL HISTORY", highlight=HL, source="Wikipedia, Kuril Islands dispute; Moscow Times", caption="19 October 1956: Moscow and Tokyo end the state of war",
  cities=[mk([146.0, 43.45], "HABOMAI", W("p15", "two"), BLUE, "dot", 7), mk([146.75, 43.8], "SHIKOTAN", W("p15", "two") + 0.5, BLUE, "dot", 7)],
  labels=[lb([147.6, 44.8], "ITURUP, KUNASHIR: NOT OFFERED", W("p15", "four"), AMBER), lb([144.2, 43.8], "TWO ISLANDS PROMISED", W("p15", "two"), WHITE), lb([144.2, 42.9], "NO TREATY EVER FOLLOWED", W("p15", "No"), YELLOW), lb([147.8, 42.4], "THE WAR ENDS, 1956", a + 0.3, WHITE)])
a, b = b, W("p15", "Japan")
stamp("c2-2022", a, b, "MARCH 2022", "Russia suspends the peace talks", AMBER, "REAL HISTORY", source="Moscow Times; Lowy Interpreter")
a, b = b, S("p16")
R("c2-nophone", a, b, ZM(a, b, [137.0, 42.0], 2600, [140.0, 42.0], 2000), tag="REAL HISTORY", highlight=HL, legend=LEG, source="Lowy Interpreter",
  lines=[ln(VLA, TKY, a + 2.0, a + 4.0, WHITE, "NO CHANNEL OPEN", True, 2)], cities=[mk(TKY, "TOKYO", a + 1.2, BLUE, "dot", 7)],
  labels=[lb([133.0, 46.0], "JAPAN JOINED THE SANCTIONS", W("p15", "sanctions"), BLUE), lb([145.0, 38.5], "NOBODY HAS A CHANNEL OPEN", W("p15", "nobody"), YELLOW)])
a, b = S("p16"), W("p16", "It", 2)
R("c2-belenko", a, b, ZP(a, b, [([136.0, 42.8], 1500), ([137.5, 42.5], 1100), ([141.2, 42.0], 480)]), tag="REAL HISTORY", highlight=HL, source="Wikipedia, Defection of Viktor Belenko", caption="6 September 1976: a Soviet fighter lands at Hakodate",
  lines=[ln(VLA, HAK, a + 0.8, a + 4.5, WHITE, "ONE FIGHTER", True, 3)], cities=[mk(VLA, "VLADIVOSTOK", a + 0.3, AMBER, "base", 8), mk(HAK, "HAKODATE", W("p16", "Hakodate"), BLUE, "target", 8),
  mk(CHI, "CHITOSE: TWO FIGHTERS UP", W("p16", "fighters"), BLUE, "base", 8)], labels=[lb([141.0, 40.8], "THEY NEVER FOUND HIM", W("p16", "never"), YELLOW), lb([138.5, 43.8], "RADAR SAW HIM", W("p16", "Radar"), WHITE)])
a, b = b, S("p17")
R("c2-air", a, b, ZM(a, b, [137.5, 43.2], 1400, [135.5, 43.5], 900), tag="REAL HISTORY", highlight=HL, source="Wikipedia, Defection of Viktor Belenko",
  labels=[lb([139.0, 44.8], "A DEFECTION, NOT AN ATTACK", W("p16", "defection"), WHITE), lb([132.3, 44.4], "SOVIET AIR BASES NEARBY", W("p16", "Soviet", 2), AMBER)], cities=[mk(VLA, "VLADIVOSTOK", a + 0.4, AMBER, "base", 8)])
a, b = S("p17"), S("p19")
R("c2-calm", a, b, ZM(a, b, [145.6, 43.7], 600, [146.0, 43.9], 1500), tag="REAL HISTORY", highlight=HL, legend=LEG, source="Reports at the time",
  labels=[lb([145.2, 44.6], "NO CLASH", W("p17", "clash"), WHITE), lb([145.2, 43.9], "NO BLOCKADE", W("p17", "blockade"), WHITE), lb([145.2, 43.2], "NO SHOT FIRED", W("p17", "shot"), WHITE), lb([148.5, 45.0], "THE AUGUST FIRINGS WERE DRILLS", W("p17", "drills"), AMBER),
          lb([141.0, 43.3], "A QUARREL, THEN WHAT?", W("p18", "quarrel"), YELLOW)])

# ================================================================== Chapter 03 [SIMULATION]
a = chapter("c3-card", S("p19"), 3.7, "CHAPTER 03", "The spark", "SIMULATION")
b = S("p20")
R("c3-collide", a, b, ZM(a, b, [145.6, 43.7], 330, [145.6, 43.6], 190), **DAY(1, "THE COLLISION"), highlight=HL, legend=LEG,
  ships=[ship([NEM, [145.6, 43.6]], a, a + 6.0, "coastguard", BLUE, "JAPAN COAST GUARD", 22), ship([[145.55, 43.95], [145.6, 43.62]], a, a + 6.0, "coastguard", AMBER, "RUSSIAN BORDER BOAT", 22)],
  labels=[lb([145.2, 43.2], "NEMURO STRAIT", W("p19", "Nemuro"), WHITE), lb([145.3, 43.75], "THEY TOUCH", W("p19", "touch"), RED), lb([146.1, 43.45], "THE CAUSE IS LEFT UNSAID", W("p19", "cause"), YELLOW)])
a, b, MID = S("p20"), S("p21"), W("p20", "Japan")
ZONE = [[145.2, 43.45], [146.1, 43.45], [146.15, 43.95], [145.3, 44.05]]
R("c3-zone", a, b, ZP(a, b, [([137.5, 41.0], 2900), ([139.0, 42.0], 2200), ([145.7, 43.7], 330), ([145.7, 43.8], 220), ([142.6, 41.2], 1100)]), **DAY(2, "THE CLOSURE ZONE"), highlight=HL, legend=LEG,
  lines=[ln(VLA, TKY, a + 1.0, a + 3.0, WHITE, "TALKS FROZEN SINCE 2022", True, 2)], cities=[mk(TKY, "TOKYO", a + 0.4, BLUE, "dot", 7), mk(VLA, "VLADIVOSTOK", a + 0.8, AMBER, "dot", 7), mk(YKS, "YOKOSUKA", W("p20", "Yokosuka"), BLUE, "base", 8)],
  zones=[zn(ZONE, W("p20", "closure"), AMBER, "RUSSIAN CLOSURE ZONE", 0.14, True)], labels=[lb([145.0, 43.1], "LIVE-FIRE WARNINGS", W("p20", "live-fire"), AMBER)],
  ships=[ship([[141.5, 41.9], [145.0, 43.3]], MID + 0.2, b, "ally", BLUE, "JAPANESE DESTROYERS", 22), ship([[139.7, 35.0], [142.0, 40.5], [145.0, 42.4]], MID + 1.0, b, "us", BLUE, "US SHIPS FROM YOKOSUKA", 22)])
a, b = S("p21"), S("p22")
R("c3-soil", a, b, ZP(a, b, [([146.0, 44.4], 1000), ([146.3, 44.8], 600), ([147.0, 45.5], 800), ([146.0, 46.5], 1500)]), **DAY(2, "MOSCOW'S POSITION"), highlight=HL, legend=LEG,
  labels=[lb([146.6, 45.6], "RUSSIAN SOIL, SAYS MOSCOW", W("p21", "Russian"), AMBER), lb([144.0, 43.6], "CONSTITUTION BARS HANDOVER", W("p21", "constitution"), WHITE),
          lb([147.5, 44.4], "CRITICAL THREAT TO TERRITORY", W("p21", "critical"), AMBER), lb([145.0, 47.5], "A CONDITION FOR NUCLEAR USE", W("p21", "nuclear"), RED)])
a, b = S("p22"), S("p23")
R("c3-pressure", a, b, ZP(a, b, [([145.5, 43.8], 600), ([145.0, 43.5], 1100), ([144.0, 44.5], 1900)]), **DAY(2, "OUR CHOICE"), highlight=HL, legend=LEG,
  labels=[lb([144.3, 44.7], "THE SIMULATION'S CHOICE", W("p22", "chooses"), YELLOW), lb([141.4, 42.2], "NO PUBLISHED WARGAME FOUND", W("p22", "published"), YELLOW), lb([147.5, 45.6], "EVERY STEP IS OUR CHOICE", W("p22", "step"), WHITE)])

# ================================================================== Chapter 04 [SIMULATION]
KA2, KB2 = W("p27", "leaves"), S("p32") - 0.4
a = chapter("c4-card", S("p23"), 3.7, "CHAPTER 04", "Day by day", "SIMULATION")
OA, OB = W("p23", "fires"), W("p23", "target")
b = S("p24")
R("c4-d3", a, b, ZP(a, b, [([145.7, 43.75], 280), ([145.65, 43.7], 190), ([145.5, 43.5], 300)]), **DAY(3, "BASTION FIRES"), highlight=HL, legend=LEG,
  ships=[ship([[145.6, 43.45], DEST], a, b, "ally", BLUE, "JAPANESE DESTROYER", 22), fly(a, OB + 0.0, KUN, DEST, OA, OB, "ONIKS", 24)], lines=[ln(KUN, DEST, OA, OB, RED, "54 KM", True, 2)],
  cities=[mk(KUN, "BASTION BATTERY (SITE SIMULATED)", a + 0.3, AMBER, "base", 8)],
  labels=[lb([146.0, 43.8], "UNDER FOUR MINUTES", W("p23", "four"), RED), lb([145.0, 43.9], "WE DO NOT SAY IF IT SURVIVES", W("p23", "Whether"), YELLOW), lb([146.0, 43.3], "CREW: NOT SIMULATED", W("p23", "crew"), WHITE)])
a, b = S("p24"), S("p25")
R("c4-d4", a, b, ZP(a, b, [([145.7, 43.7], 450), ([145.6, 43.6], 330), ([141.5, 46.0], 2800), ([142.0, 44.0], 2000), ([138.5, 41.0], 2500), ([140.5, 42.0], 2000)]), **DAY(4, "NOTHING IS FIRED"), highlight=HL, legend=LEG,
  ships=[ship([[145.9, 43.9], [145.85, 43.85]], a, a + 5.0, "coastguard", AMBER, "RUSSIAN BOAT", 20), ship([[145.5, 43.35], [145.55, 43.4]], a, a + 5.0, "coastguard", BLUE, "JAPAN COAST GUARD", 20)],
  labels=[lb([146.2, 43.2], "NOTHING IS FIRED", a + 0.4, WHITE), lb([142.7, 50.4], "RUSSIA: NO WIDER WAR", W("p24", "Both"), AMBER), lb([142.3, 43.2], "JAPAN: NO WIDER WAR", W("p24", "governments"), BLUE)],
  lines=[ln(VLA, TKY, W("p24", "calm") + 1.0, W("p24", "calm") + 3.0, WHITE, None, True, 2)], cities=[mk(TKY, "ONE PHONE", W("p24", "phones"), BLUE, "dot", 8), mk(VLA, "THE OTHER, SILENT", W("p24", "phones") + 0.6, AMBER, "dot", 8)])
a, b = S("p25"), S("p26")
TA, TB = W("p25", "fires"), S("p26") - 1.0
R("c4-d5", a, b, ZP(a, b, [([144.0, 43.5], 900), ([143.0, 43.3], 600), ([143.6, 43.6], 650), ([144.2, 43.9], 520)]), highlight=HL, legend=LEG, **cd(a, b, TA, TB, 1218, "SINCE LAUNCH"),
  ships=[fly(a, b, HOKL, KUN, TA, TB, "TYPE-12 (ASSUMED)", 24, BLUE, "us")], lines=[ln(HOKL, KUN, TA, TA + 2.0, BLUE, "288 KM", True, 2)],
  cities=[mk(HOKL, "ASSUMED: CENTRAL HOKKAIDO", W("p25", "central"), BLUE, "base", 8), mk(KUN, "BASTION BATTERY", W("p25", "Bastion"), AMBER, "target", 8)],
  labels=[lb([143.0, 44.6], "JAPAN ANSWERS, CONVENTIONALLY", W("p25", "answers"), BLUE), lb([144.6, 42.4], "NO NUCLEAR WEAPONS", W("p25", "without"), WHITE)])
a, b = S("p26"), W("p26", "doctrine")
G("c4-d6", a, b, [(a, 55, 40, 1500), (a + 4.5, 52, 90, 1100), (b, 46, 140, 800)], **DAY(6, "MOSCOW DECIDES"),
  markers=[{"at": MOS, "label": "MOSCOW: THE QUESTION", "color": AMBER, "kind": "base", "size": 9, "t": 0.3}, {"at": [146.0, 44.5], "label": "THE ISLANDS", "color": BLUE, "kind": "target", "size": 9, "t": W("p26", "islands") - a}],
  arcs=[{"from": MOS, "to": [146.0, 44.5], "t0": 1.0, "t1": 7.0, "color": AMBER, "loft": 0.1}])
a, b = b, W("p26", "Bulletin")
stamp("c4-2024", a, b, "2024", "Russia rewrites its nuclear doctrine", AMBER, "REAL DATA", source="Bulletin of the Atomic Scientists")
a, b = b, S("p27")
R("c4-d6b", a, b, ZM(a, b, [146.0, 44.5], 900, [145.0, 44.0], 600), **DAY(6, "A READING, NOT A PROMISE"), highlight=HL, legend=LEG,
  labels=[lb([147.0, 45.5], "ONE VIEW: IT LOWERED THE BAR", W("p26", "lowered"), AMBER), lb([144.5, 44.8], "A READING, NOT A PROMISE", W("p26", "reading"), YELLOW)])
a, b = S("p27"), W("p27", "We")
R("c4-d7", a, b, ZM(a, b, [146.5, 47.0], 1500, [147.3, 46.4], 900), **DAY(7, "MINUTE ZERO, 11:10 LOCAL"), highlight=HL, legend=LEG, labels=[lb([145.2, 48.6], "SEA OF OKHOTSK", a + 0.4, WHITE)],
  caption="Day seven, minute zero.", cities=[mk(SUBP, "RUSSIAN SUBMARINE (SIMULATED)", a + 3.0, AMBER, "sub", 8)])
a, b = b, S("p28")
R("c4-launch", a, b, ZP(a, b, [([147.0, 45.2], 1000), ([146.8, 44.4], 700), ([146.6, 44.0], 600)]), highlight=HL, legend=LEG, **cd(a, b, KA2, KB2, 1638), ships=GR(a, b, "ESCORT GROUP") + [fly(a, b, SUBP, BURST, KA2, KB2, "KALIBR", 26)],
  labels=[lb([145.0, 46.4], "KALIBR, NUCLEAR (ASSUMED)", W("p27", "Kalibr"), RED), lb([144.9, 45.2], "NOT PUBLIC: OUR CHOICE", W("p27", "public"), YELLOW)], cities=[mk(SUBP, "SUBMARINE", a + 0.3, AMBER, "sub", 8)])
a, b = S("p28"), S("p29")
R("c4-target", a, b, ZM(a, b, [146.8, 44.4], 720, [146.5, 43.3], 420), highlight=HL, legend=LEG, **cd(a, b, KA2, KB2, 1638), ships=GR(a, b, "ESCORT GROUP") + [fly(a, b, SUBP, BURST, KA2, KB2, "KALIBR", 26)],
  lines=[ln(SUBP, BURST, a + 0.5, a + 2.5, RED, "386 KM", True, 2)], labels=[lb([144.6, 43.8], "JAPANESE AND US GROUP", W("p28", "Japanese"), BLUE), lb([148.0, 42.2], "OFF SOUTH-EAST HOKKAIDO", W("p28", "south-east"), WHITE)])
a, b = S("p29"), W("p29", "In")
add(id="c4-27min", type="timeline", start=round(a, 3), end=round(b, 3), tag="SIMULATION", title="WARNING TIME: ABOUT 27 MINUTES", sub="Our assumption: a subsonic cruise missile, 386 km", total=27, unit="min",
    segments=[{"from": 0, "to": 27, "label": "MISSILE IN FLIGHT", "color": RED}], cursorTo=27)
a, b = b, S("p30")
R("c4-spread", a, b, ZP(a, b, [(BURST, 300), ([146.5, 42.9], 190), ([143.0, 39.5], 2200), ([143.5, 40.5], 1500)]), highlight=HL, legend=LEG, **cd(a, b, KA2, KB2, 1638), ships=GR(a, b, "THE GROUP SPREADS OUT", 9.0) + [fly(a, b, SUBP, BURST, KA2, KB2, "KALIBR", 26)],
  labels=[lb([146.0, 43.3], "A DESTROYER CAN TURN", W("p29", "turn"), BLUE), lb([147.0, 42.4], "RADAR TRACKS THE MISSILE", W("p29", "track"), WHITE), lb([147.5, 40.0], "NOBODY KNOWS THE WARHEAD", W("p29", "know"), YELLOW)],
  lines=[ln(BURST, TKY, W("p29", "Commanders"), W("p29", "Commanders") + 2.0, BLUE, "CALL TOKYO", True, 2)], cities=[mk(TKY, "TOKYO", W("p29", "Tokyo"), BLUE, "dot", 8)])
a, b = S("p30"), W("p30", "expired")
R("c4-down", a, b, ZP(a, b, [([146.5, 43.4], 500), ([146.5, 43.0], 300), ([146.5, 43.1], 170)]), highlight=HL, legend=LEG, **cd(a, b, KA2, KB2, 1638), ships=GR(a, b, "ESCORT GROUP", 9.0) + [fly(a, b, SUBP, BURST, KA2, KB2, "KALIBR", 26)],
  labels=[lb([145.0, 43.9], "CAN THE GROUP SHOOT IT DOWN?", W("p30", "shoot"), YELLOW), lb([148.0, 43.0], "WE DO NOT SAY", W("p30", "say"), WHITE), lb([147.0, 43.5], "IT GETS THROUGH: OUR CHOICE", W("p30", "gets"), RED), lb([145.6, 42.4], "NO TREATY CAP ON FORCES", W("p30", "limiting"), WHITE)])
a, b = b, S("p31")
stamp("c4-newstart", a, b, "5 FEBRUARY 2026", "New START expires: no treaty cap on US and Russian forces", WHITE, "REAL DATA", source="FAS, The Expiration of New START")
a, b = S("p31"), S("p32")
R("c4-m27", a, b, ZM(a, b, CC, 420, CC, 260), highlight=HL, legend=LEG, **cd(a, b, KA2, KB2, 1638), ships=GR(a, b, "ESCORT GROUP", 9.0) + [fly(a, b, SUBP, BURST, KA2, KB2, "KALIBR", 26)],
  labels=[lb([148.0, 43.6], "MINUTE 27", a + 0.3, RED), lb([145.0, 42.3], "WHAT DOES 10 KT DO TO WATER?", W("p31", "What"), YELLOW)])

# ================================================================== Chapter 05 [SIMULATION]
a = chapter("c5-card", S("p32"), 3.7, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
b = S("p33")
NOSC = lambda t: mk(NOS, "CAPE NOSAPPU", t, BLUE, "dot", 7)
MID = lerp(NOS, BURST, 0.5)
OVW = offp(BURST, -35, 0)
C5("c5-burst", a, b, [(CC, 200, CC, 240), (OVW, 330, BURST, 180)], clock="T+27:18", burst={"at": BURST, "t": a + 0.15, "km": 9, "fade": 9}, rings=[rr("fire", a + 0.3)], cities=[NOSC(a + 0.6)],
   labels=[lb(offp(BURST, 52, 28), "10 KT: OUR ASSUMPTION", W("p32", "ten"), YELLOW), lb(offp(BURST, 55, -28), "ABOUT 2/3 OF HIROSHIMA", W("p32", "Hiroshima"), WHITE), lb(offp(BURST, 20, -44), "LOW END OF ONE ESTIMATE", W("p32", "low"), WHITE)])
a, b = S("p33"), W("p33", "Within")
C5("c5-fireball", a, b, [(CC, 260, CC, 210), (BURST, 150, offp(BURST, -8, 2), 190), (CC, 230, CC, 280)], clock="T+27:40", rings=[rr("fire", a - 3)], cities=[NOSC(a + 0.4)],
   labels=[lb(offp(BURST, 50, 24), "A SMALL POINT ON A LARGE SEA", W("p33", "small"), WHITE), lb(offp(BURST, 52, -26), "NOT POLICY: 10 KT IS OURS", W("p33", "Russian"), YELLOW),
           lb(offp(BURST, -60, 0), "FIREBALL, 20 PSI: UNDER 0.3 KM", a + 4.6, ORANGE)])
a, b = b, S("p34")
C5("c5-20psi", a, b, [(offp(BURST, -10, 2), 170, offp(BURST, -6, 2), 140), (offp(BURST, -6, 2), 140, offp(BURST, -12, 2), 190)], clock="T+27:50", rings=[rr("fire", a - 3), rr("p20", W("p33", "pressure"))],
   labels=[lb(offp(BURST, 38, 20), "20 PSI: ABOUT 300 M", W("p33", "twenty"), RED), lb(offp(BURST, 40, -22), "WITHIN 300 M OF THE BURST", W("p33", "Within") + 0.3, WHITE)])
a, b = S("p34"), S("p35")
C5("c5-5psi", a, b, [(CC, 190, CC, 240), (offp(BURST, -20, 0), 120, offp(BURST, -20, 0), 180)], clock="T+28:00", rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", W("p34", "one"))], cities=[NOSC(a + 0.4)],
   labels=[lb(offp(BURST, 52, 28), "5 PSI: ABOUT 1.5 KM", W("p34", "one"), RED), lb(offp(BURST, 55, -28), "FLATTENS BUILDINGS ON LAND", W("p34", "flatten"), WHITE), lb(offp(BURST, 20, -44), "ABOUT 7 KM2: A SMALL TOWN", W("p34", "seven"), YELLOW)])
a, b = S("p35"), W("p35", "light")
C5("c5-burns", a, b, [(CC, 220, CC, 260), (BURST, 160, offp(BURST, -15, 0), 200)], clock="T+28:10", rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", W("p35", "burns"))], cities=[NOSC(a + 0.4)],
   labels=[lb(offp(BURST, 55, 28), "THIRD-DEGREE BURNS: 1.6 KM", W("p35", "burns"), AMBER), lb(offp(BURST, 55, -30), "A LITTLE FARTHER THAN BLAST", W("p35", "farther"), WHITE)])
a, b = b, S("p36")
C5("c5-light", a, b, [(CC, 260, CC, 210), (offp(BURST, -25, 0), 170, offp(BURST, -25, 0), 230)], clock="T+28:20", burst={"at": BURST, "t": a + 0.1, "km": 6, "fade": 6},
   rings=[rr("fire", a - 3), rr("p20", a - 3), rr("b", a - 3), rg(BURST, round(FX["psi5_km"] * SC, 2), W("p35", "shock"), RED, None, False)], cities=[NOSC(a + 0.6)],
   labels=[lb(offp(BURST, 52, 28), "THE LIGHT ARRIVES FIRST", a + 0.9, YELLOW), lb(offp(BURST, 55, -28), "THE SHOCK WAVE, SECONDS LATER", W("p35", "shock"), WHITE), lb(offp(BURST, 20, -44), "ALMOST NO TIME TO LOOK AWAY", W("p35", "almost"), RED)])
a, b = S("p36"), S("p37")
C5("c5-1psi", a, b, [(CC, 200, CC, 260), (offp(BURST, -20, -3), 150, offp(BURST, -20, -3), 200)], clock="T+28:40", rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", a - 3), rr("p1", W("p36", "Windows"))], cities=[NOSC(a + 0.4)],
   labels=[lb(offp(BURST, 55, 30), "1 PSI: WINDOWS BREAK, 4 KM", W("p36", "Windows"), TEAL), lb(offp(BURST, 58, -32), "NO PUBLISHED DATA ON WARSHIPS", W("p36", "published"), YELLOW)])
a, b = S("p37"), W("p37", "An")
C5("c5-water", a, b, [(CC, 220, CC, 300), (MID, 330, MID, 260)], clock="T+29:00", rings=[rr("fire", a - 3), rr("p20", a - 3), rr("p5", a - 3), rr("b", a - 3), rr("p1", a - 3)], cities=[NOSC(a + 0.3)],
   lines=[ln(NOS, BURST, a + 6.6, a + 8.4, WHITE, "ABOUT 85 KM", True, 2)],
   labels=[lb(offp(MID, 14, 0), "ABOUT 85 KM", a + 7.2, WHITE), lb(offp(BURST, 40, 30), "EVERY RING FALLS ON OPEN WATER", W("p37", "every"), WHITE), lb(offp(BURST, 40, -34), "NO JAPANESE LAND IN A RING", W("p37", "land"), BLUE)])
a, b = b, S("p38")
R("c5-fallout", a, b, ZM(a, b, MID, 260, MID, 200), highlight=HL, legend=LEG, clock="T+29:20", clockLabel="THE BURST", clockRate=1, burst={"at": BURST, "t": a - 5.0, "km": 4, "fade": 12},
  cities=[mk(BURST, "AIR BURST", a + 0.2, RED, "target", 8), mk(NOS, "CAPE NOSAPPU", a + 0.4, BLUE, "dot", 7)], lines=[ln(NOS, BURST, a + 1.0, a + 2.6, WHITE, "ABOUT 85 KM", True, 2)],
  plume={"at": BURST, "bearing": 90, "lengthKm": 70, "widthKm": 6, "t0": a + 2.0, "t1": a + 5.0, "color": AMBER, "label": "WIND ASSUMED"},
  labels=[lb(offp(MID, 14, 0), "ABOUT 85 KM", a + 1.8, WHITE), lb(offp(BURST, 30, 22), "LITTLE LOCAL FALLOUT", W("p37", "little"), AMBER), lb(offp(BURST, 30, -22), "LITTLE MATERIAL LIFTED", W("p37", "material"), WHITE)])

# ================================================================== Chapter 06 [SIMULATION]
a = chapter("c6-card", S("p38"), 3.7, "CHAPTER 06", "The day after", "SIMULATION")
b = S("p39")
R("c6-why", a, b, ZP(a, b, [([145.8, 43.4], 700), ([145.2, 43.2], 1400), ([144.0, 43.8], 800)]), **DAY(8, "THE DAY AFTER"), highlight=HL, legend=LEG, burst={"at": BURST, "t": a - 5, "km": 6, "fade": 12},
  cities=[mk(NEM, "NEMURO", a + 0.5, BLUE, "dot", 7), mk(BURST, "THE SHIPS", a + 0.3, RED, "ring", 7)],
  labels=[lb([148.0, 44.2], "WHY A FLEET, NOT A CITY?", W("p38", "fleet"), YELLOW), lb([148.2, 41.4], "A SIGNAL: OUR READING", W("p38", "signal"), WHITE), lb([147.8, 43.0], "IT SAYS: WE CAN", W("p38", "can"), RED),
          lb([143.0, 43.3], "A CITY WOULD SAY MORE", W("p38", "city", 2), WHITE), lb([142.5, 44.7], "NO PUBLISHED COUNT: NONE GIVEN", W("p38", "count"), YELLOW)])
a, b = S("p39"), S("p40")
R("c6-plume", a, b, ZM(a, b, [147.5, 43.0], 600, [149.5, 43.2], 1200), **DAY(8, "THE PLUME"), highlight=HL, legend=LEG, burst={"at": BURST, "t": a - 5, "km": 4, "fade": 12},
  plume={"at": BURST, "bearing": 90, "lengthKm": 220, "widthKm": 14, "t0": W("p39", "plume"), "t1": W("p39", "plume") + 4.0, "color": AMBER, "label": "ASSUMED WIND: FROM THE WEST"},
  labels=[lb([144.0, 44.0], "AWAY FROM HOKKAIDO", W("p39", "away"), BLUE), lb([151.0, 42.0], "OPEN PACIFIC", W("p39", "open"), WHITE)])
a, b = S("p40"), S("p41")
HOKZ = [[139.3, 45.8], [142.5, 46.2], [146.6, 44.6], [146.4, 42.2], [143.0, 41.2], [139.8, 41.0]]
SY = W("p40", "Soya")
R("c6-routes", a, b, ZP(a, b, [([143.0, 43.8], 1200), ([143.0, 43.8], 1700), ([137.5, 44.5], 1500), ([140.0, 45.2], 900), (SOYA, 500)]), **DAY(8, "SHIPPING AND AIR ROUTES"), highlight=HL, legend=LEG,
  zones=[zn(HOKZ, W("p40", "shipping"), WHITE, "ROUTES AROUND HOKKAIDO CLOSE", 0.10, True), zn([[141.5, 45.3], [142.4, 45.3], [142.4, 45.9], [141.5, 45.9]], W("p40", "map"), WHITE, "THE STRAIT GOES DARK", 0.4, False, 2.4, True)],
  ships=[ship([VLA, [137.0, 44.5], [141.0, 45.6], [144.5, 46.2]], SY + 0.2, SY + 7.5, "pla", AMBER, "RUSSIAN SHIPS FROM VLADIVOSTOK", 22)], cities=[mk(SOYA, "SOYA STRAIT: ABOUT 42 KM", W("p40", "forty-two"), BLUE, "dot", 8)])
a, b = S("p41"), S("p42")
R("c6-gas", a, b, ZM(a, b, [141.0, 40.5], 2200, [141.5, 42.0], 1500), **DAY(8, "THE GAS"), highlight=HL, legend=LEG, source="ZOiS Berlin; Lowy Interpreter",
  cities=[mk(SAK2, "SAKHALIN-2", W("p41", "Sakhalin-2"), AMBER, "base", 8), mk(TKY, "TOKYO REVIEWS THE SUPPLY", W("p41", "reviews"), BLUE, "dot", 8)],
  lines=[ln(SAK2, TKY, W("p41", "supplies"), W("p41", "supplies") + 3.0, AMBER, "ABOUT A TENTH OF JAPAN'S LNG", False, 3)], labels=[lb([144.5, 39.5], "MITSUI AND MITSUBISHI", W("p41", "trading"), WHITE)])
a, b = S("p42"), S("p43")
R("c6-nonuc", a, b, ZP(a, b, [([139.5, 37.5], 2000), ([139.7, 36.0], 1300), ([140.5, 38.0], 2200)]), **DAY(8, "THE DEBATE"), highlight=HL, legend=LEG, source="Nippon.com; Lowy Interpreter",
  cities=[mk(TKY, "TOKYO", a + 0.3, BLUE, "dot", 8)], labels=[lb([141.5, 38.6], "NO POSSESSING", W("p42", "possessing"), BLUE), lb([141.5, 37.7], "NO MAKING", W("p42", "making"), BLUE), lb([141.5, 36.8], "NO INTRODUCING", W("p42", "introducing"), BLUE),
          lb([136.5, 39.8], "THREE PRINCIPLES SINCE 1967", W("p42", "three"), WHITE), lb([137.5, 38.4], "SECURITY DOCUMENTS REWRITTEN", W("p42", "rewriting"), WHITE), lb([141.0, 34.9], "REOPENED IN PUBLIC", W("p42", "reopened"), YELLOW)])
a, b = S("p43"), S("p44")
R("c6-options", a, b, ZP(a, b, [([142.0, 38.5], 2600), ([143.5, 40.0], 2000), ([145.0, 42.5], 1100)]), **DAY(8, "THE DECISION"), highlight=HL, legend=LEG, cities=[mk(TKY, "TOKYO AND WASHINGTON CHOOSE", a + 0.3, BLUE, "dot", 8), mk(BURST, None, a + 0.3, RED, "ring", 7)],
  labels=[lb([147.0, 41.0], "OPTION 1: CONVENTIONAL REPLY", W("p43", "conventional"), BLUE), lb([147.0, 39.6], "OPTION 2: NUCLEAR UMBRELLA", W("p43", "umbrella"), BLUE), lb([147.0, 38.2], "OPTION 3: A THIRD-PARTY CALL", W("p43", "call"), BLUE),
          lb([147.5, 44.2], "ANALYSIS LEANS CONVENTIONAL", W("p43", "leans"), WHITE), lb([147.8, 41.5], "ALL THREE SHOWN, THEN IT STOPS", W("p43", "shows"), YELLOW)])
a, b = S("p44"), S("p45")
R("c6-empty", a, b, ZP(a, b, [(SOYA, 500), ([143.5, 44.0], 1500), ([145.0, 43.8], 1000), ([146.0, 44.3], 600)]), **DAY(8, "THE DAY AFTER"), highlight=HL, legend=LEG, zones=[zn([[141.5, 45.3], [142.4, 45.3], [142.4, 45.9], [141.5, 45.9]], a + 0.2, WHITE, "THE STRAIT IS EMPTY", 0.4, False, 2.4, True)],
  rings=[rg(BURST, FX["psi1_km"], a + 1.0, TEAL, None, True)], labels=[lb([146.5, 41.9], "THE RINGS FADE", W("p44", "rings"), TEAL), lb([146.5, 45.5], "IT HAS NOT HAPPENED", W("p44", "None"), YELLOW),
  lb([147.6, 44.8], "THE ISLANDS: REAL", W("p44", "islands"), AMBER), lb([144.0, 43.2], "THE MISSING TREATY: REAL", W("p44", "treaty"), WHITE)])

# ------------------------------------------------------------------ End slate
add(id="end", type="endslate", start=round(S("p45"), 3), end=END, tag="", title="Next scenario", line="Tsar Bomba, the largest bomb ever built, on London, Tokyo and New York.")

# ------------------------------------------------------------------ audio plan and output
b0 = max(0.0, round(min(FL - 0.3, W("p02", "simulation") - 0.3), 2))
booms = [round(FL + 0.1, 2), round(S("p32") + 3.7 + 0.15, 2), round(W("p35", "light") + 0.1, 2)]
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.5, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p19") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p19") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
