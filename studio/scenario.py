"""Scenario engine: deterministic numbers for a nuclear-strike scenario.

Every figure the script quotes about blast effects, distances, flight times and timing comes from here,
so the fact screener checks sources and inputs, never arithmetic.

Effects model
-------------
Radii scale with yield by the classic laws in Glasstone and Dolan, *The Effects of Nuclear Weapons* (1977):
blast overpressure radii with the cube root of yield, thermal radii roughly with yield^0.41, the fireball
with yield^0.4. The constants are calibrated so a 15 kt airburst reproduces the widely quoted NUKEMAP
(Alex Wellerstein) figures for Hiroshima: 5 psi at 1.67 km, 1 psi at 4.52 km, third-degree burns at 1.91 km,
fireball radius 0.18 km. Ground bursts have smaller blast radii (about 0.8 of an optimum-height airburst
at the same yield) but heavy local fallout. Treat every output as an estimate for a simulation, never as a
forecast; the script must say so.

Flight times are a simple fit to published figures (ICBM about 30 minutes over 10,000 km; SLBM about
10 minutes from 2,000 km; short-range ballistic about 5 minutes over 500 km). Scripts quote them rounded.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path

EARTH_KM = 6371.0088

# km at 1 kt (airburst at the height that maximises the 5 psi ring); scale with Y^(1/3) unless noted
_K = {
    "psi20": 0.34 / 15 ** (1 / 3),       # heavy blast: reinforced concrete buildings destroyed
    "psi5": 1.67 / 15 ** (1 / 3),        # moderate blast: most residential buildings collapse
    "psi1": 4.52 / 15 ** (1 / 3),        # light blast: windows shatter, injuries from glass
    "thermal3": 1.91 / 15 ** 0.41,       # third-degree burns to exposed skin (scales about Y^0.41)
    "fireball": 0.18 / 15 ** 0.4,        # maximum fireball radius (scales about Y^0.4)
}
_GROUND_BLAST_FACTOR = 0.8  # surface burst versus optimum airburst, blast rings only


@dataclass
class Effects:
    yield_kt: float
    burst: str                      # "air" or "ground"
    fireball_km: float
    psi20_km: float
    psi5_km: float
    psi1_km: float
    thermal3_km: float
    fallout: str                    # "little local fallout" or "heavy local fallout"

    def as_dict(self):
        return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in asdict(self).items()}


def effects(yield_kt: float, burst: str = "air") -> Effects:
    if yield_kt <= 0:
        raise ValueError("yield must be positive")
    if burst not in ("air", "ground"):
        raise ValueError("burst must be air or ground")
    f = _GROUND_BLAST_FACTOR if burst == "ground" else 1.0
    cube = yield_kt ** (1 / 3)
    return Effects(
        yield_kt=yield_kt, burst=burst,
        fireball_km=_K["fireball"] * yield_kt ** 0.4 * (1.25 if burst == "ground" else 1.0),
        psi20_km=_K["psi20"] * cube * f,
        psi5_km=_K["psi5"] * cube * f,
        psi1_km=_K["psi1"] * cube * f,
        thermal3_km=_K["thermal3"] * yield_kt ** 0.41,
        fallout="heavy local fallout" if burst == "ground" else "little local fallout",
    )


def ring_area_km2(radius_km: float) -> float:
    return math.pi * radius_km ** 2


# ------------------------------------------------------------------ geometry


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))


def initial_bearing_deg(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def flight_minutes(distance_km: float, weapon_class: str) -> float:
    """Approximate flight time. Classes: icbm, slbm, irbm, srbm, cruise, bomber, hypersonic_glide."""
    d = distance_km / 1000
    if weapon_class == "icbm":
        return max(18.0, 4 + 2.6 * d)           # 10,000 km -> 30 min
    if weapon_class == "slbm":
        return max(7.0, 4 + 2.6 * d)            # 2,000 km -> 9 min; 8,000 km -> 25 min
    if weapon_class == "irbm":
        return max(6.0, 3 + 3.0 * d)            # 3,000 km -> 12 min
    if weapon_class == "srbm":
        return max(3.0, 2 + 6.0 * d)            # 500 km -> 5 min
    if weapon_class == "hypersonic_glide":
        return max(6.0, 3 + 4.0 * d)
    if weapon_class == "cruise":
        return distance_km / 850 * 60           # about Mach 0.7
    if weapon_class == "bomber":
        return distance_km / 900 * 60
    raise ValueError(f"unknown weapon class {weapon_class}")


def subsolar_point(when: dt.datetime) -> tuple[float, float]:
    """(lat, lon) of the point where the sun is overhead, good to about a degree. `when` must be timezone-aware."""
    u = when.astimezone(dt.timezone.utc)
    day = u.timetuple().tm_yday + (u.hour + u.minute / 60) / 24
    decl = -23.44 * math.cos(math.radians(360 / 365 * (day + 10)))
    # equation of time (minutes), Spencer approximation
    b = math.radians(360 / 365 * (day - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    solar_noon_utc_min = 720 - eot
    minutes = u.hour * 60 + u.minute + u.second / 60
    lon = -(minutes - solar_noon_utc_min) / 4  # 4 minutes per degree, west negative
    lon = ((lon + 180) % 360) - 180
    return decl, lon


# ------------------------------------------------------------------ scenario


@dataclass
class Strike:
    id: str
    launch_name: str
    launch_lat: float
    launch_lon: float
    target_name: str
    target_lat: float
    target_lon: float
    weapon: str                 # label, e.g. "RS-24 Yars"
    weapon_class: str           # icbm, slbm, ...
    yield_kt: float
    burst: str = "air"
    warheads: int = 1
    launch_offset_min: float = 0.0   # minutes after T-0
    notes: str = ""


@dataclass
class Scenario:
    slug: str
    title: str
    t0_utc: str                           # ISO timestamp of the first launch
    strikes: list[Strike] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)   # [{claim, url, publisher, date}]

    @staticmethod
    def load(path: Path) -> "Scenario":
        j = json.loads(Path(path).read_text(encoding="utf-8"))
        return Scenario(slug=j["slug"], title=j["title"], t0_utc=j["t0_utc"],
                        strikes=[Strike(**s) for s in j["strikes"]], sources=j.get("sources", []))


def compute(sc: Scenario) -> dict:
    t0 = dt.datetime.fromisoformat(sc.t0_utc.replace("Z", "+00:00"))
    sun_lat, sun_lon = subsolar_point(t0)
    rows = []
    for s in sc.strikes:
        d = haversine_km(s.launch_lat, s.launch_lon, s.target_lat, s.target_lon)
        fm = flight_minutes(d, s.weapon_class)
        e = effects(s.yield_kt, s.burst)
        rows.append({
            **asdict(s),
            "distance_km": round(d, 1),
            "bearing_deg": round(initial_bearing_deg(s.launch_lat, s.launch_lon, s.target_lat, s.target_lon), 1),
            "flight_min": round(fm, 1),
            "launch_min": s.launch_offset_min,
            "impact_min": round(s.launch_offset_min + fm, 1),
            "effects": e.as_dict(),
            "area_psi5_km2": round(ring_area_km2(e.psi5_km), 1),
        })
    rows.sort(key=lambda r: r["impact_min"])
    total_warheads = sum(r["warheads"] for r in rows)
    total_yield_mt = sum(r["warheads"] * r["yield_kt"] for r in rows) / 1000
    return {
        "slug": sc.slug, "title": sc.title, "t0_utc": t0.isoformat(),
        "sun": {"lat": round(sun_lat, 2), "lon": round(sun_lon, 2)},
        "totals": {"strikes": len(rows), "warheads": total_warheads, "yield_mt": round(total_yield_mt, 2),
                   "first_impact_min": rows[0]["impact_min"] if rows else None,
                   "last_impact_min": rows[-1]["impact_min"] if rows else None},
        "strikes": rows, "sources": sc.sources,
        "model": "Glasstone and Dolan scaling calibrated to NUKEMAP Hiroshima figures; flight times fitted to "
                 "published ranges; all values are estimates for a labelled simulation.",
    }


def compute_file(path: Path) -> Path:
    sc = Scenario.load(path)
    out = Path(path).with_name("scenario.computed.json")
    out.write_text(json.dumps(compute(sc), indent=1, ensure_ascii=False), encoding="utf-8")
    return out
