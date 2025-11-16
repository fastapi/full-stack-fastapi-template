# Ticket PWA-1.2: Offline Page and Advanced Caching Configuration

## Overview
Create an offline fallback page that displays when users are offline and enhance the service worker caching configuration. This ensures users get a meaningful experience when network connectivity is lost.

## Prerequisites
- Ticket PWA-1.1 complete (vite-plugin-pwa installed and configured)
- Service worker registered and running
- React/Vite frontend working

## Step 1: Create Static Offline Page

### Create offline.html

Create a new file `frontend/public/offline.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Offline - A Seashell Company</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: #f7fafc;
      color: #2d3748;
    }
    .container {
      text-align: center;
      padding: 2rem;
      max-width: 500px;
    }
    .icon {
      font-size: 5rem;
      margin-bottom: 1rem;
    }
    h1 {
      font-size: 2rem;
      font-weight: 600;
      margin: 0 0 1rem 0;
    }
    p {
      color: #718096;
      margin: 0.5rem 0;
      line-height: 1.6;
    }
    .secondary {
      color: #a0aec0;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">📡</div>
    <h1>You're Offline</h1>
    <p>It looks like you've lost your internet connection.</p>
    <p>Please check your connection and try again.</p>
    <p class="secondary">Some previously visited pages may still be available.</p>
  </div>
</body>
</html>
```

### Why a Static HTML File?

**Critical for SPAs:**
- The offline page must load when JavaScript can't execute
- Client-side routes (React/TanStack Router) require the JS bundle to work
- A static HTML file is precached and works without any dependencies
- Workbox expects navigateFallback to point to a precached URL

**Benefits:**
- Works even if the main app bundle fails to load
- No external dependencies (CSS, JS, fonts)
- Lightweight and fast
- Always available offline

## Step 2: Update PWA Configuration for Offline Support

### Update vite.config.ts

Modify the VitePWA configuration in `frontend/vite.config.ts` to handle offline fallback:

```typescript
VitePWA({
  registerType: 'autoUpdate',
  includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
  manifest: {
    name: 'A Seashell Company',
    short_name: 'Shell',
    description: "let's sell Seashell by the seashore",
    theme_color: '#000000',
    background_color: '#ffffff',
    display: 'standalone',
    icons: [
      {
        src: 'icon-192.png',
        sizes: '192x192',
        type: 'image/png'
      },
      {
        src: 'icon-512.png',
        sizes: '512x512',
        type: 'image/png'
      }
    ]
  },
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
    // Add offline fallback
    navigateFallback: '/offline.html',
    navigateFallbackDenylist: [/^\/api/],
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.a-seashell-company\.com\/api\/.*/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 60 * 24, // 24 hours
          },
          cacheableResponse: {
            statuses: [0, 200],
          },
        },
      },
    ],
  },
  devOptions: {
    enabled: true,
    type: 'module',
  },
})
```

### What Changed?
- **navigateFallback: '/offline.html'** - Shows static offline page when navigation fails
- **navigateFallbackDenylist: [/^\/api/]** - Don't show offline page for API calls (let them fail normally)

### Why These Changes?
- navigateFallback points to static HTML file that works without JavaScript
- navigateFallbackDenylist prevents offline page from appearing for API requests
- API caching already configured from Ticket PWA-1.1

## Step 3: Test Offline Functionality

### Rebuild Frontend Container

```bash
docker compose up -d --build frontend
```

### Test Offline Mode in Browser

1. Open http://localhost:5173
2. Open DevTools (F12)
3. Go to **Application** tab
4. Click **Service Workers** in sidebar
5. Check **Offline** checkbox

### Verify Offline Behavior

1. **Test offline fallback:**
   - With offline mode enabled, try navigating to a new page you haven't visited
   - Should see the offline page component

2. **Test cached pages:**
   - Turn off offline mode
   - Visit several pages (dashboard, settings, items)
   - Turn offline mode back on
   - Navigate to those pages - they should load from cache

3. **Test API calls:**
   - With offline mode on, try actions that call the API
   - Should see network errors (not the offline page)
   - This is correct - API calls should fail, not redirect

### Check Service Worker Cache

1. In DevTools > Application tab
2. Click **Cache Storage** in sidebar
3. Should see caches:
   - `workbox-precache-...` (static assets including offline.html)
   - `api-cache` (API responses)

## Step 4: Test Network-First Caching for API

### Understanding NetworkFirst Strategy

The API uses NetworkFirst strategy:
- **Online**: Always tries network first, caches successful responses
- **Offline**: Falls back to cached API responses if available

### Test API Caching

1. **Online - populate cache:**
   - Turn off offline mode
   - Navigate to /items page
   - Open DevTools > Network tab
   - Should see API call to `/api/v1/items/`
   - Go to Application > Cache Storage > api-cache
   - Should see the API response cached

2. **Offline - use cache:**
   - Enable offline mode
   - Refresh /items page
   - Page should load with cached data
   - Network tab will show failed requests, but cached data displays

3. **Clear cache and test:**
   - Clear api-cache in DevTools
   - Refresh while offline
   - Should fail (no cached data available)

## Step 5: Verify Production Build

### Build for Production

```bash
cd frontend
npm run build
```

Should complete without errors and show:
```
vite-plugin-pwa: PWA enabled
vite-plugin-pwa: Service worker generated
```

### Preview Production Build

```bash
npm run preview
```

This starts a local server serving the production build (usually port 4173).

### Test Production PWA

1. Open production preview URL (e.g., http://localhost:4173)
2. Verify service worker registers
3. Test offline functionality same as Step 4
4. Check that all caching strategies work

## Verification Checklist

- [ ] offline.html created in public/ folder
- [ ] vite.config.ts updated with navigateFallback: '/offline.html'
- [ ] navigateFallbackDenylist configured for /api
- [ ] Frontend container rebuilt
- [ ] Offline page displays when offline and page not cached
- [ ] Previously visited pages load from cache when offline
- [ ] API calls fail gracefully (not showing offline page)
- [ ] Cache Storage shows multiple caches in DevTools
- [ ] NetworkFirst strategy caches API responses
- [ ] Cached API data displays when offline
- [ ] Production build completes successfully
- [ ] Production preview works with PWA features

## Troubleshooting

### Offline Page Not Showing

**Check navigateFallback:**
```typescript
// Should be set in vite.config.ts
navigateFallback: '/offline.html',
```

**Verify offline.html exists:**
```bash
ls frontend/public/offline.html
# Should exist
```

**Clear service worker:**
1. DevTools > Application > Service Workers
2. Click "Unregister"
3. Hard refresh (Ctrl+Shift+R)
4. Service worker should re-register with new config

### offline.html Returns 403 Forbidden

**Problem:**
Service worker shows error: `bad-precaching-response: bad-precaching-response :: [{"url":"http://localhost:5173/offline.html","status":403}]`

**Cause:**
File permissions on offline.html are too restrictive (`-rw-------`), preventing nginx from reading it.

**Fix:**
```bash
chmod 644 /workspaces/full-stack-fastapi-template/frontend/public/offline.html
```

Then rebuild the container:
```bash
docker compose up -d --build frontend
```

**Why this happens:**
When offline.html is created, it may get restrictive permissions. Docker COPY preserves these permissions, so nginx in the container can't read the file.

**Verify the fix worked:**
```bash
# Check permissions in container
docker compose exec frontend ls -la /usr/share/nginx/html/offline.html

# Should show: -rw-r--r-- (644)
```

### API Calls Showing Offline Page

This means navigateFallbackDenylist isn't working.

**Fix:**
```typescript
navigateFallbackDenylist: [/^\/api/],
```

Make sure the regex matches your API URL pattern.

### Cached Data Not Loading Offline

**Check Cache Storage:**
1. DevTools > Application > Cache Storage
2. Verify api-cache exists and has entries
3. If empty, visit pages while online to populate cache

**Check cacheableResponse:**
```typescript
cacheableResponse: {
  statuses: [0, 200],  // Should include 200
}
```

### Service Worker Not Updating

**Force update:**
```bash
# Rebuild with no cache
docker compose build --no-cache frontend
docker compose up -d frontend
```

In browser:
1. DevTools > Application > Service Workers
2. Check "Update on reload"
3. Hard refresh

## Understanding the Caching Strategies

### CacheFirst (Google Fonts)
1. Check cache first
2. If not in cache, fetch from network
3. Store in cache for next time
4. **Best for**: Static resources that rarely change

### NetworkFirst (API calls)
1. Try network first
2. If network fails, use cache
3. Update cache with fresh response
4. **Best for**: Dynamic data where fresh is preferred but stale is acceptable

### Precaching (Static Assets)
1. All matched files cached during service worker installation
2. Available immediately offline
3. Updated when service worker updates
4. **Best for**: App shell (HTML, CSS, JS)

## Next Steps

After completing this ticket:
1. Phase 1 complete (PWA infrastructure)
2. Move to Phase 2: App Icons and Branding
3. Ticket PWA-2.1: Generate and optimize app icons
4. This will fix the icon-192.png and icon-512.png errors

## Additional Resources

- [Workbox NavigateFallback](https://developer.chrome.com/docs/workbox/modules/workbox-routing/#navigation-route)
- [Workbox Caching Strategies](https://developer.chrome.com/docs/workbox/modules/workbox-strategies/)
- [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache)

## Notes

- The offline page uses static HTML instead of React components because:
  - Must work when JavaScript fails to load
  - Client-side routes require the JS bundle to execute
  - Workbox expects navigateFallback to be a precached URL
  - Static files are precached during service worker installation
- The offline page is intentionally simple with no external dependencies
- API calls fail gracefully instead of showing offline page (better UX)
- NetworkFirst strategy ensures users get fresh data when online
- Previously visited pages will work offline even without the offline page
- Service worker caching is automatic once configured
