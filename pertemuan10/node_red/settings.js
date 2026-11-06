module.exports = {
  uiHost: "127.0.0.1",
  uiPort: Number(process.env.MK38_HTTP_PORT || 1880),
  flowFile: "flow.runtime.json",
  editorTheme: { projects: { enabled: false } },
  logging: { console: { level: "info", metrics: false, audit: false } }
};
