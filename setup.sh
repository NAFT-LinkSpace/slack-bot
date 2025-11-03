#!/bin/bash

cd $(dirname "$0")

# Grant permissions to scripts
chmod +x ./src/fix_database.sh

# Make python virtual environment and install required packages
if [ ! -d "./env" ]; then
  python3 -m venv ./env
fi
source ./env/bin/activate
pip install --upgrade pip
pip install -r ./requirements.txt

# Install slackdump tool
curl -LO https://github.com/rusq/slackdump/releases/download/v3.1.8/slackdump_3.1.8_linux_amd64.deb
sudo dpkg -i slackdump_3.1.8_linux_amd64.deb
rm slackdump_3.1.8_linux_amd64.deb

# Setup slackdump with workspace info
slackdump workspace import .env

# Make directory for backup files
mkdir ./backup
