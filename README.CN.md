# 全栈 FastAPI 模板

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="测试"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="代码覆盖率"></a>

## 技术栈及功能

- ⚡ 后端 API 使用 [**FastAPI**](https://fastapi.tiangolo.com)。
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) 处理 Python 的 SQL 数据库交互（ORM）。
    - 🔍 [Pydantic](https://docs.pydantic.dev)（FastAPI 的依赖）负责数据验证和配置管理。
    - 💾 SQL 数据库采用 [PostgreSQL](https://www.postgresql.org)。
- 🚀 前端使用 [React](https://react.dev)。
    - 💃 使用 TypeScript、hooks、Vite 等现代前端技术。
    - 🎨 前端组件基于 [Chakra UI](https://chakra-ui.com)。
    - 🤖 自动生成的前端客户端。
    - 🧪 使用 [Playwright](https://playwright.dev) 进行端到端测试。
    - 🦇 支持暗黑模式。
- 🐋 使用 [Docker Compose](https://www.docker.com) 进行开发和生产环境配置。
- 🔒 默认支持安全的密码哈希。
- 🔑 基于 JWT（JSON Web Token）的认证机制。
- 📫 基于电子邮件的密码找回功能。
- ✅ 使用 [Pytest](https://pytest.org) 进行测试。
- 📞 采用 [Traefik](https://traefik.io) 作为反向代理/负载均衡器。
- 🚢 提供基于 Docker Compose 的部署指南，包括如何使用 Traefik 前端代理配置自动 HTTPS 证书。
- 🏭 基于 GitHub Actions 的 CI（持续集成）和 CD（持续部署）。

### 仪表盘登录

[![API 文档](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 仪表盘 - 管理员界面

[![API 文档](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 仪表盘 - 创建用户

[![API 文档](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 仪表盘 - 数据项

[![API 文档](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 仪表盘 - 用户设置

[![API 文档](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 仪表盘 - 暗黑模式

[![API 文档](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 交互式 API 文档

[![API 文档](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## 使用方法

您可以 **直接 fork 或克隆** 此仓库并按需使用。

✨ 它开箱即用。✨

### 如何使用私人仓库

如果您希望使用私人仓库，由于 GitHub 不允许更改 fork 仓库的可见性，您无法直接 fork 此仓库。

但您可以按照以下步骤操作：

- 创建一个新的 GitHub 仓库，例如 `my-full-stack`。
- 手动克隆此仓库，并将名称设置为您想使用的项目名称，例如 `my-full-stack`：

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
```

- 进入新目录：

```bash
cd my-full-stack
```

- 将远程仓库的地址设置为您新创建的仓库，可以从 GitHub 界面复制地址，例如：

```bash
git remote set-url origin git@github.com:octocat/my-full-stack.git
```

- 将此模板仓库添加为另一个 "remote"，以便以后获取更新：

```bash
git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git
```

- 将代码推送到您新的仓库：

```bash
git push -u origin master
```

### 从原始模板更新

在克隆仓库并进行修改后，您可能需要从此原始模板中获取最新的更改。

- 确保您已将原始仓库添加为远程仓库，可以通过以下命令检查：

```bash
git remote -v

origin    git@github.com:octocat/my-full-stack.git (fetch)
origin    git@github.com:octocat/my-full-stack.git (push)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
```

- 拉取最新的更改但不合并：

```bash
git pull --no-commit upstream master
```

这会下载此模板的最新更改但不会立即提交，您可以在提交前检查所有内容是否正确。

- 如果存在冲突，请在编辑器中解决它们。

- 完成后，提交更改：

```bash
git merge --continue
```

### 配置

您可以在 `.env` 文件中更新配置，以定制您的项目设置。

在部署前，至少需要更改以下配置项的值：

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

建议（并且应该）通过环境变量将这些配置从安全存储中传递。

详情请参阅 [deployment.md](./deployment.md) 文档。

### 生成密钥

`.env` 文件中的某些环境变量默认值为 `changethis`。

您需要用一个密钥替换这些默认值。可以运行以下命令生成密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的内容，用作密码或密钥。运行命令多次可生成不同的安全密钥。

---

## 如何使用 - 替代方式：使用 Copier

此仓库支持通过 [Copier](https://copier.readthedocs.io) 生成新项目。

Copier 会复制所有文件，询问您一些配置问题，并根据您的回答更新 `.env` 文件。

### 安装 Copier

您可以通过以下命令安装 Copier：

```bash
pip install copier
```

如果使用 [`pipx`](https://pipx.pypa.io/)，可以通过以下方式运行：

```bash
pipx install copier
```

**注意**：如果已安装 `pipx`，安装 Copier 是可选的，您可以直接运行它。

### 使用 Copier 生成项目

为您的新项目目录命名，例如 `my-awesome-project`。

进入目标父目录，并运行以下命令生成项目：

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

如果您使用了 `pipx`，且未安装 Copier，可以直接运行：

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**注意**：`--trust` 选项是必须的，它允许执行一个 [创建后脚本](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py)，以更新您的 `.env` 文件。

---

### 输入变量

Copier 会要求您提供一些配置数据。生成项目前，您可以先准备好这些数据。

但不用担心，生成后您可以随时在 `.env` 文件中修改这些设置。

以下是输入变量及其默认值（部分值会自动生成）：

- `project_name`：（默认值：`"FastAPI Project"`）项目名称，展示给 API 用户（在 .env 中）。
- `stack_name`：（默认值：`"fastapi-project"`）Docker Compose 的标签和项目名（无空格，无句号）（在 .env 中）。
- `secret_key`：（默认值：`"changethis"`）项目密钥，用于安全性（在 .env 中）。可使用上述方法生成。
- `first_superuser`：（默认值：`"admin@example.com"`）首位超级用户的邮箱（在 .env 中）。
- `first_superuser_password`：（默认值：`"changethis"`）首位超级用户的密码（在 .env 中）。
- `smtp_host`：（默认值：`""`）发送邮件的 SMTP 服务器地址，可在 .env 中稍后设置。
- `smtp_user`：（默认值：`""`）发送邮件的 SMTP 用户，可在 .env 中稍后设置。
- `smtp_password`：（默认值：`""`）发送邮件的 SMTP 密码，可在 .env 中稍后设置。
- `emails_from_email`：（默认值：`"info@example.com"`）发送邮件的账户，可在 .env 中稍后设置。
- `postgres_password`：（默认值：`"changethis"`）PostgreSQL 数据库密码（在 .env 中）。可使用上述方法生成。
- `sentry_dsn`：（默认值：`""`）Sentry 的 DSN，如果使用，可在 .env 中稍后设置。

---

## 后端开发

后端文档：[backend/README.md](./backend/README.CN.md)

## 前端开发

前端文档：[frontend/README.md](./frontend/README.CN.md)

## 部署

部署文档：[deployment.md](./deployment.CN.md)

## 开发

通用开发文档：[development.md](./development.CN.md)

内容包括使用 Docker Compose、自定义本地域名、`.env` 配置等。

## 更新日志

请查看 [release-notes.md](./release-notes.md)。

---

## 许可证

全栈 FastAPI 模板基于 MIT 许可证授权使用。
