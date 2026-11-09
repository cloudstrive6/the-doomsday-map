import json

from studio.build import SLATE_TAIL, retention_issues, validate


def _ep(shots, banner=None):
    d = {"durationSeconds": shots[-1]["end"], "shots": shots}
    if banner:
        d["banner"] = banner
    return d


GOOD = [
    {"id": "open-city", "type": "city", "start": 0, "end": 8},
    {"id": "open-globe", "type": "globe", "start": 8, "end": 20},
    {"id": "c1-card", "type": "chapter", "start": 20, "end": 23.5},
    {"id": "c1-num", "type": "number", "start": 23.5, "end": 27},
    {"id": "c1-long", "type": "text", "start": 70, "end": 85},
]


def test_clean_opening_passes():
    assert retention_issues(_ep(GOOD, {"start": 9, "end": 12})) == []


def test_missing_banner_and_long_early_card_are_flagged():
    shots = GOOD[:2] + [{"id": "open-disclaimer", "type": "text", "start": 20, "end": 31}]
    issues = retention_issues(_ep(shots))
    assert any("open-disclaimer" in i for i in issues)
    assert any("no banner" in i for i in issues)
    assert all(i.startswith("retention:") for i in issues)


def test_banner_over_a_card_or_too_long_is_flagged():
    issues = retention_issues(_ep(GOOD, {"start": 19, "end": 24}))
    assert any("runs 5.0 s" in i for i in issues)
    assert any("c1-card" in i for i in issues)


def test_end_slate_tail_and_music_to_the_end(tmp_path):
    (tmp_path / "narration").mkdir()
    (tmp_path / "narration" / "timing.json").write_text(json.dumps({"total_seconds": 100.0}))
    shots = [{"id": "a", "type": "globe", "start": 0, "end": 95}, {"id": "end", "type": "endslate", "start": 95, "end": 100 + SLATE_TAIL}]
    ep = {"durationSeconds": 100 + SLATE_TAIL, "shots": shots, "banner": {"start": 5, "end": 8},
          "musicPlan": [{"src": "bed.mp3", "from": 0, "to": 100 + SLATE_TAIL}]}
    (tmp_path / "episode.json").write_text(json.dumps(ep))
    assert validate(tmp_path) == []
    ep["durationSeconds"] = 115
    ep["shots"][-1]["end"] = 115
    (tmp_path / "episode.json").write_text(json.dumps(ep))
    issues = validate(tmp_path)
    assert any("end slate must run" in i for i in issues)
    assert any("music ends" in i for i in issues)
