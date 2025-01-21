# 🚀 BetterLMS 🚀
BetterLMS is a lightweight Learning Management System (LMS) built with **FastAPI** for the backend and **React (TypeScript + Vite + Chakra UI)** for the frontend. It supports **role-based access control**, **user management**, **course assignments**, and **tests for employees**.

### Getting started
```bash
./start.sh  # starts frontend and backend, run this after setup.
```

### Python environment
```bash
cd backend
uv sync
source .venv/bin/activate
```

### Backend (FastAPI)
```bash
cd backend
fastapi run app/main.py
```

### NODE environment 
[Install nvm](https://github.com/nvm-sh/nvm)
```bash
nvm install node # "node" is an alias for the latest version
nvm install-latest-npm
```

### Frontend (React + Vite)
```bash
cd frontend
npm install  
npm run dev
```

### Project Structure

### **Backend (`backend/` - FastAPI)**
#### `app/`
- `api/` - API routes and dependencies
  - `deps.py` - Dependency injection utilities
  - `main.py` - API router
  - `routes/` - API endpoints
    - `items.py` - CRUD operations for items
    - `login.py` - Authentication endpoints
    - `private.py` - Private routes requiring authentication
    - `users.py` - User-related operations
    - `utils.py` - Helper functions
- `core/` - Core configuration and security
  - `config.py` - Application settings
  - `db.py` - Database connection setup
  - `security.py` - Password hashing and authentication
- `crud.py` - CRUD operations for users and items
- `models.py` - SQLModel database schemas
- `utils.py` - Additional utility functions
- `data/` - Contains SQLite database file (`app.db`)
- `tests/` - Unit and integration tests

#### Other Files
- `pyproject.toml` - Backend dependencies
- `README.md` - Project documentation
- `start.sh` - Shell script for starting the backend and frontend

---

### **Frontend (`frontend/` - React + TypeScript + Vite)**

#### `src/`
- `components/` - UI components
  - `Admin/` - Admin panel components
  - `Common/` - Navbar, sidebar, modals, etc.
  - `Items/` - Item management components
  - `UserSettings/` - User profile settings
- `hooks/` - Custom React hooks
- `routes/` - Frontend routes
  - `login.tsx` - Login page
  - `signup.tsx` - User registration
  - `settings.tsx` - User settings
  - `admin.tsx` - Admin dashboard
  - `items.tsx` - Item management page
- `client/` - OpenAPI client for backend communication
- `theme.tsx` - Chakra UI theme configuration
- `utils.ts` - Helper functions

#### Other Files
- `index.html` - Entry point
- `package.json` - Frontend dependencies
- `vite.config.ts` - Vite configuration
- `tests/` - End-to-end tests (Playwright)

---
