# Frontend Dashboard Architecture (Bottom-Up Design)
## LLM-Powered UI Testing System - Web Dashboard

### Executive Summary

This document outlines a **bottom-up architecture** for a modern web dashboard that provides a user-friendly interface to the LLM-Powered UI Testing System. The architecture follows a progressive enhancement approach, starting with foundational components and building each layer upon the previous one. The system uses React.js frontend with FastAPI backend for modern, high-performance async API development.

---

## 🏗️ Bottom-Up Architecture Philosophy

The architecture follows a **progressive building approach**:

1. **Foundation Layer**: Core data models and FastAPI services
2. **Service Layer**: Business logic and API endpoints  
3. **Integration Layer**: Real-time communication and external systems
4. **Presentation Layer**: React components and user interfaces
5. **Orchestration Layer**: Complete dashboard features

```
┌─────────────────────── LAYER 5: ORCHESTRATION ───────────────────────┐
│                     Complete Dashboard Features                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ Project Mgmt │ │ Test Results │ │ Real-time UI │ │ Admin Panel │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
┌─────────────────────── LAYER 4: PRESENTATION ────────────────────────┐
│                       React.js Frontend Components                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ UI Components│ │ State Mgmt   │ │ Routing      │ │ Bootstrap   │ │
│  │ (TypeScript) │ │ (Redux TK)   │ │ (React Router│ │ (v5.13)     │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
┌─────────────────────── LAYER 3: INTEGRATION ─────────────────────────┐
│                    Real-time & External Integration                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ WebSocket    │ │ File Uploads │ │ Notifications│ │ Task Queue  │ │
│  │ (Socket.IO)  │ │ (Multipart)  │ │ (Real-time)  │ │ (Celery)    │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
┌─────────────────────── LAYER 2: SERVICE ─────────────────────────────┐
│                        FastAPI Business Logic                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ CRUD APIs    │ │ Auth Service │ │ Validation   │ │ Error       │ │
│  │ (Pydantic)   │ │ (JWT/OAuth)  │ │ (Schemas)    │ │ Handling    │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
┌─────────────────────── LAYER 1: FOUNDATION ──────────────────────────┐
│                       Core Data & Infrastructure                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ PostgreSQL   │ │ Redis Cache  │ │ File Storage │ │ Config      │ │
│  │ (SQLAlchemy) │ │ (Sessions)   │ │ (Local/Cloud)│ │ (Environment)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Task Queue     │  │  File Management │  │   Monitoring     │   │
│  │  • Celery       │  │  • Test Outputs  │  │  • System Health │   │
│  │  • Redis        │  │  • Screenshots   │  │  • Performance   │   │
│  │  • Job Status   │  │  • Reports       │  │  • Error Logs    │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ Data Persistence
                               ↓
┌─────────────────────── DATABASE LAYER ───────────────────────────────┐
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   PostgreSQL     │  │      Redis       │  │   File Storage   │   │
│  │  • User Data     │  │  • Cache Layer   │  │  • Test Artifacts│   │
│  │  • Projects      │  │  • Sessions      │  │  • Screenshots   │   │
│  │  • Test History  │  │  • Task Queue    │  │  • Reports       │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Layer 1: Foundation - Core Data Models & Infrastructure

### 1.1 Database Models (SQLAlchemy with FastAPI)

#### Core Entity Models
```python
# models/base.py
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# models/user.py
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    preferences = Column(JSON, default=dict)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    test_runs = relationship("TestRun", back_populates="created_by")

# models/project.py
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    target_url = Column(String, nullable=False)
    max_pages = Column(Integer, default=10)
    max_depth = Column(Integer, default=3)
    frameworks = Column(JSON, default=list)  # ['selenium', 'playwright']
    llm_provider = Column(String, default='openai')  # 'openai', 'anthropic', etc
    llm_model = Column(String, default='gpt-4')
    auth_config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    test_runs = relationship("TestRun", back_populates="project")

# models/test_run.py
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel

class TestStatus(PyEnum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TestRun(BaseModel):
    __tablename__ = "test_runs"
    
    name = Column(String, nullable=False)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    total_pages = Column(Integer, default=0)
    completed_pages = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    config = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    error_message = Column(Text)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    
    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project", back_populates="test_runs")
    created_by = relationship("User", back_populates="test_runs")
    test_cases = relationship("TestCase", back_populates="test_run")

# models/test_case.py
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from .base import BaseModel

class TestCase(BaseModel):
    __tablename__ = "test_cases"
    
    page_url = Column(String, nullable=False)
    test_name = Column(String, nullable=False)
    test_code = Column(Text, nullable=False)
    framework = Column(String, nullable=False)  # 'selenium', 'playwright'
    passed = Column(Boolean)
    error_message = Column(Text)
    execution_time = Column(Float)  # seconds
    screenshot_path = Column(String)
    metadata = Column(JSON, default=dict)
    
    # Foreign Keys
    test_run_id = Column(Integer, ForeignKey("test_runs.id"))
    
    # Relationships
    test_run = relationship("TestRun", back_populates="test_cases")
```

### 1.2 Configuration & Environment Setup

#### Database Configuration
```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

# Database URLs
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost/ui_testing_db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Redis connection
import redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
```

#### Application Settings
```python
# config/settings.py
from pydantic import BaseSettings, Field
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "UI Testing Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        env="ALLOWED_ORIGINS"
    )
    
    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # External Services
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 1.3 File Storage Infrastructure

#### File Management Service
```python
# services/file_storage.py
from pathlib import Path
from typing import Optional, BinaryIO
import os
import uuid
import aiofiles
from fastapi import UploadFile

class FileStorageService:
    def __init__(self, base_path: str = "./uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.base_path / "screenshots").mkdir(exist_ok=True)
        (self.base_path / "reports").mkdir(exist_ok=True)
        (self.base_path / "test_artifacts").mkdir(exist_ok=True)
    
    async def save_file(
        self, 
        file: UploadFile, 
        subfolder: str = "general"
    ) -> str:
        """Save uploaded file and return relative path"""
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create subfolder path
        subfolder_path = self.base_path / subfolder
        subfolder_path.mkdir(exist_ok=True)
        
        # Full file path
        file_path = subfolder_path / unique_filename
        
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Return relative path
        return str(file_path.relative_to(self.base_path))
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get absolute path from relative path"""
        return self.base_path / relative_path
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete file and return success status"""
        try:
            file_path = self.get_file_path(relative_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

# Global instance
file_storage = FileStorageService()
```

---

## ⚡ Layer 2: Service - FastAPI Business Logic

### 2.1 Pydantic Schemas for Data Validation

#### Base Schemas
```python
# schemas/base.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)

class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool
```

#### Core Entity Schemas
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    preferences: Dict[str, Any] = {}

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

# schemas/project.py
from typing import List, Dict, Any

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_url: str = Field(..., regex=r"^https?://")
    max_pages: int = Field(default=10, ge=1, le=1000)
    max_depth: int = Field(default=3, ge=1, le=10)
    frameworks: List[str] = Field(default=["selenium"])
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4")
    auth_config: Dict[str, Any] = Field(default={})
    is_active: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_url: Optional[str] = None
    max_pages: Optional[int] = None
    max_depth: Optional[int] = None
    frameworks: Optional[List[str]] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
```

### 2.2 Authentication Service

#### JWT Authentication
```python
# services/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.settings import settings
from config.database import get_db
from models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for JWT tokens
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# Dependency to get current active user
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

### 2.3 CRUD Services

#### Generic CRUD Base Class
```python
# services/crud_base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.base import BaseModel as DBBaseModel

ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

#### User CRUD Service
```python
# services/crud_user.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from .crud_base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(self.model).filter(User.email == email).first()
    
    def get_multi_superusers(self, db: Session) -> List[User]:
        return db.query(self.model).filter(User.is_superuser == True).all()

user = CRUDUser(User)
```

#### Project CRUD Service
```python
# services/crud_project.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate
from .crud_base import CRUDBase

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        return (
            db.query(self.model)
            .filter(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: ProjectCreate, owner_id: int
    ) -> Project:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_active_projects(
        self, db: Session, *, owner_id: int
    ) -> List[Project]:
        return (
            db.query(self.model)
            .filter(
                Project.owner_id == owner_id,
                Project.is_active == True
            )
            .all()
        )

project = CRUDProject(Project)
```

### 2.4 Error Handling & Validation

#### Custom Exception Classes
```python
# exceptions.py
from fastapi import HTTPException, status

class ProjectNotFoundError(HTTPException):
    def __init__(self, project_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

class TestRunNotFoundError(HTTPException):
    def __init__(self, test_run_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test run with id {test_run_id} not found"
        )

class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action"
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
```

---

## 🔗 Layer 3: Integration - Real-time & External Systems

### 3.1 WebSocket Implementation for Real-time Updates

#### WebSocket Manager
```python
# services/websocket.py
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.user_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.user_connections[websocket] = user_id
    
    def disconnect(self, websocket: WebSocket):
        user_id = self.user_connections.get(websocket)
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        if websocket in self.user_connections:
            del self.user_connections[websocket]
    
    async def send_personal_message(self, message: dict, user_id: int):
        connections = self.active_connections.get(user_id, [])
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                await self.disconnect(connection)
    
    async def send_test_progress_update(
        self, test_run_id: int, progress: float, user_id: int
    ):
        message = {
            "type": "test_progress",
            "test_run_id": test_run_id,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_test_completion(
        self, test_run_id: int, results: dict, user_id: int
    ):
        message = {
            "type": "test_completed",
            "test_run_id": test_run_id,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)

manager = ConnectionManager()
```

### 3.2 Celery Task Queue for Background Processing

#### Celery Configuration
```python
# celery_app.py
from celery import Celery
from config.settings import settings
import os

celery_app = Celery(
    "ui_testing_dashboard",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.test_runner"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)

# Task routing
celery_app.conf.task_routes = {
    "tasks.test_runner.run_ui_tests": {"queue": "test_queue"},
    "tasks.test_runner.generate_test_code": {"queue": "llm_queue"},
}
```

#### Background Test Runner Tasks
```python
# tasks/test_runner.py
from celery import current_task
from celery_app import celery_app
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.test_run import TestRun, TestStatus
from models.test_case import TestCase
from services.websocket import manager
import asyncio
import subprocess
import json

@celery_app.task(bind=True)
def run_ui_tests(self, test_run_id: int, user_id: int):
    """Background task to run UI tests"""
    db = SessionLocal()
    try:
        # Get test run
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            return {"error": "Test run not found"}
        
        # Update status to running
        test_run.status = TestStatus.RUNNING
        test_run.start_time = datetime.utcnow()
        db.commit()
        
        # Notify user via WebSocket
        asyncio.create_task(
            manager.send_test_progress_update(test_run_id, 0.0, user_id)
        )
        
        # Execute the actual testing logic here
        # This would integrate with your existing UI testing system
        project = test_run.project
        config = {
            "target_url": project.target_url,
            "max_pages": project.max_pages,
            "max_depth": project.max_depth,
            "frameworks": project.frameworks,
            "llm_provider": project.llm_provider,
            "llm_model": project.llm_model,
            "auth_config": project.auth_config
        }
        
        # Call your existing UI testing orchestrator
        # This is where you'd integrate with your plan.md system
        results = execute_ui_testing_pipeline(config, test_run_id, user_id)
        
        # Update test run with results
        test_run.status = TestStatus.COMPLETED
        test_run.end_time = datetime.utcnow()
        test_run.results = results
        test_run.completed_pages = results.get("completed_pages", 0)
        test_run.total_tests = results.get("total_tests", 0)
        test_run.passed_tests = results.get("passed_tests", 0)
        test_run.failed_tests = results.get("failed_tests", 0)
        db.commit()
        
        # Final notification
        asyncio.create_task(
            manager.send_test_completion(test_run_id, results, user_id)
        )
        
        return results
        
    except Exception as e:
        # Handle errors
        test_run.status = TestStatus.FAILED
        test_run.error_message = str(e)
        test_run.end_time = datetime.utcnow()
        db.commit()
        
        # Notify user of failure
        asyncio.create_task(
            manager.send_personal_message(
                {
                    "type": "test_failed",
                    "test_run_id": test_run_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                },
                user_id
            )
        )
        
        raise
    finally:
        db.close()

def execute_ui_testing_pipeline(config: dict, test_run_id: int, user_id: int) -> dict:
    """
    This function would integrate with your existing UI testing system
    from plan.md and architecture.md
    """
    # Placeholder for integration with existing system
    # You would call your orchestrator here
    
    # Mock implementation for demonstration
    import time
    import random
    
    total_pages = config["max_pages"]
    results = {
        "completed_pages": 0,
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_cases": []
    }
    
    for page_num in range(total_pages):
        # Simulate progress
        time.sleep(2)  # Simulate work
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": page_num + 1, "total": total_pages}
        )
        
        # Send real-time progress update
        asyncio.create_task(
            manager.send_test_progress_update(test_run_id, progress, user_id)
        )
        
        # Simulate test results
        page_tests = random.randint(3, 8)
        passed = random.randint(int(page_tests * 0.7), page_tests)
        failed = page_tests - passed
        
        results["completed_pages"] += 1
        results["total_tests"] += page_tests
        results["passed_tests"] += passed
        results["failed_tests"] += failed
    
    return results
```

### 3.3 File Upload & Processing

#### File Upload Service
```python
# api/endpoints/files.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from services.file_storage import file_storage
from services.auth import get_current_active_user
from models.user import User
import mimetypes

router = APIRouter()

@router.post("/upload-screenshot/")
async def upload_screenshot(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a screenshot file"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )
    
    # Save file
    file_path = await file_storage.save_file(file, "screenshots")
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "content_type": file.content_type,
        "message": "Screenshot uploaded successfully"
    }

@router.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """Serve uploaded files"""
    abs_file_path = file_storage.get_file_path(file_path)
    
    if not abs_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(str(abs_file_path))
    
    return FileResponse(
        path=abs_file_path,
        media_type=content_type,
        filename=abs_file_path.name
    )
```

---

## 🎨 Layer 4: Presentation - React.js Frontend

### 4.1 Frontend Technology Stack & Setup

#### Project Structure
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── common/             # Generic components
│   │   │   ├── Button/
│   │   │   ├── Modal/
│   │   │   ├── Table/
│   │   │   ├── Form/
│   │   │   ├── Layout/
│   │   │   └── LoadingSpinner/
│   │   ├── dashboard/          # Dashboard-specific components
│   │   │   ├── ProjectCard/
│   │   │   ├── TestResultCard/
│   │   │   ├── ProgressBar/
│   │   │   ├── StatusBadge/
│   │   │   └── QuickActions/
│   │   └── charts/             # Data visualization
│   │       ├── TestResultsChart/
│   │       ├── PerformanceChart/
│   │       └── CoverageChart/
│   ├── pages/                  # Route-level components
│   │   ├── Dashboard/
│   │   ├── Projects/
│   │   ├── TestResults/
│   │   ├── Settings/
│   │   └── Reports/
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   └── useAsync.ts
│   ├── services/               # API service layer
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── projects.ts
│   │   ├── tests.ts
│   │   └── websocket.ts
│   ├── store/                  # Redux store
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── projectsSlice.ts
│   │   │   ├── testsSlice.ts
│   │   │   └── uiSlice.ts
│   │   └── index.ts
│   ├── types/                  # TypeScript definitions
│   │   ├── api.ts
│   │   ├── project.ts
│   │   ├── test.ts
│   │   └── user.ts
│   ├── utils/                  # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   ├── styles/                 # Global styles
│   │   ├── bootstrap-custom.scss
│   │   ├── variables.scss
│   │   ├── components.scss
│   │   └── global.scss
│   ├── App.tsx
│   ├── index.tsx
│   └── setupProxy.js
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js          # If using Tailwind (optional)
```

#### Package.json Dependencies
```json
{
  "name": "ui-testing-dashboard",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@reduxjs/toolkit": "^1.9.1",
    "react-redux": "^8.0.5",
    "@tanstack/react-query": "^4.24.6",
    "axios": "^1.3.3",
    "bootstrap": "^5.3.0",
    "react-bootstrap": "^2.7.0",
    "react-hook-form": "^7.43.0",
    "@hookform/resolvers": "^2.9.10",
    "yup": "^0.32.11",
    "socket.io-client": "^4.6.1",
    "chart.js": "^4.2.1",
    "react-chartjs-2": "^5.2.0",
    "date-fns": "^2.29.3",
    "react-hot-toast": "^2.4.0",
    "lucide-react": "^0.105.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.26",
    "@types/react-dom": "^18.0.9",
    "@typescript-eslint/eslint-plugin": "^5.52.0",
    "@typescript-eslint/parser": "^5.52.0",
    "@vitejs/plugin-react": "^3.1.0",
    "eslint": "^8.33.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.3.4",
    "typescript": "^4.9.3",
    "vite": "^4.1.0",
    "sass": "^1.58.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "jest": "^29.4.1"
  }
}
```

### 4.2 Core React Components (Bottom-Up)

#### Base Component Infrastructure
```typescript
// src/types/api.ts
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface ErrorResponse {
  detail: string;
  type?: string;
}

// src/types/user.ts
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  preferences: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// src/types/project.ts
export interface Project {
  id: number;
  name: string;
  description?: string;
  target_url: string;
  max_pages: number;
  max_depth: number;
  frameworks: string[];
  llm_provider: string;
  llm_model: string;
  auth_config: Record<string, any>;
  is_active: boolean;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  target_url: string;
  max_pages?: number;
  max_depth?: number;
  frameworks?: string[];
  llm_provider?: string;
  llm_model?: string;
  auth_config?: Record<string, any>;
}

// src/types/test.ts
export enum TestStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

export interface TestRun {
  id: number;
  name: string;
  status: TestStatus;
  progress: number;
  total_pages: number;
  completed_pages: number;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  config: Record<string, any>;
  results: Record<string, any>;
  error_message?: string;
  start_time?: string;
  end_time?: string;
  project_id: number;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
}

export interface TestCase {
  id: number;
  page_url: string;
  test_name: string;
  test_code: string;
  framework: string;
  passed?: boolean;
  error_message?: string;
  execution_time?: number;
  screenshot_path?: string;
  metadata: Record<string, any>;
  test_run_id: number;
  created_at: string;
}
```

#### Authentication Service
```typescript
// src/services/auth.ts
import axios from 'axios';
import { LoginRequest, LoginResponse, User } from '../types/user';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class AuthService {
  private tokenKey = 'access_token';
  private userKey = 'user_data';

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const data = response.data;
    
    // Store token and user data
    localStorage.setItem(this.tokenKey, data.access_token);
    localStorage.setItem(this.userKey, JSON.stringify(data.user));
    
    return data;
  }

  async logout(): Promise<void> {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getUser(): User | null {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  async getCurrentUser(): Promise<User> {
    const response = await axios.get(`${API_BASE_URL}/auth/me`);
    const user = response.data;
    localStorage.setItem(this.userKey, JSON.stringify(user));
    return user;
  }
}

export const authService = new AuthService();
```

#### API Service with Axios Interceptors
```typescript
// src/services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { authService } from './auth';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = authService.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          authService.logout();
          window.location.href = '/login';
          toast.error('Session expired. Please login again.');
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.');
        } else if (error.response?.data?.detail) {
          toast.error(error.response.data.detail);
        }
        
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.delete<T>(url, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.patch<T>(url, data, config);
    return response.data;
  }
}

export const apiService = new ApiService();
```
````
This is the description of what the code block changes:
<changeDescription>
Complete the architecture document with Layer 5 (Orchestration), deployment configuration, and implementation timeline
</changeDescription>

This is the code block that represents the suggested code change:
````markdown
---

## 🚀 Layer 5: Orchestration - Complete Dashboard Features

### 5.1 FastAPI Main Application & Router Setup

#### Main FastAPI Application

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from config.database import engine
from models import Base
from api.router import api_router
from api.websocket import websocket_router

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting UI Testing Dashboard API...")
    yield
    # Shutdown
    print("📴 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for LLM-powered UI testing dashboard",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded content
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")

@app.get("/")
async def root():
    return {
        "message": "UI Testing Dashboard API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4
    )
```

#### API Router Configuration

```python
# api/router.py
from fastapi import APIRouter
from api.endpoints import auth, projects, tests, users, files

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tests.router, prefix="/tests", tags=["test-runs"])
api_router.include_router(files.router, prefix="/files", tags=["file-management"])
```

### 5.2 Complete Frontend Application

#### Main App Component with Routing

```typescript
// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { store } from './store';
import { useAuth } from './hooks/useAuth';
import Layout from './components/common/Layout/Layout';

// Pages
import Dashboard from './pages/Dashboard/Dashboard';
import Projects from './pages/Projects/Projects';
import ProjectDetail from './pages/Projects/ProjectDetail';
import TestResults from './pages/TestResults/TestResults';
import TestDetail from './pages/TestResults/TestDetail';
import Settings from './pages/Settings/Settings';
import Login from './pages/Auth/Login';

// Styles
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/global.scss';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="App">
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
            
            <Routes>
              <Route path="/login" element={<Login />} />
              
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Dashboard />} />
                <Route path="projects" element={<Projects />} />
                <Route path="projects/:id" element={<ProjectDetail />} />
                <Route path="tests" element={<TestResults />} />
                <Route path="tests/:id" element={<TestDetail />} />
                <Route path="settings" element={<Settings />} />
              </Route>
              
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </Router>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
```

#### Dashboard Component (Complete Implementation)

```typescript
// src/pages/Dashboard/Dashboard.tsx
import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { Plus, Activity, CheckCircle, XCircle, Clock } from 'lucide-react';

import { projectsService } from '../../services/projects';
import { testsService } from '../../services/tests';
import ProjectCard from '../../components/dashboard/ProjectCard/ProjectCard';
import TestResultCard from '../../components/dashboard/TestResultCard/TestResultCard';
import StatsCard from '../../components/dashboard/StatsCard/StatsCard';
import QuickActions from '../../components/dashboard/QuickActions/QuickActions';
import RecentActivity from '../../components/dashboard/RecentActivity/RecentActivity';

const Dashboard: React.FC = () => {
  const { data: projects } = useQuery({
    queryKey: ['projects', 'dashboard'],
    queryFn: () => projectsService.getProjects({ limit: 6 }),
  });

  const { data: recentTests } = useQuery({
    queryKey: ['tests', 'recent'],
    queryFn: () => testsService.getTestRuns({ limit: 5 }),
  });

  const { data: stats } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => testsService.getDashboardStats(),
  });

  return (
    <Container fluid className="dashboard">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">Dashboard</h1>
        <Button variant="primary" size="sm">
          <Plus size={16} className="me-2" />
          New Project
        </Button>
      </div>

      {/* Stats Overview */}
      <Row className="mb-4">
        <Col md={3}>
          <StatsCard
            title="Total Projects"
            value={stats?.total_projects || 0}
            icon={<Activity />}
            color="primary"
          />
        </Col>
        <Col md={3}>
          <StatsCard
            title="Active Tests"
            value={stats?.active_tests || 0}
            icon={<Clock />}
            color="warning"
          />
        </Col>
        <Col md={3}>
          <StatsCard
            title="Passed Tests"
            value={stats?.passed_tests || 0}
            icon={<CheckCircle />}
            color="success"
          />
        </Col>
        <Col md={3}>
          <StatsCard
            title="Failed Tests"
            value={stats?.failed_tests || 0}
            icon={<XCircle />}
            color="danger"
          />
        </Col>
      </Row>

      <Row>
        {/* Main Content */}
        <Col lg={8}>
          {/* Recent Projects */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Recent Projects</h5>
            </Card.Header>
            <Card.Body>
              {projects?.items?.length ? (
                <Row>
                  {projects.items.map((project) => (
                    <Col md={6} key={project.id} className="mb-3">
                      <ProjectCard project={project} />
                    </Col>
                  ))}
                </Row>
              ) : (
                <div className="text-center text-muted py-4">
                  <p>No projects yet. Create your first project to get started!</p>
                  <Button variant="outline-primary">
                    <Plus size={16} className="me-2" />
                    Create Project
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Recent Test Results */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Recent Test Results</h5>
            </Card.Header>
            <Card.Body>
              {recentTests?.items?.length ? (
                <div className="space-y-3">
                  {recentTests.items.map((test) => (
                    <TestResultCard key={test.id} testRun={test} />
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted py-4">
                  <p>No test results yet.</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Sidebar */}
        <Col lg={4}>
          <QuickActions className="mb-4" />
          <RecentActivity />
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
```

### 5.3 Real-time Integration with WebSocket

#### WebSocket Service for Frontend

```typescript
// src/services/websocket.ts
import { io, Socket } from 'socket.io-client';
import { authService } from './auth';
import toast from 'react-hot-toast';

interface WebSocketMessage {
  type: string;
  test_run_id?: number;
  progress?: number;
  results?: any;
  error?: string;
  timestamp: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = authService.getToken();
      if (!token) {
        reject(new Error('No authentication token'));
        return;
      }

      this.socket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:8000', {
        auth: { token },
        transports: ['websocket'],
        timeout: 20000,
      });

      this.socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        resolve();
      });

      this.socket.on('disconnect', (reason) => {
        console.log('❌ WebSocket disconnected:', reason);
        if (reason === 'io server disconnect') {
          // Server initiated disconnect, try to reconnect
          this.attemptReconnect();
        }
      });

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        reject(error);
      });

      this.setupMessageHandlers();
    });
  }

  private setupMessageHandlers(): void {
    if (!this.socket) return;

    this.socket.on('test_progress', (data: WebSocketMessage) => {
      // Dispatch to Redux store
      window.dispatchEvent(
        new CustomEvent('testProgress', { detail: data })
      );
    });

    this.socket.on('test_completed', (data: WebSocketMessage) => {
      toast.success(`Test completed: ${data.test_run_id}`);
      window.dispatchEvent(
        new CustomEvent('testCompleted', { detail: data })
      );
    });

    this.socket.on('test_failed', (data: WebSocketMessage) => {
      toast.error(`Test failed: ${data.error}`);
      window.dispatchEvent(
        new CustomEvent('testFailed', { detail: data })
      );
    });
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      toast.error('Failed to reconnect to server');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.connect().catch(() => {
        // Will try again if this fails
      });
    }, delay);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const webSocketService = new WebSocketService();
```

#### Custom Hook for Real-time Updates

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { webSocketService } from '../services/websocket';
import { updateTestProgress, updateTestStatus } from '../store/slices/testsSlice';

export const useWebSocket = () => {
  const dispatch = useDispatch();

  const handleTestProgress = useCallback((event: CustomEvent) => {
    const { test_run_id, progress } = event.detail;
    dispatch(updateTestProgress({ testRunId: test_run_id, progress }));
  }, [dispatch]);

  const handleTestCompleted = useCallback((event: CustomEvent) => {
    const { test_run_id, results } = event.detail;
    dispatch(updateTestStatus({ 
      testRunId: test_run_id, 
      status: 'completed',
      results 
    }));
  }, [dispatch]);

  const handleTestFailed = useCallback((event: CustomEvent) => {
    const { test_run_id, error } = event.detail;
    dispatch(updateTestStatus({ 
      testRunId: test_run_id, 
      status: 'failed',
      error 
    }));
  }, [dispatch]);

  useEffect(() => {
    // Connect to WebSocket
    webSocketService.connect().catch(console.error);

    // Add event listeners
    window.addEventListener('testProgress', handleTestProgress as EventListener);
    window.addEventListener('testCompleted', handleTestCompleted as EventListener);
    window.addEventListener('testFailed', handleTestFailed as EventListener);

    return () => {
      // Cleanup
      window.removeEventListener('testProgress', handleTestProgress as EventListener);
      window.removeEventListener('testCompleted', handleTestCompleted as EventListener);
      window.removeEventListener('testFailed', handleTestFailed as EventListener);
      webSocketService.disconnect();
    };
  }, [handleTestProgress, handleTestCompleted, handleTestFailed]);

  return {
    isConnected: webSocketService.isConnected(),
  };
};
```

---

## 🐳 Deployment Configuration

### Docker Setup

#### FastAPI Dockerfile

```dockerfile
# Dockerfile.api
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/screenshots uploads/reports uploads/test_artifacts

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### React Frontend Dockerfile

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ui_testing_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ui_testing_db
      REDIS_URL: redis://redis:6379
      SECRET_KEY: your-secret-key-here
      ALLOWED_ORIGINS: '["http://localhost:3000", "http://localhost"]'
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    environment:
      REACT_APP_API_BASE_URL: http://localhost:8000
      REACT_APP_WS_URL: ws://localhost:8000
    ports:
      - "80:80"
    depends_on:
      - api

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.api
    command: celery -A celery_app worker --loglevel=info --queues=test_queue,llm_queue
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ui_testing_db
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

---

## 📋 Implementation Timeline (Bottom-Up Approach)

### Sprint 1: Foundation (Weeks 1-2)
- ✅ Set up PostgreSQL database with SQLAlchemy models
- ✅ Configure Redis for caching and sessions
- ✅ Implement basic FastAPI app structure
- ✅ Set up file storage service
- ✅ Create core Pydantic schemas
- ✅ Implement JWT authentication

### Sprint 2: Service Layer (Weeks 3-4)
- ✅ Build CRUD services for all entities
- ✅ Implement comprehensive error handling
- ✅ Set up Celery for background tasks
- ✅ Create WebSocket manager for real-time updates
- ✅ Build file upload/download endpoints
- ✅ Add API validation and documentation

### Sprint 3: Integration (Weeks 5-6)
- ✅ Integrate with existing UI testing system
- ✅ Implement real-time progress tracking
- ✅ Set up task queue processing
- ✅ Build notification system
- ✅ Create comprehensive API endpoints
- ✅ Add monitoring and logging

### Sprint 4: Frontend & Polish (Weeks 7-8)
- ✅ Build React components bottom-up
- ✅ Implement Redux state management
- ✅ Create real-time dashboard
- ✅ Add comprehensive error handling
- ✅ Implement responsive design
- ✅ Add testing and documentation
- ✅ Deploy and optimize

---

## 🎯 Key Features Summary

### ✨ Core Capabilities
1. **Project Management**: Create, configure, and manage UI testing projects
2. **Real-time Testing**: Monitor test execution with live progress updates
3. **Result Visualization**: Rich charts and reports for test outcomes
4. **File Management**: Upload, store, and serve test artifacts
5. **User Authentication**: Secure JWT-based authentication system
6. **REST API**: Comprehensive FastAPI-based backend
7. **Real-time Updates**: WebSocket integration for live notifications

### 🚀 Technical Highlights
- **Bottom-up Architecture**: Built progressively from foundation to features
- **FastAPI Backend**: Modern async Python framework
- **React Frontend**: TypeScript-based SPA with Bootstrap 5.13
- **Real-time Communication**: WebSocket for live updates
- **Task Processing**: Celery for background job handling
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for sessions and task queue
- **Containerized**: Docker deployment with compose

This architecture provides a solid foundation for building a modern, scalable UI testing dashboard that integrates seamlessly with your existing LLM-powered testing system.



=========================END=============================================
# Frontend Dashboard Architecture - Bottom-Up Design
## LLM-Powered UI Testing System Web Dashboard

### Executive Summary

This document presents a **comprehensive bottom-up architecture** for a modern web dashboard that interfaces with the LLM-Powered UI Testing System. Following architectural best practices, we build from foundational data structures to complex user interfaces, ensuring each layer is robust before adding the next. The system employs React.js with TypeScript for the frontend and FastAPI for a modern, high-performance Python backend.

**Key Architectural Principles:**
- 🏗️ **Bottom-Up Construction**: Each component builds upon tested foundations
- ⚡ **Performance-First**: FastAPI async capabilities + React optimization
- 🔒 **Security by Design**: JWT authentication, input validation, RBAC
- 📱 **Mobile-First UI**: Bootstrap 5.3 responsive design
- 🔄 **Real-time Updates**: WebSocket integration for live test monitoring
- 🧪 **Test-Driven**: Comprehensive testing at every layer

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────── FRONTEND LAYER ──────────────────────────┐
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    React.js SPA                              │   │
│  │                  (Port: 3000)                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                    │                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Dashboard Views │  │  Component Lib   │  │   State Mgmt     │   │
│  │  • Project Mgmt  │  │  • Bootstrap 5   │  │  • Redux Toolkit │   │
│  │  • Test Results  │  │  • Custom Comp   │  │  • React Query   │   │
│  │  • Config UI     │  │  • Charts/Viz    │  │  • Local Storage │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ REST API Calls (HTTPS)
                               ↓
┌─────────────────────── API GATEWAY LAYER ────────────────────────────┐
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Django REST Framework                      │   │
│  │                    (Port: 8000)                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   Auth & RBAC   │  │   API Endpoints  │  │   WebSocket      │   │
│  │  • JWT Auth     │  │  • CRUD APIs     │  │  • Real-time     │   │
│  │  • Permissions  │  │  • File Upload   │  │  • Notifications │   │
│  │  • Rate Limit   │  │  • Data Export   │  │  • Progress      │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ Internal API Calls
                               ↓
┌──────────────────── BACKEND INTEGRATION LAYER ──────────────────────┐
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            Existing Python Testing System                    │   │
│  │             (Orchestrator Integration)                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Task Queue     │  │  File Management │  │   Monitoring     │   │
│  │  • Celery       │  │  • Test Outputs  │  │  • System Health │   │
│  │  • Redis        │  │  • Screenshots   │  │  • Performance   │   │
│  │  • Job Status   │  │  • Reports       │  │  • Error Logs    │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ Data Persistence
                               ↓
┌─────────────────────── DATABASE LAYER ───────────────────────────────┐
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   PostgreSQL     │  │      Redis       │  │   File Storage   │   │
│  │  • User Data     │  │  • Cache Layer   │  │  • Test Artifacts│   │
│  │  • Projects      │  │  • Sessions      │  │  • Screenshots   │   │
│  │  • Test History  │  │  • Task Queue    │  │  • Reports       │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Architecture (React.js)

### Technology Stack
- **Framework**: React 18+ with TypeScript
- **Styling**: Bootstrap 5.3 + Custom SCSS
- **State Management**: Redux Toolkit + React Query
- **Routing**: React Router v6
- **Build Tool**: Vite
- **HTTP Client**: Axios with interceptors
- **Real-time**: Socket.IO client
- **Charts**: Chart.js with react-chartjs-2
- **Forms**: React Hook Form with Yup validation

### Component Architecture

```
src/
├── components/                    # Reusable UI components
│   ├── common/
│   │   ├── Button/
│   │   ├── Modal/
│   │   ├── Table/
│   │   ├── Form/
│   │   └── Layout/
│   ├── dashboard/
│   │   ├── ProjectCard/
│   │   ├── TestResultCard/
│   │   ├── ProgressIndicator/
│   │   └── StatusBadge/
│   └── charts/
│       ├── TestResultsChart/
│       ├── PerformanceChart/
│       └── CoverageChart/
├── pages/                        # Route-level components
│   ├── Dashboard/
│   ├── Projects/
│   ├── TestResults/
│   ├── Configuration/
│   ├── Reports/
│   └── Settings/
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts
│   ├── useWebSocket.ts
│   ├── useLocalStorage.ts
│   └── useDebounce.ts
├── services/                     # API service layer
│   ├── api.ts
│   ├── auth.ts
│   ├── projects.ts
│   ├── tests.ts
│   └── websocket.ts
├── store/                        # Redux store configuration
│   ├── slices/
│   │   ├── authSlice.ts
│   │   ├── projectsSlice.ts
│   │   ├── testsSlice.ts
│   │   └── uiSlice.ts
│   └── index.ts
├── types/                        # TypeScript type definitions
│   ├── api.ts
│   ├── project.ts
│   ├── test.ts
│   └── user.ts
├── utils/                        # Utility functions
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
└── styles/                       # Global styles
    ├── bootstrap-custom.scss
    ├── variables.scss
    └── global.scss
```

### Key Features & Components

#### 1. **Dashboard Overview**
```typescript
interface DashboardProps {
  projects: Project[];
  recentTests: TestRun[];
  systemStats: SystemStats;
}

const Dashboard: React.FC<DashboardProps> = ({
  projects,
  recentTests,
  systemStats
}) => {
  return (
    <Container fluid>
      <Row>
        <Col md={8}>
          <ProjectsOverview projects={projects} />
          <RecentTestResults tests={recentTests} />
        </Col>
        <Col md={4}>
          <SystemHealth stats={systemStats} />
          <QuickActions />
        </Col>
      </Row>
    </Container>
  );
};
```

#### 2. **Project Management**
- Create/Edit/Delete projects
- Configure target URLs and authentication
- Set testing parameters (max pages, depth, frameworks)
- LLM provider and model selection

#### 3. **Test Configuration Wizard**
```typescript
interface TestConfigurationProps {
  onSubmit: (config: TestConfig) => void;
  initialData?: Partial<TestConfig>;
}

const TestConfiguration: React.FC<TestConfigurationProps> = ({
  onSubmit,
  initialData
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  
  return (
    <Card>
      <Card.Header>
        <ProgressBar 
          now={(currentStep / 4) * 100} 
          label={`Step ${currentStep} of 4`}
        />
      </Card.Header>
      <Card.Body>
        {currentStep === 1 && <BasicConfigStep />}
        {currentStep === 2 && <LLMConfigStep />}
        {currentStep === 3 && <AuthConfigStep />}
        {currentStep === 4 && <ReviewStep />}
      </Card.Body>
    </Card>
  );
};
```

#### 4. **Real-time Test Monitoring**
```typescript
const TestMonitor: React.FC<{ testId: string }> = ({ testId }) => {
  const { testStatus, progress } = useWebSocket(`/test/${testId}`);
  
  return (
    <Card>
      <Card.Header>
        <StatusBadge status={testStatus} />
        <span className="ms-2">Test Execution</span>
      </Card.Header>
      <Card.Body>
        <ProgressBar 
          now={progress.percentage} 
          label={`${progress.currentPage}/${progress.totalPages} pages`}
        />
        <TestLog entries={progress.logs} />
      </Card.Body>
    </Card>
  );
};
```

#### 5. **Results Visualization**
- Interactive charts for test results
- Downloadable reports (PDF, Excel)
- Screenshot galleries
- Test script previews

---

## 🔧 Backend Architecture (Django)

### Technology Stack
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Task Queue**: Celery with Redis broker
- **WebSocket**: Django Channels
- **Authentication**: Django-allauth + JWT
- **File Storage**: Django-storages (local/cloud)
- **API Documentation**: drf-spectacular (OpenAPI)

### Project Structure

```
backend/
├── config/                       # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── authentication/           # User management & auth
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── projects/                 # Project CRUD operations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── tests/                    # Test execution & results
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py              # Celery tasks
│   │   └── consumers.py          # WebSocket consumers
│   ├── files/                    # File management
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   └── monitoring/               # System monitoring
│       ├── models.py
│       ├── views.py
│       └── tasks.py
├── integration/                  # Backend system integration
│   ├── orchestrator_client.py   # Python testing system client
│   ├── task_manager.py          # Task execution management
│   └── file_processor.py       # Output file processing
├── utils/
│   ├── exceptions.py
│   ├── permissions.py
│   ├── pagination.py
│   └── validators.py
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

### API Endpoints Design

#### Authentication & Users
```python
# authentication/urls.py
urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
]
```

#### Projects Management
```python
# projects/serializers.py
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'target_url', 
            'auth_config', 'test_config', 'created_at', 
            'updated_at', 'last_test_run'
        ]
    
    def validate_target_url(self, value):
        # URL validation logic
        return value

class TestConfigSerializer(serializers.Serializer):
    llm_provider = serializers.ChoiceField(choices=['openai', 'google'])
    llm_model = serializers.CharField(max_length=100)
    max_pages = serializers.IntegerField(min_value=1, max_value=1000)
    max_depth = serializers.IntegerField(min_value=1, max_value=10)
    headless = serializers.BooleanField(default=True)
    test_framework = serializers.ChoiceField(choices=['playwright', 'selenium'])
```

#### Test Execution & Results
```python
# tests/models.py
class TestRun(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ]
    )
    progress = models.JSONField(default=dict)
    results = models.JSONField(default=dict)
    artifacts_path = models.CharField(max_length=500, null=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    error_message = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class TestResult(models.Model):
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE)
    page_url = models.URLField()
    elements_found = models.IntegerField(default=0)
    test_cases_generated = models.IntegerField(default=0)
    screenshot_path = models.CharField(max_length=500, null=True)
    metadata = models.JSONField(default=dict)
```

#### WebSocket Consumers
```python
# tests/consumers.py
class TestProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.test_id = self.scope['url_route']['kwargs']['test_id']
        self.group_name = f'test_{self.test_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def test_progress_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'data': event['data']
        }))
```

### Integration with Existing Python System

#### Orchestrator Client
```python
# integration/orchestrator_client.py
class OrchestratorClient:
    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        
    async def start_test_run(self, project_config: dict) -> str:
        """Start a new test run and return the task ID."""
        task = run_ui_tests.delay(project_config)
        return task.id
    
    def get_task_status(self, task_id: str) -> dict:
        """Get the current status of a running task."""
        task = AsyncResult(task_id)
        return {
            'status': task.status,
            'progress': task.info if task.info else {},
            'result': task.result if task.successful() else None
        }
```

#### Celery Tasks
```python
# tests/tasks.py
@shared_task(bind=True)
def run_ui_tests(self, project_config: dict):
    """Execute UI tests using the existing Python system."""
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing...'}
        )
        
        # Initialize orchestrator
        orchestrator = Orchestrator(project_config, project_config['target_url'])
        
        # Run the test suite with progress callbacks
        results = orchestrator.run_comprehensive_test_suite(
            progress_callback=lambda progress: self.update_state(
                state='PROGRESS',
                meta=progress
            )
        )
        
        return {
            'status': 'completed',
            'results': results,
            'artifacts_path': results.get('output_dir')
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise
```

---

## 📊 Data Models & Relationships

```mermaid
erDiagram
    User ||--o{ Project : owns
    User ||--o{ TestRun : creates
    Project ||--o{ TestRun : has
    TestRun ||--o{ TestResult : contains
    TestRun ||--o{ TestArtifact : generates
    
    User {
        int id
        string username
        string email
        string first_name
        string last_name
        datetime created_at
        boolean is_active
    }
    
    Project {
        int id
        string name
        text description
        string target_url
        json auth_config
        json test_config
        datetime created_at
        datetime updated_at
        int created_by_id
    }
    
    TestRun {
        int id
        string status
        json progress
        json results
        string artifacts_path
        datetime started_at
        datetime completed_at
        text error_message
        int project_id
        int created_by_id
    }
    
    TestResult {
        int id
        string page_url
        int elements_found
        int test_cases_generated
        string screenshot_path
        json metadata
        int test_run_id
    }
    
    TestArtifact {
        int id
        string file_type
        string file_path
        string file_name
        int file_size
        datetime created_at
        int test_run_id
    }
```

---

## 🔐 Security Architecture

### Authentication & Authorization
```python
# authentication/permissions.py
class ProjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only project owner can modify
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.created_by == request.user
        
        # Read access for team members
        return True

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### API Rate Limiting
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'test_execution': '10/hour'  # Limit test runs
    }
}
```

### Environment Variables
```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# LLM API Keys
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key

# File Storage
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static

# CORS Settings
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

## 🚀 Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:password@db:5432/testdb
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=testdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery:
    build: ./backend
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

### Production Considerations
- **Load Balancing**: nginx reverse proxy
- **SSL/TLS**: Let's Encrypt certificates
- **Static Files**: CDN for media and static files
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis cluster for high availability
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack or centralized logging

---

## 📱 Responsive Design & UX

### Bootstrap 5.3 Integration
```scss
// styles/bootstrap-custom.scss
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";

// Custom theme variables
$primary: #007bff;
$secondary: #6c757d;
$success: #28a745;
$info: #17a2b8;
$warning: #ffc107;
$danger: #dc3545;

// Dark mode support
$enable-dark-mode: true;

@import "~bootstrap/scss/bootstrap";
```

### Mobile-First Approach
```typescript
// components/dashboard/ProjectCard.tsx
const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  return (
    <Col xs={12} md={6} lg={4} className="mb-3">
      <Card className="h-100">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h6 className="mb-0">{project.name}</h6>
          <Badge bg={getStatusColor(project.status)}>
            {project.status}
          </Badge>
        </Card.Header>
        <Card.Body>
          <small className="text-muted">{project.target_url}</small>
          <div className="mt-2">
            <Button size="sm" variant="outline-primary" className="me-2">
              View Results
            </Button>
            <Button size="sm" variant="primary">
              Run Tests
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );
};
```

### Dark Mode Support
```typescript
// hooks/useTheme.ts
export const useTheme = () => {
  const [isDark, setIsDark] = useLocalStorage('theme-dark', false);
  
  useEffect(() => {
    document.documentElement.setAttribute(
      'data-bs-theme', 
      isDark ? 'dark' : 'light'
    );
  }, [isDark]);
  
  return { isDark, toggleTheme: () => setIsDark(!isDark) };
};
```

---

## 🔄 Real-time Features

### WebSocket Implementation
```typescript
// services/websocket.ts
class WebSocketService {
  private socket: io.Socket | null = null;
  
  connect(token: string) {
    this.socket = io('ws://localhost:8000', {
      auth: { token },
      transports: ['websocket']
    });
    
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });
    
    return this.socket;
  }
  
  subscribeToTestProgress(testId: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.emit('join', `test_${testId}`);
      this.socket.on('test_progress', callback);
    }
  }
}
```

### Real-time Notifications
```typescript
// components/common/NotificationSystem.tsx
const NotificationSystem: React.FC = () => {
  const { notifications } = useSelector(state => state.ui);
  const dispatch = useDispatch();
  
  return (
    <ToastContainer position="top-end" className="p-3">
      {notifications.map(notification => (
        <Toast 
          key={notification.id}
          onClose={() => dispatch(removeNotification(notification.id))}
          bg={notification.type}
        >
          <Toast.Header>
            <strong className="me-auto">{notification.title}</strong>
          </Toast.Header>
          <Toast.Body>{notification.message}</Toast.Body>
        </Toast>
      ))}
    </ToastContainer>
  );
};
```

---

## 📈 Performance Optimization

### Frontend Optimizations
- **Code Splitting**: Route-based and component-based splitting
- **Lazy Loading**: Components and images
- **Memoization**: React.memo and useMemo for expensive computations
- **Bundle Analysis**: Webpack Bundle Analyzer
- **CDN**: Static assets served from CDN

### Backend Optimizations
- **Database Indexing**: Proper indexing on frequently queried fields
- **Query Optimization**: Select_related and prefetch_related
- **Caching Strategy**: Redis for session, API responses, and computed data
- **Connection Pooling**: Database connection pooling
- **Background Tasks**: Celery for long-running operations

### API Response Optimization
```python
# projects/views.py
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('created_by').prefetch_related('test_runs')
    serializer_class = ProjectSerializer
    
    @action(detail=True, methods=['get'])
    @cache_page(300)  # Cache for 5 minutes
    def test_history(self, request, pk=None):
        project = self.get_object()
        test_runs = project.test_runs.order_by('-created_at')[:10]
        serializer = TestRunSerializer(test_runs, many=True)
        return Response(serializer.data)
```

---

## 🧪 Testing Strategy

### Frontend Testing
```typescript
// components/__tests__/ProjectCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ProjectCard } from '../ProjectCard';

const mockProject = {
  id: 1,
  name: 'Test Project',
  target_url: 'https://example.com',
  status: 'active'
};

test('renders project card with correct information', () => {
  render(<ProjectCard project={mockProject} />);
  
  expect(screen.getByText('Test Project')).toBeInTheDocument();
  expect(screen.getByText('https://example.com')).toBeInTheDocument();
  expect(screen.getByText('active')).toBeInTheDocument();
});
```

### Backend Testing
```python
# tests/test_projects.py
class ProjectAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_project(self):
        data = {
            'name': 'Test Project',
            'target_url': 'https://example.com',
            'test_config': {'max_pages': 10}
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 1)
```

---

## 📚 Documentation & API

### API Documentation
```python
# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### Component Documentation (Storybook)
```typescript
// components/Button/Button.stories.tsx
export default {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'success', 'danger']
    }
  }
} as ComponentMeta<typeof Button>;

export const Primary: ComponentStory<typeof Button> = (args) => (
  <Button {...args}>Primary Button</Button>
);
```

---

## 🔮 Future Enhancements

### Phase 2 Features
- **Team Collaboration**: Multi-user projects and role-based permissions
- **CI/CD Integration**: GitHub Actions, Jenkins, GitLab CI integration
- **Advanced Analytics**: Test trend analysis, performance metrics
- **Custom Templates**: User-defined test templates and patterns
- **API Testing**: REST API endpoint testing capabilities

### Phase 3 Features
- **Mobile App Testing**: React Native, Flutter app testing
- **Visual Regression**: Screenshot comparison and visual diff detection
- **AI Insights**: Predictive analytics for test failures
- **Multi-tenant Architecture**: SaaS deployment model
- **Enterprise SSO**: SAML, LDAP integration

---

## 📝 Implementation Timeline

### Sprint 1 (2 weeks): Foundation
- [ ] Django project setup and basic models
- [ ] React project setup with TypeScript
- [ ] Authentication system (JWT)
- [ ] Basic project CRUD operations

### Sprint 2 (2 weeks): Core Features
- [ ] Test execution integration
- [ ] WebSocket real-time updates
- [ ] File upload and management
- [ ] Basic dashboard views

### Sprint 3 (2 weeks): UI Polish
- [ ] Bootstrap 5 integration
- [ ] Responsive design implementation
- [ ] Charts and data visualization
- [ ] Form validation and error handling

### Sprint 4 (2 weeks): Testing & Deployment
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Documentation and API docs

---



=============================================================================================================

LLM-Powered UI Testing System - Technical Architecture
┌────────────────────────────────────── INPUT ──────────────────────────────────────┐
│                                                                                   │
│                           ┌───────────────────────────┐                           │
│                           │   Target Web Application  │                           │
│                           │  Root URL + Auth Credentials │                         │
│                           └───────────────────────────┘                           │
│                                        │                                          │
└────────────────────────────────────────┼──────────────────────────────────────────┘
                                         ↓
┌───────────────────────── INTERFACE LAYER ─────────────────────────┐
│                                                                   │
│  ┌────────────────────────┐        ┌─────────────────────────┐    │
│  │ Command Line Interface │        │  Configuration Manager   │    │
│  │ Parameter Parsing      │        │  Settings Validation     │    │
│  │ Config Loading         │        │  Environment Variables   │    │
│  └────────────────────────┘        └─────────────────────────┘    │
│                                                                   │
│  config.py: Handles API keys, browser settings, output options    │
│                                                                   │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │ Validated Configuration
                                  ↓
┌───────────────────── ORCHESTRATION LAYER ────────────────────────┐
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                        Orchestrator                        │  │
│  │          Central Coordination • Process Management         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │     State Tracker       │        │     Error Handler       │  │
│  │  Visit History • Forms  │        │  Recovery • Retry Logic │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  orchestrator.py: Controls workflow and manages process flow     │
│                                                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ Discovery Commands
                                 ↓
┌─────────────────────── CRAWLING LAYER ───────────────────────────┐
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │   Browser Controller    │        │   Crawl4AI Integration  │  │
│  │  Playwright • DOM Access│        │  Async • Deep Crawling  │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │  Authentication Handler │        │ Dynamic Content Process │  │
│  │  Login Flows • Cookies  │        │  JavaScript • Loading   │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  browser_controller.py + Crawl4AI: Navigation and DOM capture    │
│                                                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ DOM Content + Screenshots
                                 ↓
┌─────────────────────── ANALYSIS LAYER ───────────────────────────┐
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │     LLM Interface       │        │    Element Extractor    │  │
│  │  API • Prompt Management│        │  Form Detection • IDs   │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │      DOM Parser         │        │    Visual Analyzer      │  │
│  │  HTML • Shadow DOM      │        │  Screenshots • Layout   │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  llm_interface.py + element_extractor.py: LLM-powered analysis   │
│                                                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ Structured Element Metadata
                                 ↓
┌────────────────────── GENERATION LAYER ──────────────────────────┐
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │     Test Generator      │        │     Code Generator      │  │
│  │  Test Cases • Scenarios │        │  POM Classes • Scripts  │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐        ┌─────────────────────────┐  │
│  │     Template Engine     │        │        Validator        │  │
│  │  Code Templates • Style │        │  Syntax • Test Logic    │  │
│  └─────────────────────────┘        └─────────────────────────┘  │
│                                                                  │
│  test_generator.py + code_generator.py: LLM-driven generation    │
│                                                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ Test Artifacts
                                 ↓
┌──────────────────────── OUTPUT LAYER ────────────────────────────┐
│                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────┐   │
│  │    JSON     │      │  Test Cases │      │  Test Scripts   │   │
│  │   Metadata  │      │    Gherkin  │      │   Python Code   │   │
│  └─────────────┘      └─────────────┘      └─────────────────┘   │
│                                                                  │
│               ┌─────────────────────────────┐                    │
│               │        Summary Report       │                    │
│               └─────────────────────────────┘                    │
│                                                                  │
│  outputs/: metadata/, test_cases/, test_scripts/ directories     │
│                                                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ↓
                      ┌─────────────────────────┐
                      │     PyTest Runner       │
                      │    Executes Tests       │
                      └─────────────────────────┘
Layer-by-Layer Process Flow
1. Interface Layer
Receives initial inputs and configuration parameters:

Command Line Interface: Processes arguments from users
Configuration Manager: Loads and validates settings

2. Orchestration Layer
Central coordination and decision-making:

Orchestrator: Main workflow controller
State Tracker: Maintains crawl state and history
Error Handler: Manages failures and retries

3. Crawling Layer
Web interaction and content discovery:

Browser Controller: Playwright-based browser automation
Crawl4AI Integration: Enhanced crawling capabilities
Authentication Handler: Manages login processes
Dynamic Content Processor: Handles JavaScript-heavy sites

4. Analysis Layer
Content understanding and element extraction:

LLM Interface: Communicates with AI models
Element Extractor: Identifies UI components
DOM Parser: Analyzes HTML structure
Visual Analyzer: Processes screenshots

5. Generation Layer
Creates test artifacts:

Test Generator: Produces human-readable test cases
Code Generator: Builds executable test scripts
Template Engine: Manages code patterns
Validator: Ensures quality and correctness

6. Output Layer
Organizes final deliverables:

JSON Metadata: Structured element data
Test Cases: Human-readable scenarios
Test Scripts: Executable test code
Summary Report: Overall testing results

Crawl4AI Integration Points
The Crawl4AI integration enhances the Crawling Layer by:

Replacing basic navigation with high-performance async crawling
Providing BFS/DFS strategies for comprehensive site exploration
Handling complex dynamic content and JavaScript execution
Managing browser sessions across multiple interactions

Data flows unidirectionally down through the layers, with each layer performing its specific logical function before passing processed information to the next layer.
