#!/usr/bin/env python3
"""Mou els exemples.py de l'arrel de cada sessió a la seva carpeta recursos/,
amb git mv. Per defecte fa NOMÉS un informe; cal --apply per moure de debò.

Ús:
    python3 move_exemples.py            # informe: què es mouria i possibles trencaments
    python3 move_exemples.py --apply    # fa els git mv
Executa'l a l'arrel del repo, amb l'arbre net.
"""
import glob, os, subprocess, sys

APPLY = "--apply" in sys.argv
BIN_EXT = (".wav", ".mid", ".png", ".jpg", ".jpeg", ".pdf", ".docx", ".pyc")

# exemples.py que són a l'arrel d'una sessió (no ja dins recursos/)
srcs = sorted(f for f in glob.glob("**/exemples.py", recursive=True)
              if os.path.basename(os.path.dirname(f)) != "recursos")

if not srcs:
    print("No hi ha cap exemples.py per moure (ja deuen ser tots a recursos/).")
    sys.exit(0)

print("=== PLA DE MOVIMENT ===")
for s in srcs:
    print(f"  {s}  ->  {os.path.join(os.path.dirname(s), 'recursos', 'exemples.py')}")

print("\n=== COMPROVACIÓ 1: referències a 'recursos/' DINS de cada exemples.py ===")
print("(si carrega media amb ruta 'recursos/...', en moure'l caldrà treure-hi el 'recursos/')")
any_internal = False
for s in srcs:
    hits = [(i, l.rstrip()) for i, l in enumerate(open(s, encoding="utf-8"), 1) if "recursos/" in l]
    if hits:
        any_internal = True
        print(f"\n  {s}:")
        for i, l in hits:
            print(f"    L{i}: {l[:100]}")
if not any_internal:
    print("  cap. OK")

print("\n=== COMPROVACIO 2: altres fitxers que anomenen 'exemples.py' ===")
print("(enllaços o mencions que potser caldria actualitzar després del moviment)")
tracked = [p for p in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n") if p]
any_external = False
for p in tracked:
    if p in srcs or p.lower().endswith(BIN_EXT):
        continue
    try:
        if "exemples.py" in open(p, encoding="utf-8", errors="ignore").read():
            any_external = True
            print(f"  {p}")
    except Exception:
        pass
if not any_external:
    print("  cap. OK")

if not APPLY:
    print("\n(informe només. Revisa'l; torna a executar amb --apply per moure amb git mv.)")
    sys.exit(0)

print("\n=== MOVENT (git mv) ===")
for s in srcs:
    d = os.path.join(os.path.dirname(s), "recursos", "exemples.py")
    os.makedirs(os.path.dirname(d), exist_ok=True)
    r = subprocess.run(["git", "mv", s, d])
    print(f"  {'OK' if r.returncode == 0 else 'ERROR'}  {s} -> {d}")
print("\nFet. Revisa amb 'git status', després commit + push + ./sync-public.sh.")
