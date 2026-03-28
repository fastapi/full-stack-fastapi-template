# FastAPI Full-Stack Project Instructions

This workspace uses the [FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template), a production-ready full-stack application with modern Python backend and React frontend, **enhanced with RBAC (Role-Based Access Control) and a separate Next.js runner site**.

## Technology Stack

### Backend (Python/FastAPI)
- **FastAPI**: Modern, high-performance Python web framework
- **SQLModel**: SQL database ORM with Pydantic integration
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migrations
- **JWT**: Token-based authentication
- **RBAC**: Role-based access control with 4 predefined roles
- **Pytest**: Testing framework

### Frontend - Admin Portal (TypeScript/React)
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **TanStack Query**: Data fetching and caching
- **TanStack Router**: Type-safe routing
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Component library
- **Playwright**: End-to-end testing
- **Access**: `dashboard.domain.com` (admin and organizers only)

### Frontend - Runner Site (TypeScript/Next.js)
- **Next.js 15**: React framework with SSR/SSG for SEO
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **App Router**: Next.js 15 app directory
- **Server Components**: For optimal performance
- **Access**: `domain.com` (public + authenticated runners)

## Project Structure

### Backend (`/backend`)
- `app/models.py` - SQLModel database models and Pydantic schemas (includes Role and RBAC)
- `app/crud.py` - CRUD operations including role management
- `app/api/routes/` - API endpoint definitions
  - `roles.py` - Role management endpoints (admin-only)
  - `users.py` - User management with role assignment
  - `items.py` - Example resource endpoints
- `app/api/deps.py` - FastAPI dependencies (auth, database sessions, RBAC)
- `app/core/config.py` - Settings via Pydantic BaseSettings
- `app/core/security.py` - Password hashing and JWT token handling
- `app/core/db.py` - Database engine, session management, and role initialization
- `tests/` - Pytest test suite

### Frontend - Admin Portal (`/frontend`)
- `src/routes/` - TanStack Router route definitions
- `src/components/` - React components (organized by feature)
  - `Admin/` - Admin-specific components
  - `Items/` - Resource management
  - `UserSettings/` - User profile management
- `src/client/` - Auto-generated API client from OpenAPI spec
- `src/hooks/` - Custom React hooks (useAuth, etc.)
- `tests/` - Playwright end-to-end tests
- **Purpose**: Admin dashboard for system management

### Frontend - Runner Site (`/runner-site`)
- `app/` - Next.js 15 app directory
  - `page.tsx` - Home page (public)
  - `login/` - Authentication pages
  - `dashboard/` - Runner dashboard (authenticated)
- `lib/` - Utilities and configurations
  - `api-client.ts` - API client with authentication
  - `auth-context.tsx` - React context for authentication
  - `config.ts` - Environment configuration
- **Purpose**: Public-facing site for runners with SEO optimization

## Key Patterns and Conventions

### RBAC (Role-Based Access Control)

The system includes a comprehensive RBAC system with four predefined roles:

1. **Admin** - Full system access, user and role management
2. **Runner** - Register for races, manage own profile
3. **Organizer** - Create and manage races
4. **Volunteer** - Assist with race operations

#### Using RBAC in Endpoints

```python
from app.api.deps import AdminUser, RunnerUser, require_role, require_any_role
from fastapi import Depends

# Method 1: Predefined dependencies
@router.get("/admin-only")
def admin_endpoint(current_user: AdminUser) -> Any:
    """Only admins can access."""
    return {"message": "Admin access"}

# Method 2: Custom role requirements
@router.get("/staff", dependencies=[Depends(require_any_role(["organizer", "volunteer"]))])
def staff_endpoint() -> Any:
    """Staff members can access."""
    return {"message": "Staff access"}

# Method 3: Manual checking
from app import crud

@router.post("/races")
def create_race(current_user: CurrentUser, race_in: RaceCreate) -> Any:
    if not crud.user_has_any_role(current_user, ["admin", "organizer"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return race
```

**Note**: Users with `is_superuser=True` bypass all role checks.

#### Role Management API

- `GET /api/v1/roles/` - List all roles (admin-only)
- `POST /api/v1/roles/` - Create role (admin-only)
- `POST /api/v1/roles/{role_id}/assign/{user_id}` - Assign role to user
- `DELETE /api/v1/roles/{role_id}/remove/{user_id}` - Remove role from user

For complete RBAC documentation, see [RBAC.md](../RBAC.md).

### Backend Patterns

#### 1. Model Architecture (SQLModel)
Models follow a specific pattern with separate classes for different purposes:
- `*Base` - Shared properties between multiple models (e.g., `UserBase`)
- `*Create` - Properties received via API on creation (includes password)
- `*Update` - Properties for updates (all fields optional)
- `*Public` - Properties returned via API (excludes sensitive data like hashed_password)
- `*` (table=True) - Actual database table model
- `*sPublic` - List response with data array and count

Example:
```python
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    full_name: str | None = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")

class UserPublic(UserBase):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
```

#### 2. CRUD Operations
- Defined in `app/crud.py`
- Accept `session: Session` as parameter
- Use SQLModel's `model_validate()` for creating objects
- Use `sqlmodel_update()` for updating objects
- Always commit and refresh after database operations

```python
def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, 
        update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
```

#### 3. API Routes
- Organized in `app/api/routes/` by resource (users, items, login)
- Use FastAPI's `APIRouter` with prefix and tags
- Leverage dependency injection for common patterns:
  - `SessionDep` - Database session
  - `CurrentUser` - Authenticated user
  - `get_current_active_superuser` - Admin-only endpoints
- Follow RESTful conventions (GET, POST, PUT/PATCH, DELETE)
- Return appropriate response models

```python
@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, 
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100
) -> Any:
    """Retrieve items."""
    # Superusers see all items, regular users see only their own
    if current_user.is_superuser:
        statement = select(Item).offset(skip).limit(limit)
    else:
        statement = select(Item).where(Item.owner_id == current_user.id)
    items = session.exec(statement).all()
    return ItemsPublic(data=items, count=len(items))
```

#### 4. Dependencies (Dependency Injection)
- Defined in `app/api/deps.py`
- Use type annotations with `Annotated` for reusable dependencies
- Common dependencies:
  - `SessionDep` - Database session from connection pool
  - `TokenDep` - JWT token from OAuth2 scheme
  - `CurrentUser` - Authenticated user from token
  - `get_current_active_superuser()` - Admin user verification

```python
SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

#### 5. Authentication & Security
- JWT token-based authentication
- Passwords hashed with Argon2
- Token issued via `/api/v1/login/access-token` endpoint
- Protected routes use `CurrentUser` dependency
- Admin-only routes use `Depends(get_current_active_superuser)`
- Timing attack prevention in authentication (dummy hash comparison)

#### 6. Configuration
- Uses Pydantic `BaseSettings` for environment-based configuration
- Settings loaded from `../.env` file (one level above backend/)
- Database URL computed from individual components
- CORS origins validated and parsed
- Environment-specific behavior (local/staging/production)

#### 7. Database Queries
- Use SQLModel's `select()` for queries
- Use `session.exec()` to execute statements
- Add `.where()` clauses for filtering
- Use `func.count()` for counting records
- Order with `.order_by()`, paginate with `.offset()` and `.limit()`

```python
statement = (
    select(Item)
    .where(Item.owner_id == user_id)
    .order_by(col(Item.created_at).desc())
    .offset(skip)
    .limit(limit)
)
items = session.exec(statement).all()
```

### Frontend Patterns

#### 1. API Client
- Auto-generated from OpenAPI spec using `@hey-api/openapi-ts`
- Located in `src/client/`
- Regenerate with: `bash scripts/generate-client.sh`
- Import from `@/client` for type-safe API calls

#### 2. React Components
- Organized by feature in `src/components/` (Admin, Items, UserSettings, etc.)
- Use shadcn/ui components from `src/components/ui/`
- Functional components with TypeScript
- Use custom hooks from `src/hooks/`

#### 3. Routing
- TanStack Router for type-safe routing
- Route files in `src/routes/`
- Auto-generated route tree in `routeTree.gen.ts`
- Use layouts (`_layout.tsx`) for shared UI structure

#### 4. State Management
- TanStack Query for server state (data fetching, caching, mutations)
- React hooks (useState, useContext) for local state
- Custom hooks for reusable logic (useAuth, useCustomToast)

#### 5. Styling
- Tailwind CSS utility classes
- Theme support via `theme-provider.tsx`
- Dark mode compatible components
- shadcn/ui for pre-built accessible components

## Development Workflow

### Local Development

#### Backend Development
```bash
cd backend
uv sync                          # Install dependencies
source .venv/bin/activate       # Activate virtual environment
fastapi dev app/main.py         # Run development server
```

#### Frontend Development
```bash
cd frontend
bun install                      # Install dependencies
bun run dev                     # Run development server (http://localhost:5173)
```

#### Docker Compose (Recommended)
```bash
docker compose watch            # Start full stack with hot reload
```
Access points:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- Mailcatcher: http://localhost:1080

### Testing

#### Backend Tests
```bash
cd backend
bash scripts/test.sh            # Run all tests
pytest tests/api/               # Run specific test directory
pytest -k "test_name"          # Run specific test
```

#### Frontend Tests
```bash
cd frontend
bun run test:e2e               # Run Playwright tests
```

### Database Migrations

#### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add new field"
```

#### Apply Migrations
```bash
alembic upgrade head
```

### Code Quality

#### Backend Linting/Formatting
```bash
cd backend
bash scripts/format.sh         # Format code with ruff
bash scripts/lint.sh          # Lint code
```

#### Frontend Linting/Formatting
```bash
cd frontend
bun run format                # Format with Biome
bun run lint                  # Lint with Biome
```

## Common Tasks

### Adding a New Backend Feature

1. **Define Models** in `backend/app/models.py`:
   - Create Base, Create, Update, Public, and table models
   - Add relationships if needed
   - Include proper Field validators

2. **Create CRUD Functions** in `backend/app/crud.py`:
   - Add create, read, update, delete functions
   - Use session parameter and proper error handling

3. **Create API Routes** in `backend/app/api/routes/`:
   - Create new router file if needed
   - Define endpoints with proper HTTP methods
   - Use dependencies (SessionDep, CurrentUser)
   - Add response models and docstrings

4. **Register Router** in `backend/app/api/main.py`:
   ```python
   api_router.include_router(your_router.router)
   ```

5. **Create Migration**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add your_feature"
   alembic upgrade head
   ```

6. **Write Tests** in `backend/tests/`:
   - Create test file in appropriate subdirectory
   - Use fixtures from conftest.py
   - Test CRUD operations and API endpoints

7. **Regenerate Frontend Client**:
   ```bash
   bash scripts/generate-client.sh
   ```

### Adding a New Frontend Feature

1. **Create Component** in `frontend/src/components/`:
   - Use TypeScript for type safety
   - Import shadcn/ui components as needed
   - Use TanStack Query for data fetching

2. **Create Route** (if needed) in `frontend/src/routes/`:
   - Define route file with proper exports
   - Use loader for data fetching
   - Handle authentication if required

3. **Use API Client** from `src/client/`:
   - Import generated client functions
   - Wrap in TanStack Query hooks

4. **Write Tests** in `frontend/tests/`:
   - Create Playwright test spec
   - Use auth setup from `auth.setup.ts`
   - Test user interactions and assertions

## File Organization Best Practices

### Backend
- Keep models thin - business logic goes in CRUD functions or services
- One router per resource/feature
- Use deps.py for reusable dependencies
- Put utilities in `app/utils.py`
- Configuration only in `core/config.py`

### Frontend
- Components organized by feature (Admin/, Items/, UserSettings/)
- Shared components in Common/ or ui/
- One route file per page
- Custom hooks in hooks/ directory
- Utilities in lib/ or utils.ts

## Security Considerations

- Never expose `hashed_password` in API responses (use *Public models)
- Always validate user permissions before operations
- Use `CurrentUser` dependency for authenticated endpoints
- Check ownership or superuser status for resource access
- Passwords must be min 8 characters
- JWT tokens expire after 8 days (configurable)
- CORS configured via settings

## Environment Variables

Key variables (in `.env` file at project root):
- `PROJECT_NAME` - Application name
- `SECRET_KEY` - JWT signing key
- `POSTGRES_*` - Database connection details
- `FIRST_SUPERUSER*` - Initial admin user
- `SMTP_*` - Email configuration
- `FRONTEND_HOST` - Frontend URL for CORS

## Common Gotchas

1. **Database Session**: Always use `SessionDep` dependency, never create sessions manually
2. **Model Validation**: Use `model_validate()` for creating and `sqlmodel_update()` for updating
3. **Commit & Refresh**: Always commit changes and refresh objects to get updated data
4. **Response Models**: Specify `response_model` on all endpoints to ensure proper serialization
5. **UUID Types**: Use `uuid.UUID` type, not strings, for ID fields
6. **Frontend Client**: Regenerate after backend API changes
7. **Pre-commit Hooks**: Install with `pre-commit install` to auto-format on commit

## Additional Resources

- Project README: `/README.md`
- Development Guide: `/development.md`
- Contributing: `/CONTRIBUTING.md`
- Backend README: `/backend/README.md`
- Frontend README: `/frontend/README.md`
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLModel Docs: https://sqlmodel.tiangolo.com
- TanStack Query: https://tanstack.com/query
- TanStack Router: https://tanstack.com/router
