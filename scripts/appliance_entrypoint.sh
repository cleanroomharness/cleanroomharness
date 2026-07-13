#!/bin/sh
# Appliance entrypoint: start the in-container Ollama model server, wait for
# it, then run the harness API as the main process. Run the container with
# --init (or compose `init: true`) so orphaned children are reaped.
set -e

ollama serve &

i=0
until curl -sf http://127.0.0.1:11434/api/version >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -gt 60 ]; then
    echo "ollama model server failed to start" >&2
    exit 1
  fi
  sleep 1
done
echo "ollama model server ready"

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
