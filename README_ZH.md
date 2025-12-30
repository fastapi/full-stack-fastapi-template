# DataAnalysis API - 数据分析服务

基于 FastAPI 全栈模板的数据分析 API 服务。

## 技术栈

### 后端
- **FastAPI** - 现代 Python Web 框架
- **SQLModel** - 基于 Pydantic 的 ORM
- **PostgreSQL** - 关系型数据库
- **Alembic** - 数据库迁移工具
- **Pydantic** - 数据验证

### 前端
- **React 19** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **TanStack Router** - 路由管理
- **Tailwind CSS** - CSS 框架
- **shadcn/ui** - UI 组件库

### DevOps
- **Docker Compose** - 容器编排
- **Traefik** - 反向代理
- **GitHub Actions** - CI/CD

## 功能特性

- 用户认证与授权（JWT）
- 邮件密码重置
- API 文档自动生成
- 深色模式支持
- 端到端测试（Playwright）
- 响应式设计

## 快速开始

### 前置要求

- **Docker** (推荐) 或
- **Python 3.12+** 和 **Node.js 20+**

### 使用 Docker Compose 启动（推荐）

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

访问：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

默认登录：
- 邮箱：`admin@example.com`
- 密码：`changethis`

> 生产环境**必须**修改默认密码！

## 详细本地开发

详见 [本地开发指南](./LOCAL_DEV_ZH.md)

## 部署

详见 [部署指南](./deployment.md)

## 开发

详见 [开发指南](./development.md)

## 许可证

MIT License
