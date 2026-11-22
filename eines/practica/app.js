// Pràctica de Python — lògica de la pàgina.
// Estat local (localStorage) + enviament d'esdeveniments a Apps Script (si hi ha ENDPOINT).
(() => {
'use strict';
const CFG = window.CONFIG;
const FITXERS = ['py/motor.py', 'py/banc_tp1.py', 'py/banc_tp2.py'];
const MODULS = ['motor', 'banc_tp1', 'banc_tp2'];
const NOM_TIPUS = { predir: 'Què imprimeix?', escriure: 'Escriu el codi', ordenar: 'Ordena les línies' };

const $ = (id) => document.getElementById(id);
const DEBUG = new URLSearchParams(location.search).get('debug') === '1';
let cataleg = null;            // {conceptes, plantilles}
let estat = null;              // progrés de l'alumne
let codiAlumne = null;
let item = null;               // exercici actual
let intents = 0;
let resolt = false;
let conceptTriat = null;       // si l'alumne tria un concepte al mapa
let ultimaPlantilla = null;
let tInici = 0;

// ---------------------------------------------------------------- worker
let worker = null;
let pendents = new Map();
let seq = 0;
let workerPromesa = null;

function creaWorker() {
  worker = new Worker('worker.js?v=' + CFG.VERSIO);
  worker.onmessage = (e) => {
    const p = pendents.get(e.data.id);
    if (!p) return;
    pendents.delete(e.data.id);
    clearTimeout(p.timer);
    if (e.data.ok) p.resolve(e.data.res); else p.reject(new Error(e.data.error));
  };
  workerPromesa = crida({ cmd: 'init', cfg: {
    pyodide: CFG.PYODIDE, fitxers: FITXERS, moduls: MODULS, versio: CFG.VERSIO } }, 120);
  return workerPromesa;
}

function crida(msg, timeoutS) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    msg.id = id;
    const timer = setTimeout(() => {
      pendents.delete(id);
      reject(new Error('TIMEOUT'));
    }, (timeoutS || CFG.TIMEOUT_S) * 1000);
    pendents.set(id, { resolve, reject, timer });
    worker.postMessage(msg);
  });
}

async function reiniciaWorker() {
  if (worker) worker.terminate();
  for (const p of pendents.values()) clearTimeout(p.timer);
  pendents = new Map();
  await creaWorker();
}

// ---------------------------------------------------------------- estat
function clauEstat() { return 'practica_py_' + codiAlumne; }

function carregaEstat() {
  try {
    const s = localStorage.getItem(clauEstat());
    if (s) return JSON.parse(s);
  } catch (e) { /* localStorage no disponible */ }
  return { conceptes: {}, punts: 0, insignies: [] };
}

function desaEstat() {
  try { localStorage.setItem(clauEstat(), JSON.stringify(estat)); } catch (e) { /* res */ }
}

function ec(cid) {
  if (!estat.conceptes[cid]) estat.conceptes[cid] = { ratxa: [], intents: 0, encerts: 0, dominat: false };
  return estat.conceptes[cid];
}

function conceptesActius() {
  return cataleg.conceptes.filter(c => CFG.BANCS.includes(c.banc));
}

function teCodi(cid) {
  return cataleg.plantilles.some(p => p.concepte === cid && p.tipus !== 'predir');
}

function actualitzaDomini(cid) {
  const e = ec(cid);
  const n = CFG.RATXA_DOMINI;
  const ultims = e.ratxa.slice(-n);
  const tots = ultims.length === n && ultims.every(r => r.ok);
  const ambCodi = !teCodi(cid) || ultims.some(r => r.ok && r.tipus !== 'predir');
  if (tots && ambCodi) e.dominat = true;
}

function ratxaActual(cid) {
  const r = ec(cid).ratxa;
  let k = 0;
  for (let i = r.length - 1; i >= 0 && r[i].ok; i--) k++;
  return k;
}

// ---------------------------------------------------------------- tria d'exercici
function triaConcepte() {
  if (conceptTriat) return conceptTriat;
  const actius = conceptesActius();
  const pendentsC = actius.filter(c => !ec(c.id).dominat);
  const dominats = actius.filter(c => ec(c.id).dominat);
  if (dominats.length && (pendentsC.length === 0 || Math.random() < 0.2)) {
    return dominats[Math.floor(Math.random() * dominats.length)].id;   // repàs
  }
  return pendentsC.length ? pendentsC[0].id : actius[0].id;
}

function triaPlantilla(cid) {
  let opcions = cataleg.plantilles.filter(p => p.concepte === cid);
  // si la ratxa encara no té cap exercici de codi, prioritza'ls quan toqui
  const e = ec(cid);
  const ratxa = ratxaActual(cid);
  const faltaCodi = teCodi(cid) && !e.ratxa.slice(-ratxa).some(r => r.tipus !== 'predir');
  if (faltaCodi && ratxa >= CFG.RATXA_DOMINI - 1) {
    opcions = opcions.filter(p => p.tipus !== 'predir');
  }
  if (opcions.length > 1) opcions = opcions.filter(p => p.id !== ultimaPlantilla);
  return opcions[Math.floor(Math.random() * opcions.length)];
}

// ---------------------------------------------------------------- marcador
const INSIGNIES = [
  { id: 'primer', icona: '🌱', titol: 'Primer concepte dominat', cond: () => dominats().length >= 1 },
  { id: 'tp1', icona: '🐍', titol: 'Base de Python completa', cond: () => bancComplet('tp1') },
  { id: 'tp2', icona: '🎛️', titol: 'Python per a àudio complet', cond: () => bancComplet('tp2') },
  { id: 'ratxa10', icona: '🔥', titol: '10 encerts seguits', cond: () => (estat.ratxaGlobal || 0) >= 10 },
];

function dominats() { return conceptesActius().filter(c => ec(c.id).dominat); }

function bancComplet(banc) {
  const cs = cataleg.conceptes.filter(c => c.banc === banc && CFG.BANCS.includes(banc));
  return cs.length > 0 && cs.every(c => ec(c.id).dominat);
}

function pintaMarcador() {
  $('punts').textContent = '⭐ ' + (estat.punts || 0) + ' punts';
  const cont = $('insignies');
  cont.innerHTML = '';
  for (const ins of INSIGNIES) {
    if ((estat.insignies || []).includes(ins.id)) {
      const sp = document.createElement('span');
      sp.textContent = ins.icona;
      sp.title = ins.titol;
      cont.appendChild(sp);
    }
  }
}

function comprovaInsignies() {
  const noves = [];
  estat.insignies = estat.insignies || [];
  for (const ins of INSIGNIES) {
    if (!estat.insignies.includes(ins.id) && ins.cond()) {
      estat.insignies.push(ins.id);
      noves.push(ins);
    }
  }
  return noves;
}

function textProgres(cid) {
  const e = ec(cid);
  const n = CFG.RATXA_DOMINI;
  if (e.dominat) return 'Concepte dominat. Aquest exercici és de <strong>repàs</strong>: suma punts però no cal per avançar.';
  const r = Math.min(ratxaActual(cid), n);
  const ratxa = e.ratxa.slice(-ratxaActual(cid));
  const faltaCodi = teCodi(cid) && !ratxa.some(x => x.ok && x.tipus !== 'predir');
  let t = 'Encerts seguits en aquest concepte: <strong>' + r + ' de ' + n + '</strong>';
  t += ' · en ' + (n - r === 1 ? 'falta' : 'falten') + ' <strong>' + (n - r) + '</strong>';
  if (faltaCodi) t += ' (i com a mínim un ha de ser d\'escriure o ordenar codi)';
  return t + '.';
}

// ---------------------------------------------------------------- render
function escapa(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function enLinia(s) {
  return escapa(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

function markdown(text) {
  const blocs = text.split(/\n\n+/);
  return blocs.map(b => {
    const linies = b.split('\n');
    if (linies.every(l => l.startsWith('- '))) {
      return '<ul>' + linies.map(l => '<li>' + enLinia(l.slice(2)) + '</li>').join('') + '</ul>';
    }
    return '<p>' + linies.map(enLinia).join('<br>') + '</p>';
  }).join('');
}

function pintaMapa() {
  const cont = $('llista-conceptes');
  cont.innerHTML = '';
  let bancAnterior = null;
  for (const c of conceptesActius()) {
    if (c.banc !== bancAnterior) {
      const t = document.createElement('div');
      t.className = 'banc-titol';
      t.textContent = c.banc === 'tp1' ? 'Base de Python (TP1)' : 'Python per a àudio (TP2)';
      cont.appendChild(t);
      bancAnterior = c.banc;
    }
    const e = ec(c.id);
    const b = document.createElement('button');
    b.className = 'concepte' + (e.dominat ? ' dominat' : '') + (item && item.concepte === c.id ? ' actiu' : '');
    b.title = c.descripcio;
    const r = Math.min(ratxaActual(c.id), CFG.RATXA_DOMINI);
    let punts = '';
    for (let i = 0; i < CFG.RATXA_DOMINI; i++) punts += i < r ? '<span class="ple">●</span>' : '○';
    b.innerHTML = '<span class="nom">' + escapa(c.titol) + '</span><span class="punts">' +
                  (e.dominat ? '✓ ' : '') + punts + '</span>';
    b.onclick = () => { conceptTriat = c.id; nouExercici(); };
    cont.appendChild(b);
  }
}

function mostraResultat(classe, html) {
  const r = $('resultat');
  r.className = classe;
  r.innerHTML = html;
}

function amaga(id, amagar) { $(id).classList.toggle('amagat', amagar); }

// ---------------------------------------------------------------- exercici
async function nouExercici() {
  const cid = triaConcepte();
  const p = triaPlantilla(cid);
  ultimaPlantilla = p.id;
  const seed = Math.floor(Math.random() * 1e9);
  amaga('exercici', true);
  amaga('carregant', false);
  $('text-carregant').textContent = p.numpy ? 'Preparant l\'exercici (carregant NumPy la primera vegada)…' : 'Preparant l\'exercici…';
  try {
    await workerPromesa;
    item = JSON.parse(await crida({ cmd: 'genera', pid: p.id, seed, numpy: p.numpy }, p.numpy ? 90 : 20));
    item.numpy = p.numpy;
  } catch (err) {
    $('text-carregant').textContent = 'Error preparant l\'exercici: ' + err.message + '. Torna-ho a provar.';
    if (err.message === 'TIMEOUT') await reiniciaWorker();
    return;
  }
  intents = 0;
  resolt = false;
  if (DEBUG) window.__item = item;
  pintaExercici();
  pintaMapa();
}

function pintaExercici() {
  const c = cataleg.conceptes.find(x => x.id === item.concepte);
  $('ex-concepte').textContent = c.titol;
  $('ex-tipus').textContent = NOM_TIPUS[item.tipus];
  amaga('ex-repas', !ec(item.concepte).dominat);
  $('ex-progres').innerHTML = textProgres(item.concepte);
  amaga('toast', true);
  $('nota-ordenar').textContent = 'Clica les línies en l\'ordre correcte. Clica una línia de la solució per tornar-la a dalt.' +
    (item.n_distractors ? ' Compte: ' + (item.n_distractors === 1 ? 'una línia sobra' : item.n_distractors + ' línies sobren') +
     ' i s\'ha de quedar a dalt.' : '');
  tInici = Date.now();
  $('ex-enunciat').innerHTML = markdown(item.enunciat);
  amaga('ex-codi', item.tipus !== 'predir');
  if (item.tipus === 'predir') $('ex-codi').textContent = item.codi;
  amaga('resposta-predir', item.tipus !== 'predir');
  amaga('resposta-escriure', item.tipus !== 'escriure');
  amaga('resposta-ordenar', item.tipus !== 'ordenar');
  $('input-sortida').value = '';
  $('input-codi-alumne').value = item.esquelet || '';
  if (item.tipus === 'ordenar') pintaOrdenar();
  amaga('btn-comprova', false);
  $('btn-comprova').disabled = false;
  amaga('btn-solucio', true);
  amaga('btn-seguent', true);
  amaga('resultat', true);
  amaga('carregant', true);
  amaga('exercici', false);
  const focus = item.tipus === 'predir' ? 'input-sortida' : (item.tipus === 'escriure' ? 'input-codi-alumne' : null);
  if (focus) $(focus).focus();
}

function pintaOrdenar() {
  const origen = $('ord-origen');
  const desti = $('ord-desti');
  origen.innerHTML = '';
  desti.innerHTML = '';
  item.linies.forEach((l) => origen.appendChild(liniaOrdenar(l)));
}

function liniaOrdenar(text) {
  const li = document.createElement('li');
  li.textContent = text;
  li.onclick = () => {
    if (resolt) return;
    const desti = li.parentElement.id === 'ord-origen' ? $('ord-desti') : $('ord-origen');
    desti.appendChild(li);
  };
  return li;
}

function respostaActual() {
  if (item.tipus === 'predir') return $('input-sortida').value;
  if (item.tipus === 'escriure') return $('input-codi-alumne').value;
  const linies = [];
  $('ord-desti').querySelectorAll('li').forEach(li => linies.push(li.textContent));
  return linies.join('\n') + '\n';
}

async function comprova() {
  if (resolt) return;
  const resposta = respostaActual();
  if (item.tipus === 'ordenar' && $('ord-origen').children.length > (item.n_distractors || 0)) {
    mostraResultat('malament', 'Encara queden línies per col·locar.');
    return;
  }
  if (!resposta.trim()) return;
  $('btn-comprova').disabled = true;
  intents++;
  let r;
  try {
    r = JSON.parse(await crida({ cmd: 'corregeix', item: JSON.stringify(item), resposta, numpy: item.numpy }));
  } catch (err) {
    $('btn-comprova').disabled = false;
    if (err.message === 'TIMEOUT') {
      mostraResultat('malament', 'El teu codi ha trigat massa (més de ' + CFG.TIMEOUT_S +
        ' s). Potser tens un <strong>bucle infinit</strong>: un <code>while</code> que no s\'acaba, o un comptador que no avança. Reiniciant Python…');
      await reiniciaWorker();
      mostraResultat('malament', 'El teu codi ha trigat massa: potser tens un <strong>bucle infinit</strong>. Revisa-ho i torna-ho a provar.');
      return;
    }
    mostraResultat('malament', 'Error intern: ' + escapa(err.message));
    return;
  }
  $('btn-comprova').disabled = false;

  if (r.correcte) {
    const compta = item.tipus === 'predir' || intents <= CFG.INTENTS_ESCRIURE;
    finalitza(compta, resposta);
    let html = compta ? '✔ Correcte!' :
      '✔ Correcte, però amb massa intents per comptar a la ratxa. Ja ho tens: el següent sortirà millor.';
    if (r.notes && r.notes.length) {
      html += r.notes.map(n => '<p class="nota-format">' + enLinia(n) + '</p>').join('') +
        '<pre>' + escapa(r.solucio) + '</pre>';
    }
    mostraResultat('be', html);
    return;
  }
  if (item.tipus === 'predir') {
    finalitza(false, resposta);
    mostraResultat('malament', '✘ No és això. La sortida correcta era:<pre>' + escapa(r.solucio) +
      '</pre><p style="margin:.6rem 0 0">Compara-la línia a línia amb la teva i busca on t\'has desviat.</p>');
    return;
  }
  let html = '✘ Encara no.<ul>' + r.missatges.map(m => '<li>' + enLinia(m) + '</li>').join('') + '</ul>';
  if (intents >= 2) {
    amaga('btn-solucio', false);
    html += '<p style="margin:.6rem 0 0">Pots continuar intentant-ho, o veure la solució (aleshores no comptarà com a encert).</p>';
  }
  mostraResultat('malament', html);
}

function finalitza(ok, resposta) {
  resolt = true;
  const e = ec(item.concepte);
  e.intents++;
  if (ok) e.encerts++;
  e.ratxa.push({ ok, tipus: item.tipus });
  if (e.ratxa.length > 20) e.ratxa = e.ratxa.slice(-20);
  const abans = e.dominat;
  actualitzaDomini(item.concepte);
  estat.ratxaGlobal = ok ? (estat.ratxaGlobal || 0) + 1 : 0;
  let guanyats = ok ? (CFG.PUNTS[item.tipus] || 10) : 0;
  if (!abans && e.dominat) guanyats += CFG.PUNTS.domini;
  estat.punts = (estat.punts || 0) + guanyats;
  const noves = comprovaInsignies();
  desaEstat();
  const segons = Math.round((Date.now() - tInici) / 1000);
  envia({ concepte: item.concepte, plantilla: item.id, tipus: item.tipus, correcte: ok,
          intents, dominat: e.dominat, ratxa: ratxaActual(item.concepte), segons,
          repas: abans, punts: estat.punts,
          resposta: resposta.slice(0, 1500), seed: item.seed });
  pintaMarcador();
  $('ex-progres').innerHTML = textProgres(item.concepte);
  if (guanyats) mostraToast('+' + guanyats + ' punts' + (noves.length ? ' · Nova insígnia: ' +
    noves.map(n => n.icona + ' ' + n.titol).join(', ') : ''), noves.length > 0);
  amaga('btn-comprova', true);
  amaga('btn-solucio', true);
  amaga('btn-seguent', false);
  $('btn-seguent').focus();
  pintaMapa();
  if (!abans && e.dominat) {
    setTimeout(() => {
      const r = $('resultat');
      r.innerHTML += '<p style="margin:.6rem 0 0"><strong>🎉 Has dominat aquest concepte.</strong> ' +
        'Hi tornarà a sortir algun exercici de repàs de tant en tant.</p>';
    }, 50);
  }
}

function mostraToast(text, destacat) {
  const t = $('toast');
  t.textContent = text;
  t.classList.remove('amagat');
  t.style.fontWeight = destacat ? '600' : '400';
}

function veureSolucio() {
  finalitza(false, respostaActual());
  mostraResultat('malament', 'Una solució possible (llegeix-la línia a línia i compara-la amb la teva):<pre>' +
    escapa(item.solucio) + '</pre>');
}

// ---------------------------------------------------------------- enviament
function envia(dades) {
  if (!CFG.ENDPOINT) return;
  dades.codi = codiAlumne;
  dades.ts = new Date().toISOString();
  try {
    fetch(CFG.ENDPOINT, { method: 'POST', mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(dades) });
    $('estat-envio').textContent = 'Progrés desat (' + new Date().toLocaleTimeString() + ')';
  } catch (e) { /* sense xarxa: el progrés local es manté */ }
}

// ---------------------------------------------------------------- editor
function editorAmbIndentacio(ta) {
  ta.addEventListener('keydown', (e) => {
    const ini = ta.selectionStart, fi = ta.selectionEnd, v = ta.value;
    if (e.key === 'Tab') {
      e.preventDefault();
      ta.value = v.slice(0, ini) + '    ' + v.slice(fi);
      ta.selectionStart = ta.selectionEnd = ini + 4;
    } else if (e.key === 'Enter' && ta.id === 'input-codi-alumne') {
      e.preventDefault();
      const iniciLinia = v.lastIndexOf('\n', ini - 1) + 1;
      const linia = v.slice(iniciLinia, ini);
      let indent = linia.match(/^ */)[0];
      if (linia.trimEnd().endsWith(':')) indent += '    ';
      const ins = '\n' + indent;
      ta.value = v.slice(0, ini) + ins + v.slice(fi);
      ta.selectionStart = ta.selectionEnd = ini + ins.length;
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      comprova();
    }
  });
}

// ---------------------------------------------------------------- inici
async function arrenca() {
  document.title = CFG.TITOL;
  $('titol').textContent = CFG.TITOL;
  $('usuari').textContent = 'Codi: ' + codiAlumne;
  estat = carregaEstat();
  amaga('pantalla-codi', true);
  amaga('carregant', false);
  try {
    cataleg = JSON.parse(await (workerPromesa || creaWorker()));
  } catch (err) {
    $('text-carregant').textContent = 'No s\'ha pogut carregar Python: ' + err.message +
      '. Comprova la connexió i recarrega la pàgina.';
    return;
  }
  pintaMapa();
  pintaMarcador();
  nouExercici();
}

function demanaCodi() {
  amaga('carregant', true);
  amaga('pantalla-codi', false);
  const go = () => {
    const c = $('input-codi').value.trim().toUpperCase();
    if (!/^[A-Z0-9]{4,12}$/.test(c)) { $('input-codi').focus(); return; }
    codiAlumne = c;
    try { localStorage.setItem('practica_py_codi', c); } catch (e) { /* res */ }
    arrenca();
  };
  $('btn-codi').onclick = go;
  $('input-codi').onkeydown = (e) => { if (e.key === 'Enter') go(); };
  $('input-codi').focus();
}

function bloquejaCopia() {
  if (!CFG.BLOQUEJA_COPIA) return;
  for (const id of ['ex-enunciat', 'ex-codi', 'ord-origen', 'ord-desti']) {
    const el = $(id);
    el.classList.add('no-copia');
    for (const ev of ['copy', 'cut', 'contextmenu', 'dragstart', 'selectstart']) {
      el.addEventListener(ev, (e) => e.preventDefault());
    }
  }
  for (const id of ['input-codi-alumne', 'input-sortida']) {
    $(id).addEventListener('paste', (e) => {
      e.preventDefault();
      mostraToast('Aquí no es pot enganxar: escriu-ho tu (és la gràcia de practicar).', false);
    });
    $(id).addEventListener('drop', (e) => e.preventDefault());
  }
}

$('btn-comprova').onclick = comprova;
$('btn-seguent').onclick = () => { nouExercici(); };
$('btn-solucio').onclick = veureSolucio;
$('btn-auto').onclick = () => { conceptTriat = null; nouExercici(); };
editorAmbIndentacio($('input-codi-alumne'));
editorAmbIndentacio($('input-sortida'));
bloquejaCopia();

creaWorker();   // comença a carregar Python mentre l'alumne escriu el codi
const param = new URLSearchParams(location.search).get('a');
let guardat = null;
try { guardat = localStorage.getItem('practica_py_codi'); } catch (e) { /* res */ }
if (param && /^[A-Za-z0-9]{4,12}$/.test(param)) {
  codiAlumne = param.toUpperCase();
  try { localStorage.setItem('practica_py_codi', codiAlumne); } catch (e) { /* res */ }
  arrenca();
} else if (guardat) {
  codiAlumne = guardat;
  arrenca();
} else {
  demanaCodi();
}
})();
