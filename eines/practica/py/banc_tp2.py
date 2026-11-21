"""
Banc TP2 — la mateixa mecànica, dins els conceptes del curs: arrays i mostres,
blocs i callbacks, buffers circulars (delay), estat dins objectes.
"""
from motor import concepte, plantilla
from banc_tp1 import numeros

PREAMBUL_NP = "import numpy as np\n"


def mostres(rng, n, decimals=1):
    llista = []
    for _ in range(n):
        llista.append(round(rng.uniform(-1, 1), decimals))
    return llista


# ==========================================================================
concepte('t2_numpy', 'tp2', "Arrays NumPy",
         "np.zeros / np.ones / np.arange / np.linspace, llegir i assignar talls, len, np.max")
# ==========================================================================

@plantilla('t2_np_assignar', 't2_numpy', 'predir', numpy=True)
def _(rng):
    n = rng.randint(6, 9)
    a = rng.randint(1, 3)
    b = rng.randint(a + 2, n - 1)
    v = rng.choice([1, 2, 5])
    w = rng.choice([3, 4, 9])
    codi = (
        "import numpy as np\n"
        "so = np.zeros(%d)\n"
        "so[%d:%d] = %d\n"
        "so[-1] = %d\n"
        "print(so)\n"
        "print(np.max(so), len(so), so[%d])\n" % (n, a, b, v, w, b))
    return {'enunciat': "Què imprimeix? (NumPy escriu els decimals així: `[0. 1. 0.]`.)", 'codi': codi}


@plantilla('t2_np_crear', 't2_numpy', 'predir', numpy=True)
def _(rng):
    inici = rng.randint(0, 3)
    pas = rng.choice([2, 3])
    fi = inici + pas * rng.randint(3, 5)
    k = rng.choice([3, 5])
    codi = (
        "import numpy as np\n"
        "a = np.arange(%d, %d, %d)\n"
        "print(a, len(a))\n"
        "b = np.linspace(0, 1, %d)\n"
        "print(len(b), b[0], b[-1], b[1])\n"
        "c = np.ones(4) * %d\n"
        "print(c[2])\n" % (inici, fi, pas, k, rng.randint(2, 7)))
    return {'enunciat': "Què imprimeix? Recorda: `arange` **no** inclou el final; `linspace` **sí**.", 'codi': codi}


@plantilla('t2_np_silenci', 't2_numpy', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        n = rng.randint(6, 12)
        a = rng.randint(0, n - 3)
        b = rng.randint(a + 1, n)
        casos.append('silencia(np.array(%s), %d, %d)' % (mostres(rng, n), a, b))
    casos.append('__no_modifica()')
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `silencia(so, inici, fi)`: retorna una **còpia** de `so` on les mostres des de "
                     "`inici` fins a `fi` (**sense incloure** `fi`) valen 0. No modifiquis `so`: fes-ne una "
                     "còpia amb `so.copy()`."),
        'esquelet': "def silencia(so, inici, fi):\n    pass\n",
        'referencia': "def silencia(so, inici, fi):\n    resultat = so.copy()\n    resultat[inici:fi] = 0\n    return resultat\n",
        'funcio': 'silencia',
        'casos': casos,
        'ajudants': ("def __no_modifica():\n    x = np.array([0.5, 0.5, 0.5, 0.5])\n    silencia(x, 1, 3)\n"
                     "    return x\n"),
        'mutants': [
            "def silencia(so, inici, fi):\n    resultat = so.copy()\n    resultat[inici:fi + 1] = 0\n    return resultat\n",
            "def silencia(so, inici, fi):\n    resultat = so.copy()\n    resultat[inici + 1:fi] = 0\n    return resultat\n",
            "def silencia(so, inici, fi):\n    so[inici:fi] = 0\n    return so\n",
        ],
    }


# ==========================================================================
concepte('t2_vector', 'tp2', "Operar arrays sencers",
         "Operacions sense bucle: so * 0.5, a + b, np.abs, np.max, np.clip, np.linspace per a rampes")
# ==========================================================================

@plantilla('t2_vec_operacions', 't2_vector', 'predir', numpy=True)
def _(rng):
    a = mostres(rng, 4)
    g = rng.choice([2, 3, 0.5])
    o = rng.choice([1, -1])
    codi = (
        "import numpy as np\n"
        "so = np.array(%s)\n"
        "b = so * %s + %d\n"
        "print(round(b[0], 2), round(b[-1], 2))\n"
        "print(np.max(so), np.max(np.abs(so)))\n" % (a, g, o))
    return {'enunciat': "Què imprimeix? (Cada operació s'aplica a **totes** les mostres.)", 'codi': codi}


@plantilla('t2_vec_normalitza', 't2_vector', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(3):
        casos.append('normalitza(np.array(%s))' % mostres(rng, rng.randint(4, 8), 2))
    casos.append('normalitza(np.array([0.1, -0.8, 0.4]))')
    casos.append('normalitza(np.array(%s), %s)' % (mostres(rng, 5, 2), rng.choice([0.5, 0.9])))
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `normalitza(so, pic=1.0)`: retorna el so escalat perquè la mostra amb el valor "
                     "**absolut** més gran valgui exactament `pic` (en valor absolut). Sense bucles.\n\n"
                     "Compte: el pic pot ser **negatiu** (p. ex. `[0.1, -0.8, 0.4]`)."),
        'esquelet': "def normalitza(so, pic=1.0):\n    pass\n",
        'referencia': "def normalitza(so, pic=1.0):\n    return so / np.max(np.abs(so)) * pic\n",
        'funcio': 'normalitza',
        'casos': casos,
        'mutants': [
            "def normalitza(so, pic=1.0):\n    return so / np.max(so) * pic\n",
            "def normalitza(so, pic=1.0):\n    return so / np.max(np.abs(so))\n",
            "def normalitza(so, pic=1.0):\n    return np.abs(so) / np.max(np.abs(so)) * pic\n",
        ],
    }


@plantilla('t2_vec_fade', 't2_vector', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        n = rng.randint(6, 12)
        casos.append('fade_in(np.ones(%d), %d)' % (n, rng.randint(2, n)))
    casos.append('fade_in(np.array(%s), 3)' % mostres(rng, 6))
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `fade_in(so, n)`: retorna una còpia del so on les **`n` primeres mostres** es "
                     "multipliquen per una rampa que puja de 0 a 1 (`np.linspace(0, 1, n)`). La resta queda igual."),
        'esquelet': "def fade_in(so, n):\n    pass\n",
        'referencia': ("def fade_in(so, n):\n    resultat = so.copy()\n"
                       "    resultat[:n] = resultat[:n] * np.linspace(0, 1, n)\n    return resultat\n"),
        'funcio': 'fade_in',
        'casos': casos,
        'mutants': [
            "def fade_in(so, n):\n    return so * np.linspace(0, 1, len(so))\n",
            "def fade_in(so, n):\n    resultat = so.copy()\n    resultat[:n] = np.linspace(0, 1, n)\n    return resultat\n",
            "def fade_in(so, n):\n    resultat = so.copy()\n    resultat[1:n + 1] = resultat[1:n + 1] * np.linspace(0, 1, n)\n    return resultat\n",
        ],
    }


# ==========================================================================
concepte('t2_mostres', 'tp2', "Mostres, segons i notes",
         "segons ↔ mostres (int), en quin bloc cau una mostra (// i %), nota MIDI → Hz (**)")
# ==========================================================================

@plantilla('t2_mostres_conversio', 't2_mostres', 'predir')
def _(rng):
    sr = rng.choice([44100, 48000])
    t = rng.choice([0.25, 0.5, 0.1, 1.5, 0.02])
    b = rng.choice([256, 512, 1024])
    codi = (
        "sample_rate = %d\n"
        "blocksize = %d\n"
        "n = int(%s * sample_rate)\n"
        "print(n)\n"
        "print(n // blocksize, n %% blocksize)\n" % (sr, b, t))
    return {'enunciat': "Què imprimeix? (Quantes mostres són, i en quin bloc i posició cau l'última.)", 'codi': codi}


@plantilla('t2_mostres_bloc', 't2_mostres', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('on_cau(%s, %d)' % (round(rng.uniform(0, 3), 3), rng.choice([256, 512, 1024])))
    casos.append('on_cau(0.0, 512)')
    return {
        'enunciat': ("Escriu `on_cau(segons, blocksize, sample_rate=44100)`: retorna **en quin bloc** (comptant "
                     "des de 0) i **en quina posició dins el bloc** cau l'instant `segons`. Converteix primer a "
                     "mostres amb `int()`.\n\nExemple: `on_cau(0.1, 512)` → 4410 mostres → `(8, 314)`."),
        'esquelet': "def on_cau(segons, blocksize, sample_rate=44100):\n    pass\n",
        'referencia': ("def on_cau(segons, blocksize, sample_rate=44100):\n    n = int(segons * sample_rate)\n"
                       "    return n // blocksize, n % blocksize\n"),
        'funcio': 'on_cau',
        'casos': casos,
        'mutants': [
            "def on_cau(segons, blocksize, sample_rate=44100):\n    n = int(segons * sample_rate)\n    return n / blocksize, n % blocksize\n",
            "def on_cau(segons, blocksize, sample_rate=44100):\n    return segons // blocksize, segons % blocksize\n",
            "def on_cau(segons, blocksize, sample_rate=44100):\n    n = int(segons * sample_rate)\n    return n % blocksize, n // blocksize\n",
        ],
    }


@plantilla('t2_mostres_midi', 't2_mostres', 'escriure')
def _(rng):
    casos = ['midi_a_freq(69)', 'midi_a_freq(81)', 'midi_a_freq(60)']
    for _ in range(3):
        casos.append('midi_a_freq(%d)' % rng.randint(21, 108))
    return {
        'enunciat': ("Escriu `midi_a_freq(nota)`: retorna la freqüència en Hz. El La 440 és la nota 69, i cada "
                     "semitò multiplica per `2 ** (1/12)`: és a dir, `440 * 2 ** ((nota - 69) / 12)`.\n\n"
                     "Pensa bé on calen **parèntesis**."),
        'esquelet': "def midi_a_freq(nota):\n    pass\n",
        'referencia': "def midi_a_freq(nota):\n    return 440 * 2 ** ((nota - 69) / 12)\n",
        'funcio': 'midi_a_freq',
        'casos': casos,
        'mutants': [
            "def midi_a_freq(nota):\n    return 440 * 2 ** (nota - 69 / 12)\n",
            "def midi_a_freq(nota):\n    return 440 * 2 ** ((nota - 60) / 12)\n",
            "def midi_a_freq(nota):\n    return 440 * 2 ** (nota - 69) / 12\n",
        ],
    }


# ==========================================================================
concepte('t2_bucle_mostres', 'tp2', "Recórrer un so mostra a mostra",
         "for i in range(len(so)), llegir so[i] i escriure sortida[i], comptadors i condicions")
# ==========================================================================

@plantilla('t2_bm_traca', 't2_bucle_mostres', 'predir', numpy=True)
def _(rng):
    a = mostres(rng, rng.randint(5, 6))
    lim = rng.choice([0.3, 0.5])
    codi = (
        "import numpy as np\n"
        "so = np.array(%s)\n"
        "sortida = np.zeros(len(so))\n"
        "for i in range(len(so)):\n"
        "    if so[i] > %s:\n"
        "        sortida[i] = %s\n"
        "    elif so[i] < -%s:\n"
        "        sortida[i] = -%s\n"
        "    else:\n"
        "        sortida[i] = so[i]\n"
        "print(sortida)\n" % (a, lim, lim, lim, lim))
    return {'enunciat': "Què imprimeix? (És un *hard clipping*: retalla el que passa del límit.)", 'codi': codi}


@plantilla('t2_bm_compta_pics', 't2_bucle_mostres', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('compta_pics(np.array(%s), %s)' % (mostres(rng, rng.randint(4, 10)), rng.choice([0.3, 0.5, 0.8])))
    casos.append('compta_pics(np.array([0.5, -0.5, 0.2]), 0.5)')
    casos.append('compta_pics(np.array([-0.9, -0.95, 0.1]), 0.8)')
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `compta_pics(so, llindar)`: retorna **quantes mostres** tenen un valor absolut "
                     "**més gran** que `llindar`. Amb un bucle que recorri el so."),
        'esquelet': "def compta_pics(so, llindar):\n    pass\n",
        'referencia': ("def compta_pics(so, llindar):\n    compte = 0\n    for i in range(len(so)):\n"
                       "        if abs(so[i]) > llindar:\n            compte = compte + 1\n    return compte\n"),
        'funcio': 'compta_pics',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def compta_pics(so, llindar):\n    compte = 0\n    for i in range(len(so)):\n        if so[i] > llindar:\n            compte = compte + 1\n    return compte\n",
            "def compta_pics(so, llindar):\n    compte = 0\n    for i in range(len(so)):\n        if abs(so[i]) >= llindar:\n            compte = compte + 1\n    return compte\n",
            "def compta_pics(so, llindar):\n    compte = 0\n    for i in range(so):\n        if abs(so[i]) > llindar:\n            compte = compte + 1\n    return compte\n",
        ],
    }


@plantilla('t2_bm_onset', 't2_bucle_mostres', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('primer_onset(np.array(%s), %s)' % (mostres(rng, rng.randint(5, 10)), rng.choice([0.5, 0.7])))
    casos.append('primer_onset(np.array([0.1, -0.2, 0.1]), 0.5)')
    casos.append('primer_onset(np.array([0.1, -0.9, 0.9]), 0.5)')
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `primer_onset(so, llindar)`: retorna l'**índex** de la **primera** mostra el valor "
                     "absolut de la qual supera `llindar` (on comença un cop), o **-1** si no n'hi ha cap."),
        'esquelet': "def primer_onset(so, llindar):\n    pass\n",
        'referencia': ("def primer_onset(so, llindar):\n    for i in range(len(so)):\n"
                       "        if abs(so[i]) > llindar:\n            return i\n    return -1\n"),
        'funcio': 'primer_onset',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def primer_onset(so, llindar):\n    for i in range(len(so)):\n        if so[i] > llindar:\n            return i\n    return -1\n",
            "def primer_onset(so, llindar):\n    pos = -1\n    for i in range(len(so)):\n        if abs(so[i]) > llindar:\n            pos = i\n    return pos\n",
            "def primer_onset(so, llindar):\n    for i in range(len(so)):\n        if abs(so[i]) > llindar:\n            return so[i]\n    return -1\n",
        ],
    }


@plantilla('t2_bm_clip', 't2_bucle_mostres', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('retalla(np.array(%s), %s)' % (mostres(rng, rng.randint(4, 9)), rng.choice([0.3, 0.5])))
    casos.append('retalla(np.array([0.9, -0.9, 0.2]), 0.5)')
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `retalla(so, limit)` **amb un bucle mostra a mostra** (sense `np.clip`): retorna un "
                     "array nou on cada mostra més gran que `limit` val `limit`, cada mostra més petita que "
                     "`-limit` val `-limit`, i la resta no canvia."),
        'esquelet': "def retalla(so, limit):\n    pass\n",
        'referencia': ("def retalla(so, limit):\n    sortida = np.zeros(len(so))\n    for i in range(len(so)):\n"
                       "        if so[i] > limit:\n            sortida[i] = limit\n"
                       "        elif so[i] < -limit:\n            sortida[i] = -limit\n"
                       "        else:\n            sortida[i] = so[i]\n    return sortida\n"),
        'funcio': 'retalla',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def retalla(so, limit):\n    sortida = np.zeros(len(so))\n    for i in range(len(so)):\n        if so[i] > limit:\n            sortida[i] = limit\n        else:\n            sortida[i] = so[i]\n    return sortida\n",
            "def retalla(so, limit):\n    sortida = np.zeros(len(so))\n    for i in range(len(so)):\n        if so[i] > limit:\n            sortida[i] = limit\n        elif so[i] < -limit:\n            sortida[i] = -limit\n    return sortida\n",
            "def retalla(so, limit):\n    sortida = np.zeros(len(so))\n    for i in range(len(so)):\n        if abs(so[i]) > limit:\n            sortida[i] = limit\n        else:\n            sortida[i] = so[i]\n    return sortida\n",
        ],
    }


@plantilla('t2_bm_ordenar_rms', 't2_bucle_mostres', 'ordenar', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('energia(np.array(%s))' % mostres(rng, rng.randint(3, 8), 2))
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Ordena les línies perquè `energia(so)` retorni la **mitjana dels quadrats** de les mostres "
                     "(suma de `mostra * mostra`, dividida pel nombre de mostres)."),
        'referencia': ("def energia(so):\n    suma = 0.0\n    for i in range(len(so)):\n"
                       "        suma = suma + so[i] * so[i]\n    return suma / len(so)\n"),
        'funcio': 'energia',
        'casos': casos,
    }


# ==========================================================================
concepte('t2_blocs', 'tp2', "Processar per blocs",
         "Trossejar un so en blocs (com el callback): range(0, len, B), so[i:i+B], l'últim bloc incomplet")
# ==========================================================================

@plantilla('t2_blocs_traca', 't2_blocs', 'predir', numpy=True)
def _(rng):
    b = rng.choice([3, 4, 5])
    n = b * rng.randint(2, 3) + rng.randint(1, b - 1)
    codi = (
        "import numpy as np\n"
        "so = np.arange(%d)\n"
        "blocksize = %d\n"
        "for i in range(0, len(so), blocksize):\n"
        "    bloc = so[i:i + blocksize]\n"
        "    print(i, len(bloc), bloc[-1])\n" % (n, b))
    return {'enunciat': "Què imprimeix? (Fixa't en l'**últim** bloc.)", 'codi': codi}


@plantilla('t2_blocs_comptes', 't2_blocs', 'predir')
def _(rng):
    sr = rng.choice([44100, 48000])
    b = rng.choice([128, 256, 512, 1024])
    t = rng.choice([1, 2, 0.5, 0.25, 1.5, 3, 0.1])
    codi = (
        "sample_rate = %d\n"
        "blocksize = %d\n"
        "durada = %s     # segons\n"
        "n_mostres = int(durada * sample_rate)\n"
        "print(n_mostres // blocksize, n_mostres %% blocksize)\n"
        "print(round(blocksize / sample_rate * 1000, 1))     # ms per bloc\n" % (sr, b, t))
    return {'enunciat': "Què imprimeix? (Blocs complets, mostres que sobren, i quants mil·lisegons dura un bloc.)",
            'codi': codi}


@plantilla('t2_blocs_maxims', 't2_blocs', 'escriure', numpy=True)
def _(rng):
    casos = []
    for _ in range(4):
        b = rng.randint(2, 4)
        casos.append('pic_per_bloc(np.array(%s), %d)' % (mostres(rng, b * rng.randint(2, 3) + rng.randint(0, b - 1)), b))
    casos.append('pic_per_bloc(np.array([0.1, -0.9, 0.3, 0.2, 0.5]), 2)')
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu `pic_per_bloc(so, blocksize)`: trosseja el so en blocs de `blocksize` mostres i "
                     "retorna una **llista** amb el pic (màxim del **valor absolut**) de cada bloc. L'últim bloc "
                     "pot ser més curt i també compta.\n\n"
                     "Exemple: `pic_per_bloc(np.array([0.1, -0.9, 0.3, 0.2, 0.5]), 2)` → `[0.9, 0.3, 0.5]`."),
        'esquelet': "def pic_per_bloc(so, blocksize):\n    pass\n",
        'referencia': ("def pic_per_bloc(so, blocksize):\n    pics = []\n    for i in range(0, len(so), blocksize):\n"
                       "        bloc = so[i:i + blocksize]\n        pics.append(np.max(np.abs(bloc)))\n    return pics\n"),
        'funcio': 'pic_per_bloc',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def pic_per_bloc(so, blocksize):\n    pics = []\n    for i in range(len(so) // blocksize):\n        bloc = so[i * blocksize:(i + 1) * blocksize]\n        pics.append(np.max(np.abs(bloc)))\n    return pics\n",
            "def pic_per_bloc(so, blocksize):\n    pics = []\n    for i in range(0, len(so), blocksize):\n        bloc = so[i:i + blocksize]\n        pics.append(np.max(bloc))\n    return pics\n",
            "def pic_per_bloc(so, blocksize):\n    pics = []\n    for i in range(0, len(so), blocksize):\n        bloc = so[i:blocksize]\n        pics.append(np.max(np.abs(bloc)))\n    return pics\n",
        ],
    }


# ==========================================================================
concepte('t2_circular', 'tp2', "Buffers circulars (delay)",
         "Un punter que dona la volta amb %: escriure, avançar, llegir amb retard")
# ==========================================================================

@plantilla('t2_circ_escriure_traca', 't2_circular', 'predir')
def _(rng):
    n = rng.choice([3, 4, 5])
    entrades = numeros(rng, n + rng.randint(1, 3), 1, 9)
    codi = (
        "buffer = [0] * %d\n"
        "pos = 0\n"
        "for x in %s:\n"
        "    buffer[pos] = x\n"
        "    pos = (pos + 1) %% %d\n"
        "print(buffer)\n"
        "print(pos)\n" % (n, entrades, n))
    return {'enunciat': "Què imprimeix? (Quan el punter arriba al final, torna a 0 i **sobreescriu**.)", 'codi': codi}


@plantilla('t2_circ_lectura_traca', 't2_circular', 'predir')
def _(rng):
    n = rng.choice([5, 6, 8])
    buf = numeros(rng, n, 1, 9)
    pos = rng.randint(0, n - 1)
    r = rng.randint(1, n - 1)
    codi = (
        "buffer = %s\n"
        "pos_escriptura = %d\n"
        "retard = %d\n"
        "pos_lectura = (pos_escriptura - retard) %% len(buffer)\n"
        "print(pos_lectura, buffer[pos_lectura])\n" % (buf, pos, r))
    return {'enunciat': "Què imprimeix? (Llegir `retard` posicions **enrere**, donant la volta si cal.)", 'codi': codi}


@plantilla('t2_circ_avanca', 't2_circular', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        n = rng.randint(3, 8)
        casos.append('escriu(%s, %d, %d)' % ([0] * n, rng.randint(0, n - 1), rng.randint(1, 9)))
    casos.append('escriu([0, 0, 0], 2, 7)')
    casos.append('__comprova_buffer()')
    return {
        'enunciat': ("Escriu `escriu(buffer, pos, valor)`: guarda `valor` a la posició `pos` del buffer i "
                     "retorna la **nova posició**: la següent, tornant a 0 si s'acaba el buffer (amb `%`).\n\n"
                     "Exemple: amb un buffer de 3 posicions, `escriu(buffer, 2, 7)` hi guarda el 7 i retorna `0`."),
        'esquelet': "def escriu(buffer, pos, valor):\n    pass\n",
        'referencia': ("def escriu(buffer, pos, valor):\n    buffer[pos] = valor\n"
                       "    return (pos + 1) % len(buffer)\n"),
        'funcio': 'escriu',
        'casos': casos,
        'ajudants': ("def __comprova_buffer():\n    b = [0, 0, 0]\n    p = 0\n    for v in [4, 5, 6, 7]:\n"
                     "        p = escriu(b, p, v)\n    return b, p\n"),
        'mutants': [
            "def escriu(buffer, pos, valor):\n    buffer[pos] = valor\n    return pos + 1\n",
            "def escriu(buffer, pos, valor):\n    return (pos + 1) % len(buffer)\n",
            "def escriu(buffer, pos, valor):\n    buffer[pos] = valor\n    return (pos + 1) % (len(buffer) - 1)\n",
        ],
    }


@plantilla('t2_circ_delay', 't2_circular', 'escriure')
def _(rng):
    casos = []
    for _ in range(4):
        casos.append('eco(%s, %d)' % (numeros(rng, rng.randint(4, 9), 1, 9), rng.randint(1, 3)))
    casos.append('eco([1, 2, 3], 3)')
    return {
        'enunciat': ("Escriu `eco(entrada, retard)` amb un **buffer circular** de `retard` posicions (una llista "
                     "`[0] * retard`) i un punter `pos`. Per a cada mostra d'entrada: **primer** llegeix el que hi "
                     "ha al buffer a `pos` (és la mostra de fa `retard` passos) i afegeix-ho a la sortida; "
                     "**després** hi escriu la mostra nova i avança el punter amb `%`. Retorna la llista de sortida.\n\n"
                     "Exemple: `eco([1, 2, 3, 4, 5], 2)` → `[0, 0, 1, 2, 3]`."),
        'esquelet': "def eco(entrada, retard):\n    pass\n",
        'referencia': ("def eco(entrada, retard):\n    buffer = [0] * retard\n    pos = 0\n    sortida = []\n"
                       "    for x in entrada:\n        sortida.append(buffer[pos])\n        buffer[pos] = x\n"
                       "        pos = (pos + 1) % retard\n    return sortida\n"),
        'funcio': 'eco',
        'casos': casos,
        'requereix': ['For', 'While'],
        'mutants': [
            "def eco(entrada, retard):\n    buffer = [0] * retard\n    pos = 0\n    sortida = []\n    for x in entrada:\n        buffer[pos] = x\n        sortida.append(buffer[pos])\n        pos = (pos + 1) % retard\n    return sortida\n",
            "def eco(entrada, retard):\n    buffer = [0] * retard\n    pos = 0\n    sortida = []\n    for x in entrada:\n        sortida.append(buffer[pos])\n        buffer[pos] = x\n    return sortida\n",
            "def eco(entrada, retard):\n    sortida = []\n    for x in entrada:\n        buffer = [0] * retard\n        pos = 0\n        sortida.append(buffer[pos])\n        buffer[pos] = x\n        pos = (pos + 1) % retard\n    return sortida\n",
        ],
    }


# ==========================================================================
concepte('t2_objectes', 'tp2', "Objectes amb estat",
         "self.atribut vs variable local, cada instància té el seu estat, l'estat persisteix entre crides")
# ==========================================================================

@plantilla('t2_obj_dues_instancies', 't2_objectes', 'predir')
def _(rng):
    p1 = rng.randint(2, 4)
    p2 = rng.randint(3, 5)
    m = rng.choice([8, 10, 12])
    seq = []
    for _ in range(rng.randint(4, 5)):
        seq.append(rng.choice(['a', 'b']))
    linies = ''
    for x in seq:
        linies += "%s.avanca()\n" % x
    codi = (
        "class Fase:\n"
        "    def __init__(self, pas):\n"
        "        self.pas = pas\n"
        "        self._phase = 0\n"
        "\n"
        "    def avanca(self):\n"
        "        self._phase = (self._phase + self.pas) %% %d\n"
        "\n"
        "a = Fase(%d)\n"
        "b = Fase(%d)\n"
        "%s"
        "b.pas = 1\n"
        "b.avanca()\n"
        "print(a._phase, b._phase)\n" % (m, p1, p2, linies))
    return {'enunciat': "Què imprimeix? Cada objecte té el **seu** `_phase`.", 'codi': codi}


@plantilla('t2_obj_local_vs_self', 't2_objectes', 'predir')
def _(rng):
    g = rng.choice([0.5, 0.8, 2, 0.25, 3, 1.5])
    n = rng.randint(2, 5)
    codi = (
        "class Volum:\n"
        "    def __init__(self):\n"
        "        self.guany = 1\n"
        "        self.crides = 0\n"
        "\n"
        "    def canvia(self, nou):\n"
        "        guany = nou                 # compte: sense self.\n"
        "        self.crides = self.crides + 1\n"
        "\n"
        "v = Volum()\n"
        "for i in range(%d):\n"
        "    v.canvia(%s)\n"
        "print(v.guany, v.crides)\n" % (n, g))
    return {'enunciat': "Què imprimeix?", 'codi': codi}


@plantilla('t2_obj_comptador', 't2_objectes', 'escriure')
def _(rng):
    m = rng.choice([4, 8, 16])
    return {
        'enunciat': ("Escriu la classe `Pas` (un pas de seqüenciador que dona la volta):\n\n"
                     "- `Pas(n_passos)` guarda `n_passos` i comença a la posició **0** (atribut `self.posicio`).\n"
                     "- `seguent()` retorna la posició **actual** i després l'avança una passa, tornant a 0 "
                     "quan arriba a `n_passos`.\n\n"
                     "Exemple: amb `p = Pas(3)`, cridar `p.seguent()` quatre cops retorna 0, 1, 2, 0."),
        'esquelet': "class Pas:\n    def __init__(self, n_passos):\n        pass\n\n    def seguent(self):\n        pass\n",
        'referencia': ("class Pas:\n    def __init__(self, n_passos):\n        self.n_passos = n_passos\n"
                       "        self.posicio = 0\n\n    def seguent(self):\n        actual = self.posicio\n"
                       "        self.posicio = (self.posicio + 1) % self.n_passos\n        return actual\n"),
        'funcio': 'Pas',
        'casos': ['__seq(3, 4)', '__seq(%d, %d)' % (m, m + rng.randint(1, 5)), '__dos()', '__seq(1, 3)',
                  '__seq(%d, %d)' % (rng.randint(2, 6), rng.randint(5, 12))],
        'ajudants': ("def __seq(n, k):\n    p = Pas(n)\n    r = []\n    for i in range(k):\n        r.append(p.seguent())\n"
                     "    return r\n\ndef __dos():\n    a = Pas(4)\n    b = Pas(4)\n    a.seguent()\n    a.seguent()\n"
                     "    return a.seguent(), b.seguent()\n"),
        'mutants': [
            "class Pas:\n    def __init__(self, n_passos):\n        self.n_passos = n_passos\n        self.posicio = 0\n\n    def seguent(self):\n        self.posicio = (self.posicio + 1) % self.n_passos\n        return self.posicio\n",
            "class Pas:\n    def __init__(self, n_passos):\n        self.n_passos = n_passos\n        self.posicio = 0\n\n    def seguent(self):\n        actual = self.posicio\n        self.posicio = self.posicio + 1\n        return actual\n",
            "class Pas:\n    def __init__(self, n_passos):\n        self.n_passos = n_passos\n\n    def seguent(self):\n        posicio = 0\n        actual = posicio\n        posicio = (posicio + 1) % self.n_passos\n        return actual\n",
        ],
    }


@plantilla('t2_obj_mitjana', 't2_objectes', 'escriure')
def _(rng):
    vals = numeros(rng, rng.randint(3, 6), 0, 127)
    return {
        'enunciat': ("Escriu la classe `Mesurador`, que va rebent valors d'un en un i en recorda la mitjana:\n\n"
                     "- `Mesurador()` comença sense cap valor.\n"
                     "- `afegeix(x)` registra un valor nou (no retorna res).\n"
                     "- `mitjana()` retorna la mitjana de tots els valors afegits fins ara, o **0** si encara no "
                     "n'hi ha cap.\n\n"
                     "Pista: no cal guardar tots els valors; n'hi ha prou amb dos atributs."),
        'esquelet': ("class Mesurador:\n    def __init__(self):\n        pass\n\n    def afegeix(self, x):\n"
                     "        pass\n\n    def mitjana(self):\n        pass\n"),
        'referencia': ("class Mesurador:\n    def __init__(self):\n        self.suma = 0\n        self.n = 0\n\n"
                       "    def afegeix(self, x):\n        self.suma = self.suma + x\n        self.n = self.n + 1\n\n"
                       "    def mitjana(self):\n        if self.n == 0:\n            return 0\n"
                       "        return self.suma / self.n\n"),
        'funcio': 'Mesurador',
        'casos': ['__prova(%s)' % vals, '__prova([])', '__prova([%d])' % rng.randint(1, 127), '__independents()'],
        'ajudants': ("def __prova(valors):\n    m = Mesurador()\n    for v in valors:\n        m.afegeix(v)\n"
                     "    return m.mitjana()\n\ndef __independents():\n    a = Mesurador()\n    b = Mesurador()\n"
                     "    a.afegeix(10)\n    b.afegeix(20)\n    b.afegeix(40)\n    return a.mitjana(), b.mitjana()\n"),
        'mutants': [
            ("class Mesurador:\n    def __init__(self):\n        self.suma = 0\n        self.n = 0\n\n"
             "    def afegeix(self, x):\n        self.suma = x\n        self.n = self.n + 1\n\n"
             "    def mitjana(self):\n        if self.n == 0:\n            return 0\n        return self.suma / self.n\n"),
            ("class Mesurador:\n    def __init__(self):\n        self.suma = 0\n        self.n = 0\n\n"
             "    def afegeix(self, x):\n        suma = self.suma + x\n        n = self.n + 1\n\n"
             "    def mitjana(self):\n        if self.n == 0:\n            return 0\n        return self.suma / self.n\n"),
            ("class Mesurador:\n    def __init__(self):\n        self.suma = 0\n        self.n = 0\n\n"
             "    def afegeix(self, x):\n        self.suma = self.suma + x\n        self.n = self.n + 1\n\n"
             "    def mitjana(self):\n        return self.suma / self.n\n"),
        ],
    }


@plantilla('t2_obj_ordenar_lfo', 't2_objectes', 'ordenar')
def _(rng):
    return {
        'enunciat': ("Ordena les línies de la classe `Rampa`: un oscil·lador en dent de serra que va de 0 a 1. "
                     "`Rampa(increment)` comença a 0; cada crida a `seguent()` retorna el valor actual i després "
                     "l'avança `increment`, tornant a començar quan passa d'1 (amb `% 1.0`)."),
        'referencia': ("class Rampa:\n    def __init__(self, increment):\n        self.increment = increment\n"
                       "        self.valor = 0.0\n    def seguent(self):\n        actual = self.valor\n"
                       "        self.valor = (self.valor + self.increment) % 1.0\n        return actual\n"),
        'funcio': 'Rampa',
        'casos': ['__seq(0.25, 6)', '__seq(%s, %d)' % (rng.choice([0.1, 0.2, 0.3, 0.4, 0.125, 0.375]), rng.randint(4, 9)),
                  '__seq(%s, 7)' % rng.choice([0.5, 0.75, 0.6])],
        'ajudants': ("def __seq(inc, k):\n    r = Rampa(inc)\n    out = []\n    for i in range(k):\n"
                     "        out.append(round(r.seguent(), 6))\n    return out\n"),
    }


# ==========================================================================
concepte('t2_callback', 'tp2', "Estat entre crides (callbacks)",
         "Una funció cridada bloc a bloc: què recorda d'una crida a la següent (global, self) i què no")
# ==========================================================================

@plantilla('t2_cb_global', 't2_callback', 'predir')
def _(rng):
    b = rng.choice([256, 300, 400])
    m = rng.choice([1000, 1024])
    n = rng.randint(3, 4)
    codi = (
        "mostra_actual = 0\n"
        "\n"
        "def callback(frames):\n"
        "    global mostra_actual\n"
        "    inici = mostra_actual\n"
        "    mostra_actual = (mostra_actual + frames) %% %d\n"
        "    return inici\n"
        "\n"
        "for i in range(%d):\n"
        "    print(callback(%d))\n"
        "print(mostra_actual)\n" % (m, n, b))
    return {'enunciat': "Què imprimeix? (Simulem un callback cridat bloc a bloc.)", 'codi': codi}


@plantilla('t2_cb_objecte', 't2_callback', 'predir', numpy=True)
def _(rng):
    inc = rng.choice([0.25, 0.5, 0.125])
    n = rng.choice([2, 3, 4])
    crides = rng.randint(2, 3)
    codi = (
        "import numpy as np\n"
        "\n"
        "class Rampa:\n"
        "    def __init__(self, increment):\n"
        "        self.increment = increment\n"
        "        self._phase = 0.0\n"
        "\n"
        "    def process(self, n):\n"
        "        bloc = (self._phase + self.increment * np.arange(n)) %% 1.0\n"
        "        self._phase = (self._phase + self.increment * n) %% 1.0\n"
        "        return bloc\n"
        "\n"
        "r = Rampa(%s)\n"
        "for i in range(%d):\n"
        "    bloc = r.process(%d)\n"
        "print(bloc)\n"
        "print(r._phase)\n" % (inc, crides, n))
    return {'enunciat': "Què imprimeix? (Només s'imprimeix l'**últim** bloc.)", 'codi': codi}


@plantilla('t2_cb_escriure', 't2_callback', 'escriure', numpy=True)
def _(rng):
    return {
        'preambul': PREAMBUL_NP,
        'enunciat': ("Escriu la classe `Metronom`, pensada per ser cridada des d'un callback:\n\n"
                     "- `Metronom(interval)`: farà un clic cada `interval` mostres. Comença a la mostra 0.\n"
                     "- `process(n)`: retorna un array de `n` mostres amb **1.0** a les mostres on toca clic "
                     "(la 0, la `interval`, la `2*interval`...) i 0 a la resta, **continuant** el compte de "
                     "mostres de la crida anterior.\n\n"
                     "Pista: guarda en un atribut quantes mostres portes generades; dins `process`, recorre les "
                     "`n` mostres del bloc i mira si la mostra absoluta és múltiple de `interval` (amb `%`)."),
        'esquelet': "class Metronom:\n    def __init__(self, interval):\n        pass\n\n    def process(self, n):\n        pass\n",
        'referencia': ("class Metronom:\n    def __init__(self, interval):\n        self.interval = interval\n"
                       "        self.mostra = 0\n\n    def process(self, n):\n        bloc = np.zeros(n)\n"
                       "        for i in range(n):\n            if (self.mostra + i) % self.interval == 0:\n"
                       "                bloc[i] = 1.0\n        self.mostra = self.mostra + n\n        return bloc\n"),
        'funcio': 'Metronom',
        'casos': ['__blocs(4, 3, 3)', '__blocs(%d, %d, 4)' % (rng.randint(3, 7), rng.randint(2, 5)), '__blocs(5, 8, 2)'],
        'ajudants': ("def __blocs(interval, n, k):\n    m = Metronom(interval)\n    trossos = []\n"
                     "    for i in range(k):\n        trossos.append(m.process(n))\n    return np.concatenate(trossos)\n"),
        'mutants': [
            ("class Metronom:\n    def __init__(self, interval):\n        self.interval = interval\n\n"
             "    def process(self, n):\n        bloc = np.zeros(n)\n        for i in range(n):\n"
             "            if i % self.interval == 0:\n                bloc[i] = 1.0\n        return bloc\n"),
            ("class Metronom:\n    def __init__(self, interval):\n        self.interval = interval\n        self.mostra = 0\n\n"
             "    def process(self, n):\n        bloc = np.zeros(n)\n        for i in range(n):\n"
             "            if (self.mostra + i) % self.interval == 0:\n                bloc[i] = 1.0\n"
             "        self.mostra = self.mostra + 1\n        return bloc\n"),
            ("class Metronom:\n    def __init__(self, interval):\n        self.interval = interval\n        self.mostra = 0\n\n"
             "    def process(self, n):\n        bloc = np.zeros(n)\n        for i in range(n):\n"
             "            if (self.mostra + i) % self.interval == 1:\n                bloc[i] = 1.0\n"
             "        self.mostra = self.mostra + n\n        return bloc\n"),
        ],
    }
