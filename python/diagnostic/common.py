import asyncio
import json
import logging
from typing import Awaitable, Callable

from nats.aio import client, msg

logger = logging.getLogger(__name__)


async def publish_message(nc: client.Client, msg) -> None:
    await nc.publish("events.data", json.dumps(msg).encode("utf-8"))


async def start_heartbeat(nc: client.Client, service_name: str, interval_ms=10_000):
    while True:
        logger.debug("Publishing heartbeat...")
        # Add here your custom logic to check that everything is ok.
        await nc.publish(f"heartbeat.{service_name}.service")
        await asyncio.sleep(interval_ms / 1000.0)


def listen_for_agent_commands(
    nc: client.Client, service_name: str, handler: Callable[[msg.Msg], Awaitable[None]]
):
    return nc.subscribe(f"commands.{service_name}.>", cb=handler)
