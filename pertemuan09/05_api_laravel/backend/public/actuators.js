'use strict';
(() => {
    const el = id => document.getElementById(id);
    const select = el('actuator');
    let devices = [], busy = false, sending = false, online = false, lastCommand = null;
    const time = value => value ? new Intl.DateTimeFormat('id-ID', {
        timeZone: 'Asia/Jakarta', dateStyle: 'short', timeStyle: 'medium'
    }).format(new Date(value)) : 'Belum ada';
    const valueText = (value, kind) => value === null ? 'Belum ada' :
        kind === 'led' ? `${value} (${value ? 'menyala' : 'mati'})` : `${value}°`;
    const chosen = () => devices.find(d => String(d.id) === select.value);
    const controls = () => {
        const current = chosen();
        el('led-controls').hidden = current?.kind !== 'led';
        el('servo-controls').hidden = current?.kind !== 'servo';
        document.querySelectorAll('.control button,.control input').forEach(x => {
            x.disabled = !current || !online || sending;
        });
    };
    async function api(path, body) {
        const response = await fetch('/api/v1/aktuator' + path, {
            method: body ? 'POST' : 'GET', headers: {'Accept': 'application/json',
                ...(body ? {'Content-Type': 'application/json'} : {})},
            ...(body ? {body: JSON.stringify(body)} : {}), signal: AbortSignal.timeout(5000)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.errors ? Object.values(data.errors).flat().join(' ') : data.message);
        return data;
    }
    function rows(id, records, columns, empty) {
        const body = el(id);
        body.replaceChildren();
        if (!records.length) {
            const cell = document.createElement('td'); cell.colSpan = columns.length;
            cell.textContent = empty;
            const row = document.createElement('tr'); row.append(cell); body.append(row);
        }
        records.forEach(record => {
            const row = document.createElement('tr');
            columns.forEach(column => { const cell = document.createElement('td');
                cell.textContent = column(record); row.append(cell); });
            body.append(row);
        });
    }
    async function refresh() {
        if (busy) return;
        busy = true; el('refresh').disabled = true; select.disabled = true;
        try {
            const previous = select.value;
            devices = await api('');
            select.replaceChildren();
            devices.forEach(d => { const option = document.createElement('option');
                option.value = d.id; option.textContent = `${d.device_id} / ${d.name} (${d.kind})`;
                select.append(option); });
            if (devices.some(d => String(d.id) === previous)) select.value = previous;
            online = true;
            el('connection').className = 'notice';
            const current = chosen();
            if (!current) {
                el('connection').textContent = 'Belum ada aktuator. Jalankan firmware atau langkah pendaftaran pada panduan.';
                return;
            }
            const selectedId = select.value;
            const data = await api(`/${selectedId}/riwayat`);
            if (select.value !== selectedId) return;
            const a = data.actuator;
            el('requested').textContent = valueText(a.requested_value, a.kind);
            el('reported').textContent = valueText(a.reported_value, a.kind);
            el('actuator-id').textContent = a.id;
            el('boot-id').textContent = a.boot_id ?? 'Belum ada';
            el('reported-at').textContent = time(a.reported_at);
            const fresh = a.reported_at && Date.now() - Date.parse(a.reported_at) < 20000;
            el('freshness').textContent = fresh ? 'Laporan diterima kurang dari 20 detik lalu.' :
                'Belum ada laporan baru dalam 20 detik. Periksa simulator dan koneksi.';
            el('freshness').className = fresh ? 'condition' : 'condition warning';
            el('connection').textContent = 'API terhubung. Menampilkan 20 perintah dan laporan terbaru untuk aktuator terpilih.';
            rows('command-rows', data.commands, [r => r.id, r => valueText(r.value, a.kind),
                r => r.status, r => time(r.acknowledged_at)], 'Belum ada perintah.');
            rows('event-rows', data.events, [r => r.id, r => valueText(r.value, a.kind),
                r => r.reason, r => r.command_id ?? 'Tidak ada', r => time(r.created_at)], 'Belum ada laporan.');
            if (lastCommand?.actuatorId === a.id) {
                const command = data.commands.find(r => r.id === lastCommand.id);
                if (command) el('feedback').textContent = command.status === 'applied' ?
                    `Perintah ${command.id} sudah dikonfirmasi firmware: ${valueText(command.value, a.kind)}.` :
                    `Perintah ${command.id}: ${command.status}. ${command.status === 'pending' ? 'Menunggu konfirmasi ESP32.' : 'Kirim perintah baru jika masih diperlukan.'}`;
            }
        } catch (error) {
            online = false; el('connection').className = 'notice error';
            el('connection').textContent = `Data belum diperbarui: ${error.message}. Periksa Laravel, lalu tekan Perbarui data. Nilai yang masih terlihat berasal dari pembaruan sebelumnya.`;
        } finally { busy = false; select.disabled = !devices.length; el('refresh').disabled = false; controls(); }
    }
    async function send(value) {
        const current = chosen();
        if (!current || sending || !online) return;
        sending = true; controls();
        try {
            const command = await api(`/${current.id}/perintah`, {value});
            lastCommand = {id: command.id, actuatorId: current.id};
            el('feedback').textContent = `Perintah ${command.id} untuk ${current.name} tersimpan: ${valueText(value, current.kind)}. Menunggu konfirmasi ESP32.`;
            await refresh();
        } catch (error) { el('feedback').textContent = `Perintah belum tersimpan: ${error.message}`; }
        finally { sending = false; controls(); }
    }
    el('selection').addEventListener('submit', event => { event.preventDefault(); refresh(); });
    select.addEventListener('change', () => { lastCommand = null; el('feedback').textContent = 'Pilih nilai, lalu kirim perintah.'; controls(); refresh(); });
    document.querySelectorAll('[data-value]').forEach(button => button.addEventListener('click', () => send(Number(button.dataset.value))));
    el('servo-controls').addEventListener('submit', event => { event.preventDefault(); send(Number(el('angle').value)); });
    el('theme').addEventListener('click', () => {
        const dark = document.documentElement.dataset.theme !== 'dark';
        document.documentElement.dataset.theme = dark ? 'dark' : 'light';
        el('theme').textContent = dark ? 'Tema terang' : 'Tema gelap';
    });
    setInterval(() => { if (el('automatic').checked) refresh(); }, 2000);
    refresh();
})();
