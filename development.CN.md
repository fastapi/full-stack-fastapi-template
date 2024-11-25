# FastAPI 项目 - 开发指南

## Docker Compose

* 使用 Docker Compose 启动本地开发环境：

```bash
docker compose watch
```

* 启动后，您可以在浏览器中访问以下地址与项目交互：

- 前端（通过 Docker 构建，根据路径处理路由）：[http://localhost:5173](http://localhost:5173)
- 后端（基于 OpenAPI 的 JSON Web API）：[http://localhost:8000](http://localhost:8000)
- 自动交互式文档（Swagger UI 提供的 OpenAPI 文档）：[http://localhost:8000/docs](http://localhost:8000/docs)
- Adminer（数据库 Web 管理界面）：[http://localhost:8080](http://localhost:8080)
- Traefik UI（查看代理如何处理路由）：[http://localhost:8090](http://localhost:8090)

**注意**：第一次启动时，可能需要几分钟完成准备。期间后端会等待数据库就绪并完成配置。您可以通过查看日志来监控其状态。

在另一个终端窗口运行以下命令查看日志：

```bash
docker compose logs
```

如果需要查看特定服务的日志，请附加服务名称，例如：

```bash
docker compose logs backend
```

---

## 本地开发

Docker Compose 文件配置了每个服务在 `localhost` 上的不同端口。

对于后端和前端，它们使用与本地开发服务器相同的端口，因此后端服务地址为 `http://localhost:8000`，前端服务地址为 `http://localhost:5173`。

这样，您可以关闭某个 Docker Compose 服务，启动其本地开发服务器，一切仍然正常运行，因为它们使用相同的端口。

例如，可以关闭 `frontend` 服务并在另一个终端中运行以下命令：

```bash
docker compose stop frontend
```

然后启动本地前端开发服务器：

```bash
cd frontend
npm run dev
```

或者，您也可以停止 `backend` Docker Compose 服务：

```bash
docker compose stop backend
```

接着启动本地后端开发服务器：

```bash
cd backend
fastapi dev app/main.py
```

## 在 `localhost.tiangolo.com` 使用 Docker Compose

当您启动 Docker Compose 堆栈时，它默认使用 `localhost`，每个服务（后端、前端、Adminer 等）使用不同的端口。

当您部署到生产（或测试）环境时，每个服务将部署到不同的子域，例如后端使用 `api.example.com`，前端使用 `dashboard.example.com`。

在 [部署指南](deployment.md) 中，您可以阅读关于 Traefik（配置的代理）的内容。Traefik 负责根据子域将流量路由到每个服务。

如果您想在本地测试服务是否正常工作，可以编辑本地 `.env` 文件并修改：

```dotenv
DOMAIN=localhost.tiangolo.com
```

Docker Compose 文件将使用此配置来设置服务的基础域名。

Traefik 会将 `api.localhost.tiangolo.com` 的流量路由到后端，将 `dashboard.localhost.tiangolo.com` 的流量路由到前端。

`localhost.tiangolo.com` 是一个特殊的域名，其所有子域都指向 `127.0.0.1`，因此可以用于本地开发。

修改完成后，重新运行以下命令：

```bash
docker compose watch
```

在生产环境中部署时，Traefik 的主实例通常在 Docker Compose 配置外部。用于本地开发的 Traefik 包含在 `docker-compose.override.yml` 中，用于测试子域是否按预期工作（例如 `api.localhost.tiangolo.com` 和 `dashboard.localhost.tiangolo.com`）。

---

## Docker Compose 文件和环境变量

项目包含一个主要的 `docker-compose.yml` 文件，包含适用于整个堆栈的所有配置，由 `docker compose` 自动使用。

同时还有一个 `docker-compose.override.yml` 文件，提供开发环境的覆盖配置，例如将源代码挂载为卷。`docker compose` 会自动将该文件的配置叠加到 `docker-compose.yml` 上。

这些 Docker Compose 文件会使用 `.env` 文件中的配置，将其作为环境变量注入容器中。

此外，还会使用一些在运行 `docker compose` 命令前由脚本设置的环境变量。

在修改环境变量后，请重新启动堆栈：

```bash
docker compose watch
```

---

## `.env` 文件

`.env` 文件包含所有配置、生成的密钥和密码等。

根据您的工作流程，可能需要将其排除在 Git 版本控制之外，例如项目是公开的情况下。在这种情况下，您需要确保为 CI 工具设置获取 `.env` 文件的方法，以便在构建或部署时使用。

一种方法是将每个环境变量添加到您的 CI/CD 系统中，并更新 `docker-compose.yml` 文件以读取这些特定的环境变量，而不是直接从 `.env` 文件读取。

---

## 预提交钩子和代码格式化

项目使用 [pre-commit](https://pre-commit.com/) 工具来进行代码格式化和检查。

安装后，该工具会在每次 Git 提交之前运行，从而确保代码一致且格式化良好。

项目根目录中有 `.pre-commit-config.yaml` 文件，包含 pre-commit 的配置。

---

### 安装 pre-commit 以自动运行

`pre-commit` 已作为项目依赖项的一部分，但您也可以选择按照 [官方文档](https://pre-commit.com/) 的说明全局安装它。

在安装并使 `pre-commit` 工具可用后，需要将其“安装”到本地仓库，以便在每次提交之前自动运行。

如果使用 `uv`，可以通过以下命令完成：

```bash
❯ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

现在，当您尝试提交时，例如运行：

```bash
git commit
```

pre-commit 会运行并检查、格式化您要提交的代码，并要求您使用 Git 再次添加代码（暂存）后再提交。

然后，您可以通过 `git add` 添加已修改/修复的文件，再次提交即可。

#### 手动运行 pre-commit 钩子

您也可以手动运行 `pre-commit` 钩子，检查所有文件。使用 `uv` 可以执行以下命令：

```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

---

## URL 列表

生产或测试环境的 URL 将使用相同的路径，但域名会替换为您自己的。

### 开发环境 URL

用于本地开发的 URL。

- **前端**: [http://localhost:5173](http://localhost:5173)
- **后端**: [http://localhost:8000](http://localhost:8000)
- **自动交互式文档 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **自动备用文档 (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Adminer**: [http://localhost:8080](http://localhost:8080)
- **Traefik UI**: [http://localhost:8090](http://localhost:8090)
- **MailCatcher**: [http://localhost:1080](http://localhost:1080)

---

### 配置了 `localhost.tiangolo.com` 的开发环境 URL

用于本地开发的 URL。

- **前端**: [http://dashboard.localhost.tiangolo.com](http://dashboard.localhost.tiangolo.com)
- **后端**: [http://api.localhost.tiangolo.com](http://api.localhost.tiangolo.com)
- **自动交互式文档 (Swagger UI)**: [http://api.localhost.tiangolo.com/docs](http://api.localhost.tiangolo.com/docs)
- **自动备用文档 (ReDoc)**: [http://api.localhost.tiangolo.com/redoc](http://api.localhost.tiangolo.com/redoc)
- **Adminer**: [http://localhost.tiangolo.com:8080](http://localhost.tiangolo.com:8080)
- **Traefik UI**: [http://localhost.tiangolo.com:8090](http://localhost.tiangolo.com:8090)
- **MailCatcher**: [http://localhost.tiangolo.com:1080](http://localhost.tiangolo.com:1080)