# Event System Documentation

This document provides detailed information about the event system used in the modular monolith architecture.

## Overview

The event system enables loose coupling between modules by allowing them to communicate through events rather than direct dependencies. This approach has several benefits:

- **Decoupling**: Modules don't need to know about each other's implementation details
- **Extensibility**: New functionality can be added by subscribing to existing events
- **Testability**: Event handlers can be tested in isolation
- **Maintainability**: Changes to one module don't require changes to other modules

## Core Components

### Event Base Class

All events inherit from the `EventBase` class defined in `app/core/events.py`:

```python
class EventBase(SQLModel):
    """Base class for all events."""
    
    event_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def publish(self) -> None:
        """Publish the event."""
        from app.core.events import publish_event
        publish_event(self)
```

### Event Registry

The event system maintains a registry of event handlers in `app/core/events.py`:

```python
# Event handler registry
_event_handlers: Dict[str, List[Callable]] = {}
```

### Event Handler Decorator

Event handlers are registered using the `event_handler` decorator:

```python
def event_handler(event_type: str) -> Callable:
    """
    Decorator to register an event handler.
    
    Args:
        event_type: Type of event to handle
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        if event_type not in _event_handlers:
            _event_handlers[event_type] = []
        _event_handlers[event_type].append(func)
        logger.info(f"Registered handler {func.__name__} for event {event_type}")
        return func
    return decorator
```

### Event Publishing

Events are published using the `publish_event` function:

```python
def publish_event(event: EventBase) -> None:
    """
    Publish an event.
    
    Args:
        event: Event to publish
    """
    event_type = event.event_type
    logger.info(f"Publishing event {event_type}")
    
    if event_type in _event_handlers:
        for handler in _event_handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling event {event_type} with handler {handler.__name__}: {e}")
                # Continue processing other handlers
    else:
        logger.info(f"No handlers registered for event {event_type}")
```

## Using the Event System

### Defining Events

To define a new event:

1. Create a new class that inherits from `EventBase`
2. Define the `event_type` attribute
3. Add any additional attributes needed for the event
4. Implement the `publish` method

Example:

```python
class UserCreatedEvent(EventBase):
    """Event published when a user is created."""
    event_type: str = "user.created"
    user_id: uuid.UUID
    email: str
    
    def publish(self) -> None:
        """Publish the event."""
        from app.core.events import publish_event
        publish_event(self)
```

### Publishing Events

To publish an event:

1. Create an instance of the event class
2. Call the `publish` method

Example:

```python
def create_user(self, user_create: UserCreate) -> User:
    # Create user logic...
    
    # Publish event
    event = UserCreatedEvent(user_id=user.id, email=user.email)
    event.publish()
    
    return user
```

### Subscribing to Events

To subscribe to an event:

1. Create a function that takes the event as a parameter
2. Decorate the function with `@event_handler("event.type")`
3. Import the handler in the module's `__init__.py` to register it

Example:

```python
@event_handler("user.created")
def handle_user_created(event: UserCreatedEvent) -> None:
    """Handle user created event."""
    logger.info(f"User created: {event.user_id}")
    # Handle the event...
```

## Event Naming Conventions

Events should be named using the format `{entity}.{action}`:

- `user.created`
- `user.updated`
- `user.deleted`
- `item.created`
- `item.updated`
- `item.deleted`
- `email.sent`
- `password.reset`

## Best Practices

### Event Design

- **Keep Events Simple**: Events should contain only the data needed by handlers
- **Include IDs**: Always include entity IDs to allow handlers to fetch more data if needed
- **Use Meaningful Names**: Event names should clearly indicate what happened
- **Version Events**: Consider adding version information for long-lived events

### Event Handlers

- **Keep Handlers Focused**: Each handler should do one thing
- **Handle Errors Gracefully**: Errors in one handler shouldn't affect others
- **Avoid Circular Events**: Be careful not to create circular event chains
- **Document Dependencies**: Clearly document which events a module depends on

### Testing

- **Test Event Publishing**: Verify that events are published when expected
- **Test Event Handlers**: Test handlers in isolation with mock events
- **Test End-to-End**: Test the full event flow in integration tests

## Real-World Examples

### User Registration Flow

1. User registers via API
2. User service creates the user
3. User service publishes `UserCreatedEvent`
4. Email service handles `UserCreatedEvent` and sends welcome email
5. Analytics service handles `UserCreatedEvent` and logs the registration

```python
# User service
def register_user(self, user_register: UserRegister) -> User:
    # Create user
    user = User(
        email=user_register.email,
        full_name=user_register.full_name,
        hashed_password=get_password_hash(user_register.password),
    )
    
    created_user = self.user_repo.create(user)
    
    # Publish event
    event = UserCreatedEvent(user_id=created_user.id, email=created_user.email)
    event.publish()
    
    return created_user

# Email service
@event_handler("user.created")
def send_welcome_email(event: UserCreatedEvent) -> None:
    """Send welcome email to new user."""
    # Get user from database
    user = user_repo.get_by_id(event.user_id)
    
    # Send email
    email_service.send_email(
        email_to=user.email,
        subject="Welcome to our service",
        template_type=EmailTemplateType.NEW_ACCOUNT,
        template_data={"user_name": user.full_name},
    )

# Analytics service
@event_handler("user.created")
def log_user_registration(event: UserCreatedEvent) -> None:
    """Log user registration for analytics."""
    analytics_service.log_event(
        event_type="user_registration",
        user_id=event.user_id,
        timestamp=datetime.utcnow(),
    )
```

### Item Creation Flow

1. User creates an item via API
2. Item service creates the item
3. Item service publishes `ItemCreatedEvent`
4. Notification service handles `ItemCreatedEvent` and notifies relevant users
5. Search service handles `ItemCreatedEvent` and indexes the item

```python
# Item service
def create_item(self, item_create: ItemCreate, owner_id: uuid.UUID) -> Item:
    # Create item
    item = Item(
        title=item_create.title,
        description=item_create.description,
        owner_id=owner_id,
    )
    
    created_item = self.item_repo.create(item)
    
    # Publish event
    event = ItemCreatedEvent(
        item_id=created_item.id,
        title=created_item.title,
        owner_id=created_item.owner_id,
    )
    event.publish()
    
    return created_item

# Notification service
@event_handler("item.created")
def notify_item_creation(event: ItemCreatedEvent) -> None:
    """Notify relevant users about new item."""
    # Get owner's followers
    followers = follower_repo.get_followers(event.owner_id)
    
    # Notify followers
    for follower in followers:
        notification_service.send_notification(
            user_id=follower.id,
            message=f"New item: {event.title}",
            link=f"/items/{event.item_id}",
        )

# Search service
@event_handler("item.created")
def index_item(event: ItemCreatedEvent) -> None:
    """Index item in search engine."""
    # Get item from database
    item = item_repo.get_by_id(event.item_id)
    
    # Index item
    search_service.index_item(
        id=str(item.id),
        title=item.title,
        description=item.description,
        owner_id=str(item.owner_id),
    )
```

## Debugging Events

To debug events, you can use the logger in `app/core/events.py`:

```python
# Add this to your local development settings
import logging
logging.getLogger("app.core.events").setLevel(logging.DEBUG)
```

This will log detailed information about event publishing and handling.
