"""
Solució de referència — Projecte final: EFECTE ADAPTATIU
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1 (calcula_flatness) i 2 (escala) sense micròfon ni sounddevice.
La zona d'experimentació (connecta_descriptors_amb_efectes) és la decisió
musical del grup — la referència usa les connexions per defecte del template.
"""

import numpy as np

SAMPLE_RATE = 44100
BLOCK = 1024


# ── Descriptors donats (còpia del template) ──────────────────────────────────

def calcula_rms_simple(bloc):
    return float(np.sqrt(np.mean(bloc ** 2)))


# ── TODO 1 — calcula_flatness ────────────────────────────────────────────────

def calcula_flatness(bloc):
    """
    Spectral flatness: mittana geomètrica / mittana aritmètica de les magnituds.
    0 ≈ to tonal, 1 ≈ soroll blanc.
    """
    magnituds = np.abs(np.fft.rfft(bloc)) + 1e-10   # evita log(0)
    mittana_geometrica = np.exp(np.mean(np.log(magnituds)))
    mittana_aritmetica = np.mean(magnituds)
    return float(mittana_geometrica / mittana_aritmetica)


# Autotests TODO 1
# So tonal pur → flatness prop de 0
t = np.linspace(0, BLOCK / SAMPLE_RATE, BLOCK, endpoint=False)
to_pur = np.sin(2 * np.pi * 440 * t).astype('float32')
flatness_tonal = calcula_flatness(to_pur)
assert 0.0 <= flatness_tonal <= 1.0, f"Fora de rang: {flatness_tonal}"
assert flatness_tonal < 0.5, f"Un to pur hauria de tenir flatness baix, és {flatness_tonal:.3f}"

# Soroll blanc → flatness prop de 1
soroll = np.random.uniform(-1, 1, BLOCK).astype('float32')
flatness_soroll = calcula_flatness(soroll)
assert flatness_soroll > 0.5, f"El soroll blanc hauria de tenir flatness alt, és {flatness_soroll:.3f}"

print(f"✅ TODO 1 (calcula_flatness):")
print(f"   To pur 440Hz:  flatness = {flatness_tonal:.4f} (proper a 0 ✓)")
print(f"   Soroll blanc:  flatness = {flatness_soroll:.4f} (proper a 1 ✓)")


# ── TODO 2 — escala ──────────────────────────────────────────────────────────

def escala(valor, in_min, in_max, out_min, out_max):
    """Interpolació lineal + clip: [in_min, in_max] → [out_min, out_max]."""
    t = (valor - in_min) / (in_max - in_min + 1e-12)
    t = np.clip(t, 0.0, 1.0)
    return float(out_min + t * (out_max - out_min))


# Autotests TODO 2
assert abs(escala(0.5,  0.0, 1.0,  100.0, 8000.0) - 4050.0) < 1.0
assert abs(escala(0.0,  0.0, 1.0,  100.0, 8000.0) - 100.0)  < 1.0
assert abs(escala(1.0,  0.0, 1.0,  100.0, 8000.0) - 8000.0) < 1.0
# Valors fora del rang d'entrada han de quedar clipats
assert abs(escala(-1.0, 0.0, 1.0,  100.0, 8000.0) - 100.0)  < 1.0
assert abs(escala(2.0,  0.0, 1.0,  100.0, 8000.0) - 8000.0) < 1.0
print("✅ TODO 2 (escala) correcte")


# ── Efectes donats (còpia del template) ──────────────────────────────────────

class Distorsio:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.drive = 1.0

    def process(self, bloc):
        clipped = np.clip(bloc * self.drive, -self.threshold, self.threshold)
        return clipped / self.threshold


class FiltrePassaBaixos:
    def __init__(self, cutoff=8000.0, sample_rate=SAMPLE_RATE):
        self.cutoff = cutoff
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
    def __init__(self, freq=5.0, sample_rate=SAMPLE_RATE):
        self.freq = freq
        self.sample_rate = sample_rate
        self.profunditat = 0.5
        self._phase = 0.0

    def process(self, bloc):
        n = len(bloc)
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self._phase + phase_inc * np.arange(n)
        lfo = (np.sin(phases) + 1) / 2
        self._phase = (phases[-1] + phase_inc) % (2 * np.pi)
        gain = 1.0 - self.profunditat * (1.0 - lfo)
        return bloc * gain


def connecta_descriptors_amb_efectes(rms, centroide, flatness,
                                      distorsio, filtre, tremolo):
    """Connexió de referència (punt de partida del template)."""
    distorsio.drive = escala(rms,       0.0,    0.3,  1.0,    6.0)
    filtre.cutoff   = escala(centroide, 200.0,  6000.0, 300.0, 10000.0)
    tremolo.profunditat = escala(flatness, 0.0, 1.0,  0.0,    1.0)


# ── Pipeline integrat (validació end-to-end) ─────────────────────────────────

dist   = Distorsio()
filtre = FiltrePassaBaixos()
trem   = Tremolo()

# Simula un bloc d'entrada (to pur fort)
bloc_entrada = (0.7 * to_pur).astype('float32')
rms_val      = calcula_rms_simple(bloc_entrada)
centroid_val = 440.0   # valor aproximat per al test (evitem librosa)
flat_val     = calcula_flatness(bloc_entrada)

connecta_descriptors_amb_efectes(rms_val, centroid_val, flat_val, dist, filtre, trem)

sortida = dist.process(bloc_entrada)
sortida = filtre.process(sortida)
sortida = trem.process(sortida)

assert len(sortida) == BLOCK
assert np.max(np.abs(sortida)) <= 1.0 + 1e-6
assert not np.any(np.isnan(sortida))
print("✅ Pipeline complet (flatness → escala → efectes) correcte")

print("\n✅ TODOs 1 i 2 del projecte Efecte Adaptatiu validats correctament.")
print("\nNOTA DOCENT — connecta_descriptors_amb_efectes() és la decisió MUSICAL")
print("del grup: qualsevol connexió descriptor→paràmetre és vàlida.")
print("Criteris d'avaluació: que els 3 descriptors es calculin correctament,")
print("que 'escala' funcioni i que es puguin sentir canvis en els efectes.")
