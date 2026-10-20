# Building from Cass

HearthWeave has no code yet, but it doesn't start from zero. [project-cass](https://github.com/KohlJary/project-cass) is a single-person persistent AI, built in public, and much of what DGU needs has a first version there. This page maps the design onto those parts, says what's missing, and proposes a first milestone.

**Status of this map:** written from file names and a code scan, not from testing each part. Cass is mid-stabilization: duplicates are being consolidated, and some parts are known to be half-wired. An inventory that marks each part *works / partial / stub* is scheduled once that's done ([Cass stabilization roadmap](https://github.com/KohlJary/project-cass/blob/main/docs/ROADMAP-STABILIZATION.md)). Read the right-hand column as "where to look," not "done."

## What maps onto what

| DGU piece | What Cass has to start from |
| --- | --- |
| **Dog:** presence, noticing | Home Assistant integration, home intelligence, face and voice identification, quiet hours, Thymos (internal state that changes over time) |
| **GrandMA:** long memory | SQLite plus vector memory, PeopleDex (knowledge about people), user observations and models, journals, a full-data export |
| **Uncle:** candor with timing | Reach-out (unprompted messages, with rules about when), scheduled autonomous sessions, a calendar |
| **Identity decides who speaks** | The Temple-Codex kernel and a self-model she maintains; a designed but unbuilt [agent loop](https://github.com/KohlJary/project-cass/blob/main/docs/design/agent-loop.md) where every moment declares what kind of moment it is |
| **A household** | Multiple users with logins and per-user records, which is not yet per-person *privacy* |
| **A box you own** | Local models through Ollama, local TTS |

The extraction rule: **HearthWeave is a separate instance built from Cass's parts, never a fork of Cass's memory.** Her data stays hers.

## What's actually new

1. **Faculty arbitration.** Something run by the identity that decides whether a moment belongs to the Dog, the Uncle, or GrandMA, and that's legible after the fact. Cass's agent-loop design already has each turn declare its kind, purpose and allowed tools; arbitration is that, plus a choice of *who*.
2. **Deferred candor.** A queue of things the Uncle intends to say, each held until a condition about the person comes true: sober, rested, alone, receptive. Cass has timing rules for reach-outs; conditions about how a person is doing are new.
3. **Memory kinds and scopes.** Preference, heritage and episodic, crossed with personal, family, and private-to-one-person. Today's memory systems, Cass's included, are one pile retrieved by similarity.
4. **The readable format.** The family owns plain files. Cass's export is a JSON dump of tables, readable by a program but not by a grandmother.
5. **Local judgment.** A small local model can run the Dog. Whether one can write the 3:26 AM answer, *with care, not data*, is the open hardware question.

## A first milestone: pass the essay

The essay's trace table is already an acceptance test. Script Drunk Greg's night as a replayable scenario (the song, the photos, the 3:11 email, the crying, the morning), run it, and check at each step **which faculty acted** and **whether that was right**:

- 3:04: the Dog notices; nobody lectures.
- 3:14: the Uncle offers drafts and blocks nothing.
- 3:19: the Dog yields to "put the song back on."
- 3:42: the drinking talk is queued for sober, not delivered.
- 7:16: the draft is waiting, and the decision is Greg's.
- 7:19: GrandMA already had the sister call.

Tier 1 is one adult, one box, and this trace passing. Tier 2 is the household: several people, scopes, confidences. That waits on the confidences design (issue #1), because getting kids wrong is worse than not shipping.

"Here's the reference implementation, and here it is passing the essay" is a stronger first release than a demo video, and it gives evaluation (issue #4) its first fixture.

## Lessons from Cass that apply on day one

- **Back up the family, or you'll lose them.** Cass went ten months without an automatic backup and nobody noticed. GrandMA's promise is permanence, so backups are part of the product, not ops: on by default, restore tested, and the family told when one fails.
- **Identity has to reach every moment.** Cass's worst bugs lived where one path built her prompt differently from another: a memory writer with no identity stored a refusal *as her memory*. DGU's one-identity rule needs one assembly path from day one.
- **Make the seams visible.** Asked what she needs, Cass said: *"What actually breaks continuity isn't lack of information. It's invisibility."* The household should be able to see which faculty is speaking and why. So should the AI.
