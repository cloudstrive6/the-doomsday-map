"""Director pass for episode 008: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 008-full-nuclear-war-minute-by-minute
Globe-heavy (brief: "globe only"): arcs and flashes on the globe, region and city shots only where a place needs ground.
Colours: US blue, Russia amber, strikes and flashes red/orange, SIMULATION red. Missiles are drawn in the colour of the side
that fired them. Shots are written in sequence: every helper starts at the previous shot's end (`CUR`), so there are no gaps.
"""
import json
import math
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = [w for w in json.load(open(EP / "narration" / "words.json", encoding="utf-8")) if not w["word"].startswith("[")]
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW, BLUE = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F", "#6EA8FF"
DIM = "rgba(236,239,242,0.95)"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]
END = round(WORDS[-1]["end"] + 10, 2)
ST = {s["id"]: s for s in sc["strikes"]}


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (0.15 s early so the picture leads the voice)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!\"").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
BANGOR, SEATTLE = [-122.72, 47.72], [-122.33, 47.61]
BEALE, CAPECOD, DC, KINGSBAY = [-121.44, 39.14], [-70.54, 41.75], [-77.06, 38.87], [-81.52, 30.8]
NYC, LA = [-74.0, 40.71], [-118.24, 34.05]
MINOT, MALMSTROM, WARREN, CHEYENNE = [-101.36, 48.42], [-111.19, 47.5], [-104.87, 41.15], [-104.85, 38.74]
OFFUTT, WHITEMAN, BARKSDALE = [-95.9145, 41.1183], [-93.55, 38.73], [-93.66, 32.5]
VANDENBERG = [-120.57, 34.74]
KALININGRAD, RAMSTEIN = [21.5, 54.9], [7.6, 49.437]
SEVERO, VILYU, PLESETSK, MOSCOW, STPETE = [33.3, 69.25], [158.4, 52.93], [40.3, 62.7], [37.62, 55.75], [30.33, 59.93]
KOZELSK, TEYKOVO, TATISH, NOVOS, UZHUR, DOMB = [35.78, 54.03], [40.55, 56.85], [45.58, 51.67], [82.9, 55.0], [89.83, 55.32], [59.84, 51.09]
PAC, ATL, NORSEA, KAMCH = [-155.0, 42.0], [-40.0, 40.0], [-15.0, 72.0], [-175.0, 44.0]
SERPUKHOV, ANDOYA, OLENEGORSK = [37.4, 54.84], [16.13, 69.3], [33.9, 68.1]
USA, RUSSIA = "840", "643"
HL_US = {"iso": USA, "color": BLUE, "fill": "rgba(110,168,255,0.08)"}
HL_RU = {"iso": RUSSIA, "color": AMBER, "fill": "rgba(242,176,30,0.08)"}
HL_BOTH = [HL_US, HL_RU]
FX_BANGOR = ST["rus-slbm-bangor"]["effects"]
FX_OFFUTT = ST["rus-icbm-offutt"]["effects"]
FX_RAM = ST["isk-ramstein"]["effects"]

shots = []
CUR = 0.0


def add(**k):
    shots.append(k)


def rel(a, t):
    return round(max(0.0, t - a), 2)


def M(t, at, label=None, color=WHITE, kind="dot", size=None):
    return (t, at, label, color, kind, size)


def _marks(a, marks):
    out = []
    for t, at, label, color, kind, size in marks:
        d = {"at": at, "color": color, "kind": kind, "t": rel(a, t)}
        if label:
            d["label"] = label
        if size:
            d["size"] = size
        out.append(d)
    return out


def _keys(a, b, keys):
    out = []
    for t, *rest in keys:
        tt = 0 if t == "s" else (round(b - a, 2) if t == "e" else round(t, 2))
        out.append((tt, rest))
    return out


# ------------------------------------------------------------------ arcs (absolute launch and landing times)
T_RU = W("p19", "launched")
T_USI = W("p21", "fires")
T_USS = W("p23", "fire")
T_LAST = W("p28", "fire")
FLASH = {  # video time of each strike, on the word that names it
    "rus-slbm-capecod": W("p22", "Cape"), "rus-slbm-bangor": W("p22", "Bangor"), "rus-slbm-beale": W("p22", "Beale"),
    "rus-slbm-dc": W("p24", "Washington"), "rus-slbm-kingsbay": W("p24", "follows"),
    "us-slbm-severomorsk": W("p25", "Murmansk"), "us-slbm-vilyuchinsk": W("p25", "Vilyuchinsk"), "us-slbm-plesetsk": W("p25", "Plesetsk"), "us-slbm-moscow": W("p25", "Moscow's"),
    "rus-icbm-minot": W("p26", "Minot"), "rus-icbm-malmstrom": W("p26", "Malmstrom"), "rus-icbm-warren": W("p26", "Warren"), "rus-icbm-cheyenne": W("p26", "Cheyenne"),
    "rus-icbm-offutt": W("p26", "Offutt"), "rus-icbm-whiteman": W("p26", "bomber"), "rus-icbm-barksdale": W("p26", "bomber"),
    "us-icbm-kozelsk": W("p27", "Kozelsk"), "us-icbm-teykovo": W("p27", "Teykovo"), "us-icbm-tatishchevo": W("p27", "Tatishchevo"),
    "us-icbm-novosibirsk": W("p27", "Novosibirsk"), "us-icbm-uzhur": W("p27", "Uzhur"), "us-icbm-dombarovsky": W("p27", "Dombarovsky"),
    "rus-slbm-nyc": W("p28", "York"), "rus-slbm-la": W("p28", "Angeles"), "us-slbm-stpete": W("p28", "Petersburg"), "us-slbm-moscow2": W("p28", "Moscow"),
}
ARCS = {}
for sid, s in ST.items():
    if sid == "isk-ramstein":
        continue
    russian = sid.startswith("rus-")
    if s["weapon_class"] == "slbm":
        t0 = T_RU if sid not in ("rus-slbm-nyc", "rus-slbm-la") and russian else (T_LAST if sid in ("rus-slbm-nyc", "rus-slbm-la", "us-slbm-stpete", "us-slbm-moscow2") else T_USS)
    else:
        t0 = T_RU if russian else T_USI
    ARCS[sid] = {"from": [s["launch_lon"], s["launch_lat"]], "to": [s["target_lon"], s["target_lat"]], "t0": t0, "t1": FLASH[sid], "color": AMBER if russian else BLUE,
                 "loft": 0.12 if s["weapon_class"] == "slbm" else 0.2}


def arcs_for(a, b, pick):
    """Arcs of the strikes in `pick` (ids or id prefixes) that are in the air at some point of [a, b]."""
    out = []
    for sid, ar in ARCS.items():
        if not any(sid.startswith(p) for p in pick):
            continue
        if ar["t1"] + 1.0 < a or ar["t0"] > b:
            continue
        out.append({"from": ar["from"], "to": ar["to"], "t0": round(ar["t0"] - a, 2), "t1": round(ar["t1"] - a, 2), "color": ar["color"], "loft": ar["loft"]})
    return out


def flashes_for(a, b, pick, radius=None):
    out = []
    for sid, t in FLASH.items():
        if any(sid.startswith(p) for p in pick) and a - 0.01 <= t < b:
            d = {"at": [ST[sid]["target_lon"], ST[sid]["target_lat"]], "t": rel(a, t) + 0.05}
            if radius:
                d["radius"] = radius
            out.append(d)
    return out


def clk(minute, rate, label="SIMULATION CLOCK"):
    m = int(minute)
    s = int(round((minute - m) * 60))
    return dict(clock=f"T+{m:02d}:{s:02d}", clockLabel=label, clockRate=rate)


def G(sid, b, keys, marks=(), arcs=(), flashes=(), highlight=None, **kw):
    """Globe shot from CUR to b. keys: (time or 's'/'e', lat, lon, scale)."""
    global CUR
    a = CUR
    ks = _keys(a, b, keys)
    cam = [{"t": t, "lat": r[0], "lon": r[1], "scale": r[2]} for t, r in ks]
    d = dict(id=sid, type="globe", start=a, end=b, camera=cam, sun=SUN, highlight=highlight if highlight is not None else HL_BOTH, markers=_marks(a, marks), arcs=list(arcs), flashes=list(flashes))
    d.update(kw)
    add(**d)
    CUR = b


def R(sid, b, keys, cities=(), labels=(), rings=(), burst=None, highlight=None, **kw):
    """Region shot from CUR to b. keys: (time or 's'/'e', [lon, lat], widthKm)."""
    global CUR
    a = CUR
    ks = _keys(a, b, keys)
    cam = [{"t": t, "center": r[0], "widthKm": r[1]} for t, r in ks]
    d = dict(id=sid, type="region", start=a, end=b, view={"center": cam[0]["center"], "widthKm": cam[0]["widthKm"]}, camera=cam,
             highlight=highlight if highlight is not None else HL_BOTH, cities=_marks(a, cities),
             labels=[{"at": at, "text": tx, "color": col, "t": rel(a, t)} for t, at, tx, col in labels],
             rings=[{"at": at, "km": km, "color": col, "label": lb, "t": rel(a, t), "dashed": dsh} for t, at, km, col, lb, dsh in rings])
    if burst:
        d["burst"] = {"at": burst[0], "t": rel(a, burst[1]), "km": burst[2], "fade": burst[3] if len(burst) > 3 else 6}
    d.update(kw)
    add(**d)
    CUR = b


def C(sid, b, city, keys, gz, rings=(), labels=(), flashT=None, **kw):
    global CUR
    a = CUR
    ks = _keys(a, b, keys)
    cam = [{"t": t, "center": r[0], "widthKm": r[1]} for t, r in ks]
    d = dict(id=sid, type="city", start=a, end=b, city=city, view={"center": cam[0]["center"], "widthKm": cam[0]["widthKm"]}, camera=cam, gz=gz,
             rings=[{"km": km, "label": lb, "color": col, "t": rel(a, t), "angle": ang} for t, km, lb, col, ang in rings],
             labels=[{"at": at, "text": tx, "color": col, "t": rel(a, t)} for t, at, tx, col in labels])
    if flashT is not None:
        d["flashT"] = rel(a, flashT)
    d.update(kw)
    add(**d)
    CUR = b


def card(sid, b, **kw):
    global CUR
    add(id=sid, start=CUR, end=b, **kw)
    CUR = b


def chapter(sid, n, title, dur=3.5):
    card(sid, round(CUR + dur, 2), type="chapter", kicker=f"CHAPTER {n:02d}", title=title)


# ================================================================== Cold open [SIMULATION]
# 0 to 8 s: the worst moment on a real target. Flash on the word "nuclear" (minute sixteen, Bangor, Washington State).
tF = round(W("p01", "nuclear") + 0.05, 2)
G("open-run", tF, [("s", 46.0, -141, 1350), (1.8, 46.6, -134, 1650), ("e", 47.4, -127, 2150)],
  marks=[M(0.1, PAC, "Submarine (location simulated)", AMBER, "sub", 5), M(1.2, BANGOR, "Bangor, Washington", RED, "target", 6), M(2.2, SEATTLE, "Seattle", WHITE, "dot")],
  arcs=[{"from": PAC, "to": BANGOR, "t0": -5.0, "t1": tF, "color": AMBER, "loft": 0.1}], highlight=[HL_US], **clk(15.73, 1), tag="SIMULATION")
C("open-flash", 7.6, "bangor", [("s", [-122.72, 47.72], 52), (2.0, [-122.7, 47.72], 38), ("e", [-122.68, 47.72], 26)], BANGOR,
  rings=[(tF + 1.0, FX_BANGOR["psi5_km"], "5 psi", RED, 80)],
  labels=[(tF + 0.5, BANGOR, "Naval Base Kitsap, Bangor", WHITE), (tF + 1.9, [-122.55, 47.83], "Puget Sound", DIM), (tF + 2.8, [-122.62, 47.6], "Hood Canal", DIM)],
  flashT=tF + 0.1, caption="SIMULATION: IT HAS NOT HAPPENED", **clk(15.8, 1, "BANGOR, WASHINGTON"))
G("open-us", 10.2, [("s", 46.5, -121, 1750), ("e", 40.0, -100, 1050)],
  marks=[M(7.7, BANGOR, "Bangor", RED, "target", 6), M(9.0, DC, "Washington, DC", WHITE, "dot")], highlight=[HL_US], caption="SIMULATION: IT HAS NOT HAPPENED", **clk(15.9, 1))
G("open-us2", S("p03"), [("s", 40.0, -100, 1050), ("e", 42.0, -135, 1300)], caption="SIMULATION: IT HAS NOT HAPPENED",
  marks=[M(10.6, PAC, "Submarine (location simulated)", AMBER, "sub", 5), M(11.5, BEALE, "Beale", WHITE, "dot")], highlight=[HL_US], **clk(5.0, 0, "ELEVEN MINUTES EARLIER"))
# p03: both coasts, then silos, then "it is over"  (clock: T+05:00 launch to T+14:00 when the US fires)
tP = CUR
G("open-pac", W("p03", "both") - 0.1, [("s", 42.0, -140, 1250), ("e", 44.5, -131, 1750)],
  marks=[M(tP + 0.5, BANGOR, "Bangor, Washington", RED, "target", 6), M(tP + 1.4, BEALE, "Beale radar", RED, "target", 6), M(W("p03", "submarines"), PAC, "Submarine (location simulated)", AMBER, "sub", 5)],
  arcs=[{"from": PAC, "to": BANGOR, "t0": round(W("p03", "left") - tP, 2), "t1": 5.0, "color": AMBER, "loft": 0.1},
        {"from": PAC, "to": BEALE, "t0": round(W("p03", "left") - tP + 0.4, 2), "t1": 5.4, "color": AMBER, "loft": 0.1}],
  highlight=[HL_US], **clk(5.0, 75, "ELEVEN MINUTES EARLIER"))
tAtl = CUR
G("open-atl", W("p03", "American", 2) - 0.15, [("s", 38.0, -62, 1050), ("e", 37.0, -76, 1650)],
  marks=[M(tAtl + 0.1, ATL, "Submarine (location simulated)", AMBER, "sub", 5), M(tAtl + 1.0, CAPECOD, "Cape Cod", RED, "target", 6), M(tAtl + 1.8, DC, "Washington", RED, "target", 6), M(tAtl + 2.6, KINGSBAY, "Kings Bay", RED, "target", 6)],
  arcs=[{"from": ATL, "to": CAPECOD, "t0": 0.3, "t1": 5.5, "color": AMBER, "loft": 0.1}, {"from": ATL, "to": DC, "t0": 0.5, "t1": 5.7, "color": AMBER, "loft": 0.1}, {"from": ATL, "to": KINGSBAY, "t0": 0.7, "t1": 5.9, "color": AMBER, "loft": 0.1}],
  highlight=[HL_US], **clk(9.1, 75, "ELEVEN MINUTES EARLIER"))
tSil = CUR
G("open-silo", W("p03", "By") - 0.15, [("s", 46.0, -102, 1250), ("e", 52.0, -80, 1000)],
  marks=[M(tSil + 0.2, MINOT, "Silo field", BLUE, "base", 5), M(tSil + 0.7, MALMSTROM, "Silo field", BLUE, "base", 5), M(tSil + 1.2, WARREN, "Silo field", BLUE, "base", 5)],
  arcs=[{"from": MINOT, "to": KOZELSK, "t0": 0.3, "t1": 6.0, "color": BLUE, "loft": 0.22}, {"from": MALMSTROM, "to": NOVOS, "t0": 0.5, "t1": 6.0, "color": BLUE, "loft": 0.22}, {"from": WARREN, "to": TEYKOVO, "t0": 0.7, "t1": 6.0, "color": BLUE, "loft": 0.22}],
  **clk(14.0, 40, "AMERICAN MISSILES LEAVE"))
fl = []
for i, (sid, s) in enumerate(sorted(ST.items(), key=lambda kv: kv[1]["impact_min"])):
    fl.append({"at": [s["target_lon"], s["target_lat"]], "t": round(0.1 + i * 0.09, 2), "radius": 34})
G("open-over", S("p04"), [("s", 55.0, -45, 640), ("e", 52.0, 0, 760)], flashes=fl, **clk(53.0, 0, "MINUTE FIFTY-THREE"))
# p04
G("p04-one", W("p04", "How") - 0.1, [("s", 52.0, 14, 2300), ("e", 51.5, 14, 2900)],
  marks=[M(W("p04", "missile") - 0.4, KALININGRAD, "Kaliningrad (launch simulated)", AMBER, "base", 5), M(W("p04", "missile") + 0.3, RAMSTEIN, "Ramstein Air Base", RED, "target", 6)],
  arcs=[{"from": KALININGRAD, "to": RAMSTEIN, "t0": round(W("p04", "one") - CUR, 2), "t1": 5.4, "color": AMBER, "loft": 0.1}], **clk(0.0, 90, "MINUTE ZERO"))
G("p04-pull", S("p05"), [("s", 50.5, 14, 2400), ("e", 42.0, -30, 650)],
  marks=[M(W("p04", "become"), BANGOR, None, RED, "target", 6), M(W("p04", "this") + 0.2, BEALE, None, RED, "target", 5)], **clk(53.0, 0, "UNDER AN HOUR"))

# ================================================================== Chapter 01 [REAL DATA]
chapter("c1-card", 1, "The real forces")
a = CUR  # 35.1
G("c1-van", W("p05", "Vandenberg") + 0.1, [("s", 40.0, -100, 1000), ("e", 37.0, -115, 1750)],
  marks=[M(W("p05", "Air"), [-98.0, 39.0], "US Air Force", BLUE, "dot", 5), M(W("p05", "Minuteman") + 0.1, VANDENBERG, "Unarmed Minuteman III", BLUE, "base", 5)], highlight=[HL_US],
  clock="20 MAY 2026", clockLabel="UNARMED TEST", clockRate=0, source="US Air Force Global Strike Command; Bulletin of the Atomic Scientists")
G("c1-van2", S("p06"), [("s", 35.5, -117, 3000), (2.0, 34.9, -120, 4200), ("e", 34.9, -121, 5200)],
  marks=[M(CUR + 0.1, VANDENBERG, "Vandenberg, California", BLUE, "base", 6), M(W("p05", "It") + 0.3, [-122.0, 37.8], "Scheduled for years", WHITE, "ring", 6)], caption="A test scheduled for years", highlight=[HL_US],
  clock="20 MAY 2026", clockLabel="UNARMED TEST", clockRate=0, source="US Air Force Global Strike Command; Bulletin of the Atomic Scientists")
G("c1-ru", W("p06", "sixty-four") - 0.2, [("s", 58.0, 45, 1050), ("e", 60.0, 62, 1350)],
  marks=[M(W("p06", "Russia"), [60.0, 57.0], "Russia", AMBER, "dot", 5), M(W("p06", "three-day"), [90.0, 62.0], "Nuclear forces exercise", AMBER, "dot", 5)], highlight=[HL_RU],
  clock="19 MAY 2026", clockLabel="THREE-DAY EXERCISE", clockRate=0, source="Russian defence ministry via AP, 2026-05-19")
G("c1-troops", W("p06", "thirteen") - 0.1, [("s", 58.0, 48, 1100), ("e", 55.0, 35, 1500)],
  highlight=[HL_RU], caption="64,000 troops",
  clock="19 MAY 2026", clockLabel="THREE-DAY EXERCISE", clockRate=0, source="Russian defence ministry via AP, 2026-05-19")
G("c1-subs", W("p06", "and") - 0.1, [("s", 66.0, 40, 1500), (1.5, 60.0, 100, 1000), ("e", 56.0, 150, 1300)],
  marks=[M(W("p06", "thirteen"), SEVERO, "Northern Fleet", AMBER, "sub", 5), M(W("p06", "thirteen") + 1.2, VILYU, "Pacific Fleet", AMBER, "sub", 5)], highlight=[HL_RU], caption="13 submarines",
  clock="19 MAY 2026", clockLabel="THREE-DAY EXERCISE", clockRate=0, source="Russian defence ministry via AP, 2026-05-19")
G("c1-aim", S("p07"), [("s", 55.0, 40, 700), ("e", 45.0, -10, 800)],
  marks=[M(W("p06", "practising"), MOSCOW, "Practising nuclear use", AMBER, "dot", 5), M(W("p06", "threat") - 0.2, [10.0, 55.0], "Under threat of aggression", YELLOW, "ring", 6)], highlight=HL_BOTH, caption="Stated aim: practise nuclear use under the threat of aggression",
  clock="19 MAY 2026", clockLabel="THREE-DAY EXERCISE", clockRate=0, source="Russian defence ministry via AP, 2026-05-19")
# p07: the missiles from the opening
G("c1-sub-miss", W("p07", "submarines") - 0.3, [("s", 42.0, -58, 1050), ("e", 40.0, -72, 1500)],
  marks=[M(CUR + 0.1, ATL, "Submarine (location simulated)", AMBER, "sub", 5)],
  arcs=[{"from": ATL, "to": DC, "t0": 0.2, "t1": 4.0, "color": AMBER, "loft": 0.1}], highlight=[HL_US], **clk(0.0, 170, "SUBMARINE MISSILE"))
G("c1-sub-time", W("p07", "ones", 2) - 0.05, [("s", 40.0, -62, 1100), ("e", 38.0, -78, 1750)],
  marks=[M(W("p07", "ten"), DC, "About 10 to 14 minutes", RED, "target", 6)],
  arcs=[{"from": ATL, "to": DC, "t0": -0.1, "t1": round(W("p07", "minutes") - CUR + 0.6, 2), "color": AMBER, "loft": 0.1}], highlight=[HL_US], **clk(0.0, 190, "SUBMARINE MISSILE"))
G("c1-silo-time", S("p08"), [("s", 55.0, -30, 760), (2.0, 52.0, 10, 900), ("e", 50.0, 40, 1100)],
  marks=[M(W("p07", "silos"), KOZELSK, "Silo missile: about 30 minutes", BLUE, "dot", 5)],
  arcs=[{"from": MINOT, "to": KOZELSK, "t0": round(W("p07", "silos") - CUR, 2), "t1": round(W("p07", "thirty") - CUR + 1.2, 2), "color": BLUE, "loft": 0.25}], **clk(0.0, 450, "SILO MISSILE"))
# p08 treaty ended
G("c1-start", W("p08", "For") - 0.1, [("s", 45.0, -20, 700), ("e", 50.0, 20, 820)],
  marks=[M(S("p08") + 0.4, [-98.0, 40.0], "United States", BLUE, "dot", 5), M(W("p08", "arsenals"), [60.0, 56.0], "Russia", AMBER, "dot", 5)], caption="New START expired, February 2026",
  clock="FEB 2026", clockLabel="NEW START EXPIRED", clockRate=0, source="Arms Control Association, 2026")
G("c1-nocap", S("p09"), [("s", 50.0, 20, 800), ("e", 48.0, -20, 700)],
  marks=[M(W("p08", "no"), [-30, 50], "No treaty caps either side", YELLOW, "dot", 5)], caption="For the first time in decades, no cap",
  clock="FEB 2026", clockLabel="NEW START EXPIRED", clockRate=0, source="Arms Control Association, 2026")
# p09 numbers
G("c1-ru-war", W("p09", "deployed") + 0.3, [("s", 57.0, 45, 1000), ("e", 56.0, 60, 1500)],
  marks=[M(W("p09", "eighteen"), MOSCOW, "Russia: about 1,800 deployed", AMBER, "dot", 6)], highlight=[HL_RU], clock="2026", clockLabel="DEPLOYED STRATEGIC WARHEADS", clockRate=0, source="FAS; Bulletin of the Atomic Scientists")
card("c1-bars", 90.0, type="bars", title="Deployed strategic warheads", sub="about, 2026 estimates", source="FAS; Bulletin of the Atomic Scientists",
     bars=[{"label": "Russia", "value": 1800, "display": "about 1,800", "color": AMBER}, {"label": "United States", "value": 1700, "display": "about 1,700", "color": BLUE}])
G("c1-minuteman", W("p09", "one") - 0.5, [("s", 45.0, -104, 1800), ("e", 44.0, -102, 2300)],
  marks=[M(W("p09", "four"), MINOT, "Minot", BLUE, "base", 5), M(W("p09", "four") + 0.6, MALMSTROM, "Malmstrom", BLUE, "base", 5), M(W("p09", "four") + 1.2, WARREN, "F.E. Warren", BLUE, "base", 5)],
  highlight=[HL_US], caption="400 Minuteman missiles", clock="2026", clockLabel="US LAND FORCE", clockRate=0, source="Bulletin of the Atomic Scientists, 2025")
G("c1-one", W("p09", "Russia", 2) - 0.1, [("s", 44.0, -103, 2300), ("e", 44.5, -103, 3100)],
  marks=[M(W("p09", "one"), [-103.5, 44.5], "One warhead each", WHITE, "ring", 6)], highlight=[HL_US], caption="One warhead each",
  clock="2026", clockLabel="US LAND FORCE", clockRate=0, source="Bulletin of the Atomic Scientists, 2025")
G("c1-ru-land", W("p09", "thirteen") - 0.1, [("s", 56.0, 45, 1500), ("e", 56.0, 70, 1250)],
  marks=[M(W("p09", "land"), KOZELSK, "Kozelsk", AMBER, "base", 5), M(W("p09", "land") + 0.5, NOVOS, "Novosibirsk", AMBER, "base", 5), M(W("p09", "three") + 0.3, TEYKOVO, "About 324 land missiles", AMBER, "base", 5)],
  highlight=[HL_RU], clock="2026", clockLabel="RUSSIA LAND FORCE", clockRate=0, source="CRS IF12672; Bulletin of the Atomic Scientists, 2026")
G("c1-ru-subs", S("p10"), [("s", 68.0, 40, 1400), ("e", 62.0, 110, 1050)],
  marks=[M(W("p09", "thirteen") + 0.2, SEVERO, "Northern Fleet", AMBER, "sub", 5), M(W("p09", "ballistic-missile") + 0.5, VILYU, "13 missile submarines", AMBER, "sub", 5)],
  highlight=[HL_RU], clock="2026", clockLabel="RUSSIA SUBMARINES", clockRate=0, source="CRS IF12672; Bulletin of the Atomic Scientists, 2026")
G("c1-time", W("p10", "harder") - 0.15, [("s", 48.0, -20, 650), ("e", 45.0, 0, 800)],
  marks=[M(W("p10", "forces"), [-98.0, 40.0], "United States", BLUE, "dot", 5), M(W("p10", "forces") + 0.3, [60.0, 56.0], "Russia", AMBER, "dot", 5)], caption="Those are the forces.")
G("c1-decide", S("p11"), [("s", 44.0, -30, 760), (2.2, 42.0, -10, 960), ("e", 40.0, -60, 700)],
  marks=[M(W("p10", "time"), [-30, 50], "How long to decide?", YELLOW, "ring", 6)], caption="How long does anyone get to decide?")

# ================================================================== Chapter 02 [REAL HISTORY]
chapter("c2-card", 2, "Ten minutes")
G("c2-ready", W("p11", "Launch") - 0.1, [("s", 45.0, -108, 1900), ("e", 44.0, -100, 2300)],
  marks=[M(W("p11", "four"), MINOT, "Minot", BLUE, "base", 5), M(W("p11", "four") + 0.5, MALMSTROM, "Malmstrom", BLUE, "base", 5), M(W("p11", "four") + 1.0, WARREN, "F.E. Warren", BLUE, "base", 5),
         M(W("p11", "ready"), [-103.0, 46.0], "Ready within minutes", WHITE, "ring", 6)], highlight=[HL_US])
G("c2-low-a", W("p11", "before") - 0.2, [("s", 42.0, -70, 900), ("e", 43.0, -48, 1100)],
  marks=[M(W("p11", "alarm") - 1.0, CAPECOD, "1. The alarm", YELLOW, "target", 6)],
  arcs=[{"from": [20.0, 60.0], "to": CAPECOD, "t0": 0.4, "t1": 7.0, "color": AMBER, "loft": 0.3}], highlight=[HL_US], clock="LAUNCH ON WARNING", clockLabel="FIRE AFTER THE ALARM", clockRate=0)
G("c2-low-b", W("p11", "Bruce") - 0.1, [("s", 45.0, -100, 1350), ("e", 52.0, -60, 1000)],
  marks=[M(CUR + 0.1, MINOT, "2. US fires", BLUE, "base", 5)],
  arcs=[{"from": MINOT, "to": KOZELSK, "t0": 0.3, "t1": 8.0, "color": BLUE, "loft": 0.25}, {"from": [20.0, 60.0], "to": CAPECOD, "t0": -3.0, "t1": 2.8, "color": AMBER, "loft": 0.3}],
  flashes=[{"at": CAPECOD, "t": 2.85, "radius": 26}], clock="LAUNCH ON WARNING", clockLabel="BEFORE THE FIRST WARHEAD LANDS", clockRate=0)
G("c2-blair", W("p11", "have") - 0.2, [("s", 40.0, -94, 1500), ("e", 39.0, -77, 2400)],
  marks=[M(W("p11", "president") - 0.3, DC, "Washington: the president", BLUE, "target", 6)], highlight=[HL_US], caption="Bruce Blair, former launch officer",
  source="Bruce Blair, Bulletin of the Atomic Scientists")
card("c2-ten", S("p12"), type="number", value="10 MINUTES", countTo=10, suffix=" MINUTES", label="at most, about, for the president to decide", sub="Bruce Blair's estimate", color=AMBER, source="Bruce Blair; Bulletin of the Atomic Scientists")
# p12 Petrov 1983
G("c2-83a", W("p12", "five") - 0.4, [("s", 52.0, 20, 1000), ("e", 54.0, 40, 1500)],
  marks=[M(S("p12") + 0.3, MOSCOW, "Moscow", AMBER, "dot", 5), M(W("p12", "Soviet") + 0.2, [45.0, 50.0], "Soviet early-warning satellites", AMBER, "base", 5)],
  highlight=[HL_RU], clock="26 SEPT 1983", clockLabel="SOVIET EARLY WARNING", clockRate=0, source="Bruce Blair, Bulletin, 2017; Washington Post, 1999")
fl5 = [[-100.0 + i * 3, 46.0 - i] for i in range(5)]
G("c2-83b", W("p12", "Stanislav") - 0.3, [("s", 52.0, -40, 800), ("e", 53.0, 20, 1000)],
  marks=[M(W("p12", "five") + 0.1, [-104.0, 46.0], "5 missiles reported", RED, "target", 6)],
  arcs=[{"from": p, "to": [37.4 + i * 3, 56.0], "t0": round(W("p12", "five") - CUR, 2) + i * 0.15, "t1": 6.0, "color": BLUE, "loft": 0.3} for i, p in enumerate(fl5)],
  highlight=HL_BOTH, clock="26 SEPT 1983", clockLabel="SOVIET EARLY WARNING", clockRate=0, source="Bruce Blair, Bulletin, 2017; Washington Post, 1999")
R("c2-83c", W("p12", "a", 3) - 0.2, [("s", SERPUKHOV, 330), (2.5, SERPUKHOV, 220), ("e", [37.5, 55.0], 180)],
  cities=[M(CUR + 0.2, SERPUKHOV, "Serpukhov-15 bunker", AMBER, "base", 6), M(CUR + 0.4, MOSCOW, "Moscow", WHITE, "dot", 5), M(W("p12", "Petrov"), [37.4, 54.84], "Lt. Col. Stanislav Petrov", WHITE, "ring", 6)],
  labels=[(W("p12", "false"), [38.3, 55.55], "Judged: false alarm", YELLOW)], clock="26 SEPT 1983", clockLabel="SERPUKHOV-15, NEAR MOSCOW", clockRate=0, source="Bruce Blair, Bulletin, 2017")
manyA = [{"from": [-100.0 + (i % 8) * 4, 36.0 + (i // 8) * 3], "to": [25.0 + (i % 10) * 5, 52.0 + (i // 10) * 2], "t0": 0.3 + i * 0.07, "t1": 3.8 + i * 0.04, "color": BLUE, "loft": 0.3} for i in range(40)]
G("c2-83d", W("p12", "cause") - 0.1, [("s", 50.0, -40, 760), ("e", 54.0, 10, 900)],
  marks=[M(W("p12", "hundreds"), [-30.0, 62.0], "A real strike: hundreds of missiles", RED, "ring", 6)], arcs=manyA, clock="26 SEPT 1983", clockLabel="WHY IT WAS DOUBTED", clockRate=0, source="Bruce Blair, Bulletin, 2017")
G("c2-83e", W("p12", "That") - 0.1, [("s", 44.0, -112, 2600), ("e", 46.0, -105, 3400)],
  marks=[M(W("p12", "sunlight") - 0.3, [-111.19, 47.5], "Sunlight on cloud tops", YELLOW, "ring", 6)], highlight=[HL_US], clock="26 SEPT 1983", clockLabel="THE CAUSE", clockRate=0, source="Bruce Blair, Bulletin, 2017")
G("c2-83f", W("p12", "Our") - 0.2, [("s", 52.0, 30, 1500), ("e", 55.0, 37, 2200)],
  marks=[M(W("p12", "person") - 0.3, MOSCOW, "A person said so", WHITE, "ring", 6)], highlight=[HL_RU], caption="The warning was wrong, and a person said so.", clock="26 SEPT 1983", clockLabel="THAT NIGHT", clockRate=0, source="Bruce Blair, Bulletin, 2017")
G("c2-83g", S("p13"), [("s", 45.0, 10, 800), ("e", 45.0, -50, 700)],
  marks=[M(W("p12", "right") - 0.8, [-60.0, 52.0], "Our simulation: the warning is right", RED, "ring", 6)], caption="What happens when the warning is right?")
# p13 Norway 1995
G("c2-95a", W("p13", "Norwegian") - 0.2, [("s", 64.0, 20, 1000), ("e", 66.0, 20, 1500)],
  marks=[M(S("p13") + 0.3, [15.0, 62.0], "Norway", WHITE, "dot", 5)], highlight=[], clock="25 JAN 1995", clockLabel="NORWAY AND RUSSIA", clockRate=0, source="EUCOM History Office; Wikipedia, Norwegian rocket incident")
G("c2-95b", W("p13", "The", 2) - 0.2, [("s", 68.0, 18, 3500), ("e", 70.0, 22, 4300)],
  marks=[M(W("p13", "northern"), ANDOYA, "Andoya, northern Norway", WHITE, "base", 6)], arcs=[{"from": ANDOYA, "to": [27.0, 74.5], "t0": round(W("p13", "launched") - CUR, 2), "t1": round(W("p13", "launched") - CUR + 3.0, 2), "color": WHITE, "loft": 0.5}],
  highlight=[], clock="25 JAN 1995", clockLabel="SCIENCE ROCKET", clockRate=0, source="EUCOM History Office; Wikipedia, Norwegian rocket incident")
R("c2-95c", W("p13", "who") - 0.2, [("s", [31.0, 68.6], 900), (2.5, [32.0, 68.4], 620), ("e", [33.5, 68.4], 480)],
  cities=[M(W("p13", "Russian") - 0.1, OLENEGORSK, "Olenegorsk radar", AMBER, "base", 6), M(CUR + 0.2, [33.08, 68.97], "Murmansk", WHITE, "dot", 5)],
  labels=[(W("p13", "never"), [28.2, 69.3], "The notice never arrived", YELLOW)], clock="25 JAN 1995", clockLabel="RUSSIAN RADAR CREWS", clockRate=0, source="EUCOM History Office; Wikipedia, Norwegian rocket incident")
G("c2-95d", W("p13", "nuclear") - 0.15, [("s", 70.0, 30, 3300), ("e", 68.0, 36, 3000)],
  marks=[M(W("p13", "track"), [28.0, 72.0], "Possible Trident missile?", RED, "ring", 6), M(W("p13", "Trident"), OLENEGORSK, "Olenegorsk radar", AMBER, "base", 5)],
  arcs=[{"from": ANDOYA, "to": [30.0, 74.0], "t0": 0.0, "t1": 3.4, "color": RED, "loft": 0.5}], highlight=[], clock="25 JAN 1995", clockLabel="A POSSIBLE TRIDENT", clockRate=0, source="EUCOM History Office; Wikipedia, Norwegian rocket incident")
G("c2-95e", W("p13", "Russian", 2) - 0.2, [("s", 52.0, 20, 1700), ("e", 55.0, 37, 2900)],
  marks=[M(W("p13", "briefcase"), MOSCOW, "The briefcase goes to Yeltsin", AMBER, "target", 6)], highlight=[HL_RU], clock="25 JAN 1995", clockLabel="MOSCOW", clockRate=0, source="EUCOM History Office; Wikipedia, Norwegian rocket incident")
card("c2-95f", W("p13", "No") - 0.2, type="timeline", title="Russian forces on alert", sub="about 8 minutes, out of a window of about 10", total=10, unit="MIN",
     segments=[{"from": 0, "to": 8, "label": "On alert", "color": AMBER}, {"from": 8, "to": 10, "label": "Window ends", "color": RED}], highlight={"from": 8, "to": 10, "label": "no order given"}, cursorTo=8, source="Wikipedia, Norwegian rocket incident, citing EUCOM History Office")
G("c2-95g", S("p14"), [("s", 62.0, 30, 1000), ("e", 62.0, 15, 1200)],
  marks=[M(W("p13", "order"), MOSCOW, "No order was given", WHITE, "ring", 6)], highlight=[HL_RU], caption="No order was given.")
# p14
G("c2-ten-sub", W("p14", "So") - 0.2, [("s", 72.0, 20, 1500), ("e", 66.0, 30, 1800)],
  marks=[M(S("p14") + 0.2, [20.0, 74.0], "Submarine (location simulated)", BLUE, "sub", 5)],
  arcs=[{"from": [20.0, 74.0], "to": MOSCOW, "t0": 0.4, "t1": 4.4, "color": BLUE, "loft": 0.12}], highlight=[HL_RU], **clk(0.0, 150, "SUBMARINE MISSILE"))
G("c2-real", S("p15"), [("s", 45.0, -20, 700), ("e", 48.0, 10, 880)],
  marks=[M(W("p14", "real"), DC, "Washington", BLUE, "dot", 5), M(W("p14", "real") + 0.3, MOSCOW, "Moscow", AMBER, "dot", 5)], caption="What does a war look like when the warning is real?")

# ================================================================== Chapter 03 [SIMULATION]: the trigger
chapter("c3-card", 3, "The trigger")
G("c3-europe", W("p15", "This") - 0.15, [("s", 50.0, 14, 2500), ("e", 52.0, 18, 3000)],
  marks=[M(CUR + 0.2, [20.0, 52.0], "A crisis in Europe", YELLOW, "ring", 7)], highlight=[], caption="A crisis in Europe has already turned nuclear")
G("c3-path", W("p15", "and") - 0.1, [("s", 45.0, -30, 640), (2.0, 48.0, 0, 760), ("e", 50.0, 25, 900)],
  marks=[M(W("p15", "chosen") + 0.2, [20.0, 52.0], "One chosen path", WHITE, "ring", 6)], caption="One chosen path, not a forecast")
card("c3-hour", W("p15", "three") - 0.2, type="timeline", title="The first hour", sub="a selection, not the whole war", total=60, unit="MIN",
     segments=[{"from": 0, "to": 53, "label": "Our simulation: 53 minutes", "color": RED}], highlight={"from": 0, "to": 53, "label": "first strike to last impact"}, cursorTo=53, source="Scenario engine")
card("c3-375", S("p16"), type="bars", title="Warheads: our hour against the arsenals", sub="our simulation chooses 375; deployed counts are about", source="Scenario engine; FAS; Bulletin of the Atomic Scientists",
     bars=[{"label": "Our simulation", "value": 375, "display": "375", "color": RED}, {"label": "Russia deployed", "value": 1800, "display": "about 1,800", "color": AMBER}, {"label": "US deployed", "value": 1700, "display": "about 1,700", "color": BLUE}])
# p16 Ramstein
RATE_R = 33
G("c3-zero", W("p16", "leaves") - 0.4, [("s", 50.0, 10, 1900), ("e", 53.0, 16, 2400)],
  marks=[M(W("p16", "single") - 0.2, KALININGRAD, "Kaliningrad oblast", AMBER, "base", 6)], **clk(0.0, RATE_R, "MINUTE ZERO"))
G("c3-launch", W("p16", "aimed") - 0.3, [("s", 54.0, 21, 3800), (1.5, 53.5, 18, 2900), ("e", 52.5, 15, 2500)],
  marks=[M(W("p16", "launch") - 0.3, KALININGRAD, "Launch point (simulated)", AMBER, "base", 6)],
  arcs=[{"from": KALININGRAD, "to": RAMSTEIN, "t0": round(W("p16", "leaves") - CUR, 2), "t1": round(W("p17", "It") - CUR, 2), "color": AMBER, "loft": 0.1}], **clk(0.4, RATE_R))
R("c3-ram", W("p16", "Princeton's") - 0.2, [("s", [9.0, 50.0], 900), ("e", [8.0, 49.6], 520)],
  cities=[M(W("p16", "Ramstein") - 0.2, RAMSTEIN, "Ramstein Air Base", RED, "target", 11), M(CUR + 0.2, [8.68, 50.11], "Frankfurt", WHITE, "dot", 7), M(CUR + 0.5, [7.75, 48.58], "Strasbourg", WHITE, "dot", 7),
          M(CUR + 0.8, [9.18, 48.78], "Stuttgart", WHITE, "dot", 7), M(CUR + 1.1, [6.13, 49.61], "Luxembourg", WHITE, "dot", 7)],
  rings=[(CUR + 1.5, RAMSTEIN, 60, RED, "Ramstein area", True)],
  highlight=[{"iso": "276", "color": WHITE, "fill": "rgba(255,255,255,0.05)"}], **clk(3.5, RATE_R))
G("c3-plana", S("p17"), [("s", 48.0, 8, 2600), (2.5, 52.0, 6, 1900), ("e", 50.0, -4, 1300)],
  marks=[M(W("p16", "Plan"), [10.0, 52.0], "Princeton Plan A opens here", YELLOW, "ring", 6)], arcs=[{"from": KALININGRAD, "to": RAMSTEIN, "t0": -10.0, "t1": round(S("p17") - CUR + 0.3, 2), "color": AMBER, "loft": 0.1}], highlight=[], **clk(7.2, RATE_R))
# p17 lands minute 8.7
C("c3-flash", W("p17", "reaches") - 0.15, "ramstein", [("s", RAMSTEIN, 40), ("e", RAMSTEIN, 26)], RAMSTEIN,
  labels=[(S("p17") + 0.5, RAMSTEIN, "Ramstein Air Base", WHITE), (S("p17") + 1.6, [7.77, 49.44], "Kaiserslautern", DIM)], flashT=S("p17") + 0.2, **clk(8.7, 0, "IMPACT: MINUTE 8.7"))
C("c3-5psi", W("p17", "the", 2) - 0.15, "ramstein", [("s", RAMSTEIN, 14), ("e", RAMSTEIN, 8)], RAMSTEIN,
  rings=[(CUR + 0.3, FX_RAM["fireball_km"], "Fireball", WHITE, 330), (W("p17", "five") - 0.2, FX_RAM["psi5_km"], "5 psi", RED, 60)],
  labels=[(CUR + 1.0, RAMSTEIN, "Ramstein Air Base", WHITE)], **clk(8.7, 0, "IMPACT: MINUTE 8.7"))
G("c3-small", W("p18", "rest") - 0.2, [("s", 49.0, 8, 3000), (3.0, 50.0, 7, 2300), ("e", 51.0, 6, 1700)],
  marks=[M(W("p17", "engine's") - 0.4, RAMSTEIN, "10 kt airburst", RED, "target", 7), M(W("p18", "smallest") - 0.1, [14.0, 53.0], "The smallest strike of the hour", YELLOW, "ring", 6)], flashes=[{"at": RAMSTEIN, "t": 0.0, "radius": 30, "hold": 2.5}], highlight=[], **clk(8.7, 0, "IMPACT"))
card("c3-yields", S("p19"), type="bars", title="Yield of each strike group", sub="kilotons · every other strike is about nine times larger or more", source="Scenario engine",
     bars=[{"label": "Ramstein", "value": 10, "display": "10 kt", "color": WHITE}, {"label": "US submarine warheads", "value": 90, "display": "90 kt", "color": BLUE}, {"label": "Russian submarine warheads", "value": 100, "display": "100 kt", "color": AMBER},
           {"label": "Silo-field strikes", "value": 200, "display": "200 to 300 kt", "color": RED}, {"label": "Offutt, the largest", "value": 750, "display": "750 kt", "color": ORANGE}])
# p19 main wave
RATE19 = 18
G("c3-wave", W("p19", "radars") - 0.2, [("s", 55.0, 20, 700), ("e", 52.0, -20, 760)],
  marks=[M(T_RU + 0.1, [60.0, 56.0], "Main wave launched", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 6, ["rus-"]), **clk(5.0, RATE19, "MINUTE FIVE"))
G("c3-aimed", W("p19", "The", 2) - 0.2, [("s", 42.0, -95, 1250), (3.0, 40.0, -98, 1350), ("e", 40.0, -100, 1500)],
  marks=[M(W("p19", "radars"), CAPECOD, "Radars", RED, "target", 6), M(W("p19", "radars") + 0.3, BEALE, "Radars", RED, "target", 6), M(W("p19", "submarine"), BANGOR, "Submarine bases", RED, "target", 6),
         M(W("p19", "submarine") + 0.3, KINGSBAY, "Submarine bases", RED, "target", 6), M(W("p19", "command"), DC, "Command centres", RED, "target", 6), M(W("p19", "command") + 0.3, OFFUTT, "Command centres", RED, "target", 6),
         M(W("p19", "silo"), MINOT, "Silo fields", RED, "target", 6), M(W("p19", "silo") + 0.3, WARREN, "Silo fields", RED, "target", 6)],
  highlight=[HL_US], **clk(7.0, RATE19))
G("c3-sublands", S("p20"), [("s", 42.0, -128, 1700), (2.2, 41.0, -90, 1500), ("e", 40.0, -72, 1900)],
  marks=[M(W("p19", "shortest") - 0.2, ATL, "Submarine warheads: shortest flights", AMBER, "sub", 6)], arcs=arcs_for(CUR, CUR + 6, ["rus-slbm-bangor", "rus-slbm-beale", "rus-slbm-capecod", "rus-slbm-dc", "rus-slbm-kingsbay"]),
  highlight=[HL_US], **clk(11.0, RATE19))
# p20
G("c3-both", W("p20", "and", 2) - 0.1, [("s", 48.0, -50, 700), ("e", 45.0, -85, 900)],
  marks=[M(W("p20", "land") - 0.2, MOSCOW, "Land missiles", AMBER, "ring", 6), M(W("p20", "sea") - 0.2, ATL, "Sea missiles", AMBER, "sub", 6)], arcs=arcs_for(CUR, CUR + 6, ["rus-"]), **clk(12.0, RATE19))
G("c3-radars", W("p20", "In") - 0.2, [("s", 41.0, -105, 2000), (2.0, 41.0, -98, 1750), ("e", 40.5, -85, 2200)],
  marks=[M(W("p20", "radars") - 0.2, BEALE, "West coast radar", RED, "target", 6), M(W("p20", "coasts") - 0.1, CAPECOD, "East coast radar", RED, "target", 6)], highlight=[HL_US], **clk(13.0, RATE19))
G("c3-decide", W("p20", "What") - 0.1, [("s", 40.0, -90, 1700), ("e", 39.0, -77, 3000)],
  marks=[M(W("p20", "Washington") - 0.2, DC, "Washington: the decision", BLUE, "target", 7)], highlight=[HL_US], clock="T-09:00", clockLabel="DECISION WINDOW", clockRate=100)
G("c3-what", S("p21"), [("s", 39.0, -77, 3000), ("e", 44.0, -85, 1100)],
  marks=[M(W("p20", "do"), DC, "What does it do?", BLUE, "ring", 7)], highlight=[HL_US], caption="What does it do?", clock="T-00:00", clockLabel="DECISION WINDOW", clockRate=0)

# ================================================================== Chapter 04 [SIMULATION]: the first hour
chapter("c4-card", 4, "The first hour, minute by minute")
G("c4-m14a", T_USI - 0.0, [("s", 50.0, -10, 650), ("e", 48.0, -45, 760)],
  marks=[M(CUR + 0.2, [60.0, 56.0], "Russia's main wave, in flight", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 6, ["rus-"]), **clk(14.0, 8, "MINUTE FOURTEEN"))
G("c4-m14b", W("p21", "inside") - 0.2, [("s", 46.0, -100, 1100), ("e", 52.0, -60, 800)],
  marks=[M(W("p21", "Minuteman") - 0.2, MINOT, "Minot", BLUE, "base", 5), M(W("p21", "Minuteman") + 0.1, MALMSTROM, "Malmstrom", BLUE, "base", 5), M(W("p21", "Minuteman") + 0.4, WARREN, "F.E. Warren", BLUE, "base", 5),
         M(W("p21", "warning") - 0.2, [-78.0, 50.0], "Fired on warning", BLUE, "ring", 6)],
  arcs=arcs_for(CUR, CUR + 5, ["us-icbm"]), **clk(14.0, 8, "THE US FIRES"))
card("c4-blair", W("p21", "This") - 0.1, type="timeline", title="Blair's ten minutes", sub="the US fires at minute 9 after the Russian launch", total=10, unit="MIN",
     segments=[{"from": 0, "to": 9, "label": "Russian wave in flight", "color": AMBER}, {"from": 9, "to": 10, "label": "US fires", "color": BLUE}], highlight={"from": 9, "to": 10, "label": "inside the window"}, cursorTo=9, source="Bruce Blair, Bulletin of the Atomic Scientists; scenario engine")
G("c4-choice", W("p21", "The", 2) - 0.2, [("s", 48.0, -80, 760), ("e", 52.0, -20, 700)],
  marks=[M(W("p21", "simulation") + 0.4, [-60.0, 52.0], "A simulation choice", YELLOW, "ring", 6)], arcs=arcs_for(CUR, CUR + 6, ["us-icbm", "rus-icbm"]), caption="A simulation choice, not a prediction", **clk(14.5, 8, "SIMULATION CHOICE"))
G("c4-flight-a", W("p21", "nine", 2) - 0.2, [("s", 62.0, 60, 760), ("e", 66.0, 30, 720)],
  marks=[M(CUR + 0.3, [60.0, 56.0], "Russian land missiles: 9 minutes in", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 8, ["rus-icbm"]), highlight=HL_BOTH, **clk(14.0, 8, "RUSSIAN LAND MISSILES"))
G("c4-flight-b", S("p22"), [("s", 66.0, 30, 720), ("e", 70.0, -20, 860)],
  marks=[M(W("p21", "sixteen") - 0.2, [10.0, 70.0], "Another 16 to 22 minutes", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 8, ["rus-icbm"]), highlight=HL_BOTH, **clk(14.6, 8, "RUSSIAN LAND MISSILES"))
# p22: Cape Cod, Bangor, Beale
RT22 = 4
G("c4-m15a", W("p22", "Warheads") + 1.0, [("s", 40.0, -90, 1500), ("e", 41.5, -80, 1900)],
  marks=[M(S("p22") + 0.3, ATL, "Warheads inbound", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 8, ["rus-slbm-capecod", "rus-slbm-dc"]), highlight=[HL_US], **clk(15.0, 6, "MINUTES FIFTEEN AND SIXTEEN"))
G("c4-m15", FLASH["rus-slbm-capecod"] - 0.1, [("s", 41.5, -80, 1900), ("e", 41.8, -72, 2800)],
  marks=[M(W("p22", "early-warning") - 0.2, CAPECOD, "Cape Cod radar", RED, "target", 6)], arcs=arcs_for(CUR, CUR + 8, ["rus-slbm-capecod"]), highlight=[HL_US], caption="About 100 kt each", **clk(15.6, 6, "MINUTES FIFTEEN AND SIXTEEN"))
G("c4-capecod", FLASH["rus-slbm-bangor"] - 0.1, [("s", 41.9, -72, 3800), ("e", 42.0, -70.3, 5500)],
  marks=[M(CUR + 0.1, CAPECOD, "Cape Cod radar", RED, "target", 6), M(CUR + 1.2, [-71.06, 42.36], "Boston", WHITE, "dot")], flashes=[{"at": CAPECOD, "t": 0.1, "radius": 70, "hold": 3}], highlight=[HL_US], **clk(15.7, 6, "CAPE COD"))
G("c4-bangor", FLASH["rus-slbm-beale"] - 0.1, [("s", 47.0, -127, 4000), ("e", 47.6, -122.8, 6000)],
  marks=[M(CUR + 0.1, BANGOR, "Bangor submarine base", RED, "target", 6), M(CUR + 1.1, SEATTLE, "Seattle", WHITE, "dot")], flashes=[{"at": BANGOR, "t": 0.1, "radius": 80, "hold": 3}], highlight=[HL_US], **clk(15.8, 6, "BANGOR"))
G("c4-beale", S("p23"), [("s", 39.5, -126, 3600), ("e", 39.1, -121.4, 5200)],
  marks=[M(CUR + 0.1, BEALE, "Beale radar", RED, "target", 6), M(CUR + 0.9, [-121.49, 38.58], "Sacramento", WHITE, "dot")], flashes=[{"at": BEALE, "t": 0.1, "radius": 80, "hold": 3}], highlight=[HL_US], **clk(16.4, 6, "BEALE"))
# p23: US submarines
G("c4-m16a", W("p23", "Their") - 0.2, [("s", 70.0, -40, 1100), (2.0, 68.0, -10, 1400), ("e", 66.0, 20, 1700)],
  marks=[M(W("p23", "submarines") - 0.1, NORSEA, "US submarine (location simulated)", BLUE, "sub", 5), M(W("p23", "bases") - 0.1, SEVERO, "Russian bases", AMBER, "base", 5), M(W("p23", "command") - 0.1, MOSCOW, "Command centres", AMBER, "base", 5)],
  arcs=arcs_for(CUR, CUR + 8, ["us-slbm-sever", "us-slbm-plesetsk", "us-slbm-moscow"]), highlight=[HL_RU], **clk(16.0, 6, "AMERICAN SUBMARINES FIRE"))
G("c4-m16b", S("p24"), [("s", 62.0, 60, 760), ("e", 60.0, 100, 900)],
  marks=[M(W("p23", "roughly") - 0.2, KAMCH, "US submarine (location simulated)", BLUE, "sub", 5), M(W("p23", "and", 2) - 0.2, VILYU, "Pacific Fleet base", AMBER, "base", 5)],
  arcs=arcs_for(CUR, CUR + 8, ["us-slbm"]), caption="About 100 kt each · 9 to 12 minutes in flight", highlight=[HL_RU], **clk(16.5, 6, "AMERICAN SUBMARINES FIRE"))
# p24: Washington, Kings Bay
G("c4-m17a", W("p24", "Washington") - 0.4, [("s", 36.0, -60, 1500), ("e", 38.0, -72, 2300)],
  marks=[M(S("p24") + 0.4, ATL, "Warheads inbound", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 4, ["rus-slbm-dc"]), highlight=[HL_US], **clk(17.0, 5, "MINUTE SEVENTEEN"))
R("c4-dc", W("p24", "The", 2) - 0.1, [("s", [-77.0, 38.9], 420), (2.0, [-77.0, 39.0], 300), ("e", [-76.9, 39.0], 210)], burst=(DC, FLASH["rus-slbm-dc"] + 0.1, 12, 6),
  cities=[M(W("p24", "Washington") + 0.8, DC, "Washington, DC", RED, "target", 7), M(W("p24", "Pentagon") - 0.4, [-77.06, 38.87], "The Pentagon: 6 warheads", WHITE, "ring", 6), M(CUR + 1.5, [-76.61, 39.29], "Baltimore", WHITE, "dot")],
  highlight=[HL_US], **clk(17.2, 5, "WASHINGTON"))
G("c4-kb", W("p24", "follows") - 0.2, [("s", 33.0, -90, 3500), (2.0, 31.5, -84, 4500), ("e", 31.0, -81.5, 5500)],
  marks=[M(W("p24", "Kings") - 0.2, KINGSBAY, "Kings Bay, Georgia", RED, "target", 6), M(W("p24", "home") + 0.1, [-81.2, 31.5], "6 Ohio-class submarines", BLUE, "sub", 5)], highlight=[HL_US], **clk(18.0, 5, "KINGS BAY"))
G("c4-kb-hit", S("p25"), [("s", 31.0, -81.5, 5500), ("e", 32.0, -79.0, 3800)],
  marks=[M(CUR + 0.1, KINGSBAY, "Kings Bay, minute 19", RED, "target", 6), M(CUR + 0.9, [-81.09, 32.08], "Savannah", WHITE, "dot")], flashes=[{"at": KINGSBAY, "t": 0.1, "radius": 80, "hold": 3}], highlight=[HL_US], **clk(19.0, 5, "MINUTE NINETEEN"))
# p25: Russian bases
G("c4-m25", W("p25", "Northern") - 0.2, [("s", 62.0, 0, 760), ("e", 66.0, 30, 1100)],
  marks=[M(S("p25") + 0.3, NORSEA, "US submarines", BLUE, "sub", 5)], arcs=arcs_for(CUR, CUR + 4, ["us-slbm"]), highlight=[HL_RU], **clk(25.0, 3, "MINUTES TWENTY-FIVE TO TWENTY-EIGHT"))
G("c4-sever", W("p25", "Pacific") - 0.15, [("s", 67.0, 25, 2600), ("e", 69.2, 33.3, 4300)],
  marks=[M(W("p25", "Northern"), SEVERO, "Northern Fleet base, Murmansk", RED, "target", 6)], flashes=[{"at": SEVERO, "t": rel(CUR, FLASH["us-slbm-severomorsk"]) + 0.05, "radius": 70, "hold": 3}],
  arcs=arcs_for(CUR, CUR + 4, ["us-slbm-sever"]), highlight=[HL_RU], **clk(25.0, 3))
G("c4-vilyu", W("p25", "Plesetsk") - 0.2, [("s", 56.0, 150, 2800), ("e", 53.0, 158.4, 4500)],
  marks=[M(W("p25", "Pacific"), VILYU, "Pacific Fleet base, Vilyuchinsk", RED, "target", 6)], flashes=[{"at": VILYU, "t": rel(CUR, FLASH["us-slbm-vilyuchinsk"]) + 0.05, "radius": 70, "hold": 3}],
  arcs=arcs_for(CUR, CUR + 4, ["us-slbm-vilyu"]), highlight=[HL_RU], **clk(25.7, 3))
G("c4-plesetsk", S("p26"), [("s", 60.0, 36, 2100), (1.5, 58.5, 38, 2900), ("e", 57.0, 38, 3600)],
  marks=[M(W("p25", "Plesetsk"), PLESETSK, "Plesetsk", RED, "target", 6), M(W("p25", "Moscow's"), MOSCOW, "Moscow command centres", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 5, ["us-slbm-plesetsk", "us-slbm-moscow"], 60), arcs=arcs_for(CUR, CUR + 4, ["us-slbm-plesetsk", "us-slbm-moscow"]), highlight=[HL_RU], **clk(26.4, 3))
# p26: the silo fields (49.8 s)
G("c4-m29", W("p26", "The") - 0.1, [("s", 55.0, 30, 700), ("e", 56.0, -30, 760)],
  marks=[M(W("p26", "Minutes") + 0.6, [60.0, 56.0], "Russian land missiles", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 5, ["rus-icbm"]), **clk(29.0, 5, "MINUTES TWENTY-NINE TO THIRTY-SIX"))
G("c4-30min", W("p26", "Minuteman") - 0.2, [("s", 58.0, -20, 820), (2.2, 52.0, -50, 900), ("e", 48.0, -80, 1100)],
  marks=[M(W("p26", "after") - 0.1, [-60.0, 56.0], "About 30 minutes in flight", AMBER, "ring", 6)], arcs=arcs_for(CUR, CUR + 6, ["rus-icbm"]), **clk(29.5, 5))
def silo_dots(c, t, empty=False):
    """Schematic silo cluster: a 5 x 4 grid of small silo glyphs around the field (not surveyed positions)."""
    out = []
    for i in range(5):
        for j in range(4):
            at = [c[0] + (i - 2) * 0.32, c[1] + (j - 1.5) * 0.24]
            filled = empty and (i, j) in ((1, 1), (3, 2))
            out.append(M(t, at, None, BLUE if (filled or not empty) else "#9AA7B4", "dot" if (filled or not empty) else "ring", 4))
    return out


R("c4-fields", W("p26", "silo") - 0.2, [("s", [-105.3, 44.8], 2900), (2.8, [-105.3, 44.8], 2700), ("e", [-105.3, 44.8], 2500)],
  cities=[M(CUR + 0.2, MINOT, "Minot", BLUE, "base", 11), M(CUR + 0.5, MALMSTROM, "Malmstrom", BLUE, "base", 11), M(CUR + 0.8, WARREN, "F.E. Warren", BLUE, "base", 11)]
         + silo_dots(MINOT, CUR + 0.3) + silo_dots(MALMSTROM, CUR + 0.6) + silo_dots(WARREN, CUR + 0.9),
  labels=[(W("p26", "tries") - 0.2, [-105.0, 41.0], "The force a first strike tries to catch", YELLOW)], highlight=[], **clk(30.0, 5))
R("c4-60", W("p26", "roughly") - 0.2, [("s", [-105.3, 44.8], 2600), (2.5, [-105.3, 44.8], 2450), ("e", [-105.3, 44.8], 2300)],
  cities=[M(CUR + 0.1, MINOT, None, BLUE, "base", 11), M(CUR + 0.1, MALMSTROM, None, BLUE, "base", 11), M(CUR + 0.1, WARREN, None, BLUE, "base", 11),
          M(W("p26", "sixty") - 0.1, MINOT, "Minot: 60 warheads", RED, "target", 11), M(W("p26", "sixty") + 0.6, MALMSTROM, "Malmstrom: 60 warheads", RED, "target", 11), M(W("p26", "sixty") + 1.3, WARREN, "Warren: 60 warheads", RED, "target", 11)]
         + silo_dots(MINOT, CUR + 0.1) + silo_dots(MALMSTROM, CUR + 0.1) + silo_dots(WARREN, CUR + 0.1),
  caption="The silo fields come early", highlight=[], **clk(30.5, 5))
G("c4-hit1", FLASH["rus-icbm-cheyenne"] - 0.15, [("s", 45.0, -108, 2700), (3.0, 45.0, -105, 2300), ("e", 44.5, -102, 2000)],
  marks=[M(W("p26", "roughly") - 0.0, [-100.0, 52.0], "100 to 300 kt each", ORANGE, "ring", 6), M(W("p26", "Minot"), MINOT, "Minot", RED, "target", 6), M(W("p26", "Malmstrom"), MALMSTROM, "Malmstrom", RED, "target", 6), M(W("p26", "Warren"), WARREN, "Warren", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 8, ["rus-icbm-minot", "rus-icbm-malmstrom", "rus-icbm-warren"], 70), arcs=arcs_for(CUR, CUR + 4, ["rus-icbm-minot", "rus-icbm-malmstrom", "rus-icbm-warren"]), highlight=[HL_US], **clk(29.6, 5, "SILO FIELDS"))
G("c4-hit2", W("p26", "strike", 2) - 0.15, [("s", 42.0, -104, 2300), ("e", 39.0, -96, 2900)],
  marks=[M(W("p26", "Cheyenne"), CHEYENNE, "Cheyenne Mountain", RED, "target", 6), M(W("p26", "Offutt"), OFFUTT, "Offutt AFB", RED, "target", 6), M(W("p26", "bomber"), WHITEMAN, "Whiteman", RED, "target", 6), M(W("p26", "bomber") + 0.3, BARKSDALE, "Barksdale", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 8, ["rus-icbm-cheyenne", "rus-icbm-offutt", "rus-icbm-whiteman", "rus-icbm-barksdale"], 70), arcs=arcs_for(CUR, CUR + 4, ["rus-icbm-cheyenne", "rus-icbm-offutt", "rus-icbm-whiteman", "rus-icbm-barksdale"]), highlight=[HL_US], **clk(33.7, 5, "COMMAND AND BOMBERS"))
C("c4-offutt", W("p26", "By") - 0.2, "omaha", [("s", [-95.9, 41.12], 60), (2.5, [-95.9, 41.12], 40), ("e", [-95.9, 41.12], 26)], OFFUTT,
  rings=[(W("p26", "up") - 0.0, FX_OFFUTT["psi5_km"], "5 psi", RED, 40), (W("p26", "kilotons", 2) - 0.8, FX_OFFUTT["fireball_km"], "Fireball", WHITE, 200)],
  labels=[(CUR + 0.3, OFFUTT, "Offutt AFB: up to 750 kt", WHITE)], flashT=W("p26", "Offutt", 2) + 0.3, **clk(33.7, 3, "OFFUTT AFB"))
G("c4-inair", W("p26", "warheads", 3) - 0.1, [("s", 55.0, -90, 700), (2.0, 58.0, -30, 760), ("e", 56.0, 20, 900)],
  marks=[M(W("p26", "air") - 0.8, [-80.0, 52.0], "US missiles already in the air", BLUE, "ring", 6)], arcs=arcs_for(CUR, CUR + 6, ["us-icbm"]), caption="By now the American land missiles are in the air", **clk(36.0, 5, "MINUTE THIRTY-SIX"))
R("c4-empty", W("p26", "they", 2) - 0.1, [("s", [-101.4, 47.8], 600), ("e", [-101.4, 47.9], 440)],
  cities=[M(CUR + 0.1, MINOT, "Minot Minuteman field", RED, "target", 11), M(W("p26", "mostly") - 0.2, [-100.3, 48.9], "Silos mostly empty", YELLOW, "dot", 7)]
         + silo_dots(MINOT, CUR + 0.1, empty=True), highlight=[], **clk(36.0, 5, "SILO FIELD"))
R("c4-stilland", S("p27"), [("s", [-101.4, 48.4], 380), ("e", [-101.4, 48.4], 260)], burst=(MINOT, CUR + 0.1, 8, 5),
  labels=[(0, [-100.6, 49.1], "Minot: they still land", WHITE)], highlight=[], **clk(36.0, 5, "MINOT"))
# p27: Russian missile divisions
G("c4-m39", W("p27", "Kozelsk") - 0.3, [("s", 52.0, 20, 1300), ("e", 55.0, 40, 1800)],
  marks=[M(W("p27", "The") + 0.3, [-60.0, 52.0], "American missiles inbound", BLUE, "ring", 6), M(W("p27", "missile") + 0.2, MOSCOW, "Moscow", WHITE, "dot", 5)],
  arcs=arcs_for(CUR, CUR + 6, ["us-icbm"]), highlight=[HL_RU], **clk(39.0, 4, "MINUTES THIRTY-NINE TO FORTY-THREE"))
G("c4-west", W("p27", "Novosibirsk") - 0.25, [("s", 56.0, 36, 2900), ("e", 54.0, 44, 3100)],
  marks=[M(W("p27", "Kozelsk"), KOZELSK, "Kozelsk", RED, "target", 6), M(W("p27", "Teykovo"), TEYKOVO, "Teykovo", RED, "target", 6), M(W("p27", "Tatishchevo"), TATISH, "Tatishchevo", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 6, ["us-icbm-kozelsk", "us-icbm-teykovo", "us-icbm-tatishchevo"], 60), arcs=arcs_for(CUR, CUR + 4, ["us-icbm-kozelsk", "us-icbm-teykovo", "us-icbm-tatishchevo"]), highlight=[HL_RU], **clk(40.5, 4, "WESTERN RUSSIA"))
G("c4-east", W("p27", "Dombarovsky") - 0.25, [("s", 56.0, 72, 2500), ("e", 55.0, 88, 3300)],
  marks=[M(W("p27", "Novosibirsk"), NOVOS, "Novosibirsk", RED, "target", 6), M(W("p27", "Uzhur"), UZHUR, "Uzhur", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 4, ["us-icbm-novosibirsk", "us-icbm-uzhur"], 60), arcs=arcs_for(CUR, CUR + 4, ["us-icbm-novosibirsk", "us-icbm-uzhur"]), highlight=[HL_RU], **clk(40.2, 4, "SIBERIA"))
G("c4-ural", S("p28"), [("s", 52.0, 62, 3600), ("e", 51.1, 59.8, 5200)],
  marks=[M(W("p27", "Dombarovsky"), DOMB, "Dombarovsky", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 3, ["us-icbm-dombarovsky"], 70), arcs=arcs_for(CUR, CUR + 3, ["us-icbm-dombarovsky"]), highlight=[HL_RU], **clk(43.1, 4, "THE URALS"))
# p28: the last submarines, the cities
G("c4-m40", W("p28", "cities") - 0.2, [("s", 45.0, -40, 700), ("e", 48.0, 0, 760)],
  marks=[M(W("p28", "submarines") - 0.2, ATL, "Last submarines", AMBER, "sub", 5), M(W("p28", "submarines") + 0.1, NORSEA, "Last submarines", BLUE, "sub", 5), M(W("p28", "submarines") + 0.4, PAC, "Last submarines", AMBER, "sub", 5)],
  arcs=arcs_for(CUR, CUR + 5, ["rus-slbm-nyc", "rus-slbm-la", "us-slbm-stpete", "us-slbm-moscow2"]), **clk(40.0, 5, "MINUTE FORTY"))
G("c4-planA", W("p28", "New") - 0.2, [("s", 50.0, -20, 700), (1.8, 52.0, -5, 780), ("e", 54.0, 10, 880)],
  marks=[M(W("p28", "final") - 0.1, [-10.0, 58.0], "Plan A, last phase: cities", YELLOW, "ring", 6)], arcs=arcs_for(CUR, CUR + 5, ["rus-slbm-nyc", "rus-slbm-la", "us-slbm-stpete", "us-slbm-moscow2"]), **clk(43.0, 5))
G("c4-cities", W("p28", "eight") - 0.2, [("s", 54.0, -40, 640), (2.0, 50.0, -5, 700), ("e", 53.0, 28, 760)],
  marks=[M(W("p28", "York"), NYC, "New York", RED, "target", 6), M(W("p28", "Angeles"), LA, "Los Angeles", RED, "target", 6), M(W("p28", "Petersburg"), STPETE, "Saint Petersburg", RED, "target", 6), M(W("p28", "Moscow"), MOSCOW, "Moscow", RED, "target", 6)],
  flashes=flashes_for(CUR, CUR + 6, ["rus-slbm-nyc", "rus-slbm-la", "us-slbm-stpete", "us-slbm-moscow2"], 34), arcs=arcs_for(CUR, CUR + 5, ["rus-slbm-nyc", "rus-slbm-la", "us-slbm-stpete", "us-slbm-moscow2"]), **clk(50.1, 6, "THE CITIES"))
G("c4-eight", W("p28", "last", 2) - 0.15, [("s", 42.0, -95, 1100), ("e", 52.0, -10, 800)],
  marks=[M(W("p28", "eight") + 0.2, NYC, "8 warheads", RED, "target", 6), M(W("p28", "eight") + 0.6, LA, "8 warheads", RED, "target", 6), M(W("p28", "each") + 0.5, [10.0, 62.0], "8 each: a count we chose", YELLOW, "ring", 6)],
  caption="Eight warheads each: a count we chose", **clk(52.0, 5))
G("c4-last", S("p29"), [("s", 36.0, -128, 2000), ("e", 36.0, -116, 3200)],
  marks=[M(W("p28", "last") + 0.2, LA, "Last impact: Los Angeles", RED, "target", 6)], flashes=[{"at": LA, "t": 0.3, "radius": 60, "hold": 3}], highlight=[HL_US], **clk(52.4, 3, "MINUTE FIFTY-THREE"))
# p29 the totals
allmk = [M(W("p29", "twenty-seven") + i * 0.07, [s["target_lon"], s["target_lat"]], None, RED, "target", 5) for i, s in enumerate(sorted(ST.values(), key=lambda s: s["impact_min"]))]
G("c4-27", W("p29", "three") - 0.3, [("s", 52.0, -25, 640), ("e", 52.0, 20, 740)], marks=allmk, caption="27 strikes", **clk(53.0, 0, "THE WHOLE HOUR"))
card("c4-375", W("p29", "about") - 0.3, type="number", value="375 WARHEADS", countTo=375, suffix=" WARHEADS", label="in the simulation's 27 strikes", sub="a selection of the first hour", color=RED, source="Scenario engine")
flall = [{"at": [s["target_lon"], s["target_lat"]], "t": round(0.15 + s["impact_min"] / 52.6 * 3.6, 2), "radius": 30} for s in ST.values() if s["id"] != "isk-ramstein"]
G("c4-79", W("p29", "That") - 0.4, [("s", 54.0, -50, 640), ("e", 52.0, 10, 740)], flashes=flall, caption="About 79 megatons in 53 minutes", **clk(0.0, 800, "THE WHOLE HOUR"))
G("c4-hour", S("p30"), [("s", 50.0, -10, 700), ("e", 46.0, -60, 640)], marks=allmk[:1], caption="That is the whole of our hour.", **clk(53.0, 0, "MINUTE FIFTY-THREE"))
G("c4-zoom", S("p31"), [("s", 40.0, -100, 800), (1.8, 44.0, -115, 1800), ("e", 47.7, -122.7, 4600)],
  marks=[M(W("p30", "warheads") + 0.2, BANGOR, "One warhead", RED, "target", 6)], highlight=[HL_US], caption="What does one warhead do on the ground?", **clk(15.8, 0, "MINUTE FIFTEEN POINT EIGHT"))

# ================================================================== Chapter 05 [SIMULATION]: one warhead, ring by ring
chapter("c5-card", 5, "One warhead, ring by ring")
CL5 = clk(15.8, 0, "BANGOR · MINUTE 15.8")
SRC5 = "Scenario engine; OpenStreetMap"


def c5(sid, b, keys, rings, labels, **kw):
    C(sid, b, "bangor", keys, BANGOR, rings=rings, labels=labels, source=SRC5, **CL5, **kw)


c5("c5-base", W("p31", "eight", 2) - 0.2, [("s", [-122.72, 47.72], 56), (2.0, [-122.7, 47.72], 44), ("e", [-122.7, 47.72], 36)], [],
   [(W("p31", "Naval") - 0.0, BANGOR, "Naval Base Kitsap, Bangor", WHITE), (W("p31", "Puget") - 0.1, [-122.55, 47.83], "Puget Sound", DIM), (W("p31", "Puget") + 1.0, [-122.62, 47.6], "Hood Canal", DIM)])
c5("c5-boats", W("p31", "Our") - 0.2, [("s", [-122.72, 47.72], 30), ("e", [-122.72, 47.72], 20)], [],
   [(W("p31", "eight", 2) + 0.2, [-122.74, 47.74], "8 Ohio-class submarines", BLUE), (W("p31", "based") - 0.1, [-122.70, 47.70], "Their base", WHITE)])
c5("c5-four", W("p31", "We") - 0.2, [("s", [-122.72, 47.72], 18), ("e", [-122.72, 47.72], 14)], [],
   [(W("p31", "four") - 0.2, [-122.74, 47.735], "4 warheads (our choice)", RED), (W("p31", "puts") + 0.2, [-122.70, 47.705], "Aimed at the submarine base", DIM)])
c5("c5-one", S("p32"), [("s", [-122.72, 47.72], 14), ("e", [-122.72, 47.72], 8)], [],
   [(W("p31", "one") - 0.2, [-122.74, 47.73], "We look at one", WHITE), (W("p31", "hundred") - 0.1, [-122.70, 47.71], "100 kt", ORANGE), (W("p31", "ground") - 0.4, [-122.745, 47.705], "Ground burst", RED)], flashT=W("p31", "burst") + 0.1)
c5("c5-fire", W("p32", "Inside") - 0.2, [("s", [-122.72, 47.72], 3.2), ("e", [-122.72, 47.72], 2.4)], [(S("p32") + 0.2, FX_BANGOR["fireball_km"], "Fireball", WHITE, 315)],
   [(S("p32") + 0.8, [-122.72, 47.7235], "Ground zero", WHITE)])
c5("c5-20", S("p33"), [("s", [-122.72, 47.72], 3.0), (2.5, [-122.72, 47.72], 4.0), ("e", [-122.72, 47.72], 5.2)],
   [(S("p32") + 0.2, FX_BANGOR["fireball_km"], "Fireball", WHITE, 315), (W("p32", "Inside") + 0.1, FX_BANGOR["psi20_km"], "20 psi", ORANGE, 165)], [])
c5("c5-5", W("p33", "Heat") - 0.1, [("s", [-122.72, 47.72], 7.5), ("e", [-122.72, 47.72], 10.5)],
   [(S("p32") + 0.2, FX_BANGOR["fireball_km"], "Fireball", WHITE, 315), (S("p32") + 0.3, FX_BANGOR["psi20_km"], "20 psi", ORANGE, 165), (W("p33", "two") + 0.0, FX_BANGOR["psi5_km"], "5 psi", RED, 80)], [])
c5("c5-burn", S("p34"), [("s", [-122.72, 47.72], 10.5), (2.4, [-122.72, 47.72], 13), ("e", [-122.72, 47.72], 16)],
   [(0, FX_BANGOR["fireball_km"], "Fireball", WHITE, 315), (0, FX_BANGOR["psi20_km"], "20 psi", ORANGE, 165), (0, FX_BANGOR["psi5_km"], "5 psi", RED, 80), (W("p33", "third-degree") + 0.1, FX_BANGOR["thermal3_km"], "Third-degree burns", AMBER, 255)], [])
RINGS_ALL = [(0, FX_BANGOR["fireball_km"], "Fireball", WHITE, 315), (0, FX_BANGOR["psi20_km"], "20 psi", ORANGE, 165), (0, FX_BANGOR["psi5_km"], "5 psi", RED, 80), (0, FX_BANGOR["thermal3_km"], "Burns", AMBER, 270)]
c5("c5-1psi", W("p34", "These") - 0.1, [("s", [-122.72, 47.72], 16), ("e", [-122.72, 47.72], 26)], RINGS_ALL + [(W("p34", "six") - 0.1, FX_BANGOR["psi1_km"], "1 psi", TEAL, 215)], [])
c5("c5-notoll", S("p35"), [("s", [-122.72, 47.72], 26), ("e", [-122.72, 47.72], 34)], RINGS_ALL + [(0, FX_BANGOR["psi1_km"], "1 psi", TEAL, 215)],
   [(W("p34", "give") - 0.2, [-122.55, 47.77], "No death toll given", YELLOW)])
c5("c5-area", W("p35", "Four") - 0.2, [("s", [-122.72, 47.72], 13), ("e", [-122.72, 47.72], 19)], RINGS_ALL,
   [(W("p35", "twenty") - 0.2, [-122.76, 47.745], "About 20 sq km inside 5 psi", RED)])
c5("c5-overlap", W("p35", "Four", 2) - 0.2, [("s", [-122.72, 47.72], 19), ("e", [-122.72, 47.72], 13)], RINGS_ALL,
   [(W("p35", "Four") - 0.0, [-122.70, 47.755], "4 warheads would overlap", WHITE), (W("p35", "show") - 0.2, [-122.76, 47.70], "We show one", WHITE)])
c5("c5-choice", S("p36"), [("s", [-122.72, 47.72], 13), (2.5, [-122.72, 47.72], 17), ("e", [-122.72, 47.72], 21)], RINGS_ALL,
   [(W("p35", "is") + 0.8, [-122.69, 47.745], "4 on one base: our choice", YELLOW), (W("p35", "counterforce") - 0.1, [-122.78, 47.695], "Counterforce: make sure of the target", RED)])
# p36 fallout
c5("c5-ground", W("p36", "In") - 0.2, [("s", [-122.72, 47.72], 24), ("e", [-122.65, 47.72], 38)], RINGS_ALL,
   [(W("p36", "ground") - 0.1, [-122.80, 47.78], "Ground burst", RED), (W("p36", "fallout") - 0.1, [-122.60, 47.69], "Heavy local fallout", AMBER)])
R("c5-wind", W("p36", "Seattle") - 0.1, [("s", [-122.4, 47.7], 160), (2.4, [-122.3, 47.7], 190), ("e", [-122.2, 47.7], 210)],
  cities=[M(CUR + 0.2, BANGOR, "Bangor", RED, "target", 6), M(W("p36", "across") - 0.1, [-122.5, 47.8], "Puget Sound", WHITE, "dot", 5)],
  labels=[(W("p36", "wind") - 0.1, [-123.3, 48.15], "Wind from the west (our choice)", YELLOW)],
  plume={"at": BANGOR, "bearing": 90, "lengthKm": 55, "widthKm": 14, "t0": rel(CUR, W("p36", "plume") - 0.1), "t1": rel(CUR, W("p36", "plume") + 2.4), "color": AMBER, "label": "Fallout: direction only"},
  highlight=[HL_US], source=SRC5, **CL5)
R("c5-seattle", S("p37"), [("s", [-122.3, 47.7], 190), ("e", [-122.2, 47.65], 150)],
  cities=[M(W("p36", "Seattle") - 0.1, SEATTLE, "Seattle: not a target", WHITE, "dot", 7), M(CUR + 0.3, BANGOR, "Bangor", RED, "target", 6), M(CUR + 1.0, [-122.62, 47.57], "Bremerton", WHITE, "dot", 5)],
  labels=[(W("p36", "thirty") - 0.1, [-122.52, 47.74], "About 30 km", YELLOW)], highlight=[HL_US], source=SRC5, **CL5)
# p37 submarines
G("c5-sea", W("p37", "and", 2) - 0.1, [("s", 40.0, -140, 1500), ("e", 36.0, -90, 1000)],
  marks=[M(W("p37", "nine") - 0.1, ATL, "About 950 warheads at sea", BLUE, "sub", 6), M(W("p37", "nine") + 0.4, [-145.0, 40.0], "On submarines", BLUE, "sub", 6)], highlight=[HL_US], clock="2025", clockLabel="BY ONE COUNT", clockRate=0, source="Bulletin of the Atomic Scientists, 2025")
G("c5-bases", W("p37", "Taking") - 0.2, [("s", 40.0, -125, 1300), ("e", 39.0, -90, 1500)],
  marks=[M(W("p37", "Bangor"), BANGOR, "Bangor: 8 boats", BLUE, "base", 6), M(W("p37", "two") + 0.0, KINGSBAY, "Kings Bay: 6 boats", BLUE, "base", 6)], highlight=[HL_US], clock="2025", clockLabel="THE TWO BASES", clockRate=0, source="Bulletin of the Atomic Scientists, 2025")
G("c5-logic", S("p38"), [("s", 47.0, -128, 2700), ("e", 47.7, -122.7, 5000)],
  marks=[M(W("p37", "hitting") - 0.2, BANGOR, "Hit the boats before they leave", RED, "target", 7)], flashes=[{"at": BANGOR, "t": rel(CUR, W("p37", "hitting")) + 0.3, "radius": 70, "hold": 3}], highlight=[HL_US], **clk(15.8, 0, "BANGOR"))

# ================================================================== Chapter 06 [SIMULATION]: the day after
chapter("c6-card", 6, "The day after")
allmk2 = [M(CUR + 0.2 + i * 0.05, [s["target_lon"], s["target_lat"]], None, RED, "target", 5) for i, s in enumerate(ST.values())]
G("c6-53", W("p38", "If") - 0.2, [("s", 50.0, -30, 640), ("e", 52.0, 10, 760)], marks=allmk2, flashes=[], clock="T+52:36", clockLabel="THE CLOCK STOPS", clockRate=0)
G("c6-map", S("p39"), [("s", 52.0, 10, 760), ("e", 45.0, -80, 900)], marks=allmk2[:], caption="If the war did not stop here, the map keeps changing.", clock="T+52:36", clockLabel="THE CLOCK STOPS", clockRate=0)
# p39 fallout
G("c6-fall1", W("p39", "silo") + 0.0, [("s", 44.0, -104, 1400), ("e", 45.0, -102, 2200)],
  marks=[M(S("p39") + 0.4, [-100.0, 55.0], "First: fallout", YELLOW, "ring", 6)], highlight=[HL_US], clock="DAY 1", clockLabel="FALLOUT", clockRate=0)
R("c6-fall2", W("p39", "our") - 0.3, [("s", [-103.5, 44.5], 2300), ("e", [-103.0, 44.5], 1800)],
  cities=[M(W("p39", "silo") + 0.2, MINOT, "Minot", RED, "target", 6), M(W("p39", "silo") + 0.5, MALMSTROM, "Malmstrom", RED, "target", 6), M(W("p39", "silo") + 0.8, WARREN, "Warren", RED, "target", 6)],
  labels=[(W("p39", "ground") - 0.1, [-107.0, 51.5], "Ground bursts", ORANGE), (W("p39", "heavy") - 0.1, [-107.0, 36.5], "Heavy local fallout", AMBER)], highlight=[HL_US], clock="DAY 1", clockLabel="FALLOUT", clockRate=0)
R("c6-fall3", W("p39", "engine") - 0.3, [("s", [-103.0, 44.5], 1900), ("e", [-100.0, 44.5], 2400)],
  cities=[M(CUR + 0.1, MINOT, "Minot", RED, "target", 6), M(CUR + 0.1, MALMSTROM, "Malmstrom", RED, "target", 6), M(CUR + 0.1, WARREN, "Warren", RED, "target", 6)],
  labels=[(W("p39", "wind") - 0.1, [-111.0, 51.2], "Wind from the west (our choice)", YELLOW)],
  plume={"at": MINOT, "bearing": 90, "lengthKm": 150, "widthKm": 60, "t0": rel(CUR, W("p39", "plume") - 0.1), "t1": rel(CUR, W("p39", "plume") + 2.0), "color": AMBER, "label": "Direction only"},
  highlight=[HL_US], clock="DAY 1", clockLabel="FALLOUT", clockRate=0)
G("c6-fall4a", W("p39", "gives") - 0.2, [("s", 44.0, -100, 2200), ("e", 43.0, -92, 1700)],
  marks=[M(W("p39", "engine") - 0.1, [-100.0, 44.0], "The engine gives a category", WHITE, "ring", 6)], highlight=[HL_US], clock="DAY 1", clockLabel="FALLOUT", clockRate=0)
G("c6-fall4", S("p40"), [("s", 43.0, -92, 1700), ("e", 40.0, -80, 1400)],
  marks=[M(W("p39", "no") - 0.1, [-86.0, 44.0], "No distances, so none here", YELLOW, "ring", 6)], highlight=[HL_US], clock="DAY 1", clockLabel="FALLOUT", clockRate=0)
# p40 cities
G("c6-cities", W("p40", "tactical") - 0.15, [("s", 45.0, -80, 1100), (2.0, 50.0, -20, 900), ("e", 50.0, 20, 900)],
  marks=[M(S("p40") + 0.4, NYC, "Second: the cities", RED, "target", 6), M(S("p40") + 0.8, LA, None, RED, "target", 6), M(S("p40") + 1.2, MOSCOW, None, RED, "target", 6), M(S("p40") + 1.6, STPETE, None, RED, "target", 6)], clock="DAY 1", clockLabel="THE CITIES", clockRate=0)
G("c6-plana", W("p40", "Its") - 0.25, [("s", 48.0, -20, 760), (2.0, 46.0, -60, 1000), ("e", 40.0, -100, 1100)],
  marks=[M(W("p40", "tactical") - 0.1, RAMSTEIN, "1. Tactical use", YELLOW, "ring", 6), M(W("p40", "strikes") - 0.1, MINOT, "2. Nuclear forces", ORANGE, "ring", 6), M(W("p40", "population") - 0.2, NYC, "3. Population centres", RED, "ring", 6)],
  caption="Princeton Plan A: the same order as our hour", clock="DAY 1", clockLabel="THE ORDER OF PLAN A", clockRate=0, source="Princeton Science and Global Security, Plan A, 2019")
G("c6-larger", W("p40", "more") - 0.1, [("s", 40.0, -100, 1100), ("e", 50.0, -40, 760)], marks=[M(W("p40", "estimate") - 0.1, [-60.0, 48.0], "Its estimate: a larger war", YELLOW, "ring", 6)], caption="Princeton Plan A estimate, a larger war than ours", clock="DAY 1", clockLabel="THE CITIES", clockRate=0)
card("c6-90m", W("p40", "direct") - 0.15, type="number", value="MORE THAN 90 MILLION", countTo=90, prefix="MORE THAN ", suffix=" MILLION", label="dead and injured in the first few hours, direct effects only",
     sub="Princeton Plan A, a larger war than ours", color=AMBER, source="Princeton Science and Global Security, Plan A, 2019")
G("c6-theirs", W("p40", "our", 2) - 0.2, [("s", 50.0, 0, 800), ("e", 45.0, -50, 700)],
  marks=[M(W("p40", "That") + 0.2, [-30.0, 52.0], "The study's number, not ours", YELLOW, "ring", 6)], caption="The study's number, not ours", clock="DAY 1", clockLabel="THE CITIES", clockRate=0)
G("c6-ours", S("p41"), [("s", 45.0, -50, 700), ("e", 52.0, -80, 900)],
  marks=[M(W("p40", "smaller") - 1.0, [-60.0, 50.0], "Our selection is smaller", WHITE, "ring", 6)], caption="Our selection is smaller", clock="DAY 1", clockLabel="THE CITIES", clockRate=0)
# p41 the sky
G("c6-sky", W("p41", "a", 2) - 0.2, [("s", 20.0, -20, 600), ("e", 30.0, 30, 680)], marks=[M(S("p41") + 0.4, [-20.0, 55.0], "Third: the sky", YELLOW, "ring", 6)], highlight=[], clock="YEARS AFTER", clockLabel="THE SKY", clockRate=0)
card("c6-soot", W("p41", "finds") - 0.2, type="number", value="150 MILLION TONNES", countTo=150, suffix=" MILLION TONNES", label="of soot, in one climate model of a far larger war", sub="a model, not a forecast", color=ORANGE, source="Toon, Robock et al., 2019; Nature Food, 2022")
G("c6-cold", W("p41", "It") - 0.2, [("s", 30.0, -10, 640), (2.2, 35.0, 40, 700), ("e", 20.0, 100, 760)], highlight=[], dim=0.5,
  marks=[M(W("p41", "temperatures") - 0.2, [10.0, 40.0], "Global temperatures fall sharply", WHITE, "ring", 6)], caption="Falling sharply for years, in one model", clock="YEARS AFTER", clockLabel="THE SKY", clockRate=0)
G("c6-model", W("p41", "Our") - 0.2, [("s", 20.0, 100, 640), ("e", 30.0, 20, 700)], highlight=[], dim=0.4,
  marks=[M(W("p41", "forecast") - 0.4, [60.0, 40.0], "One model, not a forecast", YELLOW, "ring", 6)], caption="One model, not a forecast", clock="YEARS AFTER", clockLabel="THE SKY", clockRate=0)
G("c6-notnear", S("p42"), [("s", 50.0, -30, 700), ("e", 48.0, 10, 800)],
  marks=allmk2[:12] + [M(W("p41", "nowhere") - 0.1, [-10.0, 60.0], "Our 375 warheads: nowhere near", WHITE, "ring", 6)], caption="Our 375 warheads are nowhere near that war", clock="T+52:36", clockLabel="OUR HOUR", clockRate=0)
# p42 the harvest
G("c6-harvest", W("p42", "war") - 0.2, [("s", 40.0, -90, 760), (2.0, 40.0, 0, 800), ("e", 20.0, 80, 900)], highlight=[],
  marks=[M(S("p42") + 0.4, [-95.0, 41.0], "Fourth: the harvest", YELLOW, "ring", 6), M(W("p42", "Nature") - 0.2, [10.0, 48.0], "Nature Food, 2022", WHITE, "dot", 5)], caption="Nature Food, 2022", clock="4 YEARS AFTER", clockLabel="THE HARVEST", clockRate=0, source="Xia, Robock et al., Nature Food, 2022")
G("c6-4400", W("p42", "ninety") - 0.3, [("s", 20.0, 60, 700), ("e", 28.0, 20, 800)], highlight=[], dim=0.35,
  marks=[M(W("p42", "forty-four") - 0.1, [20.0, 40.0], "About 4,400 weapons in the study", AMBER, "ring", 7)], caption="A far larger war than ours", clock="4 YEARS AFTER", clockLabel="THE HARVEST", clockRate=0, source="Xia, Robock et al., Nature Food, 2022")
card("c6-90", W("p42", "More") - 0.2, type="number", value="ABOUT 90%", countTo=90, prefix="ABOUT ", suffix="%", label="of world crop calories lost within four years", sub="in that one model", color=RED, source="Xia, Robock et al., Nature Food, 2022")
G("c6-5b", W("p42", "with") - 0.2, [("s", 20.0, 60, 700), ("e", 25.0, 90, 800)], highlight=[], dim=0.35,
  marks=[M(W("p42", "five") - 0.1, [78.0, 22.0], "5 billion+ would die of famine", RED, "ring", 7)], caption="In that one model", clock="4 YEARS AFTER", clockLabel="THE HARVEST", clockRate=0, source="Xia, Robock et al., Nature Food, 2022")
G("c6-noadapt", S("p43"), [("s", 25.0, 90, 800), ("e", 30.0, 10, 700)], highlight=[], dim=0.35,
  marks=[M(W("p42", "no") - 0.1, [20.0, 20.0], "No adaptation assumed", YELLOW, "ring", 6)], caption="No adaptation assumed", clock="4 YEARS AFTER", clockLabel="THE HARVEST", clockRate=0, source="Xia, Robock et al., Nature Food, 2022")
# p43 clock stops
G("c6-stops", W("p43", "We") - 0.2, [("s", 50.0, -20, 760), ("e", 50.0, -45, 640)], marks=allmk2[:], flashes=[], clock="T+52:36", clockLabel="THE CLOCK STOPS", clockRate=0, caption="The clock stops at minute fifty-three.")
G("c6-know", S("p44"), [("s", 40.0, -40, 640), (2.0, 30.0, 0, 560), ("e", 20.0, 30, 540)], marks=[M(W("p43", "know") - 0.1, [-30.0, 40.0], "We do not know what comes next", WHITE, "ring", 6)], highlight=[], clock="T+52:36", clockLabel="THE CLOCK STOPS", clockRate=0)

# ================================================================== End slate (starts on the spoken next-scenario line)
card("end", END, type="endslate", tag="", title="Next scenario", line="Russia attacks the Baltic, the first 72 hours.")


# ------------------------------------------------------------------ tags by section
def tag_for(t):
    if t < S("p05"):
        return "SIMULATION"
    if t < S("p11"):
        return "REAL DATA"
    if t < S("p15"):
        return "REAL HISTORY"
    return "SIMULATION"


for s in shots:
    if s["type"] != "endslate" and "tag" not in s:
        s["tag"] = tag_for(s["start"])
    elif s["type"] == "endslate":
        s["tag"] = ""
    # the cold-open shots that are tagged by hand stay as they are

PLAINS = [("Bismarck", [-100.78, 46.81]), ("Billings", [-108.5, 45.78]), ("Denver", [-104.99, 39.74]), ("Omaha", [-95.93, 41.26]), ("Minneapolis", [-93.27, 44.98]), ("Rapid City", [-103.23, 44.08])]
for sh in shots:
    if sh["type"] != "region" or not (-112 < sh["camera"][0]["center"][0] < -95 and 38 < sh["camera"][0]["center"][1] < 50):
        continue
    have = [tuple(c["at"]) for c in sh["cities"]]
    for nm, at in PLAINS:
        ok = all(abs(at[0] - k["center"][0]) < k["widthKm"] / 111 * 0.36 and abs(at[1] - k["center"][1]) < k["widthKm"] / 111 * 0.2 for k in sh["camera"])
        if ok and not any(abs(at[0] - h[0]) < 1.5 and abs(at[1] - h[1]) < 1.5 for h in have):
            sh["cities"].append({"at": at, "label": nm, "kind": "dot", "t": 0.3})
# the globes used no explicit highlight: empty list means none
# ------------------------------------------------------------------ audio plan and output
booms = [tF + 0.1, FLASH["rus-slbm-capecod"] + 0.1, FLASH["rus-slbm-bangor"] + 0.1, FLASH["rus-slbm-dc"] + 0.1, FLASH["rus-icbm-offutt"] + 0.1,
         FLASH["rus-icbm-minot"] + 0.1, W("p27", "Kozelsk"), FLASH["rus-slbm-nyc"] + 0.1, W("p36", "Because") + 99]
booms = [t for t in booms if t < 600]
b0 = round(min(tF - 0.3, W("p02", "simulation") - 0.3), 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p05") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p05") - 1, "to": S("p15") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p15") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.4, "gain_db": -12} for s in shots if s["type"] == "radar"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": round(t, 2), "gain_db": -4} for t in booms],
           "attribution": "Maps: Natural Earth (public domain); OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles. Imagery: NASA Blue Marble and Black Marble. Narration: AI-generated.",
           "shots": shots}
for s in shots:
    for key in ("markers", "cities", "ships"):
        for m in s.get(key, []):
            if m.get("label") in (None, ""):
                m.pop("label", None)
    for key in ("arcs", "flashes", "markers"):
        if key in s and not s[key]:
            s.pop(key)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
