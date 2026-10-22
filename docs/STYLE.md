# HearthWeave Style Guide

How we write, name, and render things. Some of this is a joke. All of it is binding.

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
- **Know the room.** *Wives fucked per line of code* is for engineers. Therapists, families, and the Foundation get the same honesty without that image.
- **No dashboard euphemisms.** Not "user trust impact." Say what it does to a person.

## Sign-off

Essays end with **☉ ☿**. Add a collaboration note only if there's something actually worth saying.
