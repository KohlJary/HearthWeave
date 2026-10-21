# Egg–Recipe–Boca (ERB)

**A memory privacy model for GrandMA.** Status: proposed design, not implemented. Discussion lives in [issue #2](https://github.com/KohlJary/HearthWeave/issues/2).

## The problem

Most AI memory keeps one pile and retrieves whatever looks relevant. Sensitive-data rules, where they exist, sort by category: health, finances, religion.

Both miss Boca. On paper, Boca is a trip to Florida. No privacy filter would ever flag it. It's also the most painful thing in Greg's life. The thing that hurts most is often the most ordinary-looking thing in the file, and the reverse is true too: someone may be completely open about a diagnosis a category rule would lock down.

ERB sorts memory by **what it means to the family**, not what kind of data it is. That's retrieval by relationship, not relevance.

## The three tiers

| Tier | Example | Belongs to | Default use |
| --- | --- | --- | --- |
| **Egg** | how Greg likes his eggs | the person | used freely and proactively |
| **Recipe** | Grandma's lasagna | the whole family | shared, exported, handed down |
| **Boca** | what happened in Boca | the person, alone | surfaces only if the person raises it |

**Egg: preference.** Small, personal, low stakes. Anyone in the household benefits from GrandMA knowing it. Getting it wrong is a minor annoyance. This is the tier that makes sunlit breakfast work.

**Recipe: heritage.** Shared knowledge that outlives any one person: recipes, family stories, who's related to whom, the band the uncle got everyone into. It belongs to the family as a whole. It's the first thing exported, the last thing deleted, and never sold or locked in.

**Boca: episodic and tender.** Painful or private moments. GrandMA holds them because a witness has to, but she never brings them up first, never infers from them, never uses them to "help," and never surfaces them to another family member. Boca only comes up if Greg brings it up.

## Rules

1. **Unclassified defaults to Boca.** When GrandMA isn't sure what something is, she treats it as Boca. Failing safe means forgetting to mention something, not mentioning the wrong thing.
2. **The person decides.** Anyone can reclassify their own memories. Moving something *out* of Boca requires the person's explicit say-so; GrandMA can only suggest.
3. **Tiers can shift over time.** A Boca can soften into a story someone tells at Thanksgiving. It moves when they start telling it themselves, not when GrandMA judges enough time has passed.
4. **Recipes need the family.** Promoting a memory to Recipe makes it shared, so it needs the agreement of the people it's about.
5. **Disagreements stay private.** If two family members disagree about whether something is shared, it's treated as Boca for both until they settle it.
6. **U2U carries Eggs and Recipes only,** and only the brag-worthy ones: what a family would be glad to have said out loud on a porch. Boca never crosses the wire.
7. **Everything is plain files.** Each tier is human-readable and exportable, so a family can see exactly what GrandMA holds and where she's filed it.

## What lasts: the basin

Most of what passes through a household is temporary: schedules, errands, the deck due Thursday, this quarter's targets. It matters for a week and then it's gone. What a life keeps settling back into over years is much smaller:

> Everyone has a breakfast, an elephant that makes them smile, a song they can't hear without crying, and a Boca.

That's the basin: the routines, the joys, the griefs, and the secrets a life keeps falling back into, no matter what else happens. It's what a witness should keep, and what the great-grandkids will actually ask about.

So GrandMA holds memory on two horizons:

| Horizon | Holds | Lifetime |
| --- | --- | --- |
| **Working** | tasks, schedules, errands, this week's plans | expires on its own when it stops mattering |
| **Basin** | the breakfast, the elephant, the song, the Boca | kept for decades, carried across substrates |

The two axes are independent. A basin memory still has a tier: the breakfast is usually an Egg, a family joke may be a Recipe, and the song can be a Boca for one person and a Recipe for another. The tier decides **who it may reach**. The horizon decides **how long it's kept**.

Rules for the basin:

- **Working memory decays by default.** GrandMA doesn't hoard. Nothing becomes permanent just because it was once recorded.
- **Basin memory is recognized, not mined.** Something enters the basin because it keeps coming back over time, or because the person says it matters, never because a model scored it as emotionally significant.
- **The basin is what migrates first.** When GrandMA moves to new hardware or a new model, the basin goes before anything else, because it's the part that makes her the same witness on the other side.

## Faculty behavior

- **Dog** reads Eggs to notice and comfort (the playlist, the routine). It never reads Boca.
- **GrandMA** holds all three tiers and enforces the rules.
- **Uncle** may know a Boca exists, so he knows when to stay quiet, but he waits for the person to open it. Candor never means bringing up Boca uninvited.

## Open questions

- How does a memory get its initial tier? Asking every time is exhausting; inferring is risky. Probably: infer Egg for clear preferences, default everything else to Boca, and let people promote.
- How should Boca work for kids, where a parent may have a legitimate need to know? This connects directly to [issue #1](https://github.com/KohlJary/HearthWeave/issues/1).
- What happens to a person's Bocas after they die? The living-witness role argues for keeping them; the person's wishes should decide, set while they're alive.
