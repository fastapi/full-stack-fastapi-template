# Workflow 管理系统需求与设计

## 项目概述
纯后端 workflow 管理和运行服务，支持定时执行和顺序任务执行。

## 核心需求
1. **工作流管理** - CRUD 操作工作流定义
2. **任务调度** - 基于 cron 表达式的定时执行
3. **顺序执行** - 按顺序执行工作流中的子任务
4. **状态追踪** - 完整的执行历史和日志
5. **错误处理** - 失败重试和错误恢复
6. **并发控制** - 防止重复执行

## 技术架构
- **后端**: FastAPI + SQLModel
- **任务队列**: Celery + Redis
- **数据库**: PostgreSQL (元数据) + Redis (缓存)
- **监控**: Flower
- **部署**: Docker Compose

## 数据库设计

### 核心表结构
```sql
workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    max_concurrent_runs INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

workflow_tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    order_index INTEGER NOT NULL,
    retry_count INTEGER DEFAULT 0,
    timeout_seconds INTEGER DEFAULT 300,
    created_at TIMESTAMP DEFAULT NOW()
)

workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id),
    status VARCHAR(20) DEFAULT 'PENDING',
    trigger_type VARCHAR(20) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)

task_executions (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES workflow_runs(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES workflow_tasks(id),
    status VARCHAR(20) DEFAULT 'PENDING',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output JSONB,
    error TEXT
)
```

## API 设计

### RESTful 端点
```
POST   /api/v1/workflows              # 创建工作流
GET    /api/v1/workflows              # 获取工作流列表
GET    /api/v1/workflows/{id}         # 获取工作流详情
PUT    /api/v1/workflows/{id}         # 更新工作流
DELETE /api/v1/workflows/{id}         # 删除工作流

POST   /api/v1/workflows/{id}/tasks   # 添加任务
PUT    /api/v1/tasks/{id}             # 更新任务
DELETE /api/v1/tasks/{id}             # 删除任务

POST   /api/v1/workflows/{id}/run     # 手动触发执行
POST   /api/v1/workflows/{id}/stop    # 停止执行
GET    /api/v1/workflows/{id}/runs    # 获取执行历史
GET    /api/v1/runs/{id}              # 获取执行详情
GET    /api/v1/runs/{id}/logs         # 获取执行日志

POST   /api/v1/workflows/{id}/enable   # 启用调度
POST   /api/v1/workflows/{id}/disable  # 禁用调度
```

## 任务类型支持

### HTTP 任务
```json
{
  "task_type": "HTTP",
  "config": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {"Authorization": "Bearer token"},
    "body": {"key": "value"}
  }
}
```

### 数据库任务
```json
{
  "task_type": "DATABASE",
  "config": {
    "connection_string": "postgresql://user:pass@localhost/db",
    "sql": "SELECT * FROM users WHERE id = %s",
    "parameters": [123]
  }
}
```

### Shell 任务
```json
{
  "task_type": "SHELL",
  "config": {
    "command": "python script.py",
    "working_dir": "/app/scripts",
    "env_vars": {"DEBUG": "1"}
  }
}
```

## 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Celery        │    │   PostgreSQL    │
│   REST API      │────┤   Worker        │────┤   Metadata      │
│   ├─ workflows  │    │   ├─ Scheduler  │    │                 │
│   ├─ tasks      │    │   ├─ Executor   │    └─────────────────┘
│   └─ runs       │    │   └─ Monitor    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                   │
           ┌─────────────────┐
           │   Redis         │
           │   Queue         │
           └─────────────────┘
```

## 监控与运维
- **Flower**: http://localhost:5555
- **API 文档**: http://localhost:8000/docs
- **数据库**: http://localhost:8080 (Adminer)

## 部署与扩展
- 支持水平扩展 Celery worker
- 支持 Redis 集群
- 支持数据库读写分离
- 支持任务优先级队列

## 数据库模型

### 核心表结构
```sql
workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    max_concurrent_runs INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

workflow_tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    order_index INTEGER NOT NULL,
    retry_count INTEGER DEFAULT 0,
    timeout_seconds INTEGER DEFAULT 300,
    created_at TIMESTAMP DEFAULT NOW()
)

workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id),
    status VARCHAR(20) DEFAULT 'PENDING',
    trigger_type VARCHAR(20) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)

task_executions (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES workflow_runs(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES workflow_tasks(id),
    status VARCHAR(20) DEFAULT 'PENDING',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output JSONB,
    error TEXT
)
```

## API 端点设计

### 工作流管理
```
POST   /api/v1/workflows              # 创建工作流
GET    /api/v1/workflows              # 获取工作流列表
GET    /api/v1/workflows/{id}         # 获取工作流详情
PUT    /api/v1/workflows/{id}         # 更新工作流
DELETE /api/v1/workflows/{id}         # 删除工作流
```

### 任务管理
```
POST   /api/v1/workflows/{id}/tasks   # 添加任务
PUT    /api/v1/tasks/{id}             # 更新任务
DELETE /api/v1/tasks/{id}             # 删除任务
```

### 执行控制
```
POST   /api/v1/workflows/{id}/run     # 手动触发执行
POST   /api/v1/workflows/{id}/stop    # 停止执行
GET    /api/v1/workflows/{id}/runs    # 获取执行历史
GET    /api/v1/runs/{id}              # 获取执行详情
GET    /api/v1/runs/{id}/logs         # 获取执行日志
```

### 调度控制
```
POST   /api/v1/workflows/{id}/enable   # 启用调度
POST   /api/v1/workflows/{id}/disable  # 禁用调度
```

## 任务类型定义

### 支持的任务类型
```python
TASK_TYPES = {
    "HTTP": {
        "url": "string",
        "method": "GET|POST|PUT|DELETE",
        "headers": "dict",
        "body": "string|dict"
    },
    "DATABASE": {
        "connection_string": "string",
        "sql": "string",
        "parameters": "dict"
    },
    "SHELL": {
        "command": "string",
        "working_dir": "string",
        "env_vars": "dict"
    }
}
```

## Celery 任务设计

### 主任务
```python
@celery_app.task(bind=True)
def execute_workflow(self, workflow_id: int, trigger_type: str):
    """执行整个工作流"""
    pass

@celery_app.task(bind=True, max_retries=3)
def execute_task(self, run_id: int, task_id: int):
    """执行单个任务"""
    pass

@celery_app.task
def check_scheduled_workflows():
    """周期性检查待执行的工作流"""
    pass
```

## 项目结构
```
backend/
├── app/
│   ├── celery_app.py        # Celery 实例
│   ├── models.py           # 数据模型
│   ├── crud.py            # 数据库操作
│   ├── api/
│   │   └── routes/
│   │       └── workflows.py
│   ├── tasks/             # Celery 任务
│   │   ├── __init__.py
│   │   ├── workflow_tasks.py
│   │   └── scheduler_tasks.py
│   └── services/
│       ├── workflow_runner.py
│       └── task_executor.py
├── tests/                 # 测试文件
└── scripts/              # 工具和脚本
```

## 部署命令

```bash
# 启动完整服务
docker compose up -d

# 查看 Celery 任务
docker compose logs celery-worker

# 监控面板
open http://localhost:5555  # Flower
```

## 测试验证

```bash
# 运行测试
uv run pytest tests/

# 手动测试 API
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"name": "test-workflow", "tasks": [...]}'
```