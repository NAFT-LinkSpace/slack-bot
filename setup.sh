#!/bin/bash

cd $(dirname "$0")

# Grant permissions
chmod +x ./src/merge_slack_backup.sh

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

# Make directories
WORK_DIR="./backup"/bin
mkdir -p $WORK_DIR

# Setup mmetl tool
cd $WORK_DIR
curl -LO https://github.com/mattermost/mmetl/releases/download/v0.1.1/linux_amd64.tar.gz
tar -zxf linux_amd64.tar.gz
rm linux_amd64.tar.gz
