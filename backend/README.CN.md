# FastAPI 项目 - 后端

## 需求

* [Docker](https://www.docker.com/)。
* [uv](https://docs.astral.sh/uv/) 用于 Python 包和环境管理。

## Docker Compose

按照 [../development.md](../development.md) 中的指南启动本地开发环境。

## 一般工作流程

默认情况下，依赖项通过 [uv](https://docs.astral.sh/uv/) 管理，您可以访问该网站并安装它。

在 `./backend/` 目录下，您可以通过以下命令安装所有依赖项：

```console
$ uv sync
```

然后，您可以激活虚拟环境：

```console
$ source .venv/bin/activate
```

确保您的编辑器使用正确的 Python 虚拟环境，解释器路径为 `backend/.venv/bin/python`。

在 `./backend/app/models.py` 中修改或添加用于数据和 SQL 表的 SQLModel 模型，在 `./backend/app/api/` 中修改 API 端点，在 `./backend/app/crud.py` 中修改 CRUD（创建、读取、更新、删除）工具函数。

## VS Code

已经配置好可以通过 VS Code 调试器运行后端，这样您就可以使用断点、暂停和检查变量等功能。

该设置也已配置好，您可以通过 VS Code 的 Python 测试标签运行测试。

## Docker Compose 覆盖

在开发过程中，您可以更改 Docker Compose 设置，这些更改仅会影响本地开发环境，修改文件 `docker-compose.override.yml`。

对该文件的修改只会影响本地开发环境，不会影响生产环境。因此，您可以添加帮助开发流程的“临时”更改。

例如，后端代码所在的目录会在 Docker 容器中同步，将您修改的代码实时复制到容器内部的目录。这样，您可以立即测试您的更改，无需重新构建 Docker 镜像。这应该仅在开发过程中使用，对于生产环境，您应该使用最新版本的后端代码构建 Docker 镜像。但在开发过程中，这允许您非常快速地迭代。

另外，还有一个命令覆盖，它运行 `fastapi run --reload`，而不是默认的 `fastapi run`。它启动一个单独的服务器进程（与生产环境中的多个进程不同），并在代码更改时重新加载进程。请注意，如果您有语法错误并保存 Python 文件，程序会崩溃并退出，容器也会停止。之后，您可以通过修复错误并重新运行来重启容器：

```console
$ docker compose watch
```

另外，还有一个被注释掉的 `command` 覆盖，您可以取消注释并注释掉默认的命令。它使后端容器运行一个“无操作”进程，但保持容器存活。这允许您进入正在运行的容器并执行命令，例如进入 Python 解释器测试已安装的依赖项，或启动一个开发服务器，当检测到代码更改时会重新加载。

要进入容器并启动 `bash` 会话，您可以使用以下命令启动堆栈：

```console
$ docker compose watch
```

然后，在另一个终端中，通过 `exec` 进入运行中的容器：

```console
$ docker compose exec backend bash
```

您应该会看到如下输出：

```console
root@7f2607af31c3:/app#
```

这意味着您已进入容器中的 `bash` 会话，以 `root` 用户身份位于 `/app` 目录下，这个目录中有一个名为 "app" 的子目录，您的代码就存放在容器内部的 `/app/app` 目录中。

在这里，您可以使用 `fastapi run --reload` 命令运行调试模式的实时重载服务器。

```console
$ fastapi run --reload app/main.py
```

输出应类似于：

```console
root@7f2607af31c3:/app# fastapi run --reload app/main.py
```

然后按回车键。这将启动一个实时重载的服务器，检测到代码更改时会自动重载。

然而，如果没有检测到代码更改，但遇到语法错误，它会停止并报错。但因为容器仍在运行，并且您处于 Bash 会话中，所以可以在修复错误后通过重新运行相同的命令（按上箭头键，然后回车）来快速重启它。

...这一点说明了为什么让容器处于“空闲”状态并在 Bash 会话中启动实时重载服务器是很有用的。

## 后端测试

要测试后端，运行：

```console
$ bash ./scripts/test.sh
```

测试使用 Pytest 运行，您可以修改并添加测试到 `./backend/app/tests/` 目录。

如果您使用 GitHub Actions，测试将自动运行。

### 测试运行堆栈

如果您的堆栈已经启动，并且您只想运行测试，可以使用：

```bash
docker compose exec backend bash scripts/tests-start.sh
```

该 `/app/scripts/tests-start.sh` 脚本会在确保堆栈其余部分正在运行后调用 `pytest`。如果您需要将额外的参数传递给 `pytest`，您可以将它们传递给该命令，它们将被转发。

例如，要在遇到第一个错误时停止：

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### 测试覆盖率

运行测试时，会生成一个 `htmlcov/index.html` 文件，您可以在浏览器中打开它查看测试的覆盖率。

## 迁移

由于在本地开发时，您的应用目录作为卷挂载在容器内，您也可以在容器内使用 `alembic` 命令运行迁移，迁移代码会保存在您的应用目录中（而不仅仅保存在容器内）。因此，您可以将其添加到 Git 仓库中。

确保每次修改模型时创建一个“修订”，并使用该修订“升级”您的数据库。因为这将更新数据库中的表。否则，您的应用可能会出现错误。

* 在后端容器中启动交互式会话：

```console
$ docker compose exec backend bash
```

* Alembic 已经配置为从 `./backend/app/models.py` 导入您的 SQLModel 模型。

* 修改模型后（例如，添加列），在容器内创建修订，例如：

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* 将在 alembic 目录中生成的文件提交到 Git 仓库。

* 创建修订后，运行数据库迁移（这实际上会更改数据库）：

```console
$ alembic upgrade head
```

如果您不想使用迁移，可以取消注释文件 `./backend/app/core/db.py` 中以如下结尾的行：

```python
SQLModel.metadata.create_all(engine)
```

并注释掉文件 `scripts/prestart.sh` 中包含以下内容的行：

```console
$ alembic upgrade head
```

如果您不想使用默认模型并且想从一开始就移除或修改它们，且不需要任何之前的修订，您可以删除 `./backend/app/alembic/versions/` 目录下的修订文件（`.py` 文件）。然后，按照上面的方法创建第一次迁移。

## 邮件模板

邮件模板位于 `./backend/app/email-templates/` 目录下。这里有两个目录：`build` 和 `src`。`src` 目录包含用于构建最终邮件模板的源文件。`build` 目录包含最终的邮件模板，这些模板将被应用程序使用。

在继续之前，确保您在 VS Code 中安装了 [MJML 扩展](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml)。

安装 MJML 扩展后，您可以在 `src` 目录中创建新的邮件模板。创建新的邮件模板后，打开 `.mjml` 文件，并在编辑器中打开命令面板（`Ctrl+Shift+P`），搜索 `MJML: Export to HTML`。这将把 `.mjml` 文件转换为 `.html` 文件，您现在可以将其保存在 `build` 目录中。
