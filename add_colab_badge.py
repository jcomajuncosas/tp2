#!/usr/bin/env python3
"""Insereix un botó 'Open in Colab' a dalt dels notebooks de consulta (patches).

Per defecte NOMÉS toca els recursos/patches_*.ipynb (material de consulta que
s'obre directe des de GitHub). NO toca els notebook.ipynb d'assignment, que van
per Classroom amb còpia per alumne.

Ús:
    python3 add_colab_badge.py --dry-run   # mostra què faria, sense escriure
    python3 add_colab_badge.py             # aplica
Executa'l a l'arrel del repo. Revisa després amb 'git diff'.
"""
import json, glob, sys

OWNER_REPO = "jcomajuncosas/tp2"   # repo PÚBLIC (on l'alumne obre)
BRANCH = "main"
TARGETS = ["**/recursos/patches_*.ipynb"]
# Per incloure també els assignments (NO recomanat amb Model B), afegeix:
#   "**/notebook.ipynb"

DRY = "--dry-run" in sys.argv
BADGE_MARK = "colab-badge.svg"
canvis = 0

files = sorted({f for pat in TARGETS for f in glob.glob(pat, recursive=True)})
for f in files:
    with open(f, encoding="utf-8") as fh:
        nb = json.load(fh)
    cells = nb.setdefault("cells", [])
    if any(BADGE_MARK in "".join(c.get("source", [])) for c in cells):
        continue  # ja té botó → idempotent
    url = f"https://colab.research.google.com/github/{OWNER_REPO}/blob/{BRANCH}/{f}"
    badge = f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})\n"
    cell = {"cell_type": "markdown", "metadata": {}, "source": [badge]}
    canvis += 1
    print(f"--- {f}")
    if DRY:
        print(f"   {url}")
    else:
        cells.insert(0, cell)
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(nb, fh, ensure_ascii=False, indent=1)
        print("   botó afegit")

print(f"\n{canvis} notebook(s) afectats." + ("  (dry-run: no s'ha escrit res)" if DRY else ""))
