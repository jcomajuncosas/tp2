// Worker de Python (Pyodide). Tot el codi de l'alumne s'executa aquí, fora del
// fil principal: si es penja (bucle infinit), la pàgina el mata i en crea un altre.
let py = null;
let numpyCarregat = false;

async function inicia(cfg) {
  importScripts(cfg.pyodide + 'pyodide.js');
  py = await loadPyodide({ indexURL: cfg.pyodide });
  for (const f of cfg.fitxers) {
    const r = await fetch(f + '?v=' + cfg.versio);
    if (!r.ok) throw new Error('No puc carregar ' + f);
    py.FS.writeFile('/home/pyodide/' + f.split('/').pop(), await r.text());
  }
  py.runPython('import sys\nsys.path.insert(0, "/home/pyodide")\n' +
               cfg.moduls.map(m => 'import ' + m).join('\n'));
  return py.runPython('import motor\nmotor.cataleg_json()');
}

async function assegura(numpy) {
  if (numpy && !numpyCarregat) {
    await py.loadPackage('numpy');
    numpyCarregat = true;
  }
}

self.onmessage = async (e) => {
  const m = e.data;
  try {
    let res;
    if (m.cmd === 'init') {
      res = await inicia(m.cfg);
    } else if (m.cmd === 'numpy') {
      await assegura(true);
      res = 'ok';
    } else if (m.cmd === 'genera') {
      await assegura(m.numpy);
      py.globals.set('__pid', m.pid);
      py.globals.set('__seed', m.seed);
      res = py.runPython('motor.genera_json(__pid, __seed)');
    } else if (m.cmd === 'corregeix') {
      await assegura(m.numpy);
      py.globals.set('__item', m.item);
      py.globals.set('__resp', m.resposta);
      res = py.runPython('motor.corregeix(__item, __resp)');
    }
    self.postMessage({ id: m.id, ok: true, res });
  } catch (err) {
    self.postMessage({ id: m.id, ok: false, error: String(err && err.message ? err.message : err) });
  }
};
