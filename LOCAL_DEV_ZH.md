# 本地开发指南

本文档详细说明如何在本地启动 DataAnalysis API 项目的前后端开发环境。

---

## 目录

- [方式一：Docker Compose（推荐）](#方式一docker-compose推荐)
- [方式二：本地开发环境](#方式二本地开发环境)
  - [后端启动](#后端启动)
  - [前端启动](#前端启动)
  - [数据库配置](#数据库配置)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

---

## 方式一：Docker Compose（推荐）

这是最简单的方式，无需手动安装依赖。

### 步骤 1：启动服务

```bash
# 进入项目根目录
cd data-analysis-api

# 启动所有服务（后台运行）
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 步骤 2：等待服务就绪

首次启动需要等待数据库初始化，约 30-60 秒。

```bash
# 查看后端日志，等待出现 "Application startup complete"
docker compose logs -f backend
```

### 步骤 3：访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | React 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| API 文档 | http://localhost:8000/redoc | ReDoc |
| 邮件测试 | http://localhost:1080 | MailCatcher |

### 步骤 4：登录

- 邮箱：`admin@example.com`
- 密码：`changethis`

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止并删除数据卷（清空数据库）
docker compose down -v
```

---

## 方式二：本地开发环境

如果你想单独调试前后端，可以使用本地开发环境。

---

## 后端启动

### 前置要求

- Python 3.12+
- PostgreSQL 14+ (或使用 Docker 运行数据库)
- Redis (可选，用于 Celery 任务队列)

### 步骤 1：安装依赖

```bash
# 进入后端目录
cd backend

# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 步骤 2：配置环境变量

编辑 `.env` 文件（项目根目录）：

```bash
# 项目名称
PROJECT_NAME="DataAnalysis API"

# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

# 后端配置
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis

# 前端地址（用于 CORS）
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173"
```

### 步骤 3：启动数据库（Docker 方式）

```bash
# 只启动数据库和 Redis
docker compose up -d db redis

# 等待数据库就绪
docker compose logs -f db
```

### 步骤 4：运行数据库迁移

```bash
cd backend

# 运行 Alembic 迁移
alembic upgrade head
```

### 步骤 5：启动后端服务

```bash
cd backend

# 方式 1：使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2：使用 FastAPI CLI
fastapi dev app/main.py

# 方式 3：使用 Make（如果项目有 Makefile）
make backend
```

### 后端启动成功标志

看到以下输出表示成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 访问后端

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/utils/health-check

---

## 前端启动

### 前置要求

- Node.js 20+
- npm 或 pnpm 或 yarn

### 步骤 1：安装依赖

```bash
# 进入前端目录
cd frontend

# 使用 npm 安装
npm install

# 或使用 pnpm（更快）
pnpm install

# 或使用 yarn
yarn install
```

### 步骤 2：配置环境变量

编辑 `frontend/.env` 文件：

```bash
# API 地址
VITE_API_URL=http://localhost:8000
```

### 步骤 3：启动前端开发服务器

```bash
cd frontend

# 使用 npm
npm run dev

# 或使用 pnpm
pnpm dev

# 或使用 yarn
yarn dev
```

### 前端启动成功标志

看到以下输出表示成功：

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 访问前端

打开浏览器访问：http://localhost:5173

---

## 数据库配置

### 使用 Docker 运行 PostgreSQL

```bash
# 只启动数据库
docker compose up -d db

# 查看数据库日志
docker compose logs -f db

# 连接到数据库
docker compose exec db psql -U postgres -d app
```

### 数据库迁移

```bash
cd backend

# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 重置数据库

```bash
# 删除所有数据并重新初始化
docker compose down -v
docker compose up -d db
alembic upgrade head
```

---

## 常用命令

### 后端

```bash
# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html

# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy .
```

### 前端

```bash
# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 运行 E2E 测试
npm run test:e2e
```

### Docker

```bash
# 查看运行中的容器
docker compose ps

# 查看日志
docker compose logs -f [服务名]

# 重启服务
docker compose restart [服务名]

# 进入容器
docker compose exec backend /bin/bash
```

---

## 故障排查

### 后端无法启动

**问题：** `Connection refused` 或数据库连接失败

**解决方案：**
1. 确认数据库正在运行：`docker compose ps`
2. 检查 `.env` 文件中的数据库配置
3. 等待数据库完全启动（约 10-20 秒）

**问题：** 端口已被占用

**解决方案：**
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或更改端口
uvicorn app.main:app --reload --port 8001
```

### 前端无法连接后端

**问题：** CORS 错误或网络错误

**解决方案：**
1. 确认后端正在运行：访问 http://localhost:8000/docs
2. 检查 `.env` 中的 `BACKEND_CORS_ORIGINS` 配置
3. 检查前端的 `VITE_API_URL` 配置

### 数据库迁移失败

**问题：** Alembic 迁移出错

**解决方案：**
```bash
# 查看当前迁移状态
alembic current

# 回滚到上一个版本
alembic downgrade -1

# 如果完全乱了，重置数据库
alembic downgrade base
alembic upgrade head
```

### Docker 问题

**问题：** 容器无法启动

**解决方案：**
```bash
# 查看详细日志
docker compose logs [服务名]

# 重新构建镜像
docker compose build --no-cache [服务名]

# 清理并重新启动
docker compose down -v
docker compose up -d --build
```

---

## 开发技巧

### 热重载

- **后端**：使用 `--reload` 参数启动 uvicorn，代码修改会自动重启
- **前端**：Vite 默认支持热重载

### 调试

**后端：**
```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 ipdb（更友好）
import ipdb; ipdb.set_trace()
```

**前端：**
- 使用浏览器开发者工具
- VS Code 安装 `Debugger for Chrome` 扩展

### 查看日志

```bash
# 实时查看所有日志
docker compose logs -f

# 只查看特定服务
docker compose logs -f backend
docker compose logs -f frontend

# 查看最近 100 行
docker compose logs --tail=100
```

---

## 生产环境配置

⚠️ **警告：** 生产环境必须修改以下配置：

1. `SECRET_KEY` - 生成安全的密钥
2. `FIRST_SUPERUSER_PASSWORD` - 设置强密码
3. `POSTGRES_PASSWORD` - 设置数据库密码

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 需要帮助？

- 查看后端文档：[backend/README.md](./backend/README.md)
- 查看前端文档：[frontend/README.md](./frontend/README.md)
- 查看部署文档：[deployment.md](./deployment.md)
