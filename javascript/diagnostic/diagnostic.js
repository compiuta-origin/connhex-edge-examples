const {
  startHeartbeat,
  publishMessage,
  listenForAgentCommands,
} = require("./common");

const serviceName = "diagnostic";

// Implement your own logic to get current values.
const getBatteryCharge = () => Math.floor(Math.random() * (100 + 1));
const getFuelLevel = () => Math.floor(Math.random() * (100 + 1));

// Build a SenML message.
function buildDiagnosticMessage() {
  const now = Date.now() / 1000;
  const baseName = `urn:cpt:${serviceName}`;
  return [
    {
      t: now,
      n: `${baseName}:battery-charge`,
      u: "%EL",
      v: getBatteryCharge(),
    },
    {
      t: now,
      n: `${baseName}:fuel-level`,
      u: "%FL",
      v: getFuelLevel(),
    },
  ];
}

async function sendDiagnostic(nc) {
  const message = buildDiagnosticMessage();
  await publishMessage(nc, message);

  console.log("Diagnostic published");
}

const startUpdateLoop = (nc, interval) => {
  const intervalId = setInterval(() => sendDiagnostic(nc), interval);

  return {
    stop: () => clearInterval(intervalId),
  };
};

exports.start = async function start(nc, updateLoopIntervalMs = 60_000) {
  console.log(`Starting ${serviceName} service...`);

  const heartbeat = startHeartbeat(nc, serviceName);
  // Send diagnostic message every minute.
  const updateLoop = startUpdateLoop(nc, updateLoopIntervalMs);
  const commandsSub = listenForAgentCommands(
    nc,
    serviceName,
    async (subject, data) => {
      // Implement your own message handling logic.
      console.log(`Received command: [${subject}]`, data);
    }
  );

  return {
    dispose: async () => {
      console.log(`Stopping ${serviceName} service...`);
      updateLoop.stop();
      heartbeat.stop();
      if (!commandsSub.isClosed()) await commandsSub.drain();
    },
  };
};
