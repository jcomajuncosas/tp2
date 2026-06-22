"""
Assignment — Bloc 5b, Sessió 9 (Thonny)
Mini-repte: dues funcions curtes, dos rols ben diferenciats

IMPORTANT: aquesta sessió és densa — el repte és intencionadament CURT.
Completa les funcions marcades amb TODO. Cada una té el seu autotest:
si l'autotest passa (✅), aquella part ja és correcta.

Les dues funcions fan servir EL MATEIX PATRÓ de codi (un UGen alimenta
un paràmetre d'un altre via process()), però amb una intenció sonora
oposada — això és la idea central a interioritzar avui:

  - vibrato():   control rate — depth PETIT, modulador lent, 1 valor/bloc
                 n'hi ha prou sense artefactes (com el LFO del DX7 enrutat
                 a pitch)
  - fm_synth():  audio rate — I (índex de modulació) GRAN, modulador ràpid;
                 actualitzar-lo només 1 cop/bloc ja és una simplificació
                 amb artefactes coneguts (veure docstring)

NO cal tocar res fora de les zones marcades amb TODO.
"""

import numpy as np

sample_rate = 44100


# =================================================================
# Classe ja donada: Oscillator amb process() (igual que a exemples.py)
# =================================================================
class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n_samples):
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

        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


# =================================================================
# TODO 1: completa vibrato()
# =================================================================
def vibrato(base_freq, lfo_freq, depth, duration, sample_rate=44100, block=512):
    """
    Genera una nota amb VIBRATO: un Oscillator fent de LFO (control rate,
    freq baixa) modula lleugerament la freqüència d'un altre Oscillator
    (audio rate, el que realment sentim).

    IMPORTANT: 'depth' ha de ser PETIT (uns pocs Hz). Si 'depth' és gran,
    deixa de sonar a vibrato i passa a sonar a FM tímbrica — exactament
    la diferència que explorem amb fm_synth() més avall.

    Patró (igual que a exemples.py, Secció 3):
      1. crea 'lfo' (Oscillator amb freq=lfo_freq)
      2. crea 'osc' (Oscillator amb freq=base_freq)
      3. en un bucle per blocs de mida 'block':
         - genera un bloc del lfo amb process()
         - actualitza osc.freq = base_freq + depth * (últim valor del bloc del lfo)
         - genera el bloc de l'osc amb process() i desa'l a la sortida

    Retorna: array NumPy de longitud int(sample_rate * duration)
    """
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')

    # TODO: crea aquí 'lfo' i 'osc' (dos Oscillator)
    lfo = None  # <-- substitueix
    osc = None  # <-- substitueix

    i = 0
    while i < n_total:
        n = min(block, n_total - i)

        # TODO: genera el bloc del lfo, actualitza osc.freq,
        #       genera el bloc de l'osc i desa'l a sortida[i:i+n]
        pass  # <-- substitueix per les 3 línies necessàries

        i += n

    return sortida


# =================================================================
# TODO 2: completa fm_synth()
# =================================================================
def fm_synth(carrier_freq, mod_freq, I, duration, sample_rate=44100, block=512):
    """
    Genera 'duration' segons de so amb FM synthesis (timbre, NO vibrato):
    DOS Oscillator (modulador i portador) encadenats amb process().

    IMPORTANT: aquí el modulador es mou a freqüència d'àudio (mod_freq
    alta), no de control. Actualitzar carrier.freq només 1 cop/bloc (com
    fem aquí, per simplicitat) és una sota-mostreig del modulador — genera
    artefactes/aliasing. És una simplificació pràctica per sentir l'efecte,
    NO l'FM matemàticament correcta (això és Challenge opcional).
    I = índex de modulació (notació estàndard, Chowning/DX7), GRAN
    (desenes/centenars de Hz) — el timbre resultant ja no es reconeix com
    "una nota que ondula".

    Patró (igual que a exemples.py, Secció 4):
      1. crea 'modulator' (Oscillator amb freq=mod_freq)
      2. crea 'carrier' (Oscillator amb freq=carrier_freq)
      3. en un bucle per blocs de mida 'block':
         - genera un bloc del modulador amb process()
         - actualitza carrier.freq = carrier_freq + I * (últim valor del bloc del modulador)
         - genera el bloc del portador amb process() i desa'l a la sortida

    Retorna: array NumPy de longitud int(sample_rate * duration)
    """
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')

    # TODO: crea aquí 'modulator' i 'carrier' (dos Oscillator)
    modulator = None  # <-- substitueix
    carrier = None    # <-- substitueix

    i = 0
    while i < n_total:
        n = min(block, n_total - i)

        # TODO: genera el bloc del modulador, actualitza carrier.freq,
        #       genera el bloc del portador i desa'l a sortida[i:i+n]
        #       (fes servir 'I' com a nom del paràmetre d'excursió)
        pass  # <-- substitueix per les 3 línies necessàries

        i += n

    return sortida


# =================================================================
# Autotests — NO modificar
# =================================================================
def _test_vibrato():
    print("Test 1: vibrato()...")
    out = vibrato(base_freq=440, lfo_freq=5, depth=6, duration=0.5)

    assert out is not None, "❌ vibrato() no retorna res"
    assert isinstance(out, np.ndarray), "❌ vibrato() ha de retornar un array NumPy"

    n_esperat = int(44100 * 0.5)
    assert len(out) == n_esperat, f"❌ Longitud incorrecta: {len(out)}, esperat {n_esperat}"

    assert np.max(np.abs(out)) <= 1.0 + 1e-6, "❌ La sortida supera el rang [-1, 1]"
    assert not np.any(np.isnan(out)), "❌ La sortida conté NaN"
    assert np.max(np.abs(out)) > 0.5, "❌ La sortida sembla silenciosa — revisa que escrius a 'sortida'"

    out_sense_vibrato = vibrato(base_freq=440, lfo_freq=5, depth=0, duration=0.5)
    diff = np.max(np.abs(out - out_sense_vibrato))
    assert diff > 0.01, "❌ Amb depth=6 i depth=0 el resultat hauria de ser diferent — revisa que actualitzes osc.freq"

    print("✅ vibrato() correcte\n")


def _test_fm_synth():
    print("Test 2: fm_synth()...")
    out = fm_synth(carrier_freq=440, mod_freq=80, I=200, duration=0.5)

    assert out is not None, "❌ fm_synth() no retorna res"
    assert isinstance(out, np.ndarray), "❌ fm_synth() ha de retornar un array NumPy"

    n_esperat = int(44100 * 0.5)
    assert len(out) == n_esperat, f"❌ Longitud incorrecta: {len(out)}, esperat {n_esperat}"

    assert np.max(np.abs(out)) <= 1.0 + 1e-6, "❌ La sortida supera el rang [-1, 1]"
    assert not np.any(np.isnan(out)), "❌ La sortida conté NaN"
    assert np.max(np.abs(out)) > 0.5, "❌ La sortida sembla silenciosa — revisa que escrius a 'sortida'"

    # comprovem que el carrier realment varia de freqüència (FM real, no fix)
    out_sense_mod = fm_synth(carrier_freq=440, mod_freq=80, I=0, duration=0.5)
    diff = np.max(np.abs(out - out_sense_mod))
    assert diff > 0.01, "❌ Amb I=200 i I=0 el resultat hauria de ser molt diferent — revisa que actualitzes carrier.freq"

    print("✅ fm_synth() correcte\n")


def _test_vibrato_vs_fm_son_diferents():
    print("Test 3: vibrato i FM han de sonar de manera clarament diferent...")

    def amplada_de_banda(signal, sample_rate=44100, threshold_db=-20):
        spec = np.abs(np.fft.rfft(signal))
        spec_db = 20 * np.log10(spec / np.max(spec) + 1e-12)
        freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)
        mask = spec_db > threshold_db
        return freqs[mask].max() - freqs[mask].min() if np.any(mask) else 0

    v = vibrato(base_freq=440, lfo_freq=5, depth=6, duration=1.0)
    fm = fm_synth(carrier_freq=440, mod_freq=80, I=200, duration=1.0)

    bw_v = amplada_de_banda(v)
    bw_fm = amplada_de_banda(fm)

    print(f"   Amplada de banda vibrato: {bw_v:.0f}Hz | FM: {bw_fm:.0f}Hz")
    assert bw_fm > bw_v * 3, (
        "❌ La FM hauria d'ocupar molta més amplada de banda que el vibrato "
        "(timbre nou vs. nota que ondula) — revisa els paràmetres per defecte"
    )

    print("✅ vibrato (control) i FM (timbre) són clarament diferents\n")


if __name__ == "__main__":
    print("=== Executant autotests ===\n")
    _test_vibrato()
    _test_fm_synth()
    _test_vibrato_vs_fm_son_diferents()
    print("=== Tots els autotests passen! ===\n")

    print("Si vols escoltar el resultat, descomenta les línies següents")
    print("(requereix sounddevice i hardware d'àudio — no funciona a Colab):\n")
    print("# import sounddevice as sd")
    print("# v = vibrato(base_freq=440, lfo_freq=5, depth=6, duration=2.0)")
    print("# sd.play(v, sample_rate); sd.wait()")
    print("#")
    print("# fm = fm_synth(carrier_freq=440, mod_freq=80, I=200, duration=2.0)")
    print("# sd.play(fm, sample_rate); sd.wait()")
