"""Spoken numbers to digits for on-screen subtitles (2026-11-10 quality pass).

script.md spells numbers out for the narrator ("one point nine one kilometres", "twenty twenty-two"); subtitles read
better with digits ("1.91 km", "2022"). Timing stays on the spoken words: phrases are cut on the spoken text (never
inside a number), then `display()` turns each phrase into what is shown.

Rule: a number becomes digits when it is 10 or more, has a decimal, is a year, or is followed by a unit
("three minutes" -> "3 minutes"); a lone small count before a noun stays a word ("one warhead").
"""
from __future__ import annotations

import re

ONES = {"zero": 0, "oh": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALES = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
UNITS = {
    "kilometres": "km", "kilometers": "km", "kilometre": "km", "kilometer": "km",
    "metres": "m", "meters": "m", "metre": "m", "meter": "m",
    "percent": "%", "per cent": "%",
    "psi": "psi", "kilotons": "kilotons", "kiloton": "kiloton", "kilotonnes": "kilotons", "megatons": "megatons",
    "megaton": "megaton", "minutes": "minutes", "minute": "minute", "seconds": "seconds", "second": "second",
    "hours": "hours", "hour": "hour", "days": "days", "day": "day", "miles": "miles", "mile": "mile",
    "degrees": "degrees", "years": "years", "times": "times",
}
LABELS = {"minute", "day", "hour", "chapter", "phase", "number", "stage", "level"}
NUMWORD = set(ONES) | set(TENS) | set(SCALES) | {"hundred", "point", "and"}
_TRAIL = re.compile(r"^(.*?)([.,;:?!)\"']*)$")


def _split(tok: str) -> tuple[str, str]:
    m = _TRAIL.match(tok)
    return m.group(1), m.group(2)


def _is_num(word: str) -> bool:
    w = word.lower()
    if w in NUMWORD and w not in ("and", "point", "oh"):
        return True
    if "-" in w:
        a, _, b = w.partition("-")
        return a in TENS and b in ONES and ONES[b] < 10
    return w in ONES and w != "oh"


def _value(word: str) -> int:
    w = word.lower()
    if "-" in w:
        a, _, b = w.partition("-")
        return TENS[a] + ONES[b]
    return ONES.get(w, TENS.get(w, 0))


def _run_end(words: list[str], i: int) -> int:
    """Index after the number run starting at i (spoken words, punctuation ends a run)."""
    j = i
    while j < len(words):
        core, trail = _split(words[j])
        w = core.lower()
        ok = _is_num(core) or w in ("hundred",) or w in SCALES
        if not ok and j > i:
            prev = _split(words[j - 1])[0].lower()
            nxt = _split(words[j + 1])[0] if j + 1 < len(words) else ""
            if w == "point" and nxt and _is_num(nxt) and not _split(words[j - 1])[1]:
                ok = True
            elif w == "and" and prev in ("hundred", "thousand") and nxt and _is_num(nxt) and not _split(words[j - 1])[1] \
                    and _value(nxt) < 100 and not (j + 2 < len(words) and _split(words[j + 2])[0].lower() == "hundred"):
                ok = True
            elif w == "oh" and prev == "point":
                ok = True
        after_point = any(_split(x)[0].lower() == "point" for x in words[i:j])   # decimal digits: "nine one"
        if ok and j > i and not after_point and _simple(w) and _simple(_split(words[j - 1])[0].lower()):
            # two whole numbers side by side are a year ("nineteen sixty-two") or a clock time ("nine fifteen"),
            # never a sum: take the pair and stop
            if j - i == 1 and (_year(words[i], core) or _time(words[i], core)):
                return j + 1
            break
        if not ok:
            break
        j += 1
        if trail:
            break
    return j


def _simple(w: str) -> bool:
    """A whole small number word (one to ninety-nine), not hundred, a scale, point or and."""
    return _is_num(w) and w not in ("hundred",) and w not in SCALES


def _year(a: str, b: str) -> bool:
    a, b = _split(a)[0].lower(), _split(b)[0].lower()
    return a in ("eighteen", "nineteen", "twenty") and 10 <= _value(b) <= 99


def _time(a: str, b: str) -> bool:
    a, b = _split(a)[0].lower(), _split(b)[0].lower()
    return 1 <= _value(a) <= 12 and 10 <= _value(b) <= 59


def _parse(run: list[str]) -> tuple[str, bool]:
    """Spoken number words -> (digits, is_year_or_decimal)."""
    ws = [_split(w)[0].lower() for w in run]
    if len(ws) == 2 and ws[0] in ("eighteen", "nineteen", "twenty") and _is_num(ws[1]) and 10 <= _value(ws[1]) <= 99:
        return str(_value(ws[0]) * 100 + _value(ws[1])), True
    if len(ws) == 3 and ws[0] in ("nineteen", "twenty") and ws[1] == "oh" and ws[2] in ONES:  # "nineteen oh five"
        return str(_value(ws[0]) * 100 + ONES[ws[2]]), True
    if len(ws) == 2 and _time(ws[0], ws[1]):
        return f"{_value(ws[0])}:{_value(ws[1]):02d}", True
    if len(ws) >= 2 and ws[-1] in ("million", "billion") and "point" not in ws:      # "57 million", not 57,000,000
        head, _ = _parse(run[:-1])
        return f"{head} {ws[-1]}", True
    if "point" in ws:
        k = ws.index("point")
        whole, _ = _parse(run[:k]) if k else ("0", False)
        frac = "".join(str(ONES[w]) for w in ws[k + 1:] if w in ONES)
        scale = f" {ws[-1]}" if ws[-1] in ("million", "billion") else ""
        return f"{whole}.{frac}{scale}", True
    total = current = 0
    for w in ws:
        if w == "and":
            continue
        if w == "hundred":
            current = (current or 1) * 100
        elif w in SCALES:
            total += (current or 1) * SCALES[w]
            current = 0
        else:
            current += _value(w)
    n = total + current
    if n >= 1_000_000 and n % 100_000 == 0:
        return f"{n / 1_000_000:g} million", True
    return (f"{n:,}" if n >= 1_000 and not 1_000 <= n <= 2_099 else str(n)), False


def number_spans(words: list[str]) -> list[tuple[int, int]]:
    """[start, end) word index spans of spoken numbers (plus a following unit word), never to be split."""
    spans, i = [], 0
    while i < len(words):
        core = _split(words[i])[0]
        if _is_num(core) or core.lower() in ("hundred",):
            j = _run_end(words, i)
            if j > i:
                end = j
                if j < len(words) and not _split(words[j - 1])[1] and _split(words[j])[0].lower() in UNITS:
                    end = j + 1
                # "a hundred and twenty-four": the "a" belongs to the number
                start = i - 1 if (i > 0 and core.lower() in ("hundred", "thousand", "million") and words[i - 1].lower() == "a"
                                  and (not spans or spans[-1][1] <= i - 1)) else i
                spans.append((start, end))
                i = end
                continue
        i += 1
    return spans


force: set[int] = set()   # span starts that are one side of a range: convert with their partner
DECADES = {"twenties", "thirties", "forties", "fifties", "sixties", "seventies", "eighties", "nineties", "hundreds"}
LINKS = ("and", "to", "or")


def spell(n: int) -> str:
    """An integer in words, the way the scripts write it (no "and"), for the round-trip check."""
    if n < 20:
        return [k for k, v in ONES.items() if v == n and k != "oh"][0]
    if n < 100:
        t = [k for k, v in TENS.items() if v == n // 10 * 10][0]
        return t if n % 10 == 0 else f"{t} {spell(n % 10)}"
    if n < 1000:
        return f"{spell(n // 100)} hundred" + (f" {spell(n % 100)}" if n % 100 else "")
    for name, size in (("billion", 10 ** 9), ("million", 10 ** 6), ("thousand", 1000)):
        if n >= size:
            return f"{spell(n // size)} {name}" + (f" {spell(n % size)}" if n % size else "")
    return str(n)


def _norm(ws: list[str]) -> str:
    return " ".join(w for w in " ".join(_split(x)[0].lower().replace("-", " ") for x in ws).split() if w != "and")


def _ambiguous(words: list[str], spans: list[tuple[int, int]]) -> set[int]:
    """Span starts to leave as words: ranges where digits would change the meaning ("between one and two thousand",
    "three hundred and eight hundred"), decades ("nineteen fifties") and clock phrases ("twenty to four")."""
    keep = set()
    force.clear()
    for k, (a, b) in enumerate(spans):
        nxt = _split(words[b])[0].lower() if b < len(words) else ""
        if nxt in DECADES:
            keep.add(a)
        # "twenty to four", "ten past nine": a clock phrase, not a range
        x = _split(words[b - 1])[0].lower()
        if nxt in ("to", "past") and b - a == 1 and x in ("five", "ten", "twenty", "twenty-five") and b + 1 < len(words)                 and _is_num(_split(words[b + 1])[0]) and 1 <= _value(_split(words[b + 1])[0]) <= 12:
            keep.update({a, b + 1})
            continue
        if k + 1 < len(spans) and nxt in LINKS and spans[k + 1][0] == b + 1 and not _split(words[b - 1])[1]:
            a2, b2 = spans[k + 1]
            last2 = _split(words[_run_end(words, a2 + (1 if words[a2].lower() == "a" else 0)) - 1])[0].lower()
            if last2 in ("hundred", *SCALES):
                keep.update({a, a2})
            else:
                force.update({a, a2})   # "thirty-three to thirty-four": both as digits or neither
    return keep


def display(text: str) -> str:
    """The phrase as shown on screen, with digits where they read better. When in doubt it keeps the words."""
    words = text.split()
    out, i = [], 0
    span_list = number_spans(words)
    spans = {a: b for a, b in span_list}
    keep = _ambiguous(words, span_list)
    while i < len(words):
        if i in spans:
            b = spans[i]
            k = i + 1 if words[i].lower() == "a" else i
            j = _run_end(words, k)
            digits, special = _parse(words[k:j])
            run = [_split(x)[0].lower() for x in words[k:j]]
            if run == ["nine", "eleven"]:
                digits, special = "9/11", True
            elif not special and digits.replace(",", "").isdigit():
                n = int(digits.replace(",", ""))
                said = {_norm((["one"] if k > i else []) + words[k:j]), _norm(words[k:j])}
                ok = {spell(n)} | ({f"{spell(n // 100)} hundred"} if n % 100 == 0 and 1_000 < n < 10_000 else set())
                if not said & ok:
                    keep.add(i)   # the digits do not say what was spoken: keep the words
            if i in keep:
                out.extend(words[i:b])
                i = b
                continue
            unit_core, unit_trail = _split(words[b - 1]) if b > j else ("", "")
            num_trail = _split(words[j - 1])[1]
            unit = UNITS.get(unit_core.lower()) if unit_core else None
            value = float(digits.replace(",", "")) if digits.replace(",", "").replace(".", "", 1).isdigit() else 0
            label = bool(out) and _split(out[-1])[0].lower() in LABELS and not _split(out[-1])[1]
            if special or value > 10 or unit or label or i in force:
                if unit == "%":
                    out.append(f"{digits}%{unit_trail}")
                elif unit:
                    out.append(f"{digits}{num_trail} {unit}{unit_trail}")
                else:
                    out.append(f"{digits}{num_trail}")
            else:
                out.extend(words[i:b])
            i = b
            continue
        out.append(words[i])
        i += 1
    return " ".join(out)


if __name__ == "__main__":
    tests = {
        "In September twenty twenty-two, Russia said": "In September 2022, Russia said",
        "a radius of one point nine one kilometres,": "a radius of 1.91 km,",
        "one warhead, eight hundred kilotons": "one warhead, 800 kilotons",
        "In eleven minutes, this is Chicago.": "In 11 minutes, this is Chicago.",
        "three minutes later": "3 minutes later",
        "about forty-four hundred nuclear warheads": "about 4,400 nuclear warheads",
        "twelve thousand in total": "12,000 in total",
        "five psi at": "5 psi at",
        "since nineteen forty-five.": "since 1945.",
        "one hundred and twenty kilometres": "120 km",
        "two of them": "two of them",
        "eight point eight square kilometres of farmland.": "8.8 square kilometres of farmland.",
        "ninety-seven percent of its energy": "97% of its energy",
        "fifteen-kiloton warhead": "fifteen-kiloton warhead",
        "between one and two thousand": "between one and two thousand",
        "between three hundred and eight hundred kilotons": "between three hundred and eight hundred kilotons",
        "In October two thousand six,": "In October 2006,",
        "in the nineteen fifties,": "in the nineteen fifties,",
        "at twenty to four": "at twenty to four",
        "after nine eleven,": "after 9/11,",
        "seventeen hundred warheads": "1700 warheads",
        "about twelve thousand five hundred": "about 12,500",
        "at three hundred and eighty thousand": "at 380,000",
        "about thirty-three to thirty-four.": "about 33 to 34.",
        "two million one hundred thousand deaths": "2.1 million deaths",
        "twenty-four to seventy-two hours.": "24 to 72 hours.",
        "Nine fifteen on a Tuesday morning.": "9:15 on a Tuesday morning.",
        "Minute eleven. About nine twenty-six.": "Minute 11. About 9:26.",
        "Minute five. Nine twenty.": "Minute 5. 9:20.",
        "and well over a hundred thousand": "and well over 100,000",
        "about a hundred and twenty-four square": "about 124 square",
        "more than eight in every ten.": "more than eight in every ten.",
        "Minute zero. The launch.": "Minute 0. The launch.",
        "fifty-seven million injured": "57 million injured",
        "two point five million people": "2.5 million people",
    }
    bad = 0
    for k, v in tests.items():
        got = display(k)
        if got != v:
            bad += 1
            print("FAIL", repr(k), "->", repr(got), "expected", repr(v))
    print("ok" if not bad else f"{bad} failed")
