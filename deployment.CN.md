# FastAPI 项目 - 部署指南

您可以使用 Docker Compose 将项目部署到远程服务器。

本项目默认需要一个 **Traefik 代理** 来处理与外界的通信和 HTTPS 证书。

您可以使用 CI/CD（持续集成和持续部署）系统实现自动化部署，并提供了 GitHub Actions 的配置示例。

但在此之前需要先完成一些设置步骤。🤓

---

## 准备工作

1. 准备一个远程服务器并确保其可用。
2. 将您的域名的 DNS 记录指向该服务器的 IP 地址。
3. 为您的域名配置通配符子域（Wildcard Subdomain），例如 `*.fastapi-project.example.com`。  
   这将允许不同的组件通过不同的子域访问，如：
   - `dashboard.fastapi-project.example.com`
   - `api.fastapi-project.example.com`
   - `traefik.fastapi-project.example.com`
   - `adminer.fastapi-project.example.com`
   - `staging` 环境也可以类似访问：
     - `dashboard.staging.fastapi-project.example.com`
     - `adminer.staging.fastapi-project.example.com`
4. 在远程服务器上安装并配置 [Docker](https://docs.docker.com/engine/install/)（需要安装 Docker Engine，而不是 Docker Desktop）。

---

## 公共 Traefik 代理

我们需要一个 **Traefik 代理** 来处理传入的连接和 HTTPS 证书。

以下步骤仅需执行一次。

---

### 配置 Traefik 的 Docker Compose 文件

1. 在远程服务器上创建一个目录用于存储 Traefik 的 Docker Compose 文件：

   ```bash
   mkdir -p /root/code/traefik-public/
   ```

2. 将 Traefik 的 Docker Compose 文件复制到服务器。  
   您可以在本地终端使用 `rsync` 命令完成复制：

   ```bash
   rsync -a docker-compose.traefik.yml root@your-server.example.com:/root/code/traefik-public/
   ```

---

### 创建 Traefik 公共网络

Traefik 需要一个名为 `traefik-public` 的 Docker **公共网络**与您的应用栈进行通信。

这种方式可以通过一个 Traefik 公共代理处理所有的外部通信（HTTP 和 HTTPS），并在代理后端部署一个或多个应用栈（不同域名下的服务，即便它们位于同一台服务器上）。

在远程服务器上运行以下命令以创建 `traefik-public` 网络：

```bash
docker network create traefik-public
```

### Traefik 环境变量配置

Traefik 的 Docker Compose 文件需要您在终端中预先设置一些环境变量。可以在远程服务器上运行以下命令完成配置：

1. 设置 HTTP Basic Auth 的用户名，例如：

   ```bash
   export USERNAME=admin
   ```

2. 设置 HTTP Basic Auth 的密码，例如：

   ```bash
   export PASSWORD=changethis
   ```

3. 使用 `openssl` 生成密码的“哈希值”并将其存储到环境变量中：

   ```bash
   export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
   ```

   如果需要验证哈希值是否正确，可以打印出来：

   ```bash
   echo $HASHED_PASSWORD
   ```

4. 设置服务器的域名，例如：

   ```bash
   export DOMAIN=fastapi-project.example.com
   ```

5. 设置 Let's Encrypt 的邮箱地址，例如：

   ```bash
   export EMAIL=admin@example.com
   ```

   **注意**：必须使用实际邮箱地址，`@example.com` 结尾的邮箱地址将无法使用。

---

### 启动 Traefik 的 Docker Compose 服务

进入您在远程服务器中存放 Traefik Docker Compose 文件的目录：

```bash
cd /root/code/traefik-public/
```

确保环境变量已设置，并且 `docker-compose.traefik.yml` 文件已就位，运行以下命令启动 Traefik：

```bash
docker compose -f docker-compose.traefik.yml up -d
```

---

## 部署 FastAPI 项目

在设置好 Traefik 后，您可以使用 Docker Compose 部署 FastAPI 项目。

**提示**：可以直接跳到有关使用 GitHub Actions 实现持续部署的部分。

---

### 环境变量配置

您需要首先设置一些环境变量。

1. 设置运行环境，默认为 `local`（用于开发环境），在部署到服务器时，可以设置为 `staging` 或 `production`：

   ```bash
   export ENVIRONMENT=production
   ```

2. 设置域名，默认为 `localhost`（用于开发环境），在部署时应使用自己的域名，例如：

   ```bash
   export DOMAIN=fastapi-project.example.com
   ```

3. 配置其他变量：

   - **`PROJECT_NAME`**：项目名称，用于 API 文档和邮件中显示。
   - **`STACK_NAME`**：Docker Compose 栈的名称，用于标签和项目名。可以为不同环境（如 `staging` 和 `production`）使用不同的值，例如 `fastapi-project-example-com` 和 `staging-fastapi-project-example-com`。
   - **`BACKEND_CORS_ORIGINS`**：允许的 CORS 来源列表，用逗号分隔。
   - **`SECRET_KEY`**：用于签发令牌的密钥。
   - **`FIRST_SUPERUSER`**：首个超级用户的邮箱地址，可用于创建其他用户。
   - **`FIRST_SUPERUSER_PASSWORD`**：首个超级用户的密码。
   - **`SMTP_HOST`**：SMTP 服务器主机地址（根据邮件服务商提供，如 Mailgun、Sparkpost、Sendgrid）。
   - **`SMTP_USER`** 和 **`SMTP_PASSWORD`**：SMTP 服务器的用户名和密码。
   - **`EMAILS_FROM_EMAIL`**：发送邮件的邮箱地址。
   - **`POSTGRES_SERVER`**：PostgreSQL 服务器的主机名，默认值为 `db`（Docker Compose 提供的默认值）。
   - **`POSTGRES_PORT`**：PostgreSQL 服务器的端口号，通常无需更改。
   - **`POSTGRES_PASSWORD`**：PostgreSQL 的密码。
   - **`POSTGRES_USER`** 和 **`POSTGRES_DB`**：分别为 PostgreSQL 用户和数据库名，通常可以保留默认值。
   - **`SENTRY_DSN`**：Sentry 的 DSN 地址（如果您使用 Sentry）。

---

## GitHub Actions 环境变量配置

有一些环境变量仅供 GitHub Actions 使用，您可以进行以下配置：

1. **`LATEST_CHANGES`**：用于 GitHub Action [latest-changes](https://github.com/tiangolo/latest-changes) 自动生成基于合并 PR 的发布说明。需要个人访问令牌，详细信息请查看文档。
2. **`SMOKESHOW_AUTH_KEY`**：用于 [Smokeshow](https://github.com/samuelcolvin/smokeshow) 管理和发布代码覆盖率。按照 Smokeshow 的说明创建（免费）认证密钥。

### 生成密钥

`.env` 文件中的某些环境变量默认值为 `changethis`。

您需要用密钥替换这些值。要生成密钥，可以运行以下命令：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的内容作为密码或密钥。如果需要多个密钥，可以再次运行该命令以生成新的密钥。

---

### 使用 Docker Compose 部署

在设置好环境变量后，可以使用以下命令通过 Docker Compose 部署项目：

```bash
docker compose -f docker-compose.yml up -d
```

在生产环境中，通常不需要 `docker-compose.override.yml` 中的开发环境覆盖配置，因此明确指定仅使用 `docker-compose.yml` 文件。

---

## 持续部署（CD）

您可以使用 GitHub Actions 自动部署项目。😎

可以为多个环境配置自动部署。

此项目已经配置了两个环境：`staging` 和 `production`。🚀

---

### 安装 GitHub Actions Runner

1. 在远程服务器上为 GitHub Actions 创建一个用户：

   ```bash
   sudo adduser github
   ```

2. 为 `github` 用户添加 Docker 权限：

   ```bash
   sudo usermod -aG docker github
   ```

3. 临时切换到 `github` 用户：

   ```bash
   sudo su - github
   ```

4. 转到 `github` 用户的主目录：

   ```bash
   cd
   ```

5. [按照官方指南安装 GitHub Actions 自托管 Runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners#adding-a-self-hosted-runner-to-a-repository)。

   在配置过程中，系统会要求您为环境添加标签，例如 `production`，稍后也可以添加标签。

6. 配置完成后，指南会提示运行一个命令以启动 Runner。需要注意的是，如果进程被终止或者与服务器的连接中断，Runner 将停止运行。

---

### 将 Runner 配置为服务

为了确保 Runner 能在系统启动时运行并持续工作，可以将其安装为服务。具体步骤如下：

1. 退出 `github` 用户并返回到 `root` 用户：

   ```bash
   exit
   ```

   退出后，您将返回到之前的用户，并位于之前的工作目录。

2. 确保成为 `root` 用户（如果尚未是）：

   ```bash
   sudo su
   ```

3. 作为 `root` 用户，转到 `github` 用户主目录下的 `actions-runner` 目录：

   ```bash
   cd /home/github/actions-runner
   ```

4. 使用 `github` 用户安装自托管 Runner 服务：

   ```bash
   ./svc.sh install github
   ```

5. 启动服务：

   ```bash
   ./svc.sh start
   ```

6. 检查服务状态：

   ```bash
   ./svc.sh status
   ```

您可以在官方指南中了解更多信息：[配置自托管 Runner 应用程序为服务](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)。

### 配置 Secrets

在您的代码仓库中，为所需的环境变量配置 Secrets，包括 `SECRET_KEY` 等。您可以参考 [GitHub 官方指南](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) 了解如何设置仓库 Secrets。

当前的 GitHub Actions 工作流需要以下 Secrets：

- `DOMAIN_PRODUCTION`
- `DOMAIN_STAGING`
- `STACK_NAME_PRODUCTION`
- `STACK_NAME_STAGING`
- `EMAILS_FROM_EMAIL`
- `FIRST_SUPERUSER`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `LATEST_CHANGES`
- `SMOKESHOW_AUTH_KEY`

---

## GitHub Actions 部署工作流

`.github/workflows` 目录中已经配置了用于部署的 GitHub Actions 工作流，分别适用于以下环境（根据标签区分的 GitHub Actions Runner）：

- `staging`：当推送（或合并）到 `master` 分支时触发。
- `production`：当发布一个 Release 时触发。

如果需要添加额外的环境，可以以这些配置为基础进行修改。

---

## URLs

将 `fastapi-project.example.com` 替换为您的域名。

### 主 Traefik 仪表盘

Traefik UI: `https://traefik.fastapi-project.example.com`

### 生产环境

- 前端：`https://dashboard.fastapi-project.example.com`
- 后端 API 文档：`https://api.fastapi-project.example.com/docs`
- 后端 API 基础 URL：`https://api.fastapi-project.example.com`
- Adminer：`https://adminer.fastapi-project.example.com`

### 测试环境（Staging）

- 前端：`https://dashboard.staging.fastapi-project.example.com`
- 后端 API 文档：`https://api.staging.fastapi-project.example.com/docs`
- 后端 API 基础 URL：`https://api.staging.fastapi-project.example.com`
- Adminer：`https://adminer.staging.fastapi-project.example.com`
