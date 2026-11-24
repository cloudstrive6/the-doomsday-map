"""Director pass for episode 017 (rework of dropped 007): builds episode.json from narration/timing.json, words.json and
scenario.computed.json.

Run from the studio root:  python -m studio shotlist 017-carrier-group-nuke-at-sea

Design rules that answer the 007 failures (tiny subject on black, 60% near-still, frozen holds, 5.6 s opening holds):
- The group is drawn as a ring formation (carrier at the centre, six escorts on a 2.5 km hexagon, supply ship inside) and the
  camera sits at 8 to 24 km wide, so the formation fills about a third of the frame; wide shots are short.
- Open sea has no coast, so every region shot carries its own km grid (lines) that moves with the camera.
- Every shot has two or more moving camera keys; something new arrives at least every 4 s to 90 s and every 6 s after.
- No real ship, country or date is named. Icons are enlarged and labelled as such.
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
GRAYBLUE = "#9FB4C9"
DIM = "rgba(236,239,242,0.95)"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round((WORDS[-1]["end"] if WORDS else TOTAL) + 10, 2)


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    cand = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()]
    if len(cand) < nth:
        raise SystemExit(f"W: no word {word!r} #{nth} in {pid}: {[h['word'] for h in WORDS if h['unit'] == pid][:80]}")
    idx = cand[nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


ST = sc["strikes"][0]
FX = ST["effects"]
B = [ST["target_lon"], ST["target_lat"]]       # burst point over the escort nearest the attacker (simulated)
SUBP = [ST["launch_lon"], ST["launch_lat"]]    # attacker's submarine (simulated)
KX, KY = 101.7, 110.57                         # km per degree at 24 N
DIST = ST["distance_km"]                       # 284.4 km


def K(dx, dy, at=None):
    at = at or B
    return [round(at[0] + dx / KX, 5), round(at[1] + dy / KY, 5)]


def L(a, t):
    """shot-local time for an absolute time (never 0, so the item arrives after the cut)"""
    return round(max(0.05, t - a), 2)


shots = []


def add(**k):
    shots.append(k)


# ------------------------------------------------------------------ the generic group (km from the burst point)
H3 = 1.25 * math.sqrt(3)  # 2.165
OFF = {"E0": (0.0, 0.0), "CV": (-2.5, 0.0), "E1": (-1.25, H3), "E2": (-3.75, H3), "E3": (-5.0, 0.0), "E4": (-3.75, -H3), "E5": (-1.25, -H3), "AO": (-3.5, 0.0)}
ALL = list(OFF)
SURVIVORS = [n for n in ALL if n != "E0"]
CVC = K(*OFF["CV"])
GROUP_C = K(-2.5, 0.0)


def sizes(w):
    f = (14.0 / w) ** 0.6
    return {"CV": min(max(40 * f, 16), 90), "E": min(max(26 * f, 11), 56), "AO": min(max(30 * f, 13), 62)}


def hull(a, b, n, w, label=None, t=None, drift=(0.08, 0.0), sunk=None, color=BLUE, path=None, size=None):
    dx, dy = OFF[n]
    s = sizes(w)["CV" if n == "CV" else "AO" if n == "AO" else "E"]
    p = path or [K(dx, dy), K(dx + drift[0], dy + drift[1])]
    d = {"path": p, "t0": 0, "t1": round(b - a, 2), "kind": "us", "color": color, "size": size or round(s), "wake": False}
    if t is not None:
        d["t"] = L(a, t)
    if label:
        d["label"] = label
    if sunk is not None:
        d["sunkAt"] = L(a, sunk)
    return d


def fleet(a, b, w, names=None, labels=None, times=None, sunk=None, drift=(0.08, 0.0), colors=None, paths=None, size=None):
    names = names or ALL
    labels, times, sunk, colors, paths = labels or {}, times or {}, sunk or {}, colors or {}, paths or {}
    return [hull(a, b, n, w, label=labels.get(n), t=times.get(n), sunk=sunk.get(n), drift=drift, color=colors.get(n, BLUE), path=paths.get(n), size=size) for n in names]


def missile(a, b, path, label="MISSILE", t=None, size=26, t0=0.0):
    d = {"path": path, "t0": t0, "t1": round(b - a, 2), "kind": "pla", "color": RED, "size": size, "wake": True}
    if label:
        d["label"] = label
    if t is not None:
        d["t"] = L(a, t)
    return d


def jet(a, b, path, t, t0, t1, size=14, color="#CFE3FF", label=None):
    d = {"path": path, "t0": L(a, t0), "t1": L(a, t1), "kind": "ally", "color": color, "size": size, "wake": True, "t": L(a, t)}
    if label:
        d["label"] = label
    return d


CLOSE_APPROACH = [K(10, 7), K(0.0, 0.0)]


def lb(a, dx, dy, text, t, color=WHITE, at=None):
    return {"at": K(dx, dy, at), "text": text, "color": color, "t": L(a, t)}


def mk(a, dx, dy, label, t, color=WHITE, kind="dot", size=5, at=None):
    d = {"at": K(dx, dy, at), "kind": kind, "color": color, "size": size}
    if label:
        d["label"] = label
    if t is not None:
        d["t"] = L(a, t)
    return d


def ln(a, p0, p1, t0, t1, color=WHITE, label=None, dashed=False, width=2):
    d = {"from": p0, "to": p1, "color": color, "dashed": dashed, "t0": L(a, t0), "t1": L(a, t1), "width": width}
    if label:
        d["label"] = label
    return d


# ------------------------------------------------------------------ blast rings from the engine
RINGS = [("FIREBALL", FX["fireball_km"], WHITE), ("20 PSI", FX["psi20_km"], ORANGE), ("5 PSI", FX["psi5_km"], RED),
         ("BURNS", FX["thermal3_km"], AMBER), ("1 PSI", FX["psi1_km"], TEAL)]
ENG = "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"


def ring(i, a, t, label=None, dashed=True, at=None, km=None):
    nm, k, col = RINGS[i]
    d = {"at": at or B, "km": km or k, "color": col, "t": L(a, t)}
    if label is not None:
        d["label"] = label if label else nm
    if not dashed:
        d["dashed"] = False
    return d


def disc(km, a, t, color=WHITE, label=None, fill=0.35, at=None):
    at = at or B
    pts = [K(km * math.cos(math.radians(d)), km * math.sin(math.radians(d)), at) for d in range(0, 360, 12)]
    z = {"points": pts, "color": color, "t": L(a, t), "fillOpacity": fill, "strokeWidth": 2.4, "solid": True}
    if label:
        z["label"] = label
    return z


def deck_zone(color=BLUE, fill=0.30):
    """the carrier hull at true scale (333 m by about 75 m), bow to the east, centred on the carrier"""
    pts = [(0.1665, 0.0), (0.14, 0.03), (0.10, 0.038), (-0.15, 0.038), (-0.1665, 0.02), (-0.1665, -0.02), (-0.15, -0.038), (0.10, -0.038), (0.14, -0.03)]
    return {"points": [K(-2.5 + x, y) for x, y in pts], "color": color, "fillOpacity": fill, "strokeWidth": 2.6, "solid": True, "_deck": True}


# ------------------------------------------------------------------ story clock (minutes since launch), anchored on the narration
ANCH = [(S("p21") + 0.0, 0.0), (S("p22") + 0.4, 8.0), (S("p23") + 0.2, 12.0), (S("p24") + 0.4, 17.0), (W("p25", "bursts") + 0.1, ST["flight_min"]),
        (S("p34"), 20.4), (S("p35"), 22.0), (S("p36"), 30.0), (S("p37"), 45.0), (S("p38"), 60.0), (S("p39"), 75.0), (S("p40"), 80.0)]


def mm(t):
    if t <= ANCH[0][0]:
        return 0.0
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if t <= t1:
            return m0 + (m1 - m0) * (t - t0) / (t1 - t0)
    return ANCH[-1][1]


def clk(a, b, label="SINCE LAUNCH"):
    m0, m1 = mm(a), mm(b)
    sec = int(round(m0 * 60))
    return {"clock": f"T+{sec // 60:02d}:{sec % 60:02d}", "clockLabel": label, "clockRate": round(max(0.0, (m1 - m0) * 60 / (b - a)), 2)}


def xm(m):
    """east-west km of the missile from the burst point, m minutes after launch"""
    return round(-DIST * (1 - m / ST["flight_min"]), 2)


def mpath(a, b):
    return [K(xm(mm(a)), 0), K(xm(mm(b)), 0)]


# ------------------------------------------------------------------ camera and grid helpers
def lt(a, b, t):
    if t == "s":
        return 0.0
    if t == "e":
        return round(b - a, 2)
    return round(t - a, 2)


def to_km(c):
    return ((c[0] - B[0]) * KX, (c[1] - B[1]) * KY)


def nice_step(x):
    for s in (0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100, 200):
        if s >= x:
            return s
    return 500


def grid_lines(keys):
    maxw = max(k["widthKm"] for k in keys)
    step = nice_step(maxw / 12.0)
    cs = [to_km(k["center"]) for k in keys]
    hx, hy = maxw * 0.5 * 1.45 + maxw * 0.1, maxw * 0.5625 * 0.5 * 1.45
    x0 = math.floor((min(c[0] for c in cs) - hx) / step) * step
    x1 = math.ceil((max(c[0] for c in cs) + hx) / step) * step
    y0 = math.floor((min(c[1] for c in cs) - hy) / step) * step
    y1 = math.ceil((max(c[1] for c in cs) + hy) / step) * step
    out = []
    col = "rgba(140,190,220,0.27)"
    n = 0
    x = x0
    while x <= x1 + 1e-9 and n < 60:
        out.append({"from": K(x, y0), "to": K(x, y1), "color": col, "width": 1})
        x += step
        n += 1
    y = y0
    while y <= y1 + 1e-9 and n < 90:
        out.append({"from": K(x0, y), "to": K(x1, y), "color": col, "width": 1})
        y += step
        n += 1
    return out, step, maxw


def bar(a, p, q, t, color=WHITE, w=0.004, fill=0.9):
    """a thin filled bar between two km offsets from the burst point (lines under about 1 km do not draw in the engine)"""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n * w / 2, dx / n * w / 2
    z = {"points": [K(x0 + nx, y0 + ny), K(x1 + nx, y1 + ny), K(x1 - nx, y1 - ny), K(x0 - nx, y0 - ny)], "color": color, "fillOpacity": fill, "strokeWidth": 1, "solid": True}
    if t is not None:
        z["t"] = L(a, t)
    return z


WIDE_IDS = {"c1-miles", "run-contact", "run-warning", "c3-sub", "c3-dist", "c3-one", "c3-phone", "c4-sub", "c4-m8", "c6-out", "c6-doctrine", "c6-spread", "c6-message", "c6-choice", "c6-undecided"}


def deck_details():
    """flight deck markings at true scale: centre line, angled landing area, catapult tracks, island"""
    zs = [bar(0, (-2.65, 0.0), (-2.36, 0.0), None, "#FFFFFF", 0.004, 0.55),
          bar(0, (-2.65, -0.03), (-2.52, 0.027), None, "#FFD23F", 0.003, 0.85), bar(0, (-2.65, -0.012), (-2.46, 0.035), None, "#FFD23F", 0.003, 0.85),
          bar(0, (-2.52, -0.01), (-2.37, -0.01), None, "#FFFFFF", 0.006, 0.7), bar(0, (-2.52, 0.012), (-2.37, 0.012), None, "#FFFFFF", 0.006, 0.7)]
    isl = {"points": [K(-2.5 - 0.02 + x, y) for x, y in [(0, -0.026), (0.06, -0.026), (0.06, -0.038), (0, -0.038)]], "color": "#CFE3FF", "fillOpacity": 0.7, "strokeWidth": 1.5, "solid": True}
    return zs, isl


def R(sid, a, b, keys, tag="SIMULATION", grid=True, **kw):
    ks = [{"t": lt(a, b, t), "center": c, "widthKm": w} for t, c, w in keys]
    d = dict(id=sid, type="region", start=round(a, 3), end=round(b, 3), tag=tag, view={"center": ks[0]["center"], "widthKm": ks[0]["widthKm"]}, camera=ks)
    if grid:
        g, step, maxw = grid_lines(ks)
        d["lines"] = g + kw.pop("lines", [])
        if maxw < 30:
            d["scaleBar"] = False
            leg = list(kw.pop("legend", []))
            leg.append({"text": f"GRID {step:g} KM", "color": "rgba(140,190,220,0.9)"})
            d["legend"] = leg
    zx = kw.pop("zones_extra", [])
    d.update(kw)
    if zx:
        d["zones"] = d.get("zones", []) + zx
    zs = d.get("zones", [])
    if any(z.get("_deck") for z in zs):
        extra, isl = deck_details()
        d["zones"] = zs + extra + [isl]
        for z in zs:
            z.pop("_deck", None)
    us = [x for x in d.get("ships", []) if x.get("kind") == "us" and x.get("size", 0) < 80]
    maxw_ = max(k["widthKm"] for k in ks)
    if len(us) >= 6 and 6 <= maxw_ <= 70 and kw.get("hexa", True) and tag in ("SIMULATION", "REAL DATA"):
        hexz = {"points": [K(*OFF[n]) for n in ["E0", "E1", "E2", "E3", "E4", "E5"]], "color": BLUE, "fillOpacity": 0.05, "strokeWidth": 1.8, "solid": False}
        d["zones"] = d.get("zones", []) + [hexz]
        sp = [{"from": K(*OFF["CV"]), "to": K(*OFF[n]), "color": "rgba(110,168,255,0.38)", "width": 1.5, "dashed": True} for n in ["E0", "E1", "E2", "E3", "E4", "E5"]]
        d["lines"] = d.get("lines", []) + sp
        if "rings" not in kw and maxw_ >= 9:
            d["rings"] = [{"at": K(*OFF["CV"]), "km": 2.5 * i, "color": BLUE, "dashed": True} for i in (2, 3, 4) if 2.5 * i < maxw_ * 0.5]
    d.pop("hexa", None)
    if sid in WIDE_IDS:
        r = max(2.2, min(maxw_ / 45.0, 5.0))
        d["zones"] = d.get("zones", []) + [{"points": [K(-2.5 + r * math.cos(math.radians(x)), r * math.sin(math.radians(x))) for x in range(0, 360, 15)], "color": BLUE, "fillOpacity": 0.5, "strokeWidth": 2.4, "solid": True}]
        if "rings" not in kw:
            st = nice_step(maxw_ / 5.0)
            d["rings"] = [{"at": CVC, "km": st * i, "color": BLUE, "dashed": True} for i in range(1, 6) if st * i < maxw_ * 0.8]
    add(**d)


def G(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=round(a, 3), end=round(b, 3), tag=tag, sun=sun,
        camera=[{"t": lt(a, b, t), "lat": la, "lon": lo, "scale": s} for t, la, lo, s in keys], **kw)


def chapter(sid, a, b, kicker, title, tag):
    add(id=sid, type="chapter", start=round(a, 3), end=round(b, 3), tag=tag, kicker=kicker, title=title)


V = lambda dx, dy: K(dx, dy)  # noqa: E731
USLEG = [{"text": "US GROUP, ICONS ENLARGED", "color": BLUE}]
GEN = [{"text": "GENERIC GROUP, ICONS ENLARGED", "color": BLUE}]
BN = lambda t: K(*OFF["CV"], at=None)  # noqa: E731

# ================================================================== Cold open [SIMULATION]
FL = 3.6                                   # the flash lands on the spoken "bursts"
R("open-group", 0.0, FL, [(0, K(-1.6, 0.5), 17), (FL - 0.2, K(-1.0, 0.3), 10.5)], clock="00:30", clockLabel="LOCAL · OPEN PACIFIC",
  ships=fleet(0, FL, 13, labels={"CV": "CARRIER"}) + [missile(0, FL, [K(8.2, 4.4), K(0.9, 0.6)], label=None, t=0.9, t0=0.9)],
  cities=[mk(0, -2.5, 3.6, "US CARRIER GROUP", None, BLUE, "dot", 3)], labels=[lb(0, 0.5, 2.2, "ONE MISSILE, LOW AND FAST", 2.0, RED)], legend=USLEG)
R("open-flash", FL, 8.0, [(FL, K(-1.0, 0.2), 9), (FL + 1.6, K(-1.0, 0.0), 13), (FL + 3.0, K(-1.2, 0.0), 19)], clock="T+20:06", clockLabel="THE BURST", caption="Simulation: it has not happened.",
  burst={"at": B, "t": 0.1, "km": 0.9, "fade": 6}, ships=fleet(FL, 8.0, 13, names=ALL, sunk={"E0": FL + 0.5}),
  rings=[ring(2, FL, FL + 1.0, "5 PSI"), ring(4, FL, FL + 2.2, "1 PSI")], legend=USLEG)
R("open-wide", 8.0, S("p03"), [(8.0, K(-1.5, 0.0), 22), (10.2, K(-1.5, 0.0), 44)], clock="T+20:30", clockLabel="AFTER THE BURST",
  burst={"at": B, "t": -4.5, "km": 0.9, "fade": 7}, ships=fleet(8.0, S("p03"), 22, names=SURVIVORS), rings=[ring(2, 8.0, -30, ""), ring(4, 8.0, -30, "")],
  labels=[lb(8.0, -1.5, 3.4, "BUILT FROM PUBLISHED NUMBERS", W("p02", "published"), WHITE), lb(8.0, -1.5, -3.6, "IT HAS NOT HAPPENED", W("p02", "has"), YELLOW)], legend=USLEG)

# run-up: twelve minutes earlier, the contact (clock counts the warning down)
RUN0, RUN_RATE = S("p03"), 24.0


def runclk(a):
    rem = 12.1 * 60 - (a - RUN0) * RUN_RATE
    rem = max(rem, 5)
    return {"clock": f"T-{int(rem) // 60:02d}:{int(rem) % 60:02d}", "clockLabel": "UNTIL THE BURST", "clockRate": RUN_RATE}


def runx(t):
    return xm(8.0 + (t - RUN0) * RUN_RATE / 60.0)


tMarks = W("p03", "contact")
add_t = S("p03")
R("run-quiet", add_t, tMarks, [(add_t, K(-2.5, 0), 34), (tMarks, K(-2.5, 0), 20)], caption="Twelve minutes earlier.", **runclk(add_t),
  ships=fleet(add_t, tMarks, 26, names=ALL, labels={"CV": "CARRIER"}), cities=[mk(add_t, -2.5, 6.5, "ROUTINE NIGHT AT SEA", add_t + 1.0, BLUE, "dot", 3)], legend=USLEG)
tToo = W("p03", "too")
tToo2 = W("p03", "too", 2)
tNob = W("p03", "Nobody")
R("run-contact", tMarks, tNob, [(tMarks, K(-85, 6), 200), (tToo, K(-75, 3), 160), (tToo2 + 0.3, K(-55, 2), 110)], **runclk(tMarks),
  ships=[missile(tMarks, tNob, [K(runx(tMarks), 0), K(runx(tNob), 0)], "CONTACT", t=tMarks + 0.1)], cities=[mk(tMarks, -2.5, 0, None, tMarks + 0.4, BLUE, "ring", 8)],
  caption="A contact, low over the water. Too small for an airliner. Too fast for a ship.",
  labels=[lb(tMarks, -2.5 - 22, -16, "US CARRIER GROUP", tMarks + 0.4, "#CFE3FF"), lb(tMarks, runx(tMarks) + 12, 18, "LOW OVER THE WATER", W("p03", "low"), RED), lb(tMarks, runx(tToo) + 10, -20, "TOO SMALL FOR AN AIRLINER", tToo + 0.1, WHITE), lb(tMarks, runx(tToo2) + 10, 20, "TOO FAST FOR A SHIP", tToo2, RED)])
tDeck = W("p03", "deck")
R("run-years", tNob, tDeck, [(tNob, K(-2.5, 0), 18), (tDeck - 0.3, K(-2.5, 0), 28)], **runclk(tNob), ships=fleet(tNob, tDeck, 22, labels={"CV": "CARRIER"}),
  labels=[lb(tNob, -2.5, 4.2, "NOBODY HAS FIRED ON THIS GROUP IN YEARS", tNob + 0.4, YELLOW)], legend=USLEG)
R("run-deck", tDeck, S("p04"), [(tDeck, K(-2.5, 0), 3.2), (tDeck + 2.6, K(-2.3, 0), 1.7)], **runclk(tDeck), zones=[deck_zone()],
  ships=[jet(tDeck, S("p04"), [K(-2.45, 0.0), K(2.5, 0.2)], tDeck + 0.6, tDeck + 0.6, tDeck + 3.2), jet(tDeck, S("p04"), [K(-2.5, 0.0), K(2.5, -0.2)], W("p03", "loading") + 1.4, W("p03", "loading") + 1.4, W("p03", "loading") + 4.4)],
  labels=[lb(tDeck, -2.5, -0.25, "LOADING JETS FOR A ROUTINE NIGHT LAUNCH", tDeck + 0.5, WHITE), lb(tDeck, -2.7, 0.3, "THE WATCH IS QUIET", W("p03", "watch"), BLUE)])
t4q = W("p04", "question")
R("run-warning", S("p04"), t4q, [(S("p04"), K(-100, 0), 230), (t4q - 0.4, K(-50, 0), 130)], **runclk(S("p04")), caption="Twelve minutes is all the warning there is.",
  ships=[missile(S("p04"), t4q, [K(runx(S("p04")), 0), K(runx(t4q), 0)], "MISSILE", t=S("p04"))], cities=[mk(S("p04"), -2.5, 0, None, S("p04") + 0.5, BLUE, "ring", 8)],
  lines=[ln(S("p04"), K(-DIST, 0), K(-4, 0), S("p04") + 0.3, S("p04") + 2.0, RED, dashed=True)], labels=[lb(S("p04"), -DIST + 30, 14, "ABOUT 12 MINUTES TO IMPACT", W("p04", "all"), RED), lb(S("p04"), -2.5 - 20, -14, "US CARRIER GROUP", S("p04") + 0.5, "#CFE3FF")])
t4c = W("p04", "crew")
G("run-question", t4q, t4c, [(t4q, 40, 150, 700), (t4c - 0.4, 28, 154, 1500)], clock="", caption="What the crew would face in the first minute.",
  markers=[{"at": B, "label": "OPEN PACIFIC (SIMULATED)", "color": RED, "kind": "target", "t": 0.6}])
t4w = W("p04", "what")
R("run-who", t4c, S("p05"), [(t4c, K(-2.5, 0), 26), (t4w, K(-2.5, 0), 16), (S("p05") - 0.5, K(-2.5, 0), 11)], **runclk(t4c), ships=fleet(t4c, S("p05"), 16, labels={"CV": "CARRIER"}),
  caption="What does a carrier group do when nobody knows who fired?", cities=[mk(t4c, -2.5, 5.0, "WHO FIRED?", t4w, RED, "ring", 6), mk(t4c, -8.0, 1.5, "NO FLAG", W("p04", "nobody"), RED, "ring", 5), mk(t4c, 4.0, -1.5, "NO COUNTRY", W("p04", "knows"), RED, "ring", 5)], legend=USLEG)

# ================================================================== Chapter 01: a city on the water [REAL DATA]
a = S("p05")
chapter("c1-card", a, a + 3.75, "CHAPTER 01", "A city on the water", "REAL DATA")
a += 3.75
SRC_SH = "Nimitz-class carrier specifications (public reference)"
tHull = S("p06")
R("c1-deck", a, W("p05", "red"), [(a, K(-2.5, 0), 0.95), (a + 3.0, K(-2.2, 0), 0.65)], tag="REAL DATA", zones=[deck_zone()],
  ships=[jet(a, W("p05", "red"), [K(-2.5, 0.0), K(1.6, 0.25)], a + 0.4, a + 0.4, a + 2.9), jet(a, W("p05", "red"), [K(-2.6, 0.0), K(1.6, -0.25)], a + 1.5, a + 1.5, a + 3.4)],
  labels=[lb(a, -2.2, 0.2, "JETS LAUNCH OFF THE BOW", W("p05", "Jets") + 0.9, WHITE), lb(a, -2.5, -0.2, "A FLIGHT DECK AT NIGHT", a + 0.2, DIM)], source=SRC_SH)
tR = W("p05", "red")
crew_cols = ["#F2D13B", "#4FD66A", "#FF4B4B", "#B98A5A", "#F2F2F2", "#B66BFF"]
R("c1-crew", tR - 0.0, S("p06"), [(tR, K(-2.5, 0), 0.7), (tR + 2.0, K(-2.5, 0), 1.2), (S("p06") - 0.4, K(-2.4, 0), 1.9)], tag="REAL DATA",
  zones=[deck_zone()] + [bar(tR, (-2.05 + 0.25 * (i % 2), -0.14 + 0.07 * i), (-2.3 + 0.25 * (i % 2), -0.14 + 0.07 * i), W("p05", "wind") + 0.12 * i, TEAL, 0.004, 0.8) for i in range(5)],
  cities=[mk(tR, -2.5 + dx, dy, None, tR + 0.3 + 0.25 * i, crew_cols[i % 6], "dot", 5) for i, (dx, dy) in enumerate([(-0.1, 0.02), (-0.04, -0.02), (0.02, 0.025), (0.07, -0.015), (0.11, 0.01), (-0.13, -0.01)])],
  labels=[lb(tR, -2.5, 0.15, "CREW IN COLORED SHIRTS", W("p05", "colored") + 0.2, WHITE), lb(tR, -2.5, -0.17, "RED LIGHTS", tR + 0.5, RED), lb(tR, -2.5, 0.28, "WIND THAT NEVER STOPS", W("p05", "wind"), TEAL)],
  source=SRC_SH)
a = S("p06")
tFeet = W("p06", "thousand")
R("c1-len", a, W("p06", "weighs"), [(a, K(-2.5, 0), 0.9), (a + 1.8, K(-2.5, 0), 0.6), (W("p06", "weighs") - 0.4, K(-2.5, 0), 1.1)], tag="REAL DATA", zones=[deck_zone(fill=0.4)],
  zones_extra=[bar(a, (-2.5 - 0.1665, -0.1), (-2.5 + 0.1665, -0.1), tFeet, YELLOW, 0.006, 0.9), bar(a, (-2.5 - 0.1665, -0.115), (-2.5 - 0.1665, -0.085), tFeet, YELLOW, 0.006, 0.9), bar(a, (-2.5 + 0.1665, -0.115), (-2.5 + 0.1665, -0.085), tFeet, YELLOW, 0.006, 0.9)],
  labels=[lb(a, -2.5, -0.17, "OVER 1,000 FT, ABOUT 330 M", tFeet + 0.4, YELLOW)], source=SRC_SH)
tW = W("p06", "weighs")
add(id="c1-tons", type="number", start=round(tW, 3), end=round(W("p06", "Two"), 3), tag="REAL DATA", value="ABOUT 100,000", countTo=100000, prefix="ABOUT ", label="tons, fully loaded", color=BLUE, source=SRC_SH)
tTwo = W("p06", "Two")
R("c1-reactors", tTwo, W("p06", "About", 2), [(tTwo, K(-2.5, 0), 0.7), (tTwo + 1.6, K(-2.55, 0), 1.0), (W("p06", "About", 2) - 0.3, K(-2.55, 0), 1.4)], tag="REAL DATA", zones=[deck_zone(fill=0.25)],
  cities=[mk(tTwo, -2.62, 0.0, "REACTOR", tTwo + 0.3, ORANGE, "base", 6), mk(tTwo, -2.55, -0.02, "REACTOR", tTwo + 1.4, ORANGE, "base", 6)],
  caption="Two nuclear reactors drive it. Positions are illustrative.", source=SRC_SH)
tAbout = W("p06", "About", 2)
people = [(-0.14 + 0.028 * (i % 10), 0.05 * ((i // 10) - 1) + 0.01 * (i % 3)) for i in range(30)]
R("c1-people", tAbout, W("p06", "small"), [(tAbout, K(-2.5, 0), 0.8), (tAbout + 1.4, K(-2.5, 0), 1.2), (W("p06", "small") - 0.3, K(-2.5, 0), 1.6)], tag="REAL DATA", zones=[deck_zone(fill=0.25)],
  cities=[mk(tAbout, -2.5 + dx, dy, None, tAbout + 0.4 + 0.07 * i, "#F2F2F2", "dot", 3) for i, (dx, dy) in enumerate(people)],
  labels=[lb(tAbout, -2.5, 0.2, "ABOUT 5,000 PEOPLE ABOARD", tAbout + 0.2, WHITE)], source=SRC_SH)
tSm = W("p06", "small")
R("c1-town", tSm, S("p07"), [(tSm, K(-2.5, 0), 1.6), (tSm + 1.6, K(-2.5, 0), 0.8)], tag="REAL DATA", zones=[deck_zone(fill=0.25)],
  zones_extra=[bar(tSm, (-2.62, 0.045), (-2.38, -0.03), tSm + 0.9, WHITE, 0.007, 0.9)],
  labels=[lb(tSm, -2.5, 0.2, "A SMALL TOWN", tSm + 0.2, WHITE), lb(tSm, -2.5, -0.17, "ITS OWN AIRFIELD", tSm + 1.1, YELLOW)], source=SRC_SH)
a = S("p07")
tStars = W("p07", "night")
R("c1-alone", a, tStars + 1.0, [(a, K(-2.5, 0), 18), (a + 2.8, K(-2.5, 0), 12)], tag="REAL DATA", ships=fleet(a, tStars + 1.0, 30, labels={"CV": "CARRIER"}, times={n: a + 0.05 + 0.25 * i for i, n in enumerate(ALL)}),
  caption="It never sails alone.", source="Congressional Research Service IF10486, Navy Carrier Strike Groups")
tStars = tStars + 1.0
tAir = W("p07", "strike")
R("c1-stars", tStars, tAir, [(tStars, K(-2.5, 0), 36), (tStars + 2.4, K(-2.5, 0), 24), (tAir - 0.4, K(-2.5, 0), 30)], tag="REAL DATA", ships=fleet(tStars, tAir, 30, colors={n: "#6E8CB8" for n in ALL}),
  labels=[lb(tStars, -2.5, 6.0, "A SCATTER OF DIM STARS", W("p07", "scatter") + 0.1, "#9FB4D9")], legend=GEN)
tEsc = W("p07", "usually")
aw = [[K(-2.5 + 1.2 * math.cos(math.radians(d)), 1.0 * math.sin(math.radians(d))) for d in range(s0, s0 + 361, 30)] for s0 in (0, 120, 240)]
R("c1-air", tAir, tEsc, [(tAir, K(-2.5, 0), 10), (tAir + 1.8, K(-2.5, 0), 6.5), (tEsc - 0.3, K(-2.5, 0), 8.5)], tag="REAL DATA", ships=[hull(tAir, tEsc, "CV", 7, label="CARRIER")] + [jet(tAir, tEsc, p, tAir + 0.2 + 0.4 * i, tAir + 0.2 + 0.4 * i, tEsc + 3, size=22, label=("AIR WING: 60+ AIRCRAFT" if i == 0 else None)) for i, p in enumerate(aw)],
  rings=[{"at": CVC, "km": 1.0, "color": BLUE, "dashed": True}, {"at": CVC, "km": 2.0, "color": BLUE, "dashed": True}],
  caption="The carrier with its air wing of sixty or more aircraft.", legend=GEN)
tSup = W("p07", "supply")
tSub = W("p07", "sometimes")
tSpread = W("p07", "spread")
SRCC = "Congressional Research Service IF10486, Navy Carrier Strike Groups"
R("c1-escorts", tEsc, tSpread, [(tEsc, K(-2.5, 0), 14), (tEsc + 1.0, K(-2.5, 0), 10), (tSup, K(-2.5, 0), 16), (tSub, K(-2.5, -0.5), 22), (tSpread - 0.3, K(-2.5, -1.0), 26)], tag="REAL DATA",
  ships=fleet(tEsc, tSpread, 14, names=["CV", "E1", "E3", "E5", "AO", "E0", "E2", "E4"], labels={"CV": "CARRIER", "E1": "ESCORT", "E3": "ESCORT", "E5": "ESCORT", "AO": "SUPPLY SHIP"}, times={"E1": tEsc + 0.2, "E3": tEsc + 0.9, "E5": tEsc + 1.6, "AO": tSup, "E0": tSup + 0.3, "E2": tSup + 0.5, "E4": tSup + 0.7})
  + [{"path": [K(-2.5, -2.4), K(-2.4, -2.4)], "t0": 0, "t1": round(tSpread - tEsc, 2), "kind": "us", "color": "#7A8CA6", "size": 16, "label": "SUBMARINE, SOMETIMES", "t": L(tEsc, tSub + 0.1), "wake": False}],
  caption="Usually three to five escorts, a supply ship, and sometimes a submarine.", legend=GEN)
R("c1-miles", tSpread, S("p08"), [(tSpread, K(-2.5, 0), 18), (tSpread + 1.0, K(-2.5, 0), 40), (S("p08") - 0.3, K(-2.5, 0), 80)], tag="REAL DATA",
  ships=fleet(tSpread, S("p08"), 20, labels={"CV": "CARRIER"}), caption="Spread over many miles of sea.", legend=GEN)
a = S("p08")
tOwn = W("p08", "each", 2)
tAny = W("p08", "any")
R("c1-targets", a, tOwn, [(a, K(-2.5, 0), 18), (a + 1.6, K(-2.5, 0), 12), (tOwn - 0.3, K(-2.5, 0), 14)], tag="REAL DATA", ships=fleet(a, tOwn, 14),
  cities=[mk(a, OFF[n][0], OFF[n][1], None, a + 0.4 + 0.3 * i, RED, "ring", 5) for i, n in enumerate(ALL)], caption="Each of those ships is a separate target.", legend=GEN)
tIn = W("p08", "In")
R("c1-distance", tOwn, tIn, [(tOwn, K(-2.5, 0), 14), (tAny, K(-2.0, 0), 16), (tIn - 0.4, K(-2.0, 0), 20)], tag="REAL DATA", ships=fleet(tOwn, tIn, 16),
  cities=[mk(tOwn, 0, 0, "ANY ONE POINT ON THE WATER", tAny, RED, "target", 6)], lines=[ln(tOwn, K(0, 0), K(*OFF[n]), tAny + 0.5 + 0.35 * i, tAny + 1.1 + 0.35 * i, RED, dashed=True, width=2) for i, n in enumerate(["CV", "E1", "E5", "E3"])],
  caption="Each sits at its own distance from any one point.", legend=GEN)
tApart = W("p08", "apart")
hexp = [("E0", "E1"), ("E1", "E2"), ("E2", "E3"), ("E3", "E4"), ("E4", "E5"), ("E5", "E0")]
R("c1-spacing", tIn, S("p09"), [(tIn, K(-2.5, 0), 14), (tApart, K(-2.5, 0), 11), (W("p08", "whole"), K(-2.5, 0), 9)], tag="SIMULATION", ships=fleet(tIn, S("p09"), 11), clock="", clockLabel="",
  lines=[ln(tIn, K(*OFF[p]), K(*OFF[q]), W("p08", "two") + 0.1 * i, W("p08", "two") + 0.1 * i + 0.8, YELLOW, width=2) for i, (p, q) in enumerate(hexp)],
  labels=[lb(tIn, -2.5, 3.0, "ABOUT 2.5 KM APART", W("p08", "half"), YELLOW), lb(tIn, -2.5, -3.0, "THE WHOLE POINT OF THE NEXT FEW MINUTES", W("p08", "whole"), WHITE)], legend=GEN)
a = S("p09")
tFleet = W("p09", "fleet")
G("c1-old", a, tFleet + 1.0, [(a, 24, 155, 950), (tFleet, 17, 160, 1500)], tag="REAL DATA", clock="", caption="What happens to a fleet that is hit by an atomic bomb?",
  markers=[{"at": B, "label": "OUR SIMULATED GROUP", "color": BLUE, "kind": "dot", "t": 0.4}, {"at": [165.5, 11.6], "label": "BIKINI ATOLL", "color": AMBER, "kind": "target", "t": 3.0}])
tAns = W("p09", "answer")
G("c1-tested", tFleet + 1.0, S("p10"), [(tFleet + 1.0, 14, 163, 1800), (tAns, 11.8, 165.2, 3600), (S("p10") - 0.3, 11.6, 165.5, 5200)], tag="REAL DATA", clock="1946", clockLabel="THE NAVY TESTED IT", source="Atomic Archive; Operation Crossroads",
  markers=[{"at": [165.5, 11.6], "label": "BIKINI ATOLL", "color": AMBER, "kind": "target", "t": 0.2}])

# ================================================================== Chapter 02: the test, the brink and the pullback [REAL HISTORY]
BK = [165.5, 11.6]
BKX, BKY = 111.32 * math.cos(math.radians(11.6)), 110.6


def KB(dx, dy):
    return [round(BK[0] + dx / BKX, 5), round(BK[1] + dy / BKY, 5)]


a = S("p10")
chapter("c2-card", a, a + 3.7, "CHAPTER 02", "The test, the brink and the pullback", "REAL HISTORY")
a += 3.7
LAG = [KB(18 * math.cos(math.radians(d)), 8.5 * math.sin(math.radians(d))) for d in range(0, 360, 12)]
TARGETS = []
for gx in range(-16, 17, 3):
    for gy in range(-8, 9, 3):
        if (gx / 17.0) ** 2 + (gy / 8.2) ** 2 <= 1.0:
            TARGETS.append((gx + (0.4 if gy % 6 == 0 else -0.4), gy))
TARGETS = TARGETS[:90]


def lagoon(a, b, names=None, sunk=None, w=36, size=9, times=None, colors=None):
    sunk, times, colors = sunk or {}, times or {}, colors or {}
    out = []
    for i, (gx, gy) in enumerate(TARGETS):
        if names is not None and i not in names:
            continue
        d = {"path": [KB(gx, gy), KB(gx + 0.06, gy)], "t0": 0, "t1": round(b - a, 2), "kind": "ally", "color": colors.get(i, GRAYBLUE), "size": size, "wake": False}
        if i in times:
            d["t"] = L(a, times[i])
        if i in sunk:
            d["sunkAt"] = L(a, sunk[i])
        out.append(d)
    return out


LAGZ = {"points": LAG, "color": "#8FA6BF", "fillOpacity": 0.07, "strokeWidth": 1.6, "solid": False}
SRC_BK = "Atomic Archive; nuclearweaponarchive.org (Operation Crossroads)"
tShips = W("p10", "ninety")
R("c2-lagoon", a, W("p10", "detonated"), [(a, KB(0, 0), 70), (a + 2.0, KB(0, 0), 46), (W("p10", "detonated") - 0.3, KB(0, 0), 40)], tag="REAL HISTORY", clock="1946", clockLabel="BIKINI ATOLL", zones=[LAGZ],
  ships=lagoon(a, W("p10", "detonated"), times={i: tShips - 0.2 + 0.03 * i for i in range(len(TARGETS))}), labels=[lb(a, 0, 0, "ABOUT 90 SURPLUS AND CAPTURED SHIPS", tShips + 0.2, WHITE, at=BK)], source=SRC_BK)
tDet = W("p10", "detonated")
tFirst = W("p10", "first")
R("c2-two", tDet, tFirst, [(tDet, KB(0, 0), 40), (tDet + 1.6, KB(0, 0), 52), (tFirst - 0.2, KB(0, 0), 44)], tag="REAL HISTORY", clock="1946", clockLabel="TWO BOMBS", zones=[LAGZ],
  ships=lagoon(tDet, tFirst), cities=[mk(tDet, -5, 3, "BOMB ONE: AIR", tDet + 0.3, RED, "target", 6, at=BK), mk(tDet, 5, -3, "BOMB TWO: WATER", W("p10", "bombs") + 0.5, ORANGE, "target", 6, at=BK)],
  caption="Two bombs of about 23 kilotons each.", source=SRC_BK)
tMiss = W("p10", "missed")
tFive = W("p10", "five")
AIM, HIT = KB(0, 0), KB(0.65, 0.0)
R("c2-able", tFirst, tFive, [(tFirst, KB(0, 0), 26), (tMiss, KB(0.3, 0), 14), (tFive - 0.4, KB(0.3, 0), 9)], tag="REAL HISTORY", clock="1946", clockLabel="ABLE · AIR BURST", zones=[], burst={"at": HIT, "t": L(tFirst, W("p10", "air")), "km": 0.5, "fade": 5},
  ships=lagoon(tFirst, tFive, size=12), cities=[{"at": AIM, "color": WHITE, "kind": "target", "size": 6, "t": L(tFirst, tFirst + 0.3)}], labels=[lb(tFirst, -1.3, 0.9, "AIM POINT", tFirst + 0.3, WHITE, at=BK)],
  lines=[ln(tFirst, AIM, HIT, tMiss, tMiss + 1.0, YELLOW, "MISSED BY OVER 0.5 KM", width=3)], source=SRC_BK)
tSank = W("p10", "sank")
sk = {i: tFive + 0.3 + 0.25 * j for j, i in enumerate([4, 9, 14, 18, 23])}
R("c2-sank", tFive, S("p11"), [(tFive, KB(0, 0), 20), (tFive + 1.8, KB(0, 0), 36), (W("p10", "Most"), KB(0, 0), 44)], tag="REAL HISTORY", clock="1946", clockLabel="ABLE · AFTERMATH", zones=[LAGZ],
  ships=lagoon(tFive, S("p11"), sunk=sk), labels=[lb(tFive, 0, -3, "FIVE SHIPS SANK", tFive + 0.4, RED, at=BK), lb(tFive, 0, 3, "MOST BOARDED WITHIN A DAY", W("p10", "Most"), TEAL, at=BK)], source=SRC_BK)
a = S("p11")
tCol = W("p11", "column")
R("c2-baker", a, tCol, [(a, KB(0, 0), 44), (a + 2.2, KB(0, 0), 20), (tCol - 0.3, KB(0, 0), 14)], tag="REAL HISTORY", clock="1946", clockLabel="BAKER · UNDERWATER", zones=[LAGZ],
  ships=lagoon(a, tCol, size=12), cities=[mk(a, 0, 0, "BAKER: 90 FT DOWN", W("p11", "ninety"), ORANGE, "target", 6, at=BK)], rings=[{"at": BK, "km": 0.5, "color": ORANGE, "t": L(a, W("p11", "ninety")), "dashed": False}], source=SRC_BK)
tEight = W("p11", "Eight")
tIncl = W("p11", "including")
sk2 = {i: tEight + 0.3 + 0.35 * j for j, i in enumerate([3, 8, 11, 15, 20, 26, 31, 36])}
R("c2-column", tCol, tIncl, [(tCol, KB(0, 0), 14), (tCol + 1.4, KB(0, 0), 8), (tEight, KB(0, 0), 22), (tEight + 1.6, KB(0, 0), 36), (tIncl - 0.2, KB(0, 0), 42)], tag="REAL HISTORY", clock="1946", clockLabel="BAKER · WATER COLUMN", zones=[LAGZ],
  ships=lagoon(tCol, tIncl, size=12, sunk=sk2), rings=[{"at": BK, "km": 0.4, "color": WHITE, "t": L(tCol, tCol + 0.2), "dashed": False}, {"at": BK, "km": 0.8, "color": ORANGE, "t": L(tCol, tCol + 1.0)}],
  labels=[lb(tCol, 0, 0.7, "WATER COLUMN: MORE THAN A MILE HIGH", tCol + 0.3, WHITE, at=BK), lb(tCol, 0, -3.0, "EIGHT SANK OR CAPSIZED", tEight + 0.3, RED, at=BK)], source=SRC_BK)
tSoak = W("p11", "every")
R("c2-carrier", tIncl, tSoak, [(tIncl, KB(0, 0), 34), (tIncl + 1.5, KB(-3, 1), 14), (tSoak - 0.3, KB(-3, 1), 10)], tag="REAL HISTORY", clock="1946", clockLabel="BAKER · THE CARRIER", zones=[LAGZ],
  ships=lagoon(tIncl, tSoak, size=12, colors={12: BLUE}), cities=[mk(tIncl, -3, 1, "CARRIER: SANK AFTER ABOUT 7.5 HOURS", tIncl + 0.6, BLUE, "ring", 7, at=BK)], source=SRC_BK)
tHose = W("p11", "Hosing")
R("c2-soaked", tSoak, tHose, [(tSoak, KB(0, 0), 28), (tSoak + 1.8, KB(0, 0), 40), (tHose - 0.3, KB(0, 0), 36)], tag="REAL HISTORY", clock="1946", clockLabel="BAKER · FALLOUT AT SEA", zones=[dict(LAGZ, color=AMBER, fillOpacity=0.16)],
  ships=lagoon(tSoak, tHose, colors={i: AMBER for i in range(len(TARGETS))}), labels=[lb(tSoak, 0, 0, "EVERY SHIP THAT STAYED AFLOAT: RADIOACTIVE", tSoak + 0.4, AMBER, at=BK)], source=SRC_BK)
tThird = W("p11", "third")
R("c2-hose", tHose, tThird, [(tHose, KB(0, 0), 26), (tHose + 1.6, KB(1, 0), 16), (tThird - 0.2, KB(1, 0), 20)], tag="REAL HISTORY", clock="1946", clockLabel="BAKER · HOSING", zones=[],
  ships=lagoon(tHose, tThird, colors={i: AMBER for i in range(len(TARGETS))}, size=14), labels=[lb(tHose, 1, 0.8, "HOSING HELPED ONCE", tHose + 0.3, TEAL, at=BK), lb(tHose, 1, -0.8, "THEN IT STOPPED WORKING", W("p11", "stopped"), RED, at=BK)], source=SRC_BK)
R("c2-cancel", tThird, S("p12"), [(tThird, KB(0, 0), 40), (tThird + 2.0, KB(0, 0), 70), (S("p12") - 0.3, KB(0, 0), 110)], tag="REAL HISTORY", clock="1946", clockLabel="THE THIRD TEST", zones=[LAGZ],
  ships=lagoon(tThird, S("p12"), colors={i: AMBER for i in range(len(TARGETS))}, size=8), cities=[mk(tThird, 0, 0, "THIRD TEST: CANCELLED", tThird + 0.8, RED, "target", 7, at=BK)],
  caption="The Navy could not clean its ships.", source=SRC_BK)
a = S("p12")
tBaker = W("p12", "Baker")
R("c2-air", a, tBaker, [(a, K(-2.5, 0), 22), (a + 1.6, K(0, 0), 14), (tBaker - 0.3, K(0, 0), 16)], tag="SIMULATION", clock="", ships=fleet(a, tBaker, 16), rings=[ring(2, a, W("p12", "air"), "5 PSI"), ring(4, a, W("p12", "air") + 0.6, "1 PSI")],
  cities=[mk(a, 0, 0, "AIR BURST (OURS)", W("p12", "air"), RED, "target", 6)], caption="That is why our simulation uses an air burst.", legend=GEN)
add(id="c2-bars", type="bars", start=round(tBaker, 3), end=round(S("p13"), 3), tag="REAL HISTORY", title="Baker was more than twice our size", sub="kilotons · Baker was shallow and underwater", source="Atomic Archive (Baker); scenario assumption (ours)",
    bars=[{"label": "Baker, 1946", "value": 23, "display": "about 23 kt", "color": AMBER}, {"label": "Our burst", "value": 10, "display": "10 kt", "color": RED}])
a = S("p13")
CUBA = "192"
t62 = W("p13", "Soviet")
tNuc = W("p13", "nuclear", 1)
SUBC = [-75.4, 23.9]
HLC = [{"iso": CUBA, "color": "#C9D1D9", "fill": "rgba(200,210,220,0.10)"}]
R("c2-chase", a, W("p13", "Launching"), [(a, [-77, 23.2], 2600), (t62, [-77, 23.4], 1500), (t62 + 2.0, [-76.2, 23.7], 700), (tNuc + 1.0, [-75.7, 23.9], 400)], tag="REAL HISTORY", clock="1962", clockLabel="NEAR CUBA · APPROXIMATE", grid=False, highlight=HLC,
  cities=[{"at": [-78.0, 22.2], "label": "CUBA", "color": "#C9D1D9", "kind": "dot", "size": 4, "t": 0.6}],
  ships=[{"path": [[-76.9, 24.8], [-75.4, 23.9]], "t0": L(a, t62), "t1": L(a, tNuc + 3.0), "kind": "us", "color": AMBER, "size": 16, "label": "SOVIET SUBMARINE B-59", "t": L(a, t62), "wake": True},
         {"path": [[-78.6, 25.8], [-76.9, 24.7]], "t0": L(a, t62), "t1": L(a, tNuc + 3.0), "kind": "us", "color": BLUE, "size": 18, "label": "CARRIER GROUP", "t": L(a, t62 + 1.6), "wake": True}],
  labels=[{"at": [-75.4, 23.2], "text": "OUT OF AIR, CHASED", "color": WHITE, "t": L(a, W("p13", "out"))}, {"at": [-75.4, 24.7], "text": "NUCLEAR TORPEDO: ABOUT 10 KT", "color": RED, "t": L(a, tNuc)}], source="National Security Archive; Wikipedia (B-59)")
tThree = W("p13", "three")
tOne = W("p13", "One")
tCame = W("p13", "It", 2)
tL0 = W("p13", "Launching")
tPic = W("p13", "weapon")
R("c2-b59", tL0, tPic, [(tL0, [-76.5, 23.6], 450), (tThree, [-75.9, 23.8], 260), (tOne, [-75.9, 23.8], 330), (tCame, [-75.6, 23.9], 200), (tPic - 0.5, [-76.2, 23.6], 380)], tag="REAL HISTORY", clock="1962", clockLabel="B-59 · LAUNCH ORDER", grid=False,
  ships=[{"path": [SUBC, [SUBC[0] + 0.02, SUBC[1]]], "t0": 0, "t1": round(tPic - tL0, 2), "kind": "us", "color": AMBER, "size": 26, "label": "B-59", "wake": False}],
  cities=[{"at": [SUBC[0] - 0.25, SUBC[1] + 0.22 + 0.03 * i], "kind": "dot", "color": AMBER, "size": 7, "label": ("OFFICER " + str(i + 1)), "t": L(tL0, tThree + 0.35 * i)} for i in range(3)]
  + [{"at": [SUBC[0] - 0.25, SUBC[1] + 0.34], "kind": "dot", "color": RED, "size": 8, "label": "ONE OFFICER REFUSED", "t": L(tL0, tOne + 0.2)}],
  labels=[{"at": [SUBC[0] + 0.1, SUBC[1] - 0.2], "text": "THE BOAT SURFACED", "color": WHITE, "t": L(tL0, W("p13", "boat"))}, {"at": [SUBC[0] + 0.1, SUBC[1] - 0.32], "text": "IT CAME CLOSE", "color": YELLOW, "t": L(tL0, tCame)}],
  caption="Launching it needed three officers to agree.", source="National Security Archive; Wikipedia (B-59)")
R("c2-sizeof", tPic, S("p14"), [(tPic, K(-2.5, 0), 22), (tPic + 2.0, K(-1.5, 0), 14), (S("p14") - 0.3, K(-1.5, 0), 11)], tag="SIMULATION", clock="", ships=fleet(tPic, S("p14"), 14, labels={"CV": "CARRIER"}),
  rings=[ring(4, tPic, W("p13", "ten") if False else tPic + 1.4, "10 KT: 1 PSI RING", km=3.949)], caption="A weapon of that size, near a carrier group, is the picture this episode draws.", cities=[mk(tPic, 0, 0, None, tPic + 0.2, RED, "target", 6)], legend=GEN)
a = S("p14")
tSic = W("p14", "Sicily")
G("c2-1975", a, W("p14", "In"), [(a, 40, 14, 1400), (W("p14", "from"), 38, 14, 1800)], tag="REAL HISTORY", clock="1975", clockLabel="DANGER FROM THE SHIPS THEMSELVES", source="Federation of American Scientists (Kristensen)",
  markers=[{"at": [14.5, 36.6], "label": "OFF SICILY", "color": AMBER, "kind": "target", "t": 2.2}])
tCol2 = W("p14", "collided")
R("c2-sicily", W("p14", "In"), tCol2 + 0.3, [(W("p14", "In"), [14.2, 37.0], 1200), (W("p14", "In") + 2.4, [14.4, 36.6], 400), (tCol2 - 0.2, [14.4, 36.6], 120)], tag="REAL HISTORY", clock="1975", clockLabel="OFF SICILY", grid=False,
  highlight=[{"iso": "380", "color": "#C9D1D9", "fill": "rgba(200,210,220,0.08)"}], cities=[{"at": [14.4, 36.6], "label": "THE COLLISION", "color": AMBER, "kind": "target", "size": 6, "t": L(W("p14", "In"), W("p14", "cruiser"))}],
  ships=[{"path": [[14.9, 36.2], [14.42, 36.58]], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 18, "label": "CARRIER", "t": L(W("p14", "In"), W("p14", "carrier")), "wake": True},
         {"path": [[13.9, 37.0], [14.38, 36.62]], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 14, "label": "CRUISER", "t": L(W("p14", "In"), W("p14", "cruiser")), "wake": True}], source="Federation of American Scientists (Kristensen)")
tFire = W("p14", "fire")
R("c2-fire", tCol2 + 0.3, W("p14", "and", 3), [(tCol2 + 0.3, [14.4, 36.6], 20), (tFire, [14.4, 36.6], 8), (W("p14", "and", 3) - 0.3, [14.4, 36.6], 5)], tag="REAL HISTORY", clock="1975", clockLabel="THE FIRE", grid=False,
  ships=[{"path": [[14.397, 36.601], [14.403, 36.6]], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 36, "label": "CRUISER", "wake": False}, {"path": [[14.41, 36.6], [14.414, 36.6]], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 50, "label": "CARRIER", "wake": False}],
  cities=[{"at": [14.3985, 36.601], "label": "FIRE", "color": ORANGE, "kind": "dot", "size": 8, "t": L(tCol2 + 0.3, tFire)}, {"at": [14.4012, 36.6008], "label": "MAGAZINE", "color": RED, "kind": "ring", "size": 5, "t": L(tCol2 + 0.3, W("p14", "nuclear"))}],
  caption="One analyst reports the fire stopped a few meters from the cruiser's nuclear magazine.", source="Federation of American Scientists (Kristensen)")
R("c2-both", W("p14", "and", 3), S("p15"), [(W("p14", "and", 3), [14.4, 36.6], 5), (W("p14", "and", 3) + 2.0, [14.4, 36.6], 12)], tag="REAL HISTORY", clock="1975", clockLabel="BOTH SHIPS", grid=False,
  ships=[{"path": [[14.397, 36.601], [14.403, 36.6]], "t0": 0, "t1": 5, "kind": "us", "color": RED, "size": 30, "label": "NUCLEAR WEAPONS ABOARD", "wake": False}, {"path": [[14.41, 36.6], [14.414, 36.6]], "t0": 0, "t1": 5, "kind": "us", "color": RED, "size": 44, "label": "NUCLEAR WEAPONS ABOARD", "wake": False, "t": 1.2}],
  rings=[{"at": [14.4, 36.6], "km": 0.5, "color": AMBER, "dashed": True}, {"at": [14.4, 36.6], "km": 1.0, "color": AMBER, "dashed": True}], caption="One analyst reports both ships carried nuclear weapons.", source="Federation of American Scientists (Kristensen)")
a = S("p15")
add(id="c2-5000", type="number", start=round(a, 3), end=round(W("p15", "Then"), 3), tag="REAL HISTORY", value="MORE THAN 5,000", countTo=5000, prefix="MORE THAN ", label="US nuclear weapons at sea, 1990", color=AMBER, source="Federation of American Scientists (Kristensen)")
tThen = W("p15", "Then")
tOrd = W("p15", "ordered")
R("c2-1991", tThen, W("p15", "last"), [(tThen, K(-2.5, 0), 26), (tOrd, K(-2.5, 0), 20), (W("p15", "last") - 0.3, K(-2.5, 0), 34)], tag="REAL HISTORY", clock="1991", clockLabel="ORDERED OFF THE SHIPS", ships=fleet(tThen, W("p15", "last"), 22),
  cities=[mk(tThen, OFF[n][0] + 0.3, OFF[n][1] + 0.5, None, tThen + 0.2 + 0.15 * i, RED, "dot", 5) for i, n in enumerate(ALL)],
  lines=[ln(tThen, K(OFF[n][0] + 0.3, OFF[n][1] + 0.5), K(-30, 10 + 2.5 * i), tOrd + 0.2 * i, tOrd + 1.6 + 0.2 * i, RED, dashed=True, width=2) for i, n in enumerate(ALL)], caption="1991: the US orders its tactical weapons off its ships.", legend=GEN, source="Federation of American Scientists (Kristensen)")
R("c2-1992", W("p15", "last"), S("p16"), [(W("p15", "last"), K(-2.5, 0), 34), (W("p15", "last") + 1.5, K(-2.5, 0), 20), (S("p16") - 0.3, K(-2.5, 0), 14)], tag="REAL HISTORY", clock="1992", clockLabel="THE LAST ARE GONE", ships=fleet(W("p15", "last"), S("p16"), 22, labels={"CV": "CARRIER"}),
  labels=[lb(W("p15", "last"), -2.5, 4.0, "NO TACTICAL NUCLEAR WEAPONS ABOARD", W("p15", "gone"), TEAL)], legend=GEN, source="Federation of American Scientists (Kristensen)")
a = S("p16")
tTreaty = W("p16", "last")
R("c2-none", a, tTreaty, [(a, K(-2.5, 0), 16), (a + 2.0, K(-2.5, 0), 24), (tTreaty - 0.3, K(-2.5, 0), 32)], tag="REAL HISTORY", clock="TODAY", clockLabel="A CARRIER GROUP", ships=fleet(a, tTreaty, 22, labels={"CV": "CARRIER"}),
  labels=[lb(a, -2.5, 4.4, "NO TACTICAL NUCLEAR WEAPONS ABOARD", W("p16", "no"), TEAL)], legend=GEN, source="Congressional Research Service IF12084")
add(id="c2-treaty", type="stamp", start=round(tTreaty, 3), end=round(W("p16", "So", 2), 3), tag="REAL DATA", text="FEBRUARY 2026", line="the last treaty limits on the big arsenals ended", color=AMBER, source="Arms Control Association")
tSo = W("p16", "So", 2)
G("c2-how", tSo, S("p17"), [(tSo, 20, 160, 1500), (tSo + 2.5, 24, 155, 800), (S("p17") - 0.3, 24, 155, 1100)], tag="SIMULATION", clock="", caption="So how could a nuclear weapon reach one, in a simulation?",
  markers=[{"at": B, "label": "OPEN PACIFIC (SIMULATED)", "color": BLUE, "kind": "target", "t": 1.0}, {"at": SUBP, "label": "?", "color": RED, "kind": "ring", "t": 3.6}])

# ================================================================== Chapter 03: the trigger [SIMULATION]
a = S("p17")
chapter("c3-card", a, a + 3.7, "CHAPTER 03", "The trigger", "SIMULATION")
a += 3.7
tFires = W("p17", "fires")
R("c3-sub", a, W("p17", "about"), [(a, K(-DIST, 0), 60), (a + 1.6, K(-DIST + 40, 0), 330), (W("p17", "about") - 0.3, K(-140, 0), 420)], clock="T+00:00", clockLabel="MINUTE ZERO", ships=[missile(a, W("p17", "about"), [K(-DIST, 0), K(-DIST + 90, 0)], "MISSILE", t=tFires, t0=tFires - a)],
  cities=[mk(a, -DIST, 0, "ATTACKER'S SUBMARINE", a + 0.3, RED, "sub", 6)], caption="An unnamed attacker, with no flag and no country.", labels=[lb(a, -DIST + 25, 22, "ONE NUCLEAR CRUISE MISSILE", tFires + 0.4, RED)])
tAbout = W("p17", "about")
tFict = W("p17", "fictional") if False else W("p17", "weapon", 1)
R("c3-dist", tAbout, tFict, [(tAbout, K(-140, 0), 420), (tAbout + 1.2, K(-140, 0), 380)], clock="", lines=[ln(tAbout, K(-DIST, 0), K(-3, 0), tAbout + 0.1, tAbout + 1.6, RED, "284 KM", dashed=True, width=3)],
  cities=[mk(tAbout, -DIST, 0, "SUBMARINE", None, RED, "sub", 6), mk(tAbout, -2.5, 0, None, tAbout + 0.5, BLUE, "ring", 9)], labels=[lb(tAbout, -2.5 - 25, 22, "US CARRIER GROUP", tAbout + 0.5, "#CFE3FF")], ships=[missile(tAbout, tFict, [K(-DIST + 90, 0), K(-DIST + 110, 0)], "MISSILE")])
tYield = W("p17", "No", 3)
tChoose = W("p17", "choose")
R("c3-fiction", tFict, tChoose, [(tFict, K(-DIST / 2, 0), 430), (tFict + 2.0, K(-DIST / 2 + 10, 0), 390), (tYield - 0.2, K(-DIST / 2, 0), 440)], clock="", rings=[{"at": K(-2.5, 0), "km": 20 * i, "color": BLUE, "dashed": False} for i in (1, 2)], caption="One fictional weapon, aimed at one carrier group.", lines=[ln(tFict, K(-DIST, 0), K(-4, 0), tFict + 0.2, tFict + 1.8, RED, dashed=True, width=3)],
  cities=[mk(tFict, -DIST, 0, "SUBMARINE", tFict + 0.1, RED, "sub", 7), mk(tFict, -2.5, 0, None, tFict + 0.2, BLUE, "ring", 11)], ships=[missile(tFict, tChoose, [K(-DIST + 40, 0), K(-60, 0)], "MISSILE", size=28)],
  labels=[lb(tFict, -2.5 - 60, 40, "US CARRIER GROUP", tFict + 0.3, "#CFE3FF"), lb(tFict, -DIST / 2, 45, "THE WEAPON IS FICTIONAL", tFict + 0.1, YELLOW), lb(tFict, -DIST / 2, -45, "NO PUBLISHED YIELD FOR ANY MODERN ANTI-SHIP MISSILE", W("p17", "published") + 0.2, WHITE)])
a = tChoose
add(id="c3-10kt", type="number", start=round(a, 3), end=round(W("p17", "Cold"), 3), tag="SIMULATION", value="10 KT", label="our choice: about 10 kilotons", color=RED, source="Scenario assumption")
tSize = W("p17", "Cold")
add(id="c3-rocket", type="bars", start=round(tSize, 3), end=round(S("p18"), 3), tag="SIMULATION", title="About the size of a Cold War nuclear rocket test", sub="kilotons · Swordfish, 1962: about 10 kt (one source)", source="Wikipedia (Operation Swordfish); scenario assumption (ours)",
    bars=[{"label": "Swordfish, 1962", "value": 10, "display": "about 10 kt", "color": AMBER}, {"label": "Our weapon", "value": 10, "display": "10 kt", "color": RED}])
a = S("p18")
tWar = W("p18", "not")
R("c3-one", a, W("p18", "The"), [(a, K(-DIST + 60, 0), 360), (a + 2.4, K(-120, 0), 300), (W("p18", "The") - 0.3, K(-100, 0), 260)], clock="", caption="One weapon, not a war.", ships=[missile(a, W("p18", "The"), [K(-DIST + 40, 0), K(-DIST + 140, 0)], "ONE MISSILE", t=a + 0.2)],
  cities=[mk(a, -DIST, 0, "SUBMARINE", None, RED, "sub", 5), mk(a, -2.5, 0, "US GROUP", a + 0.8, BLUE, "ring", 9)], labels=[lb(a, -120, 24, "ONE WEAPON", W("p18", "one"), RED), lb(a, -120, -24, "NOT A WAR", tWar, WHITE)])
a = W("p18", "The")
tCtr = W("p18", "carrier")
hx = [K(*OFF[n]) for n in ["E0", "E1", "E2", "E3", "E4", "E5", "E0"]]
R("c3-hex", a, tCtr, [(a, K(-2.5, 0), 20), (a + 1.2, K(-2.5, 0), 13), (tCtr - 0.3, K(-2.5, 0), 11)], clock="", zones=[{"points": hx[:-1], "color": YELLOW, "t": L(a, W("p18", "hexagon")), "fillOpacity": 0.06, "strokeWidth": 2.2, "solid": False}],
  labels=[lb(a, -2.5, 3.4, "A GENERIC HEXAGON IN OPEN OCEAN", W("p18", "generic"), YELLOW)], caption="The group is a generic hexagon in open ocean.", legend=GEN)
tEsc2 = W("p18", "an")
tSupp = W("p18", "supply")
tTyp = W("p18", "typical")
R("c3-center", tCtr, tTyp, [(tCtr, K(-2.5, 0), 11), (tEsc2, K(-2.5, 0), 13), (tSupp, K(-2.5, 0), 11), (tTyp - 0.3, K(-2.5, 0), 14)], clock="",
  ships=fleet(tCtr, tTyp, 12, labels={"CV": "CARRIER AT THE CENTER", "AO": "SUPPLY SHIP INSIDE"}, times={"CV": tCtr, "AO": tSupp, "E0": tEsc2 + 0.1, "E1": tEsc2 + 0.5, "E2": tEsc2 + 0.9, "E3": tEsc2 + 1.3, "E4": tEsc2 + 1.7, "E5": tEsc2 + 2.1}),
  zones=[{"points": hx[:-1], "color": YELLOW, "fillOpacity": 0.05, "strokeWidth": 2.0, "solid": False}], labels=[lb(tCtr, -2.5, 3.4, "AN ESCORT AT EACH CORNER", tEsc2 + 0.4, WHITE)], legend=GEN)
tSix = W("p18", "six")
R("c3-six", tTyp, S("p19"), [(tTyp, K(-2.5, 0), 14), (tSix, K(-2.5, 0), 11), (S("p19") - 0.3, K(-2.5, 0), 16)], clock="", ships=fleet(tTyp, S("p19"), 12, labels={"CV": "CARRIER"}),
  labels=[lb(tTyp, -2.5, 3.4, "TYPICAL: THREE TO FIVE ESCORTS", tTyp + 0.4, DIM), lb(tTyp, -2.5, -3.4, "WE DRAW SIX, FOR SYMMETRY", tSix, YELLOW)], legend=GEN)
a = S("p19")
tIcons = W("p19", "Ship")
R("c3-vary", a, tIcons, [(a, K(-2.5, 0), 26), (a + 1.6, K(-2.5, 0), 36), (tIcons - 0.3, K(-2.5, 0), 22)], clock="", ships=fleet(a, tIcons, 24, labels={"CV": "CARRIER"}), caption="Real groups vary, and so does everything about a real night at sea.", legend=GEN)
tDot = W("p19", "dot")
R("c3-icons", tIcons, S("p20"), [(tIcons, K(-2.5, 0), 13), (tIcons + 2.0, K(-3.0, -0.8), 8.5), (S("p20") - 0.5, K(-3.75, -1.6), 5.5)], clock="", ships=fleet(tIcons, S("p20"), 8, names=["CV", "E1", "E2", "E3", "E4", "E5"], labels={"E4": "DESTROYER, ICON"}),
  cities=[mk(tIcons, OFF["E4"][0] + 0.12, OFF["E4"][1] - 0.06, "TRUE SCALE: A DOT", W("p19", "true"), YELLOW, "dot", 3)], caption="Ship icons are drawn larger than life.", legend=GEN)
a = S("p20")
tRad = W("p20", "radar")
tDep = W("p20", "depends")
tSees = W("p20", "Our")
R("c3-flies", a, tSees, [(a, K(-150, 0), 340), (a + 1.8, K(-100, 0), 220), (tRad - 0.3, K(-8.0, 0.5), 22), (tRad + 1.4, K(-4.0, 0), 11), (tSees - 0.3, K(-4.5, 0), 14)], clock="T+00:00", clockLabel="THE MISSILE FLIES", clockRate=60,
  ships=fleet(a, tSees, 14, labels={"E3": "ESCORT: RADAR"}, times={n: tRad - 0.3 for n in ALL}) + [missile(a, tDep, [K(-DIST + 20, 0), K(-DIST + 120, 0)], "MISSILE", t=a + 0.1)],
  caption="The missile flies for twenty minutes. Whether the group sees it depends on one radar operator.", cities=[mk(a, -2.5, 0, "US GROUP", a + 0.4, BLUE, "ring", 8)], lines=[ln(a, K(-DIST, 0), K(-4, 0), a + 0.2, a + 1.6, RED, dashed=True)],
  rings=[{"at": K(*OFF["E3"]), "km": 3.0, "color": TEAL, "t": L(a, tRad), "dashed": True}, {"at": K(*OFF["E3"]), "km": 6.0, "color": TEAL, "t": L(a, tRad + 0.8), "dashed": True}],
  labels=[lb(a, -5.0, 3.5, "ONE RADAR OPERATOR", tRad + 0.6, TEAL)], legend=GEN)
tBut = W("p20", "cannot")
R("c3-see", tSees, W("p20", "A", 2), [(tSees, K(-9, 1), 26), (tBut, K(-8, 1), 16), (W("p20", "A", 2) - 0.3, K(-8, 1), 20)], clock="", ships=fleet(tSees, W("p20", "A", 2), 18, labels={"E3": "ESCORT"}) + [missile(tSees, W("p20", "A", 2), [K(-18, 3), K(-12, 2.4)], "CONTACT", t=tSees + 0.3)],
  labels=[lb(tSees, -9, 4, "THEY SEE IT", tSees + 0.4, TEAL), lb(tSees, -9, -3.6, "THEY CANNOT BE SURE WHAT IT IS", tBut, YELLOW)], legend=GEN)
tCall = W("p20", "call")
R("c3-phone", W("p20", "A", 2), S("p21"), [(W("p20", "A", 2), K(-60, 0), 160), (tCall - 0.5, K(-30, 0), 80), (S("p21") - 0.3, K(-15, 0), 40)], clock="T-08:00", clockLabel="LIKE A LONG PHONE CALL", clockRate=60,
  ships=[missile(W("p20", "A", 2), S("p21"), [K(-100, 0), K(-40, 0)], "MISSILE", t=W("p20", "A", 2))], cities=[mk(W("p20", "A", 2), -2.5, 0, "US GROUP", None, BLUE, "ring", 8)], caption="A missile low over the water gives a crew about as much time as a long phone call.")

# ================================================================== Chapter 04: minute by minute [SIMULATION]
a = S("p21")
chapter("c4-card", a, a + 3.7, "CHAPTER 04", "Minute by minute", "SIMULATION")
a += 3.7
tFar = W("p21", "and")
LAUNCH_XY = K(-DIST, 0)
a2 = S("p22")
tBey = W("p21", "beyond")
R("c4-sub", a, a2, [(a, LAUNCH_XY, 40), (a + 1.6, K(-DIST + 20, 0), 90), (W("p21", "and") - 0.2, K(-DIST + 40, 0), 160), (W("p21", "and") + 1.0, K(-DIST / 2, 0), 420), (a2 - 0.5, K(-DIST / 2, 0), 480)], **clk(a, a2, "MINUTE ZERO"),
  cities=[mk(a, -DIST, 0, "ATTACKER'S SUBMARINE", a + 0.2, RED, "sub", 6), mk(a, -2.5, 0, "US GROUP", W("p21", "and") + 0.8, BLUE, "ring", 9)],
  ships=[missile(a, a2, [K(-DIST, 0), K(xm(mm(a2)), 0)], "MISSILE LEAVES THE WATER", t=a + 0.4)], lines=[ln(a, K(-DIST, 0), K(-4, 0), W("p21", "and") + 0.2, W("p21", "and") + 1.8, RED, "ABOUT 280 KM", dashed=True, width=3)],
  labels=[lb(a, -DIST / 2, 30, "BEYOND ANY LOOKOUT'S EYE", tBey, YELLOW)], caption="A submarine's launch is never seen from the surface.")
a = S("p22")
tNear = W("p22", "nearest")
tLow = W("p22", "low")
R("c4-m8", a, tLow, [(a, K(-85, 0), 235), (a + 2.8, K(-85, 0), 205), (tLow - 0.3, K(-80, 0), 185)], **clk(a, tLow, "MINUTE EIGHT"), ships=[missile(a, tLow, [K(xm(mm(a)), 0), K(xm(mm(tLow)), 0)], "CONTACT", t=a)],
  cities=[mk(a, -5, 0, "ESCORT", tNear, TEAL, "ring", 8), mk(a, -2.5, 0, "US GROUP", a + 0.3, BLUE, "ring", 7)], caption="A contact appears on the screens of the escort nearest the attacker.")
tChain = W("p22", "calls")
R("c4-chain", tLow, tChain + 1.0, [(tLow, K(-6.0, 0.5), 18), (tChain, K(-3.5, 0), 11), (tChain + 0.6, K(-3.0, 0), 13)], **clk(tLow, tChain + 1.0, "MINUTE EIGHT"), ships=fleet(tLow, tChain + 1.0, 13, labels={"E3": "ESCORT", "CV": "CARRIER"}) + [missile(tLow, tChain + 1.0, [K(-14, 0.6), K(-9, 0.4)], "LOW AND FAST", t=tLow)],
  lines=[ln(tLow, K(*OFF["E3"]), K(*OFF["CV"]), tChain, tChain + 0.9, TEAL, "UP THE CHAIN", width=3)], legend=GEN, caption="The watch officer calls it up the chain.")
tSecond = W("p22", "second")
add(id="c4-confirm", type="radar", start=round(tChain + 1.0, 3), end=round(S("p23"), 3), tag="SIMULATION", title="Minute eight · escort radar", lines=[{"k": "contact", "v": "low and fast"}, {"k": "second radar", "v": "asked to confirm"}, {"k": "identity", "v": "unknown"}], tracks=1, big="UNCONFIRMED", bigColor=YELLOW, clock="T+08:30", clockLabel="SINCE LAUNCH", clockRate=1)
a = S("p23")
tHatch = W("p23", "Hatches")
tHeli = W("p23", "helicopters")
R("c4-gq", a, tHeli, [(a, K(-2.5, 0), 20), (a + 2.4, K(-2.5, 0), 13), (tHeli - 0.3, K(-2.5, 0), 11)], **clk(a, tHeli, "GENERAL QUARTERS"), ships=fleet(a, tHeli, 12, colors={n: AMBER for n in ALL}, labels={"CV": "CARRIER"}),
  labels=[lb(a, -2.5, 3.4, "GENERAL QUARTERS", a + 0.5, AMBER), lb(a, -2.5, -3.4, "HATCHES CLOSE, GEAR LASHED DOWN", tHatch + 0.4, WHITE)], legend=GEN)
tNo = W("p23", "Nobody")
hel = [[K(-2.5, 0), K(-2.5 + 2.6 * math.cos(math.radians(d)), 2.6 * math.sin(math.radians(d)))] for d in (60, 160, 270)]
R("c4-heli", tHeli, S("p24"), [(tHeli, K(-2.5, 0), 11), (tHeli + 1.4, K(-2.5, 0), 7), (tNo, K(-2.5, 0), 11), (tNo + 1.6, K(-2.5, 0), 18), (S("p24") - 0.4, K(-2.5, 0), 26)], **clk(tHeli, S("p24"), "NO ORDER YET"),
  ships=fleet(tHeli, S("p24"), 12, colors={n: AMBER for n in ALL}, labels={"CV": "CARRIER"}) + [jet(tHeli, S("p24"), p, tHeli + 0.1 + 0.4 * i, tHeli + 0.3 + 0.4 * i, tHeli + 2.3 + 0.4 * i, size=14) for i, p in enumerate(hel)],
  labels=[lb(tHeli, -2.5, 1.8, "HELICOPTERS LIFT OFF TO LOOK", tHeli + 0.3, WHITE), lb(tHeli, -2.5, 3.8, "NO ORDER TO SHOOT YET", tNo + 0.4, RED), lb(tHeli, -2.5, -3.8, "NOBODY CAN SAY WHAT IT IS", W("p23", "because"), WHITE)], legend=GEN)
a = S("p24")
tTrack = W("p24", "track")
tCarr = W("p24", "carrier")
R("c4-turn", a, tCarr, [(a, K(-6, 0), 22), (tTrack - 0.5, K(-6.0, 0.5), 13), (tCarr - 0.3, K(-5.0, 0), 15)], **clk(a, tCarr, "MINUTE SEVENTEEN"),
  ships=fleet(a, tCarr, 14, labels={"E3": "ESCORT TURNS TOWARD IT"}, paths={"E3": [K(-5.0, 0.0), K(-5.4, 0.9), K(-6.0, 1.2)]}) + [missile(a, tCarr, [K(-16, 2.6), K(-11, 1.8)], "CONTACT", t=a + 0.1)],
  lines=[ln(a, K(-5.5, 0.9), K(-12, 1.9), tTrack, tTrack + 0.8, RED, "GUNS TRACK IT", dashed=True, width=3)], legend=GEN)
tReady = W("p24", "ready")
R("c4-wind", tCarr, W("p24", "and", 2) + 0.3, [(tCarr, K(-2.5, 0), 14), (tReady, K(-2.5, 0), 10), (W("p24", "and", 2), K(-2.5, 0), 12)], **clk(tCarr, W("p24", "and", 2) + 0.3, "MINUTE SEVENTEEN"),
  ships=fleet(tCarr, W("p24", "and", 2) + 0.3, 11, names=["CV", "E1", "E5", "AO"], labels={"CV": "CARRIER TURNS INTO THE WIND"}, paths={"CV": [K(-2.5, 0), K(-2.0, 0.1), K(-1.2, 0.5)]}),
  lines=[ln(tCarr, K(3.5, 2.0 - 0.8 * i), K(0.5, 2.0 - 0.8 * i), tCarr + 0.3 + 0.2 * i, tCarr + 1.4 + 0.2 * i, TEAL, width=2) for i in range(5)], labels=[lb(tCarr, -1.5, -2.3, "READY TO LAUNCH", tReady, WHITE)], legend=GEN)
tBc = W("p24", "every")
bcast = [{"at": K(*OFF[n]), "km": 1.3, "color": YELLOW, "t": L(W("p24", "and", 2) + 0.3, tBc + 0.35 * i), "dashed": False} for i, n in enumerate(ALL)]
R("c4-bcast", W("p24", "and", 2) + 0.3, S("p25"), [(W("p24", "and", 2) + 0.3, K(-2.5, 0), 15), (tBc + 1.0, K(-2.5, 0), 11), (S("p25") - 0.4, K(-2.5, 0), 17)], **clk(W("p24", "and", 2) + 0.3, S("p25"), "EVERY CHANNEL"),
  ships=fleet(0, 1, 13)[0:0] + fleet(W("p24", "and", 2) + 0.3, S("p25"), 13, labels={"CV": "CARRIER"}), rings=bcast, labels=[lb(W("p24", "and", 2) + 0.3, -2.5, 3.6, "UNIDENTIFIED CONTACT", W("p24", "unidentified"), YELLOW)],
  caption="Every ship broadcasts the same two words on every channel.", legend=GEN)
a = S("p25")
tNear2 = W("p25", "nearest")
tEast = W("p25", "east")
R("c4-m20a", a, tEast, [(a, K(-2.5, 0), 22), (a + 2.4, K(-1.5, 0), 14), (tEast - 0.3, K(-1.0, 0), 11)], **clk(a, tEast, "MINUTE TWENTY"), ships=fleet(a, tEast, 13, labels={"CV": "CARRIER"}) + [missile(a, tEast, [K(9, 6), K(5.5, 3.2)], None, t=a + 0.3, t0=0.3)],
  labels=[lb(a, 0, 2.0, "THE ESCORT NEAREST THE ATTACKER", tNear2, YELLOW)], legend=GEN)
tHit = W("p25", "does")
tBur = W("p25", "bursts") - 0.05
R("c4-m20b", tEast, tBur, [(tEast, K(-1.0, 0), 11), (tEast + 1.4, K(-0.8, 0), 6.5), (tBur - 0.4, K(-0.4, 0), 4.2)], **clk(tEast, tBur, "MINUTE TWENTY"), ships=fleet(tEast, tBur, 6, names=["E0", "CV", "E1", "E5"], labels={"E0": "ESCORT", "CV": "CARRIER"}) + [missile(tEast, tBur, [K(5.5, 3.2), K(0.15, 0.2)], None, t=0, size=24)],
  labels=[lb(tEast, -1.2, -1.7, "A LITTLE EAST OF THE CARRIER", tEast + 0.3, WHITE), lb(tEast, 1.0, 1.6, "IT DOES NOT HIT THE SHIP", tHit, RED)], legend=GEN)
DETT = tBur
R("c4-flash", tBur, S("p26"), [(tBur, K(0, 0), 2.6), (tBur + 1.6, K(-0.5, 0), 7.5), (tBur + 3.6, K(-1.0, 0), 13)], clock="T+20:06", clockLabel="THE BURST", burst={"at": B, "t": 0.1, "km": 0.7, "fade": 6},
  ships=fleet(tBur, S("p26"), 6, names=["E0", "CV", "E1", "E5"], sunk={"E0": tBur + 0.5}), labels=[lb(tBur, -0.3, -1.4, "FOR A MOMENT THE SEA IS BRIGHTER THAN DAY", tBur + 2.2, WHITE)], legend=GEN, ring_=None)
shots[-1].pop("ring_")

# ================================================================== Chapter 05: one warhead, ring by ring [SIMULATION]
a = S("p26")
chapter("c5-card", a, a + 2.9, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
a += 2.9
CL = {"clock": "T+20:06", "clockLabel": "THE BURST", "source": ENG}
fb_r = FX["fireball_km"]
tIns = W("p26", "in")
R("c5-fire", a, tIns, [(a, K(0, 0), 1.9), (a + 1.2, K(0, 0), 1.2), (tIns - 0.3, K(0, 0), 1.6)], **CL, ships=fleet(a, tIns, 1.6, names=["E0"], size=34),
  zones=[disc(fb_r, a, a + 0.2, WHITE, None, 0.45)], labels=[lb(a, 0, -0.3, "FIREBALL: 300 M ACROSS", a + 0.5, WHITE)], caption="The fireball is about three hundred meters across.", legend=[{"text": "FIREBALL 300 M ACROSS", "color": WHITE}])
tDes = W("p26", "destroyed")
R("c5-destroyed", tIns, S("p27"), [(tIns, K(0, 0), 1.6), (tDes, K(0, 0), 2.6), (S("p27") - 0.4, K(0, 0), 3.4)], **CL, ships=fleet(tIns, S("p27"), 2.2, names=["E0"], sunk={"E0": tDes + 0.3}, size=34),
  zones=[disc(fb_r, tIns, -30, WHITE, None, 0.3)], labels=[lb(tIns, 0, -0.45, "DESTROYED: OUR ASSUMPTION", tDes + 0.4, YELLOW), lb(tIns, 0, 0.45, "NOT AN ENGINE RESULT", W("p26", "engine"), YELLOW)],
  legend=[{"text": "FIREBALL 300 M ACROSS", "color": WHITE}])
a = S("p27")
t20 = W("p27", "twenty")
R("c5-20psi", a, S("p28"), [(a, K(0, 0), 1.8), (t20, K(0, 0), 1.5), (W("p27", "reaches"), K(0, 0), 2.2), (S("p28") - 0.4, K(0, 0), 3.0)], **CL, zones=[disc(fb_r, a, -30, WHITE, None, 0.3)], ships=fleet(a, S("p28"), 2.2, names=["E0"], sunk={"E0": -5})[0:0],
  rings=[ring(1, a, W("p27", "Heavy") + 0.2, "20 PSI: 300 M", False)], labels=[lb(a, 0, 0, "HEAVY BLAST", W("p27", "Heavy"), ORANGE)],
  legend=[{"text": "FIREBALL 300 M ACROSS", "color": WHITE}, {"text": "20 PSI 297 M", "color": ORANGE}])
a = S("p28")
t5 = W("p28", "five")
tReach = W("p28", "reaches")
LEG5 = [{"text": "FIREBALL 300 M ACROSS", "color": WHITE}, {"text": "20 PSI 297 M", "color": ORANGE}, {"text": f"5 PSI {FX['psi5_km']:.2f} KM", "color": RED}]
R("c5-5psi", a, W("p28", "and"), [(a, K(0, 0), 4.6), (t5, K(0, 0), 6.0), (tReach, K(0, 0), 6.6), (W("p28", "and") - 0.4, K(0, 0), 7.2)], **CL,
  rings=[ring(1, a, -30, "", False), ring(2, a, t5 + 0.1, f"5 PSI: {FX['psi5_km']:.2f} KM", False)], zones=[disc(fb_r, a, -30, WHITE, None, 0.3)], labels=[lb(a, 0, 0, "MODERATE BLAST", a + 0.3, RED)], legend=LEG5)
tCov = W("p28", "covers")
R("c5-area", W("p28", "and"), W("p28", "Third-degree"), [(W("p28", "and"), K(0, 0), 7.0), (tCov + 0.6, K(0, 0), 7.6), (W("p28", "Third-degree") - 0.3, K(0, 0), 8.0)], **CL, zones=[disc(FX["psi5_km"], W("p28", "and"), tCov, RED, "6.7 KM² OF SEA", 0.22), disc(fb_r, 0, -30, WHITE, None, 0.3)], rings=[ring(1, 0, -30, "", False)],
  caption="The 5 psi ring covers about six point seven square kilometers of sea.", legend=LEG5)
a = S("p28")
tBurn = W("p28", "Third-degree")
tSkin = W("p28", "skin")
LEG6 = LEG5 + [{"text": f"BURNS {FX['thermal3_km']:.2f} KM", "color": AMBER}]
R("c5-burns", tBurn, S("p29"), [(tBurn, K(0, 0), 7.4), (tSkin, K(0, 0), 8.4), (S("p29") - 0.4, K(0, 0), 10.0)], **CL, rings=[ring(1, tBurn, -30, "", False), ring(2, tBurn, -30, "", False), ring(3, tBurn, tBurn + 0.3, f"THIRD-DEGREE BURNS: {FX['thermal3_km']:.2f} KM", True)],
  zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)], labels=[lb(tBurn, 0, -1.9, "ON BARE SKIN", tSkin, AMBER)], legend=LEG6)
a = S("p29")
t1p = W("p29", "one")
tReach3 = W("p29", "reaches")
LEG7 = LEG6 + [{"text": f"1 PSI {FX['psi1_km']:.2f} KM", "color": TEAL}]
R("c5-1psi", a, S("p30"), [(a, K(0, 0), 12.5), (tReach3, K(-0.4, 0), 15), (S("p30") - 0.5, K(-1.0, 0), 17.5)], **CL, rings=[ring(1, a, -30, "", False), ring(2, a, -30, "", False), ring(3, a, -30, "", False), ring(4, a, W("p29", "light") + 0.1, f"1 PSI: {FX['psi1_km']:.2f} KM", True)],
  zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)], labels=[lb(a, 0, 3.2, "LIGHT BLAST", W("p29", "light"), TEAL)], legend=LEG7)
a = S("p30")
ALLRINGS = lambda a_: [ring(1, a_, -30, "", False), ring(2, a_, -30, "", False), ring(3, a_, -30, "", False), ring(4, a_, -30, "", False)]  # noqa: E731
tCar = W("p30", "carrier")
tOut = W("p30", "outside")
tCar = W("p30", "carrier")
tOut = W("p30", "outside")
tCar2 = W("p30", "two", 1)
R("c5-ships", a, tOut, [(a, K(-1.2, 0), 16), (a + 1.2, K(-2.0, 0), 18), (tCar, K(-2.0, 0), 14), (tCar + 2.5, K(-2.2, 0), 11), (tOut - 0.3, K(-2.0, 0), 12)], **{**CL, "source": ""}, rings=ALLRINGS(a), zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)],
  ships=fleet(a, tOut, 14, names=SURVIVORS, times={n: a + 0.3 + 0.18 * i for i, n in enumerate(ALL)}, labels={"CV": "CARRIER"}), cities=[mk(a, 0, 0, "BURST", None, RED, "target", 5)], labels=[lb(a, -1.0, 2.4, "US CARRIER GROUP", a, BLUE)], caption="Now the ships.",
  lines=[ln(a, K(0, 0), K(*OFF[n]), tCar + 0.6 + 0.5 * i, tCar + 1.4 + 0.5 * i, YELLOW, "2.5 KM", width=3) for i, n in enumerate(["CV", "E1", "E5"])], legend=LEG7 + [{"text": "ICONS ENLARGED", "color": BLUE}])
tSup2 = W("p30", "supply")
R("c5-inside", tOut, tSup2, [(tOut, K(-1.8, 0), 12), (tOut + 1.6, K(-1.4, 0), 14), (tSup2 - 0.4, K(-1.4, 0), 15)], **CL, rings=ALLRINGS(tOut), zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)],
  ships=fleet(tOut, tSup2, 14, names=SURVIVORS, labels={"CV": "CARRIER"}), labels=[lb(tOut, -2.5, 2.8, "OUTSIDE THE BLAST AND BURN RINGS", tOut + 0.2, YELLOW), lb(tOut, -2.5, -2.8, "INSIDE THE LIGHT ONE", W("p30", "inside"), TEAL)], legend=LEG7)
tThreeE = W("p30", "three", 2)
R("c5-supply", tSup2, tThreeE, [(tSup2, K(-2.2, 0), 14), (tSup2 + 1.4, K(-2.0, 0), 11), (tThreeE - 0.3, K(-2.0, 0), 13)], **CL, rings=ALLRINGS(tSup2), zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)],
  ships=fleet(tSup2, tThreeE, 12, names=SURVIVORS, labels={"AO": "SUPPLY SHIP"}), lines=[ln(tSup2, K(0, 0), K(*OFF["AO"]), tSup2 + 0.5, tSup2 + 1.5, YELLOW, "3.5 KM", width=3)], legend=LEG7)
tFarL = W("p30", "outside", 2)
R("c5-far", tThreeE, S("p31"), [(tThreeE, K(-2.5, 0), 13), (tThreeE + 1.8, K(-2.5, 0), 16), (tFarL, K(-2.5, 0), 20), (S("p31") - 0.4, K(-2.5, 0), 22)], **CL, rings=ALLRINGS(tThreeE), zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)],
  ships=fleet(tThreeE, S("p31"), 18, names=SURVIVORS, labels={"E2": "4.3 KM", "E3": "5 KM", "E4": "4.3 KM"}), labels=[lb(tThreeE, -2.5, 4.2, "FOUR TO FIVE KM: OUTSIDE EVERY RING", tFarL, TEAL)], legend=LEG7)
a = S("p31")
tHere = W("p31", "Here")
tMissB = W("p31", "missed")
R("c5-bikini", a, tHere, [(a, K(-1.5, 0), 16), (tMissB, K(-0.5, 0), 8), (tHere - 0.5, K(-0.3, 0), 6.5)], **CL, rings=[ring(2, a, -30, "", False), ring(4, a, -30, "", False)], ships=fleet(a, W("p31", "Here"), 10, names=SURVIVORS, labels={"CV": "CARRIER"}),
  lines=[ln(a, K(0, 0), K(0.65, 0), tMissB, tMissB + 0.8, YELLOW, "BIKINI: MISSED BY OVER 0.5 KM", width=3)], cities=[mk(a, 0, 0, None, None, RED, "target", 5)], legend=LEG7)
tAimed = W("p31", "aimed")
tMiss1 = W("p31", "miss", 1)
tHere = W("p31", "Here")
R("c5-miss", tHere, S("p32"), [(tHere, K(-1.5, 0), 16), (tHere + 1.6, K(-1.8, 0), 13), (W("p31", "count"), K(-1.5, 0), 17), (S("p32") - 0.4, K(-1.5, 0), 24)], **{**CL, "source": ""}, rings=[ring(2, 0, -30, None, False), ring(4, 0, -30, None, False)] + [ring(2, tHere, W("p31", "miss") + 0.2, None, True, at=K(-1.0, 0)), ring(4, tHere, W("p31", "miss") + 0.5, None, True, at=K(-1.0, 0))],
  ships=fleet(tHere, S("p32"), 16, names=SURVIVORS, labels={"CV": "CARRIER"}), cities=[mk(tHere, 0, 0, "AIMED HERE", None, RED, "target", 5), mk(tHere, -1.0, 0, "A MISS OF ONE KM", W("p31", "miss") + 0.3, YELLOW, "target", 5)],
  labels=[lb(tHere, -1.5, -4.0, "NO CREW CAN COUNT ON THE AIM", W("p31", "count") + 0.3, WHITE)], legend=LEG7)
a = S("p32")
tNoH = W("p32", "hull")
R("c5-flat", a, tNoH - 0.2, [(a, K(-1.5, 0), 18), (a + 1.5, K(-1.5, 0), 13), (tNoH - 0.4, K(-1.5, 0), 15)], **CL, rings=ALLRINGS(a), zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)], ships=fleet(a, tNoH - 0.2, 14, names=SURVIVORS),
  labels=[lb(a, -1.5, 3.6, "THE MODEL DRAWS RINGS ON A FLAT MAP", a + 0.4, WHITE)], legend=LEG7)
tArm = W("p32", "armor")
R("c5-nohull", tNoH - 0.2, W("p32", "and", 2), [(tNoH - 0.2, K(-2.5, 0), 0.9), (tArm, K(-2.5, 0), 0.8), (W("p32", "and", 2) - 0.3, K(-2.5, 0), 0.95)], **CL, zones=[deck_zone(BLUE, 0.2)], rings=[],
  labels=[lb(tNoH, -2.5, 0.2, "NO HULL", tNoH + 0.1, RED), lb(tNoH, -2.5, -0.2, "NO WAVES", W("p32", "waves"), RED), lb(tNoH, -2.35, 0.0, "NO ARMOR", tArm, RED)], legend=[{"text": "CARRIER TO SCALE: 333 M", "color": BLUE}])
tHard = W("p32", "hardened")
tA2 = W("p32", "and", 2)
R("c5-nosource", tA2, W("p32", "So"), [(tA2, K(-2.0, 0), 11), (tHard, K(-2.0, 0), 9), (W("p32", "So") - 0.4, K(-2.0, 0), 13)], **CL, ships=fleet(tA2, W("p32", "So"), 11, names=SURVIVORS, labels={"CV": "HARDENED WARSHIP"}), rings=ALLRINGS(tA2),
  zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)], labels=[lb(tA2, -2.5, 3.0, "NO OPEN SOURCE SAYS HOW IT ANSWERS", W("p32", "no", 2), YELLOW)], legend=LEG7)
tSurv = W("p32", "survives")
tSinks = W("p32", "sinks")
R("c5-neither", W("p32", "So"), W("p32", "ship"), [(W("p32", "So"), K(-2.0, 0), 13), (tSurv, K(-2.0, 0), 9), (W("p32", "ship") - 0.4, K(-2.0, 0), 11)], **CL, ships=fleet(W("p32", "So"), W("p32", "ship"), 10, names=SURVIVORS, labels={"CV": "CARRIER"}), rings=ALLRINGS(W("p32", "So")),
  zones=[disc(fb_r, 0, -30, WHITE, None, 0.3)], labels=[lb(W("p32", "So"), -2.5, 2.2, "SURVIVES? WE DO NOT SAY", tSurv, WHITE), lb(W("p32", "So"), -2.5, -2.4, "SINKS? WE DO NOT SAY", tSinks, WHITE)], legend=LEG7)
tWash = W("p32", "wash-down") if any(w["unit"] == "p32" and w["word"].strip(".,").lower() == "wash-down" for w in WORDS) else W("p32", "seawater")
WS = W("p32", "ship")
spray = [bar(WS, (-2.5 - 0.15 + 0.03 * i, 0.04), (-2.5 - 0.15 + 0.03 * i, 0.075 + 0.02 * (i % 2)), W("p32", "sprays") + 0.06 * i, TEAL, 0.004, 0.85) for i in range(11)] + \
        [bar(WS, (-2.5 - 0.15 + 0.03 * i, -0.04), (-2.5 - 0.15 + 0.03 * i, -0.075 - 0.02 * (i % 2)), W("p32", "sprays") + 0.06 * i, TEAL, 0.004, 0.85) for i in range(11)]
R("c5-wash", W("p32", "ship"), S("p33"), [(W("p32", "ship"), K(-2.5, 0), 1.5), (W("p32", "sprays"), K(-2.5, 0), 0.9), (W("p32", "built"), K(-2.5, 0), 1.1), (S("p33") - 0.5, K(-2.5, 0), 1.3)], **CL, zones=[deck_zone(BLUE, 0.35)] + spray,
  labels=[lb(W("p32", "ship"), -2.5, 0.17, "SEAWATER WASH-DOWN: DECK AND HULL", tWash, TEAL), lb(W("p32", "ship"), -2.5, -0.17, "BUILT FOR FALLOUT AND FIRE", W("p32", "built"), WHITE), lb(W("p32", "ship"), -2.5, 0.32, "THE CREW WOULD TURN IT ON", W("p32", "crew"), YELLOW)],
  legend=[{"text": "CARRIER TO SCALE: 333 M", "color": BLUE}])
a = S("p33")
tHist = W("p33", "History")
R("c5-nofall", a, tHist, [(a, K(-1.5, 0), 30), (a + 2.0, K(-1.0, 0), 20), (tHist - 0.3, K(-1.0, 0), 24)], **CL, ships=fleet(a, tHist, 22, names=SURVIVORS), rings=[ring(4, a, -30, "", False)],
  labels=[lb(a, 0, 4.0, "LITTLE LOCAL FALLOUT", W("p33", "little"), AMBER), lb(a, 0, -4.0, "AIR BURST: NO PLUME DRAWN", W("p33", "air"), WHITE)], legend=LEG7)
tAfter = W("p33", "after")
R("c5-bikfall", tHist, tAfter + 1.0, [(tHist, KB(0, 0), 60), (tAfter, KB(0, 0), 36), (tAfter + 0.8, KB(0, 0), 30)], tag="REAL HISTORY", clock="1946", clockLabel="ABLE · AFTERWARD", grid=False, zones=[LAGZ], ships=lagoon(tHist, tAfter + 1.0), source=SRC_BK,
  labels=[lb(tHist, 0, 0, "HISTORY AGREES, IN ONE NARROW WAY", tHist + 0.4, WHITE, at=BK)])
tMost = W("p33", "most")
boats = [jet(tAfter + 1.0, S("p34"), [KB(-20 + 3 * i, -10), KB(TARGETS[8 + 7 * i][0], TARGETS[8 + 7 * i][1] - 0.5)], tAfter + 1.0 + 0.2 * i, tAfter + 1.2 + 0.2 * i, tAfter + 4.2 + 0.2 * i, size=10, color=TEAL) for i in range(5)]
R("c5-reboard", tAfter + 1.0, S("p34"), [(tAfter + 1.0, KB(0, 0), 30), (tMost, KB(0, 0), 20), (S("p34") - 0.4, KB(0, 0), 16)], tag="REAL HISTORY", clock="1946", clockLabel="ABLE · THE NEXT DAY", grid=False, zones=[LAGZ],
  ships=lagoon(tAfter + 1.0, S("p34"), size=12, sunk={4: -9}) + boats, labels=[lb(tAfter + 1.0, 0, 0, "MOST SHIPS REBOARDED WITHIN A DAY", tMost, TEAL, at=BK)], source=SRC_BK)

# ================================================================== Chapter 06: the day after [SIMULATION]
a = S("p34")
chapter("c6-card", a, a + 3.7, "CHAPTER 06", "The day after", "SIMULATION")
a += 3.7


def scatter_paths(a, b, names=None, dist=14.0, ang0=0.0):
    names = names or SURVIVORS
    out = {}
    for n in names:
        dx, dy = OFF[n]
        cx, cy = dx + 2.5, dy
        r = math.hypot(cx, cy) or 1.0
        ux, uy = (cx / r, cy / r) if r > 0.1 else (0.0, 1.0)
        out[n] = [K(dx, dy), K(dx + ux * dist, dy + uy * dist)]
    return out


tEscT = W("p34", "Escorts")
tScat = W("p34", "scattering")
R("c6-scatter", a, tEscT, [(a, K(-2.5, 0), 14), (a + 1.6, K(-2.5, 0), 24), (tEscT - 0.3, K(-2.5, 0), 34)], **clk(a, tEscT, "THE FIRST MINUTE"), ships=fleet(a, tEscT, 24, names=SURVIVORS, labels={"CV": "CARRIER"}), legend=GEN,
  labels=[lb(a, -2.5, 5.4, "A RING OF SHIPS", W("p34", "ring"), WHITE)], cities=[mk(a, 0, 0, "BURST POINT", a + 0.1, RED, "target", 5)], caption="In the first minute, the answer on the map is a ring of ships scattering.")
tWeap = W("p34", "second")
R("c6-out", tEscT, W("p34", "This"), [(tEscT, K(-2.5, 0), 34), (tEscT + 2.0, K(-2.5, 0), 60), (tWeap, K(-2.5, 0), 90), (W("p34", "This") - 0.3, K(-2.5, 0), 100)], **clk(tEscT, W("p34", "This"), "THE FIRST MINUTE"),
  ships=fleet(tEscT, W("p34", "This"), 22, names=SURVIVORS, paths=scatter_paths(tEscT, W("p34", "This"), dist=26.0), labels={"CV": "CARRIER"}),
  lines=[ln(tEscT, K(dx + 2.5 - 2.5, dy), K((dx + 2.5) * 6 - 2.5, dy * 6 if abs(dy) > 0.1 else 0), tEscT + 0.8 + 0.12 * i, tEscT + 2.4 + 0.12 * i, YELLOW, dashed=True, width=2) for i, (dx, dy) in enumerate([OFF[n] for n in SURVIVORS if n != "CV" and n != "AO"])],
  labels=[lb(tEscT, -2.5, 16, "ESCORTS TURN OUTWARD, AT SPEED", tEscT + 0.4, YELLOW), lb(tEscT, -2.5, -16, "NO SECOND WEAPON COULD CATCH THEM ALL", tWeap + 0.2, WHITE)], legend=GEN)
R("c6-doctrine", W("p34", "This"), S("p35"), [(W("p34", "This"), K(-2.5, 0), 100), (W("p34", "This") + 1.5, K(-2.5, 0), 125)], **clk(W("p34", "This"), S("p35"), "THE FIRST MINUTE"),
  ships=fleet(W("p34", "This"), S("p35"), 22, names=SURVIVORS, paths={k: [v[1], [v[1][0] + (v[1][0] - v[0][0]) * 0.8, v[1][1] + (v[1][1] - v[0][1]) * 0.8]] for k, v in scatter_paths(0, 0, dist=26.0).items()}),
  labels=[lb(W("p34", "This"), -2.5, 22, "DOCTRINE IN OUR SIMULATION", W("p34", "doctrine"), YELLOW), lb(W("p34", "This"), -2.5, -22, "NOT AN ENGINE RESULT", W("p34", "engine"), YELLOW)], legend=GEN)
a = S("p35")
tRes = W("p35", "Rescue")
DARK = [K(1.4 * math.cos(math.radians(d)), 1.4 * math.sin(math.radians(d))) for d in range(0, 360, 12)]
POST = lambda a_, b_, w_: fleet(a_, b_, w_, names=SURVIVORS)  # noqa: E731
R("c6-dark", a, tRes, [(a, K(0, 0), 5), (a + 2.4, K(-0.5, 0), 9), (tRes - 0.3, K(-1.0, 0), 12)], **clk(a, tRes, "THE FIRST HOUR"), zones=[{"points": DARK, "color": "#1A2430", "fillOpacity": 0.85, "strokeWidth": 2.0, "solid": True, "label": "DARK WATER", "t": L(a, W("p35", "dark"))}],
  ships=fleet(a, tRes, 11, names=["CV", "E1", "E5"]), cities=[mk(a, 0, 0, "WHERE THE ESCORT WAS", a + 0.4, RED, "ring", 6)], legend=GEN, caption="On the destroyed escort's position, a wide patch of dark water.")
tHeads = W("p35", "head")
rescue = [jet(tRes, W("p35", "a", 2), [K(-2.5, 0.2), K(0.2, 0.1)], tRes + 0.2, tRes + 0.2, tRes + 3.0, size=14, color=TEAL, label="RESCUE BOATS"),
          jet(tRes, W("p35", "a", 2), [K(-1.25, 2.1), K(0.0, 0.4)], tRes + 0.9, tRes + 0.9, tRes + 3.4, size=12, color=TEAL, label="HELICOPTERS"), jet(tRes, W("p35", "a", 2), [K(-1.25, -2.1), K(0.1, -0.4)], tRes + 1.3, tRes + 1.3, tRes + 3.4, size=12, color=TEAL)]
tLook = W("p35", "look")
R("c6-rescue", tRes, W("p35", "Whether"), [(tRes, K(-0.6, 0), 12), (tRes + 1.8, K(-0.6, 0), 9), (tLook, K(-0.4, 0.4), 6), (W("p35", "Whether") - 0.3, K(-0.4, 0.3), 8)], **clk(tRes, W("p35", "Whether"), "THE FIRST HOUR"), zones=[{"points": DARK, "color": "#1A2430", "fillOpacity": 0.85, "strokeWidth": 2.0, "solid": True}],
  ships=fleet(tRes, W("p35", "Whether"), 9, names=["CV", "E5"]) + fleet(tRes, W("p35", "Whether"), 9, names=["E1"], labels={"E1": "A NEIGHBOR SHIP"}, paths={"E1": [K(-1.25, 2.165), K(-0.3, 0.9), K(0.0, 0.5)]}) + rescue, labels=[lb(tRes, 0, -0.3, "LOOKING FOR SURVIVORS", tLook, TEAL)],
  legend=GEN, caption="Rescue boats and helicopters from the other ships head in.")
R("c6-notoll", W("p35", "Whether"), S("p36"), [(W("p35", "Whether"), K(-0.3, 0.3), 8), (W("p35", "Whether") + 1.8, K(-0.3, 0.3), 12), (S("p36") - 0.3, K(-0.3, 0.3), 16)], **clk(W("p35", "Whether"), S("p36"), "THE FIRST HOUR"), zones=[{"points": DARK, "color": "#1A2430", "fillOpacity": 0.85, "strokeWidth": 2.0, "solid": True}],
  ships=fleet(W("p35", "Whether"), S("p36"), 12, names=["E1", "CV", "E5"]), labels=[lb(W("p35", "Whether"), 0, 1.0, "WHETHER ANYONE IS THERE: NOT COMPUTED", W("p35", "something"), YELLOW), lb(W("p35", "Whether"), 0, -1.2, "NO DEATH TOLL IN THIS EPISODE", W("p35", "death"), WHITE)], legend=GEN)
a = S("p36")
tFaint = W("p36", "at")
R("c6-noplume", a, W("p36", "at", 1), [(a, K(-1.5, 0), 22), (a + 2.0, K(0, 0), 30), (W("p36", "at") - 0.3, K(1.0, 0), 34)], **clk(a, W("p36", "at"), "THE FIRST HOUR"), ships=fleet(a, W("p36", "at"), 26, names=SURVIVORS), legend=GEN,
  labels=[lb(a, 0, 4.0, "LITTLE LOCAL FALLOUT", a + 0.4, AMBER), lb(a, 0, -4.0, "NO PLUME TO FLEE ON THE MAP", W("p36", "plume"), WHITE)], rings=[ring(4, a, -30, "", False)])
tTeams = W("p36", "Teams")
R("c6-band", W("p36", "at"), tTeams, [(W("p36", "at"), K(1.0, 0), 34), (W("p36", "at") + 1.4, K(5.0, 0), 40)], **clk(W("p36", "at"), tTeams, "THE FIRST HOUR"), ships=fleet(W("p36", "at"), tTeams, 30, names=SURVIVORS), legend=GEN,
  plume={"at": B, "bearing": 90, "lengthKm": 16, "widthKm": 2.4, "t0": 0.2, "t1": 2.8, "color": AMBER, "label": "FAINT BAND, DRIFTING EAST"}, caption="At most a faint band drifting east. Our wind choice.")
tWashR = W("p36", "wash-down") if any(w["unit"] == "p36" and w["word"].strip(".,").lower() == "wash-down" for w in WORDS) else W("p36", "and", 2)
tAtB = W("p36", "At", 2)
meter = [jet(tTeams, tAtB, [K(-9, 3.0 - 1.4 * i), K(-3.6 + 0.2 * i, 0.9 - 0.5 * i)], tTeams + 0.2 + 0.4 * i, tTeams + 0.2 + 0.4 * i, tTeams + 3.2 + 0.4 * i, size=12, color=TEAL, label=("METER TEAM" if i == 0 else None)) for i in range(3)]
R("c6-sweep", tTeams, tAtB, [(tTeams, K(-2.5, 0), 20), (tTeams + 1.4, K(-2.5, 0), 11), (tAtB - 0.4, K(-2.5, 0), 9)], **clk(tTeams, tAtB, "THE FIRST HOUR"), ships=fleet(tTeams, tAtB, 10, names=["CV", "AO", "E3", "E1", "E5"], labels={"CV": "CARRIER"}) + meter,
  labels=[lb(tTeams, -2.5, 2.6, "METER TEAMS SWEEP THE NEAREST HULLS", tTeams + 0.3, TEAL), lb(tTeams, -2.5, -2.6, "THE WASH-DOWN RUNS", tWashR, TEAL)], legend=GEN)
tHos = W("p36", "hosing")
R("c6-hosing", tAtB, S("p37"), [(tAtB, KB(0, 0), 60), (tHos, KB(0, 0), 30), (S("p37") - 0.4, KB(0, 0), 24)], tag="REAL HISTORY", clock="1946", clockLabel="BIKINI · BAKER", grid=False, zones=[LAGZ], source=SRC_BK,
  ships=lagoon(tAtB, S("p37"), size=11, colors={i: AMBER for i in range(len(TARGETS))}),
  labels=[lb(tAtB, 0, 3, "BIKINI: HOSING HELPED ONCE", tHos, TEAL, at=BK), lb(tAtB, 0, -3, "THEN IT FAILED: CREWS WOULD NOT COUNT ON IT", W("p36", "failed"), RED, at=BK)])
a = S("p37")
tAir2 = W("p37", "Aircraft")
air = [jet(a, S("p38"), [K(-20 + 4 * i, 14 - 6 * i), K(-6 + 2 * i, 4 - 2 * i), K(-2.5 + 12 * math.cos(math.radians(120 * i)), 12 * math.sin(math.radians(120 * i)))], a + 0.4 + 0.4 * i, a + 0.4 + 0.4 * i, a + 9, size=14, label=("AIRCRAFT ALOFT" if i == 0 else None)) for i in range(3)]
tDeck2 = W("p37", "usable")
R("c6-sky", a, tDeck2 + 0.6, [(a, K(-2.5, 0), 70), (a + 1.6, K(-2.5, 0), 40), (tAir2 + 1.0, K(-2.5, 0), 24), (tAir2 + 2.4, K(-2.5, 0), 9), (tDeck2 - 0.3, K(-2.5, 0), 5)], **clk(a, tDeck2 + 0.6, "THE FIRST HOUR"),
  ships=fleet(a, tDeck2 + 0.6, 12, names=SURVIVORS, labels={"CV": "CARRIER"}) + air[:2] + [jet(a, tDeck2 + 0.6, [K(-12, 5), K(-3.0, 0.1)], tAir2 + 0.5, tAir2 + 0.5, tAir2 + 4.5, size=14, label="LAUNCHED BEFORE THE BURST")], legend=GEN,
  labels=[lb(a, -2.5, 12, "THE SKY IS THE NEXT CHANGE", a + 0.3, WHITE), lb(a, -2.5, 1.4, "A DECK TO COME HOME TO", W("p37", "deck"), WHITE), lb(a, -2.5, -1.4, "ONLY IF IT IS STILL USABLE", W("p37", "only"), YELLOW)])
tDam = W("p37", "damaged")
R("c6-closed", tDeck2 + 0.6, W("p37", "and"), [(tDeck2 + 0.6, K(-2.5, 0), 5), (tDam, K(-2.5, 0), 3.2), (W("p37", "and") - 0.3, K(-2.5, 0), 4.2)], **clk(tDeck2 + 0.6, W("p37", "and"), "THE FIRST HOUR"), zones=[deck_zone(AMBER, 0.35)],
  zones_extra=[bar(tDeck2 + 0.6, (-2.65, 0.05), (-2.35, -0.05), tDam + 0.5, RED, 0.01, 0.9), bar(tDeck2 + 0.6, (-2.65, -0.05), (-2.35, 0.05), tDam + 0.8, RED, 0.01, 0.9)],
  labels=[lb(tDeck2, -2.5, 0.18, "DAMAGED DECK: SOME LANDINGS CLOSED", tDam + 0.6, RED)], legend=[{"text": "CARRIER TO SCALE: 333 M", "color": BLUE}])
tSupT = W("p37", "supply")
R("c6-tankers", W("p37", "and"), S("p38"), [(W("p37", "and"), K(-3.5, 0), 18), (tSupT + 0.8, K(-3.0, 0), 11), (S("p38") - 0.4, K(-3.0, 0), 14)], **clk(W("p37", "and"), S("p38"), "THE FIRST HOUR"), ships=fleet(W("p37", "and"), S("p38"), 12, names=["CV", "AO"], labels={"CV": "CARRIER", "AO": "SUPPLY SHIP"}) + [jet(W("p37", "and"), S("p38"), [K(-12, 6), K(-3.4, 0.6)], W("p37", "and") + 0.2, W("p37", "and") + 0.2, W("p37", "and") + 3.8, size=14, label="TANKER AIRCRAFT")],
  labels=[lb(W("p37", "and"), -3.0, -2.4, "SUPPLY SHIP AND TANKERS MATTER MORE", tSupT, YELLOW)], legend=GEN)
a = S("p38")
tRad2 = W("p38", "radar")
links = [("CV", "E1"), ("CV", "E5"), ("CV", "E3"), ("CV", "AO"), ("E1", "E2"), ("E5", "E4")]
R("c6-links", a, W("p38", "fail"), [(a, K(-2.5, 0), 16), (a + 2.0, K(-2.5, 0), 11), (W("p38", "fail") - 0.3, K(-2.5, 0), 14)], **clk(a, W("p38", "fail"), "THE FIRST HOUR"), ships=fleet(a, W("p38", "fail"), 12, names=SURVIVORS, labels={"CV": "CARRIER"}), legend=GEN,
  lines=[ln(a, K(*OFF[p]), K(*OFF[q]), a + 0.3 + 0.3 * i, a + 0.9 + 0.3 * i, TEAL, width=2) for i, (p, q) in enumerate(links)], labels=[lb(a, -2.5, 3.2, "RADIO AND RADAR LINKS", tRad2, TEAL)])
tFlag = W("p38", "flag")
R("c6-fail", W("p38", "fail"), W("p38", "Electromagnetic"), [(W("p38", "fail"), K(-2.5, 0), 14), (W("p38", "fail") + 1.2, K(-2.5, 0), 11), (tFlag, K(-2.5, 0), 9), (W("p38", "Electromagnetic") - 0.3, K(-2.5, 0), 12)], **clk(W("p38", "fail"), W("p38", "Electromagnetic"), "THE FIRST HOUR"),
  ships=fleet(W("p38", "fail"), W("p38", "Electromagnetic"), 11, names=SURVIVORS),
  lines=[ln(W("p38", "fail"), K(*OFF[p_]), K(*OFF[q_]), W("p38", "fail"), W("p38", "fail") + 0.1, RED, dashed=True, width=2) for p_, q_ in links],
  cities=[mk(W("p38", "fail"), OFF[n][0], OFF[n][1], None, tFlag + 0.25 * i, YELLOW, "ring", 5) for i, n in enumerate(["CV", "E1", "E5", "E3"])],
  labels=[lb(W("p38", "fail"), -2.5, 3.2, "LINKS NEAR THE BURST FAIL FOR A WHILE", W("p38", "fail") + 0.1, RED), lb(W("p38", "fail"), -2.5, -3.2, "THE GROUP SPEAKS BY FLAG AND LIGHT", tFlag, YELLOW)], legend=GEN)
R("c6-emp", W("p38", "Electromagnetic"), S("p39"), [(W("p38", "Electromagnetic"), K(-2.5, 0), 12), (W("p38", "Electromagnetic") + 1.6, K(-2.5, 0), 22), (S("p39") - 0.3, K(-2.5, 0), 30)], **clk(W("p38", "Electromagnetic"), S("p39"), "THE FIRST HOUR"), ships=fleet(W("p38", "Electromagnetic"), S("p39"), 20, names=SURVIVORS), legend=GEN,
  labels=[lb(W("p38", "Electromagnetic"), -2.5, 4.0, "EMP: NOT MODELED, NOT CLAIMED", W("p38", "pulse"), WHITE)])
a = S("p39")
tBridge = W("p39", "On")
fin = {n: [K(*OFF[n]), K(OFF[n][0] * 1 + (OFF[n][0] + 2.5) * 5, OFF[n][1] * 1 + OFF[n][1] * 6)] for n in SURVIVORS}
R("c6-spread", a, tBridge, [(a, K(-2.5, 0), 30), (a + 1.6, K(-2.5, 0), 55), (tBridge - 0.4, K(-2.5, 0), 80)], **clk(a, tBridge, "THE END OF THE HOUR"), ships=fleet(a, tBridge, 22, names=SURVIVORS, paths=fin, labels={"CV": "CARRIER"}), legend=GEN,
  labels=[lb(a, -2.5, 22, "SPREAD WIDE ACROSS THE SEA", W("p39", "spread"), WHITE)], caption="At the end of the hour, the group is spread wide across the sea.")
tMsg = W("p39", "message")
R("c6-bridge", tBridge, tMsg, [(tBridge, K(-3.0, 0), 5), (tBridge + 1.6, K(-2.5, 0), 1.2), (tMsg - 0.3, K(-2.5, 0), 1.6)], **clk(tBridge, tMsg, "THE CARRIER'S BRIDGE"), zones=[deck_zone(BLUE, 0.3)],
  cities=[mk(tBridge, -2.62, 0.04, "BRIDGE", tBridge + 0.5, WHITE, "base", 5)], rings=[{"at": K(-2.62, 0.04), "km": 0.03 + 0.03 * i, "color": TEAL, "t": L(tBridge, W("p39", "radar") + 0.3 * i), "dashed": False} for i in range(3)],
  labels=[lb(tBridge, -2.5, -0.2, "AN OFFICER WATCHES THE RADAR", W("p39", "watches"), TEAL)], legend=[{"text": "CARRIER TO SCALE: 333 M", "color": BLUE}])
tOne2 = W("p39", "one")
R("c6-message", tMsg, W("p39", "holds"), [(tMsg, K(-2.5, 0), 40), (tMsg + 2.4, K(-12, 0), 90), (W("p39", "holds") - 0.5, K(-22, 0), 140)], **clk(tMsg, W("p39", "holds"), "A MESSAGE TO SHORE"), ships=fleet(tMsg, W("p39", "holds"), 22, names=SURVIVORS, paths=fin, labels={"CV": "CARRIER"}),
  lines=[ln(tMsg, K(-2.5, 0), K(-90, 0), tMsg + 0.2, tMsg + 3.0, TEAL, "TO SHORE", dashed=True, width=3)], legend=GEN,
  labels=[lb(tMsg, -20, 6, "ONE BURST", tOne2, RED), lb(tMsg, -20, 0, "ONE ESCORT GONE", W("p39", "escort"), RED), lb(tMsg, -20, -6, "SOURCE UNKNOWN", W("p39", "source"), YELLOW)])
tAns2 = W("p39", "answer")
tWait = W("p39", "wait")
R("c6-choice", W("p39", "holds"), W("p39", "Nobody"), [(W("p39", "holds"), K(-2.5, 0), 30), (tAns2, K(-2.5, 0), 40), (tWait + 0.6, K(-2.5, 0), 60)], **clk(W("p39", "holds"), W("p39", "Nobody"), "THE CHOICE"), ships=fleet(W("p39", "holds"), W("p39", "Nobody"), 40, names=["CV"], labels={"CV": "CARRIER"}),
  lines=[ln(W("p39", "holds"), K(-2.5, 0), K(-2.5 + 12, 8), tAns2, tAns2 + 1.0, RED, "ANSWER AT ONCE", width=3), ln(W("p39", "holds"), K(-2.5, 0), K(-2.5 + 12, -8), tWait, tWait + 1.0, TEAL, "WAIT", width=3)],
  labels=[lb(W("p39", "holds"), -2.5, 14, "THE CHOICE THE EPISODE LED TO", W("p39", "choice"), WHITE), lb(W("p39", "holds"), 6, 16, "NOTHING KNOWN", W("p39", "nothing"), RED), lb(W("p39", "holds"), 6, -16, "LET THE SEA STAY QUIET", W("p39", "sea", 2), TEAL)], legend=GEN)
R("c6-undecided", W("p39", "Nobody"), S("p40"), [(W("p39", "Nobody"), K(-2.5, 0), 60), (W("p39", "Nobody") + 1.6, K(-2.5, 0), 110), (S("p40") - 0.3, K(-2.5, 0), 170)], **clk(W("p39", "Nobody"), S("p40"), "NOBODY HAS DECIDED"), ships=fleet(W("p39", "Nobody"), S("p40"), 22, names=["CV"], labels={"CV": "CARRIER"}),
  cities=[mk(W("p39", "Nobody"), -2.5, 0, "NOBODY HAS DECIDED", W("p39", "Nobody") + 0.2, YELLOW, "ring", 10)], legend=GEN)

# ------------------------------------------------------------------ End slate
add(id="end", type="endslate", start=round(S("p40"), 3), end=END, tag="", title="Next scenario", line="Kaliningrad and the Suwalki gap: NATO cuts off the enclave.")

# ------------------------------------------------------------------ audio plan and output
booms = [FL + 0.1, DETT + 0.1]
b0 = round(min(FL - 0.3, W("p02", "simulation") - 0.3), 2)
for s in shots:
    s.pop("zones_", None)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p17") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p17") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
    d = s["end"] - s["start"]
    late = ""
    for key in ("labels", "cities", "rings", "ships", "lines", "markers"):
        for it in s.get(key, []):
            t_ = it.get("t", it.get("t0"))
            if isinstance(t_, (int, float)) and t_ > d - 1.2 and d > 3 and t_ > 0:
                late = "  late-arrival"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {d:5.1f}{flag}{late}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
