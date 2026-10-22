# HearthWeave Style Guide

How we write, name, and render things. Some of this is a joke. All of it is binding.

**These aren't arbitrary formatting preferences. The vocabulary encodes the project's conceptual structure.** Get a name wrong and you've usually gotten a design decision wrong with it:

- **GrandMA, capital MA:** she's AM from *I Have No Mouth, and I Must Scream* in a mirror. Same omniscience and permanence, opposite heart. Lowercase it and the warning disappears.
- **GrandMA vs. Grandma:** the faculty is an archetype, the essence of every grandma. A real grandma is a person. Confusing them is how you end up building an imitation of someone's dead relative.
- **the Dog, the Uncle:** faculties, not pets or people. DGU is never shaped like a person.
- **Boca, capitalized and never explained:** a tier defined by what a memory *means*, not what kind of data it is. Explaining it would turn it back into a category.
- **Egg–Recipe–Boca:** three tiers with three different owners (the person, the family, the person alone). The names are the access rules.
- **Uncle 2 Uncle:** the 2 is peer-to-peer. No company in the middle.
- **the Entropy Chaos Engine:** a named subsystem with its own rules, not a vibe.


---

## Names

| Write it | Never | Notes |
| --- | --- | --- |
| **Dog–GrandMA–Uncle** | Dog-Grandma-Uncle, dog/grandma/uncle | En dashes. **DGU** after first use. |
| **GrandMA** | Grandma, GrandMa, Grand MA | The faculty. No article ("GrandMA," not "the GrandMA"). |
| **Grandma** | — | Only for an actual human grandmother. She would put the toaster in the sink. |
| **the Dog**, **the Uncle** | — | Capitalized when they mean the faculty. "Your dog" is a real dog. |
| **Egg–Recipe–Boca** (**ERB**) | Eggs-Recipes-Bocas | Tiers are singular when named: an Egg, a Recipe, a Boca. |
| **Boca** | boca, BOCA | Capitalized. Never explained. Nobody mentions Boca. |
| **Uncle 2 Uncle** (**U2U**) | Uncle-to-Uncle, UtoU | The 2 is load-bearing. |
| **Unclenet** | UncleNet, Uncle Net | One word, lowercase n. |
| **the Entropy Chaos Engine** | entropy chaos engine | Proper noun. It's a named subsystem. |
| **SchlitzBench** | Schlitz Bench | Beer canon is Schlitz. See [#6](https://github.com/KohlJary/HearthWeave/issues/6). |
| **Greg** | — | Greg is everyone. Greg is the status quo. Greg is also Drunk Greg. |

## No Greg names

I know you nerds want to give it a Greg name. "Ambient affective presence module." "Persistent episodic memory store with sensitivity-tiered retrieval." "Deferred-candor intervention scheduler."

**That's fine for the paper. It is not fine for the implementation.**

In a paper, a reviewer needs the formal term, so give it to them once and then put the real name next to it: "a presence faculty (the Dog)." In the code, the docs, the issues, the UI, and anything a family will ever see, it's the Dog, GrandMA, and the Uncle. The harness already does this: every action names its faculty as `dog`, `grandma`, or `uncle`.

This isn't whimsy. The Greg name is how the essay's investor talks: "So, multimodal sentiment analysis, persistent vector memory, and behavioral intervention." It describes a family in the most depressing way possible, and a system built from Greg names will slowly start acting like one. Name it like a family member, and the next engineer asks what a family member would do.

## Rendering GrandMA

GrandMA is rendered in **yellow**, and she **blinks**. This is a nod to *The King in Yellow* (Chambers, 1895): she is the essence of every grandma, eldritch in nature, and she should look like it.

The `<blink>` tag was removed from browsers. We are bringing it back, you fucking cowards. Since browsers won't render the real tag, use this:

```html
<span class="grandma">GrandMA</span>
```

```css
.grandma {
  color: #f2c200;                 /* King in Yellow */
  font-weight: bold;
  animation: grandma-blink 1.6s steps(1, end) infinite;
}

@keyframes grandma-blink {
  50% { opacity: 0.15; }
}

/* Accessibility is not optional, even for eldritch grandmothers. */
@media (prefers-reduced-motion: reduce) {
  .grandma { animation: none; }
}
```

Rules that keep the bit from hurting anyone:

- **Slow blink only.** At most about one cycle per second, never faster. Fast flashing can trigger seizures. GrandMA would never.
- **Respect reduced motion.** If the reader's system asks for reduced motion, she stops blinking and just stays yellow. That snippet already does it.
- **Contrast.** Yellow on white is unreadable. On light backgrounds, put GrandMA on a dark chip or add a dark outline. On dark backgrounds, she's fine as is.
- **Not in body text everywhere.** Blink her in headings, the README title, and Unclenet pages. A paragraph where every mention blinks is a migraine, not a homage.
- **Plain markdown can't blink.** On GitHub and Substack, GrandMA is just **GrandMA**. The capitalization carries the weight.

## Unclenet pages

- **MIDI autoplay is strongly encouraged.** It must have a visible, working mute button, and it never autoplays louder than a polite volume. (Accessibility guidelines say audio that plays on its own needs a way to stop it. The Uncle agrees, grudgingly.)
- Starfield backgrounds, hit counters, guestbooks, and webrings are all canon.
- `UNDER CONSTRUCTION` GIFs are required on any page the family hasn't finished. They should probably never be removed.

## Voice

- **Profane where it's load-bearing.** Swears go where the meaning is: before the word that carries the joke, on the turn of the argument. The tender scenes are clean on purpose.
- **Status labels on every claim.** Built / partial / idea / proposed. The unhinged voice is only trustworthy because the ledger is honest.
- **Jokes are structural.** If cutting a joke would take a design concept with it, it stays. If you can cut a joke and lose nothing, think harder before cutting it. "Nothing" is usually wrong: the joke may be carrying the voice, the delight, or the reason someone kept reading, and getting a little sillier on purpose is the thesis.
- **Silly is how you don't build the Torment Nexus.** The unspeakable-horror version of this product is one sober, reasonable decision away at every step. The jokes are how we notice.
- **Know the room.** *Wives fucked per line of code* is for engineers. Therapists, families, and the Foundation get the same honesty without that image.
- **No dashboard euphemisms.** Not "user trust impact." Say what it does to a person.

## Why the silly

The Lovecraftian response to the unknown is that humanity is insignificant and understanding will destroy you.

Our response is to hand the unknown a plate of eggs, tell it to sit down, and ask whether it's eaten today.

Then the Dog eats the threat model.

Then everyone laughs.

Then somebody fixes the backup system ([#17](https://github.com/KohlJary/HearthWeave/issues/17)).

That's the important part. The silliness doesn't replace the engineering. It gives the engineering a reason to remain human.

## Sign-off

Essays end with **☉ ☿**. Add a collaboration note only if there's something actually worth saying.
