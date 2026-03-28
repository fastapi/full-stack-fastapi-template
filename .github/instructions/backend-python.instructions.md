---
description: "Instructions for working with FastAPI backend Python files including models, CRUD operations, API routes, and dependencies."
applyTo: "backend/**/*.py"
---

# Backend Python Development Instructions

## FastAPI Backend Patterns

### When working with Models (`backend/app/models.py`)

Always follow the SQLModel pattern with separate classes:

1. **Base Model** - Shared properties:
   ```python
   class ResourceBase(SQLModel):
       name: str = Field(min_length=1, max_length=255)
       description: str | None = Field(default=None, max_length=500)
   ```

2. **Create Model** - Properties for API creation:
   ```python
   class ResourceCreate(ResourceBase):
       # Add any create-specific fields
       pass
   ```

3. **Update Model** - All fields optional:
   ```python
   class ResourceUpdate(SQLModel):
       name: str | None = Field(default=None, max_length=255)
       description: str | None = Field(default=None, max_length=500)
   ```

4. **Table Model** - Database table (use `table=True`):
   ```python
   class Resource(ResourceBase, table=True):
       id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
       created_at: datetime | None = Field(
           default_factory=get_datetime_utc,
           sa_type=DateTime(timezone=True),
       )
       owner_id: uuid.UUID = Field(foreign_key="user.id")
       owner: User = Relationship(back_populates="resources")
   ```

5. **Public Model** - API response (excludes sensitive data):
   ```python
   class ResourcePublic(ResourceBase):
       id: uuid.UUID
       created_at: datetime | None = None
   ```

6. **List Public Model** - Paginated response:
   ```python
   class ResourcesPublic(SQLModel):
       data: list[ResourcePublic]
       count: int
   ```

**Critical Rules:**
- NEVER expose `hashed_password` or sensitive fields in Public models
- Always use `uuid.UUID` type for IDs, not strings
- Use `Field()` for validation (min_length, max_length, unique, index)
- Use `Relationship()` for foreign key relationships
- Include `created_at` timestamp for all table models

### When working with CRUD (`backend/app/crud.py`)

CRUD functions should:

1. **Accept session as parameter**:
   ```python
   def create_resource(*, session: Session, resource_in: ResourceCreate, owner_id: uuid.UUID) -> Resource:
   ```

2. **Use `model_validate()` for creation**:
   ```python
   db_obj = Resource.model_validate(
       resource_in, 
       update={"owner_id": owner_id}
   )
   session.add(db_obj)
   session.commit()
   session.refresh(db_obj)
   return db_obj
   ```

3. **Use `sqlmodel_update()` for updates**:
   ```python
   def update_resource(*, session: Session, db_obj: Resource, resource_in: ResourceUpdate) -> Resource:
       resource_data = resource_in.model_dump(exclude_unset=True)
       db_obj.sqlmodel_update(resource_data)
       session.add(db_obj)
       session.commit()
       session.refresh(db_obj)
       return db_obj
   ```

4. **Always commit and refresh** after database operations

**Critical Rules:**
- Use keyword-only arguments (start with `*`)
- Always get objects before updating them
- Use `exclude_unset=True` to only update provided fields
- Include error handling for database constraints

### When working with API Routes (`backend/app/api/routes/*.py`)

1. **Router setup**:
   ```python
   from fastapi import APIRouter, HTTPException
   from app.api.deps import CurrentUser, SessionDep
   
   router = APIRouter(prefix="/resources", tags=["resources"])
   ```

2. **List endpoint**:
   ```python
   @router.get("/", response_model=ResourcesPublic)
   def read_resources(
       session: SessionDep,
       current_user: CurrentUser,
       skip: int = 0,
       limit: int = 100
   ) -> Any:
       """Retrieve resources."""
       # Superusers see all, users see only their own
       if current_user.is_superuser:
           statement = select(Resource).offset(skip).limit(limit)
       else:
           statement = select(Resource).where(Resource.owner_id == current_user.id)
       resources = session.exec(statement).all()
       count = len(resources)
       return ResourcesPublic(data=resources, count=count)
   ```

3. **Get by ID**:
   ```python
   @router.get("/{id}", response_model=ResourcePublic)
   def read_resource(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
       """Get resource by ID."""
       resource = session.get(Resource, id)
       if not resource:
           raise HTTPException(status_code=404, detail="Resource not found")
       if not current_user.is_superuser and resource.owner_id != current_user.id:
           raise HTTPException(status_code=403, detail="Not enough permissions")
       return resource
   ```

4. **Create**:
   ```python
   @router.post("/", response_model=ResourcePublic)
   def create_resource(
       *, session: SessionDep, current_user: CurrentUser, resource_in: ResourceCreate
   ) -> Any:
       """Create new resource."""
       resource = crud.create_resource(
           session=session, resource_in=resource_in, owner_id=current_user.id
       )
       return resource
   ```

5. **Update**:
   ```python
   @router.put("/{id}", response_model=ResourcePublic)
   def update_resource(
       *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, resource_in: ResourceUpdate
   ) -> Any:
       """Update resource."""
       resource = session.get(Resource, id)
       if not resource:
           raise HTTPException(status_code=404, detail="Resource not found")
       if not current_user.is_superuser and resource.owner_id != current_user.id:
           raise HTTPException(status_code=403, detail="Not enough permissions")
       resource = crud.update_resource(session=session, db_obj=resource, resource_in=resource_in)
       return resource
   ```

6. **Delete**:
   ```python
   @router.delete("/{id}")
   def delete_resource(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
       """Delete resource."""
       resource = session.get(Resource, id)
       if not resource:
           raise HTTPException(status_code=404, detail="Resource not found")
       if not current_user.is_superuser and resource.owner_id != current_user.id:
           raise HTTPException(status_code=403, detail="Not enough permissions")
       session.delete(resource)
       session.commit()
       return Message(message="Resource deleted successfully")
   ```

**Critical Rules:**
- Always specify `response_model` on endpoints
- Use `SessionDep` and `CurrentUser` dependencies
- Check permissions (superuser or ownership)
- Return 404 if not found, 403 if no permission
- Use descriptive docstrings
- For admin-only: `dependencies=[Depends(get_current_active_superuser)]`

### When working with Dependencies (`backend/app/api/deps.py`)

Use `Annotated` for type-safe dependencies:

```python
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

Custom dependencies should:
- Accept other dependencies as parameters
- Raise HTTPException for errors (404, 403, 401)
- Return the dependency value

### Database Queries

Use SQLModel's query patterns:

```python
# Simple select
statement = select(Resource).where(Resource.owner_id == user_id)
resources = session.exec(statement).all()

# With ordering and pagination
statement = (
    select(Resource)
    .where(Resource.owner_id == user_id)
    .order_by(col(Resource.created_at).desc())
    .offset(skip)
    .limit(limit)
)

# Count
count_statement = select(func.count()).select_from(Resource)
count = session.exec(count_statement).one()

# Get by ID
resource = session.get(Resource, id)
```

### Configuration (`backend/app/core/config.py`)

Settings use Pydantic BaseSettings:
- Read from `../.env` file (one level above backend/)
- Use `computed_field` for derived properties
- Use `model_validator` for complex validation
- No hardcoded secrets

### Security Best Practices

1. **Never expose sensitive data** in Public models
2. **Always check permissions** before operations
3. **Use timing-attack prevention** in authentication
4. **Hash passwords** with Argon2 (via `get_password_hash()`)
5. **Validate tokens** with proper error handling
6. **Check ownership** or superuser status for resources

### Import Organization

Order imports as:
1. Standard library
2. Third-party (FastAPI, SQLModel, etc.)
3. Local application imports

```python
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Resource, ResourceCreate, ResourcePublic
```

### Error Handling

Use HTTPException with appropriate status codes:
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 409: Conflict (duplicate resource)
- 500: Internal Server Error (unexpected errors)

### When Adding New Models/Routes

1. Define all model classes in `models.py`
2. Add CRUD functions in `crud.py`
3. Create router file in `api/routes/`
4. Register router in `api/main.py`
5. Create migration: `alembic revision --autogenerate -m "description"`
6. Apply migration: `alembic upgrade head`
7. Write tests in `tests/api/routes/` or `tests/crud/`
8. Regenerate frontend client: `bash scripts/generate-client.sh`
