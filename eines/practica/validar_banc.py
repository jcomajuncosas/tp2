"""
Valida el banc d'exercicis amb CPython (el mateix codi que corre a Pyodide).

    python3 validar_banc.py            # 200 variants per plantilla
    python3 validar_banc.py 1000       # més variants

Per a cada plantilla comprova:
  - genera sense errors amb N llavors diferents, i les variants són diverses
  - predir: el fragment s'executa, imprimeix alguna cosa
  - escriure/ordenar: la referència passa; l'esquelet buit falla; cada mutant
    (error típic d'alumne) falla en com a mínim el 95% de les variants
  - ordenar: les línies arriben desordenades
  - el codi que veu l'alumne no fa servir idiomes vetats al curs
"""
import ast
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'py'))
import motor                       # noqa: E402
import banc_tp1                    # noqa: E402,F401
import banc_tp2                    # noqa: E402,F401

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200

VETATS = {
    'ListComp': 'comprehension', 'DictComp': 'comprehension', 'SetComp': 'comprehension',
    'GeneratorExp': 'generator', 'Lambda': 'lambda', 'IfExp': 'ternari', 'Dict': 'dict',
    'Try': 'try/except', 'Raise': 'raise', 'With': 'with', 'Set': 'set literal',
}
CRIDES_VETADES = {'sorted', 'zip', 'any', 'all', 'next', 'set', 'dict', 'map', 'filter'}


def idiomes_vetats(codi):
    try:
        arbre = ast.parse(codi)
    except SyntaxError as e:
        return ['SINTAXI: %s' % e]
    trobats = []
    for n in ast.walk(arbre):
        k = type(n).__name__
        if k in VETATS:
            trobats.append(VETATS[k])
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in CRIDES_VETADES:
            trobats.append(n.func.id + '()')
    return trobats


def valida(pid):
    p = motor.PLANTILLES[pid]
    problemes = []
    variants = set()
    mutants_passen = {}
    n_mutants = 0
    for seed in range(N):
        try:
            item = p['genera'](__import__('random').Random(seed))
        except Exception as e:                                   # noqa: BLE001
            return ['genera falla (seed %d): %r' % (seed, e)]
        try:
            public = motor.genera(pid, seed)
        except Exception as e:                                   # noqa: BLE001
            return ['motor.genera falla (seed %d): %s' % (seed, e)]
        if p['tipus'] == 'predir':
            variants.add(item['codi'])
            if not public['solucio'].strip():
                problemes.append('seed %d: no imprimeix res' % seed)
            if seed == 0:
                for v in idiomes_vetats(item['codi']):
                    problemes.append('idioma vetat al codi: ' + v)
            # la sortida correcta s'ha d'acceptar com a resposta
            r = __import__('json').loads(motor.corregeix(public, public['solucio']))
            if not r['correcte']:
                problemes.append('seed %d: la sortida correcta no s\'accepta' % seed)
        else:
            variants.add(repr(item['casos']))
            r = motor.corregeix_codi(public, item['referencia'])
            if not r['correcte']:
                problemes.append('seed %d: la referència NO passa: %s' % (seed, r['missatges']))
            if p['tipus'] == 'escriure':
                r = motor.corregeix_codi(public, item['esquelet'])
                if r['correcte']:
                    problemes.append('seed %d: l\'esquelet buit passa!' % seed)
            if p['tipus'] == 'ordenar':
                if public['linies'] == [l for l in item['referencia'].splitlines() if l.strip()]:
                    problemes.append('seed %d: línies no desordenades' % seed)
                r = motor.corregeix_codi(public, '\n'.join(public['linies']))
                if r['correcte'] and seed < 5:
                    problemes.append('seed %d: l\'ordre barrejat ja passa' % seed)
            muts = item.get('mutants', [])
            n_mutants = len(muts)
            for i, m in enumerate(muts):
                r = motor.corregeix_codi(public, m)
                if r['correcte']:
                    mutants_passen[i] = mutants_passen.get(i, 0) + 1
            if seed == 0:
                for camp in ('referencia', 'esquelet'):
                    if camp in item:
                        for v in idiomes_vetats(item[camp]):
                            problemes.append('idioma vetat a %s: %s' % (camp, v))
    if len(variants) < min(10, N // 4):
        problemes.append('poca varietat: %d variants diferents' % len(variants))
    for i, c in mutants_passen.items():
        if c > 0.05 * N:
            problemes.append('mutant %d passa en %d/%d variants' % (i, c, N))
    if p['tipus'] == 'escriure' and n_mutants < 2:
        problemes.append('té menys de 2 mutants')
    return problemes


def main():
    total = 0
    dolentes = 0
    per_concepte = {}
    for pid, p in motor.PLANTILLES.items():
        per_concepte.setdefault(p['concepte'], []).append(p['tipus'])
        probs = valida(pid)
        total += 1
        estat = 'OK ' if not probs else 'ERR'
        if probs:
            dolentes += 1
        print('%s %-28s %-8s %s' % (estat, pid, p['tipus'], ('; '.join(probs[:3]))[:300]))
    print('\n%d plantilles, %d amb problemes' % (total, dolentes))
    for c in motor.CONCEPTES:
        tipus = per_concepte.get(c['id'], [])
        print('  %-22s %-5s %s' % (c['id'], c['banc'], ', '.join(tipus)))
    # blocs.json: cada concepte en exactament un bloc; àrees dels checkpoints vàlides
    import json
    bj = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocs.json')))
    ids = [c['id'] for c in motor.CONCEPTES]
    vistos = []
    for b in bj['blocs']:
        vistos += b['conceptes']
    for cid in ids:
        if vistos.count(cid) != 1:
            print('ERR blocs.json: %s apareix %d vegades' % (cid, vistos.count(cid)))
            dolentes += 1
    for cid in vistos:
        if cid not in ids:
            print('ERR blocs.json: concepte inexistent %s' % cid)
            dolentes += 1
    for cp in bj['checkpoints']:
        for ar in cp['arees']:
            tipus = []
            for cid in ar['conceptes']:
                if cid not in ids:
                    print('ERR %s/%s: concepte inexistent %s' % (cp['id'], ar['id'], cid))
                    dolentes += 1
                for p in motor.PLANTILLES.values():
                    if p['concepte'] == cid:
                        tipus.append(p['tipus'])
            if 'predir' not in tipus or not ('escriure' in tipus or 'ordenar' in tipus):
                print('ERR %s/%s: cal com a mínim una plantilla de predir i una de codi' % (cp['id'], ar['id']))
                dolentes += 1
    print('blocs.json: %d blocs, %d checkpoints' % (len(bj['blocs']), len(bj['checkpoints'])))
    sys.exit(1 if dolentes else 0)


if __name__ == '__main__':
    main()
