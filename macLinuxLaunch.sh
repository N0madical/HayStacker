#!/bin/bash

if ! command -v python3; then
    echo "Python 3 is not installed."
    echo "Please install it before HayStacker can run. Thanks!"
    touch pleaseInstallPython3ToRun.thankyou;
    exit 1;
fi

if ! [ -d "./App/.venv" ]; then
    python3 -m venv ./App/.venv
    source ./App/.venv/bin/activate
    pip install -r ./App/requirements.txt
fi

if [ -f "pleaseInstallPython3ToRun.thankyou" ]; then
    rm pleaseInstallPython3ToRun.thankyou
fi


### Start the program
cd ./App
./.venv/bin/python main.py
