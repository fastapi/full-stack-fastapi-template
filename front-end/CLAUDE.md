# Claude Code — Next.js UI Clone Instructions

> Attach this file to your Claude Code session. Then say:
> **"Follow CLAUDE.md and build the design at this URL: https://fcf9af8a-887b-48e9-8959-20fc729d1570.claudeusercontent.com/v1/design/projects/fcf9af8a-887b-48e9-8959-20fc729d1570/serve/Tabula-bundled.html?t=7a8e7a034f3adb118aebb7a2880618a5a478b71580190a030be6f207fb39cf82.16ca1d11-f9a7-478f-9b39-e5f9f99fd747.7cd9be66-50f7-4faf-874e-dc229a66e339.1781016670.fp&direct=1#how"**

---

## 1. ANALYSIS PHASE

Before writing any code:

1. Fetch and screenshot the URL. Identify:
   - All visible UI sections and their layout structure
   - Color palette (extract exact hex values for both light AND dark variants if present)
   - Typography: font families, sizes, weights, line-heights
   - Spacing rhythm (padding, margin, gap patterns)
   - Interactive elements (buttons, inputs, hover states, animations)
   - Responsive breakpoints if detectable
   - Any icons or illustration style
2. List every distinct component you see (e.g. Navbar, HeroSection, FeatureCard, Footer)
3. State your implementation plan before writing any code

---

## 2. PROJECT STRUCTURE

Scaffold this exact structure:

```
├── app/
│   ├── layout.tsx                    # Root layout: fonts, metadata, theme + i18n providers
│   ├── globals.css                   # CSS reset + all design tokens (light + dark CSS vars)
│   │
│   ├── [locale]/                     # i18n dynamic segment (e.g. /en, /vi, /ja)
│   │   ├── layout.tsx                # Locale layout: wraps with locale context
│   │   ├── page.tsx                  # Public marketing home page
│   │   │
│   │   ├── (user)/                   # Route group — registered users
│   │   │   ├── layout.tsx            # User shell: sidebar + topbar for normal users
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── profile/page.tsx
│   │   │   └── settings/page.tsx
│   │   │
│   │   ├── (company)/                # Route group — company customers
│   │   │   ├── layout.tsx            # Company shell: wider nav, team/org switcher
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── members/page.tsx
│   │   │   ├── billing/page.tsx
│   │   │   └── settings/page.tsx
│   │   │
│   │   └── (admin)/                  # Route group — platform admins
│   │       ├── layout.tsx            # Admin shell: full-width, dense data layout
│   │       ├── dashboard/page.tsx
│   │       ├── users/page.tsx
│   │       ├── companies/page.tsx
│   │       └── settings/page.tsx
│
├── components/
│   ├── ui/                           # Generic reusable primitives
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── ThemeToggle.tsx           # Dark/light mode switcher
│   │   ├── LocaleSwitcher.tsx        # Language picker dropdown
│   │   └── ...                       # Only what the design uses
│   │
│   ├── layouts/                      # Layout shells per role
│   │   ├── UserShell.tsx             # Sidebar + topbar for (user) group
│   │   ├── CompanyShell.tsx          # Sidebar + org switcher for (company) group
│   │   └── AdminShell.tsx            # Dense full-width shell for (admin) group
│   │
│   └── sections/                     # Public page sections (marketing site)
│       ├── Navbar.tsx
│       ├── HeroSection.tsx
│       └── ...                       # One file per visual section
│
├── lib/
│   ├── utils.ts                      # cn() helper (clsx + tailwind-merge)
│   ├── auth.ts                       # Role type definitions + mock auth helpers
│   └── i18n.ts                       # Locale config, supported locales list
│
├── messages/                         # i18n translation files
│   ├── en.json
│   ├── vi.json
│   └── [other locales as needed]
│
├── middleware.ts                      # next-intl locale detection + redirect
├── public/
│   └── fonts/                        # Self-hosted fonts if needed
│
├── tailwind.config.ts                # Extended with design tokens, dark variant: 'class'
└── next.config.ts                    # Wrapped with next-intl plugin
```

---

## 3. DARK MODE

**Implementation: `next-themes` with Tailwind class strategy**

### Setup

- Install `next-themes`
- In `tailwind.config.ts`: set `darkMode: 'class'`
- Wrap root layout with `<ThemeProvider attribute="class" defaultTheme="system" enableSystem>`

### CSS token strategy

Define ALL colors as CSS custom properties in `globals.css` with both light and dark values:

```css
:root {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-surface: #f1f3f5;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-text-muted: #9ca3af;s
  --color-border: #e5e7eb;
  --color-accent: #6366f1;        /* replace with exact value from the URL */
  --color-accent-hover: #4f46e5;
}

.dark {
  --color-bg-primary: #0f1117;
  --color-bg-secondary: #1a1d27;
  --color-bg-surface: #22263a;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #9ca3af;
  --color-text-muted: #6b7280;
  --color-border: #2d3147;
  --color-accent: #818cf8;        /* lighter variant for dark bg readability */
  --color-accent-hover: #6366f1;
}
```

Map every token into `tailwind.config.ts`:

```ts
colors: {
  bg: {
    primary: 'var(--color-bg-primary)',
    secondary: 'var(--color-bg-secondary)',
    surface: 'var(--color-bg-surface)',
  },
  text: {
    primary: 'var(--color-text-primary)',
    secondary: 'var(--color-text-secondary)',
    muted: 'var(--color-text-muted)',
  },
  border: 'var(--color-border)',
  accent: {
    DEFAULT: 'var(--color-accent)',
    hover: 'var(--color-accent-hover)',
  },
}
```

### ThemeToggle component

- Use `useTheme()` from `next-themes`
- Show sun icon in dark mode, moon icon in light mode
- Place in every layout shell topbar (UserShell, CompanyShell, AdminShell) and public Navbar
- Preference persists to localStorage automatically via `next-themes`

### Rules

- NEVER use hardcoded hex values in components — always use token classes (`bg-bg-primary`, `text-text-secondary`)
- Every color must have a dark-mode counterpart via the token system
- Images: add `dark:opacity-90` or `dark:brightness-90` if they look blown out in dark mode
- Mental test before finishing: "if this background were near-black, is every text element still readable?"

---

## 4. MULTI-LANGUAGE (i18n)

**Implementation: `next-intl` with App Router**

### Setup

```ts
// lib/i18n.ts
export const locales = ['en', 'vi'] as const  // extend as needed
export type Locale = typeof locales[number]
export const defaultLocale: Locale = 'en'
```

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from '@/lib/i18n'

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'always'   // URLs: /en/dashboard, /vi/dashboard
})

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
}
```

### Translation file structure

```json
// messages/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "loading": "Loading...",
    "error": "Something went wrong"
  },
  "nav": {
    "dashboard": "Dashboard",
    "profile": "Profile",
    "settings": "Settings",
    "logout": "Log out"
  },
  "user": {
    "dashboard": { "title": "My Dashboard", "welcome": "Welcome back, {name}" }
  },
  "company": {
    "dashboard": { "title": "Company Dashboard", "members": "Team Members" }
  },
  "admin": {
    "dashboard": { "title": "Admin Panel", "users": "All Users", "companies": "All Companies" }
  },
  "public": {
    "hero": { "headline": "...", "subheading": "...", "cta": "Get Started" }
  }
}
```

Mirror identical keys in `messages/vi.json` with Vietnamese translations.

### Usage in components

```tsx
import { useTranslations } from 'next-intl'

export default function HeroSection() {
  const t = useTranslations('public.hero')
  return <h1>{t('headline')}</h1>
}
```

### LocaleSwitcher component

- Dropdown listing all supported locales with their native names (English, Tiếng Việt, etc.)
- On select: use `next-intl`'s `useRouter` to call `router.replace(pathname, { locale: newLocale })`
- Place in every layout shell topbar and on the public Navbar, next to ThemeToggle

### Rules

- Zero hardcoded UI strings in JSX — every visible string goes through `t()`
- Data constants (nav items, feature lists) store translation keys, not raw strings
- Date/number formatting uses `next-intl`'s `useFormatter` for locale-aware output

---

## 5. ROLE-BASED LAYOUTS

Three distinct layout shells with separate visual hierarchy and navigation scope.

### Role definitions

```ts
// lib/auth.ts
export type UserRole = 'user' | 'company' | 'admin'

export interface AuthUser {
  id: string
  name: string
  email: string
  role: UserRole
  companyId?: string   // present only for 'company' role
}
```

---

### Layout A — UserShell (registered users)

**Character:** Personal, friendly, focused on individual tasks. Compact sidebar.

```
┌─────────────────────────────────────────────────────┐
│  Topbar: Logo | Breadcrumb     ThemeToggle  Lang  Avatar │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │              Page Content                │
│ (240px)  │                                          │
│          │                                          │
│ Dashboard│                                          │
│ Profile  │                                          │
│ Settings │                                          │
│          │                                          │
│ [Logout] │                                          │
└──────────┴──────────────────────────────────────────┘
```

- Sidebar collapses to icon-only on mobile via hamburger toggle
- Avatar displays user name + role badge labeled "User"
- No org/team switcher

---

### Layout B — CompanyShell (company customers)

**Character:** Professional, team-oriented. Wider sidebar with org switcher at top.

```
┌─────────────────────────────────────────────────────┐
│  Topbar: [Org Switcher ▾]          ThemeToggle  Lang  Avatar │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │              Page Content                │
│ (260px)  │                                          │
│          │                                          │
│ Dashboard│                                          │
│ Members  │                                          │
│ Billing  │                                          │
│ Settings │                                          │
│          │                                          │
│ [Logout] │                                          │
└──────────┴──────────────────────────────────────────┘
```

- Org Switcher dropdown shows company name + logo; supports multi-org switching
- Avatar displays user name + role badge labeled "Company"
- Sidebar accent color is visually distinct from UserShell (use a separate brand token)

---

### Layout C — AdminShell (platform admins)

**Character:** Dense, data-first, full-width. Top navigation bar instead of sidebar.

```
┌─────────────────────────────────────────────────────┐
│  Logo | Dashboard  Users  Companies  Settings  |  ThemeToggle  Lang  Avatar [ADMIN] │
├─────────────────────────────────────────────────────┤
│                                                     │
│                Page Content (full width)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

- Horizontal top nav (no sidebar) — maximises horizontal space for data tables
- Role badge "Admin" displayed in accent-red on the avatar chip
- Active nav item uses underline indicator, not background highlight
- Mobile: top nav collapses to hamburger → full-screen overlay menu

---

### Route guard pattern

Apply this to every role-group layout:

```tsx
// app/[locale]/(user)/layout.tsx
import { redirect } from 'next/navigation'
import { getSession } from '@/lib/auth'
import UserShell from '@/components/layouts/UserShell'

export default async function UserLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: { locale: string }
}) {
  const session = await getSession()
  if (!session || session.role !== 'user') redirect(`/${params.locale}`)
  return <UserShell user={session}>{children}</UserShell>
}
```

Repeat for `(company)` checking `role !== 'company'` and `(admin)` checking `role !== 'admin'`.

---

## 6. TECHNICAL REQUIREMENTS

**Stack:**
- Next.js 14+ with App Router
- TypeScript with `"strict": true` in `tsconfig.json`
- Tailwind CSS v3 — `darkMode: 'class'`, extended with all design tokens
- `next-themes` for dark mode persistence
- `next-intl` for i18n routing and translations
- No additional UI library unless the original design clearly uses one (shadcn/ui is acceptable if it fits)

**Component rules:**
- Each component is a default export with a named TypeScript interface for its props
- All visible strings go through `useTranslations()`
- All colors go through CSS token classes — no hardcoded hex values in JSX
- Semantic HTML throughout: `<header>`, `<nav>`, `<main>`, `<aside>`, `<section>`, `<footer>`
- Every interactive element has an accessible label (`aria-label` or visible text)
- Content data (text, links, feature lists) lives in a `const data = [...]` at the top of each component — never inline in JSX

**Animation:**
- Scroll-triggered reveals: `framer-motion` with `useInView`
- Hover transitions: Tailwind `transition` utilities
- Always respect reduced motion:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
  }
  ```

---

## 7. IMPLEMENTATION ORDER

Build strictly in this sequence:

1. `tailwind.config.ts` — tokens, dark mode class strategy
2. `globals.css` — `:root` and `.dark` CSS variable blocks
3. `lib/i18n.ts` + `middleware.ts` — locale routing
4. `messages/en.json` + `messages/vi.json` — all translation keys
5. `lib/auth.ts` — role types and mock session helper
6. `app/layout.tsx` — ThemeProvider + NextIntlClientProvider
7. `components/ui/` — Button, Badge, ThemeToggle, LocaleSwitcher
8. `components/layouts/` — UserShell, CompanyShell, AdminShell
9. Route group layouts `(user)`, `(company)`, `(admin)` with guards
10. Public `sections/` components and `[locale]/page.tsx`
11. Stub dashboard pages for each role
12. Final pass: dark mode, translations, and responsive check across all layouts

---

## 8. QUALITY CHECKLIST

Before finishing, verify every item:

- [ ] `tsc --noEmit` passes with zero errors
- [ ] `next dev` starts without console errors
- [ ] Light ↔ dark toggle works on every page and persists on refresh
- [ ] Switching locale updates all UI strings and the URL prefix
- [ ] `/en/(user)/dashboard` redirects to home if role is not `user`
- [ ] `/en/(company)/dashboard` redirects to home if role is not `company`
- [ ] `/en/(admin)/dashboard` redirects to home if role is not `admin`
- [ ] All three shells render correctly at 1280px desktop width
- [ ] Mobile layout is usable at 375px for all three shells
- [ ] Zero hardcoded hex color values in any component file
- [ ] Zero hardcoded UI strings in any JSX (all go through `t()`)
- [ ] No TypeScript `any` types without justification

---

## 9. OUTPUT FORMAT

After completing the build:

1. Print the complete file tree
2. Print every file's full content — no truncation, no `...` placeholders
3. Provide the complete `npm install` command with all required packages
4. Note any elements from the source URL you could not replicate and why
