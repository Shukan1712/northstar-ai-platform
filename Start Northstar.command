#!/bin/zsh
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if ! docker info >/dev/null 2>&1; then
  open -a Docker
  echo "Starting Docker Desktop..."
  for attempt in {1..90}; do
    if docker info >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker did not become ready. Open Docker Desktop and run this file again."
  read -k 1 "?Press any key to close."
  exit 1
fi

docker compose up --build -d
echo "Northstar is starting at http://localhost:4173"
for attempt in {1..60}; do
  if curl -fsS http://localhost:4173 >/dev/null 2>&1; then
    NORTHSTAR_CACHE_BUST="$(date +%s)"
    open "http://localhost:4173/?v=$NORTHSTAR_CACHE_BUST"
    exit 0
  fi
  sleep 2
done

echo "The containers started, but the website is still warming up."
NORTHSTAR_CACHE_BUST="$(date +%s)"
open "http://localhost:4173/?v=$NORTHSTAR_CACHE_BUST"
