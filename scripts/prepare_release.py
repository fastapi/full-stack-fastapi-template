"""Prepare a release by updating and extracting release notes."""

import re
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

import typer

RELEASE_NOTES_FILE = Path("release-notes.md")
RELEASE_NOTES_HEADER = "# Release Notes\n\n"
LATEST_CHANGES_HEADER = "## Latest Changes"
VERSION_HEADING_PATTERN = re.compile(r"(?m)^## (\d+\.\d+\.\d+)(?: \([^)]+\))?$")
BumpType = Literal["major", "minor", "patch"]

app = typer.Typer()


def parse_version(version: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Invalid version: {version!r}. Expected format: X.Y.Z")
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def get_current_version(content: str, release_notes_file: Path) -> str:
    match = VERSION_HEADING_PATTERN.search(content)
    if not match:
        raise RuntimeError(f"Could not find a version section in {release_notes_file}")
    return match.group(1)


def bump_version(version: str, bump: BumpType) -> str:
    major, minor, patch = parse_version(version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def update_release_notes(
    content: str, version: str, release_date: date, release_notes_file: Path
) -> str:
    latest_header = f"{RELEASE_NOTES_HEADER}{LATEST_CHANGES_HEADER}\n"
    if not content.startswith(latest_header):
        raise RuntimeError(f"{release_notes_file} must start with {latest_header!r}")
    if re.search(rf"^## {re.escape(version)}(?: \([^)]+\))?$", content, re.M):
        raise RuntimeError(f"Release notes already contain a section for {version}")

    current_version = get_current_version(content, release_notes_file)
    if parse_version(version) <= parse_version(current_version):
        raise RuntimeError(
            f"New version {version} must be greater than current version "
            f"{current_version}"
        )

    current_match = VERSION_HEADING_PATTERN.search(content)
    assert current_match is not None
    latest_changes = content[len(latest_header) : current_match.start()].strip()
    if not latest_changes:
        raise RuntimeError("The Latest Changes section is empty")

    release_header = f"## {version} ({release_date.isoformat()})"
    return content.replace(
        latest_header,
        f"{RELEASE_NOTES_HEADER}{LATEST_CHANGES_HEADER}\n\n{release_header}\n",
        1,
    )


def get_release_notes_body(content: str, version: str, release_notes_file: Path) -> str:
    version_heading = re.compile(rf"(?m)^## {re.escape(version)}(?: \([^)]+\))?$")
    match = version_heading.search(content)
    if not match:
        raise RuntimeError(
            f"Could not find release notes section for {version} in "
            f"{release_notes_file}"
        )

    next_match = VERSION_HEADING_PATTERN.search(content, match.end())
    end = next_match.start() if next_match else len(content)
    body = content[match.end() : end].strip()
    if not body:
        raise RuntimeError(
            f"Release notes section for {version} in {release_notes_file} is empty"
        )
    return f"{body}\n"


def prepare_release(
    bump: BumpType, release_date: date, release_notes_file: Path
) -> str:
    content = release_notes_file.read_text(encoding="utf-8")
    version = bump_version(get_current_version(content, release_notes_file), bump)
    release_notes_file.write_text(
        update_release_notes(content, version, release_date, release_notes_file),
        encoding="utf-8",
    )
    return version


@app.command()
def prepare(
    bump: Annotated[
        BumpType,
        typer.Argument(help="The release bump to make: major, minor, or patch."),
    ],
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            writable=True,
            help="Path to the release notes Markdown file.",
        ),
    ] = RELEASE_NOTES_FILE,
    release_date: Annotated[
        str,
        typer.Option(
            "--date",
            help="Release date in YYYY-MM-DD format. Defaults to today.",
        ),
    ] = date.today().isoformat(),
) -> None:
    parsed_release_date = date.fromisoformat(release_date or date.today().isoformat())
    version = prepare_release(bump, parsed_release_date, release_notes_file)
    typer.echo(f"Prepared release {version} ({parsed_release_date.isoformat()})")


@app.command()
def current_version(
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the release notes Markdown file.",
        ),
    ] = RELEASE_NOTES_FILE,
) -> None:
    typer.echo(
        get_current_version(
            release_notes_file.read_text(encoding="utf-8"), release_notes_file
        )
    )


@app.command()
def release_notes(
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the release notes Markdown file.",
        ),
    ] = RELEASE_NOTES_FILE,
) -> None:
    content = release_notes_file.read_text(encoding="utf-8")
    version = get_current_version(content, release_notes_file)
    typer.echo(
        get_release_notes_body(content, version, release_notes_file),
        nl=False,
    )


if __name__ == "__main__":
    app()
