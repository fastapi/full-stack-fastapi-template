# Data Models

## Model Architecture

SQLModel combines Pydantic and SQLAlchemy for unified data models.

## Model Patterns

Each entity follows a pattern with multiple model variants:

```python
# 1. Base - Shared properties
class UserBase(SQLModel):
    email: EmailStr
    is_active: bool = True
    # ... common fields

# 2. Create - API input for creation
class UserCreate(UserBase):
    password: str  # Additional required fields

# 3. Update - API input for updates
class UserUpdate(UserBase):
    email: EmailStr | None  # All fields optional

# 4. Database - Actual table
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str  # Sensitive fields
    items: list["Item"] = Relationship(...)

# 5. Public - API output
class UserPublic(UserBase):
    id: uuid.UUID  # No sensitive fields
```

## Core Models

### User

**Purpose**: User accounts and authentication

**Database Fields**:
- `id`: UUID (primary key)
- `email`: EmailStr (unique, indexed)
- `hashed_password`: str (never exposed in API)
- `is_active`: bool (account status)
- `is_superuser`: bool (admin privileges)
- `full_name`: str | None (optional)

**Relationships**:
- `items`: One-to-many with Item (cascade delete)

**Variants**:
- `UserBase`: Common properties
- `UserCreate`: Registration input (includes password)
- `UserUpdate`: Profile update input (all optional)
- `UserUpdateMe`: Self-update input (limited fields)
- `UserRegister`: Public signup input
- `UserPublic`: API response (excludes sensitive data)
- `UsersPublic`: Paginated list response

### Item

**Purpose**: User-owned items (example entity)

**Database Fields**:
- `id`: UUID (primary key)
- `title`: str (1-255 chars, required)
- `description`: str | None (0-255 chars, optional)
- `owner_id`: UUID (foreign key to user, CASCADE)

**Relationships**:
- `owner`: Many-to-one with User

**Variants**:
- `ItemBase`: Common properties
- `ItemCreate`: Creation input
- `ItemUpdate`: Update input (all optional)
- `ItemPublic`: API response
- `ItemsPublic`: Paginated list response

## Validation

Pydantic validation on all models:

```python
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
```

Automatic validation:
- Email format (`EmailStr`)
- String lengths (`min_length`, `max_length`)
- Required vs optional fields
- Type constraints

## Database Relationships

```python
# One-to-many
class User(UserBase, table=True):
    items: list["Item"] = Relationship(
        back_populates="owner",
        cascade_delete=True
    )

class Item(ItemBase, table=True):
    owner_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")
```

**Cascade Delete**: When user deleted, all items deleted automatically.

## Authentication Models

### Token
```python
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
```

### TokenPayload
```python
class TokenPayload(SQLModel):
    sub: str | None = None  # Subject (user ID)
```

## Generic Models

### Message
```python
class Message(SQLModel):
    message: str
```

Used for simple API responses (e.g., "Item deleted successfully").

## Best Practices

1. **Never expose sensitive fields** in Public variants
2. **Use UUIDs** for all primary keys
3. **Validate input** with Field constraints
4. **Cascade deletes** for owned relationships
5. **Index frequently queried fields** (email, foreign keys)
6. **Use type hints** throughout (`str | None` for optional)

---

For database schema changes, see [../architecture/overview.md](../architecture/overview.md#database-schema)
