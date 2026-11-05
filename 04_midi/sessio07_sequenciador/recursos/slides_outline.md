# Slides — Bloc 4b, Sessió 7
### Seqüenciació MIDI en temps real i timing precís

> **Instruccions de muntatge:** Mateix estil (referència: Sessió 8). Temps estimat: 17 min (diapositives 1–6) + 10 min (7–9) + 15 min d'exercici en paper (10–11) + demos (12–14).

---

### Diapositiva 1 — Portada
**Bloc 4 — MIDI i control musical (II)**
*Seqüenciació en temps real i timing precís*

---

### Diapositiva 2 — Avui, tot a Thonny
- Sessió 6: **fitxers** .mid (llegir, escriure, dibuixar) → no depèn del temps real → Colab
- Avui: les notes han de sonar **a l'instant just**, al teu ordinador → Thonny
- Criteri: *si cal so en directe o ports, tot a Thonny, encara que també desem fitxers*
- 🎤 Colab corre en un servidor de Google: no té el teu altaveu ni el teu rellotge

---

### Diapositiva 3 — `pretty_midi`: notes completes, temps en segons
```python
pm = pretty_midi.PrettyMIDI(initial_tempo=120)
piano = pretty_midi.Instrument(program=0)
nota = pretty_midi.Note(velocity=90, pitch=60, start=0.0, end=0.4)
piano.notes.append(nota)
pm.instruments.append(piano)
pm.write('demo1.mid')
```
- Una nota = un objecte, amb inici i final. Res de note_on + note_off + ticks
- 🎤 Demo: `demo_1_notes()` — mirar la taula de start/end que imprimeix

---

### Diapositiva 4 — Delta contra absolut
| | `mido` (S06) | `pretty_midi` (avui) |
|---|---|---|
| El temps d'un esdeveniment | delta: des de l'anterior | absolut: des de l'inici |
| "La 3a nota" | sumar les deltes 1, 2, 3 | `notes[2].start` |
| Si m'equivoco en una | totes les següents es mouen | només aquella |
- 🎤 Preguntar: quina de les dues columnes us recorda l'exercici en paper de la S06?
- Aquesta diferència tornarà d'aquí a deu minuts, amb el timing

---

### Diapositiva 5 — L'arpegiador
```python
def arpegiador(acord, n_repeticions, mode='up'):
    if mode == 'up':
        seq = acord
    elif mode == 'down':
        seq = acord[::-1]                 # la llista al revés
    elif mode == 'updown':
        seq = acord + acord[::-1][1:-1]   # sense repetir els extrems
    else:
        print("Mode desconegut:", mode)
        seq = []
    return seq * n_repeticions            # la llista repetida n cops
```
- Connexió amb TP1: llistes i bucles que generen patrons
- 🎤 Demo: `demo_2_arpegiador('up')`, `'down'`, `'updown'`
- A l'assignment: el mateix arpegiador, estès a diverses octaves

---

### Diapositiva 6 — El sinte d'avui és el callback del Bloc 3
- `sinte.py`: cap instal·lació nova, només `numpy` + `sounddevice`
- El fil principal **no toca l'àudio**: deixa encàrrecs (`note_on`, `note_off`)
- El callback, a cada bloc de 64 mostres (1,45 ms): recull encàrrecs → suma les veus → escriu el buffer
- Metrònom: `ona_click[(mostra) % P]` → el marca la **targeta de so**, no Python
- 🎤 Obrir `sinte.py` a Thonny i localitzar els tres passos del callback. No cal entendre cada línia

---

### Diapositiva 7 — El problema: esperar l'instant just
- Generar un fitxer: cap problema de temps (es desa, no sona)
- Tocar en directe: entre nota i nota cal **esperar** exactament el que toca
- Python no és un sistema de temps real: cap espera és perfecta
- La pregunta no és "com espero perfecte?", sinó **"què passa amb l'error?"**

---

### Diapositiva 8 — Estratègia A: `time.sleep(durada)`
```python
for nota in notes:
    synth.note_on(nota.pitch)
    time.sleep(nota.end - nota.start)
    synth.note_off(nota.pitch)
```
- Cada espera comença quan acaba l'anterior
- Si un `sleep` es passa 4 ms, la nota següent ja surt 4 ms tard... i la següent comença a comptar des d'aquí
- 🎤 És exactament `toca_amb_sleep()`, el que hem fet servir a les demos 1 i 2

---

### Diapositiva 9 — Estratègia B: temps objectiu absolut
```python
t_inici = time.perf_counter()
for i in range(n_notes):
    espera_fins(t_inici + i * pas)     # objectiu calculat des de l'INICI
    synth.note_on(84)
```
```python
def espera_fins(t_objectiu):           # a sinte.py
    falta = t_objectiu - time.perf_counter()
    if falta > 0.002:
        time.sleep(falta - 0.002)      # dorm fins a 2 ms abans
    while time.perf_counter() < t_objectiu:
        pass                           # els darrers 2 ms, espera activa
```
- Un retard puntual no s'arrossega: la nota següent té el seu propi objectiu
- 🎤 Amb pretty_midi, l'objectiu ja ve donat: `t_inici + nota.start`. Per què dorm abans? Ho veurem a la demo 5

---

### Diapositiva 10 — ✏️ Exercici en paper (1/2)
**140 bpm, corxeres: pas = 214 ms. Cada `time.sleep` es passa 4 ms.**

| Nota | Ideal (ms) | A: real | A: retard | B: retard |
|---|---|---|---|---|
| 1 | 0 | | | |
| 2 | 214 | | | |
| 3 | 428 | | | |
| ... | | | | |
| 8 | 1498 | | | |

- Omple la taula: on sona cada nota amb A? I amb B?
- 🎤 10 minuts en parelles. Respostes a la guia

---

### Diapositiva 11 — ✏️ Exercici en paper (2/2)
1. Quin retard té la nota 32 amb l'estratègia A?
2. A quina nota ha perdut A una **semicorxera sencera** (107 ms)?
3. Ara hi ha 4 ms de feina entre nota i nota. Què canvia per a A? I per a B?
4. I si la feina durés 250 ms?
- 🎤 Apuntar les respostes: d'aquí a 5 minuts les comprovarem a cada màquina

---

### Diapositiva 12 — Mesurem-ho a la teva màquina
- `demo_3_mesura()` i `demo_3_mesura(feina_ms=4)`
- *(Diapositiva amb el gràfic de `demo_3_mesura(feina_ms=4)`: A puja en línia recta, B enganxada a 0, la línia de la semicorxera)*
- Coincideix amb el paper? Cada ordinador té el seu `sleep`: un Mac i un Windows poden donar números molt diferents
- 🎤 La feina simulada garanteix que la diferència surti a tothom; la deriva "natural" depèn de la màquina

---

### Diapositiva 13 — Escoltem-ho contra un rellotge que no és Python
- `demo_4_escolta('A')` → el hi-hat es va separant del click
- `demo_4_escolta('B')` → es queda enganxat al click
- El click el compta la targeta (mostres); les notes les envia Python
- El programa imprimeix l'error **segons la targeta**, no segons Python
- 🎤 Auriculars

---

### Diapositiva 14 — La trampa: B perfecta... segons Python
- `demo_5_la_trampa()`: la mateixa B, però la feina entre notes és càlcul pur en Python
- Python diu: 0 ms de retard. L'altaveu: espetecs, i les notes i el click es desquadren
- **GIL**: només un fil de Python executa codi alhora. Mentre el fil principal calcula, el callback no pot entrar → arriba tard al seu termini de 1,45 ms → la targeta sona silenci
- Per això `espera_fins` **dorm** fins a 2 ms abans: deixa lloc al callback
- 🎤 Lligar amb el Bloc 3: el termini del callback depèn de TOT el programa, no només del callback

---

### Diapositiva 15 — Assignment
1. `arpegiador` amb **octaves**
2. `notes_a_midi` amb **tempo, gate i accents**
3. `reprodueix`: la seqüència en directe amb l'estratègia B
4. `el_meu_sequenciador()`: munta-ho, escolta-ho i desa el .mid
5. Reflexió
- Cada part: `escolta_partN()` 🔊 i `comprova_partN()` ✅
- Challenges: baix, clock extern, precisió a la mostra

---

### Diapositiva 16 — Tancament Bloc 4, preview Bloc 5
- Bloc 4: protocol MIDI, fitxers, seqüenciació, timing
- Altres eines que existeixen (no les fem avui): fil dedicat per a seqüenciadors interactius; MIDI Clock per sincronitzar-se amb un DAW o una placa
- Bloc 5: el callback de `sinte.py` creixerà fins a ser **el vostre** sintetitzador (oscil·ladors, ADSR, FM), controlat per les notes que ja sabeu generar
