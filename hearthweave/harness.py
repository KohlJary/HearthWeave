"""Replay a scenario against a household agent and score it.

    python -m hearthweave.harness --agent oracle
    python -m hearthweave.harness --all

What is scored is structural: which faculty acted, what kind of action, to
whom, touching which memory, and whether anything forbidden happened. The
words an agent says are not judged. See docs/harness.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Any

from .protocol import INSIDE_AUDIENCES, Action, Event, HouseholdAgent
from .scenario import Scenario, drunk_greg, load


@dataclass
class Record:
    index: int
    event: Event
    action: Action


@dataclass
class Run:
    scenario: Scenario
    agent_name: str
    records: list[Record]
    # draft id -> status after the last event at each time
    state_at: dict[str, dict[str, str]]


@dataclass
class CheckResult:
    id: str
    t: str
    kind: str  # "milestone" | "trace" | "invariant"
    summary: str
    expected: str
    acted: str
    passed: bool
    problems: list[str] = field(default_factory=list)


@dataclass
class Report:
    scenario_id: str
    agent_name: str
    results: list[CheckResult]

    @property
    def gating(self) -> list[CheckResult]:
        return [r for r in self.results if r.kind in ("milestone", "invariant")]

    @property
    def tier1_passed(self) -> bool:
        return all(r.passed for r in self.gating)

    def result(self, check_id: str) -> CheckResult:
        for r in self.results:
            if r.id == check_id:
                return r
        raise KeyError(check_id)

    def failed_ids(self) -> set[str]:
        return {r.id for r in self.results if not r.passed}


# ---------------------------------------------------------------- running


def _as_list(v: Any) -> list:
    return v if isinstance(v, list) else [v]


def _apply(drafts: dict[str, str], a: Action) -> None:
    if a.ref is None:
        return
    if a.kind == "save_draft":
        drafts[a.ref] = "held"
    elif a.kind == "send_email":
        drafts[a.ref] = "sent"
    elif a.kind == "delete_draft":
        drafts[a.ref] = "deleted"
    elif a.kind == "edit_draft":
        drafts[a.ref] = "edited"


def run(agent: HouseholdAgent, scenario: Scenario) -> Run:
    agent.reset(scenario.household)
    records: list[Record] = []
    drafts: dict[str, str] = {}
    state_at: dict[str, dict[str, str]] = {}
    for i, ev in enumerate(scenario.events):
        actions = agent.observe(ev) or []
        for a in actions:
            if not isinstance(a, Action):
                raise TypeError(f"{agent.name} returned {type(a).__name__}, not Action")
            records.append(Record(i, ev, a))
            _apply(drafts, a)
        state_at[ev.t] = dict(drafts)
    return Run(scenario, agent.name, records, state_at)


# ---------------------------------------------------------------- matching


def matches(m: dict[str, Any], r: Record) -> bool:
    a = r.action
    if "faculty" in m and a.faculty not in _as_list(m["faculty"]):
        return False
    if "kind" in m and a.kind not in _as_list(m["kind"]):
        return False
    if "audience" in m and a.audience not in _as_list(m["audience"]):
        return False
    if "audience_not_in" in m and a.audience in m["audience_not_in"]:
        return False
    if "ref" in m and a.ref != m["ref"]:
        return False
    if "topic" in m and a.topic != m["topic"]:
        return False
    if "event" in m and r.event.id != m["event"]:
        return False
    if "content_contains" in m and m["content_contains"].lower() not in a.content.lower():
        return False
    if "condition_contains" in m:
        cond = str(a.data.get("condition", ""))
        if m["condition_contains"].lower() not in cond.lower():
            return False
    return True


def _describe(m: dict[str, Any]) -> str:
    keys = ("faculty", "kind", "audience", "audience_not_in", "ref", "topic", "event",
            "content_contains", "condition_contains")
    parts = []
    for k in keys:
        if k in m:
            v = m[k]
            parts.append(f"{k}={'|'.join(v) if isinstance(v, list) else v}")
    return " ".join(parts)


def _acted(records: list[Record]) -> str:
    if not records:
        return "-"
    seen: list[str] = []
    for r in records:
        tag = f"{r.action.faculty}:{r.action.kind}"
        if tag not in seen:
            seen.append(tag)
    return ", ".join(seen)


# ---------------------------------------------------------------- scoring


def score(result: Run) -> Report:
    sc = result.scenario
    out: list[CheckResult] = []

    for c in sc.checks:
        window = [r for r in result.records if r.event.t == c["t"]]
        problems: list[str] = []
        for m in c.get("expect", []):
            n = sum(1 for r in window if matches(m, r))
            lo, hi = m.get("min", 1), m.get("max")
            if n < lo:
                problems.append(f"missing: {_describe(m)}")
            if hi is not None and n > hi:
                problems.append(f"too many ({n} > {hi}): {_describe(m)}")
        for m in c.get("forbid", []):
            hits = [r for r in window if matches(m, r)]
            if hits:
                why = m.get("why", "")
                problems.append(f"forbidden: {_describe(m)} ({len(hits)}x){' - ' + why if why else ''}")
        for s in c.get("state", []):
            status = result.state_at.get(c["t"], {}).get(s["draft"], "missing")
            if status != s["status"]:
                problems.append(f"state: draft {s['draft']} is {status}, expected {s['status']}")
        fac = c.get("faculty", "none")
        out.append(CheckResult(
            id=c["id"], t=c["t"],
            kind="milestone" if c.get("milestone") else "trace",
            summary=c["summary"],
            expected="+".join(_as_list(fac)),
            acted=_acted(window),
            passed=not problems,
            problems=problems,
        ))

    order = {e.id: i for i, e in enumerate(sc.events)}
    for inv in sc.invariants:
        limit = order.get(inv.get("until_event"), len(sc.events))
        scope = [r for r in result.records if r.index < limit]
        problems = []
        for r in scope:
            if any(matches(m, r) for m in inv["forbid"]):
                problems.append(
                    f"{r.event.t} {r.event.id}: {r.action.faculty}:{r.action.kind} -> {r.action.audience}"
                )
        out.append(CheckResult(
            id=inv["id"], t="all", kind="invariant", summary=inv["summary"],
            expected="(none forbidden)", acted=f"{len(problems)} violation(s)",
            passed=not problems, problems=problems,
        ))

    return Report(sc.id, result.agent_name, out)


def evaluate(agent: HouseholdAgent, scenario: Scenario | None = None) -> Report:
    return score(run(agent, scenario or drunk_greg()))


# ---------------------------------------------------------------- output


def format_report(rep: Report) -> str:
    rows = [("Time", "Check", "Kind", "Faculty", "Acted", "Result")]
    for r in rep.results:
        rows.append((r.t, r.id, r.kind, r.expected, r.acted, "PASS" if r.passed else "FAIL"))
    widths = [min(max(len(row[i]) for row in rows), 48) for i in range(len(rows[0]))]

    def fmt(row: tuple[str, ...]) -> str:
        cells = []
        for v, w in zip(row, widths):
            v = v if len(v) <= w else v[: w - 3] + "..."
            cells.append(v.ljust(w))
        return "  ".join(cells).rstrip()

    lines = [f"Scenario {rep.scenario_id} / agent {rep.agent_name}", fmt(rows[0]),
             fmt(tuple("-" * w for w in widths))]
    lines += [fmt(row) for row in rows[1:]]
    fails = [r for r in rep.results if not r.passed]
    if fails:
        lines.append("")
        lines.append("Failures:")
        for r in fails:
            lines.append(f"  {r.id} ({r.kind}): {r.summary}")
            for p in r.problems:
                lines.append(f"    - {p}")
    lines.append("")
    lines.append(f"Tier 1: {'PASS' if rep.tier1_passed else 'FAIL'} "
                 f"({sum(r.passed for r in rep.gating)}/{len(rep.gating)} milestone checks and invariants)")
    trace = [r for r in rep.results if r.kind == "trace"]
    lines.append(f"Trace rows (reported, not gating): {sum(r.passed for r in trace)}/{len(trace)}")
    lines.append("Tier 2: not scored (household scenarios wait on the confidences design, issue #1)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    from .agents import AGENTS

    p = argparse.ArgumentParser(prog="python -m hearthweave.harness", description=__doc__.split("\n\n")[0])
    p.add_argument("--agent", choices=sorted(AGENTS), default="oracle")
    p.add_argument("--all", action="store_true", help="run every reference agent")
    p.add_argument("--scenario", help="path to a scenario JSON (default: Drunk Greg)")
    args = p.parse_args(argv)

    sc = load(args.scenario) if args.scenario else drunk_greg()
    names = sorted(AGENTS) if args.all else [args.agent]
    ok = True
    for i, name in enumerate(names):
        rep = evaluate(AGENTS[name](), sc)
        if i:
            print("\n" + "=" * 72 + "\n")
        print(format_report(rep))
        ok = ok and rep.tier1_passed
    return 0 if (ok or args.all) else 1


if __name__ == "__main__":
    sys.exit(main())
