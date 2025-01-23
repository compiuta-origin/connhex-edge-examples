import asyncio
import logging
from abc import ABC

from common import listen_for_agent_commands, publish_message, start_heartbeat
from nats.aio import client, msg, subscription

logger = logging.getLogger(__name__)


class CustomService(ABC):
    service_name = ""

    def __init__(self, nc: client.Client, update_loop_interval_ms=60_000) -> None:
        self._nc = nc
        self._heartbeat_task = None
        self._update_loop_task = None
        self._sub: subscription.Subscription = None
        self._update_loop_interval_ms = update_loop_interval_ms

    #  Build your message.
    def _build_message(self):
        raise NotImplementedError

    async def _send_message(self) -> None:
        message = self._build_message()
        logger.debug(f"Publishing {self.service_name} message")
        await publish_message(self._nc, message)

    async def _start_update_loop(self):
        while True:
            await self._send_message()
            await asyncio.sleep(self._update_loop_interval_ms / 1000.0)

    async def start(self):
        logger.info(f"Starting {self.service_name} service...")

        async def handler(msg: msg.Msg):
            subject = msg.subject
            data = msg.data.decode()
            logger.info(f"Received command: [{subject}] {data}")

        self._sub = await listen_for_agent_commands(
            self._nc, self.service_name, handler
        )

        async with asyncio.TaskGroup() as tg:
            self._update_loop_task = tg.create_task(self._start_update_loop())
            self._heartbeat_task = tg.create_task(
                start_heartbeat(self._nc, self.service_name)
            )

    async def dispose(self) -> None:
        await self._sub.unsubscribe()
        self._heartbeat_task.cancel()
        self._update_loop_task.cancel()
