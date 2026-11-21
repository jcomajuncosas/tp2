"""
Genera un codi personal per alumne i els enllaços personals.

    python3 genera_codis.py alumnes.txt https://moodle22569.hostkey.in/apps/practica-tp2/

alumnes.txt: un nom per línia. Sortida:
  - codis.csv     → importa'l a la pestanya "Alumnes" del Google Sheet (codi, nom)
  - enllacos.txt  → l'enllaç personal de cada alumne, per enviar-lo en un
                    comentari privat del Classroom
Els codis no contenen caràcters confusibles (0/O, 1/I/L).
Si tornes a executar-lo amb la mateixa llista, els codis ja existents de codis.csv es mantenen.
"""
import csv
import os
import secrets
import sys

ALFABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


def nou_codi(usats):
    while True:
        c = ''
        for _ in range(6):
            c += secrets.choice(ALFABET)
        if c not in usats:
            return c


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    noms = []
    for l in open(sys.argv[1], encoding='utf-8'):
        if l.strip():
            noms.append(l.strip())
    url = sys.argv[2].rstrip('/') + '/'
    existents = {}
    if os.path.exists('codis.csv'):
        for fila in csv.reader(open('codis.csv', encoding='utf-8')):
            if len(fila) == 2 and fila[0] != 'codi':
                existents[fila[1]] = fila[0]
    usats = set(existents.values())
    files = []
    for nom in noms:
        codi = existents.get(nom) or nou_codi(usats)
        usats.add(codi)
        files.append((codi, nom))
    with open('codis.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['codi', 'nom'])
        for codi, nom in files:
            w.writerow([codi, nom])
    with open('enllacos.txt', 'w', encoding='utf-8') as f:
        for codi, nom in files:
            f.write('%s\t%sindex.html?a=%s\n' % (nom, url, codi))
    print('%d codis → codis.csv i enllacos.txt' % len(files))


if __name__ == '__main__':
    main()
