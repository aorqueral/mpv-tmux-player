#!/usr/bin/env python3
import socket
import json
import sys
import os
import subprocess

"""
mpv tmux music player
Runtime files (covers, socket) are stored in ~/.cache and /tmp
"""


# ---------- CONFIG ----------
SOCK = "/tmp/mpv.sock"

COVER_DIR = os.path.expanduser("~/.cache/mpv-cover")
COVER_CURRENT = os.path.join(COVER_DIR, "current.jpg")

os.makedirs(COVER_DIR, exist_ok=True)

# ---------- IPC ----------
def send(cmd):
    s = socket.socket(socket.AF_UNIX)
    s.connect(SOCK)
    s.send(json.dumps({"command": cmd}).encode() + b"\n")
    s.close()

# ---------- PLAY ----------
def play(query):
    query = query.strip()

    # ===== LOCAL FILE =====
    if os.path.exists(os.path.expanduser(query)):
        target = os.path.abspath(os.path.expanduser(query))
        title = os.path.basename(target)

        send(["loadfile", target, "replace"])
        send(["set_property", "force-media-title", title])

        # para música local: borrar cover (opcional pero limpio)
        if os.path.exists(COVER_CURRENT):
            os.remove(COVER_CURRENT)

        return

    # ===== YOUTUBE =====

    # 1) resolver URL de audio
    result = subprocess.run(
        [
            "yt-dlp",
            "-f", "ba",
            "--no-playlist",
            "--print", "url",
            "--quiet",
            "--no-warnings",
            f"ytsearch1:{query}",
        ],
        capture_output=True,
        text=True,
    )

    urls = result.stdout.strip().splitlines()
    if not urls:
        print("❌ No se pudo resolver YouTube")
        return

    audio_url = urls[0]

    # 2) descargar thumbnail y SOBREESCRIBIR siempre
    subprocess.run(
        [
            "yt-dlp",
            "--skip-download",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "-o", COVER_CURRENT,
            f"ytsearch1:{query}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 3) cargar audio en mpv
    send(["loadfile", audio_url, "replace"])
    send(["set_property", "force-media-title", query])

def search_and_play(query):
    # obtener top resultados (titulo + id)
    result = subprocess.run(
        [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(title)s | %(id)s",
            "--no-playlist",
            f"ytsearch10:{query}",
        ],
        capture_output=True,
        text=True,
    )

    raw = result.stdout.strip().splitlines()
    lines = [f"{i +1}. {line}" for i, line in enumerate(raw)]
    if not lines:
        print("❌ No hay resultados")
        return

    # fzf para elegir
    fzf = subprocess.run(
        ["fzf", "--prompt", "🎵 elegir> "],
        input="\n".join(lines),
        text=True,
        capture_output=True,
    )

    choice = fzf.stdout.strip()
    if not choice:
        return

    choice = choice.split(". ", 1)[1]
    title, vid = choice.rsplit(" | ", 1)

    # reproducir el elegido
    play(title)


# ---------- CONTROLS ----------
def pause():
    send(["cycle", "pause"])

def stop():
    send(["stop"])

# ---------- CLI ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso:")
        print("  mp play <ruta|texto>")
        print("  mp pause")
        print("  mp stop")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "play":
        play(" ".join(sys.argv[2:]))
    elif cmd == "search":
        search_and_play(" ".join(sys.argv[2:]))
    elif cmd == "pause":
        pause()
    elif cmd == "stop":
        stop()

