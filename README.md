# crypto-mm-engine

## Goals

## Architecture Overview

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This installs the package plus the dev dependency group (pytest, black, ruff, mypy, pre-commit).

Install the git hooks once per clone:

```bash
uv run pre-commit install
```

### Common commands

```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run black .             # format
uv run mypy                # type-check
uv run pre-commit run --all-files   # run all hooks against the whole tree
```
