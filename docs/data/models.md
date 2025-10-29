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
- `ingestions`: One-to-many with Ingestion (cascade delete)

**Row-Level Security (RLS)**:
✅ **Enabled** - Applied October 29, 2025

**Policies**:
1. **Service role has full access to users** - Backend service (all operations)
2. **Users can read own profile** - Authenticated users (SELECT where id = auth.uid())

**Variants**:
- `UserBase`: Common properties
- `UserCreate`: Registration input (includes password)
- `UserUpdate`: Profile update input (all optional)
- `UserUpdateMe`: Self-update input (limited fields)
- `UserRegister`: Public signup input
- `UserPublic`: API response (excludes sensitive data)
- `UsersPublic`: Paginated list response

### Ingestion (Extraction)

**Purpose**: PDF extraction metadata and processing pipeline tracking

**Table Name**: `ingestions` (matches model name)

**Database Fields**:
- `id`: UUID (primary key, auto-generated)
- `owner_id`: UUID (foreign key to user.id, CASCADE delete, indexed)
- `filename`: str (original filename, max 255 chars, required)
- `file_size`: int (file size in bytes, required)
- `page_count`: int | None (number of PDF pages, nullable for corrupted files)
- `mime_type`: str (MIME type, max 100 chars, typically "application/pdf")
- `status`: ExtractionStatus (pipeline state, default: "UPLOADED")
- `presigned_url`: str (Supabase signed URL, max 2048 chars, 7-day expiry)
- `storage_path`: str (Supabase storage path, max 512 chars)
- `uploaded_at`: datetime (upload timestamp, auto-set, UTC)

**Extraction Status Enum**:
```python
class ExtractionStatus(str, Enum):
    UPLOADED = "UPLOADED"                      # Initial upload complete
    OCR_PROCESSING = "OCR_PROCESSING"          # OCR task in progress
    OCR_COMPLETE = "OCR_COMPLETE"              # OCR completed
    SEGMENTATION_PROCESSING = "SEGMENTATION_PROCESSING"  # Segmentation in progress
    SEGMENTATION_COMPLETE = "SEGMENTATION_COMPLETE"      # Segmentation done
    TAGGING_PROCESSING = "TAGGING_PROCESSING"  # ML tagging in progress
    DRAFT = "DRAFT"                            # Ready for human review
    IN_REVIEW = "IN_REVIEW"                    # Under human review
    APPROVED = "APPROVED"                      # Reviewed and approved
    REJECTED = "REJECTED"                      # Rejected during review
    FAILED = "FAILED"                          # Processing failed
```

**Relationships**:
- `owner`: Many-to-one with User (back_populates="ingestions")

**Variants**:
- `IngestionBase`: Common properties (shared fields)
- `IngestionCreate`: Creation input (not used - file upload instead)
- `Ingestion`: Database model (`table=True`, full schema)
- `IngestionPublic`: API response (excludes `storage_path` for security)
- `IngestionsPublic`: Paginated list response

**Business Rules**:
- Filename limited to 255 characters
- Page count nullable (handles corrupted PDFs gracefully)
- Storage path never exposed in API (security)
- Presigned URLs regenerated on-demand (7-day expiry)
- Cascade delete: User deletion removes all ingestions automatically

**Database Constraints**:
```sql
FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE CASCADE
```

**Indexes** (for query performance):
- `ix_ingestions_owner_id` (B-tree on owner_id, exists)

**Optional Performance Improvements**:
- Add index on `status` for filtering queries
- Add index on `uploaded_at` for date-based sorting
- Add `updated_at` column with auto-update trigger

**Row-Level Security (RLS)**:
✅ **Enabled** - Applied October 29, 2025

**Policies**:
1. **Service role has full access to ingestions** - Backend service (all operations)
2. **Users can view own ingestions** - Authenticated users (SELECT where owner_id = auth.uid())
3. **Users can insert own ingestions** - Authenticated users (INSERT where owner_id = auth.uid())
4. **Users can update own ingestions** - Authenticated users (UPDATE where owner_id = auth.uid())
5. **Users can delete own ingestions** - Authenticated users (DELETE where owner_id = auth.uid())

**RLS Architecture**:
- Backend uses `service_role` key (bypasses RLS for all operations)
- RLS provides defense-in-depth security
- Ready for future direct Supabase client access if needed

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

### One-to-Many Pattern

**User → Items**:
```python
class User(UserBase, table=True):
    items: list["Item"] = Relationship(
        back_populates="owner",
        cascade_delete=True  # ORM-level cascade
    )

class Item(ItemBase, table=True):
    owner_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE"  # DB-level cascade
    )
    owner: User | None = Relationship(back_populates="items")
```

**User → Ingestions**:
```python
class User(UserBase, table=True):
    ingestions: list["Ingestion"] = Relationship(
        back_populates="owner",
        cascade_delete=True  # ORM-level cascade
    )

class Ingestion(IngestionBase, table=True):
    owner_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",  # DB-level cascade
        index=True  # Performance index
    )
    owner: "User" = Relationship(back_populates="ingestions")
```

**Cascade Delete Strategy**:
- **ORM-level** (`cascade_delete=True`): SQLAlchemy handles deletions in Python
- **DB-level** (`ondelete="CASCADE"`): PostgreSQL enforces at database level
- **Best Practice**: Use both for consistency (2025 standard)
- **Effect**: When user deleted, all owned items and ingestions automatically deleted

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

## Supabase Storage

### Storage Buckets

#### 1. `worksheets` (Private)
**Purpose**: Uploaded PDF worksheets from users

**Configuration**:
- File size limit: 25MB
- Allowed MIME types: `application/pdf`
- Privacy: Private (RLS enforced)

**Storage Structure**:
```
worksheets/
  {user_id}/
    {ingestion_id}/
      original.pdf
```

**RLS Policies**:
1. **Service role has full storage access** - Backend service (all operations)
2. **Users can upload worksheets to own folder** - Authenticated users can INSERT PDFs to their own user folder
3. **Users can read own worksheets** - Authenticated users can SELECT from their own folder

#### 2. `extractions` (Private)
**Purpose**: Extracted images and processing artifacts

**Configuration**:
- File size limit: 50MB
- Allowed MIME types: `image/png`, `image/jpeg`, `application/json`
- Privacy: Private (RLS enforced)

**Storage Structure**:
```
extractions/
  {user_id}/
    {ingestion_id}/
      page_{n}.png
      segments/
        segment_{n}.png
      metadata.json
```

**RLS Policies**:
1. **Service role has full storage access** - Backend service (all operations)
2. **Users can read own extractions** - Authenticated users can SELECT from their own folder

**Access Pattern**:
- Backend uses `service_role` key (bypasses storage RLS)
- Presigned URLs generated for frontend access (7-day expiry)
- Storage paths never exposed in API responses

## Best Practices

1. **Never expose sensitive fields** in Public variants
2. **Use UUIDs** for all primary keys
3. **Validate input** with Field constraints
4. **Cascade deletes** for owned relationships
5. **Index frequently queried fields** (email, foreign keys)
6. **Use type hints** throughout (`str | None` for optional)
7. **Enable RLS on all tables** for defense-in-depth security
8. **Use service_role for backend operations** (bypasses RLS, full access)
9. **Generate presigned URLs** for secure frontend file access

## Database State

**Last Synced**: October 29, 2025
**Migration Version**: `16dd7a6f4ff4` (head)
**Tables**: `user`, `ingestions`, `alembic_version`
**RLS Status**: ✅ Enabled on `user` and `ingestions`
**Storage Buckets**: `worksheets` (25MB, PDF only), `extractions` (50MB, images/JSON)

**Migration History**:
```
<base> → e2412789c190  Initialize models
e2412789c190 → 9c0a54914c78  Add VARCHAR length constraints
9c0a54914c78 → d98dd8ec85a3  Convert IDs to UUID
d98dd8ec85a3 → 1a31ce608336  Add CASCADE relationships
1a31ce608336 → 21e0899d3af8  Add ingestions table (remove items)
21e0899d3af8 → 16dd7a6f4ff4  Rename extractions → ingestions (current)
```

**Security**: 1 low-priority warning remaining (`trigger_set_timestamp` search_path)

---

For database schema changes, see [../architecture/overview.md](../architecture/overview.md#database-schema)

For detailed verification reports, see:
- `/DATABASE_SYNC_VERIFICATION_REPORT.md` - Database sync status
- `/RLS_POLICIES_APPLIED.md` - RLS configuration details
- `/TABLE_RENAME_SUMMARY.md` - Table rename documentation
