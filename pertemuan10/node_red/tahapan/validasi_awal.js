const data = msg.payload;
if (!data || Array.isArray(data) || typeof data !== "object" ||
    typeof data.suhu !== "number" || !Number.isFinite(data.suhu) ||
    typeof data.kelembapan !== "number" || !Number.isFinite(data.kelembapan) ||
    data.suhu < -40 || data.suhu > 80 ||
    data.kelembapan < 0 || data.kelembapan > 100 ||
    (data.led !== undefined && typeof data.led !== "boolean")) {
    node.warn("Data sensor ditolak: periksa tipe dan rentang nilai.");
    return null;
}
msg.payload = {
    suhu: data.suhu,
    kelembapan: data.kelembapan,
    led: data.led === undefined ? null : data.led,
    waktu: new Date().toISOString()
};
return msg;
