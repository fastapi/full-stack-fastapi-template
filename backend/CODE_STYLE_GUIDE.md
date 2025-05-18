# Code Style Guide

This document outlines the code style guidelines for the modular monolith architecture.

## General Principles

1. **Consistency**: Follow consistent patterns throughout the codebase
2. **Readability**: Write code that is easy to read and understand
3. **Maintainability**: Write code that is easy to maintain and extend
4. **Testability**: Write code that is easy to test

## Python Style Guidelines

### Imports

1. **Import Order**:
   - Standard library imports first
   - Third-party imports second
   - Application imports third
   - Sort imports alphabetically within each group

   ```python
   # Standard library imports
   import os
   import uuid
   from datetime import datetime
   from typing import Any, Dict, List, Optional

   # Third-party imports
   from fastapi import APIRouter, Depends, HTTPException, status
   from pydantic import EmailStr
   from sqlmodel import Session, select

   # Application imports
   from app.core.config import settings
   from app.core.logging import get_logger
   from app.modules.users.domain.models import UserCreate, UserPublic
   ```

2. **Import Style**:
   - Use absolute imports rather than relative imports
   - Import specific classes and functions rather than entire modules
   - Avoid wildcard imports (`from module import *`)

   ```python
   # Good
   from app.core.config import settings
   
   # Avoid
   from app.core import config
   config.settings
   
   # Bad
   from app.core.config import *
   ```

### Type Hints

1. **Use Type Hints**:
   - Add type hints to all function parameters and return values
   - Use `Optional` for parameters that can be `None`
   - Use `Any` sparingly and only when necessary

   ```python
   def get_user_by_id(user_id: uuid.UUID) -> Optional[User]:
       """Get user by ID."""
       return user_repo.get_by_id(user_id)
   ```

2. **Type Hint Style**:
   - Use `list[str]` instead of `List[str]` (Python 3.9+)
   - Use `dict[str, Any]` instead of `Dict[str, Any]` (Python 3.9+)
   - Use `Optional[str]` instead of `str | None` for clarity

   ```python
   # Good
   def get_items(skip: int = 0, limit: int = 100) -> list[Item]:
       """Get items with pagination."""
       return item_repo.get_multi(skip=skip, limit=limit)
   
   # Avoid
   def get_items(skip: int = 0, limit: int = 100) -> List[Item]:
       """Get items with pagination."""
       return item_repo.get_multi(skip=skip, limit=limit)
   ```

### Docstrings

1. **Docstring Style**:
   - Use Google-style docstrings
   - Include a brief description of the function
   - Document parameters, return values, and exceptions
   - Keep docstrings concise and focused

   ```python
   def create_user(user_create: UserCreate) -> User:
       """
       Create a new user.
       
       Args:
           user_create: User creation data
           
       Returns:
           Created user
           
       Raises:
           ValueError: If user with the same email already exists
       """
       # Implementation
   ```

2. **Module Docstrings**:
   - Include a docstring at the top of each module
   - Describe the purpose and contents of the module

   ```python
   """
   User repository module.
   
   This module provides data access for user-related operations.
   """
   ```

3. **Class Docstrings**:
   - Include a docstring for each class
   - Describe the purpose and behavior of the class

   ```python
   class UserRepository:
       """
       Repository for user-related data access.
       
       This class provides methods for creating, reading, updating,
       and deleting user records in the database.
       """
   ```

### Naming Conventions

1. **General Naming**:
   - Use descriptive names that convey the purpose
   - Avoid abbreviations unless they are widely understood
   - Be consistent with naming across the codebase

2. **Case Conventions**:
   - `snake_case` for variables, functions, methods, and modules
   - `PascalCase` for classes and type variables
   - `UPPER_CASE` for constants
   - `snake_case` for file names

   ```python
   # Variables and functions
   user_id = uuid.uuid4()
   def get_user_by_email(email: str) -> Optional[User]:
       pass
   
   # Classes
   class UserRepository:
       pass
   
   # Constants
   MAX_USERS = 100
   ```

3. **Naming Patterns**:
   - Prefix boolean variables and functions with `is_`, `has_`, `can_`, etc.
   - Use plural names for collections (lists, dictionaries, etc.)
   - Use singular names for individual items

   ```python
   # Boolean variables
   is_active = True
   has_permission = False
   
   # Collections
   users = [user1, user2, user3]
   
   # Individual items
   user = users[0]
   ```

### Code Structure

1. **Function Length**:
   - Keep functions short and focused on a single task
   - Aim for functions that are less than 20 lines
   - Extract complex logic into separate functions

2. **Line Length**:
   - Keep lines under 88 characters (Black default)
   - Use line breaks for long expressions
   - Use parentheses to group long expressions

   ```python
   # Good
   result = (
       very_long_function_name(
           long_argument1,
           long_argument2,
           long_argument3,
       )
   )
   
   # Avoid
   result = very_long_function_name(long_argument1, long_argument2, long_argument3)
   ```

3. **Whitespace**:
   - Use 4 spaces for indentation (no tabs)
   - Add a blank line between logical sections of code
   - Add a blank line between function and class definitions

### Error Handling

1. **Exception Types**:
   - Use specific exception types rather than generic ones
   - Create custom exceptions for domain-specific errors
   - Document exceptions in docstrings

   ```python
   class UserNotFoundError(Exception):
       """Raised when a user is not found."""
       pass
   
   def get_user_by_id(user_id: uuid.UUID) -> User:
       """
       Get user by ID.
       
       Args:
           user_id: User ID
           
       Returns:
           User
           
       Raises:
           UserNotFoundError: If user not found
       """
       user = user_repo.get_by_id(user_id)
       if not user:
           raise UserNotFoundError(f"User with ID {user_id} not found")
       return user
   ```

2. **Error Messages**:
   - Include relevant information in error messages
   - Make error messages actionable
   - Use consistent error message formats

   ```python
   # Good
   raise ValueError(f"User with email {email} already exists")
   
   # Avoid
   raise ValueError("User exists")
   ```

## Module-Specific Guidelines

### Domain Models

1. **Model Structure**:
   - Define base models with common properties
   - Extend base models for specific use cases
   - Use clear and consistent naming

   ```python
   class UserBase(SQLModel):
       """Base user model with common properties."""
       email: str = Field(unique=True, index=True, max_length=255)
       is_active: bool = True
   
   class UserCreate(UserBase):
       """Model for creating a user."""
       password: str = Field(min_length=8, max_length=40)
   
   class UserUpdate(UserBase):
       """Model for updating a user."""
       email: Optional[str] = Field(default=None, max_length=255)
       password: Optional[str] = Field(default=None, min_length=8, max_length=40)
   ```

2. **Field Validation**:
   - Add validation constraints to fields
   - Document validation constraints in docstrings
   - Use consistent validation patterns

   ```python
   class UserCreate(UserBase):
       """Model for creating a user."""
       password: str = Field(
           min_length=8,
           max_length=40,
           description="User password (8-40 characters)",
       )
   ```

### Repositories

1. **Repository Methods**:
   - Include standard CRUD methods (create, read, update, delete)
   - Add domain-specific query methods as needed
   - Use consistent naming and parameter patterns

   ```python
   class UserRepository:
       """Repository for user-related data access."""
       
       def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
           """Get user by ID."""
           return self.session.get(User, user_id)
       
       def get_by_email(self, email: str) -> Optional[User]:
           """Get user by email."""
           statement = select(User).where(User.email == email)
           return self.session.exec(statement).first()
   ```

2. **Error Handling**:
   - Raise specific exceptions for domain-specific errors
   - Document exceptions in docstrings
   - Handle database errors appropriately

   ```python
   def create(self, user: User) -> User:
       """
       Create new user.
       
       Args:
           user: User to create
           
       Returns:
           Created user
           
       Raises:
           ValueError: If user with the same email already exists
       """
       existing_user = self.get_by_email(user.email)
       if existing_user:
           raise ValueError(f"User with email {user.email} already exists")
       
       self.session.add(user)
       self.session.commit()
       self.session.refresh(user)
       return user
   ```

### Services

1. **Service Methods**:
   - Include business logic for domain operations
   - Coordinate repository calls and other services
   - Handle domain-specific validation and rules

   ```python
   class UserService:
       """Service for user-related operations."""
       
       def create_user(self, user_create: UserCreate) -> User:
           """
           Create a new user.
           
           Args:
               user_create: User creation data
               
           Returns:
               Created user
               
           Raises:
               ValueError: If user with the same email already exists
           """
           # Hash the password
           hashed_password = get_password_hash(user_create.password)
           
           # Create the user
           user = User(
               email=user_create.email,
               hashed_password=hashed_password,
               is_active=user_create.is_active,
           )
           
           # Save the user
           created_user = self.user_repo.create(user)
           
           # Publish event
           event = UserCreatedEvent(user_id=created_user.id, email=created_user.email)
           event.publish()
           
           return created_user
   ```

2. **Event Publishing**:
   - Publish domain events for significant state changes
   - Include relevant information in events
   - Document event publishing in docstrings

   ```python
   def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
       """
       Update user.
       
       Args:
           user_id: User ID
           user_update: User update data
           
       Returns:
           Updated user
           
       Raises:
           UserNotFoundError: If user not found
       """
       # Get the user
       user = self.user_repo.get_by_id(user_id)
       if not user:
           raise UserNotFoundError(f"User with ID {user_id} not found")
       
       # Update fields if provided
       update_data = user_update.model_dump(exclude_unset=True)
       for field, value in update_data.items():
           setattr(user, field, value)
       
       # Save the user
       updated_user = self.user_repo.update(user)
       
       # Publish event
       event = UserUpdatedEvent(user_id=updated_user.id)
       event.publish()
       
       return updated_user
   ```

### API Routes

1. **Route Structure**:
   - Group related routes in the same router
   - Use consistent URL patterns
   - Include appropriate HTTP methods and status codes

   ```python
   @router.get("/", response_model=UsersPublic)
   def read_users(
       session: SessionDep,
       current_user: CurrentUser,
       user_service: UserService = Depends(get_user_service),
       skip: int = 0,
       limit: int = 100,
   ) -> Any:
       """
       Retrieve users.
       
       Args:
           session: Database session
           current_user: Current user
           user_service: User service
           skip: Number of records to skip
           limit: Maximum number of records to return
           
       Returns:
           List of users
       """
       users = user_service.get_multi(skip=skip, limit=limit)
       count = user_service.count()
       return user_service.to_public_list(users, count)
   ```

2. **Dependency Injection**:
   - Use FastAPI's dependency injection system
   - Create helper functions for common dependencies
   - Document dependencies in docstrings

   ```python
   def get_user_service(session: SessionDep) -> UserService:
       """
       Get user service.
       
       Args:
           session: Database session
           
       Returns:
           User service
       """
       user_repo = UserRepository(session)
       return UserService(user_repo)
   ```

3. **Error Handling**:
   - Convert domain exceptions to HTTP exceptions
   - Include appropriate status codes and error messages
   - Document error responses in docstrings

   ```python
   @router.get("/{user_id}", response_model=UserPublic)
   def read_user(
       user_id: uuid.UUID,
       session: SessionDep,
       current_user: CurrentUser,
       user_service: UserService = Depends(get_user_service),
   ) -> Any:
       """
       Get user by ID.
       
       Args:
           user_id: User ID
           session: Database session
           current_user: Current user
           user_service: User service
           
       Returns:
           User
           
       Raises:
           HTTPException: If user not found
       """
       try:
           user = user_service.get_by_id(user_id)
           return user_service.to_public(user)
       except UserNotFoundError as e:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
   ```

## Tools and Automation

1. **Code Formatting**:
   - Use [Black](https://black.readthedocs.io/) for code formatting
   - Use [isort](https://pycqa.github.io/isort/) for import sorting
   - Use [Ruff](https://github.com/charliermarsh/ruff) for linting

2. **Type Checking**:
   - Use [mypy](https://mypy.readthedocs.io/) for static type checking
   - Add type hints to all functions and methods
   - Fix type errors before committing code

3. **Pre-commit Hooks**:
   - Use [pre-commit](https://pre-commit.com/) to run checks before committing
   - Configure hooks for formatting, linting, and type checking
   - Fix issues before committing code

## Conclusion

Following these code style guidelines will help maintain a consistent, readable, and maintainable codebase. Remember that the goal is to write code that is easy to understand, modify, and extend, not just code that works.
