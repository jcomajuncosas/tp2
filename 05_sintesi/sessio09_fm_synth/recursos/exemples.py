"""
Exemples — Bloc 5b, Sessió 9 (Thonny)
Arquitectura UGen, control rate, FM synthesis, integració temps real + MIDI

Requereix: sounddevice, numpy
Secció 6 (MIDI real): requereix un controlador MIDI connectat (USB o Bluetooth).
Si no en tens, salta-la i fes servir la Secció 6b (simulació amb seqüència interna).
"""

import numpy as np
import sounddevice as sd

sample_rate = 44100


# =================================================================
# 1. Recordatori de la Sessió 8: el problema del "click" de fase
# =================================================================
print("=== 1. El problema: Oscillator (S8) generat per blocs ===")


class OscillatorBatch:
    """Versió de la Sessió 8 — recordatori. NO l'usarem més a partir d'aquí."""

    def __init__(self, freq=440.0, sample_rate=44100):
        self.freq = freq
        self.sample_rate = sample_rate

    def generate(self, duration):
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        return np.sin(2 * np.pi * self.freq * t)


osc_batch = OscillatorBatch(freq=440)
bloc1 = osc_batch.generate(0.1)
bloc2 = osc_batch.generate(0.1)  # generate() torna a començar t=0 cada cop!
junts = np.concatenate([bloc1, bloc2])

print("generate() sempre comença la t a 0 → si encadenem dos blocs,")
print("la fase 'salta' i sentim un click. Comprova-ho:")
sd.play(junts, sample_rate)
sd.wait()
print("(si has sentit un petit clic/glitch entre els dos blocs, és exactament això)\n")


# =================================================================
# 2. L'arquetip UGen: process(n_samples), amb estat persistent
# =================================================================
print("=== 2. La solució: process(n_samples) amb fase pròpia ===")


class Oscillator:
    """
    Mateixa idea que a la Sessió 8, però ara amb MEMÒRIA pròpia de fase.
    En lloc de generate(duration) -> tot l'array d'un cop,
    process(n_samples) -> un bloc, recordant on s'havia quedat.

    Aquest és el patró "UGen" (unit generator): una interfície comuna
    que qualsevol peça d'un sintetitzador modular pot implementar.
    Connexió amb Max/Pd: és exactament com pensar en un patch — cada
    objecte rep/envia blocs de senyal, bloc a bloc, mantenint el seu propi estat.
    """

    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0  # ESTAT: la fase acumulada, en radians

    def process(self, n_samples):
        # increment de fase per mostra, segons la freq actual
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)

        if self.waveform == 'sine':
            out = np.sin(phases)
        elif self.waveform == 'square':
            out = np.sign(np.sin(phases))
        elif self.waveform == 'sawtooth':
            out = 2 * ((phases / (2 * np.pi)) % 1.0) - 1.0
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")

        # actualitzem la fase per a la PROPERA crida (mòdul 2π per evitar desbordaments)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


osc = Oscillator(freq=440)
bloc1 = osc.process(4410)   # 0.1s
bloc2 = osc.process(4410)   # 0.1s — continua la fase d'on l'havia deixat
junts = np.concatenate([bloc1, bloc2])

print("Ara process() recorda la fase entre crides. Compara amb l'exemple 1:")
sd.play(junts, sample_rate)
sd.wait()
print("(hauria de sonar com una ona contínua, sense click)\n")


# =================================================================
# 3. Control rate vs. audio rate: vibrato amb un LFO
# =================================================================
print("=== 3. Control rate: un LFO modulant suaument la freqüència (vibrato) ===")

# QUÈ ÉS CONTROL RATE (idea general, en un motor DSP real):
# Un generador de control (LFO, envolupant) calcula els SEUS PROPIS valors
# a una freqüència molt inferior a la d'àudio — per exemple, 100-200 valors
# per segon en lloc dels 44100/s que calen per al so que sentim. Té sentit
# perquè aquests paràmetres de control (vibrato, tremolo...) varien tan a
# poc a poc que no calen més valors que aquests per descriure'ls bé.
#
# EL NOSTRE CAS ÉS UN HÍBRID PEDAGÒGIC, no control rate "de debò":
# Per simplicitat, la classe LFO d'aquí sota REUTILITZA exactament la
# mateixa lògica que Oscillator — calcula a 44100Hz igual que el portador
# (no genera realment menys valors). El que fem és "fingir" que està a
# control rate: calculem el bloc sencer (512 mostres) i després en llegim
# només l'última (lfo_out[-1]). És una manera senzilla de mostrar el patró
# "un UGen alimenta el paràmetre d'un altre" sense haver de programar un
# generador de control real a una altra freqüència de mostreig.
#
# PER QUÈ FUNCIONA IGUALMENT (tot i ser un híbrid): com que el LFO es mou
# lent (5Hz), el seu valor amb prou feines canvia entre la primera i
# l'última mostra del bloc — per això llegir-ne només la mostra final NO
# perd informació rellevant, i sentim "la mateixa nota, ondulant" (vibrato).
# Veurem a la Secció 4 que això deixa de ser cert si el modulador es mou
# ràpid (FM): allà sí que llegir només l'última mostra perd informació real.
#
# Referència real: al Yamaha DX7 (sintetitzador FM clàssic dels 80) hi ha un
# ÚNIC LFO global que es pot enrutar com a vibrato (modula pitch) i/o tremolo
# (modula amplitud) de qualsevol operador — exactament aquesta idea.


class LFO:
    """
    HÍBRID: per simplicitat, reutilitza exactament la mateixa lògica que
    Oscillator (calcula a 44100Hz, igual que el portador). NO és un
    generador de control rate real (que calcularia menys valors per
    segon) — només "llegim" el seu resultat com si ho fos, agafant
    només l'última mostra de cada bloc (vegeu vibrato() més avall).
    """

    def __init__(self, freq=5.0, sample_rate=44100):
        self.freq = freq
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        out = np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


def vibrato(base_freq, lfo_freq, depth, duration, sample_rate=44100, block=512):
    """
    Vibrato: un LFO modula lleugerament la freqüència d'un Oscillator.
    Llegim el LFO a "control rate" (1 valor/bloc, vegeu lfo_out[-1])
    encara que per dins calculi a audio rate igual que el portador —
    és l'híbrid pedagògic explicat més amunt.
    depth = excursió en Hz, PETITA (uns pocs Hz) — la nota s'ha de sentir
    com "la mateixa nota ondulant", no com un canvi de timbre.
    """
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')

    lfo = LFO(freq=lfo_freq)
    osc = Oscillator(freq=base_freq, waveform='sine')

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        lfo_out = lfo.process(n)
        osc.freq = base_freq + depth * lfo_out[-1]   # llegim el LFO a "control rate": 1 valor/bloc
        sortida[i:i + n] = osc.process(n)
        i += n

    return sortida


print("Nota de 440Hz SENSE vibrato:")
sense_vibrato = vibrato(base_freq=440, lfo_freq=5.0, depth=0.0, duration=1.5)
sd.play(sense_vibrato, sample_rate)
sd.wait()

print("Mateixa nota AMB vibrato (LFO 5Hz, excursió de només 6Hz):")
amb_vibrato = vibrato(base_freq=440, lfo_freq=5.0, depth=6.0, duration=1.5)
sd.play(amb_vibrato, sample_rate)
sd.wait()
print("(hauries de sentir la MATEIXA nota, ondulant suaument — no un timbre nou)\n")


# =================================================================
# 4. FM synthesis: UGens encadenats, però a AUDIO RATE (no control rate)
# =================================================================
print("=== 4. FM synthesis: un UGen alimenta el paràmetre d'un altre ===")

# Diferència de fons amb el vibrato de la Secció 3 (no és només una qüestió
# de com sona): la FM és, per definició, modulació a AUDIO RATE — el
# modulador es mou a una freqüència pròpia del rang audible, no de control.
# Si llegíssim aquest modulador només un cop per bloc (com fem aquí, per
# simplicitat), ESTEM SOTA-MOSTREJANT-LO: introduïm artefactes/aliasing
# perquè el modulador canvia massa ràpid per a la resolució amb què
# l'actualitzem. És exactament la mateixa raó per la qual el vibrato SÍ pot
# llegir's a baixa resolució sense problemes: allà el modulador es mou prou
# lent perquè 1 valor/bloc sigui suficient.
#
# El patró de codi és el mateix que el vibrato (un process() alimenta un
# paràmetre d'un altre UGen) — la diferència és la freqüència del modulador
# i si llegir-lo a baixa resolució (1 valor/bloc) perd informació rellevant:
#   - Vibrato (Secció 3): modulador lent  -> 1 valor/bloc no perd res perceptible
#   - FM (aquí):           modulador ràpid -> 1 valor/bloc ja perd informació (sota-mostreig)
#
# NOTA: cap dels dos casos estalvia CPU pel fet de llegir només [-1] — en
# tots dos calculem el bloc sencer del modulador igualment. L'estalvi de
# processar en blocs (en lloc de mostra a mostra) és un tema diferent,
# que ja apliquem des de la Secció 2 i que es quantifica a la Sessió 10.
#
# I = índex de modulació: quanta excursió en Hz provoca el modulador sobre
# el portador. Notació estàndard (Chowning, DX7): I, no beta.

carrier_freq = 440.0
mod_freq = 80.0      # Hz — ja dins el rang audible, no és control rate
I = 200.0            # índex de modulació, en Hz d'excursió

modulator = Oscillator(freq=mod_freq, waveform='sine')
carrier = Oscillator(freq=carrier_freq, waveform='sine')

n_total = int(sample_rate * 2.0)
block = 512
sortida = np.zeros(n_total, dtype='float32')

i = 0
while i < n_total:
    n = min(block, n_total - i)

    mod_out = modulator.process(n)            # -1..1
    carrier.freq = carrier_freq + I * mod_out[-1]  # actualitzem freq del portador
    sortida[i:i + n] = carrier.process(n)

    i += n

print(f"FM: portador {carrier_freq}Hz modulat per {mod_freq}Hz amb I={I}Hz")
print("(IMPORTANT: actualitzem carrier.freq un cop per bloc de 512 mostres,")
print(" no mostra a mostra. Com que el modulador es mou a audio rate, això")
print(" introdueix artefactes/aliasing — és una simplificació pràctica per")
print(" sentir l'efecte, NO l'FM matemàticament correcta. El 'veritable' FM")
print(" mostra a mostra es proposa com a Challenge opcional.)")
sd.play(sortida, sample_rate)
sd.wait()
print()

# Prova també amb I encara més gran per accentuar el canvi de timbre:
I_alt = 500.0
modulator2 = Oscillator(freq=mod_freq, waveform='sine')
carrier2 = Oscillator(freq=carrier_freq, waveform='sine')
sortida2 = np.zeros(n_total, dtype='float32')
i = 0
while i < n_total:
    n = min(block, n_total - i)
    mod_out = modulator2.process(n)
    carrier2.freq = carrier_freq + I_alt * mod_out[-1]
    sortida2[i:i + n] = carrier2.process(n)
    i += n

print(f"Mateixa FM amb I={I_alt}Hz (encara més 'metàl·lic'):")
sd.play(sortida2, sample_rate)
sd.wait()
print()


# =================================================================
# 5. Envelope, també com a UGen (recordatori ràpid de S8 + petit ajust)
# =================================================================
print("=== 5. Envelope amb process(), per encaixar amb la resta ===")


class Envelope:
    """
    Mateixa idea ADSR de la Sessió 8, però servida bloc a bloc amb process()
    perquè pugui viure dins el mateix callback en temps real que l'Oscillator.
    note_on() inicia Attack; note_off() inicia Release.
    """

    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sample_rate=44100):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.sample_rate = sample_rate

        self.stage = 'idle'   # 'idle' | 'attack' | 'decay' | 'sustain' | 'release'
        self.level = 0.0
        self.stage_samples = 0  # mostres transcorregudes dins l'stage actual

    def note_on(self):
        self.stage = 'attack'
        self.stage_samples = 0

    def note_off(self):
        self.stage = 'release'
        self.stage_samples = 0
        self._release_start_level = self.level

    def process(self, n_samples):
        out = np.zeros(n_samples)
        for k in range(n_samples):
            if self.stage == 'attack':
                n_attack = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / n_attack)
                if self.stage_samples >= n_attack:
                    self.stage = 'decay'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'decay':
                n_decay = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / n_decay)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= n_decay:
                    self.stage = 'sustain'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'sustain':
                self.level = self.sustain
            elif self.stage == 'release':
                n_release = max(1, int(self.release * self.sample_rate))
                t = min(1.0, self.stage_samples / n_release)
                self.level = self._release_start_level * (1.0 - t)
                if self.stage_samples >= n_release:
                    self.stage = 'idle'
                    self.level = 0.0
            else:  # idle
                self.level = 0.0

            out[k] = self.level
            self.stage_samples += 1

        return out


print("Envelope ara és un UGen més: note_on()/note_off() canvien el seu")
print("estat intern, i process(n) ret torna el tros de corba corresponent.\n")


# =================================================================
# 6. Integració: callback temps real + MIDI (teclat connectat)
# =================================================================
print("=== 6. Integració temps real + MIDI ===")
print("Requereix un controlador MIDI connectat (USB/Bluetooth) i 'mido'.")
print("Si no en tens, salta a la Secció 6b (simulació).\n")

resposta = input("Tens un teclat MIDI connectat i vols provar-ho? (s/n): ")

if resposta.strip().lower() == 's':
    import mido

    print("Ports MIDI disponibles:", mido.get_input_names())
    port_name = mido.get_input_names()[0]  # ajusta l'índex si cal
    print(f"Obrint: {port_name}")

    def note_to_freq(note_number):
        return 440.0 * (2 ** ((note_number - 69) / 12))

    synth_osc = Oscillator(freq=440, waveform='sawtooth')
    synth_env = Envelope(attack=0.01, decay=0.08, sustain=0.6, release=0.3)

    def synth_callback(outdata, frames, time, status):
        if status:
            print(status)
        wave = synth_osc.process(frames)
        env_curve = synth_env.process(frames)
        outdata[:, 0] = (wave * env_curve).astype('float32')

    with mido.open_input(port_name) as inport:
        with sd.OutputStream(samplerate=sample_rate, blocksize=512,
                              channels=1, dtype='float32', callback=synth_callback):
            print("Toca el teclat — Ctrl+C per aturar.")
            try:
                for msg in inport:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        synth_osc.freq = note_to_freq(msg.note)
                        synth_env.note_on()
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        synth_env.note_off()
            except KeyboardInterrupt:
                pass

else:
    # ---------------------------------------------------------------
    # 6b. Simulació sense teclat: una seqüència de notes "fake MIDI"
    # ---------------------------------------------------------------
    print("\n=== 6b. Simulació: note_on/note_off programats ===")
    print("Mateix callback que amb un teclat real, però les notes")
    print("arriben des d'una llista en lloc d'un port MIDI físic.\n")

    def note_to_freq(note_number):
        return 440.0 * (2 ** ((note_number - 69) / 12))

    synth_osc = Oscillator(freq=440, waveform='sawtooth')
    synth_env = Envelope(attack=0.01, decay=0.08, sustain=0.6, release=0.3)

    def synth_callback(outdata, frames, time, status):
        if status:
            print(status)
        wave = synth_osc.process(frames)
        env_curve = synth_env.process(frames)
        outdata[:, 0] = (wave * env_curve).astype('float32')

    # seqüència: (nota_midi, moment_note_on, moment_note_off) en segons
    sequencia = [
        (60, 0.0, 0.4),
        (64, 0.5, 0.9),
        (67, 1.0, 1.4),
        (72, 1.5, 2.2),
    ]

    import time as time_module

    with sd.OutputStream(samplerate=sample_rate, blocksize=512,
                          channels=1, dtype='float32', callback=synth_callback):
        t_inici = time_module.perf_counter()
        events_fets = set()
        durada_total = max(off for (_, _, off) in sequencia) + 0.5

        while time_module.perf_counter() - t_inici < durada_total:
            t_actual = time_module.perf_counter() - t_inici
            for idx, (note, t_on, t_off) in enumerate(sequencia):
                if (idx, 'on') not in events_fets and t_actual >= t_on:
                    synth_osc.freq = note_to_freq(note)
                    synth_env.note_on()
                    events_fets.add((idx, 'on'))
                if (idx, 'off') not in events_fets and t_actual >= t_off:
                    synth_env.note_off()
                    events_fets.add((idx, 'off'))
            sd.sleep(10)

    print("Seqüència acabada. Aquesta és exactament l'estructura que faries")
    print("servir amb un teclat MIDI real: només canvia D'ON arriben note_on/note_off.\n")


# =================================================================
# 7. Tast de signalflow (10 min, NO exercici — només per veure-ho)
# =================================================================
print("=== 7. Tast de signalflow: mateixa idea, fet 'professionalment' ===")
print("""
signalflow és una llibreria de síntesi en temps real per a Python que ja
implementa l'arquetip UGen de manera optimitzada (en C++ per sota, i a
audio rate de veritat — sense l'aliasing de la nostra simplificació
per blocs de la Secció 4). A diferència del que hem fet a mà, distingeix
oscil·ladors d'àudio (Oscillator) de LFOs (LFO) com a CLASSES SEPARADES
— exactament la distinció control/audio rate que hem treballat avui.

NO cal instal·lar-la ni executar-la avui — només mira el codi
(API real, documentació a https://signalflow.dev/):

    from signalflow import *

    graph = AudioGraph()

    I = 200                                      # índex de modulació (Hz)
    modulator = SineOscillator(80) * I            # el nostre 'modulator'
    carrier = SineOscillator(440 + modulator)     # FM en UNA línia!
    carrier.play()

    graph.wait()

Compara-ho amb el bucle manual de la Secció 4: la IDEA és la mateixa
(un node alimenta el paràmetre d'un altre, amb el mateix índex de
modulació I — passar la sortida d'un node com a input d'un altre es
diu "input audio-rate" en signalflow), però ho fa mostra a mostra de
veritat, en temps real, sense que nosaltres gestionem el bucle de
blocs ni assumim el compromís d'actualitzar la freqüència només un
cop per bloc.

Si vols instal·lar-la i provar-ho de debò: Challenge opcional
(recursos/challenges.md). Funciona correctament en Mac Apple Silicon
(M1/M2/M3) — a diferència d'altres llibreries de síntesi més antigues.
""")

print("=== Fi de la demo ===")
