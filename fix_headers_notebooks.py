#!/usr/bin/env python3
"""Neteja la capçalera (cel·la 0) de cada notebook.ipynb per al flux Model B
(còpia per alumne via Classroom). Treu el text dirigit al docent i la
instrucció obsoleta de 'Save a copy in Drive', i insereix el bloc 'Com funciona'.

Ús:
    python3 fix_headers_notebooks.py --dry-run   # mostra què faria, sense escriure
    python3 fix_headers_notebooks.py             # aplica els canvis
Executa'l a l'arrel del repo. Després revisa amb 'git diff'.
"""
import json, glob, re, sys

DRY = "--dry-run" in sys.argv

MODEL_B = ("**Com funciona:** Aquest notebook és la teva còpia personal, generada des de la "
           "teva tasca del Classroom. Els canvis es desen automàticament al teu Drive mentre "
           "treballes. Quan acabis, torna a la tasca del Classroom i prem **Lliura**. No cal "
           "fer «Desa una còpia»: ja estàs treballant sobre la teva.")

def drop(par):
    p = par.strip()
    return (p.startswith("**Instruccions de muntatge:**")
            or p.startswith("**Com obrir aquest notebook:**")
            or "Pes: dins del 40%" in p
            or "còpia individual per alumne" in p)

canvis = 0
for f in sorted(glob.glob("**/notebook.ipynb", recursive=True)):
    with open(f, encoding="utf-8") as fh:
        nb = json.load(fh)
    cells = nb.get("cells", [])
    if not cells or cells[0].get("cell_type") != "markdown":
        continue
    src = "".join(cells[0].get("source", []))
    paras = re.split(r"\n\s*\n", src)
    kept = [p for p in paras if not drop(p)]
    if not any("**Com funciona:**" in p for p in kept):
        idx = next((i for i, p in enumerate(kept) if p.strip().startswith("### ")), None)
        if idx is None:
            idx = next((i for i, p in enumerate(kept) if p.strip().startswith("# ")), -1)
        kept.insert(idx + 1, MODEL_B)
    new_src = "\n\n".join(p.strip("\n") for p in kept).strip() + "\n"
    if new_src == src:
        continue
    canvis += 1
    print(f"--- {f} ---")
    if DRY:
        print(new_src)
    else:
        cells[0]["source"] = new_src.splitlines(keepends=True)
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(nb, fh, ensure_ascii=False, indent=1)
        print("  actualitzat")

print(f"\n{canvis} notebook(s) afectats." + ("  (dry-run: no s'ha escrit res)" if DRY else ""))
