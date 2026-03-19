# Hero Screenshot Enhancement — Design Spec

**Goal:** Make the `brand-impression.png` screenshot in the Hero section look like a high-quality professional landing page graphic using pure CSS — no image editing.

**Scope:** `Hero.tsx` only. ProductSection and all other screenshots are out of scope.

---

## What Changes

### File
- Modify: `src/components/landing/Hero.tsx`

### Current behaviour
The screenshot is rendered as a plain `<img>` inside a rounded white card with a basic box-shadow and a hover scale animation. There is also an `absolute` decorative gradient overlay (`h-12 bg-gradient-to-r from-slate-900/5 to-transparent`) at the top of the card.

### New behaviour
The card gains three visual upgrades:

**1. Browser chrome bar**

A light grey (`#f1f3f4`) bar sits above the screenshot, separated from it by a `1px solid #e0e0e0` bottom border. It contains:
- Three macOS-style traffic-light dots (red `#ff5f57`, yellow `#ffbd2e`, green `#28c840`), each `9×9px`, `gap: 5px`, on the left
- A pill-shaped address bar to the right of the dots that fills the remaining horizontal space. It has a white (`#ffffff`) background, `1px solid #e0e0e0` border, `border-radius: 5px`, padding `3px 8px`, and shows the text `app.kila.ai` in `#999` at `9px` font size

The existing `absolute` decorative gradient overlay div is **removed** — it is visually replaced by the browser chrome bar.

**2. Perspective tilt**

The entire card (chrome bar + screenshot) is wrapped in a `div` that applies:
```
transform: perspective(700px) rotateY(14deg) rotateX(3deg)
transform-origin: left center
```
The left edge stays flat; the right edge drops away into depth.

Add `pr-8` to the **`relative animate-fade-in-right` div** (the outermost div of the right column, not the tilt wrapper itself) so the tilted right edge has room and does not clip.

The tilt itself is **static** — no CSS transition on the tilt transform.

**3. Directional shadow + blue accent border**

- Shadow biased right to reinforce depth: `box-shadow: 24px 32px 70px -10px rgba(15,23,42,0.35), -4px 4px 20px -4px rgba(59,130,246,0.2)`
- Border: `1px solid rgba(59,130,246,0.14)` (replaces the current `border-slate-200/70`)

**Note on `overflow-hidden`:** Remove `overflow-hidden` from the inner card div (the one that currently holds the decorative overlay and `<img>`). The browser chrome bar structure (a flex row above the image) naturally constrains content without needing `overflow-hidden`, and keeping it on a direct ancestor of the 3D-transformed element causes perspective flattening in Safari/WebKit.

### Hover animation

The existing `group-hover:scale-[1.02] transition-transform duration-500` moves from the `<img>` tag to the **perspective tilt wrapper div**, so the entire card (chrome + image) scales together as one unit. This avoids a visual conflict between a flat image scale and a 3D-tilted parent. The `group` class stays on the outermost relative div as before.

### What stays the same
- The animated blue/sky glow blobs behind the card (`-inset-6 rounded-[36px] bg-gradient-to-tr ... blur-2xl animate-pulse`)
- All copy, CTAs, stats row, and layout in Hero.tsx
- Everything in ProductSection.tsx and all other landing components
