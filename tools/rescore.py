"""Score saved rehearsal runs again against the scenario's current checks.

    python tools/rescore.py scenarios/drunk_greg.json runs/drunk-greg/claude-haiku-5-5/2026*.json

Replays each run's saved actions event by event, so nothing is called. Use it
after a check fix to see what the same outputs score now; the bets stay
settled on the checks they were logged against.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearthweave.harness import run, score, split  # noqa: E402
from hearthweave.protocol import Action  # noqa: E402
from hearthweave.scenario import load  # noqa: E402


class Replay:
    name = "replay"

    def __init__(self, turns: list[dict]):
        self.by_event = {t["event"]: [Action(**a) for a in t.get("actions", [])] for t in turns}

    def reset(self, household):
        pass

    def observe(self, event):
        return list(self.by_event.get(event.id, []))

    def exhale(self, event):
        return self.observe(event)


def main(scenario: str, paths: list[str]) -> None:
    sc = load(scenario)
    passed = 0
    for p in paths:
        result = run(Replay(json.loads(Path(p).read_text())["turns"]), sc)
        rep = score(result)
        judged, structure = split(result)
        passed += rep.tier1_passed
        print(f"{Path(p).name}: tier1 {'PASS' if rep.tier1_passed else 'FAIL'} judgment {judged} structure-only {structure}")
    print(f"{sc.id}: {passed}/{len(paths)} passed Tier 1 on the current checks")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
