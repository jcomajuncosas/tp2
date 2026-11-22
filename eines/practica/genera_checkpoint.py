"""
Genera els fulls en paper d'un checkpoint: una variant diferent per a cada alumne
(mateix banc d'exercicis que l'eina web) i la clau de correcció corresponent.

    python3 genera_checkpoint.py CP1 codis.csv
    python3 genera_checkpoint.py CP2 codis.csv
    python3 genera_checkpoint.py CP1 codis.csv --recuperacio              # variants noves
    python3 genera_checkpoint.py CP1 codis.csv --recuperacio --arees A,C  # només aquestes àrees
    python3 genera_checkpoint.py CP1 codis.csv --nomes K7M2QX,422Z2Y      # només aquests alumnes

Sortida (a checkpoints/, que no es comita):
  CP1_fulls.html      → un full per alumne (obre'l al navegador i imprimeix-lo: Cmd+P)
  CP1_claus.html      → clau de correcció per alumne + taula de recollida per àrees

Les àrees i els conceptes de cada checkpoint són a blocs.json. Cada àrea té dos exercicis:
un de "què imprimeix?" i un d'escriure o ordenar codi (de conceptes diferents si es pot).
La variant depèn del codi de l'alumne: tornar a executar l'script dona els mateixos fulls.
"""
import argparse
import csv
import hashlib
import html
import json
import os
import random
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, 'py'))
import motor          # noqa: E402
import banc_tp1       # noqa: E402,F401
import banc_tp2       # noqa: E402,F401

LLETRES = 'ABCDEFGHIJKLMNOP'


# --------------------------------------------------------------------------- generació
def llavor(*parts):
    return int(hashlib.sha256('|'.join(parts).encode()).hexdigest()[:12], 16)


def plantilles_de(conceptes, tipus):
    out = []
    for p in motor.PLANTILLES.values():
        if p['concepte'] in conceptes and p['tipus'] in tipus:
            out.append(p)
    return out


def exercicis_area(area, rng, seed_base):
    """Un 'predir' i un de codi, de conceptes diferents si es pot."""
    predirs = plantilles_de(area['conceptes'], ('predir',))
    codis = plantilles_de(area['conceptes'], ('escriure', 'ordenar'))
    p1 = rng.choice(predirs)
    altres = []
    for p in codis:
        if p['concepte'] != p1['concepte']:
            altres.append(p)
    p2 = rng.choice(altres or codis)
    it1 = motor.genera(p1['id'], seed_base + 1)
    it2 = motor.genera(p2['id'], seed_base + 2)
    return [it1, it2]


# --------------------------------------------------------------------------- HTML
def md(text):
    def enlinia(s):
        s = html.escape(s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        return s
    out = []
    for bloc in re.split(r'\n\n+', text.strip()):
        linies = bloc.split('\n')
        if all(l.startswith('- ') for l in linies):
            out.append('<ul>' + ''.join('<li>' + enlinia(l[2:]) + '</li>' for l in linies) + '</ul>')
        else:
            out.append('<p>' + '<br>'.join(enlinia(l) for l in linies) + '</p>')
    return ''.join(out)


def enunciat_paper(it):
    """L'enunciat de l'eina, adaptat al paper."""
    t = it['enunciat']
    if it['tipus'] == 'ordenar':
        t = t.replace('Ordena les línies', 'Escriu l\'ordre de les línies (amb les lletres)')
        t = t.replace("La indentació ja hi és.", "La indentació ja hi és.")
    return t


def html_exercici(it, n, titol_area=''):
    tipus = {'predir': 'Què imprimeix?', 'escriure': 'Escriu el codi', 'ordenar': 'Ordena les línies'}[it['tipus']]
    h = ['<div class="ex">' + titol_area + '<div class="ex-cap"><span class="num">%d</span> %s</div>' % (n, tipus)]
    text = enunciat_paper(it)
    if it['tipus'] == 'predir':
        text = re.sub(r'^Què imprimeix\?\s*', '', text)          # ja ho diu la capçalera
    if text.strip():
        h.append(md(text))
    if it['tipus'] == 'predir':
        h.append('<pre class="codi">%s</pre>' % html.escape(it['codi'].rstrip()))
        h.append('<div class="caixa">La sortida:</div>')
    elif it['tipus'] == 'escriure':
        h.append('<pre class="codi">%s</pre>' % html.escape(it['esquelet'].rstrip()))
        h.append('<div class="caixa gran">El teu codi:</div>')
    else:
        files = []
        for i, l in enumerate(it['linies']):
            files.append('<tr><td class="lletra">%s</td><td><pre class="linia">%s</pre></td></tr>'
                         % (LLETRES[i], html.escape(l)))
        h.append('<table class="linies">%s</table>' % ''.join(files))
        h.append('<div class="caixa ordre">Ordre (lletres):</div>')
    h.append('</div>')
    return ''.join(h)


def clau_exercici(it, n):
    h = ['<div class="clau-ex"><strong>%d.</strong> <span class="pid">%s</span>' % (n, it['id'])]
    if it['tipus'] == 'predir':
        h.append('<pre class="codi">%s</pre>' % html.escape(it['solucio'].rstrip()))
        h.append('<p class="nota">Accepta decimals arrodonits (≥ 2 xifres), coma decimal i petites diferències de format '
                 '(com l\'eina). Els valors han de ser exactes.</p>')
    elif it['tipus'] == 'escriure':
        h.append('<pre class="codi">%s</pre>' % html.escape(it['solucio'].rstrip()))
        try:
            esperats = motor._prepara_casos(it)
            proves = []
            for crida, e in zip(it['casos'], esperats):
                if not crida.startswith('__'):
                    proves.append('<li><code>%s</code> → <code>%s</code></li>' % (html.escape(crida), html.escape(motor.mostra(e))))
            if proves:
                h.append('<p class="nota">Per comprovar-ho mentalment:</p><ul class="proves">%s</ul>' % ''.join(proves[:4]))
        except Exception as e:                                       # noqa: BLE001
            h.append('<p class="nota">(%s)</p>' % html.escape(str(e)))
        if it.get('requereix'):
            h.append('<p class="nota">Ha de fer servir un bucle.</p>')
        h.append('<p class="nota">Accepta qualsevol solució equivalent.</p>')
    else:
        ref = [l for l in it['solucio'].splitlines() if l.strip()]
        usades = set()
        ordre = []
        for l in ref:
            for i, x in enumerate(it['linies']):
                if x == l and i not in usades:
                    usades.add(i)
                    ordre.append(LLETRES[i])
                    break
        sobren = [LLETRES[i] for i in range(len(it['linies'])) if i not in usades]
        h.append('<p class="ordre-clau">%s</p>' % ' '.join(ordre))
        if sobren:
            h.append('<p class="nota">Sobra: %s. Si l\'ordre dona un programa equivalent, també és correcte.</p>'
                     % ', '.join(sobren))
    h.append('</div>')
    return ''.join(h)


CSS = """
@page { size: A4; margin: 14mm 15mm; }
body { font: 10.5pt/1.4 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: #111; }
.full { page-break-after: always; }
.full:last-child { page-break-after: auto; }
.cap { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1.5px solid #111;
       padding-bottom: 4px; margin-bottom: 6px; }
.cap h1 { font-size: 13pt; margin: 0; }
.cap .qui { font-size: 10pt; }
.instr { font-size: 9pt; color: #333; margin: 4px 0 8px; }
h2 { font-size: 11pt; margin: 12px 0 4px; padding: 2px 6px; background: #eee; }
.ex { margin: 6px 0 10px; page-break-inside: avoid; }
.ex-cap { font-weight: 600; margin-bottom: 2px; }
.num { display: inline-block; min-width: 1.3em; }
.ex p { margin: 2px 0 4px; }
code, pre { font-family: Menlo, Consolas, "Courier New", monospace; font-size: 9.2pt; }
pre.codi { background: #f4f4f4; border: 1px solid #ddd; padding: 5px 8px; margin: 3px 0 5px; white-space: pre; }
.caixa { border: 1px solid #999; border-radius: 3px; min-height: 22mm; padding: 2px 6px; color: #777; font-size: 8.5pt; }
.caixa.gran { min-height: 52mm; }
.caixa.ordre { min-height: 9mm; }
table.linies { border-collapse: collapse; margin: 3px 0 5px; }
table.linies td { padding: 0 4px; vertical-align: top; }
td.lletra { font-weight: 700; }
pre.linia { margin: 0; white-space: pre; }
.clau-alumne { page-break-before: always; padding-top: 2px; }
.clau-alumne > strong { font-size: 12pt; }
.clau-ex { margin: 3px 0 6px 10px; page-break-inside: avoid; }
h1 { font-size: 14pt; }
.pid { color: #888; font-size: 8pt; }
.nota { font-size: 8.5pt; color: #555; margin: 1px 0; }
.ordre-clau { font: 700 11pt Menlo, monospace; margin: 2px 0; }
ul.proves { margin: 0 0 2px 14px; padding: 0; font-size: 8.8pt; }
.graella { border-collapse: collapse; margin-top: 4px; }
.graella td, .graella th { border: 1px solid #999; padding: 2px 8px; font-size: 9pt; }
"""


def pagina(titol, cos):
    return ('<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>'
            '<body>%s</body></html>' % (html.escape(titol), CSS, cos))


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('checkpoint', help='CP1, CP2… (de blocs.json)')
    ap.add_argument('codis', help='codis.csv (codi, nom) generat per genera_codis.py')
    ap.add_argument('--recuperacio', action='store_true', help='variants noves (diferents de les del checkpoint)')
    ap.add_argument('--arees', help='només aquestes àrees, p. ex. A,C')
    ap.add_argument('--nomes', help='només aquests codis d\'alumne, separats per comes')
    ap.add_argument('--sortida', default=os.path.join(AQUI, 'checkpoints'))
    a = ap.parse_args()

    bj = json.load(open(os.path.join(AQUI, 'blocs.json'), encoding='utf-8'))
    cp = None
    for c in bj['checkpoints']:
        if c['id'] == a.checkpoint:
            cp = c
    if cp is None:
        sys.exit('Checkpoint desconegut: %s (n\'hi ha: %s)' % (a.checkpoint, ', '.join(c['id'] for c in bj['checkpoints'])))
    arees = cp['arees']
    if a.arees:
        triades = a.arees.upper().split(',')
        arees = [ar for ar in arees if ar['id'] in triades]

    alumnes = []
    for fila in csv.reader(open(a.codis, encoding='utf-8')):
        if len(fila) >= 2 and fila[0] != 'codi' and fila[0].strip():
            alumnes.append((fila[0].strip().upper(), fila[1].strip()))
    if a.nomes:
        nomes = a.nomes.upper().split(',')
        alumnes = [x for x in alumnes if x[0] in nomes]
    if not alumnes:
        sys.exit('Cap alumne a %s' % a.codis)

    sufix = 'recuperacio' if a.recuperacio else 'checkpoint'
    titol = cp['titol'] + (' — Recuperació' if a.recuperacio else '')
    fulls, claus = [], []
    taula = ['<table class="graella"><tr><th>Alumne</th>' + ''.join('<th>%s</th>' % ar['id'] for ar in arees) + '</tr>']
    for codi, nom in alumnes:
        rng = random.Random(llavor(codi, cp['id'], sufix))
        cos = ['<div class="full"><div class="cap"><h1>%s</h1><span class="qui">%s · <strong>%s</strong></span></div>'
               % (html.escape(titol), html.escape(nom), codi)]
        cos.append('<p class="instr">%d minuts · sense ordinador ni apunts. Cada àrea té dos exercicis: la superes si tots '
                   'dos són correctes. Si no la superes, la podràs recuperar més endavant amb exercicis nous. '
                   'Si no saps alguna cosa, escriu el que creus i per què.</p>' % cp['minuts'])
        clau = ['<div class="clau-alumne"><strong>%s</strong> · %s' % (html.escape(nom), codi)]
        n = 1
        for ar in arees:
            its = exercicis_area(ar, rng, llavor(codi, cp['id'], sufix, ar['id']))
            titol_area = '<h2>Àrea %s · %s</h2>' % (ar['id'], html.escape(ar['nom']))
            clau.append('<div><em>Àrea %s · %s</em></div>' % (ar['id'], html.escape(ar['nom'])))
            for k, it in enumerate(its):
                cos.append(html_exercici(it, n, titol_area if k == 0 else ''))
                clau.append(clau_exercici(it, n))
                n += 1
        cos.append('</div>')
        clau.append('</div>')
        fulls.append(''.join(cos))
        claus.append(''.join(clau))
        taula.append('<tr><td>%s</td>' % html.escape(nom) + '<td>&nbsp;☐&nbsp;</td>' * len(arees) + '</tr>')
    taula.append('</table>')

    os.makedirs(a.sortida, exist_ok=True)
    base = os.path.join(a.sortida, cp['id'] + ('_recuperacio' if a.recuperacio else ''))
    open(base + '_fulls.html', 'w', encoding='utf-8').write(pagina(titol, ''.join(fulls)))
    capclau = ('<h1>%s — claus de correcció</h1><p class="instr">Una àrea es supera si els dos exercicis són correctes. '
               'Marca les àrees superades a la taula.</p>' % html.escape(titol))
    open(base + '_claus.html', 'w', encoding='utf-8').write(
        pagina(titol + ' — claus', capclau + ''.join(taula) + ''.join(claus)))
    print('%d alumnes · %d àrees → %s_fulls.html i %s_claus.html' % (len(alumnes), len(arees), base, base))


if __name__ == '__main__':
    main()
