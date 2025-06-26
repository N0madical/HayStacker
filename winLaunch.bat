@echo off
setlocal enabledelayedexpansion

echo Welcome to HayStacker^^!


:pyCheck
@REM Check if Python is installed. It is needed to run the app. Install it if now
python --version 3>NUL
if %errorlevel% neq 0 (
    call:pythonNotInstalled
)  else (
    echo Python is installed, good
)

@rem ### Check if the Python virtual enviorment exists
if not exist .\App\.venv\ (
    call:venvMissing
    timeout /t 10
) else (
    echo Virtual enviorment exists, good
)

echo Launching!

@REM ### Start the program
cd .\App
start winLaunch.vbs

pause
endlocal
exit 0

@rem ### What to do if Python is not installed
:pythonNotInstalled
echo ---
echo Python 3.13 is necessary for this project
echo As it was built in Python, and packaging was avoided for modularity
echo Python can be installed via the windows store, at https://apps.microsoft.com/detail/9PNRBTZXMB4Z
echo To open the microsoft store, press enter
echo ---
set /p DUMMY=Press ENTER to continue...
python
set /p DUMMY2=Press ENTER when Python is installed...
goto :pyCheck

@rem ### Build Python Venv
:venvMissing
echo ---
echo Building Python Virtual Enviorment...
@echo on
python -m venv .\App\.venv
set pydir=".\App\.venv\Scripts\python.exe"
@echo off
echo -----
echo Installing dependencies...
echo -----
@echo on
%pydir% -m pip install cryptography
%pydir% -m pip install pycryptodome
%pydir% -m pip install tkintermapview
%pydir% -m pip install esptool
%pydir% -m pip install pbkdf2
%pydir% -m pip install srp
@echo off
echo Python enviorment built!
goto :eof