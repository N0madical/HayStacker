#!/bin/sh

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


### Start the program
cd ./App
./.venv/bin/python main.py
