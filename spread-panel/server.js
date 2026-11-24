const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8787;

// 新浪代码（4 位）——期货主力（默认清单，watch.html 走动态接口不受此限）
const CODES = ['TA2701', 'PX2701', 'FG2701', 'FG2705', 'SH2701', 'SH2705', 'PP2701', 'PP2705', 'UR2701', 'M2701', 'RM2701', 'JD2701', 'JD2705', 'L2701', 'LH2701', 'LH2703', 'CU2701', 'CU2703', 'J2701', 'JM2701'];
const LIST = CODES.map(c => 'nf_' + c).join(',');

// 东方财富 secid：郑商所期货 115 / 大商所期货 114 / 大商所期权 140 / 郑商所期权 141
const EM = {
  TA2701: '115.TA701', PX2701: '115.PX701',
  FG2701: '115.FG701', FG2705: '115.FG705',
  SH2701: '115.SH701', SH2705: '115.SH705',
  UR2701: '115.UR701', RM2701: '115.RM701',
  M2701: '114.m2701', PP2701: '114.pp2701',
  J2701: '114.j2701', JM2701: '114.jm2701',
  JD2701: '114.jd2701', JD2705: '114.jd2705', L2701: '114.l2701',
  LH2701: '114.lh2701', LH2703: '114.lh2703',
  CU2701: '113.cu2701', CU2703: '113.cu2703',
  UR_C1740: '141.UR701C1740', UR_C1800: '141.UR701C1800'
};
const EM_BACK = {};
for (const k in EM) EM_BACK[EM[k].split('.')[1].toUpperCase()] = k;

const diag = { sina: 'untested', em: 'untested', opt: 'untested', sinaLen: 0, emLen: 0, lastOk: null };

function withTimeout(ms) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), ms);
  return { signal: ac.signal, done: () => clearTimeout(t) };
}

function parseSina(text) {
  const out = {};
  const re = /var hq_str_nf_([A-Z]+\d+)="([^"]*)"/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    const code = m[1];
    const f = m[2].split(',');
    if (f.length < 15 || !f[8]) continue;
    out[code] = {
      name: f[0], time: f[1],
      open: +f[2], high: +f[3], low: +f[4],
      bid: +f[6], ask: +f[7], last: +f[8],
      preSettle: +f[10], bidVol: +f[11], askVol: +f[12],
      oi: +f[13], vol: +f[14], date: f[17]
    };
  }
  return out;
}

async function fromSinaList(list) {
  const to = withTimeout(8000);
  try {
    const res = await fetch('https://hq.sinajs.cn/list=' + list, {
      headers: {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      },
      signal: to.signal
    });
    const buf = Buffer.from(await res.arrayBuffer());
    const text = new TextDecoder('gbk').decode(buf);
    diag.sina = 'http ' + res.status;
    diag.sinaLen = text.length;
    const q = parseSina(text);
    if (!Object.keys(q).length) throw new Error('empty parse, body ' + text.slice(0, 60));
    return q;
  } finally { to.done(); }
}

async function fromSina() {
  return fromSinaList(LIST);
}

// 动态清单（watch.html 自选组合用）：任意 nf_ 合约，纯新浪源
async function dynamicQuotes(codes) {
  const list = codes.slice(0, 120).map(c => 'nf_' + c.toUpperCase()).join(',');
  const q = await fromSinaList(list);
  const missing = codes.map(c => c.toUpperCase()).filter(c => !q[c]);
  return { q, missing };
}

async function fetchEM(keys) {
  const secids = keys.map(k => EM[k]).filter(Boolean).join(',');
  if (!secids) return {};
  const url = 'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2'
    + '&secids=' + secids
    + '&fields=f2,f3,f4,f5,f12,f13,f14,f15,f16,f17,f18,f28,f31,f32,f108';
  const to = withTimeout(8000);
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15' },
      signal: to.signal
    });
    const j = await res.json();
    const diff = (j && j.data && j.data.diff) || [];
    const out = {};
    for (const d of diff) {
      const key = EM_BACK[String(d.f12 || '').toUpperCase()];
      if (!key) continue;
      out[key] = {
        name: d.f14, time: '',
        open: +d.f17, high: +d.f15, low: +d.f16,
        bid: +d.f31, ask: +d.f32,
        last: +d.f2,
        preSettle: +d.f28 || +d.f18,
        bidVol: 0, askVol: 0, oi: +d.f108 || 0, vol: +d.f5, date: ''
      };
    }
    return out;
  } finally { to.done(); }
}

async function fromEastmoney() {
  const q = await fetchEM(Object.keys(EM));
  if (!Object.keys(q).length) throw new Error('no mapped codes');
  diag.em = 'ok ' + Object.keys(q).length;
  return q;
}

// 期权只从东财取，取不到不影响期货数据
async function mergeOptions(q) {
  const opts = ['UR_C1740', 'UR_C1800'];
  const miss = opts.filter(k => !q[k] || !q[k].last);
  if (!miss.length) { diag.opt = 'cached'; return q; }
  try {
    const o = await fetchEM(miss);
    Object.assign(q, o);
    diag.opt = 'ok ' + Object.keys(o).length;
  } catch (e) {
    diag.opt = 'fail: ' + (e && e.message || e);
  }
  return q;
}

let cache = { t: 0, body: null };

async function quotes() {
  if (cache.body && Date.now() - cache.t < 2000) return cache.body;
  const errors = [];
  for (const [name, fn] of [['sina', fromSina], ['eastmoney', fromEastmoney]]) {
    try {
      const q = await mergeOptions(await fn());
      const body = JSON.stringify({ ts: Date.now(), src: name, q });
      cache = { t: Date.now(), body };
      diag.lastOk = name;
      return body;
    } catch (e) {
      errors.push(name + ': ' + (e && e.message || e));
    }
  }
  throw new Error(errors.join(' | '));
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x');
  const url = u.pathname;

  if (url === '/api/q') {
    const dyn = u.searchParams.get('codes');
    if (dyn) {
      const codes = dyn.split(',').map(s => s.trim()).filter(Boolean);
      if (!codes.length) { res.writeHead(400); res.end('bad codes'); return; }
      const key = 'dyn:' + codes.join(',').toUpperCase();
      if (cache.key === key && cache.body && Date.now() - cache.t < 2000) {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Access-Control-Allow-Origin': '*' });
        res.end(cache.body); return;
      }
      try {
        const { q, missing } = await dynamicQuotes(codes);
        const body = JSON.stringify({ ts: Date.now(), src: 'sina-dyn', q, missing });
        cache = { t: Date.now(), body, key };
        diag.lastOk = 'dyn';
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Access-Control-Allow-Origin': '*' });
        res.end(body);
      } catch (e) {
        res.writeHead(502, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify({ error: String(e && e.message || e), diag }));
      }
      return;
    }
    try {
      const body = await quotes();
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Access-Control-Allow-Origin': '*' });
      res.end(body);
    } catch (e) {
      res.writeHead(502, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
      res.end(JSON.stringify({ error: String(e && e.message || e), diag }));
    }
    return;
  }

  if (url === '/api/diag') {
    const probe = {};
    try { probe.sina = Object.keys(await fromSina()).length; } catch (e) { probe.sina = 'fail: ' + e.message; }
    try { probe.em = Object.keys(await fromEastmoney()).length; } catch (e) { probe.em = 'fail: ' + e.message; }
    try { probe.opt = Object.keys(await fetchEM(['UR_C1740', 'UR_C1800'])).length; } catch (e) { probe.opt = 'fail: ' + e.message; }
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ diag, probe, at: new Date().toISOString() }, null, 2));
    return;
  }

  const file = url === '/' ? 'index.html' : url.replace(/^\//, '');
  const full = path.join(__dirname, file);
  if (!full.startsWith(__dirname) || !fs.existsSync(full) || fs.statSync(full).isDirectory()) {
    res.writeHead(404); res.end('not found'); return;
  }
  const ext = path.extname(full);
  const type = ext === '.html' ? 'text/html; charset=utf-8' : ext === '.js' ? 'application/javascript' : 'text/plain; charset=utf-8';
  res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  fs.createReadStream(full).pipe(res);
});

server.listen(PORT, '0.0.0.0', () => console.log('spread panel on ' + PORT));
