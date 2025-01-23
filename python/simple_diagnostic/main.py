import asyncio
import json
import signal
import sys
from random import randrange
from time import time

import nats
from nats.aio import client, msg

SERVICE_NAME = "diagnostic"


# Sends a heartbeat message every 10s to notify
# connhex-edge-agent that this service is working properly.
# By default the connhex-edge-agent checks that all services have sent
# a heartbeat message within the last 10s (customizable).
# If a service didn't, it is marked as offline.
async def start_heartbeat(nc: client.Client) -> None:
    while True:
        print("Publishing heartbeat...")
        # Any custom logic that checks that everything is ok should be added here.
        await nc.publish(f"heartbeat.{SERVICE_NAME}.service")
        await asyncio.sleep(10_000 / 1000.0)


async def start_update_loop(nc: client.Client) -> None:
    while True:
        # Build a SenML message
        msg = [
            {
                "t": time(),
                "n": f"urn:cpt:{SERVICE_NAME}:battery-charge",
                "u": "%EL",
                "v": randrange(0, 100),
            },
        ]
        print(f"Sending message: {msg}")
        await nc.publish(f"events.data", json.dumps(msg).encode("utf-8"))
        await asyncio.sleep(60_000 / 1000.0)


async def main() -> None:
    async def handle_exit():
        await sub.unsubscribe()
        update_loop_task.cancel()
        heartbeat_task.cancel()
        sys.exit(0)

    for signame in ["SIGINT", "SIGQUIT", "SIGTERM"]:
        asyncio.get_event_loop().add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(handle_exit()),
        )

    nc = await nats.connect()

    async def handler(msg: msg.Msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"Received command: [{subject}] {data}")

    # Subscribe to NATS subject and listen for commands received.
    # ">" is used as wildcard, check https://docs.nats.io/nats-concepts/subjects#characters-allowed-for-subject-names
    sub = await nc.subscribe(f"commands.{SERVICE_NAME}.>", cb=handler)

    async with asyncio.TaskGroup() as tg:
        update_loop_task = tg.create_task(start_update_loop(nc))
        heartbeat_task = tg.create_task(start_heartbeat(nc))


if __name__ == "__main__":
    asyncio.run(main())
