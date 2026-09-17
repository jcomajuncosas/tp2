#!/usr/bin/env bash
set -euo pipefail

# =========================================================================
# init-privat.sh  —  ÚS ÚNIC
# -------------------------------------------------------------------------
# Bolca TOT el contingut i l'historial del repo PÚBLIC actual (origin)
# cap a un nou repo PRIVAT, que passarà a ser la teva font de veritat.
#
# Executa'l des de l'arrel del repo local actual (TP2_2627).
# Depèn del teu ~/.ssh/config que enruta github.com pel port 443.
# =========================================================================

# ---- CONFIG (edita aquesta línia) --------------------------------------
PRIVATE_REMOTE="git@github.com:jcomajuncosas/tp2-privat.git"   # <-- posa la URL del teu repo privat
PRIVATE_REMOTE_NAME="privat"
# ------------------------------------------------------------------------

# 1) Comprova que som dins d'un repo git i situa't a l'arrel
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✗ No ets dins d'un repositori git. Executa'l a l'arrel de TP2_2627." >&2
  exit 1
fi
cd "$(git rev-parse --show-toplevel)"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "▸ Branca actual: $BRANCH"
echo -n "▸ origin (públic): "; git remote get-url origin || { echo "✗ No hi ha remot 'origin'." >&2; exit 1; }
echo

# 2) Comprova / crea el repo privat
if git ls-remote "$PRIVATE_REMOTE" >/dev/null 2>&1; then
  echo "▸ El repo privat ja existeix: $PRIVATE_REMOTE"
else
  echo "▸ El repo privat no existeix (o no hi tens accés encara)."
  if command -v gh >/dev/null 2>&1; then
    slug="$(echo "$PRIVATE_REMOTE" | sed -E 's#.*[:/]([^/]+/[^/]+)\.git$#\1#')"
    read -r -p "  Crear-lo ara com a privat amb gh ($slug)? [s/N] " ans
    if [[ "$ans" =~ ^[sSyY]$ ]]; then
      gh repo create "$slug" --private
    else
      echo "  D'acord: crea'l manualment (buit, SENSE README) i torna a executar." >&2
      exit 1
    fi
  else
    echo "  Instal·la 'gh' o crea el repo privat buit manualment i torna a executar." >&2
    exit 1
  fi
fi
echo

# 3) Afegeix / actualitza el remot privat
if git remote get-url "$PRIVATE_REMOTE_NAME" >/dev/null 2>&1; then
  git remote set-url "$PRIVATE_REMOTE_NAME" "$PRIVATE_REMOTE"
else
  git remote add "$PRIVATE_REMOTE_NAME" "$PRIVATE_REMOTE"
fi

# 4) Empeny TOT: totes les branques i tots els tags (historial complet)
echo "▸ Enviant tot l'historial al privat…"
git push "$PRIVATE_REMOTE_NAME" --all
git push "$PRIVATE_REMOTE_NAME" --tags

# 5) Fes que el teu 'git push' local vagi al PRIVAT per defecte (xarxa de seguretat)
if git rev-parse --verify "$PRIVATE_REMOTE_NAME/$BRANCH" >/dev/null 2>&1; then
  git branch --set-upstream-to="$PRIVATE_REMOTE_NAME/$BRANCH" "$BRANCH" >/dev/null
  echo "▸ Upstream de '$BRANCH' fixat a '$PRIVATE_REMOTE_NAME'."
fi

echo
echo "✓ Fet. El privat allotja TOT amb historial: $PRIVATE_REMOTE"
echo
echo "  A partir d'ara el teu flux és:"
echo "    1) edita en local"
echo "    2) git add -A && git commit -m \"…\" && git push        (va al PRIVAT)"
echo "    3) ./sync-public.sh                                     (publica al PÚBLIC)"
echo
echo "  ⚠ No facis mai 'git push origin' a mà: el públic només el toca sync-public.sh."
