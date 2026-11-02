#!/usr/bin/env bash
# Regenera Diagrama/musica_er.png a partir de Diagrama/musica_er.mmd.
# Usa la imagen Docker de mermaid-cli, así que no hace falta instalar Node.
set -euo pipefail

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# `:z` permite el montaje en hosts con SELinux en modo Enforcing.
docker run --rm \
    -u "$(id -u):$(id -g)" \
    -v "${raiz}/Diagrama:/data:z" \
    minlag/mermaid-cli \
    -i /data/musica_er.mmd \
    -o /data/musica_er.png \
    --scale 2 \
    --backgroundColor white

echo "Diagrama generado en Diagrama/musica_er.png"
