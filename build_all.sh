#!/bin/bash
# Executa build.sh a totes les carpetes de sessió del repositori
set -e

for d in */sessio*/; do
    if [ -f "$d/build.sh" ]; then
        echo "== $d =="
        (cd "$d" && ./build.sh)
    fi
done
