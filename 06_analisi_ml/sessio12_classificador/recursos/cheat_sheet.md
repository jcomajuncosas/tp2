# Cheat sheet — Sessió 12
### Bloc 7: Classificadors (KNN, Decision Tree, SVM)

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 12".

---

## 1. Train/test split

```python
from sklearn.model_selection import train_test_split

X = df[['centroid', 'zcr']].values
y = (df['classe'] == 'hihat').astype(int).values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
```

**Per què cal separar dades:** si entrenem i avaluem amb les mateixes dades, el model pot haver-se "après de memòria" les dades sense haver après cap patró general (*overfitting*). Avaluar amb dades NO vistes durant l'entrenament és l'única manera honesta de saber si el model funciona.

`stratify=y` manté la mateixa proporció de classes a train i test que al dataset original — important amb pocs exemples.

---

## 2. El patró universal d'`sklearn`: `fit()` / `predict()`

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

clf = KNeighborsClassifier(n_neighbors=3)
clf.fit(X_train, y_train)        # entrena
y_pred = clf.predict(X_test)     # prediu

from sklearn.metrics import accuracy_score
acc = accuracy_score(y_test, y_pred)
```

**Tots** els classificadors d'`sklearn` segueixen aquest mateix patró, independentment de l'algorisme intern — el codi és pràcticament idèntic per a KNN, Decision Tree o SVM.

---

## 3. Confusion matrix

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=['kick', 'hihat']).plot()
```

| | Predit: kick | Predit: hihat |
|---|---|---|
| **Real: kick** | encerts | errors (kick confós amb hihat) |
| **Real: hihat** | errors (hihat confós amb kick) | encerts |

La diagonal (dalt-esquerra → baix-dreta) són els encerts; fora de la diagonal, els errors i de quin tipus.

---

## 4. Fronteres de decisió: com "pensa" cada algorisme

| Algorisme | Com decideix | Forma típica de la frontera |
|---|---|---|
| **KNN** | Mira les K mostres més properes i vota | Irregular, segueix els punts locals |
| **Decision Tree** | Sèrie de talls "si valor > X" | Rectangles, cantonades a 90° |
| **SVM (rbf)** | Busca el marge més ample entre classes | Corba suau |

```python
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
plt.contourf(xx, yy, Z, alpha=0.3, cmap='RdYlGn')
plt.scatter(X[:, 0], X[:, 1], c=y)
```

⚠️ **Important:** amb features molt separades (com `centroid`/`zcr` en aquest dataset), els tres algorismes acaben dibuixant pràcticament la mateixa frontera — no hi ha ambigüitat real a resoldre. Les diferències es veuen millor amb relacions menys òbvies (per exemple `mfcc_1`/`mfcc_2`).

---

## 5. Llegir l'accuracy amb sentit crític

```python
acc = accuracy_score(y_test, y_pred)
```

Amb un dataset petit (com els 29 sons d'avui), un sol exemple mal classificat ja canvia l'accuracy en més d'un 10%. Un 100% d'accuracy **no és sinònim de "model perfecte"** — pot simplement voler dir que el problema concret era fàcil de separar amb les mostres disponibles. El procediment (split, entrenar, avaluar, interpretar) és el que cal dominar; el número concret s'ha de llegir sempre en context (mida del dataset, dificultat del problema).

---

## 6. Resum del flux complet

| Pas | Codi | Per què |
|---|---|---|
| Separar dades | `train_test_split(..., stratify=y)` | Avaluació honesta, sense overfitting |
| Entrenar | `clf.fit(X_train, y_train)` | El model n'aprèn el patró |
| Predir | `clf.predict(X_test)` | Aplicar-ho a dades noves |
| Avaluar | `accuracy_score()`, `confusion_matrix()` | Mesurar com de bé funciona |
| Interpretar | Fronteres de decisió, context del dataset | Entendre el "per què", no només el número |
