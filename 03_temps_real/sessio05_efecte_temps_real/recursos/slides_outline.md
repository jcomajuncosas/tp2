# Slides — Sessió 5
### Bloc 3c: Efectes amb memòria

---

### Diapositiva 1 — Efectes amb memòria
- Bloc 3: offline (S03) → callback (S04) → **avui: efectes que recorden**
- Avui farem sonar: un oscil·lador, un ring modulator, un eco
- 🎤 Recordar: auriculars posats durant tota la sessió.

---

### Diapositiva 2 — La callback té amnèsia
- Cada crida veu **només el bloc actual**: 1024 mostres ≈ 23 ms
- 43 crides per segon, i cap no sap res de l'anterior
- La distorsió de la S04 no en patia: cada mostra només depèn d'ella mateixa
- 🎤 Enllaçar amb la pregunta 3 del warm-up.

---

### Diapositiva 3 — Experiment: un sinus bloc a bloc
```python
t = np.arange(frames) / sample_rate
outdata[:, 0] = 0.2 * np.sin(2 * np.pi * 440 * t)
```
- Què sentirem? (pregunta 4 del warm-up)
- 🎤 Fer sonar `demo_sinus_sense_memoria()` ARA, abans d'explicar res. Deixar que identifiquin el brunzit.

---

### Diapositiva 4 — D'on surt el brunzit
- `t` torna a 0 a cada bloc → el sinus es talla i torna a començar
- 1024 mostres a 440 Hz = 10.2 cicles: no encaixa → **clic a cada frontera**
- 43 clics per segon → brunzit de **~43 Hz** (`sample_rate / blocksize`)
- 🎤 Ensenyar el gràfic de la secció 1 del Colab (càmera lenta).

---

### Diapositiva 5 — La solució: recordar UN número
```python
fase = 0.0                                   # fora de la callback

def sinus_callback(indata, outdata, frames, time_info, status):
    global fase
    increment = 2 * np.pi * freq / sample_rate
    fases = fase + increment * np.arange(frames)
    outdata[:, 0] = 0.2 * np.sin(fases)
    fase = (fase + increment * frames) % (2 * np.pi)
```
- La **fase**: on s'ha quedat l'oscil·lador dins el seu cicle
- Ara la callback **escriu** una global → ara sí cal `global` (pregunta 2 del warm-up)
- 🎤 `demo_sinus()` i comparar.

---

### Diapositiva 6 — Ring modulator
- Entrada × portadora (un sinus) → freqüències noves: suma i diferència
- So metàl·lic, robòtic (Dalek, Stockhausen *Mixtur*)
- Mateixa memòria que el sinus: la fase
- 🎤 `demo_ringmod()`: provar 30, 150, 600, 1500 Hz… i 5 Hz (s'assembla a un trèmolo: el pont cap a l'assignment).

---

### Diapositiva 7 — Eco: ara cal recordar MOLTES mostres
- El so de fa 0.3 s = 13.230 mostres ≈ 13 blocs enrere
- Les guardem en una **cinta** (`delay_buffer`)
```
  surt ◄── [ més antic · · · · · · · · · · més nou ] ◄── entra
  (eco)
```
- 🎤 Pregunta 6 del warm-up: amb 6 caselles i blocs de 2, quantes crides? Resoldre-ho amb la taula del Colab (secció 2).

---

### Diapositiva 8 — Tres passos a cada crida
```python
eco = delay_buffer[:frames]                      # 1. LLEGIR el més antic
sortida = mono + volum_eco * eco                 # 2. MESCLAR
delay_buffer = np.roll(delay_buffer, -frames)    # 3. AVANÇAR...
delay_buffer[-frames:] = mono                    #    ...i ESCRIURE
```
- **Retard = mida de la cinta**, exacte, sigui quin sigui el blocksize
- Retard mínim: un bloc (23 ms)
- 🎤 `demo_eco()`. Fer notar: UNA sola repetició. Per què? (a la cinta hi va `mono`)

---

### Diapositiva 9 — Una nota d'honestedat
- `np.roll` mou **totes** les mostres a cada crida (13.230 per escriure'n 1.024)
- Un **buffer circular** de veritat deixa les dades quietes i mou un índex
- Per a nosaltres: la cinta és més clara i prou ràpida
- 🎤 El buffer circular de debò apareix al Bloc 5 (i al challenge del stutter, amb `%`).

---

### Diapositiva 10 — Paràmetres en directe: qui toca què
- El **bucle** canvia números: `delay_samples`, `volum_eco`
- La **callback** és l'única que toca la cinta
- Entrada de l'usuari: mai ignorar en silenci (`"No t'entenc"`)
- 🎤 `demo_eco_control()`: provar `r 0.05`, `r 0.5`, `v 0.9`, i una ordre mal escrita.

---

### Diapositiva 11 — L'ordre importa?
- `demo_disto_eco()`: distorsió → eco
- I eco → distorsió? Sonarà igual?
- 🎤 NO respondre: és la Part 3 de l'assignment.

---

### Diapositiva 12 — Comptem globals
| Efecte | Memòria |
|---|---|
| Distorsió | res |
| Oscil·lador | 1 número |
| Eco | una cinta |
- Avui: `fase_sinus`, `fase_ringmod`, `delay_buffer`, `delay_buffer_1`, `delay_buffer_2`…
- I si en volguéssim 5? I un trèmolo a sobre?
- 🎤 `demo_dos_ecos()`. Deixar la pregunta oberta → Bloc 5.
