#!/bin/sh

cd $(dirname "$0")
cd ../

# Grant permissions to scripts
chmod +x ./src/fix_database.sh

IS_WINDOWS=0
if [ "$(uname -s | grep -i Windows)" != "" ]; then
  IS_WINDOWS=1
fi

# Pick a python executable (python3 preferred)
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Error: Could not find Python in PATH." >&2
  exit 1
fi

# Make python virtual environment and install required packages
if [ ! -d "./env" ]; then
  if [ $IS_WINDOWS -eq 0 ]; then
    $PYTHON -m venv ./env
  else
    cmd.exe /C "$PYTHON -m venv .\env"
  fi
fi

if [ -f ./env/bin/activate ]; then
  . ./env/bin/activate
elif [ -f ./env/Scripts/activate ]; then
  . ./env/Scripts/activate
else
  echo "Error: virtualenv activate script not found in ./env." >&2
  exit 1
fi

pip install --upgrade pip
pip install -r ./requirements.txt

# Install slackdump tool
if command -v slackdump >/dev/null 2>&1; then
  echo "slackdump already available in PATH; skipping install."
else
  if [ $IS_WINDOWS -eq 0 ]; then
    echo "Installing slackdump (.deb) via dpkg..."
    curl -LO https://github.com/rusq/slackdump/releases/download/v3.1.8/slackdump_3.1.8_linux_amd64.deb
    sudo dpkg -i slackdump_3.1.8_linux_amd64.deb
    rm slackdump_3.1.8_linux_amd64.deb
  else
    echo "please install slackdump manually." >&2
    exit 1
  fi
fi

# Setup slackdump with workspace info
slackdump workspace import .env

# Make directory for backup files
mkdir ./backup
