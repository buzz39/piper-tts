#!/bin/sh
set -e

# Fallbacks if envs are not set
: "${PIPER_VOICE:=en_US-lessac-medium}"
: "${PIPER_DATA_DIR:=/app/voices}"

# Start Piper HTTP server with env-configured voice
exec python -m piper.http_server \
  --data-dir "${PIPER_DATA_DIR}" \
  -m "${PIPER_VOICE}" \
  --host 0.0.0.0 \
  --port 5000
