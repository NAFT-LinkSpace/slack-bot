#!/bin/sh

cd $(dirname "$0")
cd ../

# Prefer POSIX-compatible activation (use '.' instead of 'source')
if [ -f ./env/bin/activate ]; then
  # Unix-like venv
  . ./env/bin/activate
elif [ -f ./env/Scripts/activate ]; then
  # Windows venv (when using BusyBox/MSYS/Git-Bash/etc.)
  . ./env/Scripts/activate
else
  echo "Error: virtualenv activate script not found in ./env." >&2
  exit 1
fi

python ./src/main.py
