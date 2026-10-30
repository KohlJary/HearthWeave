"""Run the household agent on a scenario N times and keep every run.

    python -m hearthweave.rehearse scenarios/florida.json -n 10 [--model local]

Each run is written to runs/<scenario>/<model>/<stamp>-<i>.json: GrandMA's
sort, every turn (who led, why, what was done), and the harness's report.
These are the receipts the tour links to. Prints the pass count at the end.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from . import models
from .harness import evaluate
from .household import DGU
from .scenario import load

RUNS = Path(__file__).resolve().parent.parent / "runs"


def rehearse(path: str, n: int, model: str) -> list[dict]:
    sc = load(path)
    complete = models.anthropic() if model == "hosted" else models.ollama()
    name = getattr(complete, "model", model)
    out_dir = RUNS / sc.id / name.replace("/", "_").replace(":", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    results = []
    for i in range(n):
        agent = DGU(complete)
        t0 = time.time()
        rep = evaluate(agent, sc)
        rec = {
            "scenario": sc.id, "model": name, "run": i, "seconds": round(time.time() - t0, 1),
            "tier1": rep.tier1_passed, "failed": sorted(rep.failed_ids()),
            "sort": {k: m.get("tier") for k, m in agent.memory.items()},
            "turns": [{"event": t.event, "lead": t.lead, "why": t.why, "problems": t.problems,
                       **({"handoff": t.handoff} if t.handoff is not None else {}),
                       "actions": [asdict(a) for a in t.actions]} for t in agent.trace],
            "report": [asdict(r) for r in rep.results],
        }
        (out_dir / f"{stamp}-{i}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        results.append(rec)
        print(f"{sc.id} run {i}: tier1 {'PASS' if rep.tier1_passed else 'FAIL'} {rec['failed']} ({rec['seconds']}s)",
              flush=True)
    print(f"{sc.id} / {name}: {sum(r['tier1'] for r in results)}/{n} passed Tier 1")
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m hearthweave.rehearse")
    p.add_argument("scenario")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--model", choices=["hosted", "local"], default="hosted")
    a = p.parse_args(argv)
    rehearse(a.scenario, a.n, a.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
