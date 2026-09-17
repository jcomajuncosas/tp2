#!/usr/bin/env python3
"""Treu la nota docent '> **Instruccions de muntatge:** ...' de la capçalera
de cada cheat_sheet.md, deixant intacte el contingut de referència.

Ús:
    python3 fix_cheatsheets.py --dry-run   # mostra què faria, sense escriure
    python3 fix_cheatsheets.py             # aplica els canvis
Executa'l a l'arrel del repo. Després revisa amb 'git diff'.
"""
import glob, re, sys

DRY = "--dry-run" in sys.argv
canvis = 0

for f in sorted(glob.glob("**/cheat_sheet.md", recursive=True)):
    txt = open(f, encoding="utf-8").read()
    out, skipping = [], False
    for ln in txt.split("\n"):
        s = ln.lstrip()
        if s.startswith("> **Instruccions de muntatge:**"):
            skipping = True           # comença el blockquote docent
            continue
        if skipping:
            if s.startswith(">"):     # línies de continuació del mateix blockquote
                continue
            skipping = False
        out.append(ln)
    new = re.sub(r"\n{3,}", "\n\n", "\n".join(out))   # col·lapsa blancs sobrants
    if new == txt:
        continue
    canvis += 1
    print(f"--- {f}")
    if DRY:
        print("\n".join(new.split("\n")[:6]))
        print("   ...")
    else:
        open(f, "w", encoding="utf-8").write(new)
        print("   actualitzat")

print(f"\n{canvis} cheat sheet(s) afectats." + ("  (dry-run: no s'ha escrit res)" if DRY else ""))
