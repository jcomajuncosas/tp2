/**
 * Receptor de resultats de la Pràctica de Python → Google Sheet.
 *
 * El full de càlcul ha de tenir una pestanya "Alumnes" amb dues columnes:
 *   A: codi (p. ex. K7M2QX)   B: nom
 * (la genera eines/practica/genera_codis.py). Les pestanyes "Esdeveniments"
 * i "Progrés" es creen soles.
 *
 * Desplegament: Extensions → Apps Script → enganxa aquest fitxer →
 *   Desplega → Nova implementació → Tipus: Aplicació web
 *   Executa com a: Jo · Qui hi té accés: Qualsevol usuari
 * Copia l'URL (acaba en /exec) a config.js → ENDPOINT.
 */

const PESTANYA_ALUMNES = 'Alumnes';
const PESTANYA_LOG = 'Esdeveniments';
const PESTANYA_PROGRES = 'Progrés';
const PESTANYA_ESTAT = 'Estat';        // l'últim estat de cada alumne (JSON), per recuperar-lo a qualsevol ordinador
const CAPCALERA_LOG = ['data', 'codi', 'nom', 'concepte', 'plantilla', 'tipus', 'correcte',
                       'intents', 'segons', 'ratxa', 'dominat', 'repàs', 'resposta'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const d = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const nom = nomDe_(ss, d.codi);
    if (nom === null) return resposta_({ ok: false, error: 'codi desconegut' });

    if (d.estat) desaEstat_(ss, d.codi, d.estat);
    if (d.nomes_estat) return resposta_({ ok: true });

    const log = pestanya_(ss, PESTANYA_LOG, CAPCALERA_LOG);
    log.appendRow([new Date(d.ts || Date.now()), d.codi, nom, d.concepte, d.plantilla, d.tipus,
                   d.correcte ? 'sí' : 'no', d.intents, d.segons, d.ratxa, d.dominat ? 'sí' : 'no',
                   d.repas ? 'sí' : 'no', String(d.resposta || '').slice(0, 2000)]);

    actualitzaProgres_(ss, d, nom);
    return resposta_({ ok: true });
  } catch (err) {
    return resposta_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  const codi = e && e.parameter && e.parameter.codi;
  if (!codi) return resposta_({ ok: true, servei: 'practica-python' });
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const nom = nomDe_(ss, codi);
  if (nom === null) return resposta_({ ok: false, error: 'codi desconegut' });
  const sh = ss.getSheetByName(PESTANYA_ESTAT);
  if (!sh || sh.getLastRow() < 2) return resposta_({ ok: true, nom: nom, estat: null });
  const files = sh.getRange(2, 1, sh.getLastRow() - 1, 3).getValues();
  for (let i = 0; i < files.length; i++) {
    if (String(files[i][0]).toUpperCase() === String(codi).toUpperCase()) {
      return resposta_({ ok: true, nom: nom, estat: JSON.parse(files[i][2]) });
    }
  }
  return resposta_({ ok: true, nom: nom, estat: null });
}

function desaEstat_(ss, codi, estat) {
  const sh = pestanya_(ss, PESTANYA_ESTAT, ['codi', 'actualitzat', 'estat (JSON)']);
  const json = JSON.stringify(estat);
  const quan = new Date(estat.actualitzat || Date.now());
  const n = sh.getLastRow() - 1;
  if (n > 0) {
    const codis = sh.getRange(2, 1, n, 1).getValues();
    for (let i = 0; i < n; i++) {
      if (codis[i][0] === codi) {
        sh.getRange(i + 2, 2, 1, 2).setValues([[quan, json]]);
        return;
      }
    }
  }
  sh.appendRow([codi, quan, json]);
}

function nomDe_(ss, codi) {
  const sh = ss.getSheetByName(PESTANYA_ALUMNES);
  if (!sh || !codi) return null;
  const valors = sh.getDataRange().getValues();
  for (let i = 1; i < valors.length; i++) {
    if (String(valors[i][0]).trim().toUpperCase() === String(codi).toUpperCase()) return valors[i][1];
  }
  return null;
}

function pestanya_(ss, nom, capcalera) {
  let sh = ss.getSheetByName(nom);
  if (!sh) {
    sh = ss.insertSheet(nom);
    sh.appendRow(capcalera);
    sh.setFrozenRows(1);
  }
  return sh;
}

/**
 * Pestanya "Progrés": una fila per alumne, una columna per concepte.
 * Cel·la: "✓" si l'ha dominat; si no, "ratxa · encerts/intents".
 */
function actualitzaProgres_(ss, d, nom) {
  const sh = pestanya_(ss, PESTANYA_PROGRES, ['codi', 'nom', 'darrera activitat', 'exercicis', 'punts']);
  const capcalera = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  let col = capcalera.indexOf(d.concepte) + 1;
  if (col === 0) {
    col = capcalera.length + 1;
    sh.getRange(1, col).setValue(d.concepte);
  }
  const codis = sh.getLastRow() > 1 ? sh.getRange(2, 1, sh.getLastRow() - 1, 1).getValues() : [];
  let fila = -1;
  for (let i = 0; i < codis.length; i++) if (codis[i][0] === d.codi) fila = i + 2;
  if (fila === -1) {
    fila = sh.getLastRow() + 1;
    sh.getRange(fila, 1, 1, 5).setValues([[d.codi, nom, new Date(), 0, 0]]);
  }
  const cel = sh.getRange(fila, col);
  const abans = String(cel.getValue() || '');
  let encerts = 0, intents = 0;
  const m = abans.match(/(\d+)\/(\d+)/);
  if (m) { encerts = Number(m[1]); intents = Number(m[2]); }
  intents += 1;
  if (d.correcte) encerts += 1;
  cel.setValue((d.dominat ? '✓ ' : d.ratxa + ' · ') + encerts + '/' + intents);
  sh.getRange(fila, 3).setValue(new Date());
  sh.getRange(fila, 4).setValue(Number(sh.getRange(fila, 4).getValue() || 0) + 1);
  if (d.punts !== undefined) sh.getRange(fila, 5).setValue(d.punts);
}

function resposta_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
