# Workflow 管理系统实施 TODO

## 阶段1: 基础设施 (1天)

### 已完成
- ✅ 移除前端相关文件和目录
- ✅ 更新 docker-compose.yml 配置

### 已完成
- ✅ 添加 Celery + Redis 依赖
- ✅ 配置 Docker Redis 服务
- ✅ 创建 Celery 实例和基础配置

### 具体步骤

#### 1-1. 添加依赖
```bash
cd backend
uv add celery[redis] redis flower
cd ..
```

#### 1-2. 配置 Docker 服务
编辑 `docker-compose.yml` 添加：
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    depends_on:
      - redis
      - db
    volumes:
      - ./backend:/app
    env_file:
      - .env

  celery-beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    depends_on:
      - redis
      - db
    env_file:
      - .env

  flower:
    image: mher/flower
    command: celery flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

volumes:
  redis-data:
```

#### 1-3. 创建 Celery 配置
创建 `backend/app/celery_app.py`：
```python
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'workflow_app',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

celery_app.conf.beat_schedule = {
    'check-scheduled-workflows': {
        'task': 'app.tasks.check_scheduled_workflows',
        'schedule': crontab(minute='*/1'),
    },
}
```

## 阶段2: 核心功能 (2天)

### Day 2.1: 数据模型
- [ ] 更新 `backend/app/models.py` 添加 workflow 表
- [ ] 运行 `alembic revision --autogenerate -m "Add workflow tables"`
- [ ] 运行 `alembic upgrade head`

### Day 2.2: 业务逻辑
- [ ] 创建 `backend/app/crud.py` 添加 workflow CRUD
- [ ] 创建 `backend/app/services/scheduler.py`
- [ ] 创建 `backend/app/services/executor.py`

### Day 2.3: Celery 任务
- [ ] 创建 `backend/app/tasks/__init__.py`
- [ ] 创建 `backend/app/tasks/workflow_tasks.py`
- [ ] 创建 `backend/app/tasks/scheduler_tasks.py`

### Day 2.4: API 接口
- [ ] 创建 `backend/app/api/routes/workflows.py`
- [ ] 注册路由到 `main.py`
- [ ] 测试 API 文档访问

## 阶段3: 测试优化 (1天)

### Day 3.1: 单元测试
- [ ] 创建 `backend/tests/test_workflow_tasks.py`
- [ ] 创建 `backend/tests/test_api.py`
- [ ] 运行 `uv run pytest`

### Day 3.2: 集成测试
- [ ] 创建完整工作流测试
- [ ] 测试并发执行
- [ ] 测试错误恢复

### Day 3.3: 监控配置
- [ ] 配置 Flower 访问权限
- [ ] 配置日志格式
- [ ] 设置健康检查

### Day 3.4: 性能调优
- [ ] 优化 worker 并发配置
- [ ] 添加数据库索引
- [ ] 配置连接池

## 每日检查清单

### 每天开始
- [ ] 查看 PRD.md 确认需求
- [ ] 更新 TODO.md 进度
- [ ] 运行测试确保稳定性

### 每天结束
- [ ] 提交代码到 git
- [ ] 更新文档
- [ ] 记录遇到的问题和解决方案

## 验证步骤

### 部署验证
```bash
# 启动服务
docker compose up -d

# 验证 Redis
docker compose exec redis redis-cli ping

# 验证 Celery
docker compose logs celery-worker

# 验证 Flower
open http://localhost:5555

# 验证 API
curl http://localhost:8000/docs
```

### 功能验证
```bash
# 创建工作流
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"name": "test-workflow", "description": "测试工作流"}'

# 添加任务
curl -X POST http://localhost:8000/api/v1/workflows/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "http-task", "task_type": "HTTP", "config": {"url": "http://httpbin.org/get"}}'

# 执行工作流
curl -X POST http://localhost:8000/api/v1/workflows/1/run

# 查看状态
curl http://localhost:8000/api/v1/workflows/1/runs
```

## 当前进度
- ✅ 阶段1-1: 移除前端文件和目录
- ✅ 阶段1-2: 更新 docker-compose.yml 配置
- ✅ 阶段1-3: 完成添加 Celery + Redis 依赖

## 阶段1 验证
```bash
# 启动基础设施服务
docker compose up -d redis

# 验证 Redis 服务
docker compose exec redis redis-cli ping  # 应返回 PONG

# 验证依赖安装
cd backend
uv pip show celery redis flower
```

## 下一步
开始执行阶段1-3：添加依赖并创建 Celery 配置