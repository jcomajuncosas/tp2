# Slides — Bloc 3b, Sessió 4
### El model callback: àudio en temps real

> **Instruccions de muntatge:** Mateix estil que sessions anteriors. Temps estimat: 20-25 min (aquesta sessió mereix una mica més de teoria).

---

### Diapositiva 1 — Portada
**Bloc 3b — El model callback**
*Àudio en temps real: inversió de control*

---

### Diapositiva 2 — La pregunta que vam deixar oberta
- Sessió 3: `reverse` és impossible en temps real. Per qué?
- Perquè necessites totes les mostres futures — que encara no han arribat
- Avui: com treballem *mentre* les mostres arriben?
- La resposta és el model callback

---

### Diapositiva 3 — El problema del blocking per a temps real
- Diagrama: `sd.rec(3s)` → barra de progrés de 3 segons → `processa` → `sd.play()`
- Durant els 3 segons de gravació: el programa no respon a res
- Latència total: 3s de gravació + temps de procés + reproducció
- Per a un efecte "en directe": inacceptable

---

### Diapositiva 4 — La inversió de control
- En blocking: **tu crides** les funcions quan vols
- En callback: **el sistema crida** la teva funció quan necessita dades
- Analogia: blocking = anar a buscar el correu. Callback = tenir timbre
- Quan sona el timbre, has de respondre **ràpid** — el sistema no espera

---

### Diapositiva 5 — El mapa mental: dues columnes
*(Diapositiva visual clau — reproduir la taula del cheat sheet en format gran, llegible des del fons de l'aula)*

| BLOCKING | CALLBACK |
|---|---|
| Tu crides `sd.rec()` | Tu defineixes `process()` |
| Tu esperes (`sd.wait()`) | El sistema crida `process()` |
| Processes tot l'array | Processa bloc a bloc (~10ms) |
| Programa bloquejat | Programa pot fer altres coses |
| Latència alta (>1s) | Latència baixa (~10ms) |
| Cap risc especial | Callback lenta → glitch |

---

### Diapositiva 6 — "Com si gestionéssim dues coses alhora"
- El teu programa principal continua: llegeix teclat, respon a MIDI, mou sliders...
- El sistema crida `process()` automàticament cada ~10ms per processar àudio
- Tu no gestiones aquesta periodicitat — defineixes *què fer* cada cop que toca
- Diagrama: línia de temps amb `process()` cridada regularment, i el programa principal entre mig

---

### Diapositiva 7 — Estructura del callback
```python
def process(indata, outdata, frames, time, status):
    # indata:  el so que entra (micròfon) — shape (frames, channels)
    # outdata: el so que ha de sortir (altaveu) — shape (frames, channels)
    # frames:  nombre de mostres en aquest bloc
    outdata[:] = indata  # pass-through
```
- `outdata[:] = ...` — **cal el `[:]`** per modificar l'array in-place (sinó no funciona)
- La regla d'or: cap `input()`, cap `sf.read()`, cap operació lenta

---

### Diapositiva 8 — Buffer i latència: el trade-off
- `blocksize`: nombre de mostres per crida al callback
- Petit (256): latència ~6ms, risc de glitch alt (poc temps per processar)
- Gran (1024): latència ~23ms, risc de glitch baix (més temps per processar)
- Diagrama: línia de temps amb buffers de mida diferent
- Fórmula: `latència ≈ blocksize / sample_rate`

---

### Diapositiva 9 — Obrir un Stream
```python
with sd.Stream(samplerate=44100, blocksize=1024,
               channels=1, dtype='float32',
               callback=process):
    sd.sleep(10000)  # manté el stream 10 segons
```
- `sd.sleep(ms)` és no-blocking (a diferència de `time.sleep`)
- El `with` tanca el stream automàticament en acabar

---

### Diapositiva 10 — Variable compartida: el problema del gain
- Volem canviar el gain mentre el stream és actiu
- El callback no pot fer `input()` — és massa lent
- Solució simple: **variable global** llegida pel callback
- Demo en directe: modificar `gain` des del programa principal mentre el stream sona

---

### Diapositiva 11 — Variable global: honest sobre les limitacions
```python
gain = 0.5  # accessible des del callback I des del programa principal

def process(indata, outdata, frames, time, status):
    outdata[:] = indata * gain  # llegeix la variable global
```
- Funciona en pràctica (Python GIL protegeix operacions simples)
- En producció real: `queue.Queue` o variables atòmiques per seguretat
- Per ara: és lleig però funciona — ho sabem i ho acceptem
- Sessió 5: controlarem paràmetres amb sliders (`ipywidgets`) de manera més elegant

---

### Diapositiva 12 — Per qué Colab no funciona per a temps real
- Colab: codi en un servidor remot de Google → so viatja per la xarxa
- Latència de xarxa: 50-200ms → incompatible amb els ~10ms necessaris
- **WebAudio API** (navegador): s'executa localment al teu ordinador, accés directe al hardware → sí que és temps real. És la base de moltes eines d'àudio web professionals
- Conclusió: el temps real requereix accés local al hardware. Per això avui treballem amb Thonny, no Colab

---

### Diapositiva 13 — Connexió amb el projecte final
- El sintetitzador del Bloc 5 → motor d'àudio basat en callback
- El looper, la bassline, el drum-replacement del projecte final → tots usen aquest model
- La callback d'avui és el cor de tot el que farem d'aquí endavant
