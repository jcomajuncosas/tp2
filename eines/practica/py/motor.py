"""
Motor de la pràctica: genera variants d'exercicis i corregeix respostes.

S'executa igual a Pyodide (navegador) i a CPython (validar_banc.py).
Tres tipus d'exercici:
  predir   — l'alumne escriu què imprimeix un fragment (la resposta correcta
             s'obté EXECUTANT el fragment: no hi ha claus escrites a mà)
  escriure — l'alumne escriu una funció/classe; es prova amb casos aleatoris
             l'esperat dels quals surt d'executar la solució de referència
  ordenar  — línies desordenades d'una solució (Parsons); es corregeix
             executant l'ordre de l'alumne amb els mateixos casos
"""
import ast
import io
import json
import random
import sys
import contextlib

PLANTILLES = {}          # id -> dict(id, concepte, tipus, genera, numpy)
CONCEPTES = []           # llista ordenada de dict(id, banc, titol, descripcio)
_CONCEPTE_IDS = set()


def concepte(cid, banc, titol, descripcio):
    if cid not in _CONCEPTE_IDS:
        CONCEPTES.append({'id': cid, 'banc': banc, 'titol': titol, 'descripcio': descripcio})
        _CONCEPTE_IDS.add(cid)


def plantilla(pid, concepte_id, tipus, numpy=False):
    def deco(f):
        PLANTILLES[pid] = {'id': pid, 'concepte': concepte_id, 'tipus': tipus,
                           'genera': f, 'numpy': numpy}
        return f
    return deco


# --------------------------------------------------------------------------
# Execució aïllada
# --------------------------------------------------------------------------

def executa(codi, ns=None):
    """Executa codi i retorna (sortida_stdout, error_text_o_None, namespace)."""
    if ns is None:
        ns = {'__name__': '__practica__'}
    buf = io.StringIO()
    err = None
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(codi, '<el teu codi>', 'exec'), ns)
    except Exception as e:                       # noqa: BLE001 (motor, no codi d'alumne)
        err = traduir_error(e)
    return buf.getvalue(), err, ns


_ERRORS = {
    'IndexError': "Índex fora de rang: demanes una posició que no existeix",
    'NameError': "Fas servir un nom que no està definit (o està mal escrit)",
    'TypeError': "Operació amb tipus incompatibles (o crida amb arguments incorrectes)",
    'ZeroDivisionError': "Divisió per zero",
    'SyntaxError': "Error de sintaxi",
    'IndentationError': "Error d'indentació",
    'AttributeError': "L'objecte no té aquest atribut o mètode",
    'ValueError': "Valor incorrecte per a aquesta operació",
    'UnboundLocalError': "Fas servir una variable local abans d'assignar-li valor",
}


def traduir_error(e):
    nom = type(e).__name__
    linia = ''
    tb = e.__traceback__
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == '<el teu codi>':
            linia = ' (línia %d)' % tb.tb_lineno
        tb = tb.tb_next
    if isinstance(e, SyntaxError) and e.lineno:
        linia = ' (línia %d)' % e.lineno
    explicacio = _ERRORS.get(nom, '')
    return '%s%s: %s%s' % (nom, linia, e, (' — ' + explicacio) if explicacio else '')


def normalitza_sortida(text):
    linies = []
    for l in text.strip().splitlines():
        l = ' '.join(l.split())
        for a, b in (('[ ', '['), (' ]', ']'), (' ,', ','), ('( ', '('), (' )', ')')):
            while a in l:
                l = l.replace(a, b)
        l = l.replace(',', ', ').replace(',  ', ', ')
        linies.append(l.strip())
    while linies and linies[-1] == '':
        linies.pop()
    return '\n'.join(linies)


def iguals(a, b):
    try:
        import numpy as np
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            a2 = np.asarray(a, dtype=float)
            b2 = np.asarray(b, dtype=float)
            return a2.shape == b2.shape and bool(np.allclose(a2, b2, atol=1e-6))
    except ImportError:
        pass
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) < 1e-6
        except (TypeError, ValueError):
            return False
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if type(a) is not type(b) or len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if not iguals(x, y):
                return False
        return True
    return a == b


def mostra(v):
    try:
        import numpy as np
        if isinstance(v, np.ndarray):
            return 'array(' + np.array2string(np.round(v, 4), separator=', ', threshold=12) + ')'
    except ImportError:
        pass
    if isinstance(v, float):
        return repr(round(v, 6))
    return repr(v)


# --------------------------------------------------------------------------
# Generació
# --------------------------------------------------------------------------

def _prepara_casos(item):
    """Executa la referència per calcular l'esperat de cada cas."""
    _, err, ns = executa(item.get('preambul', '') + '\n' + item['referencia'] + '\n' + item.get('ajudants', ''))
    if err:
        raise RuntimeError('La referència falla: ' + err)
    esperats = []
    for crida in item['casos']:
        _, err, ns2 = executa('__r = ' + crida, ns)
        if err:
            raise RuntimeError('Cas %s falla a la referència: %s' % (crida, err))
        esperats.append(ns2['__r'])
    return esperats


def genera(pid, seed):
    """Retorna un ítem serialitzable (JSON) per al navegador."""
    p = PLANTILLES[pid]
    rng = random.Random(seed)
    item = p['genera'](rng)
    item['id'] = pid
    item['concepte'] = p['concepte']
    item['tipus'] = p['tipus']
    item['seed'] = seed
    if p['tipus'] == 'predir':
        sortida, err, _ = executa(item['codi'])
        if err:
            raise RuntimeError('El fragment de predir falla: ' + err)
        item['solucio'] = sortida
    else:
        item['solucio'] = item['referencia']
        if p['tipus'] == 'ordenar':
            linies = [l for l in item['referencia'].splitlines() if l.strip()]
            item['linies'] = barreja_diferent(linies, rng)
    item.pop('mutants', None)
    return item


def barreja_diferent(linies, rng):
    if len(linies) < 2:
        return list(linies)
    for _ in range(20):
        copia = list(linies)
        rng.shuffle(copia)
        if copia != linies:
            return copia
    return list(reversed(linies))


# --------------------------------------------------------------------------
# Correcció
# --------------------------------------------------------------------------

def _usa(codi, noms_nodes):
    try:
        arbre = ast.parse(codi)
    except SyntaxError:
        return False
    for n in ast.walk(arbre):
        if type(n).__name__ in noms_nodes:
            return True
    return False


def corregeix_codi(item, codi):
    """Per a 'escriure' i 'ordenar'. Retorna dict(correcte, missatges)."""
    if item.get('requereix'):
        req = item['requereix']                      # p. ex. ['For', 'While']
        if not _usa(codi, req):
            return {'correcte': False, 'missatges': [item.get('missatge_requereix',
                    "Aquest exercici s'ha de resoldre amb un bucle")]}
    if item.get('prohibeix'):
        try:
            arbre = ast.parse(codi)
        except SyntaxError:
            arbre = None
        if arbre is not None:
            for n in ast.walk(arbre):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in item['prohibeix']:
                    return {'correcte': False, 'missatges': ["En aquest exercici no pots fer servir `%s()`: fes-ho tu amb un bucle" % n.func.id]}
    preambul = item.get('preambul', '')
    _, err, ns = executa(preambul + '\n' + codi + '\n' + item.get('ajudants', ''))
    if err:
        if preambul:
            err = err.replace('(línia ', '(línia ~')
        return {'correcte': False, 'missatges': [err]}
    if item.get('funcio') and item['funcio'] not in ns:
        return {'correcte': False, 'missatges': ["No trobo `%s`: comprova el nom" % item['funcio']]}
    esperats = _prepara_casos(item)
    missatges = []
    for crida, esperat in zip(item['casos'], esperats):
        sortida, err, ns2 = executa('__r = ' + crida, dict(ns))
        if err:
            missatges.append('`%s` → error: %s' % (crida, err))
        elif not iguals(ns2['__r'], esperat):
            m = '`%s` → has retornat %s, s\'esperava %s' % (crida, mostra(ns2['__r']), mostra(esperat))
            if ns2['__r'] is None:
                m += ' (et falta un `return`?)'
            missatges.append(m)
        if len(missatges) >= 3:
            break
    return {'correcte': not missatges, 'missatges': missatges}


def corregeix(item_json, resposta):
    item = json.loads(item_json) if isinstance(item_json, str) else item_json
    if item['tipus'] == 'predir':
        bona = normalitza_sortida(item['solucio'])
        teva = normalitza_sortida(resposta)
        return json.dumps({'correcte': bona == teva,
                           'missatges': [] if bona == teva else ['La sortida correcta era:'],
                           'solucio': item['solucio']})
    res = corregeix_codi(item, resposta)
    return json.dumps(res)


def genera_json(pid, seed):
    return json.dumps(genera(pid, seed))


def cataleg_json():
    pl = []
    for p in PLANTILLES.values():
        pl.append({'id': p['id'], 'concepte': p['concepte'], 'tipus': p['tipus'], 'numpy': p['numpy']})
    return json.dumps({'conceptes': CONCEPTES, 'plantilles': pl})
