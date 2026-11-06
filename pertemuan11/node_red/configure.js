const fs = require("node:fs");
const path = require("node:path");
const config = JSON.parse(fs.readFileSync(path.join(__dirname, "config.json"), "utf8"));
const root = process.env.MK38_TOPIC_ROOT || config.topicRoot;
const broker = process.env.MK38_BROKER || config.broker;
const port = Number(process.env.MK38_MQTT_PORT || config.port);
if (!/^[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)+$/.test(root) || root.length > 100) {
  throw new Error("Topic root tidak valid; gunakan huruf, angka, garis miring, atau tanda hubung.");
}
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("Port MQTT tidak valid.");
fs.mkdirSync(path.join(__dirname, "data"), { recursive: true });
const replacements = {
  "__SENSOR_WIDGET__": fs.readFileSync(path.join(__dirname, "functions", "sensor_widget.html"), "utf8"),
  "__CLOUD_STATUS__": fs.readFileSync(path.join(__dirname, "functions", "status_cloud.js"), "utf8"),
  "__ROOT__": root,
  "__BROKER__": broker,
  "__PORT__": String(port),
  "__DB_FILE__": path.join(__dirname, "data", "sensor.sqlite"),
  "__VALIDATE__": fs.readFileSync(path.join(__dirname, "functions", "validasi.js"), "utf8"),
  "__PARAMS__": fs.readFileSync(path.join(__dirname, "functions", "parameter_sql.js"), "utf8")
};
function replace(value) {
  if (typeof value === "string") {
    for (const [key, data] of Object.entries(replacements)) value = value.split(key).join(data);
    return value;
  }
  if (Array.isArray(value)) return value.map(replace);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k,v]) => [k, replace(v)]));
  return value;
}
const flow = replace(JSON.parse(fs.readFileSync(path.join(__dirname, "flow.template.json"), "utf8")));
fs.writeFileSync(path.join(__dirname, "flow.runtime.json"), JSON.stringify(flow, null, 2) + "\n");
console.log(`Topic root: ${root}; broker: ${broker}:${port}`);
