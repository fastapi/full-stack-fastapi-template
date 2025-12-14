# STRIPE-2.2: Frontend Item Limit Error Handling

## Status: COMPLETE

## Summary
Update the frontend to handle 403 errors when creating items. Show an upgrade modal instead of a generic error toast.

## Acceptance Criteria
- [ ] 403 error on item creation shows upgrade modal (not error toast)
- [ ] Modal explains the 2-item limit
- [ ] Modal has "Upgrade to Premium" button
- [ ] Upgrade button calls create-checkout-session endpoint
- [ ] User is redirected to Stripe Checkout
- [ ] Other errors still show normal error toast

## Technical Details

### New Component
Create `frontend/src/components/Premium/UpgradeModal.tsx`:
- Props: `isOpen`, `onClose`
- Shows limit explanation and benefits
- "Upgrade Now - $1" button calls StripeService.createCheckoutSession()
- On success, redirect to checkout_url via window.location.href

### Modify AddItem Component
Update `frontend/src/components/Items/AddItem.tsx`:
- Add state: `showUpgradeModal`
- In mutation onError: check if `err.status === 403`
- If 403: close add dialog, show upgrade modal
- Otherwise: use existing `handleError(err)`

### Generate TypeScript Client
```bash
./scripts/generate-client.sh
```
This creates `StripeService.createCheckoutSession()` from OpenAPI schema.

### Files to Create/Modify
1. `frontend/src/components/Premium/UpgradeModal.tsx` - NEW
2. `frontend/src/components/Items/AddItem.tsx` - Handle 403
3. Regenerate client after backend changes

## Dependencies
- STRIPE-1.3 (create-checkout-session endpoint)
- STRIPE-2.1 (backend returns 403 on limit)

## Testing
- [ ] Create items until limit reached
- [ ] 403 error shows upgrade modal (not toast)
- [ ] Upgrade button redirects to Stripe
- [ ] Cancel closes modal
- [ ] Other errors show normal toast

## Notes
- StripeService auto-generated from OpenAPI schema
- Redirect via window.location.href to Stripe checkout
- User returns to /payment-success after payment
