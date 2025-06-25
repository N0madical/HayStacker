@echo off
setlocal enabledelayedexpansion

echo Welcome to HayStacker^^!

@REM ### Check if WSL is installed. It is needed to run linux commands on windows. Install it if not
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    call:wslNotInstalled
) 

wsl -l -q | findstr "U.b.u.n.t.u" >nul 2>nul
if %errorlevel% equ 0 (
    echo Ubuntu is installed in WSL, good
) else (
    echo ---
    echo Ubuntu is not installed in WSL.
    call:wslNotInstalled
)


@REM Check if Python is installed. It is needed to run the app. Install it if now
where python >nul 2>&1
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

endlocal
exit 0

@rem ### What to do if WSL is not installed or improperly configured
:wslNotInstalled
echo ---
echo WSL ^(Windows Subsystem for Linux^) Ubuntu is necessary for this project
echo It allows Linux commands and programs to run on Windows
echo This is necessary for the script that communicates with Apple's servers
echo ---
set /p name=Install? ^(y/n^):

if /i "!name!" == "y" (
    echo Installing WSL...
    wsl --install -d Ubuntu
    if !ERRORLEVEL! NEQ 0 (
        echo ---
        echo Administrator access is required or something else has gone wrong :(
        echo Right click this .bat file and click 'run as admininstrator'
        echo ---
        pause
        exit 126
    ) 
) else (
        echo HayStacker dependency install declined...
        pause
        exit 0
)
goto :eof

@rem ### What to do if Python is not installed
:pythonNotInstalled
echo ---
echo Python 3.13 is necessary for this project
echo As it was built in Python, and packaging was avoided for modularity
echo Python can be installed via the windows store
echo Please visit: https://apps.microsoft.com/detail/9PNRBTZXMB4Z
echo ---
pause
goto :eof

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