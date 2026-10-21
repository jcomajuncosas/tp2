"""
Assignment — Bloc 3c, Sessió 5
Mini-repte: efectes amb memòria (trèmolo, eco amb realimentació, ordre d'efectes)

⚠️  AURICULARS OBLIGATORIS. Micròfon + altaveus = realimentació (Larsen).

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom.

COM TREBALLAR-HI A THONNY:
  1. Completa un TODO.
  2. Prem F5 (Run). Això només DEFINEIX les funcions; no sona res.
  3. A la consola (Shell), crida la funció d'escolta d'aquella part:
         >>> escolta_part1()
     Cada escolta_partN() primer comprova la teva callback i, si és
     correcta, obre l'stream perquè la sentis.
  4. Passa al TODO següent. Pots tornar a cridar qualsevol part quan vulguis.

Parts:  1 trèmolo (memòria d'un número)
        2 eco amb realimentació (memòria d'una cinta)
        3 eco → distorsió (la fas tu sencera) i comparació amb distorsió → eco
        4 reflexió · CHALLENGE stutter

Tens recursos/exemples.py al costat: hi trobaràs el sinus amb fase i l'eco
d'una repetició. Fes-los servir de model, però entén cada línia.
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024


# ===============================================================
# PART 1 — Trèmolo
#
#   Un trèmolo puja i baixa el volum amb un oscil·lador lent (LFO).
#   És el mateix problema que el sinus de exemples.py: si l'LFO
#   torna a començar a cada bloc, el trèmolo es trenca.
#
#   Fórmula (fes-la servir exactament així, l'autotest la comprova):
#       lfo   = 0.5 + 0.5 * sin(fase)      → oscil·la entre 0 i 1
#       guany = 1 - profunditat * lfo      → entre 1 i (1 - profunditat)
#       sortida = entrada * guany
# ===============================================================

rate_hz = 5.0          # velocitat del trèmolo (cicles per segon)
profunditat = 0.8      # 0 = res, 1 = arriba al silenci

# TODO 1: declara la global 'fase_lfo' amb valor inicial 0.0
fase_lfo = None  # <-- substitueix


def tremolo_callback(indata, outdata, frames, time_info, status):
    global fase_lfo
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    # TODO 2:
    #   a) calcula les fases d'aquest bloc a partir de fase_lfo i rate_hz
    #      (mira sinus_callback a exemples.py)
    #   b) lfo i guany amb la fórmula de dalt
    #   c) outdata[:, 0] = mono * guany
    #   d) actualitza fase_lfo perquè el bloc següent continuï on s'acaba aquest
    pass  # <-- substitueix aquest 'pass'


def escolta_part1():
    global rate_hz, fase_lfo
    comprova_part1()
    fase_lfo = 0.0
    print("Trèmolo. Parla o toca alguna cosa sostinguda.")
    print("Escriu una velocitat (0.5 – 20 Hz) o 'q' per sortir.\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=tremolo_callback):
        while True:
            try:
                entrada = input(f"rate = {rate_hz:.1f} Hz → ")
            except KeyboardInterrupt:
                break
            entrada = entrada.strip().strip("'\"")
            if entrada.lower() == 'q':
                break
            try:
                nou = float(entrada)
            except ValueError:
                print("  Escriu només un número, per exemple: 7")
                continue
            if 0.5 <= nou <= 20.0:
                rate_hz = nou
            else:
                print("  Fora de rang (0.5 – 20 Hz)")
    print("Stream tancat.")


def comprova_part1():
    global fase_lfo, rate_hz, profunditat
    assert fase_lfo is not None, "Declara la global 'fase_lfo' (TODO 1)"
    # Fem a mà el que fa l'stream: cridem la callback DUES vegades seguides.
    # Truc: posem un LFO molt ràpid (un cicle cada 16 mostres) perquè es
    # vegi el moviment dins de blocs de només 8 mostres.
    rate_guardat, prof_guardada = rate_hz, profunditat
    rate_hz = sample_rate / 16
    profunditat = 0.8
    fase_lfo = 0.0
    entrada = np.ones((8, 1), dtype='float32')
    blocs = []
    try:
        for _ in range(2):
            sortida = np.zeros((8, 1), dtype='float32')
            tremolo_callback(entrada, sortida, 8, None, None)
            blocs.append(sortida[:, 0].copy())
    except UnboundLocalError:
        raise AssertionError("La callback no troba 'fase_lfo'. "
                             "Hi tens la línia `global fase_lfo`?")
    finally:
        rate_hz, profunditat = rate_guardat, prof_guardada
        fase_lfo = 0.0

    n = np.arange(16)
    esperat = 1 - 0.8 * (0.5 + 0.5 * np.sin(2 * np.pi * n / 16))
    assert not np.allclose(blocs[0], 0), "outdata no s'ha modificat — completa el TODO 2"
    assert np.allclose(blocs[0], esperat[:8], atol=1e-5), \
        f"El primer bloc no quadra amb la fórmula.\n  Esperat:  {np.round(esperat[:8], 3)}" \
        f"\n  Obtingut: {np.round(blocs[0], 3)}"
    assert not np.allclose(blocs[1], esperat[:8], atol=1e-5), \
        "El segon bloc és idèntic al primer: l'LFO torna a començar a cada bloc. " \
        "Actualitzes 'fase_lfo' al final de la callback?"
    assert np.allclose(blocs[1], esperat[8:], atol=1e-5), \
        f"El segon bloc no continua on s'acaba el primer.\n  Esperat:  " \
        f"{np.round(esperat[8:], 3)}\n  Obtingut: {np.round(blocs[1], 3)}"
    print("✅ Part 1: el trèmolo recorda la fase entre blocs")


# ===============================================================
# PART 2 — Eco amb realimentació
#
#   L'eco de exemples.py fa UNA sola repetició, perquè a la cinta
#   hi guarda l'entrada neta. Un eco "de muntanya" repeteix la
#   repetició, i la repetició de la repetició...
#
#   Canvia UNA cosa respecte a eco_callback: què escrius a la cinta.
#   Si hi escrius el que SURT (que ja porta l'eco a dins), l'eco
#   tornarà a passar per la cinta, cada vegada multiplicat per
#   'feedback'.
#
#       sortida = np.clip(mono + feedback * eco, -1.0, 1.0)
# ===============================================================

delay_s = 0.35
feedback = 0.6

# TODO 3: calcula delay_samples i crea la cinta (np.zeros, dtype='float32')
delay_samples = None   # <-- substitueix
delay_buffer = None    # <-- substitueix


def eco_fb_callback(indata, outdata, frames, time_info, status):
    global delay_buffer
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    # TODO 4: llegeix l'eco, calcula la sortida, avança la cinta,
    #         escriu-hi el que toca i omple outdata[:, 0]
    pass  # <-- substitueix aquest 'pass'


def escolta_part2():
    global feedback, delay_buffer
    comprova_part2()
    delay_buffer = np.zeros(delay_samples, dtype='float32')   # cinta en blanc
    print("Eco amb realimentació. Pica de mans i escolta les repeticions.")
    print("Escriu un feedback (0.0 – 1.0) o 'q' per sortir.")
    print("Prova 0.3, 0.8, 0.95... i 1.0 (compte amb el volum!).\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=eco_fb_callback):
        while True:
            try:
                entrada = input(f"feedback = {feedback:.2f} → ")
            except KeyboardInterrupt:
                break
            entrada = entrada.strip().strip("'\"")
            if entrada.lower() == 'q':
                break
            try:
                nou = float(entrada)
            except ValueError:
                print("  Escriu només un número, per exemple: 0.7")
                continue
            if 0.0 <= nou <= 1.0:
                feedback = nou
            else:
                print("  Fora de rang (0.0 – 1.0)")
    print("Stream tancat.")


def comprova_part2():
    global delay_buffer, feedback
    assert delay_samples is not None, "Calcula delay_samples (TODO 3)"
    assert delay_samples == int(delay_s * sample_rate), \
        f"delay_samples hauria de ser {int(delay_s * sample_rate)}, és {delay_samples}"
    assert delay_buffer is not None, "Crea la cinta delay_buffer (TODO 3)"
    assert len(delay_buffer) == delay_samples, \
        f"La cinta hauria de tenir {delay_samples} mostres, en té {len(delay_buffer)}"

    # Prova amb una cinta minúscula de 4 mostres (retard = 4 mostres)
    # i blocs de 2: entra un clic (1.0) i després silenci.
    fb_guardat = feedback
    feedback = 0.5
    delay_buffer = np.zeros(4, dtype='float32')
    entrada = np.zeros(10, dtype='float32')
    entrada[0] = 1.0
    sortida = np.zeros(10, dtype='float32')
    try:
        for i in range(0, 10, 2):
            bloc_out = np.zeros((2, 1), dtype='float32')
            eco_fb_callback(entrada[i:i + 2].reshape(-1, 1), bloc_out, 2, None, None)
            sortida[i:i + 2] = bloc_out[:, 0]
    except UnboundLocalError:
        raise AssertionError("La callback no troba 'delay_buffer'. "
                             "Hi tens la línia `global delay_buffer`?")
    finally:
        feedback = fb_guardat
        delay_buffer = np.zeros(delay_samples, dtype='float32')

    esperat = np.zeros(10)
    esperat[0], esperat[4], esperat[8] = 1.0, 0.5, 0.25
    assert not np.allclose(sortida, 0), "outdata no s'ha modificat — completa el TODO 4"
    assert np.isclose(sortida[4], 0.5, atol=1e-5), \
        f"L'eco no surt on toca (4 mostres després del clic). Sortida: {np.round(sortida, 3)}\n" \
        "  Llegeixes la part MÉS ANTIGA de la cinta?"
    assert not np.isclose(sortida[8], 0.0, atol=1e-5), \
        f"Només hi ha UNA repetició. Sortida: {np.round(sortida, 3)}\n" \
        "  Què estàs escrivint a la cinta?"
    assert np.allclose(sortida, esperat, atol=1e-5), \
        f"Esperat:  {esperat}\nObtingut: {np.round(sortida, 3)}"
    print("✅ Part 2: l'eco es realimenta (1 → 0.5 → 0.25 → ...)")


# ===============================================================
# PART 3 — L'ordre dels efectes: eco → distorsió (LA FAS TU SENCERA)
#
#   A exemples.py tens distorsió → eco: l'eco repeteix el so ja
#   distorsionat. Aquí tens aquella callback copiada (no la toquis)
#   per poder comparar.
#
#   Tu has d'escriure l'ordre INVERS: primer l'eco (d'una sola
#   repetició, com eco_callback de exemples.py: a la cinta hi va
#   l'entrada neta) i després tanh(... * drive) de TOT el resultat.
#
#   Fes servir la cinta delay_buffer_combo i els paràmetres de sota,
#   que són els mateixos de la versió de referència.
# ===============================================================

drive = 8.0
volum_eco = 0.5
delay_samples_combo = int(0.25 * sample_rate)
delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')


# --- Referència: distorsió → eco (ja feta, no la toquis) ---------
def disto_eco_callback(indata, outdata, frames, time_info, status):
    global delay_buffer_combo
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]
    dist = np.tanh(mono * drive)
    eco = delay_buffer_combo[:frames]
    sortida = dist + volum_eco * eco
    delay_buffer_combo = np.roll(delay_buffer_combo, -frames)
    delay_buffer_combo[-frames:] = dist
    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)


def escolta_disto_eco(segons=10):
    global delay_buffer_combo
    delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')
    print("REFERÈNCIA: distorsió → eco. Parla amb frases curtes.")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=disto_eco_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


# --- La teva: eco → distorsió ------------------------------------
def eco_disto_callback(indata, outdata, frames, time_info, status):
    # TODO 5: escriu la callback sencera (global, status, eco, tanh, cinta, outdata)
    pass  # <-- substitueix


def escolta_part3(segons=10):
    global delay_buffer_combo
    comprova_part3()
    delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')
    print("LA TEVA: eco → distorsió. Digues les mateixes frases que abans.")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=eco_disto_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


def comprova_part3():
    global delay_buffer_combo, drive
    # Cinta de 4 mostres, blocs de 2, drive suau perquè es noti la diferència
    drive_guardat = drive
    drive = 2.0
    delay_buffer_combo = np.zeros(4, dtype='float32')
    x = np.array([0.1, 0.2, 0.3, -0.4, 0.05, 0.0, 0.0, 0.0], dtype='float32')
    sortida = np.zeros(8, dtype='float32')
    try:
        for i in range(0, 8, 2):
            bloc_out = np.zeros((2, 1), dtype='float32')
            eco_disto_callback(x[i:i + 2].reshape(-1, 1), bloc_out, 2, None, None)
            sortida[i:i + 2] = bloc_out[:, 0]
    except UnboundLocalError:
        raise AssertionError("La callback no troba 'delay_buffer_combo'. "
                             "Hi tens la línia `global delay_buffer_combo`?")
    finally:
        drive = drive_guardat
        delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')

    retardat = np.concatenate([np.zeros(4), x[:4]])
    esperat = np.tanh(2.0 * (x + 0.5 * retardat))
    ordre_demo = np.clip(np.tanh(2.0 * x) + 0.5 * np.tanh(2.0 * retardat), -1, 1)
    assert not np.allclose(sortida, 0), "outdata no s'ha modificat — completa el TODO 5"
    assert not np.allclose(sortida, ordre_demo, atol=1e-5), \
        "Això és distorsió → eco (l'ordre de la referència). Aquí volem eco → distorsió."
    assert np.allclose(sortida, esperat, atol=1e-5), \
        f"Esperat:  {np.round(esperat, 3)}\nObtingut: {np.round(sortida, 3)}\n" \
        "  Recorda: eco d'una repetició (a la cinta hi va l'entrada neta) i " \
        "després tanh(… * drive)."
    print("✅ Part 3: eco → distorsió correcte")


# ===============================================================
# PART 4 — Reflexió (edita les strings)
# ===============================================================

# TODO 6
reflexio = {
    'brunzit_sinus':
        '',  # A demo_sinus_sense_memoria() sona un brunzit greu.
             # D'on surt? Per què té aproximadament aquella freqüència?

    'tremolo_sense_fase':
        '',  # Prova-ho: a la teva tremolo_callback, comenta la línia que
             # actualitza fase_lfo i escolta amb rate 5 Hz. Què sents?
             # Per què l'error és fins i tot més greu que al sinus de 440 Hz?

    'feedback':
        '',  # Què passa amb feedback = 1.0? I què passaria amb 1.2
             # si no hi hagués el np.clip?

    'ordre_efectes':
        '',  # Compara escolta_disto_eco() amb escolta_part3().
             # Què sents diferent? Per què passa?

    'preview_classes':
        '',  # Si volguessis un trèmolo + tres ecos amb realimentació a la
             # mateixa callback, quantes globals d'estat necessitaries?
             # Què et sembla aquesta manera de treballar?
}


# ===============================================================
# 🚀 CHALLENGE (opcional) — Stutter
#
#   El stutter "enganxa" un fragment curt de so i el repeteix en
#   bucle (ta-ta-ta-ta) fins que el deixes anar.
#
#   Pistes:
#   - stutter_buffer: una cinta de N mostres (prova 0.12 s) on, en
#     mode normal, vas guardant l'entrada (com l'eco).
#   - stutter_actiu: una global bool. El bucle principal la canvia
#     cada vegada que prems Enter.
#   - Mode normal (False): pass-through + anar alimentant la cinta.
#   - Mode stutter (True): NO toquis la cinta; reprodueix-la en bucle.
#     Necessitaràs recordar per on vas llegint entre crides (una
#     altra global!). Per llegir en bucle, l'operador % és el teu amic:
#         index = (posicio + np.arange(frames)) % N
# ===============================================================

# El teu codi del stutter aquí (callback + escolta_stutter())


# ===============================================================
def comprova_tot():
    comprova_part1()
    comprova_part2()
    comprova_part3()
    pendents = [p for p, r in reflexio.items() if not r.strip()]
    if pendents:
        print("⚠️  Reflexió pendent:", ", ".join(pendents))
    else:
        print("✅ Part 4: reflexió completa")


print("Funcions definides. Crida-les des de la consola, per exemple:")
print("  escolta_part1()   escolta_part2()")
print("  escolta_disto_eco()   escolta_part3()   comprova_tot()")
print("⚠️  Auriculars posats!")
