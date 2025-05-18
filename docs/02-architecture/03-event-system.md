# Event System

The event system is a crucial component of the modular monolith architecture, enabling loose coupling between modules while maintaining clear communication paths.

## Overview

The event system follows a publish-subscribe (pub/sub) pattern:

1. **Publishers** (modules) emit events when something significant happens
2. **Subscribers** (other modules) react to these events without the publisher needing to know about them

This approach has several benefits:

- **Decoupling**: Modules don't need direct dependencies on each other
- **Extensibility**: New functionality can be added by subscribing to existing events
- **Testability**: Event handlers can be tested in isolation
- **Maintainability**: Changes to one module don't require changes to other modules

## Core Components

### EventBase Class

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

The event system maintains a registry of event handlers:

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

## How to Use the Event System

### 1. Define a Domain Event

Create a new event class in your module's `domain/events.py` file:

```python
# app/modules/users/domain/events.py
from app.core.events import EventBase

class UserCreatedEvent(EventBase):
    """Event emitted when a new user is created."""
    event_type: str = "user.created"
    user_id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    
    def publish(self) -> None:
        """Publish this event to all registered handlers."""
        from app.core.events import publish_event
        publish_event(self)
```

### 2. Publish an Event

In your service, create and publish the event when something significant happens:

```python
# app/modules/users/services/user_service.py
def create_user(self, user_create: UserCreate) -> User:
    """Create a new user."""
    # Create the user in the database
    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
    )
    created_user = self.user_repo.create(user)
    
    # Publish the event
    event = UserCreatedEvent(
        user_id=created_user.id,
        email=created_user.email,
        full_name=created_user.full_name,
    )
    event.publish()
    
    return created_user
```

### 3. Create an Event Handler

In the subscribing module, create a handler function:

```python
# app/modules/email/services/email_event_handlers.py
from app.core.events import event_handler
from app.modules.users.domain.events import UserCreatedEvent

@event_handler("user.created")
def handle_user_created_event(event: UserCreatedEvent) -> None:
    """Handle user created event by sending welcome email."""
    email_service = get_email_service()
    email_service.send_new_account_email(
        email_to=event.email,
        username=event.full_name or event.email,
    )
```

### 4. Register the Handler

Import the handler in the module's initialization code to register it:

```python
# app/modules/email/__init__.py
def init_email_module(app: FastAPI) -> None:
    """Initialize email module."""
    # Import here to avoid circular imports
    from app.modules.email.api.routes import router as email_router
    
    # Include the router in the application
    app.include_router(email_router, prefix=settings.API_V1_STR)
    
    # Import event handlers to register them
    from app.modules.email.services import email_event_handlers
    
    logger.info("Email module initialized")
```

## Event Naming Conventions

Events should be named using the format `{entity}.{action}`, where:

- `entity` is the domain entity (e.g., `user`, `item`, `password`)
- `action` is what happened, usually in past tense (e.g., `created`, `updated`, `deleted`)

Examples:

- `user.created`
- `user.updated`
- `user.deleted`
- `item.created`
- `password.reset.requested`
- `email.sent`

## Real-World Examples

### Password Reset Flow

1. User requests password reset via API
2. Auth service generates reset token
3. Auth service publishes `PasswordResetRequested` event
4. Email service handles the event and sends reset email

```python
# Auth Service
def request_password_reset(self, email: str) -> None:
    """Request password reset."""
    user = self.user_repo.get_by_email(email)
    if not user:
        # Don't reveal if user exists
        return
    
    password_reset_token = generate_password_reset_token(email)
    
    # Publish event
    event = PasswordResetRequested(
        email=email,
        token=password_reset_token,
        username=user.full_name or email
    )
    event.publish()

# Email Event Handler
@event_handler("password.reset.requested")
def handle_password_reset_requested_event(event: PasswordResetRequested) -> None:
    """Handle password reset requested event by sending reset email."""
    email_service = get_email_service()
    email_service.send_password_reset_email(
        email_to=event.email,
        username=event.username or event.email,
        token=event.token
    )
```

### Item Creation Flow

1. User creates an item via API
2. Item service creates the item in database
3. Item service publishes `ItemCreated` event
4. Notification service notifies relevant users
5. Search service indexes the new item

## Best Practices

### Event Design

- **Keep Events Simple**: Include only the data needed by handlers
- **Include IDs**: Always include entity IDs to allow handlers to fetch more data if needed
- **Use Meaningful Names**: Event names should clearly indicate what happened
- **Version Events**: Consider adding version information for long-lived events

### Event Handlers

- **Keep Handlers Focused**: Each handler should do one thing
- **Handle Errors Gracefully**: Errors in one handler shouldn't affect others
- **Avoid Circular Events**: Be careful not to create circular event chains
- **Document Dependencies**: Clearly document which events a module depends on

### Performance Considerations

- **Keep Handlers Fast**: Event handlers run synchronously by default
- **Defer Heavy Processing**: For complex operations, consider using a background task
- **Monitor Handler Execution**: Add logging to track handler performance

## Testing Events

### Testing Event Publishing

Test that events are published when expected:

```python
def test_create_user_publishes_event(mocker):
    # Arrange
    user_service = UserService(user_repo_mock)
    publish_mock = mocker.patch("app.core.events.publish_event")
    
    # Act
    user_service.create_user(user_create)
    
    # Assert
    publish_mock.assert_called_once()
    event = publish_mock.call_args[0][0]
    assert isinstance(event, UserCreatedEvent)
    assert event.email == user_create.email
```

### Testing Event Handlers

Test handlers in isolation with mock events:

```python
def test_handle_user_created_event():
    # Arrange
    event = UserCreatedEvent(user_id=uuid.uuid4(), email="test@example.com")
    email_service_mock = mocker.MagicMock()
    mocker.patch("app.modules.email.services.email_event_handlers.get_email_service", 
                 return_value=email_service_mock)
    
    # Act
    handle_user_created_event(event)
    
    # Assert
    email_service_mock.send_new_account_email.assert_called_once_with(
        email_to="test@example.com",
        username="test@example.com"
    )
```

## Debugging Events

The event system logs information about event publishing and handling. To increase logging verbosity:

```python
# Add this to your local development settings
import logging
logging.getLogger("app.core.events").setLevel(logging.DEBUG)
```

## Future Enhancements

Potential future enhancements to the event system:

1. **Asynchronous Event Processing**: Using background tasks for non-blocking event handling
2. **Event Persistence**: Storing events for replay and audit purposes
3. **Event Monitoring**: Dashboards for event frequency and handler performance
4. **Event Versioning**: Formal versioning for event schema evolution

## Next Steps

- Learn about [Shared Components](04-shared-components.md)
- See how to [Implement a New Module](../04-guides/01-extending-the-api.md)