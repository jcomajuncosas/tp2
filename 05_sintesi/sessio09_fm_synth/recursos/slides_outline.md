# Slides — Bloc 5b, Sessió 9
### Síntesi FM i envolvents amb estat

> **Instruccions de muntatge:** 8 diapositives curtes, **intercalades** amb el notebook (no és un bloc de teoria). Cada diapositiva es mostra just abans de la part del notebook corresponent i dura 1-3 minuts. La resta del temps es projecta el notebook. Abans de cada execució important, predicció oral (🎤).

---

### Diapositiva 1 — Portada
**Bloc 5 — Síntesi (II)**
*Síntesi FM i envolvents amb estat*
- Avui: el midterm (20'), i després construireu una veu FM i la tocareu en temps real

---

### Diapositiva 2 — El callback parla en mostres (abans de la Part 1)
```python
def callback(outdata, frames, time_info, status):
    outdata[:, 0] = ...      # em demanen `frames` MOSTRES, ara
```
```python
osc.generate(duration)       # S08: en segons
osc.process(n_samples)       # avui: en mostres, el que demana el callback
```
- Mateixa fase (`self._phase`), mateix so: només canvia **la pregunta** que li fem
- 🎤 *Si `generate` i `process` fan el mateix `if/elif`... on arreglaríeu un error de la dent de serra?*

---

### Diapositiva 3 — Vibrato vs. FM: la mateixa idea (abans de la Part 2)
| | Modulador | Excursió | Es percep com |
|---|---|---|---|
| Vibrato | 5 Hz | 6 Hz | la mateixa nota, ondulant |
| FM (Chowning, 1973; DX7, 1983) | **80 Hz** | **200 Hz** | ? |
- El vostre `vibrato()` ja ho fa: només cal canviar els números
- 🎤 *Votació abans d'escoltar: timbre metàl·lic nou / vibrato molt ràpid / una altra cosa?*

---

### Diapositiva 4 — Què ha passat? (després del paper, abans de la Part 3)
- Mirem el modulador **86 cops per segon** (un cop per bloc de 512)
- Un senyal de 80 Hz mirat 86 cops per segon sembla un senyal de **6 Hz** → la sirena
- És l'**aliasing** de la Sessió 2, aplicat al modulador
- La idea era bona; l'estructura del codi, no: el portador ha de canviar de freqüència **a cada mostra**
```python
osc.process(n)              # una freqüència per a tot el bloc
osc.process_freqs(freqs)    # una freqüència per a CADA mostra (freqs: array)
```

---

### Diapositiva 5 — L'índex de modulació (Part 3)
- Chowning (i el DX7) no donen l'excursió en Hz, sinó l'**índex** `I`, sense unitats:

  **excursió (Hz) = I × freqüència del modulador**

- 200 Hz d'excursió amb un modulador de 80 Hz → **I = 2,5**
- Els parcials apareixen a **portador ± k × modulador**; com més `I`, més parcials
- 🎤 *Abans d'escoltar la versió nova: on esperes veure les línies de l'espectre? (440, 360, 520, …)*

---

### Diapositiva 6 — Una envolvent que recorda on és (Part 4)
```
          note_on                  note_off
 idle ──────────► attack ──► decay ──► sustain ──────────► release ──► idle
                  (puja)    (baixa)   (s'hi queda)         (baixa des d'on sigui)
```
- `note_on()` / `note_off()` **només canvien l'estat** (`self.stage`)
- `process(n)` fa avançar la corba mostra a mostra: un `if/elif` per estat
- 🎤 *Attack de 0,01 s, blocs de 512: a quin bloc passa a decay?*

---

### Diapositiva 7 — `VeuFM`: una veu, no un sintetitzador (Part 5)
- 🎤 *Quines classes ja teniu? Quantes de cada en necessita una veu FM?*
- Configuració (es tria un cop): `ratio` (C:M), `I_max`, ADSR
- Estat (canvia a cada nota): la nota, el guany… i, a dins, les fases i l'`stage`
- **El detall de Chowning:** `I = I_max × envolvent` → brillant a l'atac, fosc a la cua (metalls, campanes)
- `ratio` enter → afinat; `ratio` 1,41 → campana; `ratio` 3,5 → 🎤 *quina nota sents?*

---

### Diapositiva 8 — Tancament i S10
- Avui heu canviat **l'estructura** del codi, no només els números:
  - `_ona`: un sol lloc per a les formes d'ona
  - `process_freqs`: una freqüència per mostra → FM de debò
  - `VeuFM`: una classe feta de les vostres classes
- **Sessió 10:** quant costa el vostre bucle mostra a mostra? (el mesurarem i l'accelerarem), teclat MIDI real, i `signalflow`: la mateixa idea, feta per professionals
