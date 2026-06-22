"""
Projecte final — Rol: EFECTE ADAPTATIU
Un instrument acoblat (jack/interface d'àudio) passa per 3 efectes
simultanis, cadascun modulat contínuament per un descriptor tímbric
calculat en temps real sobre el propi senyal d'entrada.

INSTRUMENT AUTÒNOM: només processa la teva pròpia entrada — no depèn de
cap altre instrument de l'ensemble.

Requereix: numpy, sounddevice, librosa

Com s'executa:
  python3 efecte_adaptatiu.py

NO hi ha controls MIDI en aquest rol: l'únic "control" és el so que toques
a l'instrument connectat. Tot l'efecte reacciona al teu propi timbre.

DESCRIPTORS (calculats per blocs, sobre l'entrada en temps real):
  - RMS (energia)               -> ja donat, via librosa (com a S5/drum-replacer)
  - Centroide espectral (brillantor) -> ja donat, via librosa (com a S11)
  - Spectral flatness (tonal <-> sorollós) -> TODO, calculat a mà amb FFT

EFECTES (sempre actius simultàniament, ja construïts — NO cal tocar-los):
  - Distorsió (clipping, com S5)
  - Filtre passa-baixos (1 pol, IIR senzill)
  - Tremolo/AM (LFO modulant amplitude, com el "tremolo" esmentat a S9)

CONNEXIONS PER DEFECTE (descriptor -> paràmetre d'efecte):
  RMS         -> quantitat de distorsió (drive)
  Centroide   -> cutoff del filtre
  Flatness    -> profunditat del tremolo
Aquestes connexions són només un punt de partida — és la decisió MUSICAL
del grup, no una part tècnica del nucli. Veure "ZONA D'EXPERIMENTACIÓ" al
final del fitxer per canviar-les lliurement (quin descriptor mou quin
paràmetre, quants efectes alhora, etc.).

ESTRUCTURA D'AQUEST FITXER:
  - NUCLI MÍNIM (TODO 1-2): calcular flatness, escalar un valor d'un rang
    a un altre (per connectar descriptors amb paràmetres d'efecte).
  - ZONA D'EXPERIMENTACIÓ (no-TODO): on es decideix quin descriptor mou
    quin paràmetre — canvia-ho com vulguis un cop el nucli funcioni.
"""

import numpy as np
import sounddevice as sd
import librosa

SAMPLE_RATE = 44100
BLOCK = 1024


# =================================================================
# Descriptors ja donats (reaprofiten patrons ja vistos a S5/S11)
# =================================================================
def calcula_rms(bloc):
    """Energia del bloc. Mateix càlcul que ja vau fer servir per
    'hi_ha_trigger()' al drum-replacer."""
    return float(librosa.feature.rms(y=bloc, frame_length=len(bloc),
                                      hop_length=len(bloc) + 1)[0, 0])


def calcula_centroide(bloc, sr=SAMPLE_RATE):
    """Centroide espectral (brillantor). Mateixa funció que a S11."""
    return float(librosa.feature.spectral_centroid(
        y=bloc, sr=sr, n_fft=len(bloc), hop_length=len(bloc) + 1)[0, 0])


# =================================================================
# TODO 1 (NUCLI MÍNIM): spectral flatness, calculat a mà
# =================================================================
def calcula_flatness(bloc):
    """
    Spectral flatness: ràtio entre la mitjana GEOMÈTRICA i la mitjana
    ARITMÈTICA de les magnituds de l'espectre.
      - Espectre amb un pic clar (so tonal, com una nota pinçada) ->
        flatness PROP DE 0.
      - Espectre pla (soroll blanc, raspall de corda, etc.) ->
        flatness PROP DE 1.

    Passos (reutilitza np.fft.rfft, ja conegut de S11):
      1. Calcula l'espectre de magnituds: np.abs(np.fft.rfft(bloc))
      2. Per evitar log(0), suma una constant petita (p.ex. 1e-10)
         a les magnituds abans de fer-ne la mitjana geomètrica.
      3. Mitjana geomètrica = exp(mitjana(log(magnituds)))
      4. Mitjana aritmètica  = mitjana(magnituds)
      5. flatness = mitjana_geometrica / mitjana_aritmetica
    """
    # TODO 1: implementa els 5 passos de dalt
    return 0.0  # <-- substitueix


# =================================================================
# TODO 2 (NUCLI MÍNIM): escalat d'un rang a un altre
# =================================================================
def escala(valor, in_min, in_max, out_min, out_max):
    """
    Converteix 'valor' (que viu al rang [in_min, in_max]) al rang
    corresponent [out_min, out_max]. Aquesta és la peça que connecta
    qualsevol descriptor amb qualsevol paràmetre d'efecte.

    Exemple: escala(0.5, 0.0, 1.0, 100.0, 8000.0) -> 4050.0
    (un valor a la meitat del rang d'entrada cau a la meitat del de sortida)

    Recorda deixar el resultat sempre DINS de [out_min, out_max] encara
    que 'valor' surti una mica del rang d'entrada esperat (np.clip et pot
    anar bé aquí, com ja heu fet servir a S5).
    """
    # TODO 2: substitueix pel càlcul real
    return out_min  # <-- substitueix


# =================================================================
# Efectes ja construïts — NO cal tocar-los
# =================================================================
class Distorsio:
    """Clipping, mateix patró que 'distorsio_callback' de S5."""

    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.drive = 1.0  # paràmetre modulable

    def process(self, bloc):
        clipped = np.clip(bloc * self.drive, -self.threshold, self.threshold)
        return clipped / self.threshold


class FiltrePassaBaixos:
    """Filtre IIR d'1 pol — versió mínima d'un passa-baixos.
    y[n] = y[n-1] + alpha * (x[n] - y[n-1]), amb alpha derivat del cutoff."""

    def __init__(self, cutoff=8000.0, sample_rate=SAMPLE_RATE):
        self.cutoff = cutoff  # paràmetre modulable
        self.sample_rate = sample_rate
        self._y_anterior = 0.0

    def process(self, bloc):
        alpha = 1.0 - np.exp(-2 * np.pi * self.cutoff / self.sample_rate)
        out = np.zeros_like(bloc)
        y = self._y_anterior
        for i, x in enumerate(bloc):
            y = y + alpha * (x - y)
            out[i] = y
        self._y_anterior = y
        return out


class Tremolo:
    """AM: un LFO modula l'amplitud del senyal d'entrada.
    Mateixa idea que S9 esmenta per a tremolo (LFO sobre amplitude
    en lloc de pitch)."""

    def __init__(self, freq=5.0, sample_rate=SAMPLE_RATE):
        self.freq = freq
        self.sample_rate = sample_rate
        self.profunditat = 0.5  # paràmetre modulable (0=sense efecte, 1=al màxim)
        self._phase = 0.0

    def process(self, bloc):
        n = len(bloc)
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self._phase + phase_inc * np.arange(n)
        lfo = (np.sin(phases) + 1) / 2  # 0..1
        self._phase = (phases[-1] + phase_inc) % (2 * np.pi)
        gain = 1.0 - self.profunditat * (1.0 - lfo)
        return bloc * gain


# =================================================================
# Cadena d'efectes adaptativa
# =================================================================
class EfecteAdaptatiu:
    def __init__(self):
        self.distorsio = Distorsio()
        self.filtre = FiltrePassaBaixos()
        self.tremolo = Tremolo()

    def actualitza_parametres(self, bloc):
        """Calcula els 3 descriptors i actualitza els paràmetres dels
        3 efectes. Aquí és on viu la ZONA D'EXPERIMENTACIÓ (a sota)."""
        rms = calcula_rms(bloc)
        centroide = calcula_centroide(bloc)
        flatness = calcula_flatness(bloc)
        connecta_descriptors_amb_efectes(rms, centroide, flatness,
                                          self.distorsio, self.filtre, self.tremolo)

    def process(self, bloc):
        self.actualitza_parametres(bloc)
        out = self.distorsio.process(bloc)
        out = self.filtre.process(out)
        out = self.tremolo.process(out)
        return out


# =================================================================
# ZONA D'EXPERIMENTACIÓ — aquí decidiu vosaltres, no és un TODO tècnic
# =================================================================
def connecta_descriptors_amb_efectes(rms, centroide, flatness,
                                      distorsio, filtre, tremolo):
    """
    Aquesta funció és el "cablejat" entre el que sent l'instrument i com
    reaccionen els efectes. Les connexions de sota són un punt de partida
    raonable, NO la solució correcta — canvieu-les com vulgueu un cop el
    nucli (TODO 1-2) funcioni:

      - Proveu d'intercanviar quin descriptor mou quin paràmetre.
      - Proveu corbes no lineals (per exemple escala(valor**2, ...) en
        lloc de escala(valor, ...) per a una resposta més brusca).
      - Proveu de fer que un sol descriptor moduli DOS paràmetres alhora.
      - Proveu de desactivar un efecte (deixar el paràmetre fix) i jugar
        només amb els altres dos.

    Rangs orientatius dels descriptors (depenen molt de l'instrument i el
    nivell d'entrada real — ajusteu-los escoltant el vostre propi senyal):
      rms:        normalment entre 0.0 i 0.3
      centroide:  normalment entre 200 i 6000 (Hz)
      flatness:   sempre entre 0.0 i 1.0
    """
    distorsio.drive = escala(rms, 0.0, 0.3, 1.0, 6.0)
    filtre.cutoff = escala(centroide, 200.0, 6000.0, 300.0, 10000.0)
    tremolo.profunditat = escala(flatness, 0.0, 1.0, 0.0, 1.0)


def main():
    ea = EfecteAdaptatiu()

    def callback(indata, outdata, frames, time_info, status):
        mono = indata[:, 0]
        outdata[:, 0] = ea.process(mono)

    with sd.Stream(samplerate=SAMPLE_RATE, blocksize=BLOCK,
                    channels=1, dtype='float32', callback=callback):
        print("Efecte adaptatiu actiu. Toca el teu instrument.")
        print("Ctrl+C per aturar.")
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\nAturant...")


if __name__ == "__main__":
    main()
