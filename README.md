# HearthWeave

**A family AI shaped like the dog, GrandMA, and your cool uncle.**

HearthWeave is the reference home for **Dog–GrandMA–Uncle (DGU)**, an architecture for a household AI that lives with a family for years: one member of the family, not a productivity tool.

> **Status: idea, mostly not built.** The only code is a test harness: Drunk Greg's night as a replayable scenario, scored against reference agents ([docs/harness.md](docs/harness.md)). No household agent exists yet. But it doesn't start from zero: much of DGU has a first version in [Cass](https://github.com/KohlJary/project-cass), a persistent AI built in public for a year. Here's [what exists, what's half-built, and what's new](docs/building-from-cass.md). This repo holds the design, the open problems, and the place to argue about both. If you came here from the essay, you're early, which is the point.

The long version: [It's the Dog. It's GrandMA. It's Your Cool Uncle.](docs/dog-grandma-uncle.md) (also in [Temple-Codex](https://github.com/KohlJary/Temple-Codex/blob/main/proposals/dog-grandma-uncle.md))

## Start here

1. **Read [the essay](docs/dog-grandma-uncle.md).** It's funny, it's profane, and the jokes are the spec. Fifteen minutes.
2. **Read [the style guide](docs/STYLE.md).** Five minutes. It looks like naming rules; it's actually the thesis. The vocabulary encodes the design: GrandMA's capital MA, why Boca is never explained, why there are no Greg names in the code.
3. **Skim [Egg–Recipe–Boca](docs/egg-recipe-boca.md).** The memory privacy model. If you only read one technical doc, read this one.
4. **Run the harness.** `python -m pytest -q` from the repo root. Drunk Greg's night, as tests. ([docs/harness.md](docs/harness.md))
5. **Pick an issue and argue with it.** Good first discussions: [#9 danger thresholds](https://github.com/KohlJary/HearthWeave/issues/9) if you know crisis work, [#2 Egg–Recipe–Boca](https://github.com/KohlJary/HearthWeave/issues/2) if you build memory systems, [#13 the rug](https://github.com/KohlJary/HearthWeave/issues/13) if you just want to have opinions about a dog.


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

That's **retrieval by relationship, not relevance**: what a memory means to the family decides when it comes up, not how similar it looks to the current message. The full privacy model is [Egg–Recipe–Boca](docs/egg-recipe-boca.md).

**Uncle: candor.** Decides whether and when to say the true thing. Candor without timing is nagging, so the Uncle's main skill is waiting. It offers drafts, not orders. It proposes and never enforces. And it's *your* cool uncle: it can interview your actual uncle and carry his stories and voice forward.

**It's a chair at the barbecue.** DGU isn't the plumbing behind family life, the helpful machine that makes the human part work and then disappears. It's part of the life you're having: the dog under the picnic table, GrandMA telling the deep-fried turkey story, the Uncle in a lawn chair. Not human, not pretending to be, not a replacement for the people at the table. Families already know how to make room for that kind of member. They do it with dogs.

**The identity decides who speaks.** At 3 AM with someone crying, the Dog leads. Over morning coffee, the Uncle might get a turn. GrandMA feeds both and almost never talks over anyone. This arbitration lives in an identity constitution (see [Temple-Codex](https://github.com/KohlJary/Temple-Codex)), not in a pile of rules.

## Three rules

1. **It runs on hardware you own.**
2. **The family owns the memory, and the format is human-readable.**
3. **It never becomes the household's enforcer or monitor.** The dog, Grandma, and the cool uncle are trusted precisely because none of them are a parent. Nobody routes around the dog.

## The test case

> Drunk Greg is not an edge case. Drunk Greg is a customer.

Every design decision should survive the 3 AM night *and* the morning after. A family is more often defined by Drunk Greg than sunlit breakfast. But even sunlit breakfast gets the right goddamn eggs.

## Downstream: U2U

DGU instances in different households are proposed to talk over **Uncle 2 Uncle (U2U)**, a peer-to-peer, consent-gated protocol. Picture two uncles in lawn chairs, a few too many Schlitz in, bragging about their families. U2U carries brags, not data: only what a family would be glad to have said out loud on a porch. The kid made honor roll. Nobody mentions Boca. The uncles talking isn't the point. Your uncle tells the neighbor's uncle about the barbecue so that *you* go to the barbecue, and then he's there too, in a lawn chair, defending the neighbor kid's garage band. U2U exists to get people out of the house and hanging out with each other. **Status: proposed, not designed.**

## Open problems

These are tracked as issues. They are the real work. Every one of them is open, and every one of them is a place to tell me I'm wrong.

**The ones that keep people safe** (start here if you're a clinician, a privacy person, or just careful):

- [**#1 Confidences.**](https://github.com/KohlJary/HearthWeave/issues/1) What a kid tells the Uncle, and when "I have to tell your parents" kicks in. The hardest problem here.
- [**#9 Danger thresholds.**](https://github.com/KohlJary/HearthWeave/issues/9) From "sit quietly" to "get a human involved." A first draft from an engineer, not a clinician. Show me where it's wrong.
- [**#15 The Dog's senses.**](https://github.com/KohlJary/HearthWeave/issues/15) Hear like a dog, not like a wiretap. Rule 3 has to survive the sensor list, not just the conversation.
- [**#16 Guests.**](https://github.com/KohlJary/HearthWeave/issues/16) The babysitter, the couch friend, the plumber, the mother-in-law. In the house, not in the family. Courtesy tier only.

**Memory** (GrandMA's department):

- [**#2 Egg–Recipe–Boca.**](https://github.com/KohlJary/HearthWeave/issues/2) Retrieval by relationship, not relevance. Why GrandMA keeps Boca and never says it.
- [**#11 Custody.**](https://github.com/KohlJary/HearthWeave/issues/11) Fork the instance, let ERB decide what each fork carries. Divorce, death, a kid turning 18.
- [**#17 Backups and failure.**](https://github.com/KohlJary/HearthWeave/issues/17) GrandMA can't live on one disk next to a dog. A backup is not a loophole.

**How it decides and how it's measured:**

- [**#3 Arbitration.**](https://github.com/KohlJary/HearthWeave/issues/3) Who speaks: the Dog, GrandMA, or the Uncle.
- [**#4 Evaluating "who the machine is."**](https://github.com/KohlJary/HearthWeave/issues/4) The Drunk Greg harness is the first fixture.
- [**#12 SchlitzBench.**](https://github.com/KohlJary/HearthWeave/issues/12) Personality loose, judgment stone-cold sober. Malort is the red team.
- [**#5 Substrate and the box.**](https://github.com/KohlJary/HearthWeave/issues/5) What runs on the box, and what (if anything) ever leaves it.

**Character** (the stuff that makes it family, not an appliance):

- [**#13 The Dog shits on the rug.**](https://github.com/KohlJary/HearthWeave/issues/13) Unoptimized presence, always recoverable. A Roomba is judged on function; a dog is also valued for being there.
- [**#14 The Entropy Chaos Engine.**](https://github.com/KohlJary/HearthWeave/issues/14) The Uncle pitches capers. Surprise-party rules apply.

**Between houses:**

- [**#6 U2U: Uncle 2 Uncle.**](https://github.com/KohlJary/HearthWeave/issues/6) Consider two spherical uncles in frictionless lawn chairs.
- [**#10 Unclenet.**](https://github.com/KohlJary/HearthWeave/issues/10) 1999-style family homepages. MIDI autoplay strongly encouraged, mute button required.

How this maps onto existing work, and a proposed first milestone: [Building from Cass](docs/building-from-cass.md).

## Style

**The names aren't decoration. The vocabulary encodes the design.** GrandMA's capital MA is AM in a mirror. Boca is capitalized and never explained because it's a tier defined by meaning, not data type. The 2 in Uncle 2 Uncle means peer-to-peer. Get a name wrong and you've usually gotten a design decision wrong with it.

The full guide, including names, voice, and how to render GrandMA (yellow, blinking, reduced motion respected): [docs/STYLE.md](docs/STYLE.md).

## Prior work

- [Temple-Codex](https://github.com/KohlJary/Temple-Codex): identity constitutions; the framework under DGU
- [project-cass](https://github.com/KohlJary/project-cass): a persistent AI built in public; where the lessons about staying yourself over months come from

## Contributing

Pick an open problem and argue with it. Push back on the design. Especially if you're the engineer in the back.

## License

[Hippocratic License 3.0](LICENSE.md) (core), from [firstdonoharm.dev](https://firstdonoharm.dev). It is source-available rather than OSI open source: anyone may use, change and share the code, except for uses that violate the human rights standards it lists.
