const mqtt = require("mqtt");
const config = require("./config.json");
const root = process.env.MK38_TOPIC_ROOT || config.topicRoot;
const broker = process.env.MK38_BROKER || config.broker;
const port = Number(process.env.MK38_MQTT_PORT || config.port);
const mode = process.argv[2] || "watch";
const command = process.argv[3];
if (!["watch", "send", "clear"].includes(mode) ||
    (mode === "send" && !["on", "off", "salah"].includes(command))) {
  console.error("Gunakan: node mqtt_cli.js watch | send on | send off | send salah | clear");
  process.exit(1);
}
const client = mqtt.connect(`mqtt://${broker}:${port}`, {
  clientId: `mk38-cli-${process.pid}-${Date.now().toString(16)}`,
  protocolVersion: 4, connectTimeout: 10000, reconnectPeriod: 2000
});
client.on("connect", () => {
  if (mode === "watch") {
    client.subscribe(`${root}/#`, { qos: 1 }, err => {
      if (err) throw err;
      console.log(`Memantau ${root}/#`);
    });
  } else if (mode === "send") {
    client.publish(`${root}/led/set`, command, { qos: 1, retain: false }, err => {
      if (err) throw err;
      console.log(`Perintah ${command} dikirim; periksa konfirmasi perangkat.`);
      client.end();
    });
  } else {
    client.publish(`${root}/led/state`, "", { qos: 1, retain: true }, err => {
      if (err) throw err;
      console.log("Retained state milik topic root ini dihapus.");
      client.end();
    });
  }
});
client.on("message", (topic, payload, packet) => {
  console.log(JSON.stringify({ waktu: new Date().toISOString(), topic,
    payload: payload.toString(), qos: packet.qos, retained: packet.retain }));
});
client.on("error", err => console.error(`MQTT: ${err.message}`));
process.on("SIGINT", () => client.end(false, () => process.exit()));
