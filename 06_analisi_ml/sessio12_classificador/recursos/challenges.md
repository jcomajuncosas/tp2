# Challenges opcionals — Sessió 12
### Per a qui vulgui aprofundir fora de classe (NO avaluat, NO contingut de classe)

---

## Challenge 1 — Cross-validation: una avaluació més robusta

Amb un dataset tan petit, un sol train/test split pot donar resultats que depenen molt de "quina sort" hem tingut amb la separació. La **validació creuada** (cross-validation) repeteix el procés diverses vegades amb particions diferents:

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(clf, X, y, cv=5)  # 5 particions diferents
print(f"Accuracy mitjana: {scores.mean():.2%} (+/- {scores.std():.2%})")
```

**Experimenta:** aplica-ho als tres classificadors d'avui. Els resultats varien gaire respecte al split únic que vau fer al repte? Per què creus que `cross_val_score` dona una estimació més fiable que un sol split, especialment amb pocs exemples?

---

## Challenge 2 — Ampliar a més classes

Si vas fer el Challenge 3 de la Sessió 11 (ampliar el dataset amb una tercera classe), repeteix avui l'exercici de classificació amb 3 classes en lloc de 2.

**Pregunta per reflexionar:** la confusion matrix, com canvia de forma amb 3 classes en lloc de 2? Segueix sent fàcil "llegir-la" d'un cop d'ull?

---

## Challenge 3 — Random Forest: un "comitè" d'arbres

Un Random Forest entrena molts Decision Trees diferents (cadascun amb una mostra aleatòria de dades) i fa que "votin" la classe final:

```python
from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators=50, random_state=42)
```

**Experimenta:** compara'n l'accuracy i la frontera de decisió amb el Decision Tree simple d'avui. La frontera és més o menys "esglaonada"? Per què creus que combinar molts arbres sol funcionar millor que un de sol?

---

## Challenge 4 — Provar amb un dataset propi

Si vas fer el Challenge 1 de la Sessió 10 (FM mostra a mostra) o el Challenge 2 (ampliar el kit de percussió amb un snare), genera el teu propi petit conjunt de sons sintètics (amb les teves classes de S8-S10) i repeteix tot el pipeline d'avui: extreu features → entrena classificadors → visualitza fronteres.

**Pregunta per reflexionar:** amb sons sintètics (que tu controles completament), esperaries que la classificació sigui més fàcil o més difícil que amb els sons reals d'avui? Per què?

---

## Per què aquests challenges queden fora de classe

El docent ha decidit explícitament no incloure'ls a la Sessió 12: la cross-validation (Challenge 1) és una millora metodològica important però no imprescindible per entendre el concepte bàsic d'avaluació; ampliar a més classes (Challenge 2) i Random Forest (Challenge 3) són extensions naturals que no aporten conceptes nous respecte al que ja s'ha vist; i generar el propi dataset (Challenge 4) requereix temps de síntesi que s'allunya del focus d'avui (classificació, no generació). Són aquí per a qui vulgui aprofundir-hi pel seu compte, especialment de cara al projecte final si el rol "efecte adaptatiu" acaba necessitant classificació en algun moment.
