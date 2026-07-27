from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from crypto_mm_engine.live.config import load_live_config
from crypto_mm_engine.live.logging_setup import configure_logging
from crypto_mm_engine.live.runner import PaperTradingRunner


def main() -> None:
    load_dotenv()
    configure_logging()
    config = load_live_config()
    asyncio.run(PaperTradingRunner(config).run())


if __name__ == "__main__":
    main()
