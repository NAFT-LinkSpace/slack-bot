#!/bin/bash

cd $(dirname "$0")
source ./env/bin/activate
python ./src/main.py
