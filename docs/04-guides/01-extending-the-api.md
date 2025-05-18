# Extending the API

This guide will walk you through the process of extending the API by adding new modules or enhancing existing ones in the modular monolith architecture.

## Creating a New Module

When adding a new feature to the application, you'll typically need to create a new module within the modular architecture. This section provides a step-by-step guide for creating a complete module.

### Step 1: Create the Module Structure

Start by creating the directory structure for your module:

```bash
mkdir -p backend/app/modules/new_module/{api,domain,repository,services}
touch backend/app/modules/new_module/__init__.py
touch backend/app/modules/new_module/api/{__init__.py,dependencies.py,routes.py}
touch backend/app/modules/new_module/domain/{__init__.py,dependencies.py,models.py,events.py}
touch backend/app/modules/new_module/repository/{__init__.py,dependencies.py,new_module_repo.py}
touch backend/app/modules/new_module/services/{__init__.py,dependencies.py,new_module_service.py}
```

### Step 2: Implement the Domain Models

Define your domain models in `domain/models.py`:

```python
import uuid
from typing import List, Optional

from sqlmodel import Field, SQLModel

from app.shared.models import BaseModel


# Base model for common properties
class ItemBase(SQLModel):
    """Base item model with common properties."""
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(gt=0)
    

# Create model (for API input)
class ItemCreate(ItemBase):
    """Model for creating a new item."""
    pass


# Update model (for API input)
class ItemUpdate(SQLModel):
    """Model for updating an item."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[float] = Field(default=None, gt=0)


# Database model
class Item(ItemBase, BaseModel, table=True):
    """Database model for an item."""
    __tablename__ = "item"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")


# Public response model
class ItemPublic(ItemBase):
    """Public item model for API responses."""
    id: uuid.UUID


# List response model
class ItemsPublic(SQLModel):
    """List of public items for API responses."""
    data: List[ItemPublic]
    count: int
```

### Step 3: Implement the Repository

Create the repository for data access in `repository/new_module_repo.py`:

```python
import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.modules.new_module.domain.models import Item
from app.shared.exceptions import NotFoundException


class ItemRepository:
    """Repository for item data access."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def get_by_id(self, item_id: uuid.UUID) -> Item:
        """Get item by ID."""
        item = self.session.get(Item, item_id)
        if not item:
            raise NotFoundException(f"Item with ID {item_id} not found")
        return item

    def get_multi(
        self, *, skip: int = 0, limit: int = 100, owner_id: Optional[uuid.UUID] = None
    ) -> List[Item]:
        """Get multiple items with optional filtering by owner."""
        query = select(Item)
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
        
        query = query.offset(skip).limit(limit)
        return list(self.session.exec(query))

    def count(self, *, owner_id: Optional[uuid.UUID] = None) -> int:
        """Count items with optional filtering by owner."""
        query = select([func.count()]).select_from(Item)
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
        
        return self.session.exec(query).one()

    def create(self, item: Item) -> Item:
        """Create a new item."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, item: Item) -> Item:
        """Update an existing item."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item_id: uuid.UUID) -> None:
        """Delete an item."""
        item = self.get_by_id(item_id)
        self.session.delete(item)
        self.session.commit()
```

### Step 4: Implement the Service

Create the service layer for business logic in `services/new_module_service.py`:

```python
import uuid
from typing import List, Optional

from app.core.logging import get_logger
from app.modules.new_module.domain.models import (
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.modules.new_module.repository.new_module_repo import ItemRepository

# Initialize logger
logger = get_logger("item_service")


class ItemService:
    """Service for item management."""

    def __init__(self, item_repo: ItemRepository):
        """Initialize with repository."""
        self.item_repo = item_repo

    def get_by_id(self, item_id: uuid.UUID) -> Item:
        """Get item by ID."""
        return self.item_repo.get_by_id(item_id)

    def get_multi(
        self, *, skip: int = 0, limit: int = 100, owner_id: Optional[uuid.UUID] = None
    ) -> List[Item]:
        """Get multiple items with optional filtering by owner."""
        return self.item_repo.get_multi(skip=skip, limit=limit, owner_id=owner_id)

    def create_item(self, *, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        """Create a new item."""
        item = Item(
            name=item_in.name,
            description=item_in.description,
            price=item_in.price,
            owner_id=owner_id,
        )
        
        created_item = self.item_repo.create(item)
        logger.info(f"Created item with ID {created_item.id}")
        
        return created_item

    def update_item(
        self, *, item_id: uuid.UUID, item_in: ItemUpdate, owner_id: uuid.UUID
    ) -> Item:
        """Update an item."""
        item = self.get_by_id(item_id)
        
        # Check ownership
        if item.owner_id != owner_id:
            raise ValueError("Item does not belong to this user")
        
        # Update fields
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        updated_item = self.item_repo.update(item)
        logger.info(f"Updated item with ID {updated_item.id}")
        
        return updated_item

    def delete_item(self, *, item_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        """Delete an item."""
        item = self.get_by_id(item_id)
        
        # Check ownership
        if item.owner_id != owner_id:
            raise ValueError("Item does not belong to this user")
        
        self.item_repo.delete(item_id)
        logger.info(f"Deleted item with ID {item_id}")

    # Public model conversions
    
    def to_public(self, item: Item) -> ItemPublic:
        """Convert item to public model."""
        return ItemPublic.model_validate(item)

    def to_public_list(self, items: List[Item], count: int) -> ItemsPublic:
        """Convert list of items to public model."""
        return ItemsPublic(
            data=[self.to_public(item) for item in items],
            count=count,
        )
```

### Step 5: Implement the API Routes

Create the API endpoints in `api/routes.py`:

```python
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.modules.new_module.domain.models import (
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.modules.new_module.repository.new_module_repo import ItemRepository
from app.modules.new_module.services.new_module_service import ItemService
from app.shared.exceptions import NotFoundException
from app.shared.models import Message


# Create router
router = APIRouter(prefix="/items", tags=["items"])


# Dependencies
def get_item_repository(session: SessionDep) -> ItemRepository:
    """Get item repository."""
    return ItemRepository(session)


def get_item_service(
    item_repo: ItemRepository = Depends(get_item_repository),
) -> ItemService:
    """Get item service."""
    return ItemService(item_repo)


# Routes
@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    item_service: ItemService = Depends(get_item_service),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items.
    
    Args:
        current_user: Current user (from token)
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of items
    """
    items = item_service.get_multi(skip=skip, limit=limit)
    count = len(items)  # For simplicity, using length instead of count query
    return item_service.to_public_list(items, count)


@router.get("/me", response_model=ItemsPublic)
def read_own_items(
    session: SessionDep,
    current_user: CurrentUser,
    item_service: ItemService = Depends(get_item_service),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve current user's items.
    
    Args:
        current_user: Current user (from token)
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of user's items
    """
    items = item_service.get_multi(
        skip=skip, limit=limit, owner_id=current_user.id
    )
    count = len(items)
    return item_service.to_public_list(items, count)


@router.post("/", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Create new item.
    
    Args:
        current_user: Current user (from token)
        item_in: Item creation data
        
    Returns:
        Created item
    """
    item = item_service.create_item(item_in=item_in, owner_id=current_user.id)
    return item_service.to_public(item)


@router.get("/{item_id}", response_model=ItemPublic)
def read_item(
    item_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Get item by ID.
    
    Args:
        item_id: Item ID
        current_user: Current user (from token)
        
    Returns:
        Item
    """
    try:
        item = item_service.get_by_id(item_id)
        return item_service.to_public(item)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{item_id}", response_model=ItemPublic)
def update_item(
    *,
    item_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Update item.
    
    Args:
        item_id: Item ID
        current_user: Current user (from token)
        item_in: Item update data
        
    Returns:
        Updated item
    """
    try:
        item = item_service.update_item(
            item_id=item_id, item_in=item_in, owner_id=current_user.id
        )
        return item_service.to_public(item)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{item_id}", response_model=Message)
def delete_item(
    item_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Delete item.
    
    Args:
        item_id: Item ID
        current_user: Current user (from token)
        
    Returns:
        Success message
    """
    try:
        item_service.delete_item(item_id=item_id, owner_id=current_user.id)
        return Message(message="Item deleted successfully")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
```

### Step 6: Configure Module Initialization

Set up the module initialization in `__init__.py`:

```python
"""
Items module initialization.

This module handles item management.
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger

# Initialize logger
logger = get_logger("items")


def init_items_module(app: FastAPI) -> None:
    """
    Initialize items module.

    This function registers all routes and initializes the module.

    Args:
        app: FastAPI application
    """
    # Import here to avoid circular imports
    from app.modules.new_module.api.routes import router as items_router

    # Include the router in the application
    app.include_router(items_router, prefix=settings.API_V1_STR)

    logger.info("Items module initialized")
```

### Step 7: Register the Module

Update the main API initialization file (`app/api/main.py`) to include your new module:

```python
# Import the module initialization function
from app.modules.new_module import init_items_module

def init_api_routes(app: FastAPI) -> None:
    """Initialize API routes."""
    # ... existing modules
    
    # Initialize your new module
    init_items_module(app)
    
    # ... other initialization code
```

### Step 8: Create a Migration

After adding your new model, create a database migration:

```bash
# Using Docker Compose
docker compose exec backend bash -c "alembic revision --autogenerate -m 'add_item_model'"

# Local development
cd backend
alembic revision --autogenerate -m "add_item_model"
```

Apply the migration:

```bash
# Using Docker Compose
docker compose exec backend bash -c "alembic upgrade head"

# Local development
cd backend
alembic upgrade head
```

### Step 9: Write Tests

Create tests for your new module in `backend/tests/modules/new_module/`:

```python
# tests/modules/new_module/services/test_item_service.py
import uuid
from unittest.mock import MagicMock

import pytest

from app.modules.new_module.domain.models import ItemCreate, ItemUpdate
from app.modules.new_module.repository.new_module_repo import ItemRepository
from app.modules.new_module.services.new_module_service import ItemService


def test_create_item():
    # Arrange
    item_repo = MagicMock(spec=ItemRepository)
    service = ItemService(item_repo)
    
    owner_id = uuid.uuid4()
    item_create = ItemCreate(name="Test Item", price=10.0)
    
    # Act
    service.create_item(item_in=item_create, owner_id=owner_id)
    
    # Assert
    item_repo.create.assert_called_once()
    created_item = item_repo.create.call_args[0][0]
    assert created_item.name == "Test Item"
    assert created_item.price == 10.0
    assert created_item.owner_id == owner_id


def test_update_item():
    # Arrange
    item_repo = MagicMock(spec=ItemRepository)
    service = ItemService(item_repo)
    
    item_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    
    # Mock the get_by_id method
    mock_item = MagicMock()
    mock_item.id = item_id
    mock_item.owner_id = owner_id
    item_repo.get_by_id.return_value = mock_item
    
    item_update = ItemUpdate(name="Updated Item")
    
    # Act
    service.update_item(item_id=item_id, item_in=item_update, owner_id=owner_id)
    
    # Assert
    item_repo.update.assert_called_once()
    assert mock_item.name == "Updated Item"


def test_update_item_wrong_owner():
    # Arrange
    item_repo = MagicMock(spec=ItemRepository)
    service = ItemService(item_repo)
    
    item_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    different_owner_id = uuid.uuid4()
    
    # Mock the get_by_id method
    mock_item = MagicMock()
    mock_item.id = item_id
    mock_item.owner_id = owner_id
    item_repo.get_by_id.return_value = mock_item
    
    item_update = ItemUpdate(name="Updated Item")
    
    # Act and Assert
    with pytest.raises(ValueError):
        service.update_item(
            item_id=item_id, item_in=item_update, owner_id=different_owner_id
        )
```

## Adding Events to an Existing Module

Events allow different modules to communicate without direct dependencies. Here's how to add an event to an existing module:

### Step 1: Define the Event

Create or update an `events.py` file in your module's domain directory:

```python
# app/modules/new_module/domain/events.py
import uuid
from typing import Optional

from app.core.events import EventBase, publish_event


class ItemCreatedEvent(EventBase):
    """Event emitted when a new item is created."""
    event_type: str = "item.created"
    item_id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    
    def publish(self) -> None:
        """Publish this event to all registered handlers."""
        publish_event(self)


class ItemUpdatedEvent(EventBase):
    """Event emitted when an item is updated."""
    event_type: str = "item.updated"
    item_id: uuid.UUID
    owner_id: uuid.UUID
    
    def publish(self) -> None:
        """Publish this event to all registered handlers."""
        publish_event(self)
```

### Step 2: Update the Service to Publish Events

Modify your service to publish events:

```python
# app/modules/new_module/services/new_module_service.py
from app.modules.new_module.domain.events import ItemCreatedEvent, ItemUpdatedEvent

# In the create_item method
def create_item(self, *, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item."""
    # ... existing code
    
    created_item = self.item_repo.create(item)
    
    # Publish event
    event = ItemCreatedEvent(
        item_id=created_item.id,
        name=created_item.name,
        owner_id=created_item.owner_id,
    )
    event.publish()
    
    return created_item

# In the update_item method
def update_item(self, *, item_id: uuid.UUID, item_in: ItemUpdate, owner_id: uuid.UUID) -> Item:
    """Update an item."""
    # ... existing code
    
    updated_item = self.item_repo.update(item)
    
    # Publish event
    event = ItemUpdatedEvent(
        item_id=updated_item.id,
        owner_id=updated_item.owner_id,
    )
    event.publish()
    
    return updated_item
```

### Step 3: Create an Event Handler in Another Module

Create an event handler in a module that needs to react to these events:

```python
# app/modules/notifications/services/notification_event_handlers.py
from app.core.events import event_handler
from app.core.logging import get_logger
from app.modules.new_module.domain.events import ItemCreatedEvent
from app.modules.notifications.services.notification_service import get_notification_service

logger = get_logger("notification_event_handlers")


@event_handler("item.created")
def handle_item_created_event(event: ItemCreatedEvent) -> None:
    """
    Handle item created event by sending notification to owner.
    
    Args:
        event: Item created event
    """
    logger.info(f"Handling item.created event for item {event.item_id}")
    
    notification_service = get_notification_service()
    
    notification_service.send_notification(
        user_id=event.owner_id,
        message=f"Your item '{event.name}' has been created successfully",
        reference_id=str(event.item_id),
        reference_type="item",
    )
```

### Step 4: Register the Event Handler

Make sure the event handler is imported during module initialization:

```python
# app/modules/notifications/__init__.py
def init_notifications_module(app: FastAPI) -> None:
    """Initialize notifications module."""
    # Import here to avoid circular imports
    from app.modules.notifications.api.routes import router as notifications_router
    
    # Include the router in the application
    app.include_router(notifications_router, prefix=settings.API_V1_STR)
    
    # Import event handlers to register them
    from app.modules.notifications.services import notification_event_handlers
    
    logger.info("Notifications module initialized")
```

## Best Practices for Module Development

### 1. Keep Modules Focused

Each module should represent a specific business domain and have a clear responsibility.

### 2. Use Events for Cross-Module Communication

Prefer events over direct imports between modules to maintain loose coupling.

### 3. Follow the Layered Architecture

Respect the layered architecture within each module:
- Domain layer defines what is
- Repository layer handles data access
- Service layer contains business logic
- API layer exposes endpoints

### 4. Keep Dependencies Clean

- Use dependency injection
- Avoid circular dependencies
- Import module-level dependencies locally to avoid cyclic imports

### 5. Add Comprehensive Tests

Write tests for all layers:
- Unit tests for services
- Integration tests for repositories
- API tests for endpoints

### 6. Document Public APIs

Add clear docstrings to all public methods and API endpoints.

## When to Create a New Module

Create a new module when:

1. The feature represents a distinct business domain
2. The feature has its own data models and business logic
3. The feature could potentially be extracted into a separate service in the future
4. The feature has a clear boundary with the rest of the application

Examples of good candidates for separate modules:
- User management (already a module)
- Authentication (already a module)
- Product catalog
- Shopping cart
- Orders
- Payments
- Notifications
- Analytics

## When to Extend an Existing Module

Extend an existing module when:

1. The new feature is closely related to an existing domain
2. The feature shares most of its data models with an existing module
3. The feature would have many direct dependencies on an existing module

Examples:
- Adding user preferences to the users module
- Adding payment methods to a payments module
- Adding item categories to an items module