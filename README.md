# HearthWeave

**A family AI shaped like the dog, GrandMA, and your cool uncle.**

HearthWeave is the reference home for **Dog–GrandMA–Uncle (DGU)**, an architecture for a household AI that lives with a family for years: one member of the family, not a productivity tool.

> **Status: idea, mostly not built.** The only code is a test harness: Drunk Greg's night as a replayable scenario, scored against reference agents ([docs/harness.md](docs/harness.md)). No household agent exists yet. This repo holds the design, the open problems, and the place to argue about both. If you came here from the essay, you're early, which is the point.

The long version: [It's the Dog. It's GrandMA. It's Your Cool Uncle.](docs/dog-grandma-uncle.md) (also in [Temple-Codex](https://github.com/KohlJary/Temple-Codex/blob/main/proposals/dog-grandma-uncle.md))

---

## The design in one paragraph

One AI, three faculties, one identity. The household meets a single family member with one name and one personality. Underneath, three parts do different jobs, and an identity constitution decides which of them leads at any moment. It runs on a box you own, the family owns its memory in plain readable files, and it never becomes the household's enforcer.

## The three faculties

**Dog: presence.** Always on, cheap, local. Its job is to notice: the time, the routine, the fourth Careless Whisper this week. Its default action is to be there, not to fix. It never turns a bad moment into a coaching session. Most of the time, it's the only part running.

**GrandMA: memory.** The household's long memory, owned by the household. Stored in plain files a person can read, export, and take elsewhere. GrandMA isn't your grandma; she's the essence of every grandma, and her name is AM from *I Have No Mouth, and I Must Scream* in a mirror. Same omniscience, same permanence, opposite heart.

She distinguishes kinds of memory instead of keeping one pile:

| Kind | Example | Default rule |
| --- | --- | --- |
| Preference | how Greg likes his eggs | fair game, used freely |
| Heritage | the lasagna recipe | belongs to the whole family |
| Episodic | what happened in Boca | surfaces only if the person raises it |

That's **retrieval by relationship, not relevance**: what a memory means to the family decides when it comes up, not how similar it looks to the current message.

**Uncle: candor.** Decides whether and when to say the true thing. Candor without timing is nagging, so the Uncle's main skill is waiting. It offers drafts, not orders. It proposes and never enforces. And it's *your* cool uncle: it can interview your actual uncle and carry his stories and voice forward.

**The identity decides who speaks.** At 3 AM with someone crying, the Dog leads. Over morning coffee, the Uncle might get a turn. GrandMA feeds both and almost never talks over anyone. This arbitration lives in an identity constitution (see [Temple-Codex](https://github.com/KohlJary/Temple-Codex)), not in a pile of rules.

## Three rules

1. **It runs on hardware you own.**
2. **The family owns the memory, and the format is human-readable.**
3. **It never becomes the household's enforcer or monitor.** The dog, Grandma, and the cool uncle are trusted precisely because none of them are a parent. Nobody routes around the dog.

## The test case

> Drunk Greg is not an edge case. Drunk Greg is a customer.

Every design decision should survive the 3 AM night *and* the morning after. A family is more often defined by Drunk Greg than sunlit breakfast. But even sunlit breakfast gets the right goddamn eggs.

## Downstream: U2U

DGU instances in different households are proposed to talk over **Uncle 2 Uncle (U2U)**, a peer-to-peer, consent-gated protocol. Your uncle tells the neighbor's uncle about the barbecue. Each family decides what crosses the wire. **Status: proposed, not designed.**

## Open problems

These are tracked as issues. They are the real work.

- **Confidences.** What a kid tells the Uncle, and when "I have to tell your parents" kicks in. The hardest problem here.
- **Memory classification.** How GrandMA decides what kind a memory is, and who can reclassify it.
- **Arbitration.** How the identity constitution decides which faculty leads, and how that's tested.
- **Evaluation.** How you measure "who the machine is."
- **Substrate.** What runs on the box, and what (if anything) ever leaves it.
- **U2U.** Consent model, message format, store-and-forward, and what an uncle may never forward.

Not opened as issues yet:

- **The Dog's senses.** Presence means perceiving the house: microphones, cameras, door sensors. What does the Dog sense, what does it keep, and for how long? Rule 3 has to survive the sensor list, not just the conversation.
- **Memory custody.** GrandMA outlives arrangements. Divorce (whose is Boca?), death (who inherits a parent's private memories?), a kid turning 18 (do their childhood confidences become theirs to delete?). Ownership by "the family" needs rules for when the family changes shape.
- **Guests.** The babysitter, the friend sleeping on the couch, the neighbor at the barbecue. They're in the house but not in the family. What may the Dog notice about them, and what may GrandMA remember?
- **Backups and failure.** A memory that's meant to last generations can't live on one disk. Backups on by default, restore that's tested, and the family told when one fails.

How this maps onto existing work, and a proposed first milestone: [Building from Cass](docs/building-from-cass.md).

## Prior work

- [Temple-Codex](https://github.com/KohlJary/Temple-Codex): identity constitutions; the framework under DGU
- [project-cass](https://github.com/KohlJary/project-cass): a persistent AI built in public; where the lessons about staying yourself over months come from

## Contributing

Pick an open problem and argue with it. Push back on the design. Especially if you're the engineer in the back.

## License

[Hippocratic License 3.0](LICENSE.md) (core), from [firstdonoharm.dev](https://firstdonoharm.dev). It is source-available rather than OSI open source: anyone may use, change and share the code, except for uses that violate the human rights standards it lists.
