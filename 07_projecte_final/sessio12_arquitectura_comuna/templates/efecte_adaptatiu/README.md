# Efecte adaptatiu

Un instrument acoblat (jack/interface d'àudio) passa per 3 efectes
simultanis — distorsió, filtre passa-baixos, tremolo — cadascun modulat
contínuament pel propi timbre de qui toca. No hi ha "controls" en el
sentit MIDI: l'únic control és com sona l'instrument moment a moment.

## Com funciona

Cada bloc d'àudio que entra es passa per 3 anàlisis tímbriques en paral·lel:

| Descriptor | Què mesura | Per defecte mou |
|---|---|---|
| RMS (energia) | Quant de fort toques | Quantitat de distorsió |
| Centroide espectral | Brillantor del so | Cutoff del filtre passa-baixos |
| Spectral flatness | Tonal (pic clar) ↔ sorollós (espectre pla) | Profunditat del tremolo |

Després, el senyal passa per la cadena **distorsió → filtre → tremolo**,
amb els paràmetres ja actualitzats segons el que s'acaba d'analitzar.
Tot passa dins del mateix bloc: el so reacciona al timbre en temps real.

**Instrument autònom:** només processa la teva pròpia entrada — no
necessita ni envia res a cap altre instrument de l'ensemble.

## Què has de completar (NUCLI MÍNIM, TODO 1-2)

1. `calcula_flatness()` — spectral flatness a mà, amb FFT (`np.fft.rfft`,
   ja conegut de S11): ràtio entre mitjana geomètrica i mitjana aritmètica
   de l'espectre de magnituds. RMS i centroide ja venen donats (via
   librosa, igual que a S11) perquè ja en coneixeu la mecànica — flatness
   és l'únic que no heu calculat mai abans.
2. `escala()` — converteix un valor d'un rang d'entrada (p.ex. el rang
   típic del centroide) a un rang de sortida (p.ex. el rang útil del
   cutoff del filtre). És la peça que connecta qualsevol descriptor amb
   qualsevol paràmetre d'efecte.

## Zona d'experimentació (no és un TODO tècnic — és la part musical)

La funció `connecta_descriptors_amb_efectes()` decideix quin descriptor
mou quin paràmetre. Les connexions per defecte (RMS→distorsió,
centroide→filtre, flatness→tremolo) són només un punt de partida — un
cop el nucli (TODO 1-2) funcioni, és cosa vostra:

- Intercanviar quin descriptor mou quin paràmetre.
- Provar corbes no lineals dins de `escala()` (per exemple `valor**2`
  abans d'escalar, per a una resposta més brusca).
- Fer que un sol descriptor moduli dos paràmetres alhora.
- Desactivar un efecte (deixar el seu paràmetre fix) i centrar-vos en
  com interactuen només els altres dos.

Aquesta és la decisió realment creativa del rol: el "cablejat" entre el
que sona i com reacciona.

## Efectes ja construïts (no cal tocar-los)

- **Distorsió** — clipping, mateix patró que `distorsio_callback` de S5.
- **Filtre passa-baixos** — IIR d'1 pol (`y[n] = y[n-1] + α(x[n]-y[n-1])`),
  amb estat persistent entre blocs (per això el so "decau" de forma real
  i no canvia de cop quan canvies de timbre).
- **Tremolo** — un `LFO` modulant l'amplitud del senyal (AM), la mateixa
  idea que S9 ja esmenta com a aplicació de l'LFO global del DX7
  ("vibrato i/o tremolo"), aquí aplicada de debò.

## Per què no hi ha onsets ni ZCR

Els onsets (atacs/cops) ja són el terreny del Drum-replacer — aquí ens
centrem en **modulació tímbrica contínua**, no en esdeveniments puntuals.
ZCR es va descartar perquè és un proxy molt indirecte del timbre
(útil per distingir percussió tonal/sorollosa, com al Drum-replacer, però
poc interessant per modular un efecte contínuament); spectral flatness
fa una feina semblant però d'una manera més directa i amb més resolució.
