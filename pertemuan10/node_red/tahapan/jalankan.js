// Pilih cabang latihan; template lengkap tetap menjadi sumber konfigurasi.
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const stage = Number(process.argv[2]);
if (![1, 2, 3, 4].includes(stage)) throw new Error("Gunakan nomor tahap 1, 2, 3, atau 4.");
const base = path.resolve(__dirname, "..");
require(path.join(base, "configure.js"));
let flow = JSON.parse(fs.readFileSync(path.join(base, "flow.runtime.json"), "utf8"));
const keep = {
  1: ["tab", "broker", "sensor", "debug"],
  2: ["tab", "broker", "sensor", "json", "valid", "debug", "catch", "errors"],
  3: ["tab", "broker", "db", "init", "create", "schema", "ready", "sensor", "json", "valid",
      "params", "insert", "count", "countvalue", "debug", "catch", "errors"]
};
if (stage < 4) {
  const ids = new Set(keep[stage].map(id => "p10" + id));
  flow = flow.filter(node => ids.has(node.id));
  for (const node of flow) {
    if (node.wires) node.wires = node.wires.map(output => output.filter(id => ids.has(id)));
  }
  if (stage === 1) flow.find(node => node.id === "p10sensor").wires = [["p10debug"]];
  if (stage === 2) {
    flow.find(node => node.id === "p10valid").func = fs.readFileSync(path.join(__dirname, "validasi_awal.js"), "utf8");
  }
  const debug = flow.find(node => node.id === "p10debug");
  debug.console = true;
  flow.find(node => node.id === "p10tab").label = "Latihan tahap " + stage;
}
const filename = `flow.tahap${stage}.runtime.json`;
fs.writeFileSync(path.join(base, filename), JSON.stringify(flow, null, 2) + "\n");
console.log(`Tahap ${stage}: ${flow.length} node; simpan ekspor editor sebelum mengulang perintah ini.`);
if (!process.argv.includes("--prepare-only")) {
  const child = spawn(process.execPath, [path.join(base, "node_modules/node-red/red.js"),
    "--userDir", base, "--settings", path.join(base, "settings.js"), filename], { stdio: "inherit", cwd: base });
  for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
  child.on("exit", code => { process.exitCode = code || 0; });
}
