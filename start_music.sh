#!/bin/bash

# mpv daemon (si no existe)
if ! pgrep -f "mpv --no-video --idle=yes --input-ipc-server=/tmp/mpv.sock" > /dev/null; then
  mpv --no-video --idle=yes --input-ipc-server=/tmp/mpv.sock &
  sleep 0.5
fi

# sesión tmux
if ! tmux has-session -t music 2>/dev/null; then
  tmux new-session -d -s music

  # pane principal (dashboard)
  tmux send-keys -t music '
tput civis
while true; do
  tput cup 0 0
  tput ed
  ~/.tmux/scripts/music/mpv_status.sh
  sleep 1
done' C-m
fi

tmux attach -t music

