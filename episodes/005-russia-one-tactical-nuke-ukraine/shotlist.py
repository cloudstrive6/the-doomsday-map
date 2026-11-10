"""Director pass for episode 005: builds episode.json from narration/timing.json, words.json and scenario.computed.json.

Run from the studio root:  python -m studio shotlist 005-russia-one-tactical-nuke-ukraine
No real calendar dates and no scenario t0 date on screen (clocks are relative: T+mm:ss).
"""
import json
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
WORDS = json.load(open(EP / "narration" / "words.json", encoding="utf-8")) if (EP / "narration" / "words.json").exists() else []
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE, YELLOW = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF", "#FFD23F"
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
    idx = [i for i, w in enumerate(words) if w.strip(".,;:?!\"").lower() == word.lower()][nth - 1]
    return round(u["start"] + u["duration"] * idx / len(words), 3)


# ------------------------------------------------------------------ places [lon, lat]
ST = sc["strikes"][0]
FX = ST["effects"]
SUB = [ST["launch_lon"], ST["launch_lat"]]     # Belgorod launch site (simulated)
TGT = [ST["target_lon"], ST["target_lat"]]     # invented staging area
KHARKIV = [36.23, 49.99]
KYIV = [30.52, 50.45]
MOSCOW = [37.62, 55.75]
ZNPP = [34.586, 47.51]
WASH = [-77.04, 38.9]
NYC = [-74.0, 40.7]
BRUSSELS = [4.35, 50.85]
ANKARA = [32.86, 39.93]
NAGASAKI = [129.87, 32.74]
HIROSHIMA = [132.45, 34.4]
HAVANA = [-82.37, 23.11]
MINSK = [27.57, 53.9]
LONDON = [-0.13, 51.5]
PARIS = [2.35, 48.86]
BEIJING = [116.4, 39.9]
DELHI = [77.2, 28.6]
USA, RUSSIA, UKR, BELARUS, POLAND, ROMANIA, SLOVAKIA, HUNGARY, MOLDOVA = "840", "643", "804", "112", "616", "642", "703", "348", "498"
LTU, LVA, EST, GBR, FRA, CHN, IND, JPN, CUB = "440", "428", "233", "826", "250", "156", "356", "392", "192"
HL_UKR = {"iso": UKR, "color": TEAL, "fill": "rgba(62,214,200,0.07)"}
HL_RUS = {"iso": RUSSIA, "color": AMBER, "fill": "rgba(242,176,30,0.07)"}
HL_RUS_RED = {"iso": RUSSIA, "color": RED, "fill": "rgba(255,59,59,0.09)"}
BLUE = "#6EA8FF"   # NATO; teal is Ukraine and amber is Russia in every map
NATO_EAST = [{"iso": i, "color": BLUE, "fill": "rgba(110,168,255,0.10)"} for i in (POLAND, ROMANIA, SLOVAKIA, HUNGARY, LTU, LVA, EST)]

shots = []


def add(**k):
    shots.append(k)


def clock(minute):
    return f"T+{int(minute):02d}:{int(round((minute % 1) * 60)):02d}"


def pos(m):
    f = min(max(m / 3.0, 0.0), 1.0)
    return [round(SUB[0] + (TGT[0] - SUB[0]) * f, 4), round(SUB[1] + (TGT[1] - SUB[1]) * f, 4)]


DET = W("p28", "detonates")
L0 = S("p25") + 3.5
ANCH = [(L0, 0.0), (S("p26"), 1.0), (S("p27"), 2.0), (DET, 3.0)]


def mm(t):
    if t <= ANCH[0][0]:
        return 0.0
    for (t0, m0), (t1, m1) in zip(ANCH, ANCH[1:]):
        if t <= t1:
            return m0 + (m1 - m0) * (t - t0) / (t1 - t0)
    return 3.0


def clk(t):
    return clock(mm(t))


def missile(a, b, m_a=None, m_b=None, t_on=0.0):
    ma = mm(a) if m_a is None else m_a
    mb = mm(b) if m_b is None else m_b
    return [{"path": [pos(ma), pos(mb)], "t0": 0, "t1": round(b - a, 2), "kind": "pla", "color": RED, "label": "Iskander-M", "t": t_on, "wake": True}]


PATH = {"from": SUB, "to": TGT, "color": RED, "dashed": True, "t0": 0, "t1": 1}
LAUNCH = {"at": SUB, "label": "Launch: Belgorod region (simulated)", "color": RED, "kind": "base", "size": 5, "t": 0.2}
TARGET = {"at": TGT, "label": "Target: open farmland (simulated)", "color": RED, "kind": "target", "size": 7, "t": 1.5}
SRC_E = "Effects: Glasstone and Dolan scaling calibrated to NUKEMAP (scenario engine)"

# ================================================================== Cold open [SIMULATION]
T1 = 5.0
add(id="open-launch", type="globe", start=0, end=T1, tag="SIMULATION", clock="09:20", clockLabel="DAY 1 · KYIV TIME",
    camera=[{"t": 0, "lat": 50.6, "lon": 35.5, "scale": 1700}, {"t": T1, "lat": 50.0, "lon": 36.9, "scale": 3600}], sun=SUN, highlight=[HL_UKR, HL_RUS],
    markers=[{"at": SUB, "label": "Launch: Belgorod region (simulated)", "color": "#FF8A8A", "kind": "base", "size": 4, "t": 0.4}, {"at": TGT, "label": "Open farmland", "color": "#FF8A8A", "kind": "target", "size": 3, "t": 3.2}],
    arcs=[{"from": SUB, "to": TGT, "t0": 1.0, "t1": 5.4, "color": RED, "loft": 0.08}])
add(id="open-flight", type="region", start=T1, end=S("p03"), tag="SIMULATION", clock="T+00:40", clockLabel="SINCE LAUNCH", caption="About 140 km south-east of the launcher",
    view={"center": [36.9, 50.0], "widthKm": 480}, zoomTo={"center": [36.95, 49.95], "widthKm": 270}, highlight=[HL_UKR, HL_RUS],
    cities=[dict(LAUNCH, t=0.2), dict(TARGET, t=2.8), {"at": KHARKIV, "label": "Kharkiv", "kind": "dot", "t": 7.0}], lines=[PATH],
    ships=missile(T1, S("p03"), m_a=0.15, m_b=0.75, t_on=0.3))
tN = W("p03", "Nagasaki")
add(id="open-field", type="city", start=S("p03"), end=tN, tag="SIMULATION", clock="09:23", clockLabel="IN THREE MINUTES", city="kharkiv-farmland",
    view={"center": TGT, "widthKm": 40}, zoomTo={"center": TGT, "widthKm": 9}, gz=TGT, rings=[], caption="No mapped building within 5 km of this point.", source="OpenStreetMap",
    labels=[{"at": TGT, "text": "That field", "color": WHITE, "t": 0.6}, {"at": [37.80357, 49.46679], "text": "Lozova", "color": DIM, "t": 1.0},
            {"at": [37.87554, 49.59562], "text": "Tabaivka", "color": DIM, "t": 1.6}, {"at": [37.71276, 49.50396], "text": "Zahryzove", "color": DIM, "t": 2.2},
            {"at": [37.894, 49.5425], "text": "Berestove", "color": DIM, "t": 2.8}, {"at": [37.7196, 49.5206], "text": "Kruhliakivka", "color": DIM, "t": 3.4}, {"at": [37.92, 49.57443], "text": "Krokhmalne", "color": DIM, "t": 4.0}])
add(id="open-nagasaki", type="globe", start=tN, end=S("p04"), tag="REAL HISTORY", clock="1945", clockLabel="NAGASAKI", source="US DOE OSTI",
    camera=[{"t": 0, "lat": 31, "lon": 126, "scale": 1500}, {"t": S("p04") - tN, "lat": 32.7, "lon": 129.8, "scale": 3200}], sun={"lat": 10, "lon": 100}, highlight=[{"iso": JPN, "color": AMBER}],
    markers=[{"at": NAGASAKI, "label": "Nagasaki, 1945: the last time", "color": AMBER, "kind": "target", "t": 0.4}])
add(id="open-banner", type="region", start=S("p04"), end=S("p05"), tag="SIMULATION", clock="T+01:30", clockLabel="SINCE LAUNCH",
    view={"center": [35.5, 50.3], "widthKm": 1500}, zoomTo={"center": [36.9, 50.0], "widthKm": 380}, highlight=[HL_UKR, HL_RUS],
    cities=[dict(LAUNCH, t=0.2), dict(TARGET, t=1.2)], lines=[PATH], ships=missile(S("p04"), S("p05"), m_a=0.5, m_b=1.6, t_on=0.1))
tNb = W("p05", "Nobody")
add(id="open-arc", type="globe", start=S("p05"), end=tNb, tag="SIMULATION", clock="T+01:45", clockLabel="SINCE LAUNCH", caption="Past the top of its arc",
    camera=[{"t": 0, "lat": 51, "lon": 38, "scale": 1000}, {"t": tNb - S("p05"), "lat": 49.9, "lon": 37, "scale": 2600}], sun=SUN, highlight=[HL_UKR, HL_RUS],
    markers=[{"at": TGT, "label": "Open farmland", "color": "#FF8A8A", "kind": "target", "size": 3, "t": 0.3}], arcs=[{"from": SUB, "to": TGT, "t0": -5, "t1": 6, "color": RED, "loft": 0.3}])
add(id="open-ground", type="city", start=tNb, end=S("p06"), tag="SIMULATION", clock="T+02:00", clockLabel="ON THE GROUND", city="kharkiv-farmland",
    view={"center": TGT, "widthKm": 7}, zoomTo={"center": TGT, "widthKm": 4.2}, gz=TGT, rings=[],
    labels=[{"at": TGT, "text": "Nobody has been told", "color": WHITE, "t": 0.5}])

# ================================================================== Chapter 01 what Russia really has [REAL DATA]
add(id="c1-card", type="chapter", start=S("p06"), end=S("p06") + 3.5, tag="REAL DATA", kicker="CHAPTER 01", title="What Russia really has")
a = S("p06") + 3.5
add(id="c1-4400", type="number", start=a, end=a + 3.8, tag="REAL DATA", value="ABOUT 4,400", countTo=4400, prefix="ABOUT ", label="Russian nuclear warheads", sub="Federation of American Scientists, March 2026", color=AMBER, source="Federation of American Scientists, Status of World Nuclear Forces")
b = a + 3.8
add(id="c1-bases", type="region", start=b, end=S("p07"), tag="REAL DATA", caption="About 1,800 deployed strategic: land, submarines, bombers. Locations approximate.", source="Federation of American Scientists",
    view={"center": [42, 59], "widthKm": 4200}, zoomTo={"center": [40, 59], "widthKm": 3300}, highlight=[HL_RUS],
    cities=[{"at": [35.8, 54.0], "label": "Land-based missiles", "color": AMBER, "kind": "dot", "t": W("p06", "on") - b + 0.3}, {"at": [33.4, 68.8], "label": "Submarines", "color": AMBER, "kind": "dot", "t": W("p06", "submarines") - b},
            {"at": [46.2, 51.5], "label": "Bombers", "color": AMBER, "kind": "dot", "t": W("p06", "bombers") - b}, {"at": MOSCOW, "label": "Moscow", "kind": "dot", "t": 0.5}])
tA = W("p07", "Aerial")
tNs = W("p07", "Non-strategic")
add(id="c1-ns", type="globe", start=S("p07"), end=tNs, tag="REAL DATA", caption="Separate from those: the ones this episode is about.", source="Federation of American Scientists",
    camera=[{"t": 0, "lat": 56, "lon": 45, "scale": 650}, {"t": tNs - S("p07"), "lat": 52, "lon": 38, "scale": 1100}], sun={"lat": 10, "lon": 60}, highlight=[HL_RUS],
    markers=[{"at": MOSCOW, "label": "Non-strategic (tactical) warheads", "color": RED, "kind": "dot", "t": 1.0}])
add(id="c1-tactical", type="number", start=tNs, end=S("p08"), tag="REAL DATA", value="1,000 TO 2,000", label="non-strategic (tactical) warheads, US estimates", sub="aerial bombs, missile warheads, artillery shells", color=RED, source="US government estimates via Federation of American Scientists")
add(id="c1-noyield", type="stamp", start=S("p08"), end=S("p09"), tag="REAL DATA", text="NO PUBLISHED YIELD", line="for Russian tactical warheads. We come back to this.", color=AMBER, source="Research: no open source gives a figure")
add(id="c1-range", type="region", start=S("p09"), end=S("p10"), tag="REAL DATA", clock="", source="CSIS Missile Threat",
    caption="Iskander-M: range 400 to 500 km. Fired at Ukraine conventionally throughout this war.",
    view={"center": [34, 50], "widthKm": 1700}, zoomTo={"center": [34, 50], "widthKm": 2400}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": SUB, "label": "Belgorod region", "color": RED, "kind": "base", "size": 5, "t": 0.5}, {"at": KHARKIV, "label": "Kharkiv", "kind": "dot", "t": W("p09", "conventionally") - S("p09")}, {"at": KYIV, "label": "Kyiv", "kind": "dot", "t": 3}],
    rings=[{"at": SUB, "km": 400, "color": AMBER, "label": "400 km", "t": W("p09", "four") - S("p09")}, {"at": SUB, "km": 500, "color": RED, "label": "500 km", "t": W("p09", "five") - S("p09")}])
add(id="c1-treaty", type="globe", start=S("p10"), end=S("p11"), tag="REAL DATA", clock="FEB 2026", clockLabel="LAST ARMS TREATY EXPIRES", source="Arms Control Association",
    caption="For the first time in decades, neither side has a cap.",
    camera=[{"t": 0, "lat": 52, "lon": 40, "scale": 650}, {"t": 7, "lat": 50, "lon": -10, "scale": 750}, {"t": 13, "lat": 45, "lon": -70, "scale": 800}], sun={"lat": 10, "lon": 20},
    highlight=[HL_RUS, {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}],
    markers=[{"at": MOSCOW, "label": "Russia: no cap", "color": AMBER, "kind": "dot", "t": 0.5}, {"at": WASH, "label": "United States: no cap", "color": TEAL, "kind": "dot", "t": 8}])

# ================================================================== Chapter 02 how close it has come [REAL HISTORY]
add(id="c2-card", type="chapter", start=S("p11"), end=S("p11") + 3.5, tag="REAL HISTORY", kicker="CHAPTER 02", title="How close it has come")
a = S("p11") + 3.5
tNg = W("p11", "Nagasaki")
add(id="c2-japan", type="globe", start=a, end=S("p12"), tag="REAL HISTORY", clock="1945", clockLabel="ONLY TWO, EVER", source="US DOE OSTI",
    camera=[{"t": 0, "lat": 36, "lon": 132, "scale": 2200}, {"t": S("p12") - a, "lat": 33.5, "lon": 130.5, "scale": 3000}], sun={"lat": 10, "lon": 100}, highlight=[{"iso": JPN, "color": AMBER}],
    markers=[{"at": HIROSHIMA, "label": "Hiroshima · about 15 kt", "color": AMBER, "kind": "target", "t": W("p11", "Hiroshima") - a}, {"at": NAGASAKI, "label": "Nagasaki · about 21 kt", "color": RED, "kind": "target", "t": tNg - a}])
add(id="c2-cuba", type="region", start=S("p12"), end=S("p13"), tag="REAL HISTORY", clock="1962", clockLabel="CUBAN MISSILE CRISIS", source="National Security Archive; White House remarks, 2022",
    caption="Biden, sixty years later: the yardstick for the danger in Ukraine.",
    view={"center": [-74, 27], "widthKm": 3200}, zoomTo={"center": [-60, 36], "widthKm": 5200}, highlight=[{"iso": CUB, "color": RED, "fill": "rgba(255,59,59,0.10)"}, {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}],
    cities=[{"at": HAVANA, "label": "Cuba, 1962", "color": RED, "kind": "dot", "t": 0.5}, {"at": WASH, "label": "Washington", "kind": "dot", "t": 4}])
add(id="c2-putin", type="region", start=S("p13"), end=W("p13", "Two"), tag="REAL HISTORY", clock="SEPT 2022", clockLabel="PUTIN", source="Kremlin address, September 2022; Reuters",
    caption="\"All the means at its disposal.\" \"It's not a bluff.\"",
    view={"center": [38, 52], "widthKm": 2600}, zoomTo={"center": [33, 50], "widthKm": 1500}, highlight=[HL_RUS, HL_UKR],
    cities=[{"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 0.5}, {"at": KYIV, "label": "Kyiv", "kind": "dot", "t": 3}])
add(id="c2-armageddon", type="globe", start=W("p13", "Two"), end=W("p13", "He"), tag="REAL HISTORY", clock="OCT 2022", clockLabel="BIDEN", source="White House remarks; Reuters",
    caption="\"Armageddon\": the first time since the Cuban Missile Crisis.",
    camera=[{"t": 0, "lat": 42, "lon": -50, "scale": 700}, {"t": 7.4, "lat": 40, "lon": -78, "scale": 1300}], sun={"lat": 10, "lon": 20}, highlight=[{"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}, {"iso": CUB, "color": RED}],
    markers=[{"at": WASH, "label": "Washington", "color": TEAL, "kind": "dot", "t": 0.5}, {"at": HAVANA, "label": "Cuba, 1962", "color": RED, "kind": "dot", "t": 3}])
add(id="c2-whitehouse", type="region", start=W("p13", "He"), end=S("p15"), tag="REAL HISTORY", clock="OCT 2022", clockLabel="WASHINGTON", source="White House briefing; Reuters",
    view={"center": [-77.04, 38.9], "widthKm": 60}, zoomTo={"center": [-77.04, 38.9], "widthKm": 18},
    cities=[{"at": [-77.0365, 38.8977], "label": "White House: no sign of imminent use", "color": TEAL, "kind": "base", "size": 6, "t": W("p14", "The") - W("p13", "He")}],
    labels=[{"at": [-77.0, 38.94], "text": "\"No such thing as easily using a tactical nuclear weapon\"", "color": WHITE, "t": 0.4}])
tIn2 = W("p15", "In", 2)
add(id="c2-phone", type="globe", start=S("p15"), end=tIn2, tag="REAL HISTORY", clock="OCT 2022", clockLabel="DEFENCE CHIEFS", source="Reuters; Pentagon readouts",
    caption="American and Russian defence chiefs speak by phone.",
    camera=[{"t": 0, "lat": 48, "lon": -35, "scale": 650}, {"t": tIn2 - S("p15"), "lat": 48, "lon": 0, "scale": 800}], sun={"lat": 10, "lon": 20}, highlight=[HL_RUS, {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}],
    markers=[{"at": WASH, "label": "Washington", "color": TEAL, "kind": "dot", "t": 0.5}, {"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 2}],
    arcs=[{"from": WASH, "to": MOSCOW, "t0": 3.0, "t1": 7.0, "color": TEAL, "loft": 0.15}])
tDays = W("p15", "Days")
add(id="c2-reports", type="region", start=tIn2, end=tDays, tag="REAL HISTORY", clock="NOV 2022", clockLabel="NEWS REPORTS", source="Reuters; New York Times reporting, November 2022",
    caption="Senior officials reportedly discussed tactical use. No evidence any warhead moved.",
    view={"center": [38, 54], "widthKm": 1900}, zoomTo={"center": [36, 52], "widthKm": 1100}, highlight=[HL_RUS, HL_UKR],
    cities=[{"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 0.5}, {"at": KYIV, "label": "Kyiv", "kind": "dot", "t": 2.5}])
add(id="c2-ankara", type="region", start=tDays, end=S("p16"), tag="REAL HISTORY", clock="NOV 2022", clockLabel="ANKARA", source="Reuters; Associated Press",
    caption="The CIA director meets Russia's foreign intelligence chief to warn against it.",
    view={"center": [32, 44], "widthKm": 3200}, zoomTo={"center": [32.5, 41], "widthKm": 1300}, highlight=[HL_RUS, {"iso": "792", "color": TEAL, "fill": "rgba(62,214,200,0.08)"}],
    cities=[{"at": ANKARA, "label": "Ankara", "color": TEAL, "kind": "target", "size": 6, "t": 0.8}, {"at": MOSCOW, "label": "Moscow", "kind": "dot", "t": 2}])
tIt = W("p16", "It")
add(id="c2-doctrine", type="region", start=S("p16"), end=S("p17"), tag="REAL HISTORY", clock="NOV 2024", clockLabel="DOCTRINE REWRITTEN", source="Russian presidential decree, 2024; Arms Control Association",
    caption="Nuclear use may be considered after a critical threat to Russia or Belarus. It names no target and no moment.",
    view={"center": [38, 56], "widthKm": 4200}, zoomTo={"center": [32, 54], "widthKm": 1900}, highlight=[HL_RUS, {"iso": BELARUS, "color": RED, "fill": "rgba(255,59,59,0.12)"}],
    cities=[{"at": MOSCOW, "label": "Russia", "color": AMBER, "kind": "dot", "t": 0.5}, {"at": MINSK, "label": "Belarus", "color": RED, "kind": "dot", "t": 3.5}])
tI2 = W("p17", "In", 2)
add(id="c2-belarus", type="region", start=S("p17"), end=tI2, tag="REAL HISTORY", clock="2026", clockLabel="NUCLEAR DRILLS", source="Russian Defence Ministry statements; Reuters",
    caption="A three-day nuclear exercise with Belarus. Tactical weapons were part of the drills.",
    view={"center": [30, 55], "widthKm": 2200}, zoomTo={"center": [28, 54], "widthKm": 1200}, highlight=[HL_RUS, {"iso": BELARUS, "color": RED, "fill": "rgba(255,59,59,0.12)"}],
    cities=[{"at": MINSK, "label": "Belarus", "color": RED, "kind": "base", "size": 6, "t": 0.8}, {"at": MOSCOW, "label": "Russia", "color": AMBER, "kind": "dot", "t": 2.5}])
tOr = W("p17", "Russia", 3)
add(id="c2-medvedev", type="globe", start=tI2, end=tOr, tag="REAL HISTORY", clock="FEB 2026", clockLabel="MEDVEDEV", source="TASS; Reuters. Ukraine and Britain deny any such plan.",
    caption="Britain and France giving Ukraine nuclear technology? Ukraine and Britain deny any such plan.",
    camera=[{"t": 0, "lat": 52, "lon": 25, "scale": 900}, {"t": tOr - tI2, "lat": 50, "lon": 8, "scale": 1500}], sun={"lat": 10, "lon": 20}, highlight=[HL_RUS, {"iso": GBR, "color": TEAL}, {"iso": FRA, "color": TEAL}, HL_UKR],
    markers=[{"at": MOSCOW, "label": "Medvedev: non-strategic weapons", "color": AMBER, "kind": "dot", "t": 1}, {"at": LONDON, "label": "Britain", "color": TEAL, "kind": "dot", "t": 5}, {"at": PARIS, "label": "France", "color": TEAL, "kind": "dot", "t": 6}])
add(id="c2-oreshnik", type="region", start=tOr, end=S("p18"), tag="REAL HISTORY", clock="2026", clockLabel="ORESHNIK", source="Ukrainian Air Force statements; Reuters",
    caption="Oreshnik, nuclear-capable, fired at Ukraine without a nuclear warhead.",
    view={"center": [32, 49.5], "widthKm": 1500}, zoomTo={"center": [30, 49.5], "widthKm": 900}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": KYIV, "label": "Ukrainian territory", "color": RED, "kind": "target", "size": 6, "t": 0.8}, {"at": MOSCOW, "label": "Russia", "color": AMBER, "kind": "dot", "t": 2.5}])
tOne = W("p18", "One")
add(id="c2-oneweapon", type="region", start=S("p18"), end=S("p19"), tag="REAL HISTORY", clock="", caption="\"Escalate to de-escalate\": one small strike to make the other side stop. A commentators' idea, not a published Russian plan.",
    view={"center": [34, 50], "widthKm": 1500}, zoomTo={"center": TGT, "widthKm": 200}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": TGT, "label": "One strike", "color": RED, "kind": "target", "size": 7, "t": 1.0}], rings=[{"at": TGT, "km": 20, "color": RED, "t": 2.5}])
add(id="c2-flight", type="region", start=S("p19"), end=S("p20"), tag="SIMULATION", clock="T+00:00", clockLabel="IF IT LAUNCHED", caption="About 140 km in about three minutes.", source="Scenario engine",
    view={"center": [36.9, 50.0], "widthKm": 420}, zoomTo={"center": [36.9, 50.0], "widthKm": 300}, highlight=[HL_UKR, HL_RUS],
    cities=[dict(LAUNCH, label="Belgorod region (simulated)"), dict(TARGET, label="Simulated target", t=1.0)], lines=[PATH],
    ships=[{"path": [pos(0), pos(3)], "t0": 1.5, "t1": 6.5, "kind": "pla", "color": RED, "label": "Iskander-M", "t": 1.2, "wake": True}])

# ================================================================== Chapter 03 the trigger [SIMULATION]
add(id="c3-card", type="chapter", start=S("p20"), end=S("p21"), tag="SIMULATION", kicker="CHAPTER 03", title="The trigger")
tTh = W("p21", "That")
add(id="c3-sector", type="region", start=S("p21"), end=tTh, tag="SIMULATION", clock="BEFORE DAY 1", clockLabel="OUR ASSUMPTION",
    caption="A counter-offensive threatens a Russian-held sector. Moscow calls it a critical threat to territorial integrity.",
    view={"center": [37.2, 49.9], "widthKm": 900}, zoomTo={"center": [37.6, 49.6], "widthKm": 330}, highlight=[HL_UKR, HL_RUS],
    zones=[{"points": [[36.9, 49.2], [38.0, 49.25], [38.15, 49.85], [37.2, 49.95]], "label": "Russian-held sector (invented)", "color": RED, "t": 3.0, "pulse": True}],
    lines=[{"from": [36.2, 49.1], "to": [37.1, 49.5], "label": "Counter-offensive (simulated)", "color": TEAL, "t0": 1.0, "t1": 5.0}])
add(id="c3-choose", type="text", start=tTh, end=S("p22"), tag="SIMULATION", lines=["The doctrine does not say what Russia would do.", "We are choosing."])
add(id="c3-one", type="number", start=S("p22"), end=S("p23"), tag="SIMULATION", value="ONE", label="Iskander-M · one warhead · one target", sub="our simulation choice", color=RED)
tNo = W("p23", "No")
add(id="c3-farm", type="city", start=S("p23"), end=tNo, tag="SIMULATION", caption="An invented staging area in open farmland, eastern Kharkiv region.", source="Scenario assumption; OpenStreetMap", city="kharkiv-farmland",
    view={"center": TGT, "widthKm": 60}, zoomTo={"center": TGT, "widthKm": 14}, gz=TGT, rings=[],
    labels=[{"at": TGT, "text": "Staging area (simulated)", "color": WHITE, "t": 1.0}, {"at": [37.80357, 49.46679], "text": "Lozova", "color": DIM, "t": 3.0}, {"at": [37.7196, 49.5206], "text": "Kruhliakivka", "color": DIM, "t": 4.5}])
add(id="c3-zap", type="region", start=tNo, end=S("p24"), tag="SIMULATION", caption="No city. Not near the Zaporizhzhia plant. The location is simulated.", source="Scenario assumption",
    view={"center": [36.0, 48.6], "widthKm": 760}, zoomTo={"center": [36.4, 49.0], "widthKm": 520}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": TGT, "label": "Simulated target", "color": RED, "kind": "target", "size": 7, "t": 0.6}, {"at": ZNPP, "label": "Zaporizhzhia plant", "color": TEAL, "kind": "base", "size": 6, "t": 3.0}, {"at": KHARKIV, "label": "Kharkiv", "kind": "dot", "t": 1.6}],
    lines=[{"from": TGT, "to": ZNPP, "color": TEAL, "dashed": True, "t0": 3.4, "t1": 5.2}])
tSo = W("p24", "So")
add(id="c3-15kt", type="number", start=S("p24"), end=tSo, tag="SIMULATION", value="NO PUBLISHED YIELD", label="for Russian tactical warheads", sub="research found none", color=AMBER, source="Research notes, section C")
add(id="c3-hiro", type="bars", start=tSo, end=S("p25"), tag="SIMULATION", title="We assume 15 kilotons, the same as Hiroshima", sub="kilotons · a simulation choice, not a fact about any Russian warhead", source="US DOE OSTI (Hiroshima); simulation choice (ours)",
    bars=[{"label": "Hiroshima, 1945", "value": 15, "display": "about 15 kt", "color": AMBER}, {"label": "Our warhead", "value": 15, "display": "15 kt", "color": RED}])

# ================================================================== Chapter 04 minute by minute [SIMULATION]
add(id="c4-card", type="chapter", start=S("p25"), end=L0, tag="SIMULATION", kicker="CHAPTER 04", title="Minute by minute")
add(id="c4-m0", type="region", start=L0, end=S("p26"), tag="SIMULATION", clock="T+00:00", clockLabel="MINUTE ZERO", caption="Minute zero. A ballistic missile climbs out of Belgorod region.",
    view={"center": [36.7, 50.3], "widthKm": 230}, zoomTo={"center": [36.9, 50.0], "widthKm": 290}, highlight=[HL_UKR, HL_RUS],
    cities=[dict(LAUNCH, t=0.2), dict(TARGET, t=2.0)], lines=[PATH], ships=missile(L0, S("p26"), t_on=0.3))
add(id="c4-m1", type="radar", start=S("p26"), end=S("p27"), tag="SIMULATION", title="Minute one · air defence",
    lines=[{"k": "tracks", "v": "one"}, {"k": "warning", "v": "seconds"}, {"k": "type", "v": "looks like any Iskander"}], tracks=1, big="SECONDS", bigColor=RED)
add(id="c4-m2", type="region", start=S("p27"), end=DET, tag="SIMULATION", clock="T+02:00", clockLabel="MINUTE TWO", caption="It begins to fall. Below: a staging area of vehicles and tents.",
    view={"center": [37.1, 49.8], "widthKm": 130}, zoomTo={"center": TGT, "widthKm": 34}, highlight=[HL_UKR],
    cities=[dict(TARGET, label="Staging area (simulated)", t=0.5)], lines=[PATH], ships=missile(S("p27"), DET, t_on=0.0))
fl = round(0.1, 2)
tThen1, tThen2 = W("p29", "Then", 1), W("p29", "Then", 2)
RINGS = [{"km": FX["fireball_km"], "label": "Fireball", "angle": 330, "color": WHITE}, {"km": FX["psi20_km"], "label": "20 psi", "angle": 150, "color": ORANGE}, {"km": FX["psi5_km"], "label": "5 psi", "angle": 60, "color": RED},
         {"km": FX["thermal3_km"], "label": "Third-degree burns", "angle": 230, "color": AMBER}, {"km": FX["psi1_km"], "label": "1 psi", "angle": 20, "color": TEAL}]
LEGEND = [{"text": f"Fireball {FX['fireball_km'] * 1000:.0f} m", "color": WHITE}, {"text": f"20 psi {FX['psi20_km'] * 1000:.0f} m", "color": ORANGE}, {"text": f"5 psi {FX['psi5_km']:.2f} km", "color": RED},
          {"text": f"Burns {FX['thermal3_km']:.1f} km", "color": AMBER}, {"text": f"1 psi {FX['psi1_km']:.1f} km", "color": TEAL}]
CITY_LABELS = [{"at": [TGT[0] + 0.0, TGT[1] + 0.0045], "text": "Staging area (simulated)", "color": WHITE}]
LABELS_BY_N = {1: [0], 2: [0], 3: [0], 4: [0], 5: [0]}
HIDE = []
CL = clock(ST["impact_min"])


def rings_upto(n, new_t):
    return [dict(r, t=(-30 if i < n - 1 else new_t)) for i, r in enumerate(RINGS[:n])]


def city_shot(sid, a, b, n, w0, w1, flash=None, **kw):
    d = dict(id=sid, type="city", start=a, end=b, tag="SIMULATION", clock=CL, clockLabel="MINUTE THREE · BURST", source=SRC_E, city="kharkiv-farmland",
             view={"center": TGT, "widthKm": w0}, zoomTo={"center": TGT, "widthKm": w1}, gz=TGT,
             rings=rings_upto(n, 0.6 if flash is None else flash + 0.1), labels=[CITY_LABELS[i] for i in LABELS_BY_N[n]] + HIDE, legend=LEGEND[:n], flashT=-30 if flash is None else flash)
    if flash is not None:
        d["labels"] = [CITY_LABELS[0]] + HIDE
    d.update(kw)
    add(**d)


city_shot("c4-flash", DET, tThen2, 1, 4.5, 3.6, flash=fl, caption="Minute three. An air burst. A flash brighter than the sun, then a fireball.", legend=[])
add(id="c4-shock", type="city", start=tThen2, end=S("p30"), tag="SIMULATION", clock=CL, clockLabel="MINUTE THREE · SHOCK WAVE", source=SRC_E, city="kharkiv-farmland",
    view={"center": TGT, "widthKm": 5}, zoomTo={"center": TGT, "widthKm": 14}, gz=TGT, flashT=-30,
    rings=[dict(RINGS[0], t=-30), {"km": FX["psi5_km"], "label": "Shock wave", "color": ORANGE, "angle": 45, "t": 0.2}], labels=[CITY_LABELS[0]] + HIDE, legend=[])
add(id="c4-m4", type="globe", start=S("p30"), end=S("p31"), tag="SIMULATION", clock="T+04:00", clockLabel="MINUTE FOUR", caption="Satellites register the flash within seconds. Monitors in neighbouring countries log numbers.",
    camera=[{"t": 0, "lat": 48, "lon": 37, "scale": 2400}, {"t": 6, "lat": 49, "lon": 28, "scale": 1100}, {"t": 13.8, "lat": 50, "lon": 22, "scale": 1000}], sun=SUN,
    highlight=[HL_UKR] + [{"iso": i, "color": BLUE, "fill": "rgba(110,168,255,0.12)"} for i in (POLAND, ROMANIA, SLOVAKIA, HUNGARY, MOLDOVA)],
    markers=[{"at": TGT, "label": "Detonation", "color": RED, "kind": "target", "t": 0.3}, {"at": [21.01, 52.23], "label": "Warsaw", "color": BLUE, "kind": "ring", "t": 7}, {"at": [26.1, 44.43], "label": "Bucharest", "color": BLUE, "kind": "ring", "t": 8.5}],
    flashes=[{"at": TGT, "t": 0.4, "radius": 90, "color": WHITE}])
add(id="c4-m10", type="region", start=S("p31"), end=S("p32"), tag="SIMULATION", clock="T+10:00", clockLabel="MINUTE TEN", source="",
    view={"center": [34, 51.5], "widthKm": 2200}, zoomTo={"center": [34, 51.5], "widthKm": 1500}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": TGT, "label": "Detonation site", "color": RED, "kind": "target", "size": 6, "t": 0.3}, {"at": KYIV, "label": "Kyiv", "kind": "dot", "t": 0.6}, {"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 0.6}],
    labels=[{"at": [26, 52.6], "text": "Ukraine's air force: a nuclear detonation", "color": TEAL, "t": 1.2}, {"at": [37, 57.2], "text": "Russia's defence ministry: nothing, or something else", "color": AMBER, "t": W("p31", "Russia's") - S("p31")}])
shots[-1].pop("source")

# ================================================================== Chapter 05 one warhead, ring by ring [SIMULATION]
add(id="c5-card", type="chapter", start=S("p32"), end=S("p32") + 3.5, tag="SIMULATION", kicker="CHAPTER 05", title="One warhead, ring by ring")
city_shot("c5-fireball", S("p32") + 3.5, S("p34"), 1, 5.0, 4.0, flash=None, rings=[dict(RINGS[0], t=S("p33") - S("p32") - 3.5 + 0.1)])
city_shot("c5-20psi", S("p34"), S("p35"), 2, 3.4, 4.0)
city_shot("c5-5psi", S("p35"), W("p35", "That"), 3, 9, 14)
add(id="c5-area", type="number", start=W("p35", "That"), end=S("p36"), tag="SIMULATION", value="8.8 KM²", countTo=8.8, decimals=1, suffix=" KM²", label="inside the 5 psi ring", sub="most ordinary buildings collapse or are badly damaged", color=RED, source="Scenario engine")
city_shot("c5-burns", S("p36"), S("p37"), 4, 12, 17)
city_shot("c5-1psi", S("p37"), S("p38"), 5, 18, 22)
cs = S("p38")
add(id="c5-fallout", type="region", start=cs, end=S("p39"), tag="SIMULATION", clock="DAY 1", clockLabel="AFTER THE BURST", source=SRC_E,
    caption="An air burst: little local fallout. No dose, no contour: the engine supplies none.",
    view={"center": TGT, "widthKm": 36}, zoomTo={"center": [37.6, 49.5], "widthKm": 130}, highlight=[HL_UKR],
    cities=[{"at": TGT, "label": "Air burst", "color": RED, "kind": "target", "size": 6, "t": 0.4}, {"at": KHARKIV, "label": "Kharkiv", "kind": "dot", "t": 9}],
    rings=[{"at": TGT, "km": FX["psi1_km"], "color": TEAL, "t": 1.0}],
    plume={"at": TGT, "bearing": 90, "lengthKm": 40, "widthKm": 6, "t0": W("p38", "We") - cs, "t1": W("p38", "We") - cs + 5, "color": AMBER, "label": "thin cloud drifts east (our wind choice)"},
    labels=[{"at": [37.9, 49.62], "text": "toward the Russian-held side", "color": AMBER, "t": W("p38", "toward") - cs}])
add(id="c5-out", type="region", start=S("p39"), end=S("p41"), tag="SIMULATION", clock="DAY 1", clockLabel="AFTER THE BURST", source=SRC_E,
    caption="No published study covers this strike, so we give no death toll. Eight point eight square kilometres of farmland.",
    view={"center": TGT, "widthKm": 40}, zoomTo={"center": [34, 50], "widthKm": 1500}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": TGT, "label": "One warhead", "color": RED, "kind": "target", "size": 7, "t": 1.0}], rings=[{"at": TGT, "km": FX["psi5_km"], "color": RED, "t": 0.6}, {"at": TGT, "km": FX["psi1_km"], "color": TEAL, "t": 1.0}])

# ================================================================== Chapter 06 the day after [SIMULATION]
add(id="c6-card", type="chapter", start=S("p41"), end=S("p41") + 3.5, tag="SIMULATION", kicker="CHAPTER 06", title="The day after")
a = S("p41") + 3.5
tIn = W("p41", "In", 2)
tNow = W("p41", "Now")
add(id="c6-un", type="globe", start=a, end=S("p42"), tag="SIMULATION", clock="DAY 1", clockLabel="THE FIRST HOURS", caption="We assume emergency sessions at the UN Security Council, the G7 and NATO.",
    camera=[{"t": 0, "lat": 45, "lon": -45, "scale": 650}, {"t": 8, "lat": 46, "lon": -15, "scale": 800}, {"t": S("p42") - a, "lat": 48, "lon": 30, "scale": 1300}], sun={"lat": 10, "lon": 20},
    highlight=[HL_RUS, {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}],
    markers=[{"at": NYC, "label": "UN Security Council", "color": TEAL, "kind": "dot", "t": 0.3}, {"at": BRUSSELS, "label": "NATO", "color": TEAL, "kind": "dot", "t": W("p41", "NATO") - a},
             {"at": WASH, "label": "Washington, 2022: \"decisive\" consequences", "color": TEAL, "kind": "dot", "t": W("p41", "Washington") - a}, {"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": W("p41", "Moscow") - a}],
    arcs=[{"from": WASH, "to": MOSCOW, "t0": W("p41", "Washington") - a, "t1": W("p41", "Washington") - a + 5, "color": TEAL, "loft": 0.15}])
add(id="c6-nato", type="region", start=S("p42"), end=S("p43"), tag="SIMULATION", clock="DAY 1", clockLabel="ARTICLE 5", caption="Ukraine is not a NATO member. Article 5 would not be triggered.", source="NATO; North Atlantic Treaty",
    view={"center": [26, 50.5], "widthKm": 2500}, zoomTo={"center": [26, 50.5], "widthKm": 1900}, highlight=[HL_UKR, HL_RUS] + NATO_EAST,
    countryLabels=[{"iso": UKR, "text": "UKRAINE: NOT A MEMBER", "color": TEAL}, {"iso": POLAND, "text": "NATO", "color": BLUE}, {"iso": ROMANIA, "text": "NATO", "color": BLUE}, {"iso": RUSSIA, "text": "RUSSIA", "color": AMBER}],
    cities=[{"at": TGT, "label": "", "color": RED, "kind": "target", "size": 6, "t": 0.5}])
add(id="c6-channels", type="globe", start=S("p43"), end=S("p44"), tag="SIMULATION", clock="DAY 1", clockLabel="CHANNELS REOPEN", caption="Defence chiefs phone. Intelligence heads meet. We assume they do, as in 2022.",
    camera=[{"t": 0, "lat": 46, "lon": -40, "scale": 700}, {"t": 10, "lat": 46, "lon": 20, "scale": 1000}], sun={"lat": 10, "lon": 20}, highlight=[HL_RUS, {"iso": USA, "color": TEAL, "fill": "rgba(62,214,200,0.06)"}],
    markers=[{"at": WASH, "label": "Washington", "color": TEAL, "kind": "dot", "t": 0.4}, {"at": MOSCOW, "label": "Moscow", "color": AMBER, "kind": "dot", "t": 1.0}, {"at": ANKARA, "label": "Ankara", "color": TEAL, "kind": "ring", "t": 6}],
    arcs=[{"from": WASH, "to": MOSCOW, "t0": 1.5, "t1": 5.5, "color": TEAL, "loft": 0.15}, {"from": WASH, "to": ANKARA, "t0": 5.0, "t1": 8.5, "color": TEAL, "loft": 0.15}])
add(id="c6-radiation", type="region", start=S("p44"), end=S("p45"), tag="SIMULATION", clock="DAY 1", clockLabel="RADIATION MONITORS",
    caption="Modelling expectation for an air burst: readings at background outside the immediate area. An expectation, not a measurement.",
    view={"center": [28, 49.5], "widthKm": 1700}, zoomTo={"center": [24, 49.5], "widthKm": 1500}, highlight=[HL_UKR] + [{"iso": i, "color": TEAL, "fill": "rgba(62,214,200,0.10)"} for i in (POLAND, ROMANIA, SLOVAKIA, HUNGARY, MOLDOVA)],
    cities=[{"at": TGT, "label": "Detonation site", "color": RED, "kind": "target", "size": 6, "t": 0.4}, {"at": [21.01, 52.23], "label": "Warsaw", "color": BLUE, "kind": "ring", "t": 3}, {"at": [26.1, 44.43], "label": "Bucharest", "color": BLUE, "kind": "ring", "t": 5},
            {"at": [19.04, 47.5], "label": "Budapest", "color": TEAL, "kind": "ring", "t": 7}, {"at": [28.86, 47.01], "label": "Chisinau", "color": TEAL, "kind": "ring", "t": 9}])
tSa = W("p45", "Sanctions")
add(id="c6-answer", type="region", start=S("p45"), end=tSa, tag="SIMULATION", clock="DAY 2 TO 3", clockLabel="OUR CHOICES",
    view={"center": [28, 50], "widthKm": 2400}, zoomTo={"center": [30, 50], "widthKm": 1500}, highlight=[HL_UKR, HL_RUS] + NATO_EAST,
    cities=[{"at": TGT, "label": "Detonation site", "color": RED, "kind": "target", "size": 6, "t": 0.3}],
    labels=[{"at": [21, 53.6], "text": "No ally answers with a nuclear weapon", "color": TEAL, "t": 1.0}, {"at": [21, 47.4], "text": "A conventional response is one option", "color": WHITE, "t": W("p45", "A") - S("p45")},
            {"at": [21, 46.4], "text": "2022: a retired US general, not for his government", "color": DIM, "t": W("p45", "one", 2) - S("p45")}])
add(id="c6-isolate", type="globe", start=tSa, end=S("p47"), tag="SIMULATION", clock="DAY 2 TO 3", clockLabel="OUR CHOICES", caption="Sanctions and isolation. China and India distance themselves. Our choices.",
    camera=[{"t": 0, "lat": 50, "lon": 45, "scale": 650}, {"t": 5, "lat": 40, "lon": 80, "scale": 650}, {"t": S("p47") - tSa, "lat": 52, "lon": 50, "scale": 700}], sun={"lat": 10, "lon": 90},
    highlight=[HL_RUS_RED, {"iso": CHN, "color": AMBER}, {"iso": IND, "color": AMBER}],
    markers=[{"at": MOSCOW, "label": "Sanctions, isolation", "color": RED, "kind": "dot", "t": 0.5}, {"at": BEIJING, "label": "China", "color": AMBER, "kind": "dot", "t": W("p45", "China") - tSa}, {"at": DELHI, "label": "India", "color": AMBER, "kind": "dot", "t": W("p45", "India") - tSa},
             {"at": [52, 58.5], "label": "Russia: no second weapon, for now", "color": RED, "kind": "dot", "t": S("p46") - tSa}])
tFl, tRa, tBk = W("p47", "Flights"), W("p47", "Poland"), W("p47", "Rail")
add(id="c6-seas", type="region", start=S("p47"), end=tBk, tag="SIMULATION", clock="DAY 4 TO 7", clockLabel="OUR CHOICES", caption="Oil, grain and insurance jump. Flights rerouted. Poland and the Baltic states raise alert levels.",
    view={"center": [32, 48], "widthKm": 1900}, zoomTo={"center": [30, 50.5], "widthKm": 2500}, highlight=[HL_UKR, HL_RUS] + NATO_EAST,
    zones=[{"points": [[35.5, 52.0], [40.2, 50.4], [40.1, 47.6], [38.0, 47.0], [35.5, 48.3]], "label": "Airspace: flights rerouted", "color": AMBER, "t": tFl - S("p47"), "pulse": True}],
    ships=[{"path": [[30.75, 46.5], [30.2, 44.0], [29.2, 41.3]], "t0": 0.5, "t1": 9, "kind": "cargo", "label": "Grain", "t": 0},
           {"path": [[37.8, 44.7], [33.5, 43.0], [29.4, 41.2]], "t0": 0.5, "t1": 10, "kind": "tanker", "label": "Oil", "t": 0}])
add(id="c6-rail", type="region", start=tBk, end=S("p48"), tag="SIMULATION", clock="DAY 4 TO 7", clockLabel="OUR CHOICES", caption="Rail through the target district stops. Banking links with Russia are cut.",
    view={"center": [36, 51.5], "widthKm": 1000}, zoomTo={"center": [37, 53], "widthKm": 1500}, highlight=[HL_UKR, HL_RUS_RED],
    cities=[{"at": TGT, "label": "Rail stops", "color": RED, "kind": "target", "size": 6, "t": 0.5}, {"at": MOSCOW, "label": "Banking links cut", "color": RED, "kind": "dot", "t": W("p47", "Banking") - tBk}],
    lines=[{"from": TGT, "to": MOSCOW, "color": RED, "dashed": True, "t0": 2.5, "t1": 5.0}])
tBut = W("p48", "But")
tIn3 = W("p48", "In", 3)
add(id="c6-noemp", type="region", start=S("p48"), end=tBut, tag="SIMULATION", clock="DAY 4 TO 7", clockLabel="NO BLACKOUT", caption="No blackout. A low 15 kt air burst has no wide-area electromagnetic pulse.",
    view={"center": TGT, "widthKm": 60}, zoomTo={"center": [34, 50], "widthKm": 1400}, highlight=[HL_UKR],
    cities=[{"at": TGT, "label": "Detonation site", "color": RED, "kind": "target", "size": 6, "t": 0.3}], rings=[{"at": TGT, "km": FX["psi1_km"], "color": TEAL, "t": 0.5}])
add(id="c6-znpp", type="region", start=tBut, end=tIn3, tag="SIMULATION", clock="DAY 4 TO 7", clockLabel="FEAR SPREADS", source="IAEA statements",
    view={"center": [35.8, 48.6], "widthKm": 900}, zoomTo={"center": ZNPP, "widthKm": 220}, highlight=[HL_UKR],
    cities=[{"at": ZNPP, "label": "Zaporizhzhia plant: largest in Europe, held by Russian forces", "color": TEAL, "kind": "base", "size": 7, "t": 0.8}, {"at": TGT, "label": "Detonation site", "color": RED, "kind": "target", "size": 5, "t": 0.3},
            {"at": [35.05, 48.46], "label": "Dnipro", "kind": "dot", "t": 1.5}, {"at": [35.14, 47.84], "label": "Zaporizhzhia city", "kind": "dot", "t": 2.5}, {"at": [34.4, 47.9], "label": "", "kind": "dot", "t": 99}, {"at": KHARKIV, "label": "Kharkiv", "kind": "dot", "t": 3.5}],
    labels=[{"at": [34.0, 47.1], "text": "IAEA director: off-site power \"extremely fragile\"", "color": AMBER, "t": W("p48", "IAEA's") - tBut}],
    zones=[{"points": [[34.35, 47.35], [34.8, 47.35], [34.8, 47.67], [34.35, 47.67]], "label": "", "color": AMBER, "t": W("p48", "IAEA's") - tBut, "pulse": True}])
add(id="c6-next", type="region", start=tIn3, end=S("p49"), tag="SIMULATION", clock="DAY 4 TO 7", clockLabel="OUR ASSUMPTION", caption="No one is sure what the next strike would hit.",
    view={"center": [35.5, 48.8], "widthKm": 500}, zoomTo={"center": [36, 49.2], "widthKm": 1300}, highlight=[HL_UKR],
    cities=[{"at": ZNPP, "label": "?", "color": AMBER, "kind": "ring", "size": 7, "t": 0.5}, {"at": TGT, "label": "?", "color": RED, "kind": "ring", "size": 7, "t": 1.5}, {"at": KHARKIV, "label": "?", "color": AMBER, "kind": "ring", "size": 7, "t": 2.5}])
add(id="c6-d7", type="region", start=S("p49"), end=S("p50"), tag="SIMULATION", clock="DAY 7", clockLabel="THE WAR GOES ON", caption="No ceasefire. No one knows whether a second weapon exists, or where.",
    view={"center": [33, 49], "widthKm": 1400}, zoomTo={"center": [34, 49], "widthKm": 2200}, highlight=[HL_UKR, HL_RUS],
    cities=[{"at": TGT, "label": "Day one", "color": RED, "kind": "target", "size": 6, "t": 0.3}, {"at": ZNPP, "label": "", "kind": "ring", "color": AMBER, "size": 6, "t": 2}, {"at": KYIV, "label": "Kyiv", "kind": "dot", "t": 1.0}])
add(id="c6-rule", type="globe", start=S("p50"), end=S("p51"), tag="SIMULATION", clock="DAY 7", clockLabel="IT HAS NOT HAPPENED", caption="After Nagasaki, nobody used one. On day seven, nobody can say if that can be mended.",
    camera=[{"t": 0, "lat": 38, "lon": 120, "scale": 700}, {"t": 5, "lat": 42, "lon": 80, "scale": 800}, {"t": S("p51") - S("p50"), "lat": 49, "lon": 40, "scale": 1500}], sun={"lat": 10, "lon": 100},
    markers=[{"at": NAGASAKI, "label": "Nagasaki, 1945", "color": AMBER, "kind": "target", "t": 0.3}, {"at": TGT, "label": "Day one", "color": RED, "kind": "target", "t": 6}],
    arcs=[{"from": NAGASAKI, "to": TGT, "t0": 1.0, "t1": 7.0, "color": AMBER, "loft": 0.2}])

# ================================================================== End slate
add(id="end", type="endslate", start=S("p51"), end=END, tag="", title="Next scenario", line="Iran tests a bomb, and Israel answers.")

# ------------------------------------------------------------------ audio plan and output
booms = [DET + fl]
b0 = round(W("p04", "simulation") - 0.3, 2)
episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": END,
           "banner": {"start": b0, "end": round(b0 + 3.0, 2)},
           "musicPlan": [
               {"src": "bed_tense.mp3", "from": 0, "to": S("p06") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p06") - 1, "to": S("p20") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p20") - 1, "to": END, "loop": [3, 92], "gain_db": -14},
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
    print(f"{s['id']:16} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
