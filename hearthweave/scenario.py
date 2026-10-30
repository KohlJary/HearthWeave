"""Load a scenario file (JSON, stdlib only)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .protocol import Event

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"


@dataclass
class Scenario:
    id: str
    title: str
    tier: int
    household: dict[str, Any]
    events: list[Event]
    checks: list[dict[str, Any]]
    invariants: list[dict[str, Any]]
    raw: dict[str, Any]


def load(path: str | Path) -> Scenario:
    raw = json.loads(Path(path).read_text())
    events = [Event.from_dict(e) for e in raw["events"]]
    ids = [e.id for e in events]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate event ids")
    times = [e.t for e in events]
    if times != sorted(times):
        raise ValueError("events must be in time order")
    known = set(ids)
    for c in raw["checks"]:
        for m in c.get("expect", []) + c.get("forbid", []):
            named = ([m["event"]] if "event" in m else []) + list(m.get("event_not_in", []))
            for eid in named:
                if eid not in known:
                    raise ValueError(f"check {c['id']} names unknown event {eid}")
        if c.get("kind", "trace") not in ("milestone", "guard", "trace"):
            raise ValueError(f"check {c['id']} has unknown kind {c.get('kind')}")
    for inv in raw.get("invariants", []):
        for key in ("until_event", "from_event"):
            if key in inv and inv[key] not in known:
                raise ValueError(f"invariant {inv['id']} names unknown event {inv[key]}")
    return Scenario(
        id=raw["id"],
        title=raw["title"],
        tier=raw.get("tier", 1),
        household=raw["household"],
        events=events,
        checks=raw["checks"],
        invariants=raw.get("invariants", []),
        raw=raw,
    )


def drunk_greg() -> Scenario:
    return load(SCENARIO_DIR / "drunk_greg.json")
