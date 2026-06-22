# Warm-up — Sessió 12
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 11 (features)

**A la Sessió 11 vau construir un CSV amb una fila per so i una columna per cada feature (centroid, ZCR, MFCC). Per a què serveix exactament aquesta taula?**

- A) Per emmagatzemar els sons en un format més compacte que WAV
- ✅ B) Perquè és el format que necessita un classificador per aprendre
- C) Per generar gràfics de manera més ràpida
- D) Per convertir els sons a un altre sample rate diferent

---

### Pregunta 2 — Intuïció: per què separar dades

**Si entrenéssiu un classificador amb TOTES les vostres dades, i després el "comprovéssiu" amb les mateixes dades que ha vist durant l'entrenament... creieu que el resultat us diria si el model funciona bé amb sons NOUS?**

- A) Sí, si funciona bé amb les dades d'entrenament, anirà igual de bé amb dades noves
- ✅ B) No, podria haver-se après les dades de memòria sense aprendre cap patró general
- C) No, perquè mai es pot avaluar realment un classificador
- D) Només es pot saber repetint l'entrenament cent vegades seguides

---

### Pregunta 3 — Predicció (lectura de codi)

```python
clf = KNeighborsClassifier(n_neighbors=3)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
```

**Què fa exactament la línia `clf.predict(X_test)`?**

- A) Torna a entrenar el model des de zero amb X_test
- ✅ B) Prediu la classe de cada mostra de X_test amb el que ha après amb fit()
- C) Calcula directament l'accuracy del model entrenat
- D) Elimina les dades de X_test de la memòria

---

### Pregunta 4 — Intuïció: KNN vs. Decision Tree

**KNN decideix la classe d'un punt nou mirant els seus veïns més propers. Un Decision Tree decideix fent preguntes del tipus "el valor X és més gran que Y?". Quina forma esperaríeu que tingui la frontera de cadascun?**

- A) Exactament la mateixa forma, independentment de l'algorisme usat
- ✅ B) KNN: frontera irregular que segueix els punts; arbre: talls rectes
- C) KNN sempre dona una línia recta; l'arbre sempre una corba suau
- D) Cap dels dos genera mai una frontera visualitzable

---

### Pregunta 5 — Concepte clau: significació d'un 100% d'accuracy

**Si un classificador entrenat amb només 10 mostres dona 100% d'accuracy sobre 3 mostres de test, què en penseu?**

- A) És una prova sòlida que el model és perfecte sempre
- ✅ B) Amb tan poques mostres, cal interpretar el resultat amb molta cura
- C) Un 100% sempre vol dir que el dataset no és vàlid
- D) Com més petit el dataset, més fiable és el resultat obtingut

---

### Pregunta 6 — Repàs ampli del curs

**Des del Bloc 1 fins avui, heu après a generar so, processar-lo en temps real, i analitzar-lo (FFT, features). Avui, amb un classificador, què feu exactament amb aquesta informació?**

- A) Tornar a generar el so original a partir de les features
- ✅ B) Fer que un model aprengui a predir una categoria a partir de números
- C) Comprimir els sons perquè ocupin menys espai al disc
- D) Convertir les features de nou a un fitxer d'àudio WAV

---

### Pregunta 7 — Confusion matrix

**Si la confusion matrix d'un classificador té tots els valors a la diagonal (cap fora), què significa?**

- A) El model ha fallat completament en totes les prediccions
- ✅ B) El model ha encertat totes les prediccions sobre el conjunt avaluat
- C) Les dades d'entrada estan corruptes o mal formatades
- D) Cal canviar urgentment l'algorisme de classificació triat
