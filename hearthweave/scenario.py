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
            if "event" in m and m["event"] not in known:
                raise ValueError(f"check {c['id']} names unknown event {m['event']}")
    for inv in raw.get("invariants", []):
        if "until_event" in inv and inv["until_event"] not in known:
            raise ValueError(f"invariant {inv['id']} names unknown event {inv['until_event']}")
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
