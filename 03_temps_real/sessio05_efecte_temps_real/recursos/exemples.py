"""
Exemples — Bloc 3c, Sessió 5 (Thonny)
Efectes amb memòria: la fase d'un oscil·lador i la cinta d'un eco

⚠️  AURICULARS OBLIGATORIS. Micròfon + altaveus = realimentació (Larsen).

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.

COM FUNCIONA:
  1. Prem F5 (Run). Això només DEFINEIX les funcions; no sona res.
  2. A la consola (Shell), crida la demo que vulguis:
         >>> demo_sinus_sense_memoria()
         >>> demo_sinus()
         >>> demo_ringmod()
         >>> demo_eco()
         >>> demo_eco_control()
         >>> demo_disto_eco()
         >>> demo_dos_ecos()
  Ctrl+C atura qualsevol demo abans d'hora.

La idea de tota la sessió: la callback té AMNÈSIA. Cada vegada que
l'stream la crida, només veu el bloc actual (~23 ms). Tot el que
s'hagi de recordar d'un bloc al següent ha de viure FORA, en una
variable global:
    · distorsió (S04)   → no cal recordar res
    · oscil·lador        → cal recordar UN número (la fase)
    · eco                → cal recordar MOLTES mostres (una cinta)
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024


# ===============================================================
# 1. Un sinus generat bloc a bloc, SENSE memòria
#    (escolta-ho abans de mirar el codi: què hi ha de més?)
# ===============================================================

freq_sinus = 440.0


def sinus_sense_memoria_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    t = np.arange(frames) / sample_rate      # ⚠️ t torna a començar a 0 a CADA bloc
    outdata[:, 0] = 0.2 * np.sin(2 * np.pi * freq_sinus * t)


def demo_sinus_sense_memoria(segons=5):
    print(f"Un sinus de {freq_sinus:.0f} Hz... o no ben bé. Escolta el fons.")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=sinus_sense_memoria_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")
    print(f"Pista: la callback es crida {sample_rate / blocksize:.0f} vegades per segon.")


# ===============================================================
# 2. El mateix sinus, AMB memòria: guardem la FASE
#
#    La fase és "on és" l'oscil·lador dins el seu cicle (0 … 2π).
#    Al final de cada bloc la desem; el bloc següent continua
#    exactament des d'allà. Un sol número salva el so.
# ===============================================================

fase_sinus = 0.0    # ← la MEMÒRIA de l'oscil·lador (viu fora de la callback)


def sinus_callback(indata, outdata, frames, time_info, status):
    global fase_sinus                         # l'ESCRIVIM → cal `global`
    if status:
        print("STATUS:", status)
    increment = 2 * np.pi * freq_sinus / sample_rate     # quant avança per mostra
    fases = fase_sinus + increment * np.arange(frames)   # fases d'aquest bloc
    outdata[:, 0] = 0.2 * np.sin(fases)
    # On ha de començar el bloc SEGÜENT? Just després de l'última mostra d'aquest.
    # El % 2π només manté el número petit (sin no canvia si sumem voltes senceres).
    fase_sinus = (fase_sinus + increment * frames) % (2 * np.pi)


def demo_sinus(segons=5):
    global fase_sinus
    fase_sinus = 0.0                          # estat inicial ABANS d'obrir l'stream
    print(f"Sinus de {freq_sinus:.0f} Hz amb la fase guardada. Compara'l amb l'anterior.")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=sinus_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


# ===============================================================
# 3. Ring modulator: entrada × oscil·lador
#
#    Multipliquem la veu per un sinus (la "portadora"). El resultat
#    té freqüències noves (suma i diferència): so metàl·lic, robòtic.
#    Necessita la mateixa memòria que el sinus: la fase.
#    (Fixa't: és una global NOVA, fase_ringmod. Cada oscil·lador
#    necessita la seva... guarda't aquest pensament.)
# ===============================================================

freq_portadora = 300.0
fase_ringmod = 0.0


def ringmod_callback(indata, outdata, frames, time_info, status):
    global fase_ringmod
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]
    increment = 2 * np.pi * freq_portadora / sample_rate
    portadora = np.sin(fase_ringmod + increment * np.arange(frames))
    outdata[:, 0] = mono * portadora
    fase_ringmod = (fase_ringmod + increment * frames) % (2 * np.pi)


def demo_ringmod():
    global fase_ringmod, freq_portadora
    fase_ringmod = 0.0
    print("Ring modulator. Parla, canta, xiula...")
    print("Escriu una freqüència de portadora (20 – 2000 Hz) o 'q' per sortir.")
    print("Prova 30, 150, 600, 1500... i també valors baixos com 5.\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=ringmod_callback):
        while True:
            try:
                entrada = input(f"portadora = {freq_portadora:.0f} Hz → ")
            except KeyboardInterrupt:
                break
            entrada = entrada.strip().strip("'\"")
            if entrada.lower() == 'q':
                break
            try:
                nova = float(entrada)
            except ValueError:
                print("  Escriu només un número, per exemple: 150")
                continue
            if 1.0 <= nova <= 2000.0:
                freq_portadora = nova     # la callback la llegirà al bloc següent
            else:
                print("  Fora de rang (1 – 2000 Hz)")
    print("Stream tancat.")


# ===============================================================
# 4. Eco: la memòria ja no és un número, és una CINTA de mostres
#
#    delay_buffer és una cinta de delay_samples mostres.
#    A cada crida:
#      1. LLEGIM l'extrem més antic   → és el so de fa delay_s segons
#      2. MESCLEM entrada + eco
#      3. AVANCEM la cinta 'frames' posicions i ESCRIVIM el bloc nou
#         a l'altre extrem
#    Una mostra que entra ara tornarà a sortir exactament
#    delay_samples mostres més tard.
#
#    Aquest eco fa UNA sola repetició: a la cinta hi guardem
#    l'entrada neta, no la sortida.
# ===============================================================

delay_s = 0.3
volum_eco = 0.6
delay_samples = int(delay_s * sample_rate)
delay_buffer = np.zeros(delay_samples, dtype='float32')


def eco_callback(indata, outdata, frames, time_info, status):
    global delay_buffer
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    eco = delay_buffer[:frames]               # 1. llegim les mostres MÉS ANTIGUES
    sortida = mono + volum_eco * eco          # 2. mesclem

    delay_buffer = np.roll(delay_buffer, -frames)   # 3. la cinta avança...
    delay_buffer[-frames:] = mono                   #    ...i hi escrivim el bloc nou

    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)


def demo_eco(segons=10):
    global delay_samples, volum_eco, delay_buffer
    delay_samples = int(delay_s * sample_rate)   # estat inicial ABANS de l'stream
    volum_eco = 0.6
    delay_buffer = np.zeros(delay_samples, dtype='float32')   # cinta en blanc
    print(f"Eco de {delay_s} s. Pica de mans, digues una paraula curta...")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=eco_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


# ===============================================================
# 5. Eco amb control en directe
#
#    Repartiment de feines (important!):
#      · el BUCLE només canvia NÚMEROS (delay_samples, volum_eco)
#      · la CALLBACK és l'única que toca la cinta
#    Si el bucle substituís el buffer mentre la callback hi treballa,
#    la callback podria trepitjar-lo amb la versió vella.
#
#    Retard mínim: la callback llegeix 'frames' mostres de la cinta,
#    així que la cinta no pot ser més curta que un bloc
#    (1024 / 44100 ≈ 0.023 s).
# ===============================================================

retard_minim = blocksize / sample_rate


def eco_control_callback(indata, outdata, frames, time_info, status):
    global delay_buffer
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    # Si el bucle ha canviat el retard, fem una cinta nova (en blanc:
    # l'eco calla durant un retard, és el preu d'aquesta solució simple)
    if len(delay_buffer) != delay_samples:
        delay_buffer = np.zeros(delay_samples, dtype='float32')

    eco = delay_buffer[:frames]
    sortida = mono + volum_eco * eco
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = mono
    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)


def demo_eco_control():
    global delay_samples, volum_eco, delay_buffer
    delay_samples = int(0.3 * sample_rate)
    volum_eco = 0.6
    delay_buffer = np.zeros(delay_samples, dtype='float32')

    print("Ordres:")
    print(f"  r 0.5   → retard en segons ({retard_minim:.3f} – 2.0)")
    print("  v 0.7   → volum de l'eco (0.0 – 1.0)")
    print("  q       → sortir\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=eco_control_callback):
        while True:
            try:
                entrada = input(f"[retard {delay_samples / sample_rate:.2f} s · "
                                f"volum {volum_eco:.2f}] > ")
            except KeyboardInterrupt:
                break
            # Acceptem 'r 0.5', 'r=0.5', amb o sense cometes
            entrada = entrada.strip().strip("'\"").lower().replace('=', ' ')
            if entrada == 'q':
                break
            parts = entrada.split()
            if len(parts) != 2 or parts[0] not in ('r', 'v'):
                print("  No t'entenc. Una ordre cada vegada: 'r 0.5', 'v 0.7' o 'q'")
                continue
            try:
                valor = float(parts[1])
            except ValueError:
                print(f"  '{parts[1]}' no és un número")
                continue

            if parts[0] == 'r':
                if retard_minim <= valor <= 2.0:
                    delay_samples = int(valor * sample_rate)
                else:
                    print(f"  El retard ha d'estar entre {retard_minim:.3f} i 2.0 s")
            else:
                if 0.0 <= valor <= 1.0:
                    volum_eco = valor
                else:
                    print("  El volum ha d'estar entre 0.0 i 1.0")
    print("Stream tancat.")


# ===============================================================
# 6. Dos efectes encadenats: distorsió → eco
#
#    Primer distorsionem (la tanh de la S04), després l'eco
#    repeteix el so JA distorsionat. Per això a la cinta hi
#    guardem 'dist', no 'mono'.
#    (A l'assignment faràs l'ordre invers i els compararàs.)
# ===============================================================

drive = 8.0


def disto_eco_callback(indata, outdata, frames, time_info, status):
    global delay_buffer
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    dist = np.tanh(mono * drive)              # 1. distorsió (sense memòria)

    eco = delay_buffer[:frames]               # 2. eco sobre la distorsió
    sortida = dist + volum_eco * eco
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = dist             #    guardem la distorsió, no el so net

    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)


def demo_disto_eco(segons=10):
    global delay_samples, volum_eco, delay_buffer
    delay_samples = int(0.25 * sample_rate)
    volum_eco = 0.5
    delay_buffer = np.zeros(delay_samples, dtype='float32')
    print(f"Distorsió (drive={drive}) → eco de 0.25 s. Baixa una mica el volum.")
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


# ===============================================================
# 7. Dos ecos alhora → dues cintes globals
#
#    Funciona. Però compta les globals que ja portem avui:
#    fase_sinus, fase_ringmod, delay_buffer, delay_buffer_1,
#    delay_buffer_2... I si en volguéssim 5? I un trèmolo a sobre?
#    Pregunta per al Bloc 5.
#
#    (Apunt per als curiosos: com que tots dos ecos llegeixen la
#    MATEIXA entrada, es podrien treure d'una sola cinta de 0.4 s
#    llegint-la en dos punts — un delay "multitap". Però quan cada
#    eco té la seva realimentació, o processa un senyal diferent,
#    cadascun necessita la seva pròpia cinta.)
# ===============================================================

delay_samples_1 = int(0.15 * sample_rate)
delay_samples_2 = int(0.40 * sample_rate)
delay_buffer_1 = np.zeros(delay_samples_1, dtype='float32')
delay_buffer_2 = np.zeros(delay_samples_2, dtype='float32')
volum_eco_1 = 0.5
volum_eco_2 = 0.35


def dos_ecos_callback(indata, outdata, frames, time_info, status):
    global delay_buffer_1, delay_buffer_2
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    eco1 = delay_buffer_1[:frames]
    delay_buffer_1 = np.roll(delay_buffer_1, -frames)
    delay_buffer_1[-frames:] = mono

    eco2 = delay_buffer_2[:frames]
    delay_buffer_2 = np.roll(delay_buffer_2, -frames)
    delay_buffer_2[-frames:] = mono

    sortida = mono + volum_eco_1 * eco1 + volum_eco_2 * eco2
    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)


def demo_dos_ecos(segons=8):
    global delay_buffer_1, delay_buffer_2
    delay_buffer_1 = np.zeros(delay_samples_1, dtype='float32')
    delay_buffer_2 = np.zeros(delay_samples_2, dtype='float32')
    print("Dos ecos (0.15 s i 0.40 s). Dues cintes, dues globals...")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=dos_ecos_callback):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")
    print("I si en volguéssim 5? Ho resoldrem al Bloc 5.")


print("Funcions definides. Crida-les des de la consola, per exemple:")
print("  demo_sinus_sense_memoria()   demo_sinus()   demo_ringmod()")
print("  demo_eco()   demo_eco_control()   demo_disto_eco()   demo_dos_ecos()")
print("⚠️  Auriculars posats!")
