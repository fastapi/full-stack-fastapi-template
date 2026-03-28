---
description: "Instructions for working with React/TypeScript frontend files including components, routes, hooks, and API client usage."
applyTo: "frontend/src/**/*.{ts,tsx}"
---

# Frontend React/TypeScript Development Instructions

## React + TypeScript + Vite Patterns

### Component Structure

Organize components by feature in `frontend/src/components/`:

```
components/
├── Admin/          # Admin-specific components
├── Items/          # Item management components
├── UserSettings/   # User settings components
├── Common/         # Shared components
├── Sidebar/        # Navigation components
└── ui/            # shadcn/ui components (don't modify)
```

### Component Pattern

Use functional components with TypeScript:

```tsx
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { ResourcesService, type ResourcePublic, type ResourceCreate } from '@/client'
import { useCustomToast } from '@/hooks/useCustomToast'

interface ResourceListProps {
  userId?: string
  showAll?: boolean
}

export function ResourceList({ userId, showAll = false }: ResourceListProps) {
  const [isOpen, setIsOpen] = useState(false)
  const showToast = useCustomToast()
  
  // Data fetching with TanStack Query
  const { data, isLoading, error } = useQuery({
    queryKey: ['resources', userId],
    queryFn: () => ResourcesService.readResources({ skip: 0, limit: 100 }),
  })
  
  // Mutation for create/update
  const createMutation = useMutation({
    mutationFn: (resourceData: ResourceCreate) => 
      ResourcesService.createResource({ requestBody: resourceData }),
    onSuccess: () => {
      showToast('Success', 'Resource created successfully', 'success')
      queryClient.invalidateQueries({ queryKey: ['resources'] })
    },
    onError: (err) => {
      showToast('Error', 'Failed to create resource', 'error')
    },
  })
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading resources</div>
  
  return (
    <div className="space-y-4">
      {data?.data.map((resource) => (
        <ResourceCard key={resource.id} resource={resource} />
      ))}
    </div>
  )
}
```

### Key Patterns

#### 1. API Client Usage

Import from auto-generated client (regenerate after backend changes):

```tsx
import { 
  ResourcesService, 
  UsersService,
  type ResourcePublic, 
  type ResourceCreate,
  type UserPublic 
} from '@/client'
```

**Never modify files in `src/client/` - they are auto-generated!**

#### 2. TanStack Query for Data Fetching

**Query (GET requests):**
```tsx
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['resources', filters],  // Cache key
  queryFn: () => ResourcesService.readResources({ skip: 0, limit: 100 }),
  enabled: !!userId,  // Only run if condition is true
})
```

**Mutation (POST/PUT/DELETE):**
```tsx
const mutation = useMutation({
  mutationFn: (data: ResourceCreate) => 
    ResourcesService.createResource({ requestBody: data }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['resources'] })
    showToast('Success', 'Created successfully', 'success')
  },
  onError: (error) => {
    showToast('Error', error.message, 'error')
  },
})

// Use in handler
const handleCreate = async (data: ResourceCreate) => {
  mutation.mutate(data)
}
```

#### 3. Custom Hooks

Use hooks from `src/hooks/`:

```tsx
import { useAuth } from '@/hooks/useAuth'
import { useCustomToast } from '@/hooks/useCustomToast'
import { useMobile } from '@/hooks/useMobile'

function MyComponent() {
  const { user, logout } = useAuth()
  const showToast = useCustomToast()
  const isMobile = useMobile()
  
  // Your component logic
}
```

#### 4. Form Handling

Forms should use controlled components:

```tsx
import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

function ResourceForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  })
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // Submit logic
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        name="title"
        value={formData.title}
        onChange={handleChange}
        placeholder="Title"
      />
      <Button type="submit">Submit</Button>
    </form>
  )
}
```

#### 5. shadcn/ui Components

Import pre-built components from `@/components/ui/`:

```tsx
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
```

**Do not modify files in `components/ui/` - they are managed by shadcn!**

#### 6. Styling with Tailwind

Use Tailwind utility classes:

```tsx
<div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-card">
  <h2 className="text-2xl font-bold">Title</h2>
  <Button variant="outline" size="sm">Action</Button>
</div>
```

Common patterns:
- Layout: `flex`, `grid`, `space-y-4`, `gap-4`
- Spacing: `p-4`, `m-2`, `px-6`, `py-3`
- Colors: `bg-primary`, `text-muted-foreground`, `border-border`
- Dark mode: automatic via theme (don't add dark: variants manually)

### Routing with TanStack Router

Route files in `frontend/src/routes/`:

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { ResourceList } from '@/components/Resources/ResourceList'

export const Route = createFileRoute('/resources')({
  component: ResourcesPage,
  // Optional: Load data before rendering
  loader: async () => {
    const resources = await ResourcesService.readResources()
    return { resources }
  },
})

function ResourcesPage() {
  const { resources } = Route.useLoaderData()
  const navigate = useNavigate()
  
  return (
    <div>
      <h1>Resources</h1>
      <ResourceList initialData={resources} />
    </div>
  )
}
```

**Route structure maps to URLs:**
- `routes/index.tsx` → `/`
- `routes/resources/index.tsx` → `/resources`
- `routes/resources/$id.tsx` → `/resources/:id`
- `routes/_layout.tsx` → Layout wrapper for child routes

### Authentication

Use the `useAuth` hook:

```tsx
import { useAuth } from '@/hooks/useAuth'

function ProtectedComponent() {
  const { user, isLoading, logout } = useAuth()
  
  if (isLoading) return <div>Loading...</div>
  if (!user) return <div>Please login</div>
  
  return (
    <div>
      <p>Welcome, {user.full_name}</p>
      {user.is_superuser && <AdminPanel />}
    </div>
  )
}
```

### TypeScript Best Practices

1. **Use generated types** from `@/client`:
   ```tsx
   import type { ResourcePublic, UserPublic } from '@/client'
   ```

2. **Define component props**:
   ```tsx
   interface ComponentProps {
     title: string
     isActive?: boolean
     onSubmit: (data: FormData) => Promise<void>
   }
   ```

3. **Type event handlers**:
   ```tsx
   const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {}
   const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {}
   const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {}
   ```

4. **Type state properly**:
   ```tsx
   const [data, setData] = useState<ResourcePublic | null>(null)
   const [items, setItems] = useState<ResourcePublic[]>([])
   ```

### State Management

1. **Server State**: Use TanStack Query (for API data)
2. **Component State**: Use `useState` (for UI state)
3. **Shared State**: Use React Context or prop drilling
4. **Form State**: Controlled components with `useState`

### Error Handling

Always handle errors from API calls:

```tsx
const { data, error, isLoading } = useQuery({
  queryKey: ['resource', id],
  queryFn: () => ResourcesService.readResource({ id }),
})

if (isLoading) return <LoadingSpinner />
if (error) {
  return <ErrorMessage message={error.message} />
}
if (!data) return null
```

### Performance Optimization

1. **Memoize expensive computations**:
   ```tsx
   const filteredItems = useMemo(
     () => items.filter(item => item.active),
     [items]
   )
   ```

2. **Memoize callbacks**:
   ```tsx
   const handleClick = useCallback(() => {
     doSomething(id)
   }, [id])
   ```

3. **Use query invalidation** instead of refetching:
   ```tsx
   queryClient.invalidateQueries({ queryKey: ['resources'] })
   ```

### Accessibility

- Use semantic HTML elements
- Add ARIA labels when needed
- shadcn/ui components have accessibility built-in
- Test keyboard navigation

### Testing

Write Playwright tests in `frontend/tests/`:

```typescript
import { test, expect } from '@playwright/test'

test('should create resource', async ({ page }) => {
  await page.goto('/resources')
  await page.click('button:has-text("New Resource")')
  await page.fill('input[name="title"]', 'Test Resource')
  await page.click('button:has-text("Create")')
  await expect(page.locator('text=Test Resource')).toBeVisible()
})
```

### Common Patterns

#### Loading States
```tsx
{isLoading && <LoadingSpinner />}
{data && <DataView data={data} />}
```

#### Empty States
```tsx
{data?.data.length === 0 && (
  <EmptyState 
    message="No resources found" 
    action={<Button>Create First Resource</Button>}
  />
)}
```

#### Modals/Dialogs
```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
    </DialogHeader>
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

### When Adding New Features

1. Check if API client needs regeneration: `bash scripts/generate-client.sh`
2. Create component in appropriate feature folder
3. Use TanStack Query for data fetching
4. Import types from `@/client`
5. Use shadcn/ui components for UI
6. Style with Tailwind classes
7. Handle loading and error states
8. Write Playwright tests
9. Test dark mode compatibility

### Don't Do This

❌ Modify files in `src/client/` (auto-generated)
❌ Modify files in `src/components/ui/` (managed by shadcn)
❌ Use inline styles (use Tailwind classes)
❌ Fetch data with fetch/axios (use generated client)
❌ Store server state in useState (use TanStack Query)
❌ Forget error handling
❌ Skip TypeScript types
