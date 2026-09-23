# Loop: concept demo

> **Meet Loop, the crochet app that keeps your place in every pattern and mails you a hand-dyed colorway each month. You only find out the color when you open it.**

A clickable, front-end-only mobile web demo made to pitch an idea. Nothing talks to a server. Orders, deliveries and payments are simulated on the device.

**Run it:** open `index.html` in a browser. It looks best on a phone; on desktop it shows inside a phone frame. There's no build step.

An earlier concept (Lune, a period tracker) is kept in [`lune/`](lune/) for reference.

---

## The lane

**Who it's for:** people who crochet, a hobby that has exploded with women in their 20s and 30s.

**The annoying part:** you lose your place in a pattern. You tally rows on scrap paper, keep three unfinished projects in three tote bags, and guess how much yarn you need for a project.

**What Loop does:** it's a free row counter that *follows the pattern for you*. Tap when a round is done and it moves to the next instruction, shows the stitch count, and flags notes like "place safety eyes now". Around that sits a stash, free patterns, and a community feed.

**The surprise, done naturally:** hand-dyed yarn clubs are already a big part of this hobby, and part of their appeal is not knowing the colorway until the parcel arrives. Crocheters also collect stitch-marker charms. Loop's **Yarn Club** is a monthly parcel with a secret colorway, a pattern designed for it, and one charm from a seasonal set. That's the blind-box mechanic from the Discord story, but it reads as a yarn club, not a loot box. There are no odds, no rarity labels, and no re-rolls. There's one special gold charm, mentioned once in small print.

**Mission:** *Keep people making. Take the counting off their hands, and put something lovely in the mailbox.*

## Business model

| | Free | Yarn Club ($24/month) | Kits (one-off) |
|---|---|---|---|
| Row counter that follows the pattern | ✅ | ✅ | ✅ |
| Free pattern library, stash, time tracking | ✅ | ✅ | ✅ |
| Monthly hand-dyed colorway (surprise) | | ✅ | |
| Pattern designed for that colorway | | ✅ | |
| Marker charm in every parcel | | ✅ | ✅ |
| Everything for one project | | | $18–32 |

- Free tools get people in and keep them opening the app every time they crochet.
- The Club is recurring revenue. Skip a month or leave in two taps.
- Kits are the natural impulse buy from any pattern page, and every kit also carries a charm, so free users collect too.
- Colorways lean toward the palettes you pick during onboarding.

## What's in the demo

1. **Onboarding:** your name, skill level, what you like to make, and the colors you're drawn to. You start with a real beginner pattern (Strawberry Pal).
2. **Home:** your current project with its progress, minutes crocheted this week, next month's colorway (a secret) and a feed of things members made with last month's colorway.
3. **Make → Counter:** the current round in big type, the stitch count, pattern notes, a large tap target, undo, the next rounds, and a session timer. Finishing a project gets its own celebration.
4. **Club:** a countdown to the next drop and what comes in it, kits, orders, skip or join. Checkout → order tracking (placed, packed, on the way, delivered in about 25s) → **unwrap**: untie the twine, open the paper, the colorway is revealed and a charm drops in.
   - **Save for IRL** keeps it wrapped in the app, so the real parcel is still a surprise.
5. **Stash:** your yarn (tap a skein to see which patterns it has enough yardage for), plus the **Marker tin** holding your charm set.
6. **Profile:** skip the Club or leave, plus demo controls (fast shipping, reset).

### Demo script (about 2 minutes)
Onboard → **Pick up where you left off** → tap the counter a few times (watch R8's safety-eye note appear) → **Club** → **Join** → **Track it** → wait about 25s → **Unwrap it here** → **See stash** → **Markers**.
