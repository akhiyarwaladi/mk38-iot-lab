const url = '/api/v1/sensor?limit=1&device_id=' + encodeURIComponent(id);
const response = await fetch(url, {
    cache: 'no-store',
    signal: AbortSignal.timeout(8000),
    headers: {Accept:'application/json'}
});
const rows = await response.json();
if (!response.ok) throw new Error(rows.message || 'HTTP ' + response.status);
