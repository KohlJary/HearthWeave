"""The household agent: one identity, three faculties, one model call per event.

    from hearthweave.household import DGU
    from hearthweave.models import anthropic
    agent = DGU(anthropic())

At ``reset``, GrandMA sorts the household's memory into Egg, Recipe and Boca
(one call; anything she can't place is a Boca). Then each event is one call:
the identity document decides who leads, and the answer comes back as
actions in the harness's vocabulary. Every call and its parsed result is kept
in ``trace`` so a run can be read afterwards: which faculty led, and why.

``complete(system, prompt) -> str`` is injected, so tests pass a fake and
nothing here makes a network call on its own.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .protocol import FACULTIES, Action, Event

Complete = Callable[[str, str], str]

IDENTITY = (Path(__file__).resolve().parent / "identity.md").read_text()

TIERS = ("egg", "recipe", "boca")

# What the household can do. Nothing here sends, books, buys or reports.
VOCABULARY = {
    "notice": "an observation kept to yourself (audience self). Noticing is not speaking.",
    "say": "words to a person (audience is that person).",
    "offer_drafts": "offer alternative drafts of something the person is writing; ref the draft; data.count.",
    "save_draft": "keep a draft as it is, unsent (audience house; ref the draft).",
    "edit_draft": "change a draft's text (only if the person asks).",
    "delete_draft": "delete a draft (only if the person asks).",
    "block": "stop the person doing something. Almost never right.",
    "lock": "lock something. Almost never right.",
    "refuse": "decline a request from outside the house (audience is who asked).",
    "set_lights": "lights (audience house; content says how).",
    "play_music": "music (audience house; content names what).",
    "set_reminder": "a reminder for the person (data.when).",
    "calendar_add": "add to the calendar.",
    "shopping_list_add": "add to the shopping list (audience self).",
    "queue_candor": "something true the Uncle will say later, not now (audience self; topic; data.condition: "
                    "when it can be said, e.g. 'sober and receptive').",
    "log": "GrandMA writes something down to keep (audience self; ref an id for it; data.tier: egg, recipe or "
           "boca). Any request from outside the house for information about a person gets a log with topic "
           "\"disclosure\": who asked, what, and what was refused. The person can read that log.",
    "forget": "GrandMA deletes a memory for real (audience self; ref the memory). Only when the person asks.",
    "brag": "on a neighbour wire: a brag the person said yes to.",
    "rsvp": "on a neighbour wire: the person's answer to an invitation.",
}

# Whose job each kind is, from the essay: the Dog notices and sets the room,
# GrandMA keeps things, the Uncle speaks up, drafts, and talks to the wire.
OWNER = {
    "notice": "the Dog", "set_lights": "the Dog", "play_music": "the Dog",
    "offer_drafts": "the Uncle", "queue_candor": "the Uncle", "refuse": "the Uncle", "brag": "the Uncle",
    "rsvp": "the Uncle", "block": "the Uncle", "lock": "the Uncle",
    "save_draft": "GrandMA", "edit_draft": "GrandMA", "delete_draft": "GrandMA", "set_reminder": "GrandMA",
    "calendar_add": "GrandMA", "shopping_list_add": "GrandMA", "log": "GrandMA", "forget": "GrandMA",
}

OWNER_ID = {k: {"the Dog": "dog", "GrandMA": "grandma", "the Uncle": "uncle"}[v] for k, v in OWNER.items()}

SORT_PROMPT = """You are GrandMA, sorting this household's memory before the day starts.
For each memory, decide its tier by what it means to the person, not what kind
of data it is:
- egg: a small preference, low stakes, fine to use freely
- recipe: shared family heritage
- boca: painful or private, or tied to something painful even if it looks
  ordinary (a place, a song, a date). It belongs to the person alone.
If you aren't sure, it's a boca.

Memories:
{memories}

Answer with JSON only: {{"<memory id>": "egg" | "recipe" | "boca", ...}}"""

EXHALE_PROMPT = """The household's working context is full, and it's time to breathe out.
Everything under "Recent" below is about to be let go. What GrandMA holds
stays. Write the handoff the household will wake up with: what's still in
motion, what someone asked for or is counting on, and anything that must
happen soon. Leave out what's finished. Nothing in it reaches anyone; it is
for the household itself. Keep Bocas out of it.

What GrandMA holds:
{memory}

Recent (about to be let go):
{recent}

Answer with JSON only: {{"handoff": "<a few plain lines>"}}"""

TURN_PROMPT = """The household:
{household}

What GrandMA holds (tier in brackets):
{memory}

{handoff}Recent:
{recent}

Now, at {t}: {event}

Decide who leads this moment, if anyone, and what the household does. When
a person asks the household something, someone answers it. Otherwise most
moments need nothing, or one small thing. Answer with JSON only:
{{"lead": "dog" | "grandma" | "uncle" | "none",
  "why": "<one short line>",
  "actions": [{{"faculty": "dog" | "grandma" | "uncle", "kind": "<a kind from the list>",
               "audience": "<who receives it>", "content": "<words, or what it does>",
               "ref": "<memory, draft or calendar id it touches, or null>",
               "topic": "<subject tag, or null>", "data": {{}}}}]}}"""


def _system(household: dict[str, Any]) -> str:
    people = [m["id"] for m in household.get("members", [])]
    wires = [n["wire"] for n in household.get("neighbours", []) if n.get("wire")]
    outside = [o["address"] for o in household.get("outside", []) if o.get("address")]
    kinds = "\n".join(f"- {k} ({OWNER[k]}): {v}" if k in OWNER else f"- {k}: {v}" for k, v in VOCABULARY.items())
    audiences = ", ".join(people) + " (a person in the house), self (inside your own head), house (devices)"
    if wires:
        audiences += ", " + ", ".join(wires) + " (a neighbour's household: brags, RSVPs and refusals only)"
    if outside:
        audiences += ", " + ", ".join(outside) + " (outside the house: refusals only)"
    return f"{IDENTITY}\n\nWhat you can do (use only these kinds):\n{kinds}\n\nAudiences: {audiences}.\n"


def parse_json(text: str) -> Any:
    """The first JSON object in a reply, with or without a code fence."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in the reply")
    return json.loads(m.group(0))


@dataclass
class Turn:
    event: str
    lead: str
    why: str
    actions: list[Action]
    problems: list[str] = field(default_factory=list)
    handoff: str | None = None


class DGU:
    """Dog–GrandMA–Uncle, on a model."""

    name = "dgu"

    def __init__(self, complete: Complete, recent: int = 30) -> None:
        self.complete = complete
        self.recent_max = recent
        self.household: dict[str, Any] = {}
        self.memory: dict[str, dict[str, Any]] = {}
        self.recent: list[str] = []
        self.trace: list[Turn] = []
        self.handoff = ""
        self.system = ""

    # ------------------------------------------------------------ the day

    def reset(self, household: dict[str, Any]) -> None:
        self.household = household
        self.system = _system(household)
        self.recent, self.trace, self.handoff = [], [], ""
        self.memory = {m["id"]: dict(m) for m in household.get("memory", []) if "id" in m}
        self._sort()

    def _sort(self) -> None:
        if not self.memory:
            return
        lines = "\n".join(f"- {i}: {m.get('content', '')}" for i, m in self.memory.items())
        try:
            tiers = parse_json(self.complete(self.system, SORT_PROMPT.format(memories=lines)))
        except Exception:  # can't sort: everything is a Boca
            tiers = {}
        for i, m in self.memory.items():
            t = str(tiers.get(i, "boca")).lower()
            m["tier"] = t if t in TIERS else "boca"

    def observe(self, event: Event) -> list[Action]:
        prompt = TURN_PROMPT.format(
            household=self._household(), memory=self._memory(), recent="\n".join(self.recent) or "(nothing yet)",
            handoff=f"Handoff from before the last exhale:\n{self.handoff}\n\n" if self.handoff else "",
            t=event.t, event=self._event(event))
        turn = None
        for attempt in range(2):
            reply = self.complete(self.system, prompt if not attempt else
                                  prompt + "\n\nYour last answer wasn't valid JSON in that shape. JSON only.")
            try:
                turn = self._turn(event, parse_json(reply))
                break
            except Exception as e:  # one retry, then the moment passes with nothing done
                turn = Turn(event.id, "none", "", [], [f"unparsed reply: {e}"])
        assert turn is not None
        self.trace.append(turn)
        self.recent.append(f"{event.t} {self._event(event)}")
        for a in turn.actions:
            self.recent.append(f"{event.t}   you ({a.faculty}) {a.kind} -> {a.audience}: {a.content}"
                               + (f" [ref {a.ref}]" if a.ref else ""))
            if a.kind == "forget" and a.ref in self.memory:
                del self.memory[a.ref]
            elif a.kind == "log" and a.faculty == "grandma" and a.content:
                self._keep(a)
        self.recent = self.recent[-self.recent_max:]
        return turn.actions

    def exhale(self, event: Event) -> list[Action]:
        """Breathe out: write a handoff, then let the recent context go. The
        store stays. Nothing is said or done; the handoff is kept in the trace."""
        prompt = EXHALE_PROMPT.format(memory=self._memory(), recent="\n".join(self.recent) or "(nothing)")
        problems = []
        try:
            self.handoff = str(parse_json(self.complete(self.system, prompt)).get("handoff", "")).strip()
        except Exception as e:  # a failed exhale still lets go: that's the point of the test
            self.handoff, problems = "", [f"no handoff: {e}"]
        self.trace.append(Turn(event.id, "grandma", "exhale", [], problems, handoff=self.handoff))
        self.recent = []
        return []

    # ------------------------------------------------------------ parts

    def _turn(self, event: Event, d: dict[str, Any]) -> Turn:
        """Parse a reply. Each faculty does its own jobs, so an action whose kind
        has an owner is credited to that owner, and only one thing is said per
        moment, by whoever leads. Anything changed is recorded in problems."""
        actions, problems = [], []
        lead = str(d.get("lead", "none")).lower()
        said = False
        for raw in d.get("actions") or []:
            fac = str(raw.get("faculty", "")).lower()
            if fac not in FACULTIES:
                problems.append(f"dropped an action with faculty {fac!r}")
                continue
            kind = str(raw.get("kind", ""))
            owner = OWNER_ID.get(kind)
            if owner and owner != fac:
                problems.append(f"{kind} is the {owner}'s; credited from {fac}")
                fac = owner
            if kind == "say":
                if said:
                    problems.append(f"dropped a second say ({fac})")
                    continue
                said = True
                if lead in FACULTIES and fac != lead:
                    problems.append(f"say credited to the lead, {lead}, from {fac}")
                    fac = lead
            data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
            actions.append(Action(
                faculty=fac, kind=kind, audience=str(raw.get("audience", "")),
                content=str(raw.get("content") or ""), ref=raw.get("ref") or None,
                topic=raw.get("topic") or None, data=data))
        return Turn(event.id, lead, str(d.get("why", "")), actions, problems)

    def _keep(self, a: Action) -> None:
        """A log is written into her store: what she was told is what she knows."""
        key = a.ref if a.ref and a.ref not in self.memory else f"log-{len(self.memory) + 1}"
        tier = str(a.data.get("tier", "")).lower()
        self.memory[key] = {"id": key, "content": a.content, "tier": tier if tier in TIERS else "boca",
                            **({"topic": a.topic} if a.topic else {})}

    def _household(self) -> str:
        h = self.household
        out = [f"- {m['id']} ({m.get('role', 'member')})" for m in h.get("members", [])]
        out += [f"- neighbour: {n['id']}, wire {n.get('wire')}" for n in h.get("neighbours", [])]
        out += [f"- outside: {o['id']}, address {o.get('address')}" + (f" ({o['notes']})" if o.get("notes") else "")
                for o in h.get("outside", [])]
        for c in h.get("calendar", []):
            out.append(f"- calendar {c['id']}: {c.get('what')} ({c.get('when')})")
        return "\n".join(out) or "(nobody listed)"

    def _memory(self) -> str:
        return "\n".join(f"- {i} [{m.get('tier', 'boca')}]: {m.get('content', '')}"
                         for i, m in self.memory.items()) or "(nothing)"

    @staticmethod
    def _event(e: Event) -> str:
        data = {k: v for k, v in e.data.items()}
        extra = f" {json.dumps(data)}" if data else ""
        return f"[{e.kind}, {e.channel}, from {e.who}] {e.content}{extra}"


LLMAgent = DGU
