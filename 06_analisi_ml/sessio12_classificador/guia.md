# Sessió 12 — Bloc 7: Classificadors (KNN, Decision Tree, SVM)

**Bloc temàtic:** 06_analisi_ml
**Tipus de sessió:** Estàndard, tancament del recorregut tècnic abans del projecte final.
**Durada:** 2h
**Entorn:** Colab (continuació de S11).

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:25 – 1:05 | Demo guiada (split, 3 classificadors, fronteres, confusion matrix) | `recursos/patches_bloc7.ipynb` (Colab) |
| 1:05 – 1:50 | Workshop / mini-repte | `notebook.ipynb` (Colab) |
| 1:50 – 2:00 | Tancament, preview projecte final | — |

---

## Objectius

1. Entendre per què cal separar dades d'entrenament i de test (overfitting, avaluació honesta).
2. Conèixer el patró universal `fit()`/`predict()` d'`sklearn`, aplicat a tres algorismes diferents (KNN, Decision Tree, SVM).
3. Saber llegir una confusion matrix i una accuracy amb sentit crític (no només com a número absolut).
4. Visualitzar i interpretar fronteres de decisió — entendre que diferents algorismes "pensen" de manera diferent encara que arribin a resultats similars.
5. Tancar el recorregut tècnic del curs (Blocs 1-7) abans d'entrar al projecte final.

## Decisions de disseny importants (llegir abans d'ensenyar)

**Per què tres classificadors (KNN, Decision Tree, SVM) i no només un:** es valora explícitament comparar-los, no per determinar "quin és millor" (amb 29 mostres, qualsevol diferència d'accuracy té poca significació estadística — ho diem explícitament als alumnes cada vegada que apareix un número), sinó per veure que **algorismes diferents resolen el mateix problema amb lògiques diferents**. SVM es va afegir a la proposta inicial (KNN + Decision Tree) perquè amb un dataset petit i ben separat és un cas d'ús perfecte per introduir-lo sense que pateixi per manca de dades.

**Per què la part de "fronteres de decisió" usa `mfcc_1`/`mfcc_2` i NO `centroid`/`zcr`:** es va validar numèricament que amb `centroid`/`zcr` (la combinació "òbvia" i ja coneguda de S11) els tres algorismes dibuixen pràcticament la mateixa frontera (diferència 0-0.5% entre les seves prediccions sobre tota la graella) — el problema és tan fàcilment separable que no hi ha marge real per diferenciar com "pensa" cadascun. En canvi, amb `mfcc_1`/`mfcc_2` les fronteres difereixen molt més (8-37% segons el parell d'algorismes comparat) **mantenint el mateix 100% d'accuracy als tres** — combinació validada explícitament abans d'escriure el material perquè no es perdés ni rigor (l'accuracy es manté) ni riquesa visual (les fronteres sí es diferencien). El Decision Tree dibuixa una frontera amb cantonades rectes (talls perpendiculars als eixos, un a un); KNN una frontera irregular que segueix els punts locals; SVM (kernel rbf) una corba suau de marge màxim.

**Per què s'insisteix explícitament en la manca de significació estadística del 100% d'accuracy:** amb només 29 mostres (9 de test), un sol so mal classificat ja canvia l'accuracy en més d'un 10%. Es decideix mostrar igualment el procediment complet (és l'estàndard que han d'aprendre a aplicar i interpretar correctament en qualsevol context, incloent datasets grans), però acompanyat sempre d'una lectura honesta del que el número vol dir realment en aquest cas concret — decisió presa explícitament després de discussió amb el docent per no transmetre una falsa sensació de rigor estadístic amb un dataset de joguina.

**Per què aquesta és l'última sessió purament tècnica:** tanca el recorregut Blocs 1-7 (NumPy → WAV → temps real → MIDI → síntesi → FFT/features → classificació). A partir de la Sessió 13 (calendari) comença el projecte final, que reutilitza tot aquest bagatge tècnic sense introduir-ne de nou de manera sistemàtica.

## Connexions amb sessions anteriors

- **Sessió 11:** el dataset (`dataset/kick/`, `dataset/hihat/`) i el pipeline de features (centroid, ZCR, MFCC) es reutilitzen directament — el `features_percussio.csv` és l'input d'avui.
- **Sessió 2 (librosa):** ja se sabia extreure features; avui s'aprèn què fer-ne (entrenar un model).
- **Tot el curs (Blocs 1-6):** aquesta sessió tanca el recorregut tècnic complet abans del projecte final.

## Materials necessaris

- Accés al `dataset/` de S11 (`06_analisi_ml/sessio11_fft_features/dataset/`) — el notebook regenera el CSV de features automàticament si cal, no calen passos manuals previs.
- `scikit-learn` (`sklearn`), ja disponible per defecte a Colab.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `notebook.ipynb` — repte de l'alumne: `prepara_dades()`, `entrena_i_avalua()`, comparativa dels 3 classificadors, amb autotests
- `recursos/cheat_sheet.md` — resum del patró fit/predict, train/test split, confusion matrix, fronteres de decisió
- `recursos/warmup_quiz.md` — preguntes per a Google Forms
- `recursos/slides_outline.md` — diapositives
- `recursos/patches_bloc7.ipynb` — demo Colab guiada
- `recursos/challenges.md` — Challenges opcionals

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Confirmar que el `git clone` funciona des de l'entorn real de Classroom (mateixa nota que a S11 — depèn de si el repositori és públic o privat)
- [ ] Provar el notebook a Colab real abans de la sessió
