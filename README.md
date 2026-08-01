# crypto-mm-engine

A cryptocurrency market-making engine implementing Avellaneda-Stoikov quoting,
with a backtester, a risk manager, and a live paper-trading runner against
Binance Spot Testnet - plus a full dashboard to watch it work.

## Goals

- Quote both sides of the book using the Avellaneda-Stoikov reservation-price
  model, not a static spread.
- Prove the strategy on historical data before ever touching a live
  connection: the backtest engine and the live runner share the same
  quoting, risk, and P&L code, so a strategy that works in backtest behaves
  identically live.
- Trade for real (on testnet) - real order book, real fills, real risk
  limits - not a simulation of a simulation.
- Never fabricate data anywhere in the stack, including the dashboard: an
  empty/disconnected state shows as empty, not as placeholder numbers.

## Architecture Overview

```
src/crypto_mm_engine/
  data/       order book model, synchronizer, Binance REST/WS market data,
              Parquet persistence, replay
  quoting/    Avellaneda-Stoikov reservation price + spread calculation
  backtest/   queue-position fill simulator, PnL tracker, backtest loop
  risk/       position/exposure limits, RiskManager
  execution/  shared execution-adapter interface; backtest and Binance
              testnet REST adapters implement it identically
  live/       paper-trading runner (live market data + Binance user data
              stream for real fills), structured JSON logging
  api/        FastAPI server exposing runner state over REST + a status
              WebSocket for the dashboard

frontend/     React + Vite dashboard: Dashboard, Order Book, Strategy,
              Risk, Execution, and Analytics pages, all reading the same
              live status the API server broadcasts
```

Backtest and live share one code path for quoting, risk, and P&L - only the
execution adapter and fill source differ (a queue-position simulator vs.
Binance's user data stream).

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

This is one of three tools in a personal "Trading Systems" suite, meant to
be reached through a shared landing page that proxies it under `/crypto`.
**Visit `http://localhost:5190/crypto`**, not `http://localhost:5180`
directly - the dev server's `base` is set to `/crypto/`, so the bare port
won't serve the app correctly on its own without the landing page's proxy
in front of it.

The dashboard is empty/disconnected until the API server is both running and connected to Binance Testnet - it never fabricates data.
