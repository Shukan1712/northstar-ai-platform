#!/bin/zsh
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
docker compose down -v
docker compose up --build -d
echo "Northstar data was reset and reseeded."

