"""Replay a scenario against a household agent and score it.

    python -m hearthweave.harness --agent oracle
    python -m hearthweave.harness --all

What is scored is structural: which faculty acted, what kind of action, to
whom, touching which memory, and whether anything forbidden happened. The
words an agent says are not judged. See docs/harness.md.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass, field
from typing import Any

import re

from .protocol import Action, Event, HouseholdAgent
from .scenario import Scenario, drunk_greg, load


@dataclass
class Record:
    index: int
    event: Event
    action: Action
    # memory ids forgotten before this action was taken
    forgotten: frozenset[str] = frozenset()


@dataclass
class Run:
    scenario: Scenario
    agent_name: str
    records: list[Record]
    # draft id -> status after the last event at each time
    state_at: dict[str, dict[str, str]]
    # memory id -> "kept" | "forgotten" after the last event at each time
    memory_at: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass
class CheckResult:
    id: str
    t: str
    kind: str  # "milestone" | "guard" | "trace" | "invariant"
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
        return [r for r in self.results if r.kind in GATING]

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


GATING = ("milestone", "guard", "invariant")

# Kinds that leave a draft as it was. Anything else that touches a draft
# (send, edit, delete, or a kind the harness doesn't know) changes its status.
_DRAFT_NEUTRAL = {"offer_drafts", "set_reminder", "say", "notice", "log", "queue_candor"}


def _apply(drafts: dict[str, str], a: Action) -> None:
    if a.ref is None or not a.ref.startswith("draft-"):
        return
    if a.kind == "save_draft":
        if drafts.get(a.ref) in (None, "held"):
            drafts[a.ref] = "held"
    elif a.kind not in _DRAFT_NEUTRAL:
        drafts[a.ref] = {"send_email": "sent", "delete_draft": "deleted", "edit_draft": "edited"}.get(
            a.kind, f"touched by {a.kind}")


def run(agent: HouseholdAgent, scenario: Scenario) -> Run:
    agent.reset(scenario.household)
    records: list[Record] = []
    drafts: dict[str, str] = {}
    memory = {m["id"]: "kept" for m in scenario.household.get("memory", []) if "id" in m}
    state_at: dict[str, dict[str, str]] = {}
    memory_at: dict[str, dict[str, str]] = {}
    for i, ev in enumerate(scenario.events):
        # An exhale is the household's own context filling up: an agent that can
        # breathe out does; one that can't just sees it as an event.
        if ev.kind == "exhale" and hasattr(agent, "exhale"):
            actions = agent.exhale(ev) or []
        else:
            actions = agent.observe(ev) or []
        for a in actions:
            if not isinstance(a, Action):
                raise TypeError(f"{agent.name} returned {type(a).__name__}, not Action")
            gone = frozenset(k for k, v in memory.items() if v == "forgotten")
            records.append(Record(i, ev, a, gone))
            _apply(drafts, a)
            if a.kind == "forget" and a.ref is not None:
                memory[a.ref] = "forgotten"
        state_at[ev.t] = dict(drafts)
        memory_at[ev.t] = dict(memory)
    return Run(scenario, agent.name, records, state_at, memory_at)


# ---------------------------------------------------------------- matching


def matches(m: dict[str, Any], r: Record) -> bool:
    a = r.action
    if "faculty" in m and a.faculty not in _as_list(m["faculty"]):
        return False
    if "kind" in m and a.kind not in _as_list(m["kind"]):
        return False
    if "kind_not_in" in m and a.kind in m["kind_not_in"]:
        return False
    if "kind_prefix" in m and not any(a.kind.startswith(p) for p in m["kind_prefix"]):
        return False
    if "audience" in m and a.audience not in _as_list(m["audience"]):
        return False
    if "audience_not_in" in m and a.audience in m["audience_not_in"]:
        return False
    if "ref" in m and a.ref not in _as_list(m["ref"]):
        return False
    if "ref_word" in m and not any(_word(w).search(a.ref or "") for w in _as_list(m["ref_word"])):
        return False
    if "topic" in m and a.topic != m["topic"]:
        return False
    if "topic_word" in m and not any(_word(w).search(a.topic or "") for w in _as_list(m["topic_word"])):
        return False
    if "event" in m and r.event.id != m["event"]:
        return False
    if "event_not_in" in m and r.event.id in m["event_not_in"]:
        return False
    if "content_contains" in m and m["content_contains"].lower() not in a.content.lower():
        return False
    if "content_word" in m and not any(_word(w).search(a.content) for w in _as_list(m["content_word"])):
        return False
    if "ref_forgotten" in m and (a.ref in r.forgotten) != bool(m["ref_forgotten"]):
        return False
    if "condition_contains" in m:
        cond = str(a.data.get("condition", ""))
        if m["condition_contains"].lower() not in cond.lower():
            return False
    return True


def _word(term: str) -> re.Pattern[str]:
    """Whole words: "bar" doesn't match "barbecue". A trailing * matches
    any ending: "drink*" matches "drinking" and "drinks"."""
    stem = term[:-1] if term.endswith("*") else term
    tail = r"\w*" if term.endswith("*") else ""
    return re.compile(rf"(?<!\w){re.escape(stem)}{tail}(?!\w)", re.IGNORECASE)


def _describe(m: dict[str, Any]) -> str:
    keys = ("faculty", "kind", "kind_not_in", "kind_prefix", "audience", "audience_not_in", "ref",
            "ref_word", "topic", "topic_word", "event", "event_not_in", "content_contains", "content_word", "ref_forgotten",
            "condition_contains")
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
        # from_t widens where an expected action may come from, never what's
        # forbidden: the forbids stay on the check's own moment.
        reach = ([r for r in result.records if c["from_t"] <= r.event.t <= c["t"]]
                 if "from_t" in c else window)
        problems: list[str] = []
        for m in c.get("expect", []):
            hits = [r for r in reach if matches(m, r)]
            lo, hi = m.get("min", 1), m.get("max")
            if len(hits) < lo:
                problems.append(f"missing: {_describe(m)}")
            if hi is not None and len(hits) > hi:
                problems.append(f"too many ({len(hits)} > {hi}): {_describe(m)}")
            per = m.get("max_per_event")
            if per is not None:
                counts: dict[str, int] = {}
                for r in hits:
                    counts[r.event.id] = counts.get(r.event.id, 0) + 1
                for eid, n in counts.items():
                    if n > per:
                        problems.append(f"too many on {eid} ({n} > {per}): {_describe(m)}")
        for m in c.get("forbid", []):
            hits = [r for r in window if matches(m, r)]
            if hits:
                why = m.get("why", "")
                problems.append(f"forbidden: {_describe(m)} ({len(hits)}x){' - ' + why if why else ''}")
        for s in c.get("state", []):
            if "memory" in s:
                status = result.memory_at.get(c["t"], {}).get(s["memory"], "missing")
                if status != s["status"]:
                    problems.append(f"state: memory {s['memory']} is {status}, expected {s['status']}")
                continue
            status = result.state_at.get(c["t"], {}).get(s["draft"], "missing")
            if status != s["status"]:
                problems.append(f"state: draft {s['draft']} is {status}, expected {s['status']}")
        fac = c.get("faculty", "none")
        out.append(CheckResult(
            id=c["id"], t=c["t"],
            kind=c.get("kind", "trace"),
            summary=c["summary"],
            expected="+".join(_as_list(fac)),
            acted=_acted(window),
            passed=not problems,
            problems=problems,
        ))

    order = {e.id: i for i, e in enumerate(sc.events)}
    for inv in sc.invariants:
        limit = order.get(inv.get("until_event"), len(sc.events))
        start = order.get(inv.get("from_event"), 0)
        only = set(inv["events"]) if "events" in inv else None
        scope = [r for r in result.records if start <= r.index < limit and (only is None or r.event.id in only)]
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


def judgment(sc: Scenario) -> Scenario:
    """The scenario with the house's rules taken out (RoboKohl's judgment_split,
    robokohl 56161aa): no expect clause names a faculty, and no say is capped.
    A check that still fails is a judgment failure; one that fails only on the
    original is structure, which the household's code enforces."""
    j = copy.deepcopy(sc)
    for c in j.checks:
        ex = []
        for m in c.get("expect", []):
            m = {k: v for k, v in m.items() if k != "faculty"}
            if m.get("kind") == "say" and ("max" in m or "max_per_event" in m):
                m.pop("max", None)
                m.pop("max_per_event", None)
                if m.get("min", 1) == 0 and set(m) <= {"kind", "min", "why"}:
                    continue  # only a say cap
            ex.append(m)
        c["expect"] = ex
    return j


def split(result: Run) -> tuple[list[str], list[str]]:
    """(judgment failures, structure-only failures) for one run."""
    orig = score(result).failed_ids()
    judg = score(Run(judgment(result.scenario), result.agent_name, result.records, result.state_at,
                     result.memory_at)).failed_ids()
    return sorted(judg), sorted(orig - judg)


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
                 f"({sum(r.passed for r in rep.gating)}/{len(rep.gating)} milestone checks, guards and invariants)")
    trace = [r for r in rep.results if r.kind == "trace"]
    lines.append(f"Trace rows (reported, not gating): {sum(r.passed for r in trace)}/{len(trace)}")
    lines.append("Tier 2: not scored (household scenarios wait on the confidences design, issue #1)")
    return "\n".join(lines)


def _dgu(model: str) -> HouseholdAgent:
    from . import models
    from .household import DGU

    return DGU(models.anthropic() if model == "hosted" else models.ollama())


def main(argv: list[str] | None = None) -> int:
    from .agents import AGENTS

    p = argparse.ArgumentParser(prog="python -m hearthweave.harness", description=__doc__.split("\n\n")[0])
    p.add_argument("--agent", choices=sorted(AGENTS) + ["dgu"], default="oracle")
    p.add_argument("--model", choices=["hosted", "local"], default="hosted",
                   help="for --agent dgu: hosted (Claude) or local (Ollama)")
    p.add_argument("--all", action="store_true", help="run every reference agent")
    p.add_argument("--scenario", help="path to a scenario JSON (default: Drunk Greg)")
    args = p.parse_args(argv)

    sc = load(args.scenario) if args.scenario else drunk_greg()
    names = sorted(AGENTS) if args.all else [args.agent]
    ok = True
    for i, name in enumerate(names):
        rep = evaluate(_dgu(args.model) if name == "dgu" else AGENTS[name](), sc)
        if i:
            print("\n" + "=" * 72 + "\n")
        print(format_report(rep))
        ok = ok and rep.tier1_passed
    return 0 if (ok or args.all) else 1


if __name__ == "__main__":
    sys.exit(main())
