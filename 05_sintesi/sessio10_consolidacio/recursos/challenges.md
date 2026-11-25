# Challenges opcionals — Sessió 10
### Per a qui vulgui anar més enllà (no avaluat)

Tots tres parteixen del teu `assignment.py` d'avui.

---

## Challenge 1 — Un hi-hat a la tecla 42

La tecla 42 és el *closed hi-hat* al mapa General MIDI. Un hi-hat sintètic és **soroll** amb una envolvent molt curta.

1. Escriu una classe `Noise` amb `process(n_samples)`, que retorni soroll blanc entre −1 i 1 (`np.random.uniform`). Fixa't: és el primer UGen del curs **sense estat**. No ha de recordar res entre blocs. Per què l'`Oscillator` sí que en necessita, i el soroll no?
2. Escriu una classe `HiHat` amb la mateixa interfície que el `Kick` (`note_on(velocity)`, `note_off()`, `process(n)`), feta amb un `Noise` i una `Envelope` sense sustain.
3. Fes-la sonar a la tecla 42. Caldrà que l'`Instrument` i `gestiona` la coneguin.

Per pensar: una caixa (*snare*) combina una part tonal (com el kick, però més aguda) i una de soroll. Te'n surts amb el que ja tens?

---

## Challenge 2 — `process_freqs` sense bucle

`process_freqs` té un bucle de Python mostra a mostra. La fase de cada mostra és la fase inicial **més la suma de tots els increments anteriors**, i NumPy té una funció que fa justament sumes acumulades: `np.cumsum`.

1. Escriu `process_freqs_rapid(self, freqs)` sense cap bucle. Ha de donar **el mateix resultat** que la teva (comprova-ho amb `np.allclose` sobre uns quants blocs seguits, no només el primer: la fase ha de continuar bé d'un bloc a l'altre).
2. Fes que la `VeuFM` el faci servir i torna a executar `mesura_cost`. Quantes vegades més ràpid és? Quantes veus hi cabrien ara?

---

## Challenge 3 — Polifonia

Ara la veu toca una sola nota. Fes una classe `Polifonic` amb una **llista** de 4 `VeuFM` (és el challenge de la S09, ara amb teclat):
- cada nota nova va a la veu següent (l'operador `%` és el teu amic);
- un final de nota ha d'aturar la veu que toca **aquella** nota (el que has après a la Part E);
- `process(n)` suma les 4 veus.

Pensa on ha de viure ara la comprovació de la Part E: amb 4 veus, `gestiona` ja no pot preguntar a *una* veu quina nota toca. Si el `Polifonic` té `note_on`, `note_off` i `process`, l'`Instrument` el pot fer servir com si fos una sola veu. Toca un acord!

---

## Annex — Tres reptes amb `signalflow`

Per instal·lar-lo i provar-lo des de Thonny, segueix **`signalflow_thonny.md`** (en aquesta carpeta). No cal terminal ni entorn virtual. Un cop `prova_signalflow.py` sona, prova aquests reptes. Documentació: https://signalflow.dev/

**Repte 1 — Reproduir la FM de la Sessió 9, amb `signalflow`:**
```python
from signalflow import *

graph = AudioGraph()

fm = 80
I = 2.5                                         # índex de Chowning: excursió = I × fm = 200 Hz
modulator = SineOscillator(fm) * (I * fm)
carrier = SineOscillator(440 + modulator)
carrier.play()

graph.wait(5)                                   # 5 segons (sense número, espera per sempre)
```
Compara-ho amb el teu `fm_synth(440, 80, 2.5, ...)` de la Sessió 9 (la versió amb `process_freqs`). Han de sonar igual: totes dues actualitzen la freqüència a cada mostra. I amb la versió per blocs (`vibrato(440, 80, 200, ...)`)?

**Repte 2 — Envolvent ADSR amb `signalflow`:**
```python
graph = AudioGraph()

gate = 1
env = ADSREnvelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3, gate=gate)
osc = SineOscillator(440) * env
osc.play()

graph.wait(1.0)
env.set_input("gate", 0)   # equivalent al nostre note_off()
graph.wait(1.0)
```
Compara amb la classe `Envelope` pròpia: en lloc de mètodes `note_on()`/`note_off()`, `signalflow` fa servir un paràmetre `gate` (1=premuda, 0=alliberada) que es pot canviar en qualsevol moment amb `set_input()`. Quines diferències d'API trobes? Quins avantatges/inconvenients té cada disseny?

**Repte 3 (obert) — MIDI amb `signalflow`:**
La pròpia llibreria té un exemple oficial de teclat MIDI: `examples/midi-keyboard-example.py` al repositori (https://github.com/ideoforms/signalflow), que combina `MidiNoteToFrequency(note)` amb `ADSREnvelope(..., gate=gate)` — fent servir `mido`, la mateixa llibreria MIDI que ja coneixeu de les Sessions 6-7. Descarrega l'exemple, i compara la quantitat de codi necessària amb la nostra integració manual (el `Reproductor` i el callback de l'`assignment.py` de la Sessió 9). Atenció: l'exemple oficial obre el port amb `mido.open_input`, que necessita `python-rtmidi` (sense versió per a Python 3.13); adapta'l amb `rtmidi2` i `mido.Message.from_bytes`, com a la Sessió 7.

---
