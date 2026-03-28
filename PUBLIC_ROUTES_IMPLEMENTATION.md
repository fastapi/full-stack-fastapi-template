# Public Routes Implementation Guide

## Overview

Successfully implemented Option 1: Unified React Application with public and protected routes. The existing React admin portal has been extended to include public pages, eliminating the need for a separate Next.js runner site.

## What Was Implemented

### 1. Public Layout System
- **Created**: `frontend/src/routes/_public.tsx` - Layout wrapper for all public pages
- **Components**:
  - `PublicHeader.tsx` - Navigation header with login/signup buttons
  - `PublicFooter.tsx` - Footer with links and branding

### 2. Public Pages
All public pages are accessible without authentication:

- **Home Page** (`/`)
  - Hero section with CTAs
  - Features showcase
  - Call-to-action for registration
  
- **Races Page** (`/races`)
  - Browse upcoming races
  - Placeholder data (ready for API integration)
  - Filter section for future enhancements
  
- **About Page** (`/about`)
  - Platform information
  - Mission statement
  - Features for runners and organizers

### 3. Route Structure

```
frontend/src/routes/
├── __root.tsx                 # Root layout
├── _public.tsx                # Public layout (no auth required)
│   ├── index.tsx              # Home page (/)
│   ├── about.tsx              # About page (/about)
│   └── races.tsx              # Races listing (/races)
├── _layout.tsx                # Protected layout (requires auth)
│   ├── dashboard.tsx          # Dashboard (/dashboard) - NEW!
│   ├── admin.tsx              # Admin panel (/admin)
│   ├── items.tsx              # Items management (/items)
│   └── settings.tsx           # User settings (/settings)
├── login.tsx                  # Login page (/login)
└── signup.tsx                 # Signup page (/signup)
```

### 4. Authentication Flow

- **Public visitors**: Can browse `/`, `/races`, `/about`
- **Already logged in**: Header shows "Dashboard" button
- **After login**: Redirects to `/dashboard` instead of `/`
- **Protected routes**: Require authentication, redirect to `/login` if not logged in

## SEO Support

All public pages include meta tags via TanStack Router's `head` function:

```typescript
export const Route = createFileRoute("/_public/")({
  component: HomePage,
  head: () => ({
    meta: [
      {
        title: "RaceHub - Find and Register for Running Races",
        description: "Discover running races near you...",
      },
    ],
  }),
})
```

## Next Steps

### 1. Add Race Management API

Create race endpoints in the backend:

```bash
# backend/app/models.py - Add Race model
# backend/app/crud.py - Add race CRUD operations
# backend/app/api/routes/races.py - Add race endpoints
```

### 2. Connect Races Page to API

Update `frontend/src/routes/_public/races.tsx` to fetch real data:

```typescript
import { useQuery } from "@tanstack/react-query"
import { RacesService } from "@/client"

const { data: races } = useQuery({
  queryKey: ["races"],
  queryFn: RacesService.listRaces,
})
```

### 3. Add Race Registration Flow

- Create race detail page: `/races/$raceId`
- Add registration form for authenticated users
- Handle payment processing

### 4. Enhance SEO (Optional)

For critical SEO needs, add prerendering:

```bash
cd frontend
bun add -D vite-plugin-ssr
```

Configure in `vite.config.ts` to prerender static pages.

### 5. Clean Up Runner Site (Optional)

The `runner-site/` directory is now obsolete and can be:
- Deleted completely, or
- Kept as backup/reference during transition

## Testing the Implementation

1. **Start the dev server**:
   ```bash
   cd frontend
   bun run dev
   ```

2. **Visit public pages** (no login required):
   - http://localhost:5173/ - Home page
   - http://localhost:5173/races - Races listing
   - http://localhost:5173/about - About page

3. **Test authentication flow**:
   - Click "Login" in header
   - Log in with test credentials
   - Should redirect to `/dashboard`
   - Header should show "Dashboard" button

4. **Test protected routes**:
   - Try accessing `/dashboard`, `/admin`, `/items` without login
   - Should redirect to `/login`

## Benefits Achieved

✅ **Single Codebase**: No more maintaining two separate frontends
✅ **Shared Infrastructure**: Reuse API client, components, utilities
✅ **Type Safety**: Full TypeScript + TanStack Router type safety
✅ **Consistent UX**: Same UI patterns across all pages
✅ **Auto-generated API Client**: Changes to backend API automatically update frontend
✅ **Modern SEO**: Meta tags support with potential for prerendering
✅ **Faster Development**: One build process, one deployment

## Updated Documentation

- ✅ RBAC.md updated to reflect unified architecture
- ✅ Removed references to separate Next.js runner site
- ✅ Updated deployment instructions

## Files Modified

### Created:
- `frontend/src/components/Public/PublicHeader.tsx`
- `frontend/src/components/Public/PublicFooter.tsx`
- `frontend/src/routes/_public.tsx`
- `frontend/src/routes/_public/index.tsx`
- `frontend/src/routes/_public/about.tsx`
- `frontend/src/routes/_public/races.tsx`

### Modified:
- `frontend/src/routes/_layout/index.tsx` → `dashboard.tsx` (moved)
- `frontend/src/hooks/useAuth.ts` (redirect to /dashboard)
- `frontend/src/routes/login.tsx` (redirect to /dashboard)
- `RBAC.md` (updated architecture documentation)

### Auto-generated:
- `frontend/src/routeTree.gen.ts` (TanStack Router route tree)

## Troubleshooting

### "Route not found" errors
- Route tree regenerates automatically when dev server runs
- If issues persist, restart the dev server

### Type errors on routes
- Make sure dev server has run at least once to generate route tree
- Check `frontend/src/routeTree.gen.ts` exists

### Styling issues
- All components use Tailwind CSS and shadcn/ui
- Dark mode supported via theme provider

## Questions?

Refer to:
- Main README: `/README.md`
- RBAC Documentation: `/RBAC.md`
- Frontend README: `/frontend/README.md`
- TanStack Router Docs: https://tanstack.com/router
