const { connect } = require("nats");
const diagnosticService = require("./diagnostic");

(async () => {
  const nc = await connect();
  console.log("NATS connected");

  const diagnosticServiceInstance = await diagnosticService.start(nc);

  const handleExit = (signal) => {
    console.log(`Received ${signal}.`);
    nc.drain()
      .then(() => diagnosticServiceInstance.dispose())
      .then(() => process.exit(0));
  };

  process.on("SIGINT", handleExit);
  process.on("SIGQUIT", handleExit);
  process.on("SIGTERM", handleExit);
})();
