'use strict';
const byId = id => document.getElementById(id);
const number = new Intl.NumberFormat('id-ID', {minimumFractionDigits:1,maximumFractionDigits:1});
const time = value => value ? new Intl.DateTimeFormat('id-ID', {timeZone:'Asia/Jakarta',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date(value)) : '';
const statusText = {pending:'Menunggu ESP32',applied:'Dikonfirmasi ESP32',superseded:'Diganti perintah baru',expired:'Kedaluwarsa'};
let selected = new URLSearchParams(location.search).get('device_id') || '';
let lastData = null;
let loading = false;
let commandBusy = false;
let refreshQueued = false;
try { byId('dark-mode').checked = localStorage.getItem('mk38-theme') === 'dark'; } catch (_) {}
function setTheme() { document.documentElement.dataset.theme = byId('dark-mode').checked ? 'dark' : 'light'; try { localStorage.setItem('mk38-theme',document.documentElement.dataset.theme); } catch (_) {} }
setTheme();
byId('dark-mode').addEventListener('change',setTheme);
async function api(path, options = {}) {
    const response = await fetch(path, {cache:'no-store',signal:AbortSignal.timeout(8000),...options,headers:{Accept:'application/json','Content-Type':'application/json',...options.headers}});
    const body = await response.json();
    if (!response.ok) throw new Error(body.errors ? Object.values(body.errors).flat().join(' ') : body.message || `HTTP ${response.status}`);
    return body;
}
function cell(row,value) { const td=document.createElement('td'); td.textContent=value; row.append(td); }
function chart(id,rows,key,unit) {
    const svg=byId(id), width=Math.max(250,Math.round(svg.getBoundingClientRect().width)), height=180;
    svg.replaceChildren(); svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
    const make=(tag,attrs,text)=>{ const node=document.createElementNS('http://www.w3.org/2000/svg',tag); for(const [k,v] of Object.entries(attrs)) node.setAttribute(k,v); if(text!==undefined) node.textContent=text; svg.append(node); return node; };
    if(!rows.length) { make('text',{x:12,y:80},'Belum ada kiriman untuk digambar.'); svg.setAttribute('aria-label',`Grafik ${key}: belum ada data`); return; }
    const values=rows.map(r=>r[key]), low=Math.min(...values), high=Math.max(...values), margin=Math.max((high-low)*.12,.5);
    const min=low-margin,max=high+margin,left=45,right=width-12,top=15,bottom=145;
    const stamps=rows.map(r=>Date.parse(r.created_at)), start=stamps[0],end=stamps.at(-1);
    const x=i=>end===start ? (left+right)/2 : left+(stamps[i]-start)/(end-start)*(right-left);
    const y=v=>bottom-(v-min)/(max-min)*(bottom-top);
    for(const v of [min,(min+max)/2,max]) {make('line',{x1:left,y1:y(v),x2:right,y2:y(v),class:'axis'});make('text',{x:0,y:y(v)+4},number.format(v));}
    make('path',{d:rows.map((r,i)=>`${i?'L':'M'} ${x(i)} ${y(r[key])}`).join(' '),class:'line'});
    const last=rows.length-1; make('circle',{cx:x(last),cy:y(rows[last][key]),r:3,class:'point'});
    const short=v=>new Intl.DateTimeFormat('id-ID',{timeZone:'Asia/Jakarta',hour:'2-digit',minute:'2-digit'}).format(new Date(v));
    make('text',{x:left,y:170},short(start));make('text',{x:right,y:170,'text-anchor':'end'},short(end));
    svg.setAttribute('aria-label',`${rows.length} kiriman ${key}; minimum ${number.format(low)} ${unit}, maksimum ${number.format(high)} ${unit}. Nilai lengkap tersedia pada tabel riwayat.`);
}
function render(data) {
    lastData=data; selected=data.selected_device || selected;
    const select=byId('device'); select.replaceChildren();
    const ids=[...data.devices]; if(selected&&!ids.includes(selected)) ids.push(selected);
    if(!ids.length) select.add(new Option('Belum ada perangkat',''));
    for(const id of ids) select.add(new Option(id,id)); select.value=selected;
    const latest=data.latest;
    byId('temperature').textContent=latest ? `${number.format(latest.suhu)} °C` : 'Belum ada';
    byId('humidity').textContent=latest ? `${number.format(latest.kelembapan)} %` : 'Belum ada';
    for(const id of ['temperature','humidity'])byId(id).classList.toggle('missing',!latest);
    byId('connection').textContent=!latest ? 'Belum ada kiriman' : data.online ? 'Kiriman masih diterima' : 'Belum ada kiriman baru';
    byId('last-seen').textContent=latest ? `Diterima ${time(latest.created_at)} WIB · ${data.age_seconds} detik sebelum pemeriksaan.` : 'Jalankan firmware dan kirim data dengan device_id yang dipilih.';
    const note=byId('temperature-note'); note.classList.toggle('warning',Boolean(data.warning));
    note.textContent=latest&&data.device ? `${data.warning?'Peringatan suhu':'Suhu di bawah ambang'} · ambang latihan ${number.format(data.device.suhu_batas)} °C. ${data.online?'':'Nilai berasal dari kiriman lama.'}` : 'Ambang suhu adalah aturan latihan, bukan batas keselamatan.';
    const device=data.device;
    for(const id of ['led-on','led-off','save-threshold','threshold']) byId(id).disabled=!device||commandBusy;
    byId('reported-led').textContent=device?.led===null||!device ? 'Belum ada laporan' : device.led ? 'Nyala' : 'Mati';
    byId('reported-at').textContent=device?.reported_at ? `Dilaporkan ${time(device.reported_at)} WIB. ${data.online?'':'Perangkat belum mengirim sensor baru.'}` : 'Status LED belum diketahui; jalankan firmware kendali.';
    if(document.activeElement!==byId('threshold')&&device) byId('threshold').value=device.suhu_batas;
    if(!device) byId('threshold').value='';
    byId('commands').replaceChildren();
    if(!data.commands.length) { const li=document.createElement('li');li.textContent='Belum ada perintah untuk perangkat ini.';byId('commands').append(li); }
    for(const command of data.commands) { const li=document.createElement('li');li.textContent=`#${command.id} · ${command.led?'Nyala':'Mati'} · ${statusText[command.status] || command.status}`;const date=document.createElement('time');date.dateTime=command.created_at;date.textContent=time(command.created_at)+' WIB';li.append(date);byId('commands').append(li); }
    chart('chart-temperature',data.readings,'suhu','°C');chart('chart-humidity',data.readings,'kelembapan','% RH');
    byId('chart-note').textContent=data.readings.length ? `${data.readings.length} kiriman terakhir yang tersedia. Sumbu waktu memakai waktu penerimaan, WIB; setiap grafik memiliki skala sendiri.` : 'Belum ada kiriman. Periksa API_BASE, device_id, dan proses Laravel.';
    byId('history').replaceChildren();
    for(const row of [...data.readings].reverse()) {const tr=document.createElement('tr');cell(tr,row.id);cell(tr,time(row.created_at));cell(tr,number.format(row.suhu));cell(tr,number.format(row.kelembapan));byId('history').append(tr);}
    if(!data.readings.length) {const tr=document.createElement('tr');cell(tr,'Belum ada kiriman untuk perangkat ini. Jalankan ESP32 sebelum memeriksa riwayat.');tr.firstChild.colSpan=4;byId('history').append(tr);}
    const query=new URLSearchParams({limit:byId('limit').value});if(selected)query.set('device_id',selected);
    if(latest)query.set('until_id',latest.id);
    byId('csv').href='/api/v1/ekspor.csv?'+query;
    byId('history-note').textContent=selected ? `Perangkat ${selected}. CSV berisi catatan yang sama dengan grafik dan tabel ini, waktu dalam UTC.` : 'CSV masih kosong sampai perangkat mengirim data.';
}
async function refresh(manual=false) {
    if(loading) {refreshQueued ||= manual;return;} loading=true; byId('refresh').disabled=true;
    if(manual||!lastData) byId('network').textContent='Memuat kiriman dari API…';
    const query=new URLSearchParams({limit:byId('limit').value});if(selected)query.set('device_id',selected);
    const requestedDevice=selected,requestedLimit=byId('limit').value;
    try { const data=await api('/api/v1/pemantauan?'+query);if(requestedDevice!==selected||requestedLimit!==byId('limit').value){refreshQueued=true;return;}render(data);byId('network').classList.remove('error');byId('network').textContent=`Pemeriksaan terakhir ${time(data.server_time)} WIB. ${byId('auto-refresh').checked?'Pembaruan otomatis aktif.':'Pembaruan otomatis dijeda.'}`; }
    catch(error) {byId('network').classList.add('error');byId('network').textContent=`Gagal membaca API. ${lastData?'Tampilan masih memakai data sebelumnya. ':''}Periksa proses Laravel dan MySQL, lalu pilih Perbarui data. (${error.message})`;}
    finally {loading=false;byId('refresh').disabled=false;if(refreshQueued){refreshQueued=false;refresh(true);}}
}
byId('filter-form').addEventListener('submit',event=>{event.preventDefault();selected=byId('device').value;refresh(true);});
byId('device').addEventListener('change',()=>{selected=byId('device').value;refresh(true);});
byId('limit').addEventListener('change',()=>refresh(true));
byId('auto-refresh').addEventListener('change',()=>refresh(true));
async function command(led) {
    if(!lastData?.device||commandBusy) return;commandBusy=true;for(const id of ['led-on','led-off']) byId(id).disabled=true;
    byId('feedback').textContent='Mengirim permintaan ke API…';
    try {const result=await api(`/api/v1/perangkat/${encodeURIComponent(selected)}/perintah`,{method:'POST',body:JSON.stringify({led})});byId('feedback').textContent=`Perintah #${result.id} tersimpan. Menunggu ESP32; status LED belum dinyatakan berubah.`;}
    catch(error){byId('feedback').textContent='Perintah gagal dikirim: '+error.message;}
    finally{commandBusy=false;for(const id of ['led-on','led-off'])byId(id).disabled=!lastData?.device;await refresh(true);}
}
byId('led-on').addEventListener('click',()=>command(true));byId('led-off').addEventListener('click',()=>command(false));
byId('settings-form').addEventListener('submit',async event=>{
    event.preventDefault();if(!lastData?.device) return;byId('save-threshold').disabled=true;
    try {await api(`/api/v1/perangkat/${encodeURIComponent(selected)}/pengaturan`,{method:'PUT',body:JSON.stringify({suhu_batas:Number(byId('threshold').value)})});byId('feedback').textContent='Ambang latihan disimpan. Indikator mengikuti pembacaan sensor terakhir.';}
    catch(error){byId('feedback').textContent='Ambang gagal disimpan: '+error.message;}
    finally{byId('save-threshold').disabled=!lastData?.device;await refresh(true);}
});
setInterval(()=>{if(byId('auto-refresh').checked&&!document.hidden) refresh();},5000);
window.addEventListener('resize',()=>{if(lastData){chart('chart-temperature',lastData.readings,'suhu','°C');chart('chart-humidity',lastData.readings,'kelembapan','% RH');}});
refresh();
