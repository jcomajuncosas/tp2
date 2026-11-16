# Cheat sheet — Sessió 9
### Síntesi FM i envolvents amb estat

---

## 1. `process(n_samples)`: parlar en mostres

El callback demana `frames` **mostres**. Per això els components tenen un mètode que en retorna exactament `n_samples`, continuant on s'havien quedat (`self._phase`).

| Mètode | Retorna | Quan |
|---|---|---|
| `generate(duration)` | `duration` segons | offline (S08) |
| `process(n_samples)` | `n_samples` mostres, freqüència constant | blocs, callback |
| `process_freqs(freqs)` | una mostra per a cada freqüència de l'array | quan la freqüència canvia a cada mostra (FM) |

**Mateix nom de mètode → mateixa feina.** Qualsevol objecte amb `process(n)` es pot fer servir igual dins un callback: oscil·lador, envolvent, veu, reproductor… (UGen, *unit generator*: com els objectes de Max/Pd).

## 2. Refactoritzar: un mètode intern

Si dos mètodes repeteixen el mateix codi, treu-lo a un mètode propi i crida'l amb `self.`:

```python
class Exemple:
    def _ajuda(self, x):        # guió baix: d'ús intern
        return x * 2

    def feina(self, y):
        return self._ajuda(y) + 1
```

## 3. Vibrato i "FM" per blocs

```
cada bloc:  bloc_lfo = lfo.process(512)
            osc.freq = base + depth × bloc_lfo[-1]     ← 1 valor per bloc
```
- Amb un modulador **lent** (vibrato, 5 Hz) funciona: dins un bloc gairebé no canvia.
- Amb un modulador **ràpid** (80 Hz) **no**: el llegim 44100 / 512 ≈ **86 cops per segon**, i un senyal de 80 Hz llegit 86 cops per segon sembla de 86 − 80 ≈ **6 Hz** (aliasing). Sona una sirena, no un timbre.
- Si el modulador fa exactament 86,13 Hz (o un múltiple), sempre el llegim al mateix punt: la nota es **congela**.

## 4. FM de debò

La freqüència del portador canvia **a cada mostra**:

```
freqs = freq_portador + I × freq_modulador × bloc_del_modulador     (un array)
sortida = portador.process_freqs(freqs)
```

- **Índex de modulació `I`** (Chowning, DX7), sense unitats: **excursió (Hz) = I × freq_modulador**
- Parcials a **portador ± k × modulador** (k = 1, 2, 3…). Com més gran és `I`, més parcials.
- **Relació C:M** (`ratio` = modulador / portador):

| `ratio` | Parcials | So típic |
|---|---|---|
| 1, 2, 3… (enter) | harmònics | afinat: metall, fusta, orgue… |
| 1,41 (irracional) | inharmònics | campana, metall percudit |
| 3,5 | múltiples de la **meitat** de la nota | sona una octava més greu |

## 5. `Envelope` amb estat (temps real)

```
          note_on                  note_off
 idle ──────────► attack ──► decay ──► sustain ──────────► release ──► idle
```

| Atribut | Què és |
|---|---|
| `self.stage` | estat: `'idle'`, `'attack'`, `'decay'`, `'sustain'`, `'release'` |
| `self.level` | nivell actual (0 … 1) |
| `self._pas` | quant canvia el nivell a cada mostra |

- `note_on()` i `note_off()` **només canvien l'estat**. És `process(n)` qui avança, mostra a mostra, amb un `if/elif` per estat.
- El release baixa **des del nivell actual**: deixar anar la tecla a mitja pujada no fa salt.
- Un `note_on` a mig release puja **des d'on és**: sense clic.
- Quantes mostres dura una fase: `segons × 44100`. En quin bloc cau la mostra `m`: `m // 512`.

## 6. `VeuFM`: una classe feta de classes

```
VeuFM
├── self.carrier    (Oscillator)
├── self.modulator  (Oscillator)      freq = carrier.freq × ratio
└── self.env        (Envelope)
configuració: ratio, I_max, ADSR       estat: la nota, el guany
```
- `note_on(nota, velocity)` · `note_off()` · `process(n)`
- **Índex que segueix l'envolvent:** `I = I_max × corba` → brillant a l'atac, fosc a la cua.
- Les peces es creen **un sol cop**, a `__init__`. Cada nota només en canvia l'estat.

## 7. En temps real (Thonny)

```python
def callback(outdata, frames, time_info, status):
    outdata[:, 0] = 0.5 * reproductor.process(frames)
```
Tota la memòria (fases, `stage`, posició de la seqüència) viu **dins els objectes**. Cost aproximat d'una `VeuFM` amb bucle mostra a mostra: ~0,25 ms per bloc de 512, i el bloc dura 11,6 ms.

## 8. Taula resum del Bloc 5 fins ara

| Concepte | Sessió 8 | Sessió 9 |
|---|---|---|
| Unitat de temps | segons (`generate`) | mostres (`process`) |
| Freqüència | constant per crida | també una per mostra (`process_freqs`) |
| Envolvent | corba sencera, durada coneguda | màquina d'estats, `note_on`/`note_off` |
| Instrument | `Veu` (osc + env) | `VeuFM` (2 osc + env, índex variable) |
| Entorn | Colab | Colab + Thonny (temps real) |
