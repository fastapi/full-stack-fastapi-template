# Hero Screenshot Enhancement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain screenshot card in Hero.tsx with a browser-frame + perspective-tilt treatment to create a professional SaaS landing page graphic effect.

**Architecture:** Pure CSS/JSX change to a single component. No new files, no dependencies. The existing `<img>` card is restructured to add a macOS-style browser chrome bar above the screenshot and wrap the whole thing in a CSS 3D perspective transform (right side drops away, left stays flat).

**Tech Stack:** React, Tailwind CSS, inline styles for precise CSS values not available as Tailwind utilities.

---

## Chunk 1: Implement and verify

### Task 1: Create feature branch

**Files:**
- No file changes — git only

- [ ] **Step 1: Create and checkout a new branch**

```bash
cd /Users/yongzhang/Development/GEO/kila
git checkout -b feat/hero-screenshot-enhancement
```

Expected: `Switched to a new branch 'feat/hero-screenshot-enhancement'`

---

### Task 2: Update Hero.tsx

**Files:**
- Modify: `frontend/src/components/landing/Hero.tsx:76-97`

**Context:** The right column of the Hero grid (lines 76–97) currently renders a plain `<img>` inside a white rounded card with a decorative gradient overlay. We are replacing the card internals with: a browser chrome bar + screenshot, wrapped in a perspective tilt div.

- [ ] **Step 1: Open the file and locate the right column div**

The target block starts at line 76:
```tsx
<div
  className="relative animate-fade-in-right"
  style={{ animationDelay: "0.2s" }}
>
```
And ends at line 97 (`</div>` closing that block). Everything inside this div is what we're replacing.

- [ ] **Step 2: Replace the right column content**

Replace lines 76–97 entirely with the following:

```tsx
<div
  className="relative animate-fade-in-right pr-8 group"
  style={{ animationDelay: "0.2s" }}
>
  {/* Ambient glow — unchanged */}
  <div
    className="absolute -inset-6 rounded-[36px] bg-gradient-to-tr from-blue-600/15 via-transparent to-sky-400/15 blur-2xl animate-pulse"
    style={{ animationDuration: "6s" }}
  />
  {/* Scale wrapper — Tailwind hover scale must be on a separate div from the
      inline transform, otherwise the inline style wins and scale is silently ignored */}
  <div className="relative group-hover:scale-[1.02] transition-transform duration-500">
  {/* Perspective tilt wrapper */}
  <div
    style={{
      transform: "perspective(700px) rotateY(14deg) rotateX(3deg)",
      transformOrigin: "left center",
    }}
  >
    <div
      className="rounded-[28px] bg-white"
      style={{
        boxShadow:
          "24px 32px 70px -10px rgba(15,23,42,0.35), -4px 4px 20px -4px rgba(59,130,246,0.2)",
        border: "1px solid rgba(59,130,246,0.14)",
      }}
    >
      {/* Browser chrome bar */}
      <div
        style={{
          background: "#f1f3f4",
          padding: "8px 12px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          borderBottom: "1px solid #e0e0e0",
          borderRadius: "28px 28px 0 0",
        }}
      >
        <div style={{ display: "flex", gap: "5px" }}>
          <div style={{ width: "9px", height: "9px", borderRadius: "50%", background: "#ff5f57" }} />
          <div style={{ width: "9px", height: "9px", borderRadius: "50%", background: "#ffbd2e" }} />
          <div style={{ width: "9px", height: "9px", borderRadius: "50%", background: "#28c840" }} />
        </div>
        <div
          style={{
            flex: 1,
            background: "white",
            borderRadius: "5px",
            padding: "3px 8px",
            fontSize: "9px",
            color: "#999",
            border: "1px solid #e0e0e0",
          }}
        >
          app.kila.ai
        </div>
      </div>
      {/* Screenshot */}
      <img
        src="/assets/screens/brand-impression.png"
        alt="Kila brand impression dashboard"
        className="w-full object-cover"
        style={{ display: "block", borderRadius: "0 0 28px 28px" }}
      />
    </div>
  </div>{/* end tilt wrapper */}
  </div>{/* end scale wrapper */}
</div>
```

Key changes vs. current code:
- `pr-8` added to outer div to give the tilted right edge room
- `group` moved from inner card div to the outer div
- Decorative `absolute h-12` gradient overlay **removed** (replaced by browser chrome bar)
- `overflow-hidden` **removed** from card div (prevented perspective rendering in Safari)
- `group-hover:scale-[1.02] transition-transform duration-500` moved from `<img>` to the tilt wrapper, so the whole card scales as a unit
- New browser chrome bar div inserted above `<img>`
- `<img>` loses `h-full` and `transform` classes (transform now lives on wrapper); gains `style={{ borderRadius: "0 0 28px 28px" }}` to round only the bottom corners

- [ ] **Step 3: Verify the dev server starts without errors**

```bash
cd /Users/yongzhang/Development/GEO/kila/frontend
pnpm dev
```

Expected: No TypeScript or build errors. Server starts on port 5173 (or similar).

- [ ] **Step 4: Visual check in browser**

Open `http://localhost:5173` and verify:
- The hero screenshot has a grey browser chrome bar at the top with 3 coloured dots and `app.kila.ai` text
- The card tilts in 3D: left edge is flat/vertical, right edge drops away into depth
- The right side of the card has visible shadow depth
- Hovering the hero section causes the entire tilted card to scale up slightly
- No clipping of the right edge (the card should fully visible, not cut off)
- Looks correct in both a wide desktop viewport and a narrowed browser window

- [ ] **Step 5: Commit**

```bash
cd /Users/yongzhang/Development/GEO/kila
git add frontend/src/components/landing/Hero.tsx
git commit -m "feat: add browser chrome frame + perspective tilt to hero screenshot"
```

---

### Task 3: Commit spec and design docs

**Files:**
- Add: `frontend/docs/superpowers/specs/2026-03-18-hero-screenshot-enhancement-design.md`
- Add: `frontend/docs/superpowers/plans/2026-03-18-hero-screenshot-enhancement.md`

- [ ] **Step 1: Commit docs**

```bash
cd /Users/yongzhang/Development/GEO/kila
git add frontend/docs/
git commit -m "docs: add hero screenshot enhancement spec and plan"
```
