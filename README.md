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

### Paper trading (Binance Spot Testnet)

1. Generate API credentials at [testnet.binance.vision](https://testnet.binance.vision/) - Spot Testnet only, never mainnet keys.
2. Copy `.env.example` to `.env` and fill in `BINANCE_TESTNET_API_KEY` / `BINANCE_TESTNET_API_SECRET`. `.env` is gitignored.
3. Run:

```bash
uv run python -m crypto_mm_engine.live
```

This wires live market data into the same quoting/risk code the backtest harness uses; only the execution adapter and fill source (Binance's user data stream instead of a simulator) differ. Status and fills are logged as structured JSON lines to stdout.

### Live dashboard

The dashboard needs both the API server (which also runs the paper-trading runner) and the frontend dev server.

```bash
uv run python -m crypto_mm_engine.api   # http://localhost:8010 - requires the same .env as above
```

```bash
cd frontend
npm install     # first time only
npm run dev     # http://localhost:5180
```

The dashboard is empty/disconnected until the API server is both running and connected to Binance Testnet - it never fabricates data.
