const d = msg.payload;
if (!d || typeof d.mode !== "string" || !Number.isInteger(d.http)) return null;
if (d.mode === "thingspeak" && d.http === 200 && d.tersimpan === true &&
    Number.isInteger(d.entry_id) && d.entry_id > 0) {
    msg.payload = "ThingSpeak: entry " + d.entry_id;
} else if (d.mode === "read_public" && d.http === 200 && d.read_ok === true) {
    msg.payload = "Baca channel publik berhasil; sensor belum dikirim ke channel sendiri";
} else {
    msg.payload = "REST belum berhasil; HTTP " + d.http;
}
return msg;
