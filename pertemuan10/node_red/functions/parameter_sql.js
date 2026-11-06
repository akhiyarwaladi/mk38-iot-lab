const data = msg.payload;
msg.params = {
    $waktu: data.waktu,
    $suhu: data.suhu,
    $kelembapan: data.kelembapan,
    $led: data.led === null ? null : (data.led ? 1 : 0)
};
return msg;
