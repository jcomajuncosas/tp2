# Drum-replacer (beatbox)

Converteix el teu beatbox en percussió sintètica, mantenint el ritme exacte que toques.

## Com funciona (dues fases, ja donades)

**Fase 1 — ENSENYAR (classificació SUPERVISADA, exactament com S11-S12):**
Abans de tocar el loop real, graves uns quants exemples del teu propi so vocal per a cada classe (per exemple, "tssh" per al hihat, "bum" per al kick), etiquetats per tu mateix (perquè els graves per separat, ja saps quin és quin). Amb aquests exemples s'entrena un KNN — el mateix pipeline (features → `fit()`) que ja coneixeu, només que ara el dataset és el teu propi vocabulari sonor, no un fitxer extern.

```
IDLE --[REC_KICK]--> GRAVANT_KICK --[STOP_REC]--> IDLE   (repeteix uns quants cops)
IDLE --[REC_HIHAT]--> GRAVANT_HIHAT --[STOP_REC]--> IDLE  (repeteix uns quants cops)
IDLE --[TRAIN]--> LLEST   (entrena amb totes les referències acumulades)
```

**Fase 2 — TOCAR:**
```
LLEST --[REC]--> ESCOLTANT --[PLAY]--> REPRODUINT --[STOP]--> LLEST
```
1. **REC**: toca el teu ritme lliurement. Cada cop es detecta per energia i es classifica amb el model ja entrenat a la Fase 1.
2. **PLAY**: el loop es tanca (la seva durada és la del que acabes de tocar) i es reprodueix indefinidament substituint cada cop pel so sintètic de la classe detectada — ja des del primer cicle, perquè el model ja sabia classificar abans de començar.
3. **STOP**: torna a LLEST (pots fer un altre REC sense haver de re-ensenyar).

**Instrument autònom:** no envia ni rep res d'altres instruments de l'ensemble.

## Controls MIDI (per defecte, veure `CONFIG` al codi)

| Nota | Acció |
|---|---|
| 24 (C0) | REC_KICK — comença a gravar referències de kick |
| 26 (D0) | REC_HIHAT — comença a gravar referències de hihat |
| 28 (E0) | STOP_REC — atura la gravació (repetible) |
| 30 (F0) | TRAIN — entrena el classificador |
| 36 (C1) | REC — captura el loop real |
| 38 (D1) | PLAY — tanca el loop i el reprodueix substituït |
| 40 (E1) | STOP — atura tot |

## Què has de completar (NUCLI MÍNIM, TODO 1-4)

1. `hi_ha_trigger()` — detector de cop per energia (RMS), Bloc 3.
2. `extreu_features_cop()` — centroid + ZCR d'un cop capturat, Bloc 6.
3. `entrena_classificador()` — KNN supervisat amb les teves referències etiquetades, Bloc 7 (exactament `prepara_dades()`/`entrena_i_avalua()` de S12, adaptat).
4. `so_substitut()` — tria entre `fes_kick()`/`fes_hihat()` (ja donades, Bloc 5/S10).

## Extensions opcionals (si vas sobrat de temps)

5. **Overdub**: capturar un segon loop superposat sense esborrar el primer.
6. **Més classes**: afegeix `REC_SNARE` i una tercera classe (snare = Oscillator greu + Noise combinats, com al Challenge 2 de S10).

## Per què cal gravar referències abans de tocar

A diferència de S11-S12 (dataset extern ja preparat i etiquetat), aquí no hi ha cap dada prèvia sobre com sona EL TEU beatbox — cada persona el fa diferent. La fase ENSENYAR soluciona això exactament igual que ho faríeu amb qualsevol classificador real: primer cal exemples etiquetats, després `fit()`, després `predict()` sobre dades noves (els cops del loop). És el mateix pipeline del curs, només que ara la captura de dades la feu vosaltres mateixos en directe.

**Consell pràctic:** com més diferenciats siguin els teus dos sons vocals (un clarament greu, un clarament agut/sorollós) i com més referències gravis (4-6 de cada com a mínim), més fiable serà la classificació del loop real.
