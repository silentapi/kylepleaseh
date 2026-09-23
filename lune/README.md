# Lune: concept demo

> **Your period kit shows up before your period does.**

A clickable, front-end-only mobile web demo to pitch a product idea. Nothing talks to a server. Orders, deliveries and payments are simulated on the device.

**Run it:** open `index.html` in any browser. It looks best on a phone, or in a desktop browser, which shows a phone frame. There's no build step and no dependencies. It uses Google Fonts and falls back to system fonts offline.

---

## The lane

**Problem.** Almost every woman has been caught without supplies at some point: at work, on a trip, or at 11pm with an empty box under the sink. Period tracking apps already predict the date, but they stop at a notification. You still have to remember, go to the store, and buy the stuff.

**Solution.** Lune is a free cycle tracker that can also send supplies. If you opt in, it ships your products timed to your cycle (not the calendar) so the box lands **3 days before your period**. The Discord blind-box story is the fun part: **every box has a sealed mystery collectible** from a numbered series. You can reveal it in the app, or tap "Open it IRL" and keep the surprise for the real unboxing.

**Mission statement.** *Take the chore out of every cycle, and put a small moment of delight in its place.*

## Why everyone wins

| | Free | Lune Box ($16/cycle + optional extras) |
|---|---|---|
| Cycle tracking, predictions, calendar | ✅ | ✅ |
| Daily check-in + phase tips | ✅ | ✅ |
| Moon stars → free **digital** buddy pouch | ✅ | ✅ |
| Products delivered 3 days before your period | | ✅ |
| Sealed **real** collectible in every box | | ✅ |
| Add-ons: heat patches, chocolate, tea | | ✅ |
| One-off next-day top-up kit ($9) | ✅ | ✅ |

- **The user** gets a genuinely useful free tracker, never runs out, and gets a small treat on the worst week of the month. Skip and cancel each take two taps, with no guilt trips.
- **The business** gets recurring revenue on a need that never goes away (about 13 cycles a year, not 12 months). Add-ons raise the order value, and a collectible series drives retention ("I only need Twinkle and Prism"). New series drop each season.
- **Ethics guardrails built in:** published pull odds for each rarity, no pay-to-reroll, the free tier never paywalls health info, and a medical disclaimer.

## What's in the demo

1. **Onboarding** (4 screens): name, last period date, cycle length, products, flow. No paywall at the start.
2. **Today:** cycle ring with phase, period countdown, box status card, daily check-in (mood + symptoms), moon-star streak, and a phase tip.
3. **Calendar:** logged, predicted and fertile days, plus the box arrival day. Tap any day to log a period start.
4. **Box:** "how it works" pitch, contents built from your products and flow, add-on toggles, checkout, a simulated order timeline (placed → packed → shipped → out for delivery → delivered in about 25s), order history, skip/resume, cancel.
5. **Mystery reveal:** tap the foil pouch 3 times to tear it open. Rarity and odds are shown, and the buddy goes to your shelf. Or choose **Open it IRL** and add it later.
6. **Shelf:** 12-buddy "Night Garden" series with Common, Rare and Secret tiers. Tiles show whether you own the real figure, the digital one, or both.
7. **Profile:** cycle and period length, skip or cancel the box, plus **demo controls** (fast shipping toggle, "give me 5 stars", reset demo).

### Demo script (≈90 seconds)
Onboard → do a check-in (earns the 5th star) → **Open pouch** on Today → **Box** tab → **Start my box** → **Track order** → wait about 25s for "Delivered" → **Reveal now** (or **Open it IRL**) → **Shelf**.

## Design notes
Motion follows design-engineering practice: custom ease-out curves, UI transitions under 300ms, a 0.97 press scale on buttons, drag-to-dismiss bottom sheets on a drawer curve, and no animation on high-frequency actions like tab switches. Hover effects are limited to fine pointers, and everything respects `prefers-reduced-motion`. QA was done in headless Chromium at 390×844 and 375×667, plus a desktop frame: no console errors and no horizontal overflow.
