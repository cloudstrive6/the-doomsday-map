"""Director pass for episode 007: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 007-carrier-group-nuke-at-sea
No ship, country or date is named. The engine has no sea model: every strike picture is a region shot on open water
(no city file), views of 15 to 20 km where the rings are, and ship icons are enlarged and labelled as such.
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
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


HERO = sc["strikes"][0]
FX = HERO["effects"]
B = [HERO["target_lon"], HERO["target_lat"]]       # burst point over the lead destroyer (simulated, open Pacific)
SUBP = [HERO["launch_lon"], HERO["launch_lat"]]    # attacker's submarine (simulated)
KX, KY = 101.7, 110.57                             # km per degree at 24 N


def K(dx, dy, at=None):
    at = at or B
    return [round(at[0] + dx / KX, 5), round(at[1] + dy / KY, 5)]


IWO, MARCUS, GUAM, TOKYO, WAKE, HONOLULU = [141.32, 24.78], [153.98, 24.29], [144.79, 13.44], [139.69, 35.69], [166.65, 19.29], [-157.86, 21.31]
BIKINI, SANDIEGO, WIGWAM, WASH = [165.5, 11.6], [-117.16, 32.72], [-126.0, 29.0], [-77.04, 38.9]
CUBA_SEA = [-73.0, 22.5]
CUBA_ISO, USA_ISO = "192", "840"
HL_US = {"iso": USA_ISO, "color": BLUE, "fill": "rgba(110,168,255,0.06)"}
HL_CUBA = {"iso": CUBA_ISO, "color": WHITE, "fill": "rgba(255,255,255,0.05)"}

# the generic group, offsets in km from the burst point (lead destroyer at the centre; carrier 2.5 km away)
FLEET = {
    "DD1": ((0.0, 0.0), 12, "Lead destroyer"), "CV": ((1.77, -1.77), 19, "Carrier"), "DD2": ((-0.9, 1.1), 12, "Destroyer"),
    "DD3": ((-3.2, -1.4), 12, "Destroyer"), "DD4": ((2.4, 4.0), 12, "Destroyer"), "CG": ((-1.0, -3.6), 14, "Cruiser"),
    "AO": ((4.5, -3.0), 13, "Supply ship"), "SSN": ((6.0, 2.5), 9, "Submarine"),
}
FPOS = {k: K(*v[0]) for k, v in FLEET.items()}

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


def lk(a, dx, dy, text, t, color=WHITE):
    """label placed dx, dy km from the burst point"""
    return lab(a, K(dx, dy), text, t, color)


def missile(a, path, t0, t1, label="Missile", color=RED, t_on=None):
    return {"path": path, "t0": rel(a, t0), "t1": rel(a, t1), "kind": "pla", "color": color, "label": label, "t": rel(a, t0 if t_on is None else t_on), "wake": True}


def hull(a, b, nm, t=None, label=True, drift=(0.0, 0.0), sunk=None, size=None, lab_text=None):
    """one group ship; t = absolute appearance time (default the shot start). drift: km it moves north-east to reach its place."""
    (dx, dy), sz, name = FLEET[nm]
    end = K(dx, dy)
    start = K(dx - drift[0], dy - drift[1])
    if start == end:
        start = K(dx - 0.04, dy)
    d = {"_id": nm, "path": [start, end], "t0": 0, "t1": round(b - a, 2), "kind": "us", "color": BLUE, "size": size or sz, "t": 0 if t is None else rel(a, t), "wake": False}
    if label:
        d["label"] = lab_text or name
    if sunk:
        d["sunkAt"] = rel(a, sunk)
    return d


def fleet(a, b, names=None, drift=(0.0, 0.0), times=None, labels=None):
    times = times or {}
    names = names or list(FLEET)
    return [hull(a, b, n, t=times.get(n), label=(labels is None or n in labels), drift=drift, lab_text=(labels or {}).get(n)) for n in names]


def lt(a, b, t):
    """shot-local camera time: "s" start, "e" end, a number below the shot start is already local, a larger one is absolute"""
    if t == "s":
        return 0
    if t == "e":
        return round(b - a, 2)
    return round(t, 2) if t < a else round(max(0.0, t - a), 2)


def cam(a, b, *keys):
    out = []
    for t, c, w in keys:
        tt = lt(a, b, t)
        out.append({"t": tt, "center": c, "widthKm": w})
    return out


def reg(sid, a, b, keys, tag="SIMULATION", **kw):
    c = cam(a, b, *keys)
    add(id=sid, type="region", start=a, end=b, tag=tag, view={"center": c[0]["center"], "widthKm": c[0]["widthKm"]}, camera=c, **kw)


def glob(sid, a, b, keys, tag="SIMULATION", sun=SUN, **kw):
    add(id=sid, type="globe", start=a, end=b, tag=tag, camera=[{"t": lt(a, b, t), "lat": la, "lon": lo, "scale": sc_} for t, la, lo, sc_ in keys], sun=sun, **kw)


def chapter(sid, a, dur, kicker, title, tag):
    add(id=sid, type="chapter", start=a, end=round(a + dur, 2), tag=tag, kicker=kicker, title=title)
    return round(a + dur, 2)


RINGS = [("Fireball", FX["fireball_km"], WHITE, f"Fireball {FX['fireball_km'] * 1000:.0f} m radius"), ("20 psi", FX["psi20_km"], ORANGE, f"20 psi {FX['psi20_km'] * 1000:.0f} m"),
         ("5 psi", FX["psi5_km"], RED, f"5 psi {FX['psi5_km']:.2f} km"), ("Burns", FX["thermal3_km"], AMBER, f"Third-degree burns {FX['thermal3_km']:.1f} km"),
         ("1 psi", FX["psi1_km"], TEAL, f"Broken windows {FX['psi1_km']:.1f} km")]
LEGEND = [{"text": r[3], "color": r[2]} for r in RINGS]
ENG = "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"


def disc(km, t, label=None, color=WHITE, at=None):
    """a circle as a zone polygon (very small rings are not drawn by the ring layer)"""
    at = at or B
    pts = [K(km * math.cos(math.radians(d)), km * math.sin(math.radians(d)), at) for d in range(0, 360, 10)]
    z = {"points": pts, "color": color, "t": t}
    if label:
        z["label"] = label
    return z


def ring(i, t, label=True, dashed=False):
    nm, km, col, _ = RINGS[i]
    d = {"at": B, "km": km, "color": col, "t": t}
    if label:
        d["label"] = nm
    if dashed:
        d["dashed"] = True
    return d


def prior(n):
    return [ring(i, -30) for i in range(n)]


def clk(sec):
    sec = max(0, int(round(sec)))
    return f"T+{sec // 60:02d}:{sec % 60:02d}"


SIMLOC = "Simulated location"

# ================================================================== Cold open [SIMULATION]
FLASH = round(W("p01", "bursts") - 0.12, 2)
tF = FLASH
CVP, DD1P = FPOS["CV"], FPOS["DD1"]
# --- run-up under the stakes line, a real map with real places and a missile moving
glob("open-run", 0, tF, [("s", 27, 143, 1500), (1.8, 25.5, 148, 2200), ("e", 24.2, 153.5, 3200)], clock="T+19:10", clockLabel="AFTER LAUNCH", clockRate=10,
     markers=[{"at": TOKYO, "label": "Japan", "color": WHITE, "kind": "dot", "t": 0.2}, {"at": IWO, "label": "Iwo Jima", "color": WHITE, "kind": "dot", "t": 0.7}, {"at": GUAM, "label": "Guam", "color": WHITE, "kind": "dot", "t": 1.2},
              {"at": SUBP, "label": "Submarine (simulated)", "color": RED, "kind": "sub", "size": 5, "t": 0.4}, {"at": B, "label": "US carrier group (simulated)", "color": BLUE, "kind": "target", "size": 6, "t": 2.0}],
     arcs=[{"from": SUBP, "to": B, "t0": 0.3, "t1": tF - 0.1, "color": RED, "loft": 0.1}])
tS2 = S("p02")
reg("open-flash", tF, tS2, [("s", B, 20), (2.0, K(1.0, 0), 16), ("e", K(1.0, -0.6), 13)], clock="01:10", clockLabel="LOCAL TIME · NIGHT", clockRate=0, source="",
    burst={"at": B, "t": 0.1, "km": 1.6, "fade": 7}, ships=fleet(tF, tS2, ["DD1", "CV", "DD2"], labels={}),
    rings=[ring(2, 0.7, True)], labels=[lk(tF, 0.0, 1.9, "Burst over the lead destroyer", tF + 1.2, RED)],
    caption="Simulation: it has not happened.")
tp3c = W("p03", "one", 2)
reg("open-b", tS2, S("p03"), [("s", K(1.0, -0.6), 13), (2.8, K(0.6, -0.4), 17), ("e", K(0.3, -0.2), 21)], clock="01:10", clockLabel="LOCAL TIME · NIGHT", clockRate=0,
    burst={"at": B, "t": -3.0, "km": 1.6, "fade": 7}, ships=fleet(tS2, S("p03"), ["DD1", "CV", "DD2", "DD3"], labels={"CV": "Carrier, 2.5 km away"}),
    rings=[ring(2, -30), ring(4, 0.4, True)], labels=[lk(tS2, -2.6, 3.0, "Ring sizes: engine", W("p02", "published") , WHITE), lk(tS2, -2.6, -3.9, "Ships and glow: enlarged", W("p02", "from"), YELLOW)])
p3a, p3b = W("p03", "It", 1), W("p03", "toward")
glob("open-launch", S("p03"), p3a, [("s", 24, 148, 1700), ("e", 24, 152, 2300)], clock="T-20:00", clockLabel="TO BURST", clockRate=70,
     markers=[{"at": SUBP, "label": "Submarine (simulated)", "color": RED, "kind": "sub", "size": 5, "t": rel(S("p03"), W("p03", "submarine"))}, {"at": B, "label": "Strike group", "color": BLUE, "kind": "target", "size": 6, "t": rel(S("p03"), W("p03", "ten"))}],
     arcs=[{"from": SUBP, "to": B, "t0": rel(S("p03"), W("p03", "fires")), "t1": rel(S("p03"), W("p03", "It")) + 2.0, "color": RED, "loft": 0.15}], caption="Ten to one, local time. One missile.")
reg("open-flight", p3a, p3b, [("s", [153.2, 24.1], 700), (2.0, [153.6, 24.1], 480), ("e", [154.4, 24.05], 330)], clock="T-14:40", clockLabel="TO BURST", clockRate=70,
    cities=[city(p3a, SUBP, "Launch point", p3a + 0.1, RED, "sub", 5), city(p3a, MARCUS, "Minami-Torishima (Japan)", p3a + 1.0, WHITE, "dot")],
    ships=[missile(p3a, [SUBP, B], p3a, p3b + 3.5, "Missile: 10 kt warhead", t_on=p3a)],
    labels=[lab(p3a, [153.0, 24.6], "A small weapon: 10 kt", W("p03", "ten"), YELLOW), lab(p3a, [154.0, 23.6], "Low over black water", W("p03", "low"), WHITE)])
reg("open-group", p3b, S("p04"), [("s", [154.5, 24.05], 90), (2.0, K(-1.0, 0.0), 40), ("e", K(0, 0), 26)], clock="T-03:20", clockLabel="TO BURST", clockRate=70,
    ships=fleet(p3b, S("p04"), drift=(0.0, 0.7), times={"DD1": p3b + 0.2, "CV": W("p03", "one", 2), "DD2": p3b + 0.4, "DD3": p3b + 0.6, "DD4": p3b + 0.8, "CG": p3b + 1.0, "AO": p3b + 1.2, "SSN": p3b + 1.4}, labels={"CV": "Carrier: about 100,000 t"}),
    labels=[lk(p3b, -4.0, 5.0, "A group of ships", W("p03", "group"), WHITE)])
# p04
a = S("p04")
tNo = W("p04", "nobody")
tQ = W("p04", "question")
reg("open-dark", a, tNo, [("s", K(0, 0), 28), ("e", K(0, 0), 36)], clock="T-01:40", clockLabel="TO BURST", clockRate=7,
    ships=fleet(a, tNo, drift=(0.0, 0.5), labels={}), legend=[{"text": "US GROUP (ENLARGED ICONS)", "color": BLUE}],
    labels=[lk(a, -5.0, 6.5, "Steaming in the dark", W("p04", "steaming"), WHITE), lk(a, 4.5, 6.5, "Spread across the sea", W("p04", "spread"), WHITE)])
reg("open-bridge", tNo, tQ, [("s", K(1.8, -1.8), 16), ("e", K(1.8, -1.8), 11)], clock="T-00:55", clockLabel="TO BURST", clockRate=7,
    ships=fleet(tNo, tQ, ["CV", "DD1", "DD2", "DD3"], drift=(0.0, 0.3), labels={"CV": "Carrier"}),
    labels=[lk(tNo, 1.8, 0.6, "Nobody on the bridge knows yet", W("p04", "knows"), YELLOW)])
reg("open-question", tQ, S("p05"), [("s", B, 12), (2.2, B, 15), (4.0, B, 20), ("e", B, 23)], clock="T-00:30", clockLabel="TO BURST", clockRate=7,
    ships=fleet(tQ, S("p05"), ["CV", "DD1", "DD2", "DD3"], labels={}),
    rings=[ring(4, rel(tQ, W("p04", "far")), True, dashed=True)],
    labels=[lk(tQ, -2.0, 4.6, "What does one small bomb do to a ship that big?", W("p04", "bomb"), YELLOW), lk(tQ, 3.0, -4.6, "How far does the damage reach?", W("p04", "damage"), WHITE)])

# ================================================================== Chapter 01 [REAL DATA]
a = chapter("c1-card", S("p05"), 3.5, "CHAPTER 01", "The ships and the test", "REAL DATA")
SRC_W = "Nuclear Weapon Archive; Operation Wigwam records"
tHung, tThirty, tIt = W("p05", "hung"), W("p05", "thirty"), W("p05", "it")
reg("w-where", a, tHung, [("s", [-120.0, 31.5], 2600), (2.2, [-121.0, 31.0], 1900), ("e", [-121.5, 30.6], 1600)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W, highlight=[HL_US],
    cities=[city(a, SANDIEGO, "San Diego", a + 0.2, BLUE, "base", 5), city(a, WIGWAM, "Wigwam: about 500 miles away", W("p05", "southwest"), RED, "target", 7)],
    lines=[{"from": SANDIEGO, "to": WIGWAM, "color": WHITE, "dashed": True, "t0": rel(a, W("p05", "southwest")), "t1": rel(a, W("p05", "southwest")) + 1.5, "label": "500 miles"}])
reg("w-cable", tHung, tThirty, [("s", WIGWAM, 160), (3.0, WIGWAM, 60), ("e", WIGWAM, 28)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W,
    cities=[city(tHung, WIGWAM, "30 kt device on a cable, 2,000 ft down", W("p05", "thirty-kiloton"), RED, "target", 7)],
    rings=[{"at": WIGWAM, "km": 4, "color": RED, "dashed": True, "t": rel(tHung, W("p05", "cable"))}],
    labels=[lab(tHung, K(-2.0, -4.2, WIGWAM), "Deep ocean", W("p05", "deep"), WHITE)])
fl = [K(dx, dy, WIGWAM) for dx, dy in [(-8, 4), (-7, -3), (-9, 0), (-6, 6), (-10, -5), (-5, -6), (-9, 7), (-7, 1)]]
reg("w-ships", tThirty, tIt, [("s", WIGWAM, 30), (2.0, WIGWAM, 36), ("e", WIGWAM, 44)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W,
    cities=[city(tThirty, WIGWAM, "Wigwam", tThirty + 0.1, RED, "target", 6)],
    ships=[{"path": [p, [p[0] + 0.01, p[1]]], "t0": 0, "t1": 8, "kind": "us", "color": BLUE, "size": 11, "t": rel(tThirty, tThirty + 0.2 + 0.25 * i), "wake": False, "label": ("30 ships" if i == 0 else "")} for i, p in enumerate(fl)],
    labels=[lab(tThirty, K(5.0, 7.0, WIGWAM), "About 6,800 people", W("p05", "sixty-eight"), YELLOW)], caption="Thirty ships. Icons enlarged.")
glob("w-only", tIt, S("p06"), [("s", 30, -132, 1000), (3.0, 30, -124, 1200), ("e", 30, -118, 1500)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W, highlight=[HL_US],
     markers=[{"at": WIGWAM, "label": "Wigwam, 1955", "color": RED, "kind": "target", "size": 6, "t": 0.2}, {"at": SANDIEGO, "label": "San Diego", "color": BLUE, "kind": "base", "size": 5, "t": 1.4}, {"at": [-125.0, 38.0], "label": "The only test fired in deep water", "color": YELLOW, "kind": "dot", "t": rel(tIt, W("p05", "only"))}],
     arcs=[{"from": SANDIEGO, "to": WIGWAM, "t0": 0.6, "t1": 2.4, "color": WHITE, "loft": 0.1}])
a = S("p06")
tDw = W("p06", "two")
reg("w-upwind", a, tDw, [("s", WIGWAM, 26), (2.5, WIGWAM, 22), ("e", WIGWAM, 19)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W,
    cities=[city(a, WIGWAM, "Ground zero", a + 0.1, RED, "target", 6)],
    rings=[{"at": WIGWAM, "km": 8, "color": WHITE, "dashed": True, "t": rel(a, W("p06", "five")), "label": "5 miles = 8 km"}],
    ships=[{"path": [K(-6.2, 4.6, WIGWAM), K(-6.1, 4.6, WIGWAM)], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 11, "t": rel(a, W("p06", "ships")), "wake": False, "label": "Most ships: upwind"},
           {"path": [K(-7.0, -1.6, WIGWAM), K(-6.9, -1.6, WIGWAM)], "t0": 0, "t1": 5, "kind": "us", "color": BLUE, "size": 11, "t": rel(a, W("p06", "ships")) + 0.2, "wake": False}])
reg("w-downwind", tDw, S("p07"), [("s", WIGWAM, 22), (3.0, K(2, 0, WIGWAM), 26), ("e", K(3, 0, WIGWAM), 30)], tag="REAL DATA", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W,
    rings=[{"at": WIGWAM, "km": 8, "color": WHITE, "dashed": True, "t": -30}], cities=[city(tDw, WIGWAM, "Ground zero", tDw + 0.1, RED, "target", 6)],
    ships=[{"path": [K(7.9, 1.8, WIGWAM), K(8.0, 1.8, WIGWAM)], "t0": 0, "t1": 8, "kind": "us", "color": BLUE, "size": 11, "t": rel(tDw, W("p06", "heavily")), "wake": False, "label": "Shielded ship"},
           {"path": [K(7.7, -2.2, WIGWAM), K(7.8, -2.2, WIGWAM)], "t0": 0, "t1": 8, "kind": "us", "color": BLUE, "size": 11, "t": rel(tDw, W("p06", "heavily")) + 0.4, "wake": False, "label": "Shielded ship"}],
    plume={"at": WIGWAM, "bearing": 90, "lengthKm": 10, "widthKm": 4, "t0": rel(tDw, W("p06", "base")), "t1": rel(tDw, W("p06", "base")) + 2.5, "color": AMBER, "label": "Base surge"},
    labels=[lab(tDw, K(1.5, 7.5, WIGWAM), "By one account: under the dose limit", W("p06", "limit"), YELLOW)])
a = S("p07")
reg("q1", a, S("p08"), [("s", K(0, 0), 17), (2.5, K(0.6, -0.4), 21), (4.8, K(0, 0), 24), ("e", K(0, 0), 27)], clock="", source="",
    ships=fleet(a, S("p08"), ["CV", "DD1", "DD2", "DD3", "DD4", "CG"], labels={}), rings=[ring(4, 0.5, False, dashed=True)],
    labels=[lk(a, -3.0, 4.8, "One burst", W("p07", "burst"), RED), lk(a, 2.6, -4.8, "One group", W("p07", "group"), BLUE), lk(a, -3.2, -4.8, "What does the sea do with it?", W("p07", "what"), YELLOW)])
a = S("p08")
tFive, tAir = W("p08", "five"), W("p08", "its")
reg("cv-tons", a, tFive, [("s", CVP, 9), (2.0, CVP, 7), ("e", CVP, 6)], tag="REAL DATA", clock="", source="US Navy fact file; Congressional Research Service",
    ships=fleet(a, tFive, ["CV"], labels={"CV": "Nimitz class"}), legend=[{"text": "ICON ENLARGED: REAL LENGTH 333 M", "color": BLUE}],
    labels=[lab(a, K(1.77, -0.9), "About 100,000 tons", W("p08", "hundred"), YELLOW)])
reg("cv-people", tFive, tAir, [("s", CVP, 6), (1.5, CVP, 8), ("e", CVP, 10)], tag="REAL DATA", clock="", source="US Navy fact file; Congressional Research Service",
    ships=fleet(tFive, tAir, ["CV"], labels={}), labels=[lab(tFive, K(1.77, -0.9), "About 5,000 people aboard", W("p08", "five") + 0.2, YELLOW)])
reg("cv-wing", tAir, S("p09"), [("s", CVP, 10), (1.6, CVP, 13), ("e", CVP, 17)], tag="REAL DATA", clock="", source="US Navy fact file; Congressional Research Service",
    ships=fleet(tAir, S("p09"), ["CV"], labels={}) + [{"path": [K(1.77 + 0.4 * i, -1.77 + 0.5, ), K(1.77 + 0.4 * i + 0.4, -1.77 + 1.4)], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 7, "t": rel(tAir, W("p08", "sixty")) + 0.12 * i, "wake": False} for i in range(6)],
    labels=[lab(tAir, K(3.4, -2.6), "Air wing: 60 aircraft or more", W("p08", "sixty"), YELLOW)])
a = S("p09")
tG = W("p09", "a", 2)
reg("grp-ships", a, tG, [("s", K(0, 0), 26), (2.0, K(0, 0), 20), ("e", K(0, 0), 24)], tag="REAL DATA", clock="", source="Congressional Research Service; US Navy",
    ships=fleet(a, tG, ["CV", "DD1", "DD2"], times={"CV": a, "DD1": W("p09", "three"), "DD2": W("p09", "three") + 0.3}, labels={"CV": "Carrier", "DD1": "Warship"}),
    labels=[lk(a, -4.0, 5.0, "Rarely alone", W("p09", "alone"), YELLOW)])
reg("grp-support", tG, S("p10"), [("s", K(0, 0), 24), (2.0, K(1.0, 0), 28), ("e", K(1.0, 0), 33)], tag="REAL DATA", clock="", source="Congressional Research Service; US Navy",
    ships=fleet(tG, S("p10"), times={"AO": W("p09", "supply"), "SSN": W("p09", "submarine"), "CG": W("p09", "warships") , "DD3": W("p09", "warships"), "DD4": W("p09", "warships") + 0.3, "DD1": tG - 5, "CV": tG - 5, "DD2": tG - 5}, labels={"AO": "Supply ship", "SSN": "Submarine (perhaps)", "CG": "Cruiser"}),
    legend=[{"text": "US GROUP (ENLARGED ICONS)", "color": BLUE}])
glob("old-test", S("p10"), S("p11"), [("s", 20, 175, 1500), ("e", 14, 168, 2300)], tag="REAL HISTORY", clock="", source="",
     markers=[{"at": BIKINI, "label": "Bikini, 1946", "color": RED, "kind": "target", "size": 6, "t": rel(S("p10"), W("p10", "scale"))}, {"at": B, "label": "Our site", "color": BLUE, "kind": "dot", "t": 0.3}],
     arcs=[{"from": B, "to": BIKINI, "t0": rel(S("p10"), W("p10", "shows")), "t1": rel(S("p10"), W("p10", "shows")) + 2.5, "color": WHITE, "loft": 0.2}])

# ================================================================== Chapter 02 [REAL HISTORY]
a = chapter("c2-card", S("p11"), 3.5, "CHAPTER 02", "How close it has come", "REAL HISTORY")
SRC_C = "Atomic Archive; Operation Crossroads records"
tOp, tAble, tMiss, tFive2 = W("p11", "operation"), W("p11", "first"), W("p11", "missed"), W("p11", "five")
LAG = [165.45, 11.55]
reg("bk-atoll", a, tOp, [("s", [166.0, 12.5], 1500), (2.0, [165.6, 11.8], 700), ("e", BIKINI, 330)], tag="REAL HISTORY", clock="JULY 1946", clockLabel="BIKINI", clockRate=0, source=SRC_C,
    cities=[city(a, BIKINI, "Bikini Atoll", W("p11", "bikini"), RED, "target", 7), city(a, [162.35, 11.35], "Kwajalein area", a + 0.3, WHITE, "dot")])
reg("bk-ships", tOp, tAble, [("s", LAG, 40), (2.5, LAG, 25), ("e", LAG, 18)], tag="REAL HISTORY", clock="JULY 1946", clockLabel="OPERATION CROSSROADS", clockRate=0, source=SRC_C,
    ships=[{"path": [K(dx, dy, LAG), K(dx + 0.05, dy, LAG)], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 9, "t": rel(tOp, W("p11", "used")) + 0.18 * i, "wake": False, "label": ("About 90 target ships" if i == 0 else "")}
           for i, (dx, dy) in enumerate([(-6, 3), (-4, 1), (-2, 4), (0, 2), (2, 5), (4, 3), (6, 1), (-5, -2), (-2, -3), (1, -1), (3, -4), (6, -2)])],
    labels=[lab(tOp, K(-2, 7, LAG), "Operation Crossroads", tOp + 0.3, WHITE)], caption="Target ships anchored in the lagoon. Icons enlarged.")
AIM, DET = K(0, 0, LAG), K(0.7, 0.0, LAG)
reg("bk-able", tAble, tMiss, [("s", LAG, 14), (2.0, LAG, 10), ("e", K(0.35, 0, LAG), 8)], tag="REAL HISTORY", clock="1 JULY 1946", clockLabel="ABLE", clockRate=0, source=SRC_C,
    cities=[city(tAble, AIM, "Aim point", tAble + 0.3, WHITE, "target", 6)],
    ships=[{"path": [AIM, [AIM[0] + 0.004, AIM[1]]], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 11, "t": 0, "wake": False, "label": "Target ship"}],
    labels=[lab(tAble, K(-3.0, 3.0, LAG), "Able: 23 kt air burst", W("p11", "twenty-three-kiloton"), YELLOW)])
reg("bk-miss", tMiss, tFive2, [("s", K(0.35, 0, LAG), 8), (2.0, K(0.35, 0, LAG), 5.5), ("e", K(0.35, 0, LAG), 4.2)], tag="REAL HISTORY", clock="1 JULY 1946", clockLabel="ABLE", clockRate=0, source=SRC_C,
    ships=[{"path": [AIM, [AIM[0] + 0.004, AIM[1]]], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 11, "t": 0, "wake": False}],
    cities=[city(tMiss, AIM, "Aim point", tMiss - 1, WHITE, "target", 6), city(tMiss, DET, "Burst", tMiss + 1.0, RED, "target", 6)],
    lines=[{"from": AIM, "to": DET, "color": YELLOW, "label": "Missed by about 700 m", "t0": rel(tMiss, W("p11", "roughly")), "t1": rel(tMiss, W("p11", "roughly")) + 1.5}])
reg("bk-sank", tFive2, S("p12"), [("s", LAG, 18), (2.0, LAG, 14), ("e", LAG, 12)], tag="REAL HISTORY", clock="1 JULY 1946", clockLabel="ABLE", clockRate=0, source=SRC_C,
    ships=[{"path": [K(dx, dy, LAG), K(dx + 0.05, dy, LAG)], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 10, "t": 0, "wake": False, **({"sunkAt": rel(tFive2, tFive2 + 1.3 + 0.35 * i)} if i < 5 else {})}
           for i, (dx, dy) in enumerate([(-2, 1), (0.5, 1.5), (1.5, -0.5), (-1, -1.5), (2.5, 1.0), (-4, 2), (4, -2), (-3, -3), (5, 2)])],
    labels=[lab(tFive2, K(-3, 4.8, LAG), "Five ships sank", W("p11", "sank"), RED)])
a = S("p12")
reg("miss-ours", a, S("p13"), [("s", K(0.5, -0.6), 12), (2.5, K(0.9, -0.9), 9), ("e", K(0.9, -0.9), 7.5)], clock="", source="",
    ships=fleet(a, S("p13"), ["DD1", "CV"], labels={"CV": "Carrier"}),
    lines=[{"from": B, "to": CVP, "color": YELLOW, "label": "Our miss: 2.5 km", "t0": rel(a, W("p12", "lands")), "t1": rel(a, W("p12", "lands")) + 1.2}],
    cities=[city(a, B, "Burst point (ours)", W("p12", "burst"), RED, "target", 6)],
    labels=[lk(a, -1.5, 1.4, "The same kind of miss", W("p12", "miss"), YELLOW)])
a = S("p13")
SRC_B = "Wikipedia; National Security Archive"
RS = [-76.0, 24.0]
tTor, tArk, tSurf, tAmer = W("p13", "ten-kiloton"), W("p13", "launch"), W("p13", "boat"), W("p13", "americans")
reg("b59-map", a, tTor, [("s", [-74.0, 23.0], 2400), (3.0, [-73.5, 23.2], 1700), ("e", [-73.0, 23.0], 1200)], tag="REAL HISTORY", clock="OCTOBER 1962", clockLabel="NEAR CUBA", clockRate=0, source=SRC_B, highlight=[HL_CUBA],
    countryLabels=[{"iso": CUBA_ISO, "text": "CUBA", "color": WHITE}],
    cities=[city(a, CUBA_SEA, "B-59, Soviet submarine", W("p13", "b-59"), RED, "sub", 6)],
    ships=[{"path": [K(-60, -45, CUBA_SEA), K(-8, -6, CUBA_SEA)], "t0": W("p13", "chased") - a - 0.5, "t1": rel(a, tTor) + 1.0, "kind": "us", "color": BLUE, "size": 14, "t": W("p13", "chased") - a - 0.5, "label": "US carrier group", "wake": True}])
reg("b59-torpedo", tTor, tArk, [("s", CUBA_SEA, 90), (2.0, CUBA_SEA, 40), ("e", CUBA_SEA, 22)], tag="REAL HISTORY", clock="27 OCT 1962", clockLabel="B-59", clockRate=0, source=SRC_B,
    cities=[city(tTor, CUBA_SEA, "B-59", tTor + 0.1, RED, "sub", 6)], rings=[{"at": CUBA_SEA, "km": 3.9, "color": RED, "dashed": True, "t": rel(tTor, W("p13", "torpedo")), "label": "10 kt torpedo"}],
    labels=[lab(tTor, K(2, 3, CUBA_SEA), "Nuclear torpedo: 10 kt", W("p13", "nuclear"), YELLOW)])
reg("b59-officers", tArk, tSurf, [("s", CUBA_SEA, 22), (2.0, CUBA_SEA, 17), ("e", CUBA_SEA, 14)], tag="REAL HISTORY", clock="27 OCT 1962", clockLabel="B-59", clockRate=0, source=SRC_B,
    cities=[city(tArk, CUBA_SEA, "B-59", tArk - 0.1, RED, "sub", 6)],
    labels=[lab(tArk, K(-4, 3.5, CUBA_SEA), "Launch needed three officers", W("p13", "needed"), WHITE), lab(tArk, K(-4, 1.5, CUBA_SEA), "Two said yes, by one account", W("p13", "officers") + 0.4, WHITE) if False else lab(tArk, K(-4, -3.8, CUBA_SEA), "Vasily Arkhipov: refused", W("p13", "vasily"), YELLOW)])
reg("b59-surface", tSurf, tAmer, [("s", CUBA_SEA, 14), (2.0, K(0, 2, CUBA_SEA), 18), ("e", K(0, 2, CUBA_SEA), 22)], tag="REAL HISTORY", clock="27 OCT 1962", clockLabel="B-59", clockRate=0, source=SRC_B,
    ships=[{"path": [K(0, -1, CUBA_SEA), K(0, 2, CUBA_SEA)], "t0": 0, "t1": 2.0, "kind": "pla", "color": RED, "size": 12, "t": 0, "wake": True, "label": "B-59 surfaces"}],
    labels=[lab(tSurf, K(-5, -3, CUBA_SEA), "The boat surfaced", W("p13", "surfaced"), YELLOW)])
reg("b59-unknown", tAmer, S("p14"), [("s", K(0, 1.5, CUBA_SEA), 20), (2.2, K(8, 1.0, CUBA_SEA), 40), ("e", K(10, 0, CUBA_SEA), 60)], tag="REAL HISTORY", clock="27 OCT 1962", clockLabel="B-59", clockRate=0, source=SRC_B,
    ships=[{"path": [K(0, 2, CUBA_SEA), K(0.1, 2, CUBA_SEA)], "t0": 0, "t1": 8, "kind": "pla", "color": RED, "size": 12, "t": 0, "wake": False}, {"path": [K(14, -3, CUBA_SEA), K(8, -1.5, CUBA_SEA)], "t0": 0, "t1": 6, "kind": "us", "color": BLUE, "size": 14, "t": 0, "wake": True, "label": "US group"}],
    labels=[lab(tAmer, K(-8, 6, CUBA_SEA), "The US did not know the torpedo was aboard", W("p13", "torpedo", 2), YELLOW)])
a = S("p14")
add(id="yields", type="bars", start=a, end=S("p15"), tag="REAL HISTORY", title="Ten kilotons is our yield too", sub="kilotons · published figures and our choice", source="Nuclear Weapon Archive; National Security Archive; our scenario",
    bars=[{"label": "Wigwam, 1955", "value": 30, "display": "30 kt", "color": AMBER}, {"label": "Able, 1946", "value": 23, "display": "23 kt", "color": AMBER}, {"label": "B-59 torpedo, 1962", "value": 10, "display": "10 kt", "color": AMBER}, {"label": "Our simulated warhead", "value": 10, "display": "10 kt", "color": RED}])
a = S("p15")
tSep, tJob, tToday, tNew = W("p15", "september"), W("p15", "job"), W("p15", "a", 2), W("p15", "new")
SRC_N = "Federation of American Scientists; Congressional Research Service"
glob("cw", a, tJob + 3.0, [("s", 30, -100, 800), (3.2, 35, -70, 900), (6.0, 30, -25, 800), ("e", 26, 20, 750)], tag="REAL HISTORY", clock="", source=SRC_N, highlight=[HL_US],
     markers=[{"at": WASH, "label": "Washington: September 1991", "color": BLUE, "kind": "base", "size": 5, "t": rel(a, tSep)}, {"at": [-5.0, 36.0], "label": "Ships at sea", "color": BLUE, "kind": "dot", "t": rel(a, W("p15", "naval"))}, {"at": [-12.0, 30.0], "label": "Finished: 1992", "color": BLUE, "kind": "dot", "t": rel(a, tJob)}],
     arcs=[{"from": WASH, "to": [-5.0, 36.0], "t0": rel(a, W("p15", "take")), "t1": rel(a, W("p15", "take")) + 2.4, "color": BLUE, "loft": 0.25}], caption="1991: tactical nuclear weapons come off US ships. 1992: finished.")
glob("cg-slcm", tJob + 3.0, S("p16"), [("s", 30, 150, 1000), (3.0, 26, 154, 1400), ("e", 24, 154, 1800)], tag="REAL DATA", clock="", source=SRC_N,
     markers=[{"at": B, "label": "A carrier group today: no nuclear weapons aboard", "color": BLUE, "kind": "target", "size": 6, "t": rel(tJob + 3.0, W("p15", "none"))}, {"at": [160.0, 31.0], "label": "SLCM-N: a missile still in development", "color": AMBER, "kind": "dot", "t": rel(tJob + 3.0, W("p15", "development"))}, {"at": WASH, "label": "", "color": BLUE, "kind": "dot", "t": 20}],
     caption="No tactical nuclear weapons aboard since 1992.")
a = S("p16")
tTw = W("p16", "twenty")
reg("no-answer", a, tTw, [("s", K(0, 0), 30), (2.0, K(1.0, 0), 22), ("e", K(1.0, 0), 20)], clock="", source="",
    ships=fleet(a, tTw, ["CV", "DD1", "DD2", "DD3"], labels={"CV": "Carrier"}), labels=[lk(a, -3.5, 4.0, "No nuclear answer on its decks", W("p16", "nuclear"), YELLOW)])
reg("twenty-min", tTw, W("p16", "how"), [("s", [153.6, 24.0], 700), ("e", [154.5, 24.0], 450)], clock="T+00:00", clockLabel="TWENTY MINUTES", clockRate=60,
    ships=[missile(tTw, [SUBP, B], tTw - 0.5, tTw + 3.5, "Missile")] + fleet(tTw, W("p16", "how"), ["CV"], labels={"CV": "Strike group"}),
    labels=[lab(tTw, [153.2, 25.2], "Launch: 284 km away", tTw + 0.3, WHITE)])
reg("unseen", W("p16", "how"), S("p17"), [("s", [154.0, 24.0], 500), (2.0, [154.5, 24.0], 700), ("e", [154.2, 24.0], 1100)], clock="T+12:00", clockLabel="STILL UNSEEN?", clockRate=0,
    ships=fleet(W("p16", "how"), S("p17"), ["CV"], labels={}), lines=[{"from": SUBP, "to": B, "color": RED, "dashed": True, "t0": 0.2, "t1": 2.0}],
    labels=[lab(W("p16", "how"), [154.1, 25.0], "How does a missile get that far unseen?", W("p16", "how") + 0.3, YELLOW)])

# ================================================================== Chapter 03 the trigger [SIMULATION]
a = chapter("c3-card", S("p17"), 3.5, "CHAPTER 03", "The trigger", "SIMULATION")
tFi, tNm = W("p17", "fires"), W("p17", "the")
reg("t-attacker", a, tFi, [("s", [150.0, 25.0], 2500), (2.2, [151.5, 24.4], 1500), ("e", [152.2, 24.0], 1000)], clock="", source="",
    countryLabels=[], cities=[city(a, SUBP, "Attacker's submarine (simulated)", W("p17", "unnamed"), RED, "sub", 6), city(a, MARCUS, "Minami-Torishima (Japan)", a + 0.2, WHITE, "dot")],
    labels=[lab(a, [148.2, 26.0], "No country. No flag.", W("p17", "country"), YELLOW)])
reg("t-fires", tFi, tNm, [("s", [153.0, 24.1], 700), (2.4, [153.8, 24.0], 460), ("e", [154.4, 24.0], 400)], clock="T+00:00", clockLabel="MINUTE ZERO", clockRate=0,
    cities=[city(tFi, SUBP, "Submarine", tFi + 0.1, RED, "sub", 6)], ships=[missile(tFi, [SUBP, B], tFi + 0.2, tFi + 3.8, "Fictional anti-ship missile", t_on=tFi + 0.2)],
    labels=[lab(tFi, [153.1, 25.0], "One missile", W("p17", "one"), WHITE)])
reg("t-warhead", tNm, S("p18"), [("s", B, 24), (2.0, B, 18), ("e", B, 14)], clock="", source="",
    ships=fleet(tNm, S("p18"), ["DD1", "CV"], labels={}), rings=[ring(2, rel(tNm, W("p17", "ten-kiloton")), False, dashed=True)],
    cities=[city(tNm, B, "One warhead: 10 kt", W("p17", "warhead"), RED, "target", 6)])
a = S("p18")
tNo2, tBor = W("p18", "no"), W("p18", "borrowed")
reg("t-choice", a, tNo2, [("s", B, 18), ("e", B, 15)], clock="", source="", ships=fleet(a, tNo2, ["DD1", "CV"], labels={}),
    labels=[lk(a, -4.0, 3.6, "10 kt: our choice", W("p18", "choice"), YELLOW)], rings=[ring(2, 0.5, True)])
reg("t-nosrc", tNo2, tBor, [("s", [154.2, 24.0], 600), (2.4, [154.4, 24.0], 450), ("e", [154.5, 24.0], 400)], clock="", source="",
    cities=[city(tNo2, B, "Modern anti-ship weapon", tNo2 + 0.3, BLUE, "target", 6)], labels=[lab(tNo2, [153.9, 24.5], "No published source gives its yield", W("p18", "published"), YELLOW)])
glob("t-b59", tBor, S("p19"), [("s", 22, -100, 900), ("e", 24, 150, 1300)], tag="SIMULATION", clock="", source="",
     markers=[{"at": CUBA_SEA, "label": "B-59 torpedo: 10 kt, 1962", "color": AMBER, "kind": "dot", "t": 0.3}, {"at": B, "label": "Our size: the same", "color": RED, "kind": "target", "t": rel(tBor, W("p18", "size")) + 0.8}],
     arcs=[{"from": CUBA_SEA, "to": B, "t0": 0.4, "t1": 3.6, "color": AMBER, "loft": 0.3}])
a = S("p19")
tCr, tWest = W("p19", "a", 2), W("p19", "somewhere")
reg("t-group", a, tWest, [("s", K(0, 0), 30), (2.5, K(1.0, 0), 38), ("e", K(1.0, 0), 44)], clock="", source="", legend=[{"text": "GENERIC GROUP (ENLARGED ICONS)", "color": BLUE}],
    ships=fleet(a, tWest, times={"CV": a, "CG": W("p19", "cruiser"), "DD1": W("p19", "three"), "DD2": W("p19", "three") + 0.3, "DD3": W("p19", "four"), "DD4": W("p19", "four") + 0.3, "AO": W("p19", "supply"), "SSN": W("p19", "submarine")},
               labels={"CV": "Carrier", "CG": "Cruiser", "DD1": "Destroyer", "AO": "Supply ship", "SSN": "Submarine"}))
glob("t-night", tWest, S("p20"), [("s", 22, 140, 1000), (2.5, 24, 150, 1500), ("e", 24, 155, 2200)], clock="01:10", clockLabel="LOCAL · NIGHT", clockRate=0,
     markers=[{"at": B, "label": "Western Pacific (simulated position)", "color": BLUE, "kind": "target", "t": rel(tWest, W("p19", "western"))}], caption="Local night.")
a = S("p20")
reg("t-noname", a, W("p20", "so"), [("s", CVP, 14), ("e", CVP, 10)], clock="", source="", ships=fleet(a, W("p20", "so"), ["CV", "DD1"], labels={}),
    labels=[lab(a, K(1.8, -0.4), "No real ship is the target", W("p20", "real"), YELLOW)])
reg("t-hull", W("p20", "so"), S("p21"), [("s", CVP, 10), (2.4, CVP, 13), ("e", CVP, 15)], clock="", source="", ships=fleet(W("p20", "so"), S("p21"), ["CV"], labels={"CV": "Carrier"}),
    labels=[lk(W("p20", "so"), 3.5, -2.6, "No name", W("p20", "name"), WHITE), lk(W("p20", "so"), 3.5, -3.6, "No hull number", W("p20", "hull"), WHITE), lk(W("p20", "so"), 3.5, -4.6, "No real date", W("p20", "place"), WHITE)])
a = S("p21")
tCa, tIn, tAb, tOu = W("p21", "carrier"), W("p21", "both"), W("p21", "able"), W("p21", "ours")
reg("t-lead", a, tCa, [("s", B, 12), (2.2, B, 9), ("e", B, 8)], clock="", source="", ships=fleet(a, tCa, ["DD1"], labels={"DD1": "Lead destroyer"}),
    cities=[city(a, B, "Burst point", W("p21", "burst"), RED, "target", 6)], labels=[lk(a, 1.6, 2.0, "The screen's lead ship", W("p21", "screen"), WHITE)])
reg("t-25", tCa, tIn, [("s", K(0.9, -0.9), 9), (2.2, K(0.9, -0.9), 7.5), ("e", K(0.9, -0.9), 6.5)], clock="", source="", ships=fleet(tCa, tIn, ["DD1", "CV"], labels={"CV": "Carrier"}),
    lines=[{"from": B, "to": CVP, "color": YELLOW, "label": "2.5 km", "t0": rel(tCa, W("p21", "kilometers")) , "t1": rel(tCa, W("p21", "kilometers")) + 1.0}])
reg("t-inputs", tIn, tAb, [("s", K(0.9, -0.9), 7), (2.0, K(0.9, -0.9), 9), ("e", K(0.9, -0.9), 11)], clock="", source="", ships=fleet(tIn, tAb, ["DD1", "CV"], labels={}),
    lines=[{"from": B, "to": CVP, "color": YELLOW, "t0": -30, "t1": -29}],
    labels=[lk(tIn, -1.0, 2.0, "Both are inputs", W("p21", "inputs"), YELLOW)])
reg("t-able", tAb, tOu, [("s", K(0.5, -0.5), 8), (2.0, K(0.5, -0.5), 6), ("e", K(0.5, -0.5), 5)], clock="", source="", ships=fleet(tAb, tOu, ["DD1", "CV"], labels={}),
    rings=[{"at": B, "km": 0.7, "color": AMBER, "dashed": True, "t": rel(tAb, W("p21", "seven")), "label": "Able's miss: 700 m"}],
    labels=[lk(tAb, -1.3, 1.6, "Able missed by about 700 m", tAb + 0.2, AMBER)])
reg("t-larger", tOu, S("p22"), [("s", K(0.5, -0.5), 5), (1.8, K(0.9, -0.9), 7), ("e", K(0.9, -0.9), 9)], clock="", source="", ships=fleet(tOu, S("p22"), ["DD1", "CV"], labels={}),
    lines=[{"from": B, "to": CVP, "color": YELLOW, "label": "Ours: 2.5 km", "t0": rel(tOu, W("p21", "larger")), "t1": rel(tOu, W("p21", "larger")) + 1.0}],
    labels=[lk(tOu, -1.6, 1.8, "A larger miss: our choice", W("p21", "choice"), YELLOW)])
a = S("p22")
glob("t-wait", a, S("p23"), [("s", 24, 148, 1600), (3.0, 24, 152, 2100), ("e", 24, 155, 2600)], clock="T-00:30", clockLabel="NOT YET LAUNCHED", clockRate=0,
     markers=[{"at": SUBP, "label": "Submarine (simulated)", "color": RED, "kind": "sub", "size": 5, "t": 0.3}, {"at": B, "label": "Strike group", "color": BLUE, "kind": "target", "size": 6, "t": 1.4}, {"at": [154.0, 25.8], "label": "What does the group see?", "color": YELLOW, "kind": "dot", "t": rel(a, W("p22", "see"))}, {"at": [153.0, 22.2], "label": "And when?", "color": WHITE, "kind": "dot", "t": rel(a, W("p22", "when"))}], caption="The missile is not yet in the air.")

# ================================================================== Chapter 04 minute by minute [SIMULATION]
a = chapter("c4-card", S("p23"), 3.5, "CHAPTER 04", "Minute by minute", "SIMULATION")
TZ = a
DET = W("p26", "detonates")
RATE = round(1206.0 / (DET - TZ), 2)
GREY = "#8A8F98"


def tclk(t):
    return clk((t - TZ) * RATE)


def postfleet(a, b, names=None, labels=None, times=None, drift=(0.0, 0.0), paths=None):
    out = []
    for n in names or list(FLEET):
        h = hull(a, b, n, t=(times or {}).get(n), label=(labels is None or n in labels), drift=drift, lab_text=(labels or {}).get(n))
        if n in ("DD1", "DD2"):
            h["color"] = GREY
        out.append(h)
    return out


tSet, tFl, tUnd = W("p23", "settles"), W("p23", "flies"), W("p23", "under")
reg("m-launch", a, S("p24"), [("s", [152.6, 24.0], 90), (1.6, [153.4, 24.1], 500), (4.0, [154.0, 24.1], 700), ("e", [154.6, 24.0], 600)], clock=tclk(a), clockLabel="MINUTE ZERO", clockRate=RATE,
    cities=[city(a, SUBP, "Submarine launches", W("p23", "launches"), RED, "sub", 6), city(a, B, "Strike group", a + 2.4, BLUE, "target", 6)],
    ships=[missile(a, [SUBP, B], W("p23", "launches"), W("p23", "launches") + 8.0, "Missile", t_on=W("p23", "launches"))],
    labels=[lab(a, [153.4, 24.7], "Low altitude", tSet + 0.5, WHITE), lab(a, [154.6, 23.4], "A little under the speed of sound", tUnd, YELLOW)])
a = S("p24")
tSv, tMs = W("p24", "seven"), W("p24", "the", 2)
reg("m-hulls", a, tSv, [("s", K(0, 0), 30), (2.5, K(1.0, 0), 38), ("e", K(1.0, 0), 44)], clock=tclk(a), clockLabel="MINUTE ZERO", clockRate=RATE,
    ships=fleet(a, tSv, drift=(0.0, 0.6), times={"CV": a, "CG": W("p24", "cruiser"), "DD1": W("p24", "three"), "DD2": W("p24", "three") + 0.3, "DD3": W("p24", "destroyers"), "DD4": W("p24", "destroyers") + 0.3, "AO": W("p24", "supply"), "SSN": W("p24", "submarine")},
               labels={"CV": "Carrier", "CG": "Cruiser", "DD1": "Destroyer", "AO": "Supply ship", "SSN": "Submarine"}))
reg("m-sea", tSv, tMs, [("s", K(0, 0), 60), (2.4, K(0, 0), 120), ("e", K(0, 0), 200)], clock=tclk(tSv), clockLabel="MINUTE ZERO", clockRate=RATE,
    ships=fleet(tSv, tMs, drift=(0.0, 1.2), labels={}), legend=[{"text": "SEVEN OR EIGHT HULLS (ICONS ENLARGED)", "color": BLUE}],
    labels=[lk(tSv, -14, 14, "A wide dark sea", W("p24", "wide"), WHITE)])
reg("m-find", tMs, S("p25"), [("s", [153.0, 24.0], 400), (2.2, [153.9, 24.0], 260), ("e", [154.5, 24.0], 180)], clock=tclk(tMs), clockLabel="MINUTE ZERO", clockRate=RATE,
    ships=[missile(tMs, [[152.4, 24.0], B], tMs, S("p25"), "Missile")] + fleet(tMs, S("p25"), ["CV"], labels={"CV": "Strike group"}),
    labels=[lab(tMs, [153.0, 24.9], "No need to find every hull", W("p24", "find"), YELLOW)])
a = S("p25")
tDue, tTwen, tUns = W("p25", "due"), W("p25", "twenty"), W("p25", "unseen")
a = S("p26")
reg("m-p25", S("p25"), DET, [("s", [153.6, 24.0], 600), (2.2, [153.6, 24.0], 460), (4.4, [153.8, 24.1], 520), (7.0, [154.0, 24.1], 580), (9.4, [154.3, 24.1], 360), (12.0, [154.6, 24.0], 220), (14.0, [154.8, 24.0], 120), ("e", B, 40)], clock=tclk(S("p25")), clockLabel="IN FLIGHT", clockRate=RATE,
    cities=[city(S("p25"), SUBP, "Launch", S("p25") + 0.2, RED, "sub", 5), city(S("p25"), B, "Burst point", S("p25") + 1.0, BLUE, "target", 6)],
    lines=[{"from": SUBP, "to": B, "color": RED, "label": "284 km", "t0": rel(S("p25"), W("p25", "path")), "t1": rel(S("p25"), W("p25", "path")) + 1.8}],
    ships=[missile(S("p25"), [[152.9, 24.0], B], S("p25"), DET, "Missile", t_on=S("p25"))] + fleet(S("p25"), DET, ["CV", "DD1", "DD2", "DD3", "CG"], drift=(0.0, 0.3), times={"CV": tTwen}, labels={}),
    labels=[lab(S("p25"), [152.9, 24.6], "Due east", tDue, WHITE), lab(S("p25"), [153.8, 23.4], "Across open water", W("p25", "open"), WHITE), lab(S("p25"), [153.4, 24.8], "Flight: 20 minutes", tTwen + 0.2, YELLOW), lab(S("p25"), [154.3, 23.5], "Assumed: unseen, unstopped", tUns, YELLOW),
            lab(S("p25"), K(-8, 11), "Minute twenty point one", W("p26", "point"), YELLOW)])
FX_T = round(DET, 2)
reg("m-flash", FX_T, S("p27"), [("s", B, 20), (2.2, K(0.8, 0), 15), ("e", K(0.8, -0.4), 13)], clock="T+20:06", clockLabel="THE BURST", clockRate=0, source="",
    burst={"at": B, "t": 0.1, "km": 1.6, "fade": 7}, ships=postfleet(FX_T, S("p27"), ["DD1", "CV", "DD2"], labels={}), rings=[ring(2, 0.8, True)],
    labels=[lk(FX_T, 0.0, 2.2, "Air burst over the lead destroyer", FX_T + 1.4, RED)], caption="About ten past one, local time.")
a = S("p27")
tDes, tAnd2, tShips = W("p27", "destroyers"), W("p27", "and", 2), W("p27", "ships")
reg("m-light", a, tDes, [("s", K(1, 0), 13), ("e", K(1, 0), 15)], clock="T+20:07", clockLabel="THE BURST", clockRate=0, source="",
    burst={"at": B, "t": -2.0, "km": 1.6, "fade": 7}, ships=postfleet(a, tDes, ["DD1", "CV", "DD2"], labels={}), rings=[ring(2, -30)],
    labels=[lk(a, -2.2, 2.2, "The sea is lit from above", W("p27", "lit"), YELLOW)])
reg("m-inside", tDes, tAnd2, [("s", K(0, 0), 5), (2.0, K(0, 0), 4), ("e", K(0, 0), 3.2)], clock="T+20:08", clockLabel="THE BURST", clockRate=0, source=ENG,
    ships=postfleet(tDes, tAnd2, ["DD1", "DD2"], labels={"DD1": "Lead destroyer", "DD2": "Destroyer"}), rings=[ring(0, rel(tDes, W("p27", "fireball")), True), ring(2, rel(tDes, W("p27", "heaviest")), True)],
    labels=[lk(tDes, 0.9, 0.9, "Closest to the centre", tDes + 0.4, WHITE)])
reg("m-lost", tAnd2, tShips, [("s", K(0, 0), 4), (1.8, K(0, 0), 6), ("e", K(0, 0), 8)], clock="T+20:30", clockLabel="THE BURST", clockRate=0, source=ENG,
    ships=postfleet(tAnd2, tShips, ["DD1", "DD2", "CV"], labels={"DD1": "Lost or crippled", "DD2": "Lost or crippled"}), rings=[ring(0, -30), ring(2, -30)],
    labels=[lk(tAnd2, -2.0, 2.6, "Our assumption, not a record", W("p27", "simulation"), YELLOW)])
reg("m-edge", tShips, S("p28"), [("s", K(0, 0), 14), (2.0, K(0, 0), 22), ("e", K(0, 0), 32)], clock="T+21:00", clockLabel="THE BURST", clockRate=0, source=ENG,
    ships=postfleet(tShips, S("p28"), ["DD1", "DD2"], labels={}) + [
        {"path": [FPOS[n], K(FLEET[n][0][0] * 2.6, FLEET[n][0][1] * 2.6)], "t0": rel(tShips, W("p27", "moving")) - 0.5, "t1": rel(tShips, tShips) + 3.4, "kind": "us", "color": BLUE, "size": FLEET[n][1], "t": 0, "wake": True, "label": (FLEET[n][2] if n in ("DD3", "DD4", "AO") else "")} for n in ("CV", "DD3", "DD4", "CG", "AO", "SSN")],
    labels=[lk(tShips, -9, 8.5, "At the edge: shaken, still moving", W("p27", "shaken"), YELLOW)], rings=[ring(2, -30, False), ring(4, -30, False)])
a = S("p28")
tBl = W("p28", "blast")
reg("m-whitecv", a, tBl, [("s", CVP, 13), (2.4, CVP, 9), (5.0, CVP, 11), ("e", CVP, 13)], clock="T+20:07", clockLabel="ON THE CARRIER", clockRate=0, source="",
    ships=postfleet(a, tBl, ["CV", "DD1"], labels={"CV": "Carrier"}), burst={"at": B, "t": rel(a, W("p28", "turns")), "km": 2.4, "fade": 5},
    labels=[lab(a, K(1.8, -0.2), "First: light", W("p28", "light"), WHITE), lab(a, K(1.8, -3.4), "At night: the horizon turns white", W("p28", "whole"), YELLOW), lab(a, K(-1.2, -3.4), "The sea itself glows", W("p28", "sea"), WHITE)])
reg("m-blastwave", tBl, S("p29"), [("s", K(0.6, -0.6), 11), (2.2, K(0.6, -0.6), 9), ("e", K(0.6, -0.6), 8)], clock="T+20:08", clockLabel="ON THE CARRIER", clockRate=0, source="",
    ships=postfleet(tBl, S("p29"), ["CV", "DD1"], labels={"CV": "Carrier"}),
    rings=[{"at": B, "km": 2.5, "color": ORANGE, "t": rel(tBl, W("p28", "arrives")), "label": "Blast wave"}],
    labels=[lk(tBl, -2.0, 2.4, "Afterward: slower than light", W("p28", "slower"), YELLOW)])
a = S("p29")
tGq, tAir2, tWing, tSo, tThese = W("p29", "goes"), W("p29", "and"), W("p29", "a"), W("p29", "so"), W("p29", "these")
AC = lambda a, n, t0: [{"path": [K(1.77 + 0.3 * i, -1.77 + 0.4), K(1.77 + 12 * math.cos(0.5 + i * 0.9), -1.77 + 12 * math.sin(0.5 + i * 0.9))], "t0": rel(a, t0) + 0.15 * i, "t1": rel(a, t0) + 0.15 * i + 6.0, "kind": "ally", "color": WHITE, "size": 7, "t": rel(a, t0) + 0.15 * i, "wake": True} for i in range(n)]
reg("a-quarters", a, tAir2, [("s", CVP, 14), ("e", CVP, 10)], clock="T+20:10", clockLabel="GENERAL QUARTERS", clockRate=0, source="", ships=postfleet(a, tAir2, ["CV", "DD1"], labels={"CV": "Carrier"}),
    labels=[lab(a, K(1.8, -0.4), "General quarters", tGq, YELLOW)])
reg("a-aloft", tAir2, tWing, [("s", CVP, 14), (2.0, CVP, 30), ("e", CVP, 44)], clock="T+20:12", clockLabel="AIRCRAFT ALOFT", clockRate=0, source="",
    ships=postfleet(tAir2, tWing, ["CV", "DD1"], labels={}) + AC(tAir2, 5, tAir2),
    labels=[lk(tAir2, -9, 8, "Aircraft already aloft", W("p29", "aircraft"), WHITE), lk(tAir2, -9, -8, "The main striking force left", W("p29", "main"), YELLOW)], legend=[{"text": "AIRCRAFT ICONS ENLARGED", "color": WHITE}])
reg("a-wing", tWing, tSo, [("s", CVP, 44), (2.5, CVP, 60), ("e", CVP, 74)], clock="T+20:12", clockLabel="AIR WING", clockRate=0, source="Congressional Research Service",
    ships=postfleet(tWing, tSo, ["CV"], labels={}) + AC(tWing, 7, tWing - 1),
    labels=[lab(tWing, K(2, -6), "Air wing: 60 aircraft or more", W("p29", "sixty"), WHITE), lab(tWing, K(2, -10), "40 or more strike fighters", W("p29", "forty"), YELLOW)])
reg("a-reach", tSo, tThese, [("s", CVP, 74), (2.0, CVP, 50), ("e", CVP, 30)], clock="T+20:13", clockLabel="THE GROUP'S REACH", clockRate=0, source="",
    ships=postfleet(tSo, tThese, ["CV"], labels={}) + AC(tSo, 5, tSo - 2), labels=[lk(tSo, -8, 8, "In the air now: the group's reach", W("p29", "group's"), YELLOW)])
reg("a-choice", tThese, S("p30"), [("s", CVP, 30), ("e", CVP, 18)], clock="T+20:14", clockLabel="OUR CHOICES", clockRate=0, source="",
    ships=postfleet(tThese, S("p30"), ["CV"], labels={}) + AC(tThese, 4, tThese - 3), labels=[lk(tThese, -4.5, 4.0, "Our choices, not a record", W("p29", "choices"), YELLOW)])
a = S("p30")
tAirb, tAnd3 = W("p30", "aircraft"), W("p30", "and")
reg("f-deck", a, tAirb, [("s", CVP, 7), ("e", CVP, 9)], clock="T+20:20", clockLabel="THE FLIGHT DECK", clockRate=0, source="", ships=postfleet(a, tAirb, ["CV"], labels={"CV": "Carrier"}),
    labels=[lab(a, K(2.4, -0.7), "The problem is simple", W("p30", "problem"), YELLOW)])
CIRC = lambda t0, n, r: [{"path": [K(1.77 + r * math.cos(i * 2.1), -1.77 + r * math.sin(i * 2.1)), K(1.77 + r * math.cos(i * 2.1 + 2.5), -1.77 + r * math.sin(i * 2.1 + 2.5)), K(1.77 + r * math.cos(i * 2.1 + 5.0), -1.77 + r * math.sin(i * 2.1 + 5.0))], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 7, "t": rel(t0, t0) + 0.2 * i, "wake": True} for i in range(n)]
reg("f-land", tAirb, tAnd3, [("s", CVP, 9), (1.6, CVP, 14), ("e", CVP, 18)], clock="T+20:30", clockLabel="THE FLIGHT DECK", clockRate=0, source="", ships=postfleet(tAirb, tAnd3, ["CV"], labels={}) + CIRC(tAirb, 4, 2.5),
    labels=[lab(tAirb, K(2.4, -4.8), "Airborne: they need somewhere to land", W("p30", "need"), YELLOW)])
reg("f-radar", tAnd3, S("p31"), [("s", CVP, 18), (2.0, CVP, 24), ("e", CVP, 30)], clock="T+21:00", clockLabel="RADAR", clockRate=0, source="", ships=postfleet(tAnd3, S("p31"), ["CV"], labels={}) + CIRC(tAnd3, 4, 3.5),
    zones=[{"points": [K(-4, -6), K(8, -6), K(8, 4), K(-4, 4)], "label": "Radar: blind for a while (assumed)", "color": GREY, "t": rel(tAnd3, W("p30", "radar")), "pulse": True}])
a = S("p31")
reg("f-dist", a, S("p32"), [("s", B, 10), (2.0, B, 12), (4.2, B, 15), ("e", B, 17)], clock="T+20:06", clockLabel="THE BURST", clockRate=0, source=ENG, legend=LEGEND,
    ships=postfleet(a, S("p32"), ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    rings=[ring(0, rel(a, W("p31", "reaches")), False), ring(1, rel(a, W("p31", "depends")), False), ring(2, rel(a, W("p31", "distance")), False), ring(3, rel(a, W("p31", "ring")), False), ring(4, rel(a, W("p31", "ring", 2)), False)],
    labels=[lk(a, -4.4, 4.8, "How much reaches the carrier?", a + 0.3, YELLOW)])

# ================================================================== Chapter 05 ring by ring [SIMULATION]
tC5 = S("p32") + 3.5
chapter("c5-card", S("p32"), 3.5, "CHAPTER 05", "One warhead, ring by ring", "SIMULATION")
HC = {"clock": "T+20:06", "clockLabel": "THE BURST", "clockRate": 0, "source": ENG}
a = tC5
tRd, tRough = W("p32", "radius"), W("p32", "roughly")
reg("r-fire", a, tRough, [("s", B, 3.2), (2.2, B, 2.7), ("e", B, 2.3)], **HC,
    ships=postfleet(a, tRough, ["DD1"], labels={"DD1": "Lead destroyer"}), zones=[disc(FX["fireball_km"], rel(a, W("p32", "fireball")))],
    labels=[lk(a, 0.0, 0.2, "Radius: 150 m", tRd, WHITE), lk(a, 0.0, -0.3, "About 300 m across", W("p32", "three"), YELLOW)], legend=LEGEND[:1])
reg("r-cv", tRough, S("p33"), [("s", B, 2.3), (2.0, B, 2.0), ("e", B, 1.7)], **HC, zones=[disc(FX["fireball_km"], -30, "Fireball: 300 m across"), {"points": [K(-0.1665, -0.30), K(0.1665, -0.30), K(0.1665, -0.23), K(-0.1665, -0.23)], "color": BLUE, "t": rel(tRough, W("p32", "length")), "label": "Nimitz class: 333 m long"}],
    ships=postfleet(tRough, S("p33"), ["DD1"], labels={"DD1": "Lead destroyer: inside"}, times={"DD1": W("p32", "lead")}), legend=LEGEND[:1])
a = S("p33")
tAt2, tThat = W("p33", "at", 2), W("p33", "that")
reg("r-20", a, tAt2, [("s", B, 1.5), (2.5, B, 1.8), ("e", B, 2.4)], **HC, rings=[ring(0, -30, False), ring(1, rel(a, W("p33", "twenty")), True)], legend=LEGEND[:2],
    ships=postfleet(a, tAt2, ["DD1"], labels={}), labels=[lk(a, 0.0, 0.42, "Heavy blast: 20 psi", W("p33", "heavy"), YELLOW)])
reg("r-5", tAt2, tThat, [("s", B, 3.6), ("e", B, 4.6)], **HC, rings=prior(2) + [ring(2, rel(tAt2, W("p33", "five")), True)], legend=LEGEND[:3],
    ships=postfleet(tAt2, tThat, ["DD1", "DD2"], labels={}), labels=[lk(tAt2, 0.0, 1.8, "Falls to 5 psi", W("p33", "falls"), YELLOW)])
reg("r-area", tThat, S("p34"), [("s", B, 4.6), ("e", B, 5.6)], **HC, rings=prior(3), legend=LEGEND[:3], ships=postfleet(tThat, S("p34"), ["DD1", "DD2"], labels={}),
    labels=[lk(tThat, 0.0, 2.2, "6.7 km2 inside the 5 psi ring", W("p33", "covers"), YELLOW)])
a = S("p34")
tEs = W("p34", "escorts")
reg("r-burn", a, tEs, [("s", B, 5.0), (2.4, B, 6.0), ("e", B, 7.0)], **HC, rings=prior(3) + [ring(3, rel(a, W("p34", "reaches")), True)], legend=LEGEND[:4],
    ships=postfleet(a, tEs, ["DD1", "DD2"], labels={}), labels=[lk(a, 0.0, 2.8, "Exposed skin: 1.6 km", W("p34", "exposed"), YELLOW)])
reg("r-escort", tEs, S("p35"), [("s", B, 7.0), ("e", B, 8.0)], **HC, rings=prior(4), legend=LEGEND[:4],
    ships=postfleet(tEs, S("p35"), ["DD1", "DD2", "DD3", "CG"], labels={"DD2": "Escort", "DD3": "Escort", "CG": "Escort"}), labels=[lk(tEs, 0.0, 3.4, "Escorts inside: at risk of heavy damage", W("p34", "risk"), RED)])
a = S("p35")
tSo2, tThe3 = W("p35", "so"), W("p35", "the", 4)
reg("r-scale", a, tSo2, [("s", B, 9), (2.6, B, 12), ("e", B, 14)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(a, tSo2, ["DD1"], labels={"DD1": "A destroyer: a dot"}),
    labels=[lk(a, -4.0, 4.6, "Look at the scale", a + 0.3, YELLOW), lk(a, 4.0, -4.6, "Ring: almost 8 km across", W("p35", "eight"), WHITE)])
reg("r-big", tSo2, tThe3, [("s", B, 14), ("e", B, 10)], **HC, rings=prior(5), legend=[{"text": "SHIP ICONS ENLARGED", "color": BLUE}], ships=postfleet(tSo2, tThe3, ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    labels=[lk(tSo2, -3.0, 4.6, "Ships drawn larger than they are", W("p35", "larger"), YELLOW)])
reg("r-exact", tThe3, S("p36"), [("s", B, 10), ("e", B, 12)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(tThe3, S("p36"), ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    labels=[lk(tThe3, -3.0, 4.4, "Rings: exactly as the engine computes", W("p35", "exactly"), WHITE)])
a = S("p36")
tThe2, tThe5 = W("p36", "the", 2), W("p36", "the", 5)
reg("r-1psi", a, tThe2, [("s", B, 10), (3.0, B, 11), ("e", B, 12)], **HC, rings=prior(4) + [ring(4, rel(a, W("p36", "one")), True)], legend=LEGEND, ships=postfleet(a, tThe2, ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    labels=[lk(a, -4.4, 4.8, "Light blast: 1 psi", W("p36", "light"), YELLOW), lk(a, 4.4, -4.8, "Reaches 3.9 km", W("p36", "three"), WHITE)])
reg("r-cv25", tThe2, tThe5, [("s", K(0.9, -0.9), 9), (2.6, K(0.9, -0.9), 7), ("e", K(0.9, -0.9), 6.5)], **HC, rings=prior(5), legend=LEGEND,
    ships=postfleet(tThe2, tThe5, ["DD1", "CV"], labels={"CV": "Carrier"}),
    lines=[{"from": B, "to": CVP, "color": YELLOW, "label": "2.5 km", "t0": rel(tThe2, W("p36", "two")), "t1": rel(tThe2, W("p36", "two")) + 1.2}],
    labels=[lk(tThe2, -1.8, 1.6, "Between the burn ring and the edge", W("p36", "between"), WHITE)])
reg("r-model", tThe5, S("p37"), [("s", K(0.9, -0.9), 6.5), (2.2, K(0.9, -0.9), 9), ("e", K(0.9, -0.9), 11)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(tThe5, S("p37"), ["DD1", "CV"], labels={"CV": "Carrier"}),
    labels=[lk(tThe5, -2.2, 2.0, "Model: between 1 and 5 psi", W("p36", "model"), YELLOW), lk(tThe5, -2.2, -3.4, "Outside the burn ring", W("p36", "outside"), WHITE)])
a = S("p37")
tWith, tSo3, tAnd4 = W("p37", "with"), W("p37", "so"), W("p37", "and", 2)
reg("l-land", a, tWith, [("s", B, 12), ("e", B, 10)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(a, tWith, ["DD1", "CV"], labels={}),
    labels=[lk(a, -4.6, 5.0, "Two limits", a + 0.2, YELLOW), lk(a, 3.0, 5.0, "Limit 1: rings drawn for land", W("p37", "land"), WHITE)])
reg("l-model", tWith, tSo3, [("s", B, 10), (3.0, B, 13), ("e", B, 16)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(tWith, tSo3, ["DD1", "CV"], labels={}),
    labels=[lk(tWith, -5.0, 6.0, "No model of a ship", W("p37", "ship"), WHITE), lk(tWith, 3.0, 6.0, "No wave, no hardened hull", W("p37", "wave"), WHITE), lk(tWith, -5.0, -6.0, "Limit 2: no burst height", W("p37", "burst"), YELLOW)])
reg("l-neither", tSo3, S("p38"), [("s", B, 16), (2.8, B, 12), ("e", B, 10)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(tSo3, S("p38"), ["DD1", "CV"], labels={"CV": "Carrier"}),
    labels=[lk(tSo3, -5.0, 6.0, "We do not say it survives", W("p37", "survives"), YELLOW), lk(tSo3, -5.0, -6.0, "We do not say it sinks", W("p37", "sinks"), YELLOW)])
a = S("p38")
tIts, tOv, tOurs, tSoA = W("p38", "its"), W("p38", "over"), W("p38", "ours", 2), W("p38", "so")
reg("ab-guide", a, tOurs, [("s", [165.5, 11.6], 90), (2.4, LAG, 30), (tIts + 1.0, LAG, 22), ("e", LAG, 14)], tag="REAL HISTORY", clock="1 JULY 1946", clockLabel="ABLE", clockRate=0, source=SRC_C,
    cities=[city(a, BIKINI, "Bikini lagoon", a + 0.2, RED, "target", 6)],
    ships=[{"path": [K(dx, dy, LAG), K(dx + 0.05, dy, LAG)], "t0": 0, "t1": 8, "kind": "ally", "color": WHITE, "size": 9, "t": rel(a, tOv), "wake": False, "label": ("About 90 anchored ships" if i == 0 else ""), **({"sunkAt": rel(a, W("p38", "sank")) + 0.2 * i} if i < 5 else {})}
           for i, (dx, dy) in enumerate([(-2, 1), (0.5, 1.5), (1.5, -0.5), (-1, -1.5), (2.5, 1.0), (-4, 2), (4, -2), (-3, -3), (5, 2), (-6, 0), (6, -4)])],
    labels=[lab(a, [165.5, 12.6], "Able: the closest real guide", W("p38", "closest"), YELLOW), lab(a, [165.5, 10.6], "Not a match", W("p38", "not"), WHITE), lab(a, K(5, 7, LAG), "23 kt: more than twice ours", W("p38", "twenty-three"), AMBER), lab(a, K(-6, -7, LAG), "Five sank", W("p38", "five"), RED)], caption="Able: 23 kt. Ours: 10 kt.")
reg("ab-ours", tOurs, tSoA, [("s", K(0.6, -0.5), 20), (2.0, K(0.6, -0.5), 15), ("e", K(0.6, -0.5), 12)], clock="", source="", ships=postfleet(tOurs, tSoA, ["DD1", "CV", "DD2", "DD3", "CG"], labels={}), rings=prior(5),
    labels=[lk(tOurs, -4.0, 5.2, "Ours: 10 kt over a group at sea", tOurs + 0.2, YELLOW)])
reg("ab-scale", tSoA, S("p39"), [("s", K(0.6, -0.5), 12), ("e", K(0.6, -0.5), 17)], clock="", source="", ships=postfleet(tSoA, S("p39"), ["DD1", "CV", "DD2", "DD3", "CG"], labels={}), rings=prior(5),
    labels=[lk(tSoA, -4.0, 5.0, "Able sets a scale", W("p38", "scale"), WHITE), lk(tSoA, 2.0, -5.2, "Not a forecast", W("p38", "forecast"), YELLOW)])
a = S("p39")
tAtW, tWh = W("p39", "at"), W("p39", "which")
reg("wg-habit", a, tAtW, [("s", B, 16), (2.2, B, 20), ("e", B, 24)], clock="", source="", ships=postfleet(a, tAtW, ["DD1", "CV", "DD2", "DD3", "CG"], labels={}), rings=[ring(4, -30, False)],
    labels=[lk(a, -4.4, 5.6, "The Navy's habit: keep distance", W("p39", "respect"), YELLOW)])
reg("wg-eight", tAtW, tWh, [("s", B, 24), (2.4, B, 20), ("e", K(2, 0), 22)], clock="", source="Nuclear Weapon Archive", ships=postfleet(tAtW, tWh, ["DD1", "CV"], labels={}), rings=[ring(4, -30, False)],
    lines=[{"from": B, "to": K(8.0, 0), "color": WHITE, "label": "Wigwam: 5 miles upwind = 8 km", "t0": rel(tAtW, W("p39", "five")), "t1": rel(tAtW, W("p39", "five")) + 1.6}],
    labels=[lk(tAtW, -4.4, 6.0, "At Wigwam, most ships kept 8 km away", W("p39", "wigwam"), YELLOW)])
reg("wg-ring", tWh, S("p40"), [("s", K(1, 0), 22), (2.0, B, 18), ("e", B, 15)], clock="", source=ENG, ships=postfleet(tWh, S("p40"), ["DD1", "CV"], labels={}), rings=[ring(4, rel(tWh, W("p39", "outer")), True)],
    lines=[{"from": K(-3.95, 0), "to": K(3.95, 0), "color": WHITE, "label": "Our outer ring: 7.9 km across", "t0": rel(tWh, W("p39", "width")), "t1": rel(tWh, W("p39", "width")) + 1.0}])
a = S("p40")
tAnd5, tSoB = W("p40", "and", 2), W("p40", "so")
reg("bk-baker", a, tSoB, [("s", LAG, 14), (2.6, LAG, 18), (5.0, LAG, 22), ("e", LAG, 26)], tag="REAL HISTORY", clock="25 JULY 1946", clockLabel="BAKER", clockRate=0, source=SRC_C,
    cities=[city(a, LAG, "Bikini lagoon", a + 0.2, RED, "target", 6)],
    labels=[lab(a, K(-4, 4, LAG), "Not Baker", W("p40", "baker"), YELLOW), lab(a, K(-4, 2, LAG), "Shallow: underwater", W("p40", "shallow"), WHITE), lab(a, K(-4, 0, LAG), "23 kt, in a lagoon", W("p40", "twenty-three"), WHITE)])
reg("bk-air", tSoB, S("p41"), [("s", B, 14), (2.0, B, 17), ("e", B, 20)], clock="", source="", ships=postfleet(tSoB, S("p41"), ["DD1", "CV"], labels={}), rings=[ring(4, 0.6, False, dashed=True)],
    labels=[lk(tSoB, -4.4, 4.8, "Ours: an air burst", W("p40", "air"), YELLOW), lk(tSoB, -4.4, -4.8, "No water column", W("p40", "water"), WHITE)])
a = S("p41")
tOne1, tOne2, tEv = W("p41", "one"), W("p41", "one", 2), W("p41", "every")
reg("ct-edge", a, tOne2 - 0.2, [("s", B, 10), (2.4, B, 8.5), ("e", B, 7.5)], **HC, rings=[ring(4, rel(a, W("p41", "three")), True), ring(3, rel(a, tOne1), True)], legend=LEGEND,
    ships=postfleet(a, tOne2 - 0.2, ["DD1", "CV"], labels={}), labels=[lk(a, -3.2, 3.6, "3.9 km", W("p41", "kilometers"), TEAL), lk(a, 2.4, -3.6, "1.6 km", tOne1, AMBER)])
reg("ct-in", tOne2 - 0.2, tEv, [("s", B, 4.5), ("e", B, 3.0)], **HC, rings=[ring(4, -30, False), ring(3, -30, False), ring(2, 0.3, True), ring(1, rel(tOne2, W("p41", "three", 2)), True)], legend=LEGEND,
    ships=postfleet(tOne2, tEv, ["DD1", "DD2"], labels={}), labels=[lk(tOne2, 0.0, 1.9, "1.5 km", tOne2 + 0.2, RED)])
reg("ct-all", tEv, S("p42"), [("s", B, 9), (2.2, B, 11), (4.4, B, 13), ("e", B, 15)], **HC, rings=prior(5), legend=LEGEND, ships=postfleet(tEv, S("p42"), ["DD1", "CV", "DD2", "DD3", "DD4", "CG", "AO"], labels={}),
    labels=[lk(tEv, -4.6, 5.4, "Every ship sits somewhere on this target", W("p41", "sits"), WHITE), lk(tEv, -4.6, -5.6, "Distance decides what it feels", W("p41", "distance"), YELLOW)])
a = S("p42")
reg("fade", a, S("p43"), [("s", B, 15), ("e", B, 26)], clock="T+22:00", clockLabel="THE LIGHT FADES", clockRate=0, source="", ships=postfleet(a, S("p43"), ["DD1", "CV", "DD2", "DD3", "DD4", "CG", "AO", "SSN"], labels={}),
    labels=[lk(a, -6.0, 5.6, "What does the group do?", W("p42", "what"), YELLOW)])

# ================================================================== Chapter 06 the day after [SIMULATION]
a = chapter("c6-card", S("p43"), 3.5, "CHAPTER 06", "The day after", "SIMULATION")
tBg, tTurn, tDisp = W("p43", "group", 2), W("p43", "turn"), W("p43", "dispersal")
reg("d-q", a, tBg, [("s", B, 20), ("e", B, 26)], clock="", source="", ships=postfleet(a, tBg, drift=(0, 0), labels={}),
    labels=[lk(a, -6.0, 6.5, "What does one small bomb do to a ship that big?", W("p43", "bomb"), YELLOW)])


def spread(a, b, t0, mult=5.0, names=("CV", "DD3", "DD4", "CG", "AO", "SSN")):
    out = []
    for n in names:
        (dx, dy), sz, nm = FLEET[n]
        out.append({"path": [K(dx, dy), K(dx * mult, dy * mult)], "t0": rel(a, t0), "t1": rel(a, t0) + 5.0, "kind": "us", "color": BLUE, "size": sz, "t": 0, "wake": True})
    return out


reg("d-spread", tBg, tDisp, [("s", B, 26), (2.0, B, 40), ("e", B, 80)], clock="", source="", ships=postfleet(tBg, tDisp, ["DD1", "DD2"], labels={}) + spread(tBg, tDisp, tTurn),
    labels=[lk(tBg, -14, 14, "The group stops being a group", W("p43", "stops"), YELLOW), lk(tBg, 8, -14, "The ships turn outward", tTurn, WHITE)], legend=[{"text": "ICONS ENLARGED", "color": BLUE}])
reg("d-chose", tDisp, S("p44"), [("s", B, 80), (2.2, B, 110), ("e", B, 140)], clock="", source="",
    ships=postfleet(tDisp, S("p44"), ["DD1", "DD2"], labels={}) + [dict(s_, path=[s_["path"][1], s_["path"][1]], t0=0, t1=4, t=0, wake=False) for s_ in spread(tDisp, S("p44"), tDisp)],
    labels=[lk(tDisp, -26, 22, "A dispersal we chose", tDisp + 0.2, YELLOW), lk(tDisp, 6, -22, "Not a record", W("p43", "record"), WHITE)])
a = S("p44")
tWe = W("p44", "we")
reg("rs-steam", a, tWe, [("s", B, 60), (2.5, B, 45), ("e", B, 36)], clock="", source="",
    ships=postfleet(a, tWe, ["DD1", "DD2"], labels={}) + [{"path": [K(dx * 4, dy * 4), K(dx * 1.5, dy * 1.5)], "t0": W("p44", "begins") - a, "t1": rel(a, tWe) + 1.0, "kind": "us", "color": BLUE, "size": 12, "t": 0, "wake": True, "label": ("Rescue and medical" if n == "DD3" else "")} for n, ((dx, dy), _, _) in FLEET.items() if n in ("DD3", "DD4", "CG")],
    labels=[lk(a, -8, 8, "Rescue and medical effort begins", W("p44", "rescue"), YELLOW), lk(a, 5, -9, "From ships that can still steam", W("p44", "steam"), WHITE)])
reg("rs-count", tWe, S("p45"), [("s", B, 36), (2.4, B, 50), ("e", B, 70)], clock="", source="", ships=postfleet(tWe, S("p45"), ["DD1", "DD2", "DD3", "DD4", "CG"], labels={}),
    labels=[lk(tWe, -8, 8, "No count of anyone", W("p44", "count"), YELLOW), lk(tWe, -8, 5.5, "No count of ships", W("p44", "many"), WHITE)])
a = S("p45")
tPi, tNa = W("p45", "the", 2), W("p45", "the", 3)
reg("ww-on", a, tPi, [("s", CVP, 9), ("e", CVP, 6)], clock="", source="Wikipedia (Nimitz-class carrier)", ships=postfleet(a, tPi, ["CV"], labels={"CV": "Carrier"}),
    labels=[lab(a, K(2.4, -1.0), "Counter-measure wash-down: on", W("p45", "counter-measure"), YELLOW)])
reg("ww-pipes", tPi, tNa, [("s", CVP, 6), ("e", CVP, 5)], clock="", source="Wikipedia (Nimitz-class carrier)", ships=postfleet(tPi, tNa, ["CV"], labels={}),
    zones=[{"points": [K(0.6, -2.4), K(2.9, -2.4), K(2.9, -1.1), K(0.6, -1.1)], "label": "Seawater over deck and hull", "color": TEAL, "t": rel(tPi, W("p45", "spray")), "pulse": True}])
reg("ww-fires", tNa, W("p45", "and", 3), [("s", CVP, 5), ("e", CVP, 7)], clock="", source="Wikipedia (Nimitz-class carrier)", ships=postfleet(tNa, W("p45", "and", 3), ["CV"], labels={}),
    labels=[lab(tNa, K(2.4, -0.8), "Built for fires", W("p45", "fires"), WHITE), lab(tNa, K(2.4, -2.8), "And radiological threats", W("p45", "radiological"), WHITE)])
reg("ww-unknown", W("p45", "and", 3), S("p46"), [("s", CVP, 7), ("e", CVP, 10)], clock="", source="", ships=postfleet(W("p45", "and", 3), S("p46"), ["CV"], labels={}),
    labels=[lab(W("p45", "and", 3), K(2.6, -0.8), "Nobody knows how it would work after a burst", W("p45", "nobody"), YELLOW)])
a = S("p46")
tAtA, tAnd6, tTho = W("p46", "at"), W("p46", "and"), W("p46", "those")
reg("fo-empty", a, tAtA, [("s", B, 16), (2.6, B, 26), ("e", B, 40)], clock="", source="Scenario engine", ships=postfleet(a, tAtA, ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    labels=[lk(a, -7, 7, "The fallout map is nearly empty", W("p46", "empty"), YELLOW), lk(a, -7, -7, "Little local fallout from an air burst", W("p46", "little"), WHITE)])
reg("fo-able", tAtA, tAnd6, [("s", LAG, 26), ("e", LAG, 20)], tag="REAL HISTORY", clock="1 JULY 1946", clockLabel="ABLE", clockRate=0, source=SRC_C,
    labels=[lab(tAtA, K(-5, 4, LAG), "Able: most ships reboarded within a day", W("p46", "reboarded"), YELLOW)], cities=[city(tAtA, BIKINI, "Bikini lagoon", tAtA + 0.2, RED, "target", 6)])
reg("fo-wig", tAnd6, tTho, [("s", WIGWAM, 22), (2.6, K(3, 0, WIGWAM), 28), ("e", K(4, 0, WIGWAM), 34)], tag="REAL HISTORY", clock="14 MAY 1955", clockLabel="WIGWAM", clockRate=0, source=SRC_W,
    cities=[city(tAnd6, WIGWAM, "Wigwam", tAnd6 + 0.1, RED, "target", 6)],
    ships=[{"path": [K(7.9, 1.8, WIGWAM), K(8.0, 1.8, WIGWAM)], "t0": 0, "t1": 8, "kind": "us", "color": BLUE, "size": 11, "t": rel(tAnd6, W("p46", "downwind")), "wake": False, "label": "Shielded ship"}],
    labels=[lab(tAnd6, K(0, 6.5, WIGWAM), "Downwind ships: under the dose limit (one account)", W("p46", "limit"), YELLOW)])
reg("fo-two", tTho, S("p47"), [("s", B, 26), ("e", B, 18)], clock="", source="", ships=postfleet(tTho, S("p47"), ["DD1", "CV", "DD2"], labels={}),
    labels=[lk(tTho, -5, 4.8, "Two histories", W("p46", "histories"), WHITE), lk(tTho, -5, -4.8, "Not a forecast", W("p46", "forecast"), YELLOW)])
a = S("p47")
tRa, tAnd7, tThe4 = W("p47", "radio"), W("p47", "and", 3), W("p47", "the", 4)
reg("x-react", a, tRa, [("s", CVP, 8), ("e", CVP, 6)], clock="", source="", ships=postfleet(a, tRa, ["CV"], labels={"CV": "Carrier"}),
    labels=[lab(a, K(2.3, -0.8), "Reactors: shut down and checked", W("p47", "shut"), YELLOW), lab(a, K(2.3, -2.7), "An assumption", W("p47", "assumption"), WHITE)])
reg("x-radio", tRa, tAnd7, [("s", CVP, 6), ("e", CVP, 15)], clock="", source="", ships=postfleet(tRa, tAnd7, ["CV", "DD1", "DD2"], labels={}),
    zones=[{"points": [K(-5, -7), K(7, -7), K(7, 4), K(-5, 4)], "label": "Radio and radar: may fail", "color": GREY, "t": rel(tRa, W("p47", "radar")), "pulse": True}])
reg("x-wing", tAnd7, tThe4, [("s", CVP, 15), (1.8, CVP, 20), ("e", CVP, 26)], clock="", source="", ships=postfleet(tAnd7, tThe4, ["CV"], labels={}) + CIRC(tAnd7, 4, 4.0),
    labels=[lab(tAnd7, K(2.4, -8.0), "Air wing: nowhere safe to land?", W("p47", "nowhere"), YELLOW)])
reg("x-emp", tThe4, S("p48"), [("s", B, 26), (2.6, B, 20), ("e", B, 16)], clock="", source="Scenario engine", ships=postfleet(tThe4, S("p48"), ["DD1", "CV", "DD2", "DD3"], labels={}),
    labels=[lk(tThe4, -5.0, 4.8, "EMP: not modelled", W("p47", "electromagnetic"), WHITE), lk(tThe4, -5.0, -4.8, "We claim none", W("p47", "claim"), YELLOW)])
a = S("p48")
reg("nt", a, S("p49"), [("s", B, 16), (2.6, B, 20), ("e", B, 24)], clock="", source="", ships=postfleet(a, S("p49"), ["DD1", "CV", "DD2", "DD3"], labels={}),
    labels=[lk(a, -5.2, 5.2, "No published death toll", W("p48", "death"), YELLOW), lk(a, -5.2, -5.2, "So we give none", W("p48", "give"), WHITE)])
a = S("p49")
tOnB, tWi = W("p49", "on", 2), W("p49", "with")
glob("g-gap", a, tOnB, [("s", 24, 156, 1100), (3.0, 20, 150, 1500), ("e", 15, 140, 2000)], clock="", markers=[{"at": B, "label": "A dark gap on a screen", "color": BLUE, "kind": "target", "size": 6, "t": rel(a, W("p49", "dark"))}, {"at": GUAM, "label": "Guam", "color": WHITE, "kind": "dot", "t": 0.4}, {"at": TOKYO, "label": "Tokyo", "color": WHITE, "kind": "dot", "t": 1.0}],
     caption="The world does not know who fired.")
reg("g-bridge", tOnB, tWi, [("s", CVP, 14), (2.0, CVP, 10), ("e", CVP, 8)], clock="", source="", ships=postfleet(tOnB, tWi, ["CV"], labels={"CV": "Carrier"}),
    labels=[lab(tOnB, K(2.4, -0.6), "On the bridge: someone must decide", W("p49", "decide"), YELLOW)])
reg("g-answer", tWi, S("p50"), [("s", CVP, 8), (2.2, B, 16), ("e", B, 22)], clock="", source="", ships=postfleet(tWi, S("p50"), ["DD1", "CV", "DD2", "DD3"], labels={}),
    labels=[lk(tWi, -5.0, 5.0, "No weapon on the decks to answer", W("p49", "weapon"), WHITE), lk(tWi, -5.0, -5.0, "No name to answer", W("p49", "name"), YELLOW)])
reg("q-morning", S("p50"), S("p51"), [("s", B, 30), (1.8, B, 60), ("e", B, 120)], clock="06:00", clockLabel="LOCAL · MORNING", clockRate=0, source="", ships=postfleet(S("p50"), S("p51"), ["DD1", "CV", "DD2", "DD3", "CG"], labels={}),
    labels=[lk(S("p50"), -8.0, 8.0, "The sea is quiet again", W("p50", "quiet"), WHITE)])
# ================================================================== End slate
add(id="end", type="endslate", start=S("p51"), end=END, tag="", title="Next scenario", line="Full nuclear war minute by minute, globe only.")

# ------------------------------------------------------------------ merge short neighbouring region shots into longer ones with a continuous camera
import copy


def _sh(d, off, *fields):
    for f in fields:
        if isinstance(d.get(f), (int, float)):
            d[f] = round(d[f] + off, 2)


def merge(newid, ids):
    segs = [next(x for x in shots if x["id"] == i) for i in ids]
    assert [x["start"] for x in segs[1:]] == [x["end"] for x in segs[:-1]], ("not contiguous", ids)
    first = copy.deepcopy(segs[0])
    first["id"], first["end"] = newid, segs[-1]["end"]
    base = first["start"]
    for s in segs[1:]:
        s = copy.deepcopy(s)
        off = round(s["start"] - base, 2)
        assert s["type"] == first["type"] == "region" and s.get("tag") == first.get("tag"), ids
        for k in s["camera"][1:]:
            k["t"] = round(k["t"] + off, 2)
            if k["t"] - max(c["t"] for c in first["camera"]) < 0.3:
                continue
            first["camera"].append(k)
        for key in ("cities", "labels"):
            for it in s.get(key, []):
                _sh(it, off, "t")
                first.setdefault(key, []).append(it)
        for it in s.get("ships", []):
            ex = next((e for e in first.get("ships", []) if it.get("_id") and e.get("_id") == it["_id"]), None)
            if ex is not None:
                if it.get("label") and not ex.get("label"):
                    first.setdefault("labels", []).append({"at": it["path"][-1], "text": it["label"], "color": WHITE, "t": round((it.get("t") or 0) + off, 2)})
                continue
            _sh(it, off, "t", "t0", "t1", "sunkAt")
            first.setdefault("ships", []).append(it)
        for it in s.get("rings", []):
            if it.get("t", 0) <= -20:
                if any(abs(e["km"] - it["km"]) < 1e-6 for e in first.get("rings", [])):
                    continue
                it["t"] = off
            else:
                _sh(it, off, "t")
            first.setdefault("rings", []).append(it)
        for key in ("lines",):
            for it in s.get(key, []):
                _sh(it, off, "t0", "t1")
                first.setdefault(key, []).append(it)
        for it in s.get("zones", []):
            _sh(it, off, "t")
            first.setdefault("zones", []).append(it)
        if s.get("plume") and not first.get("plume"):
            first["plume"] = s["plume"]
            _sh(first["plume"], off, "t0", "t1")
        if s.get("burst") and not first.get("burst"):
            first["burst"] = s["burst"]
            _sh(first["burst"], off, "t")
        for it in s.get("legend", []):
            if it not in first.setdefault("legend", []):
                first["legend"].append(it)
        for f in ("caption", "source"):
            if not first.get(f) and s.get(f):
                first[f] = s[f]
    first["camera"].sort(key=lambda k: k["t"])
    first["view"] = {"center": first["camera"][0]["center"], "widthKm": first["camera"][0]["widthKm"]}
    i0 = shots.index(next(x for x in shots if x["id"] == ids[0]))
    for i in ids:
        shots.remove(next(x for x in shots if x["id"] == i))
    shots.insert(i0, first)


MERGES = [
    ("cv-b", ["cv-people", "cv-wing"]), ("b59-b", ["b59-b", "b59-c"]), ("f-a2", ["f-a", "f-radar"]), ("l-a2", ["l-a", "l-neither"]), ("wg-a2", ["wg-a", "wg-ring"]), ("ct-b", ["ct-all", "fade"]),
    ("d-a2", ["d-a", "d-chose"]), ("ww-c", ["ww-a", "ww-b"]), ("q-m", ["g-b", "q-morning"]), ("x-c", ["x-a", "x-b"]), ("t-g", ["t-d", "t-e"]), ("a-d", ["a-b", "a-c"]), ("r-h", ["r-20", "r-c"]),
    ("m-k", ["m-flash", "m-g"]), ("m-l", ["m-whitecv", "m-j"]),
]
MERGES2 = [
    ("open-dark", ["open-dark", "open-bridge"]), ("w-test", ["w-where", "w-cable"]), ("grp", ["grp-ships", "grp-support"]),
    ("bk-intro", ["bk-atoll", "bk-ships", "bk-able"]), ("bk-after", ["bk-miss", "bk-sank"]), ("b59-b", ["b59-torpedo", "b59-officers"]), ("b59-c", ["b59-surface", "b59-unknown"]),
    ("noans", ["no-answer", "twenty-min", "unseen"]), ("t-a", ["t-attacker", "t-fires", "t-warhead"]), ("t-b", ["t-choice", "t-nosrc"]), ("t-d", ["t-noname", "t-hull"]),
    ("t-e", ["t-lead", "t-25", "t-inputs"]), ("t-f", ["t-able", "t-larger"]), ("m-b", ["m-hulls", "m-sea", "m-find"]), ("m-g", ["m-light", "m-inside"]), ("m-h", ["m-lost", "m-edge"]), ("m-j", ["m-blastwave", "a-quarters"]), ("a-b", ["a-aloft", "a-wing"]), ("a-c", ["a-reach", "a-choice"]),
    ("f-a", ["f-deck", "f-land"]), ("r-a", ["r-fire", "r-cv"]), ("r-c", ["r-5", "r-area"]), ("r-d", ["r-burn", "r-escort"]), ("r-e", ["r-scale", "r-big"]), ("r-f", ["r-exact", "r-1psi"]),
    ("r-g", ["r-cv25", "r-model"]), ("l-a", ["l-land", "l-model"]), ("ab-a", ["ab-ours", "ab-scale"]), ("wg-a", ["wg-habit", "wg-eight"]), ("ct-a", ["ct-edge", "ct-in"]),
    ("d-a", ["d-q", "d-spread"]), ("rs-a", ["rs-steam", "rs-count"]), ("ww-a", ["ww-on", "ww-pipes"]), ("ww-b", ["ww-fires", "ww-unknown"]), ("fo-a", ["fo-able", "fo-wig"]), ("x-a", ["x-react", "x-radio"]), ("x-b", ["x-wing", "x-emp"]), ("g-b", ["g-bridge", "g-answer"]),
]
for m in MERGES2:
    merge(*m)
for m in MERGES:
    merge(*m)

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
        for a, b in zip(times, times[1:]):
            limit = 3.6 if a < 90 else 5.4
            if b - a <= limit:
                continue
            s = next((x for x in shots if x["start"] <= a + 1e-6 < x["end"]), None)
            if not s or s["type"] not in ("region", "globe", "city") or "camera" not in s:
                continue
            n = math.ceil((b - a) / limit) - 1
            fields = ["center", "widthKm"] if s["type"] in ("region", "city") else ["lat", "lon", "scale"]
            for i in range(1, n + 1):
                tt = round(a + (b - a) * i / (n + 1) - s["start"], 2)
                key = {"t": tt}
                key.update(interp(s["camera"], tt, fields))
                s["camera"].append(key)
            s["camera"].sort(key=lambda k: k["t"])
            changed = True
        if not changed:
            break


densify()


# ------------------------------------------------------------------ audio plan and output
booms = [tF + 0.1, FX_T + 0.1]
b0 = round(min(tF - 0.3, W("p02", "simulation") - 0.3), 2)
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
            m.pop("_id", None)
            if m.get("label") in (None, ""):
                m.pop("label", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
