# Vocoder

"Cantant solista": cantes o parles pel micro (modulador) mentre toques una
nota amb el controlador MIDI (carrier). El resultat és la teva veu amb
l'alçada exacta de la nota que toques — l'efecte vocoder clàssic dels anys
70-80 (Kraftwerk, Bode/Moog Vocoder, EMS Vocoder 5000...).

## Com funciona

Un vocoder de banc de filtres "vintage" divideix tant la teva veu com un
oscil·lador en les mateixes 16 bandes de freqüència, i fa servir l'energia
de cada banda de la veu per "esculpir" l'oscil·lador banda a banda:

```
VEU (micro, modulador)              NOTA MIDI (carrier)
        │                                   │
   [16 filtres banda]                [16 filtres banda]
   (mateixes freqüències)            (mateixes freqüències)
        │                                   │
  [envolupant per banda]                    │
  (Abs + Smooth: "quanta                    │
   energia hi ha ARA en                     │
   aquesta zona")                           │
        │                                   │
        └──────── multiplica per banda ─────┘
                          │
                    SUMA de les 16 bandes
                          │
                       SORTIDA
```

L'oscil·lador (carrier) té sempre la mateixa alçada que la nota MIDI que
toques; la veu (modulador) li dona la "forma" tímbrica — el resultat sona
com si cantessis exactament aquella nota.

**Instrument autònom:** només processa la teva pròpia veu i les teves
pròpies notes — no depèn de cap altre instrument de l'ensemble.

## Controls MIDI

| Acció | Efecte |
|---|---|
| Qualsevol nota (note_on) | Defineix l'alçada del carrier mentre la mantens polsada |
| Deixar anar la nota (note_off) | Tanca l'envolvent del carrier (release) |

**Monofònic**: només sona la darrera nota tocada, no és polifònic (com
correspon a un "cantant solista" que canta una nota a la vegada).

## Les 16 bandes

Repartiment logarítmic entre 100Hz i 8000Hz, amb més densitat a la zona
de formants vocals (300-3000Hz, on viu la intel·ligibilitat de la parla)
— inspirat en el repartiment típic de vocoders clàssics (Bode/Moog ~10
bandes, EMS Vocoder 5000, Roland VP-330):

```
100, 144, 208, 300, 387, 500, 646, 835, 1078, 1392, 1798, 2323, 3000, 4160, 5769, 8000
```

## Què has de completar (NUCLI MÍNIM, TODO 1)

Un sol TODO, però és **la cadena completa del vocoder en si** — banc de
filtres, envolupant i aplicació al carrier són un sol procés en passos
relacionats, no peces independents:

1. Per cada freqüència de `BANDES_HZ`: filtra el modulador amb un
   `BiquadFilter` band-pass centrat en aquesta freqüència.
2. Segueix-ne l'envolupant: `Smooth(Abs(banda_modulador), ...)`.
3. Filtra el carrier amb el mateix `BiquadFilter` a la mateixa freqüència.
4. Multiplica la banda del carrier per l'envolupant del modulador.
5. Suma totes les bandes (`Sum(...)`) per obtenir la sortida final.

Ja donat (no cal tocar-ho): el carrier (`SquareOscillator` + `ADSREnvelope`
amb `gate`), la construcció del `Patch`, i el dispatch MIDI.

## Extensions opcionals (si vas sobrat de temps)

2. **Barreja robot/veu**: afegeix un input `mix` que barregi la sortida
   del vocoder amb la veu original sense processar (0=100% robot,
   1=100% veu neta).
3. **Carrier alternatiu**: prova `SawOscillator`, una FM senzilla (S9),
   o afegeix vibrato amb un `LFO` sobre la freqüència del carrier (com
   al Sinte) per a un caràcter de veu diferent.

## Per què `SquareOscillator` i no `SineOscillator` com a carrier

El filtratge per bandes només pot "esculpir" el que ja hi és present a
l'espectre. Una sinusoide pura no té pràcticament res a les freqüències
de la majoria de bandes — el resultat sonaria molt prim. Un oscil·lador
ric en harmònics (quadrada, dent de serra) dona al banc de filtres
"material" real per treballar a totes les bandes.
