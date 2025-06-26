#!/bin/bash

if ! command -v python3; then
    echo "Python 3 is not installed."
    echo "Please install it before HayStacker can run. Thanks!"
    touch pleaseInstallPython3ToRun.thankyou;
    exit 1;
fi

if ! [ -d "./App/.venv" ]; then
    python -m venv ./App/.venv
    pydir="./App/.venv/bin/python"
    $pydir -m pip install cryptography
    $pydir -m pip install pycryptodome
    $pydir -m pip install tkintermapview
    $pydir -m pip install esptool
    $pydir -m pip install pbkdf2
    $pydir -m pip install srp
fi

if [ -f "pleaseInstallPython3ToRun.thankyou" ]; then
    rm pleaseInstallPython3ToRun.thankyou
fi


### Start the program
cd ./App
./.venv/bin/python main.py
