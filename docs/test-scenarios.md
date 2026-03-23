# Kila Platform — Comprehensive Test Scenarios

> **Scope:** End-to-end user experience (landing page → onboarding → brand management → dashboards → billing) and offline pipeline jobs (subscription eligibility → AI search → metrics → insight signals).
>
> **How to read this document:**
> - Each scenario has an ID (`TS-XXX`), preconditions, numbered steps, and expected results.
> - `[FE]` = frontend assertion, `[BE]` = backend/API assertion, `[DB]` = database assertion, `[JOB]` = offline job assertion.
> - Scenarios are grouped by user journey phase.

---

## Table of Contents

1. [Landing Page & Marketing](#1-landing-page--marketing)
2. [Authentication](#2-authentication)
3. [Onboarding — Profile Setup](#3-onboarding--profile-setup)
4. [Brand Management](#4-brand-management)
5. [Segment & Prompt Management](#5-segment--prompt-management)
6. [Dashboard — Brand Impression](#6-dashboard--brand-impression)
7. [Dashboard — Competitive Analysis](#7-dashboard--competitive-analysis)
8. [Insight — Market Dynamic](#8-insight--market-dynamic)
9. [Insight — Risk Intelligence](#9-insight--risk-intelligence)
10. [Pricing & Subscription](#10-pricing--subscription)
11. [Billing & Stripe Portal](#11-billing--stripe-portal)
12. [Subscription Expiry & Enforcement](#12-subscription-expiry--enforcement)
13. [Settings & Profile Management](#13-settings--profile-management)
14. [Quota & Entitlement Gates](#14-quota--entitlement-gates)
15. [Offline Pipeline — Stage 0: Subscription Eligibility Job](#15-offline-pipeline--stage-0-subscription-eligibility-job)
16. [Offline Pipeline — Stage 1: Brand Search Response Job](#16-offline-pipeline--stage-1-brand-search-response-job)
17. [Offline Pipeline — Stage 2: Basic Metrics Jobs](#17-offline-pipeline--stage-2-basic-metrics-jobs)
18. [Offline Pipeline — Stage 3: Awareness Performance Jobs](#18-offline-pipeline--stage-3-awareness-performance-jobs)
19. [Offline Pipeline — Stage 4: Insight Signal Jobs](#19-offline-pipeline--stage-4-insight-signal-jobs)
20. [Pipeline Orchestrator — daily_pipeline.py](#20-pipeline-orchestrator--daily_pipelinepy)
21. [Data Integrity & Edge Cases](#21-data-integrity--edge-cases)
22. [Security](#22-security)

---

## 1. Landing Page & Marketing

### TS-001 — Landing page renders all sections for unauthenticated visitor

**Preconditions:** User is not signed in. Navigate to `https://spekila.com`.

**Steps:**
1. Open the root URL `/`
2. Scroll through the entire page

**Expected:**
- `[FE]` Header shows logo, nav links, and "Sign In" / "Get Started" buttons
- `[FE]` Hero section shows headline "Turn AI Search Into Growth Intelligence" and a "Start Free Trial" CTA button
- `[FE]` Feature Grid section renders feature cards (Brand Impression, Competitive Analysis, Market Dynamic, etc.)
- `[FE]` Product section renders three category groups (Brand Impression, Competitive Analysis, Market Dynamic) with screenshots
- `[FE]` Integrations section shows AI model logos: Gemini, ChatGPT, Claude, Copilot, Perplexity
- `[FE]` How It Works section renders step-by-step process cards
- `[FE]` FAQ section renders accordion items; each expands on click
- `[FE]` Pricing section renders Free Trial ($0), Pro ($299/mo), and Enterprise (Contact Sales) cards
- `[FE]` Final CTA section renders with "Start Free Trial" and "Book a Demo" buttons
- `[FE]` Footer renders with links

---

### TS-002 — Landing page "Start Free Trial" CTA opens Clerk sign-up modal

**Preconditions:** Unauthenticated visitor on `/`.

**Steps:**
1. Click "Start Free Trial" button in the Hero section

**Expected:**
- `[FE]` Clerk sign-up modal opens in-page (not a redirect)
- `[FE]` After successful sign-up, user is redirected to `/app/brands` (Clerk `forceRedirectUrl`)

---

### TS-003 — Landing page pricing "Start Free Trial" button opens Clerk sign-up

**Preconditions:** Unauthenticated visitor.

**Steps:**
1. Scroll to Pricing section
2. Click "Start Free Trial" on the Free Trial card

**Expected:**
- `[FE]` Clerk sign-up modal opens
- `[FE]` "Contact Sales" on Enterprise card links to a contact form or email (does not open Clerk)

---

### TS-004 — Signed-in user visiting `/` is redirected to `/app/brands`

**Preconditions:** User is signed in via Clerk.

**Steps:**
1. Navigate to `/`

**Expected:**
- `[FE]` App redirects immediately to `/app/brands` without showing the landing page

---

### TS-005 — FAQ items expand and collapse correctly

**Preconditions:** Any user on `/`.

**Steps:**
1. Click an FAQ question
2. Verify the answer expands
3. Click the same question again
4. Verify the answer collapses

**Expected:**
- `[FE]` Each FAQ item toggles open/closed independently
- `[FE]` No more than one item needs to be forced closed when another opens (accordion behavior depends on implementation)

---

## 2. Authentication

### TS-010 — New user signs up via Clerk and is auto-provisioned in backend

**Preconditions:** Email does not exist in the system.

**Steps:**
1. Click "Sign Up" anywhere on the landing page
2. Complete Clerk sign-up with a new email and password
3. Clerk redirects to `/app/brands`
4. App calls `POST /api/v1/auth/clerk-sync`

**Expected:**
- `[BE]` `POST /api/v1/auth/clerk-sync` returns 200 with `{ profile_complete: false }`
- `[DB]` New record created in `UsersTable` with `external_user_id` = Clerk user ID
- `[DB]` New record created in `UserSubscriptionTable` with `tier=free_trial`, `status=active`, `trial_expires_at = now() + 28 days`
- `[FE]` User is redirected to `/app/profile-setup` (because `profile_complete === false`)

---

### TS-011 — Returning user signs in and lands on brands page

**Preconditions:** User exists in DB with completed profile.

**Steps:**
1. Click "Sign In" on the landing page
2. Enter valid credentials in Clerk sign-in modal
3. Clerk redirects to `/app/brands`
4. App calls `POST /api/v1/auth/clerk-sync`

**Expected:**
- `[BE]` `/clerk-sync` returns 200 with `{ profile_complete: true }`
- `[FE]` User lands on `/app/brands` with their brand list visible
- `[FE]` No redirect to profile setup

---

### TS-012 — Existing user whose email already exists in DB is linked by email on first Clerk sign-up

**Preconditions:** A `UsersTable` record exists for `user@example.com` (created via legacy signup) with no `external_user_id`. User signs up via Clerk using the same email.

**Steps:**
1. Sign up with Clerk using `user@example.com`
2. App calls `POST /api/v1/auth/clerk-sync`

**Expected:**
- `[DB]` Existing `UsersTable` row has its `external_user_id` updated to the Clerk user ID (no duplicate created)
- `[BE]` Response returns 200 with the user's existing data

---

### TS-013 — Unauthenticated access to `/app/*` routes is blocked

**Preconditions:** User is not signed in.

**Steps:**
1. Navigate directly to `/app/brands`

**Expected:**
- `[FE]` App redirects to `/` (landing page) — Clerk `AppGuard` enforces this

---

### TS-014 — Legacy signup via `POST /api/v1/auth/signup`

**Preconditions:** Using API directly.

**Steps:**
1. POST to `/api/v1/auth/signup` with `{ email, password, first_name, last_name }`

**Expected:**
- `[BE]` Returns 201 with `access_token` and `refresh_token`
- `[DB]` `UsersTable` record created
- `[DB]` `UserSubscriptionTable` record created with `tier=free_trial`

---

### TS-015 — Login with invalid credentials returns 401

**Preconditions:** User exists in DB.

**Steps:**
1. POST to `/api/v1/auth/login` with wrong password

**Expected:**
- `[BE]` Returns 401 with error message
- `[DB]` No session created

---

### TS-016 — Token cache works: repeated Clerk-sync calls within 10 hours use cached result

**Preconditions:** User is signed in.

**Steps:**
1. Call `POST /api/v1/auth/clerk-sync` twice in quick succession with the same JWT

**Expected:**
- `[BE]` Both calls succeed (200)
- `[BE]` Second call uses in-memory cache (no Clerk API call on second verify) — verifiable via backend logs showing cache hit

---

## 3. Onboarding — Profile Setup

### TS-020 — New user is redirected to profile setup until profile is complete

**Preconditions:** New user just signed up (profile_complete = false).

**Steps:**
1. After Clerk sign-up, user is at `/app/profile-setup`
2. Navigate away to `/app/brands` without completing the form

**Expected:**
- `[FE]` App immediately redirects back to `/app/profile-setup`
- `[FE]` The redirect happens on every `/app/*` navigation until profile is complete

---

### TS-021 — Profile setup form validates required fields

**Preconditions:** User is on `/app/profile-setup`.

**Steps:**
1. Leave First Name blank
2. Leave Last Name blank
3. Leave Company Name blank
4. Click "Continue" / submit

**Expected:**
- `[FE]` Form shows inline validation errors for First Name, Last Name, and Company Name
- `[FE]` Form does NOT submit

---

### TS-022 — Company name autocomplete returns existing companies

**Preconditions:** Company "Acme Corp" exists in `CompaniesTable`.

**Steps:**
1. In the Company Name field, type "Acme"
2. Wait for debounce (~300ms)

**Expected:**
- `[FE]` Autocomplete dropdown appears showing "Acme Corp"
- `[BE]` `GET /api/v1/profile/companies/search?q=Acme` returns matching companies
- `[FE]` Selecting "Acme Corp" from dropdown fills the field

---

### TS-023 — Completing profile setup creates profile record and redirects to brands

**Preconditions:** User on `/app/profile-setup`.

**Steps:**
1. Fill in: First Name = "Jane", Last Name = "Smith", Company = "TestCo", Email = pre-filled
2. Click submit

**Expected:**
- `[BE]` `POST /api/v1/profile/setup` returns 200
- `[DB]` `UsersProfileTable` record created with correct name, email, company_id
- `[DB]` If "TestCo" is a new company, a `CompaniesTable` record is created
- `[FE]` User is redirected to `/app/brands`
- `[FE]` Subsequent navigation does NOT redirect to profile setup

---

### TS-024 — Profile setup with a new company name creates the company automatically

**Preconditions:** "BrandNewCo" does not exist in `CompaniesTable`.

**Steps:**
1. Type "BrandNewCo" in Company Name and do not select an autocomplete result
2. Submit the form

**Expected:**
- `[DB]` New `CompaniesTable` record created for "BrandNewCo"
- `[DB]` `UsersProfileTable` references the new `company_id`

---

## 4. Brand Management

### TS-030 — Free trial user can create exactly 1 brand

**Preconditions:** User is signed in, profile complete, subscription tier = `free_trial`, no brands exist.

**Steps:**
1. Navigate to `/app/brands`
2. Click "Add Brand"
3. Enter Brand Name = "Nike", Description = "Athletic footwear"
4. Add 1 segment: Name = "Running Shoes", Prompt = "What is the best running shoe brand?"
5. Click "Save"

**Expected:**
- `[FE]` Brand appears in the brand list table
- `[BE]` `POST /api/v1/brands/setup` returns 201
- `[DB]` `BrandsTable` row created with `is_active=true`
- `[DB]` `BrandUserTable` row created with `user_role=owner`
- `[DB]` `BrandPromptTable` row created with `segment="Running Shoes"`, `is_active=true`

---

### TS-031 — Free trial user cannot add a second brand (quota enforced)

**Preconditions:** Free trial user with 1 active brand already created.

**Steps:**
1. Navigate to `/app/brands`
2. Click "Add Brand"

**Expected:**
- `[FE]` "Add Brand" button is either disabled or wrapped in a `QuotaGate` that shows an upgrade prompt
- `[BE]` If API called directly: `POST /api/v1/brands/setup` returns 403 with quota exceeded error

---

### TS-032 — Brand edit — update name and description

**Preconditions:** User has 1 brand.

**Steps:**
1. On `/app/brands`, click the edit (pencil) icon on the brand row
2. Change name to "Nike Inc", change description to "Updated desc"
3. Save

**Expected:**
- `[FE]` Brand row updates immediately in the table
- `[BE]` `PATCH /api/v1/brands/{brand_id}` returns 200
- `[DB]` `BrandsTable` row updated

---

### TS-033 — Brand deactivation via toggle disables prompts

**Preconditions:** User has 1 active brand.

**Steps:**
1. On `/app/brands`, click the "Active" checkbox to deactivate the brand

**Expected:**
- `[BE]` `PATCH /api/v1/brands/{brand_id}` with `{ is_active: false }` returns 200
- `[DB]` `BrandsTable.is_active = false`
- `[DB]` All associated `BrandPromptTable` rows: `is_active = false`
- `[FE]` Brand row shows inactive state

---

### TS-034 — Reactivating a brand reactivates its prompts

**Preconditions:** Brand is inactive.

**Steps:**
1. Click the inactive checkbox to re-activate

**Expected:**
- `[DB]` `BrandsTable.is_active = true`
- `[DB]` `BrandPromptTable` rows for this brand: `is_active = true`

---

### TS-035 — Brand delete removes brand and all associated data

**Preconditions:** User has 1 brand with segments and prompts.

**Steps:**
1. Click the trash icon on the brand row
2. Confirm deletion in the confirmation dialog

**Expected:**
- `[BE]` `DELETE /api/v1/brands/{brand_id}` returns 200
- `[DB]` `BrandsTable` row deleted (or soft-deleted)
- `[DB]` `BrandUserTable` rows for this brand deleted
- `[DB]` `BrandPromptTable` rows for this brand deleted
- `[FE]` Brand disappears from the table

---

### TS-036 — Non-owner cannot delete or edit a brand

**Preconditions:** User B is a `monitor` member of a brand owned by User A.

**Steps:**
1. User B navigates to `/app/brands`
2. Attempts to click delete icon

**Expected:**
- `[FE]` Delete and edit icons are hidden or disabled for monitor-role users
- `[BE]` `DELETE /api/v1/brands/{brand_id}` with User B's token returns 403

---

### TS-037 — Brand detail view shows segments and prompts

**Preconditions:** Brand has 2 segments.

**Steps:**
1. Click the eye (view) icon on a brand row
2. Observe the brand detail panel

**Expected:**
- `[BE]` `GET /api/v1/brands/{brand_id}` returns brand with nested segments and prompts
- `[FE]` Detail view shows each segment name and its prompt text

---

### TS-038 — Only 1 brand can be active at a time regardless of tier

**Preconditions:** User has 1 active brand and 1 inactive brand.

**Steps:**
1. Activate the second brand

**Expected:**
- `[BE]` API enforces single active brand limit — either rejects or auto-deactivates the previously active brand
- `[DB]` Only 1 `BrandsTable` row with `is_active=true` per user at any time

---

## 5. Segment & Prompt Management

### TS-050 — Free trial user can add only 1 segment per brand

**Preconditions:** Free trial user creating or editing a brand.

**Steps:**
1. In the brand setup form, try to add a second segment by clicking "Add Segment"

**Expected:**
- `[FE]` "Add Segment" button is disabled or shows upgrade prompt after 1 segment
- `[BE]` If submitted with 2 segments: API returns 403 quota error

---

### TS-051 — Pro user can add up to 3 segments per brand

**Preconditions:** Pro user creating a brand.

**Steps:**
1. Add 3 segments with distinct names and prompts
2. Try to add a 4th segment

**Expected:**
- `[FE]` Segments 1-3 added successfully
- `[FE]` 4th segment add button is disabled (max 3 reached)
- `[BE]` `POST /api/v1/brands/setup` with 3 segments returns 201 with 3 prompt records

---

### TS-052 — Each segment has exactly 1 prompt (per current quota)

**Preconditions:** User in brand setup form.

**Steps:**
1. For a segment, enter a prompt
2. Try to add a second prompt to the same segment

**Expected:**
- `[FE]` UI allows only 1 prompt per segment (no "add prompt" button after first)
- `[DB]` Only 1 `BrandPromptTable` row per segment per brand

---

### TS-053 — Prompt text is required and cannot be empty

**Preconditions:** User in brand setup form.

**Steps:**
1. Add a segment with an empty prompt field
2. Try to submit

**Expected:**
- `[FE]` Validation error shown: "Prompt is required"
- `[FE]` Form does not submit

---

### TS-054 — Segment name is required

**Preconditions:** User in brand setup form with 1 segment.

**Steps:**
1. Leave segment name blank
2. Submit

**Expected:**
- `[FE]` Validation error shown on segment name field

---

### TS-055 — Brand full update (PUT) replaces all prompts

**Preconditions:** Brand has 2 segments/prompts. User is owner.

**Steps:**
1. Edit brand, remove segment 1, update segment 2 prompt
2. Save

**Expected:**
- `[BE]` `PUT /api/v1/brands/{brand_id}` replaces the prompt set
- `[DB]` Old prompt records for removed segment are deleted/deactivated
- `[DB]` Updated prompt record reflects new text

---

## 6. Dashboard — Brand Impression

### TS-060 — Brand Impression page shows summary metrics with data

**Preconditions:** User has 1 active brand with data from at least 1 pipeline run.

**Steps:**
1. Navigate to `/app/dashboard/brand-impression`
2. Select the brand from the brand selector
3. Select the segment from the segment selector
4. Select time range "1 Month"

**Expected:**
- `[FE]` Four metric cards render: Share of Visibility, Average Rank, Sentiment Score, Consistency Index
- `[BE]` `GET /api/v1/dashboard/brand-impression-summary` returns non-empty data
- `[FE]` Metric cards show numeric values (not loading skeletons or "—")
- `[FE]` Trend arrows indicate direction (up/down) vs previous period

---

### TS-061 — Brand Impression page shows "no data" state before first pipeline run

**Preconditions:** Brand was just created — no pipeline has run yet.

**Steps:**
1. Navigate to `/app/dashboard/brand-impression`
2. Select the newly created brand

**Expected:**
- `[FE]` Charts and metric cards show empty/zero state with a helpful message (e.g., "Data will appear after the first daily scan")
- `[FE]` No JavaScript errors or blank white areas

---

### TS-062 — Historical trend chart renders correct date range for "1 Quarter"

**Preconditions:** Brand has ~90 days of pipeline data.

**Steps:**
1. Navigate to Brand Impression
2. Change time range picker to "1 Quarter"

**Expected:**
- `[BE]` `GET /api/v1/dashboard/brand-impression-trend?time_range=1q` returns data spanning ~90 days
- `[FE]` Line chart X-axis spans approximately 3 months
- `[FE]` Chart re-renders without page reload

---

### TS-063 — Custom date range picker filters data correctly

**Preconditions:** Brand has data spanning multiple months.

**Steps:**
1. Select "Custom" in the time range picker
2. Set start date = 2025-01-01, end date = 2025-01-31
3. Apply

**Expected:**
- `[BE]` API called with correct start/end params
- `[FE]` Charts only show data within Jan 2025
- `[FE]` Metric cards reflect the custom range totals

---

### TS-064 — Switching between segments updates all dashboard data

**Preconditions:** Brand has 2 segments with different data.

**Steps:**
1. Select segment "Running Shoes" — note the metric values
2. Switch segment selector to "Sneakers"

**Expected:**
- `[FE]` All metric cards, charts, and tables reload with segment-specific data
- `[BE]` All API calls include the new `segment` parameter
- `[FE]` Values differ between the two segments (confirming data is segment-specific)

---

### TS-065 — AI Reference Sources table shows correct sources

**Preconditions:** Pipeline has run and populated reference sources.

**Steps:**
1. Scroll to the AI Reference Sources table on Brand Impression

**Expected:**
- `[FE]` Table shows URL, weight, and count for each source
- `[BE]` `GET /api/v1/dashboard/reference-sources` returns source list
- `[FE]` Sources are sorted by weight descending

---

### TS-066 — Customer Review table shows sentiment breakdown

**Preconditions:** Pipeline has run and reviews exist.

**Steps:**
1. Scroll to the Customer Reviews table

**Expected:**
- `[FE]` Table shows review text and sentiment badge (positive/neutral/negative)
- `[FE]` Sentiment filter chips filter the table by sentiment type
- `[BE]` `GET /api/v1/dashboard/customer-reviews` returns paginated review data

---

### TS-067 — Switching brands updates all dashboard sections

**Preconditions:** User has 2 brands (e.g., Nike and Adidas — as monitor member).

**Steps:**
1. Select "Nike" in brand selector — note values
2. Switch to "Adidas"

**Expected:**
- `[FE]` All sections reload with Adidas-specific data
- `[FE]` Segment selector resets to first available segment for Adidas
- `[BE]` All API calls include `brand_id` of Adidas

---

### TS-068 — Awareness score is normalized to 0-10 for display

**Preconditions:** Pipeline has run. `BrandAwarenessDailyPerformanceTable` has scores stored 0-100.

**Steps:**
1. Navigate to Brand Impression and read the Awareness Score gauge

**Expected:**
- `[FE]` Gauge displays a value between 0.0 and 10.0
- `[BE]` API returns score in the 0-100 range; frontend divides by 10 for display

---

## 7. Dashboard — Competitive Analysis

### TS-070 — Free trial user sees only "Visibility Gap" metric, rest is gated

**Preconditions:** User tier = `free_trial`.

**Steps:**
1. Navigate to `/app/dashboard/competitors`

**Expected:**
- `[FE]` "Competitive Current Status" card shows only the "Visibility Gap" metric (SOV gap)
- `[FE]` The rest of the Competitive Analysis content is blurred with a lock overlay
- `[FE]` Lock overlay shows "Upgrade to Pro" CTA button
- `[FE]` Clicking "Upgrade to Pro" navigates to `/app/settings` (pricing page)

---

### TS-071 — Pro user sees full Competitive Analysis with all charts

**Preconditions:** User tier = `pro`.

**Steps:**
1. Navigate to `/app/dashboard/competitors`

**Expected:**
- `[FE]` No lock overlay or blur visible
- `[FE]` Competitor Gap Summary card shows SOV gap, rank gap, sentiment gap vs top competitor
- `[FE]` Competitor Gap Trend chart renders area/line chart over time
- `[FE]` Competitor Ranking Detail chart shows per-competitor rank comparison
- `[FE]` Reference Source Comparison table shows brand vs competitor sources side-by-side
- `[FE]` Sentiment Comparison table shows sentiment breakdown for brand and competitor
- `[BE]` All competitor API endpoints return data (not 403)

---

### TS-072 — Competitor data reflects correct competitor from Gemini results

**Preconditions:** Brand = Nike, Gemini returns Adidas as top competitor in results.

**Steps:**
1. Navigate to Competitive Analysis for Nike

**Expected:**
- `[FE]` "Top Competitor" shown as Adidas (derived from `BrandCompetitorsTable`)
- `[BE]` `GET /api/v1/dashboard/competitor-gap-summary?brand_id=Nike` returns Adidas as the comparison target

---

### TS-073 — Competitive gap trend shows correct direction (positive = brand gaining)

**Preconditions:** Brand SOV increased from 30% to 40% over last month while competitor dropped from 35% to 30%.

**Steps:**
1. View Competitive Gap Trend chart over "1 Month"

**Expected:**
- `[FE]` Gap trend line moves upward (brand SOV gap widening in brand's favor)
- `[FE]` Chart tooltip shows exact gap value for each date point

---

### TS-074 — Sentiment comparison table shows all three sentiment categories

**Preconditions:** Pipeline data has positive, neutral, and negative reviews for both brand and competitor.

**Steps:**
1. Navigate to Competitive Analysis → Sentiment Comparison

**Expected:**
- `[FE]` Table shows separate rows for Positive, Neutral, Negative counts
- `[FE]` Brand column and Competitor column have distinct values
- `[FE]` Totals add up correctly

---

## 8. Insight — Market Dynamic

### TS-080 — Free trial user cannot access Market Dynamic page

**Preconditions:** User tier = `free_trial`.

**Steps:**
1. Inspect the sidebar — "Market Dynamic" nav item
2. Try to navigate to `/app/insight/market-dynamic`

**Expected:**
- `[FE]` Market Dynamic nav item is grayed out / disabled (requires `insightAll` feature)
- `[FE]` If URL is typed directly: page shows `FeatureGate` blocking overlay with upgrade prompt

---

### TS-081 — Pro user sees Market Dynamic with multi-brand SOV data

**Preconditions:** User tier = `pro`. Pipeline has run with multiple brands appearing in Gemini results.

**Steps:**
1. Navigate to `/app/insight/market-dynamic`

**Expected:**
- `[FE]` Area chart renders SOV over time, one area per brand
- `[FE]` Bar chart shows SOV by segment
- `[FE]` Scatter/bubble chart shows brand position vs SOV
- `[FE]` Momentum trend line chart renders
- `[BE]` `GET /api/v1/dashboard/market-dynamic` returns multi-brand data
- `[FE]` Brand legend in charts is clickable to show/hide individual brands

---

### TS-082 — Market Dynamic time range selector works

**Preconditions:** Pro user on Market Dynamic page.

**Steps:**
1. Change time range to "YTD"

**Expected:**
- `[FE]` All charts reload with data from January 1 of current year to today
- `[BE]` API called with correct `time_range` parameter

---

## 9. Insight — Risk Intelligence

### TS-090 — Risk Intelligence is not visible in the sidebar navigation

**Preconditions:** Any authenticated user.

**Steps:**
1. Inspect the sidebar navigation

**Expected:**
- `[FE]` "Risk Intelligence" nav item is **not present** (commented out of nav — pre-MVP)

---

### TS-091 — Risk Intelligence page loads directly via URL for Pro user

**Preconditions:** User tier = `pro`. Navigate directly to `/app/insight/risk-intelligence`.

**Steps:**
1. Navigate to `/app/insight/risk-intelligence`

**Expected:**
- `[FE]` Page loads (route exists even if nav is hidden)
- `[FE]` Three tabs render: "Competitive Risk", "Growth Risk", "Ranking Risk"
- `[FE]` Each tab shows relevant signal cards

---

### TS-092 — Risk signals show correct severity badges

**Preconditions:** Pipeline has populated `BrandPerformanceInsightTable` with signal data.

**Steps:**
1. Navigate to Risk Intelligence → "Competitive Risk" tab

**Expected:**
- `[FE]` Competitive Dominance, Competitive Erosion, and Competitor Breakthrough signals each show a severity badge: low/medium/high/critical
- `[FE]` Severity badge color matches severity level (green/yellow/orange/red)
- `[FE]` Historical trend chart shows signal score over time for each signal

---

### TS-093 — Risk Intelligence page shows empty state before pipeline data exists

**Preconditions:** Brand just created, no pipeline run yet.

**Steps:**
1. Navigate to `/app/insight/risk-intelligence`

**Expected:**
- `[FE]` Empty state message shown (no crashes, no blank panels)

---

## 10. Pricing & Subscription

### TS-100 — Free trial user sees days remaining on trial

**Preconditions:** User tier = `free_trial`, status = `active`, `trial_expires_at` = now + 14 days.

**Steps:**
1. Navigate to `/app/settings`

**Expected:**
- `[FE]` Current plan shown as "Free Trial"
- `[FE]` Trial expiry countdown shown (e.g., "14 days remaining")
- `[FE]` "Upgrade to Pro" button is visible and active

---

### TS-101 — Free trial user upgrades to Pro via Stripe Checkout

**Preconditions:** User tier = `free_trial`. Stripe test mode configured.

**Steps:**
1. Navigate to `/app/settings`
2. Click "Upgrade to Pro"
3. `POST /api/v1/billing/create-checkout-session` is called
4. User is redirected to Stripe Checkout
5. Enter test card `4242 4242 4242 4242` (Stripe test success card)
6. Complete checkout
7. Stripe redirects back with `?status=success`

**Expected:**
- `[BE]` `POST /api/v1/billing/create-checkout-session` returns a valid Stripe Checkout URL
- `[BE]` Stripe webhook `checkout.session.completed` fires → backend upgrades subscription
- `[DB]` `UserSubscriptionTable.tier = pro`, `status = active`, `stripe_customer_id` saved
- `[FE]` App polls `GET /api/v1/profile/me` up to 10 times (1-second interval) until tier changes
- `[FE]` Settings page updates to show "Pro" tier without page reload
- `[FE]` Gated features (Competitive Analysis, Market Dynamic) unlock immediately

---

### TS-102 — Pro user can cancel subscription

**Preconditions:** User tier = `pro`, `status = active`.

**Steps:**
1. Navigate to `/app/settings`
2. Click "Cancel Subscription"
3. Confirm in dialog

**Expected:**
- `[BE]` `POST /api/v1/billing/cancel` triggers Stripe `cancel_at_period_end=true`
- `[DB]` `UserSubscriptionTable.status = cancelled` (or remains `active` with `cancel_at_period_end` flag until period end)
- `[FE]` Settings page shows "Cancellation pending — active until {period_end_date}"
- `[FE]` "Reactivate" button appears

---

### TS-103 — Cancelled user can reactivate subscription

**Preconditions:** User tier = `pro`, status = `cancelled`, still within paid period.

**Steps:**
1. Navigate to `/app/settings`
2. Click "Reactivate"

**Expected:**
- `[BE]` `POST /api/v1/billing/reactivate` calls Stripe to remove `cancel_at_period_end`
- `[DB]` Subscription status reverted to `active`
- `[FE]` Settings page shows "Pro" plan as active, cancel button returns

---

### TS-104 — Expired user sees Expiry Modal on first app load

**Preconditions:** User tier = `free_trial`, status = `expired`.

**Steps:**
1. Sign in as the expired user
2. Navigate to `/app/brands`

**Expected:**
- `[FE]` Expiry Modal appears over the page on first load of the session
- `[FE]` Modal prompts user to upgrade and shows "Upgrade to Pro" button
- `[FE]` Modal can be dismissed; it does not appear again in the same browser session (stored in `sessionStorage`)

---

### TS-105 — Expiry Modal does not appear on subsequent navigations in same session

**Preconditions:** User has seen and dismissed the expiry modal.

**Steps:**
1. Navigate to `/app/dashboard/brand-impression`
2. Navigate back to `/app/brands`

**Expected:**
- `[FE]` Expiry Modal does NOT appear on subsequent navigations
- `[FE]` `sessionStorage` flag is set after first show

---

### TS-106 — Payment failure sets subscription to past_due

**Preconditions:** Stripe sends `invoice.payment_failed` webhook.

**Steps:**
1. Simulate Stripe `invoice.payment_failed` event via Stripe CLI: `stripe trigger invoice.payment_failed`

**Expected:**
- `[DB]` `UserSubscriptionTable.status = past_due`
- `[FE]` Next sign-in: user sees warning banner or modal about payment failure

---

### TS-107 — Stripe webhook signature is validated (reject invalid requests)

**Preconditions:** Backend Stripe webhook endpoint at `POST /api/v1/webhooks/stripe`.

**Steps:**
1. POST to `/api/v1/webhooks/stripe` with a made-up JSON payload and no `Stripe-Signature` header

**Expected:**
- `[BE]` Returns 400 or 403 — signature validation fails, event is rejected

---

## 11. Billing & Stripe Portal

### TS-110 — Pro user opens Stripe Customer Portal

**Preconditions:** User tier = `pro`, status = `active`.

**Steps:**
1. Navigate to `/app/billing`
2. Click "Manage Subscription"

**Expected:**
- `[BE]` `POST /api/v1/billing/create-portal-session` returns a Stripe portal URL
- `[FE]` Portal opens in a new browser tab
- `[FE]` Stripe portal shows current plan, payment method, invoice history

---

### TS-111 — Billing page reflects correct subscription state

**Preconditions:** Pro user.

**Steps:**
1. Navigate to `/app/billing`

**Expected:**
- `[FE]` Shows plan name "Pro", status "Active"
- `[FE]` Shows next billing date (current_period_end from Stripe)
- `[FE]` Shows "Manage Subscription" button

---

### TS-112 — Billing page polls for subscription changes when returning from portal

**Preconditions:** Pro user has Stripe portal open in another tab.

**Steps:**
1. Make a change in Stripe portal (e.g., update payment method)
2. Close the portal tab
3. Return focus to the Kila billing tab

**Expected:**
- `[FE]` On `visibilitychange` event (tab gains focus), app polls `GET /api/v1/profile/me`
- `[FE]` If subscription changed, billing page updates to reflect new state

---

## 12. Subscription Expiry & Enforcement

### TS-120 — Daily subscription eligibility job expires free trial accounts after 28 days

**Preconditions:** `UserSubscriptionTable` has `tier=free_trial`, `status=active`, `trial_expires_at = yesterday`.

**Steps:**
1. Run `subscription_eligibility_job` (Stage 0 of daily pipeline)

**Expected:**
- `[DB]` `UserSubscriptionTable.status = expired`
- `[DB]` All `BrandPromptTable.is_active = false` for this user's brands
- `[DB]` All `BrandsTable.is_active = false` for this user's brands
- `[JOB]` Job logs: "Expired free trial for user X"

---

### TS-121 — Lazy subscription check on GET /profile/me expires trial user in real-time

**Preconditions:** User's trial expired but `subscription_eligibility_job` hasn't run yet.

**Steps:**
1. Expired user signs in and app calls `GET /api/v1/profile/me`

**Expected:**
- `[BE]` Endpoint detects `trial_expires_at < now()` and sets `status=expired` before returning
- `[BE]` Response shows `status=expired`
- `[FE]` Expiry modal is shown

---

### TS-122 — Cancelled subscription via Stripe webhook deactivates all brands and prompts

**Preconditions:** Pro user, Stripe webhook `customer.subscription.deleted` fired.

**Steps:**
1. Simulate `stripe trigger customer.subscription.deleted`

**Expected:**
- `[DB]` `UserSubscriptionTable.status = cancelled`
- `[DB]` `BrandsTable.is_active = false` for all brands
- `[DB]` `BrandPromptTable.is_active = false` for all prompts
- `[JOB]` Subscription eligibility job on next run: no active brands to deactivate (already done)

---

### TS-123 — Expired user cannot create a new brand (API-level enforcement)

**Preconditions:** User status = `expired`.

**Steps:**
1. POST to `/api/v1/brands/setup` with valid brand data

**Expected:**
- `[BE]` Returns 403 — "Subscription expired, cannot create new brands"

---

### TS-124 — Super user is exempt from brand quota limits

**Preconditions:** `UserSubscriptionTable.is_super_user = true`.

**Steps:**
1. Try to create a second brand

**Expected:**
- `[BE]` `POST /api/v1/brands/setup` succeeds (200/201)
- `[DB]` Second brand created as active

---

## 13. Settings & Profile Management

### TS-130 — User can update their profile name and phone

**Preconditions:** User has completed profile setup.

**Steps:**
1. Navigate to user profile settings (if accessible via UI)
2. Update phone number
3. Save

**Expected:**
- `[BE]` Profile update API returns 200
- `[DB]` `UsersProfileTable` updated

---

### TS-131 — User can change their password

**Preconditions:** User signed up via legacy email/password (not Clerk-only).

**Steps:**
1. Open "Change Password" dialog
2. Enter current password, new password, confirm new password
3. Submit

**Expected:**
- `[BE]` Returns 200 on success
- `[DB]` `UsersTable.password_hash` updated with bcrypt hash of new password
- `[FE]` Success toast message shown

---

### TS-132 — Change password with wrong current password returns error

**Preconditions:** User is authenticated.

**Steps:**
1. Open "Change Password" dialog
2. Enter incorrect current password
3. Submit

**Expected:**
- `[BE]` Returns 400/401 with error
- `[FE]` Error message shown in dialog

---

### TS-133 — Settings page shows current subscription tier and upgrade/cancel controls

**Preconditions:** Any authenticated user.

**Steps:**
1. Navigate to `/app/settings`

**Expected:**
- `[FE]` Pricing cards rendered with current tier highlighted
- `[FE]` Free trial user: "Upgrade to Pro" button active, days remaining shown
- `[FE]` Pro user: "Cancel Subscription" button visible, billing date shown

---

## 14. Quota & Entitlement Gates

### TS-140 — FeatureGate hides gated content for free trial users

**Preconditions:** User tier = `free_trial`.

**Steps:**
1. Navigate to Competitive Analysis

**Expected:**
- `[FE]` Gated content sections render but are blurred and have a `FeatureGate` overlay
- `[FE]` Lock icon and "View plans" link visible
- `[FE]` No gated API data is fetched (no unnecessary API calls for locked content)

---

### TS-141 — QuotaGate disables "Add Brand" after limit reached

**Preconditions:** Free trial user with 1 brand (quota = 1).

**Steps:**
1. Navigate to `/app/brands`

**Expected:**
- `[FE]` "Add Brand" button is disabled or shows a tooltip "Upgrade to add more brands"

---

### TS-142 — QuotaGate disables "Add Segment" after limit reached for free trial

**Preconditions:** Free trial user editing a brand with 1 segment.

**Steps:**
1. Open brand edit form

**Expected:**
- `[FE]` "Add Segment" button is disabled after 1 segment added

---

### TS-143 — Pro user "Add Segment" is enabled up to 3 segments

**Preconditions:** Pro user with a brand having 2 segments.

**Steps:**
1. Edit brand
2. Verify "Add Segment" is still enabled

**Expected:**
- `[FE]` "Add Segment" button is enabled (2 < 3 limit)
- After adding 3rd segment: button becomes disabled (3 = limit)

---

### TS-144 — Entitlement context is loaded once on app shell and propagated to all components

**Preconditions:** User signs in.

**Steps:**
1. Sign in and observe network calls

**Expected:**
- `[BE]` `GET /api/v1/profile/me` called once by the app shell (`app.tsx`)
- `[FE]` Subscription context propagates tier and feature flags to all child components
- `[FE]` No child component independently re-fetches subscription data

---

## 15. Offline Pipeline — Stage 0: Subscription Eligibility Job

### TS-150 — Job expires free trial users past their trial_expires_at

**Preconditions:**
```sql
UserSubscriptionTable: tier='free_trial', status='active', trial_expires_at='2026-01-01'
BrandsTable: is_active=true
BrandPromptTable: is_active=true
```

**Steps:**
1. Run: `ENVIRONMENT=production python -m app.jobs.subscription_eligibility_job`

**Expected:**
- `[DB]` `UserSubscriptionTable.status = 'expired'`
- `[DB]` All associated `BrandsTable.is_active = false`
- `[DB]` All associated `BrandPromptTable.is_active = false`
- `[JOB]` Exit code = 0

---

### TS-151 — Job does not affect active, non-expired subscriptions

**Preconditions:** Pro user with `status='active'`, `trial_expires_at=null`.

**Steps:**
1. Run subscription eligibility job

**Expected:**
- `[DB]` Pro user's subscription unchanged
- `[DB]` Pro user's brands remain active

---

### TS-152 — Job is idempotent — running twice produces same result

**Preconditions:** Expired user.

**Steps:**
1. Run subscription eligibility job twice in sequence

**Expected:**
- `[DB]` State identical after both runs (no duplicate deactivations or errors)
- `[JOB]` Both runs exit 0

---

### TS-153 — Job handles empty DB gracefully (no active subscriptions to process)

**Preconditions:** No users in DB.

**Steps:**
1. Run subscription eligibility job

**Expected:**
- `[JOB]` Job logs "0 users processed" (or similar)
- `[JOB]` Exit code = 0

---

## 16. Offline Pipeline — Stage 1: Brand Search Response Job

### TS-160 — Job queries Gemini for each active prompt and saves raw + parsed results

**Preconditions:**
- `BrandPromptTable` has 2 active prompts for Brand A
- Gemini API is reachable
- `MODEL_WEIGHTS: gemini=1.0` (only active model)

**Steps:**
1. Run: `ENVIRONMENT=production python -m app.jobs.brand_search_jobs.brand_search_response_job --mode daily --full-run`

**Expected:**
- `[DB]` `BrandSearchRawResponseTable`: 2 new rows (one per prompt)
- `[DB]` `BrandSearchResultTable`: N rows per prompt (top brands returned by Gemini, up to 10 each)
- `[DB]` `BrandPromptRunningTable`: empty after successful run (all prompts removed on success)
- `[JOB]` Log shows: "Job validation passed. Raw responses written: 2/2. BrandPromptRunningTable is empty."
- `[JOB]` Exit code = 0

---

### TS-161 — Job resumes from BrandPromptRunningTable after partial failure

**Preconditions:** Previous run completed 1 of 2 prompts. `BrandPromptRunningTable` still has 1 prompt.

**Steps:**
1. Run job WITHOUT `--full-run` (resume mode)

**Expected:**
- `[DB]` Only the remaining prompt is processed
- `[DB]` `BrandPromptRunningTable` is empty after run
- `[JOB]` Log shows: "Resume run: reading remaining records from BrandPromptRunningTable"

---

### TS-162 — Full-run clears BrandPromptRunningTable before starting

**Preconditions:** `BrandPromptRunningTable` has stale data from a previous aborted run.

**Steps:**
1. Run job with `--full-run`

**Expected:**
- `[DB]` `BrandPromptRunningTable` is cleared and repopulated from `BrandPromptTable` at run start
- `[JOB]` Log shows: "Cleared BrandPromptRunningTable"

---

### TS-163 — Dry run shows prompts without making Gemini API calls

**Preconditions:** 3 active prompts in `BrandPromptTable`.

**Steps:**
1. Run: `python -m app.jobs.brand_search_jobs.brand_search_response_job --mode daily --full-run --dry-run`

**Expected:**
- `[JOB]` Log lists each prompt_id and brand_name that would be processed
- `[JOB]` No Gemini API calls made
- `[DB]` No new rows in `BrandSearchResultTable` or `BrandSearchRawResponseTable`
- `[JOB]` Stats show `job_status = 'dry_run'`, exit code = 0

---

### TS-164 — Job exits with code 1 on failure (for Ofelia alerting)

**Preconditions:** Gemini API key is invalid (or revoked).

**Steps:**
1. Set `GEMINI_API_KEY=invalid` in environment
2. Run job with `--full-run`

**Expected:**
- `[JOB]` Log shows authentication/API error for each prompt
- `[JOB]` `job_status = 'failed'`
- `[JOB]` Exit code = **1** (so Ofelia marks the job as failed)

---

### TS-165 — Healthchecks.io ping sent on successful job completion

**Preconditions:** `HEALTHCHECKS_PING_URL` is configured in `.env.prod`.

**Steps:**
1. Run job with `--full-run` and all prompts succeed

**Expected:**
- `[JOB]` Log shows: "Healthchecks.io ping sent: {url}"
- `[EXT]` Healthchecks.io dashboard shows the check as "healthy"

---

### TS-166 — Job processes daily prompts only (trailing window filter)

**Preconditions:**
- Prompt A: `created_datetime` = 2 months ago (within 3-month window)
- Prompt B: `created_datetime` = 5 months ago (outside 3-month window)

**Steps:**
1. Run job with `--mode daily --trailing-window 3 --full-run`

**Expected:**
- `[DB]` Only Prompt A is processed
- `[DB]` Prompt B is not in `BrandPromptRunningTable`

---

### TS-167 — Job skips inactive prompts

**Preconditions:** `BrandPromptTable` has 1 active + 1 inactive prompt for the same brand.

**Steps:**
1. Run job with `--full-run`

**Expected:**
- `[DB]` Only the active prompt's results are saved
- `[DB]` Inactive prompt generates no new rows in result tables

---

### TS-168 — Invalid Gemini JSON response is logged and prompt stays in running table

**Preconditions:** Gemini returns malformed/non-JSON response for one prompt.

**Steps:**
1. Mock Gemini to return "I cannot answer this query" (non-JSON) for prompt X

**Expected:**
- `[JOB]` Log shows: "Failed to parse gemini response for prompt X: JSONDecodeError"
- `[DB]` Prompt X remains in `BrandPromptRunningTable` (not removed)
- `[DB]` No result rows saved for prompt X
- `[JOB]` Overall `job_status = 'failed'` (prompt X not processed)

---

## 17. Offline Pipeline — Stage 2: Basic Metrics Jobs

### TS-170 — brand_search_basic_metrics_job computes 7-day trailing visibility metrics

**Preconditions:** 7 days of `BrandSearchResultTable` data for Brand A / Segment S.

**Steps:**
1. Run: `ENVIRONMENT=production python -m app.jobs.brand_analysis_jobs.brand_search_basic_metrics_job`

**Expected:**
- `[DB]` `BrandSearchDailyBasicMetricsTable` row created with:
  - `brand_id = Brand A`, `segment = S`, `date_start = today-6`, `date_end = today`
  - `total_search_count > 0`
  - `search_visibility_count <= total_search_count`
  - `avg_ranking` between 1 and 10
  - `positive_sentiment_score + neutral_sentiment_score + negative_sentiment_score ≈ 1.0` (normalized)
- `[JOB]` Exit code = 0

---

### TS-171 — brand_search_competitors_basic_metrics_job computes competitor metrics

**Preconditions:** Gemini returned "Adidas" as a result for Nike's prompt. `BrandCompetitorsTable` populated.

**Steps:**
1. Run competitors basic metrics job

**Expected:**
- `[DB]` `BrandSearchCompetitorDailyBasicMetricsTable` row created for Adidas
  - `search_target_brand_id = Nike's brand_id`
  - `competitor_brand_name = 'Adidas'`
  - Correct ranking/visibility/sentiment metrics for Adidas

---

### TS-172 — Metrics job is idempotent — upserts do not create duplicates

**Preconditions:** Metrics job ran once today.

**Steps:**
1. Run metrics job a second time on the same day

**Expected:**
- `[DB]` No duplicate rows in `BrandSearchDailyBasicMetricsTable`
- `[DB]` Existing row is updated (upsert on PK: brand_id, segment, date_start, date_end, model)

---

### TS-173 — Metrics job handles brand with no search results today

**Preconditions:** A brand has no `BrandSearchResultTable` rows for today.

**Steps:**
1. Run basic metrics job

**Expected:**
- `[JOB]` Job logs a warning for the brand with no data
- `[JOB]` Job exits 0 (partial data is OK — no crash)
- `[DB]` No metrics row written for that brand

---

## 18. Offline Pipeline — Stage 3: Awareness Performance Jobs

### TS-180 — brand_awareness_performance_job computes BAI components correctly

**Preconditions:** `BrandSearchDailyBasicMetricsTable` has 7 days of data for Brand A / Segment S.

**Steps:**
1. Run: `ENVIRONMENT=production python -m app.jobs.brand_analysis_jobs.brand_awareness_performance_job --type daily --start 2026-03-21 --end 2026-03-21`

**Expected:**
- `[DB]` `BrandAwarenessDailyPerformanceTable` row created with:
  - `brand_id, segment, date, model='gemini'`
  - `share_of_voice` (SOV) between 0 and 1
  - `search_share_index` (SSI) between 0 and 1
  - `position_strength` between 0 and 1
  - `search_momentum` value present (positive = growing, negative = declining)
  - `awareness_score` between 0 and 100 (weighted composite)
  - `consistency_index` between 0 and 1
- `[DB]` Additional row with `model='all'` (aggregate) using normalized weights
- `[JOB]` Exit code = 0

---

### TS-181 — Awareness score formula is correctly weighted

**Preconditions:** Known metric values for a brand:
  - SOV = 0.50, SSI = 0.40, PS = 0.60, SM = 1.10

**Steps:**
1. Run awareness performance job
2. Query `BrandAwarenessDailyPerformanceTable.awareness_score`

**Expected:**
- `[DB]` `awareness_score ≈ (0.50×35 + 0.40×25 + 0.60×20 + 1.10×20) = 17.5+10+12+22 = 61.5` (approximately, pre-scaling)
- Score is stored 0-100

---

### TS-182 — brand_competitors_awareness_performance_job computes competitor BAI

**Preconditions:** `BrandSearchCompetitorDailyBasicMetricsTable` has data for Adidas (as Nike's competitor).

**Steps:**
1. Run competitors awareness performance job

**Expected:**
- `[DB]` `BrandCompetitorsAwarenessDailyPerformanceTable` row created for Adidas
  - `search_target_brand_id = Nike's brand_id`
  - `competitor_brand_name = 'Adidas'`
  - All BAI component fields populated

---

### TS-183 — Performance job handles brand with only 1 day of data (no 28-day window for SM)

**Preconditions:** Brand has only 1 day of `BrandSearchDailyBasicMetricsTable` data.

**Steps:**
1. Run awareness performance job

**Expected:**
- `[DB]` Row is still created (no crash)
- `[DB]` `search_momentum` is null or 0 (insufficient data for long-window ratio)
- `[JOB]` Job logs a warning about insufficient data for momentum calculation

---

## 19. Offline Pipeline — Stage 4: Insight Signal Jobs

### TS-190 — competitive_dominance_signal_job sets score=1.0 when brand SOV >= 60% and gap >= 5%

**Preconditions:**
- Brand SOV = 65%, top competitor SOV = 55% (gap = 10%), position_strength = 70%

**Steps:**
1. Run: `python -m app.jobs.brand_insight_jobs.competitive_dominance_signal_job`

**Expected:**
- `[DB]` `BrandPerformanceInsightTable` row: `signal_type='competitive_dominance'`, `signal_score=1.0`, `severity='low'` (dominant position is a positive)

---

### TS-191 — competitive_dominance_signal_job sets score=0.0 when conditions not met

**Preconditions:** Brand SOV = 40% (below 60% threshold).

**Steps:**
1. Run competitive dominance signal job

**Expected:**
- `[DB]` `signal_score = 0.0`

---

### TS-192 — competitive_erosion_signal_job detects declining SOV trend

**Preconditions:** Brand SOV over 7 days: 50%, 48%, 45%, 42%, 40%, 38%, 35% (consistent decline).

**Steps:**
1. Run competitive erosion signal job

**Expected:**
- `[DB]` `signal_type='competitive_erosion'`, `signal_score > 0.5`, `severity='high'` or `'critical'`

---

### TS-193 — volatility_spike_signal_job detects high ranking standard deviation

**Preconditions:** Brand rankings over 7 days: 1, 8, 2, 9, 1, 7, 3 (high std deviation ~3.5).

**Steps:**
1. Run volatility spike signal job

**Expected:**
- `[DB]` `signal_type='volatility_spike'`, `signal_score > 0.7`, `severity` = `'high'` or `'critical'`

---

### TS-194 — new_entrant_signal_job detects a brand appearing for the first time

**Preconditions:** A new brand "Hoka" appears in Gemini results today but had no presence in the prior 7-day window.

**Steps:**
1. Run new entrant signal job

**Expected:**
- `[DB]` `signal_type='new_entrant'`, `signal_score > 0` for the tracked brand (Nike, whose competitive landscape now includes Hoka)

---

### TS-195 — fragile_leadership_signal_job detects high SOV + high volatility

**Preconditions:** Brand has SOV = 70% but ranking std_dev is very high (volatile top-rank).

**Steps:**
1. Run fragile leadership signal job

**Expected:**
- `[DB]` `signal_type='fragile_leadership'`, `signal_score > 0.5`

---

### TS-196 — All signal jobs run in parallel (Stage 4) and all succeed independently

**Preconditions:** Normal pipeline data available.

**Steps:**
1. Run daily_pipeline.py to Stage 4

**Expected:**
- `[JOB]` All 9 signal jobs are launched concurrently by `asyncio.gather`
- `[JOB]` Log shows Stage 4 start with "(9 job(s))"
- `[JOB]` All 9 exit 0 independently
- `[JOB]` If 1 signal job fails, Stage 4 is marked failed but other 8 still complete

---

### TS-197 — Signal jobs produce one row per brand/segment/date

**Preconditions:** 2 brands, each with 1 segment. All 9 signal jobs run.

**Steps:**
1. Run Stage 4

**Expected:**
- `[DB]` `BrandPerformanceInsightTable` has 2 × 9 = 18 rows for today (1 per brand per signal)
- `[DB]` All rows have `date = today`

---

## 20. Pipeline Orchestrator — daily_pipeline.py

### TS-200 — Full pipeline runs all 5 stages in order and succeeds

**Preconditions:** Normal data available. All jobs configured correctly.

**Steps:**
1. Run: `ENVIRONMENT=production python -m app.jobs.daily_pipeline`

**Expected:**
- `[JOB]` Stage 0 completes first (subscription eligibility)
- `[JOB]` Stage 1 completes next (brand search responses)
- `[JOB]` Stages 2 and 3 each run their jobs in parallel
- `[JOB]` Stage 4 runs all 9 signal jobs in parallel
- `[JOB]` Pipeline logs "Pipeline COMPLETED successfully in Xs"
- `[JOB]` Exit code = 0
- `[DB]` `pipeline_runs` table: run record with `status='completed'`

---

### TS-201 — Pipeline stops at Stage 1 if brand search job fails

**Preconditions:** Gemini API key is invalid.

**Steps:**
1. Set `GEMINI_API_KEY=bad` and run `daily_pipeline.py`

**Expected:**
- `[JOB]` Stage 0 completes successfully
- `[JOB]` Stage 1 fails after 1 retry (max_retries=1)
- `[JOB]` Pipeline logs "Pipeline ABORTED — Stage 1 had failures"
- `[JOB]` Stages 2, 3, 4 do NOT run
- `[JOB]` Exit code = 1
- `[DB]` `pipeline_runs` record: `status='failed'`

---

### TS-202 — Pipeline dry run shows all stages and jobs without executing

**Preconditions:** Any environment.

**Steps:**
1. Run: `python -m app.jobs.daily_pipeline --dry-run`

**Expected:**
- `[JOB]` All 5 stages are logged as "[DRY RUN] would run: ..."
- `[JOB]` No subprocess calls made
- `[JOB]` No DB writes (no pipeline_runs record in dry-run mode)
- `[JOB]` Exit code = 0

---

### TS-203 — Pipeline resume skips already-completed jobs

**Preconditions:** Previous pipeline run completed Stages 0 and 1, then failed at Stage 2.
`pipeline_runs` table shows Stage 0 and 1 jobs as `status='success'`.

**Steps:**
1. Run: `python -m app.jobs.daily_pipeline --resume-run-id {previous_run_id}`

**Expected:**
- `[JOB]` Stage 0 and Stage 1 jobs are logged as "Skipping already-completed"
- `[JOB]` Stage 2 jobs are executed (they failed last time)
- `[JOB]` Resume starts from the first incomplete stage

---

### TS-204 — Stage 2 runs basic metrics jobs in parallel

**Preconditions:** Stage 1 has completed successfully.

**Steps:**
1. Run pipeline to Stage 2 (or run Stage 2 jobs manually)

**Expected:**
- `[JOB]` `brand_search_basic_metrics_job` and `brand_search_competitors_basic_metrics_job` both start simultaneously (asyncio.gather)
- `[JOB]` Both complete independently
- `[JOB]` Stage 2 only marks success when BOTH jobs exit 0

---

### TS-205 — Stage 2 failure prevents Stage 3 from running

**Preconditions:** `brand_search_basic_metrics_job` fails.

**Steps:**
1. Make `brand_search_basic_metrics_job` fail
2. Run pipeline

**Expected:**
- `[JOB]` Stage 2 logged as failed
- `[JOB]` Stage 3 (awareness performance) does NOT run
- `[JOB]` Exit code = 1

---

### TS-206 — Pipeline retry with exponential backoff on job failure

**Preconditions:** A Stage 2 job fails on the first attempt but succeeds on the second.

**Steps:**
1. Run pipeline with a job configured `max_retries=2, retry_delay_seconds=60`
2. Mock first attempt to fail, second to succeed

**Expected:**
- `[JOB]` Log shows "Retrying {job} in 60s..." after first failure
- `[JOB]` Second attempt succeeds
- `[JOB]` Stage 2 overall = success

---

### TS-207 — Ofelia triggers daily_pipeline at 02:00 UTC

**Preconditions:** Production server. Ofelia running with label `schedule: "0 0 2 * * *"`.

**Steps:**
1. Wait until 02:00 UTC (or mock system clock)

**Expected:**
- `[JOB]` `docker logs kila-ofelia-1` shows "[Job "brand-search-daily"] Started - python -m app.jobs.daily_pipeline"
- `[JOB]` After completion: "[Job "brand-search-daily"] Finished in Xs"

---

### TS-208 — Ofelia picks up new job label after scraper container redeploy

**Preconditions:** kila-scraper redeployed with updated Ofelia label command.

**Steps:**
1. Push code change to GitHub → CI deploys new scraper image and restarts Ofelia
2. Check Ofelia logs

**Expected:**
- `[JOB]` `docker logs kila-ofelia-1` shows: `New job registered "brand-search-daily" - "python -m app.jobs.daily_pipeline"`
- `[JOB]` Old command is no longer registered

---

## 21. Data Integrity & Edge Cases

### TS-210 — Brand with no segments cannot be saved

**Preconditions:** Brand setup form.

**Steps:**
1. Enter only a brand name, no segments
2. Submit

**Expected:**
- `[FE]` Validation error: "At least one segment is required"
- `[BE]` `POST /api/v1/brands/setup` with empty segments returns 422

---

### TS-211 — Duplicate brand name for the same user is handled gracefully

**Preconditions:** User has brand "Nike".

**Steps:**
1. Try to create another brand with name "Nike"

**Expected:**
- `[BE]` Returns 409 Conflict or 422 with a clear error message
- `[FE]` Error toast shown

---

### TS-212 — Pipeline produces aggregate model='all' row when multiple models active

**Preconditions:** `MODEL_WEIGHTS: gemini=0.6, chatgpt=0.4` (both active).

**Steps:**
1. Run brand awareness performance job

**Expected:**
- `[DB]` Three rows in `BrandAwarenessDailyPerformanceTable`: `model='gemini'`, `model='chatgpt'`, `model='all'`
- `[DB]` `model='all'` awareness_score = weighted combination using normalized weights

---

### TS-213 — Pipeline skips brand if no search results exist today

**Preconditions:** Brand B has no `BrandSearchResultTable` rows for today.

**Steps:**
1. Run basic metrics job

**Expected:**
- `[JOB]` Job logs "No data for brand B on date X — skipping"
- `[JOB]` Job exits 0 (partial data is acceptable)
- `[DB]` No metrics or performance rows written for brand B today

---

### TS-214 — Dashboard returns empty data (not 500) for a brand with no pipeline data

**Preconditions:** Brand created but pipeline has never run.

**Steps:**
1. Call `GET /api/v1/dashboard/brand-impression-summary?brand_id=X`

**Expected:**
- `[BE]` Returns 200 with empty arrays / zero values (not 500)
- `[FE]` Dashboard renders empty state

---

### TS-215 — Concurrent pipeline runs are prevented

**Preconditions:** Daily pipeline is already running.

**Steps:**
1. Try to start a second instance of `daily_pipeline.py` simultaneously

**Expected:**
- `[JOB]` Second instance detects ongoing run (via pipeline_runs table) and either aborts gracefully or Ofelia only triggers one instance at a time (cron doesn't allow overlap)

---

### TS-216 — BrandSearchRawResponseTable stores actual Gemini response JSON

**Preconditions:** Pipeline Stage 1 ran successfully.

**Steps:**
1. Query `BrandSearchRawResponseTable` for today's results

**Expected:**
- `[DB]` `search_raw_response` column contains valid JSON string
- `[DB]` `model` column matches the model that generated the response (e.g., "gemini-2.5-flash")
- `[DB]` `search_date` = today's date

---

## 22. Security

### TS-220 — Unauthenticated API request returns 401

**Preconditions:** No auth token provided.

**Steps:**
1. GET `/api/v1/dashboard/user-brands` with no `Authorization` header

**Expected:**
- `[BE]` Returns 401 Unauthorized

---

### TS-221 — User A cannot access User B's brand data

**Preconditions:** User A and User B each have brands.

**Steps:**
1. Authenticated as User A
2. Call `GET /api/v1/brands/{brand_id_of_user_B}`

**Expected:**
- `[BE]` Returns 403 or 404 — User A has no membership in User B's brand

---

### TS-222 — User A cannot delete User B's brand via API

**Preconditions:** User A knows User B's brand_id.

**Steps:**
1. `DELETE /api/v1/brands/{brand_id_of_user_B}` with User A's token

**Expected:**
- `[BE]` Returns 403 — only owners can delete brands

---

### TS-223 — User A cannot view User B's dashboard data

**Preconditions:** User A is not a member of any brand owned by User B.

**Steps:**
1. GET `/api/v1/dashboard/brand-impression-summary?brand_id={brand_id_of_user_B}` with User A's token

**Expected:**
- `[BE]` Returns 403 or 404

---

### TS-224 — Stripe webhook endpoint rejects requests without valid signature

**Preconditions:** Stripe signing secret is configured.

**Steps:**
1. POST to `/api/v1/webhooks/stripe` with arbitrary JSON, no `Stripe-Signature` header

**Expected:**
- `[BE]` Returns 400 — signature validation fails

---

### TS-225 — Expired JWT token is rejected

**Preconditions:** Generate a Clerk JWT and wait for it to expire (or backdate the expiry).

**Steps:**
1. POST to `/api/v1/auth/clerk-sync` with an expired JWT

**Expected:**
- `[BE]` Returns 401 — token expired

---

### TS-226 — SQL injection attempt in search/filter params is handled safely

**Preconditions:** Any authenticated user.

**Steps:**
1. GET `/api/v1/profile/companies/search?q=' OR 1=1 --`

**Expected:**
- `[BE]` Returns 200 with an empty result set (no companies match the literal string)
- `[BE]` No SQL error — SQLAlchemy parameterized queries prevent injection

---

### TS-227 — XSS — brand name containing script tags is stored and displayed safely

**Preconditions:** User creates a brand.

**Steps:**
1. Set brand name to `<script>alert('xss')</script>`
2. Save brand
3. View brand list

**Expected:**
- `[DB]` Brand name stored as-is (raw string)
- `[FE]` Brand name displayed as escaped text — no alert fires
- `[FE]` React's JSX auto-escaping prevents XSS

---

### TS-228 — Rate limiting on auth endpoints prevents brute force

**Preconditions:** Login endpoint.

**Steps:**
1. Send 20+ rapid requests to `POST /api/v1/auth/login` with wrong password

**Expected:**
- `[BE]` After threshold, returns 429 Too Many Requests
- `[BE]` Correct password attempts are also blocked temporarily

---

---

## Appendix — Test Coverage Matrix

| Area | Unit | Integration | E2E |
|---|---|---|---|
| Landing page | — | — | TS-001 to TS-005 |
| Auth (Clerk) | TS-016 | TS-010 to TS-013 | TS-011 |
| Auth (legacy JWT) | — | TS-014, TS-015 | — |
| Profile setup | — | TS-021 to TS-024 | TS-020 to TS-024 |
| Brand CRUD | — | TS-030 to TS-038 | TS-030 to TS-036 |
| Segments & prompts | — | TS-050 to TS-055 | TS-050 to TS-054 |
| Brand Impression | — | TS-060 to TS-068 | TS-060 to TS-067 |
| Competitive Analysis | — | TS-070 to TS-074 | TS-070 to TS-072 |
| Market Dynamic | — | TS-080 to TS-082 | TS-080, TS-081 |
| Risk Intelligence | — | TS-091 to TS-093 | TS-090, TS-091 |
| Pricing & subscription | — | TS-100 to TS-107 | TS-100, TS-101 |
| Billing & Stripe | — | TS-110 to TS-112 | TS-110 |
| Subscription expiry | TS-152 | TS-120 to TS-124 | — |
| Quota gates | — | TS-140 to TS-144 | TS-140 to TS-143 |
| Job: eligibility | TS-152, TS-153 | TS-150 to TS-153 | — |
| Job: search response | TS-163, TS-164 | TS-160 to TS-168 | — |
| Job: basic metrics | TS-172 | TS-170 to TS-173 | — |
| Job: awareness | TS-181 | TS-180 to TS-183 | — |
| Job: signals | TS-191 | TS-190 to TS-197 | — |
| Pipeline orchestrator | — | TS-200 to TS-208 | — |
| Data integrity | — | TS-210 to TS-216 | — |
| Security | TS-226, TS-227 | TS-220 to TS-228 | TS-220 |
