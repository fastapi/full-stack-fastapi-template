# Extending the Modular Monolith Architecture

This guide explains how to extend the modular monolith architecture by adding new modules or enhancing existing ones.

## Creating a New Module

### 1. Create the Module Structure

Create a new directory for your module under `app/modules/` with the following structure:

```
app/modules/{module_name}/
├── __init__.py           # Module initialization
├── api/                  # API layer
│   ├── __init__.py
│   ├── dependencies.py   # Module-specific dependencies
│   └── routes.py         # API endpoints
├── domain/               # Domain layer
│   ├── __init__.py
│   ├── events.py         # Domain events
│   └── models.py         # Domain models
├── repository/           # Data access layer
│   ├── __init__.py
│   └── {module}_repo.py  # Repository implementation
└── services/             # Business logic layer
    ├── __init__.py
    └── {module}_service.py  # Service implementation
```

### 2. Implement the Module Components

#### Module Initialization

In `app/modules/{module_name}/__init__.py`:

```python
"""
{Module name} module initialization.

This module handles {module description}.
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger

# Initialize logger
logger = get_logger("{module_name}")


def init_{module_name}_module(app: FastAPI) -> None:
    """
    Initialize {module name} module.

    This function registers all routes and initializes the module.

    Args:
        app: FastAPI application
    """
    # Import here to avoid circular imports
    from app.modules.{module_name}.api.routes import router as {module_name}_router

    # Include the router in the application
    app.include_router({module_name}_router, prefix=settings.API_V1_STR)

    logger.info("{Module name} module initialized")
```

#### Domain Models

In `app/modules/{module_name}/domain/models.py`:

```python
"""
{Module name} domain models.

This module contains domain models related to {module description}.
"""
import uuid
from typing import List, Optional

from sqlmodel import Field, SQLModel

from app.shared.models import BaseModel


# Define your models here
class {Entity}Base(SQLModel):
    """Base {entity} model with common properties."""
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class {Entity}Create({Entity}Base):
    """Model for creating a {entity}."""
    pass


class {Entity}Update({Entity}Base):
    """Model for updating a {entity}."""
    name: Optional[str] = Field(default=None, max_length=255)  # type: ignore
    description: Optional[str] = Field(default=None, max_length=255)


class {Entity}({Entity}Base, BaseModel, table=True):
    """Database model for a {entity}."""
    __tablename__ = "{entity_lowercase}"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class {Entity}Public({Entity}Base):
    """Public {entity} model for API responses."""
    id: uuid.UUID


class {Entity}sPublic(SQLModel):
    """List of public {entity}s for API responses."""
    data: List[{Entity}Public]
    count: int
```

#### Repository

In `app/modules/{module_name}/repository/{module_name}_repo.py`:

```python
"""
{Module name} repository.

This module provides data access for {module description}.
"""
import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.modules.{module_name}.domain.models import {Entity}
from app.shared.exceptions import NotFoundException


class {Module}Repository:
    """Repository for {module description}."""

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: Database session
        """
        self.session = session

    def get_by_id(self, {entity}_id: uuid.UUID) -> {Entity}:
        """
        Get {entity} by ID.

        Args:
            {entity}_id: {Entity} ID

        Returns:
            {Entity}

        Raises:
            NotFoundException: If {entity} not found
        """
        {entity} = self.session.get({Entity}, {entity}_id)
        if not {entity}:
            raise NotFoundException(f"{Entity} with ID {{{entity}_id}} not found")
        return {entity}

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[{Entity}]:
        """
        Get multiple {entity}s.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of {entity}s
        """
        statement = select({Entity}).offset(skip).limit(limit)
        return list(self.session.exec(statement))

    def count(self) -> int:
        """
        Count total {entity}s.

        Returns:
            Total count
        """
        statement = select([count()]).select_from({Entity})
        return self.session.exec(statement).one()

    def create(self, {entity}: {Entity}) -> {Entity}:
        """
        Create new {entity}.

        Args:
            {entity}: {Entity} to create

        Returns:
            Created {entity}
        """
        self.session.add({entity})
        self.session.commit()
        self.session.refresh({entity})
        return {entity}

    def update(self, {entity}: {Entity}) -> {Entity}:
        """
        Update {entity}.

        Args:
            {entity}: {Entity} to update

        Returns:
            Updated {entity}
        """
        self.session.add({entity})
        self.session.commit()
        self.session.refresh({entity})
        return {entity}

    def delete(self, {entity}_id: uuid.UUID) -> None:
        """
        Delete {entity}.

        Args:
            {entity}_id: {Entity} ID

        Raises:
            NotFoundException: If {entity} not found
        """
        {entity} = self.get_by_id({entity}_id)
        self.session.delete({entity})
        self.session.commit()
```

#### Service

In `app/modules/{module_name}/services/{module_name}_service.py`:

```python
"""
{Module name} service.

This module provides business logic for {module description}.
"""
import uuid
from typing import List, Optional

from app.core.logging import get_logger
from app.modules.{module_name}.domain.models import (
    {Entity},
    {Entity}Create,
    {Entity}Public,
    {Entity}sPublic,
    {Entity}Update,
)
from app.modules.{module_name}.repository.{module_name}_repo import {Module}Repository
from app.shared.exceptions import NotFoundException

# Initialize logger
logger = get_logger("{module_name}_service")


class {Module}Service:
    """Service for {module description}."""

    def __init__(self, {module_name}_repo: {Module}Repository):
        """
        Initialize service with repository.

        Args:
            {module_name}_repo: {Module} repository
        """
        self.{module_name}_repo = {module_name}_repo

    def get_by_id(self, {entity}_id: uuid.UUID) -> {Entity}:
        """
        Get {entity} by ID.

        Args:
            {entity}_id: {Entity} ID

        Returns:
            {Entity}

        Raises:
            NotFoundException: If {entity} not found
        """
        return self.{module_name}_repo.get_by_id({entity}_id)

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[{Entity}]:
        """
        Get multiple {entity}s.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of {entity}s
        """
        return self.{module_name}_repo.get_multi(skip=skip, limit=limit)

    def create_{entity}(self, {entity}_create: {Entity}Create) -> {Entity}:
        """
        Create new {entity}.

        Args:
            {entity}_create: {Entity} creation data

        Returns:
            Created {entity}
        """
        # Create {entity}
        {entity} = {Entity}(
            name={entity}_create.name,
            description={entity}_create.description,
        )

        created_{entity} = self.{module_name}_repo.create({entity})
        logger.info(f"Created {entity} with ID {created_{entity}.id}")

        return created_{entity}

    def update_{entity}(
        self, {entity}_id: uuid.UUID, {entity}_update: {Entity}Update
    ) -> {Entity}:
        """
        Update {entity}.

        Args:
            {entity}_id: {Entity} ID
            {entity}_update: {Entity} update data

        Returns:
            Updated {entity}

        Raises:
            NotFoundException: If {entity} not found
        """
        {entity} = self.get_by_id({entity}_id)

        # Update fields if provided
        update_data = {entity}_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr({entity}, field, value)

        updated_{entity} = self.{module_name}_repo.update({entity})
        logger.info(f"Updated {entity} with ID {updated_{entity}.id}")

        return updated_{entity}

    def delete_{entity}(self, {entity}_id: uuid.UUID) -> None:
        """
        Delete {entity}.

        Args:
            {entity}_id: {Entity} ID

        Raises:
            NotFoundException: If {entity} not found
        """
        self.{module_name}_repo.delete({entity}_id)
        logger.info(f"Deleted {entity} with ID {{{entity}_id}}")

    # Public model conversions

    def to_public(self, {entity}: {Entity}) -> {Entity}Public:
        """
        Convert {entity} to public model.

        Args:
            {entity}: {Entity} to convert

        Returns:
            Public {entity}
        """
        return {Entity}Public.model_validate({entity})

    def to_public_list(self, {entity}s: List[{Entity}], count: int) -> {Entity}sPublic:
        """
        Convert list of {entity}s to public model.

        Args:
            {entity}s: {Entity}s to convert
            count: Total count

        Returns:
            Public {entity}s list
        """
        return {Entity}sPublic(
            data=[self.to_public({entity}) for {entity} in {entity}s],
            count=count,
        )
```

#### API Routes

In `app/modules/{module_name}/api/routes.py`:

```python
"""
{Module name} API routes.

This module provides API endpoints for {module description}.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.modules.{module_name}.domain.models import (
    {Entity}Create,
    {Entity}Public,
    {Entity}sPublic,
    {Entity}Update,
)
from app.modules.{module_name}.repository.{module_name}_repo import {Module}Repository
from app.modules.{module_name}.services.{module_name}_service import {Module}Service
from app.shared.exceptions import NotFoundException
from app.shared.models import Message

# Create router
router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])


# Dependencies
def get_{module_name}_service(session: SessionDep) -> {Module}Service:
    """
    Get {module name} service.

    Args:
        session: Database session

    Returns:
        {Module} service
    """
    {module_name}_repo = {Module}Repository(session)
    return {Module}Service({module_name}_repo)


# Routes
@router.get("/", response_model={Entity}sPublic)
def read_{entity}s(
    session: SessionDep,
    current_user: CurrentUser,
    {module_name}_service: {Module}Service = Depends(get_{module_name}_service),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve {entity}s.

    Args:
        session: Database session
        current_user: Current user
        {module_name}_service: {Module} service
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of {entity}s
    """
    {entity}s = {module_name}_service.get_multi(skip=skip, limit=limit)
    count = len({entity}s)  # For simplicity, using length instead of count query
    return {module_name}_service.to_public_list({entity}s, count)


@router.post("/", response_model={Entity}Public, status_code=status.HTTP_201_CREATED)
def create_{entity}(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    {entity}_in: {Entity}Create,
    {module_name}_service: {Module}Service = Depends(get_{module_name}_service),
) -> Any:
    """
    Create new {entity}.

    Args:
        session: Database session
        current_user: Current user
        {entity}_in: {Entity} creation data
        {module_name}_service: {Module} service

    Returns:
        Created {entity}
    """
    {entity} = {module_name}_service.create_{entity}({entity}_in)
    return {module_name}_service.to_public({entity})


@router.get("/{{{entity}_id}}", response_model={Entity}Public)
def read_{entity}(
    {entity}_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    {module_name}_service: {Module}Service = Depends(get_{module_name}_service),
) -> Any:
    """
    Get {entity} by ID.

    Args:
        {entity}_id: {Entity} ID
        session: Database session
        current_user: Current user
        {module_name}_service: {Module} service

    Returns:
        {Entity}

    Raises:
        HTTPException: If {entity} not found
    """
    try:
        {entity} = {module_name}_service.get_by_id({entity}_id)
        return {module_name}_service.to_public({entity})
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{{{entity}_id}}", response_model={Entity}Public)
def update_{entity}(
    *,
    {entity}_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    {entity}_in: {Entity}Update,
    {module_name}_service: {Module}Service = Depends(get_{module_name}_service),
) -> Any:
    """
    Update {entity}.

    Args:
        {entity}_id: {Entity} ID
        session: Database session
        current_user: Current user
        {entity}_in: {Entity} update data
        {module_name}_service: {Module} service

    Returns:
        Updated {entity}

    Raises:
        HTTPException: If {entity} not found
    """
    try:
        {entity} = {module_name}_service.update_{entity}({entity}_id, {entity}_in)
        return {module_name}_service.to_public({entity})
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{{{entity}_id}}", response_model=Message)
def delete_{entity}(
    {entity}_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    {module_name}_service: {Module}Service = Depends(get_{module_name}_service),
) -> Any:
    """
    Delete {entity}.

    Args:
        {entity}_id: {Entity} ID
        session: Database session
        current_user: Current user
        {module_name}_service: {Module} service

    Returns:
        Success message

    Raises:
        HTTPException: If {entity} not found
    """
    try:
        {module_name}_service.delete_{entity}({entity}_id)
        return Message(message=f"{Entity} deleted successfully")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### 3. Register the Module

In `app/api/main.py`, import and initialize your module:

```python
from app.modules.{module_name} import init_{module_name}_module

def init_api_routes(app: FastAPI) -> None:
    # ... existing code ...

    # Initialize your module
    init_{module_name}_module(app)

    # ... existing code ...
```

### 4. Create Tests

Create tests for your module in the `tests/modules/{module_name}/` directory, following the same structure as the module.

## Enhancing Existing Modules

To add functionality to an existing module:

1. **Add Domain Models**: Add new models to the module's `domain/models.py` file.
2. **Add Repository Methods**: Add new methods to the module's repository.
3. **Add Service Methods**: Add new business logic to the module's service.
4. **Add API Endpoints**: Add new endpoints to the module's `api/routes.py` file.
5. **Add Tests**: Add tests for the new functionality.

## Adding Cross-Module Communication

To enable communication between modules:

1. **Define Events**: Create event classes in the source module's `domain/events.py` file.
2. **Publish Events**: Publish events from the source module's services.
3. **Subscribe to Events**: Create event handlers in the target module's services.
4. **Register Handlers**: Import the handlers in the target module's `__init__.py` file.

## Best Practices

1. **Maintain Module Boundaries**: Keep module code within its directory structure.
2. **Use Dependency Injection**: Inject dependencies rather than importing them directly.
3. **Follow Layered Architecture**: Respect the layered architecture within each module.
4. **Document Your Code**: Add docstrings to all classes and methods.
5. **Write Tests**: Create tests for all new functionality.
6. **Use Events for Cross-Module Communication**: Avoid direct imports between modules.
