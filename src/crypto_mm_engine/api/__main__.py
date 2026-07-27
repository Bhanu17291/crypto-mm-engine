from __future__ import annotations

import asyncio
import logging
import os

import uvicorn
from dotenv import load_dotenv

from crypto_mm_engine.api.server import create_app
from crypto_mm_engine.live.config import load_live_config
from crypto_mm_engine.live.logging_setup import configure_logging
from crypto_mm_engine.live.runner import PaperTradingRunner

logger = logging.getLogger(__name__)


async def _main() -> None:
    load_dotenv()
    configure_logging()
    config = load_live_config()
    runner = PaperTradingRunner(config)
    app = create_app(runner)

    port = int(os.environ.get("API_PORT", "8010"))
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))

    logger.info("starting paper trading runner and API server on port %d", port)
    await asyncio.gather(runner.run(), server.serve())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
