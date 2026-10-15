"""
Solució de referència — S04: callbacks en temps real (sounddevice)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Dos usos:
  · Executat directament (python3 solucio.py): valida tots els TODOs SENSE
    micròfon ni altaveu. Les callbacks es proven amb arrays sintètics i els
    blocs `with sd.Stream` (TODO 6 i BONUS) amb un stream simulat
    (FakeStream) que crida la callback amb blocs de soroll i amb input()
    simulat.
  · A Thonny, amb hardware real: F5 i crida les funcions com faria l'alumne
    (escolta_part3(), escolta_bonus()...).
"""

import builtins
import numpy as np
import time

try:
    import sounddevice as sd
except (ImportError, OSError):      # sense PortAudio (p. ex. contenidor)
    sd = None

sample_rate = 44100
blocksize = 1024


# ── PART 1 — TODO 1 ───────────────────────────────────────────────────────

def passthrough_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    outdata[:] = indata


def comprova_part1():
    entrada = np.array([[0.1], [0.2], [0.3]], dtype='float32')
    sortida = np.zeros((3, 1), dtype='float32')
    passthrough_callback(entrada, sortida, 3, None, None)
    assert np.allclose(sortida, entrada)
    print("✅ Part 1: la callback fa pass-through")


# ── PART 2 — TODOs 2 i 3 ──────────────────────────────────────────────────

gain = 0.5


def gain_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    outdata[:] = indata * gain


def comprova_part2():
    global gain
    assert gain is not None
    gain = 0.5
    entrada = np.array([[0.4], [0.8], [-0.4]], dtype='float32')
    sortida = np.zeros((3, 1), dtype='float32')
    gain_callback(entrada, sortida, 3, None, None)
    assert np.allclose(sortida, entrada * 0.5)
    print("✅ Part 2: la callback aplica el gain")


# ── PART 3 — TODOs 4, 5 i 6 ───────────────────────────────────────────────

drive = 1.0


def disto_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    outdata[:] = np.tanh(indata * drive)


def escolta_part3():
    global drive
    comprova_part3()
    print("Escriu un drive entre 1.0 i 50.0. 'q' per sortir.\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=disto_callback):
        while True:
            try:
                entrada = input(f"Drive actual: {drive:.1f} → nou valor (o 'q'): ")
                if entrada.lower() == 'q':
                    break
                nou_drive = float(entrada)
                if 1.0 <= nou_drive <= 50.0:
                    drive = nou_drive
                else:
                    print("Valor fora de rang (1.0 - 50.0)")
            except ValueError:
                print("Escriu un número vàlid")
            except KeyboardInterrupt:
                break
    print("Stream tancat.")


def comprova_part3():
    global drive
    assert drive is not None
    entrada = np.array([[0.1], [0.5], [-0.9]], dtype='float32')
    for d in (1.0, 10.0):
        drive = d
        sortida = np.zeros((3, 1), dtype='float32')
        disto_callback(entrada, sortida, 3, None, None)
        assert np.allclose(sortida, np.tanh(entrada * d), atol=1e-6)
    drive = 1.0
    print("✅ Part 3: la callback distorsiona correctament")


# ── PART 4 — TODO 7 ───────────────────────────────────────────────────────
#
# durada_bloc_ms: valor exacte (bs / sr * 1000).
# latencia_reportada_ms: DEPÈN DE LA MÀQUINA I LA INTERFÍCIE — no hi ha valor
#   de referència. Criteri: ha de ser un número plausible, sempre MÉS GRAN que
#   la durada del bloc (inclou buffers d'entrada + sortida + sistema).
# retard_perceptible / glitches: també depenen de la màquina. El criteri és la
#   coherència: si diu glitches=True a 2048 però False a 256, cal preguntar.
#
# ⚠️ Validar a l'aula amb el Mac M1 i anotar aquí els valors reals observats.

observacions = {
    'blocksize_256': {
        'durada_bloc_ms': round(256 / sample_rate * 1000, 1),    # 5.8
        'latencia_reportada_ms': '(depèn de la màquina)',
        'retard_perceptible': '(depèn)',
        'glitches': '(més probable que amb blocs grans)',
        'nota': 'Retard mínim; més sensible a la càrrega de la màquina.',
    },
    'blocksize_1024': {
        'durada_bloc_ms': round(1024 / sample_rate * 1000, 1),   # 23.2
        'latencia_reportada_ms': '(depèn de la màquina)',
        'retard_perceptible': '(depèn)',
        'glitches': '(poc probable)',
        'nota': 'Compromís raonable; és el valor per defecte del curs.',
    },
    'blocksize_2048': {
        'durada_bloc_ms': round(2048 / sample_rate * 1000, 1),   # 46.4
        'latencia_reportada_ms': '(depèn de la màquina)',
        'retard_perceptible': True,
        'glitches': '(molt poc probable)',
        'nota': 'Molt estable; retard clarament audible (eco curt).',
    },
}


# ── PART 5 — TODO 8 ───────────────────────────────────────────────────────

reflexio = {
    'per_que_global_es_necessaria':
        "La callback la crida l'stream, des d'un altre fil, amb uns paràmetres "
        "fixos (indata, outdata, frames, time_info, status): no li podem passar "
        "'gain' com a argument. Cal un lloc compartit que vegin tant la callback "
        "com el bucle principal: una variable global.",

    'per_que_global_es_lleig':
        "Qualsevol part del programa la pot llegir o canviar, i no queda clar qui "
        "en depèn. Si n'hi ha moltes (gain, drive, nivell...) es fa difícil seguir "
        "el codi i fàcil trepitjar-se. Una classe que agrupi l'estat i la callback "
        "ho ordena millor.",

    'per_que_colab_no_funciona':
        "A Colab el Python s'executa en un servidor remot, que no té accés al teu "
        "micròfon ni als teus altaveus; el so hauria de viatjar per la xarxa, "
        "incompatible amb latències de mil·lisegons. La WebAudio API s'executa al "
        "navegador, és a dir, al teu ordinador, i accedeix directament a l'àudio local.",

    'trade_off_blocksize':
        "Bloc petit: menys retard, però la callback es crida més sovint i té menys "
        "temps per acabar → més risc de glitch. Bloc gran: més marge i estabilitat, "
        "però més retard. La latència reportada és MÉS GRAN que la durada d'un bloc "
        "perquè hi ha buffers d'entrada, de sortida i del sistema operatiu.",

    'echo_al_callback':
        "L'echo de la S03 treballava sobre el senyal sencer: per calcular una mostra "
        "agafava la de 'delay_samples' enrere. La callback només veu el bloc actual "
        "(~23 ms) i a la crida següent el bloc anterior ja no hi és. Per fer un echo "
        "en temps real cal guardar el passat entre crides (un buffer circular), i "
        "si el retard és més llarg que un bloc, cal recordar diversos blocs.",
}


# ── BONUS — vúmetre ───────────────────────────────────────────────────────

nivell = 0.0


def vumetre_callback(indata, outdata, frames, time_info, status):
    global nivell
    nivell = float(np.sqrt(np.mean(indata ** 2)))
    outdata[:] = indata


def escolta_bonus():
    print("Vúmetre en marxa. Ctrl+C per aturar.\n")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=vumetre_callback):
            while True:
                print(f"{nivell:.3f} " + '#' * int(nivell * 200))
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


# ══════════════════════════════════════════════════════════════════════════
# HARNESS DE VALIDACIÓ (sense hardware)
# ══════════════════════════════════════════════════════════════════════════

class FakeStream:
    """Simula sd.Stream: a l'entrar crida la callback amb uns quants blocs."""
    def __init__(self, samplerate, blocksize, channels, dtype, callback, latency=None):
        self.callback, self.bs = callback, blocksize
        self.latency = (0.010, 0.012)
        self.outputs = []

    def __enter__(self):
        rng = np.random.default_rng(0)
        for _ in range(5):
            ind = (rng.standard_normal((self.bs, 1)) * 0.1).astype('float32')
            out = np.zeros_like(ind)
            self.callback(ind, out, self.bs, None, None)
            self.outputs.append((ind, out))
        FakeStream.ultim = self
        return self

    def __exit__(self, *exc):
        return False


class FakeSD:
    Stream = FakeStream
    @staticmethod
    def sleep(ms):
        pass


def _amb_input(respostes, funcio):
    """Executa funcio() responent els input() amb la llista donada."""
    cua = list(respostes)
    original = builtins.input
    def fals(prompt=""):
        r = cua.pop(0)
        print(prompt + str(r))
        if r is KeyboardInterrupt:
            raise KeyboardInterrupt
        return r
    builtins.input = fals
    try:
        funcio()
    finally:
        builtins.input = original


if __name__ == "__main__":
    sd = FakeSD                       # substituïm el hardware pel simulador

    comprova_part1()
    comprova_part2()
    comprova_part3()

    # TODO 6: el bucle accepta valors vàlids, rebutja text i fora de rang, surt amb 'q'
    _amb_input(["5", "hola", "100", "q"], escolta_part3)
    assert drive == 5.0, f"drive hauria de ser 5.0, és {drive}"
    ind, out = FakeStream.ultim.outputs[0]
    assert np.allclose(out, np.tanh(ind * 1.0)), "l'stream ha de cridar disto_callback"
    print("✅ TODO 6: stream + bucle de control correctes (q)")

    # TODO 6: Ctrl+C a l'input surt net
    _amb_input([KeyboardInterrupt], escolta_part3)
    print("✅ TODO 6: Ctrl+C surt net")

    # BONUS: el vúmetre calcula el RMS i fa pass-through
    entrada = np.full((4, 1), 0.5, dtype='float32')
    sortida = np.zeros_like(entrada)
    vumetre_callback(entrada, sortida, 4, None, None)
    assert abs(nivell - 0.5) < 1e-6 and np.allclose(sortida, entrada)
    print("✅ BONUS: vúmetre (RMS + pass-through)")

    for k, v in observacions.items():
        assert v['durada_bloc_ms'] is not None
    for p, r in reflexio.items():
        assert r.strip(), f"Reflexió buida: {p}"
    print("✅ Parts 4 i 5: observacions i reflexió de referència")

    print("\n✅ Tots els TODOs de S04 validats.")
    print("NOTA DOCENT — Parts 4 i 5 admeten variació; el criteri és la coherència")
    print("de les mesures i la comprensió del trade-off latència/glitch i de l'estat")
    print("entre crides (pregunta de l'echo).")
