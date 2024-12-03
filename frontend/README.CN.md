# FastAPI 项目 - 前端

前端是使用 [Vite](https://vitejs.dev/)、[React](https://reactjs.org/)、[TypeScript](https://www.typescriptlang.org/)、[TanStack Query](https://tanstack.com/query)、[TanStack Router](https://tanstack.com/router) 和 [Chakra UI](https://chakra-ui.com/) 构建的。

## 前端开发

在开始之前，确保您的系统上已安装 Node 版本管理器（nvm）或 Fast Node 管理器（fnm）。

* 要安装 fnm，请按照 [官方 fnm 安装指南](https://github.com/Schniz/fnm#installation) 操作。如果您更喜欢 nvm，可以使用 [官方 nvm 安装指南](https://github.com/nvm-sh/nvm#installing-and-updating) 进行安装。

* 安装了 nvm 或 fnm 后，进入 `frontend` 目录：

```bash
cd frontend
```

* 如果 `.nvmrc` 文件中指定的 Node.js 版本未安装在您的系统上，您可以使用相应的命令进行安装：

```bash
# 使用 fnm
fnm install

# 使用 nvm
nvm install
```

* 安装完成后，切换到已安装的版本：

```bash
# 使用 fnm
fnm use

# 使用 nvm
nvm use
```

[中文](./README.CN.md)

* 在 `frontend` 目录中，安装所需的 NPM 包：

```bash
npm install
```

* 然后使用以下 `npm` 脚本启动实时服务器：

```bash
npm run dev
```

* 然后在浏览器中打开 http://localhost:5173/。

请注意，这个实时服务器并没有在 Docker 内部运行，它是为本地开发设计的，这是推荐的工作流程。一旦您对前端满意，您可以构建前端 Docker 镜像并启动它，以在类似生产的环境中进行测试。但每次更改时都构建镜像并不像运行本地开发服务器和实时重载那样高效。

查看 `package.json` 文件以查看其他可用选项。

### 移除前端

如果您正在开发一个仅 API 的应用，并且希望移除前端，您可以轻松完成：

* 删除 `./frontend` 目录。

* 在 `docker-compose.yml` 文件中，删除整个 `frontend` 服务/部分。

* 在 `docker-compose.override.yml` 文件中，删除整个 `frontend` 服务/部分。

完成后，您就得到了一个没有前端的（仅 API）应用。🤓

---

如果需要，您还可以从以下文件中移除 `FRONTEND` 环境变量：

* `.env`
* `./scripts/*.sh`

但是，这样做仅仅是为了清理，保留这些变量不会产生任何实际影响。

## 生成客户端

### 自动生成

* 激活后端虚拟环境。
* 在项目的顶层目录下，运行脚本：

```bash
./scripts/generate-frontend-client.sh
```

* 提交更改。

### 手动生成

* 启动 Docker Compose 堆栈。

* 从 `http://localhost/api/v1/openapi.json` 下载 OpenAPI JSON 文件，并将其复制到 `frontend` 目录的根目录下，命名为 `openapi.json`。

* 为了简化生成的前端客户端代码中的名称，通过运行以下脚本修改 `openapi.json` 文件：

```bash
node modify-openapi-operationids.js
```

* 生成前端客户端，运行：

```bash
npm run generate-client
```

* 提交更改。

请注意，每当后端发生更改（更改 OpenAPI 模式）时，您应该再次按照这些步骤来更新前端客户端。

## 使用远程 API

如果您希望使用远程 API，可以将环境变量 `VITE_API_URL` 设置为远程 API 的 URL。例如，您可以在 `frontend/.env` 文件中设置：

```env
VITE_API_URL=https://api.my-domain.example.com
```

然后，当您运行前端时，它将使用该 URL 作为 API 的基础 URL。

## 代码结构

前端代码的结构如下：

* `frontend/src` - 主要的前端代码。
* `frontend/src/assets` - 静态资源。
* `frontend/src/client` - 生成的 OpenAPI 客户端。
* `frontend/src/components` - 前端的不同组件。
* `frontend/src/hooks` - 自定义 hooks。
* `frontend/src/routes` - 前端的不同路由，包括页面。
* `theme.tsx` - Chakra UI 自定义主题。

## 使用 Playwright 进行端到端测试

前端包含了使用 Playwright 进行的初步端到端测试。要运行测试，您需要确保 Docker Compose 堆栈正在运行。使用以下命令启动堆栈：

```bash
docker compose up -d --wait backend
```

然后，您可以使用以下命令运行测试：

```bash
npx playwright test
```

您还可以以 UI 模式运行测试，以便看到浏览器并与其进行交互：

```bash
npx playwright test --ui
```

要停止并移除 Docker Compose 堆栈并清理测试中创建的数据，请使用以下命令：

```bash
docker compose down -v
```

要更新测试，导航到测试目录并修改现有的测试文件，或者根据需要添加新的测试文件。

有关编写和运行 Playwright 测试的更多信息，请参考官方 [Playwright 文档](https://playwright.dev/docs/intro)。