# Looper/bassline

Step-sequencer per a una línia de baix sintetitzada, amb el tempo marcat per
tu mateix en directe (tap-to-tempo manual) — com un baixista que es marca
el pols abans d'entrar.

## Com funciona

Hi ha un **cursor d'edició** que apunta sempre a un dels passos (0 a 7). El
mous amb `NEXT_STEP`, i qualsevol nota que toquis després s'assigna al pas
on és el cursor — pots posar la nota que vulguis a cada pas, no estan
lligades al seu índex. Mentre el looper REPRODUEIX, pots seguir editant
passos amb total llibertat: el canvi se sent al pròxim cop que el transport
hi torni a passar.

```
EDITANT --[TAP x2]--> (tempo actualitzat, segueix EDITANT)
EDITANT --[NEXT_STEP]--> (cursor avança un pas)
EDITANT --[nota lliure]--> (pas del cursor assignat amb aquesta alçada)
EDITANT --[PLAY]--> REPRODUINT --[STOP]--> EDITANT
```

1. **TAP** (prem-la diverses vegades seguides, al pols que vulguis): cada
   parell de taps consecutius calcula la durada d'un pas a partir de
   l'interval real entre ells.
2. **NEXT_STEP** + notes lliures: omple la seqüència de 8 passos (silenci
   o una nota, com vulguis).
3. **PLAY**: el transport recorre els 8 passos en bucle, al tempo marcat.
   Cada pas amb nota assignada sona com una nota de baix sintetitzada
   (Oscillator + Envelope tipus pluck, igual arquitectura que S8-S9).
4. **STOP**: atura el transport (pots tornar a fer PLAY sense re-marcar tempo).

**Instrument autònom:** el tempo surt només dels teus propis taps — no es
sincronitza per codi amb cap altre instrument de l'ensemble.

## Controls MIDI (per defecte, veure `CONFIG` al codi)

| Nota | Acció |
|---|---|
| 24 (C0) | TAP — marca el tempo |
| 26 (D0) | NEXT_STEP — mou el cursor d'edició al pas següent |
| 28 (E0) | CLEAR_STEP — buida el pas on és el cursor |
| 30 (F0) | PLAY — engega el transport |
| 31 (F#0) | STOP — atura el transport |
| ≥ 32 (qualsevol altra) | Assigna aquesta alçada al pas del cursor |

## Què has de completar (NUCLI MÍNIM, TODO 1-4)

1. `seguent_pas()` — avançar el cursor/pas amb mòdul (`(pas + 1) % n_passos`), com a TP1.
2. `calcula_durada_pas()` — tap-to-tempo: diferència entre dos timestamps consecutius.
3. `toca_avancar_pas()` — decidir si ja ha passat prou temps per canviar de pas, dins del bucle de blocs d'àudio (Bloc 3).
4. `so_del_pas()` — silenci si el pas és buit, o `fes_nota_baix()` (ja donada) si té nota.

## Extensions opcionals (si vas sobrat de temps)

5. **Swing**: retarda lleugerament els passos senars respecte als parells (groove).
6. **Accent per pas**: guarda `(nota, velocity)` a cada pas en lloc de només la nota, i fes-la servir com a `gain`.

## Per què calia tocar `Oscillator`/`Envelope` i no `SamplePlayer`

Un bassline és melòdic (cada pas pot tenir una alçada diferent), no un so
fix — per això es genera amb síntesi (com el Sinte i el Drum-replacer),
no amb un sample pregravat. Això evita també confondre's amb el rol de
Drum-replacer, que ja cobreix la part purament percussiva de l'ensemble.

## Per què `genera_bloc_sortida()` necessita una posició interna

Una nota de baix dura molt més que un sol bloc d'àudio (uns 0.25s = ~20
blocs de 512 mostres). Per això el codi ja donat guarda `self.pos_dins_so`:
cada crida del callback serveix el següent tros de la nota en curs, no la
nota sencera d'un sol cop — el mateix problema que ja vau resoldre amb
`Envelope.process(n)` a S8, aplicat ara a la reproducció completa d'un pas.
