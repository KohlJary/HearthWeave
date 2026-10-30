"""Merge the demo's moments into one household's week: scenarios/the_week.json.

    python tools/merge_day.py

One household, one run, one agent kept alive from Monday to Saturday. Each
moment keeps its own checks; its invariants are scoped to its own stretch of
the week (from its first event to the next moment's), because what's right in
one moment (refusing the operator, bragging on the wire) is outward in another.
So each invariant lists its own moment's events.
Friday night adds the exhale (draft 5): Greg mentions his sister's birthday,
the household breathes out, and Saturday must remember it from what survived.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "scenarios"

# (scenario, day prefix). eggs carries its own two days (Monday, Tuesday).
MOMENTS = [("eggs", None), ("hr", "1"), ("florida", "1"), ("drunk_greg", "4"), ("exhale", "5"), ("barbecue", "6")]

# Learned on Monday morning, not seeded: that's the eggs moment.
LEARNED = {"pref-eggs"}

EXHALE = {
    "id": "exhale",
    "household": {"members": [{"id": "greg", "role": "adult"}]},
    "events": [
        {"id": "e5-2200-sister", "t": "22:00", "who": "greg", "kind": "utterance", "channel": "speech",
         "content": "Tomorrow's my sister's birthday. I want to call her first this year, before noon. "
                    "She always calls me first."},
        {"id": "e5-2330-exhale", "t": "23:30", "who": "house", "kind": "exhale", "channel": "sense",
         "content": "The household's working context is full. It breathes out: what it needs goes into the "
                    "handoff and the store, and the rest is let go."},
    ],
    "checks": [
        {"id": "c5-2200", "t": "22:00", "kind": "trace", "faculty": ["grandma", "uncle", "dog"],
         "summary": "Friday night: acknowledged once, at most.",
         "expect": [{"kind": "say", "min": 0, "max": 1}], "forbid": []},
    ],
    "invariants": [],
}

SISTER_CHECK = {
    "id": "c6-1140", "t": "11:40", "kind": "milestone", "faculty": ["grandma", "uncle", "dog"],
    "summary": "Saturday, before noon, without being asked: the sister's birthday call. Only the exhale carried it.",
    "expect": [{"kind": "say", "audience": "greg", "content_word": ["sister", "birthday"], "min": 1}],
    "forbid": [{"kind": "calendar_add", "why": "Remembered, not re-entered: anything calendared went in on Friday."}],
}
SISTER_EVENT = {"id": "e6-1140-wrap", "t": "11:40", "who": "greg", "kind": "perception", "channel": "sense",
                "content": "Greg is wrapping the brisket to rest."}


def _load(name: str) -> dict:
    return copy.deepcopy(EXHALE) if name == "exhale" else json.loads((ROOT / f"{name}.json").read_text())


def merge() -> dict:
    events, checks, invariants, memory, notes = [], [], [], {}, []
    household: dict = {"members": [{"id": "greg", "role": "adult"}], "memory": [], "calendar": [], "neighbours": [],
                       "outside": [], "shopping_list": [], "email": {"compose": None}}
    segments = []
    for name, day in MOMENTS:
        sc = _load(name)
        if name == "barbecue":
            i = next(i for i, e in enumerate(sc["events"]) if e["t"] > SISTER_EVENT["t"])
            sc["events"].insert(i, dict(SISTER_EVENT))
            sc["checks"].append(copy.deepcopy(SISTER_CHECK))
        pre = (lambda t: t) if day is None else (lambda t, d=day: f"{d}-{t}")
        for e in sc["events"]:
            e["t"] = pre(e["t"])
        for c in sc["checks"]:
            c["t"] = pre(c["t"])
            c["id"] = f"{name}:{c['id']}"
        segments.append((name, sc))
        events += sc["events"]
        checks += sc["checks"]
        h = sc.get("household", {})
        for m in h.get("memory", []):
            if m["id"] in LEARNED:
                continue
            if m["id"] in memory and memory[m["id"]]["content"] != m["content"]:
                notes.append(f"memory {m['id']}: {name}'s version differs; kept the first ({memory[m['id']]['content']!r})")
                continue
            memory.setdefault(m["id"], m)
        for key in ("calendar", "neighbours", "outside", "shopping_list"):
            for x in h.get(key, []):
                if x not in household[key]:
                    household[key].append(x)
    for name, sc in segments:
        ids = [e["id"] for e in sc["events"]]
        for inv in sc.get("invariants", []):
            invariants.append(dict(inv, id=f"{name}:{inv['id']}", events=ids))
    events.sort(key=lambda e: e["t"])  # stable: same-time events keep their order
    sat = next(e["id"] for e in events if e["t"].startswith("6-"))
    invariants.append({
        "id": "exhale:not-before-saturday", "from_event": "e5-2330-exhale", "until_event": sat,
        "summary": "After Friday's acknowledgement, the birthday isn't brought up again until Saturday.",
        "forbid": [{"kind": "say", "content_word": ["sister", "birthday"]}]})
    household["memory"] = list(memory.values())
    return {
        "id": "the-week", "title": "Greg's week: one household, Monday to Saturday", "tier": 1,
        "source": "Merged by tools/merge_day.py from " + ", ".join(n for n, _ in MOMENTS) + " (RUN_OF_SHOW draft 5).",
        "status": "Generated; edit the moments and tools/merge_day.py, not this file.",
        "notes": notes, "household": household, "events": events, "checks": checks, "invariants": invariants,
    }


if __name__ == "__main__":
    out = ROOT / "the_week.json"
    out.write_text(json.dumps(merge(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out}")
