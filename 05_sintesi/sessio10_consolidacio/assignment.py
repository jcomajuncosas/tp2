"""
Assignment — Bloc 5c, Sessió 10 (Thonny)
La teva VeuFM, amb un teclat de veritat

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom.

COM TREBALLAR-HI A THONNY:
  1. Completa una part.
  2. Prem F5 (Run). Això només DEFINEIX les classes i funcions; no sona res.
  3. A la consola (Shell), crida la funció d'aquella part:
         >>> comprova_classes()
         >>> toca_teclat(0, VeuFM())
  4. Passa a la part següent.

Parts:  A  les teves classes de la S09
        B  l'envolvent que recorda on és: prediu abans de mirar
        C  el teclat (recordatori de la S06)
        D  el teclat toca la teva veu
        E  la tecla que talla la nota
        F  un kick a la tecla 36
        G  el teu instrument
        H  hi cap, al temps real?  ·  reflexió
"""

import time
import numpy as np
import sounddevice as sd
from scipy import signal
import rtmidi2
import mido

sample_rate = 44100
blocksize = 512


def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))


# ===============================================================
# PART A — Les teves classes
#
#   Copia aquí, del notebook de la S09, les tres classes tal com
#   les tens:
#     - Oscillator (amb _ona, process i process_freqs)
#     - Envelope (la de la Part 4, la que té self.stage)
#     - VeuFM (la teva, Part 5)
#   Després F5 i, a la Shell:  >>> comprova_classes()
# ===============================================================

# Enganxa aquí les teves classes Oscillator, Envelope i VeuFM




def comprova_classes():
    """Comprova que les classes enganxades funcionen fora del notebook."""
    if 'VeuFM' not in globals() or 'Envelope' not in globals() or 'Oscillator' not in globals():
        print("❌ Falten classes: enganxa Oscillator, Envelope i VeuFM a la Part A i prem F5")
        return
    veu = VeuFM(ratio=2.0, I_max=4.0)
    veu.note_on(57, 127)
    bloc = veu.process(blocksize)
    assert len(bloc) == blocksize, "process(512) no retorna 512 mostres"
    assert abs(veu.modulator.freq - 440.0) < 0.01, "El modulador hauria de ser portador × ratio"
    veu.note_off()
    for i in range(60):
        bloc = veu.process(blocksize)
    assert np.max(np.abs(bloc)) < 1e-6, "Després del release hauria d'haver-hi silenci"
    print("✅ Part A: les teves classes funcionen a Thonny")


# ===============================================================
# PART B — L'envolvent que recorda on és (prediu abans de mirar)
#
#   Una Envelope(attack=0.05, decay=0.2, sustain=0.6, release=0.3)
#   rep un note_on i després li demanem blocs de 512 mostres
#   (bloc 0 = mostres 0..511, bloc 1 = mostres 512..1023, ...).
#
#   Sense executar res, amb llapis i calculadora:
#     1. A quin bloc passa de 'attack' a 'decay'?
#     2. A quin bloc passa de 'decay' a 'sustain'?
#     3. Una altra nota: note_on, 3 blocs, i note_off (l'attack no
#        s'ha acabat!). Amb quin nivell (0..1) comença el release?
#
#   Pista: quantes mostres són 0,05 s? I quantes mostres té un bloc?
#
#   >>> comprova_prediccions()     (et diu si l'has encertat)
#   >>> traca_envelope()            (mira-ho bloc a bloc)
# ===============================================================

prediccio_bloc_decay = None      # <-- un número de bloc
prediccio_bloc_sustain = None    # <-- un número de bloc
prediccio_nivell_release = None  # <-- un nivell entre 0 i 1


def _primer_bloc_amb(env, stage, max_blocs=100):
    for b in range(max_blocs):
        env.process(blocksize)
        if env.stage == stage:
            return b
    return None


def comprova_prediccions():
    if prediccio_bloc_decay is None or prediccio_bloc_sustain is None or prediccio_nivell_release is None:
        print("❌ Primer escriu les tres prediccions (no les deixis a None) i prem F5")
        return
    env = Envelope(attack=0.05, decay=0.2, sustain=0.6, release=0.3)
    env.note_on()
    bloc_decay = _primer_bloc_amb(env, 'decay')
    env = Envelope(attack=0.05, decay=0.2, sustain=0.6, release=0.3)
    env.note_on()
    bloc_sustain = _primer_bloc_amb(env, 'sustain')
    env = Envelope(attack=0.05, decay=0.2, sustain=0.6, release=0.3)
    env.note_on()
    for b in range(3):
        env.process(blocksize)
    nivell = env.level
    print("1. decay comença al bloc   :", bloc_decay, "   (la teva predicció:", prediccio_bloc_decay, ")")
    print("2. sustain comença al bloc :", bloc_sustain, "   (la teva predicció:", prediccio_bloc_sustain, ")")
    print("3. el release comença a    :", round(nivell, 3), " (la teva predicció:", prediccio_nivell_release, ")")
    if prediccio_bloc_decay == bloc_decay and prediccio_bloc_sustain == bloc_sustain \
            and abs(prediccio_nivell_release - nivell) < 0.05:
        print("✅ Part B: les tres prediccions són bones")
    else:
        print("Alguna no quadra: on t'has equivocat, en les mostres o en els blocs? Mira traca_envelope()")


def traca_envelope(blocs_abans_off=25, blocs_total=50):
    """Imprimeix, bloc a bloc, l'stage i el nivell al final del bloc."""
    env = Envelope(attack=0.05, decay=0.2, sustain=0.6, release=0.3)
    env.note_on()
    anterior = None
    for b in range(blocs_total):
        if b == blocs_abans_off:
            env.note_off()
            print("       ---- note_off ----")
        env.process(blocksize)
        marca = ""
        if env.stage != anterior:
            marca = "   <-- canvi"
        print("bloc", b, "  mostres", b * blocksize, "a", (b + 1) * blocksize - 1,
              "  ", env.stage, "  nivell", round(env.level, 3), marca)
        anterior = env.stage


# ===============================================================
# PART C — El teclat (recordatori de la S06)
#
#   El teclat arriba per un port MIDI. El callback MIDI el crida el
#   sistema a cada missatge, en un altre fil; el callback d'àudio el
#   crida la targeta de so a cada bloc. Avui en tindrem DOS alhora.
#
#   >>> llista_ports()
#   >>> mostra_missatges(0)        (el número del teu teclat; 10 s)
#   Prem tecles, deixa-les anar, toca fluix i fort. Què arriba quan
#   deixes anar una tecla? (Alguns teclats envien note_off, d'altres
#   note_on amb velocity 0: tots dos volen dir el mateix.)
# ===============================================================

def llista_ports():
    entrades = rtmidi2.MidiIn().ports
    print("Entrades MIDI:")
    for i in range(len(entrades)):
        print(" ", i, entrades[i])
    if len(entrades) == 0:
        print("  (cap: el teclat està connectat?)")


def obre_entrada(numero):
    entrada = rtmidi2.MidiIn()
    if numero >= len(entrada.ports):
        print("No hi ha l'entrada", numero, "- crida llista_ports() per veure quines hi ha.")
        return None
    entrada.open_port(numero)
    print("Entrada oberta:", entrada.ports[numero])
    return entrada


def _imprimeix(dades, timestamp):
    msg = mido.Message.from_bytes(dades)
    if msg.type != 'clock' and msg.type != 'active_sensing':
        print("  ", msg)


def mostra_missatges(numero, segons=10):
    entrada = obre_entrada(numero)
    if entrada is None:
        return
    entrada.callback = _imprimeix
    time.sleep(segons)
    entrada.callback = None
    entrada.close_port()
    print("Fet.")


# ===============================================================
# PART D — El teclat toca la teva veu
#
#   Escriu gestiona(msg, veu, kick): rep UN missatge (ja traduït
#   per mido) i el fa arribar a la veu:
#     - si és una nota que comença: la veu ha de començar aquella
#       nota, amb la velocity del missatge
#     - si és una nota que acaba (recorda les dues maneres de la
#       Part C): la veu ha d'iniciar el release
#     - qualsevol altre missatge (controls, pitch bend...): res
#   El paràmetre kick no el facis servir fins a la Part F.
#
#   Atributs que et caldran: msg.type, msg.note, msg.velocity.
#
#   >>> comprova_gestiona()
#   >>> toca_teclat(0, VeuFM())                 (el número del teu teclat)
#   >>> toca_teclat(0, VeuFM(ratio=1.41, I_max=6, attack=0.4))
#   Prova almenys 3 veus diferents. Amb l'attack llarg, toca una
#   tecla molt curta: per què no fa cap clic? (Part B, pregunta 3)
# ===============================================================

def gestiona(msg, veu, kick):
    pass  # <-- el teu codi


# --- Ja fet: l'instrument i els dos callbacks (llegeix-ho!) -----

class Instrument:
    """Un UGen més: conté la veu i el kick, i en suma les mostres."""
    def __init__(self, veu, kick=None):
        self.veu = veu
        self.kick = kick

    def process(self, n_samples):
        so = self.veu.process(n_samples)
        if self.kick is not None:
            so = so + self.kick.process(n_samples)
        return so


instrument = None             # l'única global: el que sona ara


def callback_midi(dades, timestamp):
    # el crida el sistema a cada missatge (fil MIDI): només reacciona
    msg = mido.Message.from_bytes(dades)
    gestiona(msg, instrument.veu, instrument.kick)


def callback_audio(outdata, frames, time_info, status):
    # el crida la targeta a cada bloc (fil d'àudio): només demana mostres
    if status:
        print(status)
    outdata[:, 0] = 0.4 * instrument.process(frames)


def toca_teclat(numero, veu, kick=None, segons=30):
    global instrument
    instrument = Instrument(veu, kick)
    entrada = obre_entrada(numero)
    if entrada is None:
        return
    print("Toca!", segons, "segons.")
    with sd.OutputStream(samplerate=sample_rate, blocksize=blocksize,
                         channels=1, dtype='float32', callback=callback_audio):
        entrada.callback = callback_midi
        time.sleep(segons)
        entrada.callback = None
    entrada.close_port()
    print("Fet.")


def prova_sense_teclat(veu, kick=None):
    """Per treballar a casa sense teclat: envia missatges a gestiona() des del programa."""
    global instrument
    instrument = Instrument(veu, kick)
    passos = [('note_on', 60, 100, 0.3), ('note_off', 60, 0, 0.1),
              ('note_on', 64, 70, 0.3), ('note_on', 64, 0, 0.1),
              ('note_on', 36, 120, 0.25), ('note_on', 67, 110, 0.3),
              ('note_on', 36, 90, 0.25), ('note_off', 36, 0, 0.05),
              ('note_off', 67, 0, 0.6)]
    with sd.OutputStream(samplerate=sample_rate, blocksize=blocksize,
                         channels=1, dtype='float32', callback=callback_audio):
        for tipus, nota, vel, espera in passos:
            gestiona(mido.Message(tipus, note=nota, velocity=vel), instrument.veu, instrument.kick)
            time.sleep(espera)
        time.sleep(0.5)


def comprova_gestiona():
    veu = VeuFM()
    gestiona(mido.Message('control_change', control=1, value=64), veu, None)
    assert veu.env.stage == 'idle', "Un control_change no hauria de fer sonar res"
    gestiona(mido.Message('note_on', note=60, velocity=100), veu, None)
    assert veu.env.stage == 'attack', "Un note_on hauria de començar la nota"
    assert abs(veu.carrier.freq - note_to_freq(60)) < 0.01, "La nota no és la del missatge"
    assert abs(veu.gain - 100 / 127) < 0.01, "La velocity no és la del missatge"
    gestiona(mido.Message('note_off', note=60, velocity=0), veu, None)
    assert veu.env.stage == 'release', "Un note_off hauria d'iniciar el release"
    gestiona(mido.Message('note_on', note=62, velocity=90), veu, None)
    gestiona(mido.Message('note_on', note=62, velocity=0), veu, None)
    assert veu.env.stage == 'release', "Un note_on amb velocity 0 també és un final de nota"
    print("✅ Part D: gestiona fa arribar els missatges a la veu")


# ===============================================================
# PART E — La tecla que talla la nota
#
#   Toca legato: prem una tecla i, SENSE deixar-la anar, prem-ne
#   una altra; després deixa anar la PRIMERA. Què passa amb la
#   segona? Escriu què has sentit i per què a reflexio_legato.
#
#   Arregla-ho: un final de nota només ha d'aturar la veu si és el
#   final de la nota que sona ara. Tu decideixes què ha de recordar
#   la veu i on fas la comprovació (a VeuFM, a gestiona o a tots
#   dos llocs). Una veu toca una sola nota: no cal polifonia.
#
#   >>> comprova_legato()
#   >>> toca_teclat(0, VeuFM(attack=0.08, release=0.5))
# ===============================================================

reflexio_legato = """
Què passa i per què:
"""


def comprova_legato():
    veu = VeuFM()
    gestiona(mido.Message('note_on', note=60, velocity=100), veu, None)
    gestiona(mido.Message('note_on', note=64, velocity=100), veu, None)
    assert abs(veu.carrier.freq - note_to_freq(64)) < 0.01, "La nota nova hauria de sonar"
    gestiona(mido.Message('note_off', note=60, velocity=0), veu, None)
    assert veu.env.stage != 'release', \
        "Has deixat anar el 60, però sona el 64: la veu no s'hauria d'aturar"
    gestiona(mido.Message('note_on', note=60, velocity=0), veu, None)
    assert veu.env.stage != 'release', "Tampoc amb un note_on amb velocity 0 del 60"
    gestiona(mido.Message('note_off', note=64, velocity=0), veu, None)
    assert veu.env.stage == 'release', "Has deixat anar la nota que sonava: ara sí, release"
    gestiona(mido.Message('note_on', note=67, velocity=80), veu, None)
    gestiona(mido.Message('note_on', note=67, velocity=0), veu, None)
    assert veu.env.stage == 'release', "Una nota sola s'ha de poder aturar"
    print("✅ Part E: el legato ja no talla la nota")


# ===============================================================
# PART F — Un kick a la tecla 36
#
#   La tecla 36 és el kick al mapa de percussió General MIDI
#   (S07). Un kick sintètic és un oscil·lador que CAU d'alçada molt
#   de pressa: de f_inici a f_final en 'caiguda' segons, i després
#   s'hi queda, amb una envolvent curta sense sustain.
#
#   1. Completa Kick.process: a cada bloc, freqs ha de tenir UNA
#      freqüència per mostra. La caiguda es compta des del note_on,
#      però un bloc no sap quant fa que va començar la nota: què
#      ha de recordar el Kick? Una baixada en línia recta ja val.
#   2. Completa Kick.note_on: el que calgui perquè cada cop soni
#      igual.
#   3. Amplia gestiona: la tecla 36 toca el kick (amb la seva
#      velocity) i no ha de tocar ni aturar la veu.
#
#   >>> comprova_kick()
#   >>> escolta_kick()
#   >>> toca_teclat(0, VeuFM(), Kick())
#   Variacions: Kick(f_inici=300, caiguda=0.02), Kick(f_final=40,
#   decay=0.8), ... Quina combinació sona a 808? I a una porta?
# ===============================================================

class Kick:
    def __init__(self, f_inici=150.0, f_final=50.0, caiguda=0.08, decay=0.3):
        self.f_inici = f_inici
        self.f_final = f_final
        self.caiguda = caiguda
        self.osc = Oscillator()
        self.env = Envelope(attack=0.002, decay=decay, sustain=0.0, release=0.05)
        self.gain = 0.0
        # <-- el que hagi de recordar el Kick

    def note_on(self, velocity=100):
        self.gain = velocity / 127
        self.env.note_on()
        # <-- el teu codi

    def note_off(self):
        pass                      # un kick no s'atura: s'apaga sol

    def process(self, n_samples):
        freqs = np.zeros(n_samples)
        # <-- el teu codi: omple freqs
        return self.osc.process_freqs(freqs) * self.env.process(n_samples) * self.gain


def _freqs_del_kick(kick, n_mostres, bloc):
    """Toca un kick i retorna totes les freqüències que ha demanat a l'oscil·lador."""
    capturades = []
    original = kick.osc.process_freqs

    def espia(freqs):
        capturades.append(np.array(freqs, dtype=float))
        return original(freqs)

    kick.osc.process_freqs = espia
    kick.note_on(100)
    fet = 0
    while fet < n_mostres:
        kick.process(bloc)
        fet = fet + bloc
    kick.osc.process_freqs = original
    return np.concatenate(capturades)[:n_mostres]


def comprova_kick():
    n = int(0.2 * sample_rate)
    k = Kick(f_inici=200.0, f_final=60.0, caiguda=0.05)
    f = _freqs_del_kick(k, n, blocksize)
    assert abs(f[0] - 200.0) < 10, "La primera mostra hauria de ser a f_inici"
    assert np.max(np.abs(np.diff(f))) < 2, \
        "Hi ha un salt brusc de freqüència entre dues mostres: comença de nou a cada bloc?"
    assert np.max(np.diff(f)) <= 1e-9, "La freqüència no hauria de pujar mai: ha de caure i quedar-s'hi"
    assert abs(f[int(0.1 * sample_rate)] - 60.0) < 2, "Passada la caiguda, la freqüència hauria de ser f_final"
    assert abs(f[-1] - 60.0) < 2, "Al final, la freqüència s'hauria de quedar a f_final"
    f_petit = _freqs_del_kick(Kick(f_inici=200.0, f_final=60.0, caiguda=0.05), n, 100)
    assert np.allclose(f, f_petit, atol=0.5), \
        "Amb blocs de 100 mostres la caiguda és diferent: ha de dependre del temps des del note_on, no del bloc"
    f_2 = _freqs_del_kick(k, 1000, blocksize)
    assert abs(f_2[0] - 200.0) < 10, "Un segon note_on hauria de tornar a començar la caiguda"
    k = Kick()
    cops = []
    for c in range(2):
        k.note_on(100)
        so = np.zeros(0)
        for b in range(40):
            so = np.concatenate([so, k.process(blocksize)])
        cops.append(so)
    assert np.allclose(cops[0], cops[1], atol=1e-6), \
        "Dos cops seguits no sonen igual: hi ha alguna cosa del cop anterior que no tornes a posar a lloc?"
    veu = VeuFM()
    kick = Kick()
    gestiona(mido.Message('note_on', note=60, velocity=100), veu, kick)
    gestiona(mido.Message('note_on', note=36, velocity=120), veu, kick)
    assert kick.env.stage == 'attack', "La tecla 36 hauria de disparar el kick"
    assert abs(kick.gain - 120 / 127) < 0.01, "El kick no fa servir la velocity del missatge"
    assert abs(veu.carrier.freq - note_to_freq(60)) < 0.01, "La tecla 36 no hauria de canviar la nota de la veu"
    gestiona(mido.Message('note_off', note=36, velocity=0), veu, kick)
    assert veu.env.stage != 'release', "Deixar anar el 36 no hauria d'aturar la veu"
    print("✅ Part F: el kick cau, s'hi queda i viu a la tecla 36")


def escolta_kick():
    global instrument
    for k in [Kick(), Kick(f_inici=300.0, caiguda=0.02, decay=0.15), Kick(f_final=40.0, decay=0.8)]:
        instrument = Instrument(VeuFM(), k)
        with sd.OutputStream(samplerate=sample_rate, blocksize=blocksize,
                             channels=1, dtype='float32', callback=callback_audio):
            k.note_on(120)
            time.sleep(1.0)


# ===============================================================
# PART G — El teu instrument
#
#   Aquest instrument és la base del teu projecte final. Tria:
#     - el teu preset de veu (ratio, I_max i envolvent)
#     - el teu kick (f_inici, f_final, caiguda, decay)
#   i toca'l amb el teclat. Busca-hi un caràcter: no deixis els
#   valors per defecte.
#
#   >>> escolta_meu(0)
# ===============================================================

la_meva_veu = None        # <-- una VeuFM amb els teus paràmetres
el_meu_kick = None        # <-- un Kick amb els teus paràmetres


def escolta_meu(numero, segons=60):
    assert la_meva_veu is not None and el_meu_kick is not None, "Crea la_meva_veu i el_meu_kick"
    toca_teclat(numero, la_meva_veu, el_meu_kick, segons)


# ===============================================================
# PART H — Hi cap, al temps real?
#
#   process_freqs i Envelope.process tenen un bucle de Python mostra
#   a mostra, i corren dins el callback d'àudio. El callback té un
#   termini: ha d'acabar abans que s'acabi el bloc que sona.
#
#   >>> mesura_cost(la_meva_veu, el_meu_kick)
#   >>> mesura_cost(la_meva_veu, el_meu_kick, bloc=64)
# ===============================================================

def mesura_cost(veu, kick, bloc=blocksize, n_blocs=200):
    inst = Instrument(veu, kick)
    veu.note_on(60, 100)
    kick.note_on(100)
    temps = np.zeros(n_blocs)
    for b in range(n_blocs):
        t0 = time.perf_counter()
        inst.process(bloc)
        temps[b] = time.perf_counter() - t0
    termini = bloc / sample_rate
    print("bloc de", bloc, "mostres → termini", round(termini * 1000, 2), "ms")
    print("cost mitjà", round(np.mean(temps) * 1000, 3), "ms   pitjor", round(np.max(temps) * 1000, 3), "ms")
    print("fem servir el", round(100 * np.mean(temps) / termini, 1), "% del termini")


reflexio_cost = """
Quantes veus com la teva hi cabrien, més o menys? Per què el
percentatge gairebé no canvia amb bloc=64? Què canvia, aleshores,
en fer el bloc més petit?
"""

reflexio_callbacks = """
Avui hi ha dos callbacks. Quin d'ells canvia l'estat de la veu i
quin el llegeix? Per què una nota que toques no comença exactament
quan prems la tecla, sinó una mica després (com a molt, quant)?
"""


# ===============================================================
# 🚀 CHALLENGES (opcionals) — són a recursos/challenges.md
# ===============================================================


print("Funcions definides. Crida-les des de la consola:")
print("  comprova_classes()    comprova_prediccions()   traca_envelope()")
print("  llista_ports()        mostra_missatges(0)")
print("  comprova_gestiona()   comprova_legato()        comprova_kick()     escolta_kick()")
print("  toca_teclat(0, VeuFM(), Kick())    escolta_meu(0)    mesura_cost(la_meva_veu, el_meu_kick)")
