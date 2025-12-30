# FastAPI 后端

## 环境要求

- [Docker](https://www.docker.com/)
- [uv](https://docs.astral.sh/uv/) - Python 包管理工具

## 快速开始

### 使用 Docker Compose

最简单的开发方式是使用 Docker Compose，详见 [本地开发指南](../LOCAL_DEV_ZH.md)。

### 本地开发

从 `./backend/` 目录安装依赖：

```bash
# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

确保你的编辑器使用正确的 Python 解释器：`backend/.venv/bin/python`

### 启动后端服务

```bash
# 方式 1：直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2：使用 FastAPI CLI
fastapi dev app/main.py

# 方式 3：使用 Docker Compose
docker compose up backend
```

## 项目结构

```
backend/
├── app/
│   ├── api/             # API 路由
│   ├── core/            # 配置、安全、数据库
│   ├── crud/            # 数据库操作
│   ├── db/              # 数据库会话
│   ├── models/          # SQLModel 数据模型
│   ├── schemas/         # Pydantic 数据验证
│   ├── tests/           # 测试
│   └── main.py          # FastAPI 应用入口
├── alembic/             # 数据库迁移
├── scripts/             # 脚本
├── tests/               # 后端测试
└── pyproject.toml       # Python 依赖
```

## 开发指南

### 修改数据模型

在 `./backend/app/models.py` 中修改或添加 SQLModel 模型。

修改后需要创建数据库迁移：

```bash
# 进入后端容器
docker compose exec backend bash

# 创建迁移
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head
```

### 添加 API 端点

在 `./backend/app/api/` 目录下添加新的路由。

示例：

```python
# app/api/my_api.py
from fastapi import APIRouter
from app.api.deps import ...

router = APIRouter()

@router.get("/items")
def read_items():
    return {"items": []}
```

然后在 `app/api/api_v1/api.py` 中注册：

```python
from app.api.my_api import router as my_api_router

api_router.include_router(my_api_router, prefix="/my-api", tags=["my-api"])
```

### 数据库操作 (CRUD)

在 `./backend/app/crud.py` 中添加数据库操作函数。

## 测试

### 运行测试

```bash
# 方式 1：使用脚本
bash ./scripts/test.sh

# 方式 2：直接使用 pytest
pytest

# 方式 3：在 Docker 容器中运行
docker compose exec backend bash scripts/tests-start.sh
```

### 测试覆盖率

```bash
pytest --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 数据库迁移

### 创建迁移

修改模型后，创建新的迁移：

```bash
docker compose exec backend bash

alembic revision --autogenerate -m "Add column last_name to User model"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>
```

## VS Code 调试

项目已配置 VS Code 调试支持：

1. 打开 `backend/` 目录
2. 设置断点
3. 按 F5 或点击 "运行和调试"
4. 选择 "FastAPI" 配置

## Docker Compose 覆盖配置

本地开发可以在 `docker-compose.override.yml` 中添加配置，不会影响生产环境。

示例：启用代码热重载

```yaml
services:
  backend:
    command: fastapi dev --reload app/main.py
    volumes:
      - ./backend:/app
```

## 常用命令

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy .

# 启动开发服务器
fastapi dev app/main.py

# 运行测试
pytest
```

## 故障排查

### 导入错误

确保虚拟环境已激活：`source .venv/bin/activate`

### 数据库连接失败

检查 `.env` 文件中的数据库配置，确保数据库正在运行。

### 迁移冲突

如果迁移出现问题，可以重置数据库：

```bash
docker compose down -v
docker compose up -d db
alembic upgrade head
```

## 邮件模板

邮件模板位于 `./backend/app/email-templates/`：

- `src/` - MJML 源文件
- `build/` - 编译后的 HTML 文件

编辑 MJML 文件后，使用 VS Code 的 MJML 扩展导出为 HTML。

## 需要帮助？

- [本地开发指南](../LOCAL_DEV_ZH.md)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
