"""Director pass for episode 002: builds episode.json from narration/timing.json, narration/words.json and
scenario.computed.json.

Run from the studio root:  .venv/Scripts/python episodes/002-china-blockades-taiwan/shotlist.py
Shot boundaries follow paragraph timings; mid-paragraph cuts land on the start of a spoken word (words.json).
"""
import json
import math
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = json.load(open(EP / "narration" / "words.json", encoding="utf-8")) if (EP / "narration" / "words.json").exists() else []
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F"
DIM = "rgba(236,239,242,0.7)"
SUN = sc["sun"]
TOTAL = timing["total_seconds"]


def S(pid):
    return U[pid]["start"]


def W(pid, word, nth=1):
    """Start time of the nth spoken occurrence of `word` in paragraph pid (falls back to proportional time)."""
    hits = [w for w in WORDS if w["unit"] == pid and w["word"].strip(".,;:?!").lower() == word.lower()]
    if len(hits) >= nth:
        return round(hits[nth - 1]["start"] - 0.15, 3)
    u = U[pid]
    words = u["text"].split()
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
TAIWAN, CHINA, JAPAN, PHIL, CUBA, USA = "158", "156", "392", "608", "192", "840"
KAOHSIUNG, KEELUNG, TAICHUNG, TAIPEI, HUALIEN = [120.27, 22.61], [121.74, 25.13], [120.51, 24.29], [121.56, 25.03], [121.60, 23.98]
LNG = {"Yong-An LNG": [120.20, 22.82], "Taichung LNG": [120.49, 24.25], "Guantang LNG": [121.05, 25.07]}
PINGTAN, HSINCHU = [119.79, 25.50], [120.92, 24.81]
KINMEN, XIAMEN, PRATAS = [118.32, 24.44], [118.09, 24.48], [116.72, 20.70]
YONAGUNI, KADENA, GUAM, YOKOSUKA, MANILA = [123.0, 24.45], [127.768, 26.355], [144.93, 13.584], [139.67, 35.29], [120.98, 14.6]
BASHI, BATANES, SHANGHAI, FUZHOU = [121.4, 21.6], [121.97, 20.45], [121.47, 31.23], [119.30, 26.08]
CG = [128.0, 23.8]
STRIKES = {s["id"]: s for s in sc["strikes"]}
DF26_SITE = [STRIKES["df26n-gw"]["launch_lon"], STRIKES["df26n-gw"]["launch_lat"]]
DF17_SITE = [STRIKES["df17-kadena"]["launch_lon"], STRIKES["df17-kadena"]["launch_lat"]]
NUKE = STRIKES["df26n-gw"]["effects"]
TW_VIEW = {"center": [120.9, 23.7], "widthKm": 1300}
HL_TW = {"iso": TAIWAN, "color": YELLOW, "fill": "rgba(255,210,63,0.08)"}
HL_CN = {"iso": CHINA, "color": RED, "fill": "rgba(255,59,59,0.06)"}


def off(p, dlon, dlat):
    return [round(p[0] + dlon, 4), round(p[1] + dlat, 4)]


def around(center, r_deg, n, phase=0.0):
    return [[round(center[0] + r_deg * math.cos(phase + 2 * math.pi * i / n) / math.cos(math.radians(center[1])), 4),
             round(center[1] + r_deg * math.sin(phase + 2 * math.pi * i / n), 4)] for i in range(n)]


def box(c, w, h, rot=0.0):
    """Quadrilateral zone of w x h degrees around c, rotated by rot radians."""
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        x, y = dx * math.cos(rot) - dy * math.sin(rot), dx * math.sin(rot) + dy * math.cos(rot)
        pts.append([round(c[0] + x, 3), round(c[1] + y, 3)])
    return pts


# Coast guard stations off the ports (CSIS full-quarantine scenario: more than three dozen ships)
PORT_PICKETS = [(KAOHSIUNG, [-0.35, -0.25], 9), (TAICHUNG, [-0.45, 0.0], 8), (KEELUNG, [0.25, 0.3], 8), (LNG["Guantang LNG"], [-0.35, 0.2], 6), (HUALIEN, [0.4, 0.0], 6)]
CCG_STATIONS = []
for port, (dx, dy), n in PORT_PICKETS:
    c = off(port, dx, dy)
    CCG_STATIONS += around(c, 0.22, n, phase=0.4)

ZONES_BLOCKADE = [
    {"points": box(off(KAOHSIUNG, -0.45, -0.35), 0.8, 0.55, 0.5), "label": "CLOSURE ZONE · KAOHSIUNG"},
    {"points": box(off(TAICHUNG, -0.55, 0.0), 0.6, 0.7, 0.3), "label": "TAICHUNG"},
    {"points": box(off(KEELUNG, 0.35, 0.35), 0.75, 0.5, -0.4), "label": "KEELUNG"},
    {"points": box(off(LNG["Guantang LNG"], -0.45, 0.25), 0.55, 0.45, 0.2), "label": "GUANTANG LNG"},
    {"points": box(off(HUALIEN, 0.55, -0.1), 0.6, 0.9, 0.0), "label": "EAST COAST"},
]


def tanker_in(dest, frm, t0, t1, kind="tanker", **k):
    return {"path": [frm, dest], "t0": t0, "t1": t1, "kind": kind, **k}


shots = []


def add(**k):
    shots.append(k)


def dayclock(d):
    return {"clock": f"DAY {d}", "clockLabel": "OF THE BLOCKADE"}


# ------------------------------------------------------------------ Cold open [SIMULATION]
add(id="open-tanker", type="region", start=0, end=S("p02"), tag="SIMULATION", clock="05:00", clockLabel="TAIPEI TIME · DAY 1",
    view={"center": [120.15, 22.35], "widthKm": 240}, zoomTo={"center": [120.2, 22.42], "widthKm": 170}, highlight=[HL_TW],
    cities=[{"at": KAOHSIUNG, "label": "Kaohsiung", "kind": "dot"}],
    ships=[tanker_in(off(KAOHSIUNG, -0.1, -0.12), [119.55, 21.85], 0, 14, label="LNG carrier"),
           {"path": [[120.95, 21.9], [120.12, 22.2]], "t0": 0, "t1": 7.5, "kind": "coastguard", "label": "China Coast Guard"}],
    labels=[{"at": [119.95, 22.0], "text": "60 km off Kaohsiung", "color": DIM, "t": 2}])
add(id="open-call", type="region", start=S("p02"), end=S("p03"), tag="SIMULATION", clock="06:00", clockLabel="TAIPEI TIME · DAY 1",
    caption="Stop your engines. Prepare to be boarded for inspection.",
    view={"center": [120.8, 23.6], "widthKm": 1100}, zoomTo={"center": [120.9, 23.7], "widthKm": 1250}, highlight=[HL_TW, HL_CN],
    cities=[{"at": p, "label": n, "kind": "dot"} for n, p in (("Kaohsiung", KAOHSIUNG), ("Keelung", KEELUNG), ("Taichung", TAICHUNG))],
    ships=[{"path": [off(st, 0.9 * math.cos(i), 0.9 * math.sin(i)), st], "t0": 0.5 + (i % 9) * 0.6, "t1": 8 + (i % 9) * 0.6, "kind": "coastguard"} for i, st in enumerate(CCG_STATIONS)]
          + [{"path": [frm, mid, back], "t0": 1, "t1": 17, "kind": "tanker" if i % 2 else "cargo"} for i, (frm, mid, back) in enumerate((
              ([118.2, 21.0], [119.6, 22.0], [118.9, 21.3]), ([123.8, 21.5], [121.9, 22.4], [123.0, 21.8]), ([123.9, 26.2], [122.4, 25.4], [123.4, 25.9]),
              ([117.6, 23.0], [119.3, 23.6], [118.4, 23.2]), ([124.2, 24.0], [122.4, 23.8], [123.5, 23.9]), ([119.2, 26.8], [120.4, 25.9], [119.7, 26.4])))])
add(id="open-11", type="number", start=S("p03"), end=W("p03", "On"), tag="SIMULATION", value="11 DAYS", label="of gas in storage",
    sub="Taiwan's legal LNG reserve", color=AMBER, source="Energy Administration, Ministry of Economic Affairs; CSIS")
add(id="open-23", type="stamp", start=W("p03", "On"), end=S("p04"), tag="SIMULATION", text="DAY 23", line="the first nuclear weapon used in war since Nagasaki", color=RED)
add(id="open-disclaimer", type="text", start=S("p04"), end=W("p04", "This"), tag="SIMULATION",
    lines=["A simulation", "It has not happened. The coast guard patrols that begin it are real, and every number has a source."])
add(id="open-title", type="globe", start=W("p04", "This"), end=S("p05"), tag="SIMULATION", caption="China blockades Taiwan. Day by day.",
    camera=[{"t": 0, "lat": 22, "lon": 128, "scale": 900}, {"t": 9, "lat": 24, "lon": 122, "scale": 1500}], sun={"lat": -10, "lon": 110},
    highlight=[{"iso": TAIWAN, "color": YELLOW}, {"iso": CHINA, "color": RED}], markers=[{"at": TAIPEI, "label": "Taiwan", "color": YELLOW, "kind": "dot", "t": 1}])

# ------------------------------------------------------------------ Chapter 01 [REAL DATA]
add(id="c1-card", type="chapter", start=S("p05"), end=S("p05") + 3.5, tag="REAL DATA", kicker="CHAPTER 01", title="An island that runs on ships")
add(id="c1-97", type="number", start=S("p05") + 3.5, end=S("p06"), tag="REAL DATA", value="97%", countTo=97, suffix="%", label="of Taiwan's energy is imported",
    sub="almost all of it by sea · energy self-sufficiency 4.2%", source="CSIS, 2026-05-14; Energy Administration, MOEA")
add(id="c1-lng", type="region", start=S("p06"), end=S("p07"), tag="REAL DATA", caption="Natural gas: 47.8% of Taiwan's electricity in 2025",
    source="CSIS; Energy Administration, MOEA; Argus", view={"center": [120.7, 23.8], "widthKm": 1000}, zoomTo={"center": [120.6, 23.8], "widthKm": 900}, highlight=[HL_TW],
    cities=[{"at": p, "label": n, "color": AMBER, "kind": "base", "size": 6, "t": 1 + i * 1.6} for i, (n, p) in enumerate(LNG.items())],
    ships=[tanker_in(off(p, -0.08, 0.0), f, 0.5 + i, 12 + i, label=None) for i, (p, f) in enumerate(zip(LNG.values(), ([118.9, 22.0], [119.0, 24.0], [120.0, 26.0])))],
    labels=[{"at": [121.0, 21.8], "text": "last reactor shut down · May 2025", "color": DIM, "t": 11}])
add(id="c1-reserves", type="bars", start=S("p07"), end=S("p08"), tag="REAL DATA", title="Days in storage", sub="Taiwan, 2025 to 2026",
    source="Energy Administration, MOEA; CSIS, 2026-05-14",
    bars=[{"label": "Liquefied natural gas", "value": 11, "display": "about 11 days", "color": RED},
          {"label": "Coal", "value": 40, "display": "about 40 days", "color": AMBER},
          {"label": "Crude oil", "value": 140, "display": "about 140 days", "color": TEAL}])
add(id="c1-food", type="isotype", start=S("p08"), end=S("p09"), tag="REAL DATA", headline="30%", label="of the calories Taiwan eats are grown at home",
    total=100, filled=30, per="1%", cols=20, color=TEAL, sub="30.3% in 2023, an 18-year low", source="Taipei Times, 2024-10-16")
add(id="c1-trade", type="globe", start=S("p09"), end=S("p10"), tag="REAL DATA",
    caption="Most of the world's most advanced chips. A fifth of seaborne trade sails past: about $2.45 trillion (2022).",
    source="CSIS ChinaPower; Bloomberg Economics", camera=[{"t": 0, "lat": 18, "lon": 128, "scale": 820}, {"t": 15, "lat": 22, "lon": 124, "scale": 980}], sun={"lat": -10, "lon": 120},
    highlight=[{"iso": TAIWAN, "color": YELLOW}],
    arcs=[{"from": a, "to": b, "t0": 0.5 + i * 0.7, "t1": 7 + i * 0.7, "color": TEAL, "loft": 0.02, "width": 1.6} for i, (a, b) in enumerate((
        ([121.5, 31.0], [103.8, 1.3]), ([129.0, 35.1], [103.8, 1.3]), ([120.3, 22.6], [-118.2, 33.7]), ([118.1, 24.5], [103.8, 1.3]),
        ([126.6, 37.4], [114.2, 22.3]), ([139.7, 35.4], [103.8, 1.3]), ([121.6, 38.9], [113.9, 22.5])))])
add(id="c1-strait", type="region", start=S("p10"), end=S("p11"), tag="REAL DATA", source="Wikipedia; WorldAtlas; Britannica",
    view={"center": [120.4, 24.9], "widthKm": 480}, zoomTo={"center": [120.35, 25.0], "widthKm": 400}, highlight=[HL_TW, HL_CN],
    lines=[{"from": PINGTAN, "to": HSINCHU, "label": "about 130 km", "color": AMBER, "dashed": True, "t0": 1, "t1": 3}],
    labels=[{"at": [120.35, 25.35], "text": "about 130 km at the narrowest", "color": AMBER, "t": 3}],
    countryLabels=[{"iso": CHINA, "text": "China"}], cities=[{"at": PINGTAN, "label": "Pingtan", "color": RED, "kind": "dot"}, {"at": HSINCHU, "label": "Hsinchu", "kind": "dot"}])

# ------------------------------------------------------------------ Chapter 02 [REAL HISTORY]
add(id="c2-card", type="chapter", start=S("p11"), end=S("p12"), tag="REAL HISTORY", kicker="CHAPTER 02", title="It has already started")
add(id="c2-1996", type="region", start=S("p12"), end=S("p13"), tag="REAL HISTORY", clock="1996", clockLabel="MARCH",
    caption="Missiles off Taiwan's two biggest ports, before its first direct presidential election", source="US State Department; CSIS Missile Threat; DVIDS",
    view=TW_VIEW, highlight=[HL_TW, HL_CN], cities=[{"at": KAOHSIUNG, "label": "Kaohsiung", "kind": "dot"}, {"at": KEELUNG, "label": "Keelung", "kind": "dot"}],
    rings=[{"at": off(KEELUNG, 0.3, 0.35), "km": 30, "color": RED, "t": 2}, {"at": off(KAOHSIUNG, -0.3, -0.3), "km": 30, "color": RED, "t": 3.2}],
    ships=[{"path": [[127.5, 26.0], [123.0, 23.9]], "t0": 7, "t1": 16, "kind": "us", "label": "USS Independence"},
           {"path": [[123.5, 19.5], [122.7, 22.0]], "t0": 9, "t1": 17, "kind": "us", "label": "USS Nimitz"}])
add(id="c2-2022", type="region", start=S("p13"), end=S("p14"), tag="REAL HISTORY", clock="2022", clockLabel="AUGUST",
    caption="11 ballistic missiles. Five landed in Japan's exclusive economic zone.", source="ASPI; Taipei Times, 2022-08-05",
    view={"center": [122.0, 23.8], "widthKm": 1300}, highlight=[HL_TW, HL_CN, {"iso": JAPAN, "color": TEAL}],
    zones=[{"points": box(p, 0.7, 0.5, r), "t": 0.5 + i * 0.4} for i, (p, r) in enumerate((([119.9, 25.6], 0.3), ([122.4, 25.5], -0.3), ([123.3, 23.4], 0.0), ([121.4, 21.5], 0.2), ([119.3, 22.6], 0.4), ([118.6, 24.2], 0.0)))],
    rings=[{"at": p, "km": 18, "color": RED, "t": 4 + i * 0.6} for i, p in enumerate(([123.2, 24.0], [123.5, 23.2], [122.6, 25.6], [121.6, 21.4], [119.6, 22.6]))],
    labels=[{"at": [124.3, 24.9], "text": "Japan EEZ", "color": TEAL, "t": 6}])
add(id="c2-153", type="number", start=S("p14"), end=S("p15"), tag="REAL HISTORY", value="153", countTo=153, label="Chinese military aircraft around Taiwan in one day",
    sub="Joint Sword-2024B · 14 October 2024 · coast guard ships circling the island", color=RED, source="NBC News; VOA")
add(id="c2-2025", type="stamp", start=S("p15"), end=S("p16"), tag="REAL HISTORY", text="April 2025",
    line="Strait Thunder-2025A · training in blockade and control · live fire at simulated ports and energy facilities", color=AMBER)
add(id="c2-justice", type="region", start=S("p16"), end=S("p17"), tag="REAL HISTORY", clock="2025", clockLabel="DECEMBER",
    caption="Justice Mission 2025: zones overlapping Taiwan's territorial waters", source="USNI News, 2025-12-31; The Aviationist",
    view=TW_VIEW, highlight=[HL_TW, HL_CN],
    zones=[{"points": box(off(KEELUNG, 0.25, 0.45), 0.9, 0.5, -0.3), "t": 1, "pulse": True}, {"points": box(off(KAOHSIUNG, -0.65, -0.25), 0.7, 0.7, 0.4), "t": 2.2, "pulse": True},
           {"points": box(off(TAICHUNG, -0.7, 0.2), 0.55, 0.6, 0.0), "t": 3.4}],
    lines=[{"from": FUZHOU, "to": off(KEELUNG, 0.2, 0.45), "color": RED, "t0": 5, "t1": 7}, {"from": [118.1, 24.5], "to": off(KAOHSIUNG, -0.6, -0.25), "color": RED, "t0": 6, "t1": 8}])
add(id="c2-2026", type="region", start=S("p17"), end=S("p18"), tag="REAL DATA", clock="OCT 2026", clockLabel="NOW",
    caption="China Coast Guard \"law enforcement patrols\" east of Taiwan, since early October 2026", source="Reuters, 2026-10-31; Baird Maritime, 2026-11-02",
    view={"center": [121.9, 23.8], "widthKm": 1150}, highlight=[HL_TW],
    ships=[{"path": [[123.2, 25.6], [122.6, 24.2], [122.7, 22.8], [123.2, 22.0]], "t0": 0, "t1": 16, "kind": "coastguard", "label": "China Coast Guard"},
           {"path": [[122.8, 22.3], [122.5, 23.5], [122.9, 24.9]], "t0": 2, "t1": 16, "kind": "coastguard"}],
    labels=[{"at": [123.3, 23.6], "text": "waters east of Taiwan", "color": ORANGE, "t": 3}])

# ------------------------------------------------------------------ Chapter 03 [REAL DATA]
add(id="c3-card", type="chapter", start=S("p18"), end=S("p19"), tag="REAL DATA", kicker="CHAPTER 03", title="Quarantine, not blockade")
add(id="c3-law", type="text", start=S("p19"), end=W("p19", "quarantine"), tag="REAL DATA",
    lines=["Blockade: an act of aggression", "UN General Assembly Resolution 3314 (1974), Article 3(c). It can mark the start of a war."])
add(id="c3-quarantine", type="text", start=W("p19", "quarantine"), end=W("p19", "When"), tag="REAL DATA",
    lines=["Quarantine: law enforcement", "coast guards and customs officers. At least on paper, something less than war."])
add(id="c3-cuba", type="region", start=W("p19", "When"), end=S("p20"), tag="REAL HISTORY", clock="1962", clockLabel="OCTOBER",
    caption="1962: America called its naval ring around Cuba a \"quarantine\"", source="Lieber Institute, West Point; CSIS",
    view={"center": [-78.5, 22.5], "widthKm": 1600}, highlight=[{"iso": CUBA, "color": RED}, {"iso": USA, "color": TEAL}],
    ships=[{"path": [p, p], "t0": 0, "t1": 1, "kind": "us", "t": 0.3 + i * 0.25} for i, p in enumerate(around([-78.5, 21.8], 4.2, 12, 0.2))])
add(id="c3-ccg", type="bars", start=S("p20"), end=S("p21"), tag="REAL DATA", title="Ocean-going coast guard ships", sub="over 1,000 tonnes",
    source="CSIS, How China Could Quarantine Taiwan, 2024-06-05",
    bars=[{"label": "China Coast Guard", "value": 150, "display": "more than 150", "color": ORANGE}, {"label": "Taiwan Coast Guard", "value": 10, "display": "about 10", "color": YELLOW}])

# ------------------------------------------------------------------ Chapter 04 [SIMULATION]
add(id="c4-card", type="chapter", start=S("p21"), end=S("p21") + 3.5, tag="SIMULATION", kicker="CHAPTER 04", title="Day by day")
add(id="c4-d1", type="region", start=S("p21") + 3.5, end=S("p22"), tag="SIMULATION", **dayclock(1), caption="Customs inspection for every ship bound for Taiwan",
    view=TW_VIEW, highlight=[HL_TW, HL_CN], cities=[{"at": p, "label": n, "kind": "dot"} for n, p in (("Kaohsiung", KAOHSIUNG), ("Keelung", KEELUNG), ("Taichung", TAICHUNG))],
    ships=[{"path": [off(st, 1.2 * math.cos(i * 1.7), 1.2 * math.sin(i * 1.7)), st], "t0": 0.2 + (i % 12) * 0.35, "t1": 6 + (i % 12) * 0.35, "kind": "coastguard"} for i, st in enumerate(CCG_STATIONS)]
          + [{"path": [[118.0, 27.2], [118.6, 26.7]], "t0": 0, "t1": 9, "kind": "pla", "label": "PLA Navy · over the horizon"}],
    labels=[{"at": [122.9, 21.4], "text": "37 coast guard ships", "color": ORANGE, "t": 6}])
add(id="c4-d2", type="region", start=S("p22"), end=S("p23"), tag="SIMULATION", **dayclock(2), view={"center": [121.2, 23.4], "widthKm": 1300}, highlight=[HL_TW],
    ships=[{"path": [p, off(p, (121.0 - p[0]) * 0.25, (23.6 - p[1]) * 0.25), off(p, (121.0 - p[0]) * 0.05, (23.6 - p[1]) * 0.05)], "t0": 0, "t1": 8, "kind": "tanker" if i % 3 == 0 else "cargo"}
           for i, p in enumerate(around([121.0, 23.6], 4.2, 14, 0.3))]
          + [{"path": [st, st], "t0": 0, "t1": 1, "kind": "coastguard", "wake": False} for st in CCG_STATIONS[::2]],
    labels=[{"at": [121.0, 19.6], "text": "tankers hold position", "color": AMBER, "t": 4}])
add(id="c4-d4", type="timeline", start=S("p23"), end=S("p24"), tag="SIMULATION", **dayclock(4), title="Taiwan's gas", sub="days of LNG in storage at the start of the blockade",
    total=12, unit="DAYS", segments=[{"from": 0, "to": 4, "label": "Normal supply", "color": TEAL}, {"from": 4, "to": 11, "label": "Industry cut off · homes and hospitals first", "color": AMBER}, {"from": 11, "to": 12, "label": "Empty", "color": RED}],
    cursorTo=4)
d6_zone_t = W("p24", "That") - S("p24")
add(id="c4-d6", type="region", start=S("p24"), end=S("p25"), tag="SIMULATION", **dayclock(6),
    view={"center": [120.1, 22.45], "widthKm": 260}, zoomTo={"center": [120.9, 23.7], "widthKm": 1300}, highlight=[HL_TW, HL_CN],
    cities=[{"at": KAOHSIUNG, "label": "Kaohsiung", "kind": "dot"}],
    ships=[{"path": [[119.6, 21.85], [119.98, 22.3], [120.0, 22.33]], "t0": 0, "t1": 9, "kind": "tanker", "label": "LNG carrier"},
           {"path": [[119.7, 21.75], [120.0, 22.12], [120.01, 22.15]], "t0": 0, "t1": 9, "kind": "ally", "label": "Taiwanese frigate"},
           {"path": [[120.5, 22.1], [120.15, 22.4]], "t0": 2, "t1": 8.5, "kind": "coastguard", "label": "CCG cutter"}]
          + [{"path": [[118.2 + (i % 4) * 0.3, 21.8 + i * 0.5], off(z["points"][0], -0.05, 0)], "t0": d6_zone_t + 1 + i * 0.4, "t1": d6_zone_t + 8 + i * 0.4, "kind": "pla"} for i, z in enumerate(ZONES_BLOCKADE)],
    zones=[dict(z, t=d6_zone_t + 0.5 + i * 0.8, pulse=True) for i, z in enumerate(ZONES_BLOCKADE)],
    caption=None)
shots[-1].pop("caption")
add(id="c4-d9", type="stamp", start=S("p25"), end=S("p26"), tag="SIMULATION", **dayclock(9), text="Rolling blackouts", line="chip factories on priority power · the world starts counting its stock", color=AMBER)
add(id="c4-d11", type="timeline", start=S("p26"), end=W("p26", "Keeping"), tag="SIMULATION", **dayclock(11), title="Taiwan's gas", sub="days of LNG in storage",
    total=12, unit="DAYS", segments=[{"from": 0, "to": 4, "label": "Normal supply", "color": TEAL}, {"from": 4, "to": 11, "label": "Rationing", "color": AMBER}, {"from": 11, "to": 12, "label": "Empty", "color": RED}],
    highlight={"from": 10, "to": 11, "label": "CSIS wargames: about 10 days"}, cursorTo=11, source="CSIS, Lights Out?, 2025-07-31")
add(id="c4-airlift", type="number", start=W("p26", "Keeping"), end=S("p27"), tag="REAL DATA", value="800+", label="cargo flights a day to supply Taiwan by air",
    sub="CSIS blockade wargames, 2025 (FlightGlobal reports 860)", color=AMBER, source="CSIS; FlightGlobal")
CONVOY = [[[118.6 + 0.12 * (i % 3), 16.8 - 0.25 * i], [121.2 + 0.08 * (i % 3), 20.6 - 0.2 * i], [121.25, 21.9 - 0.15 * i]] for i in range(6)]
add(id="c4-d14", type="region", start=S("p27"), end=S("p28"), tag="SIMULATION", **dayclock(14), caption="A convoy from the south, through the Bashi Channel",
    view={"center": [121.0, 20.6], "widthKm": 1500}, highlight=[HL_TW, {"iso": PHIL, "color": TEAL}],
    ships=[{"path": p, "t0": 0.5, "t1": 11, "kind": "tanker"} for p in CONVOY]
          + [{"path": [off(p[0], 0.35, 0.1), off(p[1], 0.3, 0.1), off(p[2], 0.3, 0.1)], "t0": 0.5, "t1": 11, "kind": "us", "label": "US destroyer" if j == 0 else None} for j, p in enumerate(CONVOY[::2])],
    labels=[{"at": BASHI, "text": "Bashi Channel", "color": DIM, "t": 2}, {"at": [120.3, 18.0], "text": "Luzon", "color": DIM}],
    zones=[dict(ZONES_BLOCKADE[0], t=0)])
d16_strike = W("p28", "Within")
add(id="c4-d16", type="region", start=S("p28"), end=d16_strike, tag="SIMULATION", **dayclock(16),
    view={"center": [120.6, 21.9], "widthKm": 300}, zoomTo={"center": [120.6, 22.0], "widthKm": 240}, highlight=[HL_TW],
    zones=[dict(ZONES_BLOCKADE[0], t=0)],
    ships=[{"path": [[121.1, 21.2], [120.85, 21.75]], "t0": 0, "t1": 6, "kind": "tanker"}, {"path": [[121.25, 21.25], [121.0, 21.8]], "t0": 0, "t1": 6, "kind": "us", "label": "US destroyer"},
           {"path": [[120.2, 22.35], [120.55, 22.0]], "t0": 0, "t1": 5, "kind": "pla", "label": "PLA destroyer"}],
    lines=[{"from": [120.55, 22.0], "to": [121.0, 21.8], "color": RED, "t0": 5.5, "t1": 6.2}],
    rings=[{"at": [121.0, 21.8], "km": 4, "color": AMBER, "t": 6.3, "dashed": False}])
add(id="c4-d16-strike", type="globe", start=d16_strike, end=S("p29"), tag="SIMULATION", **dayclock(16), caption="Conventional missiles. Okinawa: about 7 minutes. Guam: about 13.",
    source="Scenario engine: 1,087 km and 3,426 km", camera=[{"t": 0, "lat": 22, "lon": 126, "scale": 900}, {"t": 16, "lat": 21, "lon": 131, "scale": 780}], sun={"lat": -20, "lon": 60},
    highlight=[{"iso": TAIWAN, "color": YELLOW}, {"iso": CHINA, "color": RED}],
    markers=[{"at": KADENA, "label": "Kadena AB", "color": TEAL, "kind": "base", "t": 0.5}, {"at": GUAM, "label": "Andersen AFB · Guam", "color": TEAL, "kind": "base", "t": 0.8}],
    arcs=[{"from": DF17_SITE, "to": KADENA, "t0": 1.0, "t1": 1.0 + 7.3 * 0.9, "color": RED, "loft": 0.08}, {"from": DF26_SITE, "to": GUAM, "t0": 1.4, "t1": 1.4 + 13.3 * 0.9, "color": RED, "loft": 0.14}],
    flashes=[{"at": KADENA, "t": 1.0 + 7.3 * 0.9, "radius": 10, "hold": 2, "color": AMBER}, {"at": GUAM, "t": 1.4 + 13.3 * 0.9, "radius": 10, "hold": 2, "color": AMBER}])
add(id="c4-d19", type="region", start=S("p29"), end=S("p30"), tag="SIMULATION", **dayclock(19), caption="In the CSIS invasion wargames, China lost more than 130 major ships",
    source="CSIS, The First Battle of the Next War, 2023", view=TW_VIEW, highlight=[HL_TW, HL_CN], zones=[dict(z, t=0) for z in ZONES_BLOCKADE],
    ships=[{"path": [off(z["points"][(i % 4)], 0.05, 0.05), off(z["points"][(i + 1) % 4], 0.05, 0.05)], "t0": 0, "t1": 14, "kind": "pla", "sunkAt": 2 + i * 1.1 if i % 3 != 2 else None}
           for i, z in enumerate(ZONES_BLOCKADE * 3)])
for s in shots[-1]["ships"]:
    if s.get("sunkAt") is None:
        s.pop("sunkAt", None)
add(id="c4-d22", type="stamp", start=S("p30"), end=S("p31"), tag="SIMULATION", **dayclock(22), text="Failing", line="for a leadership that has just purged its own top generals, a threat to the party itself", color=AMBER)
add(id="c4-pentagon", type="text", start=S("p31"), end=S("p32"), tag="REAL DATA",
    lines=["\"Probably would consider nuclear first use\"", "US Department of Defense, on China, if a conventional defeat over Taiwan gravely threatened the regime's survival"])

# ------------------------------------------------------------------ Chapter 05 [SIMULATION]
FLIGHT = STRIKES["df26n-gw"]["flight_min"]
add(id="c5-card", type="chapter", start=S("p32"), end=S("p32") + 3.5, tag="SIMULATION", kicker="CHAPTER 05", title="Day twenty-three")
add(id="c5-launch", type="globe", start=S("p32") + 3.5, end=S("p33"), tag="SIMULATION", clock="04:10", clockLabel="TAIPEI TIME · DAY 23",
    caption="Conventional or nuclear? On radar, the same missile.", camera=[{"t": 0, "lat": 24, "lon": 115, "scale": 1700}, {"t": 12, "lat": 24, "lon": 121, "scale": 1100}], sun=SUN,
    highlight=[{"iso": TAIWAN, "color": YELLOW}, {"iso": CHINA, "color": RED}],
    markers=[{"at": DF26_SITE, "label": "DF-26 launcher", "color": RED, "kind": "base", "t": 0.5}],
    arcs=[{"from": DF26_SITE, "to": CG, "t0": 2, "t1": 2 + FLIGHT * 60 / 4, "color": RED, "loft": 0.12}])
add(id="c5-target", type="region", start=S("p33"), end=S("p34"), tag="SIMULATION", clock="T+03:00", clockLabel="SINCE LAUNCH", source="Scenario engine",
    view={"center": [125.2, 24.4], "widthKm": 1500}, highlight=[HL_TW, {"iso": JAPAN, "color": TEAL}],
    cities=[{"at": HUALIEN, "label": "Hualien", "kind": "dot"}, {"at": YONAGUNI, "label": "Yonaguni", "kind": "dot"}, {"at": KADENA, "label": "Kadena", "color": TEAL, "kind": "base", "size": 5}],
    ships=[{"path": [off(CG, dx, dy), off(CG, dx + 0.1, dy + 0.05)], "t0": 0, "t1": 12, "kind": "us", "label": "US carrier group" if i == 0 else None}
           for i, (dx, dy) in enumerate(((0, 0), (0.25, 0.2), (-0.25, 0.15), (0.2, -0.25), (-0.2, -0.2), (0.4, -0.02)))],
    lines=[{"from": HUALIEN, "to": CG, "color": AMBER, "dashed": True, "t0": 2, "t1": 4}],
    labels=[{"at": [124.8, 23.5], "text": "about 650 km", "color": AMBER, "t": 4}])
RINGS = [
    {"km": NUKE["fireball_km"], "label": "Fireball · about 300 m across", "color": WHITE},
    {"km": NUKE["psi5_km"], "label": "5 psi · on land, most buildings flattened", "color": RED},
    {"km": NUKE["thermal3_km"], "label": "Flash burns", "color": ORANGE},
    {"km": NUKE["psi1_km"], "label": "1 psi · on land, windows shatter", "color": TEAL},
]
FLEET = [{"path": [off(CG, dx, dy), off(CG, dx + 0.004, dy + 0.002)], "t0": 0, "t1": 30, "kind": "us", "size": 16 if i == 0 else 11, "label": "carrier" if i == 0 else None}
         for i, (dx, dy) in enumerate(((0.0, 0.0), (0.045, 0.03), (-0.05, 0.02), (0.03, -0.045), (-0.035, -0.04), (0.075, 0.0)))]


def ring_shot(sid, start, end, upto, new_t, width, clock_txt):
    rings = [{"at": CG, "km": r["km"], "label": r["label"], "color": r["color"], "t": (-5 if i < upto else new_t), "dashed": i != 0} for i, r in enumerate(RINGS[:upto + 1])]
    add(id=sid, type="region", start=start, end=end, tag="SIMULATION", clock=clock_txt, clockLabel="SINCE LAUNCH", source="Scenario engine: Glasstone and Dolan scaling, NUKEMAP calibration",
        view={"center": CG, "widthKm": width}, zoomTo={"center": CG, "widthKm": width * 1.12}, ships=FLEET, rings=rings, scaleBar=True)


ring_shot("c5-flash", S("p34"), S("p35"), 0, W("p34", "detonates") - S("p34") + 0.1, 7, "T+07:06")
shots[-1]["burst"] = {"at": CG, "t": shots[-1]["rings"][0]["t"], "km": NUKE["fireball_km"]}
shots[-1]["clock"] = "T+07:00"
ring_shot("c5-fireball", S("p35"), S("p36"), 0, -5, 6, "T+07:06")
ring_shot("c5-5psi", S("p36"), S("p37"), 1, 0.4, 7.5, "T+07:07")
ring_shot("c5-burns", S("p37"), S("p38"), 2, 0.4, 8, "T+07:07")
ring_shot("c5-1psi", S("p38"), S("p39"), 3, 0.4, 13, "T+07:08")
add(id="c5-81", type="number", start=S("p39"), end=S("p40"), tag="REAL HISTORY", value="81 YEARS", label="since a nuclear weapon was last used in war",
    sub="Nagasaki · 9 August 1945 · about 21 kilotons", color=RED, source="US DOE OSTI; National Museum of the US Air Force")

# ------------------------------------------------------------------ Chapter 06 [REAL DATA]
add(id="c6-card", type="chapter", start=S("p40"), end=S("p40") + 3.5, tag="REAL DATA", kicker="CHAPTER 06", title="The bill")
add(id="c6-gdp", type="bars", start=S("p40") + 3.5, end=S("p41"), tag="REAL DATA", title="Cost to the world economy", sub="first year, share of global GDP · Bloomberg Economics, February 2026",
    source="Bloomberg Economics via Insurance Journal, 2026-02-12", bars=[{"label": "One-year blockade", "value": 5.3, "display": "-5.3%", "color": AMBER},
                                                                       {"label": "War over Taiwan", "value": 9.6, "display": "-9.6% · $10.6 trillion", "color": RED}])
add(id="c6-countries", type="bars", start=S("p41"), end=S("p42"), tag="REAL DATA", title="In a war over Taiwan", sub="first-year change in GDP · Bloomberg Economics, February 2026",
    source="Bloomberg Economics", bars=[{"label": "Taiwan", "value": 40, "display": "-40%", "color": RED}, {"label": "South Korea", "value": 23, "display": "-23%", "color": ORANGE},
                                        {"label": "Japan", "value": 14.7, "display": "-14.7%", "color": AMBER}, {"label": "United States", "value": 6.6, "display": "-6.6%", "color": TEAL}])
add(id="c6-nonuke", type="text", start=S("p42"), end=S("p43"), tag="REAL DATA", lines=["Not included", "a nuclear weapon"])

# ------------------------------------------------------------------ Chapter 07 [REAL HISTORY]
add(id="c7-card", type="chapter", start=S("p43"), end=S("p44"), tag="REAL HISTORY", kicker="CHAPTER 07", title="It has been planned before")
add(id="c7-1955", type="stamp", start=S("p44"), end=S("p45"), tag="REAL HISTORY", text="1955", line="Eisenhower: tactical atomic weapons on military targets, \"as you would use a bullet\"", color=AMBER)
c7_split = W("p45", "America's")
add(id="c7-kinmen", type="region", start=S("p45"), end=c7_split, tag="REAL HISTORY", clock="1958", clockLabel="AUGUST", caption="1958: shelling and a blockade of Kinmen",
    source="US State Department, Office of the Historian", view={"center": [118.25, 24.45], "widthKm": 130}, zoomTo={"center": [118.25, 24.45], "widthKm": 100}, highlight=[HL_TW, HL_CN],
    cities=[{"at": XIAMEN, "label": "Xiamen", "color": RED, "kind": "dot"}, {"at": KINMEN, "label": "Kinmen", "color": YELLOW, "kind": "dot"}],
    rings=[{"at": off(KINMEN, dx, dy), "km": 1.2, "color": ORANGE, "t": 0.5 + i * 0.35, "dashed": False} for i, (dx, dy) in enumerate(((0.02, 0.01), (-0.05, 0.02), (0.08, -0.02), (-0.02, -0.03), (0.05, 0.04), (-0.09, 0.0)))])
add(id="c7-shanghai", type="region", start=c7_split, end=S("p46"), tag="REAL HISTORY", clock="1958", clockLabel="SEPTEMBER",
    caption="\"nuclear strikes deep into China as far north as Shanghai\"", source="Documents released by Daniel Ellsberg, 2021 (New York Times; CBS News)",
    view={"center": [120.8, 29.0], "widthKm": 2100}, highlight=[HL_TW, HL_CN],
    cities=[{"at": p, "label": n, "color": RED, "kind": "target", "size": 5, "t": 1 + i * 0.8} for i, (n, p) in enumerate((("Fujian air bases", [118.6, 25.4]), ("Fuzhou", FUZHOU), ("Hangzhou", [120.15, 30.27]), ("Shanghai", SHANGHAI)))],
    labels=[{"at": [123.4, 29.0], "text": "risk of Soviet retaliation accepted", "color": AMBER, "t": 9}])

# ------------------------------------------------------------------ Chapter 08 [REAL DATA]
add(id="c8-card", type="chapter", start=S("p46"), end=S("p46") + 3.5, tag="REAL DATA", kicker="CHAPTER 08", title="The decision")
add(id="c8-620", type="number", start=S("p46") + 3.5, end=S("p47"), tag="REAL DATA", value="620", countTo=620, label="Chinese nuclear warheads · January 2026",
    sub="most in storage · over 1,000 expected by 2030 (Pentagon) · declared policy: no first use", color=RED, source="SIPRI Yearbook 2026; FAS; Pentagon 2025 report")
add(id="c8-us", type="stamp", start=S("p47"), end=S("p48"), tag="REAL DATA", text="No promise", line="the US has never ruled out first use · W76-2 low-yield Trident warhead, about 5 kilotons", color=TEAL)
add(id="c8-options", type="radar", start=S("p48"), end=S("p49"), tag="SIMULATION", title="Day 23 · the president's options",
    lines=[{"k": "option 1", "v": "a small nuclear reply · W76-2"}, {"k": "option 2", "v": "a reply without one"}, {"k": "option 3", "v": "call Beijing"}],
    tracks=1, big="DECIDE", bigColor=RED, footer="")
shots[-1].pop("footer")
add(id="c8-3of15", type="isotype", start=S("p49"), end=W("p49", "And"), tag="REAL DATA", headline="3 of 15", label="wargame runs ended in nuclear catastrophe",
    total=15, filled=3, per="one run", cols=15, color=RED, sub="CSIS and MIT, Confronting Armageddon, December 2024. Cities destroyed, millions killed.", source="CSIS, 2024-12-13")
add(id="c8-diplomacy", type="text", start=W("p49", "And"), end=S("p50"), tag="REAL DATA",
    lines=["Diplomacy, not threats", "what worked better at stopping China from gambling on a nuclear weapon · CSIS and MIT, 2024"])
add(id="c8-stop", type="text", start=S("p50"), end=S("p51"), tag="SIMULATION", lines=["The simulation stops here", "Nobody can tell you how it ends."])
add(id="c8-now", type="region", start=S("p51"), end=S("p52"), tag="REAL DATA", clock="NOW", clockLabel="NOVEMBER 2026", caption="Real: China Coast Guard patrols east of Taiwan",
    source="Reuters, 2026-10-31", view={"center": [121.9, 23.8], "widthKm": 1100}, highlight=[HL_TW],
    ships=[{"path": [[122.9, 25.2], [122.5, 23.9], [122.7, 22.6]], "t0": 0, "t1": 9, "kind": "coastguard", "label": "China Coast Guard"}])
add(id="end", type="endslate", start=S("p52"), end=TOTAL + 15, tag="", title="Next scenario", line="North Korea strikes the US West Coast. Minute by minute. New scenario every day.")

# ------------------------------------------------------------------ audio plan and output
flash_t = next(s for s in shots if s["id"] == "c5-flash")
boom_t = flash_t["start"] + flash_t["rings"][0]["t"]
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": round(TOTAL + 15, 2),
           "musicPlan": [
               {"src": "bed.mp3", "from": 0, "to": S("p21") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p21") - 1, "to": S("p40") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p40") - 1, "to": TOTAL + 15, "loop": [2, 174], "gain_db": -17},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.4, "gain_db": -12} for s in shots if s["type"] == "radar"]
                    + [{"src": "whoosh.mp3", "t": max(0, s["start"] - 0.4), "gain_db": -14} for s in shots if s["type"] == "stamp"]
                    + [{"src": "boom.mp3", "t": boom_t, "gain_db": -4}]
                    + [{"src": "boom.mp3", "t": d16_strike + f["t"], "gain_db": -12} for f in next(s for s in shots if s["id"] == "c4-d16-strike")["flashes"]],
           "attribution": "Maps: Natural Earth (public domain); OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles. Imagery: NASA Blue Marble and Black Marble. Narration: AI-generated.",
           "shots": shots}
for s in shots:
    for key in ("markers", "cities", "ships"):
        for m in s.get(key, []):
            if m.get("label") is None:
                m.pop("label", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
