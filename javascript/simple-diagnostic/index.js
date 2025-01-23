const { connect, JSONCodec } = require("nats");

const jc = JSONCodec();
const SERVICE_NAME = "diagnostic";

// Sends a heartbeat message every 10s to notify
// connhex-edge-agent that this service is working properly.
// By default the connhex-edge-agent checks that all services have sent
// a heartbeat message within the last 10s (customizable).
// If a service didn't, it is marked as offline.
const startHeartbeat = (nc) => {
  const intervalId = setInterval(() => {
    console.log("Publishing heartbeat...");
    // Any custom logic that checks that everything is ok should be added here.
    nc.publish(`heartbeat.${SERVICE_NAME}.service`);
  }, 10000);

  return {
    stop: () => clearInterval(intervalId),
  };
};

const startUpdateLoop = (nc) => {
  const intervalId = setInterval(() => {
    // Build a SenML message
    const msg = [
      {
        t: Date.now() / 1000,
        n: `urn:cpt:${SERVICE_NAME}:battery-charge`,
        u: "%EL",
        v: Math.floor(Math.random() * (100 + 1)),
      },
    ];
    console.log(`Sending message: ${JSON.stringify(msg)}`);

    nc.publish(`events.data`, jc.encode(msg));
  }, 60000);

  return {
    stop: () => clearInterval(intervalId),
  };
};

(async () => {
  const handleExit = () => {
    nc.drain()
      .then(() => updateLoop.stop())
      .then(() => heartbeat.stop())
      .then(() => process.exit(0));
  };
  process.on("SIGINT", handleExit);
  process.on("SIGQUIT", handleExit);
  process.on("SIGTERM", handleExit);

  const nc = await connect();
  console.log("NATS connected");

  const updateLoop = startUpdateLoop(nc);
  const heartbeat = startHeartbeat(nc);

  // Subscribe to NATS subject and listen for commands received.
  // ">" is used as wildcard, check https://docs.nats.io/nats-concepts/subjects#characters-allowed-for-subject-names
  sub = nc.subscribe(`commands.${SERVICE_NAME}.>`);
  for await (const m of sub) {
    console.log(
      `Received command: [${m.subject}] ${JSON.stringify(jc.decode(m.data))}`
    );
  }
})();
