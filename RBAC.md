# RBAC (Role-Based Access Control) System

## Overview

The system includes a comprehensive RBAC system that allows fine-grained permission control for different user types. The application uses a single React frontend that serves both public pages and role-based authenticated dashboards.

## Roles

The system defines four default roles:

### 1. Admin
- **Purpose**: System administrators with full access
- **Permissions**: Full CRUD access to all resources, user management, role management
- **Access**: Protected dashboard routes with admin-only features

### 2. Runner  
- **Purpose**: Regular users who participate in races
- **Permissions**: Register for races, view own profile and race history, update own information
- **Access**: Public pages + personal dashboard when authenticated

### 3. Organizer
- **Purpose**: Race organizers who create and manage events
- **Permissions**: Create/edit/delete races, manage race registrations, view participant lists
- **Access**: Protected dashboard with race management features

### 4. Volunteer
- **Purpose**: Volunteers who help with race operations  
- **Permissions**: Check-in runners, view race information, assist with race day operations
- **Access**: Limited dashboard for race day operations

## Architecture

### Database Schema

```
User (existing table)
├── id: UUID (PK)
├── email: String
├── hashed_password: String
├── is_active: Boolean
├── is_superuser: Boolean
└── roles: Relationship → UserRoleLink

Role (new table)
├── id: UUID (PK)
├── name: String (unique)
├── description: String
└── users: Relationship → UserRoleLink

UserRoleLink (new junction table)
├── user_id: UUID (FK → User)
└── role_id: UUID (FK → Role)
```

### Backend Implementation

#### Models (`backend/app/models.py`)

- **RoleEnum**: Enum defining the four role types
- **Role**: SQLModel table for roles
- **UserRoleLink**: Many-to-many relationship table
- **User**: Extended with `roles` relationship

#### CRUD Operations (`backend/app/crud.py`)

```python
# Role management
create_role(session, role_create)
get_role_by_name(session, name)
get_or_create_role(session, role_name, description)

# User-role management
assign_role_to_user(session, user, role)
remove_role_from_user(session, user, role)  
user_has_role(user, role_name)
user_has_any_role(user, role_names)
```

#### Dependencies (`backend/app/api/deps.py`)

##### Permission Checking Functions
```python
# Factory functions for custom role requirements
require_role(required_role)        # Single role
require_any_role(required_roles)   # Any of multiple roles
```

##### Predefined Dependencies
```python
AdminUser           # Requires 'admin' role
RunnerUser          # Requires 'runner' role
OrganizerUser       # Requires 'organizer' role
VolunteerUser       # Requires 'volunteer' role
AdminOrOrganizerUser # Requires 'admin' OR 'organizer'
```

#### API Routes (`backend/app/api/routes/roles.py`)

All role management endpoints are admin-only:

- `GET /api/v1/roles/` - List all roles
- `GET /api/v1/roles/{role_id}` - Get role by ID
- `POST /api/v1/roles/` - Create new role
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `POST /api/v1/roles/{role_id}/assign/{user_id}` - Assign role to user
- `DELETE /api/v1/roles/{role_id}/remove/{user_id}` - Remove role from user

## Using RBAC in API Endpoints

### Method 1: Using Predefined Dependencies

```python
from app.api.deps import AdminUser, RunnerUser, OrganizerUser

@router.get("/admin-only")
def admin_endpoint(current_user: AdminUser) -> Any:
    """Only admins can access this."""
    return {"message": "Admin access"}

@router.get("/runner-only")  
def runner_endpoint(current_user: RunnerUser) -> Any:
    """Only runners can access this."""
    return {"message": "Runner access"}
```

### Method 2: Using Custom Role Requirements

```python
from fastapi import Depends
from app.api.deps import require_role, require_any_role

@router.get("/organizers", dependencies=[Depends(require_role("organizer"))])
def organizer_endpoint() -> Any:
    """Only organizers can access this."""
    return {"message": "Organizer access"}

@router.get("/staff", dependencies=[Depends(require_any_role(["organizer", "volunteer"]))])
def staff_endpoint() -> Any:
    """Organizers or volunteers can access this."""
    return {"message": "Staff access"}
```

### Method 3: Manual Permission Checking

```python
from app import crud
from app.api.deps import CurrentUser

@router.post("/races")
def create_race(current_user: CurrentUser, race_in: RaceCreate) -> Any:
    """Create a race - requires organizer or admin role."""
    if not crud.user_has_any_role(current_user, ["admin", "organizer"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Create race logic here
    return race
```

## Superuser Override

**Important**: Users with `is_superuser=True` bypass all role checks. They automatically have access to all endpoints regardless of role requirements.

## Frontend Integration

### Unified React Application (`frontend/`)

The React frontend serves both public and authenticated users:
- **URL**: `domain.com` (production) or `http://localhost:5173` (local)
- **Technology**: React + Vite with TanStack Router & Query
- **Auto-generated API Client**: Type-safe client from OpenAPI spec

### Route Structure

#### Public Routes (`_public/`)
- **Access**: All visitors (no authentication required)
- **Layout**: Public header with login/signup, footer with links
- **Routes**:
  - `/` - Home page with features and CTAs
  - `/races` - Browse and search races
  - `/about` - About the platform
  - `/login` - Login page
  - `/signup` - Registration page

#### Protected Routes (`_layout/`)
- **Access**: Authenticated users only (redirects to login if not authenticated)
- **Layout**: Dashboard sidebar, user menu
- **Routes by Role**:
  - **Admin**: Full access to all features
    - User management (`/admin`)
    - Role management
    - System settings
  - **Organizer**: Race management features
    - Create/edit races
    - Manage registrations
    - View participant lists
  - **Runner**: Personal dashboard
    - Profile management (`/settings`)
    - Race history
    - Register for races
  - **Volunteer**: Race day operations
    - Check-in interface
    - Race information

### API Client Usage

```typescript
import { UsersService, type UserPublic } from "@/client"
import { useQuery } from "@tanstack/react-query"
import useAuth from "@/hooks/useAuth"

function MyComponent() {
  const { user, logout } = useAuth()
  
  // Check user role
  const isAdmin = user?.roles.some(role => role.name === 'admin')
  const isRunner = user?.roles.some(role => role.name === 'runner')
  
  // Use auto-generated API client
  const { data } = useQuery({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
  })
}
```

### Role-Based UI Components

```typescript
import useAuth from "@/hooks/useAuth"

function RoleBasedComponent() {
  const { user } = useAuth()
  
  const hasRole = (roleName: string) =>
    user?.roles.some(role => role.name === roleName) || user?.is_superuser
  
  return (
    <>
      {hasRole("admin") && <AdminPanel />}
      {hasRole("organizer") && <OrganizerDashboard />}
      {hasRole("runner") && <RunnerProfile />}
    </>
  )
}
```

## Initial Setup

When the database is initialized (`python app/initial_data.py`):

1. Four default roles are created
2. First superuser is created from environment variables
3. Admin role is automatically assigned to the superuser

## Migration

The RBAC system was added via Alembic migration:
- Migration file: `backend/app/alembic/versions/5280d245c748_add_rbac_with_roles_and_user_role_.py`
- Creates `role` and `userrolelink` tables
- Run: `alembic upgrade head`

## Environment Variables

Key variables (in `.env` file at project root):
- `PROJECT_NAME` - Application name
- `SECRET_KEY` - JWT signing key
- `POSTGRES_*` - Database connection details
- `FIRST_SUPERUSER*` - Initial admin user
- `SMTP_*` - Email configuration
- `FRONTEND_HOST` - Frontend URL for CORS

## Docker Deployment

The updated `compose.yml` includes two main services:

1. **frontend**: React application serving both public and authenticated routes
2. **backend**: FastAPI API server

To deploy:

```bash
# Development with hot reload
docker compose watch

# Production
docker compose up -d
```

Access points:
- Frontend: `http://localhost:5173` (development) or configured domain (production)
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Best Practices

### 1. Always Use Superuser Override Pattern
```python
# Good
if not current_user.is_superuser and not crud.user_has_role(current_user, "admin"):
    raise HTTPException(...)

# Better (built into dependencies)
AdminUser = Annotated[User, Depends(require_role("admin"))]
```

### 2. Assign Default Roles on Registration
```python
# When creating new user
user = crud.create_user(session=session, user_create=user_in, default_role="runner")
```

### 3. Check Roles in Frontend
```typescript
// Hide/show UI elements based on role
{user?.roles.some(r => r.name === 'admin') && (
  <AdminPanel />
)}
```

### 4. Use Role-Specific Endpoints
- Create separate endpoint groups for different user types
- Use dependencies to enforce access control
- Return appropriate data based on user role

## Testing RBAC

### Create Test Users with Roles

```python
# In tests
user = crud.create_user(session=db, user_create=user_data, default_role="runner")

# Assign additional roles
admin_role = crud.get_role_by_name(session=db, name="admin")
crud.assign_role_to_user(session=db, user=user, role=admin_role)
```

### Test Permission Checks

```python
def test_admin_only_endpoint(client, normal_user_token_headers):
    """Test that non-admin users cannot access admin endpoints."""
    response = client.get("/api/v1/admin-endpoint", headers=normal_user_token_headers)
    assert response.status_code == 403

def test_admin_can_access(client, superuser_token_headers):
    """Test that admin users can access admin endpoints."""
    response = client.get("/api/v1/admin-endpoint", headers=superuser_token_headers)
    assert response.status_code == 200
```

## Future Enhancements

Possible extensions to the RBAC system:

1. **Granular Permissions**: Add permission-level control (e.g., `race.create`, `race.edit`)
2. **Role Hierarchy**: Implement role inheritance
3. **Dynamic Roles**: Allow creating custom roles via API
4. **Audit Logging**: Track role assignments and permission changes
5. **Time-Based Roles**: Temporary role assignments with expiration
6. **Resource-Level Permissions**: Per-resource access control (e.g., edit only owned races)

## Troubleshooting

### User Can't Access Endpoint
1. Check if user has required role: `SELECT * FROM userrolelink WHERE user_id = 'xxx'`
2. Verify role exists: `SELECT * FROM role WHERE name = 'runner'`
3. Check if `is_superuser` should be true
4. Review endpoint dependencies

### Role Not Assigned on Registration
1. Verify default role exists in database
2. Check `create_user` function is called with `default_role` parameter
3. Ensure `init_db` has run to create default roles

### Frontend Not Showing Roles
1. Verify `/api/v1/users/me` returns roles array
2. Check `roles` relationship is loaded in SQLModel query
3. Ensure API client includes roles in User type

## API Examples

### Assign Runner Role to New User

```bash
# Get runner role ID
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/roles/

# Assign role to user
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/roles/{role_id}/assign/{user_id}
```

### Check Current User's Roles

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
```

Response includes `roles` array:
```json
{
  "id": "xxx",
  "email": "user@example.com",
  "full_name": "John Doe",
  "roles": [
    {
      "id": "yyy",
      "name": "runner",
      "description": "Regular user who can register for races"
    }
  ]
}
```
