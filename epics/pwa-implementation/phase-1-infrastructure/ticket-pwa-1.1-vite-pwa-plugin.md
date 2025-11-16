# Ticket PWA-1.1: Install and Configure Vite PWA Plugin

## Overview
Install and configure the vite-plugin-pwa package to enable Progressive Web App capabilities in the React/Vite frontend. This will set up the foundation for service worker registration, caching strategies, and PWA manifest integration.

## Prerequisites
- Node.js and npm installed in frontend development environment
- Existing Vite React application
- HTTPS deployment (already configured via Cloudflare Tunnel)

## Step 1: Install vite-plugin-pwa

### Install the Package

```bash
cd frontend
npm install -D vite-plugin-pwa
```

### Verify Installation

```bash
npm list vite-plugin-pwa
```

Should show the installed version (typically 0.17.x or later).

## Step 2: Configure Vite to Use PWA Plugin

### Update vite.config.ts

Open `frontend/vite.config.ts` and add the PWA plugin configuration:

```typescript
import path from "node:path"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
    }),
    react(),
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
    }),
  ],
})
```

## Step 3: Understanding the Configuration

### registerType: 'autoUpdate'
The service worker will automatically update when a new version is available without requiring user confirmation.

### includeAssets
List of static assets to include in the service worker precache. These will be available offline.

### manifest
The web app manifest defines how the app appears when installed:
- **name**: Full app name shown in install prompts
- **short_name**: Shorter name shown under icon
- **description**: App description
- **theme_color**: Browser UI color
- **background_color**: Splash screen background
- **display**: 'standalone' makes it look like a native app
- **icons**: App icons for different sizes

### workbox.globPatterns
File patterns to precache. These files will be available offline immediately after installation.

### workbox.runtimeCaching
- **NetworkFirst**: Try network first, fall back to cache if offline
- Good for API calls where you want fresh data when online
- Caches successful responses for offline use

### devOptions.enabled
Enables PWA functionality in development mode for testing.

## Step 4: Test PWA in Development

### Start Development Server

```bash
cd frontend
npm run dev
```

### Check Service Worker Registration

1. Open browser DevTools (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click **Service Workers** in left sidebar
4. Should see service worker registered for `http://localhost:5173`

### Verify Manifest

1. In DevTools > Application tab
2. Click **Manifest** in left sidebar
3. Should show "A Seashell Company" with your app details

### Check Console for PWA Messages

Look for messages like:
```
PWA: Service worker registered
PWA: Content cached for offline use
```

## Step 5: Build and Test PWA Build

### Create Production Build

```bash
cd frontend
npm run build
```

### Preview Production Build

```bash
npm run preview
```

This starts a local server serving the production build.

### Test Production PWA Features

1. Open `http://localhost:4173` (or port shown)
2. DevTools > Application > Service Workers
3. Verify service worker is registered
4. Check that assets are cached
5. Go offline (DevTools > Network > Offline checkbox)
6. Refresh page - should still work with cached assets

## Step 6: Verify PWA Installability

### Chrome Desktop
1. Look for install icon in address bar (+ or download icon)
2. Should show "Install A Seashell Company"
3. Don't install yet, just verify it appears

### Chrome Mobile (DevTools Device Mode)
1. Toggle device toolbar (Ctrl+Shift+M)
2. Select a mobile device
3. Check for install banner/prompt

## Verification Checklist

- [ ] vite-plugin-pwa installed successfully
- [ ] vite.config.ts updated with PWA configuration
- [ ] Development server starts without errors
- [ ] Service worker visible in DevTools
- [ ] Manifest shows correct app info
- [ ] Production build completes successfully
- [ ] Production preview works offline
- [ ] Install prompt appears in browser
- [ ] No console errors related to PWA

## Troubleshooting

### Service Worker Not Registering

Check console for errors. Common issues:
- HTTPS required (except localhost)
- manifest.json errors
- vite.config.ts syntax errors

**Fix**: Verify all config syntax is correct.

### Module Import Errors

If you see `Cannot find module 'vite-plugin-pwa'`:

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Manifest Not Loading

Check browser console for manifest errors. The plugin auto-generates manifest but uses the configuration from vite.config.ts.

**Fix**: Ensure manifest configuration in vite.config.ts has no syntax errors.

### Build Fails

If build fails with PWA-related errors:

```bash
# Check plugin version compatibility
npm list vite-plugin-pwa vite

# Update if needed
npm update vite-plugin-pwa
```

## Next Steps

After completing this ticket:
1. Ticket PWA-1.2: Create offline fallback page and configure advanced caching
2. Test service worker caching strategies
3. Prepare for icon generation in Phase 2

## Additional Resources

- [Vite PWA Plugin Documentation](https://vite-pwa-org.netlify.app/)
- [Workbox Strategies](https://developer.chrome.com/docs/workbox/modules/workbox-strategies/)
- [Web App Manifest Spec](https://w3c.github.io/manifest/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

## Notes

- The configuration above uses NetworkFirst for API calls, which prioritizes fresh data
- Static assets use precaching for instant offline access
- manifest.json in /public will be replaced by the plugin's generated manifest
- Service worker will be generated at build time in the dist folder
- Development mode includes service worker for testing purposes