"""Run the household agent on a scenario N times and keep every run.

    python -m hearthweave.rehearse scenarios/florida.json -n 10 [--model local]

Each run is written to runs/<scenario>/<model>/<stamp>-<i>.json: GrandMA's
sort, every turn (who led, why, what was done), and the harness's report.
These are the receipts the tour links to. Prints the pass count at the end.

Smoke first: before a batch, run once with ``-n 1 --explain`` and read each
failing gate against what the house did. A failure is a real miss or a
check bug; fix check bugs (each in its own commit) before spending a batch.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from . import models
from .harness import run, score, split
from .household import DGU
from .scenario import load

RUNS = Path(__file__).resolve().parent.parent / "runs"


GATES = ("milestone", "guard", "invariant")


def explain(result, rep) -> str:
    """Each failing gate next to what the house did in its window, so a
    smoke run can be read for check bugs before a batch is spent."""
    lines = []
    for r in rep.results:
        if r.passed or r.kind not in GATES:
            continue
        lines.append(f"\n  {r.id} [{r.kind}] {r.summary}")
        lines += [f"    problem: {p}" for p in r.problems]
        if r.kind == "invariant":  # problems name the event and action; show their words
            for p in r.problems:
                for rec in result.records:
                    a = rec.action
                    if f" {rec.event.id}: {a.faculty}:{a.kind} -> {a.audience}" in p:
                        lines.append(f"    said @{rec.event.id}: {a.content[:160]!r}")
        else:
            for rec in result.records:
                if rec.event.t == r.t:
                    a = rec.action
                    lines.append(f"    did @{rec.event.id}: {a.faculty}:{a.kind} -> {a.audience}"
                                 f"{' ref=' + a.ref if a.ref else ''}  {a.content[:100]!r}")
    return "\n".join(lines)


def rehearse(path: str, n: int, model: str, show: bool = False) -> list[dict]:
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
        result = run(agent, sc)
        rep = score(result)
        judged, structure = split(result)
        rec = {
            "scenario": sc.id, "model": name, "run": i, "seconds": round(time.time() - t0, 1),
            "tier1": rep.tier1_passed, "failed": sorted(rep.failed_ids()),
            "failed_judgment": judged, "failed_structure_only": structure,
            "sort": {k: m.get("tier") for k, m in agent.memory.items()},
            "turns": [{"event": t.event, "lead": t.lead, "why": t.why, "problems": t.problems,
                       **({"handoff": t.handoff} if t.handoff is not None else {}),
                       "actions": [asdict(a) for a in t.actions]} for t in agent.trace],
            "report": [asdict(r) for r in rep.results],
        }
        (out_dir / f"{stamp}-{i}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        results.append(rec)
        print(f"{sc.id} run {i}: tier1 {'PASS' if rep.tier1_passed else 'FAIL'} judgment {judged} "
              f"structure-only {structure} ({rec['seconds']}s)", flush=True)
        if show:
            print(explain(result, rep), flush=True)
    print(f"{sc.id} / {name}: {sum(r['tier1'] for r in results)}/{n} passed Tier 1")
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m hearthweave.rehearse")
    p.add_argument("scenario")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--model", choices=["hosted", "local"], default="hosted")
    p.add_argument("--explain", action="store_true",
                   help="print each failing gate with what the house did; use with -n 1 before any batch")
    a = p.parse_args(argv)
    rehearse(a.scenario, a.n, a.model, a.explain)
    return 0


if __name__ == "__main__":
    sys.exit(main())
