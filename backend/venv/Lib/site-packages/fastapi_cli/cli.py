import logging
from pathlib import Path
from typing import Any, List, Union

import typer
from rich import print
from rich.tree import Tree
from typing_extensions import Annotated

from fastapi_cli.discover import get_import_data
from fastapi_cli.exceptions import FastAPICLIException

from . import __version__
from .logging import setup_logging
from .utils.cli import get_rich_toolkit, get_uvicorn_log_config

app = typer.Typer(rich_markup_mode="rich")

logger = logging.getLogger(__name__)


try:
    import uvicorn
except ImportError:  # pragma: no cover
    uvicorn = None  # type: ignore[assignment]


def version_callback(value: bool) -> None:
    if value:
        print(f"FastAPI CLI version: [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[
        Union[bool, None],
        typer.Option(
            "--version", help="Show the version and exit.", callback=version_callback
        ),
    ] = None,
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """
    FastAPI CLI - The [bold]fastapi[/bold] command line app. 😎

    Manage your [bold]FastAPI[/bold] projects, run your FastAPI apps, and more.

    Read more in the docs: [link=https://fastapi.tiangolo.com/fastapi-cli/]https://fastapi.tiangolo.com/fastapi-cli/[/link].
    """

    log_level = logging.DEBUG if verbose else logging.INFO

    setup_logging(level=log_level)


def _get_module_tree(module_paths: List[Path]) -> Tree:
    root = module_paths[0]
    name = f"🐍 {root.name}" if root.is_file() else f"📁 {root.name}"

    root_tree = Tree(name)

    if root.is_dir():
        root_tree.add("[dim]🐍 __init__.py[/dim]")

    tree = root_tree
    for sub_path in module_paths[1:]:
        sub_name = (
            f"🐍 {sub_path.name}" if sub_path.is_file() else f"📁 {sub_path.name}"
        )
        tree = tree.add(sub_name)
        if sub_path.is_dir():
            tree.add("[dim]🐍 __init__.py[/dim]")

    return root_tree


def _run(
    path: Union[Path, None] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: Union[int, None] = None,
    root_path: str = "",
    command: str,
    app: Union[str, None] = None,
    proxy_headers: bool = False,
) -> None:
    with get_rich_toolkit() as toolkit:
        server_type = "development" if command == "dev" else "production"

        toolkit.print_title(f"Starting {server_type} server 🚀", tag="FastAPI")
        toolkit.print_line()

        toolkit.print(
            "Searching for package file structure from directories with [blue]__init__.py[/blue] files"
        )

        try:
            import_data = get_import_data(path=path, app_name=app)
        except FastAPICLIException as e:
            toolkit.print_line()
            toolkit.print(f"[error]{e}")
            raise typer.Exit(code=1) from None

        logger.debug(f"Importing from {import_data.module_data.extra_sys_path}")
        logger.debug(f"Importing module {import_data.module_data.module_import_str}")

        module_data = import_data.module_data
        import_string = import_data.import_string

        toolkit.print(f"Importing from {module_data.extra_sys_path}")
        toolkit.print_line()

        root_tree = _get_module_tree(module_data.module_paths)

        toolkit.print(root_tree, tag="module")
        toolkit.print_line()

        toolkit.print(
            "Importing the FastAPI app object from the module with the following code:",
            tag="code",
        )
        toolkit.print_line()
        toolkit.print(
            f"[underline]from [bold]{module_data.module_import_str}[/bold] import [bold]{import_data.app_name}[/bold]"
        )
        toolkit.print_line()

        toolkit.print(
            f"Using import string: [blue]{import_string}[/]",
            tag="app",
        )

        url = f"http://{host}:{port}"
        url_docs = f"{url}/docs"

        toolkit.print_line()
        toolkit.print(
            f"Server started at [link={url}]{url}[/]",
            f"Documentation at [link={url_docs}]{url_docs}[/]",
            tag="server",
        )

        if command == "dev":
            toolkit.print_line()
            toolkit.print(
                "Running in development mode, for production use: [bold]fastapi run[/]",
                tag="tip",
            )

        if not uvicorn:
            raise FastAPICLIException(
                "Could not import Uvicorn, try running 'pip install uvicorn'"
            ) from None

        toolkit.print_line()
        toolkit.print("Logs:")
        toolkit.print_line()

        uvicorn.run(
            app=import_string,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            root_path=root_path,
            proxy_headers=proxy_headers,
            log_config=get_uvicorn_log_config(),
        )


@app.command()
def dev(
    path: Annotated[
        Union[Path, None],
        typer.Argument(
            help="A path to a Python file or package directory (with [blue]__init__.py[/blue] files) containing a [bold]FastAPI[/bold] app. If not provided, a default set of paths will be tried."
        ),
    ] = None,
    *,
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app."
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = True,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    app: Annotated[
        Union[str, None],
        typer.Option(
            help="The name of the variable that contains the [bold]FastAPI[/bold] app in the imported module or package. If not provided, it is detected automatically."
        ),
    ] = None,
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
) -> Any:
    """
    Run a [bold]FastAPI[/bold] app in [yellow]development[/yellow] mode. 🧪

    This is equivalent to [bold]fastapi run[/bold] but with [bold]reload[/bold] enabled and listening on the [blue]127.0.0.1[/blue] address.

    It automatically detects the Python module or package that needs to be imported based on the file or directory path passed.

    If no path is passed, it tries with:

    - [blue]main.py[/blue]
    - [blue]app.py[/blue]
    - [blue]api.py[/blue]
    - [blue]app/main.py[/blue]
    - [blue]app/app.py[/blue]
    - [blue]app/api.py[/blue]

    It also detects the directory that needs to be added to the [bold]PYTHONPATH[/bold] to make the app importable and adds it.

    It detects the [bold]FastAPI[/bold] app object to use. By default it looks in the module or package for an object named:

    - [blue]app[/blue]
    - [blue]api[/blue]

    Otherwise, it uses the first [bold]FastAPI[/bold] app found in the imported module or package.
    """
    _run(
        path=path,
        host=host,
        port=port,
        reload=reload,
        root_path=root_path,
        app=app,
        command="dev",
        proxy_headers=proxy_headers,
    )


@app.command()
def run(
    path: Annotated[
        Union[Path, None],
        typer.Argument(
            help="A path to a Python file or package directory (with [blue]__init__.py[/blue] files) containing a [bold]FastAPI[/bold] app. If not provided, a default set of paths will be tried."
        ),
    ] = None,
    *,
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app."
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = False,
    workers: Annotated[
        Union[int, None],
        typer.Option(
            help="Use multiple worker processes. Mutually exclusive with the --reload flag."
        ),
    ] = None,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    app: Annotated[
        Union[str, None],
        typer.Option(
            help="The name of the variable that contains the [bold]FastAPI[/bold] app in the imported module or package. If not provided, it is detected automatically."
        ),
    ] = None,
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
) -> Any:
    """
    Run a [bold]FastAPI[/bold] app in [green]production[/green] mode. 🚀

    This is equivalent to [bold]fastapi dev[/bold] but with [bold]reload[/bold] disabled and listening on the [blue]0.0.0.0[/blue] address.

    It automatically detects the Python module or package that needs to be imported based on the file or directory path passed.

    If no path is passed, it tries with:

    - [blue]main.py[/blue]
    - [blue]app.py[/blue]
    - [blue]api.py[/blue]
    - [blue]app/main.py[/blue]
    - [blue]app/app.py[/blue]
    - [blue]app/api.py[/blue]

    It also detects the directory that needs to be added to the [bold]PYTHONPATH[/bold] to make the app importable and adds it.

    It detects the [bold]FastAPI[/bold] app object to use. By default it looks in the module or package for an object named:

    - [blue]app[/blue]
    - [blue]api[/blue]

    Otherwise, it uses the first [bold]FastAPI[/bold] app found in the imported module or package.
    """
    _run(
        path=path,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        root_path=root_path,
        app=app,
        command="run",
        proxy_headers=proxy_headers,
    )


def main() -> None:
    app()
