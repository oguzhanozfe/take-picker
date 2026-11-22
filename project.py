"""Rank recorded takes by ordered script coverage, logged defects and timing."""

import re

import math


def items(data, key, *, allow_empty=False):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 500:
        raise ValueError(f"{key} must be a list of up to 500 entries")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Every entry in {key} must be an object")
    return value


def number(value, field, *, positive=False):
    if type(value) not in (int, float) or not 0 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite nonnegative number at most 1e12")
    if positive and value == 0:
        raise ValueError(f"{field} must be greater than zero")
    return value


def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


TITLE = "Take Picker"
DESCRIPTION = "Rank repeated takes using ordered script coverage, target duration and logged recording defects."
PROMPT = "Recommend one take for the edit and identify any necessary pickup. Explain the tradeoff using its coverage, duration and explicitly logged defects. Do not infer delivery quality from transcripts alone."


def words(value, field):
    parts = re.findall(r"[^\W_]+(?:['’][^\W_]+)*", label(value, field).casefold().replace("’", "'"), flags=re.UNICODE)
    if not 1 <= len(parts) <= 300:
        raise ValueError(f"{field} must contain 1 to 300 words")
    return parts


def ordered_matches(script, spoken):
    # Longest common subsequence credits a script token at most once, in order.
    previous = [0] * (len(spoken) + 1)
    for word in script:
        current = [0]
        for index, heard in enumerate(spoken, start=1):
            current.append(previous[index - 1] + 1 if word == heard else max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def analyze(data: dict) -> dict:
    takes = items(data, "takes")
    if len(takes) > 80:
        raise ValueError("Compare at most 80 takes per request")
    script = words(data.get("script"), "script")
    target = number(data.get("target_seconds"), "target_seconds", positive=True)
    ranking = []
    seen = set()
    for take in takes:
        name = label(take.get("id"), "take id")
        if name in seen:
            raise ValueError("Take IDs must be unique")
        seen.add(name)
        spoken = words(take.get("transcript"), "transcript")
        duration = number(take.get("seconds"), "seconds", positive=True)
        penalty, blocked, notes = 0, False, []
        for defect in items(take, "defects", allow_empty=True):
            severity = label(defect.get("severity"), "severity").lower()
            if severity not in {"minor", "major", "blocking"}:
                raise ValueError("Defect severity must be minor, major or blocking")
            notes.append(f"{severity}: {label(defect.get('note'), 'defect note')}")
            penalty += {"minor": 5, "major": 15, "blocking": 30}[severity]
            blocked |= severity == "blocking"
        matches = ordered_matches(script, spoken)
        recall = matches / len(script)
        precision = matches / len(spoken)
        timing = max(0, (target - abs(duration - target)) / target)
        score = max(0, 70 * recall + 10 * precision + 20 * timing - penalty)
        row = {"Take": name, "Script covered (%)": round(recall * 100, 1), "Duration (s)": duration,
               "Score": round(score, 1), "Logged defects": "; ".join(notes) or "None"}
        ranking.append((blocked, -score, name, row))
    ranking.sort(key=lambda entry: entry[:3])
    available = sum(not entry[0] for entry in ranking)
    summary = f"{ranking[0][2]} leads the {available} eligible takes." if available else "All takes have blocking defects; record a pickup."
    return {"summary": summary, "metrics": {"Takes": len(takes), "Eligible": available,
            "Script words": len(script), "Target (s)": target}, "rows": [entry[3] for entry in ranking]}
