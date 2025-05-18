"""
Event system for inter-module communication.

This module provides a simple pub/sub system for communication between modules
without direct dependencies.
"""
import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Type, get_type_hints

from fastapi import FastAPI
from pydantic import BaseModel

# Configure logger
logger = logging.getLogger(__name__)


class EventBase(BaseModel):
    """Base class for all events in the system."""
    event_type: str


# Dictionary mapping event types to sets of handlers
_event_handlers: Dict[str, Set[Callable]] = {}


def publish_event(event: EventBase) -> None:
    """
    Publish an event to all registered handlers.
    
    Args:
        event: Event to publish
    """
    event_type = event.event_type
    handlers = _event_handlers.get(event_type, set())
    
    if not handlers:
        logger.debug(f"No handlers registered for event type: {event_type}")
        return
    
    for handler in handlers:
        try:
            if asyncio.iscoroutinefunction(handler):
                # Create task for async handlers
                asyncio.create_task(handler(event))
            else:
                # Execute sync handlers directly
                handler(event)
        except Exception as e:
            logger.exception(f"Error in event handler for {event_type}: {e}")


def subscribe_to_event(event_type: str, handler: Callable) -> None:
    """
    Subscribe a handler to an event type.
    
    Args:
        event_type: Type of event to subscribe to
        handler: Function to handle the event
    """
    if event_type not in _event_handlers:
        _event_handlers[event_type] = set()
    
    _event_handlers[event_type].add(handler)
    logger.debug(f"Handler {handler.__name__} subscribed to event type: {event_type}")


def unsubscribe_from_event(event_type: str, handler: Callable) -> None:
    """
    Unsubscribe a handler from an event type.
    
    Args:
        event_type: Type of event to unsubscribe from
        handler: Function to unsubscribe
    """
    if event_type in _event_handlers:
        _event_handlers[event_type].discard(handler)
        logger.debug(f"Handler {handler.__name__} unsubscribed from event type: {event_type}")


# Decorators for easier event handling
def event_handler(event_type: str):
    """
    Decorator for event handler functions.
    
    Args:
        event_type: Type of event to handle
    """
    def decorator(func: Callable):
        subscribe_to_event(event_type, func)
        return func
    return decorator


def setup_event_handlers(app: FastAPI) -> None:
    """
    Set up event handlers for application startup and shutdown.
    
    Args:
        app: FastAPI application
    """
    @app.on_event("startup")
    async def startup_event_handlers():
        logger.info("Starting event system")

    @app.on_event("shutdown")
    async def shutdown_event_handlers():
        logger.info("Shutting down event system")
        global _event_handlers
        _event_handlers = {}