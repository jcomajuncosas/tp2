# Sessió 11 — Bloc 6: FFT pràctic i extracció de features

**Bloc temàtic:** 06_analisi_ml
**Tipus de sessió:** Estàndard, però amb canvi d'entorn respecte a S9-S10.
**Durada:** 2h
**Entorn:** Colab (no Thonny). FFT i extracció de features no necessiten temps real ni hardware d'àudio — es torna a l'entorn de S1-S8 després de tres sessions seguides a Thonny (S9-S10).

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:25 – 1:05 | Demo guiada (FFT manual + features amb librosa) | `recursos/patches_bloc6.ipynb` (Colab) |
| 1:05 – 1:50 | Workshop / mini-repte | `notebook.ipynb` (Colab) |
| 1:50 – 2:00 | Tancament, preview Sessió 12 | — |

---

## Objectius

1. Entendre què és una FFT a nivell conceptual i pràctic amb `np.fft.rfft()`, sense cap llibreria d'àudio — pas necessari abans d'usar qualsevol abstracció.
2. Saber per què, un cop entès el concepte, NO té sentit reimplementar features espectrals a mà — usar `librosa` (centroide espectral, ZCR, MFCC) per eficiència i fiabilitat.
3. Construir un mini-dataset real de features (CSV) a partir d'un conjunt petit i controlat de sons de percussió (kick/hi-hat), amb llicència verificada.
4. Deixar aquest dataset llest i validat per al classificador de la Sessió 12 — primer contacte amb un pipeline complet "àudio → features → dades tabulars per a ML".

## Decisions de disseny importants (llegir abans d'ensenyar)

**Per què tornem a Colab després de tres sessions a Thonny:** S9 i S10 necessitaven temps real i MIDI (Thonny obligatori). FFT i extracció de features sobre fitxers ja existents no tenen aquest requisit — Colab torna a ser l'entorn natural, com a S1-S8. Val la pena explicitar-ho als alumnes perquè no s'estranyin del canvi.

**Per què FFT manual (NumPy) i NO amb `librosa` directament:** la decisió és ensenyar primer el concepte pelat (`np.fft.rfft()`, freqüències, magnitud) abans d'amagar-lo darrere d'una funció com `librosa.feature.spectral_centroid()`. Sense aquest pas, "centroide espectral" seria una caixa negra sense cap ancoratge matemàtic.

**Per què NO s'implementen les features (centroide, MFCC) a mà, a diferència de la FFT:** un cop entesa la FFT, calcular el centroide espectral a mà no aportaria cap concepte nou (és una mitjana ponderada) i sí consumiria temps valuós d'una sessió ja densa de cara a ML. La decisió explícita és: **FFT manual breu per al concepte, `librosa` per a la resta** — es comunica als alumnes com una tria conscient ("reinventar la roda no ensenya res que ja no haguéssim après"), no com una limitació de temps amagada.

**Per què es descarta Vamp (via `signalflow`) per a aquesta sessió:** `signalflow` té suport nadiu per a plugins Vamp (`VampAnalysis`), però Vamp és tot un ecosistema extern de plugins natius C++ que cal instal·lar separadament al sistema — exactament el tipus de fragilitat d'instal·lació que ja vam patir amb `pyo` (veure README del repositori). Per a una sola sessió introductòria de features, `librosa` (pure-Python+NumPy, ja coneguda des de S2, sense dependències natives) és l'opció correcta. Vamp queda fora del contingut de classe completament (ni tan sols com a Challenge, per no introduir el mateix risc d'instal·lació en un moment on no aporta res que `librosa` no doni ja).

**Per què un dataset extern petit i NO el kit de percussió propi de S10:** es va considerar reaprofitar els sons de `Kick`/`Noise` que cada alumne va construir a S10, però es va descartar perquè els paràmetres (freq_start, drop_time, etc.) són lliures per alumne i `Noise` és literalment aleatori — les features resultants no serien consistents ni comparables entre alumnes. En lloc d'això, s'usa un **mini-dataset extern, fix i idèntic per a tothom**.

**Procés de selecció del dataset (per transparència):** es van descartar dues alternatives abans d'arribar a la definitiva:
- `tidalcycles/Dirt-Samples` (GitHub): organització i mida ideals, però **sense llicència formal explícita** per al conjunt — una issue oberta del propi repositori demanava encara afegir metadades de llicència. Descartat per prudència.
- `crlandsc/tiny-audio-diffusion-drums` (Hugging Face): llicència `CC-BY-NC-4.0`, i l'autor mateix indica explícitament que les mostres "no es poden fer servir per entrenar cap model comercial, però es poden usar en contextos personals i de recerca" — ambigüitat de NC excessiva per a material de curs reutilitzable. Descartat.
- **Triat: "Freesound One-Shot Percussive Sounds Dataset"** (Ramires et al., Music Technology Group - UPF, Zenodo DOI [10.5281/zenodo.3665275](https://doi.org/10.5281/zenodo.3665275)). Conté `licenses.json` amb la llicència individual de cada un dels 10254 sons. Es van filtrar només els sons amb llicència CC0 1.0 o CC-BY 3.0 (9535 de 10252 entrades), i d'aquests es va seleccionar manualment una mostra de 14 kicks + 15 hihats amb noms de fitxer inequívocs, evitant efectes/loops/marcadors. Atribució completa per fitxer a `dataset/CREDITS.md`.

**Validació del dataset (feta abans de donar-lo per bo):** pipeline complet (FFT manual → centroide/ZCR/MFCC amb `librosa` → classificador KNN de prova amb validació creuada 5-fold) executat de cap a cap. Resultat: **100% d'accuracy**, separació total per centroide (kicks 106-1340Hz, hihats 2848-5415Hz, sense solapament) — confirma que el dataset és clarament separable i adequat per a un primer exercici introductori, sense ser trivial (29 sons reals de fonts/autors diferents, no sintètics idèntics).

## Connexions amb sessions anteriors

- **Bloc 1-2 (NumPy, WAV):** un so segueix sent "un array de números" — la FFT és només una altra transformació matemàtica sobre aquest array, no un concepte aliè.
- **Sessió 2 (librosa bàsic):** ja coneguda; avui se n'aprofundeix l'ús per a features, no només per a I/O.
- **Sessió 7 (MIDI, GM):** la idea de "categories discretes de percussió" (kick, hi-hat...) ja s'havia vist conceptualment al mapa General MIDI.
- **Sessió 10 (Kick/Noise propis):** el repte de S10 va explorar el mateix domini (síntesi de percussió); avui s'aborda des de l'altre extrem (anàlisi en lloc de síntesi) — connexió explícita a fer a classe.

## Materials necessaris

- `dataset/` (ja inclòs al repositori: `kick/`, `hihat/`, `CREDITS.md` — 368KB en total, 29 fitxers WAV).
- Cap instal·lació addicional a Colab (`numpy`, `librosa`, `pandas`, `matplotlib` ja hi són per defecte).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `notebook.ipynb` — repte de l'alumne: `freq_pic()`, `extreu_features()`, construcció del CSV final, amb autotests
- `dataset/` — mini-dataset de percussió (kick/hihat), amb `CREDITS.md` d'atribució completa
- `recursos/cheat_sheet.md` — resum de FFT manual i features amb librosa
- `recursos/warmup_quiz.md` — preguntes per a Google Forms
- `recursos/slides_outline.md` — diapositives
- `recursos/patches_bloc6.ipynb` — demo Colab guiada (FFT + features + visualització)
- `recursos/challenges.md` — Challenges opcionals

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Confirmar que el `git clone` del notebook funciona correctament des de l'entorn real de Classroom (depèn de si el repositori és públic o privat — si privat, caldrà adaptar la instrucció de pujada manual del `dataset/`)
- [ ] Provar el notebook a Colab real (no només al contenidor de desenvolupament) abans de la sessió
