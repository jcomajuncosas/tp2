#!/usr/bin/env bash
set -euo pipefail

# =========================================================================
# sync-public.sh  —  RECURRENT  (v2: degoteig per sessions)
# -------------------------------------------------------------------------
# Publica NOMÉS el material d'estudiant (LLISTA BLANCA) del repo PRIVAT
# cap al repo PÚBLIC, i NOMÉS de les sessions que autoritzis (RELEASED).
# Preserva l'historial públic i reflecteix esborrats: si retens una sessió
# o esborres un fitxer al privat, desapareix del públic.
#
# ⚠ Sincronitza l'estat COMMITEJAT del privat. Abans d'executar:
#      git add -A && git commit -m "…" && git push
#
# Ús:
#   ./sync-public.sh            # mostra resum i demana confirmació abans de publicar
#   ./sync-public.sh --yes      # publica sense preguntar
#   ./sync-public.sh --dry-run  # només mostra què faria (sense commit ni push)
#
# Depèn del teu ~/.ssh/config que enruta github.com pel port 443.
# =========================================================================

# ---- CONFIG (edita) ----------------------------------------------------
PRIVATE_REMOTE="git@github.com:jcomajuncosas/tp2-privat.git"   # font de veritat
PUBLIC_REMOTE="git@github.com:jcomajuncosas/tp2.git"           # mirall filtrat
BRANCH="main"
DATESTR="$(date '+%Y-%m-%d %H:%M')"
COMMIT_MSG="${SYNC_MSG:-Sync material estudiant $DATESTR}"
# ------------------------------------------------------------------------

# ---- SESSIONS ALLIBERADES ----------------------------------------------
# NOMÉS es publiquen les sessions llistades aquí (descomentades).
# Descomenta'n una a mesura que l'obris al Classroom i torna a executar.
# Llista buida = només es publica el README de l'arrel.
RELEASED=(
  'sessio01_reconnexio'
  'sessio02_wav_io'
  # 'sessio03_capture_playback'
  # 'sessio04_buffers_latencia'
  # 'sessio05_efecte_temps_real'
  # 'sessio06_estructura_midi'
  # 'sessio07_sequenciador'
  # 'sessio08_oscil_ladors_classes'
  # 'sessio09_fm_synth'
  # 'sessio10_consolidacio'
  # 'sessio11_fft_features'
  # 'sessio12_classificador'
  # 'sessio12_arquitectura_comuna'   # projecte final (plantilles)
  # 'sessio13_implementacio_rols'
)
# ------------------------------------------------------------------------

# ---- LLISTA BLANCA: NOMÉS aquests tipus de fitxer es publiquen ----------
# Qualsevol fitxer del privat que no encaixi aquí es queda PRIVAT.
WHITELIST=(
  'README.md'
  'exemples.py'
  'assignment.py'
  'notebook.ipynb'
  'teoria_exercicis.ipynb'
  'patches_*.ipynb'
  'cheat_sheet.md'
  'challenges.md'
  'reptes_opcionals.md'
  'CREDITS.md'
  'midisynth.py'
  '*.wav'
  '*.mid'
  # --- plantilles del projecte final (afegeix el nom si en crees de noves) ---
  'sinte.py'
  'drum_replacer.py'
  'efecte_adaptatiu.py'
  'looper_bassline.py'
  'vocoder.py'
)
# Docent / mai públic (la llista blanca ja els deixa fora; aquí per referència):
#   guia.md · slides_outline.md · warmup_quiz.md · build.sh · build_all.sh
#   _solucions/ · *.docx · .DS_Store · __pycache__/
# ------------------------------------------------------------------------

DRY_RUN=0; ASSUME_YES=0
for a in "${@:-}"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ASSUME_YES=1 ;;
    "")        ;;
    *) echo "Opció desconeguda: $a" >&2; exit 2 ;;
  esac
done

command -v rsync >/dev/null || { echo "✗ Cal rsync." >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
echo "▸ Espai temporal: $WORK"

# 1) Clona l'estat committejat del PRIVAT
echo "▸ Clonant privat…"
git clone --quiet --branch "$BRANCH" "$PRIVATE_REMOTE" "$WORK/private"

# 2) Filtra amb la llista blanca:  private -> filtered
echo "▸ Aplicant llista blanca…"
INC=(); for p in "${WHITELIST[@]}"; do INC+=(--include="$p"); done
rsync -a --prune-empty-dirs \
  --exclude='.git' --exclude='.DS_Store' --exclude='__pycache__' \
  --exclude='*.docx' --exclude='_solucions' \
  --include='*/' "${INC[@]}" --exclude='*' \
  "$WORK/private/" "$WORK/filtered/"

# 2b) DEGOTEIG: elimina les sessions que NO estan a RELEASED
#     (les carpetes de sessió són  bloc/sessioNN_*)
shopt -s nullglob
for d in "$WORK"/filtered/*/sessio*; do
  [ -d "$d" ] || continue
  base="$(basename "$d")"
  keep=0
  if [ "${#RELEASED[@]}" -gt 0 ]; then
    for r in "${RELEASED[@]}"; do
      [ "$base" = "$r" ] && keep=1 && break
    done
  fi
  if [ "$keep" -eq 0 ]; then
    rm -rf "$d"
  fi
done
shopt -u nullglob

# 3) Informe
echo
echo "── SESSIONS ALLIBERADES (${#RELEASED[@]}) ──"
if [ "${#RELEASED[@]}" -eq 0 ]; then
  echo "  (cap encara — només es publicarà el README)"
else
  printf '  ✓ %s\n' "${RELEASED[@]}"
fi

( cd "$WORK/private"  && find . -type f -not -path './.git/*' | sed 's#^\./##' | sort ) > "$WORK/all.txt"
( cd "$WORK/filtered" && find . -type f                       | sed 's#^\./##' | sort ) > "$WORK/pub.txt"
echo
echo "── ES PUBLICARAN ($(wc -l < "$WORK/pub.txt" | tr -d ' ') fitxers) ──"
sed 's/^/  + /' "$WORK/pub.txt"
echo
echo "── ES QUEDEN PRIVATS (docent + sessions encara no alliberades) ──"
comm -23 "$WORK/all.txt" "$WORK/pub.txt" | sed 's/^/  - /'
echo

# 4) Clona el PÚBLIC i hi aboca el filtrat (preservant .git, reflectint esborrats)
echo "▸ Clonant públic…"
git clone --quiet --branch "$BRANCH" "$PUBLIC_REMOTE" "$WORK/public"
rsync -a --delete --exclude='.git' "$WORK/filtered/" "$WORK/public/"

# 5) Commit + push si hi ha canvis
cd "$WORK/public"
git add -A
if git diff --cached --quiet; then
  echo "✓ El públic ja està al dia. Res a fer."
  exit 0
fi
echo "── CANVIS al públic ──"
git --no-pager diff --cached --stat
echo

if [[ "$DRY_RUN" == 1 ]]; then
  echo "▸ --dry-run: no es fa commit ni push."
  exit 0
fi
if [[ "$ASSUME_YES" != 1 ]]; then
  read -r -p "Publicar aquests canvis al públic? [s/N] " ans
  [[ "$ans" =~ ^[sSyY]$ ]] || { echo "Cancel·lat."; exit 0; }
fi

git commit --quiet -m "$COMMIT_MSG"
git push --quiet origin "$BRANCH"
echo "✓ Públic actualitzat."
