import asyncio
import logging
import os
import signal
import sys

import nats
from diagnostic import DiagnosticService
from nats.aio import client

logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.INFO))

logger = logging.getLogger(__name__)


async def handle_exit(nc: client.Client, service: DiagnosticService):
    await service.dispose()
    await nc.drain()
    sys.exit(0)


async def main():
    nc = await nats.connect()
    diagnostic_service = DiagnosticService(nc)

    loop = asyncio.get_event_loop()
    for signame in ["SIGINT", "SIGQUIT", "SIGTERM"]:
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(handle_exit(nc, diagnostic_service)),
        )

    await diagnostic_service.start()


if __name__ == "__main__":
    asyncio.run(main())
