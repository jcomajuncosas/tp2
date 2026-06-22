# Slides — Bloc 7, Sessió 12
### Classificadors: KNN, Decision Tree, SVM

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 15-17 min.

---

### Diapositiva 1 — Portada
**Bloc 7 — Classificació: el primer ML real**
*KNN, Decision Tree, SVM*

---

### Diapositiva 2 — On érem
- Sessió 11: vau construir `features_percussio.csv` (29 sons, centroid/ZCR/MFCC per cadascun)
- Avui: fem que un model aprengui a predir la classe (kick/hihat) a partir d'aquests números
- Últim contingut tècnic abans del projecte final

---

### Diapositiva 3 — Per què cal separar dades
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y
)
```
- 🎤 *Pregunta: si avaluem amb les mateixes dades que hem usat per entrenar, què podria passar?*
- Resposta esperada: el model podria "memoritzar" sense aprendre cap patró real (overfitting)

---

### Diapositiva 4 — El patró universal: fit / predict
```python
clf = KNeighborsClassifier(n_neighbors=3)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
```
- Mateix patró per a QUALSEVOL classificador d'sklearn
- Demo en directe: entrenar KNN sobre el dataset

---

### Diapositiva 5 — Tres classificadors, el mateix codi
```python
classificadors = {
    'KNN': KNeighborsClassifier(n_neighbors=3),
    'Decision Tree': DecisionTreeClassifier(max_depth=3),
    'SVM': SVC(kernel='rbf'),
}
```
- Demo: entrenar els tres, mostrar accuracy de cadascun
- Amb aquest dataset: probablement els tres donen ~100%

---

### Diapositiva 6 — ⚠️ Què vol dir un 100% amb 29 mostres
- Amb només 9 mostres de test, UN sol error ja canvia l'accuracy en més d'un 10%
- Un 100% aquí NO és "el model és perfecte" — és "aquest problema concret era fàcil de separar"
- El que importa: dominar el PROCEDIMENT (split, entrenar, avaluar, interpretar)

---

### Diapositiva 7 — Confusion matrix
```python
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=['kick','hihat']).plot()
```
- Diagonal = encerts; fora de la diagonal = errors (i de quin tipus)
- Demo en directe: confusion matrix dels tres classificadors

---

### Diapositiva 8 — La pregunta d'avui: com "pensa" cada algorisme
- Mateixa accuracy, però... arriben a la mateixa conclusió de la mateixa manera?
- 🎤 *Pregunta: KNN mira veïns propers; un arbre fa preguntes sí/no. Esperaríeu fronteres iguals?*

---

### Diapositiva 9 — Fronteres de decisió (demo en directe)
- Visualització amb `mfcc_1`/`mfcc_2` (relació menys òbvia que centroid/zcr)
- **Decision Tree:** talls rectes, cantonades a 90°
- **KNN:** frontera irregular, segueix els punts locals
- **SVM (rbf):** corba suau, marge màxim

---

### Diapositiva 10 — Per què amb centroid/zcr no es veu aquesta diferència
- Amb features molt separades, el problema és "massa fàcil" — qualsevol algorisme troba la mateixa solució òbvia
- Les diferències entre algorismes es revelen quan el problema és més ambigu
- Lliçó: la "facilitat" d'un problema depèn molt de quines features fas servir

---

### Diapositiva 11 — Workshop: completeu `notebook.ipynb`
- `prepara_dades()`: split amb stratify
- `entrena_i_avalua()`: fit + predict + accuracy
- Comparativa final dels 3 classificadors

---

### Diapositiva 12 — Tancament: tot el recorregut tècnic
- Bloc 1: so com a array → Bloc 2: WAV/librosa → Bloc 3: temps real
- Bloc 4: MIDI → Bloc 5: síntesi → Bloc 6: FFT/features → Bloc 7: classificació
- A partir d'ara: projecte final — reutilitzar tot això en un context propi

---

### Diapositiva 13 — Preview projecte final
- Format "banda": rols compartits (looper/bassline, sinte, drum-replacement, efecte adaptatiu)
- Arquitectura base comuna → variacions individuals → concert col·lectiu (fora de calendari)
- Properes sessions: definir l'arquitectura comuna del projecte
