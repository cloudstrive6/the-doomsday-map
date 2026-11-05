import datetime as dt

from studio import scenario as S


def test_hiroshima_calibration():
    e = S.effects(15, "air")
    assert abs(e.psi5_km - 1.67) < 0.01
    assert abs(e.psi1_km - 4.52) < 0.01
    assert abs(e.thermal3_km - 1.91) < 0.01
    assert abs(e.fireball_km - 0.18) < 0.005


def test_100kt_matches_published_descriptions():
    e = S.effects(100, "air")
    # The Nuclear Clock and Hindcast both describe a 100 kt airburst: fireball under 1 km wide,
    # 5 psi about 3 km, burns past 4 km
    assert 0.35 < e.fireball_km < 0.45
    assert 2.9 < e.psi5_km < 3.3
    assert 4.0 < e.thermal3_km < 4.6


def test_800kt_airburst():
    e = S.effects(800, "air")
    assert 6.0 < e.psi5_km < 6.6          # NUKEMAP 800 kt airburst moderate blast about 6.3 km
    assert 9.5 < e.thermal3_km < 12.5


def test_ground_burst_smaller_blast_heavy_fallout():
    a, g = S.effects(300, "air"), S.effects(300, "ground")
    assert g.psi5_km < a.psi5_km
    assert g.fallout.startswith("heavy")


def test_distances_and_flight_times():
    # Kozelsk (Russia) to Minot AFB (North Dakota): about 8,000 km by great circle
    d = S.haversine_km(54.03, 35.78, 48.42, -101.36)
    assert 7500 < d < 8500
    assert 24 < S.flight_minutes(d, "icbm") < 30
    assert 8 < S.flight_minutes(2000, "slbm") < 10
    assert 4 < S.flight_minutes(500, "srbm") < 6


def test_subsolar_point():
    lat, lon = S.subsolar_point(dt.datetime(2026, 6, 21, 12, 0, tzinfo=dt.timezone.utc))
    assert abs(lat - 23.4) < 0.3
    assert abs(lon) < 3            # near Greenwich at 12:00 UTC on the solstice
    lat2, lon2 = S.subsolar_point(dt.datetime(2026, 12, 21, 0, 0, tzinfo=dt.timezone.utc))
    assert abs(lat2 + 23.4) < 0.3
    assert abs(abs(lon2) - 180) < 3


def test_compute_sorts_by_impact():
    sc = S.Scenario(slug="t", title="t", t0_utc="2026-11-20T11:00:00Z", strikes=[
        S.Strike("a", "Kozelsk", 54.03, 35.78, "Minot AFB", 48.42, -101.36, "RS-24 Yars", "icbm", 100, "ground"),
        S.Strike("b", "Barents Sea", 72.0, 35.0, "Washington DC", 38.9, -77.04, "R-30 Bulava", "slbm", 100, "air",
                 launch_offset_min=5),
    ])
    out = S.compute(sc)
    assert out["totals"]["warheads"] == 2
    assert out["strikes"][-1]["impact_min"] >= out["strikes"][0]["impact_min"]


def test_conventional_strike_has_no_nuclear_effects():
    from studio.scenario import Scenario, Strike, compute
    sc = Scenario(slug="t", title="t", t0_utc="2026-12-15T20:10:00Z", strikes=[
        Strike(id="c", launch_name="a", launch_lat=25.0, launch_lon=114.5, target_name="b", target_lat=13.58,
               target_lon=144.93, weapon="DF-26", weapon_class="irbm", yield_kt=0, burst="conventional"),
        Strike(id="n", launch_name="a", launch_lat=25.0, launch_lon=114.5, target_name="b", target_lat=23.8,
               target_lon=128.0, weapon="DF-26", weapon_class="irbm", yield_kt=10, burst="air")])
    out = compute(sc)
    conv = next(r for r in out["strikes"] if r["id"] == "c")
    assert conv["effects"] is None and conv["flight_min"] > 0
    assert out["totals"]["warheads"] == 1 and out["totals"]["yield_mt"] == 0.01
