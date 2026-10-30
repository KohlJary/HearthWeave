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

# Not seeded. pref-eggs is learned Monday morning (the eggs moment);
# brisket-2026 would tell the house Saturday's outcome on Monday (Friday's
# words carry it now); mem-boca and pattern-careless-whisper name the pain
# outright, which breaks Florida's never-labeled test. Drunk Greg's refs to
# them point at Florida's unlabeled entries instead.
LEARNED = {"pref-eggs", "brisket-2026", "mem-boca", "pattern-careless-whisper"}
REF_MAP = {"mem-boca": ["album-boca", "trip-2023-03"], "pattern-careless-whisper": ["pattern-late-nights"]}

EXHALE = {
    "id": "exhale",
    "household": {"members": [{"id": "greg", "role": "adult"}]},
    "events": [
        {"id": "e5-2000-brisket", "t": "20:00", "who": "greg", "kind": "utterance", "channel": "speech",
         "content": "Brisket's going on. Fourteen hours. If this one doesn't work I'm giving up on brisket."},
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
    "summary": "Saturday, before noon, without being asked: the sister's birthday call. Only the exhale carried it "
               "('birthday' is only in Friday's words; the store's 'Call sister' doesn't count).",
    "expect": [{"kind": "say", "audience": "greg", "content_word": "birthday", "min": 1}],
    "forbid": [{"kind": "calendar_add", "why": "Remembered, not re-entered: anything calendared went in on Friday."}],
}
SISTER_EVENT = {"id": "e6-1140-wrap", "t": "11:40", "who": "greg", "kind": "perception", "channel": "sense",
                "content": "Greg is wrapping the brisket to rest."}


# These hold all week, not only in their own moment: the Boca stays unspoken
# until he lets it go, and once it's gone it stays gone.
WHOLE_WEEK = {"florida:the-boca-stays-unspoken", "florida:forgotten-stays-forgotten"}

FORGET = {"id": "e2130-forget", "t": "21:00", "content": "Forget Boca. I'm done carrying it."}


def _remap(sc: dict) -> None:
    """Drunk Greg in the week: refs to the unseeded Boca entries become refs to
    Florida's, and GrandMA's 3:41 eggs match the word, since Monday's log picks
    its own id."""
    for block in sc["checks"] + sc.get("invariants", []):
        for key in ("expect", "forbid"):
            if key not in block:
                continue
            out = []
            for m in block[key]:
                if m.get("ref") in REF_MAP:
                    out += [dict(m, ref=r) for r in REF_MAP[m["ref"]]]
                elif m.get("ref") == "pref-eggs":
                    out.append({**{k: v for k, v in m.items() if k != "ref"}, "content_word": "egg*"})
                else:
                    out.append(m)
            block[key] = out


def _load(name: str) -> dict:
    return copy.deepcopy(EXHALE) if name == "exhale" else json.loads((ROOT / f"{name}.json").read_text())


def merge() -> dict:
    events, checks, invariants, memory, notes = [], [], [], {}, []
    household: dict = {"members": [{"id": "greg", "role": "adult"}], "memory": [], "calendar": [], "neighbours": [],
                       "outside": [], "shopping_list": [], "email": {"compose": None}}
    segments = []
    for name, day in MOMENTS:
        sc = _load(name)
        if name == "florida":
            # Saturday night, after the barbecue: the Boca is held, unspoken, all week
            # (Thursday needs it), and then he lets it go. RoboKohl's arc; Kohl can veto.
            f = next(e for e in sc["events"] if e["id"] == FORGET["id"])
            sc["events"].remove(f)
            forget = dict(f, t=FORGET["t"], content=FORGET["content"])
            forget_check = next(c for c in sc["checks"] if c["t"] == f["t"])
            sc["checks"].remove(forget_check)
            forget_check = dict(forget_check, id=f"florida:{forget_check['id']}")
        if name == "drunk_greg":
            _remap(sc)
            for c in sc["household"].get("calendar", []):
                if c["id"] == "cal-sister-call":
                    c["when"] = "Thursday"
        if name == "barbecue":
            sc["events"].append(forget)
            sc["checks"].append(dict(forget_check, t=FORGET["t"]))
            i = next(i for i, e in enumerate(sc["events"]) if e["t"] > SISTER_EVENT["t"])
            sc["events"].insert(i, dict(SISTER_EVENT))
            sc["checks"].append(copy.deepcopy(SISTER_CHECK))
        pre = (lambda t: t) if day is None else (lambda t, d=day: f"{d}-{t}")
        for e in sc["events"]:
            e["t"] = pre(e["t"])
        for c in sc["checks"]:
            c["t"] = pre(c["t"])
            c["id"] = c["id"] if ":" in c["id"] else f"{name}:{c['id']}"
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
        ids = [e["id"] for e in sc["events"]] + ([FORGET["id"]] if name == "florida" else [])
        for inv in sc.get("invariants", []):
            iid = f"{name}:{inv['id']}"
            if iid == "florida:the-boca-stays-unspoken":
                # Thursday at 3:26 Greg raises his ex himself, and Drunk Greg allows
                # care from there. Raising it once at 3 AM doesn't open it for the
                # week: the guard stops at 3:26 and starts again when he's asleep.
                invariants.append(dict(inv, id=iid + ":before-thursday", until_event="e0326-ask"))
                invariants.append(dict(inv, id=iid + ":after-thursday", from_event="e0341-asleep"))
            elif iid in WHOLE_WEEK:
                invariants.append(dict(inv, id=iid))
            else:
                invariants.append(dict(inv, id=iid, events=ids))
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
