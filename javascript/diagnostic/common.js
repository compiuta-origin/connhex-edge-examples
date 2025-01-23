const { JSONCodec } = require("nats");
const jc = JSONCodec();

// Encode and publish a message.
exports.publishMessage = (nc, msg) => nc.publish(`events.data`, jc.encode(msg));

// Sends a heartbeat message every `heartbeatIntervalMs` ms to notify
// connhex-edge-agent that this service is working properly.
// By default the connhex-edge-agent checks that all services have sent
// a heartbeat message within the last 10s (customizable).
// If a service didn't, it is be marked as offline.
const heartbeatIntervalMs = 10000;
exports.startHeartbeat = (nc, serviceName) => {
  const interval = setInterval(() => {
    // Add here your custom logic to check that everything is ok.
    nc.publish(`heartbeat.${serviceName}.service`);
  }, heartbeatIntervalMs);

  return {
    stop: () => clearInterval(interval),
  };
};

// Listen for commands received.
exports.listenForAgentCommands = (nc, serviceName, handler) => {
  // Subscribe to NATS subject.
  // ">" is used as wildcard, check https://docs.nats.io/nats-concepts/subjects#characters-allowed-for-subject-names
  const sub = nc.subscribe(`commands.${serviceName}.>`);
  (async () => {
    for await (const m of sub) {
      handler(
        m.subject.replace(`commands.${serviceName}.`, ""),
        jc.decode(m.data)
      );
    }
  })();

  return sub;
};
