#!/bin/bash
# Genera versions .docx de tots els .md d'aquesta sessió (incloent recursos/)
# Sortida: docx/ (mateixa estructura relativa, ignorat per git)

set -e

mkdir -p docx
mkdir -p docx/recursos

for f in *.md; do
    [ -e "$f" ] || continue
    pandoc "$f" -o "docx/${f%.md}.docx"
    echo "✓ $f -> docx/${f%.md}.docx"
done

for f in recursos/*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    pandoc "$f" -o "docx/recursos/${base%.md}.docx"
    echo "✓ $f -> docx/recursos/${base%.md}.docx"
done
