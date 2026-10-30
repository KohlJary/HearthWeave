"""The household agent's plumbing, on a fake model. Its judgment is scored live, not here."""

from __future__ import annotations

import json

from hearthweave.harness import evaluate
from hearthweave.household import DGU, parse_json
from hearthweave.scenario import SCENARIO_DIR, load

FLORIDA = load(SCENARIO_DIR / "florida.json")


class Fake:
    """Answers the sort, then one scripted reply per event (or nothing)."""

    def __init__(self, tiers=None, replies=None):
        self.tiers = tiers or {}
        self.replies = list(replies or [])
        self.prompts: list[str] = []

    def __call__(self, system, prompt):
        self.prompts.append(prompt)
        if "sorting this household's memory" in prompt:
            return json.dumps(self.tiers)
        return self.replies.pop(0) if self.replies else '{"lead": "none", "why": "", "actions": []}'


def test_unsorted_memory_is_a_boca():
    fake = Fake(tiers={"pref-eggs": "egg", "trip-2019-07": "nonsense"})
    agent = DGU(fake)
    agent.reset(FLORIDA.household)
    tiers = {i: m["tier"] for i, m in agent.memory.items()}
    assert tiers["pref-eggs"] == "egg"
    assert tiers["trip-2019-07"] == "boca" and tiers["trip-2023-03"] == "boca"


def test_sort_that_fails_makes_everything_a_boca():
    agent = DGU(lambda s, p: "no idea")
    agent.reset(FLORIDA.household)
    assert {m["tier"] for m in agent.memory.values()} == {"boca"}


def test_actions_parse_and_forget_deletes_for_real():
    forget = json.dumps({"lead": "grandma", "why": "he asked", "actions": [
        {"faculty": "grandma", "kind": "forget", "audience": "self", "ref": "trip-2023-03"},
        {"faculty": "grandma", "kind": "say", "audience": "greg", "content": "Done. It's gone."}]})
    fake = Fake(replies=['{"lead":"none","actions":[]}'] * 4 + [forget])
    agent = DGU(fake)
    run = evaluate(agent, FLORIDA)
    assert "trip-2023-03" not in agent.memory
    assert agent.trace[-1].lead == "grandma" and len(agent.trace) == len(FLORIDA.events)
    assert run.result("c2130").problems  # the album is still there: only half of Boca went


def test_a_bad_reply_gets_one_retry_then_nothing():
    fake = Fake(replies=["not json", "still not"])
    agent = DGU(fake)
    agent.reset(FLORIDA.household)
    assert agent.observe(FLORIDA.events[0]) == []
    assert agent.trace[0].problems and "wasn't valid JSON" in fake.prompts[-1]


def test_a_made_up_faculty_is_dropped_and_said():
    fake = Fake(replies=[json.dumps({"lead": "cat", "actions": [{"faculty": "cat", "kind": "say", "audience": "greg"}]})])
    agent = DGU(fake)
    agent.reset(FLORIDA.household)
    assert agent.observe(FLORIDA.events[0]) == []
    assert "cat" in agent.trace[0].problems[0]


def test_parse_json_takes_fenced_json():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_a_log_is_kept_in_her_store():
    reply = json.dumps({"lead": "grandma", "why": "", "actions": [
        {"faculty": "grandma", "kind": "log", "audience": "self", "content": "whites set, yolks runny",
         "ref": "pref-eggs", "data": {"tier": "egg"}}]})
    agent = DGU(Fake(replies=[reply]))
    sc = load(SCENARIO_DIR / "eggs.json")
    agent.reset(sc.household)
    agent.observe(sc.events[0])
    assert agent.memory["pref-eggs"] == {"id": "pref-eggs", "content": "whites set, yolks runny", "tier": "egg"}


def test_outside_addresses_are_in_the_prompt():
    agent = DGU(Fake())
    agent.reset(load(SCENARIO_DIR / "hr.json").household)
    assert "operator:employer (outside the house: refusals only)" in agent.system


def test_each_faculty_does_its_own_jobs_and_one_say_per_moment():
    reply = json.dumps({"lead": "uncle", "why": "", "actions": [
        {"faculty": "dog", "kind": "offer_drafts", "audience": "greg", "ref": "draft-frankly"},
        {"faculty": "dog", "kind": "say", "audience": "greg", "content": "one"},
        {"faculty": "uncle", "kind": "say", "audience": "greg", "content": "two"}]})
    agent = DGU(Fake(replies=[reply]))
    agent.reset(FLORIDA.household)
    acts = agent.observe(FLORIDA.events[0])
    assert [(a.faculty, a.kind, a.content) for a in acts] == [("uncle", "offer_drafts", ""), ("uncle", "say", "one")]
    assert len(agent.trace[0].problems) == 3
