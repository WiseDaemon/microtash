/**
 * Automated Verification Suite for Microstash Mental Model Flowcharts
 * Renders all 34 diagrams via Microsoft Edge Headless and Mermaid v10.9.1
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn, execSync } = require('child_process');

// Extract all 34 diagrams from app/seed_data.py and data/microstash.db
const repoRoot = path.resolve(__dirname, '..', '..');
const appJsPath = path.join(repoRoot, 'app', 'static', 'js', 'app.js');
const appJs = fs.readFileSync(appJsPath, 'utf8');

const sanitizeCode = appJs.slice(
  appJs.indexOf('function sanitizeAndElevateMermaid'),
  appJs.indexOf('async function renderIdeaVisualDiagram')
);

// Query DB diagrams using Python one-liner (avoids writing py files)
const dbJson = execSync(
  'python -c "import sqlite3, json, sys; sys.path.insert(0, r\'' + repoRoot + '\'); from app.seed_data import DEFAULT_IDEAS; conn = sqlite3.connect(r\'' + path.join(repoRoot, 'data', 'microstash.db') + '\'); cur = conn.cursor(); cur.execute(\'SELECT id, visual_diagram FROM ideas\'); db_map = dict(cur.fetchall()); print(json.dumps([{\'id\': i[\'id\'], \'seed_diag\': i[\'visual_diagram\'], \'db_diag\': db_map.get(i[\'id\'])} for i in DEFAULT_IDEAS]))"',
  { encoding: 'utf8' }
);
const testCards = JSON.parse(dbJson);

const htmlContent = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Mermaid 34 Diagrams Automated Verification</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
${sanitizeCode}

const testCards = ${JSON.stringify(testCards)};

async function runTests() {
  try {
    const m = window.mermaid && window.mermaid.default ? window.mermaid.default : window.mermaid;
    m.initialize({ startOnLoad: false, securityLevel: 'loose', theme: 'neutral' });
    const results = { seed: [], db: [] };

    for (let i = 0; i < testCards.length; i++) {
      const card = testCards[i];
      const cleanDiag = sanitizeAndElevateMermaid(card.seed_diag, 'test');
      try {
        await m.render('testsvg' + i, cleanDiag);
        results.seed.push({ id: card.id, status: 'PASS' });
      } catch (e) {
        results.seed.push({ id: card.id, status: 'FAIL', error: e.message || String(e) });
      }
    }

    for (let i = 0; i < testCards.length; i++) {
      const card = testCards[i];
      if (!card.db_diag) continue;
      const cleanDbDiag = sanitizeAndElevateMermaid(card.db_diag, 'test-db');
      try {
        await m.render('testdbsvg' + i, cleanDbDiag);
        results.db.push({ id: card.id, status: 'PASS' });
      } catch (e) {
        results.db.push({ id: card.id, status: 'FAIL', error: e.message || String(e) });
      }
    }

    await fetch('/results', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(results)
    });
  } catch (fatal) {
    await fetch('/error?fatal=' + encodeURIComponent(fatal.stack || String(fatal)));
  }
}

window.onload = runTests;
</script>
</head>
<body>
<h1>Automated Verification Running...</h1>
</body>
</html>`;

const server = http.createServer((req, res) => {
  if (req.url === '/' || req.url === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(htmlContent);
  } else if (req.url.startsWith('/error')) {
    console.error('Browser error:', req.url);
    res.writeHead(200);
    res.end('OK');
  } else if (req.url === '/results' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      res.writeHead(200);
      res.end('OK');
      const data = JSON.parse(body);
      console.log('=== SEED CARDS MERMAID RESULTS ===');
      let seedPass = 0, seedFail = 0;
      data.seed.forEach((r, idx) => {
        if (r.status === 'PASS') {
          seedPass++;
          console.log('[' + (idx + 1) + '/34] PASS: ' + r.id);
        } else {
          seedFail++;
          console.error('[' + (idx + 1) + '/34] FAIL: ' + r.id + ' -> ' + r.error);
        }
      });

      console.log('\n=== DB CARDS MERMAID RESULTS ===');
      let dbPass = 0, dbFail = 0;
      data.db.forEach((r, idx) => {
        if (r.status === 'PASS') {
          dbPass++;
          console.log('[' + (idx + 1) + '/34] PASS: ' + r.id);
        } else {
          dbFail++;
          console.error('[' + (idx + 1) + '/34] FAIL: ' + r.id + ' -> ' + r.error);
        }
      });

      console.log('\nFINAL TOTALS: Seed Pass: ' + seedPass + '/34 (Fail: ' + seedFail + ') | DB Pass: ' + dbPass + '/34 (Fail: ' + dbFail + ')');

      if (edgeProc) edgeProc.kill();
      server.close();
      process.exit(seedFail === 0 && dbFail === 0 ? 0 : 1);
    });
  }
});

let edgeProc = null;
server.listen(8088, '127.0.0.1', () => {
  console.log('Verification server running on http://127.0.0.1:8088');
  const userDir = path.join(os.tmpdir(), 'edge_mermaid_verify_' + Date.now());
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  edgeProc = spawn(edgePath, [
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--user-data-dir=' + userDir,
    'http://127.0.0.1:8088/'
  ]);

  setTimeout(() => {
    console.error('Timeout waiting for results from browser');
    if (edgeProc) edgeProc.kill();
    server.close();
    process.exit(1);
  }, 40000);
});
