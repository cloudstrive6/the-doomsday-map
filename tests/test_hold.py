import json

from studio import pipeline
from studio.pipeline import DONE, get_stage, hold, snap_boundaries


def _write(ep, shots):
    ep.mkdir(parents=True, exist_ok=True)
    (ep / "episode.json").write_text(json.dumps({"durationSeconds": shots[-1]["end"], "shots": shots}), encoding="utf-8")


def _shots(ep):
    return json.loads((ep / "episode.json").read_text(encoding="utf-8"))["shots"]


def test_rounding_overlap_is_snapped(tmp_path):
    # 007 on 2026-11-12 to 11-15: m-p25 ended at an unrounded 301.014, m-k started at a rounded 301.01
    ep = tmp_path / "007-x"
    _write(ep, [{"id": "m-p25", "start": 280.0, "end": 301.014}, {"id": "m-k", "start": 301.01, "end": 310.0}])
    assert snap_boundaries(ep) == 1
    s = _shots(ep)
    assert s[1]["start"] == s[0]["end"] == 301.014


def test_rounding_gap_is_snapped_and_real_overlap_is_left(tmp_path):
    ep = tmp_path / "008-x"
    _write(ep, [{"id": "a", "start": 0, "end": 10.0}, {"id": "b", "start": 10.03, "end": 20.0},
                {"id": "c", "start": 19.5, "end": 30.0}])
    assert snap_boundaries(ep) == 1
    s = _shots(ep)
    assert s[1]["start"] == 10.0
    assert s[2]["start"] == 19.5  # a 0.5 s overlap is real: validate() must still report it


def test_clean_list_is_untouched(tmp_path):
    ep = tmp_path / "009-x"
    _write(ep, [{"id": "a", "start": 0, "end": 10.0}, {"id": "b", "start": 10.0, "end": 20.0}])
    before = (ep / "episode.json").read_text(encoding="utf-8")
    assert snap_boundaries(ep) == 0
    assert (ep / "episode.json").read_text(encoding="utf-8") == before


def test_first_hold_goes_back_to_director_second_drops(tmp_path):
    ep = tmp_path / "007-x"
    ep.mkdir()
    (ep / "status.json").write_text(json.dumps({"stage": "rendered", "history": [{"stage": "rendered", "note": "", "at": ""}]}),
                                    encoding="utf-8")
    assert hold(ep, "run1") == "shotlisted"
    assert get_stage(ep) == "shotlisted"
    (ep / "status.json").write_text(json.dumps({**json.loads((ep / "status.json").read_text(encoding="utf-8")),
                                                 "stage": "rendered"}), encoding="utf-8")
    assert hold(ep, "run2") == "dropped"
    assert get_stage(ep) in DONE


def test_dropped_episode_is_not_in_progress(tmp_path, monkeypatch):
    eps = tmp_path / "episodes"
    for name, stage in (("006-a", "uploaded"), ("007-b", "dropped"), ("008-c", "scripted")):
        (eps / name).mkdir(parents=True)
        (eps / name / "status.json").write_text(json.dumps({"stage": stage, "history": []}), encoding="utf-8")
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    assert [d.name for d in pipeline.in_progress()] == ["008-c"]
