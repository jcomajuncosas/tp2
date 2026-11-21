"""
Banc TP1 — mecànica de Python en context musical neutre.
Pensat també per a l'anivellament a l'inici de TP2 (edicions futures):
NO conté cap contingut propi de TP2 (ni NumPy, ni àudio, ni classes).

Cada plantilla rep un random.Random i retorna un dict:
  predir:   enunciat, codi
  escriure: enunciat, esquelet, referencia, casos, funcio, [requereix, prohibeix, mutants]
  ordenar:  enunciat, referencia, casos, funcio, [mutants]
"""
from motor import concepte, plantilla

NOMS_LLISTA = ['notes', 'melodia', 'acord', 'linia', 'motiu', 'escala']


def notes_aleatories(rng, n, baix=55, alt=79):
    llista = []
    for _ in range(n):
        llista.append(rng.randint(baix, alt))
    return llista


def numeros(rng, n, baix=-9, alt=9):
    llista = []
    for _ in range(n):
        llista.append(rng.randint(baix, alt))
    return llista


# ==========================================================================
concepte('t1_aritmetica', 'tp1', "Operadors: / // % ** i conversions",
         "Divisió real i entera, residu, potència, int(), round(), abs()")
# ==========================================================================

@plantilla('t1_arit_compas', 't1_aritmetica', 'predir')
def _(rng):
    per_compas = rng.choice([3, 4, 6])
    pulsacio = rng.randint(per_compas + 1, 6 * per_compas)
    while pulsacio % per_compas == 0:
        pulsacio = pulsacio + 1
    codi = (
        "pulsacio = %d       # comptem les pulsacions des de 0\n"
        "per_compas = %d\n"
        "print(pulsacio // per_compas, pulsacio %% per_compas)\n"
        "print(pulsacio / per_compas)\n" % (pulsacio, per_compas))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_arit_conversions', 't1_aritmetica', 'predir')
def _(rng):
    x = rng.randint(1, 9) + rng.choice([0.2, 0.3, 0.7, 0.8])
    e = rng.randint(2, 5)
    b = rng.choice([2, 3])
    v = -rng.randint(2, 30)
    codi = (
        "x = %s\n"
        "print(int(x), round(x))\n"
        "print(%d ** %d, abs(%d))\n" % (x, b, e, v))
    return {'enunciat': "Què imprimeix? Fixa't en la diferència entre `int()` i `round()`.", 'codi': codi}


@plantilla('t1_arit_octava', 't1_aritmetica', 'escriure')
def _(rng):
    return {
        'enunciat': ("Escriu `octava_i_classe(nota)`: rep un número de nota MIDI i retorna dos valors, "
                     "**l'octava** (`nota` dividit enterament per 12, menys 1) i la **classe de nota** "
                     "(de 0 = do a 11 = si: el residu de dividir per 12).\n\n"
                     "Exemple: `octava_i_classe(61)` → `(4, 1)` (do# de l'octava 4)."),
        'esquelet': "def octava_i_classe(nota):\n    pass\n",
        'referencia': "def octava_i_classe(nota):\n    octava = nota // 12 - 1\n    classe = nota % 12\n    return octava, classe\n",
        'funcio': 'octava_i_classe',
        'casos': ['octava_i_classe(%d)' % n for n in [60, 61, 71, 72, rng.randint(21, 108), rng.randint(21, 108)]],
        'mutants': [
            "def octava_i_classe(nota):\n    return nota / 12 - 1, nota % 12\n",
            "def octava_i_classe(nota):\n    return nota // 12, nota % 12\n",
            "def octava_i_classe(nota):\n    return nota % 12, nota // 12 - 1\n",
        ],
    }


@plantilla('t1_arit_compas_escriure', 't1_aritmetica', 'escriure')
def _(rng):
    return {
        'enunciat': ("Escriu `on_som(pulsacio, per_compas)`: `pulsacio` compta les pulsacions **des de 0**. "
                     "Retorna el **compàs** i el **temps** dins el compàs, però comptant **des d'1**, "
                     "com un músic.\n\n"
                     "Exemple: amb 4 temps per compàs, la pulsació 0 és `(1, 1)` i la 5 és `(2, 2)`."),
        'esquelet': "def on_som(pulsacio, per_compas):\n    pass\n",
        'referencia': "def on_som(pulsacio, per_compas):\n    compas = pulsacio // per_compas + 1\n    temps = pulsacio % per_compas + 1\n    return compas, temps\n",
        'funcio': 'on_som',
        'casos': ['on_som(0, 4)', 'on_som(5, 4)', 'on_som(%d, 3)' % rng.randint(6, 30),
                  'on_som(%d, 4)' % rng.randint(6, 30), 'on_som(%d, 6)' % rng.randint(6, 30)],
        'mutants': [
            "def on_som(pulsacio, per_compas):\n    return pulsacio // per_compas, pulsacio % per_compas\n",
            "def on_som(pulsacio, per_compas):\n    return pulsacio / per_compas + 1, pulsacio % per_compas + 1\n",
            "def on_som(pulsacio, per_compas):\n    return pulsacio % per_compas + 1, pulsacio // per_compas + 1\n",
        ],
    }


# ==========================================================================
concepte('t1_index', 'tp1', "Índexs de llista",
         "Posicions des de 0, índexs negatius (-1 = l'últim), len()")
# ==========================================================================

@plantilla('t1_index_llegir', 't1_index', 'predir')
def _(rng):
    nom = rng.choice(NOMS_LLISTA)
    llista = notes_aleatories(rng, rng.randint(4, 7))
    k = rng.randint(1, len(llista) - 2)
    neg = rng.randint(2, len(llista))
    codi = (
        "%s = %s\n"
        "print(%s[0], %s[-1])\n"
        "print(%s[%d], %s[-%d])\n"
        "print(len(%s))\n" % (nom, llista, nom, nom, nom, k, nom, neg, nom))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_index_modificar', 't1_index', 'predir')
def _(rng):
    nom = rng.choice(NOMS_LLISTA)
    llista = notes_aleatories(rng, rng.randint(4, 6))
    i = rng.randint(0, len(llista) - 1)
    d = rng.choice([12, -12, 7, 5])
    codi = (
        "%s = %s\n"
        "%s[%d] = %s[%d] + (%d)\n"
        "%s[-1] = %s[0]\n"
        "print(%s)\n" % (nom, llista, nom, i, nom, i, d, nom, nom, nom))
    return {'enunciat': "Què imprimeix? (Escriu la llista sencera.)", 'codi': codi}


@plantilla('t1_index_extrems', 't1_index', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('extrems(%s)' % notes_aleatories(rng, rng.randint(2, 8)))
    casos.append('extrems([%d])' % rng.randint(50, 70))
    return {
        'enunciat': ("Escriu `extrems(llista)`: retorna el **primer** i l'**últim** element d'una llista "
                     "(de qualsevol longitud, com a mínim 1).\n\nExemple: `extrems([60, 64, 67])` → `(60, 67)`."),
        'esquelet': "def extrems(llista):\n    pass\n",
        'referencia': "def extrems(llista):\n    return llista[0], llista[-1]\n",
        'funcio': 'extrems',
        'casos': casos,
        'mutants': [
            "def extrems(llista):\n    return llista[0], llista[len(llista)]\n",
            "def extrems(llista):\n    return llista[1], llista[-1]\n",
            "def extrems(llista):\n    return llista[0], llista[-2]\n",
        ],
    }


@plantilla('t1_index_penultim', 't1_index', 'escriure')
def _(rng):
    casos = []
    for _ in range(5):
        casos.append('penultim(%s)' % notes_aleatories(rng, rng.randint(2, 8)))
    return {
        'enunciat': ("Escriu `penultim(llista)`: retorna l'element **just abans de l'últim** "
                     "(la llista té com a mínim 2 elements).\n\nExemple: `penultim([60, 62, 64, 65])` → `64`."),
        'esquelet': "def penultim(llista):\n    pass\n",
        'referencia': "def penultim(llista):\n    return llista[-2]\n",
        'funcio': 'penultim',
        'casos': casos,
        'mutants': [
            "def penultim(llista):\n    return llista[-1]\n",
            "def penultim(llista):\n    return llista[len(llista) - 1]\n",
            "def penultim(llista):\n    return llista[1]\n",
        ],
    }


# ==========================================================================
concepte('t1_talls', 'tp1', "Talls de llista",
         "llista[a:b] (b no inclòs), [:n], [-n:], [::-1], [::2]")
# ==========================================================================

@plantilla('t1_talls_llegir', 't1_talls', 'predir')
def _(rng):
    nom = rng.choice(NOMS_LLISTA)
    llista = notes_aleatories(rng, rng.randint(6, 8))
    a = rng.randint(1, 3)
    b = rng.randint(a + 1, len(llista) - 1)
    opcions = ['%s[:%d]' % (nom, rng.randint(2, 4)), '%s[-%d:]' % (nom, rng.randint(2, 3)),
               '%s[::-1]' % nom, '%s[::2]' % nom, '%s[1:-1]' % nom]
    rng.shuffle(opcions)
    codi = (
        "%s = %s\n"
        "print(%s[%d:%d])\n"
        "print(%s)\n"
        "print(%s)\n" % (nom, llista, nom, a, b, opcions[0], opcions[1]))
    return {'enunciat': "Què imprimeix? Recorda: a `[a:b]`, `b` **no** hi és inclòs. "
                        "`[::-1]` és la llista al revés; `[::2]`, un de cada dos.", 'codi': codi}


@plantilla('t1_talls_retalla', 't1_talls', 'escriure')
def _(rng):
    casos = []
    for _ in range(5):
        l = notes_aleatories(rng, rng.randint(6, 10))
        inici = rng.randint(0, 3)
        n = rng.randint(1, len(l) - inici)
        casos.append('fragment(%s, %d, %d)' % (l, inici, n))
    return {
        'enunciat': ("Escriu `fragment(llista, inici, n)`: retorna **`n` elements** de la llista "
                     "començant a la posició `inici`. Fes-ho amb un tall.\n\n"
                     "Exemple: `fragment([60, 62, 64, 65, 67], 1, 3)` → `[62, 64, 65]`."),
        'esquelet': "def fragment(llista, inici, n):\n    pass\n",
        'referencia': "def fragment(llista, inici, n):\n    return llista[inici:inici + n]\n",
        'funcio': 'fragment',
        'casos': casos,
        'mutants': [
            "def fragment(llista, inici, n):\n    return llista[inici:n]\n",
            "def fragment(llista, inici, n):\n    return llista[inici:inici + n + 1]\n",
            "def fragment(llista, inici, n):\n    return llista[inici + 1:inici + n + 1]\n",
        ],
    }


@plantilla('t1_talls_retrograd', 't1_talls', 'escriure')
def _(rng):
    casos = []
    for _ in range(5):
        casos.append('retrograd_sense_extrems(%s)' % notes_aleatories(rng, rng.randint(3, 8)))
    return {
        'enunciat': ("Escriu `retrograd_sense_extrems(motiu)`: treu la **primera** i l'**última** nota i "
                     "retorna la resta **al revés** (retrogradació). Dues operacions de tall.\n\n"
                     "Exemple: `retrograd_sense_extrems([60, 62, 64, 65, 67])` → `[65, 64, 62]`."),
        'esquelet': "def retrograd_sense_extrems(motiu):\n    pass\n",
        'referencia': "def retrograd_sense_extrems(motiu):\n    mig = motiu[1:-1]\n    return mig[::-1]\n",
        'funcio': 'retrograd_sense_extrems',
        'casos': casos,
        'mutants': [
            "def retrograd_sense_extrems(motiu):\n    return motiu[::-1]\n",
            "def retrograd_sense_extrems(motiu):\n    return motiu[1:-1]\n",
            "def retrograd_sense_extrems(motiu):\n    return motiu[-1:1:-1]\n",
        ],
    }


# ==========================================================================
concepte('t1_bucles', 'tp1', "Bucles for i while",
         "range(inici, final, pas), recórrer una llista, while amb condició")
# ==========================================================================

@plantilla('t1_bucles_range', 't1_bucles', 'predir')
def _(rng):
    if rng.random() < 0.7:
        a = rng.randint(0, 4)
        pas = rng.choice([1, 2, 3])
        b = a + pas * rng.randint(2, 4) + rng.choice([0, 1])
        codi = "for i in range(%d, %d, %d):\n    print(i)\n" % (a, b, pas)
    else:
        a = rng.randint(5, 9)
        b = rng.randint(0, 2)
        pas = rng.choice([-1, -2])
        codi = "for i in range(%d, %d, %d):\n    print(i)\n" % (a, b, pas)
    return {'enunciat': "Què imprimeix? (Un número per línia.)", 'codi': codi}


@plantilla('t1_bucles_llista_index', 't1_bucles', 'predir')
def _(rng):
    nom = rng.choice(NOMS_LLISTA)
    llista = notes_aleatories(rng, rng.randint(4, 5))
    n = rng.randint(2, len(llista) - 1)
    codi = (
        "%s = %s\n"
        "for i in range(%d):\n"
        "    print(i, %s[i] - %s[0])\n" % (nom, llista, n, nom, nom))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_bucles_while', 't1_bucles', 'predir')
def _(rng):
    n = rng.choice([100, 96, 80, 120, 64, 90])
    lim = rng.choice([5, 8, 10, 12])
    div = rng.choice([2, 3])
    codi = (
        "durada = %d\n"
        "while durada > %d:\n"
        "    durada = durada // %d\n"
        "    print(durada)\n" % (n, lim, div))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_bucles_escala', 't1_bucles', 'escriure')
def _(rng):
    casos = []
    for _ in range(5):
        casos.append('serie(%d, %d, %d)' % (rng.randint(40, 70), rng.randint(1, 8), rng.choice([1, 2, 3, 5, 7, -2])))
    casos.append('serie(60, 0, 2)')
    return {
        'enunciat': ("Escriu `serie(inici, n, pas)`: retorna una llista de **`n` notes**, començant a `inici` "
                     "i sumant `pas` cada vegada. Fes-ho amb un bucle i `append`.\n\n"
                     "Exemple: `serie(60, 4, 2)` → `[60, 62, 64, 66]` (escala de tons)."),
        'esquelet': "def serie(inici, n, pas):\n    pass\n",
        'referencia': ("def serie(inici, n, pas):\n    resultat = []\n    nota = inici\n"
                       "    for i in range(n):\n        resultat.append(nota)\n        nota = nota + pas\n"
                       "    return resultat\n"),
        'funcio': 'serie',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def serie(inici, n, pas):\n    resultat = []\n    for i in range(n + 1):\n        resultat.append(inici + i * pas)\n    return resultat\n",
            "def serie(inici, n, pas):\n    resultat = []\n    for i in range(1, n + 1):\n        resultat.append(inici + i * pas)\n    return resultat\n",
            "def serie(inici, n, pas):\n    for i in range(n):\n        resultat = []\n        resultat.append(inici + i * pas)\n    return resultat\n",
        ],
    }


# ==========================================================================
concepte('t1_acumuladors', 'tp1', "Comptar, sumar, buscar",
         "Patrons d'acumulador: un comptador, una suma, un màxim, el primer que compleix")
# ==========================================================================

@plantilla('t1_acum_traca', 't1_acumuladors', 'predir')
def _(rng):
    nom = rng.choice(['velocities', 'intensitats', 'cops'])
    llista = numeros(rng, rng.randint(5, 7), 10, 127)
    llindar = rng.choice([50, 64, 80, 100])
    codi = (
        "%s = %s\n"
        "compte = 0\n"
        "total = 0\n"
        "for v in %s:\n"
        "    if v > %d:\n"
        "        compte = compte + 1\n"
        "        total = total + v\n"
        "print(compte, total)\n" % (nom, llista, nom, llindar))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_acum_compta', 't1_acumuladors', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('compta_majors(%s, %d)' % (numeros(rng, rng.randint(4, 9), 0, 127), rng.choice([40, 64, 90])))
    casos.append('compta_majors([64, 64, 65], 64)')
    casos.append('compta_majors([], 50)')
    return {
        'enunciat': ("Escriu `compta_majors(llista, llindar)`: retorna **quants** elements són "
                     "**estrictament més grans** que `llindar`. Amb un bucle.\n\n"
                     "Exemple: `compta_majors([30, 90, 64, 100], 64)` → `2`."),
        'esquelet': "def compta_majors(llista, llindar):\n    pass\n",
        'referencia': ("def compta_majors(llista, llindar):\n    compte = 0\n    for x in llista:\n"
                       "        if x > llindar:\n            compte = compte + 1\n    return compte\n"),
        'funcio': 'compta_majors',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def compta_majors(llista, llindar):\n    compte = 0\n    for x in llista:\n        if x >= llindar:\n            compte = compte + 1\n    return compte\n",
            "def compta_majors(llista, llindar):\n    for x in llista:\n        compte = 0\n        if x > llindar:\n            compte = compte + 1\n    return compte\n",
            "def compta_majors(llista, llindar):\n    compte = 0\n    for x in llista:\n        if x > llindar:\n            compte = compte + 1\n        return compte\n",
        ],
    }


@plantilla('t1_acum_maxim', 't1_acumuladors', 'escriure')
def _(rng):
    casos = []
    for _ in range(3):
        casos.append('maxim(%s)' % numeros(rng, rng.randint(3, 8)))
    casos.append('maxim(%s)' % numeros(rng, 5, -20, -2))
    casos.append('maxim([%d])' % rng.randint(-5, 5))
    return {
        'enunciat': ("Escriu `maxim(llista)`: retorna l'element **més gran** d'una llista no buida, "
                     "**sense** fer servir `max()`: recorre-la i recorda el més gran que has vist.\n\n"
                     "Compte: la llista pot tenir tots els valors **negatius**."),
        'esquelet': "def maxim(llista):\n    pass\n",
        'referencia': ("def maxim(llista):\n    millor = llista[0]\n    for x in llista:\n"
                       "        if x > millor:\n            millor = x\n    return millor\n"),
        'funcio': 'maxim',
        'casos': casos,
        'requereix': ['For', 'While'],
        'prohibeix': ['max', 'sorted'],
        'mutants': [
            "def maxim(llista):\n    millor = 0\n    for x in llista:\n        if x > millor:\n            millor = x\n    return millor\n",
            "def maxim(llista):\n    millor = llista[0]\n    for x in llista:\n        if x > millor:\n            millor = x\n        return millor\n",
            "def maxim(llista):\n    millor = llista[0]\n    for x in llista:\n        if x < millor:\n            millor = x\n    return millor\n",
        ],
    }


@plantilla('t1_acum_primer', 't1_acumuladors', 'escriure')
def _(rng):
    casos = []
    for _ in range(3):
        l = notes_aleatories(rng, rng.randint(4, 8), 60, 67)
        casos.append('primera_posicio(%s, %d)' % (l, rng.choice(l)))
    casos.append('primera_posicio([60, 64, 60, 64], 64)')
    casos.append('primera_posicio([60, 62], 71)')
    return {
        'enunciat': ("Escriu `primera_posicio(llista, valor)`: retorna la **posició** (índex) de la **primera** "
                     "aparició de `valor`, o **-1** si no hi és. Amb un bucle (sense `.index()`).\n\n"
                     "Exemple: `primera_posicio([60, 64, 60, 64], 64)` → `1`."),
        'esquelet': "def primera_posicio(llista, valor):\n    pass\n",
        'referencia': ("def primera_posicio(llista, valor):\n    for i in range(len(llista)):\n"
                       "        if llista[i] == valor:\n            return i\n    return -1\n"),
        'funcio': 'primera_posicio',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def primera_posicio(llista, valor):\n    for i in range(len(llista)):\n        if llista[i] == valor:\n            return i\n        else:\n            return -1\n",
            "def primera_posicio(llista, valor):\n    pos = -1\n    for i in range(len(llista)):\n        if llista[i] == valor:\n            pos = i\n    return pos\n",
            "def primera_posicio(llista, valor):\n    for i in range(len(llista)):\n        if llista[i] == valor:\n            return llista[i]\n    return -1\n",
        ],
    }


@plantilla('t1_acum_ordenar_compta', 't1_acumuladors', 'ordenar')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('compta_dins(%s, %d, %d)' % (notes_aleatories(rng, rng.randint(4, 9), 48, 84), 55, 72))
    casos.append('compta_dins([], 60, 72)')
    return {
        'enunciat': ("Ordena les línies perquè `compta_dins(notes, baix, alt)` retorni quantes notes són "
                     "**dins el registre** `[baix, alt]` (tots dos inclosos). La indentació ja hi és."),
        'referencia': ("def compta_dins(notes, baix, alt):\n    compte = 0\n    for nota in notes:\n"
                       "        if nota >= baix and nota <= alt:\n            compte = compte + 1\n"
                       "    return compte\n"),
        'funcio': 'compta_dins',
        'casos': casos,
    }


# ==========================================================================
concepte('t1_condicionals', 'tp1', "Condicionals",
         "if / elif / else (només s'executa UNA branca), and / or, comparacions")
# ==========================================================================

@plantilla('t1_cond_dinamica', 't1_condicionals', 'predir')
def _(rng):
    l1 = rng.choice([40, 50])
    l2 = rng.choice([80, 90, 100])
    vals = numeros(rng, 3, 10, 127)
    vals[rng.randint(0, 2)] = rng.choice([l1, l2])
    codi = (
        "for vel in %s:\n"
        "    if vel < %d:\n"
        "        print('pp')\n"
        "    elif vel < %d:\n"
        "        print('mf')\n"
        "    else:\n"
        "        print('ff')\n" % (vals, l1, l2))
    return {'enunciat': "Què imprimeix? (Compte amb els valors que cauen just a la frontera.)", 'codi': codi}


@plantilla('t1_cond_maquina', 't1_condicionals', 'predir')
def _(rng):
    a = rng.choice([4, 5, 6])
    b = rng.choice([8, 9, 10])
    s1 = rng.choice([2, 3])
    n = rng.randint(6, 8)
    codi = (
        "nivell = 0\n"
        "for k in range(%d):\n"
        "    if nivell < %d:\n"
        "        nivell = nivell + %d\n"
        "    elif nivell < %d:\n"
        "        nivell = nivell + 1\n"
        "    else:\n"
        "        nivell = 0\n"
        "    print(k, nivell)\n" % (n, a, s1, b))
    return {'enunciat': "Què imprimeix? A cada volta només s'executa **una** de les branques.", 'codi': codi}


@plantilla('t1_cond_andor', 't1_condicionals', 'predir')
def _(rng):
    nota = rng.randint(50, 80)
    vel = rng.randint(0, 127)
    baix = rng.choice([55, 60])
    alt = rng.choice([72, 76])
    codi = (
        "nota = %d\n"
        "vel = %d\n"
        "print(nota >= %d and nota <= %d)\n"
        "print(vel == 0 or nota > %d)\n"
        "print(not (vel > 64))\n" % (nota, vel, baix, alt, alt))
    return {'enunciat': "Què imprimeix? (`True` o `False` a cada línia.)", 'codi': codi}


@plantilla('t1_cond_escriure', 't1_condicionals', 'escriure')
def _(rng):
    l1 = rng.choice([40, 48])
    l2 = rng.choice([88, 96])
    casos = []
    for v in [0, l1 - 1, l1, l2 - 1, l2, 127, rng.randint(1, 127)]:
        casos.append('dinamica(%d)' % v)
    return {
        'enunciat': ("Escriu `dinamica(vel)`: retorna `'pp'` si `vel` és **menor que %d**, `'mf'` si és "
                     "**menor que %d** (i no pp), i `'ff'` en la resta de casos." % (l1, l2)),
        'esquelet': "def dinamica(vel):\n    pass\n",
        'referencia': ("def dinamica(vel):\n    if vel < %d:\n        return 'pp'\n    elif vel < %d:\n"
                       "        return 'mf'\n    else:\n        return 'ff'\n" % (l1, l2)),
        'funcio': 'dinamica',
        'casos': casos,
        'mutants': [
            "def dinamica(vel):\n    if vel < %d:\n        return 'mf'\n    elif vel < %d:\n        return 'pp'\n    else:\n        return 'ff'\n" % (l2, l1),
            "def dinamica(vel):\n    if vel <= %d:\n        return 'pp'\n    elif vel <= %d:\n        return 'mf'\n    else:\n        return 'ff'\n" % (l1, l2),
            "def dinamica(vel):\n    if vel < %d:\n        print('pp')\n    elif vel < %d:\n        print('mf')\n    else:\n        print('ff')\n" % (l1, l2),
        ],
    }


# ==========================================================================
concepte('t1_funcions', 'tp1', "Funcions",
         "return vs print, paràmetres amb valor per defecte, retornar diversos valors")
# ==========================================================================

@plantilla('t1_func_return_print', 't1_funcions', 'predir')
def _(rng):
    x = rng.randint(2, 9)
    k = rng.randint(2, 5)
    codi = (
        "def doble_print(x):\n"
        "    print(x * 2)\n"
        "\n"
        "def multiplica(x):\n"
        "    return x * %d\n"
        "\n"
        "a = doble_print(%d)\n"
        "b = multiplica(%d)\n"
        "print(a, b)\n" % (k, x, x))
    return {'enunciat': "Què imprimeix? Pensa què retorna una funció que **no** té `return`.", 'codi': codi}


@plantilla('t1_func_defecte', 't1_funcions', 'predir')
def _(rng):
    d = rng.choice([12, 7, 5])
    n1 = rng.randint(55, 70)
    i2 = rng.choice([-12, 2, 4, -5])
    codi = (
        "def transposa(nota, interval=%d):\n"
        "    return nota + interval\n"
        "\n"
        "print(transposa(%d))\n"
        "print(transposa(%d, %d))\n"
        "print(transposa(transposa(%d), %d))\n" % (d, n1, n1, i2, n1, i2))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_func_tupla', 't1_funcions', 'predir')
def _(rng):
    l = notes_aleatories(rng, rng.randint(4, 6))
    codi = (
        "def registre(notes):\n"
        "    return min(notes), max(notes)\n"
        "\n"
        "greu, aguda = registre(%s)\n"
        "print(aguda - greu)\n"
        "print(registre([%d, %d]))\n" % (l, l[0], l[1]))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_func_escriure', 't1_funcions', 'escriure')
def _(rng):
    casos = []
    for _ in range(3):
        casos.append('transposa_tot(%s)' % notes_aleatories(rng, rng.randint(2, 6)))
    for _ in range(2):
        casos.append('transposa_tot(%s, %d)' % (notes_aleatories(rng, rng.randint(2, 6)), rng.choice([-12, 2, 7, -5])))
    return {
        'enunciat': ("Escriu `transposa_tot(notes, interval=12)`: retorna una **llista nova** amb totes les "
                     "notes transposades `interval` semitons. Si no es dona `interval`, ha de ser **12** "
                     "(una octava amunt). No modifiquis la llista original."),
        'esquelet': "def transposa_tot(notes, interval=12):\n    pass\n",
        'referencia': ("def transposa_tot(notes, interval=12):\n    resultat = []\n    for nota in notes:\n"
                       "        resultat.append(nota + interval)\n    return resultat\n"),
        'funcio': 'transposa_tot',
        'casos': casos,
        'mutants': [
            "def transposa_tot(notes, interval):\n    resultat = []\n    for nota in notes:\n        resultat.append(nota + interval)\n    return resultat\n",
            "def transposa_tot(notes, interval=12):\n    resultat = []\n    for nota in notes:\n        resultat.append(nota + 12)\n    return resultat\n",
            "def transposa_tot(notes, interval=12):\n    for nota in notes:\n        nota = nota + interval\n    return notes\n",
        ],
    }


# ==========================================================================
concepte('t1_llistes', 'tp1', "Construir llistes",
         "append, llistes noves vs modificar, concatenació (+), repetició (*)")
# ==========================================================================

@plantilla('t1_llistes_append_concat', 't1_llistes', 'predir')
def _(rng):
    a = notes_aleatories(rng, rng.randint(2, 3))
    x = rng.randint(60, 72)
    y = rng.randint(60, 72)
    codi = (
        "a = %s\n"
        "b = a + [%d]\n"
        "a.append(%d)\n"
        "print(len(a), len(b))\n"
        "print(b[-1], a[-1])\n" % (a, x, y))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_llistes_repeticio', 't1_llistes', 'predir')
def _(rng):
    patro = []
    for _ in range(rng.randint(2, 3)):
        patro.append(rng.choice([0, 1]))
    patro[0] = 1
    n = rng.randint(2, 4)
    codi = (
        "ritme = %s * %d\n"
        "print(ritme)\n"
        "print(len(ritme), ritme[-1])\n" % (patro, n))
    return {'enunciat': "Què imprimeix? (`llista * n` repeteix la llista `n` vegades.)", 'codi': codi}


@plantilla('t1_llistes_filtra', 't1_llistes', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('filtra(%s, %d)' % (numeros(rng, rng.randint(3, 8), 0, 127), rng.choice([20, 50, 64])))
    casos.append('filtra([], 10)')
    casos.append('filtra([64, 30, 64, 100], 64)')
    return {
        'enunciat': ("Escriu `filtra(velocities, minim)`: retorna una **llista nova** només amb les velocities "
                     "que són **com a mínim** `minim` (en el mateix ordre)."),
        'esquelet': "def filtra(velocities, minim):\n    pass\n",
        'referencia': ("def filtra(velocities, minim):\n    resultat = []\n    for v in velocities:\n"
                       "        if v >= minim:\n            resultat.append(v)\n    return resultat\n"),
        'funcio': 'filtra',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def filtra(velocities, minim):\n    resultat = []\n    for v in velocities:\n        if v > minim:\n            resultat.append(v)\n    return resultat\n",
            "def filtra(velocities, minim):\n    resultat = []\n    for v in velocities:\n        if v >= minim:\n            resultat = [v]\n    return resultat\n",
            "def filtra(velocities, minim):\n    resultat = []\n    for v in velocities:\n        if v >= minim:\n            resultat.append(v)\n        return resultat\n",
        ],
    }


@plantilla('t1_llistes_ordenar', 't1_llistes', 'ordenar')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('intervals(%s)' % notes_aleatories(rng, rng.randint(2, 7)))
    return {
        'enunciat': ("Ordena les línies perquè `intervals(notes)` retorni la llista dels **intervals** entre "
                     "notes consecutives (cada nota menys l'anterior). Exemple: `[60, 64, 62]` → `[4, -2]`."),
        'referencia': ("def intervals(notes):\n    resultat = []\n    for i in range(1, len(notes)):\n"
                       "        salt = notes[i] - notes[i - 1]\n        resultat.append(salt)\n    return resultat\n"),
        'funcio': 'intervals',
        'casos': casos,
    }


# ==========================================================================
concepte('t1_tuples', 'tp1', "Tuples i desempaquetar",
         "Llistes de tuples (nota, durada), for a, b in ..., retornar i rebre tuples")
# ==========================================================================

@plantilla('t1_tuples_recorre', 't1_tuples', 'predir')
def _(rng):
    notes = []
    for _ in range(rng.randint(3, 4)):
        notes.append((rng.randint(60, 72), rng.choice([1, 2, 4])))
    codi = (
        "frase = %s     # (nota, durada en semicorxeres)\n"
        "total = 0\n"
        "for nota, durada in frase:\n"
        "    total = total + durada\n"
        "    print(nota, total)\n" % notes)
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t1_tuples_escriure', 't1_tuples', 'escriure')
def _(rng):
    casos = []
    for _ in range(5):
        fr = []
        for _ in range(rng.randint(1, 5)):
            fr.append((rng.randint(55, 80), rng.choice([1, 2, 3, 4, 8])))
        casos.append('nota_mes_llarga(%s)' % fr)
    casos.append('nota_mes_llarga([(60, 2), (64, 4), (67, 4)])')
    return {
        'enunciat': ("Escriu `nota_mes_llarga(frase)`: `frase` és una llista de tuples `(nota, durada)`. "
                     "Retorna la **nota** (no la durada) que dura més. Si n'hi ha diverses d'empatades, "
                     "la **primera**."),
        'esquelet': "def nota_mes_llarga(frase):\n    pass\n",
        'referencia': ("def nota_mes_llarga(frase):\n    millor_nota, millor_durada = frase[0]\n"
                       "    for nota, durada in frase:\n        if durada > millor_durada:\n"
                       "            millor_nota = nota\n            millor_durada = durada\n    return millor_nota\n"),
        'funcio': 'nota_mes_llarga',
        'casos': casos,
        'mutants': [
            "def nota_mes_llarga(frase):\n    millor_nota, millor_durada = frase[0]\n    for nota, durada in frase:\n        if durada >= millor_durada:\n            millor_nota = nota\n            millor_durada = durada\n    return millor_nota\n",
            "def nota_mes_llarga(frase):\n    millor_nota, millor_durada = frase[0]\n    for nota, durada in frase:\n        if durada > millor_durada:\n            millor_nota = nota\n            millor_durada = durada\n    return millor_durada\n",
            "def nota_mes_llarga(frase):\n    millor_nota, millor_durada = frase[0]\n    for nota, durada in frase:\n        if nota > millor_nota:\n            millor_nota = nota\n            millor_durada = durada\n    return millor_nota\n",
        ],
    }
