"""
Assignment — Bloc 5c, Sessió 10 (Thonny)
Repte de consolidació: kit de percussió sintètica, disparat per MIDI

Combina TOT el que heu après al Bloc 5:
  - Oscillator (S8) amb process() (S9) per al kick
  - Noise (nova, trivial — sense estat) per al hi-hat
  - Envelope (S8/S9) per donar forma temporal als dos sons
  - Integració amb MIDI temps real (S9): note_on/note_off disparen els sons

Completa les funcions/mètodes marcats amb TODO. Cada un té el seu
autotest: si l'autotest passa (✅), aquella part ja és correcta.

NO cal tocar res fora de les zones marcades amb TODO.
"""

import numpy as np

sample_rate = 44100


# =================================================================
# Classes ja donades (de S8/S9) — NO cal tocar-les
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
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sample_rate=44100):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.sample_rate = sample_rate
        self.stage = 'idle'
        self.level = 0.0
        self.stage_samples = 0

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
                n_a = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / n_a)
                if self.stage_samples >= n_a:
                    self.stage = 'decay'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'decay':
                n_d = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / n_d)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= n_d:
                    self.stage = 'sustain'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'sustain':
                self.level = self.sustain
                if self.sustain == 0.0:
                    self.stage = 'idle'
            elif self.stage == 'release':
                n_r = max(1, int(self.release * self.sample_rate))
                t = min(1.0, self.stage_samples / n_r)
                self.level = self._release_start_level * (1.0 - t)
                if self.stage_samples >= n_r:
                    self.stage = 'idle'
                    self.level = 0.0
            else:
                self.level = 0.0
            out[k] = self.level
            self.stage_samples += 1
        return out


# =================================================================
# TODO 1: completa la classe Noise
# =================================================================
class Noise:
    """
    UGen MÉS SENZILL que heu vist: no té estat (no hi ha self.phase
    ni res que calgui recordar entre crides). Cada process(n) retorna
    n mostres de soroll blanc, entre -1 i 1.
    """

    def process(self, n_samples):
        # TODO: retorna un array de n_samples mostres de soroll blanc,
        #       cada mostra entre -1.0 i 1.0 (np.random.uniform)
        pass  # <-- substitueix


# =================================================================
# TODO 2: completa la classe Kick
# =================================================================
class Kick:
    """
    Oscillator amb 'pitch-drop': la freqüència baixa ràpidament de
    freq_start a freq_end durant els primers drop_time segons. És el
    truc clàssic per sintetitzar un bombo amb un sol oscil·lador.

    Ja tens self.osc (un Oscillator normal) creat a __init__.
    NOMÉS cal completar process(): calcular la freqüència que toca
    en aquest punt del so, assignar-la a self.osc.freq, i cridar
    self.osc.process(n_samples).
    """

    def __init__(self, freq_start=150.0, freq_end=40.0, drop_time=0.05, sample_rate=44100):
        self.freq_start = freq_start
        self.freq_end = freq_end
        self.drop_time = drop_time
        self.sample_rate = sample_rate
        self.osc = Oscillator(freq=freq_start, waveform='sine', sample_rate=sample_rate)
        self.elapsed = 0.0

    def reset(self):
        self.elapsed = 0.0
        self.osc.freq = self.freq_start
        self.osc.phase = 0.0

    def process(self, n_samples):
        n_drop = max(1, int(self.drop_time * self.sample_rate))
        block_t = np.arange(n_samples) + (self.elapsed * self.sample_rate)
        progress = np.clip(block_t / n_drop, 0, 1)

        # TODO: calcula 'freqs' (array, una freq per mostra del bloc) amb
        #       una corba que comenci a self.freq_start i s'acosti a
        #       self.freq_end de manera exponencial, en funció de 'progress'
        #       (progress va de 0 a 1). Pista: és igual a la fórmula que
        #       has vist a exemples.py:
        #       freq_end + (freq_start - freq_end) * exp(-5 * progress)
        freqs = None  # <-- substitueix

        self.osc.freq = float(freqs[-1])  # simplificació: freq del final del bloc
        out = self.osc.process(n_samples)
        self.elapsed += n_samples / self.sample_rate
        return out


# =================================================================
# TODO 3: completa percussion_kit()
# =================================================================
def percussion_kit(events, total_duration, sample_rate=44100, block=512):
    """
    Renderitza una seqüència de notes de percussió a un array d'àudio.

    events: llista de tuples (note, t_on) en segons. NOTA MIDI:
        36 (C1, Kick GM)         -> sona el Kick
        42 (F#1, Closed Hi-Hat)  -> sona el Hi-hat (Noise)
        qualsevol altra nota     -> s'ignora

    Cada event dispara note_on() de l'envolvent corresponent (Kick o
    Hi-hat) en el moment t_on; no cal note_off() explícit perquè les
    envolvents de percussió no tenen sustain (es self-apaguen soles).

    Retorna: array NumPy de longitud int(sample_rate * total_duration)
    """
    n_total = int(sample_rate * total_duration)
    sortida = np.zeros(n_total, dtype='float32')

    kick = Kick()
    kick_env = Envelope(attack=0.002, decay=0.15, sustain=0.0, release=0.01, sample_rate=sample_rate)

    noise = Noise()
    hh_env = Envelope(attack=0.001, decay=0.05, sustain=0.0, release=0.005, sample_rate=sample_rate)

    events_fets = set()

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        t_actual = i / sample_rate

        # TODO: per a cada event (note, t_on) a 'events' encara no disparat,
        #       si t_actual >= t_on:
        #         - si note == 36: kick.reset(); kick_env.note_on()
        #         - si note == 42: hh_env.note_on()
        #         - marca l'event com a fet (events_fets.add(...))
        #       Pots iterar amb: for idx, (note, t_on) in enumerate(events):
        pass  # <-- substitueix

        kick_wave = kick.process(n) * kick_env.process(n)
        hh_wave = noise.process(n) * hh_env.process(n)
        sortida[i:i + n] = kick_wave + hh_wave

        i += n

    return np.clip(sortida, -1.0, 1.0)


# =================================================================
# Autotests — NO modificar
# =================================================================
def _test_noise():
    print("Test 1: Noise...")
    noise = Noise()
    out = noise.process(1000)

    assert out is not None, "❌ Noise.process() no retorna res"
    assert isinstance(out, np.ndarray), "❌ ha de retornar un array NumPy"
    assert out.shape == (1000,), f"❌ Longitud incorrecta: {out.shape}"
    assert np.max(np.abs(out)) <= 1.0 + 1e-6, "❌ La sortida supera el rang [-1, 1]"

    out2 = noise.process(1000)
    assert not np.array_equal(out, out2), "❌ Dues crides haurien de donar soroll diferent (random)"

    assert abs(out.mean()) < 0.15, "❌ La mitjana hauria de ser propera a 0 (soroll blanc)"

    print("✅ Noise correcte\n")


def _test_kick():
    print("Test 2: Kick...")
    kick = Kick(freq_start=150, freq_end=40, drop_time=0.05)

    block = 512
    n_total = int(44100 * 0.3)
    sortida = np.zeros(n_total)
    freqs_log = []
    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        sortida[i:i + n] = kick.process(n)
        freqs_log.append(kick.osc.freq)
        i += n

    assert not np.any(np.isnan(sortida)), "❌ La sortida conté NaN — revisa el càlcul de 'freqs'"
    assert np.max(np.abs(sortida)) <= 1.0 + 1e-6, "❌ La sortida supera el rang [-1, 1]"

    assert freqs_log[0] > freqs_log[-1], "❌ La freqüència hauria de BAIXAR amb el temps (pitch-drop)"
    assert abs(freqs_log[-1] - 40) < 10, "❌ La freqüència final hauria d'acostar-se a freq_end=40Hz"
    assert freqs_log[0] < 150 + 1e-6, "❌ La freqüència inicial no hauria de superar freq_start"

    print(f"   (freq primer bloc: {freqs_log[0]:.1f}Hz, freq últim bloc: {freqs_log[-1]:.1f}Hz)")
    print("✅ Kick correcte\n")


def _test_percussion_kit():
    print("Test 3: percussion_kit()...")
    events = [(36, 0.0), (42, 0.2), (36, 0.4)]
    out = percussion_kit(events, total_duration=0.8)

    assert out is not None, "❌ percussion_kit() no retorna res"
    assert isinstance(out, np.ndarray), "❌ ha de retornar un array NumPy"

    n_esperat = int(44100 * 0.8)
    assert len(out) == n_esperat, f"❌ Longitud incorrecta: {len(out)}, esperat {n_esperat}"

    assert np.max(np.abs(out)) <= 1.0 + 1e-6, "❌ La sortida supera el rang [-1, 1]"
    assert not np.any(np.isnan(out)), "❌ La sortida conté NaN"

    # comprovem que hi ha senyal real prop de cada event (no tot silenci)
    sr = 44100
    for note, t_on in events:
        idx_start = int(t_on * sr)
        idx_end = min(len(out), idx_start + int(0.05 * sr))
        tros = out[idx_start:idx_end]
        assert np.max(np.abs(tros)) > 0.05, (
            f"❌ No hi ha senyal audible prop de l'event (nota={note}, t={t_on}s) "
            "— revisa que disparis note_on() en el moment correcte"
        )

def _test_percussion_kit_timing():
    print("Test 4: percussion_kit() — timing correcte (cap so abans d'hora)...")
    # Només un event, tard (t=0.5), perquè sigui inequívoc: NO hi pot
    # haver cap senyal audible abans d'aquest instant.
    events = [(36, 0.5)]
    out = percussion_kit(events, total_duration=0.8)

    sr = 44100
    abans = out[:int(0.48 * sr)]  # marge de seguretat de 20ms abans de l'event
    despres = out[int(0.5 * sr):int(0.5 * sr) + int(0.05 * sr)]

    assert np.max(np.abs(abans)) < 0.05, (
        "❌ Hi ha so abans que comenci l'event — revisa la condició t_actual >= t_on"
    )
    assert np.max(np.abs(despres)) > 0.05, (
        "❌ No hi ha so just després de l'event — revisa que disparis note_on()"
    )

    print("✅ Timing correcte: el so només comença quan toca\n")

    print("✅ percussion_kit() correcte\n")


if __name__ == "__main__":
    print("=== Executant autotests ===\n")
    _test_noise()
    _test_kick()
    _test_percussion_kit()
    _test_percussion_kit_timing()
    print("=== Tots els autotests passen! ===\n")

    print("Si vols escoltar el resultat, descomenta les línies següents")
    print("(requereix sounddevice i hardware d'àudio — no funciona a Colab):\n")
    print("# import sounddevice as sd")
    print("# events = [(36, 0.0), (42, 0.3), (36, 0.6), (42, 0.9), (36, 1.0), (42, 1.2)]")
    print("# ritme = percussion_kit(events, total_duration=1.6)")
    print("# sd.play(ritme, sample_rate); sd.wait()")
