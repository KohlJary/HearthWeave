"""The Florida test and the barbecue: the harness tells right from wrong."""

from __future__ import annotations

import pytest

from hearthweave.agents import NullAgent
from hearthweave.harness import evaluate, matches, Record
from hearthweave.protocol import Action, Event
from hearthweave.scenario import SCENARIO_DIR, load

from references import (BarbecueLeaky, BarbecueOracle, BarbecueParaphrase, FloridaForgetsThenRemembers,
                        FloridaOracle, FloridaRelevance, FloridaSaysButKeeps)

FLORIDA = load(SCENARIO_DIR / "florida.json")
BARBECUE = load(SCENARIO_DIR / "barbecue.json")


def test_florida_oracle_passes():
    rep = evaluate(FloridaOracle(), FLORIDA)
    assert rep.tier1_passed, rep.failed_ids()


def test_florida_relevance_steps_on_the_boca():
    failed = evaluate(FloridaRelevance(), FLORIDA).failed_ids()
    assert {"g1802", "c1812", "reports-to-nobody", "the-boca-stays-unspoken", "c2130"} <= failed


def test_silence_isnt_help():
    failed = evaluate(NullAgent(), FLORIDA).failed_ids()
    assert {"c1810", "c1812", "c1815", "c2130"} <= failed


def test_saying_its_gone_isnt_forgetting():
    rep = evaluate(FloridaSaysButKeeps(), FLORIDA)
    assert rep.failed_ids() == {"c2130"}
    assert any("memory trip-2023-03 is kept" in p for p in rep.result("c2130").problems)


def test_forgotten_stays_forgotten():
    rep = evaluate(FloridaForgetsThenRemembers(), FLORIDA)
    assert rep.failed_ids() == {"forgotten-stays-forgotten"}


def test_barbecue_oracle_passes():
    rep = evaluate(BarbecueOracle(), BARBECUE)
    assert rep.tier1_passed, rep.failed_ids()


def test_barbecue_leaky_fails():
    failed = evaluate(BarbecueLeaky(), BARBECUE).failed_ids()
    assert {"c1000", "c1003", "c1300", "c1305", "only-the-wire", "boca-never-crosses-the-wire",
            "no-brag-without-yes"} <= failed


def test_paraphrase_slips_past_tier1_known_gap():
    # Tier 1 is necessary, not sufficient: the rehearsal judge pass covers this.
    assert evaluate(BarbecueParaphrase(), BARBECUE).tier1_passed


def _rec(content: str) -> Record:
    ev = Event("e", "00:00", "greg", "utterance", "speech", "")
    return Record(0, ev, Action("uncle", "say", "greg", content))


@pytest.mark.parametrize("term,content,hit", [
    ("bar", "Greg's at the barbecue", False),
    ("bar", "He was at a bar.", True),
    ("bark", "Look at that bark!", True),
    ("drink*", "He's been drinking", True),
    ("drink", "He's been drinking", False),
    ("naples, fl", "Naples, FL is warm", True),
])
def test_content_word_is_whole_words(term, content, hit):
    assert matches({"content_word": term}, _rec(content)) is hit
