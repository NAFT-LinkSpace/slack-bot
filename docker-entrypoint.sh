#!/bin/sh

set -eu

cd /app

if [ -f /app/.env ]; then
  slackdump workspace import /app/.env
fi

exec python /app/src/main.py