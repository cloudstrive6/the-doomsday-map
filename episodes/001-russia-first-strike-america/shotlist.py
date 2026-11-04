"""Director pass for episode 001: builds episode.json from narration/timing.json and scenario.computed.json.

Run from the studio root:  .venv/Scripts/python episodes/001-russia-first-strike-america/shotlist.py
Shot boundaries follow paragraph timings; the clock in chapter 4 follows scenario minutes at 15 video seconds per minute.
"""
import json
from pathlib import Path

EP = Path(__file__).parent
timing = json.load(open(EP / "narration" / "timing.json", encoding="utf-8"))
sc = json.load(open(EP / "scenario.computed.json", encoding="utf-8"))
U = {u["id"]: u for u in timing["units"]}
RED, TEAL, AMBER, ORANGE, WHITE = "#FF3B3B", "#3ED6C8", "#F2B01E", "#FF7A1A", "#FFFFFF"
SUN = sc["sun"]  # subsolar point at T-0

def S(pid):  # start of paragraph
    return U[pid]["start"]

def E(pid):  # end of paragraph (plus the gap before the next)
    ids = list(U)
    i = ids.index(pid)
    return U[ids[i + 1]]["start"] if i + 1 < len(ids) else timing["total_seconds"]

DIVISIONS = {
    "Kozelsk": [35.78, 54.03], "Tatishchevo": [45.58, 51.67], "Dombarovsky": [59.84, 51.09], "Uzhur": [89.83, 55.32],
    "Yoshkar-Ola": [47.9, 56.63], "Teykovo": [40.55, 56.85], "Nizhny Tagil": [60.0, 57.9], "Novosibirsk": [82.9, 55.0],
    "Barnaul": [83.8, 53.35], "Irkutsk": [104.3, 52.3],
}
SUBS = {"Barents Sea": [35.0, 72.0], "Sea of Okhotsk": [150.0, 55.0]}
HARBOURS = {"Gadzhiyevo": [33.33, 69.25], "Vilyuchinsk": [158.4, 52.93]}
FIELDS = {"Minot AFB": [-101.36, 48.42], "Malmstrom AFB": [-111.19, 47.5], "F.E. Warren AFB": [-104.87, 41.15]}
BOMBERS = {"Whiteman AFB": [-93.55, 38.73], "Barksdale AFB": [-93.66, 32.5], "Ellsworth AFB": [-103.1, 44.14]}
SUBBASES = {"Kings Bay": [-81.52, 30.8], "Bangor": [-122.72, 47.72]}
RADARS = {"Pituffik": [-68.7, 76.53], "Clear SFS": [-149.19, 64.29], "Fylingdales": [-0.67, 54.36], "Cape Cod SFS": [-70.54, 41.75], "Beale AFB": [-121.44, 39.14]}
COMMAND = {"Offutt AFB": [-95.9145, 41.1183], "Cheyenne Mountain": [-104.85, 38.74], "Pentagon": [-77.06, 38.87]}
OFFUTT = [-95.9145, 41.1183]
DOWNTOWN = [-95.9345, 41.2565]

def arcs_at(minute, secs_per_min=15.0, color=RED, include_us=False):
    """Russian strikes as arcs with progress consistent with `minute` of the scenario at shot start."""
    out = []
    for s in sc["strikes"]:
        D = s["flight_min"] * secs_per_min
        t0 = -(minute - s["launch_min"]) * secs_per_min
        out.append({"from": [s["launch_lon"], s["launch_lat"]], "to": [s["target_lon"], s["target_lat"]], "t0": t0, "t1": t0 + D,
                    "color": ORANGE if s["weapon_class"] == "slbm" else color, "loft": 0.16 if s["weapon_class"] == "icbm" else 0.1})
    if include_us:
        for name, ll in FIELDS.items():
            for i, tgt in enumerate(list(DIVISIONS.values())[:6]):
                t0 = 0.5 + i * 0.4
                out.append({"from": ll, "to": tgt, "t0": t0, "t1": t0 + 28 * secs_per_min, "color": TEAL, "loft": 0.16, "width": 1.2})
    return out

def flashes_until(minute, secs_per_min=15.0):
    out = []
    for s in sc["strikes"]:
        t = (s["impact_min"] - minute) * secs_per_min
        if t < 60:
            out.append({"at": [s["target_lon"], s["target_lat"]], "t": t, "hold": 2.5, "radius": 18 if s["yield_kt"] >= 300 else 12})
    return out

def clock(minute):
    return f"T+{int(minute):02d}:{int(round((minute % 1) * 60)):02d}"

shots = []
def add(**k):
    shots.append(k)

# ---- Cold open
add(id="open-city", type="city", start=0, end=S("p02"), tag="SIMULATION", clock="03:40", clockLabel="CENTRAL TIME · NEBRASKA", city="omaha",
    view={"center": [-95.96, 41.22], "widthKm": 90}, zoomTo={"center": [-95.95, 41.2], "widthKm": 60}, gz=OFFUTT, rings=[],
    labels=[{"at": DOWNTOWN, "text": "Omaha", "color": "rgba(236,239,242,0.7)"}])
add(id="open-globe", type="globe", start=S("p02"), end=S("p03"), tag="SIMULATION", clock="T+00:00", clockLabel="FIRST LAUNCH",
    camera=[{"t": 0, "lat": 55, "lon": 38, "scale": 1500}, {"t": 6, "lat": 58, "lon": 30, "scale": 620}, {"t": 16, "lat": 62, "lon": 5, "scale": 470}],
    sun=SUN, markers=[{"at": ll, "label": n if n in ("Kozelsk", "Uzhur", "Irkutsk") else None, "color": RED, "kind": "base", "t": 0.3 + i * 0.5} for i, (n, ll) in enumerate(DIVISIONS.items())],
    arcs=[{"from": ll, "to": FIELDS[list(FIELDS)[i % 3]], "t0": 3 + i * 0.6, "t1": 3 + i * 0.6 + 26 * 15, "loft": 0.16} for i, ll in enumerate(DIVISIONS.values())])
add(id="open-disclaimer", type="text", start=S("p03"), end=S("p03") + 11, tag="SIMULATION", lines=["A simulation", "It has not happened. The missiles, the bases and the timings are real, and every number has a source."])
add(id="open-title", type="globe", start=S("p03") + 11, end=S("p04"), tag="SIMULATION", caption="Russia launches a nuclear strike on America. Minute by minute.",
    camera=[{"t": 0, "lat": 60, "lon": -45, "scale": 380}, {"t": 12, "lat": 55, "lon": -60, "scale": 420}], sun=SUN, arcs=arcs_at(6), dim=0.1)

# ---- Chapter 01 the real forces
add(id="c1-card", type="chapter", start=S("p04"), end=S("p04") + 4, tag="REAL DATA", kicker="CHAPTER 01", title="The real forces")
add(id="c1-iso", type="isotype", start=S("p04") + 4, end=S("p05"), tag="REAL DATA", headline="12,000+", label="nuclear warheads in the world", total=240, filled=212, per="50 warheads",
    cols=30, sub="Russia and the United States hold almost nine in ten. About 1,700 strategic warheads deployed on each side.", source="FAS Status of World Nuclear Forces 2025; SIPRI Yearbook 2025")
add(id="c1-russia", type="region", start=S("p05"), end=S("p06"), tag="REAL DATA", source="Bulletin of the Atomic Scientists, Russian nuclear weapons 2025",
    view={"center": [62, 57], "widthKm": 7800}, zoomTo={"center": [66, 56], "widthKm": 6800}, highlight=[{"iso": "643", "color": RED}],
    countryLabels=[{"iso": "643", "text": "Russia"}, {"iso": "398", "text": "Kazakhstan"}, {"iso": "156", "text": "China"}],
    cities=[{"at": ll, "label": n, "color": RED, "kind": "base", "size": 5, "t": 1 + i * 1.4} for i, (n, ll) in enumerate(DIVISIONS.items())],
    labels=[{"at": [60, 47.5], "text": "about 330 intercontinental missiles · 11 divisions", "color": "rgba(236,239,242,0.75)", "t": 17}])
add(id="c1-subs", type="globe", start=S("p06"), end=S("p07"), tag="REAL DATA", source="Barents Observer; FAS Nuclear Notebook 2025", caption="Borei submarines: 16 Bulava missiles each, reach about 8,000 km",
    camera=[{"t": 0, "lat": 72, "lon": 90, "scale": 560}, {"t": 18, "lat": 68, "lon": 80, "scale": 600}], sun={"lat": 10, "lon": 60},
    markers=[{"at": HARBOURS["Gadzhiyevo"], "label": "Gadzhiyevo · Northern Fleet", "color": ORANGE, "kind": "sub", "t": 1}, {"at": HARBOURS["Vilyuchinsk"], "label": "Vilyuchinsk · Pacific Fleet", "color": ORANGE, "kind": "sub", "t": 4}],
    arcs=[{"from": HARBOURS["Gadzhiyevo"], "to": [-77.06, 38.87], "t0": 7, "t1": 16, "color": ORANGE, "loft": 0.1}, {"from": HARBOURS["Vilyuchinsk"], "to": [-122.72, 47.72], "t0": 9, "t1": 17, "color": ORANGE, "loft": 0.1}])
add(id="c1-plains", type="region", start=S("p07"), end=S("p08"), tag="REAL DATA", source="Air Force Global Strike Command; minutemanmissile.com", caption="400 Minuteman III missiles in 450 silos",
    view={"center": [-105.5, 45.5], "widthKm": 2600}, zoomTo={"center": [-105.5, 45.2], "widthKm": 2100},
    cities=[{"at": ll, "label": n, "color": TEAL, "kind": "base", "size": 6, "t": 1 + i * 2} for i, (n, ll) in enumerate(FIELDS.items())] + [{"at": OFFUTT, "label": "Offutt AFB", "color": RED, "kind": "base", "size": 5, "t": 12}],
    rings=[{"at": ll, "km": 130, "color": TEAL, "t": 2 + i * 2} for i, ll in enumerate(FIELDS.values())],
    labels=[{"at": [-105.5, 50.2], "text": "silo fields · Montana, North Dakota, Wyoming, Colorado, Nebraska", "color": "rgba(236,239,242,0.75)", "t": 8}])
add(id="c1-offutt", type="city", start=S("p08"), end=S("p08") + 16, tag="REAL DATA", source="US Strategic Command history; Brookings", city="omaha",
    view={"center": [-95.95, 41.2], "widthKm": 60}, zoomTo={"center": [-95.93, 41.17], "widthKm": 34}, gz=OFFUTT, rings=[],
    labels=[{"at": OFFUTT, "text": "Offutt AFB · US Strategic Command", "color": RED, "t": 1}, {"at": DOWNTOWN, "text": "Downtown Omaha", "color": "rgba(236,239,242,0.8)", "t": 4}, {"at": [-95.89, 41.15], "text": "Bellevue", "color": "rgba(236,239,242,0.6)", "t": 6}])
add(id="c1-stamp", type="stamp", start=S("p08") + 16, end=S("p09"), tag="REAL HISTORY", text="Since the 1950s", line="SAC built its command post underground to survive a Soviet strike")

# ---- Chapter 02 thirty minutes
add(id="c2-card", type="chapter", start=S("p09"), end=S("p09") + 3.5, tag="REAL DATA", kicker="CHAPTER 02", title="Thirty minutes")
add(id="c2-num", type="number", start=S("p09") + 3.5, end=S("p10"), tag="REAL DATA", value="30 MIN", label="from a launch in Russia to impact in America", source="Reuters; Global Zero launch-on-warning timeline")
add(id="c2-sbirs", type="globe", start=S("p10"), end=S("p11"), tag="REAL DATA", caption="Infrared satellites register a launch within seconds",
    camera=[{"t": 0, "lat": 45, "lon": -40, "scale": 450}, {"t": 12, "lat": 42, "lon": -70, "scale": 520}], sun=SUN,
    markers=[{"at": [-104.76, 39.72], "label": "Buckley SFB · satellite ground station", "color": TEAL, "kind": "ring", "t": 1}, {"at": COMMAND["Cheyenne Mountain"], "label": "NORAD", "color": TEAL, "kind": "base", "t": 3},
             {"at": OFFUTT, "label": "STRATCOM", "color": TEAL, "kind": "base", "t": 4.5}, {"at": COMMAND["Pentagon"], "label": "National Military Command Center", "color": TEAL, "kind": "base", "t": 6}])
add(id="c2-radars", type="globe", start=S("p11"), end=S("p11") + 15, tag="REAL DATA", caption="Ground radars confirm the launch as missiles rise over the horizon: about ten minutes",
    camera=[{"t": 0, "lat": 70, "lon": -60, "scale": 480}, {"t": 15, "lat": 66, "lon": -70, "scale": 520}], sun=SUN,
    markers=[{"at": ll, "label": n, "color": TEAL, "kind": "ring", "t": 1 + i * 1.2} for i, (n, ll) in enumerate(RADARS.items())])
add(id="c2-timeline", type="timeline", start=S("p11") + 15, end=S("p12"), tag="REAL DATA", title="Thirty minutes", sub="launch to impact · who does what", total=30, source="Global Zero LOW timeline (Blair); National Interest",
    segments=[{"from": 0, "to": 1, "label": "Detect", "color": TEAL}, {"from": 1, "to": 10, "label": "Radar confirms", "color": TEAL}, {"from": 10, "to": 13, "label": "Brief", "color": TEAL}, {"from": 13, "to": 19, "label": "Decide", "color": RED}, {"from": 19, "to": 30, "label": "Launch · missiles in the air", "color": AMBER}],
    highlight={"from": 13, "to": 19, "label": "about 6 minutes"}, cursorTo=30)
add(id="c2-nobody", type="text", start=S("p12"), end=S("p13"), tag="REAL DATA", lines=["Nobody has ever decided", "Our simulation asks what the thirty minutes look like if they ever do."])

# ---- Chapter 03 the warning shot
add(id="c3-card", type="chapter", start=S("p13"), end=S("p13") + 4, tag="SIMULATION", kicker="CHAPTER 03", title="The warning shot that was never answered")
add(id="c3-baltic", type="region", start=S("p13") + 4, end=S("p13") + 17, tag="SIMULATION", source="Russia's 2026-09-30 note to NATO (CTV News, Kyiv Independent)",
    view={"center": [22, 55], "widthKm": 2000}, zoomTo={"center": [23, 54.8], "widthKm": 1500},
    highlight=[{"iso": "643", "color": RED}, {"iso": "112", "color": RED}, {"iso": "616", "color": TEAL}, {"iso": "440", "color": TEAL}, {"iso": "428", "color": TEAL}, {"iso": "233", "color": TEAL}],
    countryLabels=[{"iso": "616", "text": "Poland"}, {"iso": "440", "text": "Lithuania"}, {"iso": "112", "text": "Belarus"}, {"iso": "428", "text": "Latvia"}],
    cities=[{"at": [20.51, 54.71], "label": "Kaliningrad", "color": RED, "kind": "base", "size": 6}],
    lines=[{"from": [20.9, 54.4], "to": [23.6, 53.9], "color": AMBER, "dashed": True, "t0": 2, "t1": 4}],
    labels=[{"at": [22.3, 53.6], "text": "Suwalki Gap", "color": AMBER, "t": 4}])
add(id="c3-doctrine", type="stamp", start=S("p13") + 17, end=S("p14"), tag="REAL HISTORY", text="Doctrine · 2024", line="an attack backed by a nuclear power counts as a joint attack")
add(id="c3-targets", type="region", start=S("p14"), end=S("p14") + 17, tag="SIMULATION", caption="About 650 warheads at some 500 aim points. A scenario, not a forecast.",
    view={"center": [-98, 39.5], "widthKm": 5600}, zoomTo={"center": [-98, 40], "widthKm": 5000},
    rings=[{"at": ll, "km": 130, "color": RED, "t": 1 + i} for i, ll in enumerate(FIELDS.values())],
    cities=[{"at": ll, "label": n, "color": RED, "kind": "target", "size": 5, "t": 4 + i * 0.7} for i, (n, ll) in enumerate(list(BOMBERS.items()) + list(SUBBASES.items()))]
          + [{"at": ll, "label": n, "color": AMBER, "kind": "ring", "size": 4, "t": 8 + i * 0.6} for i, (n, ll) in enumerate(RADARS.items()) if n not in ("Fylingdales",)]
          + [{"at": ll, "label": n, "color": WHITE, "kind": "base", "size": 6, "t": 11 + i * 0.8} for i, (n, ll) in enumerate(COMMAND.items())])
add(id="c3-650", type="number", start=S("p14") + 17, end=S("p15"), tag="SIMULATION", value="650", countTo=650, label="warheads in the first wave", sub="two for every Minuteman silo · bomber and submarine bases · radars · command posts. Simulation assumption, built from open sources.")

# ---- Chapter 04 minute by minute (15 video seconds per scenario minute inside globe shots)
add(id="c4-card", type="chapter", start=S("p15"), end=S("p15") + 3.5, tag="SIMULATION", kicker="CHAPTER 04", title="Minute by minute")
add(id="c4-m0", type="globe", start=S("p15") + 3.5, end=S("p16"), tag="SIMULATION", clock=clock(0), clockLabel="03:40 CENTRAL",
    camera=[{"t": 0, "lat": 57, "lon": 55, "scale": 640}, {"t": 22, "lat": 66, "lon": 50, "scale": 520}], sun=SUN,
    markers=[{"at": ll, "label": n, "color": RED, "kind": "base", "t": 0.5 + i * 0.9} for i, (n, ll) in enumerate(DIVISIONS.items())] + [{"at": ll, "label": n, "color": ORANGE, "kind": "sub", "t": 10 + i * 2} for i, (n, ll) in enumerate(SUBS.items())],
    arcs=[dict(a, t0=max(a["t0"], 2 + i * 0.5)) for i, a in enumerate(arcs_at(0))])
add(id="c4-m1", type="radar", start=S("p16"), end=S("p17"), tag="SIMULATION", clock=clock(1), clockLabel="SINCE FIRST LAUNCH", title="Infrared warning · Buckley SFB",
    lines=[{"k": "launch flares", "v": "300+"}, {"k": "origin", "v": "Russia · 10 divisions · 2 sea areas"}, {"k": "first call", "v": "NORAD"}], tracks=12, big="LAUNCH · MULTIPLE · RUSSIA", footer="This is not a test")
add(id="c4-m3", type="region", start=S("p17"), end=S("p18"), tag="SIMULATION", clock=clock(3), clockLabel="SINCE FIRST LAUNCH", caption="The conference opens. The president is woken.",
    view={"center": [-96, 41], "widthKm": 4600}, cities=[{"at": COMMAND["Cheyenne Mountain"], "label": "NORAD · Cheyenne Mountain", "color": TEAL, "kind": "base", "size": 6, "t": 0.5}, {"at": OFFUTT, "label": "STRATCOM · Offutt", "color": TEAL, "kind": "base", "size": 6, "t": 2}, {"at": COMMAND["Pentagon"], "label": "NMCC · Pentagon", "color": TEAL, "kind": "base", "size": 6, "t": 3.5}, {"at": [-77.04, 38.9], "label": "The president", "color": WHITE, "kind": "ring", "size": 5, "t": 6}],
    lines=[{"from": COMMAND["Cheyenne Mountain"], "to": OFFUTT, "color": TEAL, "dashed": True, "t0": 2, "t1": 3}, {"from": OFFUTT, "to": COMMAND["Pentagon"], "color": TEAL, "dashed": True, "t0": 3.5, "t1": 4.5}])
add(id="c4-m8", type="globe", start=S("p18"), end=S("p19"), tag="SIMULATION", clock=clock(8), clockLabel="SINCE FIRST LAUNCH", caption="Pituffik, Greenland: the radar sees the first missiles over the pole",
    camera=[{"t": 0, "lat": 78, "lon": -40, "scale": 620}, {"t": 10, "lat": 80, "lon": -50, "scale": 700}], sun=SUN, arcs=arcs_at(8), markers=[{"at": RADARS["Pituffik"], "label": "Pituffik radar", "color": TEAL, "kind": "ring", "t": 0.5}])
add(id="c4-m12", type="globe", start=S("p19"), end=S("p20"), tag="SIMULATION", clock=clock(12), clockLabel="SINCE FIRST LAUNCH", caption="The first warhead of the war: a submarine shot at the radar",
    camera=[{"t": 0, "lat": 76, "lon": -55, "scale": 900}, {"t": 14, "lat": 76, "lon": -62, "scale": 1300}], sun=SUN, arcs=arcs_at(12), markers=[{"at": RADARS["Pituffik"], "label": "Pituffik", "color": TEAL, "kind": "ring"}],
    flashes=[{"at": RADARS["Pituffik"], "t": 2.5, "hold": 3, "radius": 40}])
add(id="c4-m13", type="timeline", start=S("p20"), end=S("p21"), tag="SIMULATION", clock=clock(13), clockLabel="SINCE FIRST LAUNCH", title="The options are on a card", sub="launch the Minuteman force now, or absorb the strike", total=30,
    segments=[{"from": 0, "to": 1, "label": "Detect", "color": TEAL}, {"from": 1, "to": 10, "label": "Radar confirms", "color": TEAL}, {"from": 10, "to": 13, "label": "Brief", "color": TEAL}, {"from": 13, "to": 19, "label": "Decide", "color": RED}, {"from": 19, "to": 30, "label": "Impact window", "color": AMBER}],
    highlight={"from": 13, "to": 19, "label": "six minutes"}, cursorTo=19)
add(id="c4-m19", type="globe", start=S("p21"), end=S("p22"), tag="SIMULATION", clock=clock(19), clockLabel="SINCE FIRST LAUNCH", caption="Launch under attack: 400 Minuteman missiles head north",
    camera=[{"t": 0, "lat": 72, "lon": -95, "scale": 520}, {"t": 18, "lat": 78, "lon": -70, "scale": 560}], sun=SUN, arcs=arcs_at(19, include_us=True),
    markers=[{"at": ll, "label": n, "color": TEAL, "kind": "base"} for n, ll in FIELDS.items()])
add(id="c4-m20", type="region", start=S("p22"), end=S("p23"), tag="SIMULATION", clock=clock(20), clockLabel="SINCE FIRST LAUNCH", caption="Bangor: two ground bursts on the submarine piers",
    view={"center": [-122.6, 47.75], "widthKm": 110}, zoomTo={"center": [-122.68, 47.72], "widthKm": 80},
    cities=[{"at": SUBBASES["Bangor"], "label": "Naval Base Kitsap · Bangor", "color": RED, "kind": "base", "size": 6}, {"at": [-122.33, 47.61], "label": "Seattle"}, {"at": [-122.63, 47.57], "label": "Bremerton"}, {"at": [-122.44, 47.25], "label": "Tacoma"}],
    rings=[{"at": SUBBASES["Bangor"], "km": 0.56, "color": WHITE, "t": 2, "dashed": False, "label": "fireball"}, {"at": SUBBASES["Bangor"], "km": 2.9, "color": RED, "t": 2.6, "label": "5 psi"}, {"at": SUBBASES["Bangor"], "km": 4.9, "color": AMBER, "t": 3.3, "label": "3rd degree burns"}, {"at": SUBBASES["Bangor"], "km": 7.8, "color": TEAL, "t": 4, "label": "1 psi"}])
add(id="c4-m22", type="region", start=S("p23"), end=S("p24"), tag="SIMULATION", clock=clock(22), clockLabel="SINCE FIRST LAUNCH", caption="Washington: six warheads, airburst",
    view={"center": [-77.1, 38.88], "widthKm": 90}, zoomTo={"center": [-77.06, 38.88], "widthKm": 60},
    cities=[{"at": COMMAND["Pentagon"], "label": "Pentagon", "color": RED, "kind": "base", "size": 6}, {"at": [-77.01, 38.89], "label": "Capitol"}, {"at": [-76.87, 38.81], "label": "Andrews"}, {"at": [-77.45, 38.95], "label": "Dulles"}, {"at": [-76.61, 39.29], "label": "Baltimore"}],
    rings=[{"at": COMMAND["Pentagon"], "km": 0.45, "color": WHITE, "t": 1.5, "dashed": False, "label": "fireball"}, {"at": COMMAND["Pentagon"], "km": 3.6, "color": RED, "t": 2.2, "label": "5 psi"}, {"at": [-76.87, 38.81], "km": 3.6, "color": RED, "t": 3.2}, {"at": [-77.01, 38.9], "km": 3.6, "color": RED, "t": 4.0}, {"at": COMMAND["Pentagon"], "km": 9.7, "color": TEAL, "t": 5, "label": "1 psi"}])
add(id="c4-m25", type="region", start=S("p24"), end=S("p25"), tag="SIMULATION", clock=clock(25), clockLabel="SINCE FIRST LAUNCH", caption="The silo fields: hundreds of ground bursts, two on each silo",
    view={"center": [-105.5, 45.5], "widthKm": 2300}, zoomTo={"center": [-105.5, 45.5], "widthKm": 2000},
    cities=[{"at": ll, "label": n, "color": TEAL, "kind": "base", "size": 5} for n, ll in FIELDS.items()],
    rings=[{"at": ll, "km": 130, "color": RED, "t": 1 + i * 2.2, "dashed": False} for i, ll in enumerate(FIELDS.values())])
add(id="c4-m27", type="number", start=S("p25"), end=S("p26"), tag="SIMULATION", value="T+00:27", label="Offutt", color=RED)

# ---- Chapter 05 one warhead (Omaha, real streets)
RINGS = [{"km": 1.1, "label": "Fireball", "color": WHITE}, {"km": 5.0, "label": "5 psi · most buildings destroyed", "color": RED}, {"km": 9.8, "label": "3rd degree burns", "color": AMBER}, {"km": 13.6, "label": "1 psi · windows", "color": TEAL}]
def rings_upto(n, new_t):
    return [dict(r, t=(-30 if i < n - 1 else new_t)) for i, r in enumerate(RINGS[:n])]
CITY_LABELS = [{"at": OFFUTT, "text": "Offutt AFB", "color": RED}, {"at": DOWNTOWN, "text": "Downtown Omaha · 15 km", "color": "rgba(236,239,242,0.85)"}, {"at": [-95.89, 41.15], "text": "Bellevue", "color": "rgba(236,239,242,0.7)"}, {"at": [-95.86, 41.26], "text": "Council Bluffs", "color": "rgba(236,239,242,0.6)"}]
LEGEND = [{"text": "5 psi: most buildings destroyed", "color": RED}, {"text": "3rd degree burns from the flash", "color": AMBER}, {"text": "1 psi: windows shatter", "color": TEAL}]
add(id="c5-flash", type="city", start=S("p26"), end=S("p27"), tag="SIMULATION", clock=clock(27), clockLabel="SINCE FIRST LAUNCH", source="Effects: Glasstone and Dolan scaling calibrated to NUKEMAP", city="omaha",
    view={"center": [-95.92, 41.14], "widthKm": 24}, zoomTo={"center": [-95.92, 41.15], "widthKm": 28}, gz=OFFUTT, flashT=2.5, rings=rings_upto(1, 2.6), labels=CITY_LABELS[:1], legend=LEGEND)
add(id="c5-5psi", type="city", start=S("p27"), end=S("p28"), tag="SIMULATION", clock=clock(27), clockLabel="SINCE FIRST LAUNCH", city="omaha",
    view={"center": [-95.92, 41.15], "widthKm": 28}, zoomTo={"center": [-95.92, 41.16], "widthKm": 34}, gz=OFFUTT, flashT=-30, rings=rings_upto(2, 0.6), labels=CITY_LABELS[:3], legend=LEGEND)
add(id="c5-burns", type="city", start=S("p28"), end=S("p29"), tag="SIMULATION", clock=clock(27), clockLabel="SINCE FIRST LAUNCH", city="omaha",
    view={"center": [-95.92, 41.16], "widthKm": 34}, zoomTo={"center": [-95.93, 41.18], "widthKm": 42}, gz=OFFUTT, flashT=-30, rings=rings_upto(3, 0.6), labels=CITY_LABELS[:3], legend=LEGEND)
add(id="c5-1psi", type="city", start=S("p29"), end=S("p30"), tag="SIMULATION", clock=clock(27), clockLabel="SINCE FIRST LAUNCH", city="omaha",
    view={"center": [-95.93, 41.18], "widthKm": 42}, zoomTo={"center": [-95.93, 41.19], "widthKm": 50}, gz=OFFUTT, flashT=-30, rings=rings_upto(4, 0.6), labels=CITY_LABELS, legend=LEGEND)
add(id="c5-fallout", type="region", start=S("p30"), end=S("p31"), tag="SIMULATION", clock="+6 HOURS", clockLabel="AFTER THE BURST", caption="A ground burst. The wind in November blows from the west.",
    view={"center": [-95.0, 41.3], "widthKm": 260}, zoomTo={"center": [-94.6, 41.3], "widthKm": 300},
    cities=[{"at": OFFUTT, "label": "Offutt", "color": RED, "kind": "base", "size": 5}, {"at": DOWNTOWN, "label": "Omaha"}, {"at": [-95.86, 41.26], "label": "Council Bluffs"}, {"at": [-93.62, 41.59], "label": "Des Moines"}, {"at": [-96.68, 40.81], "label": "Lincoln"}],
    plume={"at": OFFUTT, "bearing": 95, "lengthKm": 190, "widthKm": 55, "t0": 1, "t1": 10, "label": "fallout · +6 h"})

# ---- Chapter 06 the day after
add(id="c6-card", type="chapter", start=S("p31"), end=S("p31") + 3.5, tag="REAL DATA", kicker="CHAPTER 06", title="The day after")
add(id="c6-710", type="bars", start=S("p31") + 3.5, end=S("p32"), tag="REAL DATA", title="The seven-ten rule", sub="fallout radiation after a ground burst", source="Glasstone and Dolan; Ready.gov",
    bars=[{"label": "1 hour after", "value": 100, "display": "100%", "color": RED}, {"label": "7 hours after", "value": 10, "display": "10%", "color": AMBER}, {"label": "2 days after", "value": 1, "display": "1%", "color": TEAL}, {"label": "2 weeks after", "value": 0.1, "display": "0.1%", "color": TEAL}])
add(id="c6-shelter", type="stamp", start=S("p32"), end=S("p33"), tag="REAL DATA", text="No shelter system", line="get inside · stay inside · stay tuned")
add(id="c6-plan-a", type="number", start=S("p33"), end=S("p33") + 13, tag="REAL DATA", value="34.1 MILLION", countTo=34.1, decimals=1, suffix=" MILLION", label="dead within a few hours", sub="Princeton University, Plan A (2019): 34.1 million dead, 57.4 million injured, before fallout", source="sgs.princeton.edu/the-lab/plan-a; ICAN")
add(id="c6-915", type="text", start=S("p33") + 13, end=S("p34"), tag="REAL DATA", lines=["91,500,000 casualties", "in the first few hours. Fallout and the collapse of hospitals come after."])
add(id="c6-famine", type="isotype", start=S("p34"), end=S("p34") + 13, tag="REAL DATA", headline="5,000,000,000", label="could be starving within two years", sub="Xia et al., Nature Food, 2022. US-Russia war scenario, about 150 million tonnes of soot.", total=800, filled=630, per="10 million people", cols=40, source="Nature Food 3, 586-596 (2022)")
add(id="c6-dark", type="globe", start=S("p34") + 13, end=S("p35"), tag="REAL DATA", caption="Average temperatures fall for years. Harvests fail.",
    camera=[{"t": 0, "lat": 35, "lon": -30, "scale": 430}, {"t": 11, "lat": 30, "lon": -40, "scale": 450}], sun={"lat": -20, "lon": 60}, dim=0.55)

# ---- Chapter 07 how close it has come
add(id="c7-card", type="chapter", start=S("p35"), end=S("p36"), tag="REAL HISTORY", kicker="CHAPTER 07", title="How close it has come")
add(id="c7-1979", type="stamp", start=S("p36"), end=S("p37"), tag="REAL HISTORY", text="1979", line="NORAD · a training tape shows a full Soviet attack · the adviser is minutes from calling the president", color=AMBER)
add(id="c7-chip", type="number", start=S("p37"), end=S("p38"), tag="REAL HISTORY", value="46 CENTS", label="one faulty chip · June 1980", sub="random numbers written into the missile-warning messages. Twice in a week the screens showed an attack.", color=AMBER, source="National Security Archive; GlobalSecurity")
add(id="c7-petrov", type="radar", start=S("p38"), end=S("p39"), tag="REAL HISTORY", title="Serpukhov-15 · 26 September 1983", lines=[{"k": "tracks · inbound", "v": "5"}, {"k": "reported origin", "v": "United States"}, {"k": "duty officer", "v": "Lt Col Stanislav Petrov"}], tracks=5, big="FALSE ALARM", bigColor=AMBER, footer="He was right.")
add(id="c7-norway", type="region", start=S("p39"), end=S("p40"), tag="REAL HISTORY", caption="1995: a Norwegian science rocket, read by Russian radar as a possible missile",
    view={"center": [25, 69], "widthKm": 2600}, cities=[{"at": [16.0, 69.3], "label": "Andoya rocket range", "color": AMBER, "kind": "base", "size": 5}, {"at": [33.08, 68.97], "label": "Murmansk"}, {"at": [37.62, 55.75], "label": "Moscow"}],
    lines=[{"from": [16.0, 69.3], "to": [10.0, 79.0], "color": AMBER, "dashed": True, "t0": 1, "t1": 5}], countryLabels=[{"iso": "578", "text": "Norway"}, {"iso": "643", "text": "Russia"}, {"iso": "246", "text": "Finland"}])

# ---- Chapter 08 the clock
add(id="c8-card", type="chapter", start=S("p40"), end=S("p40") + 3, tag="REAL DATA", kicker="CHAPTER 08", title="The clock")
add(id="c8-85", type="number", start=S("p40") + 3, end=S("p41"), tag="REAL DATA", value="85 SECONDS", label="to midnight · 27 January 2026", sub="Bulletin of the Atomic Scientists. The closest the Doomsday Clock has ever been.", source="thebulletin.org")
add(id="c8-start", type="stamp", start=S("p41"), end=S("p42"), tag="REAL DATA", text="New START · expired", line="5 February 2026 · no treaty limit on strategic weapons for the first time in half a century")
add(id="c8-earth", type="globe", start=S("p42"), end=S("p43"), tag="REAL DATA", caption="Eighty-one years. Every person with the authority to launch has decided not to.",
    camera=[{"t": 0, "lat": 40, "lon": -60, "scale": 400}, {"t": 10, "lat": 38, "lon": -70, "scale": 410}], sun={"lat": -20, "lon": -100})
add(id="c8-zero", type="text", start=S("p43"), end=S("p44"), tag="SIMULATION", lines=["Minute zero", "The only way to keep the thirty minutes on this map is for the first decision never to be made."])
add(id="end", type="endslate", start=S("p44"), end=timing["total_seconds"] + 15, tag="", title="Next scenario", line="China blockades Taiwan, and the first nuclear weapon since 1945 is used. New scenario every day.")

episode = {"slug": EP.name, "fps": 60, "width": 1920, "height": 1080, "durationSeconds": round(timing["total_seconds"] + 15, 2),
           "musicPlan": [
               {"src": "bed.mp3", "from": 0, "to": S("p15") + 1, "loop": [2, 174], "gain_db": -17},
               {"src": "bed_tense.mp3", "from": S("p15") - 1, "to": S("p31") + 1, "loop": [3, 92], "gain_db": -14},
               {"src": "bed.mp3", "from": S("p31") - 1, "to": timing["total_seconds"] + 15, "loop": [2, 174], "gain_db": -17},
           ],
           "sfxPlan": [{"src": "impact.mp3", "t": s["start"] + 0.15, "gain_db": -9} for s in shots if s["type"] == "chapter"]
                    + [{"src": "radar.mp3", "t": s["start"] + 0.4, "gain_db": -12} for s in shots if s["type"] == "radar"]
                    + [{"src": "boom.mp3", "t": s["start"] + s["flashT"], "gain_db": -4} for s in shots if s["type"] == "city" and s.get("flashT", -1) >= 0]
                    + [{"src": "boom.mp3", "t": s["start"] + f["t"], "gain_db": -10} for s in shots if s["id"] in ("c4-m12",) for f in s.get("flashes", []) if 0 <= f["t"] < s["end"] - s["start"]]
                    + [{"src": "whoosh.mp3", "t": s["start"] - 0.4, "gain_db": -14} for s in shots if s["type"] == "stamp"],
           "attribution": "Maps: Natural Earth (public domain); OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles. Imagery: NASA Blue Marble and Black Marble. Narration: AI-generated.",
           "shots": shots}
# strip None labels
for s in shots:
    for m in s.get("markers", []) + s.get("cities", []):
        if m.get("label") is None:
            m.pop("label", None)
(EP / "episode.json").write_text(json.dumps(episode, indent=1, ensure_ascii=False), encoding="utf-8")
prev = 0
for s in shots:
    flag = "" if abs(s["start"] - prev) < 0.01 else f"  <-- gap/overlap {s['start'] - prev:+.2f}"
    print(f"{s['id']:14} {s['type']:9} {s['start']:7.1f} {s['end']:7.1f} {s['end'] - s['start']:5.1f}{flag}")
    prev = s["end"]
print(len(shots), "shots,", episode["durationSeconds"], "s")
