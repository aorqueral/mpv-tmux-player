#!/bin/bash

SOCK="/tmp/mpv.sock"
COVER="$HOME/.cache/mpv-cover/current.jpg.jpg"

cmd() {
  printf '{ "command": %s }\n' "$1" | socat - UNIX-CONNECT:$SOCK 2>/dev/null
}

title=$(cmd '["get_property","media-title"]' | jq -r '.data // empty')
pause=$(cmd '["get_property","pause"]' | jq -r '.data')
pos=$(cmd '["get_property","time-pos"]' | jq -r '.data')
dur=$(cmd '["get_property","duration"]' | jq -r '.data')

# si no hay nada sonando, no mostrar nada
[[ -z "$title" ]] && exit 0

fmt() {
  [[ -z "$1" || "$1" == "null" ]] && echo "--:--" && return
  printf "%02d:%02d" $((${1%.*}/60)) $((${1%.*}%60))
}

[[ "$pause" == "true" ]] && icon="⏸" || icon="▶︎"

# portada ASCII si existe
if [[ -f "$COVER" ]]; then
  cols=$(tput cols)
  rows=12
  # ancho real de la imagen (aprox)
  img_width=$cols
  pad=$(( (cols - img_width) / 2 ))
  [[ $pad -lt 0 ]] && pad=0
  chafa \
    --format=symbols \
    --symbols=block \
    --colors=256 \
    -s "${img_width}x${rows}" \
    "$COVER" | sed "s/^/$(printf '%*s' $pad)/"
  echo
fi

echo "🎵 $title"
echo "$icon $(fmt $pos) / $(fmt $dur)"

