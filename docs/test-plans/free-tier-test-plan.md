# Free Tier User Test Plan

## Overview
Test the entitlement enforcement for `free_trial` tier users, covering quota limits, feature gates, and backend enforcement.

---

## 1. Quota Limits

| Resource | Free Trial Limit | Test Scenario |
|----------|-----------------|---------------|
| `brands` | 1 | Create 2 brands → 2nd should fail with 403 |
| `brandsPerProject` | 1 | (deferred - project system not fully implemented) |
| `segmentsPerBrand` | 1 | Add 2 segments to a brand → 2nd should fail with 403 |
| `promptsPerSegment` | 1 | (frontend disabled - verify no crash) |

### Test Cases

- **FQT-001**: Free trial user creates first brand → success
- **FQT-002**: Free trial user creates second brand → 403 error with message "Free trial is limited to 1 active brand"
- **FQT-003**: Free trial user creates brand with 2 segments → 403 error with message "Free trial is limited to 1 segment per brand"
- **FQT-004**: Free trial user attempts to add second segment to existing brand → 403 error
- **FQT-005**: QuotaGate disables "Add Brand" button when user has 1 brand (tooltip shows limit)
- **FQT-006**: QuotaGate disables "Add Segment" button when brand has 1 segment

---

## 2. Feature Gates

| Feature | Free Trial Access | Test Scenario |
|---------|-------------------|---------------|
| `brandImpression` | ✅ true | Can access brand impression page |
| `competitiveAnalysisFull` | ❌ false | Sees blurred content + lock overlay with "Upgrade to Pro" |
| `competitiveVisibilityGap` | ✅ true | Can see Visibility Gap pill in Competitive Current Status |
| `InsightBrandRisk` | ❌ false | Cannot access Brand Risk Overview page |
| `InsightAll` | ❌ false | Cannot access insight pages |

### Test Cases

- **FQT-007**: Free trial user visits Competitive Analysis → sees full charts blurred with upgrade CTA
- **FQT-008**: Free trial user clicks "View plans" in FeatureGate → navigates to /app/settings
- **FQT-009**: Free trial user navigates to Brand Risk insight → sees FeatureGate lock overlay
- **FQT-010**: Free trial user navigates to Growth Risk / Ranking Risk insights → sees FeatureGate lock overlay

---

## 3. Read-Only Mode

Triggers: `expired`, `cancelled`, `past_due` status

### Test Cases

- **FQT-011**: User with `expired` status tries to create brand → fails (canAccess returns false)
- **FQT-012**: User with `cancelled` status tries to add segment → fails
- **FQT-013**: User with `past_due` status can view existing brands but cannot create new ones

---

## 4. Super User Bypass

### Test Cases

- **FQT-014**: Super user (`is_super_user=true`) bypasses all quota limits → can create unlimited brands/segments
- **FQT-015**: Super user bypasses all feature gates → sees all features without upgrade CTAs

---

## 5. UI/UX Verification

### Test Cases

- **FQT-016**: Free trial user sees "Free Trial" badge in header/settings
- **FQT-017**: Free trial user sees upgrade prompt in navigation when accessing gated features
- **FQT-018**: Pricing page shows correct feature comparison between Free Trial and Pro
- **FQT-019**: Stripe checkout flow works for upgrading from free trial to Pro

---

## 6. Backend Enforcement Verification

### Test Cases

- **FQT-020**: API POST /brands/setup with 2 segments returns 403 (backend enforcement)
- **FQT-021**: API POST /brands/{id}/activate when user already has 1 active brand returns 403
- **FQT-022**: Backend rejects requests that bypass frontend quota gates

---

## Test Data Setup

```typescript
// Free trial subscription
const freeTrialSubscription = {
  tier: "free_trial",
  status: "active",
  trial_expires_at: "2026-04-14T00:00:00Z",
  current_period_end: null,
  cancel_at_period_end: false,
  is_super_user: false,
}
```

---

## Notes

- Frontend enforcement is primary; backend has partial enforcement only for brands/segments
- Some quota fields (`brandsPerProject`, `promptsPerSegment`) may not be actively used yet
- Rate limiting is configured but not actively enforced in code
